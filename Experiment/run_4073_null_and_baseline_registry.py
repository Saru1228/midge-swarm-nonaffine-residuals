"""4073 null and baseline registry.

This synthesis node freezes the baseline/null vocabulary used by 4071, 4074,
and the later 408x-411x branches. It does not reprocess trajectories.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4073"

NODE = "4073_null_and_baseline_registry"
DATE = "2026-08-25"


BASELINE_COLUMNS = [
    "baseline_id",
    "name",
    "class",
    "definition",
    "preserves",
    "removes_or_controls",
    "primary_use",
    "allowed_future_nodes",
    "status",
]


NULL_COLUMNS = [
    "null_id",
    "name",
    "class",
    "definition",
    "preserves",
    "destroys",
    "primary_use",
    "allowed_future_nodes",
    "status",
]


NODE_COLUMNS = [
    "future_node",
    "required_primary_metrics",
    "required_baselines",
    "required_nulls_or_controls",
    "forbidden_shortcut",
    "entry_condition",
]


BASELINES = [
    {
        "baseline_id": "B0",
        "name": "identity_measurement_audit",
        "class": "artifact_control",
        "definition": "Track dropout, membership change, finite-N averaging, velocity-estimation sensitivity, and frame-rate sensitivity checks.",
        "preserves": "Raw measurement process and trajectory identity metadata.",
        "removes_or_controls": "Measurement and preprocessing artifacts before interpreting residual organization.",
        "primary_use": "Required diagnostic layer before strong mechanism claims.",
        "allowed_future_nodes": "4074,4080,4081,4090,4100,4110",
        "status": "registered_required_artifact_layer",
    },
    {
        "baseline_id": "B1",
        "name": "translation",
        "class": "geometric_baseline",
        "definition": "Subtract swarm-level center-of-mass/common translational velocity.",
        "preserves": "Relative motion, rotation, strain, shear, local deformation, and residual individual differences.",
        "removes_or_controls": "Global common motion.",
        "primary_use": "First rung of 4081 geometry ladder.",
        "allowed_future_nodes": "4081",
        "status": "registered",
    },
    {
        "baseline_id": "B2",
        "name": "global_rigid",
        "class": "geometric_baseline",
        "definition": "Subtract translation plus best global rigid rotation.",
        "preserves": "Global strain/shear, local deformation, non-affine motion, and stochastic residuals.",
        "removes_or_controls": "Common motion plus rigid-body rotation.",
        "primary_use": "Second rung of 4081 geometry ladder.",
        "allowed_future_nodes": "4081",
        "status": "registered",
    },
    {
        "baseline_id": "B3",
        "name": "global_affine",
        "class": "geometric_baseline",
        "definition": "Subtract translation plus global affine deformation, including rotation, strain, stretching, and shear.",
        "preserves": "Spatially heterogeneous local affine deformation, local non-affine motion, stochastic residuals, and graph/network structure.",
        "removes_or_controls": "Ordinary global non-rigid group geometry.",
        "primary_use": "Current 4001/4002A baseline and 4071 replication baseline.",
        "allowed_future_nodes": "4071,4074,4081,4090",
        "status": "registered_current_target_baseline",
    },
    {
        "baseline_id": "B4",
        "name": "local_affine",
        "class": "geometric_baseline",
        "definition": "For each focal individual and neighbor scale, fit a local affine deformation tensor before computing residual/non-affine motion.",
        "preserves": "Local non-affine rearrangement, state-dependent stochasticity, transient propagation, and network-level residual structure.",
        "removes_or_controls": "Spatially heterogeneous but locally affine deformation.",
        "primary_use": "4080 feasibility and 4081 major geometry-irreducibility gate.",
        "allowed_future_nodes": "4080,4081,4082,4083,4084,4090,4100,4110",
        "status": "registered_not_yet_computed",
    },
]


NULLS = [
    {
        "null_id": "N1",
        "name": "time_shift_or_shifted_event",
        "class": "temporal_null",
        "definition": "Shift event labels or comparison windows in time while preserving within-observation trajectories and individual-level statistics.",
        "preserves": "Individual trajectories, smooth temporal structure, approximate observation-level distributions.",
        "destroys": "Event-locked synchrony between target residual metrics and compact-density transitions.",
        "primary_use": "4071 replication of 4001/4002A style event-conditioned residual signals.",
        "allowed_future_nodes": "4071,4074,4081,4090,4101,405x-style graph controls",
        "status": "registered_current_primary_event_null",
    },
    {
        "null_id": "N2",
        "name": "phase_or_spectrum_preserving_temporal_null",
        "class": "temporal_smooth_null",
        "definition": "Preserve autocorrelation/spectrum or smooth rank structure while disrupting cross-individual or event-specific organization.",
        "preserves": "Smooth temporal autocorrelation and broad spectrum of a metric.",
        "destroys": "Specific cross-individual or event-aligned organization beyond smooth time-series structure.",
        "primary_use": "Guard against smooth time-series artifacts in 4074, 4090, and 4101.",
        "allowed_future_nodes": "4074,4090,4101,4104",
        "status": "registered_required_for_smooth_time_series_claims",
    },
    {
        "null_id": "N3",
        "name": "identity_permutation",
        "class": "identity_history_null",
        "definition": "Preserve frame-level geometry while permuting identity/history labels within valid constraints.",
        "preserves": "Frame geometry, density, radial positions, and instantaneous spatial configuration.",
        "destroys": "Individual identity continuity and history-dependent coupling.",
        "primary_use": "Membership/history artifact control and graph-history checks.",
        "allowed_future_nodes": "4074,4110,4111,4112",
        "status": "registered",
    },
    {
        "null_id": "N4",
        "name": "neighbor_or_geometry_matched_null",
        "class": "geometry_matched_null",
        "definition": "Preserve local distance, density, radial position, and core-edge composition as much as possible while disrupting residual coupling.",
        "preserves": "Geometry, density, radial/core-edge structure, and approximate neighbor context.",
        "destroys": "Residual coupling beyond geometry-matched context.",
        "primary_use": "Required for core/edge, density, local-affine, and graph claims.",
        "allowed_future_nodes": "4081,4084,4092,4110,4114",
        "status": "registered_required_for_geometry_sensitive_claims",
    },
    {
        "null_id": "N5",
        "name": "matched_non_event_window",
        "class": "sampling_window_control",
        "definition": "Sample non-event windows matched on observation, window length, N, radial/density context, and available track coverage.",
        "preserves": "Observation context, measurement availability, and broad geometry/density composition.",
        "destroys": "Selection of the original compact-density transition event labels.",
        "primary_use": "4074 event-free versus event-conditioned audit.",
        "allowed_future_nodes": "4074,4101",
        "status": "registered_for_event_selection_control",
    },
]


FUTURE_NODE_RULES = [
    {
        "future_node": "4071_cross_dataset_baseline_audit",
        "required_primary_metrics": "4072 primary metrics only",
        "required_baselines": "B3",
        "required_nulls_or_controls": "N1; report dataset-wise effects and sign consistency",
        "forbidden_shortcut": "Do not add or replace primary metrics after seeing Ob2/Ob3.",
        "entry_condition": "4072 and 4073 completed.",
    },
    {
        "future_node": "4074_event_free_vs_event_conditioned_audit",
        "required_primary_metrics": "4072 primary metrics; secondary diagnostics only as context",
        "required_baselines": "B0,B3",
        "required_nulls_or_controls": "N1,N2,N5",
        "forbidden_shortcut": "Do not define events using the same downstream propagation metric.",
        "entry_condition": "4071 completed or explicitly skipped for a documented reason.",
    },
    {
        "future_node": "4080_local_affine_feasibility",
        "required_primary_metrics": "not metric-driven; fit-quality diagnostics first",
        "required_baselines": "B4 feasibility only",
        "required_nulls_or_controls": "condition-number and neighbor-turnover diagnostics",
        "forbidden_shortcut": "Do not interpret D2min if local affine fits are numerically unstable.",
        "entry_condition": "4072/4073 completed; 4071 does not collapse the target.",
    },
    {
        "future_node": "4081_global_vs_local_geometry_ladder",
        "required_primary_metrics": "4072 primary metrics",
        "required_baselines": "B1,B2,B3,B4",
        "required_nulls_or_controls": "N4 geometry-matched null if claiming non-affine residual beyond local geometry",
        "forbidden_shortcut": "Do not claim non-affinity from B3 residual alone.",
        "entry_condition": "4080 feasibility pass.",
    },
    {
        "future_node": "4090_conditional_mean_vs_variance",
        "required_primary_metrics": "4072 metrics or 408x local-nonaffine metric if Route A survives",
        "required_baselines": "B3 or B4, depending on Route A result",
        "required_nulls_or_controls": "N1,N2,N4; out-of-sample mean-vs-variance comparison",
        "forbidden_shortcut": "Do not treat correlation or in-sample fit gain as force/mechanism.",
        "entry_condition": "M1 review says residual survives the relevant geometry baseline.",
    },
    {
        "future_node": "410x_transient_propagation",
        "required_primary_metrics": "Frozen residual/non-affine activity metric",
        "required_baselines": "B3 or B4",
        "required_nulls_or_controls": "N1,N2,N5; matched non-burst windows",
        "forbidden_shortcut": "Do not call lagged correlation a wave without stable lag-distance structure and replication.",
        "entry_condition": "Frozen burst/activity definition from 4072 or 408x.",
    },
    {
        "future_node": "411x_network_organization",
        "required_primary_metrics": "Frozen residual/non-affine activity metric",
        "required_baselines": "B0,B3 or B4",
        "required_nulls_or_controls": "N3,N4 plus degree/geometry preserving graph controls",
        "forbidden_shortcut": "Do not infer biological interaction from a single graph edge or metric.",
        "entry_condition": "4072/4073 completed and target residual variable frozen; preferably after Route A.",
    },
]


def write_csv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
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
        node_type: foundation_null_baseline_freeze
        parent_node: 4072_residual_observable_taxonomy
        no_trajectory_reprocessing: true
        next_node: 4071_cross_dataset_baseline_audit
        registry_items:
          baselines: {len(BASELINES)}
          nulls: {len(NULLS)}
          future_node_rules: {len(FUTURE_NODE_RULES)}
        """
    )
    (OUT / "config.yaml").write_text(text, encoding="utf-8")


def write_summary() -> None:
    decision = {
        "node": NODE,
        "question": "Which baselines and nulls are allowed for each future 407x-411x branch?",
        "result": "pass",
        "baseline_ids": [b["baseline_id"] for b in BASELINES],
        "null_ids": [n["null_id"] for n in NULLS],
        "future_node_rules": [r["future_node"] for r in FUTURE_NODE_RULES],
        "gate": "Registry must define what each baseline/null preserves and destroys, and must map future nodes to allowed controls.",
        "gate_evaluation": f"baselines={len(BASELINES)}, nulls={len(NULLS)}, future_node_rules={len(FUTURE_NODE_RULES)}",
        "interpretation": "Future replication and mechanism tests now have a frozen baseline/null vocabulary.",
        "next": ["4071_cross_dataset_baseline_audit"],
    }
    write_json(OUT / "decision.json", decision)

    text = dedent(
        f"""\
        # Node 4073 Summary

        ## Question

        Which baseline and null models are allowed for each future node, what does each preserve, and what does each destroy?

        ## Why this node exists

        4072 froze the primary residual metrics. 4073 freezes the baseline/null vocabulary so that 4071 replication and 408x local-affine tests do not change controls after seeing results.

        ## Data

        No raw trajectories were reprocessed. This is a registry/synthesis node derived from the 4070-4072 roadmap and completed 4xxx evidence.

        ## Frozen parameters

        Baselines:

        {md_table(BASELINES, ["baseline_id", "name", "class", "primary_use", "status"])}

        Nulls and controls:

        {md_table(NULLS, ["null_id", "name", "class", "primary_use", "status"])}

        ## Baseline

        The current target baseline remains `B3_global_affine`. Route A must explicitly compare `B1 -> B2 -> B3 -> B4`.

        ## Null model

        The current replication null is `N1_time_shift_or_shifted_event`. Smooth temporal and geometry-sensitive claims require `N2` and/or `N4`.

        ## Primary metrics

        Use only the 4072 primary metrics in 4071:

        ```text
        resid_velocity_cov_trace
        resid_speed_rms
        resid_tangential_speed_mean
        resid_radial_abs_mean
        edge_minus_core_resid_speed
        edge_minus_core_resid_tangential
        ```

        ## Results

        Future-node registry:

        {md_table(FUTURE_NODE_RULES, NODE_COLUMNS)}

        ## Dataset-wise replication

        Not run in 4073. Replication starts in 4071 using 4072 metrics and this registry.

        ## Gate evaluation

        `pass`: baselines={len(BASELINES)}, nulls={len(NULLS)}, future-node rules={len(FUTURE_NODE_RULES)}.

        ## What this rules out

        4071 cannot add new primary metrics, and 4081 cannot claim non-affinity from the global-affine residual alone. Graph or stochastic claims must use geometry-sensitive controls when relevant.

        ## What this does NOT prove

        4073 does not prove residual robustness or any mechanism. It only freezes controls.

        ## Decision

        `pass`: proceed to 4071 cross-dataset baseline audit.

        ## Next node

        `4071_cross_dataset_baseline_audit`
        """
    )
    (OUT / "4073_summary.md").write_text(text, encoding="utf-8")


def main() -> None:
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    write_config()
    write_csv(OUT / "baseline_registry.csv", BASELINES, BASELINE_COLUMNS)
    write_csv(OUT / "null_registry.csv", NULLS, NULL_COLUMNS)
    write_csv(OUT / "future_node_control_rules.csv", FUTURE_NODE_RULES, NODE_COLUMNS)
    write_csv(OUT / "tables" / "baseline_registry.csv", BASELINES, BASELINE_COLUMNS)
    write_csv(OUT / "tables" / "null_registry.csv", NULLS, NULL_COLUMNS)
    write_csv(OUT / "tables" / "future_node_control_rules.csv", FUTURE_NODE_RULES, NODE_COLUMNS)
    write_json(OUT / "baseline_registry.json", BASELINES)
    write_json(OUT / "null_registry.json", NULLS)
    write_json(OUT / "future_node_control_rules.json", FUTURE_NODE_RULES)
    write_summary()
    print(f"Wrote 4073 registry outputs to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
