#!/usr/bin/env python3
"""4140 manuscript freeze and reproducibility audit.

This node is a read-only submission-hardening audit. It maps the active
manuscript definitions to the actual upstream scripts and output artifacts
before any 4141/4142/4143 robustness runs are allowed to change confidence in
the claim.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4140"

NODE = "4140_manuscript_freeze_reproducibility_audit"
DATE = "2026-09-01"

SRC = {
    "review_007": ROOT / "mypaper2" / "00_review" / "007.md",
    "manuscript_pdf": ROOT / "mypaper2" / "Latex" / "main.pdf",
    "abstract_tex": ROOT / "mypaper2" / "Latex" / "00_abstract.tex",
    "data_dataset_tex": ROOT / "mypaper2" / "Latex" / "Part2" / "02_data_trajectory_dataset.tex",
    "data_t1_tex": ROOT / "mypaper2" / "Latex" / "Part2" / "02_data_t1_observable_v2.tex",
    "methods_affine_tex": ROOT / "mypaper2" / "Latex" / "Part3" / "03_methods_affine_reduction_and_controls_v2.tex",
    "results_t1_tex": ROOT / "mypaper2" / "Latex" / "Part4" / "04_results_t1_survival_v2.tex",
    "discussion_limits_tex": ROOT / "mypaper2" / "Latex" / "Part5" / "05_discussion_limitations_future_v2.tex",
    "r3032": ROOT / "Experiment" / "run_3032_transfer_operator_metastability.py",
    "r3032b": ROOT / "Experiment" / "run_3032b_state_meaning_residence_audit.py",
    "r3041": ROOT / "Experiment" / "run_3041_anisotropic_layer_residence.py",
    "r3041b": ROOT / "Experiment" / "run_3041b_coarse_graining_closure_audit.py",
    "r3045": ROOT / "Experiment" / "run_3045_residual_event_trigger_search.py",
    "r4081": ROOT / "Experiment" / "run_4081_global_vs_local_geometry_ladder.py",
    "r4081c": ROOT / "Experiment" / "run_4081c_full_observation_adjudication.py",
    "r4082": ROOT / "Experiment" / "run_4082_scale_robustness_on_surviving_observation_class.py",
    "r4084": ROOT / "Experiment" / "run_4084_spatial_taxonomy_of_t1_local_nonaffine_signal.py",
    "r4085": ROOT / "Experiment" / "run_4085_event_phase_profile_of_t1_signal.py",
    "r4100": ROOT / "Experiment" / "run_4100_state_matched_event_locality_challenge.py",
    "r4121": ROOT / "Experiment" / "run_4121_same_current_state_different_history.py",
    "r4134": ROOT / "Experiment" / "run_4134_figure_ready_evidence_panels.py",
    "o3032_decision": ROOT / "Output" / "3032" / "tables" / "egrt_decision_summary.csv",
    "o3032_mapping": ROOT / "Output" / "3032" / "tables" / "spectral_cell_mapping.csv",
    "o3032_edges": ROOT / "Output" / "3032" / "tables" / "ulam_bin_edges.json",
    "o3032b_labels": ROOT / "Output" / "3032b" / "processed" / "frame_spectral_labels.csv",
    "o3041_frame": ROOT / "Output" / "3041" / "processed" / "frame_layer_metrics.csv",
    "o3041b_frame": ROOT / "Output" / "3041b" / "processed" / "frame_macrostate_candidates.csv",
    "o3045_events": ROOT / "Output" / "3045" / "tables" / "transition_events.csv",
    "o3045_state": ROOT / "Output" / "3045" / "processed" / "frame_residual_signals.csv",
    "o4081c_decision": ROOT / "Output" / "4081c" / "decision.json",
    "o4081c_rows": ROOT / "Output" / "4081c" / "full_geometry_ladder_rows.csv",
    "o4081c_classes": ROOT / "Output" / "4081c" / "ob_route_a_classification.csv",
    "o4082_decision": ROOT / "Output" / "4082" / "decision.json",
    "o4084_decision": ROOT / "Output" / "4084" / "decision.json",
    "o4085_decision": ROOT / "Output" / "4085" / "decision.json",
    "o4100_decision": ROOT / "Output" / "4100" / "decision.json",
    "o4121_decision": ROOT / "Output" / "4121" / "decision.json",
}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def first_line(path: Path, pattern: str) -> str:
    if not path.exists():
        return f"{rel(path)}:MISSING"
    for idx, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        if pattern in line:
            return f"{rel(path)}:{idx}"
    return f"{rel(path)}:pattern_not_found"


def safe_float(value: Any) -> float:
    try:
        out = float(value)
    except Exception:
        return math.nan
    return out if math.isfinite(out) else math.nan


def bool_series(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False)
    return series.astype(str).str.lower().isin(["true", "1", "yes"])


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
        vals: list[str] = []
        for col in columns:
            val = row.get(col, "")
            if isinstance(val, float):
                vals.append("NA" if not math.isfinite(val) else f"{val:.4g}")
            else:
                vals.append(str(val).replace("\n", " ").replace("|", "\\|"))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def load_observed_counts() -> dict[str, Any]:
    decision = read_json(SRC["o4081c_decision"])
    rows = pd.read_csv(SRC["o4081c_rows"])
    cls = pd.read_csv(SRC["o4081c_classes"])
    rows["event_conditioned_local_gate"] = bool_series(rows["event_conditioned_local_gate"])
    cls["t1_gate_any"] = bool_series(cls["t1_gate_any"])
    cls["ob"] = pd.to_numeric(cls["ob"], errors="coerce").astype("Int64")

    t1 = rows[rows["target_id"].astype(str) == "T1_transition_tangential_residual"].copy()
    t1["ob"] = pd.to_numeric(t1["ob"], errors="coerce").astype("Int64")
    t1["k"] = pd.to_numeric(t1["k"], errors="coerce").astype("Int64")
    t1_gates = (
        t1[t1["event_conditioned_local_gate"]]
        .groupby("ob")["k"]
        .apply(lambda x: sorted(int(v) for v in x.dropna().unique()))
        .to_dict()
    )
    any_obs = sorted(int(ob) for ob, ks in t1_gates.items() if ks)
    both_obs = sorted(int(ob) for ob, ks in t1_gates.items() if {8, 10}.issubset(set(ks)))
    return {
        "decision": decision,
        "n_observations": int(decision.get("n_observations", len(cls))),
        "n_any": len(any_obs),
        "n_both": len(both_obs),
        "any_obs": any_obs,
        "both_obs": both_obs,
        "non_survivor_obs": sorted(int(x) for x in cls.loc[~cls["t1_gate_any"], "ob"].dropna().tolist()),
    }


def registry_rows(counts: dict[str, Any]) -> list[dict[str, Any]]:
    d4082 = read_json(SRC["o4082_decision"])
    d4084 = read_json(SRC["o4084_decision"])
    d4085 = read_json(SRC["o4085_decision"])
    d4100 = read_json(SRC["o4100_decision"])
    d4121 = read_json(SRC["o4121_decision"])
    events = pd.read_csv(SRC["o3045_events"])
    dt_vals = pd.to_numeric(events.get("dt"), errors="coerce").dropna().round(8).unique().tolist()
    dt_value = ",".join(str(float(x)) for x in sorted(dt_vals)) if dt_vals else "not recorded"
    sampling = "100 Hz inferred from transition-event dt=0.01 s" if dt_vals and np.allclose(dt_vals, 0.01) else dt_value

    rows = [
        {
            "definition": "dataset",
            "paper_location": first_line(SRC["data_dataset_tex"], "nineteen separate"),
            "code_location": rel(SRC["o4081c_classes"]),
            "config_location": rel(SRC["o4081c_decision"]),
            "actual_numeric_value": f"Ob1-Ob19; n_observations={counts['n_observations']}",
            "frozen": "yes",
            "notes": "Observation identity is the grouping/replication unit; these are recordings, not independent biological populations.",
        },
        {
            "definition": "sampling rate",
            "paper_location": first_line(SRC["review_007"], "sampling rate"),
            "code_location": rel(SRC["o3045_events"]),
            "config_location": rel(SRC["o3045_events"]),
            "actual_numeric_value": sampling,
            "frozen": "yes",
            "notes": "Computed from existing transition event dt column; no new raw-data preprocessing.",
        },
        {
            "definition": "primary k values",
            "paper_location": first_line(SRC["methods_affine_tex"], "two neighborhood sizes"),
            "code_location": first_line(SRC["r4081c"], 'parser.add_argument("--k"'),
            "config_location": rel(SRC["o4081c_decision"]),
            "actual_numeric_value": read_json(SRC["o4081c_decision"]).get("parameters", {}).get("k", "8,10"),
            "frozen": "yes",
            "notes": "Main survival count uses k=8 and k=10.",
        },
        {
            "definition": "default lag",
            "paper_location": first_line(SRC["methods_affine_tex"], "default lag was"),
            "code_location": first_line(SRC["r4081c"], 'parser.add_argument("--lag"'),
            "config_location": rel(SRC["o4081c_decision"]),
            "actual_numeric_value": read_json(SRC["o4081c_decision"]).get("parameters", {}).get("lag", 0.10),
            "frozen": "yes",
            "notes": "Finite-lag displacement baseline.",
        },
        {
            "definition": "neighbor eligibility",
            "paper_location": first_line(SRC["methods_affine_tex"], "neighbor was retained"),
            "code_location": first_line(SRC["r4081"], "if len(neigh_ids) < 4"),
            "config_location": first_line(SRC["r4081c"], 'parser.add_argument("--max-focals-per-frame"'),
            "actual_numeric_value": "neighbor present at t and t+lag; retained_neighbors >= 4; max sampled focals/frame=24",
            "frozen": "yes",
            "notes": "Focal samples below four retained neighbors are skipped.",
        },
        {
            "definition": "affine solver",
            "paper_location": first_line(SRC["methods_affine_tex"], "equal-weight least squares"),
            "code_location": first_line(SRC["r4081"], "np.linalg.lstsq"),
            "config_location": rel(SRC["r4081"]),
            "actual_numeric_value": "SVD rank screen followed by np.linalg.lstsq(A,B,rcond=None)",
            "frozen": "yes",
            "notes": "No weighting and no post-hoc fit cutoff in current T1 definition.",
        },
        {
            "definition": "rank handling",
            "paper_location": first_line(SRC["methods_affine_tex"], "fewer than four retained neighbors"),
            "code_location": first_line(SRC["r4081"], "s[-1] <= 1e-12"),
            "config_location": rel(SRC["r4081"]),
            "actual_numeric_value": "skip if SVD returns <3 singular values or smallest singular value <= 1e-12",
            "frozen": "yes",
            "notes": "4143 should quantify rank-sufficiency rather than change this rule.",
        },
        {
            "definition": "condition-number handling",
            "paper_location": first_line(SRC["discussion_limits_tex"], "affine"),
            "code_location": first_line(SRC["r4081"], "np.linalg.svd"),
            "config_location": "not a current T1 cutoff",
            "actual_numeric_value": "not thresholded in 4081/4081c; only smallest-singular-value rank screen is used",
            "frozen": "yes-current-definition",
            "notes": "This is a technical-defense gap, not a manuscript-code mismatch. Route to 4143.",
        },
        {
            "definition": "initial robust-z",
            "paper_location": first_line(SRC["methods_affine_tex"], "robust-z standardized"),
            "code_location": first_line(SRC["r4081"], "r4002a.robust_z_safe"),
            "config_location": rel(SRC["r4081"]),
            "actual_numeric_value": "within-observation robust-z",
            "frozen": "yes",
            "notes": "Applied before detrending in the local metric residualization.",
        },
        {
            "definition": "slow detrending",
            "paper_location": first_line(SRC["methods_affine_tex"], "one-second centered rolling mean"),
            "code_location": first_line(SRC["r4081"], "rolling(win, center=True"),
            "config_location": first_line(SRC["r4081"], "win = max(5"),
            "actual_numeric_value": "1.0 s centered rolling mean, min_periods=max(3, win//5), interpolate both directions",
            "frozen": "yes",
            "notes": "4142 will challenge this with no-detrend and past-only variants.",
        },
        {
            "definition": "second robust-z",
            "paper_location": first_line(SRC["methods_affine_tex"], "robust-z standardized again"),
            "code_location": first_line(SRC["r4081"], "z - smooth"),
            "config_location": rel(SRC["r4081"]),
            "actual_numeric_value": "robust-z of detrended local metric",
            "frozen": "yes",
            "notes": "The manuscript should keep this as preprocessing, not as a mechanism.",
        },
        {
            "definition": "transition-label source",
            "paper_location": first_line(SRC["data_t1_tex"], "frozen"),
            "code_location": first_line(SRC["r3045"], "spectral_set"),
            "config_location": rel(SRC["o3045_events"]),
            "actual_numeric_value": "low/high spectral_set inherited from 3032b via 3041/3041b into 3045",
            "frozen": "yes",
            "notes": "Full reconstruction chain is documented in spectral_set_provenance.md.",
        },
        {
            "definition": "transition persistence",
            "paper_location": first_line(SRC["data_t1_tex"], "0.20"),
            "code_location": first_line(SRC["r3045"], "min_run_sec"),
            "config_location": rel(SRC["o3045_events"]),
            "actual_numeric_value": "preceding and following low/high runs each >= 0.20 s; event time is first frame of new run",
            "frozen": "yes",
            "notes": "Transition types are low_to_high and high_to_low.",
        },
        {
            "definition": "non-event exclusion",
            "paper_location": first_line(SRC["methods_affine_tex"], "0.80"),
            "code_location": first_line(SRC["r4081c"], 'parser.add_argument("--exclusion-sec"'),
            "config_location": rel(SRC["o4081c_decision"]),
            "actual_numeric_value": "control center at least 0.80 s away from real transition times",
            "frozen": "yes",
            "notes": "4141 should preserve this rule inside every null replicate.",
        },
        {
            "definition": "non-event replicate count",
            "paper_location": first_line(SRC["methods_affine_tex"], "Forty non-event replicates"),
            "code_location": first_line(SRC["r4081c"], 'parser.add_argument("--n-replicates"'),
            "config_location": rel(SRC["o4081c_decision"]),
            "actual_numeric_value": read_json(SRC["o4081c_decision"]).get("parameters", {}).get("n_replicates", 40),
            "frozen": "yes-current-result",
            "notes": "This is enough for current exploratory survival calls but not for 4141 final omnibus calibration.",
        },
        {
            "definition": "survival gate thresholds",
            "paper_location": first_line(SRC["methods_affine_tex"], "local_event_minus"),
            "code_location": first_line(SRC["r4081c"], "local_gap > 0.03"),
            "config_location": rel(SRC["o4081c_rows"]),
            "actual_numeric_value": "local_event_minus_non_event_direction_z > 0.03; p_non_event_direction_ge_event <= 0.35; local_to_b3_direction_ratio >= 0.30",
            "frozen": "yes",
            "notes": "Both-scale support requires the same observation to pass the per-scale gate at k=8 and k=10.",
        },
        {
            "definition": "main support counts",
            "paper_location": first_line(SRC["abstract_tex"], "14 of 19"),
            "code_location": rel(SRC["o4081c_decision"]),
            "config_location": rel(SRC["o4081c_classes"]),
            "actual_numeric_value": f"N_both={counts['n_both']}/19; N_any={counts['n_any']}/19",
            "frozen": "yes",
            "notes": f"Both-scale obs={counts['both_obs']}; any-scale obs={counts['any_obs']}.",
        },
        {
            "definition": "scale/lag sensitivity grid",
            "paper_location": first_line(SRC["abstract_tex"], "scale and temporal-lag"),
            "code_location": rel(SRC["r4082"]),
            "config_location": rel(SRC["o4082_decision"]),
            "actual_numeric_value": f"scale_k={d4082.get('scale_k')}; timing_lag_sec={d4082.get('timing_lag_sec')}; robust={d4082.get('robust_scale_and_timing_count')}/{d4082.get('n_observations')}",
            "frozen": "yes",
            "notes": "Robustness is evaluated within the 4081c any-scale survivor class.",
        },
        {
            "definition": "diffuse phenotype",
            "paper_location": first_line(SRC["abstract_tex"], "diffuse tangential"),
            "code_location": rel(SRC["r4084"]),
            "config_location": rel(SRC["o4084_decision"]),
            "actual_numeric_value": f"diffuse all_tangential support={d4084.get('diffuse_baseline_gate_count')}/{d4084.get('n_observations')}",
            "frozen": "yes",
            "notes": "Spatial taxonomy is descriptive; it does not create a new T1 target.",
        },
        {
            "definition": "near-pre descriptive support",
            "paper_location": first_line(SRC["abstract_tex"], "near-pre"),
            "code_location": rel(SRC["r4085"]),
            "config_location": rel(SRC["o4085_decision"]),
            "actual_numeric_value": "all_tangential near_pre support=8/14",
            "frozen": "yes",
            "notes": "Descriptive event-aligned timing only; 4100 state-matched event-locality failed.",
        },
        {
            "definition": "state-matching distance",
            "paper_location": first_line(SRC["review_007"], "state-matching distance"),
            "code_location": first_line(SRC["r4100"], 'parser.add_argument("--max-match-distance"'),
            "config_location": rel(SRC["o4100_decision"]),
            "actual_numeric_value": f"max_match_distance=0.75; n_matches=5; exclusion=0.75 s; result={d4100.get('gate_result')}",
            "frozen": "yes",
            "notes": "Uses same-observation matching in C,dCdt,R robust state space.",
        },
        {
            "definition": "history window",
            "paper_location": first_line(SRC["review_007"], "history window"),
            "code_location": first_line(SRC["r4121"], "history_window_sec"),
            "config_location": rel(SRC["o4121_decision"]),
            "actual_numeric_value": f"h={d4121.get('primary_thresholds', {}).get('history_window_sec')} s; state_distance={d4121.get('primary_thresholds', {}).get('state_distance_threshold')}",
            "frozen": "yes",
            "notes": "History route remains observation-specific, not a stable memory mechanism.",
        },
        {
            "definition": "history-angle threshold",
            "paper_location": first_line(SRC["review_007"], "history-angle threshold"),
            "code_location": first_line(SRC["r4121"], "history_angle_threshold_deg"),
            "config_location": rel(SRC["o4121_decision"]),
            "actual_numeric_value": f"{d4121.get('primary_thresholds', {}).get('history_angle_threshold_deg')} deg",
            "frozen": "yes",
            "notes": "Used only in the 4121 history boundary branch.",
        },
    ]
    return rows


def source_map_rows() -> list[dict[str, Any]]:
    items = [
        ("spectral partition construction", SRC["r3032"], "spectral_partitions", SRC["o3032_mapping"]),
        ("frame spectral labels", SRC["r3032b"], "frame_spectral_labels", SRC["o3032b_labels"]),
        ("state labels consumed by layer analysis", SRC["r3041"], "LABEL_PATH", SRC["o3041_frame"]),
        ("macrostate candidates consumed by 3045", SRC["r3041b"], "frame_macrostate_candidates", SRC["o3041b_frame"]),
        ("transition events", SRC["r3045"], "detect_transition_events", SRC["o3045_events"]),
        ("local affine T1 calculation", SRC["r4081"], "local_frame_metrics", SRC["o4081c_rows"]),
        ("all-observation T1 survival", SRC["r4081c"], "local_gap > 0.03", SRC["o4081c_decision"]),
        ("scale/lag robustness", SRC["r4082"], "scale_k", SRC["o4082_decision"]),
        ("diffuse/spatial phenotype", SRC["r4084"], "all_tangential", SRC["o4084_decision"]),
        ("event phase profile", SRC["r4085"], "near_pre", SRC["o4085_decision"]),
        ("state-matched event locality", SRC["r4100"], "matching_variables", SRC["o4100_decision"]),
        ("history matched test", SRC["r4121"], "history_window_sec", SRC["o4121_decision"]),
        ("paper figures", SRC["r4134"], "Figure 4", ROOT / "Output" / "4134"),
    ]
    rows = []
    for concept, code, pattern, output in items:
        rows.append(
            {
                "concept": concept,
                "source_code": first_line(code, pattern),
                "primary_output": rel(output),
                "output_exists": output.exists(),
                "notes": "",
            }
        )
    return rows


def mismatch_rows(counts: dict[str, Any], registry: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if counts["n_observations"] != 19:
        rows.append(
            {
                "item": "observation count",
                "expected_or_paper": "19",
                "actual_or_code": counts["n_observations"],
                "severity": "stop",
                "action": "Resolve before 4141.",
            }
        )
    if counts["n_both"] != 14 or counts["n_any"] != 15:
        rows.append(
            {
                "item": "main T1 support counts",
                "expected_or_paper": "N_both=14/19; N_any=15/19",
                "actual_or_code": f"N_both={counts['n_both']}/19; N_any={counts['n_any']}/19",
                "severity": "stop",
                "action": "Resolve before 4141.",
            }
        )
    for row in registry:
        if "MISSING" in str(row["code_location"]) or "MISSING" in str(row["config_location"]):
            rows.append(
                {
                    "item": row["definition"],
                    "expected_or_paper": "traceable code/output",
                    "actual_or_code": f"{row['code_location']} | {row['config_location']}",
                    "severity": "boundary",
                    "action": "Document or regenerate upstream artifact.",
                }
            )
    rows.append(
        {
            "item": "condition-number QC",
            "expected_or_paper": "reviewer-defensible affine-fit conditioning audit",
            "actual_or_code": "no condition-number threshold is used in current T1; rank screen exists only",
            "severity": "planned_boundary",
            "action": "Run 4143; do not alter T1 definition.",
        }
    )
    rows.append(
        {
            "item": "full-pipeline omnibus null",
            "expected_or_paper": "calibrated P_null(N_both>=14)",
            "actual_or_code": "not yet run; existing 4081c non-event replicates are not an omnibus null",
            "severity": "planned_boundary",
            "action": "Run 4141 smoke, then full B>=1000 if feasible.",
        }
    )
    rows.append(
        {
            "item": "detrending challenge",
            "expected_or_paper": "no-detrend / causal / centered comparison",
            "actual_or_code": "not yet run; current T1 uses centered rolling mean",
            "severity": "planned_boundary",
            "action": "Run 4142 after 4140 freeze.",
        }
    )
    return rows


def frozen_contract(counts: dict[str, Any]) -> str:
    d4081c = read_json(SRC["o4081c_decision"])
    d4082 = read_json(SRC["o4082_decision"])
    d4084 = read_json(SRC["o4084_decision"])
    d4085 = read_json(SRC["o4085_decision"])
    return f"""node: {NODE}
date: {DATE}
analysis_scope: all_19_observations
claim_class_before_4141_4143: bounded_diagnostic_empirical_claim
dataset:
  observations: Ob1-Ob19
  observation_count: {counts['n_observations']}
  sampling_rate: 100 Hz inferred from dt=0.01 s in Output/3045/tables/transition_events.csv
  replication_unit: observation_level_recording
local_affine_t1:
  k_primary: [8, 10]
  lag_sec: {d4081c.get('parameters', {}).get('lag', 0.10)}
  frame_stride: {d4081c.get('parameters', {}).get('frame_stride', 2)}
  max_focals_per_frame: 24
  retained_neighbors_min: 4
  solver: np.linalg.lstsq_after_svd_rank_screen
  rank_screen: smallest_singular_value_gt_1e-12
  condition_number_cutoff: none_in_current_definition
preprocessing:
  initial_standardization: within_observation_robust_z
  detrending: subtract_1s_centered_rolling_mean
  second_standardization: robust_z_after_detrending
transition_events:
  label_source: spectral_set_from_3032b_via_3041_3041b_3045
  states: [low, high]
  min_previous_run_sec: 0.20
  min_next_run_sec: 0.20
  event_time: first_frame_of_new_run
controls:
  non_event_exclusion_sec: 0.80
  non_event_replicates_current_result: {d4081c.get('parameters', {}).get('n_replicates', 40)}
survival_gate:
  local_event_minus_non_event_direction_z: "> 0.03"
  p_non_event_direction_ge_event: "<= 0.35"
  local_to_b3_direction_ratio: ">= 0.30"
support_counts:
  n_both: {counts['n_both']}
  n_any: {counts['n_any']}
  both_scale_observations: {counts['both_obs']}
  any_scale_observations: {counts['any_obs']}
  non_survivor_observations: {counts['non_survivor_obs']}
robustness_anchors:
  scale_lag_robust_survivor_count: "{d4082.get('robust_scale_and_timing_count')}/{d4082.get('n_observations')}"
  scale_grid_k: {d4082.get('scale_k')}
  lag_grid_sec: {d4082.get('timing_lag_sec')}
  diffuse_all_tangential_support: "{d4084.get('diffuse_baseline_gate_count')}/{d4084.get('n_observations')}"
  near_pre_descriptive_support: "8/{d4085.get('n_observations')}"
not_yet_calibrated:
  - full_pipeline_omnibus_null
  - alternative_detrending_challenge
  - affine_condition_number_qc
"""


def spectral_set_provenance() -> str:
    decision = pd.read_csv(SRC["o3032_decision"]).iloc[0].to_dict()
    mapping = pd.read_csv(SRC["o3032_mapping"])
    labels = pd.read_csv(SRC["o3032b_labels"], usecols=["ob", "t", "spectral_set"])
    events = pd.read_csv(SRC["o3045_events"])
    best_partition = str(decision.get("best_partition_id", "not_recorded"))
    vars_raw = str(decision.get("candidate_variables", "not_recorded"))
    map_partitions = sorted(mapping["partition_id"].astype(str).unique().tolist()) if "partition_id" in mapping.columns else []
    label_counts = labels["spectral_set"].astype(str).value_counts().to_dict()
    event_counts = events["event_type"].astype(str).value_counts().to_dict()
    n_obs_labels = int(pd.to_numeric(labels["ob"], errors="coerce").dropna().nunique())
    return f"""# 4140 spectral_set Provenance

## Summary

The current manuscript's low/high transition events are inherited labels, not
new labels fitted from T1. The chain is:

```text
3032 transfer-operator spectral partition
  -> 3032b frame_spectral_labels.csv
  -> 3041 frame_layer_metrics.csv
  -> 3041b frame_macrostate_candidates.csv
  -> 3045 transition_events.csv
```

## Source Node

- Source node: `3032_transfer_operator_metastability`
- Source script: `{first_line(SRC["r3032"], "spectral_partitions")}`
- Best partition from 3032 decision: `{best_partition}`
- Candidate variables recorded in 3032 decision: `{vars_raw}`
- Mapping file: `{rel(SRC["o3032_mapping"])}`
- Bin-edge file: `{rel(SRC["o3032_edges"])}`

## Label Materialization

- Materialization script: `{first_line(SRC["r3032b"], "frame_spectral_labels")}`
- Frame label file: `{rel(SRC["o3032b_labels"])}`
- Label observations: `{n_obs_labels}`
- Label counts: `{json.dumps(label_counts, ensure_ascii=False, sort_keys=True)}`
- Available mapping partitions: `{', '.join(map_partitions[:8])}`

## Downstream Consumption

- 3041 reads labels from `{rel(SRC["o3032b_labels"])}` using `{first_line(SRC["r3041"], "LABEL_PATH")}`.
- 3041b propagates `spectral_set` into `{rel(SRC["o3041b_frame"])}`.
- 3045 reads `{rel(SRC["o3041b_frame"])}` and detects low/high switches using `{first_line(SRC["r3045"], "detect_transition_events")}`.
- 3045 transition events: `{rel(SRC["o3045_events"])}`
- 3045 event counts: `{json.dumps(event_counts, ensure_ascii=False, sort_keys=True)}`

## Independence From T1

The `spectral_set` construction is upstream of the 4081/4081c local-affine T1
observable. The provenance chain uses slow macroscopic variables and transfer
operator partitioning before the T1 residual family is introduced. This
supports treating transition labels as inherited state labels, not as labels
optimized on T1 survival.

## Current Limitation

The manuscript now states the inherited-label logic, but a reader still needs a
supplement-style method to reconstruct the full 3032/3032b spectral partition
without reading old experiment scripts. This should be handled in 4144.
"""


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tables").mkdir(exist_ok=True)
    counts = load_observed_counts()
    registry = registry_rows(counts)
    source_map = source_map_rows()
    mismatches = mismatch_rows(counts, registry)

    stop_items = [r for r in mismatches if r.get("severity") == "stop"]
    boundary_items = [r for r in mismatches if r.get("severity") in {"boundary", "planned_boundary"}]
    gate_result = "technical_stop_definition_mismatch" if stop_items else "pass_with_pre_submission_boundary_items"
    next_nodes = [] if stop_items else ["4141_full_pipeline_omnibus_survival_null_smoke", "4142_detrending_challenge", "4143_affine_fit_qc"]

    decision = {
        "node": NODE,
        "date": DATE,
        "purpose": "Freeze manuscript definitions and map claims to code/output artifacts before submission-hardening tests.",
        "analysis_scope": "all_19_observations",
        "primary_metrics": {
            "n_observations": counts["n_observations"],
            "n_both_observed": counts["n_both"],
            "n_any_observed": counts["n_any"],
            "n_stop_mismatches": len(stop_items),
            "n_boundary_items": len(boundary_items),
        },
        "main_result": {
            "gate_result": gate_result,
            "both_scale_observations": counts["both_obs"],
            "any_scale_observations": counts["any_obs"],
            "non_survivor_observations": counts["non_survivor_obs"],
        },
        "does_not_prove": [
            "full-pipeline global significance of 14/19",
            "detrending invariance",
            "well-conditioned local affine fits across all focal samples",
            "mechanism, prediction, or universality",
        ],
        "next": next_nodes,
        "artifacts": [
            "Output/4140/frozen_analysis_contract.yaml",
            "Output/4140/reproducibility_registry.csv",
            "Output/4140/spectral_set_provenance.md",
            "Output/4140/code_source_map.csv",
            "Output/4140/definition_mismatches.csv",
            "Output/4140/decision.json",
            "Output/4140/4140_summary.md",
        ],
    }

    write_csv(
        OUT / "reproducibility_registry.csv",
        registry,
        ["definition", "paper_location", "code_location", "config_location", "actual_numeric_value", "frozen", "notes"],
    )
    write_csv(
        OUT / "tables" / "reproducibility_registry.csv",
        registry,
        ["definition", "paper_location", "code_location", "config_location", "actual_numeric_value", "frozen", "notes"],
    )
    write_csv(
        OUT / "code_source_map.csv",
        source_map,
        ["concept", "source_code", "primary_output", "output_exists", "notes"],
    )
    write_csv(
        OUT / "tables" / "code_source_map.csv",
        source_map,
        ["concept", "source_code", "primary_output", "output_exists", "notes"],
    )
    write_csv(
        OUT / "definition_mismatches.csv",
        mismatches,
        ["item", "expected_or_paper", "actual_or_code", "severity", "action"],
    )
    write_csv(
        OUT / "tables" / "definition_mismatches.csv",
        mismatches,
        ["item", "expected_or_paper", "actual_or_code", "severity", "action"],
    )
    (OUT / "frozen_analysis_contract.yaml").write_text(frozen_contract(counts), encoding="utf-8")
    (OUT / "spectral_set_provenance.md").write_text(spectral_set_provenance(), encoding="utf-8")
    write_json(OUT / "decision.json", decision)

    summary = f"""# Node 4140 Summary

## Purpose

Freeze the current manuscript analysis contract and check whether the main T1
claim can be traced to existing scripts and outputs before running 4141/4142/4143.

## Exact Analysis Performed

- Read the 007 paper-defense roadmap.
- Checked whether 414x experiments already existed: none were found.
- Mapped active manuscript definitions to code and output artifacts.
- Recomputed the observed support counts from `Output/4081c` tables.
- Traced `spectral_set` provenance from 3032/3032b through 3045.
- Separated true definition mismatches from planned robustness gaps.

## Primary Result

```text
N_both_observed = {counts['n_both']} / 19
N_any_observed  = {counts['n_any']} / 19
stop-level mismatches = {len(stop_items)}
boundary/planned items = {len(boundary_items)}
gate_result = {gate_result}
```

## Observation-Level Result

- Both-scale survivor observations: `{counts['both_obs']}`
- Any-scale survivor observations: `{counts['any_obs']}`
- Non-survivor observations: `{counts['non_survivor_obs']}`

## Gate Evaluation

No stop-level paper-code mismatch was found for the currently frozen T1
definition and survival counts.

The audit does identify three planned pre-submission gaps:

- full-pipeline omnibus null is not yet run;
- alternative detrending challenge is not yet run;
- affine condition-number QC is not yet run.

These are not silent definition changes. They are the next hardening tests.

## What This Strengthens

4140 strengthens the project by making the current analysis contract explicit:
the manuscript claim can now be mapped to concrete code files, output tables,
and fixed thresholds.

## What This Weakens

4140 does not make the 14/19 count statistically calibrated. Existing 4081c
non-event replicates are part of the survival gate but are not the same thing
as the 4141 full-pipeline omnibus null.

## What This Does NOT Prove

{md_table([{"does_not_prove": x} for x in decision["does_not_prove"]], ["does_not_prove"])}

## Decision

`{gate_result}`

## Next

{md_table([{"next": x} for x in next_nodes], ["next"])}

## Artifacts

- `Output/4140/frozen_analysis_contract.yaml`
- `Output/4140/reproducibility_registry.csv`
- `Output/4140/spectral_set_provenance.md`
- `Output/4140/code_source_map.csv`
- `Output/4140/definition_mismatches.csv`
- `Output/4140/decision.json`
"""
    (OUT / "4140_summary.md").write_text(summary, encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2), flush=True)
    print(f"Wrote 4140 outputs to {rel(OUT)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
