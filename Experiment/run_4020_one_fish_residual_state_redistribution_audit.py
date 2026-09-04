#!/usr/bin/env python3
"""Experiment 4020: one-fish residual state redistribution pilot.

4020 follows the 4003 synthesis. Instead of asking whether neighboring fish have
robust pair-level cumulants, it asks whether affine-residual one-fish states are
redistributed across core/mid/edge regions around compact-density transitions.

This is intentionally a pilot-first node. By default it runs only Ob1 and uses a
screening-scale shifted-event null. Full 19-observation runs should be reserved
for nodes that pass the pilot gate with a clear, interpretable signal.
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

from run_4001_geometric_baseline_residual_audit import (
    fit_affine_frame,
    finite_median,
    median_dt,
    read_events,
    read_raw_ob,
    resolve_data_dir,
    safe_float,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4020"
FIG = OUT / "figures"
TAB = OUT / "tables"
PROC = OUT / "processed"

RNG_SEED = 402001

STATE_FAMILIES = {
    "edge_energy_share": "residual_energy_distribution",
    "core_energy_share": "residual_energy_distribution",
    "edge_minus_core_energy_share": "residual_energy_distribution",
    "edge_minus_core_speed_mean": "shell_residual_speed",
    "edge_minus_core_speed_q75": "shell_residual_speed",
    "edge_minus_core_tangential_mean": "shell_tangential_state",
    "edge_minus_core_tangential_q75": "shell_tangential_state",
    "edge_minus_core_radial_abs_mean": "shell_radial_state",
    "edge_minus_core_radial_abs_q75": "shell_radial_state",
    "edge_minus_core_radial_signed_mean": "shell_radial_state",
    "edge_high_speed_fraction_minus_core": "high_residual_fish_location",
    "top_speed_radius_mean_z": "high_residual_fish_location",
    "top_tangential_radius_mean_z": "high_residual_fish_location",
    "resid_speed_gini": "residual_state_concentration",
    "resid_energy_shell_entropy": "residual_state_concentration",
}
STATE_VARIABLES = list(STATE_FAMILIES)


@dataclass(frozen=True)
class RunConfig:
    data_dir: str = r"data/raw"
    pilot_ob: int = 1
    smooth_window_sec: float = 1.00
    prepost_window_sec: float = 0.20
    n_null: int = 64
    direction_gap_gate_z: float = 0.15
    null_p_gate: float = 0.15
    min_events_gate: int = 20
    oriented_fraction_gate: float = 0.55
    min_survivors_for_expand: int = 2


def ensure_dirs() -> None:
    for path in (OUT, FIG, TAB, PROC):
        path.mkdir(parents=True, exist_ok=True)


def out_rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


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


def finite_mean(values: Iterable[float]) -> float:
    arr = np.asarray(list(values), dtype="float64")
    arr = arr[np.isfinite(arr)]
    return float(np.mean(arr)) if arr.size else math.nan


def finite_quantile(values: Iterable[float], q: float) -> float:
    arr = np.asarray(list(values), dtype="float64")
    arr = arr[np.isfinite(arr)]
    return float(np.quantile(arr, q)) if arr.size else math.nan


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


def gini(values: np.ndarray) -> float:
    vals = np.asarray(values, dtype="float64")
    vals = vals[np.isfinite(vals)]
    vals = vals[vals >= 0]
    if vals.size < 2:
        return math.nan
    vals = np.sort(vals)
    total = float(np.sum(vals))
    if total <= 1e-12:
        return math.nan
    n = vals.size
    weights = np.arange(1, n + 1, dtype="float64")
    return float((2.0 * np.sum(weights * vals) / (n * total)) - ((n + 1.0) / n))


def shell_masks(radius: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    radius = np.asarray(radius, dtype="float64")
    if not np.isfinite(radius).any():
        empty = np.zeros(radius.shape, dtype=bool)
        return np.full(radius.shape, -1, dtype="int64"), empty, empty, empty
    q33 = float(np.nanquantile(radius, 1.0 / 3.0))
    q67 = float(np.nanquantile(radius, 2.0 / 3.0))
    core = radius <= q33
    mid = (radius > q33) & (radius < q67)
    edge = radius >= q67
    shell = np.full(radius.shape, -1, dtype="int64")
    shell[core] = 0
    shell[mid] = 1
    shell[edge] = 2
    return shell, core, mid, edge


def mean_or_nan(values: np.ndarray) -> float:
    vals = np.asarray(values, dtype="float64")
    vals = vals[np.isfinite(vals)]
    return float(np.mean(vals)) if vals.size else math.nan


def q75_or_nan(values: np.ndarray) -> float:
    vals = np.asarray(values, dtype="float64")
    vals = vals[np.isfinite(vals)]
    return float(np.quantile(vals, 0.75)) if vals.size else math.nan


def share_or_nan(values: np.ndarray, mask: np.ndarray) -> float:
    vals = np.asarray(values, dtype="float64")
    good = np.isfinite(vals) & mask
    total = float(np.nansum(vals[np.isfinite(vals)]))
    if total <= 1e-12 or not np.any(good):
        return math.nan
    return float(np.nansum(vals[good]) / total)


def normalized_entropy(proportions: np.ndarray) -> float:
    p = np.asarray(proportions, dtype="float64")
    p = p[np.isfinite(p) & (p > 0)]
    if p.size == 0:
        return math.nan
    p = p / np.sum(p)
    return float(-np.sum(p * np.log(p)) / math.log(3.0))


def frame_one_fish_state_metrics(relative_pos: np.ndarray, resid_velocity: np.ndarray) -> dict[str, float]:
    n = int(len(relative_pos))
    radius = np.linalg.norm(relative_pos, axis=1)
    shell, core, _mid, edge = shell_masks(radius)
    speed_sq = np.sum(resid_velocity * resid_velocity, axis=1)
    speed = np.sqrt(np.maximum(speed_sq, 0.0))

    radial = np.full(n, np.nan, dtype="float64")
    valid_r = radius > 1e-12
    radial[valid_r] = np.sum(relative_pos[valid_r] * resid_velocity[valid_r], axis=1) / radius[valid_r]
    radial_abs = np.abs(radial)
    tangential_sq = np.maximum(speed_sq - np.nan_to_num(radial, nan=0.0) ** 2, 0.0)
    tangential = np.sqrt(tangential_sq)

    radius_z = robust_z_safe(radius)
    high_speed = speed >= finite_quantile(speed, 0.75)
    high_tangential = tangential >= finite_quantile(tangential, 0.75)

    shell_energy = np.array(
        [
            np.nansum(speed_sq[core]),
            np.nansum(speed_sq[shell == 1]),
            np.nansum(speed_sq[edge]),
        ],
        dtype="float64",
    )
    total_energy = float(np.nansum(speed_sq))
    energy_prop = shell_energy / total_energy if total_energy > 1e-12 else np.full(3, np.nan)

    edge_high_frac = mean_or_nan(high_speed[edge].astype("float64")) if np.any(edge) else math.nan
    core_high_frac = mean_or_nan(high_speed[core].astype("float64")) if np.any(core) else math.nan

    return {
        "edge_energy_share": share_or_nan(speed_sq, edge),
        "core_energy_share": share_or_nan(speed_sq, core),
        "edge_minus_core_energy_share": energy_prop[2] - energy_prop[0]
        if np.isfinite(energy_prop[2]) and np.isfinite(energy_prop[0])
        else math.nan,
        "edge_minus_core_speed_mean": mean_or_nan(speed[edge]) - mean_or_nan(speed[core])
        if np.any(edge) and np.any(core)
        else math.nan,
        "edge_minus_core_speed_q75": q75_or_nan(speed[edge]) - q75_or_nan(speed[core])
        if np.any(edge) and np.any(core)
        else math.nan,
        "edge_minus_core_tangential_mean": mean_or_nan(tangential[edge]) - mean_or_nan(tangential[core])
        if np.any(edge) and np.any(core)
        else math.nan,
        "edge_minus_core_tangential_q75": q75_or_nan(tangential[edge]) - q75_or_nan(tangential[core])
        if np.any(edge) and np.any(core)
        else math.nan,
        "edge_minus_core_radial_abs_mean": mean_or_nan(radial_abs[edge]) - mean_or_nan(radial_abs[core])
        if np.any(edge) and np.any(core)
        else math.nan,
        "edge_minus_core_radial_abs_q75": q75_or_nan(radial_abs[edge]) - q75_or_nan(radial_abs[core])
        if np.any(edge) and np.any(core)
        else math.nan,
        "edge_minus_core_radial_signed_mean": mean_or_nan(radial[edge]) - mean_or_nan(radial[core])
        if np.any(edge) and np.any(core)
        else math.nan,
        "edge_high_speed_fraction_minus_core": edge_high_frac - core_high_frac
        if np.isfinite(edge_high_frac) and np.isfinite(core_high_frac)
        else math.nan,
        "top_speed_radius_mean_z": mean_or_nan(radius_z[high_speed]),
        "top_tangential_radius_mean_z": mean_or_nan(radius_z[high_tangential]),
        "resid_speed_gini": gini(speed),
        "resid_energy_shell_entropy": normalized_entropy(energy_prop),
    }


def frame_state_metrics_for_ob(ob: int, dataset: str, data_dir: Path) -> pd.DataFrame:
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
            "affine_residual_rms_fraction": safe_float(fit["affine_residual_rms_fraction"]),
        }
        row.update(frame_one_fish_state_metrics(fit["relative_pos"], fit["affine_resid"]))
        rows.append(row)
    return pd.DataFrame(rows).sort_values("t", kind="mergesort").reset_index(drop=True)


def add_residualized_metrics(frame: pd.DataFrame, cfg: RunConfig) -> pd.DataFrame:
    d = frame.sort_values("t").reset_index(drop=True).copy()
    dt = median_dt(d["t"].to_numpy(dtype="float64"))
    win = max(5, int(round(cfg.smooth_window_sec / dt))) if np.isfinite(dt) and dt > 0 else 101
    if win % 2 == 0:
        win += 1
    min_periods = max(3, win // 5)
    for var in STATE_VARIABLES:
        z = robust_z_safe(d[var])
        smooth = (
            pd.Series(z)
            .rolling(win, center=True, min_periods=min_periods)
            .mean()
            .interpolate(limit_direction="both")
            .to_numpy(dtype="float64")
        )
        resid = z - smooth
        d[f"{var}__z4020"] = z
        d[f"{var}__smooth4020"] = smooth
        d[f"{var}__resid4020"] = robust_z_safe(resid)
    return d


def build_arrays(frame: pd.DataFrame) -> dict[tuple[int, str], dict[str, np.ndarray]]:
    arrays: dict[tuple[int, str], dict[str, np.ndarray]] = {}
    for (ob, dataset), d0 in frame.groupby(["ob", "dataset"], sort=True):
        d = d0.sort_values("t").reset_index(drop=True)
        rec: dict[str, np.ndarray] = {"t": d["t"].to_numpy(dtype="float64")}
        for var in STATE_VARIABLES:
            rec[var] = d[f"{var}__resid4020"].to_numpy(dtype="float64")
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
        for var in STATE_VARIABLES:
            x = rec[var]
            pre = x[p0:p1]
            post = x[q0:q1]
            if not np.isfinite(pre).any() or not np.isfinite(post).any():
                continue
            pre_mean = safe_float(np.nanmean(pre))
            post_mean = safe_float(np.nanmean(post))
            delta = post_mean - pre_mean if np.isfinite(pre_mean) and np.isfinite(post_mean) else math.nan
            event_type = str(event.event_type)
            orient = 1.0 if event_type == "low_to_high" else -1.0 if event_type == "high_to_low" else math.nan
            rows.append(
                {
                    "event_id": int(event.event_id),
                    "ob": int(event.ob),
                    "dataset": str(event.dataset),
                    "event_t": event_t,
                    "event_type": event_type,
                    "variable": var,
                    "family": STATE_FAMILIES[var],
                    "pre_mean_resid_z": pre_mean,
                    "post_mean_resid_z": post_mean,
                    "signed_delta_post_minus_pre_z": delta,
                    "oriented_delta_z": delta * orient if np.isfinite(delta) and np.isfinite(orient) else math.nan,
                }
            )
    return pd.DataFrame(rows)


def summarize_direction(features: pd.DataFrame, prefix: str = "real") -> pd.DataFrame:
    if features.empty:
        return pd.DataFrame()
    keep = features[features["event_type"].isin(["low_to_high", "high_to_low"])].copy()
    rows = []
    for (variable, family), d in keep.groupby(["variable", "family"], sort=True):
        low = d.loc[d["event_type"] == "low_to_high", "signed_delta_post_minus_pre_z"].to_numpy(dtype="float64")
        high = d.loc[d["event_type"] == "high_to_low", "signed_delta_post_minus_pre_z"].to_numpy(dtype="float64")
        oriented = d["oriented_delta_z"].to_numpy(dtype="float64")
        oriented = oriented[np.isfinite(oriented)]
        low_med = finite_median(low)
        high_med = finite_median(high)
        contrast = low_med - high_med if np.isfinite(low_med) and np.isfinite(high_med) else math.nan
        rows.append(
            {
                "variable": variable,
                "family": family,
                "n_ob": int(d["ob"].nunique()),
                "n_events": int(d["event_id"].nunique()),
                f"{prefix}_median_low_to_high_delta_z": low_med,
                f"{prefix}_median_high_to_low_delta_z": high_med,
                f"{prefix}_median_direction_contrast_z": contrast,
                f"{prefix}_abs_median_direction_contrast_z": abs(contrast) if np.isfinite(contrast) else math.nan,
                f"{prefix}_median_oriented_delta_z": finite_median(oriented),
                f"{prefix}_oriented_positive_fraction": finite_mean((oriented > 0).astype("float64"))
                if oriented.size
                else math.nan,
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


def run_nulls(
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
        if replicate == 1 or replicate % 16 == 0 or replicate == cfg.n_null:
            print(f"[4020] shifted null replicate {replicate}/{cfg.n_null}", flush=True)
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
        oriented_fraction = safe_float(rec.real_oriented_positive_fraction)
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
                "real_median_oriented_delta_z": safe_float(rec.real_median_oriented_delta_z),
                "real_oriented_positive_fraction": oriented_fraction,
                "null_abs_median_direction_contrast_z": null_med,
                "real_minus_null_abs_direction_contrast_z": gap,
                "p_null_abs_direction_ge_real": p,
                "pilot_survives_gate": bool(
                    rec.n_events >= cfg.min_events_gate
                    and np.isfinite(gap)
                    and gap >= cfg.direction_gap_gate_z
                    and np.isfinite(p)
                    and p <= cfg.null_p_gate
                    and np.isfinite(oriented_fraction)
                    and oriented_fraction >= cfg.oriented_fraction_gate
                ),
            }
        )
    return pd.DataFrame(rows).sort_values("real_minus_null_abs_direction_contrast_z", ascending=False)


def decision_summary(comparison: pd.DataFrame, cfg: RunConfig) -> pd.DataFrame:
    survivors = comparison[comparison["pilot_survives_gate"]].copy() if not comparison.empty else pd.DataFrame()
    if len(survivors) >= cfg.min_survivors_for_expand:
        decision = "pilot_support_one_fish_residual_state_redistribution_signal"
        next_node = "4020b selective multi-ob expansion"
        boundary = "Single-observation pilot found multiple state-redistribution variables above shifted-event null gates."
    elif len(survivors) == 1:
        decision = "boundary_single_variable_one_fish_state_signal"
        next_node = "pause full run; optionally test one adjacent observation or route to 4030"
        boundary = "Only one variable passed the pilot gate; this is not enough to justify a full 19-observation run."
    else:
        decision = "weak_one_fish_residual_state_redistribution_pilot"
        next_node = "4030 coarse-grained stochastic state transition pilot"
        boundary = "No one-fish residual state redistribution variable passes the single-observation pilot gate."

    families: dict[str, list[str]] = {}
    if not survivors.empty:
        for family, d in survivors.groupby("family", sort=True):
            families[family] = d["variable"].astype(str).tolist()

    return pd.DataFrame(
        [
            {
                "node_id": "4020_one_fish_residual_state_redistribution_audit",
                "node_type": "single-observation pilot screen",
                "pilot_ob": int(cfg.pilot_ob),
                "n_surviving_variables": int(len(survivors)),
                "surviving_variables": ", ".join(survivors["variable"].astype(str).tolist()) if not survivors.empty else "",
                "surviving_families": "; ".join(f"{k}: {', '.join(v)}" for k, v in families.items()),
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
        samples = []
        for event in events.itertuples(index=False):
            rec = arrays.get((int(event.ob), str(event.dataset)))
            if rec is None:
                continue
            sign = 1.0 if str(event.event_type) == "low_to_high" else -1.0 if str(event.event_type) == "high_to_low" else math.nan
            if not np.isfinite(sign):
                continue
            t = rec["t"]
            x = rec[var] * sign
            target = float(event.event_t) + rel_grid
            valid = (target >= np.nanmin(t)) & (target <= np.nanmax(t))
            y = np.full(rel_grid.shape, np.nan, dtype="float64")
            if np.any(valid):
                y[valid] = np.interp(target[valid], t, x)
            samples.append(y)
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
                    "family": STATE_FAMILIES[var],
                    "relative_time_sec": float(rel_t),
                    "median_aligned_resid_z": safe_float(m),
                    "q25_aligned_resid_z": safe_float(lo),
                    "q75_aligned_resid_z": safe_float(hi),
                    "n_events": int(len(samples)),
                }
            )
    return pd.DataFrame(rows)


def make_figures(comparison: pd.DataFrame, profiles: pd.DataFrame) -> None:
    if not comparison.empty:
        d = comparison.sort_values("real_minus_null_abs_direction_contrast_z", ascending=True)
        colors = {
            "residual_energy_distribution": "#4c78a8",
            "shell_residual_speed": "#5f8f3d",
            "shell_tangential_state": "#b55d60",
            "shell_radial_state": "#8b6f2d",
            "high_residual_fish_location": "#6b5a8e",
            "residual_state_concentration": "#5a7184",
        }
        fig, ax = plt.subplots(figsize=(9.2, max(4.6, 0.36 * len(d) + 1.6)))
        y = np.arange(len(d))
        bar_colors = [colors.get(f, "#666666") for f in d["family"]]
        bars = ax.barh(y, d["real_minus_null_abs_direction_contrast_z"], color=bar_colors, alpha=0.88)
        for bar, gate in zip(bars, d["pilot_survives_gate"]):
            if bool(gate):
                ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, " *", va="center", ha="left", fontsize=12)
        ax.axvline(0.0, color="#222222", linewidth=0.8)
        ax.axvline(0.15, color="#777777", linewidth=0.7, linestyle="--")
        ax.set_yticks(y)
        ax.set_yticklabels(d["variable"])
        ax.set_xlabel("real - shifted-null direction contrast (pilot z)")
        ax.set_title("4020 one-fish residual state redistribution pilot")
        fig.tight_layout()
        fig.savefig(FIG / "one_fish_state_direction_screen.png", dpi=180)
        plt.close(fig)

    if not profiles.empty:
        variables = list(dict.fromkeys(profiles["variable"].tolist()))
        fig, axes = plt.subplots(len(variables), 1, figsize=(8.8, max(3.0, 2.2 * len(variables))), sharex=True)
        if len(variables) == 1:
            axes = [axes]
        for ax, var in zip(axes, variables):
            d = profiles[profiles["variable"] == var].sort_values("relative_time_sec")
            ax.plot(d["relative_time_sec"], d["median_aligned_resid_z"], color="#4c78a8", lw=1.7)
            ax.fill_between(d["relative_time_sec"], d["q25_aligned_resid_z"], d["q75_aligned_resid_z"], color="#4c78a8", alpha=0.16)
            ax.axvline(0.0, color="#222222", linewidth=0.8)
            ax.axhline(0.0, color="#999999", linewidth=0.7)
            ax.set_ylabel(var)
            ax.grid(alpha=0.18)
        axes[0].set_title("4020 direction-aligned one-fish state profiles")
        axes[-1].set_xlabel("time relative to transition (sec)")
        fig.tight_layout()
        fig.savefig(FIG / "one_fish_state_aligned_profiles.png", dpi=180)
        plt.close(fig)


def write_node_schema(decision: pd.DataFrame, cfg: RunConfig) -> None:
    rec = decision.iloc[0].to_dict()
    node = {
        "node_id": "4020_one_fish_residual_state_redistribution_audit",
        "series": "4xxx",
        "node_type": "single-observation pilot screen",
        "parent_node": "4003_residual_velocity_synthesis",
        "question": "Are transition-linked affine-residual effects better described as one-fish state redistribution across school regions than as local pair cumulants?",
        "competing_interpretations": [
            "H_state_redistribution: residual speed/radial/tangential states move across core/mid/edge regions around transitions",
            "H_concentration: residual activity becomes concentrated in fewer fish or shells",
            "H_shift_null: shifted event times show comparable one-fish state changes",
            "H_pair_not_needed: one-fish state redistribution is a better next language than local pair cumulants",
        ],
        "input_artifacts": [
            "data/raw/Ob*.txt",
            "Output/3045/tables/transition_events.csv",
            "Output/4003/4003_summary.md",
        ],
        "method": [
            f"run pilot on Ob{cfg.pilot_ob}",
            "fit per-frame affine baseline and compute affine residual velocities",
            "compute one-fish residual state distribution metrics across core/mid/edge shells",
            "remove 1-sec smooth trend and robust-z residualize within the pilot observation",
            f"compare transition events against {cfg.n_null} shifted-event null replicates",
        ],
        "pass_gate": {
            "pilot": f"event count >= {cfg.min_events_gate}, real-null direction gap >= {cfg.direction_gap_gate_z}, p <= {cfg.null_p_gate}, oriented positive fraction >= {cfg.oriented_fraction_gate}",
            "expand": f"at least {cfg.min_survivors_for_expand} variables pass before considering multi-ob expansion",
        },
        "fail_gate": "No variable passes the single-observation pilot gate.",
        "next_if_pass": "4020b selective multi-ob expansion",
        "next_if_fail": "4030 coarse-grained stochastic state transition pilot",
        "outputs": [
            out_rel(TAB / "one_fish_state_direction_null_comparison.csv"),
            out_rel(TAB / "egrt_decision_summary.csv"),
            out_rel(OUT / "4020_summary.md"),
        ],
        "provenance": {"script": "Experiment/run_4020_one_fish_residual_state_redistribution_audit.py", "config": asdict(cfg), "decision": rec},
    }
    (OUT / "4020_egrt_node.json").write_text(json.dumps(node, ensure_ascii=False, indent=2), encoding="utf-8")


def write_summary(comparison: pd.DataFrame, decision: pd.DataFrame, cfg: RunConfig) -> None:
    rec = decision.iloc[0]
    survivors = comparison[comparison["pilot_survives_gate"]].copy() if not comparison.empty else pd.DataFrame()
    top = comparison.sort_values("real_minus_null_abs_direction_contrast_z", ascending=False).head(8) if not comparison.empty else pd.DataFrame()
    text = f"""# 4020 One-Fish Residual State Redistribution Pilot

## Scope

4020 follows `4003_residual_velocity_synthesis`. It uses the new pilot-first
rule and runs only `Ob{cfg.pilot_ob}` by default.

Plain-language question:

> After removing ordinary group geometry, do the fish with stronger residual
> speed/radial/tangential states shift across core/mid/edge regions around
> compact-density transitions?

## EGRT Node

| field | value |
| --- | --- |
| node_id | 4020_one_fish_residual_state_redistribution_audit |
| parent | 4003_residual_velocity_synthesis |
| node_type | single-observation pilot screen |
| pilot observation | Ob{cfg.pilot_ob} |
| decision | {rec.eg_rt_decision} |
| recommended next node | {rec.recommended_next_node} |
| boundary reading | {rec.boundary_reading} |

## Methods

- Fit the per-frame affine geometric baseline.
- Compute one-fish affine residual states.
- Split fish into core/mid/edge radial shells.
- Measure residual energy shares, edge-core residual state differences, top
  residual-fish location, and residual concentration.
- Remove a `{cfg.smooth_window_sec}` sec smooth trend within the pilot
  observation.
- Compare transition post-minus-pre direction contrasts against `{cfg.n_null}`
  shifted-event null replicates.

Pilot gate:

- event count >= `{cfg.min_events_gate}`;
- real-null direction gap >= `{cfg.direction_gap_gate_z}`;
- shifted-null p <= `{cfg.null_p_gate}`;
- oriented positive event fraction >= `{cfg.oriented_fraction_gate}`;
- at least `{cfg.min_survivors_for_expand}` survivors needed before multi-ob
  expansion.

## Decision Metrics

{dataframe_to_markdown(decision)}

## Pilot-Surviving Variables

{dataframe_to_markdown(survivors)}

## Top Direction/Null Rows

{dataframe_to_markdown(top)}

## Interpretation

This is a pilot, not a full-series confirmation. A positive result only
supports expanding selectively. A weak result should be recorded as a boundary
and routed to the next node instead of spending time on a full 19-observation
run.

## Outputs

- `{out_rel(OUT / "4020_egrt_node.json")}`
- `{out_rel(TAB / "one_fish_state_direction_null_comparison.csv")}`
- `{out_rel(TAB / "egrt_decision_summary.csv")}`
- `{out_rel(FIG / "one_fish_state_direction_screen.png")}`
- `{out_rel(FIG / "one_fish_state_aligned_profiles.png")}`
"""
    (OUT / "4020_summary.md").write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default=RunConfig.data_dir)
    parser.add_argument("--pilot-ob", type=int, default=RunConfig.pilot_ob)
    parser.add_argument("--n-null", type=int, default=RunConfig.n_null)
    parser.add_argument("--output-subdir", default="", help="Optional subdirectory under Output/ for this pilot run.")
    parser.add_argument("--quick", action="store_true", help="Use 24 shifted-event null replicates.")
    return parser.parse_args()


def main() -> int:
    global OUT, FIG, TAB, PROC
    args = parse_args()
    if args.output_subdir:
        subdir = Path(args.output_subdir)
        if subdir.is_absolute() or ".." in subdir.parts:
            raise ValueError("--output-subdir must be a safe relative path under Output/")
        OUT = ROOT / "Output" / subdir
        FIG = OUT / "figures"
        TAB = OUT / "tables"
        PROC = OUT / "processed"
    cfg = RunConfig(
        data_dir=args.data_dir,
        pilot_ob=args.pilot_ob,
        n_null=24 if args.quick else args.n_null,
    )
    ensure_dirs()
    pd.DataFrame([asdict(cfg)]).to_csv(PROC / "run_config.csv", index=False)

    events_all = read_events()
    events = events_all[events_all["ob"].astype(int) == int(cfg.pilot_ob)].copy()
    if events.empty:
        raise ValueError(f"No transition events found for Ob{cfg.pilot_ob}")
    data_dir = resolve_data_dir(cfg)
    dataset = str(events["dataset"].iloc[0])
    print(f"[4020] pilot Ob{cfg.pilot_ob}: {len(events)} events", flush=True)

    frame = frame_state_metrics_for_ob(cfg.pilot_ob, dataset, data_dir)
    print(f"[4020] built one-fish state metrics Ob{cfg.pilot_ob}: {len(frame)} frames", flush=True)
    frame = add_residualized_metrics(frame, cfg)
    arrays = build_arrays(frame)

    features = extract_event_features(arrays, events, cfg)
    real_direction = summarize_direction(features, prefix="real")
    null_direction = run_nulls(arrays, events, cfg)
    comparison = compare_direction_to_null(real_direction, null_direction, cfg)
    decision = decision_summary(comparison, cfg)

    profile_vars = comparison.sort_values("real_minus_null_abs_direction_contrast_z", ascending=False)["variable"].astype(str).head(6).tolist()
    profiles = aligned_profiles(arrays, events, profile_vars)
    make_figures(comparison, profiles)

    frame.to_csv(PROC / "frame_one_fish_state_metrics.csv", index=False)
    features.to_csv(TAB / "one_fish_state_event_features.csv", index=False)
    real_direction.to_csv(TAB / "real_one_fish_state_direction_summary.csv", index=False)
    null_direction.to_csv(TAB / "shift_null_one_fish_state_direction_summary.csv", index=False)
    comparison.to_csv(TAB / "one_fish_state_direction_null_comparison.csv", index=False)
    decision.to_csv(TAB / "egrt_decision_summary.csv", index=False)
    if not profiles.empty:
        profiles.to_csv(TAB / "one_fish_state_aligned_profiles.csv", index=False)
    write_node_schema(decision, cfg)
    write_summary(comparison, decision, cfg)

    print(decision.to_string(index=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
