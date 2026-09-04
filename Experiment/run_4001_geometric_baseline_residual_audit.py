#!/usr/bin/env python3
"""Experiment 4001: geometric baseline residual audit.

4001 starts the 4xxx line. It asks whether the 3045c velocity event signal is
mostly a geometric inevitability of non-rigid shape change. Per frame, velocities
are decomposed into:

    raw velocity
    affine_pred: translation + linear deformation from relative position
    affine_resid: velocity left after that affine geometric baseline

If the transition-aligned velocity signal remains in affine_resid, it supports
an extra coordination route. If it is absorbed by affine_pred, the safer reading
is that the 3045c velocity result is mainly a natural consequence of group
shape deformation.
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
OUT = ROOT / "Output" / "4001"
FIG = OUT / "figures"
TAB = OUT / "tables"
PROC = OUT / "processed"

EVENTS_3045 = ROOT / "Output" / "3045" / "tables" / "transition_events.csv"
DIRECTION_3045C = ROOT / "Output" / "3045c" / "tables" / "velocity_direction_null_comparison.csv"

RAW_COLS = ["id", "x", "z", "y", "t", "vx", "vz", "vy", "ax", "az", "ay"]
USECOLS = [0, 1, 2, 3, 4, 5, 6, 7]
RNG_SEED = 400101

COMPONENTS = ["raw", "affine_pred", "affine_resid"]
CORE_VARIABLES = ["mean_speed", "speed_rms", "velocity_cov_trace", "tangential_speed_mean"]


@dataclass(frozen=True)
class RunConfig:
    data_dir: str = r"data/raw"
    max_ob: int | None = None
    smooth_window_sec: float = 1.00
    event_window_sec: float = 0.35
    prepost_window_sec: float = 0.20
    n_null: int = 160
    direction_gap_gate_z: float = 0.12
    null_p_gate: float = 0.10
    min_ob_gate: int = 12
    residual_retention_gate: float = 0.30
    min_residual_survivors_for_extra_coordination: int = 2


def ensure_dirs() -> None:
    for path in (OUT, FIG, TAB, PROC):
        path.mkdir(parents=True, exist_ok=True)


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


def sign_consistency(values: Iterable[float]) -> float:
    arr = np.asarray(list(values), dtype="float64")
    arr = arr[np.isfinite(arr)]
    signs = np.sign(arr)
    signs = signs[signs != 0]
    if not signs.size:
        return math.nan
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


def median_dt(times: np.ndarray) -> float:
    t = np.unique(np.asarray(times, dtype="float64"))
    t = t[np.isfinite(t)]
    if t.size < 2:
        return math.nan
    return safe_float(np.nanmedian(np.diff(t)))


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


def resolve_data_dir(cfg: RunConfig) -> Path:
    path = Path(cfg.data_dir)
    if (path / "Ob1.txt").exists():
        return path
    raise FileNotFoundError(f"Dataset folder does not contain Ob1.txt: {path}")


def read_events() -> pd.DataFrame:
    if not EVENTS_3045.exists():
        raise FileNotFoundError(f"Run 3045 first; missing {EVENTS_3045}")
    events = pd.read_csv(EVENTS_3045)
    needed = ["event_id", "ob", "dataset", "event_t", "event_type"]
    missing = [col for col in needed if col not in events.columns]
    if missing:
        raise ValueError(f"Missing columns in {EVENTS_3045}: {missing}")
    for col in ["event_id", "ob", "event_t"]:
        events[col] = pd.to_numeric(events[col], errors="coerce")
    events = events.dropna(subset=needed).copy()
    events["event_id"] = events["event_id"].astype("int64")
    events["ob"] = events["ob"].astype("int64")
    return events.sort_values(["ob", "event_t"], kind="mergesort").reset_index(drop=True)


def selected_variables() -> list[str]:
    if not DIRECTION_3045C.exists():
        return CORE_VARIABLES.copy()
    direction = pd.read_csv(DIRECTION_3045C)
    if "direction_survives_gate" not in direction.columns:
        return CORE_VARIABLES.copy()
    keep = direction[direction["direction_survives_gate"].astype(bool)]["variable"].astype(str).tolist()
    out = [var for var in keep if var in CORE_VARIABLES]
    return out or CORE_VARIABLES.copy()


def read_raw_ob(path: Path) -> pd.DataFrame:
    try:
        df = pd.read_csv(path, sep=",", header=None, names=RAW_COLS, usecols=USECOLS, engine="c")
    except Exception:
        df = pd.read_csv(path, sep=r"\s+", header=None, names=RAW_COLS, usecols=USECOLS, engine="python")
    cols = ["id", "x", "z", "y", "t", "vx", "vz", "vy"]
    df = df[cols].copy()
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=cols).copy()
    df["id"] = df["id"].astype("int64")
    return df.sort_values(["t", "id"], kind="mergesort").reset_index(drop=True)


def velocity_metrics(relative_pos: np.ndarray, velocity: np.ndarray) -> dict[str, float]:
    speed_sq = np.sum(velocity * velocity, axis=1)
    speed = np.sqrt(np.maximum(speed_sq, 0.0))
    mean_v = np.nanmean(velocity, axis=0)
    center_velocity_speed = float(np.linalg.norm(mean_v))
    radius = np.linalg.norm(relative_pos, axis=1)
    radial_velocity = np.full(speed.shape, np.nan, dtype="float64")
    valid_r = radius > 1e-12
    radial_velocity[valid_r] = np.sum(relative_pos[valid_r] * velocity[valid_r], axis=1) / radius[valid_r]
    tangential_sq = np.maximum(speed_sq - np.nan_to_num(radial_velocity, nan=0.0) ** 2, 0.0)
    mean_speed_sq = safe_float(np.nanmean(speed_sq))
    return {
        "mean_speed": safe_float(np.nanmean(speed)),
        "speed_rms": math.sqrt(mean_speed_sq) if np.isfinite(mean_speed_sq) and mean_speed_sq >= 0 else math.nan,
        "speed_std": safe_float(np.nanstd(speed, ddof=1)) if speed.size > 1 else math.nan,
        "velocity_cov_trace": mean_speed_sq - center_velocity_speed**2 if np.isfinite(mean_speed_sq) else math.nan,
        "tangential_speed_mean": safe_float(np.nanmean(np.sqrt(tangential_sq))),
    }


def fit_affine_frame(positions: np.ndarray, velocities: np.ndarray) -> dict[str, object]:
    center = np.nanmean(positions, axis=0)
    center_velocity = np.nanmean(velocities, axis=0)
    rel = positions - center
    centered_v = velocities - center_velocity
    n = int(len(positions))
    if n >= 5:
        coef, residuals, rank, _ = np.linalg.lstsq(rel, centered_v, rcond=None)
        pred = center_velocity + rel @ coef
        resid = velocities - pred
        rank = int(rank)
    else:
        coef = np.full((3, 3), np.nan, dtype="float64")
        pred = np.tile(center_velocity, (n, 1))
        resid = velocities - pred
        rank = 0

    total_ss = float(np.sum(centered_v * centered_v))
    resid_ss = float(np.sum(resid * resid))
    pred_centered = pred - center_velocity
    pred_ss = float(np.sum(pred_centered * pred_centered))
    full_ss = float(np.sum(velocities * velocities))
    r2_centered = 1.0 - resid_ss / total_ss if total_ss > 1e-12 else math.nan
    residual_rms_fraction = math.sqrt(resid_ss / total_ss) if total_ss > 1e-12 else math.nan
    pred_full_energy_fraction = pred_ss / full_ss if full_ss > 1e-12 else math.nan
    if np.isfinite(coef).all():
        sym = 0.5 * (coef + coef.T)
        anti = 0.5 * (coef - coef.T)
        trace_rate = float(np.trace(coef) / 3.0)
        sym_fro = float(np.linalg.norm(sym, ord="fro"))
        anti_fro = float(np.linalg.norm(anti, ord="fro"))
        coef_fro = float(np.linalg.norm(coef, ord="fro"))
    else:
        trace_rate = sym_fro = anti_fro = coef_fro = math.nan

    return {
        "center": center,
        "center_velocity": center_velocity,
        "relative_pos": rel,
        "affine_coef": coef,
        "affine_pred": pred,
        "affine_resid": resid,
        "affine_rank": rank,
        "affine_r2_centered": r2_centered,
        "affine_residual_rms_fraction": residual_rms_fraction,
        "affine_pred_full_energy_fraction": pred_full_energy_fraction,
        "affine_coef_fro": coef_fro,
        "affine_symmetric_fro": sym_fro,
        "affine_antisymmetric_fro": anti_fro,
        "affine_trace_rate": trace_rate,
    }


def frame_geometric_metrics_for_ob(ob: int, dataset: str, data_dir: Path) -> pd.DataFrame:
    path = data_dir / dataset
    if not path.exists():
        path = data_dir / f"Ob{int(ob)}.txt"
    df = read_raw_ob(path)
    rows = []
    for t, d in df.groupby("t", sort=True):
        positions = d[["x", "y", "z"]].to_numpy(dtype="float64")
        velocities = d[["vx", "vy", "vz"]].to_numpy(dtype="float64")
        fit = fit_affine_frame(positions, velocities)
        rel = fit["relative_pos"]
        row = {
            "ob": int(ob),
            "dataset": dataset,
            "t": safe_float(t),
            "n": int(len(d)),
            "affine_rank": int(fit["affine_rank"]),
            "affine_r2_centered": safe_float(fit["affine_r2_centered"]),
            "affine_residual_rms_fraction": safe_float(fit["affine_residual_rms_fraction"]),
            "affine_pred_full_energy_fraction": safe_float(fit["affine_pred_full_energy_fraction"]),
            "affine_coef_fro": safe_float(fit["affine_coef_fro"]),
            "affine_symmetric_fro": safe_float(fit["affine_symmetric_fro"]),
            "affine_antisymmetric_fro": safe_float(fit["affine_antisymmetric_fro"]),
            "affine_trace_rate": safe_float(fit["affine_trace_rate"]),
        }
        component_velocities = {
            "raw": velocities,
            "affine_pred": fit["affine_pred"],
            "affine_resid": fit["affine_resid"],
        }
        for component, vel in component_velocities.items():
            metrics = velocity_metrics(rel, vel)
            for var, value in metrics.items():
                row[f"{component}__{var}"] = value
        rows.append(row)
    return pd.DataFrame(rows).sort_values("t", kind="mergesort").reset_index(drop=True)


def build_frame_geometric_metrics(events: pd.DataFrame, cfg: RunConfig) -> pd.DataFrame:
    data_dir = resolve_data_dir(cfg)
    parts = []
    for ob, d in events.groupby("ob", sort=True):
        dataset = str(d["dataset"].iloc[0])
        metrics = frame_geometric_metrics_for_ob(int(ob), dataset, data_dir)
        parts.append(metrics)
        print(f"[4001] built affine metrics Ob{int(ob)}: {len(metrics)} frames", flush=True)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


def metric_columns(variables: list[str]) -> list[str]:
    return [f"{component}__{var}" for component in COMPONENTS for var in variables]


def add_residualized_metrics(frame: pd.DataFrame, variables: list[str], cfg: RunConfig) -> pd.DataFrame:
    columns = metric_columns(variables)
    geometry_cols = [
        "affine_r2_centered",
        "affine_residual_rms_fraction",
        "affine_pred_full_energy_fraction",
        "affine_coef_fro",
        "affine_symmetric_fro",
        "affine_antisymmetric_fro",
        "affine_trace_rate",
    ]
    parts = []
    for (ob, dataset), d0 in frame.groupby(["ob", "dataset"], sort=True):
        d = d0.sort_values("t").reset_index(drop=True).copy()
        dt = median_dt(d["t"].to_numpy(dtype="float64"))
        win = max(5, int(round(cfg.smooth_window_sec / dt))) if np.isfinite(dt) and dt > 0 else 101
        if win % 2 == 0:
            win += 1
        min_periods = max(3, win // 5)
        for col in [*columns, *geometry_cols]:
            if col not in d.columns:
                continue
            z = robust_z(d[col])
            smooth = (
                pd.Series(z)
                .rolling(win, center=True, min_periods=min_periods)
                .mean()
                .interpolate(limit_direction="both")
                .to_numpy(dtype="float64")
            )
            resid = z - smooth
            d[f"{col}__z4001"] = z
            d[f"{col}__smooth4001"] = smooth
            d[f"{col}__resid4001"] = robust_z(resid)
        parts.append(d)
    return pd.concat(parts, ignore_index=True)


def build_arrays(frame: pd.DataFrame, variables: list[str]) -> dict[tuple[int, str], dict[str, np.ndarray]]:
    arrays: dict[tuple[int, str], dict[str, np.ndarray]] = {}
    columns = metric_columns(variables)
    geometry_cols = ["affine_r2_centered", "affine_residual_rms_fraction", "affine_trace_rate"]
    for (ob, dataset), d0 in frame.groupby(["ob", "dataset"], sort=True):
        d = d0.sort_values("t").reset_index(drop=True)
        rec: dict[str, np.ndarray] = {"t": d["t"].to_numpy(dtype="float64")}
        for col in [*columns, *geometry_cols]:
            key = f"{col}__resid4001"
            if key in d.columns:
                rec[col] = d[key].to_numpy(dtype="float64")
        arrays[(int(ob), str(dataset))] = rec
    return arrays


def event_direction_sign(event_type: str) -> float:
    if event_type == "low_to_high":
        return 1.0
    if event_type == "high_to_low":
        return -1.0
    return math.nan


def extract_event_features(
    arrays: dict[tuple[int, str], dict[str, np.ndarray]],
    events: pd.DataFrame,
    variables: list[str],
    cfg: RunConfig,
) -> pd.DataFrame:
    rows = []
    keys = metric_columns(variables)
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
        for key in keys:
            x = rec.get(key)
            if x is None:
                continue
            pre = x[p0:p1]
            post = x[q0:q1]
            if not np.isfinite(pre).any() or not np.isfinite(post).any():
                continue
            pre_mean = safe_float(np.nanmean(pre))
            post_mean = safe_float(np.nanmean(post))
            component, variable = key.split("__", 1)
            rows.append(
                {
                    "event_id": int(event.event_id),
                    "ob": int(event.ob),
                    "dataset": str(event.dataset),
                    "event_t": event_t,
                    "event_type": str(event.event_type),
                    "component": component,
                    "variable": variable,
                    "metric_key": key,
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
        keep.groupby(["ob", "component", "variable", "metric_key", "event_type"], as_index=False)
        .agg(
            n_events=("event_id", "nunique"),
            median_signed_delta_z=("signed_delta_post_minus_pre_z", "median"),
        )
        .dropna(subset=["median_signed_delta_z"])
    )
    wide = by_ob_type.pivot_table(
        index=["ob", "component", "variable", "metric_key"],
        columns="event_type",
        values="median_signed_delta_z",
        aggfunc="first",
    ).reset_index()
    if "low_to_high" not in wide or "high_to_low" not in wide:
        return pd.DataFrame()
    wide = wide.dropna(subset=["low_to_high", "high_to_low"]).copy()
    wide["direction_contrast_z"] = wide["low_to_high"] - wide["high_to_low"]
    rows = []
    for (component, variable, metric_key), d in wide.groupby(["component", "variable", "metric_key"], sort=True):
        rows.append(
            {
                "component": component,
                "variable": variable,
                "metric_key": metric_key,
                "n_ob": int(d["ob"].nunique()),
                "n_events": int(by_ob_type[by_ob_type["metric_key"] == metric_key]["n_events"].sum()),
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


def run_nulls(
    arrays: dict[tuple[int, str], dict[str, np.ndarray]],
    events: pd.DataFrame,
    variables: list[str],
    cfg: RunConfig,
) -> pd.DataFrame:
    rng = np.random.default_rng(RNG_SEED)
    rows = []
    for replicate in range(1, cfg.n_null + 1):
        shifted = shifted_events(events, arrays, rng)
        features = extract_event_features(arrays, shifted, variables, cfg)
        summary = summarize_direction(features, prefix="null")
        summary["replicate"] = int(replicate)
        rows.append(summary)
        if replicate == 1 or replicate % 25 == 0 or replicate == cfg.n_null:
            print(f"[4001] null replicate {replicate}/{cfg.n_null}", flush=True)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def compare_direction_to_null(real: pd.DataFrame, null: pd.DataFrame, cfg: RunConfig) -> pd.DataFrame:
    rows = []
    for rec in real.itertuples(index=False):
        d = null[null["metric_key"] == rec.metric_key]
        vals = d["null_abs_median_direction_contrast_z"].to_numpy(dtype="float64") if not d.empty else np.array([])
        vals = vals[np.isfinite(vals)]
        real_abs = safe_float(rec.real_abs_median_direction_contrast_z)
        null_med = float(np.median(vals)) if vals.size else math.nan
        gap = real_abs - null_med if np.isfinite(real_abs) and np.isfinite(null_med) else math.nan
        p = float((1 + np.sum(vals >= real_abs)) / (len(vals) + 1)) if vals.size else math.nan
        sign_cons = safe_float(rec.real_direction_contrast_sign_consistency)
        rows.append(
            {
                "component": rec.component,
                "variable": rec.variable,
                "metric_key": rec.metric_key,
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
    return pd.DataFrame(rows).sort_values(
        ["variable", "component", "real_minus_null_abs_direction_contrast_z"],
        ascending=[True, True, False],
    )


def component_retention_table(comparison: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for variable, d in comparison.groupby("variable", sort=True):
        by_comp = {row.component: row for row in d.itertuples(index=False)}
        raw = by_comp.get("raw")
        pred = by_comp.get("affine_pred")
        resid = by_comp.get("affine_resid")
        raw_abs = safe_float(getattr(raw, "real_abs_median_direction_contrast_z", math.nan)) if raw is not None else math.nan
        pred_abs = safe_float(getattr(pred, "real_abs_median_direction_contrast_z", math.nan)) if pred is not None else math.nan
        resid_abs = safe_float(getattr(resid, "real_abs_median_direction_contrast_z", math.nan)) if resid is not None else math.nan
        rows.append(
            {
                "variable": variable,
                "raw_abs_direction_contrast_z": raw_abs,
                "affine_pred_abs_direction_contrast_z": pred_abs,
                "affine_resid_abs_direction_contrast_z": resid_abs,
                "affine_pred_to_raw_abs_ratio": pred_abs / raw_abs if np.isfinite(pred_abs) and np.isfinite(raw_abs) and raw_abs > 1e-12 else math.nan,
                "affine_resid_to_raw_abs_ratio": resid_abs / raw_abs if np.isfinite(resid_abs) and np.isfinite(raw_abs) and raw_abs > 1e-12 else math.nan,
                "raw_survives_gate": bool(getattr(raw, "direction_survives_gate", False)) if raw is not None else False,
                "affine_pred_survives_gate": bool(getattr(pred, "direction_survives_gate", False)) if pred is not None else False,
                "affine_resid_survives_gate": bool(getattr(resid, "direction_survives_gate", False)) if resid is not None else False,
            }
        )
    return pd.DataFrame(rows).sort_values("raw_abs_direction_contrast_z", ascending=False)


def geometry_event_summary(frame: pd.DataFrame, events: pd.DataFrame, cfg: RunConfig) -> pd.DataFrame:
    arrays = build_arrays(frame, [])
    keys = ["affine_r2_centered", "affine_residual_rms_fraction", "affine_trace_rate"]
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
        sign = event_direction_sign(str(event.event_type))
        for key in keys:
            x = rec.get(key)
            if x is None:
                continue
            pre = safe_float(np.nanmean(x[p0:p1]))
            post = safe_float(np.nanmean(x[q0:q1]))
            rows.append(
                {
                    "event_id": int(event.event_id),
                    "ob": int(event.ob),
                    "dataset": str(event.dataset),
                    "event_type": str(event.event_type),
                    "metric": key,
                    "signed_delta_post_minus_pre_z": sign * (post - pre)
                    if np.isfinite(sign) and np.isfinite(pre) and np.isfinite(post)
                    else math.nan,
                }
            )
    feat = pd.DataFrame(rows)
    if feat.empty:
        return pd.DataFrame()
    by_ob = (
        feat.groupby(["ob", "metric"], as_index=False)
        .agg(n_events=("event_id", "nunique"), median_aligned_delta_z=("signed_delta_post_minus_pre_z", "median"))
        .dropna(subset=["median_aligned_delta_z"])
    )
    out = []
    for metric, d in by_ob.groupby("metric", sort=True):
        out.append(
            {
                "metric": metric,
                "n_ob": int(d["ob"].nunique()),
                "n_events": int(d["n_events"].sum()),
                "median_aligned_delta_z": finite_median(d["median_aligned_delta_z"]),
                "q25_aligned_delta_z": finite_quantile(d["median_aligned_delta_z"], 0.25),
                "q75_aligned_delta_z": finite_quantile(d["median_aligned_delta_z"], 0.75),
                "sign_consistency": sign_consistency(d["median_aligned_delta_z"]),
            }
        )
    return pd.DataFrame(out).sort_values("median_aligned_delta_z", ascending=False)


def decision_summary(retention: pd.DataFrame, comparison: pd.DataFrame, geometry_summary: pd.DataFrame, cfg: RunConfig) -> pd.DataFrame:
    raw_vars = retention[retention["raw_survives_gate"]]["variable"].astype(str).tolist() if not retention.empty else []
    pred_vars = retention[retention["affine_pred_survives_gate"]]["variable"].astype(str).tolist() if not retention.empty else []
    resid_vars = retention[retention["affine_resid_survives_gate"]]["variable"].astype(str).tolist() if not retention.empty else []
    residual_ratios = retention.loc[retention["raw_survives_gate"], "affine_resid_to_raw_abs_ratio"].to_numpy(dtype="float64")
    residual_ratios = residual_ratios[np.isfinite(residual_ratios)]
    median_resid_ratio = float(np.median(residual_ratios)) if residual_ratios.size else math.nan
    pred_ratios = retention.loc[retention["raw_survives_gate"], "affine_pred_to_raw_abs_ratio"].to_numpy(dtype="float64")
    pred_ratios = pred_ratios[np.isfinite(pred_ratios)]
    median_pred_ratio = float(np.median(pred_ratios)) if pred_ratios.size else math.nan

    if len(resid_vars) >= cfg.min_residual_survivors_for_extra_coordination:
        decision = "support_extra_affine_residual_velocity_coordination"
        next_node = "4002 residual coordination structure audit"
        boundary = "Velocity event signal survives after subtracting translation plus affine deformation, supporting an extra coordination route."
    elif len(resid_vars) == 1:
        decision = "boundary_single_residual_velocity_variable_after_geometry"
        next_node = "4002 narrow residual-variable robustness audit or synthesize geometry boundary"
        boundary = "One velocity variable remains after the affine geometry baseline, but the signal is too narrow for a broad coordination claim."
    elif len(raw_vars) >= 2 and (len(pred_vars) >= 1 or (np.isfinite(median_resid_ratio) and median_resid_ratio < cfg.residual_retention_gate)):
        decision = "support_geometric_baseline_explains_velocity_event_signal"
        next_node = "4001b weaker geometry baseline decomposition or 4002 synthesize geometry boundary"
        boundary = "The 3045c-style velocity event signal is largely absorbed by the non-rigid affine geometry baseline."
    elif len(raw_vars) >= 1:
        decision = "boundary_raw_signal_not_clearly_allocated_by_affine_baseline"
        next_node = "4001b compare weaker baselines: translation, rigid rotation, isotropic expansion, affine"
        boundary = "Raw signal exists, but the affine baseline does not cleanly allocate it to explained or residual components."
    else:
        decision = "weak_velocity_event_signal_under_4001_reprocessing"
        next_node = "pause 4xxx velocity-geometric route"
        boundary = "The raw event signal did not reproduce strongly enough under the 4001 preprocessing."

    geom_r2 = math.nan
    if not geometry_summary.empty and "affine_r2_centered" in set(geometry_summary["metric"]):
        geom_r2 = safe_float(geometry_summary.loc[geometry_summary["metric"] == "affine_r2_centered", "median_aligned_delta_z"].iloc[0])

    return pd.DataFrame(
        [
            {
                "node_id": "4001_geometric_baseline_residual_audit",
                "node_type": "artifact-control / baseline audit",
                "n_raw_direction_survivors": int(len(raw_vars)),
                "n_affine_pred_direction_survivors": int(len(pred_vars)),
                "n_affine_resid_direction_survivors": int(len(resid_vars)),
                "raw_surviving_variables": ", ".join(raw_vars),
                "affine_pred_surviving_variables": ", ".join(pred_vars),
                "affine_resid_surviving_variables": ", ".join(resid_vars),
                "median_affine_pred_to_raw_abs_ratio_for_raw_survivors": median_pred_ratio,
                "median_affine_resid_to_raw_abs_ratio_for_raw_survivors": median_resid_ratio,
                "aligned_affine_r2_delta_z": geom_r2,
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
    for variable in variables:
        for component in COMPONENTS:
            key = f"{component}__{variable}"
            samples = []
            for event in events.itertuples(index=False):
                sign = event_direction_sign(str(event.event_type))
                rec = arrays.get((int(event.ob), str(event.dataset)))
                if rec is None or not np.isfinite(sign):
                    continue
                x = rec.get(key)
                if x is None:
                    continue
                t = rec["t"]
                target = float(event.event_t) + rel_grid
                valid = (target >= np.nanmin(t)) & (target <= np.nanmax(t))
                y = np.full(rel_grid.shape, np.nan, dtype="float64")
                if np.any(valid):
                    y[valid] = sign * np.interp(target[valid], t, x)
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
                        "variable": variable,
                        "component": component,
                        "relative_time_sec": float(rel_t),
                        "median_aligned_resid_z": safe_float(m),
                        "q25_aligned_resid_z": safe_float(lo),
                        "q75_aligned_resid_z": safe_float(hi),
                        "n_events": int(len(samples)),
                    }
                )
    return pd.DataFrame(rows)


def make_figures(comparison: pd.DataFrame, retention: pd.DataFrame, profiles: pd.DataFrame) -> None:
    if not comparison.empty:
        order = ["raw", "affine_pred", "affine_resid"]
        variables = list(dict.fromkeys(comparison["variable"].tolist()))
        x = np.arange(len(variables))
        width = 0.24
        fig, ax = plt.subplots(figsize=(9.4, 4.8))
        colors = {"raw": "#4c78a8", "affine_pred": "#8b6f2d", "affine_resid": "#b55d60"}
        for i, component in enumerate(order):
            vals = []
            gates = []
            for var in variables:
                d = comparison[(comparison["variable"] == var) & (comparison["component"] == component)]
                vals.append(float(d["real_minus_null_abs_direction_contrast_z"].iloc[0]) if not d.empty else math.nan)
                gates.append(bool(d["direction_survives_gate"].iloc[0]) if not d.empty else False)
            bars = ax.bar(x + (i - 1) * width, vals, width=width, label=component, color=colors[component], alpha=0.88)
            for bar, gate in zip(bars, gates):
                if gate:
                    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), "*", ha="center", va="bottom", fontsize=12)
        ax.axhline(0.0, color="#222222", linewidth=0.8)
        ax.axhline(0.12, color="#777777", linewidth=0.7, linestyle="--", label="gate gap")
        ax.set_xticks(x)
        ax.set_xticklabels(variables, rotation=20, ha="right")
        ax.set_ylabel("real - shifted-null direction contrast (z)")
        ax.set_title("4001 allocation of velocity event signal")
        ax.legend(frameon=False, ncols=4)
        fig.tight_layout()
        fig.savefig(FIG / "component_direction_signal_allocation.png", dpi=180)
        plt.close(fig)

    if not retention.empty:
        d = retention.sort_values("raw_abs_direction_contrast_z", ascending=True)
        fig, ax = plt.subplots(figsize=(8.2, 4.6))
        y = np.arange(len(d))
        ax.barh(y - 0.18, d["affine_pred_to_raw_abs_ratio"], height=0.32, label="affine_pred/raw", color="#8b6f2d")
        ax.barh(y + 0.18, d["affine_resid_to_raw_abs_ratio"], height=0.32, label="affine_resid/raw", color="#b55d60")
        ax.axvline(1.0, color="#222222", linewidth=0.8)
        ax.axvline(0.30, color="#777777", linewidth=0.7, linestyle="--")
        ax.set_yticks(y)
        ax.set_yticklabels(d["variable"])
        ax.set_xlabel("absolute direction contrast ratio relative to raw")
        ax.set_title("4001 residual retention after affine geometry baseline")
        ax.legend(frameon=False)
        fig.tight_layout()
        fig.savefig(FIG / "affine_residual_retention_ratios.png", dpi=180)
        plt.close(fig)

    if not profiles.empty:
        variables = list(dict.fromkeys(profiles["variable"].tolist()))
        fig, axes = plt.subplots(len(variables), 1, figsize=(8.8, max(3.0, 2.35 * len(variables))), sharex=True)
        if len(variables) == 1:
            axes = [axes]
        colors = {"raw": "#4c78a8", "affine_pred": "#8b6f2d", "affine_resid": "#b55d60"}
        for ax, var in zip(axes, variables):
            for component in COMPONENTS:
                d = profiles[(profiles["variable"] == var) & (profiles["component"] == component)].sort_values("relative_time_sec")
                if d.empty:
                    continue
                ax.plot(d["relative_time_sec"], d["median_aligned_resid_z"], label=component, color=colors[component], lw=1.6)
            ax.axvline(0.0, color="#222222", linewidth=0.8)
            ax.axhline(0.0, color="#999999", linewidth=0.7)
            ax.set_ylabel(var)
            ax.grid(alpha=0.18)
        axes[0].set_title("4001 direction-aligned profiles by velocity component")
        axes[0].legend(frameon=False, ncols=3)
        axes[-1].set_xlabel("time relative to transition (sec)")
        fig.tight_layout()
        fig.savefig(FIG / "component_aligned_velocity_profiles.png", dpi=180)
        plt.close(fig)


def write_node_schema(decision: pd.DataFrame, variables: list[str], cfg: RunConfig) -> None:
    rec = decision.iloc[0].to_dict()
    node = {
        "node_id": "4001_geometric_baseline_residual_audit",
        "series": "4xxx",
        "node_type": "artifact-control / baseline audit",
        "parent_node": "3045d_velocity_timing_audit",
        "question": "Do 3045c velocity event signals survive after subtracting translation plus affine non-rigid geometry?",
        "competing_interpretations": [
            "H_geometry: velocity signal is mostly a natural consequence of group deformation",
            "H_extra_coordination: velocity signal remains in affine residuals",
            "H_mixed: both affine-predicted and residual components carry event signal",
            "H_shift_null: shifted event times show comparable component signals",
        ],
        "input_artifacts": [
            "data/raw/Ob*.txt",
            "Output/3045/tables/transition_events.csv",
            "Output/3045c/tables/velocity_direction_null_comparison.csv",
        ],
        "method": [
            "fit per-frame v = center_velocity + relative_position @ A",
            "compute raw, affine_pred, and affine_resid velocity metrics",
            "remove 1-sec smooth trend and robust-z residualize within observation",
            f"compare transition events against {cfg.n_null} circularly shifted event-time nulls",
        ],
        "pass_gate": {
            "direction": f"real-null direction gap >= {cfg.direction_gap_gate_z} z, p <= {cfg.null_p_gate}, sign consistency >= 0.70",
            "extra_coordination": f"at least {cfg.min_residual_survivors_for_extra_coordination} affine_resid variables pass",
            "geometry_explains": f"raw survives and affine_resid/raw median ratio < {cfg.residual_retention_gate}, or affine_pred survives while residual does not",
        },
        "outputs": [
            "Output/4001/tables/component_direction_null_comparison.csv",
            "Output/4001/tables/component_retention_summary.csv",
            "Output/4001/tables/egrt_decision_summary.csv",
            "Output/4001/4001_summary.md",
        ],
        "provenance": {"script": "Experiment/run_4001_geometric_baseline_residual_audit.py", "config": asdict(cfg), "variables": variables, "decision": rec},
    }
    (OUT / "4001_egrt_node.json").write_text(json.dumps(node, ensure_ascii=False, indent=2), encoding="utf-8")


def write_summary(
    variables: list[str],
    comparison: pd.DataFrame,
    retention: pd.DataFrame,
    geometry_summary: pd.DataFrame,
    decision: pd.DataFrame,
    cfg: RunConfig,
) -> None:
    rec = decision.iloc[0]
    text = f"""# 4001 Geometric Baseline Residual Audit

## Scope

4001 starts the 4xxx line. The question is whether the 3045c velocity event
signal is an extra coordination signal, or mostly a geometric inevitability of
non-rigid group deformation.

## Plain-Language Baseline

For every frame, we ask how much of each fish's velocity can be explained by
where it is inside the group:

- the whole group translating;
- the group rotating;
- the group expanding or contracting;
- the group stretching or shearing.

All of those are captured by a per-frame affine model:

`velocity = group_center_velocity + relative_position * A`

The remaining velocity is `affine_resid`.

## EGRT Node

| field | value |
| --- | --- |
| node_id | 4001_geometric_baseline_residual_audit |
| parent | 3045d_velocity_timing_audit |
| node_type | artifact-control / baseline audit |
| decision | {rec['eg_rt_decision']} |
| recommended next node | {rec['recommended_next_node']} |
| boundary reading | {rec['boundary_reading']} |

## Methods

- Selected variables from 3045c direction survivors: `{', '.join(variables)}`.
- Components: `raw`, `affine_pred`, `affine_resid`.
- Smooth trend removal: `{cfg.smooth_window_sec}` sec centered rolling mean.
- Event feature: post-minus-pre residual change around 3045 persistent transitions.
- Direction alignment: low-to-high positive, high-to-low negative.
- Null: circularly shifted event times within each observation.
- Null replicates: `{cfg.n_null}`.

## Decision Metrics

{dataframe_to_markdown(decision)}

## Component Retention Summary

{dataframe_to_markdown(retention)}

## Direction Null Comparison

{dataframe_to_markdown(comparison)}

## Geometry Event Summary

{dataframe_to_markdown(geometry_summary)}

## Interpretation

If `affine_resid` keeps the transition-aligned signal, the speed result cannot
be dismissed as ordinary shape change. If `affine_resid` loses the signal while
`affine_pred` or low residual-retention ratios explain it, the safer reading is
that the earlier speed result is mainly a byproduct of non-rigid group geometry.

## Outputs

- `Output/4001/4001_egrt_node.json`
- `Output/4001/tables/component_direction_null_comparison.csv`
- `Output/4001/tables/component_retention_summary.csv`
- `Output/4001/tables/geometric_event_summary.csv`
- `Output/4001/tables/egrt_decision_summary.csv`
- `Output/4001/figures/component_direction_signal_allocation.png`
- `Output/4001/figures/affine_residual_retention_ratios.png`
- `Output/4001/figures/component_aligned_velocity_profiles.png`
"""
    (OUT / "4001_summary.md").write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default=RunConfig.data_dir)
    parser.add_argument("--max-ob", type=int, default=None, help="Limit to the first N observations for smoke testing.")
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
    variables = selected_variables()
    events = read_events()
    if cfg.max_ob is not None and cfg.max_ob > 0:
        keep_obs = sorted(events["ob"].unique().tolist())[: cfg.max_ob]
        events = events[events["ob"].isin(keep_obs)].copy().reset_index(drop=True)
        print(f"[4001] smoke-test observation limit: {keep_obs}", flush=True)
    print(f"[4001] selected variables: {', '.join(variables)}", flush=True)
    print(f"[4001] events: {len(events)}", flush=True)
    frame_raw = build_frame_geometric_metrics(events, cfg)
    frame = add_residualized_metrics(frame_raw, variables, cfg)
    arrays = build_arrays(frame, variables)
    real_features = extract_event_features(arrays, events, variables, cfg)
    real_direction = summarize_direction(real_features, prefix="real")
    null_direction = run_nulls(arrays, events, variables, cfg)
    comparison = compare_direction_to_null(real_direction, null_direction, cfg)
    retention = component_retention_table(comparison)
    geometry_summary = geometry_event_summary(frame, events, cfg)
    decision = decision_summary(retention, comparison, geometry_summary, cfg)
    profiles = aligned_profiles(arrays, events, variables)

    keep_cols = [
        "ob",
        "dataset",
        "t",
        "n",
        "affine_rank",
        "affine_r2_centered",
        "affine_residual_rms_fraction",
        "affine_pred_full_energy_fraction",
        "affine_trace_rate",
        *[f"{col}__resid4001" for col in metric_columns(variables)],
        "affine_r2_centered__resid4001",
        "affine_residual_rms_fraction__resid4001",
        "affine_trace_rate__resid4001",
    ]
    frame[[col for col in keep_cols if col in frame.columns]].to_csv(PROC / "frame_geometric_velocity_metrics.csv", index=False)
    real_features.to_csv(TAB / "component_event_features.csv", index=False)
    real_direction.to_csv(TAB / "real_component_direction_summary.csv", index=False)
    null_direction.to_csv(TAB / "shift_null_component_direction_summary.csv", index=False)
    comparison.to_csv(TAB / "component_direction_null_comparison.csv", index=False)
    retention.to_csv(TAB / "component_retention_summary.csv", index=False)
    geometry_summary.to_csv(TAB / "geometric_event_summary.csv", index=False)
    decision.to_csv(TAB / "egrt_decision_summary.csv", index=False)
    profiles.to_csv(TAB / "component_aligned_velocity_profiles.csv", index=False)
    pd.DataFrame([asdict(cfg)]).to_csv(PROC / "run_config.csv", index=False)

    make_figures(comparison, retention, profiles)
    write_node_schema(decision, variables, cfg)
    write_summary(variables, comparison, retention, geometry_summary, decision, cfg)
    print(decision.to_string(index=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
