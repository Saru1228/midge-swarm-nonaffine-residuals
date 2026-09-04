#!/usr/bin/env python3
"""4142 detrending challenge.

This submission-hardening node asks whether the frozen T1 survival result and
the weaker near-pre profile depend on the centered 1-second detrending used in
4081/4084.

The node reuses cached local T1 frame series from 4141 and raw 4084 spatial
series. It does not redefine the local affine observable.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from textwrap import dedent
from typing import Any

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_DIR = ROOT / "Experiment"
if str(EXPERIMENT_DIR) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_DIR))

import run_4002a_residual_spatial_structure_audit as r4002a  # noqa: E402
import run_4081_global_vs_local_geometry_ladder as r4081  # noqa: E402
import run_4141_full_pipeline_omnibus_survival_null as r4141  # noqa: E402


OUT = ROOT / "Output" / "4142"
FIG = OUT / "figures"
TABLES = OUT / "tables"

NODE = "4142_detrending_challenge"
DATE = "2026-09-02"
RNG_SEED = 4142_20260902

EVENT_PATH = ROOT / "Output" / "3045" / "tables" / "transition_events.csv"
OBSERVED_PATH = ROOT / "Output" / "4081c" / "full_geometry_ladder_rows.csv"
CLASS_PATH = ROOT / "Output" / "4081c" / "ob_route_a_classification.csv"
LOCAL_CACHE = ROOT / "Output" / "4141" / "cache"
SPATIAL_4084 = ROOT / "Output" / "4084" / "per_ob"

TARGET_ID = "T1_transition_tangential_residual"
LOCAL_VARIABLE = "local_tangential_speed_mean"
PHASE_VARIABLE = "all_tangential"

GAP_GATE = 0.03
P_GATE = 0.35
RATIO_GATE = 0.30

BASELINE_N_BOTH = 14
BASELINE_N_ANY = 15

PHASE_BINS = [
    ("early_pre", -0.50, -0.25),
    ("near_pre", -0.25, 0.00),
    ("near_post", 0.00, 0.25),
    ("late_post", 0.25, 0.50),
]

SURVIVAL_COLUMNS = [
    "variant",
    "ob",
    "dataset",
    "k",
    "n_events",
    "local_event_direction_abs_z",
    "local_non_event_direction_abs_median_z",
    "local_event_minus_non_event_direction_z",
    "p_non_event_direction_ge_event",
    "local_to_b3_direction_ratio",
    "event_conditioned_local_gate",
]

VARIANT_SUMMARY_COLUMNS = [
    "variant",
    "n_observations",
    "n_both",
    "n_any",
    "n_k8",
    "n_k10",
    "both_fraction",
    "any_fraction",
    "delta_both_vs_4081c",
    "delta_any_vs_4081c",
    "both_observations",
    "any_observations",
]

PHASE_COLUMNS = [
    "variant",
    "ob",
    "dataset",
    "variable",
    "phase",
    "n_events",
    "real_phase_aligned_z",
    "null_phase_median_aligned_z",
    "null_phase_abs_median_z",
    "event_minus_null_phase_z",
    "abs_event_minus_abs_null_z",
    "p_null_abs_ge_real_abs",
    "phase_gate",
]

PHASE_SUMMARY_COLUMNS = [
    "variant",
    "variable",
    "phase",
    "n_observations",
    "phase_gate_count",
    "phase_gate_fraction",
    "median_abs_event_minus_abs_null_z",
    "median_event_minus_null_phase_z",
    "majority_gate",
]


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def ensure_dirs() -> None:
    for path in (OUT, FIG, TABLES):
        path.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in columns})


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def md_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    if not rows:
        return "_No rows._"
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        vals = []
        for col in columns:
            val = row.get(col, "")
            if isinstance(val, float):
                vals.append("NA" if not math.isfinite(val) else f"{val:.4g}")
            else:
                vals.append(str(val).replace("\n", " ").replace("|", "\\|"))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def finite_median(values: Any) -> float:
    arr = np.asarray(values, dtype="float64")
    arr = arr[np.isfinite(arr)]
    return float(np.median(arr)) if arr.size else math.nan


def finite_quantile(values: Any, q: float) -> float:
    arr = np.asarray(values, dtype="float64")
    arr = arr[np.isfinite(arr)]
    return float(np.quantile(arr, q)) if arr.size else math.nan


def bool_from_csv(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def lag_label(lag: float) -> str:
    return f"{lag:.3f}".replace(".", "p")


def parse_variants(text: str) -> list[str]:
    variants = [x.strip() for x in text.split(",") if x.strip()]
    if not variants:
        raise ValueError("At least one detrending variant is required.")
    return variants


def rolling_window_size(t: np.ndarray, window_sec: float) -> tuple[int, int]:
    dt = r4081.median_dt(np.asarray(t, dtype="float64"))
    win = max(5, int(round(window_sec / dt))) if math.isfinite(dt) and dt > 0 else 101
    if win % 2 == 0:
        win += 1
    min_periods = max(3, win // 5)
    return win, min_periods


def preprocess_series(t: np.ndarray, x: np.ndarray, variant: str) -> np.ndarray:
    z = r4002a.robust_z_safe(np.asarray(x, dtype="float64"))
    if variant == "none_z":
        return z

    if variant.startswith("centered_"):
        seconds = float(variant.split("_", 1)[1].replace("s", ""))
        win, min_periods = rolling_window_size(t, seconds)
        smooth = (
            pd.Series(z)
            .rolling(win, center=True, min_periods=min_periods)
            .mean()
            .interpolate(limit_direction="both")
            .to_numpy(dtype="float64")
        )
        return r4002a.robust_z_safe(z - smooth)

    if variant.startswith("past_"):
        seconds = float(variant.split("_", 1)[1].replace("s", ""))
        win, min_periods = rolling_window_size(t, seconds)
        smooth = pd.Series(z).shift(1).rolling(win, center=False, min_periods=min_periods).mean()
        smooth = smooth.fillna(0.0).to_numpy(dtype="float64")
        return r4002a.robust_z_safe(z - smooth)

    raise ValueError(f"Unknown detrending variant: {variant}")


def read_events() -> pd.DataFrame:
    if not EVENT_PATH.exists():
        raise FileNotFoundError(f"Missing {rel(EVENT_PATH)}")
    events = pd.read_csv(EVENT_PATH)
    for col in ["event_id", "ob", "event_t"]:
        events[col] = pd.to_numeric(events[col], errors="coerce")
    events = events.dropna(subset=["event_id", "ob", "dataset", "event_t", "event_type"]).copy()
    events["event_id"] = events["event_id"].astype("int64")
    events["ob"] = events["ob"].astype("int64")
    return events.sort_values(["ob", "event_t"], kind="mergesort").reset_index(drop=True)


def b3_abs_lookup() -> dict[int, float]:
    if not OBSERVED_PATH.exists():
        raise FileNotFoundError(f"Missing {rel(OBSERVED_PATH)}")
    rows = pd.read_csv(OBSERVED_PATH)
    rows = rows[rows["target_id"].astype(str).eq(TARGET_ID)].copy()
    rows["ob"] = pd.to_numeric(rows["ob"], errors="coerce").astype("Int64")
    rows["b3_event_direction_abs_z"] = pd.to_numeric(rows["b3_event_direction_abs_z"], errors="coerce")
    out: dict[int, float] = {}
    for ob, d in rows.groupby("ob", sort=True):
        out[int(ob)] = finite_median(d["b3_event_direction_abs_z"])
    return out


def survivor_observations() -> list[int]:
    if not CLASS_PATH.exists():
        return [2, 5, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
    rows = pd.read_csv(CLASS_PATH)
    rows["ob"] = pd.to_numeric(rows["ob"], errors="coerce").astype("Int64")
    rows["t1_gate_k_values"] = rows["t1_gate_k_values"].fillna("").astype(str)
    both = rows[rows["t1_gate_k_values"].str.contains("8") & rows["t1_gate_k_values"].str.contains("10")]
    return sorted(int(x) for x in both["ob"].dropna().tolist())


def local_cache_path(ob: int, k: int, lag_sec: float, frame_stride: int, max_focals: int) -> Path:
    return LOCAL_CACHE / f"Ob{ob}_k{k}_lag{lag_label(lag_sec)}_stride{frame_stride}_focals{max_focals}.csv"


def build_record_from_cache(path: Path, variant: str) -> dict[str, np.ndarray]:
    if not path.exists():
        raise FileNotFoundError(f"Missing local T1 cache: {rel(path)}")
    frame = pd.read_csv(path)
    t = frame["t"].to_numpy(dtype="float64")
    x = frame[LOCAL_VARIABLE].to_numpy(dtype="float64")
    return {"t": t, LOCAL_VARIABLE: preprocess_series(t, x, variant)}


def gate_values(local_abs: float, control_abs_values: list[float], b3_abs: float) -> dict[str, Any]:
    controls = np.asarray(control_abs_values, dtype="float64")
    controls = controls[np.isfinite(controls)]
    null_med = float(np.median(controls)) if controls.size else math.nan
    p_ge = float(np.mean(controls >= local_abs)) if controls.size and math.isfinite(local_abs) else math.nan
    gap = local_abs - null_med if math.isfinite(local_abs) and math.isfinite(null_med) else math.nan
    ratio = local_abs / b3_abs if math.isfinite(local_abs) and math.isfinite(b3_abs) and b3_abs > 1e-12 else math.nan
    passed = bool(
        math.isfinite(gap)
        and gap > GAP_GATE
        and math.isfinite(p_ge)
        and p_ge <= P_GATE
        and math.isfinite(ratio)
        and ratio >= RATIO_GATE
    )
    return {
        "local_non_event_direction_abs_median_z": null_med,
        "local_event_minus_non_event_direction_z": gap,
        "p_non_event_direction_ge_event": p_ge,
        "local_to_b3_direction_ratio": ratio,
        "pass": passed,
    }


def run_survival_challenge(
    *,
    events: pd.DataFrame,
    variants: list[str],
    n_controls: int,
    prepost_sec: float,
    exclusion_sec: float,
    lag_sec: float,
    frame_stride: int,
    max_focals: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    b3_lookup = b3_abs_lookup()
    rng = np.random.default_rng(RNG_SEED)
    rows: list[dict[str, Any]] = []
    for variant in variants:
        print(f"[4142] survival variant {variant}", flush=True)
        for ob, events_ob in events.groupby("ob", sort=True):
            ob_int = int(ob)
            dataset = str(events_ob["dataset"].iloc[0])
            true_times = pd.to_numeric(events_ob["event_t"], errors="coerce").to_numpy(dtype="float64")
            b3_abs = b3_lookup.get(ob_int, math.nan)
            for k in (8, 10):
                path = local_cache_path(ob_int, k, lag_sec, frame_stride, max_focals)
                rec = build_record_from_cache(path, variant)
                _, local_abs = r4141.direction_abs_from_record(rec, events_ob, LOCAL_VARIABLE, prepost_sec)
                controls = [
                    r4141.sample_like_events(
                        events_ob,
                        rec["t"],
                        rng,
                        prepost_sec,
                        exclusion_sec,
                        avoid_times=true_times,
                        event_id_offset=(ob_int * 1_000_000 + k * 10_000 + idx * 100),
                    )
                    for idx in range(n_controls)
                ]
                control_abs = [
                    r4141.direction_abs_from_record(rec, sampled, LOCAL_VARIABLE, prepost_sec)[1]
                    for sampled in controls
                ]
                gv = gate_values(local_abs, control_abs, b3_abs)
                rows.append(
                    {
                        "variant": variant,
                        "ob": ob_int,
                        "dataset": dataset,
                        "k": int(k),
                        "n_events": int(len(events_ob)),
                        "local_event_direction_abs_z": local_abs,
                        "local_non_event_direction_abs_median_z": gv["local_non_event_direction_abs_median_z"],
                        "local_event_minus_non_event_direction_z": gv["local_event_minus_non_event_direction_z"],
                        "p_non_event_direction_ge_event": gv["p_non_event_direction_ge_event"],
                        "local_to_b3_direction_ratio": gv["local_to_b3_direction_ratio"],
                        "event_conditioned_local_gate": bool(gv["pass"]),
                    }
                )

    summary: list[dict[str, Any]] = []
    table = pd.DataFrame(rows)
    table["event_conditioned_local_gate"] = table["event_conditioned_local_gate"].map(bool_from_csv)
    for variant, d in table.groupby("variant", sort=False):
        ob_rows = []
        for ob, g in d.groupby("ob", sort=True):
            k8 = bool(g[(g["k"] == 8) & g["event_conditioned_local_gate"]].shape[0])
            k10 = bool(g[(g["k"] == 10) & g["event_conditioned_local_gate"]].shape[0])
            ob_rows.append({"ob": int(ob), "k8": k8, "k10": k10, "both": k8 and k10, "any": k8 or k10})
        both_obs = [str(r["ob"]) for r in ob_rows if r["both"]]
        any_obs = [str(r["ob"]) for r in ob_rows if r["any"]]
        summary.append(
            {
                "variant": variant,
                "n_observations": int(len(ob_rows)),
                "n_both": int(sum(1 for r in ob_rows if r["both"])),
                "n_any": int(sum(1 for r in ob_rows if r["any"])),
                "n_k8": int(sum(1 for r in ob_rows if r["k8"])),
                "n_k10": int(sum(1 for r in ob_rows if r["k10"])),
                "both_fraction": float(sum(1 for r in ob_rows if r["both"]) / len(ob_rows)) if ob_rows else math.nan,
                "any_fraction": float(sum(1 for r in ob_rows if r["any"]) / len(ob_rows)) if ob_rows else math.nan,
                "delta_both_vs_4081c": int(sum(1 for r in ob_rows if r["both"]) - BASELINE_N_BOTH),
                "delta_any_vs_4081c": int(sum(1 for r in ob_rows if r["any"]) - BASELINE_N_ANY),
                "both_observations": ",".join(both_obs),
                "any_observations": ",".join(any_obs),
            }
        )
    return rows, summary


def event_direction_sign(event_type: str) -> float:
    if event_type == "low_to_high":
        return 1.0
    if event_type == "high_to_low":
        return -1.0
    return math.nan


def align_phase(frame: pd.DataFrame, events: pd.DataFrame, rel_grid: np.ndarray, value_col: str) -> pd.DataFrame:
    t = frame["t"].to_numpy(dtype="float64")
    x = frame[value_col].to_numpy(dtype="float64")
    rows: list[dict[str, Any]] = []
    for event in events.itertuples(index=False):
        sign = event_direction_sign(str(event.event_type))
        if not math.isfinite(sign):
            continue
        target = float(event.event_t) + rel_grid
        valid = (target >= np.nanmin(t)) & (target <= np.nanmax(t))
        y = np.full(rel_grid.shape, np.nan, dtype="float64")
        if np.any(valid):
            y[valid] = np.interp(target[valid], t, x)
        for rel_t, val in zip(rel_grid, y):
            if not math.isfinite(float(val)):
                continue
            rows.append(
                {
                    "event_id": int(event.event_id),
                    "ob": int(event.ob),
                    "dataset": str(event.dataset),
                    "event_t": float(event.event_t),
                    "event_type": str(event.event_type),
                    "relative_time_sec": float(rel_t),
                    "value_z": float(val),
                    "direction_aligned_value_z": float(sign * val),
                }
            )
    return pd.DataFrame(rows)


def phase_value(aligned: pd.DataFrame, phase: str) -> float:
    _, lo, hi = next(row for row in PHASE_BINS if row[0] == phase)
    upper = aligned["relative_time_sec"] < hi if hi <= 0 else aligned["relative_time_sec"] <= hi
    d = aligned[(aligned["relative_time_sec"] >= lo) & upper]
    return finite_median(d["direction_aligned_value_z"].to_numpy(dtype="float64")) if not d.empty else math.nan


def run_phase_challenge(
    *,
    events: pd.DataFrame,
    variants: list[str],
    obs: list[int],
    n_controls: int,
    prepost_sec: float,
    exclusion_sec: float,
    rel_step: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rel_grid = np.round(np.arange(-0.50, 0.50 + rel_step / 2, rel_step), 10)
    rows: list[dict[str, Any]] = []
    rng = np.random.default_rng(RNG_SEED + 90_000)
    for variant in variants:
        print(f"[4142] phase variant {variant}", flush=True)
        for ob in obs:
            frame_path = SPATIAL_4084 / f"Ob{ob}" / "local_spatial_metric_frame.csv"
            if not frame_path.exists():
                raise FileNotFoundError(f"Missing 4084 spatial frame: {rel(frame_path)}")
            frame = pd.read_csv(frame_path, usecols=lambda c: c in {"ob", "dataset", "t", PHASE_VARIABLE})
            frame = frame.sort_values("t", kind="mergesort").reset_index(drop=True)
            frame["value_4142"] = preprocess_series(
                frame["t"].to_numpy(dtype="float64"),
                frame[PHASE_VARIABLE].to_numpy(dtype="float64"),
                variant,
            )
            dataset = str(frame["dataset"].iloc[0])
            events_ob = events[(events["ob"] == ob) & events["dataset"].eq(dataset)].copy().reset_index(drop=True)
            if events_ob.empty:
                continue
            real_aligned = align_phase(frame, events_ob, rel_grid, "value_4142")
            t = frame["t"].to_numpy(dtype="float64")
            true_times = pd.to_numeric(events_ob["event_t"], errors="coerce").to_numpy(dtype="float64")
            null_phase: dict[str, list[float]] = {phase: [] for phase, _, _ in PHASE_BINS}
            for idx in range(n_controls):
                sampled = r4141.sample_like_events(
                    events_ob,
                    t,
                    rng,
                    prepost_sec,
                    exclusion_sec,
                    avoid_times=true_times,
                    event_id_offset=(10_000_000 + ob * 10_000 + idx * 100),
                )
                aligned = align_phase(frame, sampled, rel_grid, "value_4142")
                for phase, _, _ in PHASE_BINS:
                    null_phase[phase].append(phase_value(aligned, phase))
            for phase, _, _ in PHASE_BINS:
                real = phase_value(real_aligned, phase)
                null = np.asarray(null_phase[phase], dtype="float64")
                null = null[np.isfinite(null)]
                null_med = float(np.median(null)) if null.size else math.nan
                null_abs_med = float(np.median(np.abs(null))) if null.size else math.nan
                event_minus_null = real - null_med if math.isfinite(real) and math.isfinite(null_med) else math.nan
                abs_gap = abs(real) - null_abs_med if math.isfinite(real) and math.isfinite(null_abs_med) else math.nan
                p_ge = float(np.mean(np.abs(null) >= abs(real))) if null.size and math.isfinite(real) else math.nan
                gate = bool(math.isfinite(abs_gap) and abs_gap > GAP_GATE and math.isfinite(p_ge) and p_ge <= P_GATE)
                rows.append(
                    {
                        "variant": variant,
                        "ob": int(ob),
                        "dataset": dataset,
                        "variable": PHASE_VARIABLE,
                        "phase": phase,
                        "n_events": int(len(events_ob)),
                        "real_phase_aligned_z": real,
                        "null_phase_median_aligned_z": null_med,
                        "null_phase_abs_median_z": null_abs_med,
                        "event_minus_null_phase_z": event_minus_null,
                        "abs_event_minus_abs_null_z": abs_gap,
                        "p_null_abs_ge_real_abs": p_ge,
                        "phase_gate": gate,
                    }
                )

    phase_df = pd.DataFrame(rows)
    phase_df["phase_gate"] = phase_df["phase_gate"].map(bool_from_csv)
    summary: list[dict[str, Any]] = []
    majority = int(math.floor(len(obs) / 2) + 1)
    for (variant, variable, phase), d in phase_df.groupby(["variant", "variable", "phase"], sort=False):
        gate_count = int(d["phase_gate"].sum())
        summary.append(
            {
                "variant": variant,
                "variable": variable,
                "phase": phase,
                "n_observations": int(d["ob"].nunique()),
                "phase_gate_count": gate_count,
                "phase_gate_fraction": float(gate_count / d["ob"].nunique()) if d["ob"].nunique() else math.nan,
                "median_abs_event_minus_abs_null_z": finite_median(d["abs_event_minus_abs_null_z"]),
                "median_event_minus_null_phase_z": finite_median(d["event_minus_null_phase_z"]),
                "majority_gate": bool(gate_count >= majority),
            }
        )
    return rows, summary


def make_figures(variant_summary: pd.DataFrame, phase_summary: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.2), constrained_layout=True)
    d = variant_summary.copy()
    x = np.arange(len(d))
    ax.bar(x - 0.18, d["n_both"], width=0.36, color="#4c78a8", label="both-scale")
    ax.bar(x + 0.18, d["n_any"], width=0.36, color="#72a24d", label="any-scale")
    ax.axhline(BASELINE_N_BOTH, color="#333333", linestyle="--", linewidth=1.0, label="4081c both=14")
    ax.set_xticks(x)
    ax.set_xticklabels(d["variant"], rotation=25, ha="right")
    ax.set_ylabel("surviving observations out of 19")
    ax.set_title("4142 T1 survival under detrending variants")
    ax.set_ylim(0, 19)
    ax.legend(frameon=False, fontsize=8)
    fig.savefig(FIG / "4142_survival_detrending_variants.png", dpi=180)
    plt.close(fig)

    near = phase_summary[phase_summary["phase"].eq("near_pre")].copy()
    if not near.empty:
        fig, ax = plt.subplots(figsize=(7.2, 4.2), constrained_layout=True)
        x = np.arange(len(near))
        ax.bar(x, near["phase_gate_count"], color="#b27946")
        ax.axhline(math.floor(float(near["n_observations"].iloc[0]) / 2) + 1, color="#333333", linestyle="--", linewidth=1.0, label="majority")
        ax.set_xticks(x)
        ax.set_xticklabels(near["variant"], rotation=25, ha="right")
        ax.set_ylabel("near-pre phase gates")
        ax.set_title("4142 all-tangential near-pre profile sensitivity")
        ax.set_ylim(0, max(1, int(near["n_observations"].max())))
        ax.legend(frameon=False, fontsize=8)
        fig.savefig(FIG / "4142_near_pre_phase_detrending_variants.png", dpi=180)
        plt.close(fig)


def decide(variant_summary: list[dict[str, Any]], phase_summary: list[dict[str, Any]]) -> dict[str, Any]:
    by_variant = {str(row["variant"]): row for row in variant_summary}
    phase_by_variant = {
        str(row["variant"]): row
        for row in phase_summary
        if str(row.get("phase")) == "near_pre" and str(row.get("variable")) == PHASE_VARIABLE
    }
    centered = by_variant.get("centered_1s", {})
    past = by_variant.get("past_1s", {})
    none = by_variant.get("none_z", {})
    centered_both = int(centered.get("n_both", -999))
    past_both = int(past.get("n_both", -999))
    none_both = int(none.get("n_both", -999))
    past_near_pre = int(phase_by_variant.get("past_1s", {}).get("phase_gate_count", -999))

    if abs(centered_both - BASELINE_N_BOTH) > 2:
        gate_result = "boundary_recomputed_centered_baseline_shift"
        interpretation = (
            "The recomputed centered run differs materially from frozen 4081c; "
            "inspect control sampling before using detrending comparisons."
        )
        next_nodes = ["4142_control_sampling_audit"]
    elif past_both >= 12 and past_near_pre >= 6:
        gate_result = "pass_core_and_near_pre_detrending_challenge"
        interpretation = (
            "The core both-scale T1 survival and the weaker near-pre profile both "
            "survive the past-only detrending challenge."
        )
        next_nodes = ["4143_local_affine_conditioning_QC"]
    elif past_both >= 12:
        gate_result = "pass_core_survival_but_near_pre_profile_boundary"
        interpretation = (
            "The main T1 survival result survives past-only detrending, but the "
            "near-pre phase profile should remain descriptive or be softened."
        )
        next_nodes = ["4143_local_affine_conditioning_QC"]
    elif past_both >= 8:
        gate_result = "boundary_causal_detrending_reduces_core_survival"
        interpretation = (
            "Past-only detrending reduces the core T1 survival count; keep the "
            "T1 result but soften robustness language and inspect which observations flip."
        )
        next_nodes = ["4142_flip_audit", "4143_local_affine_conditioning_QC"]
    else:
        gate_result = "fail_core_survival_detrending_challenge"
        interpretation = (
            "The core T1 survival result does not survive the past-only detrending "
            "challenge; manuscript claims must be revised before further hardening."
        )
        next_nodes = ["revise_T1_claim_boundary_before_4143"]

    return {
        "node": NODE,
        "date": DATE,
        "question": "Does the T1 survival result depend on centered detrending or future-window information?",
        "gate_result": gate_result,
        "interpretation": interpretation,
        "primary_metrics": {
            "baseline_4081c_n_both": BASELINE_N_BOTH,
            "baseline_4081c_n_any": BASELINE_N_ANY,
            "centered_1s_n_both": centered_both,
            "past_1s_n_both": past_both,
            "none_z_n_both": none_both,
            "past_1s_near_pre_phase_gate_count": past_near_pre,
        },
        "variant_summary": variant_summary,
        "phase_near_pre_summary": [row for row in phase_summary if str(row.get("phase")) == "near_pre"],
        "does_not_prove": [
            "biological mechanism",
            "online prediction",
            "universal T1 law",
            "formal p-value for 4141",
            "local affine conditioning robustness",
        ],
        "next": next_nodes,
    }


def write_config(args: argparse.Namespace, variants: list[str], phase_obs: list[int]) -> None:
    text = dedent(
        f"""\
        node: {NODE}
        date: {DATE}
        node_type: submission_hardening_artifact_control
        survival_source: Output/4141/cache
        phase_source: Output/4084/per_ob
        events: Output/3045/tables/transition_events.csv
        variants: {variants}
        k_values: [8, 10]
        lag_sec: {args.lag}
        frame_stride: {args.frame_stride}
        max_focals_per_frame: {args.max_focals_per_frame}
        n_controls: {args.n_controls}
        prepost_sec: {args.prepost_sec}
        exclusion_sec: {args.exclusion_sec}
        phase_observations: {phase_obs}
        """
    )
    (OUT / "config.yaml").write_text(text, encoding="utf-8")


def write_summary(
    decision: dict[str, Any],
    variant_summary: list[dict[str, Any]],
    phase_summary: list[dict[str, Any]],
    args: argparse.Namespace,
) -> None:
    near = [row for row in phase_summary if str(row.get("phase")) == "near_pre"]
    text = f"""# Node 4142 Summary

## Question

Does the T1 result depend on the centered 1-second detrending used in the
frozen 4081/4084 pipeline?

## Method

The node reuses existing local T1 frame caches and raw 4084 spatial frames.
It does not redefine the local affine observable.

Three detrending variants are tested by default:

```text
centered_1s = frozen-style within-observation robust-z, centered rolling mean subtraction, robust-z again
past_1s     = same window length, but the smooth trend uses only earlier samples
none_z      = within-observation robust-z only, no smooth trend subtraction
```

For the survival gate, each variant reruns the event/control comparison for
`local_tangential_speed_mean` at `k=8` and `k=10`, using the frozen gate:

```text
gap > {GAP_GATE}
p_non_event_direction_ge_event <= {P_GATE}
local_to_B3_ratio >= {RATIO_GATE}
```

For the weaker phase result, the node reruns the 4085-style phase test for
`all_tangential` in the 14 both-scale survivor observations.

## Survival Results

{md_table(variant_summary, VARIANT_SUMMARY_COLUMNS)}

## Near-Pre Phase Results

{md_table(near, PHASE_SUMMARY_COLUMNS)}

## Decision

`{decision["gate_result"]}`

{decision["interpretation"]}

## Boundary

This node tests detrending sensitivity only. It does not test local-affine
conditioning, formal high-B omnibus p-values, or biological mechanism.

## Next

{md_table([{"next": x} for x in decision["next"]], ["next"])}

## Artifacts

- `Output/4142/survival_detrending_rows.csv`
- `Output/4142/survival_variant_summary.csv`
- `Output/4142/phase_detrending_rows.csv`
- `Output/4142/phase_variant_summary.csv`
- `Output/4142/figures/4142_survival_detrending_variants.png`
- `Output/4142/figures/4142_near_pre_phase_detrending_variants.png`
- `Output/4142/decision.json`
"""
    (OUT / "4142_summary.md").write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variants", default="centered_1s,past_1s,none_z")
    parser.add_argument("--n-controls", type=int, default=40)
    parser.add_argument("--prepost-sec", type=float, default=0.20)
    parser.add_argument("--exclusion-sec", type=float, default=0.80)
    parser.add_argument("--lag", type=float, default=0.10)
    parser.add_argument("--frame-stride", type=int, default=2)
    parser.add_argument("--max-focals-per-frame", type=int, default=24)
    parser.add_argument("--phase-rel-step", type=float, default=0.05)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_dirs()
    variants = parse_variants(args.variants)
    events = read_events()
    phase_obs = survivor_observations()
    write_config(args, variants, phase_obs)

    survival_rows, variant_summary = run_survival_challenge(
        events=events,
        variants=variants,
        n_controls=args.n_controls,
        prepost_sec=args.prepost_sec,
        exclusion_sec=args.exclusion_sec,
        lag_sec=args.lag,
        frame_stride=args.frame_stride,
        max_focals=args.max_focals_per_frame,
    )
    phase_rows, phase_summary = run_phase_challenge(
        events=events,
        variants=variants,
        obs=phase_obs,
        n_controls=args.n_controls,
        prepost_sec=args.prepost_sec,
        exclusion_sec=args.exclusion_sec,
        rel_step=args.phase_rel_step,
    )

    write_csv(OUT / "survival_detrending_rows.csv", survival_rows, SURVIVAL_COLUMNS)
    write_csv(TABLES / "survival_detrending_rows.csv", survival_rows, SURVIVAL_COLUMNS)
    write_csv(OUT / "survival_variant_summary.csv", variant_summary, VARIANT_SUMMARY_COLUMNS)
    write_csv(TABLES / "survival_variant_summary.csv", variant_summary, VARIANT_SUMMARY_COLUMNS)
    write_json(OUT / "survival_variant_summary.json", variant_summary)

    write_csv(OUT / "phase_detrending_rows.csv", phase_rows, PHASE_COLUMNS)
    write_csv(TABLES / "phase_detrending_rows.csv", phase_rows, PHASE_COLUMNS)
    write_csv(OUT / "phase_variant_summary.csv", phase_summary, PHASE_SUMMARY_COLUMNS)
    write_csv(TABLES / "phase_variant_summary.csv", phase_summary, PHASE_SUMMARY_COLUMNS)
    write_json(OUT / "phase_variant_summary.json", phase_summary)

    variant_df = pd.DataFrame(variant_summary)
    phase_df = pd.DataFrame(phase_summary)
    make_figures(variant_df, phase_df)

    decision = decide(variant_summary, phase_summary)
    write_json(OUT / "decision.json", decision)
    write_summary(decision, variant_summary, phase_summary, args)
    print(json.dumps(decision, ensure_ascii=False, indent=2), flush=True)
    print(f"Wrote 4142 outputs to {rel(OUT)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
