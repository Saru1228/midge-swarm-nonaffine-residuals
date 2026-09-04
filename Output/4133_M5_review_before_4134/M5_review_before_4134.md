# M5 Review Before 4134

## Purpose

This is a review node between `4133_observation_heterogeneity_map` and
`4134_figure_ready_evidence_panels`. It does not add a new mechanism,
residual target, threshold, or predictive model. Its only job is to
decide whether the completed 4130-4133 evidence can be safely converted
into paper-ready figures.

## Gate Result

```text
gate_result = pass_M5_review_enter_4134_with_actions
latest_completed_node = M5_REVIEW_before_4134
next_node = 4134_figure_ready_evidence_panels
```

## Main Decision

The review passes with explicit 4134 actions. The evidence chain is
ready to enter figure-panel construction, but 4134 must treat Figure 1
as a definition/data-orientation figure and must keep metadata,
propagation, history, and negative mechanism boundaries explicit.

## Gate Review

| gate_id | criterion | status | evidence | action_before_4134 |
| --- | --- | --- | --- | --- |
| M5_G1 | Upstream gates passed | PASS | 4130=pass_4130_registry_ready_with_metadata_boundary; 4131=pass_4131_positive_atlas_ready_with_secondary_boundaries; 4132=pass_4132_negative_boundary_atlas_ready; 4133=pass_4133_heterogeneity_map_ready_with_metadata_boundary | Enter figure planning only if every upstream synthesis node passed. |
| M5_G2 | Definition registry is frozen | PASS | definition_rows=10; missing_required_terms=none | Use the 4130 T1 and variable definitions without introducing a new residual target. |
| M5_G3 | Positive atlas has bounded primary positives | PASS | primary_positive_rows=3; secondary_or_bounded_rows=2 | Main figures may show common T1 survival, scale/lag robustness, and diffuse tangential activity. |
| M5_G4 | Negative atlas separates tested failures from open routes | PASS | not_supported_rows=2; not_tested_rows=1 | Write C,dCdt,R and event-locality as tested reductions that failed; write propagation as not tested. |
| M5_G5 | Observation heterogeneity remains all-19 and descriptive | PASS_WITH_BOUNDARY | observation_class_rows=19; metadata_status={'raw_column_0_4_metadata': 'VERIFIED_FROM_RAW_COLUMNS_0_AND_4', 'recording_condition_daytime_dusk': 'UNVERIFIED', 'observation_index_as_order_proxy': 'UNVERIFIED'}; recording_condition_not_used_as_causal=True | Keep Ob6/Ob8 and daytime/dusk/order-proxy explanations as annotations, not causal claims. |
| M5_G6 | Existing figure artifacts are available | PASS | figure_artifacts=13; missing_or_empty=0 | Use existing 4131-4133 figures as evidence sources; rebuild publication panels where needed. |
| M5_G7 | Figure 1 concept/data panels are not yet final artifacts | ACTION_REQUIRED_IN_4134 | 4130-4133 provide definitions and evidence, but no final 3D snapshot / affine schematic / T1 definition panel set. | Build Figure 1 as definition and data orientation only; do not let it imply a new mechanism. |
| M5_G8 | Overclaim guards are explicit | PASS | claim_registry_forbidden_wording_complete=True; negative_atlas_forbidden_wording_complete=True | Every 4134 caption must include allowed interpretation and forbidden stronger interpretation. |

## Main Figure Candidate Count

```text
total_candidate_panels = 16
main_or_main_descriptive_candidate_panels = 15
panels_needing_4134_assembly = 7
```

## Figure Candidates Needing Assembly

| figure_id | panel_id | panel_question | source_status | 4134_action | boundary_guard |
| --- | --- | --- | --- | --- | --- |
| Figure 1 | 1A | What data are being reduced? | needs_assembly | Select one representative 3D trajectory snapshot and label it as data orientation only. | Do not infer mechanism, interaction, or recording-condition causality from the snapshot. |
| Figure 1 | 1B | What is removed by global/local affine reduction? | concept_panel_to_build | Draw a compact schematic distinguishing global affine, local affine, and residual components. | Do not present the schematic as a fitted physical model. |
| Figure 1 | 1C | What is the frozen T1 observable? | concept_panel_to_build | Convert the frozen T1 definition into a visual equation/flow panel. | Do not rename or redefine the target in 4134. |
| Figure 1 | 1D | How does the event-conditioned time profile look? | needs_assembly | Build one example trace with clear labels: event, pre window, matched control/null. | Avoid choosing an example that hides failure observations. |
| Figure 2 | 2A | Does T1 survive local affine subtraction across all observations? | needs_assembly | Render an all-19 forest/strip panel with Ob1, Ob3, Ob6, and Ob8 retained. | Do not write universal survival or omit stable failures. |
| Figure 2 | 2C | Which observations are robust, fragile, or failures? | needs_assembly | Draw the observation class strip beside the all-19 evidence panel. | Do not treat failure classes as artifacts unless independently verified. |
| Figure 5 | 5C | Which observations define the strongest positive and failure cases? | needs_assembly | Build a compact exemplar panel only if it does not hide all-19 heterogeneity. | Do not let examples substitute for the all-19 result. |

## Claim Storyline Review

| claim_id | claim_strength | recommended_4134_location | m5_status | forbidden_stronger_claim |
| --- | --- | --- | --- | --- |
| C1_LOCAL_NONAFFINE_SURVIVAL | SUPPORTED_WITH_BOUNDARY | Figure 2 | MAIN_ALLOWED_WITH_BOUNDARY_WORDING | T1 is universal across all observations or causal. |
| C2_SCALE_LAG_ROBUST_SURVIVORS | SUPPORTED_WITH_BOUNDARY | Figure 2 | MAIN_ALLOWED_WITH_BOUNDARY_WORDING | Scale/lag robustness holds for all 19 observations. |
| C3_DIFFUSE_TANGENTIAL_DOMINANCE | SUPPORTED_WITH_BOUNDARY | Figure 3 | MAIN_ALLOWED_WITH_BOUNDARY_WORDING | A stable edge/core trigger or propagation source is identified. |
| C4_SIGNED_EVENT_HETEROGENEITY | BOUNDARY | Supplement or Figure 3C boundary annotation | SUPPLEMENT_OR_BOUNDARY_ONLY | A universal signed force or mirror law is supported. |
| C5_NO_SIMPLE_STATE_MOMENT_CLOSURE | NOT_SUPPORTED | Figure 4A | MAIN_ALLOWED_WITH_BOUNDARY_WORDING | Stochastic dynamics or all state dependence are impossible. |
| C6_NO_EVENT_TIMESTAMP_EXCESS | NOT_SUPPORTED | Figure 4B | MAIN_ALLOWED_WITH_BOUNDARY_WORDING | Transitions have no special dynamics. |
| C7_OBSERVATION_SPECIFIC_HISTORY_BOUNDARY | BOUNDARY | Figure 4C | MAIN_ALLOWED_WITH_BOUNDARY_WORDING | A robust universal history dependence or causal memory mechanism is supported. |
| C8_PROPAGATION_NOT_CONFIRMATORILY_TESTED | NOT_TESTED | Limitations / remaining open mechanism space | DO_NOT_MAIN_FIGURE_AS_RESULT | No propagation exists. |

## Overclaim Risk Register

| risk_id | risk | severity | mitigation | status_after_m5 |
| --- | --- | --- | --- | --- |
| R1 | T1 is described as universal or causal. | high | Always retain 'most observations', show all-19 context, and name failure/boundary observations. | guarded |
| R2 | Tested C,dCdt,R failure is upgraded into a claim that stochastic dynamics are impossible. | high | Write only that the tested first/second moment closure did not provide a stable reduction. | guarded |
| R3 | Event-locality failure is written as absence of transition dynamics. | high | Write only that true timestamps add no robust near-pre excess beyond matched C,dCdt,R state. | guarded |
| R4 | Propagation is written as disproven. | high | Mark propagation as NOT_TESTED and place it in remaining open mechanism space. | guarded |
| R5 | History effect is written as universal memory or hysteresis. | high | Write observation-specific history separation and show sign/order heterogeneity. | guarded |
| R6 | Daytime/dusk or observation order is written as a causal explanation. | medium_high | Label metadata as descriptive only; do not use it as a regime explanation. | guarded |
| R7 | Survivor-only panels hide negative observations. | high | Put all-19 survival/classification before survivor-subset robustness. | guarded |
| R8 | Concept figure is mistaken for a tested physical model. | medium | Caption Figure 1 as measurement definition and data orientation only. | guarded |

## 4134 Checklist

| step_order | 4134_task | input | completion_gate |
| --- | --- | --- | --- |
| 1 | Create figure_source_map.csv from the M5 figure candidate table. | Output/4133_M5_review_before_4134/main_vs_supplement_figure_candidates.csv | Every panel has question, metric/source, sample size or scope, baseline/null, interpretation, and guard. |
| 2 | Build Figure 1 as data and definition orientation. | Output/4130/definition_dictionary.csv; raw trajectory source; 4088/4131 examples | No new mechanism or residual target is introduced. |
| 3 | Assemble Figure 2 around all-19 T1 survival before survivor-subset robustness. | Output/4131/observation_positive_coverage_matrix.csv; Output/4133/observation_classes.csv | Failure and fragile observations remain visible. |
| 4 | Assemble Figure 3 around diffuse tangential activity and timing boundaries. | Output/4131/figures/4131_spatial_phase_positive_summary.png; Output/4132/negative_boundary_atlas.csv | Diffuse tangential activity is primary; edge/core and signed structure are bounded. |
| 5 | Assemble Figure 4 as the mechanism-boundary figure. | Output/4132/figures/*.png; Output/4131/figures/4131_history_secondary_positive.png | Negative panels are written as tested reduction failures, not nonexistence claims. |
| 6 | Assemble Figure 5 as the observation heterogeneity figure. | Output/4133/figures/*.png; Output/4133/heterogeneity_associations.csv | Metadata associations remain descriptive and all-19 evidence remains visible. |
| 7 | Draft figure captions and panel metadata. | M5 claim storyline review and overclaim risk register | Each caption states what it supports and what it does not prove. |

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
