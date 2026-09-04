# Node 4133 Observation Heterogeneity Map

## Question

What structure is visible across the 19 observations after the positive
and negative/boundary atlases are fixed?

## Gate Result

```text
gate_result = pass_4133_heterogeneity_map_ready_with_metadata_boundary
```

## Main Interpretation

Observation-level heterogeneity can be mapped descriptively. The main
classes are robust survivor/diffuse-positive observations, fragile
408x boundaries, stable 408x failures, and a fragile survivor. The
association tests are small-n descriptive checks only.

## Class Counts

| observation_class | count |
| --- | --- |
| robust_survivor_diffuse_positive | 13 |
| fragile_408x_boundary | 2 |
| stable_408x_failure | 2 |
| fragile_survivor | 1 |
| robust_survivor_without_diffuse_gate | 1 |

## Strongest Descriptive Associations

| question | association | n | spearman_rho | spearman_pvalue_descriptive | loo_rho_min | loo_rho_max | association_label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| HET4 | ob index proxy vs T1 effect | 19 | 0.6544 | 0.002367 | 0.6017 | 0.7276 | moderate_descriptive_association |
| HET1 | T1 effect vs mean track length | 19 | 0.5105 | 0.02552 | 0.4241 | 0.6078 | weak_to_moderate_descriptive_association |
| HET3 | stable failure vs route score | 19 | -0.5033 | 0.02804 | -0.5318 | -0.3416 | weak_to_moderate_descriptive_association |
| HET2 | history abs effect vs route score | 19 | 0.4312 | 0.0653 | 0.3405 | 0.6207 | weak_to_moderate_descriptive_association |

## Metadata Status

| raw_column_0_4_metadata | recording_condition_daytime_dusk | observation_index_as_order_proxy |
| --- | --- | --- |
| VERIFIED_FROM_RAW_COLUMNS_0_AND_4 | UNVERIFIED | UNVERIFIED |

## Observation Classes

| ob | observation_class | route_positive_score | 408x_pass_class | 408x_robustness | failure_boundary_class | recording_condition | recording_condition_verification_status | boundary_flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | fragile_408x_boundary | 1 | t1_not_event_conditioned_after_local_affine | NA | fragile_narrow_setting_rescue | mainly_dusk | UNVERIFIED | 408x_failure_or_boundary;history_beats_median_shuffle |
| 2 | robust_survivor_diffuse_positive | 6 | t1_local_nonaffine_survives_both_k | robust_scale_and_timing | NA | mainly_dusk | UNVERIFIED | history_beats_median_shuffle |
| 3 | fragile_408x_boundary | 1 | t1_not_event_conditioned_after_local_affine | NA | fragile_narrow_setting_rescue | mainly_dusk | UNVERIFIED | 408x_failure_or_boundary;history_beats_median_shuffle |
| 4 | fragile_survivor | 1 | t1_local_nonaffine_survives_one_k | fragile_or_boundary | NA | mainly_dusk | UNVERIFIED | scale_lag_fragile |
| 5 | robust_survivor_diffuse_positive | 6 | t1_local_nonaffine_survives_both_k | robust_scale_and_timing | NA | mainly_dusk | UNVERIFIED | history_beats_median_shuffle |
| 6 | stable_408x_failure | 0 | t1_not_event_conditioned_after_local_affine | NA | stable_failure_under_predefined_sensitivity | daytime | UNVERIFIED | daytime_annotation_unverified;408x_failure_or_boundary |
| 7 | robust_survivor_without_diffuse_gate | 4 | t1_local_nonaffine_survives_both_k | robust_scale_and_timing | NA | mainly_dusk | UNVERIFIED | history_beats_median_shuffle |
| 8 | stable_408x_failure | 1 | t1_not_event_conditioned_after_local_affine | NA | stable_failure_under_predefined_sensitivity | mainly_dusk | UNVERIFIED | 408x_failure_or_boundary;history_beats_median_shuffle |
| 9 | robust_survivor_diffuse_positive | 5 | t1_local_nonaffine_survives_both_k | robust_scale_and_timing | NA | mainly_dusk | UNVERIFIED | history_beats_median_shuffle |
| 10 | robust_survivor_diffuse_positive | 5 | t1_local_nonaffine_survives_both_k | robust_scale_and_timing | NA | mainly_dusk | UNVERIFIED | history_beats_median_shuffle |
| 11 | robust_survivor_diffuse_positive | 5 | t1_local_nonaffine_survives_both_k | robust_scale_and_timing | NA | daytime | UNVERIFIED | daytime_annotation_unverified;history_beats_median_shuffle |
| 12 | robust_survivor_diffuse_positive | 5 | t1_local_nonaffine_survives_both_k | robust_scale_and_timing | NA | mainly_dusk | UNVERIFIED | history_beats_median_shuffle |
| 13 | robust_survivor_diffuse_positive | 4 | t1_local_nonaffine_survives_both_k | robust_scale_and_timing | NA | mainly_dusk | UNVERIFIED |  |
| 14 | robust_survivor_diffuse_positive | 5 | t1_local_nonaffine_survives_both_k | robust_scale_and_timing | NA | mainly_dusk | UNVERIFIED | history_beats_median_shuffle |
| 15 | robust_survivor_diffuse_positive | 6 | t1_local_nonaffine_survives_both_k | robust_scale_and_timing | NA | mainly_dusk | UNVERIFIED | history_beats_median_shuffle |
| 16 | robust_survivor_diffuse_positive | 5 | t1_local_nonaffine_survives_both_k | robust_scale_and_timing | NA | mainly_dusk | UNVERIFIED | history_beats_median_shuffle |
| 17 | robust_survivor_diffuse_positive | 5 | t1_local_nonaffine_survives_both_k | robust_scale_and_timing | NA | mainly_dusk | UNVERIFIED | history_beats_median_shuffle |
| 18 | robust_survivor_diffuse_positive | 4 | t1_local_nonaffine_survives_both_k | robust_scale_and_timing | NA | mainly_dusk | UNVERIFIED |  |
| 19 | robust_survivor_diffuse_positive | 4 | t1_local_nonaffine_survives_both_k | robust_scale_and_timing | NA | mainly_dusk | UNVERIFIED |  |

## What This Does Not Prove

| does_not_prove |
| --- |
| metadata regime explanation |
| causal source of Ob6/Ob8 failure |
| universal subgroup law |
| predictive observation classifier |
| new mechanism |

## Next Node

`4134_figure_ready_evidence_panels`

## Artifacts

- `Output/4133/raw_metadata_by_ob.csv`
- `Output/4133/observation_master_table.csv`
- `Output/4133/heterogeneity_associations.csv`
- `Output/4133/leave_one_out_sensitivity.csv`
- `Output/4133/observation_classes.csv`
- `Output/4133/figures/4133_observation_route_matrix.png`
- `Output/4133/figures/4133_t1_effect_vs_mean_swarm_size.png`
- `Output/4133/figures/4133_t1_effect_vs_mean_track_length.png`
- `Output/4133/figures/4133_history_abs_vs_t1_effect.png`
- `Output/4133/figures/4133_route_score_by_observation_class.png`
