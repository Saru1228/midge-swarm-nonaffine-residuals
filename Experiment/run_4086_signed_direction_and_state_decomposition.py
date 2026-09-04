"""4086 signed direction and state decomposition.

4085 found that the edge/core target has no stable phase profile, while the
diffuse T1 local tangential variable (`all_tangential`) has a near-pre majority
phase gate. This node asks whether the near-pre signal is mirrored between
low-to-high and high-to-low transitions, or dominated by one transition type.
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


OUT = ROOT / "Output" / "4086"
SRC_4084 = ROOT / "Output" / "4084"
NODE = "4086_signed_direction_and_state_decomposition"
DATE = "2026-08-26"
RNG_SEED = 4086_0101

DEFAULT_VARIABLES = [
    "all_tangential",
    "shell_edge_minus_core",
    "shell_core_tangential",
    "shell_middle_tangential",
    "shell_edge_tangential",
]

PHASE_BINS = [
    ("early_pre", -0.50, -0.25),
    ("near_pre", -0.25, 0.00),
    ("near_post", 0.00, 0.25),
    ("late_post", 0.25, 0.50),
]

EVENT_TYPES = ["low_to_high", "high_to_low"]

EVENT_TYPE_COLUMNS = [
    "ob",
    "variable",
    "phase",
    "event_type",
    "n_events",
    "real_phase_median_z",
    "null_phase_median_z",
    "event_minus_null_z",
    "p_null_abs_excess_ge_real_abs_excess",
    "event_type_gate",
]

DECOMP_COLUMNS = [
    "ob",
    "variable",
    "phase",
    "low_to_high_excess_z",
    "high_to_low_excess_z",
    "signed_separation_z",
    "mirror_opposite_sign",
    "mirror_balance",
    "low_to_high_gate",
    "high_to_low_gate",
    "signed_class",
    "interpretation",
]

OB_COLUMNS = [
    "ob",
    "target_variable",
    "target_phase",
    "low_to_high_excess_z",
    "high_to_low_excess_z",
    "signed_separation_z",
    "mirror_balance",
    "low_to_high_gate",
    "high_to_low_gate",
    "signed_class",
    "interpretation",
]

SUMMARY_COLUMNS = [
    "variable",
    "phase",
    "n_ob_tested",
    "mirror_symmetric_count",
    "opposite_sign_imbalanced_count",
    "low_to_high_dominant_count",
    "high_to_low_dominant_count",
    "same_direction_count",
    "no_signed_gate_count",
    "median_low_to_high_excess_z",
    "median_high_to_low_excess_z",
    "median_signed_separation_z",
    "majority_signed_class",
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


def bool_from_csv(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


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


def parse_variables(text: str) -> list[str]:
    return [x.strip() for x in text.split(",") if x.strip()]


def read_obs(arg: str) -> list[int]:
    if arg.lower() in {"4084", "4085", "robust", "robust-survivors"}:
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


def read_frame(ob: int, variables: list[str]) -> pd.DataFrame:
    path = SRC_4084 / "per_ob" / f"Ob{ob}" / "local_spatial_metric_frame.csv"
    if not path.exists():
        raise FileNotFoundError(f"Run 4084 first; missing {path}")
    usecols = {"ob", "dataset", "t", *[f"{var}__resid4084" for var in variables]}
    frame = pd.read_csv(path, usecols=lambda c: c in usecols)
    missing = [f"{var}__resid4084" for var in variables if f"{var}__resid4084" not in frame.columns]
    if missing:
        raise ValueError(f"Missing 4084 residual columns for Ob{ob}: {missing}")
    return frame.sort_values("t").reset_index(drop=True)


def phase_mask(rel: np.ndarray, phase: str) -> np.ndarray:
    _, lo, hi = next(row for row in PHASE_BINS if row[0] == phase)
    upper = rel < hi if hi <= 0 else rel <= hi
    return (rel >= lo) & upper


def event_phase_median(
    frame: pd.DataFrame,
    events: pd.DataFrame,
    variable: str,
    phase: str,
    event_type: str,
    rel_grid: np.ndarray,
) -> tuple[int, float]:
    t = frame["t"].to_numpy(dtype="float64")
    x = frame[f"{variable}__resid4084"].to_numpy(dtype="float64")
    rel_keep = phase_mask(rel_grid, phase)
    vals: list[float] = []
    d = events[events["event_type"].eq(event_type)]
    for event in d.itertuples(index=False):
        target = float(event.event_t) + rel_grid[rel_keep]
        valid = (target >= np.nanmin(t)) & (target <= np.nanmax(t))
        if not np.any(valid):
            continue
        y = np.interp(target[valid], t, x)
        y = y[np.isfinite(y)]
        if y.size:
            vals.append(float(np.median(y)))
    return int(d["event_id"].nunique()), finite_median(vals)


def sample_non_event_times(events_ob: pd.DataFrame, t: np.ndarray, rng: np.random.Generator, prepost_sec: float, exclusion_sec: float) -> pd.DataFrame:
    return r4081.sample_non_event_times(events_ob, t, rng, prepost_sec, exclusion_sec)


def event_type_row(
    ob: int,
    variable: str,
    phase: str,
    event_type: str,
    n_events: int,
    real: float,
    null_values: list[float],
    gap_gate: float,
    p_gate: float,
) -> dict[str, object]:
    null = np.asarray(null_values, dtype="float64")
    null = null[np.isfinite(null)]
    null_med = float(np.median(null)) if null.size else math.nan
    excess = real - null_med if np.isfinite(real) and np.isfinite(null_med) else math.nan
    null_excess = null - null_med if null.size and np.isfinite(null_med) else np.array([], dtype="float64")
    p_ge = float(np.mean(np.abs(null_excess) >= abs(excess))) if null_excess.size and np.isfinite(excess) else math.nan
    gate = bool(np.isfinite(excess) and abs(excess) >= gap_gate and np.isfinite(p_ge) and p_ge <= p_gate)
    return {
        "ob": ob,
        "variable": variable,
        "phase": phase,
        "event_type": event_type,
        "n_events": n_events,
        "real_phase_median_z": real,
        "null_phase_median_z": null_med,
        "event_minus_null_z": excess,
        "p_null_abs_excess_ge_real_abs_excess": p_ge,
        "event_type_gate": gate,
    }


def classify_signed(row_low: dict[str, object], row_high: dict[str, object]) -> dict[str, object]:
    l = float(row_low.get("event_minus_null_z", math.nan))
    h = float(row_high.get("event_minus_null_z", math.nan))
    l_gate = bool_from_csv(row_low.get("event_type_gate", False))
    h_gate = bool_from_csv(row_high.get("event_type_gate", False))
    if np.isfinite(l) and np.isfinite(h):
        separation = l - h
        opposite = bool(l * h < 0)
        balance = min(abs(l), abs(h)) / max(abs(l), abs(h)) if max(abs(l), abs(h)) > 1e-12 else math.nan
    else:
        separation = math.nan
        opposite = False
        balance = math.nan

    if l_gate and h_gate and opposite and np.isfinite(balance) and balance >= 0.50:
        cls = "mirror_symmetric_opposite_sign"
        interp = "Both transition directions pass and have balanced opposite signs."
    elif l_gate and h_gate and opposite:
        cls = "opposite_sign_but_imbalanced"
        interp = "Both transition directions pass with opposite signs, but one side is much larger."
    elif l_gate and h_gate:
        cls = "same_direction_both_event_types"
        interp = "Both transition directions pass but shift in the same sign."
    elif l_gate:
        cls = "low_to_high_dominant"
        interp = "Only low-to-high passes the event-type gate."
    elif h_gate:
        cls = "high_to_low_dominant"
        interp = "Only high-to-low passes the event-type gate."
    else:
        cls = "no_signed_gate"
        interp = "Neither transition direction passes the signed event-type gate."

    return {
        "ob": int(row_low["ob"]),
        "variable": str(row_low["variable"]),
        "phase": str(row_low["phase"]),
        "low_to_high_excess_z": l,
        "high_to_low_excess_z": h,
        "signed_separation_z": separation,
        "mirror_opposite_sign": opposite,
        "mirror_balance": balance,
        "low_to_high_gate": l_gate,
        "high_to_low_gate": h_gate,
        "signed_class": cls,
        "interpretation": interp,
    }


def run_ob(
    ob: int,
    events_all: pd.DataFrame,
    variables: list[str],
    phases: list[str],
    rel_grid: np.ndarray,
    n_replicates: int,
    prepost_sec: float,
    exclusion_sec: float,
    gap_gate: float,
    p_gate: float,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    ob_dir = OUT / "per_ob" / f"Ob{ob}"
    event_type_path = ob_dir / "signed_event_type_phase_rows.csv"
    decomp_path = ob_dir / "signed_decomposition_rows.csv"
    if event_type_path.exists() and decomp_path.exists():
        return (
            list(csv.DictReader(event_type_path.open(newline="", encoding="utf-8"))),
            list(csv.DictReader(decomp_path.open(newline="", encoding="utf-8"))),
        )

    ob_dir.mkdir(parents=True, exist_ok=True)
    frame = read_frame(ob, variables)
    dataset = str(frame["dataset"].iloc[0])
    events_ob = events_all[(events_all["ob"] == ob) & (events_all["dataset"].eq(dataset))].copy().reset_index(drop=True)
    if events_ob.empty:
        raise RuntimeError(f"No events for Ob{ob}")

    print(f"[4086] Ob{ob}: signed event-type decomposition", flush=True)
    t = frame["t"].to_numpy(dtype="float64")
    real_rows: dict[tuple[str, str, str], dict[str, object]] = {}
    null_values: dict[tuple[str, str, str], list[float]] = {
        (var, phase, event_type): [] for var in variables for phase in phases for event_type in EVENT_TYPES
    }
    for var in variables:
        for phase in phases:
            for event_type in EVENT_TYPES:
                n_events, real = event_phase_median(frame, events_ob, var, phase, event_type, rel_grid)
                real_rows[(var, phase, event_type)] = {
                    "n_events": n_events,
                    "real": real,
                }

    rng = np.random.default_rng(RNG_SEED + ob)
    for rep in range(n_replicates):
        if rep == 0 or rep + 1 == n_replicates or (rep + 1) % 20 == 0:
            print(f"[4086] Ob{ob}: non-event signed replicate {rep + 1}/{n_replicates}", flush=True)
        sampled = sample_non_event_times(events_ob, t, rng, prepost_sec, exclusion_sec)
        for var in variables:
            for phase in phases:
                for event_type in EVENT_TYPES:
                    _, val = event_phase_median(frame, sampled, var, phase, event_type, rel_grid)
                    null_values[(var, phase, event_type)].append(val)

    event_type_rows: list[dict[str, object]] = []
    for var in variables:
        for phase in phases:
            for event_type in EVENT_TYPES:
                real = real_rows[(var, phase, event_type)]
                event_type_rows.append(
                    event_type_row(
                        ob,
                        var,
                        phase,
                        event_type,
                        int(real["n_events"]),
                        float(real["real"]),
                        null_values[(var, phase, event_type)],
                        gap_gate,
                        p_gate,
                    )
                )

    event_type_by_key = {
        (row["variable"], row["phase"], row["event_type"]): row for row in event_type_rows
    }
    decomp_rows: list[dict[str, object]] = []
    for var in variables:
        for phase in phases:
            decomp_rows.append(
                classify_signed(
                    event_type_by_key[(var, phase, "low_to_high")],
                    event_type_by_key[(var, phase, "high_to_low")],
                )
            )

    write_csv(event_type_path, event_type_rows, EVENT_TYPE_COLUMNS)
    write_csv(decomp_path, decomp_rows, DECOMP_COLUMNS)
    write_json(ob_dir / "signed_event_type_phase_rows.json", event_type_rows)
    write_json(ob_dir / "signed_decomposition_rows.json", decomp_rows)
    return event_type_rows, decomp_rows


def classify_ob(decomp_rows: list[dict[str, object]], ob: int, target_variable: str, target_phase: str) -> dict[str, object]:
    d = pd.DataFrame(decomp_rows)
    row = d[(d["ob"].astype(int) == ob) & d["variable"].eq(target_variable) & d["phase"].eq(target_phase)]
    if row.empty:
        raise RuntimeError(f"Missing target row for Ob{ob} {target_variable} {target_phase}")
    r = row.iloc[0].to_dict()
    return {
        "ob": ob,
        "target_variable": target_variable,
        "target_phase": target_phase,
        "low_to_high_excess_z": float(r["low_to_high_excess_z"]),
        "high_to_low_excess_z": float(r["high_to_low_excess_z"]),
        "signed_separation_z": float(r["signed_separation_z"]),
        "mirror_balance": float(r["mirror_balance"]),
        "low_to_high_gate": bool_from_csv(r["low_to_high_gate"]),
        "high_to_low_gate": bool_from_csv(r["high_to_low_gate"]),
        "signed_class": str(r["signed_class"]),
        "interpretation": str(r["interpretation"]),
    }


def summarize_decomposition(decomp_rows: list[dict[str, object]], n_ob: int) -> list[dict[str, object]]:
    d = pd.DataFrame(decomp_rows)
    if d.empty:
        return []
    for col in ["low_to_high_excess_z", "high_to_low_excess_z", "signed_separation_z"]:
        d[col] = pd.to_numeric(d[col], errors="coerce")
    majority = int(math.floor(n_ob / 2) + 1)
    rows: list[dict[str, object]] = []
    for (var, phase), g in d.groupby(["variable", "phase"], sort=True):
        counts = g["signed_class"].value_counts().to_dict()
        class_counts = {
            "mirror_symmetric_count": int(counts.get("mirror_symmetric_opposite_sign", 0)),
            "opposite_sign_imbalanced_count": int(counts.get("opposite_sign_but_imbalanced", 0)),
            "low_to_high_dominant_count": int(counts.get("low_to_high_dominant", 0)),
            "high_to_low_dominant_count": int(counts.get("high_to_low_dominant", 0)),
            "same_direction_count": int(counts.get("same_direction_both_event_types", 0)),
            "no_signed_gate_count": int(counts.get("no_signed_gate", 0)),
        }
        best_class = max(class_counts.items(), key=lambda kv: kv[1])[0].replace("_count", "")
        if class_counts.get(f"{best_class}_count", 0) >= majority:
            majority_class = best_class
        else:
            majority_class = "no_majority_signed_class"
        if majority_class == "mirror_symmetric":
            interp = "majority mirror-symmetric signed response"
        elif majority_class == "opposite_sign_imbalanced":
            interp = "majority opposite-sign but imbalanced response"
        elif majority_class in {"low_to_high_dominant", "high_to_low_dominant"}:
            interp = f"majority {majority_class.replace('_', '-')} response"
        elif majority_class == "no_signed_gate":
            interp = "majority no signed event-type gate"
        else:
            interp = "signed response is heterogeneous across observations"
        rows.append(
            {
                "variable": var,
                "phase": phase,
                "n_ob_tested": n_ob,
                **class_counts,
                "median_low_to_high_excess_z": finite_median(g["low_to_high_excess_z"]),
                "median_high_to_low_excess_z": finite_median(g["high_to_low_excess_z"]),
                "median_signed_separation_z": finite_median(g["signed_separation_z"]),
                "majority_signed_class": majority_class,
                "interpretation": interp,
            }
        )
    phase_order = {name: i for i, (name, _, _) in enumerate(PHASE_BINS)}
    return sorted(rows, key=lambda r: (str(r["variable"]), phase_order.get(str(r["phase"]), 99)))


def decide(ob_rows: list[dict[str, object]], summary_rows: list[dict[str, object]], target_variable: str, target_phase: str) -> dict[str, object]:
    n_ob = len(ob_rows)
    majority = int(math.floor(n_ob / 2) + 1)
    target = next(
        row for row in summary_rows if row["variable"] == target_variable and row["phase"] == target_phase
    )
    cls = str(target["majority_signed_class"])
    if n_ob < 5:
        result = "pilot_signed_direction_screen_only"
        next_node = "expand_4086_to_4084_robust_survivor_observations"
        interpretation = "Fewer than five observations were tested, so this run validates the signed workflow but is not replicated evidence."
    elif cls == "mirror_symmetric":
        result = "support_mirror_symmetric_signed_t1_near_pre_profile"
        next_node = "4085b_phase_space_projection_or_4087_failure_boundary_sensitivity"
        interpretation = "The near-pre diffuse T1 timing profile is mirrored between low-to-high and high-to-low transitions."
    elif cls == "opposite_sign_imbalanced":
        result = "support_opposite_sign_but_imbalanced_t1_near_pre_profile"
        next_node = "4085b_phase_space_projection_or_4087_failure_boundary_sensitivity"
        interpretation = "The near-pre diffuse T1 timing profile has opposite signs between transition directions, but the response is imbalanced."
    elif cls in {"low_to_high_dominant", "high_to_low_dominant"}:
        result = "support_one_direction_dominant_signed_t1_near_pre_profile"
        next_node = "4085b_phase_space_projection_or_4087_failure_boundary_sensitivity"
        interpretation = f"The near-pre diffuse T1 timing profile is dominated by {cls.replace('_', '-')} transitions."
    elif cls == "no_signed_gate":
        result = "boundary_no_event_type_specific_signed_gate_for_t1_near_pre"
        next_node = "4085b_phase_space_projection_as_diagnostic_then_4088_synthesis"
        interpretation = "The 4085 near-pre diffuse profile does not decompose into stable event-type-specific gates."
    else:
        result = "boundary_signed_direction_heterogeneous_across_observations"
        next_node = "4085b_phase_space_projection_as_diagnostic_then_4087_failure_boundary_sensitivity"
        interpretation = "The near-pre diffuse T1 timing profile has signed event-type heterogeneity rather than a stable mirror or one-direction rule."

    return {
        "node": NODE,
        "date": DATE,
        "result": result,
        "target_variable": target_variable,
        "target_phase": target_phase,
        "n_observations": n_ob,
        "majority_gate_count": majority,
        "target_summary": target,
        "target_ob_class_counts": pd.DataFrame(ob_rows)["signed_class"].value_counts().to_dict() if ob_rows else {},
        "interpretation": interpretation,
        "next": [next_node],
        "artifacts": [
            "Output/4086/signed_event_type_phase_rows.csv",
            "Output/4086/signed_decomposition_rows.csv",
            "Output/4086/ob_signed_classification.csv",
            "Output/4086/variable_phase_signed_summary.csv",
            "Output/4086/figures/4086_target_signed_excess.png",
            "Output/4086/figures/4086_signed_class_counts.png",
        ],
    }


def make_figures(event_rows: pd.DataFrame, ob_rows: pd.DataFrame, summary_rows: pd.DataFrame, target_variable: str, target_phase: str) -> None:
    fig_dir = OUT / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    if not ob_rows.empty:
        d = ob_rows.sort_values("ob").copy()
        x = np.arange(len(d))
        fig, ax = plt.subplots(figsize=(11, 5), constrained_layout=True)
        ax.bar(x - 0.18, d["low_to_high_excess_z"], width=0.36, color="#2f6f9f", label="low_to_high")
        ax.bar(x + 0.18, d["high_to_low_excess_z"], width=0.36, color="#b45f5f", label="high_to_low")
        ax.axhline(0, color="#333333", linewidth=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels([f"Ob{int(v)}" for v in d["ob"]], rotation=45, ha="right")
        ax.set_ylabel("event minus non-event phase median (z)")
        ax.set_title(f"4086 signed event-type excess: {target_variable} {target_phase}")
        ax.legend(frameon=False)
        ax.grid(axis="y", color="#dddddd", linewidth=0.7)
        fig.savefig(fig_dir / "4086_target_signed_excess.png", dpi=180)
        plt.close(fig)

        counts = d["signed_class"].value_counts()
        fig, ax = plt.subplots(figsize=(8, 4.8), constrained_layout=True)
        ax.bar(counts.index.astype(str), counts.values, color="#5d7f31")
        ax.set_ylabel("observation count")
        ax.set_title("4086 target signed class counts")
        ax.tick_params(axis="x", rotation=35)
        ax.grid(axis="y", color="#dddddd", linewidth=0.7)
        fig.savefig(fig_dir / "4086_signed_class_counts.png", dpi=180)
        plt.close(fig)

    if not summary_rows.empty:
        d = summary_rows[summary_rows["variable"].isin([target_variable, "shell_edge_minus_core"])].copy()
        labels = [f"{r.variable}\n{r.phase}" for r in d.itertuples(index=False)]
        x = np.arange(len(d))
        fig, ax = plt.subplots(figsize=(11, 5.2), constrained_layout=True)
        ax.bar(x - 0.2, d["mirror_symmetric_count"], width=0.2, label="mirror", color="#2f6f9f")
        ax.bar(x, d["low_to_high_dominant_count"], width=0.2, label="L->H", color="#5d7f31")
        ax.bar(x + 0.2, d["high_to_low_dominant_count"], width=0.2, label="H->L", color="#b45f5f")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=55, ha="right")
        ax.set_ylabel("observation count")
        ax.set_title("4086 signed decomposition by variable and phase")
        ax.legend(frameon=False)
        ax.grid(axis="y", color="#dddddd", linewidth=0.7)
        fig.savefig(fig_dir / "4086_variable_phase_signed_counts.png", dpi=180)
        plt.close(fig)


def write_config(args: argparse.Namespace, obs: list[int], variables: list[str], phases: list[str]) -> None:
    text = dedent(
        f"""\
        node: {NODE}
        date: {DATE}
        node_type: mechanism
        input_nodes:
          - 4085_event_phase_profile_of_t1_signal
          - 4084_spatial_taxonomy_of_t1_local_nonaffine_signal
        observations: {','.join(str(x) for x in obs)}
        variables: {','.join(variables)}
        phases: {','.join(phases)}
        target_variable: {args.target_variable}
        target_phase: {args.target_phase}
        relative_time_step_sec: {args.rel_step}
        n_non_event_replicates: {args.n_replicates}
        event_type_gap_gate_z: {args.gap_gate}
        event_type_p_gate: {args.p_gate}
        """
    )
    (OUT / "config.yaml").write_text(text, encoding="utf-8")


def write_summary(decision: dict[str, object], ob_rows: list[dict[str, object]], summary_rows: list[dict[str, object]], args: argparse.Namespace) -> None:
    target_summary_rows = [
        r
        for r in summary_rows
        if r["variable"] in {args.target_variable, "shell_edge_minus_core"} and r["phase"] in {"near_pre", "near_post"}
    ]
    ob_display = [
        "ob",
        "low_to_high_excess_z",
        "high_to_low_excess_z",
        "signed_separation_z",
        "mirror_balance",
        "low_to_high_gate",
        "high_to_low_gate",
        "signed_class",
    ]
    summary_display = [
        "variable",
        "phase",
        "mirror_symmetric_count",
        "low_to_high_dominant_count",
        "high_to_low_dominant_count",
        "opposite_sign_imbalanced_count",
        "same_direction_count",
        "no_signed_gate_count",
        "median_low_to_high_excess_z",
        "median_high_to_low_excess_z",
        "majority_signed_class",
    ]
    text = dedent(
        f"""\
        # Node 4086 Summary

        ## Question

        Is the 4085 near-pre diffuse T1 timing profile mirrored between
        low-to-high and high-to-low transitions, or is it dominated by one
        transition direction?

        ## Inputs

        - `Output/4084/per_ob/Ob*/local_spatial_metric_frame.csv`
        - `Output/4085/decision.json`
        - `Output/3045/tables/transition_events.csv`

        ## Method

        For each observation, variable, phase, and transition type, 4086 compares
        real phase medians against matched non-event windows with the same event
        type labels.

        ```text
        target variable = {args.target_variable}
        target phase = {args.target_phase}
        non-event replicates = {args.n_replicates}
        event-type gate = abs(real-null) >= {args.gap_gate}, p <= {args.p_gate}
        ```

        Signed classes:

        - `mirror_symmetric_opposite_sign`: both event types pass with balanced
          opposite signs;
        - `low_to_high_dominant`;
        - `high_to_low_dominant`;
        - `same_direction_both_event_types`;
        - `no_signed_gate`.

        ## Decision

        `{decision["result"]}`

        ## Main Reading

        {decision["interpretation"]}

        ```text
        observations tested = {decision["n_observations"]}
        majority gate count = {decision["majority_gate_count"]}
        target class counts = {json.dumps(decision["target_ob_class_counts"], ensure_ascii=False)}
        ```

        ## Target Observation Classification

        {md_table(ob_rows, ob_display)}

        ## Variable/Phase Signed Summary

        {md_table(target_summary_rows, summary_display)}

        ## Boundary

        This node does not claim a deterministic trigger. It only asks whether
        the 4085 near-pre timing profile has a stable signed decomposition.

        ## Next

        `{decision["next"][0]}`

        ## Artifacts

        - `Output/4086/signed_event_type_phase_rows.csv`
        - `Output/4086/signed_decomposition_rows.csv`
        - `Output/4086/ob_signed_classification.csv`
        - `Output/4086/variable_phase_signed_summary.csv`
        - `Output/4086/figures/4086_target_signed_excess.png`
        - `Output/4086/figures/4086_signed_class_counts.png`
        """
    ).lstrip()
    summary = "\n".join(line[8:] if line.startswith("        ") else line for line in text.splitlines()) + "\n"
    (OUT / "4086_summary.md").write_text(summary, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--obs", default="4084")
    parser.add_argument("--variables", default=",".join(DEFAULT_VARIABLES))
    parser.add_argument("--phases", default="near_pre,near_post")
    parser.add_argument("--target-variable", default="all_tangential")
    parser.add_argument("--target-phase", default="near_pre")
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
    phases = parse_variables(args.phases)
    obs = read_obs(args.obs)
    rel_grid = np.round(np.arange(args.rel_min, args.rel_max + args.rel_step / 2, args.rel_step), 6)
    events = r4002a.read_events()
    write_config(args, obs, variables, phases)

    if args.force:
        for ob in obs:
            ob_dir = OUT / "per_ob" / f"Ob{ob}"
            for name in ["signed_event_type_phase_rows.csv", "signed_decomposition_rows.csv"]:
                path = ob_dir / name
                if path.exists():
                    path.unlink()

    all_event_rows: list[dict[str, object]] = []
    all_decomp_rows: list[dict[str, object]] = []
    for ob in obs:
        event_rows, decomp_rows = run_ob(
            ob,
            events,
            variables,
            phases,
            rel_grid,
            args.n_replicates,
            args.prepost_sec,
            args.exclusion_sec,
            args.gap_gate,
            args.p_gate,
        )
        all_event_rows.extend(event_rows)
        all_decomp_rows.extend(decomp_rows)

    ob_rows = [classify_ob(all_decomp_rows, ob, args.target_variable, args.target_phase) for ob in obs]
    summary_rows = summarize_decomposition(all_decomp_rows, len(obs))
    decision = decide(ob_rows, summary_rows, args.target_variable, args.target_phase)

    write_csv(OUT / "signed_event_type_phase_rows.csv", all_event_rows, EVENT_TYPE_COLUMNS)
    write_csv(OUT / "tables" / "signed_event_type_phase_rows.csv", all_event_rows, EVENT_TYPE_COLUMNS)
    write_json(OUT / "signed_event_type_phase_rows.json", all_event_rows)
    write_csv(OUT / "signed_decomposition_rows.csv", all_decomp_rows, DECOMP_COLUMNS)
    write_csv(OUT / "tables" / "signed_decomposition_rows.csv", all_decomp_rows, DECOMP_COLUMNS)
    write_json(OUT / "signed_decomposition_rows.json", all_decomp_rows)
    write_csv(OUT / "ob_signed_classification.csv", ob_rows, OB_COLUMNS)
    write_csv(OUT / "tables" / "ob_signed_classification.csv", ob_rows, OB_COLUMNS)
    write_json(OUT / "ob_signed_classification.json", ob_rows)
    write_csv(OUT / "variable_phase_signed_summary.csv", summary_rows, SUMMARY_COLUMNS)
    write_csv(OUT / "tables" / "variable_phase_signed_summary.csv", summary_rows, SUMMARY_COLUMNS)
    write_json(OUT / "variable_phase_signed_summary.json", summary_rows)
    write_json(OUT / "decision.json", decision)
    make_figures(pd.DataFrame(all_event_rows), pd.DataFrame(ob_rows), pd.DataFrame(summary_rows), args.target_variable, args.target_phase)
    write_summary(decision, ob_rows, summary_rows, args)
    print(f"Wrote 4086 outputs to {OUT.relative_to(ROOT)}")
    print(json.dumps(decision, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
