"""4130 definition and evidence registry for the 413x synthesis route.

This node does not run a new mechanism experiment. It normalizes completed
408x-412x evidence into machine-readable registries for later atlas, figure,
and manuscript work.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from textwrap import dedent

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4130"
DATE = "2026-08-27"
NODE = "4130_definition_and_evidence_registry"


CLAIM_CLASSES = {
    "SUPPORTED",
    "SUPPORTED_WITH_BOUNDARY",
    "NOT_SUPPORTED",
    "BOUNDARY",
    "TECHNICAL_PASS",
    "TECHNICAL_STOP",
    "NOT_TESTED",
}


SOURCE_NODES = [
    "4001",
    "4080",
    "4081",
    "4081c",
    "4081d",
    "4082",
    "4082b",
    "4083",
    "4084",
    "4085",
    "4085b",
    "4086",
    "4087",
    "4088",
    "4090A",
    "4090B",
    "4090",
    "4094",
    "4100A",
    "4100",
    "4105",
    "4120",
    "4121",
    "4125",
]


def ensure_dirs() -> None:
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    (OUT / "figures").mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def write_csv_pair(df: pd.DataFrame, name: str) -> None:
    df.to_csv(OUT / name, index=False)
    df.to_csv(OUT / "tables" / name, index=False)


def md_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in rows:
        vals: list[str] = []
        for col in columns:
            val = row.get(col, "")
            if isinstance(val, (float, np.floating)):
                vals.append("NA" if not math.isfinite(float(val)) else f"{float(val):.4g}")
            else:
                vals.append(str(val).replace("\n", " ").replace("|", "\\|"))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def build_source_map() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for node in SOURCE_NODES:
        out_dir = ROOT / "Output" / node
        decision = out_dir / "decision.json"
        summary = out_dir / f"{node}_summary.md"
        if node == "4001":
            summary = out_dir / "4001_summary.md"
        rows.append(
            {
                "node": node,
                "output_dir": rel(out_dir),
                "decision_json": rel(decision),
                "decision_exists": decision.exists(),
                "summary_md": rel(summary),
                "summary_exists": summary.exists(),
                "provenance_level": "decision_json" if decision.exists() else "summary_only" if summary.exists() else "missing",
            }
        )
    return pd.DataFrame(rows)


def build_definition_dictionary() -> pd.DataFrame:
    rows = [
        {
            "term": "T1",
            "canonical_definition": "transition-linked local tangential non-affine residual after local affine deformation is removed",
            "source_node": "4088",
            "source_file": "Output/4088/decision.json",
            "unit_of_analysis": "frame/observation depending on downstream node",
            "aggregation_level": "local focal-neighborhood to swarm/observation aggregate",
            "allowed_aliases": "local non-affine tangential residual; local tangential non-affine activity",
            "incompatible_aliases": "raw speed; global affine residual speed; individual causal velocity",
            "notes": "Use as the frozen phenomenon object, not as a unique individual-level force.",
        },
        {
            "term": "A_swarm_tangential_z",
            "canonical_definition": "swarm-level frame aggregate of focal-centered local non-affine tangential activity from 4100A",
            "source_node": "4100A",
            "source_file": "Output/4100A/swarm_activity_frame.csv",
            "unit_of_analysis": "frame",
            "aggregation_level": "swarm aggregate",
            "allowed_aliases": "T1 activity frame aggregate; focal aggregate A_i(t) summarized to swarm frame",
            "incompatible_aliases": "raw overlapping neighbor residual vector; unique individual residual velocity",
            "notes": "Primary activity column for 4100 and 412x.",
        },
        {
            "term": "all_tangential",
            "canonical_definition": "diffuse local tangential non-affine activity diagnostic used in 4084/4085 spatial-timing characterization",
            "source_node": "4084",
            "source_file": "Output/4084/decision.json",
            "unit_of_analysis": "observation/condition",
            "aggregation_level": "spatially diffuse local activity",
            "allowed_aliases": "diffuse tangential activity",
            "incompatible_aliases": "shell_edge_minus_core direct contrast; event-local matched activity",
            "notes": "Use as a spatial/timing diagnostic, not as a separate new target.",
        },
        {
            "term": "shell_edge_minus_core",
            "canonical_definition": "edge-minus-core direct contrast in local tangential non-affine activity",
            "source_node": "4084",
            "source_file": "Output/4084/decision.json",
            "unit_of_analysis": "observation/condition",
            "aggregation_level": "spatial contrast",
            "allowed_aliases": "edge/core contrast",
            "incompatible_aliases": "diffuse all_tangential baseline",
            "notes": "Secondary bounded spatial contrast; not a universal phase-localized trigger.",
        },
        {
            "term": "C",
            "canonical_definition": "density_rms_z3045 compact-density state coordinate",
            "source_node": "4090B/4120",
            "source_file": "Output/4120/state_path_frame.csv",
            "unit_of_analysis": "frame",
            "aggregation_level": "swarm state",
            "allowed_aliases": "density_rms_z3045",
            "incompatible_aliases": "raw density without 3045 normalization",
            "notes": "Used in current-state matching and moment closure tests.",
        },
        {
            "term": "dCdt",
            "canonical_definition": "time gradient of density_rms_smooth3045",
            "source_node": "4090B/4120",
            "source_file": "Output/4120/state_path_frame.csv",
            "unit_of_analysis": "frame",
            "aggregation_level": "swarm state velocity",
            "allowed_aliases": "gradient(density_rms_smooth3045,t)",
            "incompatible_aliases": "finite difference of raw noisy C without smoothing",
            "notes": "Important leakage control variable for 412x.",
        },
        {
            "term": "R",
            "canonical_definition": "r_rms_z3045 compact-radius coordinate",
            "source_node": "4090B/4120",
            "source_file": "Output/4120/state_path_frame.csv",
            "unit_of_analysis": "frame",
            "aggregation_level": "swarm state",
            "allowed_aliases": "radius; r_rms_z3045 when normalized by 3045 convention",
            "incompatible_aliases": "focal_radius in vector-sample 4090 without noting unit change",
            "notes": "Used in 4100/412x state matching; 4090 used focal_radius in vector-level samples.",
        },
        {
            "term": "h500_theta_h",
            "canonical_definition": "recent C-R path direction over h=0.50 sec, atan2(DeltaR_h, DeltaC_h)",
            "source_node": "4120",
            "source_file": "Output/4120/state_path_frame.csv",
            "unit_of_analysis": "frame",
            "aggregation_level": "state-path feature",
            "allowed_aliases": "theta_h at 0.50 sec; recent path direction",
            "incompatible_aliases": "theta_v instantaneous direction; turning_proxy",
            "notes": "Primary history feature in 4121.",
        },
        {
            "term": "event-local near-pre activity",
            "canonical_definition": "near-pre [-0.25,0.00] sec median A_swarm_tangential_z around transition timestamps",
            "source_node": "4100",
            "source_file": "Output/4100/decision.json",
            "unit_of_analysis": "event",
            "aggregation_level": "state-matched event/control comparison",
            "allowed_aliases": "event_A_pre_z; A_pre_z",
            "incompatible_aliases": "unmatched event average; propagation source signal",
            "notes": "Failed to exceed state-matched non-event controls in 4100.",
        },
        {
            "term": "observation-level effect strength",
            "canonical_definition": "per-observation median or robust summary of node-specific T1 effect",
            "source_node": "4088/4125",
            "source_file": "Output/4125/decision.json",
            "unit_of_analysis": "observation",
            "aggregation_level": "observation summary",
            "allowed_aliases": "ob-level effect; dataset-level effect",
            "incompatible_aliases": "pooled frame-level significance without observation grouping",
            "notes": "Must preserve observation heterogeneity in 413x.",
        },
    ]
    return pd.DataFrame(rows)


def evidence_rows_from_decisions() -> list[dict[str, object]]:
    # Rows are explicit by design: 4130 is a registry, not a text-mining task.
    return [
        {
            "node": "4001",
            "question": "Does the velocity event signal survive a global affine geometric baseline?",
            "target": "3045c velocity event signal",
            "data_scope": "all_19_observations",
            "baseline": "per-frame translation plus affine deformation",
            "null": "circularly shifted event times",
            "primary_metric": "4/4 raw direction survivors retained in affine_resid; median affine_resid/raw abs ratio 0.9554",
            "gate": "affine_resid_direction_survivors retained beyond shifted-event null",
            "result": "support_extra_affine_residual_velocity_coordination",
            "claim_class": "SUPPORTED_WITH_BOUNDARY",
            "robustness": "summary_only provenance; 19 observations, 1471 events",
            "supported_claim": "Velocity event signal is not fully explained by whole-swarm affine geometry.",
            "unsupported_claim": "local T1 mechanism, causal coordination law, or individual interaction mechanism",
            "next_route_meaning": "opens local/non-affine residual route",
            "main_artifact": "Output/4001/4001_summary.md",
            "figure_candidate": "yes",
        },
        {
            "node": "4080",
            "question": "Can local affine residualization be computed for the dataset?",
            "target": "local tangential non-affine residual candidate",
            "data_scope": "all_19_observations",
            "baseline": "local affine fit",
            "null": "technical feasibility/QC",
            "primary_metric": "decision.json gate result",
            "gate": "local affine computation feasible",
            "result": "technical local-affine feasibility",
            "claim_class": "TECHNICAL_PASS",
            "robustness": "technical gate",
            "supported_claim": "Local affine subtraction is technically available for downstream tests.",
            "unsupported_claim": "T1 biological mechanism",
            "next_route_meaning": "enter 4081/4081c survival tests",
            "main_artifact": "Output/4080/4080_summary.md",
            "figure_candidate": "supplement",
        },
        {
            "node": "4081",
            "question": "In the Ob1 pilot, does the local affine geometry ladder preserve or absorb the candidate T1 signal?",
            "target": "local tangential non-affine residual pilot",
            "data_scope": "Ob1 pilot",
            "baseline": "global-vs-local geometry ladder",
            "null": "pilot gate only",
            "primary_metric": "t1_local_gate_any false in Ob1 pilot",
            "gate": "pilot local geometry survival",
            "result": "boundary_t1_absorbed_or_not_event_conditioned",
            "claim_class": "BOUNDARY",
            "robustness": "single-observation pilot; superseded by 4081c all-19 adjudication",
            "supported_claim": "Ob1 is a boundary case in the local-affine ladder.",
            "unsupported_claim": "all observations absorb T1 under local affine subtraction",
            "next_route_meaning": "requires all-19 adjudication before route decision",
            "main_artifact": "Output/4081/decision.json",
            "figure_candidate": "supplement",
        },
        {
            "node": "4081c",
            "question": "Across all 19 observations, does T1 survive local affine subtraction?",
            "target": "T1 local tangential non-affine residual",
            "data_scope": "all_19_observations",
            "baseline": "local affine residualization at original k values",
            "null": "event-conditioned local-affine comparison gates",
            "primary_metric": "15/19 pass at least one k; 14/19 pass both original k",
            "gate": "observation-level survival class",
            "result": "support_observation_heterogeneous_but_common_t1_survival",
            "claim_class": "SUPPORTED_WITH_BOUNDARY",
            "robustness": "explicit failures Ob1/Ob3/Ob6/Ob8",
            "supported_claim": "T1 survival is common across observations but not universal.",
            "unsupported_claim": "universal all-observation law",
            "next_route_meaning": "test robustness on survivor class",
            "main_artifact": "Output/4081c/4081c_summary.md",
            "figure_candidate": "yes",
        },
        {
            "node": "4081d",
            "question": "Can the all-19 local-affine survival pattern be summarized as common T1 survival with an early-observation boundary?",
            "target": "observation-level T1 survival heterogeneity",
            "data_scope": "all_19_observations",
            "baseline": "4081c all-19 adjudication",
            "null": "rough failure-concentration and feature contrasts",
            "primary_metric": "15/19 survive any k; 14/19 survive both k; failures Ob1/Ob3/Ob6/Ob8",
            "gate": "heterogeneity interpretation before robustness",
            "result": "support_common_t1_survival_with_early_observation_boundary",
            "claim_class": "SUPPORTED_WITH_BOUNDARY",
            "robustness": "early-observation proxy remains unconfirmed",
            "supported_claim": "T1 survival is common, with explicit observation heterogeneity.",
            "unsupported_claim": "confirmed recording-order artifact or universal all-observation survival",
            "next_route_meaning": "enter 4082 and 4082b",
            "main_artifact": "Output/4081d/decision.json",
            "figure_candidate": "supplement",
        },
        {
            "node": "4082",
            "question": "Is T1 survival robust to nearby local scale and lag choices?",
            "target": "4081c T1 survivor observations",
            "data_scope": "15 survivor observations",
            "baseline": "nearby k and lag grid",
            "null": "predefined scale/timing robustness gate",
            "primary_metric": "14/15 robust scale and timing; median pass fractions 1.0",
            "gate": "scale and lag robustness in survivor class",
            "result": "support_scale_timing_robust_t1_survival_with_boundary_cases",
            "claim_class": "SUPPORTED_WITH_BOUNDARY",
            "robustness": "survivor-class robustness; not all-19 primary",
            "supported_claim": "Within the survivor class, T1 is robust to nearby k and lag choices.",
            "unsupported_claim": "survivor-only universal statement",
            "next_route_meaning": "audit failure boundary",
            "main_artifact": "Output/4082/4082_summary.md",
            "figure_candidate": "yes",
        },
        {
            "node": "4082b",
            "question": "Are early failures explained by simple quality or event-count covariates?",
            "target": "4081c failure/boundary observations",
            "data_scope": "failure/boundary observations plus available covariates",
            "baseline": "raw quality/event-count checks",
            "null": "descriptive artifact audit",
            "primary_metric": "no strong raw-quality or event-structure explanation",
            "gate": "artifact explanation sufficient or not",
            "result": "boundary_early_failure_not_explained_by_basic_quality_or_event_counts",
            "claim_class": "BOUNDARY",
            "robustness": "basic covariates only",
            "supported_claim": "The failure boundary is not explained by the audited simple quality/event covariates.",
            "unsupported_claim": "confirmed batch effect or confirmed biological regime",
            "next_route_meaning": "keep explicit failure boundary",
            "main_artifact": "Output/4082b/4082b_summary.md",
            "figure_candidate": "supplement",
        },
        {
            "node": "4083",
            "question": "Should the route jump to 409x/410x or deepen 408x after initial synthesis?",
            "target": "408x route state",
            "data_scope": "4081c/4082 evidence",
            "baseline": "route reset and bounded synthesis",
            "null": "not a mechanism test",
            "primary_metric": "bounded 408x claim retained; unresolved spatial/timing/signed questions",
            "gate": "route reset",
            "result": "continue_deeper_408x_not_409x_410x_yet",
            "claim_class": "BOUNDARY",
            "robustness": "planning/synthesis node",
            "supported_claim": "408x needed spatial, timing, signed, and failure-boundary characterization before 409x/410x.",
            "unsupported_claim": "408x was complete before spatial/timing characterization",
            "next_route_meaning": "enter 4084",
            "main_artifact": "Output/4083/decision.json",
            "figure_candidate": "no",
        },
        {
            "node": "4084",
            "question": "Where spatially does the T1 local non-affine signal live?",
            "target": "T1 spatial decomposition",
            "data_scope": "14 robust survivor observations",
            "baseline": "spatial shell/density decompositions",
            "null": "replicated variable gate",
            "primary_metric": "all_tangential passes 13/14; shell_edge_minus_core passes 9/14",
            "gate": "majority replicated spatial candidate",
            "result": "support_replicated_edge_core_spatial_contrast_with_boundaries",
            "claim_class": "SUPPORTED_WITH_BOUNDARY",
            "robustness": "diffuse signal stronger than direct edge/core contrast",
            "supported_claim": "Diffuse tangential activity is strongest; edge/core contrast is bounded and secondary.",
            "unsupported_claim": "stable edge trigger or full spatial taxonomy",
            "next_route_meaning": "ask timing of spatial signal",
            "main_artifact": "Output/4084/4084_summary.md",
            "figure_candidate": "yes",
        },
        {
            "node": "4085",
            "question": "When does the T1 spatial/tangential signal appear around transitions?",
            "target": "T1 event-phase profile",
            "data_scope": "robust survivor observations",
            "baseline": "phase windows around transitions",
            "null": "phase-profile gate",
            "primary_metric": "diffuse all_tangential near-pre majority; edge/core lacks stable majority phase",
            "gate": "phase majority and robustness",
            "result": "boundary_edge_core_no_stable_phase_but_diffuse_t1_has_phase_profile",
            "claim_class": "SUPPORTED_WITH_BOUNDARY",
            "robustness": "timing clearer for diffuse activity than edge/core contrast",
            "supported_claim": "The clearest timing view is diffuse near-pre local tangential non-affinity.",
            "unsupported_claim": "single edge/core phase-localized trigger",
            "next_route_meaning": "test signed transition direction heterogeneity",
            "main_artifact": "Output/4085/4085_summary.md",
            "figure_candidate": "yes",
        },
        {
            "node": "4085b",
            "question": "What does the 4085/4086 signal look like in compactness-T1 phase-space projection?",
            "target": "diagnostic phase-space projection of T1",
            "data_scope": "408x diagnostic samples",
            "baseline": "visual/metric projection",
            "null": "diagnostic only; not attractor evidence",
            "primary_metric": "projection supports signed diffuse near-pre separation",
            "gate": "diagnostic visualization, no confirmatory mechanism gate",
            "result": "diagnostic_phase_space_supports_signed_diffuse_near_pre_separation",
            "claim_class": "BOUNDARY",
            "robustness": "diagnostic projection only",
            "supported_claim": "Phase-space projection is useful for visualization of signed diffuse separation.",
            "unsupported_claim": "attractor, limit cycle, or basin transition evidence",
            "next_route_meaning": "route to 4087/4088 synthesis",
            "main_artifact": "Output/4085b/decision.json",
            "figure_candidate": "supplement",
        },
        {
            "node": "4086",
            "question": "Is the near-pre diffuse T1 profile mirrored or one-direction dominated?",
            "target": "signed low-to-high/high-to-low T1 structure",
            "data_scope": "robust survivor observations",
            "baseline": "signed transition direction decomposition",
            "null": "signed gate",
            "primary_metric": "6/14 mirror, 3/14 low-to-high dominant, 4/14 no signed gate",
            "gate": "signed consistency",
            "result": "boundary_signed_direction_heterogeneous_across_observations",
            "claim_class": "BOUNDARY",
            "robustness": "signed structure exists but heterogeneous",
            "supported_claim": "Signed event-type structure is heterogeneous across observations.",
            "unsupported_claim": "universal signed force or mirror law",
            "next_route_meaning": "synthesize bounded 408x result",
            "main_artifact": "Output/4086/4086_summary.md",
            "figure_candidate": "supplement",
        },
        {
            "node": "4087",
            "question": "Do the non-survival observations remain failures under predefined sensitivity checks?",
            "target": "Ob1/Ob3/Ob6/Ob8 failure boundary",
            "data_scope": "4 non-survival observations",
            "baseline": "predefined sensitivity families",
            "null": "definition/window artifact audit",
            "primary_metric": "Ob1/Ob3 fragile boundary cases; Ob6/Ob8 stable failures",
            "gate": "robust rescue or stable failure",
            "result": "boundary_failure_group_mostly_stable_with_fragile_rescues",
            "claim_class": "BOUNDARY",
            "robustness": "explicit failure and fragile-rescue classes",
            "supported_claim": "The failure boundary is explicit but not perfectly sharp.",
            "unsupported_claim": "all failures are artifacts or all can be merged into survivor class",
            "next_route_meaning": "enter 4088 synthesis",
            "main_artifact": "Output/4087/4087_summary.md",
            "figure_candidate": "yes",
        },
        {
            "node": "4088",
            "question": "What bounded Route A claim remains after 4080-4087?",
            "target": "T1 local tangential non-affine residual",
            "data_scope": "all_19_observations with survivor/failure classes",
            "baseline": "local affine geometry and route-specific gates",
            "null": "synthesis of 408x nulls/gates",
            "primary_metric": "bounded claim with robust survivors and explicit failures",
            "gate": "synthesis claim strength",
            "result": "bounded_local_nonaffine_tangential_signal_with_explicit_failure_boundary",
            "claim_class": "SUPPORTED_WITH_BOUNDARY",
            "robustness": "14/15 survivor robustness; Ob1/Ob3 fragile, Ob6/Ob8 stable failures",
            "supported_claim": "Most observations contain a transition-linked local non-affine tangential residual.",
            "unsupported_claim": "causal trigger, propagation, attractor, universal law",
            "next_route_meaning": "freeze T1 and test reductions",
            "main_artifact": "Output/4088/decision.json",
            "figure_candidate": "yes",
        },
        {
            "node": "4090A",
            "question": "Does T1 strength mainly track observation regime, raw/event quality, or known metadata?",
            "target": "observation-level T1 strength",
            "data_scope": "all_19_observations",
            "baseline": "known raw/event covariates",
            "null": "observation-regime boundary audit",
            "primary_metric": "early-observation proxy noted; no confirmed raw/event covariate",
            "gate": "artifact/regime stop or proceed",
            "result": "R1_unconfirmed_observation_sequence_proxy",
            "claim_class": "BOUNDARY",
            "robustness": "metadata incomplete",
            "supported_claim": "Observation identity and early-observation proxy remain explicit boundaries.",
            "unsupported_claim": "confirmed batch artifact or causal metadata explanation",
            "next_route_meaning": "proceed with grouped validation and heterogeneity caution",
            "main_artifact": "Output/4090A/4090A_summary.md",
            "figure_candidate": "supplement",
        },
        {
            "node": "4090B",
            "question": "Are vector-level residual samples and continuous compact-density state available?",
            "target": "T1 vector samples and C,dCdt state",
            "data_scope": "all_19_observations",
            "baseline": "technical feasibility",
            "null": "availability/QC",
            "primary_metric": "vector samples and C,dCdt available; residual unit boundary recorded",
            "gate": "technical feasibility",
            "result": "B1_vector_available_with_unit_boundary_and_C_available",
            "claim_class": "TECHNICAL_PASS",
            "robustness": "unit boundary: focal-neighborhood neighbor residual vector",
            "supported_claim": "4090 can test current-state moment closure with explicit residual-unit caveat.",
            "unsupported_claim": "unique focal-individual residual vector",
            "next_route_meaning": "enter 4090",
            "main_artifact": "Output/4090B/4090B_summary.md",
            "figure_candidate": "no",
        },
        {
            "node": "4090",
            "question": "Does C,dCdt,R organize T1 as first or second moment structure?",
            "target": "signed_tan_projection and log_tan_energy",
            "data_scope": "all_19_observations",
            "baseline": "radius-only binned model",
            "null": "within-observation circular shift of C,dCdt",
            "primary_metric": "first moment median incremental R2 -0.00063; second moment -0.00062",
            "gate": "grouped OOS improvement and shifted-state separation",
            "result": "transition_linked_but_not_lowdimensional_state_conditioned",
            "claim_class": "NOT_SUPPORTED",
            "robustness": "leave-one-observation-out; shifted-state null",
            "supported_claim": "A simple C,dCdt,R-conditioned first/second moment closure is not stable.",
            "unsupported_claim": "stochastic dynamics do not matter; all state dependence is absent",
            "next_route_meaning": "synthesize negative reduction boundary",
            "main_artifact": "Output/4090/decision.json",
            "figure_candidate": "yes",
        },
        {
            "node": "4094",
            "question": "What bounded stochastic-negative claim remains after 4090?",
            "target": "T1 low-dimensional moment closure",
            "data_scope": "all_19_observations",
            "baseline": "4090 grouped OOS models",
            "null": "shifted-state null and residual-unit caveats",
            "primary_metric": "synthesis of failed first/second moment gates",
            "gate": "bounded negative synthesis",
            "result": "bounded_stochastic_negative_result_after_4090",
            "claim_class": "NOT_SUPPORTED",
            "robustness": "bounded to tested C,dCdt,R moment closure",
            "supported_claim": "T1 is not stably reduced by the tested low-dimensional moment closure.",
            "unsupported_claim": "all stochastic or Langevin explanations are impossible",
            "next_route_meaning": "route to event-local/state-matched tests",
            "main_artifact": "Output/4094/decision.json",
            "figure_candidate": "yes",
        },
        {
            "node": "4100A",
            "question": "Can a unique focal-centered activity unit be constructed before event-locality tests?",
            "target": "A_i(t) focal-centered local non-affine tangential activity",
            "data_scope": "all_19_observations",
            "baseline": "unique focal activity rows and overlap audit",
            "null": "technical coverage/QC",
            "primary_metric": "uniqueness_ok true; coverage_ok true; ref_good 10/14",
            "gate": "unique focal aggregate with overlap boundary",
            "result": "pass_unique_focal_activity_with_overlap_boundary",
            "claim_class": "TECHNICAL_PASS",
            "robustness": "underlying neighbor overlap remains nontrivial",
            "supported_claim": "Use focal aggregate A_i(t)/A_swarm_tangential_z for later state/event tests.",
            "unsupported_claim": "raw overlapping neighbor vectors are safe for spatial correlation",
            "next_route_meaning": "enter 4100",
            "main_artifact": "Output/4100A/decision.json",
            "figure_candidate": "supplement",
        },
        {
            "node": "4100",
            "question": "Do true transition timestamps contain extra T1 beyond matched C,dCdt,R state?",
            "target": "near-pre A_swarm_tangential_z",
            "data_scope": "all_19_observations",
            "baseline": "same-observation state-matched non-event controls",
            "null": "within-observation shifted event times",
            "primary_metric": "median delta -0.0329 z; same-direction 0.421; real beats shifted null 0.275",
            "gate": "effect, direction, null, and matching-quality gates",
            "result": "fail_event_timing_not_beyond_continuous_state",
            "claim_class": "NOT_SUPPORTED",
            "robustness": "matching quality passed; event-local effect failed",
            "supported_claim": "True transition timestamp adds no robust near-pre excess beyond matched C,dCdt,R state.",
            "unsupported_claim": "transitions have no special dynamics; propagation does not exist",
            "next_route_meaning": "stop burst/propagation route and synthesize",
            "main_artifact": "Output/4100/decision.json",
            "figure_candidate": "yes",
        },
        {
            "node": "4105",
            "question": "What bounded claim remains after 4100 fails event-locality?",
            "target": "T1 event-locality route",
            "data_scope": "all_19_observations",
            "baseline": "4100 state-matched controls",
            "null": "4100 shifted-event null",
            "primary_metric": "T0 synthesis",
            "gate": "technical synthesis",
            "result": "T0_no_event_local_information_beyond_matched_continuous_state",
            "claim_class": "NOT_SUPPORTED",
            "robustness": "bounded to event-timestamp route",
            "supported_claim": "T1 is transition-linked but not event-timing-specific after state matching.",
            "unsupported_claim": "burst propagation has been confirmatorily tested",
            "next_route_meaning": "pause 410x and optionally reframe around state paths",
            "main_artifact": "Output/4105/decision.json",
            "figure_candidate": "yes",
        },
        {
            "node": "4120",
            "question": "Can recent C-R state-path features be measured for history tests?",
            "target": "recent C-R path features",
            "data_scope": "all_19_observations",
            "baseline": "feature coverage and derivative stability",
            "null": "technical leakage audit",
            "primary_metric": "19/19 path coverage >=0.90; 19/19 theta valid >=0.90; max leakage |rho| 0.894",
            "gate": "state-path feature feasibility",
            "result": "pass_state_path_features_feasible_with_leakage_audit",
            "claim_class": "TECHNICAL_PASS",
            "robustness": "history-current leakage requires strict matching",
            "supported_claim": "Recent C-R path features are measurable.",
            "unsupported_claim": "history dependence of T1",
            "next_route_meaning": "enter 4121 with current-state matching",
            "main_artifact": "Output/4120/decision.json",
            "figure_candidate": "supplement",
        },
        {
            "node": "4121",
            "question": "With same current state, do different recent path directions separate T1?",
            "target": "A_swarm_tangential_z conditioned on h500_theta_h",
            "data_scope": "all_19_observations",
            "baseline": "same-observation current-state matched frame pairs",
            "null": "within-observation theta_h shuffle with pair recomputation",
            "primary_metric": "19/19 sufficient; median abs effect 0.0763 z; direction consistency 0.526",
            "gate": "matched coverage, effect size, direction consistency, shuffled-history null",
            "result": "boundary_observation_specific_history_dependence",
            "claim_class": "BOUNDARY",
            "robustness": "14/19 beat shuffled-null median; sign/order flips 9 positive vs 10 negative",
            "supported_claim": "Recent path direction gives observation-specific T1 separation.",
            "unsupported_claim": "universal recent-history rule or causal memory mechanism",
            "next_route_meaning": "route to 4125; do not enter confirmatory 4122/4123",
            "main_artifact": "Output/4121/decision.json",
            "figure_candidate": "yes",
        },
        {
            "node": "4125",
            "question": "What bounded state-path/history claim remains after 4121?",
            "target": "state-path/history route",
            "data_scope": "all_19_observations",
            "baseline": "4120/4121 gates",
            "null": "shuffled-history boundary",
            "primary_metric": "P1 observation-specific history dependence boundary",
            "gate": "technical synthesis",
            "result": "P1_observation_specific_history_dependence_boundary",
            "claim_class": "BOUNDARY",
            "robustness": "not stable as universal direction/order",
            "supported_claim": "The recent-history route is a bounded observation-specific result.",
            "unsupported_claim": "approach/departure hysteresis, OOS history gain, network propagation",
            "next_route_meaning": "stop 412x confirmatory route and enter 413x synthesis",
            "main_artifact": "Output/4125/decision.json",
            "figure_candidate": "yes",
        },
    ]


def build_evidence_registry() -> pd.DataFrame:
    rows = evidence_rows_from_decisions()
    source_map = build_source_map().set_index("node")
    for row in rows:
        node = str(row["node"])
        if node in source_map.index:
            row["source_provenance"] = source_map.loc[node, "provenance_level"]
            row["decision_exists"] = bool(source_map.loc[node, "decision_exists"])
            row["summary_exists"] = bool(source_map.loc[node, "summary_exists"])
        else:
            row["source_provenance"] = "manual"
            row["decision_exists"] = False
            row["summary_exists"] = False
    return pd.DataFrame(rows)


def build_claim_strength_registry() -> pd.DataFrame:
    rows = [
        {
            "claim_id": "C1_LOCAL_NONAFFINE_SURVIVAL",
            "claim_text": "Local affine deformation is insufficient to remove the transition-linked tangential residual in most observations.",
            "claim_strength": "SUPPORTED_WITH_BOUNDARY",
            "support_nodes": "4081c;4082;4088",
            "required_conditions": "T1 definition from 4088; local affine residualization; all-19 context retained",
            "boundary_observations": "Ob1;Ob3;Ob6;Ob8",
            "forbidden_stronger_claim": "T1 is universal across all observations or causal.",
            "figure_priority": "main",
        },
        {
            "claim_id": "C2_SCALE_LAG_ROBUST_SURVIVORS",
            "claim_text": "Within the 4081c survivor class, T1 survival is robust across nearby local scales and lags.",
            "claim_strength": "SUPPORTED_WITH_BOUNDARY",
            "support_nodes": "4082;4088",
            "required_conditions": "survivor class only; do not omit all-19 boundary",
            "boundary_observations": "Ob4 fragile survivor; non-survivors excluded by definition",
            "forbidden_stronger_claim": "Scale/lag robustness holds for all 19 observations.",
            "figure_priority": "main",
        },
        {
            "claim_id": "C3_DIFFUSE_TANGENTIAL_DOMINANCE",
            "claim_text": "The strongest repeated spatial/timing form is diffuse tangential activity, with edge/core contrast as a bounded secondary structure.",
            "claim_strength": "SUPPORTED_WITH_BOUNDARY",
            "support_nodes": "4084;4085;4088",
            "required_conditions": "robust survivor context; spatial/timing diagnostic variables",
            "boundary_observations": "edge/core contrast only 9/14; phase not stable",
            "forbidden_stronger_claim": "A stable edge/core trigger or propagation source is identified.",
            "figure_priority": "main",
        },
        {
            "claim_id": "C4_SIGNED_EVENT_HETEROGENEITY",
            "claim_text": "Signed low-to-high/high-to-low T1 structure exists but is heterogeneous across observations.",
            "claim_strength": "BOUNDARY",
            "support_nodes": "4086;4088",
            "required_conditions": "signed event-type decomposition",
            "boundary_observations": "multiple signed classes; no universal sign",
            "forbidden_stronger_claim": "A universal signed force or mirror law is supported.",
            "figure_priority": "supplement",
        },
        {
            "claim_id": "C5_NO_SIMPLE_STATE_MOMENT_CLOSURE",
            "claim_text": "A C,dCdt,R-conditioned low-dimensional first/second moment closure is not stable across observations under grouped validation.",
            "claim_strength": "NOT_SUPPORTED",
            "support_nodes": "4090;4094",
            "required_conditions": "tested target families and binned grouped OOS setup",
            "boundary_observations": "all observations in grouped validation",
            "forbidden_stronger_claim": "Stochastic dynamics or all state dependence are impossible.",
            "figure_priority": "main",
        },
        {
            "claim_id": "C6_NO_EVENT_TIMESTAMP_EXCESS",
            "claim_text": "True transition timestamps do not contain robust near-pre T1 excess beyond same-observation C,dCdt,R-matched controls.",
            "claim_strength": "NOT_SUPPORTED",
            "support_nodes": "4100;4105",
            "required_conditions": "A_swarm_tangential_z; near-pre window; state-matched controls",
            "boundary_observations": "matching quality passed but event-local effect failed",
            "forbidden_stronger_claim": "Transitions have no special dynamics.",
            "figure_priority": "main",
        },
        {
            "claim_id": "C7_OBSERVATION_SPECIFIC_HISTORY_BOUNDARY",
            "claim_text": "Recent C-R path direction can separate T1 within some observations, but the sign/order is not universal.",
            "claim_strength": "BOUNDARY",
            "support_nodes": "4120;4121;4125",
            "required_conditions": "h=0.50 theta_h; same-current-state matching; shuffled-history null",
            "boundary_observations": "9 positive and 10 negative signed observations",
            "forbidden_stronger_claim": "A robust universal history dependence or causal memory mechanism is supported.",
            "figure_priority": "main",
        },
        {
            "claim_id": "C8_PROPAGATION_NOT_CONFIRMATORILY_TESTED",
            "claim_text": "Propagation/burst-source mechanisms are not confirmatorily tested because the 4100 event-locality gate failed.",
            "claim_strength": "NOT_TESTED",
            "support_nodes": "4100;4105;4125",
            "required_conditions": "EGRT stop-before-4101/4102/4103",
            "boundary_observations": "not applicable",
            "forbidden_stronger_claim": "No propagation exists.",
            "figure_priority": "none",
        },
    ]
    return pd.DataFrame(rows)


def build_metadata_source_audit() -> pd.DataFrame:
    rows = [
        {
            "metadata_item": "recording_condition_daytime_dusk",
            "claim_or_value": "Ob6 and Ob11 daytime; others mainly dusk",
            "source_file": "idea/413x_phenomenon_boundary_evidence_synthesis_roadmap.md",
            "source_type": "current roadmap note",
            "verification_status": "UNVERIFIED",
            "allowed_use": "descriptive_annotation_only",
            "disallowed_use": "causal explanation or regime claim",
            "required_next_check": "Find independent dataset documentation or raw metadata before using as a claim.",
        },
        {
            "metadata_item": "observation_index_as_recording_order_proxy",
            "claim_or_value": "early-observation proxy noted in 4090A",
            "source_file": "Output/4090A/4090A_summary.md",
            "source_type": "analysis output",
            "verification_status": "UNVERIFIED",
            "allowed_use": "boundary annotation",
            "disallowed_use": "confirmed batch effect",
            "required_next_check": "Verify true recording order before interpreting.",
        },
        {
            "metadata_item": "408x_failure_labels",
            "claim_or_value": "Ob1/Ob3 fragile boundary; Ob6/Ob8 stable failures",
            "source_file": "Output/4087/decision.json; Output/4088/decision.json",
            "source_type": "analysis output",
            "verification_status": "VERIFIED",
            "allowed_use": "evidence registry and heterogeneity map",
            "disallowed_use": "causal recording-condition explanation",
            "required_next_check": "None for label use; metadata interpretation still separate.",
        },
        {
            "metadata_item": "4121_opposite_signed_history_groups",
            "claim_or_value": "negative examples Ob5/Ob8/Ob9; positive examples Ob12/Ob15/Ob17",
            "source_file": "Output/4125/tables/strongest_observation_effects.csv",
            "source_type": "analysis output",
            "verification_status": "VERIFIED",
            "allowed_use": "descriptive heterogeneity result",
            "disallowed_use": "universal history mechanism",
            "required_next_check": "Use all-19 context if plotted.",
        },
    ]
    return pd.DataFrame(rows)


def build_dependency_graph() -> str:
    return dedent(
        """
        # 4130 Claim Dependency Graph

        ```text
        4001 global affine residual baseline
                |
                v
        4080 local affine feasibility
                |
                v
        4081c all-19 local non-affine T1 survival
                |
                +--> 4082 scale/lag robustness in survivor class
                |
                +--> 4084/4085 spatial and timing characterization
                |
                +--> 4086/4087 signed and failure-boundary heterogeneity
                |
                v
        4088 bounded local non-affine T1 synthesis
                |
                +--> 4090/4094 no stable C,dCdt,R first/second moment closure
                |
                +--> 4100/4105 no event-timestamp excess after state matching
                |
                +--> 4120/4121/4125 observation-specific recent-history boundary
                |
                v
        413x phenomenon-and-boundary evidence synthesis
        ```
        """
    ).strip() + "\n"


def build_route_timeline(evidence: pd.DataFrame) -> str:
    rows = []
    for _, row in evidence.iterrows():
        rows.append(
            {
                "node": row["node"],
                "class": row["claim_class"],
                "result": row["result"],
                "route": row["next_route_meaning"],
            }
        )
    return "# 4130 Route Timeline\n\n" + md_table(rows, ["node", "class", "result", "route"]) + "\n"


def evaluate(
    source_map: pd.DataFrame,
    definitions: pd.DataFrame,
    evidence: pd.DataFrame,
    claims: pd.DataFrame,
    metadata: pd.DataFrame,
) -> dict[str, object]:
    required_terms = {
        "T1",
        "A_swarm_tangential_z",
        "all_tangential",
        "shell_edge_minus_core",
        "C",
        "dCdt",
        "R",
        "h500_theta_h",
        "event-local near-pre activity",
        "observation-level effect strength",
    }
    missing_terms = sorted(required_terms - set(definitions["term"]))
    invalid_claim_classes = sorted(set(evidence["claim_class"]) - CLAIM_CLASSES)
    invalid_claim_strengths = sorted(set(claims["claim_strength"]) - CLAIM_CLASSES - {"TECHNICAL"})
    core_nodes = [
        "4088",
        "4090",
        "4094",
        "4100A",
        "4100",
        "4105",
        "4120",
        "4121",
        "4125",
    ]
    sm = source_map.set_index("node")
    missing_core = [
        node
        for node in core_nodes
        if node not in sm.index or not bool(sm.loc[node, "decision_exists"]) or not bool(sm.loc[node, "summary_exists"])
    ]
    has_unverified_metadata = bool((metadata["verification_status"] == "UNVERIFIED").any())
    definition_ok = not missing_terms and not invalid_claim_classes and not invalid_claim_strengths
    source_ok = not missing_core
    if definition_ok and source_ok:
        gate = "pass_4130_registry_ready_with_metadata_boundary"
        interpretation = (
            "The evidence registry, definition dictionary, claim strength registry, and metadata audit are ready for 4131/4132. "
            "Metadata-dependent heterogeneity claims must remain descriptive until independently verified."
        )
        next_nodes = [
            "4131_robust_positive_phenomenon_atlas",
            "4132_negative_mechanism_boundary_atlas",
        ]
    else:
        gate = "technical_stop_4130_registry_incomplete"
        interpretation = "4130 found missing core sources or definition/claim-class inconsistencies. Fix registry before continuing."
        next_nodes = ["fix_4130_registry"]
    return {
        "node": NODE,
        "date": DATE,
        "node_type": "synthesis_registry",
        "upstream_node": "4125_state_path_history_synthesis",
        "data_scope": "all_19_observations",
        "primary_goal": "convert_408x_412x_evidence_into_paper_ready_phenomenon_boundary_architecture",
        "source_counts": {
            "nodes_checked": int(len(source_map)),
            "nodes_with_decision_json": int(source_map["decision_exists"].sum()),
            "nodes_with_summary_md": int(source_map["summary_exists"].sum()),
            "summary_only_nodes": int((source_map["provenance_level"] == "summary_only").sum()),
        },
        "registry_counts": {
            "definitions": int(len(definitions)),
            "evidence_rows": int(len(evidence)),
            "claim_strength_rows": int(len(claims)),
            "metadata_audit_rows": int(len(metadata)),
        },
        "quality_checks": {
            "missing_required_terms": missing_terms,
            "invalid_evidence_claim_classes": invalid_claim_classes,
            "invalid_claim_strengths": invalid_claim_strengths,
            "missing_core_sources": missing_core,
            "has_unverified_metadata": has_unverified_metadata,
            "definition_registry_ok": definition_ok,
            "source_registry_ok": source_ok,
        },
        "gate_result": gate,
        "interpretation": interpretation,
        "does_not_prove": [
            "new mechanism",
            "causal explanation",
            "metadata regime",
            "universal history dependence",
            "publication-ready figures",
        ],
        "next": next_nodes,
        "artifacts": [
            "Output/4130/definition_dictionary.csv",
            "Output/4130/evidence_registry.csv",
            "Output/4130/evidence_registry.json",
            "Output/4130/claim_strength_registry.csv",
            "Output/4130/metadata_source_audit.csv",
            "Output/4130/source_map.csv",
            "Output/4130/claim_dependency_graph.md",
            "Output/4130/route_timeline.md",
            "Output/4130/decision.json",
            "Output/4130/4130_summary.md",
        ],
    }


def write_config() -> None:
    text = dedent(
        f"""
        node: {NODE}
        date: {DATE}
        route: 413x_phenomenon_boundary_evidence_synthesis
        upstream_node: 4125_state_path_history_synthesis
        new_mechanism_search_allowed: false
        new_target_search_allowed: false
        required_outputs:
          - definition_dictionary.csv
          - evidence_registry.csv
          - claim_strength_registry.csv
          - metadata_source_audit.csv
          - claim_dependency_graph.md
          - route_timeline.md
        """
    ).strip()
    (OUT / "config.yaml").write_text(text + "\n", encoding="utf-8")


def write_summary(
    decision: dict[str, object],
    source_map: pd.DataFrame,
    definitions: pd.DataFrame,
    evidence: pd.DataFrame,
    claims: pd.DataFrame,
    metadata: pd.DataFrame,
) -> None:
    class_counts = evidence["claim_class"].value_counts().rename_axis("claim_class").reset_index(name="count")
    figure_counts = evidence["figure_candidate"].value_counts().rename_axis("figure_candidate").reset_index(name="count")
    next_rows = [{"next": x} for x in decision["next"]]
    parts = [
        "# Node 4130 Summary",
        "## Question\n\n"
        "Can the completed 408x-412x evidence be normalized into a definition dictionary, evidence registry, claim-strength registry, and metadata audit before writing positive/negative atlases?",
        "## Implementation Scope\n\n"
        "4130 is a registry/synthesis node. It does not add a mechanism model, does not change the T1 target, and does not rerun old thresholds.",
        "## Registry Counts\n\n"
        + md_table(
            [
                {
                    "definitions": len(definitions),
                    "evidence_rows": len(evidence),
                    "claim_rows": len(claims),
                    "metadata_rows": len(metadata),
                    "decision_json_sources": decision["source_counts"]["nodes_with_decision_json"],
                    "summary_only_sources": decision["source_counts"]["summary_only_nodes"],
                }
            ],
            [
                "definitions",
                "evidence_rows",
                "claim_rows",
                "metadata_rows",
                "decision_json_sources",
                "summary_only_sources",
            ],
        ),
        "## Evidence Claim Class Counts\n\n"
        + md_table(class_counts.to_dict("records"), ["claim_class", "count"]),
        "## Figure Candidate Counts\n\n"
        + md_table(figure_counts.to_dict("records"), ["figure_candidate", "count"]),
        "## Main Claim Strength Registry\n\n"
        + md_table(
            claims.to_dict("records"),
            ["claim_id", "claim_strength", "claim_text", "support_nodes", "forbidden_stronger_claim", "figure_priority"],
        ),
        "## Metadata Audit\n\n"
        + md_table(
            metadata.to_dict("records"),
            ["metadata_item", "claim_or_value", "verification_status", "allowed_use", "disallowed_use"],
        ),
        "## Quality Checks\n\n"
        "```json\n" + json.dumps(decision["quality_checks"], indent=2) + "\n```",
        "## Gate Evaluation\n\n"
        "```text\n" f"gate_result = {decision['gate_result']}\n" "```\n\n" + decision["interpretation"],
        "## What This Supports\n\n"
        "- 4131 positive phenomenon atlas can now use fixed definitions.\n"
        "- 4132 negative boundary atlas can distinguish `NOT_SUPPORTED` from `NOT_TESTED`.\n"
        "- 4133 must keep unverified metadata as descriptive annotation only.",
        "## What This Does Not Prove\n\n"
        + md_table([{"does_not_prove": x} for x in decision["does_not_prove"]], ["does_not_prove"]),
        "## Next Node\n\n" + md_table(next_rows, ["next"]),
        "## Artifacts\n\n" + "\n".join(f"- `{a}`" for a in decision["artifacts"]),
    ]
    (OUT / "4130_summary.md").write_text("\n\n".join(parts) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    write_config()

    source_map = build_source_map()
    definitions = build_definition_dictionary()
    evidence = build_evidence_registry()
    claims = build_claim_strength_registry()
    metadata = build_metadata_source_audit()
    decision = evaluate(source_map, definitions, evidence, claims, metadata)

    write_csv_pair(source_map, "source_map.csv")
    write_csv_pair(definitions, "definition_dictionary.csv")
    write_csv_pair(evidence, "evidence_registry.csv")
    write_csv_pair(claims, "claim_strength_registry.csv")
    write_csv_pair(metadata, "metadata_source_audit.csv")
    (OUT / "evidence_registry.json").write_text(
        json.dumps(evidence.to_dict("records"), indent=2),
        encoding="utf-8",
    )
    (OUT / "claim_dependency_graph.md").write_text(build_dependency_graph(), encoding="utf-8")
    (OUT / "route_timeline.md").write_text(build_route_timeline(evidence), encoding="utf-8")
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2), encoding="utf-8")
    write_summary(decision, source_map, definitions, evidence, claims, metadata)

    print(json.dumps(decision, indent=2))
    print(f"Wrote 4130 outputs to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
