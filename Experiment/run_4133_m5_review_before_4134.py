"""M5 review before entering 4134 figure-ready evidence panels.

This is a review node, not a new experiment. It checks whether the completed
4130-4133 synthesis outputs are internally consistent enough to enter 4134,
and it freezes figure-routing and overclaim guards before paper-style panels
are assembled.
"""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4133_M5_review_before_4134"
DATE = "2026-08-28"
NODE = "M5_REVIEW_before_4134"


def ensure_dirs() -> None:
    (OUT / "tables").mkdir(parents=True, exist_ok=True)


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def write_csv_pair(df: pd.DataFrame, name: str) -> None:
    df.to_csv(OUT / name, index=False)
    df.to_csv(OUT / "tables" / name, index=False)


def md_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    if not rows:
        return "_No rows._"
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        values: list[str] = []
        for col in columns:
            val = row.get(col, "")
            values.append(str(val).replace("\n", " ").replace("|", "\\|"))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def artifact_audit(decisions: dict[str, dict[str, object]]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    seen: set[str] = set()
    for source_node, decision in decisions.items():
        for artifact in decision.get("artifacts", []):
            artifact_s = str(artifact)
            if artifact_s in seen:
                continue
            seen.add(artifact_s)
            path = ROOT / artifact_s
            rows.append(
                {
                    "source_node": source_node,
                    "artifact": artifact_s,
                    "exists": path.exists(),
                    "size_bytes": path.stat().st_size if path.exists() else 0,
                    "artifact_type": path.suffix.lstrip(".") or "directory",
                    "figure_artifact": artifact_s.lower().endswith((".png", ".jpg", ".jpeg", ".svg", ".pdf")),
                }
            )
    return pd.DataFrame(rows)


def build_gate_review(
    decisions: dict[str, dict[str, object]],
    claim_registry: pd.DataFrame,
    positive_atlas: pd.DataFrame,
    negative_atlas: pd.DataFrame,
    observation_classes: pd.DataFrame,
    artifacts: pd.DataFrame,
) -> pd.DataFrame:
    upstream_gates = {node: str(decision.get("gate_result", "")) for node, decision in decisions.items()}
    all_upstream_pass = all(gate.startswith("pass_") for gate in upstream_gates.values())

    definition_dict = ROOT / "Output" / "4130" / "definition_dictionary.csv"
    definition_rows = len(read_csv(definition_dict)) if definition_dict.exists() else 0
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
    if definition_dict.exists():
        definition_terms = set(read_csv(definition_dict)["term"].astype(str))
    else:
        definition_terms = set()
    missing_terms = sorted(required_terms - definition_terms)

    primary_positive = positive_atlas[positive_atlas["atlas_role"].astype(str).eq("primary_positive")]
    secondary_positive = positive_atlas[
        positive_atlas["atlas_role"].astype(str).str.contains("secondary", case=False, na=False)
    ]
    not_supported_rows = negative_atlas[negative_atlas["claim_class"].astype(str).eq("NOT_SUPPORTED")]
    not_tested_rows = negative_atlas[negative_atlas["claim_class"].astype(str).eq("NOT_TESTED")]
    metadata_status = decisions["4133"].get("metadata_status", {})
    quality_4133 = decisions["4133"].get("quality_checks", {})

    figure_artifacts = artifacts[artifacts["figure_artifact"].astype(bool)]
    figures_ok = bool(len(figure_artifacts)) and bool(figure_artifacts["exists"].all()) and bool(
        (figure_artifacts["size_bytes"] > 0).all()
    )

    forbidden_claims_present = (
        "forbidden_stronger_claim" in claim_registry.columns
        and claim_registry["forbidden_stronger_claim"].fillna("").astype(str).str.len().gt(0).all()
    )
    forbidden_boundary_present = (
        "forbidden_wording" in negative_atlas.columns
        and negative_atlas["forbidden_wording"].fillna("").astype(str).str.len().gt(0).all()
    )

    rows = [
        {
            "gate_id": "M5_G1",
            "criterion": "Upstream gates passed",
            "status": "PASS" if all_upstream_pass else "STOP",
            "evidence": "; ".join(f"{node}={gate}" for node, gate in upstream_gates.items()),
            "action_before_4134": "Enter figure planning only if every upstream synthesis node passed.",
        },
        {
            "gate_id": "M5_G2",
            "criterion": "Definition registry is frozen",
            "status": "PASS" if not missing_terms and definition_rows >= 10 else "STOP",
            "evidence": f"definition_rows={definition_rows}; missing_required_terms={','.join(missing_terms) or 'none'}",
            "action_before_4134": "Use the 4130 T1 and variable definitions without introducing a new residual target.",
        },
        {
            "gate_id": "M5_G3",
            "criterion": "Positive atlas has bounded primary positives",
            "status": "PASS" if len(primary_positive) >= 3 else "STOP",
            "evidence": f"primary_positive_rows={len(primary_positive)}; secondary_or_bounded_rows={len(secondary_positive)}",
            "action_before_4134": "Main figures may show common T1 survival, scale/lag robustness, and diffuse tangential activity.",
        },
        {
            "gate_id": "M5_G4",
            "criterion": "Negative atlas separates tested failures from open routes",
            "status": "PASS" if len(not_supported_rows) >= 2 and len(not_tested_rows) >= 1 else "STOP",
            "evidence": f"not_supported_rows={len(not_supported_rows)}; not_tested_rows={len(not_tested_rows)}",
            "action_before_4134": "Write C,dCdt,R and event-locality as tested reductions that failed; write propagation as not tested.",
        },
        {
            "gate_id": "M5_G5",
            "criterion": "Observation heterogeneity remains all-19 and descriptive",
            "status": "PASS_WITH_BOUNDARY"
            if len(observation_classes) == 19 and bool(quality_4133.get("recording_condition_not_used_as_causal"))
            else "STOP",
            "evidence": (
                f"observation_class_rows={len(observation_classes)}; "
                f"metadata_status={metadata_status}; "
                f"recording_condition_not_used_as_causal={quality_4133.get('recording_condition_not_used_as_causal')}"
            ),
            "action_before_4134": "Keep Ob6/Ob8 and daytime/dusk/order-proxy explanations as annotations, not causal claims.",
        },
        {
            "gate_id": "M5_G6",
            "criterion": "Existing figure artifacts are available",
            "status": "PASS" if figures_ok else "ACTION_REQUIRED_IN_4134",
            "evidence": (
                f"figure_artifacts={len(figure_artifacts)}; "
                f"missing_or_empty={len(figure_artifacts[(~figure_artifacts['exists']) | (figure_artifacts['size_bytes'] <= 0)])}"
            ),
            "action_before_4134": "Use existing 4131-4133 figures as evidence sources; rebuild publication panels where needed.",
        },
        {
            "gate_id": "M5_G7",
            "criterion": "Figure 1 concept/data panels are not yet final artifacts",
            "status": "ACTION_REQUIRED_IN_4134",
            "evidence": "4130-4133 provide definitions and evidence, but no final 3D snapshot / affine schematic / T1 definition panel set.",
            "action_before_4134": "Build Figure 1 as definition and data orientation only; do not let it imply a new mechanism.",
        },
        {
            "gate_id": "M5_G8",
            "criterion": "Overclaim guards are explicit",
            "status": "PASS" if forbidden_claims_present and forbidden_boundary_present else "STOP",
            "evidence": (
                f"claim_registry_forbidden_wording_complete={forbidden_claims_present}; "
                f"negative_atlas_forbidden_wording_complete={forbidden_boundary_present}"
            ),
            "action_before_4134": "Every 4134 caption must include allowed interpretation and forbidden stronger interpretation.",
        },
    ]
    return pd.DataFrame(rows)


def build_figure_candidates() -> pd.DataFrame:
    rows = [
        {
            "figure_id": "Figure 1",
            "panel_id": "1A",
            "panel_question": "What data are being reduced?",
            "source_node": "raw data / 4133",
            "source_artifact": "Output/4133/raw_metadata_by_ob.csv",
            "source_status": "needs_assembly",
            "recommended_role": "main",
            "4134_action": "Select one representative 3D trajectory snapshot and label it as data orientation only.",
            "allowed_claim": "The dataset consists of 3D individual trajectories in laboratory midge swarms.",
            "boundary_guard": "Do not infer mechanism, interaction, or recording-condition causality from the snapshot.",
        },
        {
            "figure_id": "Figure 1",
            "panel_id": "1B",
            "panel_question": "What is removed by global/local affine reduction?",
            "source_node": "4130",
            "source_artifact": "Output/4130/definition_dictionary.csv",
            "source_status": "concept_panel_to_build",
            "recommended_role": "main",
            "4134_action": "Draw a compact schematic distinguishing global affine, local affine, and residual components.",
            "allowed_claim": "T1 is interpreted only after defined affine components are subtracted.",
            "boundary_guard": "Do not present the schematic as a fitted physical model.",
        },
        {
            "figure_id": "Figure 1",
            "panel_id": "1C",
            "panel_question": "What is the frozen T1 observable?",
            "source_node": "4130 / 4088",
            "source_artifact": "Output/4130/definition_dictionary.csv",
            "source_status": "concept_panel_to_build",
            "recommended_role": "main",
            "4134_action": "Convert the frozen T1 definition into a visual equation/flow panel.",
            "allowed_claim": "T1 is the transition-linked local tangential non-affine residual used in 413x.",
            "boundary_guard": "Do not rename or redefine the target in 4134.",
        },
        {
            "figure_id": "Figure 1",
            "panel_id": "1D",
            "panel_question": "How does the event-conditioned time profile look?",
            "source_node": "4131",
            "source_artifact": "Output/4131/positive_phenomenon_atlas.csv",
            "source_status": "needs_assembly",
            "recommended_role": "main",
            "4134_action": "Build one example trace with clear labels: event, pre window, matched control/null.",
            "allowed_claim": "The time trace illustrates the measurement pipeline, not a universal temporal law.",
            "boundary_guard": "Avoid choosing an example that hides failure observations.",
        },
        {
            "figure_id": "Figure 2",
            "panel_id": "2A",
            "panel_question": "Does T1 survive local affine subtraction across all observations?",
            "source_node": "4131 / 4133",
            "source_artifact": "Output/4131/observation_positive_coverage_matrix.csv",
            "source_status": "needs_assembly",
            "recommended_role": "main",
            "4134_action": "Render an all-19 forest/strip panel with Ob1, Ob3, Ob6, and Ob8 retained.",
            "allowed_claim": "T1 survival is common in most observations.",
            "boundary_guard": "Do not write universal survival or omit stable failures.",
        },
        {
            "figure_id": "Figure 2",
            "panel_id": "2B",
            "panel_question": "Is the survivor class stable to nearby scale and lag choices?",
            "source_node": "4131",
            "source_artifact": "Output/4131/figures/4131_observation_coverage_matrix.png",
            "source_status": "ready_source",
            "recommended_role": "main",
            "4134_action": "Reuse or redraw as a publication heatmap, preserving all-19 context.",
            "allowed_claim": "Scale/lag robustness is high inside the survivor class.",
            "boundary_guard": "Do not generalize survivor-only robustness to all 19 observations.",
        },
        {
            "figure_id": "Figure 2",
            "panel_id": "2C",
            "panel_question": "Which observations are robust, fragile, or failures?",
            "source_node": "4133",
            "source_artifact": "Output/4133/observation_classes.csv",
            "source_status": "needs_assembly",
            "recommended_role": "main",
            "4134_action": "Draw the observation class strip beside the all-19 evidence panel.",
            "allowed_claim": "The positive result has explicit observation-level boundaries.",
            "boundary_guard": "Do not treat failure classes as artifacts unless independently verified.",
        },
        {
            "figure_id": "Figure 3",
            "panel_id": "3A",
            "panel_question": "What spatial/activity form is most stable?",
            "source_node": "4131",
            "source_artifact": "Output/4131/figures/4131_spatial_phase_positive_summary.png",
            "source_status": "ready_source",
            "recommended_role": "main",
            "4134_action": "Show all_tangential support beside edge-core support.",
            "allowed_claim": "Diffuse tangential activity is the strongest repeated form.",
            "boundary_guard": "Do not write edge/core contrast as a universal trigger.",
        },
        {
            "figure_id": "Figure 3",
            "panel_id": "3B",
            "panel_question": "Is near-pre timing stable?",
            "source_node": "4131",
            "source_artifact": "Output/4131/figures/4131_spatial_phase_positive_summary.png",
            "source_status": "ready_source",
            "recommended_role": "main",
            "4134_action": "Include near-pre as moderate timing evidence, not as the central claim.",
            "allowed_claim": "Near-pre timing appears in part of the tested survivor subset.",
            "boundary_guard": "Do not write a sharp universal precursor.",
        },
        {
            "figure_id": "Figure 3",
            "panel_id": "3C",
            "panel_question": "Is there a universal signed direction law?",
            "source_node": "4132 / 4086",
            "source_artifact": "Output/4132/negative_boundary_atlas.csv",
            "source_status": "ready_table_source",
            "recommended_role": "supplement_or_small_boundary_panel",
            "4134_action": "Use only as a compact boundary annotation if the main figure has space.",
            "allowed_claim": "Signed structure is heterogeneous across observations.",
            "boundary_guard": "Do not write universal low-to-high, high-to-low, or mirror law.",
        },
        {
            "figure_id": "Figure 4",
            "panel_id": "4A",
            "panel_question": "Does C,dCdt,R provide a stable low-dimensional moment closure?",
            "source_node": "4132 / 4090",
            "source_artifact": "Output/4132/figures/4132_moment_closure_negative_metrics.png",
            "source_status": "ready_source",
            "recommended_role": "main",
            "4134_action": "Use as the first mechanism-boundary panel.",
            "allowed_claim": "The tested C,dCdt,R first/second moment closure is not stably supported.",
            "boundary_guard": "Do not write that stochastic dynamics or all state dependence are impossible.",
        },
        {
            "figure_id": "Figure 4",
            "panel_id": "4B",
            "panel_question": "Do true transition timestamps add state-matched near-pre excess?",
            "source_node": "4132 / 4100",
            "source_artifact": "Output/4132/figures/4132_event_locality_negative_metrics.png",
            "source_status": "ready_source",
            "recommended_role": "main",
            "4134_action": "Use as the second mechanism-boundary panel.",
            "allowed_claim": "The tested state-matched near-pre event-locality route is not supported.",
            "boundary_guard": "Do not write that transitions have no special dynamics.",
        },
        {
            "figure_id": "Figure 4",
            "panel_id": "4C",
            "panel_question": "Does recent history become a universal rule?",
            "source_node": "4131 / 4132 / 4121",
            "source_artifact": "Output/4131/figures/4131_history_secondary_positive.png",
            "source_status": "ready_source",
            "recommended_role": "main",
            "4134_action": "Frame as observation-specific history boundary, not as a positive universal mechanism.",
            "allowed_claim": "Recent path direction separates T1 in some observations but sign/order is not universal.",
            "boundary_guard": "Do not write causal memory, hysteresis, or universal history dependence.",
        },
        {
            "figure_id": "Figure 5",
            "panel_id": "5A",
            "panel_question": "How does evidence vary across observations and routes?",
            "source_node": "4133",
            "source_artifact": "Output/4133/figures/4133_observation_route_matrix.png",
            "source_status": "ready_source",
            "recommended_role": "main",
            "4134_action": "Use as the anchor heterogeneity panel.",
            "allowed_claim": "Heterogeneity is structured enough to map explicitly.",
            "boundary_guard": "Do not turn route scores into a predictive classifier.",
        },
        {
            "figure_id": "Figure 5",
            "panel_id": "5B",
            "panel_question": "Are descriptive metadata associations visible?",
            "source_node": "4133",
            "source_artifact": "Output/4133/figures/4133_t1_effect_vs_mean_track_length.png",
            "source_status": "ready_source",
            "recommended_role": "main_with_descriptive_label",
            "4134_action": "Choose track length or swarm size panel; place the other in supplement if needed.",
            "allowed_claim": "Some small-n descriptive associations are visible and sensitivity-audited.",
            "boundary_guard": "Do not write causal metadata or recording-condition explanations.",
        },
        {
            "figure_id": "Figure 5",
            "panel_id": "5C",
            "panel_question": "Which observations define the strongest positive and failure cases?",
            "source_node": "4133",
            "source_artifact": "Output/4133/observation_classes.csv",
            "source_status": "needs_assembly",
            "recommended_role": "main_or_supplement",
            "4134_action": "Build a compact exemplar panel only if it does not hide all-19 heterogeneity.",
            "allowed_claim": "Examples illustrate classes already defined by all-19 tables.",
            "boundary_guard": "Do not let examples substitute for the all-19 result.",
        },
    ]
    return pd.DataFrame(rows)


def build_claim_storyline_review(claim_registry: pd.DataFrame) -> pd.DataFrame:
    figure_map = {
        "C1_LOCAL_NONAFFINE_SURVIVAL": "Figure 2",
        "C2_SCALE_LAG_ROBUST_SURVIVORS": "Figure 2",
        "C3_DIFFUSE_TANGENTIAL_DOMINANCE": "Figure 3",
        "C4_SIGNED_EVENT_HETEROGENEITY": "Supplement or Figure 3C boundary annotation",
        "C5_NO_SIMPLE_STATE_MOMENT_CLOSURE": "Figure 4A",
        "C6_NO_EVENT_TIMESTAMP_EXCESS": "Figure 4B",
        "C7_OBSERVATION_SPECIFIC_HISTORY_BOUNDARY": "Figure 4C",
        "C8_PROPAGATION_NOT_CONFIRMATORILY_TESTED": "Limitations / remaining open mechanism space",
    }
    rows: list[dict[str, object]] = []
    for record in claim_registry.to_dict("records"):
        claim_id = str(record.get("claim_id", ""))
        strength = str(record.get("claim_strength", ""))
        priority = str(record.get("figure_priority", ""))
        if strength == "NOT_TESTED" or priority == "none":
            m5_status = "DO_NOT_MAIN_FIGURE_AS_RESULT"
        elif priority == "supplement":
            m5_status = "SUPPLEMENT_OR_BOUNDARY_ONLY"
        elif strength in {"SUPPORTED_WITH_BOUNDARY", "NOT_SUPPORTED", "BOUNDARY"}:
            m5_status = "MAIN_ALLOWED_WITH_BOUNDARY_WORDING"
        else:
            m5_status = "REVIEW_BEFORE_USE"
        rows.append(
            {
                "claim_id": claim_id,
                "claim_strength": strength,
                "figure_priority_from_4130": priority,
                "recommended_4134_location": figure_map.get(claim_id, "review"),
                "m5_status": m5_status,
                "allowed_claim_text": record.get("claim_text", ""),
                "required_conditions": record.get("required_conditions", ""),
                "boundary_observations": record.get("boundary_observations", ""),
                "forbidden_stronger_claim": record.get("forbidden_stronger_claim", ""),
            }
        )
    return pd.DataFrame(rows)


def build_overclaim_risks() -> pd.DataFrame:
    rows = [
        {
            "risk_id": "R1",
            "risk": "T1 is described as universal or causal.",
            "severity": "high",
            "trigger": "Writing the 15/19 result without failures and boundaries.",
            "mitigation": "Always retain 'most observations', show all-19 context, and name failure/boundary observations.",
            "status_after_m5": "guarded",
        },
        {
            "risk_id": "R2",
            "risk": "Tested C,dCdt,R failure is upgraded into a claim that stochastic dynamics are impossible.",
            "severity": "high",
            "trigger": "Over-reading 4090/4094 negative results.",
            "mitigation": "Write only that the tested first/second moment closure did not provide a stable reduction.",
            "status_after_m5": "guarded",
        },
        {
            "risk_id": "R3",
            "risk": "Event-locality failure is written as absence of transition dynamics.",
            "severity": "high",
            "trigger": "Treating state-matched near-pre aggregate failure as a full event-dynamics test.",
            "mitigation": "Write only that true timestamps add no robust near-pre excess beyond matched C,dCdt,R state.",
            "status_after_m5": "guarded",
        },
        {
            "risk_id": "R4",
            "risk": "Propagation is written as disproven.",
            "severity": "high",
            "trigger": "Forgetting that confirmatory propagation route was not entered.",
            "mitigation": "Mark propagation as NOT_TESTED and place it in remaining open mechanism space.",
            "status_after_m5": "guarded",
        },
        {
            "risk_id": "R5",
            "risk": "History effect is written as universal memory or hysteresis.",
            "severity": "high",
            "trigger": "Using 14/19 beats-shuffle count without the failed direction/order consistency.",
            "mitigation": "Write observation-specific history separation and show sign/order heterogeneity.",
            "status_after_m5": "guarded",
        },
        {
            "risk_id": "R6",
            "risk": "Daytime/dusk or observation order is written as a causal explanation.",
            "severity": "medium_high",
            "trigger": "Using unverified metadata annotations and n=19 associations too strongly.",
            "mitigation": "Label metadata as descriptive only; do not use it as a regime explanation.",
            "status_after_m5": "guarded",
        },
        {
            "risk_id": "R7",
            "risk": "Survivor-only panels hide negative observations.",
            "severity": "high",
            "trigger": "Showing robustness only inside the 15-observation survivor subset.",
            "mitigation": "Put all-19 survival/classification before survivor-subset robustness.",
            "status_after_m5": "guarded",
        },
        {
            "risk_id": "R8",
            "risk": "Concept figure is mistaken for a tested physical model.",
            "severity": "medium",
            "trigger": "Figure 1 affine/T1 schematic is drawn too mechanistically.",
            "mitigation": "Caption Figure 1 as measurement definition and data orientation only.",
            "status_after_m5": "guarded",
        },
    ]
    return pd.DataFrame(rows)


def build_4134_action_checklist() -> pd.DataFrame:
    rows = [
        {
            "step_order": 1,
            "4134_task": "Create figure_source_map.csv from the M5 figure candidate table.",
            "input": "Output/4133_M5_review_before_4134/main_vs_supplement_figure_candidates.csv",
            "completion_gate": "Every panel has question, metric/source, sample size or scope, baseline/null, interpretation, and guard.",
        },
        {
            "step_order": 2,
            "4134_task": "Build Figure 1 as data and definition orientation.",
            "input": "Output/4130/definition_dictionary.csv; raw trajectory source; 4088/4131 examples",
            "completion_gate": "No new mechanism or residual target is introduced.",
        },
        {
            "step_order": 3,
            "4134_task": "Assemble Figure 2 around all-19 T1 survival before survivor-subset robustness.",
            "input": "Output/4131/observation_positive_coverage_matrix.csv; Output/4133/observation_classes.csv",
            "completion_gate": "Failure and fragile observations remain visible.",
        },
        {
            "step_order": 4,
            "4134_task": "Assemble Figure 3 around diffuse tangential activity and timing boundaries.",
            "input": "Output/4131/figures/4131_spatial_phase_positive_summary.png; Output/4132/negative_boundary_atlas.csv",
            "completion_gate": "Diffuse tangential activity is primary; edge/core and signed structure are bounded.",
        },
        {
            "step_order": 5,
            "4134_task": "Assemble Figure 4 as the mechanism-boundary figure.",
            "input": "Output/4132/figures/*.png; Output/4131/figures/4131_history_secondary_positive.png",
            "completion_gate": "Negative panels are written as tested reduction failures, not nonexistence claims.",
        },
        {
            "step_order": 6,
            "4134_task": "Assemble Figure 5 as the observation heterogeneity figure.",
            "input": "Output/4133/figures/*.png; Output/4133/heterogeneity_associations.csv",
            "completion_gate": "Metadata associations remain descriptive and all-19 evidence remains visible.",
        },
        {
            "step_order": 7,
            "4134_task": "Draft figure captions and panel metadata.",
            "input": "M5 claim storyline review and overclaim risk register",
            "completion_gate": "Each caption states what it supports and what it does not prove.",
        },
    ]
    return pd.DataFrame(rows)


def build_source_map(output_names: list[str]) -> pd.DataFrame:
    inputs = [
        "Experiment/run_4133_m5_review_before_4134.py",
        "Output/4130/decision.json",
        "Output/4130/definition_dictionary.csv",
        "Output/4130/claim_strength_registry.csv",
        "Output/4131/decision.json",
        "Output/4131/positive_phenomenon_atlas.csv",
        "Output/4131/positive_figure_plan.csv",
        "Output/4132/decision.json",
        "Output/4132/negative_boundary_atlas.csv",
        "Output/4133/decision.json",
        "Output/4133/observation_classes.csv",
        "Output/4133/heterogeneity_associations.csv",
    ]
    rows: list[dict[str, object]] = []
    for path in inputs:
        p = ROOT / path
        rows.append(
            {
                "role": "input",
                "path": path,
                "exists": p.exists(),
                "size_bytes": p.stat().st_size if p.exists() else 0,
            }
        )
    for name in output_names:
        p = OUT / name
        rows.append(
            {
                "role": "output",
                "path": rel(p),
                "exists": p.exists(),
                "size_bytes": p.stat().st_size if p.exists() else 0,
            }
        )
    return pd.DataFrame(rows)


def write_summary(
    decision: dict[str, object],
    gate_review: pd.DataFrame,
    figure_candidates: pd.DataFrame,
    claim_review: pd.DataFrame,
    overclaim_risks: pd.DataFrame,
    checklist: pd.DataFrame,
) -> None:
    main_candidates = figure_candidates[
        figure_candidates["recommended_role"].astype(str).str.contains("main", case=False, na=False)
    ]
    action_candidates = figure_candidates[
        figure_candidates["source_status"].astype(str).str.contains("needs|concept", case=False, na=False)
    ]
    summary = dedent(
        f"""\
        # M5 Review Before 4134

        ## Purpose

        This is a review node between `4133_observation_heterogeneity_map` and
        `4134_figure_ready_evidence_panels`. It does not add a new mechanism,
        residual target, threshold, or predictive model. Its only job is to
        decide whether the completed 4130-4133 evidence can be safely converted
        into paper-ready figures.

        ## Gate Result

        ```text
        gate_result = {decision["gate_result"]}
        latest_completed_node = {NODE}
        next_node = 4134_figure_ready_evidence_panels
        ```

        ## Main Decision

        The review passes with explicit 4134 actions. The evidence chain is
        ready to enter figure-panel construction, but 4134 must treat Figure 1
        as a definition/data-orientation figure and must keep metadata,
        propagation, history, and negative mechanism boundaries explicit.

        ## Gate Review

        {md_table(gate_review.to_dict("records"), ["gate_id", "criterion", "status", "evidence", "action_before_4134"])}

        ## Main Figure Candidate Count

        ```text
        total_candidate_panels = {len(figure_candidates)}
        main_or_main_descriptive_candidate_panels = {len(main_candidates)}
        panels_needing_4134_assembly = {len(action_candidates)}
        ```

        ## Figure Candidates Needing Assembly

        {md_table(action_candidates.to_dict("records"), ["figure_id", "panel_id", "panel_question", "source_status", "4134_action", "boundary_guard"])}

        ## Claim Storyline Review

        {md_table(claim_review.to_dict("records"), ["claim_id", "claim_strength", "recommended_4134_location", "m5_status", "forbidden_stronger_claim"])}

        ## Overclaim Risk Register

        {md_table(overclaim_risks.to_dict("records"), ["risk_id", "risk", "severity", "mitigation", "status_after_m5"])}

        ## 4134 Checklist

        {md_table(checklist.to_dict("records"), ["step_order", "4134_task", "input", "completion_gate"])}

        ## Interpretation

        The 413x route can now move from evidence synthesis into figure
        assembly. The clean narrative is not that a final mechanism has been
        found; it is that a bounded, reproducible local non-affine collective
        observable survived several geometric reductions, while several simple
        low-dimensional reductions failed or remained explicitly outside the
        tested route.

        ## Artifacts

        - `Output/4133_M5_review_before_4134/m5_gate_review.csv`
        - `Output/4133_M5_review_before_4134/main_vs_supplement_figure_candidates.csv`
        - `Output/4133_M5_review_before_4134/claim_storyline_review.csv`
        - `Output/4133_M5_review_before_4134/overclaim_risk_register.csv`
        - `Output/4133_M5_review_before_4134/4134_action_checklist.csv`
        - `Output/4133_M5_review_before_4134/artifact_audit.csv`
        - `Output/4133_M5_review_before_4134/source_map.csv`
        - `Output/4133_M5_review_before_4134/decision.json`
        """
    )
    summary = summary.replace("\n        ", "\n").lstrip()
    (OUT / "M5_review_before_4134.md").write_text(summary, encoding="utf-8")


def main() -> None:
    ensure_dirs()

    decisions = {
        "4130": read_json(ROOT / "Output" / "4130" / "decision.json"),
        "4131": read_json(ROOT / "Output" / "4131" / "decision.json"),
        "4132": read_json(ROOT / "Output" / "4132" / "decision.json"),
        "4133": read_json(ROOT / "Output" / "4133" / "decision.json"),
    }
    claim_registry = read_csv(ROOT / "Output" / "4130" / "claim_strength_registry.csv")
    positive_atlas = read_csv(ROOT / "Output" / "4131" / "positive_phenomenon_atlas.csv")
    negative_atlas = read_csv(ROOT / "Output" / "4132" / "negative_boundary_atlas.csv")
    observation_classes = read_csv(ROOT / "Output" / "4133" / "observation_classes.csv")

    artifacts = artifact_audit(decisions)
    gate_review = build_gate_review(
        decisions=decisions,
        claim_registry=claim_registry,
        positive_atlas=positive_atlas,
        negative_atlas=negative_atlas,
        observation_classes=observation_classes,
        artifacts=artifacts,
    )
    figure_candidates = build_figure_candidates()
    claim_review = build_claim_storyline_review(claim_registry)
    overclaim_risks = build_overclaim_risks()
    checklist = build_4134_action_checklist()

    write_csv_pair(artifacts, "artifact_audit.csv")
    write_csv_pair(gate_review, "m5_gate_review.csv")
    write_csv_pair(figure_candidates, "main_vs_supplement_figure_candidates.csv")
    write_csv_pair(claim_review, "claim_storyline_review.csv")
    write_csv_pair(overclaim_risks, "overclaim_risk_register.csv")
    write_csv_pair(checklist, "4134_action_checklist.csv")

    gate_statuses = gate_review["status"].value_counts().to_dict()
    stop_count = int((gate_review["status"] == "STOP").sum())
    action_count = int(gate_review["status"].isin(["ACTION_REQUIRED_IN_4134", "PASS_WITH_BOUNDARY"]).sum())
    decision = {
        "node": NODE,
        "date": DATE,
        "node_type": "review_gate",
        "upstream_nodes": [
            "4130_definition_and_evidence_registry",
            "4131_robust_positive_phenomenon_atlas",
            "4132_negative_mechanism_boundary_atlas",
            "4133_observation_heterogeneity_map",
        ],
        "data_scope": "all_19_observations_from_existing_4130_4133_outputs",
        "new_experiment_run": False,
        "new_target_or_mechanism_introduced": False,
        "gate_counts": {
            "review_gates": len(gate_review),
            "stop_gates": stop_count,
            "action_or_boundary_gates": action_count,
            "figure_candidate_panels": len(figure_candidates),
            "claim_review_rows": len(claim_review),
            "overclaim_risk_rows": len(overclaim_risks),
        },
        "gate_status_counts": gate_statuses,
        "gate_result": "pass_M5_review_enter_4134_with_actions" if stop_count == 0 else "stop_M5_review_before_4134",
        "primary_actions_for_4134": [
            "build Figure 1 as data and T1-definition orientation",
            "preserve all-19 context before survivor-subset panels",
            "write metadata associations as descriptive only",
            "write propagation as NOT_TESTED",
            "write history as observation-specific rather than universal",
            "write negative mechanism panels as tested reduction failures",
        ],
        "interpretation": (
            "4130-4133 are sufficient to enter 4134 figure-panel construction, "
            "provided the existing boundary wording is retained and Figure 1 is "
            "constructed as a measurement-definition figure rather than a new mechanism."
        ),
        "does_not_prove": [
            "publication-ready final figures are already assembled",
            "a new mechanism has been identified",
            "metadata explains observation failures",
            "propagation has been tested or ruled out",
            "history dependence is universal",
        ],
        "next": ["4134_figure_ready_evidence_panels"],
        "artifacts": [
            "Output/4133_M5_review_before_4134/m5_gate_review.csv",
            "Output/4133_M5_review_before_4134/main_vs_supplement_figure_candidates.csv",
            "Output/4133_M5_review_before_4134/claim_storyline_review.csv",
            "Output/4133_M5_review_before_4134/overclaim_risk_register.csv",
            "Output/4133_M5_review_before_4134/4134_action_checklist.csv",
            "Output/4133_M5_review_before_4134/artifact_audit.csv",
            "Output/4133_M5_review_before_4134/source_map.csv",
            "Output/4133_M5_review_before_4134/decision.json",
            "Output/4133_M5_review_before_4134/M5_review_before_4134.md",
        ],
    }
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2), encoding="utf-8")

    output_names = [
        "m5_gate_review.csv",
        "main_vs_supplement_figure_candidates.csv",
        "claim_storyline_review.csv",
        "overclaim_risk_register.csv",
        "4134_action_checklist.csv",
        "artifact_audit.csv",
        "decision.json",
        "M5_review_before_4134.md",
    ]
    source_map = build_source_map(output_names)
    write_csv_pair(source_map, "source_map.csv")

    write_summary(
        decision=decision,
        gate_review=gate_review,
        figure_candidates=figure_candidates,
        claim_review=claim_review,
        overclaim_risks=overclaim_risks,
        checklist=checklist,
    )

    print(json.dumps(decision, indent=2))
    print(f"Wrote M5 review outputs to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
