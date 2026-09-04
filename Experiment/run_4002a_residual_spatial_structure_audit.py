#!/usr/bin/env python3
"""Experiment 4002A: residual spatial-structure audit.

4001 showed that transition-linked velocity signals survive after subtracting
translation plus affine non-rigid geometry. 4002A asks what kind of residual
velocity structure remains: edge/core localization, radial residual motion,
tangential/swirl-like organization, or residual velocity order.
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
OUT = ROOT / "Output" / "4002A"
FIG = OUT / "figures"
TAB = OUT / "tables"
PROC = OUT / "processed"

RNG_SEED = 400201

RESIDUAL_FAMILIES = {
    "edge_minus_core_resid_speed": "edge_core",
    "edge_minus_core_resid_tangential": "edge_core",
    "radius_resid_speed_corr": "edge_core",
    "radius_resid_tangential_corr": "edge_core",
    "resid_radial_velocity_mean": "radial",
    "resid_radial_abs_mean": "radial",
    "resid_inward_fraction": "radial",
    "resid_tangential_speed_mean": "tangential_swirl",
    "resid_tangential_fraction": "tangential_swirl",
    "resid_angular_momentum_coherence": "tangential_swirl",
    "resid_speed_rms": "residual_intensity",
    "resid_velocity_cov_trace": "residual_intensity",
    "resid_polarization": "residual_order",
}
RESIDUAL_VARIABLES = list(RESIDUAL_FAMILIES)


@dataclass(frozen=True)
class RunConfig:
    data_dir: str = r"data/raw"
    max_ob: int | None = None
    smooth_window_sec: float = 1.00
    event_window_sec: float = 0.40
    prepost_window_sec: float = 0.20
    n_null: int = 160
    direction_gap_gate_z: float = 0.12
    null_p_gate: float = 0.10
    min_ob_gate: int = 12
    min_family_survivors_for_route: int = 1


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


def corr_or_nan(a: np.ndarray, b: np.ndarray) -> float:
    mask = np.isfinite(a) & np.isfinite(b)
    if int(mask.sum()) < 5:
        return math.nan
    aa = a[mask]
    bb = b[mask]
    if float(np.nanstd(aa)) <= 1e-12 or float(np.nanstd(bb)) <= 1e-12:
        return math.nan
    return safe_float(np.corrcoef(aa, bb)[0, 1])


def mean_or_nan(x: np.ndarray) -> float:
    x = x[np.isfinite(x)]
    return float(np.mean(x)) if x.size else math.nan


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


def residual_spatial_metrics(relative_pos: np.ndarray, resid_velocity: np.ndarray) -> dict[str, float]:
    radius = np.linalg.norm(relative_pos, axis=1)
    speed_sq = np.sum(resid_velocity * resid_velocity, axis=1)
    speed = np.sqrt(np.maximum(speed_sq, 0.0))
    mean_speed = mean_or_nan(speed)
    mean_v = np.nanmean(resid_velocity, axis=0)
    center_speed = float(np.linalg.norm(mean_v))
    mean_speed_sq = mean_or_nan(speed_sq)
    velocity_cov_trace = mean_speed_sq - center_speed**2 if np.isfinite(mean_speed_sq) else math.nan

    radial_velocity = np.full(speed.shape, np.nan, dtype="float64")
    valid_r = radius > 1e-12
    radial_velocity[valid_r] = np.sum(relative_pos[valid_r] * resid_velocity[valid_r], axis=1) / radius[valid_r]
    tangential_sq = np.maximum(speed_sq - np.nan_to_num(radial_velocity, nan=0.0) ** 2, 0.0)
    tangential = np.sqrt(tangential_sq)

    q33 = float(np.nanquantile(radius, 0.33)) if np.isfinite(radius).any() else math.nan
    q67 = float(np.nanquantile(radius, 0.67)) if np.isfinite(radius).any() else math.nan
    core = radius <= q33 if np.isfinite(q33) else np.zeros(radius.shape, dtype=bool)
    edge = radius >= q67 if np.isfinite(q67) else np.zeros(radius.shape, dtype=bool)

    core_speed = mean_or_nan(speed[core])
    edge_speed = mean_or_nan(speed[edge])
    core_tangential = mean_or_nan(tangential[core])
    edge_tangential = mean_or_nan(tangential[edge])

    good_speed = speed > 1e-12
    unit = np.full_like(resid_velocity, np.nan, dtype="float64")
    unit[good_speed] = resid_velocity[good_speed] / speed[good_speed, None]
    if np.any(good_speed):
        mean_unit = np.nanmean(unit[good_speed], axis=0)
        polarization = float(np.linalg.norm(mean_unit)) if np.isfinite(mean_unit).all() else math.nan
    else:
        polarization = math.nan

    cross = np.cross(relative_pos, resid_velocity)
    angular = np.nansum(cross, axis=0)
    angular_denom = float(np.nansum(radius * speed))
    angular_coherence = float(np.linalg.norm(angular) / angular_denom) if angular_denom > 1e-12 else math.nan

    return {
        "edge_minus_core_resid_speed": edge_speed - core_speed
        if np.isfinite(edge_speed) and np.isfinite(core_speed)
        else math.nan,
        "edge_minus_core_resid_tangential": edge_tangential - core_tangential
        if np.isfinite(edge_tangential) and np.isfinite(core_tangential)
        else math.nan,
        "radius_resid_speed_corr": corr_or_nan(radius, speed),
        "radius_resid_tangential_corr": corr_or_nan(radius, tangential),
        "resid_radial_velocity_mean": mean_or_nan(radial_velocity),
        "resid_radial_abs_mean": mean_or_nan(np.abs(radial_velocity)),
        "resid_inward_fraction": mean_or_nan((radial_velocity < 0).astype("float64")),
        "resid_tangential_speed_mean": mean_or_nan(tangential),
        "resid_tangential_fraction": mean_or_nan(tangential) / mean_speed
        if np.isfinite(mean_speed) and mean_speed > 1e-12
        else math.nan,
        "resid_angular_momentum_coherence": angular_coherence,
        "resid_speed_rms": math.sqrt(mean_speed_sq) if np.isfinite(mean_speed_sq) and mean_speed_sq >= 0 else math.nan,
        "resid_velocity_cov_trace": velocity_cov_trace,
        "resid_polarization": polarization,
    }


def frame_residual_spatial_metrics_for_ob(ob: int, dataset: str, data_dir: Path) -> pd.DataFrame:
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
        row.update(residual_spatial_metrics(fit["relative_pos"], fit["affine_resid"]))
        rows.append(row)
    return pd.DataFrame(rows).sort_values("t", kind="mergesort").reset_index(drop=True)


def build_frame_metrics(events: pd.DataFrame, cfg: RunConfig) -> pd.DataFrame:
    data_dir = resolve_data_dir(cfg)
    parts = []
    for ob, d in events.groupby("ob", sort=True):
        dataset = str(d["dataset"].iloc[0])
        metrics = frame_residual_spatial_metrics_for_ob(int(ob), dataset, data_dir)
        parts.append(metrics)
        print(f"[4002A] built residual spatial metrics Ob{int(ob)}: {len(metrics)} frames", flush=True)
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
        for var in RESIDUAL_VARIABLES:
            z = robust_z_safe(d[var])
            smooth = (
                pd.Series(z)
                .rolling(win, center=True, min_periods=min_periods)
                .mean()
                .interpolate(limit_direction="both")
                .to_numpy(dtype="float64")
            )
            resid = z - smooth
            d[f"{var}__z4002a"] = z
            d[f"{var}__smooth4002a"] = smooth
            d[f"{var}__resid4002a"] = robust_z_safe(resid)
        parts.append(d)
    return pd.concat(parts, ignore_index=True)


def build_arrays(frame: pd.DataFrame) -> dict[tuple[int, str], dict[str, np.ndarray]]:
    arrays: dict[tuple[int, str], dict[str, np.ndarray]] = {}
    for (ob, dataset), d0 in frame.groupby(["ob", "dataset"], sort=True):
        d = d0.sort_values("t").reset_index(drop=True)
        rec: dict[str, np.ndarray] = {"t": d["t"].to_numpy(dtype="float64")}
        for var in RESIDUAL_VARIABLES:
            rec[var] = d[f"{var}__resid4002a"].to_numpy(dtype="float64")
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
        for var in RESIDUAL_VARIABLES:
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
                    "family": RESIDUAL_FAMILIES[var],
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
        if replicate == 1 or replicate % 25 == 0 or replicate == cfg.n_null:
            print(f"[4002A] null replicate {replicate}/{cfg.n_null}", flush=True)
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
    families: dict[str, list[str]] = {}
    if not survivors.empty:
        for family, d in survivors.groupby("family", sort=True):
            families[family] = d["variable"].astype(str).tolist()

    route_order = [
        ("edge_core", "4002b edge/core residual localization audit"),
        ("tangential_swirl", "4002c residual tangential/swirl audit"),
        ("radial", "4002d residual radial expansion-contraction audit"),
        ("residual_order", "4002e residual local-alignment audit"),
        ("residual_intensity", "4002f residual intensity timing robustness audit"),
    ]
    if not survivors.empty:
        chosen_family = None
        next_node = None
        for family, route in route_order:
            if len(families.get(family, [])) >= cfg.min_family_survivors_for_route:
                chosen_family = family
                next_node = route
                break
        if chosen_family is None:
            chosen_family = str(survivors["family"].iloc[0])
            next_node = "4002b targeted residual structure robustness audit"
        decision = f"support_residual_{chosen_family}_structure_signal"
        boundary = "Residual affine-subtracted velocities have shifted-null robust spatial-structure signals; route to the strongest interpretable family."
    else:
        decision = "weak_residual_spatial_structure_signal"
        next_node = "pause 4002 structure route or broaden residual metrics"
        boundary = "No residual spatial-structure variable survives shifted-event null gates."

    return pd.DataFrame(
        [
            {
                "node_id": "4002a_residual_spatial_structure_audit",
                "node_type": "mechanism screen",
                "n_surviving_variables": int(len(survivors)),
                "n_edge_core_survivors": int(len(families.get("edge_core", []))),
                "n_radial_survivors": int(len(families.get("radial", []))),
                "n_tangential_swirl_survivors": int(len(families.get("tangential_swirl", []))),
                "n_residual_intensity_survivors": int(len(families.get("residual_intensity", []))),
                "n_residual_order_survivors": int(len(families.get("residual_order", []))),
                "surviving_variables": ", ".join(survivors["variable"].astype(str).tolist()) if not survivors.empty else "",
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
                    "family": RESIDUAL_FAMILIES[var],
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
            "edge_core": "#4c78a8",
            "radial": "#8b6f2d",
            "tangential_swirl": "#b55d60",
            "residual_intensity": "#5f8f3d",
            "residual_order": "#6b5a8e",
        }
        fig, ax = plt.subplots(figsize=(9.0, max(4.4, 0.36 * len(d) + 1.6)))
        y = np.arange(len(d))
        bar_colors = [colors.get(f, "#666666") for f in d["family"]]
        bars = ax.barh(y, d["real_minus_null_abs_direction_contrast_z"], color=bar_colors, alpha=0.88)
        for bar, gate in zip(bars, d["direction_survives_gate"]):
            if bool(gate):
                ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, " *", va="center", ha="left", fontsize=12)
        ax.axvline(0.0, color="#222222", linewidth=0.8)
        ax.axvline(0.12, color="#777777", linewidth=0.7, linestyle="--")
        ax.set_yticks(y)
        ax.set_yticklabels(d["variable"])
        ax.set_xlabel("real - shifted-null direction contrast (z)")
        ax.set_title("4002A residual spatial-structure signal screen")
        fig.tight_layout()
        fig.savefig(FIG / "residual_structure_direction_screen.png", dpi=180)
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
        axes[0].set_title("4002A direction-aligned residual structure profiles")
        axes[-1].set_xlabel("time relative to transition (sec)")
        fig.tight_layout()
        fig.savefig(FIG / "residual_structure_aligned_profiles.png", dpi=180)
        plt.close(fig)


def write_node_schema(decision: pd.DataFrame, cfg: RunConfig) -> None:
    rec = decision.iloc[0].to_dict()
    node = {
        "node_id": "4002a_residual_spatial_structure_audit",
        "series": "4xxx",
        "node_type": "mechanism screen",
        "parent_node": "4001_geometric_baseline_residual_audit",
        "question": "What kind of affine-residual velocity structure remains around compact-density transitions?",
        "competing_interpretations": [
            "H_edge_core: residual signal is localized by position inside the school",
            "H_radial: residual signal is expansion/contraction-like after affine subtraction",
            "H_tangential: residual signal is tangential or swirl-like",
            "H_order: residual velocities become more globally ordered",
            "H_shift_null: shifted event times show comparable spatial-structure changes",
        ],
        "input_artifacts": [
            "data/raw/Ob*.txt",
            "Output/3045/tables/transition_events.csv",
            "Output/4001/tables/egrt_decision_summary.csv",
        ],
        "method": [
            "fit per-frame affine baseline and compute affine residual velocities",
            "compute edge/core, radial, tangential/swirl, intensity, and order metrics",
            "remove 1-sec smooth trend and robust-z residualize within observation",
            f"compare transition events against {cfg.n_null} shifted-event null replicates",
        ],
        "pass_gate": {
            "direction": f"real-null direction gap >= {cfg.direction_gap_gate_z} z, p <= {cfg.null_p_gate}, sign consistency >= 0.70",
            "route": "route to the first surviving interpretable family in edge_core, tangential_swirl, radial, residual_order, residual_intensity order",
        },
        "outputs": [
            "Output/4002A/tables/residual_structure_direction_null_comparison.csv",
            "Output/4002A/tables/egrt_decision_summary.csv",
            "Output/4002A/4002A_summary.md",
        ],
        "provenance": {"script": "Experiment/run_4002a_residual_spatial_structure_audit.py", "config": asdict(cfg), "decision": rec},
    }
    (OUT / "4002A_egrt_node.json").write_text(json.dumps(node, ensure_ascii=False, indent=2), encoding="utf-8")


def write_summary(comparison: pd.DataFrame, decision: pd.DataFrame, cfg: RunConfig) -> None:
    rec = decision.iloc[0]
    survivors = comparison[comparison["direction_survives_gate"]].copy() if not comparison.empty else pd.DataFrame()
    text = f"""# 4002A Residual Spatial-Structure Audit

## Scope

4001 showed that velocity event signals survive an affine geometric baseline.
4002A asks what kind of affine-residual velocity structure remains.

Plain-language question:

> After removing ordinary school deformation, is the leftover velocity signal
> located at the edge, radial, tangential/swirl-like, or globally ordered?

## EGRT Node

| field | value |
| --- | --- |
| node_id | 4002a_residual_spatial_structure_audit |
| parent | 4001_geometric_baseline_residual_audit |
| node_type | mechanism screen |
| decision | {rec['eg_rt_decision']} |
| recommended next node | {rec['recommended_next_node']} |
| boundary reading | {rec['boundary_reading']} |

## Methods

- Per frame, fit and subtract the affine velocity baseline from 4001.
- Compute affine-residual spatial metrics:
  - edge/core residual speed and tangential differences;
  - radius-residual speed correlations;
  - residual radial motion;
  - residual tangential and angular-momentum coherence;
  - residual speed intensity and residual polarization.
- Remove a `{cfg.smooth_window_sec}` sec smooth trend within each observation.
- Compare post-minus-pre transition changes with `{cfg.n_null}` shifted-event null replicates.

## Decision Metrics

{dataframe_to_markdown(decision)}

## Surviving Variables

{dataframe_to_markdown(survivors)}

## Full Direction Null Comparison

{dataframe_to_markdown(comparison)}

## Interpretation

4002A is a route-selection node. It should not be treated as a final mechanism
claim. A surviving family means that the 4xxx route can now ask a narrower
question about that residual structure.

## Outputs

- `Output/4002A/4002A_egrt_node.json`
- `Output/4002A/tables/residual_structure_direction_null_comparison.csv`
- `Output/4002A/tables/egrt_decision_summary.csv`
- `Output/4002A/figures/residual_structure_direction_screen.png`
- `Output/4002A/figures/residual_structure_aligned_profiles.png`
"""
    (OUT / "4002A_summary.md").write_text(text, encoding="utf-8")


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
        print(f"[4002A] smoke-test observation limit: {keep_obs}", flush=True)
    print(f"[4002A] events: {len(events)}", flush=True)
    frame_raw = build_frame_metrics(events, cfg)
    frame = add_residualized_metrics(frame_raw, cfg)
    arrays = build_arrays(frame)
    features = extract_event_features(arrays, events, cfg)
    real_direction = summarize_direction(features, prefix="real")
    null_direction = run_nulls(arrays, events, cfg)
    comparison = compare_direction_to_null(real_direction, null_direction, cfg)
    decision = decision_summary(comparison, cfg)
    profile_vars = (
        comparison[comparison["direction_survives_gate"]]
        .sort_values("real_minus_null_abs_direction_contrast_z", ascending=False)["variable"]
        .astype(str)
        .head(6)
        .tolist()
    )
    if not profile_vars:
        profile_vars = comparison.sort_values("real_minus_null_abs_direction_contrast_z", ascending=False)["variable"].astype(str).head(6).tolist()
    profiles = aligned_profiles(arrays, events, profile_vars)

    keep_cols = ["ob", "dataset", "t", "n", "affine_r2_centered", "affine_residual_rms_fraction"]
    keep_cols.extend([f"{var}__resid4002a" for var in RESIDUAL_VARIABLES])
    frame[[col for col in keep_cols if col in frame.columns]].to_csv(PROC / "frame_residual_spatial_metrics.csv", index=False)
    features.to_csv(TAB / "residual_structure_event_features.csv", index=False)
    real_direction.to_csv(TAB / "real_residual_structure_direction_summary.csv", index=False)
    null_direction.to_csv(TAB / "shift_null_residual_structure_direction_summary.csv", index=False)
    comparison.to_csv(TAB / "residual_structure_direction_null_comparison.csv", index=False)
    decision.to_csv(TAB / "egrt_decision_summary.csv", index=False)
    profiles.to_csv(TAB / "residual_structure_aligned_profiles.csv", index=False)
    pd.DataFrame([asdict(cfg)]).to_csv(PROC / "run_config.csv", index=False)

    make_figures(comparison, profiles)
    write_node_schema(decision, cfg)
    write_summary(comparison, decision, cfg)
    print(decision.to_string(index=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
