# Node 4082b Summary

## Question

Why do Ob1/Ob3/Ob6/Ob8 fail the local-affine T1 event-specificity gate,
while most later observations pass?

## Inputs

- `Output/4081d/heterogeneity_features.csv`
- `Output/4082/ob_scale_timing_robustness.csv`
- raw trajectory files from the configured data directory

## Decision

`boundary_early_failure_not_explained_by_basic_quality_or_event_counts`

## Main Reading

Failure observations:

```text
Ob1, Ob3, Ob6, Ob8
```

Robust survivor observations after 4082:

```text
Ob2, Ob5, Ob7, Ob9, Ob10, Ob11, Ob12, Ob13, Ob14, Ob15, Ob16, Ob17, Ob18, Ob19
```

## Audit Features

| ob | failure_group | robustness_class | n_events | event_rate_per_sec | median_individuals_per_frame | track_continuity_fraction | median_raw_speed | median_swarm_radius | t1_median_local_event_minus_non_event_z |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | True |  | 28 | 0.2667 | 93 | 1 | 262.6 | 215.5 | -0.0189 |
| 2 | False | robust_scale_and_timing | 43 | 0.3076 | 69 | 1 | 249.6 | 204.9 | 0.3596 |
| 3 | True |  | 40 | 0.2731 | 46 | 1 | 228.6 | 167.5 | -0.1775 |
| 4 | False | fragile_or_boundary | 58 | 0.4017 | 30 | 1 | 210.2 | 144.3 | 0.0385 |
| 5 | False | robust_scale_and_timing | 93 | 0.6322 | 22 | 1 | 211.2 | 122.7 | 0.1828 |
| 6 | True |  | 112 | 0.5697 | 18 | 1 | 202.5 | 107 | -0.1299 |
| 7 | False | robust_scale_and_timing | 33 | 0.3589 | 58 | 1 | 252.3 | 191.8 | 0.1723 |
| 8 | True |  | 84 | 0.4538 | 27 | 1 | 217.1 | 156.6 | -0.0913 |
| 9 | False | robust_scale_and_timing | 36 | 0.3826 | 49 | 1 | 256.1 | 176.1 | 0.4661 |
| 10 | False | robust_scale_and_timing | 36 | 0.256 | 71 | 1 | 252.5 | 191.4 | 0.363 |
| 11 | False | robust_scale_and_timing | 119 | 0.6048 | 14 | 1 | 220.8 | 104.2 | 0.6009 |
| 12 | False | robust_scale_and_timing | 91 | 0.4853 | 19 | 1 | 282.6 | 170.5 | 0.315 |
| 13 | False | robust_scale_and_timing | 102 | 0.5296 | 27 | 1 | 256 | 168 | 0.517 |
| 14 | False | robust_scale_and_timing | 47 | 0.2528 | 54 | 1 | 248.9 | 204.6 | 0.3732 |
| 15 | False | robust_scale_and_timing | 96 | 0.486 | 21 | 1 | 250 | 175.3 | 0.6945 |
| 16 | False | robust_scale_and_timing | 84 | 0.4356 | 34 | 1 | 250.3 | 160.5 | 0.5399 |
| 17 | False | robust_scale_and_timing | 122 | 0.6214 | 15 | 1 | 263 | 161.1 | 0.2287 |
| 18 | False | robust_scale_and_timing | 103 | 0.5429 | 19 | 1 | 260 | 156.4 | 0.2802 |
| 19 | False | robust_scale_and_timing | 143 | 0.4809 | 29 | 1 | 283.8 | 182.7 | 0.642 |

## Strongest Contrasts

| feature | feature_family | failure_median | survivor_median | median_difference_failure_minus_survivor | exact_permutation_p_two_sided | interpretation |
| --- | --- | --- | --- | --- | --- | --- |
| t1_median_local_event_minus_non_event_z | result_or_gate_context | -0.1106 | 0.363 | -0.4736 | 0.002064 | describes the outcome split; not an independent artifact explanation |
| t1_k10_local_event_direction_abs_z | result_or_gate_context | 0.09326 | 0.6177 | -0.5244 | 0.002064 | describes the outcome split; not an independent artifact explanation |
| t1_k8_local_event_direction_abs_z | result_or_gate_context | 0.1926 | 0.5137 | -0.3211 | 0.01703 | describes the outcome split; not an independent artifact explanation |
| t2_gate_count | result_or_gate_context | 1 | 4 | -3 | 0.02657 | describes the outcome split; not an independent artifact explanation |
| median_raw_speed | raw_trajectory_quality | 222.8 | 252.3 | -29.49 | 0.05753 | weak routing clue |
| ob | result_or_gate_context | 4.5 | 12 | -7.5 | 0.06398 | describes the outcome split; not an independent artifact explanation |
| unique_ids | raw_trajectory_quality | 3434 | 1081 | 2352 | 0.0805 | weak routing clue |
| t1_k8_local_non_event_direction_abs_median_z | result_or_gate_context | 0.2549 | 0.1984 | 0.05652 | 0.08824 | describes the outcome split; not an independent artifact explanation |
| q95_raw_speed | raw_trajectory_quality | 427.3 | 459.3 | -31.97 | 0.2136 | no clear failure-group separation |
| event_rate_per_sec | event_structure | 0.3635 | 0.4809 | -0.1175 | 0.235 | no clear failure-group separation |
| early_ob_le_8 | result_or_gate_context | 1 | 0 | 1 | 0.2621 | describes the outcome split; not an independent artifact explanation |
| t1_k10_local_non_event_direction_abs_median_z | result_or_gate_context | 0.2252 | 0.1911 | 0.03407 | 0.2724 | describes the outcome split; not an independent artifact explanation |
| n_events | event_structure | 62 | 91 | -29 | 0.3233 | no clear failure-group separation |
| duration_sec | raw_trajectory_quality | 169.9 | 199.9 | -30 | 0.3511 | no clear failure-group separation |

## Interpretation

This audit should not be read as a mechanism discovery step. It asks
whether the failure class has an obvious condition/artifact explanation.

- T1 gate-derived variables sharply separate failure and survivor groups;
  that is expected and not independent evidence.
- Raw trajectory and event-structure variables are treated as more useful
  artifact/condition clues.
- If those raw/event variables do not separate clearly, the correct
  route is to keep the early-observation boundary visible rather than
  claiming it is solved.

## Next

`bounded_408x_synthesis_or_metadata_deep_audit`

## Artifacts

- `Output/4082b/failure_audit_features.csv`
- `Output/4082b/failure_audit_feature_contrasts.csv`
- `Output/4082b/figures/4082b_failure_audit_overview.png`
- `Output/4082b/figures/4082b_raw_event_feature_contrasts.png`
- `Output/4082b/figures/4082b_event_rate_vs_group_size.png`
