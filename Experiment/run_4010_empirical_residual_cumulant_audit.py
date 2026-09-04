#!/usr/bin/env python3
"""Experiment 4010: empirical residual cumulant audit.

4010 translates the Boltzmann/cumulant reference into an empirical fish-school
test. After subtracting the affine geometric baseline, it asks whether local
neighbor residual-velocity correlations survive a one-fish conditional baseline.

The baseline is computed within each frame and radial shell. It preserves the
single-fish residual distribution in each shell and asks what kNN-pair
correlations would be expected if those one-fish residuals were independently
assigned to fish positions. The empirical cumulant is observed minus expected.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    from scipy.spatial import cKDTree
except Exception:  # pragma: no cover - fallback for minimal environments
    cKDTree = None

from run_4001_geometric_baseline_residual_audit import (
    fit_affine_frame,
    read_events,
    read_raw_ob,
    resolve_data_dir,
    safe_float,
    median_dt,
    finite_median,
    finite_quantile,
    sign_consistency,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4010"
FIG = OUT / "figures"
TAB = OUT / "tables"
PROC = OUT / "processed"

RNG_SEED = 401001

PAIR_METRICS = [
    "knn_resid_alignment",
    "knn_resid_speed_cov",
    "knn_resid_radial_cov",
    "knn_resid_tangential_cov",
]
COMPONENTS = ["observed", "expected", "cumulant"]
METRIC_KEYS = [f"{metric}_{component}" for metric in PAIR_METRICS for component in COMPONENTS]
METRIC_FAMILIES = {
    f"{metric}_observed": "observed_pair" for metric in PAIR_METRICS
} | {
    f"{metric}_expected": "one_fish_conditional_baseline" for metric in PAIR_METRICS
} | {
    f"{metric}_cumulant": "empirical_cumulant" for metric in PAIR_METRICS
}


@dataclass(frozen=True)
class RunConfig:
    data_dir: str = r"data/raw"
    max_ob: int | None = None
    knn_k: int = 6
    n_shells: int = 3
    smooth_window_sec: float = 1.00
    event_window_sec: float = 0.35
    prepost_window_sec: float = 0.20
    n_null: int = 160
    direction_gap_gate_z: float = 0.10
    null_p_gate: float = 0.10
    min_ob_gate: int = 12
    min_cumulant_survivors: int = 2


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
        vals = []
        for col in cols:
            val = row[col]
            if isinstance(val, float):
                vals.append("NA" if not np.isfinite(val) else f"{val:.4g}")
            else:
                vals.append(str(val))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def robust_z_safe(x: pd.Series | np.ndarray) -> np.ndarray:
    arr = pd.to_numeric(pd.Series(x), errors="coerce").to_numpy(dtype="float64")
    finite = arr[np.isfinite(arr)]
    if finite.size < 3:
        return np.full(arr.shape, np.nan, dtype="float64")
    med = float(np.median(finite))
    q25 = float(np.quantile(finite, 0.25))
    q75 = float(np.quantile(finite, 0.75))
    scale = (q75 - q25) / 1.349 if (q75 - q25) > 0 else math.nan
    if not np.isfinite(scale) or scale <= 1e-12:
        scale = float(np.std(finite))
    if not np.isfinite(scale) or scale <= 1e-12:
        return np.full(arr.shape, np.nan, dtype="float64")
    return (arr - med) / scale


def shell_labels(radius: np.ndarray, n_shells: int) -> np.ndarray:
    labels = np.full(radius.shape, -1, dtype="int64")
    valid = np.isfinite(radius)
    if int(valid.sum()) < n_shells:
        return labels
    quantiles = np.quantile(radius[valid], np.linspace(0, 1, n_shells + 1)[1:-1])
    labels[valid] = np.searchsorted(quantiles, radius[valid], side="right")
    return labels


def zscore_within_shell(values: np.ndarray, shells: np.ndarray, n_shells: int) -> np.ndarray:
    out = np.full(values.shape, np.nan, dtype="float64")
    for shell in range(n_shells):
        mask = (shells == shell) & np.isfinite(values)
        if int(mask.sum()) < 3:
            continue
        vals = values[mask]
        sd = float(np.std(vals))
        if not np.isfinite(sd) or sd <= 1e-12:
            continue
        out[mask] = (vals - float(np.mean(vals))) / sd
    return out


def knn_edges(positions: np.ndarray, k: int) -> np.ndarray:
    n = int(len(positions))
    if n <= 1:
        return np.empty((0, 2), dtype="int64")
    kk = max(1, min(k, n - 1))
    if cKDTree is not None:
        tree = cKDTree(positions)
        _, idx = tree.query(positions, k=kk + 1)
        neigh = np.asarray(idx[:, 1:], dtype="int64")
    else:
        diff = positions[:, None, :] - positions[None, :, :]
        dist = np.sum(diff * diff, axis=2)
        np.fill_diagonal(dist, np.inf)
        neigh = np.argpartition(dist, kth=kk - 1, axis=1)[:, :kk]
    edges = set()
    for i in range(n):
        for j in np.asarray(neigh[i]).ravel():
            jj = int(j)
            if jj == i or jj < 0 or jj >= n:
                continue
            a, b = (i, jj) if i < jj else (jj, i)
            edges.add((a, b))
    return np.asarray(sorted(edges), dtype="int64") if edges else np.empty((0, 2), dtype="int64")


def shell_pair_expectations_vector(vectors: np.ndarray, shells: np.ndarray, valid: np.ndarray, n_shells: int) -> tuple[np.ndarray, np.ndarray]:
    mean_vec = np.full((n_shells, vectors.shape[1]), np.nan, dtype="float64")
    same = np.full(n_shells, np.nan, dtype="float64")
    for shell in range(n_shells):
        mask = (shells == shell) & valid
        vals = vectors[mask]
        n = int(len(vals))
        if n < 1:
            continue
        mean_vec[shell] = np.mean(vals, axis=0)
        if n > 1:
            sum_vec = np.sum(vals, axis=0)
            sum_sq = float(np.sum(vals * vals))
            same[shell] = (float(np.dot(sum_vec, sum_vec)) - sum_sq) / (n * (n - 1))
    return mean_vec, same


def shell_pair_expectations_scalar(values: np.ndarray, shells: np.ndarray, n_shells: int) -> tuple[np.ndarray, np.ndarray]:
    mean_val = np.full(n_shells, np.nan, dtype="float64")
    same = np.full(n_shells, np.nan, dtype="float64")
    for shell in range(n_shells):
        mask = (shells == shell) & np.isfinite(values)
        vals = values[mask]
        n = int(len(vals))
        if n < 1:
            continue
        mean_val[shell] = float(np.mean(vals))
        if n > 1:
            s = float(np.sum(vals))
            ss = float(np.sum(vals * vals))
            same[shell] = (s * s - ss) / (n * (n - 1))
    return mean_val, same


def expected_for_edges(shells: np.ndarray, edges: np.ndarray, diff_fn, same_values: np.ndarray) -> np.ndarray:
    vals = np.full(len(edges), np.nan, dtype="float64")
    for idx, (i, j) in enumerate(edges):
        si = int(shells[i])
        sj = int(shells[j])
        if si < 0 or sj < 0:
            continue
        if si == sj:
            vals[idx] = same_values[si]
        else:
            vals[idx] = diff_fn(si, sj)
    return vals


def frame_pair_cumulant_metrics(relative_pos: np.ndarray, resid_velocity: np.ndarray, cfg: RunConfig) -> dict[str, float]:
    n = int(len(relative_pos))
    if n <= cfg.knn_k:
        return {key: math.nan for key in METRIC_KEYS} | {"n_edges": 0}

    radius = np.linalg.norm(relative_pos, axis=1)
    shells = shell_labels(radius, cfg.n_shells)
    edges = knn_edges(relative_pos, cfg.knn_k)
    if len(edges) == 0:
        return {key: math.nan for key in METRIC_KEYS} | {"n_edges": 0}

    speed_sq = np.sum(resid_velocity * resid_velocity, axis=1)
    speed = np.sqrt(np.maximum(speed_sq, 0.0))
    good_speed = speed > 1e-12
    unit = np.full_like(resid_velocity, np.nan, dtype="float64")
    unit[good_speed] = resid_velocity[good_speed] / speed[good_speed, None]

    radial = np.full(n, np.nan, dtype="float64")
    valid_r = radius > 1e-12
    radial[valid_r] = np.sum(relative_pos[valid_r] * resid_velocity[valid_r], axis=1) / radius[valid_r]
    tangential_sq = np.maximum(speed_sq - np.nan_to_num(radial, nan=0.0) ** 2, 0.0)
    tangential = np.sqrt(tangential_sq)

    speed_z = zscore_within_shell(speed, shells, cfg.n_shells)
    radial_z = zscore_within_shell(radial, shells, cfg.n_shells)
    tangential_z = zscore_within_shell(tangential, shells, cfg.n_shells)

    out: dict[str, float] = {"n_edges": int(len(edges))}

    i = edges[:, 0]
    j = edges[:, 1]

    align_obs = np.sum(unit[i] * unit[j], axis=1)
    valid_align_edges = np.isfinite(align_obs)
    mean_vec, same_align = shell_pair_expectations_vector(unit, shells, good_speed, cfg.n_shells)

    def align_diff(a: int, b: int) -> float:
        if not np.isfinite(mean_vec[a]).all() or not np.isfinite(mean_vec[b]).all():
            return math.nan
        return float(np.dot(mean_vec[a], mean_vec[b]))

    align_exp = expected_for_edges(shells, edges, align_diff, same_align)
    out["knn_resid_alignment_observed"] = safe_float(np.nanmean(align_obs[valid_align_edges])) if np.any(valid_align_edges) else math.nan
    out["knn_resid_alignment_expected"] = safe_float(np.nanmean(align_exp[np.isfinite(align_exp)]))
    out["knn_resid_alignment_cumulant"] = out["knn_resid_alignment_observed"] - out["knn_resid_alignment_expected"] if np.isfinite(out["knn_resid_alignment_observed"]) and np.isfinite(out["knn_resid_alignment_expected"]) else math.nan

    for base, values in [
        ("knn_resid_speed_cov", speed_z),
        ("knn_resid_radial_cov", radial_z),
        ("knn_resid_tangential_cov", tangential_z),
    ]:
        prod = values[i] * values[j]
        valid_prod = np.isfinite(prod)
        mean_val, same_val = shell_pair_expectations_scalar(values, shells, cfg.n_shells)

        def diff(a: int, b: int) -> float:
            if not np.isfinite(mean_val[a]) or not np.isfinite(mean_val[b]):
                return math.nan
            return float(mean_val[a] * mean_val[b])

        exp = expected_for_edges(shells, edges, diff, same_val)
        out[f"{base}_observed"] = safe_float(np.nanmean(prod[valid_prod])) if np.any(valid_prod) else math.nan
        out[f"{base}_expected"] = safe_float(np.nanmean(exp[np.isfinite(exp)]))
        out[f"{base}_cumulant"] = out[f"{base}_observed"] - out[f"{base}_expected"] if np.isfinite(out[f"{base}_observed"]) and np.isfinite(out[f"{base}_expected"]) else math.nan

    return out


def frame_cumulant_metrics_for_ob(ob: int, dataset: str, data_dir: Path, cfg: RunConfig) -> pd.DataFrame:
    path = data_dir / dataset
    if not path.exists():
        path = data_dir / f"Ob{int(ob)}.txt"
    df = read_raw_ob(path)
    rows = []
    for t, d in df.groupby("t", sort=True):
        positions = d[["x", "y", "z"]].to_numpy(dtype="float64")
        velocities = d[["vx", "vy", "vz"]].to_numpy(dtype="float64")
        fit = fit_affine_frame(positions, velocities)
        row = {
            "ob": int(ob),
            "dataset": dataset,
            "t": safe_float(t),
            "n": int(len(d)),
            "affine_r2_centered": safe_float(fit["affine_r2_centered"]),
        }
        row.update(frame_pair_cumulant_metrics(fit["relative_pos"], fit["affine_resid"], cfg))
        rows.append(row)
    return pd.DataFrame(rows).sort_values("t", kind="mergesort").reset_index(drop=True)


def build_frame_metrics(events: pd.DataFrame, cfg: RunConfig) -> pd.DataFrame:
    data_dir = resolve_data_dir(cfg)
    parts = []
    for ob, d in events.groupby("ob", sort=True):
        dataset = str(d["dataset"].iloc[0])
        metrics = frame_cumulant_metrics_for_ob(int(ob), dataset, data_dir, cfg)
        parts.append(metrics)
        print(f"[4010] built pair-cumulant metrics Ob{int(ob)}: {len(metrics)} frames", flush=True)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


def add_residualized_metrics(frame: pd.DataFrame, cfg: RunConfig) -> pd.DataFrame:
    parts = []
    for (ob, dataset), d0 in frame.groupby(["ob", "dataset"], sort=True):
        d = d0.sort_values("t").reset_index(drop=True).copy()
        dt = median_dt(d["t"].to_numpy(dtype="float64"))
        win = max(5, int(round(cfg.smooth_window_sec / dt))) if np.isfinite(dt) and dt > 0 else 101
        if win % 2 == 0:
            win += 1
        min_periods = max(3, win // 5)
        for var in METRIC_KEYS:
            z = robust_z_safe(d[var])
            smooth = (
                pd.Series(z)
                .rolling(win, center=True, min_periods=min_periods)
                .mean()
                .interpolate(limit_direction="both")
                .to_numpy(dtype="float64")
            )
            resid = z - smooth
            d[f"{var}__z4010"] = z
            d[f"{var}__smooth4010"] = smooth
            d[f"{var}__resid4010"] = robust_z_safe(resid)
        parts.append(d)
    return pd.concat(parts, ignore_index=True)


def build_arrays(frame: pd.DataFrame) -> dict[tuple[int, str], dict[str, np.ndarray]]:
    arrays: dict[tuple[int, str], dict[str, np.ndarray]] = {}
    for (ob, dataset), d0 in frame.groupby(["ob", "dataset"], sort=True):
        d = d0.sort_values("t").reset_index(drop=True)
        rec: dict[str, np.ndarray] = {"t": d["t"].to_numpy(dtype="float64")}
        for var in METRIC_KEYS:
            rec[var] = d[f"{var}__resid4010"].to_numpy(dtype="float64")
        arrays[(int(ob), str(dataset))] = rec
    return arrays


def extract_event_features(
    arrays: dict[tuple[int, str], dict[str, np.ndarray]],
    events: pd.DataFrame,
    cfg: RunConfig,
) -> pd.DataFrame:
    rows = []
    for event in events.itertuples(index=False):
        rec = arrays.get((int(event.ob), str(event.dataset)))
        if rec is None:
            continue
        t = rec["t"]
        event_t = float(event.event_t)
        p0 = int(np.searchsorted(t, event_t - cfg.prepost_window_sec, side="left"))
        p1 = int(np.searchsorted(t, event_t, side="left"))
        q0 = int(np.searchsorted(t, event_t, side="left"))
        q1 = int(np.searchsorted(t, event_t + cfg.prepost_window_sec, side="right"))
        if p1 <= p0 or q1 <= q0:
            continue
        for var in METRIC_KEYS:
            x = rec[var]
            pre = x[p0:p1]
            post = x[q0:q1]
            if not np.isfinite(pre).any() or not np.isfinite(post).any():
                continue
            pre_mean = safe_float(np.nanmean(pre))
            post_mean = safe_float(np.nanmean(post))
            rows.append(
                {
                    "event_id": int(event.event_id),
                    "ob": int(event.ob),
                    "dataset": str(event.dataset),
                    "event_t": event_t,
                    "event_type": str(event.event_type),
                    "variable": var,
                    "family": METRIC_FAMILIES[var],
                    "pre_mean_resid_z": pre_mean,
                    "post_mean_resid_z": post_mean,
                    "signed_delta_post_minus_pre_z": post_mean - pre_mean
                    if np.isfinite(pre_mean) and np.isfinite(post_mean)
                    else math.nan,
                }
            )
    return pd.DataFrame(rows)


def summarize_direction(features: pd.DataFrame, prefix: str = "real") -> pd.DataFrame:
    if features.empty:
        return pd.DataFrame()
    keep = features[features["event_type"].isin(["low_to_high", "high_to_low"])].copy()
    by_ob_type = (
        keep.groupby(["ob", "variable", "family", "event_type"], as_index=False)
        .agg(
            n_events=("event_id", "nunique"),
            median_signed_delta_z=("signed_delta_post_minus_pre_z", "median"),
        )
        .dropna(subset=["median_signed_delta_z"])
    )
    wide = by_ob_type.pivot_table(
        index=["ob", "variable", "family"],
        columns="event_type",
        values="median_signed_delta_z",
        aggfunc="first",
    ).reset_index()
    if "low_to_high" not in wide or "high_to_low" not in wide:
        return pd.DataFrame()
    wide = wide.dropna(subset=["low_to_high", "high_to_low"]).copy()
    wide["direction_contrast_z"] = wide["low_to_high"] - wide["high_to_low"]
    rows = []
    for (variable, family), d in wide.groupby(["variable", "family"], sort=True):
        rows.append(
            {
                "variable": variable,
                "family": family,
                "n_ob": int(d["ob"].nunique()),
                "n_events": int(by_ob_type[by_ob_type["variable"] == variable]["n_events"].sum()),
                f"{prefix}_median_low_to_high_delta_z": finite_median(d["low_to_high"]),
                f"{prefix}_median_high_to_low_delta_z": finite_median(d["high_to_low"]),
                f"{prefix}_median_direction_contrast_z": finite_median(d["direction_contrast_z"]),
                f"{prefix}_abs_median_direction_contrast_z": abs(finite_median(d["direction_contrast_z"])),
                f"{prefix}_direction_contrast_sign_consistency": sign_consistency(d["direction_contrast_z"]),
            }
        )
    return pd.DataFrame(rows).sort_values(f"{prefix}_abs_median_direction_contrast_z", ascending=False)


def shifted_events(
    events: pd.DataFrame,
    arrays: dict[tuple[int, str], dict[str, np.ndarray]],
    rng: np.random.Generator,
) -> pd.DataFrame:
    parts = []
    for (ob, dataset), d0 in events.groupby(["ob", "dataset"], sort=True):
        rec = arrays.get((int(ob), str(dataset)))
        if rec is None:
            continue
        t = rec["t"]
        if t.size < 2:
            continue
        t_min = float(np.nanmin(t))
        t_max = float(np.nanmax(t))
        span = t_max - t_min
        if not np.isfinite(span) or span <= 0:
            continue
        shift = float(rng.uniform(0.10 * span, 0.90 * span))
        d = d0.copy()
        d["event_t"] = ((pd.to_numeric(d["event_t"], errors="coerce") - t_min + shift) % span) + t_min
        parts.append(d)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


def run_shift_nulls(
    arrays: dict[tuple[int, str], dict[str, np.ndarray]],
    events: pd.DataFrame,
    cfg: RunConfig,
) -> pd.DataFrame:
    rng = np.random.default_rng(RNG_SEED)
    rows = []
    for replicate in range(1, cfg.n_null + 1):
        shifted = shifted_events(events, arrays, rng)
        features = extract_event_features(arrays, shifted, cfg)
        summary = summarize_direction(features, prefix="null")
        summary["replicate"] = int(replicate)
        rows.append(summary)
        if replicate == 1 or replicate % 25 == 0 or replicate == cfg.n_null:
            print(f"[4010] shifted null replicate {replicate}/{cfg.n_null}", flush=True)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def compare_direction_to_null(real: pd.DataFrame, null: pd.DataFrame, cfg: RunConfig) -> pd.DataFrame:
    rows = []
    for rec in real.itertuples(index=False):
        d = null[null["variable"] == rec.variable]
        vals = d["null_abs_median_direction_contrast_z"].to_numpy(dtype="float64") if not d.empty else np.array([])
        vals = vals[np.isfinite(vals)]
        real_abs = safe_float(rec.real_abs_median_direction_contrast_z)
        null_med = float(np.median(vals)) if vals.size else math.nan
        gap = real_abs - null_med if np.isfinite(real_abs) and np.isfinite(null_med) else math.nan
        p = float((1 + np.sum(vals >= real_abs)) / (len(vals) + 1)) if vals.size else math.nan
        sign_cons = safe_float(rec.real_direction_contrast_sign_consistency)
        rows.append(
            {
                "variable": rec.variable,
                "family": rec.family,
                "n_ob": int(rec.n_ob),
                "n_events": int(rec.n_events),
                "real_median_low_to_high_delta_z": safe_float(rec.real_median_low_to_high_delta_z),
                "real_median_high_to_low_delta_z": safe_float(rec.real_median_high_to_low_delta_z),
                "real_median_direction_contrast_z": safe_float(rec.real_median_direction_contrast_z),
                "real_abs_median_direction_contrast_z": real_abs,
                "direction_contrast_sign_consistency": sign_cons,
                "null_abs_median_direction_contrast_z": null_med,
                "real_minus_null_abs_direction_contrast_z": gap,
                "p_null_abs_direction_ge_real": p,
                "direction_survives_gate": bool(
                    rec.n_ob >= cfg.min_ob_gate
                    and np.isfinite(gap)
                    and gap >= cfg.direction_gap_gate_z
                    and np.isfinite(p)
                    and p <= cfg.null_p_gate
                    and sign_cons >= 0.70
                ),
            }
        )
    return pd.DataFrame(rows).sort_values("real_minus_null_abs_direction_contrast_z", ascending=False)


def decision_summary(comparison: pd.DataFrame, cfg: RunConfig) -> pd.DataFrame:
    survivors = comparison[comparison["direction_survives_gate"]].copy() if not comparison.empty else pd.DataFrame()
    cumulant = survivors[survivors["family"] == "empirical_cumulant"].copy() if not survivors.empty else pd.DataFrame()
    observed = survivors[survivors["family"] == "observed_pair"].copy() if not survivors.empty else pd.DataFrame()
    expected = survivors[survivors["family"] == "one_fish_conditional_baseline"].copy() if not survivors.empty else pd.DataFrame()

    if len(cumulant) >= cfg.min_cumulant_survivors:
        decision = "support_empirical_residual_cumulant_signal"
        next_node = "4011 transition molecule graph screen"
        boundary = "Local residual-velocity correlations survive a frame/shell one-fish conditional baseline and shifted-event nulls."
    elif len(cumulant) == 1:
        decision = "boundary_single_empirical_residual_cumulant_variable"
        next_node = "4010b cumulant robustness or narrow 4011 graph screen"
        boundary = "Only one local residual cumulant variable survives; this is suggestive but too narrow for a broad multi-fish correlation claim."
    elif len(observed) >= 1 and len(expected) >= 1:
        decision = "boundary_observed_pair_signal_matches_one_fish_baseline"
        next_node = "pause molecule graph route; synthesize one-fish conditional boundary"
        boundary = "Observed pair signal appears, but it is largely captured by the one-fish conditional baseline."
    elif len(observed) >= 1:
        decision = "boundary_observed_pair_signal_without_cumulant"
        next_node = "pause molecule graph route or refine conditioning"
        boundary = "Observed pair statistics survive, but observed-minus-conditional cumulants do not."
    else:
        decision = "weak_empirical_residual_cumulant_signal"
        next_node = "pause 4010 cumulant route"
        boundary = "No observed or empirical-cumulant pair variable survives shifted-event null gates."

    return pd.DataFrame(
        [
            {
                "node_id": "4010_empirical_residual_cumulant_audit",
                "node_type": "cumulant / factorization audit",
                "n_surviving_variables": int(len(survivors)),
                "n_empirical_cumulant_survivors": int(len(cumulant)),
                "n_observed_pair_survivors": int(len(observed)),
                "n_one_fish_baseline_survivors": int(len(expected)),
                "empirical_cumulant_surviving_variables": ", ".join(cumulant["variable"].astype(str).tolist()) if not cumulant.empty else "",
                "observed_pair_surviving_variables": ", ".join(observed["variable"].astype(str).tolist()) if not observed.empty else "",
                "one_fish_baseline_surviving_variables": ", ".join(expected["variable"].astype(str).tolist()) if not expected.empty else "",
                "eg_rt_decision": decision,
                "recommended_next_node": next_node,
                "boundary_reading": boundary,
            }
        ]
    )


def aligned_profiles(
    arrays: dict[tuple[int, str], dict[str, np.ndarray]],
    events: pd.DataFrame,
    variables: list[str],
) -> pd.DataFrame:
    rel_grid = np.round(np.arange(-0.50, 0.51, 0.05), 5)
    rows = []
    for var in variables:
        samples_by_type: dict[str, list[np.ndarray]] = {"low_to_high": [], "high_to_low": []}
        for event in events.itertuples(index=False):
            event_type = str(event.event_type)
            if event_type not in samples_by_type:
                continue
            rec = arrays.get((int(event.ob), str(event.dataset)))
            if rec is None:
                continue
            t = rec["t"]
            x = rec[var]
            target = float(event.event_t) + rel_grid
            valid = (target >= np.nanmin(t)) & (target <= np.nanmax(t))
            y = np.full(rel_grid.shape, np.nan, dtype="float64")
            if np.any(valid):
                y[valid] = np.interp(target[valid], t, x)
            samples_by_type[event_type].append(y)
        for event_type, samples in samples_by_type.items():
            if not samples:
                continue
            mat = np.vstack(samples)
            med = np.nanmedian(mat, axis=0)
            q25 = np.nanquantile(mat, 0.25, axis=0)
            q75 = np.nanquantile(mat, 0.75, axis=0)
            for rel_t, m, lo, hi in zip(rel_grid, med, q25, q75):
                rows.append(
                    {
                        "variable": var,
                        "family": METRIC_FAMILIES[var],
                        "event_type": event_type,
                        "relative_time_sec": float(rel_t),
                        "median_resid_z": safe_float(m),
                        "q25_resid_z": safe_float(lo),
                        "q75_resid_z": safe_float(hi),
                        "n_events": int(len(samples)),
                    }
                )
    return pd.DataFrame(rows)


def make_figures(comparison: pd.DataFrame, profiles: pd.DataFrame) -> None:
    if not comparison.empty:
        d = comparison.sort_values("real_minus_null_abs_direction_contrast_z", ascending=True)
        colors = {
            "observed_pair": "#4c78a8",
            "one_fish_conditional_baseline": "#8b6f2d",
            "empirical_cumulant": "#b55d60",
        }
        fig, ax = plt.subplots(figsize=(9.6, max(4.6, 0.34 * len(d) + 1.6)))
        y = np.arange(len(d))
        bar_colors = [colors.get(f, "#666666") for f in d["family"]]
        bars = ax.barh(y, d["real_minus_null_abs_direction_contrast_z"], color=bar_colors, alpha=0.88)
        for bar, gate in zip(bars, d["direction_survives_gate"]):
            if bool(gate):
                ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, " *", va="center", ha="left", fontsize=12)
        ax.axvline(0.0, color="#222222", linewidth=0.8)
        ax.axvline(0.10, color="#777777", linewidth=0.7, linestyle="--")
        ax.set_yticks(y)
        ax.set_yticklabels(d["variable"])
        ax.set_xlabel("real - shifted-null direction contrast (z)")
        ax.set_title("4010 observed, one-fish baseline, and empirical cumulant signals")
        fig.tight_layout()
        fig.savefig(FIG / "empirical_cumulant_direction_screen.png", dpi=180)
        plt.close(fig)

    if not profiles.empty:
        variables = list(dict.fromkeys(profiles["variable"].tolist()))
        fig, axes = plt.subplots(len(variables), 1, figsize=(8.8, max(3.0, 2.35 * len(variables))), sharex=True)
        if len(variables) == 1:
            axes = [axes]
        colors = {"low_to_high": "#4c78a8", "high_to_low": "#b55d60"}
        for ax, var in zip(axes, variables):
            for event_type in ["low_to_high", "high_to_low"]:
                d = profiles[(profiles["variable"] == var) & (profiles["event_type"] == event_type)].sort_values("relative_time_sec")
                if d.empty:
                    continue
                ax.plot(d["relative_time_sec"], d["median_resid_z"], label=event_type, color=colors[event_type], lw=1.7)
            ax.axvline(0.0, color="#222222", linewidth=0.8)
            ax.axhline(0.0, color="#999999", linewidth=0.7)
            ax.set_ylabel(var)
            ax.grid(alpha=0.18)
        axes[0].set_title("4010 event-aligned empirical cumulant profiles")
        axes[0].legend(frameon=False, ncols=2)
        axes[-1].set_xlabel("time relative to transition (sec)")
        fig.tight_layout()
        fig.savefig(FIG / "empirical_cumulant_aligned_profiles.png", dpi=180)
        plt.close(fig)


def write_node_schema(decision: pd.DataFrame, cfg: RunConfig) -> None:
    rec = decision.iloc[0].to_dict()
    node = {
        "node_id": "4010_empirical_residual_cumulant_audit",
        "series": "4xxx / Boltzmann-inspired cumulant branch",
        "node_type": "cumulant / factorization audit",
        "parent_node": "4004_boltzmann_molecule_cumulant_reframe",
        "question": "Do local affine-residual velocity correlations survive a one-fish conditional factorized baseline?",
        "competing_interpretations": [
            "H_cumulant: transition-linked residual signal includes multi-fish pair correlations",
            "H_one_fish: transition-linked pair statistics are explained by shell-conditioned one-fish residual distributions",
            "H_shift_null: shifted event times show comparable cumulant changes",
        ],
        "input_artifacts": [
            "data/raw/Ob*.txt",
            "Output/3045/tables/transition_events.csv",
            "idea/4004_boltzmann_molecule_cumulant_reframe.md",
        ],
        "method": [
            "fit per-frame affine baseline and compute affine residual velocity",
            f"build undirected kNN graph with k={cfg.knn_k}",
            f"condition one-fish residual distributions on {cfg.n_shells} radial shells within each frame",
            "compute observed pair statistic, one-fish conditional expectation, and empirical cumulant",
            f"compare transition events against {cfg.n_null} shifted-event null replicates",
        ],
        "outputs": [
            "Output/4010/tables/empirical_cumulant_direction_null_comparison.csv",
            "Output/4010/tables/egrt_decision_summary.csv",
            "Output/4010/4010_summary.md",
        ],
        "provenance": {"script": "Experiment/run_4010_empirical_residual_cumulant_audit.py", "config": asdict(cfg), "decision": rec},
    }
    (OUT / "4010_egrt_node.json").write_text(json.dumps(node, ensure_ascii=False, indent=2), encoding="utf-8")


def write_summary(comparison: pd.DataFrame, decision: pd.DataFrame, cfg: RunConfig) -> None:
    rec = decision.iloc[0]
    survivors = comparison[comparison["direction_survives_gate"]].copy() if not comparison.empty else pd.DataFrame()
    text = f"""# 4010 Empirical Residual Cumulant Audit

## Scope

4010 translates the Boltzmann molecule/cumulant reference into an empirical
fish-school test. It asks whether affine-residual velocity correlations survive
a one-fish conditional baseline.

Plain-language question:

> If we preserve what individual fish residual velocities look like in each
> radial shell of each frame, do real neighboring fish still show extra
> transition-linked correlation?

## EGRT Node

| field | value |
| --- | --- |
| node_id | 4010_empirical_residual_cumulant_audit |
| parent | 4004_boltzmann_molecule_cumulant_reframe |
| node_type | cumulant / factorization audit |
| decision | {rec['eg_rt_decision']} |
| recommended next node | {rec['recommended_next_node']} |
| boundary reading | {rec['boundary_reading']} |

## Methods

- Per frame, fit the affine geometric baseline and compute residual velocities.
- Build an undirected kNN spatial graph with `k={cfg.knn_k}`.
- Split fish into `{cfg.n_shells}` radial shells within each frame.
- For each local pair metric, compute:
  - observed kNN pair statistic;
  - expected value under shell-conditioned one-fish independence;
  - empirical cumulant = observed - expected.
- Slow-trend remove metrics within each observation.
- Compare transition post-minus-pre direction contrasts against `{cfg.n_null}`
  shifted-event null replicates.

## Decision Metrics

{dataframe_to_markdown(decision)}

## Surviving Variables

{dataframe_to_markdown(survivors)}

## Full Direction Null Comparison

{dataframe_to_markdown(comparison)}

## Interpretation

If empirical cumulants survive, the transition-linked residual signal is not
just a one-fish shell-distribution effect. This supports moving toward
interaction-history graph tests. If observed pair statistics survive but
cumulants do not, the molecule-graph route should pause.

## Outputs

- `Output/4010/4010_egrt_node.json`
- `Output/4010/tables/empirical_cumulant_direction_null_comparison.csv`
- `Output/4010/tables/egrt_decision_summary.csv`
- `Output/4010/figures/empirical_cumulant_direction_screen.png`
- `Output/4010/figures/empirical_cumulant_aligned_profiles.png`
"""
    (OUT / "4010_summary.md").write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default=RunConfig.data_dir)
    parser.add_argument("--max-ob", type=int, default=None)
    parser.add_argument("--n-null", type=int, default=RunConfig.n_null)
    parser.add_argument("--min-ob-gate", type=int, default=RunConfig.min_ob_gate)
    parser.add_argument("--quick", action="store_true", help="Use 40 shifted-event null replicates.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cfg = RunConfig(
        data_dir=args.data_dir,
        max_ob=args.max_ob,
        n_null=40 if args.quick else args.n_null,
        min_ob_gate=args.min_ob_gate,
    )
    ensure_dirs()
    events = read_events()
    if cfg.max_ob is not None and cfg.max_ob > 0:
        keep_obs = sorted(events["ob"].unique().tolist())[: cfg.max_ob]
        events = events[events["ob"].isin(keep_obs)].copy().reset_index(drop=True)
        print(f"[4010] smoke-test observation limit: {keep_obs}", flush=True)
    print(f"[4010] events: {len(events)}", flush=True)
    frame_raw = build_frame_metrics(events, cfg)
    frame = add_residualized_metrics(frame_raw, cfg)
    arrays = build_arrays(frame)
    features = extract_event_features(arrays, events, cfg)
    real_direction = summarize_direction(features, prefix="real")
    null_direction = run_shift_nulls(arrays, events, cfg)
    comparison = compare_direction_to_null(real_direction, null_direction, cfg)
    decision = decision_summary(comparison, cfg)
    profile_vars = (
        comparison[comparison["direction_survives_gate"] & (comparison["family"] == "empirical_cumulant")]
        .sort_values("real_minus_null_abs_direction_contrast_z", ascending=False)["variable"]
        .astype(str)
        .head(6)
        .tolist()
    )
    if not profile_vars:
        profile_vars = (
            comparison[comparison["family"] == "empirical_cumulant"]
            .sort_values("real_minus_null_abs_direction_contrast_z", ascending=False)["variable"]
            .astype(str)
            .head(4)
            .tolist()
        )
    profiles = aligned_profiles(arrays, events, profile_vars)

    keep_cols = ["ob", "dataset", "t", "n", "n_edges", "affine_r2_centered"]
    keep_cols.extend([f"{var}__resid4010" for var in METRIC_KEYS])
    frame[[col for col in keep_cols if col in frame.columns]].to_csv(PROC / "frame_empirical_cumulant_metrics.csv", index=False)
    features.to_csv(TAB / "empirical_cumulant_event_features.csv", index=False)
    real_direction.to_csv(TAB / "real_empirical_cumulant_direction_summary.csv", index=False)
    null_direction.to_csv(TAB / "shift_null_empirical_cumulant_direction_summary.csv", index=False)
    comparison.to_csv(TAB / "empirical_cumulant_direction_null_comparison.csv", index=False)
    decision.to_csv(TAB / "egrt_decision_summary.csv", index=False)
    profiles.to_csv(TAB / "empirical_cumulant_aligned_profiles.csv", index=False)
    pd.DataFrame([asdict(cfg)]).to_csv(PROC / "run_config.csv", index=False)

    make_figures(comparison, profiles)
    write_node_schema(decision, cfg)
    write_summary(comparison, decision, cfg)
    print(decision.to_string(index=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
