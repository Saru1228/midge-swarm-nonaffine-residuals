"""4070 bounded result and negative mechanism map.

This node is a synthesis experiment. It does not reprocess trajectories.
It converts the completed 4001-4066 EGRT branch into machine-readable
mechanism status tables and concise Markdown summaries.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4070"


NODE = "4070_bounded_result_and_negative_mechanism_map"
DATE = "2026-08-25"


COLUMNS = [
    "mechanism_class",
    "node",
    "question",
    "observable",
    "baseline_or_null",
    "main_result",
    "robustness",
    "gate_result",
    "claim_strength",
    "current_status",
    "interpretation",
    "next_action",
    "provenance",
]


MECHANISM_ROWS = [
    {
        "mechanism_class": "global_affine_geometry",
        "node": "4001",
        "question": "Does the 3045c velocity signal survive translation plus global affine deformation?",
        "observable": "affine-residual velocity variables: speed_rms, velocity_cov_trace, mean_speed, tangential_speed_mean",
        "baseline_or_null": "translation + global affine fit; shifted-event null",
        "main_result": "4/4 direction-surviving variables remain in affine residual; median affine_resid/raw abs ratio = 0.9554; n_ob=19; n_events=1471",
        "robustness": "full 19-observation original 4001 screen, but not yet frozen against local-affine or independent replication gates",
        "gate_result": "pass",
        "claim_strength": "supported_descriptive",
        "current_status": "surviving_target_candidate",
        "interpretation": "Ordinary global affine geometry is insufficient for the transition-aligned velocity signal.",
        "next_action": "Freeze target residual metrics in 4072, freeze null hierarchy in 4073, then replicate in 4071 and test local-affine closure in 408x.",
        "provenance": "Output/4001/4001_summary.md; Output/4001/tables/egrt_decision_summary.csv",
    },
    {
        "mechanism_class": "residual_spatial_structure",
        "node": "4002A",
        "question": "What kind of affine-residual velocity structure remains?",
        "observable": "residual intensity, edge/core, radial, tangential residual families",
        "baseline_or_null": "4001 affine residual; shifted-event null",
        "main_result": "6 variables survive: 2 residual intensity, 2 edge/core, 1 radial, 1 tangential; residual order does not survive",
        "robustness": "full 19-observation screen under shifted-event nulls",
        "gate_result": "pass",
        "claim_strength": "supported_descriptive",
        "current_status": "residual_has_spatial_structure",
        "interpretation": "The residual is not simply global alignment; it includes spatial redistribution and intensity structure.",
        "next_action": "Use 4072 taxonomy to restrict these families to primary metrics before new tests.",
        "provenance": "Output/4002A/4002A_summary.md; Output/4002A/tables/egrt_decision_summary.csv",
    },
    {
        "mechanism_class": "edge_core_timing_mechanism",
        "node": "4002B",
        "question": "Does edge/core residual redistribution appear in clear timing windows?",
        "observable": "pretrigger, event/post, and follow-window edge/core residual variables",
        "baseline_or_null": "timing-window shifted-event null",
        "main_result": "n_pretrigger_variables=0; n_event_or_post_variables=0; n_follow_variables=0",
        "robustness": "timing robustness audit after 4002A",
        "gate_result": "fail",
        "claim_strength": "not_supported",
        "current_status": "excluded_as_timing_trigger",
        "interpretation": "Edge/core residual redistribution is not supported as a timing-robust trigger or event-window mechanism.",
        "next_action": "Keep only as broad descriptive contrast unless a new event-free/timing-independent definition appears.",
        "provenance": "Output/4002B/4002B_summary.md; Output/4002B/tables/egrt_decision_summary.csv",
    },
    {
        "mechanism_class": "local_pair_cumulant",
        "node": "4010",
        "question": "Do local neighbor residual correlations survive a shell-conditioned one-fish baseline?",
        "observable": "kNN residual alignment and speed/radial/tangential covariance, observed and empirical-cumulant forms",
        "baseline_or_null": "one-fish conditional baseline; shifted-event null",
        "main_result": "0 empirical-cumulant survivors; 0 observed-pair survivors; 0 one-fish-baseline survivors over 19 observations and 1471 events",
        "robustness": "full 19-observation cumulant/factorization audit",
        "gate_result": "fail",
        "claim_strength": "not_supported",
        "current_status": "local_knn_cumulant_route_paused",
        "interpretation": "The transition-linked residual signal is not currently explained by simple local observed-pair or cumulant variables.",
        "next_action": "Do not reopen local-pair cumulants without a new residual target or geometry-matched theoretical reason.",
        "provenance": "Output/4010/4010_summary.md; Output/4010/tables/egrt_decision_summary.csv",
    },
    {
        "mechanism_class": "one_individual_residual_redistribution",
        "node": "4020/4020B",
        "question": "Do one-fish residual states redistribute consistently across core/mid/edge?",
        "observable": "one-fish shell residual speed, radial/tangential state, and high-residual fish location variables",
        "baseline_or_null": "single-observation shifted-event nulls",
        "main_result": "Ob1 passes with 2 variables; Ob2 passes with 3 variables; Ob3 passes with 0 variables; surviving variables differ between Ob1 and Ob2",
        "robustness": "selective single-observation replication only; cross-observation variable identity unstable",
        "gate_result": "boundary",
        "claim_strength": "suggestive_unstable",
        "current_status": "bounded_dataset_heterogeneous_signal",
        "interpretation": "One-individual residual redistribution may exist in some observations but is not stable enough to be a main mechanism.",
        "next_action": "Do not expand to all 19 observations unless 4072 freezes a specific target family with a clear reason.",
        "provenance": "Output/4020/4020_summary.md; Output/4020B/4020B_summary.md",
    },
    {
        "mechanism_class": "coarse_residual_state_transition",
        "node": "4030",
        "question": "Do coarse residual high/low bins modulate compact-state transition probability?",
        "observable": "high/low residual variable bins versus compact-state up/down transition probabilities",
        "baseline_or_null": "shifted-bin null in Ob3 pilot",
        "main_result": "0 surviving variables; top transition modulation gap = 0.0202 for top_tangential_radius_mean_z but real-minus-null = -0.002577; p=0.6154",
        "robustness": "single-observation Ob3 pilot following mixed 4020/4020B result",
        "gate_result": "fail",
        "claim_strength": "not_supported_pilot",
        "current_status": "coarse_state_route_not_rescued",
        "interpretation": "Simple residual high/low bins do not rescue the unstable one-fish redistribution branch.",
        "next_action": "Do not use coarse residual bins as the next mechanism line; any stochastic line should restart from 4090 mean-vs-variance after metric freeze.",
        "provenance": "Output/4030/Ob3/4030_summary.md; Output/4030/Ob3/tables/egrt_decision_summary.csv",
    },
    {
        "mechanism_class": "interaction_history_representation",
        "node": "4051",
        "question": "Can transition-centered trajectories be converted into nondegenerate multilayer interaction-history graphs?",
        "observable": "event graph layers, nodes, identity coverage, edge-type coverage",
        "baseline_or_null": "construction smoke test, no mechanism null",
        "main_result": "28/28 Ob1 events built; median 21 layers; median 1942 nodes; identity coverage = 0.960; 3 non-identity edge types",
        "robustness": "Ob1 construction feasibility only",
        "gate_result": "method_pass",
        "claim_strength": "method_supported",
        "current_status": "representation_viable_not_mechanism",
        "interpretation": "Graph history is a usable representation, but construction success alone is not evidence for interaction mechanism.",
        "next_action": "Keep graph tools for later 411x only after target residual metrics are frozen.",
        "provenance": "Output/4051/4051_summary.md; idea/4xxx_EGRT_route_map.md",
    },
    {
        "mechanism_class": "shifted_event_graph_signal",
        "node": "4052",
        "question": "Do real transition-window graphs differ from shifted-event null graphs?",
        "observable": "persistent pair count and residual-speed coactivation graph metrics",
        "baseline_or_null": "shifted-event graph nulls",
        "main_result": "2 metrics pass: persistent_pair_count and edges_residual_speed_coactivation; raw graph size and kNN count do not pass",
        "robustness": "Ob1 pilot with 28 real events and shifted-event nulls",
        "gate_result": "boundary_pass_to_reducibility",
        "claim_strength": "suggestive_screen",
        "current_status": "graph_signal_without_mechanism",
        "interpretation": "Some graph signals exceed shifted-event nulls, but this supports reducibility testing, not pair-rule claims.",
        "next_action": "Do not interpret as interaction until 411x tests graph-level stability beyond geometry and metric freeze.",
        "provenance": "Output/4052/4052_summary.md; idea/4xxx_EGRT_route_map.md",
    },
    {
        "mechanism_class": "graph_core_reducibility",
        "node": "4053",
        "question": "Does a residual graph core remain after cutting proximity scaffold and one-frame dyads?",
        "observable": "core2/core3 residual alignment, speed, edge, and pair fractions",
        "baseline_or_null": "shifted-event graph nulls after cutting",
        "main_result": "1 passing metric: core2_alignment_pair_fraction_of_alignment_pairs; no strict core3 metric passes",
        "robustness": "Ob1 pilot; normalized loose-core signal only",
        "gate_result": "boundary",
        "claim_strength": "boundary",
        "current_status": "strict_pair_core_not_supported",
        "interpretation": "A loose residual-alignment core appears, but not enough to justify motif or stable pair-core claims.",
        "next_action": "Route only to threshold/density robustness; otherwise pause pair-core mechanism.",
        "provenance": "Output/4053/4053_summary.md; Output/4053/tables/egrt_decision_summary.csv",
    },
    {
        "mechanism_class": "graph_core_threshold_density",
        "node": "4053b",
        "question": "Does the loose core2 residual-alignment signal survive threshold and density controls?",
        "observable": "core2_alignment_pair_fraction_of_alignment_pairs at q=0.80,0.85,0.90",
        "baseline_or_null": "shifted null and per-layer density-preserving alignment shuffle",
        "main_result": "q=0.85 passes shifted and density-preserving nulls; q=0.80 and q=0.90 fail",
        "robustness": "threshold-sensitive Ob1 pilot",
        "gate_result": "boundary",
        "claim_strength": "threshold_sensitive_boundary",
        "current_status": "pair_core_mechanism_paused",
        "interpretation": "The graph-core signal is too threshold-sensitive for motif claims.",
        "next_action": "Do not route to motif classification; keep graph as later network-level representation only.",
        "provenance": "Output/4053b/4053b_summary.md; Output/4053b/tables/egrt_decision_summary.csv",
    },
    {
        "mechanism_class": "mesoscopic_residual_field",
        "node": "4060",
        "question": "Does the residual signal appear at a broader mesoscopic field scale?",
        "observable": "near/mid/long residual alignment and speed cofluctuation field-profile metrics",
        "baseline_or_null": "shifted-event residual-field nulls",
        "main_result": "0 passing metrics; 0 passing long-range metrics; closest far_minus_near_alignment_excess p=0.1515",
        "robustness": "Ob1 pilot with 28 real events and 32 shifted-event null replicates",
        "gate_result": "fail",
        "claim_strength": "not_supported_pilot",
        "current_status": "stationary_mesoscopic_field_unsupported",
        "interpretation": "Current stationary residual-field observables do not rescue the mechanism branch.",
        "next_action": "Do not claim mesoscopic field mechanism; transient propagation remains separate and can only be tested after metric freeze.",
        "provenance": "Output/4060/4060_summary.md; Output/4060/tables/egrt_decision_summary.csv",
    },
    {
        "mechanism_class": "bounded_model_criticism",
        "node": "4066",
        "question": "What should 4xxx claim after the mesoscopic-field pilot also fails?",
        "observable": "integrated evidence across affine residual, local-pair, graph-core, coarse-state, and mesoscopic-field branches",
        "baseline_or_null": "synthesis of prior EGRT gates",
        "main_result": "Geometry-resistant residual velocity remains; tested simple mechanism routes are not supported.",
        "robustness": "synthesis node based on 4001-4060 outputs",
        "gate_result": "synthesis",
        "claim_strength": "bounded_claim",
        "current_status": "ready_for_4070_mechanism_map",
        "interpretation": "The strongest current product is a bounded result plus negative mechanism map.",
        "next_action": "Generate 4070 map, then freeze metrics/nulls before cross-dataset replication and local-affine testing.",
        "provenance": "Output/4066/4066_summary.md; idea/4066_4xxx_synthesis_without_mesoscopic_field_mechanism.md",
    },
]


SURVIVING_CLAIMS = [
    {
        "claim": "Affine-residual velocity organization survives the global affine geometry baseline.",
        "strength": "supported_descriptive",
        "support": "4001 retains 4/4 velocity direction variables in the affine residual with median residual/raw ratio 0.9554 over 19 observations and 1471 events.",
        "limits": "Not yet tested against local affine deformation, frozen metric taxonomy, or event-free windows.",
    },
    {
        "claim": "The affine-residual signal has spatial structure rather than only global residual alignment.",
        "strength": "supported_descriptive",
        "support": "4002A finds residual intensity, edge/core, radial, and tangential survivors; residual order does not pass.",
        "limits": "4002B does not support a timing-robust edge/core trigger mechanism.",
    },
    {
        "claim": "Interaction-history graphs are technically viable as a representation.",
        "strength": "method_supported",
        "support": "4051 builds nondegenerate Ob1 transition graphs for all 28 events.",
        "limits": "Graph construction does not imply biological interaction; 4053/4053b block pair-core and motif claims.",
    },
]


EXCLUDED_OR_BOUNDED = [
    {
        "claim": "Edge/core residual redistribution is a timing-robust trigger.",
        "status": "not_supported",
        "evidence": "4002B: pretrigger=0, event/post=0, follow=0.",
    },
    {
        "claim": "Local kNN observed-pair or empirical-cumulant variables explain the residual signal.",
        "status": "not_supported",
        "evidence": "4010: 0 empirical-cumulant, observed-pair, or one-fish-baseline survivors.",
    },
    {
        "claim": "One-fish residual redistribution is a stable cross-observation mechanism.",
        "status": "bounded_unstable",
        "evidence": "4020/4020B: Ob1 and Ob2 pass with different variables; Ob3 fails.",
    },
    {
        "claim": "Simple coarse residual high/low states modulate compact-state transitions.",
        "status": "not_supported_pilot",
        "evidence": "4030 Ob3: 0 surviving variables.",
    },
    {
        "claim": "A stable graph pair-core or motif mechanism has been identified.",
        "status": "not_supported",
        "evidence": "4053: only loose core2 alignment passes; 4053b: q=0.85 only, q=0.80/0.90 fail.",
    },
    {
        "claim": "A stationary mesoscopic residual field explains the residual signal.",
        "status": "not_supported_pilot",
        "evidence": "4060: 0 passing metrics and 0 passing long-range metrics.",
    },
]


OPEN_SPACE = [
    {
        "class": "local_heterogeneous_affine_geometry",
        "why_open": "4001 used global affine geometry; spatially varying local affine deformation has not been subtracted.",
        "next_test": "4080 feasibility, then 4081 global-vs-local geometry ladder.",
    },
    {
        "class": "local_nonaffine_reorganization",
        "why_open": "If local affine deformation cannot explain the residual, D2min-style non-affine diagnostics become meaningful.",
        "next_test": "4081 major gate B, then 4082/4083 scale and cross-dataset robustness.",
    },
    {
        "class": "state_dependent_stochasticity",
        "why_open": "Prior drift/Langevin closures were weak, but conditional variance or multiplicative noise was not cleanly separated from conditional mean.",
        "next_test": "4090 conditional mean-vs-variance after residual target freeze.",
    },
    {
        "class": "transient_spatiotemporal_propagation",
        "why_open": "4060 only tested stationary field-like profiles; transient lagged reorganization remains distinct.",
        "next_test": "4100-4104 only after a frozen residual/non-affine activity variable.",
    },
    {
        "class": "network_level_organization",
        "why_open": "405x weakens fixed pair-core claims but does not rule out stable network-level statistics or spectral scales.",
        "next_test": "4110-4114 only after target residual observable freeze and geometry controls.",
    },
    {
        "class": "measurement_finiteN_membership_artifact",
        "why_open": "Center motion and residual signals can be affected by membership changes, velocity estimation, finite-N averaging, and event selection.",
        "next_test": "4073 baseline/null registry and 4074 event-free audit.",
    },
]


DECISION = {
    "node": NODE,
    "question": "What survived geometry in 4001-4066, which mechanism explanations failed, and what can be tested next without reopening metric search?",
    "result": "pass",
    "interpretation": "The 4xxx chain can be written as a bounded model-criticism result with a surviving affine-residual velocity target and multiple excluded or bounded mechanism stories.",
    "target_sentence": (
        "After removing translation plus global affine deformation, the transition-aligned "
        "affine-residual velocity observables speed_rms, velocity_cov_trace, mean_speed, "
        "and tangential_speed_mean remain robust under the original 4001 shifted-event "
        "screen across 19 observations and 1471 events; this target still requires "
        "4072 metric freeze, 4073 null freeze, 4071 cross-dataset replication, and 408x local-affine testing."
    ),
    "gate": "Can write one strict target sentence with explicit baseline, residual observable, and robustness caveat.",
    "gate_evaluation": "passed_with_caveat",
    "caveat": "The target is strict enough to continue foundation work, but not yet strict enough for local-affine or biological mechanism claims.",
    "next": [
        "4072_residual_observable_taxonomy",
        "4073_null_and_baseline_registry",
        "4071_cross_dataset_baseline_audit",
        "4074_event_free_vs_event_conditioned_audit",
    ],
    "frozen_parameters": {
        "full_dataset_default": False,
        "replication_before_full_set": "Ob1 -> Ob2/Ob3 -> full 19 only after predefined gates",
        "primary_next_rule": "Do not enter 408x until 4072 and 4073 are complete.",
    },
}


def ensure_output_dir() -> None:
    (OUT / "tables").mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in columns})


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def md_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = []
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("| " + " | ".join(["---"] * len(columns)) + " |")
    for row in rows:
        vals = []
        for col in columns:
            val = str(row.get(col, "")).replace("\n", " ").replace("|", "\\|")
            vals.append(val)
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def write_config() -> None:
    text = dedent(
        f"""\
        node: {NODE}
        date: {DATE}
        node_type: synthesis
        input_nodes:
          - 4001
          - 4002A
          - 4002B
          - 4010
          - 4020
          - 4020B
          - 4030
          - 4051
          - 4052
          - 4053
          - 4053b
          - 4060
          - 4066
        no_trajectory_reprocessing: true
        output_policy:
          - mechanism_map.csv
          - mechanism_map.json
          - surviving_claims.md
          - excluded_or_bounded_claims.md
          - open_explanation_space.md
          - decision.json
          - 4070_summary.md
        """
    )
    (OUT / "config.yaml").write_text(text, encoding="utf-8")


def write_surviving_claims() -> None:
    rows = [
        {
            "Claim": item["claim"],
            "Strength": item["strength"],
            "Support": item["support"],
            "Limits": item["limits"],
        }
        for item in SURVIVING_CLAIMS
    ]
    text = "# 4070 Surviving Claims\n\n"
    text += DECISION["target_sentence"] + "\n\n"
    text += md_table(rows, ["Claim", "Strength", "Support", "Limits"]) + "\n"
    (OUT / "surviving_claims.md").write_text(text, encoding="utf-8")


def write_excluded_claims() -> None:
    rows = [
        {"Claim": item["claim"], "Status": item["status"], "Evidence": item["evidence"]}
        for item in EXCLUDED_OR_BOUNDED
    ]
    text = "# 4070 Excluded Or Bounded Claims\n\n"
    text += (
        "These are not failures of the research program. They define which simple "
        "mechanism stories should not be used as the current 4xxx explanation.\n\n"
    )
    text += md_table(rows, ["Claim", "Status", "Evidence"]) + "\n"
    (OUT / "excluded_or_bounded_claims.md").write_text(text, encoding="utf-8")


def write_open_space() -> None:
    rows = [
        {
            "Open class": item["class"],
            "Why still open": item["why_open"],
            "Next test": item["next_test"],
        }
        for item in OPEN_SPACE
    ]
    text = "# 4070 Open Explanation Space\n\n"
    text += (
        "4070 does not start a new mechanism search. It names the explanation "
        "classes that remain open after the completed gates and ties each one to "
        "a specific future node.\n\n"
    )
    text += md_table(rows, ["Open class", "Why still open", "Next test"]) + "\n"
    (OUT / "open_explanation_space.md").write_text(text, encoding="utf-8")


def write_summary() -> None:
    pass_rows = [r for r in MECHANISM_ROWS if r["gate_result"] in {"pass", "method_pass"}]
    fail_rows = [r for r in MECHANISM_ROWS if r["gate_result"] == "fail"]
    boundary_rows = [r for r in MECHANISM_ROWS if "boundary" in r["gate_result"]]

    text = dedent(
        f"""\
        # Node 4070 Summary

        ## Question

        What survived geometry in the 4001-4066 chain, which mechanism explanations failed, and what can be tested next without reopening metric search?

        ## Why this node exists

        4066 concluded that the 4xxx branch should pause mechanism search. 4070 converts that branch into a bounded result map: a surviving target phenomenon, excluded or bounded mechanism stories, and a small set of open explanation classes.

        ## Data

        No raw trajectory data were reprocessed. This synthesis uses existing summaries and EGRT decision tables from `Output/4001` through `Output/4066`.

        ## Frozen parameters

        This node freezes the routing order, not the residual metric set:

        ```text
        4070 -> 4072 -> 4073 -> 4071 -> 4074 -> M0 review
        ```

        The metric and null freeze must happen in 4072 and 4073 before cross-dataset replication in 4071.

        ## Baseline

        The main surviving baseline comparison is the 4001 translation plus global affine geometry subtraction.

        ## Null model

        The branch primarily used shifted-event nulls, with additional density-preserving checks in 4053b. 4073 must convert these into a formal null/baseline registry.

        ## Primary metrics

        Current target sentence:

        > {DECISION["target_sentence"]}

        This is strict enough to continue foundation work, but still has a caveat: local affine geometry and event-free occurrence have not yet been tested.

        ## Results

        - Supported or method-supported entries: {len(pass_rows)}
        - Boundary entries: {len(boundary_rows)}
        - Failed mechanism entries: {len(fail_rows)}
        - Total mechanism-map entries: {len(MECHANISM_ROWS)}

        ## Dataset-wise replication

        4070 does not run replication. The strongest current full-series result is 4001 over 19 observations. The unstable single-observation branch is 4020/4020B, where Ob1 and Ob2 pass with different variables and Ob3 fails.

        ## Gate evaluation

        `passed_with_caveat`

        The branch can be stated as a bounded target:

        ```text
        After removing translation plus global affine deformation, a transition-aligned affine-residual velocity signal remains.
        ```

        But it cannot yet be stated as:

        ```text
        This residual is local-nonaffine, stochastic, propagating, network-driven, or biological-causal.
        ```

        ## What this rules out

        See `excluded_or_bounded_claims.md`. Current excluded or bounded claims include timing-trigger edge/core redistribution, local kNN cumulants, stable one-fish redistribution, coarse residual state transition modulation, stable graph pair-core/motifs, and stationary mesoscopic residual fields.

        ## What this does NOT prove

        4070 does not prove a new mechanism. It does not prove local non-affinity, multiplicative noise, propagation, network causality, or a biological control rule.

        ## Decision

        `{DECISION["result"]}`: proceed to foundation freeze.

        ## Next node

        ```text
        4072_residual_observable_taxonomy
        4073_null_and_baseline_registry
        4071_cross_dataset_baseline_audit
        4074_event_free_vs_event_conditioned_audit
        ```

        ## Artifacts

        - `Output/4070/mechanism_map.csv`
        - `Output/4070/mechanism_map.json`
        - `Output/4070/surviving_claims.md`
        - `Output/4070/excluded_or_bounded_claims.md`
        - `Output/4070/open_explanation_space.md`
        - `Output/4070/decision.json`
        """
    )
    (OUT / "4070_summary.md").write_text(text, encoding="utf-8")


def main() -> None:
    ensure_output_dir()
    write_config()
    write_csv(OUT / "mechanism_map.csv", MECHANISM_ROWS, COLUMNS)
    write_csv(OUT / "tables" / "mechanism_map.csv", MECHANISM_ROWS, COLUMNS)
    write_json(OUT / "mechanism_map.json", MECHANISM_ROWS)
    write_json(OUT / "decision.json", DECISION)
    write_surviving_claims()
    write_excluded_claims()
    write_open_space()
    write_summary()
    print(f"Wrote 4070 synthesis outputs to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
