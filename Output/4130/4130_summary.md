# Node 4130 Summary

## Question

Can the completed 408x-412x evidence be normalized into a definition dictionary, evidence registry, claim-strength registry, and metadata audit before writing positive/negative atlases?

## Implementation Scope

4130 is a registry/synthesis node. It does not add a mechanism model, does not change the T1 target, and does not rerun old thresholds.

## Registry Counts

| definitions | evidence_rows | claim_rows | metadata_rows | decision_json_sources | summary_only_sources |
| --- | --- | --- | --- | --- | --- |
| 10 | 24 | 8 | 4 | 23 | 1 |

## Evidence Claim Class Counts

| claim_class | count |
| --- | --- |
| BOUNDARY | 9 |
| SUPPORTED_WITH_BOUNDARY | 7 |
| TECHNICAL_PASS | 4 |
| NOT_SUPPORTED | 4 |

## Figure Candidate Counts

| figure_candidate | count |
| --- | --- |
| yes | 13 |
| supplement | 9 |
| no | 2 |

## Main Claim Strength Registry

| claim_id | claim_strength | claim_text | support_nodes | forbidden_stronger_claim | figure_priority |
| --- | --- | --- | --- | --- | --- |
| C1_LOCAL_NONAFFINE_SURVIVAL | SUPPORTED_WITH_BOUNDARY | Local affine deformation is insufficient to remove the transition-linked tangential residual in most observations. | 4081c;4082;4088 | T1 is universal across all observations or causal. | main |
| C2_SCALE_LAG_ROBUST_SURVIVORS | SUPPORTED_WITH_BOUNDARY | Within the 4081c survivor class, T1 survival is robust across nearby local scales and lags. | 4082;4088 | Scale/lag robustness holds for all 19 observations. | main |
| C3_DIFFUSE_TANGENTIAL_DOMINANCE | SUPPORTED_WITH_BOUNDARY | The strongest repeated spatial/timing form is diffuse tangential activity, with edge/core contrast as a bounded secondary structure. | 4084;4085;4088 | A stable edge/core trigger or propagation source is identified. | main |
| C4_SIGNED_EVENT_HETEROGENEITY | BOUNDARY | Signed low-to-high/high-to-low T1 structure exists but is heterogeneous across observations. | 4086;4088 | A universal signed force or mirror law is supported. | supplement |
| C5_NO_SIMPLE_STATE_MOMENT_CLOSURE | NOT_SUPPORTED | A C,dCdt,R-conditioned low-dimensional first/second moment closure is not stable across observations under grouped validation. | 4090;4094 | Stochastic dynamics or all state dependence are impossible. | main |
| C6_NO_EVENT_TIMESTAMP_EXCESS | NOT_SUPPORTED | True transition timestamps do not contain robust near-pre T1 excess beyond same-observation C,dCdt,R-matched controls. | 4100;4105 | Transitions have no special dynamics. | main |
| C7_OBSERVATION_SPECIFIC_HISTORY_BOUNDARY | BOUNDARY | Recent C-R path direction can separate T1 within some observations, but the sign/order is not universal. | 4120;4121;4125 | A robust universal history dependence or causal memory mechanism is supported. | main |
| C8_PROPAGATION_NOT_CONFIRMATORILY_TESTED | NOT_TESTED | Propagation/burst-source mechanisms are not confirmatorily tested because the 4100 event-locality gate failed. | 4100;4105;4125 | No propagation exists. | none |

## Metadata Audit

| metadata_item | claim_or_value | verification_status | allowed_use | disallowed_use |
| --- | --- | --- | --- | --- |
| recording_condition_daytime_dusk | Ob6 and Ob11 daytime; others mainly dusk | UNVERIFIED | descriptive_annotation_only | causal explanation or regime claim |
| observation_index_as_recording_order_proxy | early-observation proxy noted in 4090A | UNVERIFIED | boundary annotation | confirmed batch effect |
| 408x_failure_labels | Ob1/Ob3 fragile boundary; Ob6/Ob8 stable failures | VERIFIED | evidence registry and heterogeneity map | causal recording-condition explanation |
| 4121_opposite_signed_history_groups | negative examples Ob5/Ob8/Ob9; positive examples Ob12/Ob15/Ob17 | VERIFIED | descriptive heterogeneity result | universal history mechanism |

## Quality Checks

```json
{
  "missing_required_terms": [],
  "invalid_evidence_claim_classes": [],
  "invalid_claim_strengths": [],
  "missing_core_sources": [],
  "has_unverified_metadata": true,
  "definition_registry_ok": true,
  "source_registry_ok": true
}
```

## Gate Evaluation

```text
gate_result = pass_4130_registry_ready_with_metadata_boundary
```

The evidence registry, definition dictionary, claim strength registry, and metadata audit are ready for 4131/4132. Metadata-dependent heterogeneity claims must remain descriptive until independently verified.

## What This Supports

- 4131 positive phenomenon atlas can now use fixed definitions.
- 4132 negative boundary atlas can distinguish `NOT_SUPPORTED` from `NOT_TESTED`.
- 4133 must keep unverified metadata as descriptive annotation only.

## What This Does Not Prove

| does_not_prove |
| --- |
| new mechanism |
| causal explanation |
| metadata regime |
| universal history dependence |
| publication-ready figures |

## Next Node

| next |
| --- |
| 4131_robust_positive_phenomenon_atlas |
| 4132_negative_mechanism_boundary_atlas |

## Artifacts

- `Output/4130/definition_dictionary.csv`
- `Output/4130/evidence_registry.csv`
- `Output/4130/evidence_registry.json`
- `Output/4130/claim_strength_registry.csv`
- `Output/4130/metadata_source_audit.csv`
- `Output/4130/source_map.csv`
- `Output/4130/claim_dependency_graph.md`
- `Output/4130/route_timeline.md`
- `Output/4130/decision.json`
- `Output/4130/4130_summary.md`
