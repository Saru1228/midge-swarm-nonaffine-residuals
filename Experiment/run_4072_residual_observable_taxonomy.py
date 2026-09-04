"""4072 residual observable taxonomy.

This node freezes the residual-observable target set before any
cross-dataset replication. It reads the 4002A residual-structure screen and
assigns each metric to a role: primary target, secondary diagnostic, or
retired/control.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4072"
SOURCE = ROOT / "Output" / "4002A" / "tables" / "residual_structure_direction_null_comparison.csv"

NODE = "4072_residual_observable_taxonomy"
DATE = "2026-08-25"


PRIMARY_METRICS = {
    "resid_velocity_cov_trace": {
        "taxonomy_class": "V_covariance_anisotropy",
        "reason": "Strongest affine-residual velocity dispersion/covariance survivor; bridges 4001 velocity_cov_trace and 408x residual-energy tests.",
    },
    "resid_speed_rms": {
        "taxonomy_class": "I_magnitude_energy",
        "reason": "Direct residual speed magnitude/energy target; interpretable for local-affine residual energy ladders.",
    },
    "resid_tangential_speed_mean": {
        "taxonomy_class": "III_tangential",
        "reason": "Strong tangential residual survivor with highest sign consistency among main kinematic metrics.",
    },
    "resid_radial_abs_mean": {
        "taxonomy_class": "II_radial",
        "reason": "Radial residual magnitude survivor; keeps inward/outward geometry distinct from tangential motion.",
    },
    "edge_minus_core_resid_speed": {
        "taxonomy_class": "VII_core_edge_contrast",
        "reason": "Primary core-edge residual speed contrast; interpretable spatial redistribution metric.",
    },
    "edge_minus_core_resid_tangential": {
        "taxonomy_class": "VII_core_edge_contrast",
        "reason": "Core-edge tangential residual contrast; complements speed contrast without adding a new family.",
    },
}


SECONDARY_OVERRIDES = {
    "radius_resid_speed_corr": {
        "taxonomy_class": "VI_spatial_heterogeneity",
        "reason": "Spatial-gradient diagnostic. It has notable effect size but did not satisfy the full survivor gate, so it remains secondary.",
    },
    "radius_resid_tangential_corr": {
        "taxonomy_class": "VI_spatial_heterogeneity",
        "reason": "Tangential spatial-gradient diagnostic retained only for sensitivity/context.",
    },
    "resid_inward_fraction": {
        "taxonomy_class": "II_radial",
        "reason": "Directional radial fraction diagnostic; lower gate support than radial absolute magnitude.",
    },
    "resid_radial_velocity_mean": {
        "taxonomy_class": "II_radial",
        "reason": "Signed radial residual diagnostic; kept secondary because sign can be sensitive to event definition.",
    },
    "resid_tangential_fraction": {
        "taxonomy_class": "III_tangential",
        "reason": "Tangential direction fraction diagnostic; lower support than tangential speed mean.",
    },
}


RETIRED_OVERRIDES = {
    "resid_polarization": {
        "taxonomy_class": "IV_directional_alignment",
        "reason": "Residual order/alignment did not survive 4002A; global residual alignment should not drive the next route.",
    },
}


COLUMNS = [
    "variable",
    "family",
    "taxonomy_class",
    "role",
    "primary_rank",
    "n_ob",
    "n_events",
    "real_abs_median_direction_contrast_z",
    "direction_contrast_sign_consistency",
    "null_abs_median_direction_contrast_z",
    "real_minus_null_abs_direction_contrast_z",
    "p_null_abs_direction_ge_real",
    "direction_survives_gate",
    "reason",
]


def read_source() -> list[dict[str, str]]:
    with SOURCE.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def as_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def classify(row: dict[str, str]) -> dict[str, str]:
    variable = row["variable"]
    if variable in PRIMARY_METRICS:
        meta = PRIMARY_METRICS[variable]
        role = "primary_target"
        primary_rank = list(PRIMARY_METRICS).index(variable) + 1
    elif variable in RETIRED_OVERRIDES:
        meta = RETIRED_OVERRIDES[variable]
        role = "retired_or_negative_control"
        primary_rank = ""
    elif variable in SECONDARY_OVERRIDES:
        meta = SECONDARY_OVERRIDES[variable]
        role = "secondary_diagnostic"
        primary_rank = ""
    else:
        meta = {
            "taxonomy_class": "unassigned_secondary_context",
            "reason": "Kept as secondary context only; not selected as a primary target.",
        }
        role = "secondary_diagnostic"
        primary_rank = ""

    out = {col: row.get(col, "") for col in COLUMNS}
    out["taxonomy_class"] = meta["taxonomy_class"]
    out["role"] = role
    out["primary_rank"] = str(primary_rank)
    out["reason"] = meta["reason"]
    return out


def write_csv(path: Path, rows: list[dict[str, str]], columns: list[str] = COLUMNS) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in columns})


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def md_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        vals = []
        for col in columns:
            vals.append(str(row.get(col, "")).replace("\n", " ").replace("|", "\\|"))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def write_config() -> None:
    text = dedent(
        f"""\
        node: {NODE}
        date: {DATE}
        node_type: foundation_metric_freeze
        source_table: Output/4002A/tables/residual_structure_direction_null_comparison.csv
        parent_node: 4070_bounded_result_and_negative_mechanism_map
        primary_metric_limit: 6
        secondary_diagnostic_limit: 12
        next_node: 4073_null_and_baseline_registry
        """
    )
    (OUT / "config.yaml").write_text(text, encoding="utf-8")


def write_summary(records: list[dict[str, str]]) -> None:
    primary = [r for r in records if r["role"] == "primary_target"]
    secondary = [r for r in records if r["role"] == "secondary_diagnostic"]
    retired = [r for r in records if r["role"] == "retired_or_negative_control"]

    by_taxonomy: dict[str, int] = {}
    for row in records:
        by_taxonomy[row["taxonomy_class"]] = by_taxonomy.get(row["taxonomy_class"], 0) + 1

    gate_result = "pass" if len(primary) <= 6 and len(secondary) <= 12 else "fail"
    decision = {
        "node": NODE,
        "question": "Which residual observables are primary targets, secondary diagnostics, or retired controls before replication?",
        "result": gate_result,
        "primary_target_metrics": [r["variable"] for r in sorted(primary, key=lambda x: int(x["primary_rank"]))],
        "secondary_diagnostics": [r["variable"] for r in secondary],
        "retired_or_negative_controls": [r["variable"] for r in retired],
        "gate": "primary_target_metrics <= 6 and secondary_diagnostics <= 12",
        "gate_evaluation": f"primary={len(primary)}, secondary={len(secondary)}, retired={len(retired)}",
        "interpretation": "The residual target is now metric-frozen for 4073/4071. New primary metrics should not be added during replication.",
        "next": ["4073_null_and_baseline_registry"],
    }
    write_json(OUT / "decision.json", decision)

    text = dedent(
        f"""\
        # Node 4072 Summary

        ## Question

        Which affine-residual velocity observables are primary targets, which are secondary diagnostics, and which should be retired before cross-dataset replication?

        ## Why this node exists

        4070 produced a strict target sentence but did not freeze the metric set. 4072 prevents metric search in 4071/408x by selecting a small, interpretable residual-observable taxonomy before seeing new replication outcomes.

        ## Data

        Source table:

        `Output/4002A/tables/residual_structure_direction_null_comparison.csv`

        No raw trajectories were reprocessed.

        ## Frozen parameters

        ```text
        primary_target_metrics <= 6
        secondary_diagnostics <= 12
        no new primary metrics during 4071 replication
        ```

        ## Baseline

        4002A affine residuals after the 4001 translation plus global affine subtraction.

        ## Null model

        4002A shifted-event nulls are inherited here only for metric selection. 4073 must still formalize which nulls are used in future tests.

        ## Primary metrics

        {md_table(sorted(primary, key=lambda x: int(x["primary_rank"])), ["primary_rank", "variable", "taxonomy_class", "family", "real_abs_median_direction_contrast_z", "direction_contrast_sign_consistency", "reason"])}

        ## Secondary diagnostics

        {md_table(secondary, ["variable", "taxonomy_class", "family", "real_abs_median_direction_contrast_z", "direction_survives_gate", "reason"])}

        ## Retired or negative controls

        {md_table(retired, ["variable", "taxonomy_class", "family", "real_abs_median_direction_contrast_z", "direction_survives_gate", "reason"])}

        ## Dataset-wise replication

        Not run in 4072. These metric roles must be used unchanged in 4071.

        ## Gate evaluation

        `{gate_result}`: primary={len(primary)}, secondary={len(secondary)}, retired={len(retired)}.

        ## What this rules out

        The next branch should not use global residual polarization/order as a primary target, and should not add individual-distribution tail metrics from 4020/4020B unless a new node explicitly reopens that route.

        ## What this does NOT prove

        4072 does not prove robustness, local non-affinity, stochasticity, propagation, or network mechanism. It only freezes observables.

        ## Decision

        `{gate_result}`: proceed to 4073 null/baseline registry.

        ## Next node

        `4073_null_and_baseline_registry`
        """
    )
    (OUT / "4072_summary.md").write_text(text, encoding="utf-8")


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Missing source table: {SOURCE}")
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    rows = read_source()
    records = [classify(row) for row in rows]

    records.sort(
        key=lambda r: (
            {"primary_target": 0, "secondary_diagnostic": 1, "retired_or_negative_control": 2}.get(r["role"], 9),
            int(r["primary_rank"]) if r["primary_rank"] else 99,
            -as_float(r["real_abs_median_direction_contrast_z"]),
        )
    )

    primary = [r for r in records if r["role"] == "primary_target"]
    secondary = [r for r in records if r["role"] == "secondary_diagnostic"]
    retired = [r for r in records if r["role"] == "retired_or_negative_control"]

    write_config()
    write_csv(OUT / "residual_observable_taxonomy.csv", records)
    write_csv(OUT / "tables" / "residual_observable_taxonomy.csv", records)
    write_csv(OUT / "primary_metrics.csv", primary)
    write_csv(OUT / "secondary_diagnostics.csv", secondary)
    write_csv(OUT / "retired_metrics.csv", retired)
    write_json(OUT / "residual_observable_taxonomy.json", records)
    write_summary(records)
    print(f"Wrote 4072 taxonomy outputs to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
