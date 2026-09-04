# Node 4090A Summary

## Question

Does the frozen 4088 T1 effect strength mainly track observation-level regime,
batch/recording order, raw trajectory quality, event structure, or metadata?

## Why this node exists after 408x

4088 froze a bounded positive result:

```text
T1 = local tangential non-affine residual
```

with boundary cases Ob1/Ob3/Ob6/Ob8 and fragile Ob4. Before 4090 tries to
classify first-vs-second moment structure, 4090A checks whether the all-19 T1
heterogeneity is mostly an observation-regime issue.

## Inputs

- `Output/4081c/tables/ob_route_a_classification.csv`
- `Output/4082/tables/ob_scale_timing_robustness.csv`
- `Output/4082b/tables/failure_audit_features.csv`
- `Output/4087/tables/ob_failure_boundary_sensitivity.csv`
- `Output/4088/decision.json`

## Metadata

```text
metadata_available = False
recording_order_confirmed = False
```

Observation number is therefore treated only as an `ob_index_proxy`, not as
confirmed acquisition order or batch metadata.

## Data Scope

All 19 observations are included. Survivor-only modeling is not used.

## Primary Target

```text
t1_effect_z = t1_median_local_event_minus_non_event_z
```

Secondary effect views are `t1_local_to_b3_ratio`, `t1_k8_event_abs_z`, and
`t1_predefined_pass_fraction`.

## Main Observation Table

| ob | dataset | metadata_available | recording_order_confirmed | ob_index_proxy | early_ob_le_8 | t1_gate_any | t1_gate_k_values | t1_4088_class | t1_median_local_event_minus_non_event_z | t1_median_local_to_b3_ratio | t1_predefined_pass_fraction | scale_pass_fraction | timing_pass_fraction | failure_boundary_class | median_individuals_per_frame | median_raw_speed | median_swarm_radius | n_events | event_rate_per_sec | duration_sec | unique_ids | track_continuity_fraction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ob1.txt | False | False | 1 | 1 | False | NA | fragile_narrow_setting_rescue | -0.0189 | 0.3081 | 0.1538 | NA | NA | fragile_narrow_setting_rescue | 93 | 262.6 | 215.5 | 28 | 0.2667 | 109.9 | 4588 | 1 |
| 2 | Ob2.txt | False | False | 2 | 1 | True | 8,10 | robust_survivor | 0.3596 | 0.8905 | 1 | 1 | 1 | NA | 69 | 249.6 | 204.9 | 43 | 0.3076 | 148.6 | 5242 | 1 |
| 3 | Ob3.txt | False | False | 3 | 1 | False | NA | fragile_narrow_setting_rescue | -0.1775 | 0.4612 | 0.1538 | NA | NA | fragile_narrow_setting_rescue | 46 | 228.6 | 167.5 | 40 | 0.2731 | 149.9 | 4228 | 1 |
| 4 | Ob4.txt | False | False | 4 | 1 | True | 10 | fragile_survivor | 0.0385 | 0.5667 | 0.2857 | 0.5 | 0 | NA | 30 | 210.2 | 144.3 | 58 | 0.4017 | 149.9 | 1054 | 1 |
| 5 | Ob5.txt | False | False | 5 | 1 | True | 8,10 | robust_survivor | 0.1828 | 0.8399 | 1 | 1 | 1 | NA | 22 | 211.2 | 122.7 | 93 | 0.6322 | 149.9 | 639 | 1 |
| 6 | Ob6.txt | False | False | 6 | 1 | False | NA | stable_failure_under_predefined_sensitivity | -0.1299 | 37.25 | 0 | NA | NA | stable_failure_under_predefined_sensitivity | 18 | 202.5 | 107 | 112 | 0.5697 | 199.9 | 711 | 1 |
| 7 | Ob7.txt | False | False | 7 | 1 | True | 8,10 | robust_survivor | 0.1723 | 1.097 | 1 | 1 | 1 | NA | 58 | 252.3 | 191.8 | 33 | 0.3589 | 99.91 | 2688 | 1 |
| 8 | Ob8.txt | False | False | 8 | 1 | False | NA | stable_failure_under_predefined_sensitivity | -0.0913 | 1.605 | 0 | NA | NA | stable_failure_under_predefined_sensitivity | 27 | 217.1 | 156.6 | 84 | 0.4538 | 189.9 | 2639 | 1 |
| 9 | Ob9.txt | False | False | 9 | 0 | True | 8,10 | robust_survivor | 0.4661 | 2.1 | 1 | 1 | 1 | NA | 49 | 256.1 | 176.1 | 36 | 0.3826 | 99.88 | 2239 | 1 |
| 10 | Ob10.txt | False | False | 10 | 0 | True | 8,10 | robust_survivor | 0.363 | 1.202 | 0.8571 | 1 | 0.6667 | NA | 71 | 252.5 | 191.4 | 36 | 0.256 | 149.9 | 3937 | 1 |
| 11 | Ob11.txt | False | False | 11 | 0 | True | 8,10 | robust_survivor | 0.6009 | 1.724 | 1 | 1 | 1 | NA | 14 | 220.8 | 104.2 | 119 | 0.6048 | 199.9 | 277 | 1 |
| 12 | Ob12.txt | False | False | 12 | 0 | True | 8,10 | robust_survivor | 0.315 | 2.815 | 1 | 1 | 1 | NA | 19 | 282.6 | 170.5 | 91 | 0.4853 | 199.9 | 1126 | 1 |
| 13 | Ob13.txt | False | False | 13 | 0 | True | 8,10 | robust_survivor | 0.517 | 1.506 | 1 | 1 | 1 | NA | 27 | 256 | 168 | 102 | 0.5296 | 199.9 | 1042 | 1 |
| 14 | Ob14.txt | False | False | 14 | 0 | True | 8,10 | robust_survivor | 0.3732 | 0.984 | 1 | 1 | 1 | NA | 54 | 248.9 | 204.6 | 47 | 0.2528 | 199.9 | 5112 | 1 |
| 15 | Ob15.txt | False | False | 15 | 0 | True | 8,10 | robust_survivor | 0.6945 | 1.53 | 1 | 1 | 1 | NA | 21 | 250 | 175.3 | 96 | 0.486 | 199.9 | 740 | 1 |
| 16 | Ob16.txt | False | False | 16 | 0 | True | 8,10 | robust_survivor | 0.5399 | 2.277 | 1 | 1 | 1 | NA | 34 | 250.3 | 160.5 | 84 | 0.4356 | 199.9 | 1222 | 1 |
| 17 | Ob17.txt | False | False | 17 | 0 | True | 8,10 | robust_survivor | 0.2287 | 2.003 | 0.8571 | 0.75 | 1 | NA | 15 | 263 | 161.1 | 122 | 0.6214 | 199.9 | 202 | 1 |
| 18 | Ob18.txt | False | False | 18 | 0 | True | 8,10 | robust_survivor | 0.2802 | 0.6995 | 1 | 1 | 1 | NA | 19 | 260 | 156.4 | 103 | 0.5429 | 199.9 | 780 | 1 |
| 19 | Ob19.txt | False | False | 19 | 0 | True | 8,10 | robust_survivor | 0.642 | 1.53 | 1 | 1 | 1 | NA | 29 | 283.8 | 182.7 | 143 | 0.4809 | 299.9 | 1081 | 1 |

## T1 Effect Snapshot

| ob | class | T1_gap | local_B3 | pass_fraction |
| --- | --- | --- | --- | --- |
| 1 | fragile_narrow_setting_rescue | -0.0189 | 0.3081 | 0.1538 |
| 2 | robust_survivor | 0.3596 | 0.8905 | 1 |
| 3 | fragile_narrow_setting_rescue | -0.1775 | 0.4612 | 0.1538 |
| 4 | fragile_survivor | 0.0385 | 0.5667 | 0.2857 |
| 5 | robust_survivor | 0.1828 | 0.8399 | 1 |
| 6 | stable_failure_under_predefined_sensitivity | -0.1299 | 37.25 | 0 |
| 7 | robust_survivor | 0.1723 | 1.097 | 1 |
| 8 | stable_failure_under_predefined_sensitivity | -0.0913 | 1.605 | 0 |
| 9 | robust_survivor | 0.4661 | 2.1 | 1 |
| 10 | robust_survivor | 0.363 | 1.202 | 0.8571 |
| 11 | robust_survivor | 0.6009 | 1.724 | 1 |
| 12 | robust_survivor | 0.315 | 2.815 | 1 |
| 13 | robust_survivor | 0.517 | 1.506 | 1 |
| 14 | robust_survivor | 0.3732 | 0.984 | 1 |
| 15 | robust_survivor | 0.6945 | 1.53 | 1 |
| 16 | robust_survivor | 0.5399 | 2.277 | 1 |
| 17 | robust_survivor | 0.2287 | 2.003 | 0.8571 |
| 18 | robust_survivor | 0.2802 | 0.6995 | 1 |
| 19 | robust_survivor | 0.642 | 1.53 | 1 |

## Strongest Primary Associations

| target | covariate | covariate_family | n | spearman_rho | permutation_p_two_sided | theil_sen_slope | theil_sen_iqr_delta | loo_slope_min | loo_slope_max | loo_slope_sign_stability | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| t1_effect_z | early_ob_le_8 | observation_sequence_proxy | 19 | -0.798 | 0.0002 | -0.4228 | -0.4228 | -0.4592 | -0.3819 | 1 | sequence proxy; not confirmed metadata |
| t1_effect_z | ob_index_proxy | observation_sequence_proxy | 19 | 0.6544 | 0.0027 | 0.0325 | 0.2922 | 0.0304 | 0.036 | 1 | sequence proxy; not confirmed metadata |
| t1_effect_z | median_dt_sec | raw_trajectory_quality | 19 | -0.3892 | 0.1076 | NA | NA | NA | NA | NA | no strong association |
| t1_effect_z | duration_sec | raw_trajectory_quality | 19 | 0.3645 | 0.126 | 0.0025 | 0.1244 | 0.0019 | 0.0034 | 1 | no strong association |
| t1_effect_z | median_raw_speed | raw_trajectory_quality | 19 | 0.3579 | 0.1329 | 0.0047 | 0.1556 | 0.0036 | 0.0059 | 1 | no strong association |
| t1_effect_z | n_frames | raw_trajectory_quality | 19 | 0.3567 | 0.1326 | 0 | 0.1183 | 0 | 0 | 1 | no strong association |
| t1_effect_z | median_track_span_sec | raw_trajectory_quality | 19 | 0.3404 | 0.1516 | 0.2448 | 0.2227 | 0.1563 | 0.2954 | 1 | no strong association |
| t1_effect_z | median_track_length_frames | raw_trajectory_quality | 19 | 0.3404 | 0.1518 | 0.0024 | 0.2227 | 0.0016 | 0.003 | 1 | no strong association |
| t1_effect_z | q95_raw_speed | raw_trajectory_quality | 19 | 0.3228 | 0.1749 | 0.0018 | 0.0766 | 0.0014 | 0.0028 | 1 | no strong association |
| t1_effect_z | n_events | event_structure | 19 | 0.3205 | 0.177 | 0.0026 | 0.1595 | 0.0017 | 0.003 | 1 | no strong association |
| t1_effect_z | median_swarm_radius | raw_trajectory_quality | 19 | 0.1807 | 0.4602 | 0.0016 | 0.05 | 0.0008 | 0.0028 | 1 | no strong association |
| t1_effect_z | unique_ids | raw_trajectory_quality | 19 | -0.1737 | 0.4774 | -0 | -0.1145 | -0.0001 | -0 | 1 | no strong association |

## Strongest Raw/Event Associations

| target | covariate | covariate_family | n | spearman_rho | permutation_p_two_sided | theil_sen_slope | theil_sen_iqr_delta | loo_slope_min | loo_slope_max | loo_slope_sign_stability | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| t1_effect_z | median_dt_sec | raw_trajectory_quality | 19 | -0.3892 | 0.1076 | NA | NA | NA | NA | NA | no strong association |
| t1_effect_z | duration_sec | raw_trajectory_quality | 19 | 0.3645 | 0.126 | 0.0025 | 0.1244 | 0.0019 | 0.0034 | 1 | no strong association |
| t1_effect_z | median_raw_speed | raw_trajectory_quality | 19 | 0.3579 | 0.1329 | 0.0047 | 0.1556 | 0.0036 | 0.0059 | 1 | no strong association |
| t1_effect_z | n_frames | raw_trajectory_quality | 19 | 0.3567 | 0.1326 | 0 | 0.1183 | 0 | 0 | 1 | no strong association |
| t1_effect_z | median_track_span_sec | raw_trajectory_quality | 19 | 0.3404 | 0.1516 | 0.2448 | 0.2227 | 0.1563 | 0.2954 | 1 | no strong association |
| t1_effect_z | median_track_length_frames | raw_trajectory_quality | 19 | 0.3404 | 0.1518 | 0.0024 | 0.2227 | 0.0016 | 0.003 | 1 | no strong association |
| t1_effect_z | q95_raw_speed | raw_trajectory_quality | 19 | 0.3228 | 0.1749 | 0.0018 | 0.0766 | 0.0014 | 0.0028 | 1 | no strong association |
| t1_effect_z | n_events | event_structure | 19 | 0.3205 | 0.177 | 0.0026 | 0.1595 | 0.0017 | 0.003 | 1 | no strong association |
| t1_effect_z | median_swarm_radius | raw_trajectory_quality | 19 | 0.1807 | 0.4602 | 0.0016 | 0.05 | 0.0008 | 0.0028 | 1 | no strong association |
| t1_effect_z | unique_ids | raw_trajectory_quality | 19 | -0.1737 | 0.4774 | -0 | -0.1145 | -0.0001 | -0 | 1 | no strong association |

## Gate Evaluation

```text
gate_result = R1_unconfirmed_observation_sequence_proxy
```

T1 effect strength is strongly associated with observation sequence proxy variable(s): early_ob_le_8. Because metadata are unavailable, this is a routing boundary rather than proof of batch artifact. 4090 should keep observation identity and survivor/failure stratification explicit.

## What This Supports

- 4090 should not ignore observation identity or the 4088 failure/boundary class.
- Metadata are unavailable, so an observation-sequence association cannot be
  promoted to a confirmed batch artifact.
- Known raw/event covariates should be treated as routing clues only when their
  association is strong and leave-one-out stable.

## What This Rules Out

4090A does not find enough evidence to delete Ob1/Ob3/Ob6/Ob8 as bad data.
They remain part of the all-19 primary scope.

## What This Does NOT Prove

| does_not_prove |
| --- |
| batch artifact, because recording metadata are unavailable |
| biological mechanism |
| causal explanation of Ob6/Ob8 stable failures |
| first-vs-second moment structure |

## Decision

`R1_unconfirmed_observation_sequence_proxy`

## Next Node

`4090B_then_4090_with_observation_identity_and_boundary_strata`

## Artifacts

- `Output/4090A/observation_regime_table.csv`
- `Output/4090A/t1_continuous_effects.csv`
- `Output/4090A/covariate_association_table.csv`
- `Output/4090A/leave_one_out_sensitivity.csv`
- `Output/4090A/figures/4090A_observation_regime_overview.png`
- `Output/4090A/figures/4090A_t1_effect_vs_covariates.png`
- `Output/4090A/figures/4090A_primary_association_ranking.png`
