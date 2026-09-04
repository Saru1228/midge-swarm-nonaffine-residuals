"""4090 continuous compactness first-vs-second moment classification.

This node uses the frozen 4088 T1 residual definition, the 4090B vector-unit
boundary, and C(t), dC/dt from 3045. It asks whether the vector-level local
non-affine tangential residual is better organized as a first moment or a second
moment with respect to continuous compact-density state.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from textwrap import dedent

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_DIR = ROOT / "Experiment"
if str(EXPERIMENT_DIR) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_DIR))

import run_4081_global_vs_local_geometry_ladder as r4081  # noqa: E402
import run_4090B_vector_state_feasibility_check as r4090b  # noqa: E402
from run_4001_geometric_baseline_residual_audit import (  # noqa: E402
    RunConfig as BaseRunConfig,
    median_dt,
    resolve_data_dir,
)


OUT = ROOT / "Output" / "4090"
DATE = "2026-08-26"
NODE = "4090_continuous_moment_classification_with_vector_unit_note"

SRC_4090A = ROOT / "Output" / "4090A" / "decision.json"
SRC_4090B = ROOT / "Output" / "4090B" / "decision.json"
SRC_4088 = ROOT / "Output" / "4088" / "decision.json"
SRC_4090B_COVERAGE = ROOT / "Output" / "4090B" / "continuous_state_coverage.csv"

VECTOR_COLUMNS = [
    "ob",
    "dataset",
    "t",
    "k",
    "lag_sec",
    "lag_dt",
    "focal_id",
    "neighbor_id",
    "focal_radius",
    "neighbor_rank",
    "condition_number",
    "C",
    "dCdt",
    "C_shift",
    "dCdt_shift",
    "resid_tan_vx",
    "resid_tan_vy",
    "resid_tan_vz",
    "resid_tan_norm",
    "resid_tan_energy",
    "raw_tan_norm",
    "signed_tan_projection",
    "unit_resid_tan_vx",
    "unit_resid_tan_vy",
    "unit_resid_tan_vz",
]

OOS_COLUMNS = [
    "heldout_ob",
    "target_family",
    "target",
    "n_train",
    "n_test",
    "mse_radius_baseline",
    "mse_state_model",
    "mse_shifted_state_model",
    "incremental_r2_state_vs_radius",
    "incremental_r2_shift_vs_radius",
    "real_minus_shift_incremental_r2",
]

PROFILE_COLUMNS = [
    "C_bin",
    "dCdt_bin",
    "radius_bin",
    "n",
    "mean_signed_tan_projection",
    "mean_log_tan_energy",
    "mean_tan_energy",
    "mean_vector_strength",
    "directional_coherence",
]

DATASET_EFFECT_COLUMNS = [
    "ob",
    "dataset",
    "n",
    "signed_highC_minus_lowC",
    "log_energy_highC_minus_lowC",
    "energy_highC_minus_lowC",
    "coherence_highC_minus_lowC",
    "median_C",
    "q25_C",
    "q75_C",
]

PRIMARY_METRIC_COLUMNS = [
    "target_family",
    "target",
    "median_incremental_r2",
    "positive_ob_fraction",
    "median_shift_incremental_r2",
    "median_real_minus_shift",
    "real_gt_shift_fraction",
    "pass_gate",
    "interpretation",
]


def ensure_dirs() -> None:
    for path in (OUT, OUT / "tables", OUT / "figures", OUT / "cache"):
        path.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in columns})


def to_jsonable(obj: object) -> object:
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_jsonable(v) for v in obj]
    if isinstance(obj, tuple):
        return [to_jsonable(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        val = float(obj)
        return None if not math.isfinite(val) else val
    if isinstance(obj, float):
        return None if not math.isfinite(obj) else obj
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    return obj


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(to_jsonable(data), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def md_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        vals: list[str] = []
        for col in columns:
            val = row.get(col, "")
            if isinstance(val, float):
                vals.append("NA" if not math.isfinite(val) else f"{val:.4g}")
            else:
                vals.append(str(val).replace("\n", " ").replace("|", "\\|"))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def state_frame_with_shift(shift_fraction: float) -> pd.DataFrame:
    state = r4090b.add_state_derivative(r4090b.load_state_frame())
    state = state.rename(
        columns={
            "density_rms_z3045": "C",
            "dCdt_density_rms_smooth3045": "dCdt",
        }
    )
    state["t_key"] = state["t"].round(5)
    state["C_shift"] = math.nan
    state["dCdt_shift"] = math.nan
    for ob, idx in state.groupby("ob", sort=True).groups.items():
        d = state.loc[idx].sort_values("t")
        n = len(d)
        shift = max(1, int(round(n * shift_fraction)))
        state.loc[d.index, "C_shift"] = np.roll(d["C"].to_numpy(dtype="float64"), shift)
        state.loc[d.index, "dCdt_shift"] = np.roll(d["dCdt"].to_numpy(dtype="float64"), shift)
    return state[["ob", "dataset", "t_key", "C", "dCdt", "C_shift", "dCdt_shift"]].copy()


def build_vector_sample_for_ob(
    *,
    ob: int,
    data_dir: Path,
    k: int,
    lag_sec: float,
    frame_stride: int,
    max_focals: int,
) -> pd.DataFrame:
    dataset = f"Ob{ob}.txt"
    df = r4081.load_ob_df(ob, data_dir, dataset)
    times = np.asarray(sorted(df["t"].unique()), dtype="float64")
    frames = {float(t): d.sort_values("id").copy() for t, d in df.groupby("t", sort=True)}
    dt = median_dt(times)
    lag_steps = max(1, int(round(lag_sec / dt)))
    idxs = np.arange(0, len(times) - lag_steps, frame_stride, dtype=int)
    rng = np.random.default_rng(4090_1000 + ob * 101 + k)
    rows: list[dict[str, object]] = []
    for nn, idx in enumerate(idxs):
        if nn % 500 == 0:
            print(f"[4090] Ob{ob} frame sample {nn + 1}/{len(idxs)}", flush=True)
        t0 = float(times[idx])
        ids0, pos0 = r4081.frame_arrays(frames[t0])
        ids1, pos1 = r4081.frame_arrays(frames[float(times[idx + lag_steps])])
        id_to_idx0 = {int(v): i for i, v in enumerate(ids0)}
        id_to_idx1 = {int(v): i for i, v in enumerate(ids1)}
        common = np.asarray([v for v in ids0 if int(v) in id_to_idx1], dtype="int64")
        if common.size == 0:
            continue
        if common.size > max_focals:
            focals = rng.choice(common, size=max_focals, replace=False)
        else:
            focals = common
        center = np.nanmean(pos0, axis=0)
        lag_dt = lag_steps * dt
        for focal_id in focals:
            focal_id = int(focal_id)
            i0 = id_to_idx0[focal_id]
            i1 = id_to_idx1[focal_id]
            rel_all = pos0 - pos0[i0]
            dist = np.linalg.norm(rel_all, axis=1)
            order = np.argsort(dist)
            neigh_ids = [int(ids0[j]) for j in order if int(ids0[j]) != focal_id and int(ids0[j]) in id_to_idx1][:k]
            if len(neigh_ids) < 4:
                continue
            A = []
            B = []
            kept_ids = []
            for nid in neigh_ids:
                j0 = id_to_idx0[nid]
                j1 = id_to_idx1[nid]
                r0 = pos0[j0] - pos0[i0]
                r1 = pos1[j1] - pos1[i1]
                A.append(r0)
                B.append(r1 - r0)
                kept_ids.append(nid)
            A = np.asarray(A, dtype="float64")
            B = np.asarray(B, dtype="float64")
            if not (np.isfinite(A).all() and np.isfinite(B).all()):
                continue
            try:
                _, s, _ = np.linalg.svd(A, full_matrices=False)
                if s.size < 3 or s[-1] <= 1e-12:
                    continue
                cond = float(s[0] / s[-1])
                J, _, _, _ = np.linalg.lstsq(A, B, rcond=None)
            except np.linalg.LinAlgError:
                continue
            resid = (B - A @ J) / lag_dt
            raw_rel_v = B / lag_dt
            focal_rel = pos0[i0] - center
            focal_radius = float(np.linalg.norm(focal_rel))
            if not math.isfinite(focal_radius) or focal_radius <= 1e-12:
                continue
            radial_unit = focal_rel / focal_radius
            resid_radial = resid @ radial_unit
            resid_tan = resid - resid_radial[:, None] * radial_unit[None, :]
            raw_radial = raw_rel_v @ radial_unit
            raw_tan = raw_rel_v - raw_radial[:, None] * radial_unit[None, :]
            resid_tan_norm = np.sqrt(np.maximum(np.sum(resid_tan * resid_tan, axis=1), 0.0))
            raw_tan_norm = np.sqrt(np.maximum(np.sum(raw_tan * raw_tan, axis=1), 0.0))
            resid_tan_energy = resid_tan_norm * resid_tan_norm
            raw_unit = np.full_like(raw_tan, math.nan, dtype="float64")
            ok_raw = raw_tan_norm > 1e-12
            raw_unit[ok_raw] = raw_tan[ok_raw] / raw_tan_norm[ok_raw, None]
            signed_proj = np.sum(resid_tan * raw_unit, axis=1)
            resid_unit = np.full_like(resid_tan, math.nan, dtype="float64")
            ok_resid = resid_tan_norm > 1e-12
            resid_unit[ok_resid] = resid_tan[ok_resid] / resid_tan_norm[ok_resid, None]
            for rank, nid in enumerate(kept_ids, start=1):
                i = rank - 1
                if not np.isfinite(resid_tan[i]).all() or not math.isfinite(float(signed_proj[i])):
                    continue
                rows.append(
                    {
                        "ob": ob,
                        "dataset": dataset,
                        "t": t0,
                        "k": k,
                        "lag_sec": lag_sec,
                        "lag_dt": lag_dt,
                        "focal_id": focal_id,
                        "neighbor_id": int(nid),
                        "focal_radius": focal_radius,
                        "neighbor_rank": rank,
                        "condition_number": cond,
                        "resid_tan_vx": float(resid_tan[i, 0]),
                        "resid_tan_vy": float(resid_tan[i, 1]),
                        "resid_tan_vz": float(resid_tan[i, 2]),
                        "resid_tan_norm": float(resid_tan_norm[i]),
                        "resid_tan_energy": float(resid_tan_energy[i]),
                        "raw_tan_norm": float(raw_tan_norm[i]),
                        "signed_tan_projection": float(signed_proj[i]),
                        "unit_resid_tan_vx": float(resid_unit[i, 0]),
                        "unit_resid_tan_vy": float(resid_unit[i, 1]),
                        "unit_resid_tan_vz": float(resid_unit[i, 2]),
                    }
                )
    return pd.DataFrame(rows)


def build_or_load_vector_sample(
    *,
    data_dir: Path,
    obs: list[int],
    k: int,
    lag_sec: float,
    frame_stride: int,
    max_focals: int,
    force: bool,
) -> pd.DataFrame:
    cache = OUT / "cache" / f"vector_sample_k{k}_lag{lag_sec:.3f}_stride{frame_stride}_focals{max_focals}.csv.gz"
    if cache.exists() and not force:
        return pd.read_csv(cache, low_memory=False)
    parts: list[pd.DataFrame] = []
    for ob in obs:
        print(f"[4090] building vector sample for Ob{ob}", flush=True)
        part = build_vector_sample_for_ob(
            ob=ob,
            data_dir=data_dir,
            k=k,
            lag_sec=lag_sec,
            frame_stride=frame_stride,
            max_focals=max_focals,
        )
        parts.append(part)
    sample = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=VECTOR_COLUMNS)
    state = state_frame_with_shift(0.33)
    sample["t_key"] = sample["t"].round(5)
    sample = sample.merge(state, on=["ob", "dataset", "t_key"], how="left")
    sample = sample.drop(columns=["t_key"], errors="ignore")
    sample = sample.dropna(subset=["C", "dCdt", "C_shift", "dCdt_shift", "focal_radius", "signed_tan_projection", "resid_tan_energy"])
    sample.to_csv(cache, index=False, compression="gzip")
    return sample


def quantile_edges(values: np.ndarray, n_bins: int) -> np.ndarray:
    values = np.asarray(values, dtype="float64")
    values = values[np.isfinite(values)]
    if values.size == 0:
        return np.asarray([-math.inf, math.inf], dtype="float64")
    qs = np.linspace(0, 1, n_bins + 1)
    edges = np.unique(np.quantile(values, qs))
    if edges.size < 2:
        val = float(edges[0]) if edges.size else 0.0
        return np.asarray([val - 1e-9, val + 1e-9], dtype="float64")
    edges[0] = -math.inf
    edges[-1] = math.inf
    return edges


def assign_bins(values: np.ndarray, edges: np.ndarray) -> np.ndarray:
    return np.digitize(np.asarray(values, dtype="float64"), edges[1:-1], right=False)


def fit_bin_model(train: pd.DataFrame, target: str, cols: list[str]) -> tuple[dict[tuple[int, ...], float], float]:
    y = pd.to_numeric(train[target], errors="coerce")
    global_mean = float(y.mean()) if y.notna().any() else math.nan
    model: dict[tuple[int, ...], float] = {}
    if not cols:
        return model, global_mean
    d = train.dropna(subset=[target] + cols).copy()
    for key, g in d.groupby(cols, sort=False):
        if not isinstance(key, tuple):
            key = (int(key),)
        model[tuple(int(x) for x in key)] = float(pd.to_numeric(g[target], errors="coerce").mean())
    return model, global_mean


def predict_bin_model(df: pd.DataFrame, model: dict[tuple[int, ...], float], global_mean: float, cols: list[str]) -> np.ndarray:
    if not cols:
        return np.full(len(df), global_mean, dtype="float64")
    preds = np.full(len(df), global_mean, dtype="float64")
    if not math.isfinite(global_mean):
        return preds
    values = df[cols].to_numpy(dtype="int64")
    for i, row in enumerate(values):
        preds[i] = model.get(tuple(int(x) for x in row), global_mean)
    return preds


def mse(y: np.ndarray, pred: np.ndarray) -> float:
    y = np.asarray(y, dtype="float64")
    pred = np.asarray(pred, dtype="float64")
    ok = np.isfinite(y) & np.isfinite(pred)
    if int(ok.sum()) == 0:
        return math.nan
    return float(np.mean((y[ok] - pred[ok]) ** 2))


def evaluate_grouped_oos(sample: pd.DataFrame, *, c_bins: int, dc_bins: int, radius_bins: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    targets = [
        ("first_moment", "signed_tan_projection"),
        ("second_moment", "log_tan_energy"),
    ]
    obs = sorted(int(x) for x in sample["ob"].unique())
    for heldout in obs:
        train = sample[sample["ob"] != heldout].copy()
        test = sample[sample["ob"] == heldout].copy()
        edges = {
            "C": quantile_edges(train["C"].to_numpy(dtype="float64"), c_bins),
            "dCdt": quantile_edges(train["dCdt"].to_numpy(dtype="float64"), dc_bins),
            "C_shift": quantile_edges(train["C_shift"].to_numpy(dtype="float64"), c_bins),
            "dCdt_shift": quantile_edges(train["dCdt_shift"].to_numpy(dtype="float64"), dc_bins),
            "focal_radius": quantile_edges(train["focal_radius"].to_numpy(dtype="float64"), radius_bins),
        }
        for d in (train, test):
            d["C_bin"] = assign_bins(d["C"].to_numpy(dtype="float64"), edges["C"])
            d["dCdt_bin"] = assign_bins(d["dCdt"].to_numpy(dtype="float64"), edges["dCdt"])
            d["C_shift_bin"] = assign_bins(d["C_shift"].to_numpy(dtype="float64"), edges["C_shift"])
            d["dCdt_shift_bin"] = assign_bins(d["dCdt_shift"].to_numpy(dtype="float64"), edges["dCdt_shift"])
            d["radius_bin"] = assign_bins(d["focal_radius"].to_numpy(dtype="float64"), edges["focal_radius"])
        for family, target in targets:
            radius_model, radius_global = fit_bin_model(train, target, ["radius_bin"])
            state_model, state_global = fit_bin_model(train, target, ["C_bin", "dCdt_bin", "radius_bin"])
            shift_model, shift_global = fit_bin_model(train, target, ["C_shift_bin", "dCdt_shift_bin", "radius_bin"])
            y = test[target].to_numpy(dtype="float64")
            mse_radius = mse(y, predict_bin_model(test, radius_model, radius_global, ["radius_bin"]))
            mse_state = mse(y, predict_bin_model(test, state_model, state_global, ["C_bin", "dCdt_bin", "radius_bin"]))
            mse_shift = mse(y, predict_bin_model(test, shift_model, shift_global, ["C_shift_bin", "dCdt_shift_bin", "radius_bin"]))
            r2_state = 1.0 - mse_state / mse_radius if math.isfinite(mse_radius) and mse_radius > 1e-12 else math.nan
            r2_shift = 1.0 - mse_shift / mse_radius if math.isfinite(mse_radius) and mse_radius > 1e-12 else math.nan
            rows.append(
                {
                    "heldout_ob": heldout,
                    "target_family": family,
                    "target": target,
                    "n_train": int(len(train)),
                    "n_test": int(len(test)),
                    "mse_radius_baseline": mse_radius,
                    "mse_state_model": mse_state,
                    "mse_shifted_state_model": mse_shift,
                    "incremental_r2_state_vs_radius": r2_state,
                    "incremental_r2_shift_vs_radius": r2_shift,
                    "real_minus_shift_incremental_r2": r2_state - r2_shift if math.isfinite(r2_state) and math.isfinite(r2_shift) else math.nan,
                }
            )
    return pd.DataFrame(rows)


def primary_metrics(oos: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (family, target), d in oos.groupby(["target_family", "target"], sort=False):
        real = pd.to_numeric(d["incremental_r2_state_vs_radius"], errors="coerce").to_numpy(dtype="float64")
        shift = pd.to_numeric(d["incremental_r2_shift_vs_radius"], errors="coerce").to_numpy(dtype="float64")
        gap = pd.to_numeric(d["real_minus_shift_incremental_r2"], errors="coerce").to_numpy(dtype="float64")
        ok = np.isfinite(real)
        median_real = float(np.nanmedian(real)) if np.any(ok) else math.nan
        positive = float(np.nanmean(real > 0.0)) if np.any(ok) else math.nan
        median_shift = float(np.nanmedian(shift)) if np.isfinite(shift).any() else math.nan
        median_gap = float(np.nanmedian(gap)) if np.isfinite(gap).any() else math.nan
        real_gt_shift = float(np.nanmean(gap > 0.0)) if np.isfinite(gap).any() else math.nan
        passed = bool(
            math.isfinite(median_real)
            and median_real > 0.005
            and positive >= 0.60
            and math.isfinite(median_gap)
            and median_gap > 0.002
            and real_gt_shift >= 0.60
        )
        if passed:
            interp = "passes grouped OOS and shifted-state separation gate"
        elif math.isfinite(median_real) and median_real > 0.0:
            interp = "weak positive but below gate"
        else:
            interp = "no stable grouped OOS support"
        rows.append(
            {
                "target_family": family,
                "target": target,
                "median_incremental_r2": median_real,
                "positive_ob_fraction": positive,
                "median_shift_incremental_r2": median_shift,
                "median_real_minus_shift": median_gap,
                "real_gt_shift_fraction": real_gt_shift,
                "pass_gate": passed,
                "interpretation": interp,
            }
        )
    return pd.DataFrame(rows)


def state_profiles(sample: pd.DataFrame, *, c_bins: int, dc_bins: int, radius_bins: int) -> pd.DataFrame:
    d = sample.copy()
    d["C_bin"] = assign_bins(d["C"].to_numpy(dtype="float64"), quantile_edges(d["C"].to_numpy(dtype="float64"), c_bins))
    d["dCdt_bin"] = assign_bins(d["dCdt"].to_numpy(dtype="float64"), quantile_edges(d["dCdt"].to_numpy(dtype="float64"), dc_bins))
    d["radius_bin"] = assign_bins(d["focal_radius"].to_numpy(dtype="float64"), quantile_edges(d["focal_radius"].to_numpy(dtype="float64"), radius_bins))
    rows: list[dict[str, object]] = []
    for key, g in d.groupby(["C_bin", "dCdt_bin", "radius_bin"], sort=True):
        V = g[["resid_tan_vx", "resid_tan_vy", "resid_tan_vz"]].to_numpy(dtype="float64")
        U = g[["unit_resid_tan_vx", "unit_resid_tan_vy", "unit_resid_tan_vz"]].to_numpy(dtype="float64")
        mean_v = np.nanmean(V, axis=0)
        mean_u = np.nanmean(U, axis=0)
        rows.append(
            {
                "C_bin": int(key[0]),
                "dCdt_bin": int(key[1]),
                "radius_bin": int(key[2]),
                "n": int(len(g)),
                "mean_signed_tan_projection": float(g["signed_tan_projection"].mean()),
                "mean_log_tan_energy": float(g["log_tan_energy"].mean()),
                "mean_tan_energy": float(g["resid_tan_energy"].mean()),
                "mean_vector_strength": float(np.linalg.norm(mean_v)),
                "directional_coherence": float(np.linalg.norm(mean_u)),
            }
        )
    return pd.DataFrame(rows)


def dataset_effects(sample: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for ob, d in sample.groupby("ob", sort=True):
        c = d["C"].to_numpy(dtype="float64")
        q25, q50, q75 = np.nanquantile(c[np.isfinite(c)], [0.25, 0.50, 0.75])
        low = d[d["C"] <= q25]
        high = d[d["C"] >= q75]
        def diff(col: str) -> float:
            if low.empty or high.empty:
                return math.nan
            return float(high[col].mean() - low[col].mean())
        def coherence(g: pd.DataFrame) -> float:
            U = g[["unit_resid_tan_vx", "unit_resid_tan_vy", "unit_resid_tan_vz"]].to_numpy(dtype="float64")
            if U.size == 0:
                return math.nan
            return float(np.linalg.norm(np.nanmean(U, axis=0)))
        rows.append(
            {
                "ob": int(ob),
                "dataset": str(d["dataset"].iloc[0]),
                "n": int(len(d)),
                "signed_highC_minus_lowC": diff("signed_tan_projection"),
                "log_energy_highC_minus_lowC": diff("log_tan_energy"),
                "energy_highC_minus_lowC": diff("resid_tan_energy"),
                "coherence_highC_minus_lowC": coherence(high) - coherence(low) if not low.empty and not high.empty else math.nan,
                "median_C": float(q50),
                "q25_C": float(q25),
                "q75_C": float(q75),
            }
        )
    return pd.DataFrame(rows)


def classify(metrics: pd.DataFrame) -> dict[str, object]:
    first = metrics[metrics["target_family"] == "first_moment"].iloc[0].to_dict()
    second = metrics[metrics["target_family"] == "second_moment"].iloc[0].to_dict()
    first_pass = bool(first["pass_gate"])
    second_pass = bool(second["pass_gate"])
    first_r2 = float(first["median_incremental_r2"])
    second_r2 = float(second["median_incremental_r2"])
    if second_pass and not first_pass:
        result = "support_variance_dominant_nonaffine_organization"
        next_nodes = ["4091_density_neighbor_conditioned_variance"]
        interpretation = (
            "Second-moment state model passes grouped OOS and shifted-state separation, while the signed first-moment "
            "projection does not. Route to density/neighbor-conditioned variance."
        )
    elif first_pass and not second_pass:
        result = "support_mean_dominant_nonaffine_organization"
        next_nodes = ["4092_speed_conditioned_mean_variance"]
        interpretation = (
            "Signed first-moment projection passes grouped OOS and shifted-state separation more clearly than the "
            "second moment. Route to speed-conditioned mean/variance."
        )
    elif first_pass and second_pass:
        result = "support_mixed_mean_variance_structure"
        next_nodes = ["4091_density_neighbor_conditioned_variance", "4092_speed_conditioned_mean_variance"]
        interpretation = "Both first and second moment gates pass; route to both conditional-modulator branches."
    else:
        result = "transition_linked_but_not_lowdimensional_state_conditioned"
        next_nodes = ["4094_bounded_stochastic_negative_synthesis", "consider_410x_transient_event_local_route"]
        interpretation = (
            "Neither signed first moment nor second moment shows stable grouped OOS improvement over radius-only baseline "
            "with shifted-state separation. This routes away from low-dimensional stochastic closure."
        )
    if second_pass and first_pass and math.isfinite(second_r2) and math.isfinite(first_r2) and second_r2 > first_r2 * 2:
        result = "support_variance_dominant_with_weak_first_moment"
        next_nodes = ["4091_density_neighbor_conditioned_variance", "4092_speed_conditioned_variance_secondary"]
    return {
        "node": NODE,
        "date": DATE,
        "node_type": "screen",
        "upstream_node": "4090B_residual_vector_and_continuous_state_feasibility_check",
        "upstream_target": "T1_local_tangential_nonaffine_residual",
        "residual_unit": "focal_neighborhood_neighbor_residual_vector",
        "conditioning_state": ["C_density_rms_z3045", "dCdt_gradient_density_rms_smooth3045", "focal_radius"],
        "baseline": "radius_only_binned_model",
        "null": "within_observation_circular_shift_of_C_and_dCdt",
        "grouped_validation": "leave_one_observation_out",
        "gate_result": result,
        "interpretation": interpretation,
        "first_moment_metric": first,
        "second_moment_metric": second,
        "next": next_nodes,
        "does_not_prove": [
            "biological force law",
            "multiplicative Langevin mechanism",
            "causal precursor",
            "unique focal-individual residual vector",
        ],
        "artifacts": [
            "Output/4090/vector_moment_samples.csv.gz",
            "Output/4090/grouped_oos_results.csv",
            "Output/4090/primary_metrics.csv",
            "Output/4090/dataset_level_effects.csv",
            "Output/4090/state_bin_profiles.csv",
            "Output/4090/null_results.csv",
            "Output/4090/figures/4090_oos_by_observation.png",
            "Output/4090/figures/4090_dataset_highC_effects.png",
            "Output/4090/figures/4090_state_profile_heatmaps.png",
            "Output/4090/4090_summary.md",
        ],
    }


def make_figures(oos: pd.DataFrame, effects: pd.DataFrame, profiles: pd.DataFrame) -> None:
    fig_dir = OUT / "figures"
    fig, ax = plt.subplots(figsize=(10, 5.5), constrained_layout=True)
    width = 0.35
    obs = sorted(oos["heldout_ob"].unique())
    x = np.arange(len(obs))
    first = oos[oos["target_family"] == "first_moment"].set_index("heldout_ob").reindex(obs)
    second = oos[oos["target_family"] == "second_moment"].set_index("heldout_ob").reindex(obs)
    ax.bar(x - width / 2, first["incremental_r2_state_vs_radius"], width=width, label="first: signed projection", color="#4c78a8")
    ax.bar(x + width / 2, second["incremental_r2_state_vs_radius"], width=width, label="second: log energy", color="#f58518")
    ax.axhline(0, color="#444444", linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels([f"Ob{int(v)}" for v in obs], rotation=45)
    ax.set_ylabel("LOO incremental R2 over radius-only")
    ax.set_title("4090 grouped OOS moment comparison")
    ax.grid(axis="y", color="#dddddd", linewidth=0.8)
    ax.legend(frameon=False)
    fig.savefig(fig_dir / "4090_oos_by_observation.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5), constrained_layout=True)
    x = np.arange(len(effects))
    ax.bar(x - width / 2, effects["signed_highC_minus_lowC"], width=width, color="#4c78a8", label="signed projection")
    ax.bar(x + width / 2, effects["log_energy_highC_minus_lowC"], width=width, color="#f58518", label="log energy")
    ax.axhline(0, color="#444444", linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels([f"Ob{int(v)}" for v in effects["ob"]], rotation=45)
    ax.set_ylabel("high C - low C")
    ax.set_title("4090 dataset-level high-compactness effects")
    ax.grid(axis="y", color="#dddddd", linewidth=0.8)
    ax.legend(frameon=False)
    fig.savefig(fig_dir / "4090_dataset_highC_effects.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), constrained_layout=True)
    prof = profiles.groupby(["C_bin", "dCdt_bin"], as_index=False).agg(
        mean_signed_tan_projection=("mean_signed_tan_projection", "mean"),
        mean_log_tan_energy=("mean_log_tan_energy", "mean"),
    )
    for ax, col, title in [
        (axes[0], "mean_signed_tan_projection", "first moment"),
        (axes[1], "mean_log_tan_energy", "second moment"),
    ]:
        pivot = prof.pivot(index="C_bin", columns="dCdt_bin", values=col).sort_index()
        im = ax.imshow(pivot.to_numpy(dtype="float64"), aspect="auto", origin="lower", cmap="RdYlGn")
        ax.set_title(title)
        ax.set_xlabel("dCdt bin")
        ax.set_ylabel("C bin")
        ax.set_xticks(np.arange(len(pivot.columns)))
        ax.set_xticklabels([str(int(v)) for v in pivot.columns])
        ax.set_yticks(np.arange(len(pivot.index)))
        ax.set_yticklabels([str(int(v)) for v in pivot.index])
        fig.colorbar(im, ax=ax)
    fig.suptitle("4090 state-bin profiles")
    fig.savefig(fig_dir / "4090_state_profile_heatmaps.png", dpi=180)
    plt.close(fig)


def write_config(args: argparse.Namespace) -> None:
    text = dedent(
        f"""\
        node: {NODE}
        date: {DATE}
        node_type: screen
        upstream_nodes:
          - 4088_bounded_408x_synthesis_with_failure_boundary
          - 4090A_observation_regime_boundary_audit
          - 4090B_residual_vector_and_continuous_state_feasibility_check
        residual_unit: focal_neighborhood_neighbor_residual_vector
        k: {args.k}
        lag_sec: {args.lag_sec}
        frame_stride: {args.frame_stride}
        max_focals_per_frame: {args.max_focals}
        observations: {args.obs}
        C: density_rms_z3045
        dCdt: gradient(density_rms_smooth3045,t)
        baseline: radius_only_binned_model
        state_model: C_dCdt_radius_binned_model
        null: within_observation_circular_shift_C_dCdt
        validation: leave_one_observation_out
        c_bins: {args.c_bins}
        dCdt_bins: {args.dc_bins}
        radius_bins: {args.radius_bins}
        """
    )
    (OUT / "config.yaml").write_text(text, encoding="utf-8")


def write_summary(
    *,
    sample: pd.DataFrame,
    oos: pd.DataFrame,
    metrics: pd.DataFrame,
    effects: pd.DataFrame,
    profiles: pd.DataFrame,
    decision: dict[str, object],
) -> None:
    sample_stats = {
        "rows": int(len(sample)),
        "observations": int(sample["ob"].nunique()),
        "median_rows_per_ob": float(sample.groupby("ob").size().median()),
        "median_condition_number": float(sample["condition_number"].median()),
        "median_tan_norm": float(sample["resid_tan_norm"].median()),
        "median_raw_tan_norm": float(sample["raw_tan_norm"].median()),
    }
    metric_display = metrics.copy()
    for col in metric_display.columns:
        if pd.api.types.is_numeric_dtype(metric_display[col]):
            metric_display[col] = metric_display[col].round(5)
    oos_display = oos.copy()
    for col in oos_display.columns:
        if pd.api.types.is_numeric_dtype(oos_display[col]):
            oos_display[col] = oos_display[col].round(5)
    effects_display = effects.copy()
    for col in effects_display.columns:
        if pd.api.types.is_numeric_dtype(effects_display[col]):
            effects_display[col] = effects_display[col].round(5)
    text = f"""# Node 4090 Summary

## Question

Does continuous compact-density state organize the frozen local non-affine T1
residual mainly as first-moment structure or as second-moment fluctuation
structure?

## Why this node exists after 408x

4088 froze a bounded T1 local non-affine tangential residual. 4090A showed an
unconfirmed early-observation proxy boundary but did not find a known raw/event
artifact that explains away T1. 4090B showed that vector-level residual samples
and C,dC are available.

## Frozen Upstream Target

```text
T1 = local tangential non-affine residual
```

## Data Scope

All 19 observations are included.

## Residual Unit Boundary

```text
residual_unit = focal-neighborhood neighbor residual vector
```

This matches the 4081/4088 `all_tangential` aggregate source, but it is not yet
a unique focal-individual residual vector.

## Continuous State Definition

```text
C(t) = density_rms_z3045
dC/dt = gradient(density_rms_smooth3045, t)
```

## Sample

```json
{json.dumps(to_jsonable(sample_stats), ensure_ascii=False, indent=2)}
```

## Baseline And Null

```text
baseline = radius-only binned model
state_model = C,dCdt,radius binned model
null = within-observation circular shift of C,dCdt
validation = leave-one-observation-out by observation
```

## Primary Metrics

{md_table(metric_display.to_dict("records"), PRIMARY_METRIC_COLUMNS)}

## Grouped OOS Results

{md_table(oos_display.to_dict("records"), OOS_COLUMNS)}

## Dataset-level High-C Effects

{md_table(effects_display.to_dict("records"), DATASET_EFFECT_COLUMNS)}

## Gate Evaluation

```text
gate_result = {decision["gate_result"]}
```

{decision["interpretation"]}

## What This Supports

- It supports the route decision encoded in `gate_result`.
- It keeps all 19 observations as the primary scope.
- It keeps the early-observation boundary as a stratification issue, not a
  deletion rule.

## What This Rules Out

If a moment family does not pass, 4090 rules out treating that family as a
stable low-dimensional C,dC-conditioned explanation under the current sampling
and binning definition.

## What This Does NOT Prove

{md_table([{"does_not_prove": x} for x in decision["does_not_prove"]], ["does_not_prove"])}

## Decision

`{decision["gate_result"]}`

## Next Node

{md_table([{"next": x} for x in decision["next"]], ["next"])}

## Artifacts

- `Output/4090/vector_moment_samples.csv.gz`
- `Output/4090/grouped_oos_results.csv`
- `Output/4090/primary_metrics.csv`
- `Output/4090/dataset_level_effects.csv`
- `Output/4090/state_bin_profiles.csv`
- `Output/4090/null_results.csv`
- `Output/4090/figures/4090_oos_by_observation.png`
- `Output/4090/figures/4090_dataset_highC_effects.png`
- `Output/4090/figures/4090_state_profile_heatmaps.png`
"""
    (OUT / "4090_summary.md").write_text(text, encoding="utf-8")


def parse_obs(text: str) -> list[int]:
    if text == "all":
        return list(range(1, 20))
    return [int(x.strip()) for x in text.split(",") if x.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default=BaseRunConfig.data_dir)
    parser.add_argument("--obs", default="all")
    parser.add_argument("--k", type=int, default=8)
    parser.add_argument("--lag-sec", type=float, default=0.10)
    parser.add_argument("--frame-stride", type=int, default=100)
    parser.add_argument("--max-focals", type=int, default=8)
    parser.add_argument("--c-bins", type=int, default=4)
    parser.add_argument("--dc-bins", type=int, default=3)
    parser.add_argument("--radius-bins", type=int, default=3)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_dirs()
    write_config(args)
    data_dir = resolve_data_dir(BaseRunConfig(data_dir=args.data_dir))
    obs = parse_obs(args.obs)

    sample = build_or_load_vector_sample(
        data_dir=data_dir,
        obs=obs,
        k=args.k,
        lag_sec=args.lag_sec,
        frame_stride=args.frame_stride,
        max_focals=args.max_focals,
        force=args.force,
    )
    sample["log_tan_energy"] = np.log1p(sample["resid_tan_energy"].to_numpy(dtype="float64"))
    sample = sample.dropna(
        subset=[
            "C",
            "dCdt",
            "C_shift",
            "dCdt_shift",
            "focal_radius",
            "signed_tan_projection",
            "log_tan_energy",
            "resid_tan_energy",
        ]
    ).reset_index(drop=True)
    sample.to_csv(OUT / "vector_moment_samples.csv.gz", index=False, compression="gzip")

    oos = evaluate_grouped_oos(sample, c_bins=args.c_bins, dc_bins=args.dc_bins, radius_bins=args.radius_bins)
    metrics = primary_metrics(oos)
    profiles = state_profiles(sample, c_bins=args.c_bins, dc_bins=args.dc_bins, radius_bins=args.radius_bins)
    effects = dataset_effects(sample)
    null = oos[
        [
            "heldout_ob",
            "target_family",
            "target",
            "incremental_r2_shift_vs_radius",
            "real_minus_shift_incremental_r2",
        ]
    ].copy()
    decision = classify(metrics)
    make_figures(oos, effects, profiles)

    write_csv(OUT / "grouped_oos_results.csv", oos.to_dict("records"), OOS_COLUMNS)
    write_csv(OUT / "tables" / "grouped_oos_results.csv", oos.to_dict("records"), OOS_COLUMNS)
    write_csv(OUT / "primary_metrics.csv", metrics.to_dict("records"), PRIMARY_METRIC_COLUMNS)
    write_csv(OUT / "tables" / "primary_metrics.csv", metrics.to_dict("records"), PRIMARY_METRIC_COLUMNS)
    write_csv(OUT / "state_bin_profiles.csv", profiles.to_dict("records"), PROFILE_COLUMNS)
    write_csv(OUT / "tables" / "state_bin_profiles.csv", profiles.to_dict("records"), PROFILE_COLUMNS)
    write_csv(OUT / "dataset_level_effects.csv", effects.to_dict("records"), DATASET_EFFECT_COLUMNS)
    write_csv(OUT / "tables" / "dataset_level_effects.csv", effects.to_dict("records"), DATASET_EFFECT_COLUMNS)
    write_csv(OUT / "null_results.csv", null.to_dict("records"), list(null.columns))
    write_csv(OUT / "tables" / "null_results.csv", null.to_dict("records"), list(null.columns))
    write_json(OUT / "primary_metrics.json", metrics.to_dict("records"))
    write_json(OUT / "decision.json", decision)
    write_summary(sample=sample, oos=oos, metrics=metrics, effects=effects, profiles=profiles, decision=decision)

    print(json.dumps(to_jsonable(decision), ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
