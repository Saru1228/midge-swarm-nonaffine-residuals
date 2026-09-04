# Node 4100A Summary

## Question

Can the 410x route construct a unique focal-centered local non-affine tangential activity unit before testing event-locality or propagation?

## Why This Node Exists After 4094

4094 routed the workflow away from low-dimensional `C,dCdt,radius` moment closure and toward transient/event-local organization. However, 4090B showed that the available vector unit is a focal-neighborhood neighbor residual vector. Directly computing spatial correlations on those overlapping neighbor vectors could create pseudo-correlation. 4100A therefore audits the representation before any propagation analysis.

## Data Scope

This run covers all 19 observations.

```text
Ob1, Ob2, Ob3, Ob4, Ob5, Ob6, Ob7, Ob8, Ob9, Ob10, Ob11, Ob12, Ob13, Ob14, Ob15, Ob16, Ob17, Ob18, Ob19
```

This is the primary technical-gate scope for 4100A, because 410x inherits the all-observation validation requirement after 4088 and 4094.

## Spatial Unit

```text
focal_centered_local_nonaffine_tangential_activity
```

Primary activity:

```text
A_i(t) = median_j ||u_NA_ij,tan(t)||^2
```

The naming remains focal-centered activity, not individual residual velocity, because each value aggregates neighbor residual vectors around a focal individual.

## Main QC

| ob | dataset | n_sampled_frames | n_valid_frames | valid_frame_fraction | n_focal_activity_rows | duplicate_focal_frame_rows | median_focals_per_valid_frame | median_condition_number | median_activity_energy_median | median_activity_tangential_norm_median | median_neighbor_slots_per_frame | median_unique_neighbors_per_frame | median_neighbor_overlap_ratio | median_fraction_multimembership_neighbors |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ob1.txt | 1098 | 1098 | 1 | 26352 | 0 | 24 | 2.161 | 3.36e+04 | 181.9 | 192 | 78 | 2.462 | 0.7195 |
| 2 | Ob2.txt | 1485 | 1485 | 1 | 35640 | 0 | 24 | 2.235 | 2.824e+04 | 166.7 | 192 | 60 | 3.2 | 0.8169 |
| 3 | Ob3.txt | 1498 | 1498 | 1 | 35952 | 0 | 24 | 2.344 | 2.414e+04 | 154.3 | 192 | 41 | 4.683 | 0.9 |
| 4 | Ob4.txt | 1495 | 1494 | 0.9993 | 35849 | 0 | 24 | 2.601 | 1.903e+04 | 136.9 | 192 | 28 | 6.857 | 0.931 |
| 5 | Ob5.txt | 1495 | 1494 | 0.9993 | 32679 | 0 | 22 | 2.591 | 1.827e+04 | 134.1 | 176 | 21 | 8.348 | 0.9565 |
| 6 | Ob6.txt | 1999 | 1998 | 0.9995 | 35552 | 0 | 18 | 2.624 | 1.689e+04 | 129 | 144 | 17 | 8 | 1 |
| 7 | Ob7.txt | 999 | 998 | 0.999 | 23952 | 0 | 24 | 2.266 | 2.937e+04 | 170.2 | 192 | 52 | 3.692 | 0.8571 |
| 8 | Ob8.txt | 1898 | 1898 | 1 | 44900 | 0 | 24 | 2.662 | 2.004e+04 | 140.4 | 192 | 25 | 7.68 | 0.9565 |
| 9 | Ob9.txt | 994 | 990 | 0.996 | 23760 | 0 | 24 | 2.227 | 2.98e+04 | 171.4 | 192 | 46 | 4.174 | 0.8953 |
| 10 | Ob10.txt | 1499 | 1498 | 0.9993 | 35952 | 0 | 24 | 2.17 | 2.992e+04 | 171.8 | 192 | 63 | 3.048 | 0.8103 |
| 11 | Ob11.txt | 1998 | 1997 | 0.9995 | 28251 | 0 | 14 | 2.76 | 1.916e+04 | 137.5 | 112 | 14 | 8 | 1 |
| 12 | Ob12.txt | 1998 | 1997 | 0.9995 | 36584 | 0 | 18 | 2.429 | 3.422e+04 | 183.7 | 144 | 18 | 8 | 1 |
| 13 | Ob13.txt | 1998 | 1998 | 1 | 47587 | 0 | 24 | 2.343 | 2.937e+04 | 170.2 | 192 | 27 | 7.111 | 0.9655 |
| 14 | Ob14.txt | 1998 | 1998 | 1 | 47952 | 0 | 24 | 2.239 | 2.817e+04 | 166.6 | 192 | 49 | 3.918 | 0.88 |
| 15 | Ob15.txt | 1998 | 1997 | 0.9995 | 39908 | 0 | 20 | 2.684 | 2.668e+04 | 162.1 | 160 | 20 | 8 | 0.9565 |
| 16 | Ob16.txt | 1998 | 1997 | 0.9995 | 47928 | 0 | 24 | 2.41 | 2.726e+04 | 163.9 | 192 | 32 | 6 | 0.9375 |
| 17 | Ob17.txt | 1999 | 1998 | 0.9995 | 29441 | 0 | 15 | 2.834 | 2.87e+04 | 168.1 | 120 | 15 | 8 | 1 |
| 18 | Ob18.txt | 1998 | 1998 | 1 | 37716 | 0 | 19 | 2.578 | 2.919e+04 | 169.7 | 152 | 18 | 8 | 1 |
| 19 | Ob19.txt | 2999 | 2998 | 0.9997 | 71849 | 0 | 24 | 2.405 | 3.587e+04 | 188 | 192 | 28 | 6.857 | 0.963 |

## Upstream Reproduction Diagnostic

| ob | dataset | n_events | n_controls | near_pre_event_median_z | near_pre_control_median_z | near_pre_event_minus_control_z | agg_vs_4084_pearson | agg_vs_4084_spearman | agg_vs_4084_n | qualitative_reproduction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ob1.txt | 28 | 560 | 0.05605 | -0.1289 | 0.1849 | NA | NA | 0 | event_profile_only_no_4084_reference |
| 2 | Ob2.txt | 43 | 860 | 0.1898 | -0.01332 | 0.2031 | 0.5708 | 0.564 | 1485 | weak_aggregate_consistency |
| 3 | Ob3.txt | 40 | 800 | -0.0471 | 0.1215 | -0.1686 | NA | NA | 0 | event_profile_only_no_4084_reference |
| 4 | Ob4.txt | 58 | 1154 | -0.1264 | 0.08604 | -0.2124 | NA | NA | 0 | event_profile_only_no_4084_reference |
| 5 | Ob5.txt | 93 | 1844 | 0.1058 | -0.01281 | 0.1186 | 0.898 | 0.886 | 1494 | aggregate_consistent_with_4084 |
| 6 | Ob6.txt | 112 | 2240 | -0.03528 | 0.09567 | -0.1309 | NA | NA | 0 | event_profile_only_no_4084_reference |
| 7 | Ob7.txt | 33 | 660 | 0.02201 | -0.1091 | 0.1311 | 0.6461 | 0.6237 | 998 | weak_aggregate_consistency |
| 8 | Ob8.txt | 84 | 1680 | -0.1523 | 0.08453 | -0.2368 | NA | NA | 0 | event_profile_only_no_4084_reference |
| 9 | Ob9.txt | 37 | 740 | 0.09561 | -0.06451 | 0.1601 | 0.7854 | 0.7101 | 990 | aggregate_consistent_with_4084 |
| 10 | Ob10.txt | 36 | 720 | -0.01067 | 0.03037 | -0.04104 | 0.6139 | 0.5985 | 1498 | weak_aggregate_consistency |
| 11 | Ob11.txt | 119 | 2380 | 0.02841 | -0.003407 | 0.03182 | 0.9107 | 0.9029 | 1997 | aggregate_consistent_with_4084 |
| 12 | Ob12.txt | 91 | 1820 | -0.1147 | 0.03484 | -0.1495 | 0.8978 | 0.8876 | 1997 | aggregate_consistent_with_4084 |
| 13 | Ob13.txt | 102 | 2040 | 0.01275 | 0.02531 | -0.01255 | 0.868 | 0.8609 | 1998 | aggregate_consistent_with_4084 |
| 14 | Ob14.txt | 47 | 940 | 0.006741 | 0.09731 | -0.09057 | 0.6933 | 0.6674 | 1998 | weak_aggregate_consistency |
| 15 | Ob15.txt | 96 | 1920 | -0.0907 | 0.04947 | -0.1402 | 0.9048 | 0.8943 | 1997 | aggregate_consistent_with_4084 |
| 16 | Ob16.txt | 84 | 1680 | -0.03615 | -0.03809 | 0.001945 | 0.8096 | 0.7986 | 1997 | aggregate_consistent_with_4084 |
| 17 | Ob17.txt | 122 | 2440 | -0.03445 | -0.02325 | -0.0112 | 0.8964 | 0.8925 | 1998 | aggregate_consistent_with_4084 |
| 18 | Ob18.txt | 103 | 2060 | 0.01648 | -0.01812 | 0.0346 | 0.9092 | 0.9028 | 1998 | aggregate_consistent_with_4084 |
| 19 | Ob19.txt | 143 | 2860 | -0.06032 | 0.0422 | -0.1025 | 0.8639 | 0.8475 | 2998 | aggregate_consistent_with_4084 |

## Gate Evaluation

```text
gate_result = pass_unique_focal_activity_with_overlap_boundary
```

The all-19 run constructs unique focal-centered activity rows with adequate coverage. Underlying neighbor overlap remains nontrivial, so later spatial correlation must use the focal aggregate rather than raw neighbor residual vectors.

## What This Supports

- It tests whether a unique `(observation, frame, focal_id)` activity table can be constructed.
- It quantifies the underlying neighbor-overlap issue.
- It checks whether the focal-centered aggregate is consistent with the earlier 4084 `all_tangential` aggregate where a reference exists.

## What This Does Not Prove

| does_not_prove |
| --- |
| state-matched event-locality |
| burst localization |
| propagation |
| causal trigger |
| unique individual residual velocity rather than focal-neighborhood activity |

## Decision

`pass_unique_focal_activity_with_overlap_boundary`

## Next Node

| next |
| --- |
| 4100_state_matched_event_locality_challenge |

## Artifacts

- `Output/4100A/focal_activity.csv.gz`
- `Output/4100A/focal_activity_qc.csv`
- `Output/4100A/overlap_audit.csv`
- `Output/4100A/swarm_activity_frame.csv`
- `Output/4100A/upstream_reproduction.csv`
- `Output/4100A/figures/4100A_qc_overview.png`
- `Output/4100A/figures/4100A_aggregate_vs_4084.png`
- `Output/4100A/figures/4100A_near_pre_reproduction.png`
- `Output/4100A/decision.json`
