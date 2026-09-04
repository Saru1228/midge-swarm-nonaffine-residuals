#!/usr/bin/env python3
"""Experiment 3032: EGRT transfer-operator metastability node.

3030 routed the 303x attractor branch away from deterministic-attractor
tests and toward stochastic/metastable recurrence. This node asks whether the
slow variables selected by 3030 form reproducible almost-invariant sets.
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

RAW_PATH = ROOT / "Output" / "3001" / "processed" / "geometric_center_observables_all.csv"
DECISION_3030 = ROOT / "Output" / "3030" / "tables" / "egrt_decision_summary.csv"
VAR_SUMMARY_3030 = ROOT / "Output" / "3030" / "tables" / "variable_evidence_summary.csv"
OUT = ROOT / "Output" / "3032"
FIG = OUT / "figures"
TAB = OUT / "tables"
PROC = OUT / "processed"

DEFAULT_SLOW_VARIABLES = ["r_rms", "density_rms", "anisotropy"]
COARSE_STATE_ORDER = ["quiet", "outward", "mobile", "other"]
SET_ORDER = ["low", "high"]
RNG_SEED = 3032

try:
    from run_3013_quiet_mobile_first_passage import (  # type: ignore
        RunConfig as BasinConfig,
        classify_states,
        median_dt as basin_median_dt,
    )

    HAVE_3013 = True
except Exception:
    HAVE_3013 = False
    BasinConfig = None  # type: ignore
    classify_states = None  # type: ignore
    basin_median_dt = None  # type: ignore


@dataclass(frozen=True)
class RunConfig:
    lag_sec: float = 0.10
    n_bins: int = 4
    max_partitions: int = 4
    coverage_gate: float = 0.98
    eigenvalue_gate: float = 0.85
    pooled_retention_gate: float = 0.80
    retention_lift_gate: float = 0.20
    ob_q25_retention_gate: float = 0.65
    ob_positive_lift_fraction_gate: float = 0.70
    min_set_mass: float = 0.08
    min_origin_count_by_ob: int = 20
    scatter_sample: int = 60000


def ensure_dirs() -> None:
    for path in (OUT, FIG, TAB, PROC):
        path.mkdir(parents=True, exist_ok=True)


def dataframe_to_markdown(df: pd.DataFrame, max_rows: int | None = None) -> str:
    if max_rows is not None:
        df = df.head(max_rows)
    if df.empty:
        return "_No rows._"
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df.iterrows():
        vals: list[str] = []
        for col in cols:
            val = row[col]
            if isinstance(val, float):
                vals.append("NA" if not np.isfinite(val) else f"{val:.4g}")
            else:
                vals.append(str(val))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def finite_median(values: Iterable[float]) -> float:
    arr = np.asarray(list(values), dtype="float64")
    arr = arr[np.isfinite(arr)]
    return float(np.median(arr)) if arr.size else math.nan


def finite_quantile(values: Iterable[float], q: float) -> float:
    arr = np.asarray(list(values), dtype="float64")
    arr = arr[np.isfinite(arr)]
    return float(np.quantile(arr, q)) if arr.size else math.nan


def finite_fraction(values: Iterable[bool]) -> float:
    arr = np.asarray(list(values), dtype=object)
    arr = arr[pd.notna(arr)]
    return float(np.mean(arr.astype(bool))) if arr.size else math.nan


def safe_float(value: object) -> float:
    try:
        out = float(value)
    except Exception:
        return math.nan
    return out if np.isfinite(out) else math.nan


def weighted_median(values: np.ndarray, weights: np.ndarray) -> float:
    values = np.asarray(values, dtype="float64")
    weights = np.asarray(weights, dtype="float64")
    mask = np.isfinite(values) & np.isfinite(weights) & (weights > 0)
    if not np.any(mask):
        return math.nan
    order = np.argsort(values[mask])
    vals = values[mask][order]
    w = weights[mask][order]
    cutoff = 0.5 * float(np.sum(w))
    idx = int(np.searchsorted(np.cumsum(w), cutoff, side="left"))
    return float(vals[min(idx, len(vals) - 1)])


def robust_z(x: pd.Series) -> np.ndarray:
    arr = pd.to_numeric(x, errors="coerce").to_numpy(dtype="float64")
    med = float(np.nanmedian(arr))
    q25 = float(np.nanquantile(arr, 0.25))
    q75 = float(np.nanquantile(arr, 0.75))
    scale = (q75 - q25) / 1.349 if np.isfinite(q75 - q25) and (q75 - q25) > 0 else math.nan
    if not np.isfinite(scale) or scale <= 1e-12:
        scale = float(np.nanstd(arr))
    if not np.isfinite(scale) or scale <= 1e-12:
        return np.full(arr.shape, np.nan, dtype="float64")
    return (arr - med) / scale


def median_dt(d: pd.DataFrame) -> float:
    dt = safe_float(d["dt"].median(skipna=True)) if "dt" in d.columns else math.nan
    if not np.isfinite(dt) or dt <= 0:
        t = pd.to_numeric(d["t"], errors="coerce").to_numpy(dtype="float64")
        dt = safe_float(np.nanmedian(np.diff(t)))
    return dt


def strip_candidate_name(name: str) -> str:
    name = str(name).strip()
    for prefix in ("raw_", "stable_"):
        if name.startswith(prefix):
            return name[len(prefix) :]
    return name


def read_3030_candidates() -> list[str]:
    candidates: list[str] = []
    if DECISION_3030.exists():
        decision = pd.read_csv(DECISION_3030)
        if not decision.empty and "metastability_candidate_variables" in decision.columns:
            raw_value = str(decision["metastability_candidate_variables"].iloc[0])
            if raw_value and raw_value.lower() != "nan":
                candidates.extend(strip_candidate_name(x) for x in raw_value.split(",") if str(x).strip())
    if not candidates and VAR_SUMMARY_3030.exists():
        summary = pd.read_csv(VAR_SUMMARY_3030)
        if "metastability_like_support" in summary.columns:
            mask = summary["metastability_like_support"].astype(str).str.lower().isin(["true", "1"])
            candidates.extend(strip_candidate_name(x) for x in summary.loc[mask, "variable"].tolist())
    ordered = [x for x in DEFAULT_SLOW_VARIABLES if x in set(candidates)]
    ordered.extend(x for x in candidates if x not in ordered)
    return ordered if len(ordered) >= 2 else list(DEFAULT_SLOW_VARIABLES)


def read_input(variables: list[str]) -> pd.DataFrame:
    if not RAW_PATH.exists():
        raise FileNotFoundError(f"Missing input table: {RAW_PATH}")
    required = [
        "dataset",
        "ob",
        "t",
        "dt",
        "center_speed",
        "radial_velocity_mean",
        "frac_outward",
        *variables,
    ]
    df = pd.read_csv(RAW_PATH, usecols=lambda c: c in set(required))
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in {RAW_PATH}: {missing}")
    for col in ["ob", "t", "dt", "center_speed", "radial_velocity_mean", "frac_outward", *variables]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.sort_values(["ob", "t"], kind="mergesort").reset_index(drop=True)
    return df


def standardize_within_ob(df: pd.DataFrame, variables: list[str]) -> pd.DataFrame:
    out = []
    for (_, _dataset), d in df.groupby(["ob", "dataset"], sort=True):
        d = d.copy()
        for var in variables:
            d[f"{var}_z"] = robust_z(d[var])
        out.append(d)
    zcols = [f"{x}_z" for x in variables]
    result = pd.concat(out, ignore_index=True)
    result = result.dropna(subset=zcols).reset_index(drop=True)
    return result


def assign_ulam_cells(df: pd.DataFrame, variables: list[str], cfg: RunConfig) -> tuple[pd.DataFrame, dict[str, list[float]]]:
    df = df.copy()
    edges: dict[str, list[float]] = {}
    cell = np.zeros(len(df), dtype="int64")
    for var in variables:
        zcol = f"{var}_z"
        vals = df[zcol].to_numpy(dtype="float64")
        qs = np.nanquantile(vals[np.isfinite(vals)], np.linspace(0, 1, cfg.n_bins + 1)[1:-1])
        qs = np.asarray(qs, dtype="float64")
        edges[var] = [float(x) for x in qs]
        bins = np.searchsorted(qs, vals, side="right").astype("int64")
        bins = np.clip(bins, 0, cfg.n_bins - 1)
        df[f"{var}_bin"] = bins
        cell = cell * cfg.n_bins + bins
    df["ulam_cell"] = cell
    return df, edges


def decode_cell(cell_id: int, n_vars: int, n_bins: int) -> list[int]:
    out = [0] * n_vars
    value = int(cell_id)
    for i in range(n_vars - 1, -1, -1):
        out[i] = value % n_bins
        value //= n_bins
    return out


def build_cell_summary(df: pd.DataFrame, variables: list[str], cfg: RunConfig) -> pd.DataFrame:
    rows = []
    total = len(df)
    grouped = df.groupby("ulam_cell", sort=True)
    for cell_id, d in grouped:
        row: dict[str, object] = {
            "ulam_cell": int(cell_id),
            "frame_count": int(len(d)),
            "occupancy_fraction": float(len(d) / total) if total else math.nan,
        }
        for var, bin_id in zip(variables, decode_cell(int(cell_id), len(variables), cfg.n_bins)):
            row[f"{var}_bin"] = int(bin_id)
            row[f"{var}_median"] = float(np.nanmedian(d[var]))
            row[f"{var}_z_median"] = float(np.nanmedian(d[f"{var}_z"]))
        rows.append(row)
    return pd.DataFrame(rows).sort_values("ulam_cell").reset_index(drop=True)


def transition_counts(df: pd.DataFrame, active_cells: list[int], cfg: RunConfig) -> tuple[np.ndarray, pd.DataFrame]:
    idx = {cell: i for i, cell in enumerate(active_cells)}
    counts = np.zeros((len(active_cells), len(active_cells)), dtype="float64")
    rows = []
    for (ob, dataset), d in df.groupby(["ob", "dataset"], sort=True):
        d = d.sort_values("t").reset_index(drop=True)
        dt = median_dt(d)
        if not np.isfinite(dt) or dt <= 0:
            continue
        lag_frames = max(1, int(round(cfg.lag_sec / dt)))
        actual_lag = float(lag_frames * dt)
        cells = d["ulam_cell"].to_numpy(dtype="int64")
        if len(cells) <= lag_frames:
            continue
        origin = cells[:-lag_frames]
        dest = cells[lag_frames:]
        local_counts = np.zeros_like(counts)
        for a, b in zip(origin, dest):
            ai = idx.get(int(a))
            bi = idx.get(int(b))
            if ai is None or bi is None:
                continue
            counts[ai, bi] += 1.0
            local_counts[ai, bi] += 1.0
        rows.append(
            {
                "ob": int(ob),
                "dataset": str(dataset),
                "dt_sec": float(dt),
                "lag_frames": int(lag_frames),
                "actual_lag_sec": actual_lag,
                "transition_count": int(local_counts.sum()),
            }
        )
    return counts, pd.DataFrame(rows)


def row_stochastic(counts: np.ndarray) -> np.ndarray:
    counts = np.asarray(counts, dtype="float64")
    p = np.zeros_like(counts, dtype="float64")
    for i in range(counts.shape[0]):
        row_sum = float(np.sum(counts[i, :]))
        if row_sum > 0:
            p[i, :] = counts[i, :] / row_sum
        else:
            p[i, i] = 1.0
    return p


def stationary_distribution(p: np.ndarray, max_iter: int = 20000, tol: float = 1e-14) -> np.ndarray:
    n = p.shape[0]
    pi = np.ones(n, dtype="float64") / n
    for _ in range(max_iter):
        new_pi = pi @ p
        if np.max(np.abs(new_pi - pi)) < tol:
            return new_pi / np.sum(new_pi)
        pi = new_pi
    return pi / np.sum(pi)


def implied_timescale(eigenvalue_abs: float, lag_sec: float) -> float:
    if not np.isfinite(eigenvalue_abs) or eigenvalue_abs <= 0 or eigenvalue_abs >= 1:
        return math.inf if np.isfinite(eigenvalue_abs) and eigenvalue_abs >= 1 else math.nan
    return float(-lag_sec / math.log(eigenvalue_abs))


def set_retention(p: np.ndarray, pi: np.ndarray, mask: np.ndarray) -> dict[str, float]:
    mask = np.asarray(mask, dtype=bool)
    mass = float(np.sum(pi[mask]))
    if mass <= 0:
        return {"mass": math.nan, "retention": math.nan, "lift": math.nan, "exit_probability": math.nan}
    stay = float(np.sum(pi[mask] * np.sum(p[np.ix_(mask, mask)], axis=1)))
    retention = stay / mass
    return {
        "mass": mass,
        "retention": retention,
        "lift": retention - mass,
        "exit_probability": 1.0 - retention,
    }


def describe_axis(
    cell_summary: pd.DataFrame,
    active_cells: list[int],
    pi: np.ndarray,
    variables: list[str],
    set_mask: np.ndarray,
) -> str:
    lookup = cell_summary.set_index("ulam_cell")
    diffs = []
    for var in variables:
        z = np.array([safe_float(lookup.loc[cell, f"{var}_z_median"]) for cell in active_cells], dtype="float64")
        high = set_mask
        low = ~set_mask
        high_mean = float(np.average(z[high], weights=pi[high])) if np.any(high) else math.nan
        low_mean = float(np.average(z[low], weights=pi[low])) if np.any(low) else math.nan
        diffs.append((var, high_mean - low_mean, high_mean, low_mean))
    diffs = sorted(diffs, key=lambda x: abs(x[1]) if np.isfinite(x[1]) else -1, reverse=True)
    parts = []
    for var, diff, _high_mean, _low_mean in diffs[:3]:
        direction = "higher" if diff >= 0 else "lower"
        parts.append(f"high set {direction} {var} (delta_z={diff:.3g})")
    return "; ".join(parts)


def spectral_partitions(
    p: np.ndarray,
    pi: np.ndarray,
    active_cells: list[int],
    cell_summary: pd.DataFrame,
    variables: list[str],
    cfg: RunConfig,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    eigvals, eigvecs = np.linalg.eig(p)
    order = sorted(range(len(eigvals)), key=lambda i: (eigvals[i].real, abs(eigvals[i])), reverse=True)
    eigen_rows = []
    for rank, i in enumerate(order[: min(len(order), 20)], start=1):
        val = eigvals[i]
        eigen_rows.append(
            {
                "eigen_rank": rank,
                "eigenvalue_real": float(val.real),
                "eigenvalue_imag": float(val.imag),
                "eigenvalue_abs": float(abs(val)),
                "implied_timescale_sec": implied_timescale(float(abs(val)), cfg.lag_sec),
            }
        )
    eigen_table = pd.DataFrame(eigen_rows)

    summary_rows = []
    mapping_rows = []
    chosen = 0
    for rank, i in enumerate(order, start=1):
        if chosen >= cfg.max_partitions:
            break
        val = eigvals[i]
        if rank == 1:
            continue
        vec = np.asarray(eigvecs[:, i].real, dtype="float64")
        if np.nanstd(vec) <= 1e-12:
            continue
        cut = weighted_median(vec, pi)
        if not np.isfinite(cut):
            continue
        high_mask = vec > cut
        low_mask = ~high_mask
        if not np.any(high_mask) or not np.any(low_mask):
            continue
        high_metrics = set_retention(p, pi, high_mask)
        low_metrics = set_retention(p, pi, low_mask)
        if high_metrics["mass"] < cfg.min_set_mass or low_metrics["mass"] < cfg.min_set_mass:
            continue
        chosen += 1
        partition_id = f"eig{rank}"
        summary_rows.append(
            {
                "partition_id": partition_id,
                "eigen_rank": int(rank),
                "eigenvalue_real": float(val.real),
                "eigenvalue_imag": float(val.imag),
                "eigenvalue_abs": float(abs(val)),
                "implied_timescale_sec": implied_timescale(float(abs(val)), cfg.lag_sec),
                "low_mass": low_metrics["mass"],
                "high_mass": high_metrics["mass"],
                "low_pooled_retention": low_metrics["retention"],
                "high_pooled_retention": high_metrics["retention"],
                "low_retention_lift": low_metrics["lift"],
                "high_retention_lift": high_metrics["lift"],
                "min_pooled_retention": min(low_metrics["retention"], high_metrics["retention"]),
                "min_retention_lift": min(low_metrics["lift"], high_metrics["lift"]),
                "low_exit_probability": low_metrics["exit_probability"],
                "high_exit_probability": high_metrics["exit_probability"],
                "n_cells_low": int(np.sum(low_mask)),
                "n_cells_high": int(np.sum(high_mask)),
                "interpretive_axis": describe_axis(cell_summary, active_cells, pi, variables, high_mask),
            }
        )
        for set_name, mask in [("low", low_mask), ("high", high_mask)]:
            for cell, value, mass in zip(active_cells, vec, pi):
                in_set = bool(mask[active_cells.index(cell)])
                if not in_set:
                    continue
                mapping_rows.append(
                    {
                        "partition_id": partition_id,
                        "ulam_cell": int(cell),
                        "spectral_set": set_name,
                        "eigenvector_value": float(value),
                        "stationary_mass": float(mass),
                    }
                )
    return eigen_table, pd.DataFrame(summary_rows), pd.DataFrame(mapping_rows)


def label_sequence(cells: np.ndarray, mapping: dict[int, str]) -> np.ndarray:
    return np.array([mapping.get(int(cell), "unmapped") for cell in cells], dtype=object)


def run_lengths(labels: np.ndarray, dt: float) -> list[dict[str, float | str | int]]:
    rows: list[dict[str, float | str | int]] = []
    if len(labels) == 0:
        return rows
    start = 0
    current = labels[0]
    for i in range(1, len(labels) + 1):
        if i < len(labels) and labels[i] == current:
            continue
        if current != "unmapped":
            length = i - start
            rows.append({"spectral_set": str(current), "run_frames": int(length), "run_duration_sec": float(length * dt)})
        if i < len(labels):
            start = i
            current = labels[i]
    return rows


def partition_retention_by_ob(df: pd.DataFrame, mapping: pd.DataFrame, cfg: RunConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    retention_rows = []
    residence_rows = []
    for partition_id, dmap in mapping.groupby("partition_id", sort=True):
        cell_to_set = {int(r.ulam_cell): str(r.spectral_set) for r in dmap.itertuples(index=False)}
        for (ob, dataset), d in df.groupby(["ob", "dataset"], sort=True):
            d = d.sort_values("t").reset_index(drop=True)
            dt = median_dt(d)
            if not np.isfinite(dt) or dt <= 0:
                continue
            lag_frames = max(1, int(round(cfg.lag_sec / dt)))
            labels = label_sequence(d["ulam_cell"].to_numpy(dtype="int64"), cell_to_set)
            known = labels != "unmapped"
            for set_name in SET_ORDER:
                mass = float(np.mean(labels == set_name)) if len(labels) else math.nan
                if len(labels) <= lag_frames:
                    continue
                origin = labels[:-lag_frames]
                dest = labels[lag_frames:]
                mask = origin == set_name
                origin_count = int(np.sum(mask))
                retained = int(np.sum(mask & (dest == set_name)))
                retention = float(retained / origin_count) if origin_count else math.nan
                lift = retention - mass if np.isfinite(retention) and np.isfinite(mass) else math.nan
                retention_rows.append(
                    {
                        "partition_id": str(partition_id),
                        "ob": int(ob),
                        "dataset": str(dataset),
                        "spectral_set": set_name,
                        "mass": mass,
                        "known_fraction": float(np.mean(known)) if len(labels) else math.nan,
                        "lag_frames": int(lag_frames),
                        "actual_lag_sec": float(lag_frames * dt),
                        "origin_count": origin_count,
                        "retained_count": retained,
                        "retention": retention,
                        "retention_lift": lift,
                    }
                )
            for row in run_lengths(labels, dt):
                row.update({"partition_id": str(partition_id), "ob": int(ob), "dataset": str(dataset)})
                residence_rows.append(row)
    return pd.DataFrame(retention_rows), pd.DataFrame(residence_rows)


def summarize_partitions(summary: pd.DataFrame, retention: pd.DataFrame, residence: pd.DataFrame, cfg: RunConfig) -> pd.DataFrame:
    if summary.empty:
        return summary
    rows = []
    for row in summary.itertuples(index=False):
        d = retention[(retention["partition_id"] == row.partition_id) & (retention["origin_count"] >= cfg.min_origin_count_by_ob)]
        runs = residence[residence["partition_id"] == row.partition_id] if not residence.empty else pd.DataFrame()
        rows.append(
            {
                **row._asdict(),
                "median_ob_retention": finite_median(d["retention"]) if not d.empty else math.nan,
                "q25_ob_retention": finite_quantile(d["retention"], 0.25) if not d.empty else math.nan,
                "median_ob_retention_lift": finite_median(d["retention_lift"]) if not d.empty else math.nan,
                "frac_ob_set_lift_positive": finite_fraction(d["retention_lift"] > 0) if not d.empty else math.nan,
                "median_residence_sec": finite_median(runs["run_duration_sec"]) if not runs.empty else math.nan,
                "q75_residence_sec": finite_quantile(runs["run_duration_sec"], 0.75) if not runs.empty else math.nan,
                "score": (
                    safe_float(row.min_retention_lift)
                    + safe_float(row.min_pooled_retention)
                    + finite_quantile(d["retention"], 0.25)
                    if not d.empty
                    else math.nan
                ),
            }
        )
    return pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)


def add_coarse_states(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["coarse_state"] = "unavailable"
    if not HAVE_3013:
        return df
    basin_config = BasinConfig()  # type: ignore
    for (ob, dataset), idx in df.groupby(["ob", "dataset"], sort=True).groups.items():
        d = df.loc[idx].sort_values("t").copy()
        try:
            state, _thresholds = classify_states(d, basin_config)  # type: ignore
        except Exception:
            state = np.full(len(d), "unavailable", dtype=object)
        df.loc[d.index, "coarse_state"] = state
    return df


def entropy(prob: np.ndarray) -> float:
    prob = np.asarray(prob, dtype="float64")
    prob = prob[(prob > 0) & np.isfinite(prob)]
    return float(-np.sum(prob * np.log(prob))) if prob.size else 0.0


def overlap_statistics(table: pd.DataFrame) -> dict[str, float]:
    obs = table.to_numpy(dtype="float64")
    n = float(obs.sum())
    if n <= 0:
        return {"n": 0.0, "nmi": math.nan, "cramers_v": math.nan}
    pxy = obs / n
    px = pxy.sum(axis=1)
    py = pxy.sum(axis=0)
    denom = px[:, None] * py[None, :]
    mask = (pxy > 0) & (denom > 0)
    mi = float(np.sum(pxy[mask] * np.log(pxy[mask] / denom[mask])))
    hx = entropy(px)
    hy = entropy(py)
    nmi = mi / math.sqrt(hx * hy) if hx > 0 and hy > 0 else math.nan
    expected = np.outer(obs.sum(axis=1), obs.sum(axis=0)) / n
    valid = expected > 0
    chi2 = float(np.sum((obs[valid] - expected[valid]) ** 2 / expected[valid]))
    denom_v = n * max(1, min(obs.shape[0] - 1, obs.shape[1] - 1))
    cramers_v = math.sqrt(chi2 / denom_v) if denom_v > 0 else math.nan
    return {"n": n, "nmi": nmi, "cramers_v": cramers_v}


def interpret_best_partition(
    df: pd.DataFrame,
    mapping: pd.DataFrame,
    best_partition_id: str,
    variables: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    dmap = mapping[mapping["partition_id"] == best_partition_id]
    cell_to_set = {int(r.ulam_cell): str(r.spectral_set) for r in dmap.itertuples(index=False)}
    out = df.copy()
    out["spectral_set"] = label_sequence(out["ulam_cell"].to_numpy(dtype="int64"), cell_to_set)
    out = add_coarse_states(out)

    desc_rows = []
    for set_name, d in out[out["spectral_set"].isin(SET_ORDER)].groupby("spectral_set", sort=True):
        row: dict[str, object] = {
            "spectral_set": str(set_name),
            "n_frames": int(len(d)),
            "occupancy_fraction": float(len(d) / len(out)) if len(out) else math.nan,
            "median_center_speed": float(np.nanmedian(d["center_speed"])),
            "median_frac_outward": float(np.nanmedian(d["frac_outward"])),
            "median_radial_velocity_mean": float(np.nanmedian(d["radial_velocity_mean"])),
        }
        for var in variables:
            row[f"median_{var}"] = float(np.nanmedian(d[var]))
            row[f"median_{var}_z"] = float(np.nanmedian(d[f"{var}_z"]))
        desc_rows.append(row)
    desc = pd.DataFrame(desc_rows).sort_values("spectral_set").reset_index(drop=True)

    if "coarse_state" in out.columns:
        ctab = pd.crosstab(out["spectral_set"], out["coarse_state"])
        ctab = ctab.reindex(index=SET_ORDER, columns=COARSE_STATE_ORDER + ["unavailable"], fill_value=0)
        ctab = ctab.loc[:, (ctab.sum(axis=0) > 0)]
        stats = overlap_statistics(ctab)
        overlap = pd.DataFrame(
            [
                {
                    "partition_id": best_partition_id,
                    "n_frames": int(stats["n"]),
                    "normalized_mutual_information": stats["nmi"],
                    "cramers_v": stats["cramers_v"],
                    "coarse_state_source": "3013 classifier" if HAVE_3013 else "unavailable",
                }
            ]
        )
        composition = ctab.div(ctab.sum(axis=1).replace(0, np.nan), axis=0).reset_index()
    else:
        overlap = pd.DataFrame()
        composition = pd.DataFrame()
    return desc, overlap, composition


def decision_summary(
    partitions: pd.DataFrame,
    eigen_table: pd.DataFrame,
    active_coverage: float,
    n_active_cells: int,
    n_total_cells: int,
    variables: list[str],
    cfg: RunConfig,
) -> pd.DataFrame:
    if partitions.empty:
        rec = {
            "node_id": "3032_transfer_operator_metastability",
            "eg_rt_decision": "retire_metastability_branch",
            "recommended_next_node": "pause or revise slow-variable state space",
            "boundary_reading": "No admissible nontrivial spectral partition passed the minimum set-mass gate.",
            "active_coverage": active_coverage,
            "n_active_cells": n_active_cells,
            "n_total_cells": n_total_cells,
            "candidate_variables": ", ".join(variables),
        }
        return pd.DataFrame([rec])

    best = partitions.iloc[0]
    top_nontrivial = partitions.sort_values("eigen_rank").iloc[0]
    pass_gate = (
        active_coverage >= cfg.coverage_gate
        and safe_float(top_nontrivial["eigenvalue_real"]) >= cfg.eigenvalue_gate
        and safe_float(best["min_pooled_retention"]) >= cfg.pooled_retention_gate
        and safe_float(best["min_retention_lift"]) >= cfg.retention_lift_gate
        and safe_float(best["q25_ob_retention"]) >= cfg.ob_q25_retention_gate
        and safe_float(best["frac_ob_set_lift_positive"]) >= cfg.ob_positive_lift_fraction_gate
    )
    pooled_only = (
        active_coverage >= cfg.coverage_gate
        and safe_float(top_nontrivial["eigenvalue_real"]) >= cfg.eigenvalue_gate
        and safe_float(best["min_pooled_retention"]) >= cfg.pooled_retention_gate
        and safe_float(best["min_retention_lift"]) >= cfg.retention_lift_gate
    )
    if pass_gate:
        decision = "support_stochastic_metastability_branch"
        next_node = "3032b state-meaning and residence audit"
        boundary = "Almost-invariant slow-variable sets are reproducible enough to extend, but this supports stochastic macroscopic organization rather than deterministic center-speed attractor geometry."
    elif pooled_only:
        decision = "boundary_pooled_metastability_not_cross_ob_stable"
        next_node = "3032b robustness or variable revision"
        boundary = "Pooled transfer-operator structure is strong, but cross-Ob retention consistency is below gate."
    else:
        decision = "retire_metastability_branch"
        next_node = "pause 303x attractor narrative or try a different observable basis"
        boundary = "The slow-variable Ulam model did not pass the almost-invariant-set gates."

    rec = {
        "node_id": "3032_transfer_operator_metastability",
        "candidate_variables": ", ".join(variables),
        "lag_sec": cfg.lag_sec,
        "n_bins": cfg.n_bins,
        "n_total_cells": n_total_cells,
        "n_active_cells": n_active_cells,
        "active_coverage": active_coverage,
        "top_nontrivial_eigenvalue_real": safe_float(top_nontrivial["eigenvalue_real"]),
        "top_nontrivial_implied_timescale_sec": safe_float(top_nontrivial["implied_timescale_sec"]),
        "best_partition_id": str(best["partition_id"]),
        "best_partition_eigen_rank": int(best["eigen_rank"]),
        "best_partition_min_pooled_retention": safe_float(best["min_pooled_retention"]),
        "best_partition_min_retention_lift": safe_float(best["min_retention_lift"]),
        "best_partition_q25_ob_retention": safe_float(best["q25_ob_retention"]),
        "best_partition_frac_ob_set_lift_positive": safe_float(best["frac_ob_set_lift_positive"]),
        "best_partition_median_residence_sec": safe_float(best["median_residence_sec"]),
        "pass_gate": bool(pass_gate),
        "pooled_only_boundary": bool(pooled_only and not pass_gate),
        "eg_rt_decision": decision,
        "recommended_next_node": next_node,
        "boundary_reading": boundary,
    }
    if not eigen_table.empty:
        rec["spectrum_top5_real"] = ", ".join(f"{x:.4g}" for x in eigen_table["eigenvalue_real"].head(5))
    return pd.DataFrame([rec])


def write_node_schema(decision: pd.DataFrame, cfg: RunConfig) -> None:
    rec = decision.iloc[0].to_dict()
    node = {
        "node_id": "3032_transfer_operator_metastability",
        "series": "303x",
        "node_type": "mechanism",
        "parent_node": "3030_attractor_evidence_screen",
        "question": "Do the 3030 slow-variable candidates form reproducible almost-invariant sets under an empirical transfer operator?",
        "competing_interpretations": [
            "stochastic/metastable macroscopic organization",
            "coarse discretization artifact",
            "Ob-specific persistence without cross-sample support",
        ],
        "input_artifacts": [
            "Output/3001/processed/geometric_center_observables_all.csv",
            "Output/3030/tables/egrt_decision_summary.csv",
            "Output/3030/tables/variable_evidence_summary.csv",
        ],
        "method": [
            "within-Ob robust standardization of 3030 slow-variable candidates",
            f"{cfg.n_bins}-bin quantile Ulam discretization",
            f"pooled empirical transition operator at lag {cfg.lag_sec:.3g}s",
            "dominant right-eigenvector spectral partitions",
            "retention-lift comparison against occupancy baseline",
            "cross-Ob retention and residence diagnostics",
            "interpretive overlap with the 3013 quiet/outward/mobile/other classifier",
        ],
        "pass_gate": {
            "active_coverage": f">= {cfg.coverage_gate}",
            "top_nontrivial_eigenvalue_real": f">= {cfg.eigenvalue_gate}",
            "min_pooled_retention": f">= {cfg.pooled_retention_gate}",
            "min_retention_lift": f">= {cfg.retention_lift_gate}",
            "q25_ob_retention": f">= {cfg.ob_q25_retention_gate}",
            "frac_ob_set_lift_positive": f">= {cfg.ob_positive_lift_fraction_gate}",
        },
        "next_if_pass": "3032b state-meaning and residence audit",
        "next_if_fail": "pause 303x attractor narrative or revise observable basis",
        "next_if_boundary": "3032b robustness or variable revision",
        "outputs": [
            "Output/3032/tables/ulam_state_summary.csv",
            "Output/3032/tables/eigenvalue_spectrum.csv",
            "Output/3032/tables/spectral_partition_summary.csv",
            "Output/3032/tables/partition_retention_by_ob.csv",
            "Output/3032/tables/egrt_decision_summary.csv",
            "Output/3032/3032_summary.md",
        ],
        "provenance": {
            "script": "Experiment/run_3032_transfer_operator_metastability.py",
            "decision": rec,
        },
    }
    (OUT / "3032_egrt_node.json").write_text(json.dumps(node, ensure_ascii=False, indent=2), encoding="utf-8")


def make_figures(
    eigen_table: pd.DataFrame,
    partitions: pd.DataFrame,
    retention: pd.DataFrame,
    interpreted: pd.DataFrame,
    df: pd.DataFrame,
    mapping: pd.DataFrame,
    best_partition_id: str,
    variables: list[str],
    cfg: RunConfig,
) -> None:
    if not eigen_table.empty:
        fig, ax = plt.subplots(figsize=(7.2, 4.6))
        d = eigen_table.head(20)
        ax.scatter(d["eigen_rank"], d["eigenvalue_real"], s=45, color="#2f6f6d")
        ax.axhline(cfg.eigenvalue_gate, color="#777777", linestyle="--", linewidth=0.9)
        ax.set_xlabel("eigenvalue rank")
        ax.set_ylabel("real part")
        ax.set_title("3032 transfer-operator spectrum")
        ax.set_ylim(min(0, float(d["eigenvalue_real"].min()) - 0.05), 1.03)
        fig.tight_layout()
        fig.savefig(FIG / "transfer_operator_eigenvalue_spectrum.png", dpi=180)
        plt.close(fig)

    if not partitions.empty:
        fig, ax = plt.subplots(figsize=(9.2, 4.8))
        d = partitions.head(6).copy()
        x = np.arange(len(d))
        ax.bar(x - 0.18, d["low_pooled_retention"], width=0.36, color="#4c78a8", label="low set")
        ax.bar(x + 0.18, d["high_pooled_retention"], width=0.36, color="#f58518", label="high set")
        ax.axhline(cfg.pooled_retention_gate, color="#777777", linestyle="--", linewidth=0.9)
        ax.set_xticks(x)
        ax.set_xticklabels(d["partition_id"], rotation=0)
        ax.set_ylabel("pooled one-lag retention")
        ax.set_title("3032 pooled retention by spectral partition")
        ax.legend(frameon=False)
        fig.tight_layout()
        fig.savefig(FIG / "spectral_partition_pooled_retention.png", dpi=180)
        plt.close(fig)

    if not retention.empty:
        d = retention[(retention["partition_id"] == best_partition_id) & np.isfinite(retention["retention"])].copy()
        if not d.empty:
            fig, ax = plt.subplots(figsize=(8.0, 4.8))
            data = [d[d["spectral_set"] == set_name]["retention"].dropna().to_numpy() for set_name in SET_ORDER]
            ax.boxplot(data, tick_labels=SET_ORDER, showfliers=False)
            ax.axhline(cfg.ob_q25_retention_gate, color="#777777", linestyle="--", linewidth=0.9)
            ax.set_ylabel("per-Ob one-lag retention")
            ax.set_title(f"3032 cross-Ob retention: {best_partition_id}")
            fig.tight_layout()
            fig.savefig(FIG / "best_partition_retention_by_ob.png", dpi=180)
            plt.close(fig)

    if best_partition_id and not mapping.empty and len(variables) >= 2:
        dmap = mapping[mapping["partition_id"] == best_partition_id]
        cell_to_set = {int(r.ulam_cell): str(r.spectral_set) for r in dmap.itertuples(index=False)}
        plot_df = df.copy()
        plot_df["spectral_set"] = label_sequence(plot_df["ulam_cell"].to_numpy(dtype="int64"), cell_to_set)
        if len(plot_df) > cfg.scatter_sample:
            plot_df = plot_df.sample(cfg.scatter_sample, random_state=RNG_SEED)
        colors = {"low": "#4c78a8", "high": "#f58518", "unmapped": "#bbbbbb"}
        fig, ax = plt.subplots(figsize=(7.2, 5.8))
        for set_name, d in plot_df.groupby("spectral_set", sort=True):
            alpha = 0.18 if set_name != "unmapped" else 0.05
            ax.scatter(
                d[f"{variables[0]}_z"],
                d[f"{variables[1]}_z"],
                s=5,
                alpha=alpha,
                color=colors.get(str(set_name), "#666666"),
                label=str(set_name),
                linewidths=0,
            )
        ax.set_xlabel(f"{variables[0]} within-Ob robust z")
        ax.set_ylabel(f"{variables[1]} within-Ob robust z")
        ax.set_title(f"3032 best spectral partition: {best_partition_id}")
        ax.legend(frameon=False, markerscale=3)
        fig.tight_layout()
        fig.savefig(FIG / "best_partition_slow_state_scatter.png", dpi=180)
        plt.close(fig)

    if not interpreted.empty:
        zcols = [f"median_{var}_z" for var in variables]
        d = interpreted.set_index("spectral_set")[zcols]
        fig, ax = plt.subplots(figsize=(7.0, 3.6))
        x = np.arange(len(zcols))
        width = 0.36
        for i, set_name in enumerate(SET_ORDER):
            if set_name not in d.index:
                continue
            ax.bar(x + (i - 0.5) * width, d.loc[set_name].to_numpy(dtype="float64"), width=width, label=set_name)
        ax.axhline(0.0, color="#222222", linewidth=0.7)
        ax.set_xticks(x)
        ax.set_xticklabels([c.replace("median_", "").replace("_z", "") for c in zcols], rotation=20, ha="right")
        ax.set_ylabel("median within-Ob z")
        ax.set_title("3032 best partition slow-variable meaning")
        ax.legend(frameon=False)
        fig.tight_layout()
        fig.savefig(FIG / "best_partition_variable_profile.png", dpi=180)
        plt.close(fig)


def write_summary(
    decision: pd.DataFrame,
    variables: list[str],
    cfg: RunConfig,
    cell_summary: pd.DataFrame,
    eigen_table: pd.DataFrame,
    partitions: pd.DataFrame,
    retention: pd.DataFrame,
    interpreted: pd.DataFrame,
    overlap: pd.DataFrame,
    composition: pd.DataFrame,
) -> None:
    rec = decision.iloc[0]
    top_partitions = partitions.head(8) if not partitions.empty else partitions
    key_partition_cols = [
        "partition_id",
        "eigen_rank",
        "eigenvalue_real",
        "implied_timescale_sec",
        "min_pooled_retention",
        "min_retention_lift",
        "q25_ob_retention",
        "frac_ob_set_lift_positive",
        "median_residence_sec",
        "interpretive_axis",
    ]
    if not top_partitions.empty:
        top_partitions = top_partitions[[c for c in key_partition_cols if c in top_partitions.columns]]
    summary = f"""# 3032 EGRT Transfer-Operator Metastability

## Scope

3032 follows the 3030 screen decision. Since deterministic-attractor evidence was weak while slow shape-density variables retained recurrence structure above surrogates, this node tests a weaker and more interpretable claim: the slow-variable state space may contain almost-invariant macroscopic sets.

## EGRT Node

| field | value |
| --- | --- |
| node_id | 3032_transfer_operator_metastability |
| parent | 3030_attractor_evidence_screen |
| node_type | mechanism |
| competing interpretations | stochastic/metastable macroscopic organization; coarse discretization artifact; Ob-specific persistence |
| decision | {rec['eg_rt_decision']} |
| recommended next node | {rec['recommended_next_node']} |
| boundary reading | {rec['boundary_reading']} |

## Inputs

- Raw macroscopic observables: `Output/3001/processed/geometric_center_observables_all.csv`
- 3030 routing decision: `Output/3030/tables/egrt_decision_summary.csv`
- 3030 variable evidence: `Output/3030/tables/variable_evidence_summary.csv`

## Methods

- Candidate variables inherited from 3030: `{", ".join(variables)}`.
- Each variable is robust-standardized within Ob before pooling.
- The standardized slow-variable space is discretized into {cfg.n_bins} quantile bins per variable, giving up to {cfg.n_bins ** len(variables)} Ulam cells.
- A pooled empirical transition operator is estimated at lag {cfg.lag_sec:.3g}s.
- Dominant right-eigenvectors define binary spectral partitions.
- A partition passes only when one-lag retention is high, exceeds its occupancy baseline, and remains consistent across Ob.
- The best partition is compared with the 3013 quiet/outward/mobile/other classifier only as an interpretive coordinate.

## Decision Metrics

{dataframe_to_markdown(decision)}

## Top Spectral Partitions

{dataframe_to_markdown(top_partitions)}

## Best Partition Meaning

{dataframe_to_markdown(interpreted)}

## Coarse-State Overlap

{dataframe_to_markdown(overlap)}

## Coarse-State Composition

{dataframe_to_markdown(composition)}

## Outputs

- `Output/3032/3032_egrt_node.json`
- `Output/3032/tables/ulam_state_summary.csv`
- `Output/3032/tables/eigenvalue_spectrum.csv`
- `Output/3032/tables/spectral_partition_summary.csv`
- `Output/3032/tables/spectral_cell_mapping.csv`
- `Output/3032/tables/partition_retention_by_ob.csv`
- `Output/3032/tables/partition_residence_runs.csv`
- `Output/3032/tables/best_partition_interpretation.csv`
- `Output/3032/tables/coarse_state_overlap.csv`
- `Output/3032/tables/egrt_decision_summary.csv`
- `Output/3032/figures/transfer_operator_eigenvalue_spectrum.png`
- `Output/3032/figures/spectral_partition_pooled_retention.png`
- `Output/3032/figures/best_partition_retention_by_ob.png`
- `Output/3032/figures/best_partition_slow_state_scatter.png`
- `Output/3032/figures/best_partition_variable_profile.png`

## Interpretation Boundary

This node does not prove deterministic chaos. A positive gate means that the selected slow variables support a stochastic/metastable attractor-like reading: probability mass tends to remain inside a small number of macroscopic organization sets over the tested lag. It should not be written as a low-dimensional deterministic attractor unless later nodes add stronger geometric or predictive evidence.
"""
    (OUT / "3032_summary.md").write_text(summary, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lag-sec", type=float, default=RunConfig.lag_sec)
    parser.add_argument("--n-bins", type=int, default=RunConfig.n_bins)
    parser.add_argument("--quick", action="store_true", help="Use fewer scatter points; the transition analysis still uses all rows.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cfg = RunConfig(lag_sec=args.lag_sec, n_bins=args.n_bins, scatter_sample=15000 if args.quick else RunConfig.scatter_sample)
    ensure_dirs()
    variables = read_3030_candidates()
    raw = read_input(variables)
    df = standardize_within_ob(raw, variables)
    df, edges = assign_ulam_cells(df, variables, cfg)
    cell_summary = build_cell_summary(df, variables, cfg)

    active_cells = sorted(cell_summary["ulam_cell"].astype(int).tolist())
    n_total_cells = cfg.n_bins ** len(variables)
    active_coverage = float(cell_summary["frame_count"].sum() / len(df)) if len(df) else math.nan
    counts, transition_meta = transition_counts(df, active_cells, cfg)
    p = row_stochastic(counts)
    pi = stationary_distribution(p)

    eigen_table, raw_partitions, mapping = spectral_partitions(p, pi, active_cells, cell_summary, variables, cfg)
    retention, residence = partition_retention_by_ob(df, mapping, cfg)
    partitions = summarize_partitions(raw_partitions, retention, residence, cfg)

    decision = decision_summary(partitions, eigen_table, active_coverage, len(active_cells), n_total_cells, variables, cfg)
    best_partition_id = str(decision.iloc[0].get("best_partition_id", "")) if "best_partition_id" in decision.columns else ""
    if best_partition_id and not mapping.empty:
        interpreted, overlap, composition = interpret_best_partition(df, mapping, best_partition_id, variables)
    else:
        interpreted = pd.DataFrame()
        overlap = pd.DataFrame()
        composition = pd.DataFrame()

    cell_summary.to_csv(TAB / "ulam_state_summary.csv", index=False)
    cell_summary.to_csv(PROC / "ulam_state_summary.csv", index=False)
    eigen_table.to_csv(TAB / "eigenvalue_spectrum.csv", index=False)
    raw_partitions.to_csv(PROC / "raw_spectral_partition_summary.csv", index=False)
    partitions.to_csv(TAB / "spectral_partition_summary.csv", index=False)
    partitions.to_csv(PROC / "spectral_partition_summary.csv", index=False)
    mapping.to_csv(TAB / "spectral_cell_mapping.csv", index=False)
    retention.to_csv(TAB / "partition_retention_by_ob.csv", index=False)
    residence.to_csv(TAB / "partition_residence_runs.csv", index=False)
    transition_meta.to_csv(TAB / "transition_metadata_by_ob.csv", index=False)
    interpreted.to_csv(TAB / "best_partition_interpretation.csv", index=False)
    overlap.to_csv(TAB / "coarse_state_overlap.csv", index=False)
    composition.to_csv(TAB / "coarse_state_composition.csv", index=False)
    decision.to_csv(TAB / "egrt_decision_summary.csv", index=False)
    decision.to_csv(PROC / "egrt_decision_summary.csv", index=False)
    (TAB / "ulam_bin_edges.json").write_text(json.dumps(edges, ensure_ascii=False, indent=2), encoding="utf-8")

    write_node_schema(decision, cfg)
    make_figures(eigen_table, partitions, retention, interpreted, df, mapping, best_partition_id, variables, cfg)
    write_summary(decision, variables, cfg, cell_summary, eigen_table, partitions, retention, interpreted, overlap, composition)
    print(decision.to_string(index=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
