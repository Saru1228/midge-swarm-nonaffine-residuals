#!/usr/bin/env python3
"""4146 near-pre definition audit.

This node resolves the review-008 discrepancy between the original 4085
near-pre count (8/14) and the 4142 detrending-check centered count (11/14).
It does not rerun event extraction. It audits the already frozen output tables
and asks whether those two numbers are the same estimand.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4146"
TABLES = OUT / "tables"
DATE = "2026-09-02"
NODE = "4146_near_pre_definition_audit"

PHASE = "near_pre"
VARIABLE = "all_tangential"
PHASE_WINDOW = "[-0.25, 0.00) s"

GATE_4085 = {"abs_gap_gate": 0.12, "p_gate": 0.25}
GATE_4142 = {"abs_gap_gate": 0.03, "p_gate": 0.35}


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def ensure_dirs() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)


def read_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(ROOT / path)


def write_csv(df: pd.DataFrame, filename: str) -> None:
    df.to_csv(OUT / filename, index=False)
    df.to_csv(TABLES / filename, index=False)


def write_json(obj: dict[str, Any], filename: str) -> None:
    (OUT / filename).write_text(json.dumps(obj, indent=2), encoding="utf-8")


def bool_from_csv(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


def fmt(value: Any, digits: int = 4) -> str:
    try:
        value_f = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(value_f):
        return "NA"
    return f"{value_f:.{digits}g}"


def ob_list(df: pd.DataFrame) -> list[int]:
    return sorted(df["ob"].astype(int).unique().tolist())


def compact_list(values: list[int]) -> str:
    return ",".join(str(v) for v in values)


def near_pre_rows_4085() -> pd.DataFrame:
    rows = read_csv("Output/4085/tables/phase_profile_rows.csv")
    mask = (rows["variable"] == VARIABLE) & (rows["phase"] == PHASE)
    out = rows.loc[mask].copy()
    out["source_node"] = "4085"
    out["variant"] = "original_4085"
    out["reported_phase_gate"] = out["phase_gate"].map(bool_from_csv)
    return out


def near_pre_rows_4142() -> pd.DataFrame:
    rows = read_csv("Output/4142/phase_detrending_rows.csv")
    mask = (rows["variable"] == VARIABLE) & (rows["phase"] == PHASE)
    out = rows.loc[mask].copy()
    out["source_node"] = "4142"
    out["reported_phase_gate"] = out["phase_gate"].map(bool_from_csv)
    return out


def gate_mask(df: pd.DataFrame, gate: dict[str, float]) -> pd.Series:
    return (
        (pd.to_numeric(df["abs_event_minus_abs_null_z"], errors="coerce") > gate["abs_gap_gate"])
        & (pd.to_numeric(df["p_null_abs_ge_real_abs"], errors="coerce") <= gate["p_gate"])
    )


def summarize_source(
    source_id: str,
    df: pd.DataFrame,
    reported_gate: dict[str, float],
    preprocessing: str,
    null_sampler: str,
    source_table: str,
    source_script: str,
) -> dict[str, Any]:
    reported_count = int(df["reported_phase_gate"].sum())
    strict_count = int(gate_mask(df, GATE_4085).sum())
    loose_count = int(gate_mask(df, GATE_4142).sum())
    return {
        "source_id": source_id,
        "source_table": source_table,
        "source_script": source_script,
        "variable": VARIABLE,
        "phase": PHASE,
        "phase_window": PHASE_WINDOW,
        "n_observations": int(df["ob"].nunique()),
        "observations": compact_list(ob_list(df)),
        "preprocessing": preprocessing,
        "null_sampler": null_sampler,
        "reported_abs_gap_gate": reported_gate["abs_gap_gate"],
        "reported_p_gate": reported_gate["p_gate"],
        "reported_phase_gate_count": reported_count,
        "count_under_4085_gate": strict_count,
        "count_under_4142_gate": loose_count,
        "median_abs_event_minus_abs_null_z": float(
            pd.to_numeric(df["abs_event_minus_abs_null_z"], errors="coerce").median()
        ),
        "median_p_null_abs_ge_real_abs": float(
            pd.to_numeric(df["p_null_abs_ge_real_abs"], errors="coerce").median()
        ),
        "passed_observations_reported": compact_list(
            sorted(df.loc[df["reported_phase_gate"], "ob"].astype(int).tolist())
        ),
        "passed_observations_under_4085_gate": compact_list(
            sorted(df.loc[gate_mask(df, GATE_4085), "ob"].astype(int).tolist())
        ),
        "passed_observations_under_4142_gate": compact_list(
            sorted(df.loc[gate_mask(df, GATE_4142), "ob"].astype(int).tolist())
        ),
    }


def build_audit_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df4085 = near_pre_rows_4085()
    df4142 = near_pre_rows_4142()

    centered = df4142.loc[df4142["variant"] == "centered_1s"].copy()
    past = df4142.loc[df4142["variant"] == "past_1s"].copy()
    none = df4142.loc[df4142["variant"] == "none_z"].copy()

    source_rows = [
        summarize_source(
            source_id="4085_original",
            df=df4085,
            reported_gate=GATE_4085,
            preprocessing=(
                "frozen 4084 residual column all_tangential__resid4084 "
                "(centered one-second detrending already cached)"
            ),
            null_sampler="run_4081.sample_non_event_times",
            source_table="Output/4085/tables/phase_profile_rows.csv",
            source_script="Experiment/run_4085_event_phase_profile_of_t1_signal.py",
        ),
        summarize_source(
            source_id="4142_centered_1s",
            df=centered,
            reported_gate=GATE_4142,
            preprocessing=(
                "recomputed centered_1s from raw all_tangential in the 4084 "
                "spatial frame"
            ),
            null_sampler="run_4141.sample_like_events",
            source_table="Output/4142/phase_detrending_rows.csv",
            source_script="Experiment/run_4142_detrending_challenge.py",
        ),
        summarize_source(
            source_id="4142_past_1s",
            df=past,
            reported_gate=GATE_4142,
            preprocessing="past-only one-second detrending from raw all_tangential",
            null_sampler="run_4141.sample_like_events",
            source_table="Output/4142/phase_detrending_rows.csv",
            source_script="Experiment/run_4142_detrending_challenge.py",
        ),
        summarize_source(
            source_id="4142_none_z",
            df=none,
            reported_gate=GATE_4142,
            preprocessing="within-observation robust-z only; no rolling detrending",
            null_sampler="run_4141.sample_like_events",
            source_table="Output/4142/phase_detrending_rows.csv",
            source_script="Experiment/run_4142_detrending_challenge.py",
        ),
    ]
    audit = pd.DataFrame(source_rows)

    merged = df4085[
        [
            "ob",
            "real_phase_aligned_z",
            "null_phase_abs_median_z",
            "abs_event_minus_abs_null_z",
            "p_null_abs_ge_real_abs",
            "reported_phase_gate",
        ]
    ].merge(
        centered[
            [
                "ob",
                "real_phase_aligned_z",
                "null_phase_abs_median_z",
                "abs_event_minus_abs_null_z",
                "p_null_abs_ge_real_abs",
                "reported_phase_gate",
            ]
        ],
        on="ob",
        suffixes=("_4085", "_4142_centered"),
    )
    merged["real_phase_abs_diff"] = (
        merged["real_phase_aligned_z_4085"] - merged["real_phase_aligned_z_4142_centered"]
    ).abs()
    merged["null_abs_median_delta_4142_minus_4085"] = (
        merged["null_phase_abs_median_z_4142_centered"]
        - merged["null_phase_abs_median_z_4085"]
    )
    merged["p_delta_4142_minus_4085"] = (
        merged["p_null_abs_ge_real_abs_4142_centered"]
        - merged["p_null_abs_ge_real_abs_4085"]
    )
    merged["4085_gate_recomputed_on_4085"] = gate_mask(
        merged.rename(
            columns={
                "abs_event_minus_abs_null_z_4085": "abs_event_minus_abs_null_z",
                "p_null_abs_ge_real_abs_4085": "p_null_abs_ge_real_abs",
            }
        ),
        GATE_4085,
    )
    merged["4085_gate_recomputed_on_4142_centered"] = gate_mask(
        merged.rename(
            columns={
                "abs_event_minus_abs_null_z_4142_centered": "abs_event_minus_abs_null_z",
                "p_null_abs_ge_real_abs_4142_centered": "p_null_abs_ge_real_abs",
            }
        ),
        GATE_4085,
    )
    merged["4142_gate_recomputed_on_4085"] = gate_mask(
        merged.rename(
            columns={
                "abs_event_minus_abs_null_z_4085": "abs_event_minus_abs_null_z",
                "p_null_abs_ge_real_abs_4085": "p_null_abs_ge_real_abs",
            }
        ),
        GATE_4142,
    )
    merged["4142_gate_recomputed_on_4142_centered"] = gate_mask(
        merged.rename(
            columns={
                "abs_event_minus_abs_null_z_4142_centered": "abs_event_minus_abs_null_z",
                "p_null_abs_ge_real_abs_4142_centered": "p_null_abs_ge_real_abs",
            }
        ),
        GATE_4142,
    )

    comparisons = [
        {
            "dimension": "tested_observation_set",
            "same": ob_list(df4085) == ob_list(centered),
            "4085_value": compact_list(ob_list(df4085)),
            "4142_centered_value": compact_list(ob_list(centered)),
            "interpretation": "same denominator and observation set",
        },
        {
            "dimension": "variable",
            "same": True,
            "4085_value": VARIABLE,
            "4142_centered_value": VARIABLE,
            "interpretation": "same reported variable",
        },
        {
            "dimension": "phase_window",
            "same": True,
            "4085_value": PHASE_WINDOW,
            "4142_centered_value": PHASE_WINDOW,
            "interpretation": "same near-pre timing bin",
        },
        {
            "dimension": "real_event_values",
            "same": bool(merged["real_phase_abs_diff"].max() < 1e-12),
            "4085_value": "cached real phase values",
            "4142_centered_value": "recomputed centered real phase values",
            "interpretation": (
                f"max absolute real-value difference = "
                f"{merged['real_phase_abs_diff'].max():.3g}"
            ),
        },
        {
            "dimension": "abs_gap_gate",
            "same": GATE_4085["abs_gap_gate"] == GATE_4142["abs_gap_gate"],
            "4085_value": GATE_4085["abs_gap_gate"],
            "4142_centered_value": GATE_4142["abs_gap_gate"],
            "interpretation": "4085 is stricter on effect-size excess",
        },
        {
            "dimension": "p_gate",
            "same": GATE_4085["p_gate"] == GATE_4142["p_gate"],
            "4085_value": GATE_4085["p_gate"],
            "4142_centered_value": GATE_4142["p_gate"],
            "interpretation": "4142 is looser on the pseudo-event tail condition",
        },
        {
            "dimension": "null_sampler",
            "same": False,
            "4085_value": "run_4081.sample_non_event_times",
            "4142_centered_value": "run_4141.sample_like_events",
            "interpretation": "same real events, different pseudo-event controls",
        },
    ]

    return audit, merged, pd.DataFrame(comparisons)


def md_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
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


def write_source_trace(
    audit: pd.DataFrame,
    merged: pd.DataFrame,
    comparison: pd.DataFrame,
    decision: dict[str, Any],
) -> None:
    source_rows = audit[
        [
            "source_id",
            "reported_phase_gate_count",
            "count_under_4085_gate",
            "count_under_4142_gate",
            "reported_abs_gap_gate",
            "reported_p_gate",
            "null_sampler",
        ]
    ].to_dict(orient="records")
    comparison_rows = comparison.to_dict(orient="records")
    text = f"""# 4146 Near-Pre Definition Audit

Node: `{NODE}`  
Date: {DATE}

## Question

Why do the current materials contain both `4085` near-pre support of `8/14`
and `4142` centered near-pre support of `11/14`?

## Result

`{decision['gate_result']}`

The two numbers are not conflicting estimates of one frozen definition.
They use the same observation set, same `all_tangential` variable, same
near-pre window, and effectively identical real event values, but they differ
in the event-control gate and pseudo-event sampler.

## Source-Level Counts

{md_table(source_rows, [
    "source_id",
    "reported_phase_gate_count",
    "count_under_4085_gate",
    "count_under_4142_gate",
    "reported_abs_gap_gate",
    "reported_p_gate",
    "null_sampler",
])}

## Definition Comparison

{md_table(comparison_rows, [
    "dimension",
    "same",
    "4085_value",
    "4142_centered_value",
    "interpretation",
])}

## Key Diagnostic

- 4085 reported `8/14`; recomputing the 4085 gate on 4085 rows also gives
  `8/14`.
- Applying the looser 4142 gate to the same 4085 rows gives `11/14`.
- 4142 centered reported `11/14`; applying the stricter 4085 gate to those
  rows gives `9/14`.
- The maximum absolute difference between the 4085 and 4142-centered real
  near-pre event values is `{merged['real_phase_abs_diff'].max():.3g}`.

## Manuscript Decision

Use the original 4085 `8/14` as the main-text near-pre timing count. Treat the
4142 centered/past/no-rolling near-pre counts as detrending-specific
sensitivity evidence, not as a replacement for the original phase-localization
definition.

## Boundary

This audit resolves a definitional inconsistency. It does not decide whether
near-pre timing is mechanistic, because the earlier state-matched
event-locality route did not preserve a robust near-pre excess.
"""
    (OUT / "source_trace.md").write_text(text, encoding="utf-8")
    (OUT / "4146_summary.md").write_text(text, encoding="utf-8")


def write_manuscript_text() -> None:
    text = r"""# 4146 Manuscript Replacement Text

Recommended replacement for the near-pre paragraph in the active Results:

```latex
The near-pre enrichment should be read with this boundary in mind. It was a
descriptive pattern under the original event-control comparison and did not
survive the later state-matched event-locality challenge described below. A
detrending-specific audit of the same near-pre window retained majority-level
support under centered, past-only, and no-rolling variants, but that audit used
a looser phase-tail gate and a different pseudo-event sampler. We therefore
treat those counts as sensitivity evidence rather than as replacements for the
original $8/14$ phase-localization count.
```
"""
    (OUT / "manuscript_replacement_text.md").write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    audit, merged, comparison = build_audit_tables()

    write_csv(audit, "near_pre_definition_audit.csv")
    write_csv(merged, "near_pre_observation_comparison.csv")
    write_csv(comparison, "definition_dimension_comparison.csv")

    same_core = bool(
        comparison.loc[
            comparison["dimension"].isin(
                ["tested_observation_set", "variable", "phase_window", "real_event_values"]
            ),
            "same",
        ].all()
    )
    gate_or_null_diff = bool(
        not comparison.loc[
            comparison["dimension"].isin(["abs_gap_gate", "p_gate", "null_sampler"]),
            "same",
        ].all()
    )
    count_4085 = int(audit.loc[audit["source_id"] == "4085_original", "reported_phase_gate_count"].iloc[0])
    count_4142_centered = int(
        audit.loc[audit["source_id"] == "4142_centered_1s", "reported_phase_gate_count"].iloc[0]
    )
    count_4085_under_loose = int(
        audit.loc[audit["source_id"] == "4085_original", "count_under_4142_gate"].iloc[0]
    )

    decision = {
        "node": NODE,
        "date": DATE,
        "gate_result": (
            "pass_4146_discrepancy_explained_by_gate_and_null_definition"
            if same_core and gate_or_null_diff and count_4085 == 8 and count_4142_centered == 11
            else "boundary_4146_near_pre_requires_manual_review"
        ),
        "primary_metrics": {
            "same_observation_set_variable_window_and_real_values": same_core,
            "different_gate_or_null_sampler": gate_or_null_diff,
            "reported_4085_near_pre_count": count_4085,
            "reported_4142_centered_near_pre_count": count_4142_centered,
            "4085_rows_under_4142_gate_count": count_4085_under_loose,
            "4142_centered_rows_under_4085_gate_count": int(
                audit.loc[
                    audit["source_id"] == "4142_centered_1s",
                    "count_under_4085_gate",
                ].iloc[0]
            ),
            "max_real_phase_abs_diff_4085_vs_4142_centered": float(
                merged["real_phase_abs_diff"].max()
            ),
        },
        "manuscript_instruction": (
            "Use 4085 8/14 as the main near-pre phase-localization count; "
            "describe 4142 near-pre counts only as sensitivity evidence."
        ),
        "next": "4147_spectral_set_publication_provenance",
    }
    write_json(decision, "discrepancy_decision.json")
    write_source_trace(audit, merged, comparison, decision)
    write_manuscript_text()

    print(json.dumps(decision, indent=2))


if __name__ == "__main__":
    main()
