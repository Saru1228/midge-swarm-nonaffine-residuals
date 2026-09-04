#!/usr/bin/env python3
"""Experiment 3032b: state meaning and residence audit for 3032.

This node follows a positive 3032 transfer-operator gate. It asks whether the
best almost-invariant partition has a physically interpretable meaning and
whether its residence is deep enough to support a metastable-state narrative.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Experiment"))

from run_3032_transfer_operator_metastability import (  # noqa: E402
    COARSE_STATE_ORDER,
    DEFAULT_SLOW_VARIABLES,
    HAVE_3013,
    SET_ORDER,
    add_coarse_states,
    dataframe_to_markdown,
    finite_fraction,
    finite_median,
    finite_quantile,
    label_sequence,
    median_dt,
    robust_z,
    safe_float,
    strip_candidate_name,
    weighted_median,
)


RAW_PATH = ROOT / "Output" / "3001" / "processed" / "geometric_center_observables_all.csv"
DECISION_3032 = ROOT / "Output" / "3032" / "tables" / "egrt_decision_summary.csv"
BIN_EDGES_3032 = ROOT / "Output" / "3032" / "tables" / "ulam_bin_edges.json"
MAPPING_3032 = ROOT / "Output" / "3032" / "tables" / "spectral_cell_mapping.csv"
OUT = ROOT / "Output" / "3032b"
FIG = OUT / "figures"
TAB = OUT / "tables"
PROC = OUT / "processed"

RNG_SEED = 30322
EMISSION_VARIABLES = [
    "n",
    "center_speed",
    "radial_velocity_mean",
    "frac_outward",
    "r_rms",
    "density_rms",
    "anisotropy",
    "polarization",
    "milling",
    "kinetic_energy",
    "speed_mean",
    "p_inner",
]


@dataclass(frozen=True)
class RunConfig:
    lags_sec: tuple[float, ...] = (0.05, 0.10, 0.20, 0.50, 1.00)
    residence_thresholds_sec: tuple[float, ...] = (0.10, 0.20, 0.50, 1.00, 2.00)
    meaning_delta_gate: float = 0.50
    meaning_consistency_gate: float = 0.70
    residence_median_gate_sec: float = 0.20
    residence_q75_gate_sec: float = 0.50
    long_lag_sec: float = 0.50
    long_lag_q25_retention_gate: float = 0.60
    long_lag_lift_gate: float = 0.10
    coarse_overlap_nmi_boundary: float = 0.05
    n_bins: int = 4
    scatter_sample: int = 60000


def ensure_dirs() -> None:
    for path in (OUT, FIG, TAB, PROC):
        path.mkdir(parents=True, exist_ok=True)


def read_decision() -> dict[str, object]:
    if not DECISION_3032.exists():
        raise FileNotFoundError("Run 3032 first; missing Output/3032/tables/egrt_decision_summary.csv")
    df = pd.read_csv(DECISION_3032)
    if df.empty:
        raise ValueError("3032 decision table is empty")
    return df.iloc[0].to_dict()


def candidate_variables(decision: dict[str, object]) -> list[str]:
    raw = str(decision.get("candidate_variables", ""))
    variables = [strip_candidate_name(x) for x in raw.split(",") if str(x).strip()]
    variables = [x for x in variables if x]
    ordered = [x for x in DEFAULT_SLOW_VARIABLES if x in set(variables)]
    ordered.extend(x for x in variables if x not in ordered)
    return ordered if len(ordered) >= 2 else list(DEFAULT_SLOW_VARIABLES)


def read_edges() -> dict[str, list[float]]:
    if not BIN_EDGES_3032.exists():
        raise FileNotFoundError("Run 3032 first; missing Output/3032/tables/ulam_bin_edges.json")
    return json.loads(BIN_EDGES_3032.read_text(encoding="utf-8"))


def read_mapping(best_partition_id: str) -> pd.DataFrame:
    if not MAPPING_3032.exists():
        raise FileNotFoundError("Run 3032 first; missing Output/3032/tables/spectral_cell_mapping.csv")
    mapping = pd.read_csv(MAPPING_3032)
    mapping = mapping[mapping["partition_id"].astype(str) == str(best_partition_id)].copy()
    if mapping.empty:
        raise ValueError(f"No spectral-cell mapping found for partition {best_partition_id}")
    return mapping


def read_input(variables: list[str]) -> pd.DataFrame:
    usecols = ["dataset", "ob", "t", "dt", *sorted(set(EMISSION_VARIABLES + variables))]
    df = pd.read_csv(RAW_PATH, usecols=lambda c: c in set(usecols))
    missing = [c for c in usecols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in {RAW_PATH}: {missing}")
    for col in [c for c in df.columns if c != "dataset"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.sort_values(["ob", "t"], kind="mergesort").reset_index(drop=True)


def standardize_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = []
    for (_, _dataset), d in df.groupby(["ob", "dataset"], sort=True):
        d = d.copy()
        for col in columns:
            d[f"{col}_z"] = robust_z(d[col])
        out.append(d)
    return pd.concat(out, ignore_index=True)


def assign_cells_from_edges(df: pd.DataFrame, variables: list[str], edges: dict[str, list[float]], n_bins: int) -> pd.DataFrame:
    out = df.copy()
    cell = np.zeros(len(out), dtype="int64")
    for var in variables:
        zcol = f"{var}_z"
        qs = np.asarray(edges[var], dtype="float64")
        vals = pd.to_numeric(out[zcol], errors="coerce").to_numpy(dtype="float64")
        bins = np.searchsorted(qs, vals, side="right").astype("int64")
        bins = np.clip(bins, 0, n_bins - 1)
        out[f"{var}_bin"] = bins
        cell = cell * n_bins + bins
    out["ulam_cell"] = cell
    return out.dropna(subset=[f"{x}_z" for x in variables]).reset_index(drop=True)


def attach_partition_labels(df: pd.DataFrame, mapping: pd.DataFrame) -> pd.DataFrame:
    cell_to_set = {int(r.ulam_cell): str(r.spectral_set) for r in mapping.itertuples(index=False)}
    out = df.copy()
    out["spectral_set"] = label_sequence(out["ulam_cell"].to_numpy(dtype="int64"), cell_to_set)
    return out


def emission_summary(df: pd.DataFrame, variables: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    emission_cols = [c for c in EMISSION_VARIABLES if c in df.columns]
    rows = []
    ob_rows = []
    known = df[df["spectral_set"].isin(SET_ORDER)].copy()
    for col in emission_cols:
        zcol = f"{col}_z"
        if zcol not in known.columns:
            continue
        set_medians: dict[str, float] = {}
        set_raw_medians: dict[str, float] = {}
        for set_name in SET_ORDER:
            d = known[known["spectral_set"] == set_name]
            set_medians[set_name] = float(np.nanmedian(d[zcol])) if len(d) else math.nan
            set_raw_medians[set_name] = float(np.nanmedian(d[col])) if len(d) else math.nan
        delta = set_medians.get("high", math.nan) - set_medians.get("low", math.nan)
        for (ob, dataset), d_ob in known.groupby(["ob", "dataset"], sort=True):
            low = d_ob[d_ob["spectral_set"] == "low"]
            high = d_ob[d_ob["spectral_set"] == "high"]
            delta_ob = (
                float(np.nanmedian(high[zcol])) - float(np.nanmedian(low[zcol]))
                if len(low) and len(high)
                else math.nan
            )
            ob_rows.append(
                {
                    "variable": col,
                    "ob": int(ob),
                    "dataset": str(dataset),
                    "delta_high_minus_low_z": delta_ob,
                    "abs_delta_high_minus_low_z": abs(delta_ob) if np.isfinite(delta_ob) else math.nan,
                }
            )
        dvar = pd.DataFrame([x for x in ob_rows if x["variable"] == col])
        rows.append(
            {
                "variable": col,
                "role": "3032_state_space" if col in variables else "external_emission",
                "low_median_raw": set_raw_medians.get("low", math.nan),
                "high_median_raw": set_raw_medians.get("high", math.nan),
                "low_median_z": set_medians.get("low", math.nan),
                "high_median_z": set_medians.get("high", math.nan),
                "delta_high_minus_low_z": delta,
                "abs_delta_high_minus_low_z": abs(delta) if np.isfinite(delta) else math.nan,
                "median_ob_delta_z": finite_median(dvar["delta_high_minus_low_z"]) if not dvar.empty else math.nan,
                "q25_ob_delta_z": finite_quantile(dvar["delta_high_minus_low_z"], 0.25) if not dvar.empty else math.nan,
                "q75_ob_delta_z": finite_quantile(dvar["delta_high_minus_low_z"], 0.75) if not dvar.empty else math.nan,
                "frac_ob_same_sign": finite_fraction(np.sign(dvar["delta_high_minus_low_z"]) == np.sign(delta)) if not dvar.empty and np.isfinite(delta) else math.nan,
                "frac_ob_abs_delta_ge_0p5": finite_fraction(dvar["abs_delta_high_minus_low_z"] >= 0.5) if not dvar.empty else math.nan,
            }
        )
    summary = pd.DataFrame(rows).sort_values("abs_delta_high_minus_low_z", ascending=False).reset_index(drop=True)
    by_ob = pd.DataFrame(ob_rows)
    return summary, by_ob


def residence_runs(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (ob, dataset), d in df.groupby(["ob", "dataset"], sort=True):
        d = d.sort_values("t").reset_index(drop=True)
        dt = median_dt(d)
        if not np.isfinite(dt) or dt <= 0:
            continue
        labels = d["spectral_set"].to_numpy(dtype=object)
        if len(labels) == 0:
            continue
        start = 0
        current = labels[0]
        for i in range(1, len(labels) + 1):
            if i < len(labels) and labels[i] == current:
                continue
            if current in SET_ORDER:
                length = i - start
                rows.append(
                    {
                        "ob": int(ob),
                        "dataset": str(dataset),
                        "spectral_set": str(current),
                        "start_index": int(start),
                        "end_index_exclusive": int(i),
                        "run_frames": int(length),
                        "run_duration_sec": float(length * dt),
                    }
                )
            if i < len(labels):
                start = i
                current = labels[i]
    return pd.DataFrame(rows)


def residence_summary(runs: pd.DataFrame, cfg: RunConfig) -> pd.DataFrame:
    rows = []
    for set_name, d in runs.groupby("spectral_set", sort=True):
        row: dict[str, object] = {
            "spectral_set": str(set_name),
            "n_runs": int(len(d)),
            "median_run_duration_sec": finite_median(d["run_duration_sec"]),
            "q75_run_duration_sec": finite_quantile(d["run_duration_sec"], 0.75),
            "q90_run_duration_sec": finite_quantile(d["run_duration_sec"], 0.90),
            "q95_run_duration_sec": finite_quantile(d["run_duration_sec"], 0.95),
            "mean_run_duration_sec": float(np.nanmean(d["run_duration_sec"])) if len(d) else math.nan,
        }
        for thr in cfg.residence_thresholds_sec:
            key = str(thr).replace(".", "p")
            row[f"frac_runs_ge_{key}s"] = float(np.mean(d["run_duration_sec"] >= thr)) if len(d) else math.nan
        rows.append(row)
    all_row: dict[str, object] = {
        "spectral_set": "all",
        "n_runs": int(len(runs)),
        "median_run_duration_sec": finite_median(runs["run_duration_sec"]),
        "q75_run_duration_sec": finite_quantile(runs["run_duration_sec"], 0.75),
        "q90_run_duration_sec": finite_quantile(runs["run_duration_sec"], 0.90),
        "q95_run_duration_sec": finite_quantile(runs["run_duration_sec"], 0.95),
        "mean_run_duration_sec": float(np.nanmean(runs["run_duration_sec"])) if len(runs) else math.nan,
    }
    for thr in cfg.residence_thresholds_sec:
        key = str(thr).replace(".", "p")
        all_row[f"frac_runs_ge_{key}s"] = float(np.mean(runs["run_duration_sec"] >= thr)) if len(runs) else math.nan
    rows.append(all_row)
    return pd.DataFrame(rows)


def lag_retention(df: pd.DataFrame, cfg: RunConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    for lag_sec in cfg.lags_sec:
        for (ob, dataset), d in df.groupby(["ob", "dataset"], sort=True):
            d = d.sort_values("t").reset_index(drop=True)
            dt = median_dt(d)
            if not np.isfinite(dt) or dt <= 0:
                continue
            lag_frames = max(1, int(round(lag_sec / dt)))
            labels = d["spectral_set"].to_numpy(dtype=object)
            if len(labels) <= lag_frames:
                continue
            origin = labels[:-lag_frames]
            dest = labels[lag_frames:]
            for set_name in SET_ORDER:
                mass = float(np.mean(labels == set_name)) if len(labels) else math.nan
                mask = origin == set_name
                origin_count = int(np.sum(mask))
                retained = int(np.sum(mask & (dest == set_name)))
                retention = float(retained / origin_count) if origin_count else math.nan
                rows.append(
                    {
                        "lag_sec": float(lag_sec),
                        "ob": int(ob),
                        "dataset": str(dataset),
                        "spectral_set": set_name,
                        "mass": mass,
                        "origin_count": origin_count,
                        "retained_count": retained,
                        "retention": retention,
                        "retention_lift": retention - mass if np.isfinite(retention) and np.isfinite(mass) else math.nan,
                    }
                )
    detail = pd.DataFrame(rows)
    summary_rows = []
    for (lag_sec, set_name), d in detail.groupby(["lag_sec", "spectral_set"], sort=True):
        summary_rows.append(
            {
                "lag_sec": float(lag_sec),
                "spectral_set": str(set_name),
                "median_retention": finite_median(d["retention"]),
                "q25_retention": finite_quantile(d["retention"], 0.25),
                "q75_retention": finite_quantile(d["retention"], 0.75),
                "median_retention_lift": finite_median(d["retention_lift"]),
                "q25_retention_lift": finite_quantile(d["retention_lift"], 0.25),
                "frac_ob_lift_positive": finite_fraction(d["retention_lift"] > 0),
                "median_mass": finite_median(d["mass"]),
                "median_origin_count": finite_median(d["origin_count"]),
            }
        )
    summary = pd.DataFrame(summary_rows).sort_values(["lag_sec", "spectral_set"]).reset_index(drop=True)
    return detail, summary


def two_state_transition_summary(df: pd.DataFrame, lags_sec: tuple[float, ...]) -> pd.DataFrame:
    rows = []
    for lag_sec in lags_sec:
        counts = {(a, b): 0 for a in SET_ORDER for b in SET_ORDER}
        origins = {a: 0 for a in SET_ORDER}
        for (_ob, _dataset), d in df.groupby(["ob", "dataset"], sort=True):
            d = d.sort_values("t").reset_index(drop=True)
            dt = median_dt(d)
            if not np.isfinite(dt) or dt <= 0:
                continue
            lag_frames = max(1, int(round(lag_sec / dt)))
            labels = d["spectral_set"].to_numpy(dtype=object)
            if len(labels) <= lag_frames:
                continue
            origin = labels[:-lag_frames]
            dest = labels[lag_frames:]
            for a in SET_ORDER:
                mask = origin == a
                origins[a] += int(np.sum(mask))
                for b in SET_ORDER:
                    counts[(a, b)] += int(np.sum(mask & (dest == b)))
        for a in SET_ORDER:
            for b in SET_ORDER:
                denom = origins[a]
                rows.append(
                    {
                        "lag_sec": float(lag_sec),
                        "from_set": a,
                        "to_set": b,
                        "count": int(counts[(a, b)]),
                        "origin_count": int(denom),
                        "transition_probability": float(counts[(a, b)] / denom) if denom else math.nan,
                    }
                )
    return pd.DataFrame(rows)


def coarse_overlap(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    d = add_coarse_states(df)
    ctab = pd.crosstab(d["spectral_set"], d["coarse_state"])
    ctab = ctab.reindex(index=SET_ORDER, columns=COARSE_STATE_ORDER + ["unavailable"], fill_value=0)
    ctab = ctab.loc[:, (ctab.sum(axis=0) > 0)]
    obs = ctab.to_numpy(dtype="float64")
    n = float(obs.sum())
    if n <= 0:
        stats = {"normalized_mutual_information": math.nan, "cramers_v": math.nan}
    else:
        pxy = obs / n
        px = pxy.sum(axis=1)
        py = pxy.sum(axis=0)
        denom = px[:, None] * py[None, :]
        mask = (pxy > 0) & (denom > 0)
        mi = float(np.sum(pxy[mask] * np.log(pxy[mask] / denom[mask])))
        hx = float(-np.sum(px[px > 0] * np.log(px[px > 0])))
        hy = float(-np.sum(py[py > 0] * np.log(py[py > 0])))
        nmi = mi / math.sqrt(hx * hy) if hx > 0 and hy > 0 else math.nan
        expected = np.outer(obs.sum(axis=1), obs.sum(axis=0)) / n
        valid = expected > 0
        chi2 = float(np.sum((obs[valid] - expected[valid]) ** 2 / expected[valid]))
        denom_v = n * max(1, min(obs.shape[0] - 1, obs.shape[1] - 1))
        cramers_v = math.sqrt(chi2 / denom_v) if denom_v > 0 else math.nan
        stats = {"normalized_mutual_information": nmi, "cramers_v": cramers_v}
    overlap = pd.DataFrame(
        [
            {
                "n_frames": int(n),
                "normalized_mutual_information": stats["normalized_mutual_information"],
                "cramers_v": stats["cramers_v"],
                "coarse_state_source": "3013 classifier" if HAVE_3013 else "unavailable",
            }
        ]
    )
    composition = ctab.div(ctab.sum(axis=1).replace(0, np.nan), axis=0).reset_index()
    return overlap, composition


def decision_summary(
    parent_decision: dict[str, object],
    best_partition_id: str,
    emission: pd.DataFrame,
    residence: pd.DataFrame,
    lag_summary: pd.DataFrame,
    overlap: pd.DataFrame,
    cfg: RunConfig,
) -> pd.DataFrame:
    state_space = emission[emission["role"] == "3032_state_space"].copy()
    strongest = state_space.sort_values("abs_delta_high_minus_low_z", ascending=False).head(1)
    strongest_var = str(strongest["variable"].iloc[0]) if not strongest.empty else ""
    strongest_delta = safe_float(strongest["delta_high_minus_low_z"].iloc[0]) if not strongest.empty else math.nan
    strongest_consistency = safe_float(strongest["frac_ob_same_sign"].iloc[0]) if not strongest.empty else math.nan
    meaning_pass = (
        np.isfinite(strongest_delta)
        and abs(strongest_delta) >= cfg.meaning_delta_gate
        and strongest_consistency >= cfg.meaning_consistency_gate
    )
    all_res = residence[residence["spectral_set"] == "all"]
    median_res = safe_float(all_res["median_run_duration_sec"].iloc[0]) if not all_res.empty else math.nan
    q75_res = safe_float(all_res["q75_run_duration_sec"].iloc[0]) if not all_res.empty else math.nan
    residence_pass = (
        np.isfinite(median_res)
        and median_res >= cfg.residence_median_gate_sec
        and np.isfinite(q75_res)
        and q75_res >= cfg.residence_q75_gate_sec
    )
    long_lag = lag_summary[np.isclose(lag_summary["lag_sec"], cfg.long_lag_sec)].copy()
    q25_long = finite_median(long_lag["q25_retention"]) if not long_lag.empty else math.nan
    lift_long = finite_median(long_lag["q25_retention_lift"]) if not long_lag.empty else math.nan
    long_lag_pass = (
        np.isfinite(q25_long)
        and q25_long >= cfg.long_lag_q25_retention_gate
        and np.isfinite(lift_long)
        and lift_long >= cfg.long_lag_lift_gate
    )
    nmi = safe_float(overlap["normalized_mutual_information"].iloc[0]) if not overlap.empty else math.nan
    coarse_independent = np.isfinite(nmi) and nmi < cfg.coarse_overlap_nmi_boundary

    if meaning_pass and residence_pass and long_lag_pass:
        decision = "extend_metastable_state_branch"
        next_node = "3032c robustness against smooth-autocorrelation nulls"
        boundary = "The partition has clear slow-variable meaning and enough residence depth to justify a robustness node."
    elif meaning_pass and long_lag_pass:
        decision = "boundary_shallow_but_persistent_organization"
        next_node = "3032c smooth-autocorrelation/null-model audit"
        boundary = "The partition is interpretable and remains above baseline at longer lags, but individual residence runs are short; test whether smooth autocorrelation explains the result."
    elif meaning_pass:
        decision = "boundary_interpretable_but_shallow"
        next_node = "pause or run 3032c only if a stronger null audit is needed"
        boundary = "The partition is physically interpretable, but residence depth is too shallow for a strong metastable-state claim."
    else:
        decision = "retire_3032_partition_as_uninterpretable"
        next_node = "pause 303x attractor narrative"
        boundary = "The positive 3032 partition lacks a stable physical meaning under the emission audit."

    return pd.DataFrame(
        [
            {
                "node_id": "3032b_state_meaning_residence_audit",
                "parent_node": "3032_transfer_operator_metastability",
                "parent_decision": str(parent_decision.get("eg_rt_decision", "")),
                "best_partition_id": best_partition_id,
                "strongest_state_space_variable": strongest_var,
                "strongest_delta_high_minus_low_z": strongest_delta,
                "strongest_variable_sign_consistency": strongest_consistency,
                "meaning_pass": bool(meaning_pass),
                "median_residence_sec": median_res,
                "q75_residence_sec": q75_res,
                "residence_pass": bool(residence_pass),
                "long_lag_sec": cfg.long_lag_sec,
                "long_lag_median_q25_retention": q25_long,
                "long_lag_median_q25_retention_lift": lift_long,
                "long_lag_pass": bool(long_lag_pass),
                "coarse_state_nmi": nmi,
                "coarse_state_independent": bool(coarse_independent),
                "eg_rt_decision": decision,
                "recommended_next_node": next_node,
                "boundary_reading": boundary,
            }
        ]
    )


def write_node_schema(decision: pd.DataFrame, cfg: RunConfig) -> None:
    rec = decision.iloc[0].to_dict()
    node = {
        "node_id": "3032b_state_meaning_residence_audit",
        "series": "303x",
        "node_type": "mechanism",
        "parent_node": "3032_transfer_operator_metastability",
        "question": "Does the 3032 almost-invariant partition have clear physical meaning and residence depth?",
        "competing_interpretations": [
            "interpretable metastable macroscopic state",
            "smooth compactness fluctuation with short residence",
            "coarse-state relabeling of 3013 quiet/mobile states",
        ],
        "method": [
            "assign 3032 best spectral labels to every frame",
            "compare low/high emissions with within-Ob robust-z effect sizes",
            "measure residence-run distributions",
            "measure retention decay from 0.05s to 1.00s",
            "compare spectral labels to the 3013 coarse-state classifier",
        ],
        "pass_gate": {
            "meaning": f"strongest state-space median delta >= {cfg.meaning_delta_gate} z and sign consistency >= {cfg.meaning_consistency_gate}",
            "residence": f"median residence >= {cfg.residence_median_gate_sec}s and q75 residence >= {cfg.residence_q75_gate_sec}s",
            "long_lag": f"q25 retention at {cfg.long_lag_sec}s >= {cfg.long_lag_q25_retention_gate} and lift >= {cfg.long_lag_lift_gate}",
        },
        "next_if_pass": "3032c robustness against smooth-autocorrelation nulls",
        "next_if_fail": "pause or retire this metastability branch",
        "outputs": [
            "Output/3032b/tables/emission_effect_summary.csv",
            "Output/3032b/tables/residence_summary.csv",
            "Output/3032b/tables/lag_retention_summary.csv",
            "Output/3032b/tables/egrt_decision_summary.csv",
            "Output/3032b/3032b_summary.md",
        ],
        "provenance": {
            "script": "Experiment/run_3032b_state_meaning_residence_audit.py",
            "decision": rec,
        },
    }
    (OUT / "3032b_egrt_node.json").write_text(json.dumps(node, ensure_ascii=False, indent=2), encoding="utf-8")


def make_figures(
    emission: pd.DataFrame,
    residence: pd.DataFrame,
    lag_summary: pd.DataFrame,
    composition: pd.DataFrame,
    df: pd.DataFrame,
    cfg: RunConfig,
) -> None:
    if not emission.empty:
        d = emission.sort_values("abs_delta_high_minus_low_z", ascending=True).tail(12)
        fig, ax = plt.subplots(figsize=(8.0, 5.2))
        colors = ["#2f6f6d" if role == "3032_state_space" else "#8a8a8a" for role in d["role"]]
        ax.barh(d["variable"], d["delta_high_minus_low_z"], color=colors)
        ax.axvline(0.0, color="#222222", linewidth=0.7)
        ax.axvline(cfg.meaning_delta_gate, color="#777777", linestyle="--", linewidth=0.8)
        ax.axvline(-cfg.meaning_delta_gate, color="#777777", linestyle="--", linewidth=0.8)
        ax.set_xlabel("high minus low median within-Ob z")
        ax.set_title("3032b spectral-set emission differences")
        fig.tight_layout()
        fig.savefig(FIG / "emission_effects_high_minus_low.png", dpi=180)
        plt.close(fig)

    if not residence.empty:
        fig, ax = plt.subplots(figsize=(7.4, 4.8))
        d = residence[residence["spectral_set"].isin(SET_ORDER)]
        ax.bar(d["spectral_set"], d["median_run_duration_sec"], color=["#4c78a8", "#f58518"])
        ax.axhline(cfg.residence_median_gate_sec, color="#777777", linestyle="--", linewidth=0.8)
        ax.set_ylabel("median run duration (s)")
        ax.set_title("3032b residence-run median duration")
        fig.tight_layout()
        fig.savefig(FIG / "residence_duration_by_set.png", dpi=180)
        plt.close(fig)

    if not lag_summary.empty:
        fig, ax = plt.subplots(figsize=(7.8, 4.8))
        for set_name, color in [("low", "#4c78a8"), ("high", "#f58518")]:
            d = lag_summary[lag_summary["spectral_set"] == set_name].sort_values("lag_sec")
            ax.plot(d["lag_sec"], d["median_retention"], marker="o", color=color, label=f"{set_name} median")
            ax.fill_between(
                d["lag_sec"].to_numpy(dtype="float64"),
                d["q25_retention"].to_numpy(dtype="float64"),
                d["q75_retention"].to_numpy(dtype="float64"),
                color=color,
                alpha=0.18,
                linewidth=0,
            )
        ax.axhline(0.5, color="#222222", linewidth=0.7)
        ax.axvline(cfg.long_lag_sec, color="#777777", linestyle="--", linewidth=0.8)
        ax.set_xlabel("lag (s)")
        ax.set_ylabel("per-Ob retention")
        ax.set_title("3032b retention decay across lags")
        ax.legend(frameon=False)
        fig.tight_layout()
        fig.savefig(FIG / "retention_decay_by_lag.png", dpi=180)
        plt.close(fig)

    if not composition.empty:
        comp = composition.set_index("spectral_set")
        cols = [c for c in COARSE_STATE_ORDER if c in comp.columns]
        if cols:
            fig, ax = plt.subplots(figsize=(7.4, 4.2))
            bottom = np.zeros(len(comp))
            x = np.arange(len(comp))
            colors = {"quiet": "#4c78a8", "outward": "#f58518", "mobile": "#e45756", "other": "#72b7b2"}
            for col in cols:
                vals = comp[col].to_numpy(dtype="float64")
                ax.bar(x, vals, bottom=bottom, color=colors.get(col, "#888888"), label=col)
                bottom += vals
            ax.set_xticks(x)
            ax.set_xticklabels(comp.index)
            ax.set_ylabel("fraction")
            ax.set_title("3032b spectral sets vs 3013 coarse states")
            ax.legend(frameon=False, ncol=4, fontsize=8)
            fig.tight_layout()
            fig.savefig(FIG / "coarse_state_composition.png", dpi=180)
            plt.close(fig)

    if len(df) and {"r_rms_z", "density_rms_z"}.issubset(df.columns):
        plot_df = df[df["spectral_set"].isin(SET_ORDER)].copy()
        if len(plot_df) > cfg.scatter_sample:
            plot_df = plot_df.sample(cfg.scatter_sample, random_state=RNG_SEED)
        fig, ax = plt.subplots(figsize=(7.0, 5.6))
        colors = {"low": "#4c78a8", "high": "#f58518"}
        for set_name, d in plot_df.groupby("spectral_set", sort=True):
            ax.scatter(
                d["r_rms_z"],
                d["density_rms_z"],
                s=5,
                alpha=0.18,
                color=colors.get(str(set_name), "#888888"),
                label=str(set_name),
                linewidths=0,
            )
        ax.set_xlabel("r_rms within-Ob robust z")
        ax.set_ylabel("density_rms within-Ob robust z")
        ax.set_title("3032b compact-density axis")
        ax.legend(frameon=False, markerscale=3)
        fig.tight_layout()
        fig.savefig(FIG / "compact_density_axis_scatter.png", dpi=180)
        plt.close(fig)


def write_summary(
    decision: pd.DataFrame,
    emission: pd.DataFrame,
    residence: pd.DataFrame,
    lag_summary: pd.DataFrame,
    overlap: pd.DataFrame,
    composition: pd.DataFrame,
    cfg: RunConfig,
) -> None:
    rec = decision.iloc[0]
    emission_view = emission[
        [
            "variable",
            "role",
            "delta_high_minus_low_z",
            "median_ob_delta_z",
            "frac_ob_same_sign",
            "frac_ob_abs_delta_ge_0p5",
        ]
    ].head(12)
    summary = f"""# 3032b EGRT State-Meaning and Residence Audit

## Scope

3032 found a positive transfer-operator partition. 3032b audits whether that partition should be treated as a meaningful metastable state or as a shallow consequence of smooth slow-variable persistence.

## EGRT Node

| field | value |
| --- | --- |
| node_id | 3032b_state_meaning_residence_audit |
| parent | 3032_transfer_operator_metastability |
| node_type | mechanism |
| decision | {rec['eg_rt_decision']} |
| recommended next node | {rec['recommended_next_node']} |
| boundary reading | {rec['boundary_reading']} |

## Decision Metrics

{dataframe_to_markdown(decision)}

## Emission Meaning

{dataframe_to_markdown(emission_view)}

## Residence Summary

{dataframe_to_markdown(residence)}

## Retention Decay

{dataframe_to_markdown(lag_summary)}

## Coarse-State Overlap

{dataframe_to_markdown(overlap)}

## Coarse-State Composition

{dataframe_to_markdown(composition)}

## Outputs

- `Output/3032b/3032b_egrt_node.json`
- `Output/3032b/tables/emission_effect_summary.csv`
- `Output/3032b/tables/emission_effect_by_ob.csv`
- `Output/3032b/tables/residence_runs.csv`
- `Output/3032b/tables/residence_summary.csv`
- `Output/3032b/tables/lag_retention_by_ob.csv`
- `Output/3032b/tables/lag_retention_summary.csv`
- `Output/3032b/tables/two_state_transition_summary.csv`
- `Output/3032b/tables/coarse_state_overlap.csv`
- `Output/3032b/tables/egrt_decision_summary.csv`
- `Output/3032b/figures/emission_effects_high_minus_low.png`
- `Output/3032b/figures/residence_duration_by_set.png`
- `Output/3032b/figures/retention_decay_by_lag.png`
- `Output/3032b/figures/coarse_state_composition.png`
- `Output/3032b/figures/compact_density_axis_scatter.png`

## Interpretation Boundary

3032b separates two claims. The partition can be meaningful as a compact-density organization axis even if it is not a deep metastable basin. Strong residence would justify a more ambitious state-process model. Shallow residence redirects the branch toward null-model auditing or a narrower descriptive claim.
"""
    (OUT / "3032b_summary.md").write_text(summary, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quick", action="store_true", help="Use fewer sampled points in scatter figures.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cfg = RunConfig(scatter_sample=15000 if args.quick else RunConfig.scatter_sample)
    ensure_dirs()
    parent_decision = read_decision()
    if str(parent_decision.get("eg_rt_decision", "")) != "support_stochastic_metastability_branch":
        raise RuntimeError("3032 did not support the metastability branch; 3032b is not routed.")
    variables = candidate_variables(parent_decision)
    best_partition_id = str(parent_decision.get("best_partition_id", ""))
    edges = read_edges()
    mapping = read_mapping(best_partition_id)

    raw = read_input(variables)
    standardized = standardize_columns(raw, sorted(set(EMISSION_VARIABLES + variables)))
    df = assign_cells_from_edges(standardized, variables, edges, cfg.n_bins)
    df = attach_partition_labels(df, mapping)
    df = df[df["spectral_set"].isin(SET_ORDER)].reset_index(drop=True)

    emission, emission_by_ob = emission_summary(df, variables)
    runs = residence_runs(df)
    res_summary = residence_summary(runs, cfg)
    lag_detail, lag_summary = lag_retention(df, cfg)
    two_state = two_state_transition_summary(df, cfg.lags_sec)
    overlap, composition = coarse_overlap(df)
    decision = decision_summary(parent_decision, best_partition_id, emission, res_summary, lag_summary, overlap, cfg)

    df[["dataset", "ob", "t", "ulam_cell", "spectral_set"]].to_csv(PROC / "frame_spectral_labels.csv", index=False)
    emission.to_csv(TAB / "emission_effect_summary.csv", index=False)
    emission.to_csv(PROC / "emission_effect_summary.csv", index=False)
    emission_by_ob.to_csv(TAB / "emission_effect_by_ob.csv", index=False)
    runs.to_csv(TAB / "residence_runs.csv", index=False)
    res_summary.to_csv(TAB / "residence_summary.csv", index=False)
    lag_detail.to_csv(TAB / "lag_retention_by_ob.csv", index=False)
    lag_summary.to_csv(TAB / "lag_retention_summary.csv", index=False)
    two_state.to_csv(TAB / "two_state_transition_summary.csv", index=False)
    overlap.to_csv(TAB / "coarse_state_overlap.csv", index=False)
    composition.to_csv(TAB / "coarse_state_composition.csv", index=False)
    decision.to_csv(TAB / "egrt_decision_summary.csv", index=False)
    decision.to_csv(PROC / "egrt_decision_summary.csv", index=False)

    write_node_schema(decision, cfg)
    make_figures(emission, res_summary, lag_summary, composition, df, cfg)
    write_summary(decision, emission, res_summary, lag_summary, overlap, composition, cfg)
    print(decision.to_string(index=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
