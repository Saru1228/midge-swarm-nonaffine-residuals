"""4085 event-phase profile of the T1 local non-affine signal.

4084 found a bounded edge/core spatial contrast in the robust survivor class.
This node asks when that contrast appears relative to compact-density
transitions. It reuses the 4084 per-observation local spatial metric frames and
compares transition-aligned profiles against matched non-event windows.
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

import run_4002a_residual_spatial_structure_audit as r4002a  # noqa: E402
import run_4081_global_vs_local_geometry_ladder as r4081  # noqa: E402


OUT = ROOT / "Output" / "4085"
SRC_4084 = ROOT / "Output" / "4084"
NODE = "4085_event_phase_profile_of_t1_signal"
DATE = "2026-08-25"
RNG_SEED = 4085_0101

DEFAULT_VARIABLES = [
    "shell_edge_minus_core",
    "all_tangential",
    "shell_core_tangential",
    "shell_middle_tangential",
    "shell_edge_tangential",
    "shell_radius_corr_tangential",
    "density_dense_tangential",
    "density_sparse_minus_dense",
]

PHASE_BINS = [
    ("early_pre", -0.50, -0.25),
    ("near_pre", -0.25, 0.00),
    ("near_post", 0.00, 0.25),
    ("late_post", 0.25, 0.50),
]

EVENT_TYPES = {"low_to_high", "high_to_low"}

PROFILE_COLUMNS = [
    "ob",
    "variable",
    "relative_time_sec",
    "real_median_aligned_z",
    "real_q25_aligned_z",
    "real_q75_aligned_z",
    "null_median_aligned_z",
    "null_q25_aligned_z",
    "null_q75_aligned_z",
    "real_minus_null_aligned_z",
    "n_events",
]

EVENT_TYPE_COLUMNS = [
    "ob",
    "variable",
    "event_type",
    "relative_time_sec",
    "median_value_z",
    "q25_value_z",
    "q75_value_z",
    "n_events",
]

PHASE_COLUMNS = [
    "ob",
    "variable",
    "n_events",
    "phase",
    "real_phase_aligned_z",
    "null_phase_median_aligned_z",
    "null_phase_abs_median_z",
    "event_minus_null_phase_z",
    "abs_event_minus_abs_null_z",
    "p_null_abs_ge_real_abs",
    "phase_gate",
]

OB_COLUMNS = [
    "ob",
    "target_variable",
    "n_events",
    "peak_phase",
    "peak_abs_event_minus_abs_null_z",
    "peak_p_null_abs_ge_real_abs",
    "phase_gate_any",
    "event_centered_gate",
    "phase_class",
    "interpretation",
]

VARIABLE_COLUMNS = [
    "variable",
    "phase",
    "n_ob_tested",
    "phase_gate_count",
    "phase_gate_fraction",
    "median_abs_event_minus_abs_null_z",
    "median_event_minus_null_phase_z",
    "majority_gate",
    "interpretation",
]


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in columns})


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def finite_median(values: list[float] | np.ndarray | pd.Series) -> float:
    arr = np.asarray(values, dtype="float64")
    arr = arr[np.isfinite(arr)]
    return float(np.median(arr)) if arr.size else math.nan


def finite_quantile(values: list[float] | np.ndarray | pd.Series, q: float) -> float:
    arr = np.asarray(values, dtype="float64")
    arr = arr[np.isfinite(arr)]
    return float(np.quantile(arr, q)) if arr.size else math.nan


def md_table(rows: list[dict[str, object]], columns: list[str]) -> str:
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
                vals.append("NA" if not np.isfinite(val) else f"{val:.4g}")
            else:
                vals.append(str(val).replace("\n", " ").replace("|", "\\|"))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def bool_from_csv(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def parse_variables(text: str) -> list[str]:
    return [x.strip() for x in text.split(",") if x.strip()]


def read_obs(arg: str) -> list[int]:
    if arg.lower() in {"4084", "robust", "robust-survivors"}:
        path = SRC_4084 / "ob_spatial_taxonomy.csv"
        if not path.exists():
            raise FileNotFoundError(f"Missing {path}")
        d = pd.read_csv(path)
        d["ob"] = pd.to_numeric(d["ob"], errors="coerce").astype("int64")
        return sorted(int(x) for x in d["ob"].tolist())
    if "-" in arg and "," not in arg:
        a, b = arg.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in arg.split(",") if x.strip()]


def event_direction_sign(event_type: str) -> float:
    if event_type == "low_to_high":
        return 1.0
    if event_type == "high_to_low":
        return -1.0
    return math.nan


def read_frame(ob: int, variables: list[str]) -> pd.DataFrame:
    path = SRC_4084 / "per_ob" / f"Ob{ob}" / "local_spatial_metric_frame.csv"
    if not path.exists():
        raise FileNotFoundError(f"Run 4084 first; missing {path}")
    usecols = ["ob", "dataset", "t"]
    for var in variables:
        col = f"{var}__resid4084"
        usecols.append(col)
    d = pd.read_csv(path, usecols=lambda c: c in set(usecols))
    missing = [f"{var}__resid4084" for var in variables if f"{var}__resid4084" not in d.columns]
    if missing:
        raise ValueError(f"Missing 4084 residual columns for Ob{ob}: {missing}")
    return d.sort_values("t").reset_index(drop=True)


def align_events(
    frame: pd.DataFrame,
    events: pd.DataFrame,
    variables: list[str],
    rel_grid: np.ndarray,
) -> pd.DataFrame:
    t = frame["t"].to_numpy(dtype="float64")
    rows: list[dict[str, object]] = []
    for event in events.itertuples(index=False):
        sign = event_direction_sign(str(event.event_type))
        if not np.isfinite(sign):
            continue
        target = float(event.event_t) + rel_grid
        valid = (target >= np.nanmin(t)) & (target <= np.nanmax(t))
        for var in variables:
            x = frame[f"{var}__resid4084"].to_numpy(dtype="float64")
            y = np.full(rel_grid.shape, np.nan, dtype="float64")
            if np.any(valid):
                y[valid] = np.interp(target[valid], t, x)
            for rel_t, value in zip(rel_grid, y):
                if not np.isfinite(value):
                    continue
                rows.append(
                    {
                        "event_id": int(event.event_id),
                        "ob": int(event.ob),
                        "dataset": str(event.dataset),
                        "event_t": float(event.event_t),
                        "event_type": str(event.event_type),
                        "variable": var,
                        "relative_time_sec": float(rel_t),
                        "value_z": float(value),
                        "direction_aligned_value_z": float(sign * value),
                    }
                )
    return pd.DataFrame(rows)


def summarize_real_profile(aligned: pd.DataFrame, variables: list[str], rel_grid: np.ndarray) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    profile_rows: list[dict[str, object]] = []
    event_type_rows: list[dict[str, object]] = []
    ob = int(aligned["ob"].iloc[0]) if not aligned.empty else -1
    for var in variables:
        d_var = aligned[aligned["variable"].eq(var)]
        for rel_t in rel_grid:
            d = d_var[np.isclose(d_var["relative_time_sec"], rel_t)]
            vals = d["direction_aligned_value_z"].to_numpy(dtype="float64")
            profile_rows.append(
                {
                    "ob": ob,
                    "variable": var,
                    "relative_time_sec": float(rel_t),
                    "real_median_aligned_z": finite_median(vals),
                    "real_q25_aligned_z": finite_quantile(vals, 0.25),
                    "real_q75_aligned_z": finite_quantile(vals, 0.75),
                    "n_events": int(d["event_id"].nunique()),
                }
            )
            for event_type in sorted(EVENT_TYPES):
                e = d[d["event_type"].eq(event_type)]
                raw = e["value_z"].to_numpy(dtype="float64")
                event_type_rows.append(
                    {
                        "ob": ob,
                        "variable": var,
                        "event_type": event_type,
                        "relative_time_sec": float(rel_t),
                        "median_value_z": finite_median(raw),
                        "q25_value_z": finite_quantile(raw, 0.25),
                        "q75_value_z": finite_quantile(raw, 0.75),
                        "n_events": int(e["event_id"].nunique()),
                    }
                )
    return profile_rows, event_type_rows


def profile_medians(aligned: pd.DataFrame, variables: list[str], rel_grid: np.ndarray) -> dict[tuple[str, float], float]:
    out: dict[tuple[str, float], float] = {}
    for var in variables:
        d_var = aligned[aligned["variable"].eq(var)]
        for rel_t in rel_grid:
            d = d_var[np.isclose(d_var["relative_time_sec"], rel_t)]
            out[(var, float(rel_t))] = finite_median(d["direction_aligned_value_z"].to_numpy(dtype="float64"))
    return out


def phase_value(aligned: pd.DataFrame, variable: str, phase: str) -> float:
    _, lo, hi = next(row for row in PHASE_BINS if row[0] == phase)
    upper = aligned["relative_time_sec"] < hi if hi <= 0 else aligned["relative_time_sec"] <= hi
    mask = aligned["variable"].eq(variable) & (aligned["relative_time_sec"] >= lo) & upper
    d = aligned[mask]
    return finite_median(d["direction_aligned_value_z"].to_numpy(dtype="float64"))


def summarize_phase(
    ob: int,
    variables: list[str],
    real_aligned: pd.DataFrame,
    null_phase: dict[tuple[str, str], list[float]],
    gap_gate: float,
    p_gate: float,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for var in variables:
        n_events = int(real_aligned[real_aligned["variable"].eq(var)]["event_id"].nunique())
        for phase, _, _ in PHASE_BINS:
            real = phase_value(real_aligned, var, phase)
            null = np.asarray(null_phase[(var, phase)], dtype="float64")
            null = null[np.isfinite(null)]
            null_med = float(np.median(null)) if null.size else math.nan
            null_abs_med = float(np.median(np.abs(null))) if null.size else math.nan
            event_minus_null = real - null_med if np.isfinite(real) and np.isfinite(null_med) else math.nan
            abs_gap = abs(real) - null_abs_med if np.isfinite(real) and np.isfinite(null_abs_med) else math.nan
            p_ge = float(np.mean(np.abs(null) >= abs(real))) if null.size and np.isfinite(real) else math.nan
            gate = bool(np.isfinite(abs_gap) and abs_gap > gap_gate and np.isfinite(p_ge) and p_ge <= p_gate)
            rows.append(
                {
                    "ob": ob,
                    "variable": var,
                    "n_events": n_events,
                    "phase": phase,
                    "real_phase_aligned_z": real,
                    "null_phase_median_aligned_z": null_med,
                    "null_phase_abs_median_z": null_abs_med,
                    "event_minus_null_phase_z": event_minus_null,
                    "abs_event_minus_abs_null_z": abs_gap,
                    "p_null_abs_ge_real_abs": p_ge,
                    "phase_gate": gate,
                }
            )
    return rows


def run_ob(
    ob: int,
    events_all: pd.DataFrame,
    variables: list[str],
    rel_grid: np.ndarray,
    n_replicates: int,
    prepost_sec: float,
    exclusion_sec: float,
    gap_gate: float,
    p_gate: float,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    ob_dir = OUT / "per_ob" / f"Ob{ob}"
    profile_path = ob_dir / "real_profile_rows.csv"
    event_type_path = ob_dir / "event_type_profile_rows.csv"
    phase_path = ob_dir / "phase_rows.csv"
    if profile_path.exists() and event_type_path.exists() and phase_path.exists():
        profile_rows = list(csv.DictReader(profile_path.open(newline="", encoding="utf-8")))
        event_type_rows = list(csv.DictReader(event_type_path.open(newline="", encoding="utf-8")))
        phase_rows = list(csv.DictReader(phase_path.open(newline="", encoding="utf-8")))
        return profile_rows, event_type_rows, phase_rows

    ob_dir.mkdir(parents=True, exist_ok=True)
    frame = read_frame(ob, variables)
    dataset = str(frame["dataset"].iloc[0])
    events_ob = events_all[(events_all["ob"] == ob) & (events_all["dataset"].eq(dataset))].copy().reset_index(drop=True)
    if events_ob.empty:
        raise RuntimeError(f"No events for Ob{ob}")
    print(f"[4085] Ob{ob}: aligning {len(events_ob)} events", flush=True)
    real_aligned = align_events(frame, events_ob, variables, rel_grid)
    profile_rows, event_type_rows = summarize_real_profile(real_aligned, variables, rel_grid)

    t = frame["t"].to_numpy(dtype="float64")
    rng = np.random.default_rng(RNG_SEED + ob)
    null_profiles: dict[tuple[str, float], list[float]] = {(var, float(rel_t)): [] for var in variables for rel_t in rel_grid}
    null_phase: dict[tuple[str, str], list[float]] = {(var, phase): [] for var in variables for phase, _, _ in PHASE_BINS}
    for rep in range(n_replicates):
        if rep == 0 or rep + 1 == n_replicates or (rep + 1) % 20 == 0:
            print(f"[4085] Ob{ob}: non-event profile replicate {rep + 1}/{n_replicates}", flush=True)
        sampled = r4081.sample_non_event_times(events_ob, t, rng, prepost_sec, exclusion_sec)
        aligned = align_events(frame, sampled, variables, rel_grid)
        med = profile_medians(aligned, variables, rel_grid)
        for key, value in med.items():
            null_profiles[key].append(value)
        for var in variables:
            for phase, _, _ in PHASE_BINS:
                null_phase[(var, phase)].append(phase_value(aligned, var, phase))

    for row in profile_rows:
        key = (str(row["variable"]), float(row["relative_time_sec"]))
        null = np.asarray(null_profiles[key], dtype="float64")
        null = null[np.isfinite(null)]
        row["null_median_aligned_z"] = float(np.median(null)) if null.size else math.nan
        row["null_q25_aligned_z"] = float(np.quantile(null, 0.25)) if null.size else math.nan
        row["null_q75_aligned_z"] = float(np.quantile(null, 0.75)) if null.size else math.nan
        row["real_minus_null_aligned_z"] = (
            float(row["real_median_aligned_z"]) - row["null_median_aligned_z"]
            if np.isfinite(float(row["real_median_aligned_z"])) and np.isfinite(row["null_median_aligned_z"])
            else math.nan
        )

    phase_rows = summarize_phase(ob, variables, real_aligned, null_phase, gap_gate, p_gate)

    write_csv(profile_path, profile_rows, PROFILE_COLUMNS)
    write_csv(event_type_path, event_type_rows, EVENT_TYPE_COLUMNS)
    write_csv(phase_path, phase_rows, PHASE_COLUMNS)
    real_aligned.to_csv(ob_dir / "event_aligned_samples.csv", index=False)
    return profile_rows, event_type_rows, phase_rows


def classify_ob_phase(phase_rows: list[dict[str, object]], target: str) -> dict[str, object]:
    d = pd.DataFrame(phase_rows)
    d = d[d["variable"].eq(target)].copy()
    ob = int(pd.to_numeric(d["ob"], errors="coerce").iloc[0]) if not d.empty else -1
    for col in ["abs_event_minus_abs_null_z", "p_null_abs_ge_real_abs", "real_phase_aligned_z"]:
        d[col] = pd.to_numeric(d[col], errors="coerce")
    d["phase_gate"] = d["phase_gate"].map(bool_from_csv)
    d_sorted = d.sort_values("abs_event_minus_abs_null_z", ascending=False)
    peak = d_sorted.iloc[0].to_dict() if not d_sorted.empty else {}
    gate_any = bool(d["phase_gate"].any()) if not d.empty else False
    near_gate = bool(d[d["phase"].isin(["near_pre", "near_post"])]["phase_gate"].any()) if not d.empty else False
    peak_phase = str(peak.get("phase", ""))
    if gate_any and peak_phase == "near_pre":
        cls = "pre_transition_buildup_candidate"
        interp = "The target edge/core contrast is strongest before the transition."
    elif gate_any and peak_phase == "near_post":
        cls = "post_transition_response_candidate"
        interp = "The target edge/core contrast is strongest just after the transition."
    elif gate_any and peak_phase in {"early_pre", "late_post"}:
        cls = "broad_state_or_offcenter_profile_candidate"
        interp = "The target contrast is event-conditioned but not sharply centered on the transition."
    elif near_gate:
        cls = "weak_event_centered_candidate"
        interp = "A near-transition phase passes, but it is not the strongest phase."
    else:
        cls = "no_clear_phase_gate"
        interp = "No phase bin passes the event-vs-non-event gate for the target contrast."
    return {
        "ob": ob,
        "target_variable": target,
        "n_events": int(pd.to_numeric(d.get("n_events", pd.Series(dtype=float)), errors="coerce").max()) if "n_events" in d else "",
        "peak_phase": peak_phase,
        "peak_abs_event_minus_abs_null_z": float(peak.get("abs_event_minus_abs_null_z", math.nan)),
        "peak_p_null_abs_ge_real_abs": float(peak.get("p_null_abs_ge_real_abs", math.nan)),
        "phase_gate_any": gate_any,
        "event_centered_gate": near_gate,
        "phase_class": cls,
        "interpretation": interp,
    }


def aggregate_variable_phase(phase_rows: list[dict[str, object]], n_ob: int) -> list[dict[str, object]]:
    d = pd.DataFrame(phase_rows)
    if d.empty:
        return []
    for col in ["abs_event_minus_abs_null_z", "event_minus_null_phase_z"]:
        d[col] = pd.to_numeric(d[col], errors="coerce")
    d["phase_gate"] = d["phase_gate"].map(bool_from_csv)
    majority = int(math.floor(n_ob / 2) + 1)
    rows: list[dict[str, object]] = []
    for (var, phase), g in d.groupby(["variable", "phase"], sort=True):
        gate_count = int(g["phase_gate"].sum())
        if gate_count >= majority:
            interp = "majority replicated phase"
        elif gate_count > 0:
            interp = "minority or observation-specific phase"
        else:
            interp = "no phase gate"
        rows.append(
            {
                "variable": var,
                "phase": phase,
                "n_ob_tested": n_ob,
                "phase_gate_count": gate_count,
                "phase_gate_fraction": gate_count / n_ob if n_ob else math.nan,
                "median_abs_event_minus_abs_null_z": finite_median(g["abs_event_minus_abs_null_z"]),
                "median_event_minus_null_phase_z": finite_median(g["event_minus_null_phase_z"]),
                "majority_gate": bool(gate_count >= majority),
                "interpretation": interp,
            }
        )
    phase_order = {name: i for i, (name, _, _) in enumerate(PHASE_BINS)}
    return sorted(
        rows,
        key=lambda r: (str(r["variable"]), phase_order.get(str(r["phase"]), 99)),
    )


def aggregate_profiles(profile_rows: list[dict[str, object]]) -> pd.DataFrame:
    d = pd.DataFrame(profile_rows)
    if d.empty:
        return pd.DataFrame()
    for col in ["relative_time_sec", "real_median_aligned_z", "null_median_aligned_z", "real_minus_null_aligned_z"]:
        d[col] = pd.to_numeric(d[col], errors="coerce")
    rows: list[dict[str, object]] = []
    for (var, rel_t), g in d.groupby(["variable", "relative_time_sec"], sort=True):
        rows.append(
            {
                "variable": var,
                "relative_time_sec": float(rel_t),
                "median_real_aligned_z_across_ob": finite_median(g["real_median_aligned_z"]),
                "q25_real_aligned_z_across_ob": finite_quantile(g["real_median_aligned_z"], 0.25),
                "q75_real_aligned_z_across_ob": finite_quantile(g["real_median_aligned_z"], 0.75),
                "median_null_aligned_z_across_ob": finite_median(g["null_median_aligned_z"]),
                "median_real_minus_null_aligned_z_across_ob": finite_median(g["real_minus_null_aligned_z"]),
                "n_ob": int(g["ob"].nunique()),
            }
        )
    return pd.DataFrame(rows).sort_values(["variable", "relative_time_sec"]).reset_index(drop=True)


def decide(variable_phase_rows: list[dict[str, object]], ob_rows: list[dict[str, object]], target: str) -> dict[str, object]:
    var_df = pd.DataFrame(variable_phase_rows)
    ob_df = pd.DataFrame(ob_rows)
    n_ob = int(ob_df["ob"].nunique()) if not ob_df.empty else 0
    majority = int(math.floor(n_ob / 2) + 1)
    target_phase = var_df[var_df["variable"].eq(target)].copy()
    target_phase["phase_gate_count"] = pd.to_numeric(target_phase["phase_gate_count"], errors="coerce")
    majority_phases = target_phase[target_phase["phase_gate_count"] >= majority]["phase"].astype(str).tolist()
    secondary = var_df[
        (~var_df["variable"].eq(target))
        & (pd.to_numeric(var_df["phase_gate_count"], errors="coerce") >= majority)
    ].copy()
    secondary_candidates = [
        {
            "variable": str(row.variable),
            "phase": str(row.phase),
            "phase_gate_count": int(row.phase_gate_count),
        }
        for row in secondary.itertuples(index=False)
    ]
    near_count = int(target_phase[target_phase["phase"].isin(["near_pre", "near_post"])]["phase_gate_count"].sum()) if not target_phase.empty else 0
    phase_class_counts = ob_df["phase_class"].value_counts().to_dict() if not ob_df.empty else {}

    if n_ob < 5:
        result = "pilot_event_phase_profile_screen_only"
        next_node = "expand_4085_to_4084_robust_survivor_observations"
        interpretation = (
            "Fewer than five observations were tested, so this run is a screen only. "
            "Use it to validate the profile workflow, not as replicated timing evidence."
        )
    elif majority_phases:
        result = "support_replicated_event_phase_profile_for_edge_core_t1"
        next_node = "4086_signed_direction_and_state_decomposition"
        interpretation = (
            f"The target `{target}` has a majority-replicated phase profile in: "
            f"{', '.join(majority_phases)}."
        )
    elif near_count >= majority:
        result = "boundary_event_centered_but_phase_heterogeneous_edge_core_t1"
        next_node = "4086_signed_direction_and_state_decomposition"
        interpretation = (
            f"The target `{target}` has enough near-transition gates in aggregate, but no single phase "
            "dominates across observations."
        )
    elif secondary_candidates:
        result = "boundary_edge_core_no_stable_phase_but_diffuse_t1_has_phase_profile"
        next_node = "4086_signed_direction_and_state_decomposition"
        interp_bits = [f"{r['variable']}:{r['phase']} ({r['phase_gate_count']}/{n_ob})" for r in secondary_candidates]
        interpretation = (
            f"The edge/core target `{target}` has no stable phase-localized profile, but secondary T1 "
            f"variables do: {', '.join(interp_bits)}. This routes interpretation toward signed/state "
            "decomposition before any phase-space claim."
        )
    elif int(ob_df["phase_gate_any"].map(bool_from_csv).sum()) >= majority:
        result = "boundary_broad_or_observation_specific_phase_profile"
        next_node = "4086_signed_direction_and_state_decomposition"
        interpretation = (
            f"The target `{target}` is often event-conditioned in time, but the peak phase varies by observation."
        )
    else:
        result = "boundary_no_stable_event_phase_profile_for_edge_core_t1"
        next_node = "4086_signed_direction_or_review_4085_profile_metric"
        interpretation = (
            f"The target `{target}` does not have a stable phase-localized profile under the current gate."
        )

    return {
        "node": NODE,
        "date": DATE,
        "result": result,
        "target_variable": target,
        "n_observations": n_ob,
        "majority_gate_count": majority,
        "target_majority_phases": majority_phases,
        "secondary_majority_phase_candidates": secondary_candidates,
        "target_near_transition_gate_total": near_count,
        "target_phase_class_counts": phase_class_counts,
        "interpretation": interpretation,
        "phase_space_side_branch": "4085b_phase_space_projection_of_t1_edge_core_signal",
        "next": [next_node],
        "artifacts": [
            "Output/4085/aggregate_profiles.csv",
            "Output/4085/phase_profile_rows.csv",
            "Output/4085/ob_phase_classification.csv",
            "Output/4085/variable_phase_summary.csv",
            "Output/4085/figures/4085_target_profiles.png",
            "Output/4085/figures/4085_target_phase_heatmap.png",
            "Output/4085/figures/4085_variable_phase_gate_counts.png",
        ],
    }


def make_figures(
    aggregate_profile: pd.DataFrame,
    variable_phase: pd.DataFrame,
    phase_rows: pd.DataFrame,
    target: str,
    variables_to_plot: list[str],
) -> None:
    fig_dir = OUT / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    if not aggregate_profile.empty:
        plot_vars = [v for v in variables_to_plot if v in set(aggregate_profile["variable"])]
        fig, axes = plt.subplots(len(plot_vars), 1, figsize=(9.0, max(3.2, 2.7 * len(plot_vars))), sharex=True, constrained_layout=True)
        if len(plot_vars) == 1:
            axes = [axes]
        for ax, var in zip(axes, plot_vars):
            d = aggregate_profile[aggregate_profile["variable"].eq(var)].sort_values("relative_time_sec")
            x = d["relative_time_sec"].to_numpy(dtype="float64")
            real = d["median_real_aligned_z_across_ob"].to_numpy(dtype="float64")
            lo = d["q25_real_aligned_z_across_ob"].to_numpy(dtype="float64")
            hi = d["q75_real_aligned_z_across_ob"].to_numpy(dtype="float64")
            null = d["median_null_aligned_z_across_ob"].to_numpy(dtype="float64")
            ax.plot(x, real, color="#2f6f9f", lw=1.8, label="real aligned")
            ax.fill_between(x, lo, hi, color="#2f6f9f", alpha=0.16, linewidth=0)
            ax.plot(x, null, color="#777777", lw=1.4, linestyle="--", label="matched non-event")
            ax.axvline(0, color="#222222", linewidth=0.8)
            ax.axhline(0, color="#aaaaaa", linewidth=0.7)
            ax.set_ylabel(var)
            ax.grid(color="#dddddd", linewidth=0.7, alpha=0.7)
        axes[0].legend(frameon=False, loc="best")
        axes[0].set_title("4085 event-aligned profiles across robust survivor observations")
        axes[-1].set_xlabel("time relative to transition (sec)")
        fig.savefig(fig_dir / "4085_target_profiles.png", dpi=180)
        plt.close(fig)

    if not phase_rows.empty:
        d = phase_rows[phase_rows["variable"].eq(target)].copy()
        d["abs_event_minus_abs_null_z"] = pd.to_numeric(d["abs_event_minus_abs_null_z"], errors="coerce")
        pivot = d.pivot_table(index="phase", columns="ob", values="abs_event_minus_abs_null_z", aggfunc="first")
        pivot = pivot.reindex([name for name, _, _ in PHASE_BINS])
        fig, ax = plt.subplots(figsize=(10.2, 4.4), constrained_layout=True)
        im = ax.imshow(pivot.to_numpy(dtype="float64"), aspect="auto", cmap="RdYlGn", vmin=-0.15, vmax=0.45)
        ax.set_title(f"4085 target phase excess heatmap: {target}")
        ax.set_xlabel("Observation")
        ax.set_ylabel("Phase")
        ax.set_xticks(np.arange(len(pivot.columns)))
        ax.set_xticklabels([f"Ob{int(x)}" for x in pivot.columns], rotation=45, ha="right")
        ax.set_yticks(np.arange(len(pivot.index)))
        ax.set_yticklabels(pivot.index)
        fig.colorbar(im, ax=ax, label="abs(real phase) - median abs(null)")
        fig.savefig(fig_dir / "4085_target_phase_heatmap.png", dpi=180)
        plt.close(fig)

    if not variable_phase.empty:
        d = variable_phase.copy()
        d["phase_gate_count"] = pd.to_numeric(d["phase_gate_count"], errors="coerce")
        keep_vars = [target, "all_tangential", "shell_core_tangential", "shell_edge_tangential"]
        d = d[d["variable"].isin(keep_vars)].copy()
        phase_order = {name: i for i, (name, _, _) in enumerate(PHASE_BINS)}
        d["phase_order"] = d["phase"].map(phase_order)
        d = d.sort_values(["variable", "phase_order"])
        labels = [f"{row.variable}\n{row.phase}" for row in d.itertuples(index=False)]
        fig, ax = plt.subplots(figsize=(11.0, 5.0), constrained_layout=True)
        x = np.arange(len(d))
        ax.bar(x, d["phase_gate_count"], color="#2f6f9f")
        majority = math.floor(float(d["n_ob_tested"].iloc[0]) / 2) + 1 if len(d) else 1
        ax.axhline(majority, color="#444444", linestyle="--", linewidth=1)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=55, ha="right")
        ax.set_ylabel("observation count passing phase gate")
        ax.set_title("4085 phase gate counts")
        ax.grid(axis="y", color="#dddddd", linewidth=0.7)
        fig.savefig(fig_dir / "4085_variable_phase_gate_counts.png", dpi=180)
        plt.close(fig)


def write_config(args: argparse.Namespace, obs: list[int], variables: list[str]) -> None:
    text = dedent(
        f"""\
        node: {NODE}
        date: {DATE}
        node_type: mechanism
        input_node: 4084_spatial_taxonomy_of_t1_local_nonaffine_signal
        observations: {','.join(str(x) for x in obs)}
        variables: {','.join(variables)}
        target_variable: {args.target_variable}
        relative_time_min_sec: {args.rel_min}
        relative_time_max_sec: {args.rel_max}
        relative_time_step_sec: {args.rel_step}
        n_non_event_replicates: {args.n_replicates}
        phase_gap_gate_z: {args.gap_gate}
        phase_p_gate: {args.p_gate}
        """
    )
    (OUT / "config.yaml").write_text(text, encoding="utf-8")


def write_summary(
    decision: dict[str, object],
    ob_rows: list[dict[str, object]],
    variable_phase_rows: list[dict[str, object]],
    args: argparse.Namespace,
) -> None:
    ob_display = [
        "ob",
        "target_variable",
        "peak_phase",
        "peak_abs_event_minus_abs_null_z",
        "peak_p_null_abs_ge_real_abs",
        "phase_gate_any",
        "event_centered_gate",
        "phase_class",
    ]
    var_display = [
        "variable",
        "phase",
        "phase_gate_count",
        "phase_gate_fraction",
        "median_abs_event_minus_abs_null_z",
        "median_event_minus_null_phase_z",
        "majority_gate",
        "interpretation",
    ]
    target_phase = [r for r in variable_phase_rows if r["variable"] == args.target_variable]
    text = dedent(
        f"""\
        # Node 4085 Summary

        ## Question

        When does the 4084 edge/core T1 local non-affine contrast appear
        relative to compact-density transitions?

        ## What Else Can Be Dug Here

        Before leaving 408x, there are four defensible directions:

        - event-phase profile: when the 4084 edge/core contrast appears;
        - phase-space projection: trajectory through variables such as
          `all_tangential`, `shell_edge_minus_core`, compact state, and possibly
          radial/density coordinates;
        - signed low-to-high versus high-to-low decomposition;
        - failure-boundary sensitivity for Ob1/Ob3/Ob6/Ob8.

        This node runs the first one. The phase-space branch is kept as
        `4085b_phase_space_projection_of_t1_edge_core_signal`, because the
        temporal profile tells us which time slice should be projected.

        ## Inputs

        - `Output/4084/per_ob/Ob*/local_spatial_metric_frame.csv`
        - `Output/3045/tables/transition_events.csv`

        ## Method

        Direction-aligned profiles are built over:

        ```text
        relative time = [{args.rel_min}, {args.rel_max}] sec
        step = {args.rel_step} sec
        matched non-event replicates = {args.n_replicates}
        phase bins = early_pre, near_pre, near_post, late_post
        target variable = {args.target_variable}
        ```

        Low-to-high events are aligned positive and high-to-low events negative.
        The raw event-type profiles are also saved separately, but interpretation
        of signed asymmetry is deferred to 4086.

        ## Decision

        `{decision["result"]}`

        ## Main Reading

        {decision["interpretation"]}

        ```text
        observations tested = {decision["n_observations"]}
        majority gate count = {decision["majority_gate_count"]}
        target near-transition gate total = {decision["target_near_transition_gate_total"]}
        target majority phases = {', '.join(decision["target_majority_phases"]) if decision["target_majority_phases"] else 'none'}
        secondary majority phases = {', '.join(f"{r['variable']}:{r['phase']} ({r['phase_gate_count']}/{decision['n_observations']})" for r in decision["secondary_majority_phase_candidates"]) if decision["secondary_majority_phase_candidates"] else 'none'}
        ```

        ## Target Phase Summary

        {md_table(target_phase, var_display)}

        ## Observation Classification

        {md_table(ob_rows, ob_display)}

        ## Boundary

        A phase profile is interpreted only if it beats matched non-event
        windows. If no single phase dominates, this node routes to signed
        decomposition rather than claiming pre-trigger, trigger, or relaxation.

        ## Next

        `{decision["next"][0]}`

        Side branch available:

        `4085b_phase_space_projection_of_t1_edge_core_signal`

        ## Artifacts

        - `Output/4085/aggregate_profiles.csv`
        - `Output/4085/phase_profile_rows.csv`
        - `Output/4085/ob_phase_classification.csv`
        - `Output/4085/variable_phase_summary.csv`
        - `Output/4085/figures/4085_target_profiles.png`
        - `Output/4085/figures/4085_target_phase_heatmap.png`
        - `Output/4085/figures/4085_variable_phase_gate_counts.png`
        """
    ).lstrip()
    summary = "\n".join(line[8:] if line.startswith("        ") else line for line in text.splitlines()) + "\n"
    (OUT / "4085_summary.md").write_text(summary, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--obs", default="4084")
    parser.add_argument("--variables", default=",".join(DEFAULT_VARIABLES))
    parser.add_argument("--target-variable", default="shell_edge_minus_core")
    parser.add_argument("--rel-min", type=float, default=-0.50)
    parser.add_argument("--rel-max", type=float, default=0.50)
    parser.add_argument("--rel-step", type=float, default=0.05)
    parser.add_argument("--n-replicates", type=int, default=40)
    parser.add_argument("--prepost-sec", type=float, default=0.20)
    parser.add_argument("--exclusion-sec", type=float, default=0.80)
    parser.add_argument("--gap-gate", type=float, default=0.12)
    parser.add_argument("--p-gate", type=float, default=0.25)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    variables = parse_variables(args.variables)
    obs = read_obs(args.obs)
    rel_grid = np.round(np.arange(args.rel_min, args.rel_max + args.rel_step / 2, args.rel_step), 6)
    events = r4002a.read_events()
    write_config(args, obs, variables)

    all_profiles: list[dict[str, object]] = []
    all_event_type_profiles: list[dict[str, object]] = []
    all_phase_rows: list[dict[str, object]] = []
    if args.force:
        for ob in obs:
            ob_dir = OUT / "per_ob" / f"Ob{ob}"
            for name in ["real_profile_rows.csv", "event_type_profile_rows.csv", "phase_rows.csv"]:
                path = ob_dir / name
                if path.exists():
                    path.unlink()

    for ob in obs:
        profile_rows, event_type_rows, phase_rows = run_ob(
            ob=ob,
            events_all=events,
            variables=variables,
            rel_grid=rel_grid,
            n_replicates=args.n_replicates,
            prepost_sec=args.prepost_sec,
            exclusion_sec=args.exclusion_sec,
            gap_gate=args.gap_gate,
            p_gate=args.p_gate,
        )
        all_profiles.extend(profile_rows)
        all_event_type_profiles.extend(event_type_rows)
        all_phase_rows.extend(phase_rows)

    ob_rows = [classify_ob_phase([r for r in all_phase_rows if int(r["ob"]) == ob], args.target_variable) for ob in obs]
    variable_phase_rows = aggregate_variable_phase(all_phase_rows, len(obs))
    aggregate_profile = aggregate_profiles(all_profiles)
    decision = decide(variable_phase_rows, ob_rows, args.target_variable)

    write_csv(OUT / "profile_rows.csv", all_profiles, PROFILE_COLUMNS)
    write_csv(OUT / "tables" / "profile_rows.csv", all_profiles, PROFILE_COLUMNS)
    write_json(OUT / "profile_rows.json", all_profiles)
    write_csv(OUT / "event_type_profile_rows.csv", all_event_type_profiles, EVENT_TYPE_COLUMNS)
    write_csv(OUT / "tables" / "event_type_profile_rows.csv", all_event_type_profiles, EVENT_TYPE_COLUMNS)
    write_csv(OUT / "phase_profile_rows.csv", all_phase_rows, PHASE_COLUMNS)
    write_csv(OUT / "tables" / "phase_profile_rows.csv", all_phase_rows, PHASE_COLUMNS)
    write_json(OUT / "phase_profile_rows.json", all_phase_rows)
    write_csv(OUT / "ob_phase_classification.csv", ob_rows, OB_COLUMNS)
    write_csv(OUT / "tables" / "ob_phase_classification.csv", ob_rows, OB_COLUMNS)
    write_json(OUT / "ob_phase_classification.json", ob_rows)
    write_csv(OUT / "variable_phase_summary.csv", variable_phase_rows, VARIABLE_COLUMNS)
    write_csv(OUT / "tables" / "variable_phase_summary.csv", variable_phase_rows, VARIABLE_COLUMNS)
    write_json(OUT / "variable_phase_summary.json", variable_phase_rows)
    aggregate_profile.to_csv(OUT / "aggregate_profiles.csv", index=False)
    aggregate_profile.to_csv(OUT / "tables" / "aggregate_profiles.csv", index=False)
    write_json(OUT / "decision.json", decision)

    make_figures(
        aggregate_profile,
        pd.DataFrame(variable_phase_rows),
        pd.DataFrame(all_phase_rows),
        args.target_variable,
        [args.target_variable, "all_tangential", "shell_core_tangential", "shell_edge_tangential"],
    )
    write_summary(decision, ob_rows, variable_phase_rows, args)
    print(f"Wrote 4085 outputs to {OUT.relative_to(ROOT)}")
    print(json.dumps(decision, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
