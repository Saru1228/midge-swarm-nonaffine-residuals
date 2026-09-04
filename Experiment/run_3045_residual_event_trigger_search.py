#!/usr/bin/env python3
"""Experiment 3045: residual event-trigger search.

This EGRT node follows the 3042b boundary. It does not ask whether the full
compact-density/radial-density mode is a mechanism. Instead it removes slow
within-ob trends and asks whether persistent compact-density transitions align
with short-lived residual shocks that could justify a targeted mechanism branch.
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


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "3045"
FIG = OUT / "figures"
TAB = OUT / "tables"
PROC = OUT / "processed"

FRAME_3041B = ROOT / "Output" / "3041b" / "processed" / "frame_macrostate_candidates.csv"

STATE_ORDER = ["low", "high"]
RNG_SEED = 304505

SIGNAL_FAMILIES = {
    "density_rms": "label_basis",
    "r_rms": "label_basis",
    "anisotropy": "label_basis",
    "euclid_radius_mean": "radial_geometry",
    "euclid_outer_inner_balance": "radial_geometry",
    "shape_anisotropy_log": "shape_geometry",
    "aniso_outer_inner_balance": "shape_geometry",
    "center_speed": "kinematic_proxy",
    "radial_velocity_mean": "kinematic_proxy",
    "n": "membership_artifact_proxy",
}
SIGNALS = list(SIGNAL_FAMILIES)


@dataclass(frozen=True)
class RunConfig:
    smooth_window_sec: float = 1.00
    event_window_sec: float = 0.35
    prepost_window_sec: float = 0.20
    min_run_sec: float = 0.20
    n_null: int = 200
    peak_gap_gate_z: float = 0.15
    direction_gap_gate_z: float = 0.12
    null_p_gate: float = 0.10
    min_total_surviving_variables: int = 2
    min_nonlabel_surviving_variables: int = 1
    min_ob_gate: int = 12


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


def safe_float(value: object) -> float:
    try:
        out = float(value)
    except Exception:
        return math.nan
    return out if np.isfinite(out) else math.nan


def finite_median(values: Iterable[float]) -> float:
    arr = np.asarray(list(values), dtype="float64")
    arr = arr[np.isfinite(arr)]
    return float(np.median(arr)) if arr.size else math.nan


def finite_quantile(values: Iterable[float], q: float) -> float:
    arr = np.asarray(list(values), dtype="float64")
    arr = arr[np.isfinite(arr)]
    return float(np.quantile(arr, q)) if arr.size else math.nan


def sign_consistency(values: Iterable[float], expected_sign: float | None = None) -> float:
    arr = np.asarray(list(values), dtype="float64")
    arr = arr[np.isfinite(arr)]
    signs = np.sign(arr)
    signs = signs[signs != 0]
    if not signs.size:
        return math.nan
    if expected_sign is not None and np.isfinite(expected_sign) and expected_sign != 0:
        return float(np.mean(signs == np.sign(expected_sign)))
    counts = pd.Series(signs).value_counts()
    return float(counts.iloc[0] / signs.size)


def robust_z(x: pd.Series | np.ndarray) -> np.ndarray:
    arr = pd.to_numeric(pd.Series(x), errors="coerce").to_numpy(dtype="float64")
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
    t = pd.to_numeric(d["t"], errors="coerce").to_numpy(dtype="float64")
    t = np.unique(t[np.isfinite(t)])
    if t.size < 2:
        return math.nan
    return safe_float(np.nanmedian(np.diff(t)))


def read_input() -> pd.DataFrame:
    if not FRAME_3041B.exists():
        raise FileNotFoundError(f"Run 3041b first; missing {FRAME_3041B}")
    needed = {"ob", "dataset", "t", "spectral_set", *SIGNALS}
    df = pd.read_csv(FRAME_3041B, usecols=lambda c: c in needed, low_memory=False)
    missing = sorted(needed - set(df.columns))
    if missing:
        raise ValueError(f"Missing columns in {FRAME_3041B}: {missing}")
    for col in ["ob", "t", *SIGNALS]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["ob", "t"]).copy()
    df["ob"] = df["ob"].astype("int64")
    return df.sort_values(["ob", "t"], kind="mergesort").reset_index(drop=True)


def add_residual_signals(df: pd.DataFrame, cfg: RunConfig) -> pd.DataFrame:
    parts = []
    for (ob, dataset), d0 in df.groupby(["ob", "dataset"], sort=True):
        d = d0.sort_values("t").reset_index(drop=True).copy()
        dt = median_dt(d)
        win = max(5, int(round(cfg.smooth_window_sec / dt))) if np.isfinite(dt) and dt > 0 else 101
        if win % 2 == 0:
            win += 1
        min_periods = max(3, win // 5)
        for var in SIGNALS:
            z = robust_z(d[var])
            smooth = (
                pd.Series(z)
                .rolling(win, center=True, min_periods=min_periods)
                .mean()
                .interpolate(limit_direction="both")
                .to_numpy(dtype="float64")
            )
            resid = z - smooth
            d[f"{var}_z3045"] = z
            d[f"{var}_smooth3045"] = smooth
            d[f"{var}_resid3045"] = robust_z(resid)
        parts.append(d)
    return pd.concat(parts, ignore_index=True)


def state_shift_signs(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    known = df[df["spectral_set"].isin(STATE_ORDER)].copy()
    for var in SIGNALS:
        vals = []
        for (_ob, _dataset), d in known.groupby(["ob", "dataset"], sort=True):
            low = d[d["spectral_set"] == "low"][f"{var}_z3045"]
            high = d[d["spectral_set"] == "high"][f"{var}_z3045"]
            if len(low) < 20 or len(high) < 20:
                continue
            vals.append(safe_float(high.mean() - low.mean()))
        med = finite_median(vals)
        rows.append(
            {
                "variable": var,
                "family": SIGNAL_FAMILIES[var],
                "median_state_delta_high_minus_low_z": med,
                "state_delta_sign": int(np.sign(med)) if np.isfinite(med) and med != 0 else 0,
                "state_delta_sign_consistency": sign_consistency(vals),
                "n_ob": int(len(vals)),
            }
        )
    return pd.DataFrame(rows).sort_values("median_state_delta_high_minus_low_z")


def detect_transition_events(df: pd.DataFrame, cfg: RunConfig) -> pd.DataFrame:
    rows = []
    event_id = 0
    for (ob, dataset), d0 in df.groupby(["ob", "dataset"], sort=True):
        d = d0.sort_values("t").reset_index(drop=True)
        dt = median_dt(d)
        if not np.isfinite(dt) or dt <= 0:
            continue
        labels = d["spectral_set"].astype(str).to_numpy(dtype=object)
        times = d["t"].to_numpy(dtype="float64")
        changes = np.r_[True, labels[1:] != labels[:-1]]
        starts = np.where(changes)[0]
        ends = np.r_[starts[1:], len(d)]
        runs = []
        for start, end in zip(starts, ends):
            label = str(labels[start])
            if label not in STATE_ORDER:
                continue
            runs.append(
                {
                    "label": label,
                    "start_idx": int(start),
                    "end_idx": int(end),
                    "start_t": float(times[start]),
                    "end_t": float(times[end - 1]),
                    "duration_sec": float((end - start) * dt),
                    "n_frames": int(end - start),
                }
            )
        for i in range(1, len(runs)):
            prev = runs[i - 1]
            cur = runs[i]
            if prev["label"] == cur["label"]:
                continue
            if prev["duration_sec"] < cfg.min_run_sec or cur["duration_sec"] < cfg.min_run_sec:
                continue
            event_id += 1
            rows.append(
                {
                    "event_id": int(event_id),
                    "ob": int(ob),
                    "dataset": dataset,
                    "event_t": float(cur["start_t"]),
                    "event_type": f"{prev['label']}_to_{cur['label']}",
                    "from_state": prev["label"],
                    "to_state": cur["label"],
                    "prev_duration_sec": float(prev["duration_sec"]),
                    "next_duration_sec": float(cur["duration_sec"]),
                    "dt": float(dt),
                }
            )
    return pd.DataFrame(rows)


def build_ob_arrays(df: pd.DataFrame) -> dict[tuple[int, str], dict[str, np.ndarray]]:
    arrays: dict[tuple[int, str], dict[str, np.ndarray]] = {}
    for (ob, dataset), d0 in df.groupby(["ob", "dataset"], sort=True):
        d = d0.sort_values("t").reset_index(drop=True)
        rec: dict[str, np.ndarray] = {"t": d["t"].to_numpy(dtype="float64")}
        for var in SIGNALS:
            rec[var] = d[f"{var}_resid3045"].to_numpy(dtype="float64")
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
        w0 = int(np.searchsorted(t, event_t - cfg.event_window_sec, side="left"))
        w1 = int(np.searchsorted(t, event_t + cfg.event_window_sec, side="right"))
        p0 = int(np.searchsorted(t, event_t - cfg.prepost_window_sec, side="left"))
        p1 = int(np.searchsorted(t, event_t, side="left"))
        q0 = int(np.searchsorted(t, event_t, side="left"))
        q1 = int(np.searchsorted(t, event_t + cfg.prepost_window_sec, side="right"))
        if w1 <= w0 or p1 <= p0 or q1 <= q0:
            continue
        for var in SIGNALS:
            x = rec[var]
            window = x[w0:w1]
            pre = x[p0:p1]
            post = x[q0:q1]
            if not np.isfinite(window).any() or not np.isfinite(pre).any() or not np.isfinite(post).any():
                continue
            pre_mean = safe_float(np.nanmean(pre))
            post_mean = safe_float(np.nanmean(post))
            delta = post_mean - pre_mean if np.isfinite(pre_mean) and np.isfinite(post_mean) else math.nan
            rows.append(
                {
                    "event_id": int(event.event_id),
                    "ob": int(event.ob),
                    "dataset": str(event.dataset),
                    "event_t": event_t,
                    "event_type": str(event.event_type),
                    "variable": var,
                    "family": SIGNAL_FAMILIES[var],
                    "abs_peak_resid_z": safe_float(np.nanmax(np.abs(window))),
                    "pre_mean_resid_z": pre_mean,
                    "post_mean_resid_z": post_mean,
                    "signed_delta_post_minus_pre_z": delta,
                    "abs_delta_post_minus_pre_z": abs(delta) if np.isfinite(delta) else math.nan,
                }
            )
    return pd.DataFrame(rows)


def summarize_peak(features: pd.DataFrame) -> pd.DataFrame:
    if features.empty:
        return pd.DataFrame()
    by_ob = (
        features.groupby(["ob", "variable", "family"], as_index=False)
        .agg(
            n_events=("event_id", "nunique"),
            median_abs_peak_resid_z=("abs_peak_resid_z", "median"),
            median_abs_delta_post_minus_pre_z=("abs_delta_post_minus_pre_z", "median"),
        )
        .dropna(subset=["median_abs_peak_resid_z"])
    )
    rows = []
    for (var, family), d in by_ob.groupby(["variable", "family"], sort=True):
        rows.append(
            {
                "variable": var,
                "family": family,
                "n_ob": int(d["ob"].nunique()),
                "n_events": int(d["n_events"].sum()),
                "real_median_abs_peak_resid_z": finite_median(d["median_abs_peak_resid_z"]),
                "real_q25_abs_peak_resid_z": finite_quantile(d["median_abs_peak_resid_z"], 0.25),
                "real_q75_abs_peak_resid_z": finite_quantile(d["median_abs_peak_resid_z"], 0.75),
                "real_median_abs_delta_post_minus_pre_z": finite_median(d["median_abs_delta_post_minus_pre_z"]),
            }
        )
    return pd.DataFrame(rows).sort_values("real_median_abs_peak_resid_z", ascending=False)


def summarize_direction(features: pd.DataFrame, shift_signs: pd.DataFrame) -> pd.DataFrame:
    if features.empty:
        return pd.DataFrame()
    keep = features[features["event_type"].isin(["low_to_high", "high_to_low"])].copy()
    if keep.empty:
        return pd.DataFrame()
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
    sign_lookup = dict(zip(shift_signs["variable"], shift_signs["state_delta_sign"]))
    rows = []
    for (var, family), d in wide.groupby(["variable", "family"], sort=True):
        expected = safe_float(sign_lookup.get(var, 0))
        rows.append(
            {
                "variable": var,
                "family": family,
                "n_ob": int(d["ob"].nunique()),
                "expected_low_to_high_sign_from_state_delta": int(np.sign(expected)) if expected else 0,
                "real_median_low_to_high_delta_z": finite_median(d["low_to_high"]),
                "real_median_high_to_low_delta_z": finite_median(d["high_to_low"]),
                "real_median_direction_contrast_z": finite_median(d["direction_contrast_z"]),
                "real_abs_median_direction_contrast_z": abs(finite_median(d["direction_contrast_z"])),
                "direction_contrast_sign_consistency": sign_consistency(d["direction_contrast_z"], expected if expected else None),
            }
        )
    return pd.DataFrame(rows).sort_values("real_abs_median_direction_contrast_z", ascending=False)


def shifted_events(events: pd.DataFrame, arrays: dict[tuple[int, str], dict[str, np.ndarray]], rng: np.random.Generator) -> pd.DataFrame:
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


def compare_peaks_to_null(real_peak: pd.DataFrame, null_peak: pd.DataFrame, cfg: RunConfig) -> pd.DataFrame:
    rows = []
    for rec in real_peak.itertuples(index=False):
        d = null_peak[null_peak["variable"] == rec.variable]
        vals = d["null_median_abs_peak_resid_z"].to_numpy(dtype="float64") if not d.empty else np.array([])
        vals = vals[np.isfinite(vals)]
        real_val = safe_float(rec.real_median_abs_peak_resid_z)
        null_med = float(np.median(vals)) if vals.size else math.nan
        gap = real_val - null_med if np.isfinite(real_val) and np.isfinite(null_med) else math.nan
        p = float((1 + np.sum(vals >= real_val)) / (len(vals) + 1)) if vals.size else math.nan
        rows.append(
            {
                "variable": rec.variable,
                "family": rec.family,
                "n_ob": int(rec.n_ob),
                "n_events": int(rec.n_events),
                "real_median_abs_peak_resid_z": real_val,
                "null_median_abs_peak_resid_z": null_med,
                "real_minus_null_peak_z": gap,
                "p_null_peak_ge_real": p,
                "peak_survives_gate": bool(
                    rec.n_ob >= cfg.min_ob_gate
                    and np.isfinite(gap)
                    and gap >= cfg.peak_gap_gate_z
                    and np.isfinite(p)
                    and p <= cfg.null_p_gate
                ),
            }
        )
    return pd.DataFrame(rows).sort_values("real_minus_null_peak_z", ascending=False)


def compare_direction_to_null(real_direction: pd.DataFrame, null_direction: pd.DataFrame, cfg: RunConfig) -> pd.DataFrame:
    rows = []
    for rec in real_direction.itertuples(index=False):
        d = null_direction[null_direction["variable"] == rec.variable]
        vals = d["null_abs_median_direction_contrast_z"].to_numpy(dtype="float64") if not d.empty else np.array([])
        vals = vals[np.isfinite(vals)]
        real_abs = safe_float(rec.real_abs_median_direction_contrast_z)
        null_med = float(np.median(vals)) if vals.size else math.nan
        gap = real_abs - null_med if np.isfinite(real_abs) and np.isfinite(null_med) else math.nan
        p = float((1 + np.sum(vals >= real_abs)) / (len(vals) + 1)) if vals.size else math.nan
        rows.append(
            {
                "variable": rec.variable,
                "family": rec.family,
                "n_ob": int(rec.n_ob),
                "expected_low_to_high_sign_from_state_delta": int(rec.expected_low_to_high_sign_from_state_delta),
                "real_median_low_to_high_delta_z": safe_float(rec.real_median_low_to_high_delta_z),
                "real_median_high_to_low_delta_z": safe_float(rec.real_median_high_to_low_delta_z),
                "real_median_direction_contrast_z": safe_float(rec.real_median_direction_contrast_z),
                "real_abs_median_direction_contrast_z": real_abs,
                "direction_contrast_sign_consistency": safe_float(rec.direction_contrast_sign_consistency),
                "null_abs_median_direction_contrast_z": null_med,
                "real_minus_null_abs_direction_contrast_z": gap,
                "p_null_abs_direction_ge_real": p,
                "direction_survives_gate": bool(
                    rec.n_ob >= cfg.min_ob_gate
                    and np.isfinite(gap)
                    and gap >= cfg.direction_gap_gate_z
                    and np.isfinite(p)
                    and p <= cfg.null_p_gate
                    and safe_float(rec.direction_contrast_sign_consistency) >= 0.70
                ),
            }
        )
    return pd.DataFrame(rows).sort_values("real_minus_null_abs_direction_contrast_z", ascending=False)


def run_nulls(
    arrays: dict[tuple[int, str], dict[str, np.ndarray]],
    events: pd.DataFrame,
    shift_signs: pd.DataFrame,
    cfg: RunConfig,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(RNG_SEED)
    peak_rows = []
    direction_rows = []
    for replicate in range(1, cfg.n_null + 1):
        shifted = shifted_events(events, arrays, rng)
        features = extract_event_features(arrays, shifted, cfg)
        peak = summarize_peak(features)
        direction = summarize_direction(features, shift_signs)
        for row in peak.to_dict("records"):
            row["replicate"] = int(replicate)
            row["null_median_abs_peak_resid_z"] = row.pop("real_median_abs_peak_resid_z")
            peak_rows.append(row)
        for row in direction.to_dict("records"):
            row["replicate"] = int(replicate)
            row["null_abs_median_direction_contrast_z"] = row.pop("real_abs_median_direction_contrast_z")
            direction_rows.append(row)
        if replicate == 1 or replicate % 25 == 0 or replicate == cfg.n_null:
            print(f"[3045] null replicate {replicate}/{cfg.n_null}", flush=True)
    return pd.DataFrame(peak_rows), pd.DataFrame(direction_rows)


def decision_summary(peak_comparison: pd.DataFrame, direction_comparison: pd.DataFrame, events: pd.DataFrame, cfg: RunConfig) -> pd.DataFrame:
    peak_vars = set(peak_comparison[peak_comparison["peak_survives_gate"]]["variable"]) if not peak_comparison.empty else set()
    direction_vars = set(direction_comparison[direction_comparison["direction_survives_gate"]]["variable"]) if not direction_comparison.empty else set()
    survivors = peak_vars | direction_vars
    nonlabel = {v for v in survivors if SIGNAL_FAMILIES.get(v) != "label_basis"}
    kinematic = {v for v in survivors if SIGNAL_FAMILIES.get(v) == "kinematic_proxy"}
    artifact = {v for v in survivors if SIGNAL_FAMILIES.get(v) == "membership_artifact_proxy"}

    if len(kinematic) >= 1 and len(survivors) >= cfg.min_total_surviving_variables:
        decision = "support_residual_event_route_to_neighbor_exchange"
        next_node = "3045b event-conditioned neighbor-exchange audit"
        boundary = "Persistent compact-density transitions align with residual non-label/kinematic shocks; a targeted raw-trajectory neighbor-exchange audit is justified."
    elif len(nonlabel) >= cfg.min_nonlabel_surviving_variables and len(survivors) >= cfg.min_total_surviving_variables:
        decision = "boundary_residual_geometry_signal_without_kinematic_trigger"
        next_node = "3045b optional, or redesign trigger around raw neighbor exchange"
        boundary = "Residual event alignment extends beyond label-basis variables but does not clearly reach kinematic proxies."
    elif len(survivors) >= cfg.min_total_surviving_variables:
        decision = "boundary_residual_signal_mostly_label_basis"
        next_node = "pause before raw neighbor mechanism; avoid circular label-mechanism claim"
        boundary = "Residual alignment is present mainly in variables close to the state definition, so it is not enough for a mechanism branch."
    else:
        decision = "weak_residual_event_trigger_signal"
        next_node = "pause residual/event route"
        boundary = "Persistent compact-density transitions do not show residual shocks beyond circular-shift event nulls under current variables."

    return pd.DataFrame(
        [
            {
                "node_id": "3045_residual_event_trigger_search",
                "node_type": "screen",
                "n_transition_events": int(len(events)),
                "n_ob_with_events": int(events["ob"].nunique()) if not events.empty else 0,
                "n_peak_surviving_variables": int(len(peak_vars)),
                "n_direction_surviving_variables": int(len(direction_vars)),
                "n_total_surviving_variables": int(len(survivors)),
                "n_nonlabel_surviving_variables": int(len(nonlabel)),
                "n_kinematic_surviving_variables": int(len(kinematic)),
                "n_artifact_surviving_variables": int(len(artifact)),
                "surviving_variables": ", ".join(sorted(survivors)),
                "kinematic_surviving_variables": ", ".join(sorted(kinematic)),
                "artifact_surviving_variables": ", ".join(sorted(artifact)),
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
    cfg: RunConfig,
) -> pd.DataFrame:
    rel_grid = np.round(np.arange(-cfg.event_window_sec, cfg.event_window_sec + 1e-9, 0.05), 5)
    rows = []
    for var in variables:
        for event_type, evs in events.groupby("event_type", sort=True):
            samples = []
            for event in evs.itertuples(index=False):
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
                        "event_type": event_type,
                        "relative_time_sec": float(rel_t),
                        "median_resid_z": safe_float(m),
                        "q25_resid_z": safe_float(lo),
                        "q75_resid_z": safe_float(hi),
                        "n_events": int(len(samples)),
                    }
                )
    return pd.DataFrame(rows)


def make_figures(
    peak_comparison: pd.DataFrame,
    direction_comparison: pd.DataFrame,
    profiles: pd.DataFrame,
) -> None:
    if not peak_comparison.empty:
        d = peak_comparison.sort_values("real_minus_null_peak_z", ascending=True).tail(10)
        fig, ax = plt.subplots(figsize=(8.6, 5.0))
        y = np.arange(len(d))
        ax.barh(y - 0.18, d["real_median_abs_peak_resid_z"], height=0.36, label="real", color="#4c78a8")
        ax.barh(y + 0.18, d["null_median_abs_peak_resid_z"], height=0.36, label="shift null median", color="#999999")
        ax.set_yticks(y)
        ax.set_yticklabels(d["variable"])
        ax.axvline(0.0, color="#222222", linewidth=0.8)
        ax.set_xlabel("event-window abs residual peak (z)")
        ax.set_title("3045 residual event peaks vs shifted-event null")
        ax.legend(frameon=False)
        fig.tight_layout()
        fig.savefig(FIG / "residual_event_peak_vs_shift_null.png", dpi=180)
        plt.close(fig)

    if not direction_comparison.empty:
        d = direction_comparison.sort_values("real_minus_null_abs_direction_contrast_z", ascending=True).tail(10)
        fig, ax = plt.subplots(figsize=(8.6, 5.0))
        colors = ["#2f6f6d" if bool(x) else "#8b6f2d" for x in d["direction_survives_gate"]]
        ax.barh(d["variable"], d["real_median_direction_contrast_z"], color=colors)
        ax.axvline(0.0, color="#222222", linewidth=0.8)
        ax.set_xlabel("(low->high delta) - (high->low delta), residual z")
        ax.set_title("3045 directed residual transition contrast")
        fig.tight_layout()
        fig.savefig(FIG / "residual_direction_contrast.png", dpi=180)
        plt.close(fig)

    if not profiles.empty:
        vars_to_plot = list(dict.fromkeys(profiles["variable"].tolist()))[:4]
        fig, axes = plt.subplots(len(vars_to_plot), 1, figsize=(8.4, max(3.0, 2.4 * len(vars_to_plot))), sharex=True)
        if len(vars_to_plot) == 1:
            axes = [axes]
        colors = {"low_to_high": "#4c78a8", "high_to_low": "#f58518"}
        for ax, var in zip(axes, vars_to_plot):
            d = profiles[profiles["variable"] == var]
            for event_type, g in d.groupby("event_type", sort=True):
                g = g.sort_values("relative_time_sec")
                ax.plot(g["relative_time_sec"], g["median_resid_z"], lw=1.7, label=event_type, color=colors.get(event_type, None))
                ax.fill_between(g["relative_time_sec"], g["q25_resid_z"], g["q75_resid_z"], alpha=0.15, color=colors.get(event_type, None))
            ax.axvline(0.0, color="#222222", linewidth=0.8)
            ax.axhline(0.0, color="#999999", linewidth=0.7)
            ax.set_ylabel(var)
            ax.grid(alpha=0.20)
        axes[0].set_title("3045 event-aligned residual profiles")
        axes[-1].set_xlabel("time relative to transition (sec)")
        axes[0].legend(frameon=False, ncol=2)
        fig.tight_layout()
        fig.savefig(FIG / "event_aligned_residual_profiles.png", dpi=180)
        plt.close(fig)


def write_node_schema(decision: pd.DataFrame, cfg: RunConfig) -> None:
    rec = decision.iloc[0].to_dict()
    node = {
        "node_id": "3045_residual_event_trigger_search",
        "series": "304x",
        "node_type": "screen",
        "parent_node": "3042b_confinement_surrogate_audit",
        "question": "After removing smooth radial-density trends, do persistent compact-density transitions align with residual event shocks?",
        "competing_interpretations": [
            "H_event_trigger: transitions align with residual non-label or kinematic shocks",
            "H_label_circularity: event alignment appears only in variables close to the state definition",
            "H_smooth_null: shifted event times show comparable residual peaks",
            "H_artifact: event alignment is dominated by membership-count changes",
        ],
        "input_artifacts": ["Output/3041b/processed/frame_macrostate_candidates.csv"],
        "method": [
            "robust-z each signal within observation",
            f"subtract centered rolling mean with window {cfg.smooth_window_sec:.3g}s",
            f"define persistent low/high transitions requiring both adjacent runs >= {cfg.min_run_sec:.3g}s",
            "measure event-window residual peak and pre/post residual deltas",
            "compare event times with circularly shifted event-time nulls within each observation",
        ],
        "pass_gate": {
            "peak": f"real-null residual peak gap >= {cfg.peak_gap_gate_z} z and p <= {cfg.null_p_gate}",
            "direction": f"real-null direction contrast gap >= {cfg.direction_gap_gate_z} z, p <= {cfg.null_p_gate}, sign consistency >= 0.70",
            "mechanism_routing": "at least two surviving variables, including at least one non-label variable; kinematic survivor routes to 3045b",
        },
        "next_if_pass": "3045b event-conditioned neighbor-exchange audit",
        "next_if_boundary": "pause or redesign raw-neighbor trigger if only geometry/label variables survive",
        "next_if_fail": "pause residual/event route",
        "outputs": [
            "Output/3045/tables/transition_events.csv",
            "Output/3045/tables/residual_peak_null_comparison.csv",
            "Output/3045/tables/residual_direction_null_comparison.csv",
            "Output/3045/tables/egrt_decision_summary.csv",
            "Output/3045/3045_summary.md",
        ],
        "provenance": {"script": "Experiment/run_3045_residual_event_trigger_search.py", "config": asdict(cfg), "decision": rec},
    }
    (OUT / "3045_egrt_node.json").write_text(json.dumps(node, ensure_ascii=False, indent=2), encoding="utf-8")


def write_summary(
    events: pd.DataFrame,
    state_signs: pd.DataFrame,
    peak_comparison: pd.DataFrame,
    direction_comparison: pd.DataFrame,
    decision: pd.DataFrame,
    cfg: RunConfig,
) -> None:
    rec = decision.iloc[0]
    text = f"""# 3045 Residual Event-Trigger Search

## Scope

3042b stopped the strong stochastic-confinement mechanism because drift slopes
were explainable by smooth phase-rank nulls. 3045 changes the target: after
subtracting slow within-ob trends, it asks whether persistent compact-density
transitions still align with short-lived residual shocks.

## EGRT Node

| field | value |
| --- | --- |
| node_id | 3045_residual_event_trigger_search |
| parent | 3042b_confinement_surrogate_audit |
| node_type | screen |
| decision | {rec['eg_rt_decision']} |
| recommended next node | {rec['recommended_next_node']} |
| boundary reading | {rec['boundary_reading']} |

## Methods

- Input: `Output/3041b/processed/frame_macrostate_candidates.csv`.
- Signals are robust-z standardized within each observation.
- Slow trends are removed with a centered rolling mean of `{cfg.smooth_window_sec}` seconds.
- Transition events are compact-density low/high switches where both adjacent runs last at least `{cfg.min_run_sec}` seconds.
- Event evidence is compared with circularly shifted event-time nulls within each observation.
- Null replicates: `{cfg.n_null}`.

## Event Count

{dataframe_to_markdown(events.groupby(['event_type'], as_index=False).agg(n_events=('event_id', 'nunique'), n_ob=('ob', 'nunique')) if not events.empty else pd.DataFrame())}

## Decision Metrics

{dataframe_to_markdown(decision)}

## Residual Peak Null Comparison

{dataframe_to_markdown(peak_comparison)}

## Directional Residual Contrast Null Comparison

{dataframe_to_markdown(direction_comparison)}

## State-Delta Signs

{dataframe_to_markdown(state_signs)}

## Interpretation Boundary

This node is still a screen. A positive result does not prove a mechanism. It
only says that the residual/event target is sharper than the full smooth state
signal and can justify a raw-trajectory audit such as event-conditioned neighbor
exchange. If only label-basis variables survive, avoid claiming a mechanism
because the event definition and the signal are not independent enough.

## Outputs

- `Output/3045/3045_egrt_node.json`
- `Output/3045/tables/transition_events.csv`
- `Output/3045/tables/residual_event_features.csv`
- `Output/3045/tables/residual_peak_null_comparison.csv`
- `Output/3045/tables/residual_direction_null_comparison.csv`
- `Output/3045/tables/egrt_decision_summary.csv`
- `Output/3045/figures/residual_event_peak_vs_shift_null.png`
- `Output/3045/figures/residual_direction_contrast.png`
- `Output/3045/figures/event_aligned_residual_profiles.png`
"""
    (OUT / "3045_summary.md").write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-null", type=int, default=RunConfig.n_null)
    parser.add_argument("--quick", action="store_true", help="Use 40 null replicates.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cfg = RunConfig(n_null=40 if args.quick else args.n_null)
    ensure_dirs()
    df = add_residual_signals(read_input(), cfg)
    events = detect_transition_events(df, cfg)
    if events.empty:
        raise RuntimeError("No persistent low/high transition events found.")

    state_signs = state_shift_signs(df)
    arrays = build_ob_arrays(df)
    real_features = extract_event_features(arrays, events, cfg)
    real_peak = summarize_peak(real_features)
    real_direction = summarize_direction(real_features, state_signs)
    null_peak, null_direction = run_nulls(arrays, events, state_signs, cfg)
    peak_comparison = compare_peaks_to_null(real_peak, null_peak, cfg)
    direction_comparison = compare_direction_to_null(real_direction, null_direction, cfg)
    decision = decision_summary(peak_comparison, direction_comparison, events, cfg)

    selected = []
    if not peak_comparison.empty:
        selected.extend(peak_comparison.sort_values("real_minus_null_peak_z", ascending=False)["variable"].head(3).tolist())
    if not direction_comparison.empty:
        selected.extend(direction_comparison.sort_values("real_minus_null_abs_direction_contrast_z", ascending=False)["variable"].head(3).tolist())
    selected = list(dict.fromkeys(selected))[:4]
    profiles = aligned_profiles(arrays, events, selected, cfg) if selected else pd.DataFrame()

    df.to_csv(PROC / "frame_residual_signals.csv", index=False)
    events.to_csv(TAB / "transition_events.csv", index=False)
    events.to_csv(PROC / "transition_events.csv", index=False)
    state_signs.to_csv(TAB / "state_delta_signs.csv", index=False)
    real_features.to_csv(TAB / "residual_event_features.csv", index=False)
    real_peak.to_csv(TAB / "real_residual_peak_summary.csv", index=False)
    real_direction.to_csv(TAB / "real_residual_direction_summary.csv", index=False)
    null_peak.to_csv(TAB / "shift_null_peak_summary.csv", index=False)
    null_direction.to_csv(TAB / "shift_null_direction_summary.csv", index=False)
    peak_comparison.to_csv(TAB / "residual_peak_null_comparison.csv", index=False)
    direction_comparison.to_csv(TAB / "residual_direction_null_comparison.csv", index=False)
    decision.to_csv(TAB / "egrt_decision_summary.csv", index=False)
    decision.to_csv(PROC / "egrt_decision_summary.csv", index=False)
    pd.DataFrame([asdict(cfg)]).to_csv(PROC / "run_config.csv", index=False)
    if not profiles.empty:
        profiles.to_csv(TAB / "event_aligned_residual_profiles.csv", index=False)

    write_node_schema(decision, cfg)
    make_figures(peak_comparison, direction_comparison, profiles)
    write_summary(events, state_signs, peak_comparison, direction_comparison, decision, cfg)
    print(decision.to_string(index=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
