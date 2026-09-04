# Node 4131 Robust Positive Phenomenon Atlas

## Question

If only the robust positive evidence is retained, what does the T1
phenomenon look like?

## Gate Result

```text
gate_result = pass_4131_positive_atlas_ready_with_secondary_boundaries
```

## Main Interpretation

The positive result is a bounded atlas, not a mechanism claim. T1
survival after local affine removal is common across observations,
robustness is high inside the survivor class, and the clearest repeated
spatial/activity form is diffuse tangential activity. Edge/core contrast
and recent-history separation remain secondary bounded positives.

## Primary Metrics

| t1_survival_any_k_observations | t1_survival_both_k_observations | total_observations | scale_lag_robust_observations | scale_lag_tested_survivor_observations | diffuse_all_tangential_gate_observations | diffuse_all_tangential_tested_observations | all_tangential_near_pre_gate_observations | history_real_beats_shuffle_median_observations | history_direction_consistency_fraction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 15 | 14 | 19 | 14 | 15 | 13 | 14 | 8 | 14 | 0.5263 |

## Positive Phenomenon Atlas

| phenomenon_name | primary_metric | observation_coverage | robustness | boundary_cases | atlas_role |
| --- | --- | --- | --- | --- | --- |
| global_affine_residual_survival | 4/4 raw direction survivors retained; median affine/raw abs ratio 0.9554 | 4/4 source directions in 4001 summary | supported with boundary; source is summary-only | not yet a local T1 mechanism | upstream_motivation |
| local_nonaffine_t1_survival | 15/19 any-k survival; 14/19 both-k survival | 15/19 | common across observations, not universal | Ob1/Ob3/Ob6/Ob8 fail; Ob4 one-k survivor | primary_positive |
| scale_lag_robust_survivor_class | 14/15 robust scale and timing | 14/15 survivor observations | high inside survivor class | Ob4 fragile_or_boundary | primary_positive |
| diffuse_tangential_activity | all_tangential gates 13/14; near_pre gates 8/14 | 13/14 | repeated spatially; phase timing is moderate | near-pre timing is 8/14, not all-observation | primary_positive |
| edge_core_contrast_secondary | shell_edge_minus_core gates 9/14; target near-transition gate total 2 | 9/14 | moderate as spatial contrast, weak as phase-localized profile | target has no stable majority phase | secondary_positive |
| observation_specific_history_separation | 19/19 sufficient pairs; 14/19 beat shuffle median; direction consistency 0.526 | 19/19 sufficient pairs; 14/19 beat median shuffle null | observation-specific; sign/order fails as a universal rule | positive and negative signed groups are split 9 vs 10 | secondary_bounded_positive |

## Positive Claims Imported From 4130

| claim_id | claim_strength | 4131_role | support_nodes | forbidden_stronger_claim |
| --- | --- | --- | --- | --- |
| C1_LOCAL_NONAFFINE_SURVIVAL | SUPPORTED_WITH_BOUNDARY | primary_positive | 4081c;4082;4088 | T1 is universal across all observations or causal. |
| C2_SCALE_LAG_ROBUST_SURVIVORS | SUPPORTED_WITH_BOUNDARY | primary_positive | 4082;4088 | Scale/lag robustness holds for all 19 observations. |
| C3_DIFFUSE_TANGENTIAL_DOMINANCE | SUPPORTED_WITH_BOUNDARY | primary_positive | 4084;4085;4088 | A stable edge/core trigger or propagation source is identified. |
| C7_OBSERVATION_SPECIFIC_HISTORY_BOUNDARY | BOUNDARY | secondary_bounded_positive | 4120;4121;4125 | A robust universal history dependence or causal memory mechanism is supported. |

## Figure Plan

| figure_id | role | content | allowed_caption_claim | file |
| --- | --- | --- | --- | --- |
| Fig4131A | main | observation-by-observation coverage for T1 survival, robustness, spatial, phase, and history-positive flags | positive evidence is common but bounded at the observation level | Output/4131/figures/4131_observation_coverage_matrix.png |
| Fig4131B | main | support fractions for each positive phenomenon row | strongest positive evidence is T1 survival and scale/lag robustness within survivor observations | Output/4131/figures/4131_positive_support_bars.png |
| Fig4131C | main | spatial variable gate fractions and phase gate fractions | diffuse all-tangential activity is more stable than edge/core phase localization | Output/4131/figures/4131_spatial_phase_positive_summary.png |
| Fig4131D | supplement | observation-level history real-minus-null effects and sign split | history separation is visible but observation-specific | Output/4131/figures/4131_history_secondary_positive.png |

## What This Does Not Prove

| does_not_prove |
| --- |
| universal T1 mechanism |
| causal trigger |
| prediction rule |
| stable edge/core phase trigger |
| universal history dependence |

## Next Node

`4132_negative_mechanism_boundary_atlas`

## Artifacts

- `Output/4131/positive_phenomenon_atlas.csv`
- `Output/4131/observation_positive_coverage_matrix.csv`
- `Output/4131/positive_claims_from_4130.csv`
- `Output/4131/positive_figure_plan.csv`
- `Output/4131/figures/4131_observation_coverage_matrix.png`
- `Output/4131/figures/4131_positive_support_bars.png`
- `Output/4131/figures/4131_spatial_phase_positive_summary.png`
- `Output/4131/figures/4131_history_secondary_positive.png`
