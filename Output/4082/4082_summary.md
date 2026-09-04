# Node 4082 Summary

## Question

Does the 4081c T1 local non-affine survival result remain under nearby
local scale and lag choices, or is it a single-parameter accident?

## Inputs

- `Output/4081c/ob_route_a_classification.csv`
- `Output/4081c/full_geometry_ladder_rows.csv`
- raw trajectories through the configured data directory

## Run

```text
observations = 4081c T1 survivors (15 observations)
scale axis = k [6, 8, 10, 12] at lag 0.10 sec
timing axis = lag [0.05, 0.1, 0.15] at k 8
matched non-event replicates = 40
frame_stride = 2
```

Cached 4081c rows were reused for `k=8,10; lag=0.10`.

## Decision

`support_scale_timing_robust_t1_survival_with_boundary_cases`

## Main Counts

```text
robust scale and timing observations = 14 / 15
fragile or boundary observations = 1 / 15
median scale pass fraction = 1
median timing pass fraction = 1
```

## Observation Robustness

| ob | n_events | scale_pass_count | scale_total | scale_pass_fraction | timing_pass_count | timing_total | timing_pass_fraction | median_scale_gap | median_timing_gap | robustness_class | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 43 | 4 | 4 | 1 | 3 | 3 | 1 | 0.3466 | 0.2264 | robust_scale_and_timing | T1 survives most nearby scale and timing checks. |
| 4 | 58 | 2 | 4 | 0.5 | 0 | 3 | 0 | 0.09033 | -0.06128 | fragile_or_boundary | T1 survival is weak under nearby robustness checks. |
| 5 | 93 | 4 | 4 | 1 | 3 | 3 | 1 | 0.1828 | 0.1823 | robust_scale_and_timing | T1 survives most nearby scale and timing checks. |
| 7 | 33 | 4 | 4 | 1 | 3 | 3 | 1 | 0.1723 | 0.4611 | robust_scale_and_timing | T1 survives most nearby scale and timing checks. |
| 9 | 36 | 4 | 4 | 1 | 3 | 3 | 1 | 0.7067 | 0.4413 | robust_scale_and_timing | T1 survives most nearby scale and timing checks. |
| 10 | 36 | 4 | 4 | 1 | 2 | 3 | 0.6667 | 0.3004 | 0.2277 | robust_scale_and_timing | T1 survives most nearby scale and timing checks. |
| 11 | 119 | 4 | 4 | 1 | 3 | 3 | 1 | 0.626 | 0.6217 | robust_scale_and_timing | T1 survives most nearby scale and timing checks. |
| 12 | 91 | 4 | 4 | 1 | 3 | 3 | 1 | 0.2789 | 0.2812 | robust_scale_and_timing | T1 survives most nearby scale and timing checks. |
| 13 | 102 | 4 | 4 | 1 | 3 | 3 | 1 | 0.514 | 0.4305 | robust_scale_and_timing | T1 survives most nearby scale and timing checks. |
| 14 | 47 | 4 | 4 | 1 | 3 | 3 | 1 | 0.3056 | 0.4713 | robust_scale_and_timing | T1 survives most nearby scale and timing checks. |
| 15 | 96 | 4 | 4 | 1 | 3 | 3 | 1 | 0.7203 | 0.8207 | robust_scale_and_timing | T1 survives most nearby scale and timing checks. |
| 16 | 84 | 4 | 4 | 1 | 3 | 3 | 1 | 0.5757 | 0.3145 | robust_scale_and_timing | T1 survives most nearby scale and timing checks. |
| 17 | 122 | 3 | 4 | 0.75 | 3 | 3 | 1 | 0.1437 | 0.2029 | robust_scale_and_timing | T1 survives most nearby scale and timing checks. |
| 18 | 103 | 4 | 4 | 1 | 3 | 3 | 1 | 0.1834 | 0.2254 | robust_scale_and_timing | T1 survives most nearby scale and timing checks. |
| 19 | 143 | 4 | 4 | 1 | 3 | 3 | 1 | 0.642 | 0.5558 | robust_scale_and_timing | T1 survives most nearby scale and timing checks. |

## Interpretation

This node does not add new biological mechanism variables. It asks only
whether the 4081c T1 result persists when local scale and lag are moved
near the original setting.

## Next

`4082b_early_failure_condition_or_artifact_audit`

## Artifacts

- `Output/4082/scale_timing_condition_rows.csv`
- `Output/4082/ob_scale_timing_robustness.csv`
- `Output/4082/figures/4082_scale_gap_heatmap.png`
- `Output/4082/figures/4082_timing_gap_heatmap.png`
- `Output/4082/figures/4082_ob_robustness_fractions.png`
