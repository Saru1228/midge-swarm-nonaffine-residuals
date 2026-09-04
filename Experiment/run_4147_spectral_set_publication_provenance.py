#!/usr/bin/env python3
"""4147 publication provenance for spectral_set labels.

This node turns the inherited 3032/3032b spectral partition into a
publication-facing reconstruction record. It checks that the low/high labels
used to define transition events are upstream of the local-affine T1 analyses
and are not optimized from T1.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4147"
TABLES = OUT / "tables"
DATE = "2026-09-02"
NODE = "4147_spectral_set_publication_provenance"

SET_ORDER = ["low", "high"]
BEST_PARTITION = "eig2"
T1_TERMS = [
    r"\bT1\b",
    r"all_tangential",
    r"local_tangential",
    r"non_affine",
    r"nonaffine",
    r"run_4081",
    r"run_4084",
]


PATHS = {
    "o3032_decision_json": ROOT / "Output" / "3032" / "3032_egrt_node.json",
    "o3032_decision_csv": ROOT / "Output" / "3032" / "tables" / "egrt_decision_summary.csv",
    "o3032_partition": ROOT / "Output" / "3032" / "tables" / "spectral_partition_summary.csv",
    "o3032_mapping": ROOT / "Output" / "3032" / "tables" / "spectral_cell_mapping.csv",
    "o3032_edges": ROOT / "Output" / "3032" / "tables" / "ulam_bin_edges.json",
    "o3032_interpretation": ROOT / "Output" / "3032" / "tables" / "best_partition_interpretation.csv",
    "o3032_retention_by_ob": ROOT / "Output" / "3032" / "tables" / "partition_retention_by_ob.csv",
    "o3032b_labels": ROOT / "Output" / "3032b" / "processed" / "frame_spectral_labels.csv",
    "o3041_frame": ROOT / "Output" / "3041" / "processed" / "frame_layer_metrics.csv",
    "o3041b_frame": ROOT / "Output" / "3041b" / "processed" / "frame_macrostate_candidates.csv",
    "o3045_events": ROOT / "Output" / "3045" / "tables" / "transition_events.csv",
    "r3032": ROOT / "Experiment" / "run_3032_transfer_operator_metastability.py",
    "r3032b": ROOT / "Experiment" / "run_3032b_state_meaning_residence_audit.py",
    "r3041": ROOT / "Experiment" / "run_3041_anisotropic_layer_residence.py",
    "r3041b": ROOT / "Experiment" / "run_3041b_coarse_graining_closure_audit.py",
    "r3045": ROOT / "Experiment" / "run_3045_residual_event_trigger_search.py",
}


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def ensure_dirs() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def read_csv(path: Path, **kwargs: Any) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {rel(path)}")
    return pd.read_csv(path, **kwargs)


def write_csv(df: pd.DataFrame, filename: str) -> None:
    df.to_csv(OUT / filename, index=False)
    df.to_csv(TABLES / filename, index=False)


def write_json(obj: dict[str, Any], filename: str) -> None:
    (OUT / filename).write_text(json.dumps(obj, indent=2), encoding="utf-8")


def fmt(value: Any, digits: int = 4) -> str:
    try:
        value_f = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(value_f):
        return "NA"
    return f"{value_f:.{digits}g}"


def first_line(path: Path, pattern: str) -> int | None:
    if not path.exists():
        return None
    rx = re.compile(pattern)
    for i, line in enumerate(read_text(path).splitlines(), start=1):
        if rx.search(line):
            return i
    return None


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
                vals.append(fmt(val))
            else:
                vals.append(str(val).replace("\n", " ").replace("|", "\\|"))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def load_core() -> dict[str, Any]:
    decision_csv = read_csv(PATHS["o3032_decision_csv"])
    decision_row = decision_csv.iloc[0].to_dict()
    partition = read_csv(PATHS["o3032_partition"])
    mapping = read_csv(PATHS["o3032_mapping"])
    interpretation = read_csv(PATHS["o3032_interpretation"])
    retention = read_csv(PATHS["o3032_retention_by_ob"])
    events = read_csv(PATHS["o3045_events"])
    edges = json.loads(read_text(PATHS["o3032_edges"]))

    labels = read_csv(
        PATHS["o3032b_labels"],
        usecols=["dataset", "ob", "t", "ulam_cell", "spectral_set"],
    )
    labels["ob"] = pd.to_numeric(labels["ob"], errors="coerce").astype("Int64")
    labels["t_key"] = pd.to_numeric(labels["t"], errors="coerce").round(6)

    frame3041b = read_csv(
        PATHS["o3041b_frame"],
        usecols=lambda c: c in {"dataset", "ob", "t", "spectral_set", "compact_density_2"},
        low_memory=False,
    )
    frame3041b["ob"] = pd.to_numeric(frame3041b["ob"], errors="coerce").astype("Int64")
    frame3041b["t_key"] = pd.to_numeric(frame3041b["t"], errors="coerce").round(6)

    return {
        "decision_row": decision_row,
        "partition": partition,
        "mapping": mapping,
        "interpretation": interpretation,
        "retention": retention,
        "events": events,
        "edges": edges,
        "labels": labels,
        "frame3041b": frame3041b,
    }


def build_source_code_map() -> pd.DataFrame:
    rows = [
        {
            "stage": "3032_input",
            "role": "macroscopic input table",
            "script": rel(PATHS["r3032"]),
            "line": first_line(PATHS["r3032"], r"RAW_PATH\s*="),
            "artifact": rel(PATHS["o3032_decision_json"]),
            "notes": "3032 reads geometric center observables from 3001.",
        },
        {
            "stage": "3032_variables",
            "role": "slow variables",
            "script": rel(PATHS["r3032"]),
            "line": first_line(PATHS["r3032"], r"DEFAULT_SLOW_VARIABLES"),
            "artifact": rel(PATHS["o3032_decision_csv"]),
            "notes": "Default slow variables are r_rms, density_rms, anisotropy.",
        },
        {
            "stage": "3032_discretization",
            "role": "quantile Ulam cells",
            "script": rel(PATHS["r3032"]),
            "line": first_line(PATHS["r3032"], r"def assign_ulam_cells"),
            "artifact": rel(PATHS["o3032_edges"]),
            "notes": "Each robust-z slow variable is split into four pooled quantile bins.",
        },
        {
            "stage": "3032_transfer_operator",
            "role": "empirical lagged transition matrix",
            "script": rel(PATHS["r3032"]),
            "line": first_line(PATHS["r3032"], r"def transition_counts"),
            "artifact": rel(PATHS["o3032_partition"]),
            "notes": "Transitions are counted at lag 0.10 s within each observation.",
        },
        {
            "stage": "3032_spectral_partition",
            "role": "eigenvector split into low/high sets",
            "script": rel(PATHS["r3032"]),
            "line": first_line(PATHS["r3032"], r"def spectral_partitions"),
            "artifact": rel(PATHS["o3032_mapping"]),
            "notes": "Nontrivial right eigenvectors are cut at the stationary-mass weighted median.",
        },
        {
            "stage": "3032_best_partition",
            "role": "selected partition",
            "script": rel(PATHS["r3032"]),
            "line": first_line(PATHS["r3032"], r"best_partition_id\s*=\s*str\(decision"),
            "artifact": rel(PATHS["o3032_decision_csv"]),
            "notes": "The selected partition is eig2.",
        },
        {
            "stage": "3032b_materialization",
            "role": "frame-level spectral labels",
            "script": rel(PATHS["r3032b"]),
            "line": first_line(PATHS["r3032b"], r"frame_spectral_labels\.csv"),
            "artifact": rel(PATHS["o3032b_labels"]),
            "notes": "Frame ulam_cell values are mapped to low/high labels.",
        },
        {
            "stage": "3041_propagation",
            "role": "attach labels to layer metrics",
            "script": rel(PATHS["r3041"]),
            "line": first_line(PATHS["r3041"], r"LABEL_PATH"),
            "artifact": rel(PATHS["o3041_frame"]),
            "notes": "3032b labels are read by observation and time.",
        },
        {
            "stage": "3041b_propagation",
            "role": "propagate compact_density_2",
            "script": rel(PATHS["r3041b"]),
            "line": first_line(PATHS["r3041b"], r"compact_density_2"),
            "artifact": rel(PATHS["o3041b_frame"]),
            "notes": "compact_density_2 is copied from spectral_set when available.",
        },
        {
            "stage": "3045_event_detection",
            "role": "detect low/high run switches",
            "script": rel(PATHS["r3045"]),
            "line": first_line(PATHS["r3045"], r"def detect_transition_events"),
            "artifact": rel(PATHS["o3045_events"]),
            "notes": "Events are label switches with both adjacent runs at least 0.20 s.",
        },
    ]
    return pd.DataFrame(rows)


def build_partition_summary(core: dict[str, Any]) -> pd.DataFrame:
    decision = core["decision_row"]
    partition = core["partition"]
    best = partition[partition["partition_id"] == BEST_PARTITION].iloc[0].to_dict()
    mapping = core["mapping"]
    best_map = mapping[mapping["partition_id"] == BEST_PARTITION].copy()
    rows: list[dict[str, Any]] = []
    for set_name in SET_ORDER:
        d = best_map[best_map["spectral_set"] == set_name]
        rows.append(
            {
                "partition_id": BEST_PARTITION,
                "spectral_set": set_name,
                "eigen_rank": int(best["eigen_rank"]),
                "eigenvalue_real": float(best["eigenvalue_real"]),
                "implied_timescale_sec": float(best["implied_timescale_sec"]),
                "n_cells": int(len(d)),
                "stationary_mass_sum": float(pd.to_numeric(d["stationary_mass"], errors="coerce").sum()),
                "eigenvector_value_min": float(pd.to_numeric(d["eigenvector_value"], errors="coerce").min()),
                "eigenvector_value_max": float(pd.to_numeric(d["eigenvector_value"], errors="coerce").max()),
                "pooled_retention": float(best[f"{set_name}_pooled_retention"]),
                "retention_lift": float(best[f"{set_name}_retention_lift"]),
                "exit_probability": float(best[f"{set_name}_exit_probability"]),
                "candidate_variables": str(decision["candidate_variables"]),
                "lag_sec": float(decision["lag_sec"]),
                "n_bins_per_variable": int(decision["n_bins"]),
            }
        )
    return pd.DataFrame(rows)


def build_label_distribution(core: dict[str, Any]) -> pd.DataFrame:
    labels = core["labels"]
    frame3041b = core["frame3041b"]
    events = core["events"]

    rows: list[dict[str, Any]] = []
    for source_id, df, label_col in [
        ("3032b_frame_spectral_labels", labels, "spectral_set"),
        ("3041b_frame_macrostate_candidates", frame3041b, "spectral_set"),
        ("3041b_compact_density_2", frame3041b, "compact_density_2"),
    ]:
        counts = df[label_col].astype(str).value_counts(dropna=False).to_dict()
        rows.append(
            {
                "source_id": source_id,
                "label_column": label_col,
                "n_rows": int(len(df)),
                "n_observations": int(pd.to_numeric(df["ob"], errors="coerce").nunique()),
                "n_low": int(counts.get("low", 0)),
                "n_high": int(counts.get("high", 0)),
                "n_unavailable_or_other": int(len(df) - counts.get("low", 0) - counts.get("high", 0)),
            }
        )
    ev_counts = events["event_type"].astype(str).value_counts().to_dict()
    rows.append(
        {
            "source_id": "3045_transition_events",
            "label_column": "event_type",
            "n_rows": int(len(events)),
            "n_observations": int(pd.to_numeric(events["ob"], errors="coerce").nunique()),
            "n_low": int(ev_counts.get("high_to_low", 0)),
            "n_high": int(ev_counts.get("low_to_high", 0)),
            "n_unavailable_or_other": int(
                len(events) - ev_counts.get("high_to_low", 0) - ev_counts.get("low_to_high", 0)
            ),
        }
    )
    return pd.DataFrame(rows)


def build_propagation_check(core: dict[str, Any]) -> pd.DataFrame:
    labels = core["labels"][["dataset", "ob", "t_key", "spectral_set"]].rename(
        columns={"spectral_set": "spectral_set_3032b"}
    )
    frame = core["frame3041b"][["dataset", "ob", "t_key", "spectral_set", "compact_density_2"]].rename(
        columns={"spectral_set": "spectral_set_3041b"}
    )
    merged = labels.merge(frame, on=["dataset", "ob", "t_key"], how="inner")
    if merged.empty:
        match_spectral = math.nan
        match_compact = math.nan
    else:
        match_spectral = float((merged["spectral_set_3032b"].astype(str) == merged["spectral_set_3041b"].astype(str)).mean())
        match_compact = float((merged["spectral_set_3032b"].astype(str) == merged["compact_density_2"].astype(str)).mean())
    events = core["events"]
    duration_pass = bool(
        (pd.to_numeric(events["prev_duration_sec"], errors="coerce") >= 0.20).all()
        and (pd.to_numeric(events["next_duration_sec"], errors="coerce") >= 0.20).all()
    )
    states_pass = bool(
        events["from_state"].astype(str).isin(SET_ORDER).all()
        and events["to_state"].astype(str).isin(SET_ORDER).all()
        and (events["from_state"].astype(str) != events["to_state"].astype(str)).all()
    )
    return pd.DataFrame(
        [
            {
                "check_id": "3032b_to_3041b_spectral_set_match",
                "n_intersection_rows": int(len(merged)),
                "metric": "fraction_equal",
                "value": match_spectral,
                "pass": bool(np.isfinite(match_spectral) and match_spectral >= 0.999),
                "notes": "Frame-level spectral_set labels are preserved into 3041b.",
            },
            {
                "check_id": "3032b_to_3041b_compact_density_2_match",
                "n_intersection_rows": int(len(merged)),
                "metric": "fraction_equal",
                "value": match_compact,
                "pass": bool(np.isfinite(match_compact) and match_compact >= 0.999),
                "notes": "compact_density_2 is a copy of spectral_set for low/high frames.",
            },
            {
                "check_id": "3045_transition_state_labels",
                "n_intersection_rows": int(len(events)),
                "metric": "all_from_to_low_high_and_switch",
                "value": float(states_pass),
                "pass": states_pass,
                "notes": "Transition events switch between low and high.",
            },
            {
                "check_id": "3045_transition_persistence_filter",
                "n_intersection_rows": int(len(events)),
                "metric": "all_prev_next_duration_ge_0p20s",
                "value": float(duration_pass),
                "pass": duration_pass,
                "notes": "Both adjacent state runs satisfy the 0.20 s persistence screen.",
            },
        ]
    )


def build_t1_scan() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for key in ["r3032", "r3032b", "r3041", "r3041b", "r3045"]:
        path = PATHS[key]
        text = read_text(path) if path.exists() else ""
        stage = {
            "r3032": "label_construction",
            "r3032b": "label_materialization",
            "r3041": "label_propagation",
            "r3041b": "label_propagation",
            "r3045": "event_detection_and_downstream_residual_search",
        }[key]
        hits = []
        for term in T1_TERMS:
            if re.search(term, text):
                hits.append(term)
        rows.append(
            {
                "script": rel(path),
                "stage": stage,
                "n_t1_term_hits": int(len(hits)),
                "hit_terms": "; ".join(hits),
                "t1_independence_pass_for_label_construction": (
                    len(hits) == 0 if stage in {"label_construction", "label_materialization"} else True
                ),
                "notes": (
                    "Required to be free of T1 terms."
                    if stage in {"label_construction", "label_materialization"}
                    else "May consume labels downstream; not part of spectral label fitting."
                ),
            }
        )
    return pd.DataFrame(rows)


def build_example_trace(core: dict[str, Any]) -> pd.DataFrame:
    events = core["events"].sort_values(["ob", "event_t"]).reset_index(drop=True)
    if events.empty:
        return pd.DataFrame()
    event = events.iloc[0].to_dict()
    ob = int(event["ob"])
    dataset = str(event["dataset"])
    event_t = float(event["event_t"])
    labels = core["labels"]
    frame = core["frame3041b"]
    sub_labels = labels[
        (labels["ob"].astype("Int64") == ob)
        & (labels["dataset"].astype(str) == dataset)
        & ((pd.to_numeric(labels["t"], errors="coerce") - event_t).abs() <= 0.06)
    ][["dataset", "ob", "t", "t_key", "ulam_cell", "spectral_set"]].copy()
    sub_frame = frame[
        (frame["ob"].astype("Int64") == ob)
        & (frame["dataset"].astype(str) == dataset)
        & ((pd.to_numeric(frame["t"], errors="coerce") - event_t).abs() <= 0.06)
    ][["dataset", "ob", "t_key", "spectral_set", "compact_density_2"]].copy()
    trace = sub_labels.merge(sub_frame, on=["dataset", "ob", "t_key"], how="left", suffixes=("_3032b", "_3041b"))
    trace["example_event_id"] = int(event["event_id"])
    trace["example_event_type"] = str(event["event_type"])
    trace["event_t"] = event_t
    trace["relative_t_sec"] = pd.to_numeric(trace["t"], errors="coerce") - event_t
    trace["is_event_frame"] = np.isclose(pd.to_numeric(trace["t"], errors="coerce"), event_t, atol=5e-7)
    return trace[
        [
            "example_event_id",
            "example_event_type",
            "dataset",
            "ob",
            "event_t",
            "t",
            "relative_t_sec",
            "ulam_cell",
            "spectral_set_3032b",
            "spectral_set_3041b",
            "compact_density_2",
            "is_event_frame",
        ]
    ].sort_values("t")


def write_algorithm(core: dict[str, Any], partition_summary: pd.DataFrame) -> None:
    decision = core["decision_row"]
    edges = core["edges"]
    edge_rows = [
        {
            "variable": var,
            "quantile_edges_z": ", ".join(fmt(x, 6) for x in vals),
        }
        for var, vals in edges.items()
    ]
    part_rows = partition_summary.to_dict(orient="records")
    text = f"""# 4147 spectral_set Algorithm

Date: {DATE}

## Reconstruction Steps

1. Start from `Output/3001/processed/geometric_center_observables_all.csv`.
2. Select the 3032 slow-variable basis:
   `{decision['candidate_variables']}`.
3. Within each observation, robust-z standardize each slow variable using the
   median and IQR-based scale.
4. Pool the standardized frames and split each slow variable into
   `{int(decision['n_bins'])}` quantile bins.
5. Encode the three binned coordinates as one Ulam cell. With three variables
   and four bins per variable, the full grid has `{int(decision['n_total_cells'])}`
   possible cells; `{int(decision['n_active_cells'])}` were active.
6. Count empirical transitions between active Ulam cells at lag
   `{fmt(decision['lag_sec'])}` s within each observation.
7. Row-normalize the count matrix to obtain an empirical transfer operator.
8. Compute right eigenvectors of that operator. For each nontrivial candidate
   eigenvector, split active cells at the stationary-mass weighted median.
9. Select the best partition by the 3032 gate metrics. The selected partition
   is `{BEST_PARTITION}`, eigen-rank `{int(decision['best_partition_eigen_rank'])}`.
10. Materialize frame labels by mapping each frame's Ulam cell through the
    selected cell-to-set table.
11. Define transition events as switches between adjacent low/high runs,
    retaining only switches for which both adjacent runs last at least `0.20 s`.

## Quantile Edges

{md_table(edge_rows, ["variable", "quantile_edges_z"])}

## Selected Partition Summary

{md_table(part_rows, [
    "spectral_set",
    "n_cells",
    "stationary_mass_sum",
    "pooled_retention",
    "retention_lift",
    "exit_probability",
])}

## Interpretation

The 3032 selected partition is a compact-density partition. In the selected
`{BEST_PARTITION}` partition, the high set has higher `density_rms`, lower
`r_rms`, and lower `anisotropy` than the low set according to the 3032
interpretive axis.
"""
    (OUT / "spectral_set_algorithm.md").write_text(text, encoding="utf-8")


def write_supplement_method(core: dict[str, Any]) -> None:
    decision = core["decision_row"]
    text = rf"""\subsection{{Construction of compact-density transition labels}}

The compact-density transition labels used in the event-conditioned analyses
were inherited from an upstream transfer-operator coarse graining and were not
fitted from the T1 residual. The upstream state space was built from the
swarm-level variables \texttt{{r\_rms}}, \texttt{{density\_rms}}, and
\texttt{{anisotropy}}. Each variable was robust-z standardized within each
observation, after which pooled frames were discretized into
{int(decision['n_bins'])} quantile bins per variable. The three binned
coordinates defined an Ulam grid with {int(decision['n_total_cells'])}
possible cells, of which {int(decision['n_active_cells'])} were active in the
data.

An empirical transfer operator was estimated by counting transitions between
active Ulam cells at lag {fmt(decision['lag_sec'])} s within each observation
and row-normalizing the resulting count matrix. Nontrivial right eigenvectors
of this operator were used to form candidate two-set partitions by cutting each
eigenvector at its stationary-mass weighted median. The selected partition was
\texttt{{{BEST_PARTITION}}}, the second eigenvector partition, with eigenvalue
{fmt(decision['top_nontrivial_eigenvalue_real'])}, implied timescale
{fmt(decision['top_nontrivial_implied_timescale_sec'])} s, minimum pooled
retention {fmt(decision['best_partition_min_pooled_retention'])}, and minimum
retention lift {fmt(decision['best_partition_min_retention_lift'])}. The high
set corresponded to the more compact-density state: higher density, smaller
root-mean-square radius, and lower anisotropy in the 3032 interpretation.

Frame-level \texttt{{spectral\_set}} labels were then obtained by mapping each
frame's Ulam cell to the selected low/high set. Transition events were defined
as switches between adjacent low and high runs. A switch was retained only when
both the preceding and following runs lasted at least 0.20 s, thereby removing
single-frame or very short label flicker at the 100 Hz sampling rate. The event
time was the first frame of the new run, and events were labeled as
\texttt{{low\_to\_high}} or \texttt{{high\_to\_low}}.
"""
    (OUT / "supplement_method.tex").write_text(text, encoding="utf-8")


def write_provenance(
    core: dict[str, Any],
    source_map: pd.DataFrame,
    partition_summary: pd.DataFrame,
    label_distribution: pd.DataFrame,
    propagation: pd.DataFrame,
    t1_scan: pd.DataFrame,
    decision: dict[str, Any],
) -> None:
    interp = core["interpretation"].to_dict(orient="records")
    event_counts = core["events"]["event_type"].astype(str).value_counts().to_dict()
    text = f"""# 4147 spectral_set Publication Provenance

Node: `{NODE}`  
Date: {DATE}

## Result

`{decision['gate_result']}`

The low/high `spectral_set` labels used by the manuscript are reconstructable
from upstream macroscopic variables and are not fitted from T1.

## Provenance Chain

```text
3001 geometric center observables
  -> 3032 transfer-operator spectral partition
  -> 3032b frame_spectral_labels.csv
  -> 3041/3041b propagated frame macrostate table
  -> 3045 transition_events.csv
  -> 4081/4084/414x local-affine T1 analyses
```

## Selected Partition

{md_table(partition_summary.to_dict(orient="records"), [
    "spectral_set",
    "n_cells",
    "stationary_mass_sum",
    "pooled_retention",
    "retention_lift",
    "exit_probability",
])}

## Label and Event Counts

{md_table(label_distribution.to_dict(orient="records"), [
    "source_id",
    "label_column",
    "n_rows",
    "n_observations",
    "n_low",
    "n_high",
    "n_unavailable_or_other",
])}

Transition-event counts:

```text
{json.dumps(event_counts, sort_keys=True)}
```

## Propagation Checks

{md_table(propagation.to_dict(orient="records"), [
    "check_id",
    "metric",
    "value",
    "pass",
    "notes",
])}

## T1 Independence Scan

{md_table(t1_scan.to_dict(orient="records"), [
    "script",
    "stage",
    "n_t1_term_hits",
    "hit_terms",
    "t1_independence_pass_for_label_construction",
])}

## Source Code Map

{md_table(source_map.to_dict(orient="records"), [
    "stage",
    "role",
    "script",
    "line",
    "artifact",
])}

## Interpretation Table

{md_table(interp, [
    "spectral_set",
    "n_frames",
    "occupancy_fraction",
    "median_r_rms_z",
    "median_density_rms_z",
    "median_anisotropy_z",
])}

## Boundary

This audit supports provenance and non-circularity of the compact-density
labels. It does not prove that the two-state spectral partition is the only or
best biological state representation. In the manuscript it should be described
as an inherited compact-density coarse graining used to define events.
"""
    (OUT / "spectral_set_provenance.md").write_text(text, encoding="utf-8")
    (OUT / "4147_summary.md").write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    core = load_core()

    source_map = build_source_code_map()
    partition_summary = build_partition_summary(core)
    label_distribution = build_label_distribution(core)
    propagation = build_propagation_check(core)
    t1_scan = build_t1_scan()
    example_trace = build_example_trace(core)

    write_csv(source_map, "source_code_map.csv")
    write_csv(partition_summary, "selected_partition_summary.csv")
    write_csv(label_distribution, "label_distribution.csv")
    write_csv(propagation, "label_propagation_checks.csv")
    write_csv(t1_scan, "t1_independence_scan.csv")
    write_csv(example_trace, "example_label_trace.csv")

    no_missing_source_lines = bool(source_map["line"].notna().all())
    propagation_pass = bool(propagation["pass"].all())
    construction_scan = t1_scan[
        t1_scan["stage"].isin(["label_construction", "label_materialization"])
    ]
    t1_independent = bool(construction_scan["t1_independence_pass_for_label_construction"].all())
    decision_row = core["decision_row"]
    selected_partition_pass = (
        str(decision_row.get("best_partition_id")) == BEST_PARTITION
        and str(decision_row.get("pass_gate")).lower() == "true"
    )
    label_rows = label_distribution[
        label_distribution["source_id"] == "3032b_frame_spectral_labels"
    ].iloc[0]
    labels_available = (
        int(label_rows["n_observations"]) == 19
        and int(label_rows["n_low"]) > 0
        and int(label_rows["n_high"]) > 0
    )

    decision = {
        "node": NODE,
        "date": DATE,
        "gate_result": (
            "pass_4147_spectral_set_publication_provenance_ready"
            if selected_partition_pass
            and labels_available
            and propagation_pass
            and t1_independent
            and no_missing_source_lines
            else "boundary_4147_spectral_set_provenance_needs_manual_review"
        ),
        "primary_metrics": {
            "best_partition_id": str(decision_row.get("best_partition_id")),
            "candidate_variables": str(decision_row.get("candidate_variables")),
            "lag_sec": float(decision_row.get("lag_sec")),
            "n_bins": int(decision_row.get("n_bins")),
            "n_total_cells": int(decision_row.get("n_total_cells")),
            "n_active_cells": int(decision_row.get("n_active_cells")),
            "active_coverage": float(decision_row.get("active_coverage")),
            "top_nontrivial_eigenvalue_real": float(
                decision_row.get("top_nontrivial_eigenvalue_real")
            ),
            "best_partition_min_pooled_retention": float(
                decision_row.get("best_partition_min_pooled_retention")
            ),
            "best_partition_min_retention_lift": float(
                decision_row.get("best_partition_min_retention_lift")
            ),
            "n_frame_labels": int(label_rows["n_rows"]),
            "n_label_observations": int(label_rows["n_observations"]),
            "n_low_labels": int(label_rows["n_low"]),
            "n_high_labels": int(label_rows["n_high"]),
            "n_transition_events": int(len(core["events"])),
            "propagation_checks_pass": propagation_pass,
            "label_construction_t1_independent": t1_independent,
            "source_code_map_complete": no_missing_source_lines,
        },
        "manuscript_instruction": (
            "Describe spectral_set as an inherited transfer-operator "
            "compact-density coarse graining based on r_rms, density_rms, and "
            "anisotropy. Do not imply it was fitted from T1."
        ),
        "next": "4148_notation_and_equation_consistency_audit",
    }
    write_json(decision, "decision.json")
    write_algorithm(core, partition_summary)
    write_supplement_method(core)
    write_provenance(
        core,
        source_map,
        partition_summary,
        label_distribution,
        propagation,
        t1_scan,
        decision,
    )
    print(json.dumps(decision, indent=2))


if __name__ == "__main__":
    main()
