# Node 4087 Summary

## Question

Can Ob1/Ob3/Ob6/Ob8 become T1 local non-affine survival cases under a
principled sensitivity test, or are they genuinely different from the robust
survivor class?

## Scope

This node does not search for new metrics. It keeps:

```text
target = T1_transition_tangential_residual
local metric = local_tangential_speed_mean
gate = gap > 0.03, p <= 0.35, local/B3 ratio >= 0.3
```

Only three predefined sensitivity families are tested:

- the 4082-like scale/lag grid applied to the failure observations;
- event pre/post window length;
- compact low/high state persistence threshold.

## Decision

`boundary_failure_group_mostly_stable_with_fragile_rescues`

## Main Counts

```text
stable failure observations = 2 / 4
fragile boundary cases = 2 / 4
definition-sensitive rescues = 0 / 4
```

## Observation Boundary Classes

| ob | baseline_pass_count | baseline_total | scale_timing_pass_count | scale_timing_total | window_pass_count | window_total | state_definition_pass_count | state_definition_total | any_rescue | rescue_settings | median_nonbaseline_gap | failure_boundary_class | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0 | 2 | 2 | 7 | 0 | 3 | 0 | 3 | True | scale_k6_lag0p100_window0p200_minrun0p200, timing_k8_lag0p150_window0p200_minrun0p200 | 0.009982 | fragile_narrow_setting_rescue | The observation has only sparse fragile boundary cases and remains a boundary case. |
| 3 | 0 | 2 | 1 | 7 | 0 | 3 | 1 | 3 | True | scale_k6_lag0p100_window0p200_minrun0p200, state_k8_lag0p100_window0p200_minrun0p150 | -0.1545 | fragile_narrow_setting_rescue | The observation has only sparse fragile boundary cases and remains a boundary case. |
| 6 | 0 | 2 | 0 | 7 | 0 | 3 | 0 | 3 | False |  | -0.1252 | stable_failure_under_predefined_sensitivity | The observation remains negative across the predefined sensitivity checks. |
| 8 | 0 | 2 | 0 | 7 | 0 | 3 | 0 | 3 | False |  | 0.003604 | stable_failure_under_predefined_sensitivity | The observation remains negative across the predefined sensitivity checks. |

## Condition Rows

| ob | sensitivity_family | sensitivity_id | k | lag_sec | prepost_sec | min_run_sec | n_events | source | b3_event_direction_abs_z | local_event_direction_abs_z | local_non_event_direction_abs_median_z | local_event_minus_non_event_direction_z | p_non_event_direction_ge_event | local_to_b3_direction_ratio | event_conditioned_local_gate | geometry_ladder_reading |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | baseline | baseline_k10_lag0p100_window0p200_minrun0p200 | 10 | 0.1 | 0.2 | 0.2 | 28 | cached_4081c | 0.711 | 0.1736 | 0.2532 | -0.07961 | 0.575 | 0.2441 | False | local_affine_largely_absorbs_b3_signal |
| 1 | baseline | baseline_k8_lag0p100_window0p200_minrun0p200 | 8 | 0.1 | 0.2 | 0.2 | 28 | cached_4081c | 0.711 | 0.2646 | 0.2228 | 0.0418 | 0.425 | 0.3721 | False | inconclusive |
| 1 | scale_timing | scale_k10_lag0p100_window0p200_minrun0p200 | 10 | 0.1 | 0.2 | 0.2 | 28 | cached_4081c | 0.711 | 0.1736 | 0.2532 | -0.07961 | 0.575 | 0.2441 | False | local_affine_largely_absorbs_b3_signal |
| 1 | scale_timing | scale_k12_lag0p100_window0p200_minrun0p200 | 12 | 0.1 | 0.2 | 0.2 | 28 | computed_4087 | 0.711 | 0.09363 | 0.269 | -0.1754 | 0.775 | 0.1317 | False | local_affine_largely_absorbs_b3_signal |
| 1 | scale_timing | scale_k6_lag0p100_window0p200_minrun0p200 | 6 | 0.1 | 0.2 | 0.2 | 28 | computed_4087 | 0.711 | 0.5121 | 0.2415 | 0.2706 | 0.125 | 0.7203 | True | local_nonaffine_signal_survives_gate |
| 1 | scale_timing | scale_k8_lag0p100_window0p200_minrun0p200 | 8 | 0.1 | 0.2 | 0.2 | 28 | cached_4081c | 0.711 | 0.2646 | 0.2228 | 0.0418 | 0.425 | 0.3721 | False | inconclusive |
| 1 | scale_timing | timing_k8_lag0p050_window0p200_minrun0p200 | 8 | 0.05 | 0.2 | 0.2 | 28 | computed_4087 | 0.711 | 0.1867 | 0.1768 | 0.009982 | 0.45 | 0.2627 | False | local_affine_largely_absorbs_b3_signal |
| 1 | scale_timing | timing_k8_lag0p100_window0p200_minrun0p200 | 8 | 0.1 | 0.2 | 0.2 | 28 | cached_4081c | 0.711 | 0.2646 | 0.2228 | 0.0418 | 0.425 | 0.3721 | False | inconclusive |
| 1 | scale_timing | timing_k8_lag0p150_window0p200_minrun0p200 | 8 | 0.15 | 0.2 | 0.2 | 28 | computed_4087 | 0.711 | 0.2823 | 0.1697 | 0.1126 | 0.275 | 0.3971 | True | local_nonaffine_signal_survives_gate |
| 1 | state_definition | state_k8_lag0p100_window0p200_minrun0p150 | 8 | 0.1 | 0.2 | 0.15 | 33 | computed_4087 | 0.711 | 0.2746 | 0.2884 | -0.01378 | 0.525 | 0.3863 | False | local_nonaffine_not_event_conditioned |
| 1 | state_definition | state_k8_lag0p100_window0p200_minrun0p200 | 8 | 0.1 | 0.2 | 0.2 | 28 | cached_4081c | 0.711 | 0.2646 | 0.2228 | 0.0418 | 0.425 | 0.3721 | False | inconclusive |
| 1 | state_definition | state_k8_lag0p100_window0p200_minrun0p250 | 8 | 0.1 | 0.2 | 0.25 | 26 | computed_4087 | 0.711 | 0.1906 | 0.2386 | -0.048 | 0.525 | 0.2682 | False | local_affine_largely_absorbs_b3_signal |
| 1 | window | window_k8_lag0p100_window0p150_minrun0p200 | 8 | 0.1 | 0.15 | 0.2 | 28 | computed_4087 | 0.711 | 0.1963 | 0.199 | -0.002685 | 0.525 | 0.2761 | False | local_affine_largely_absorbs_b3_signal |
| 1 | window | window_k8_lag0p100_window0p200_minrun0p200 | 8 | 0.1 | 0.2 | 0.2 | 28 | cached_4081c | 0.711 | 0.2646 | 0.2228 | 0.0418 | 0.425 | 0.3721 | False | inconclusive |
| 1 | window | window_k8_lag0p100_window0p300_minrun0p200 | 8 | 0.1 | 0.3 | 0.2 | 28 | computed_4087 | 0.711 | 0.03589 | 0.2517 | -0.2158 | 0.9 | 0.05048 | False | local_affine_largely_absorbs_b3_signal |
| 3 | baseline | baseline_k10_lag0p100_window0p200_minrun0p200 | 10 | 0.1 | 0.2 | 0.2 | 40 | cached_4081c | 0.3003 | 0.1563 | 0.2716 | -0.1154 | 0.725 | 0.5204 | False | local_nonaffine_not_event_conditioned |
| 3 | baseline | baseline_k8_lag0p100_window0p200_minrun0p200 | 8 | 0.1 | 0.2 | 0.2 | 40 | cached_4081c | 0.3003 | 0.1207 | 0.3603 | -0.2396 | 0.925 | 0.402 | False | local_nonaffine_not_event_conditioned |
| 3 | scale_timing | scale_k10_lag0p100_window0p200_minrun0p200 | 10 | 0.1 | 0.2 | 0.2 | 40 | cached_4081c | 0.3003 | 0.1563 | 0.2716 | -0.1154 | 0.725 | 0.5204 | False | local_nonaffine_not_event_conditioned |
| 3 | scale_timing | scale_k12_lag0p100_window0p200_minrun0p200 | 12 | 0.1 | 0.2 | 0.2 | 40 | computed_4087 | 0.3003 | 0.1455 | 0.3 | -0.1545 | 0.775 | 0.4846 | False | local_nonaffine_not_event_conditioned |
| 3 | scale_timing | scale_k6_lag0p100_window0p200_minrun0p200 | 6 | 0.1 | 0.2 | 0.2 | 40 | computed_4087 | 0.3003 | 0.5187 | 0.2534 | 0.2653 | 0.2 | 1.727 | True | local_nonaffine_signal_survives_gate |
| 3 | scale_timing | scale_k8_lag0p100_window0p200_minrun0p200 | 8 | 0.1 | 0.2 | 0.2 | 40 | cached_4081c | 0.3003 | 0.1207 | 0.3603 | -0.2396 | 0.925 | 0.402 | False | local_nonaffine_not_event_conditioned |
| 3 | scale_timing | timing_k8_lag0p050_window0p200_minrun0p200 | 8 | 0.05 | 0.2 | 0.2 | 40 | computed_4087 | 0.3003 | 0.01377 | 0.2568 | -0.243 | 0.95 | 0.04586 | False | local_affine_largely_absorbs_b3_signal |
| 3 | scale_timing | timing_k8_lag0p100_window0p200_minrun0p200 | 8 | 0.1 | 0.2 | 0.2 | 40 | cached_4081c | 0.3003 | 0.1207 | 0.3603 | -0.2396 | 0.925 | 0.402 | False | local_nonaffine_not_event_conditioned |
| 3 | scale_timing | timing_k8_lag0p150_window0p200_minrun0p200 | 8 | 0.15 | 0.2 | 0.2 | 40 | computed_4087 | 0.3003 | 0.1977 | 0.188 | 0.009694 | 0.5 | 0.6584 | False | inconclusive |
| 3 | state_definition | state_k8_lag0p100_window0p200_minrun0p150 | 8 | 0.1 | 0.2 | 0.15 | 58 | computed_4087 | 0.3003 | 0.3855 | 0.2034 | 0.1821 | 0.15 | 1.284 | True | local_nonaffine_signal_survives_gate |
| 3 | state_definition | state_k8_lag0p100_window0p200_minrun0p200 | 8 | 0.1 | 0.2 | 0.2 | 40 | cached_4081c | 0.3003 | 0.1207 | 0.3603 | -0.2396 | 0.925 | 0.402 | False | local_nonaffine_not_event_conditioned |
| 3 | state_definition | state_k8_lag0p100_window0p200_minrun0p250 | 8 | 0.1 | 0.2 | 0.25 | 30 | computed_4087 | 0.3003 | 0.0748 | 0.4046 | -0.3298 | 0.875 | 0.2491 | False | local_affine_largely_absorbs_b3_signal |
| 3 | window | window_k8_lag0p100_window0p150_minrun0p200 | 8 | 0.1 | 0.15 | 0.2 | 40 | computed_4087 | 0.3003 | 0.1564 | 0.2751 | -0.1187 | 0.7 | 0.5209 | False | local_nonaffine_not_event_conditioned |
| 3 | window | window_k8_lag0p100_window0p200_minrun0p200 | 8 | 0.1 | 0.2 | 0.2 | 40 | cached_4081c | 0.3003 | 0.1207 | 0.3603 | -0.2396 | 0.925 | 0.402 | False | local_nonaffine_not_event_conditioned |
| 3 | window | window_k8_lag0p100_window0p300_minrun0p200 | 8 | 0.1 | 0.3 | 0.2 | 40 | computed_4087 | 0.3003 | 0.1123 | 0.2303 | -0.118 | 0.75 | 0.3741 | False | local_nonaffine_not_event_conditioned |
| 6 | baseline | baseline_k10_lag0p100_window0p200_minrun0p200 | 10 | 0.1 | 0.2 | 0.2 | 112 | cached_4081c | 0.001339 | 0.03028 | 0.1648 | -0.1346 | 0.875 | 22.61 | False | local_nonaffine_not_event_conditioned |
| 6 | baseline | baseline_k8_lag0p100_window0p200_minrun0p200 | 8 | 0.1 | 0.2 | 0.2 | 112 | cached_4081c | 0.001339 | 0.06948 | 0.1947 | -0.1252 | 0.875 | 51.89 | False | local_nonaffine_not_event_conditioned |
| 6 | scale_timing | scale_k10_lag0p100_window0p200_minrun0p200 | 10 | 0.1 | 0.2 | 0.2 | 112 | cached_4081c | 0.001339 | 0.03028 | 0.1648 | -0.1346 | 0.875 | 22.61 | False | local_nonaffine_not_event_conditioned |
| 6 | scale_timing | scale_k12_lag0p100_window0p200_minrun0p200 | 12 | 0.1 | 0.2 | 0.2 | 112 | computed_4087 | 0.001339 | 0.1555 | 0.1259 | 0.02954 | 0.475 | 116.1 | False | inconclusive |
| 6 | scale_timing | scale_k6_lag0p100_window0p200_minrun0p200 | 6 | 0.1 | 0.2 | 0.2 | 112 | computed_4087 | 0.001339 | 0.03039 | 0.2657 | -0.2353 | 0.975 | 22.7 | False | local_nonaffine_not_event_conditioned |
| 6 | scale_timing | scale_k8_lag0p100_window0p200_minrun0p200 | 8 | 0.1 | 0.2 | 0.2 | 112 | cached_4081c | 0.001339 | 0.06948 | 0.1947 | -0.1252 | 0.875 | 51.89 | False | local_nonaffine_not_event_conditioned |
| 6 | scale_timing | timing_k8_lag0p050_window0p200_minrun0p200 | 8 | 0.05 | 0.2 | 0.2 | 112 | computed_4087 | 0.001339 | 0.1302 | 0.2071 | -0.07697 | 0.675 | 97.22 | False | local_nonaffine_not_event_conditioned |
| 6 | scale_timing | timing_k8_lag0p100_window0p200_minrun0p200 | 8 | 0.1 | 0.2 | 0.2 | 112 | cached_4081c | 0.001339 | 0.06948 | 0.1947 | -0.1252 | 0.875 | 51.89 | False | local_nonaffine_not_event_conditioned |
| 6 | scale_timing | timing_k8_lag0p150_window0p200_minrun0p200 | 8 | 0.15 | 0.2 | 0.2 | 112 | computed_4087 | 0.001339 | 0.07821 | 0.1661 | -0.08785 | 0.75 | 58.42 | False | local_nonaffine_not_event_conditioned |
| 6 | state_definition | state_k8_lag0p100_window0p200_minrun0p150 | 8 | 0.1 | 0.2 | 0.15 | 135 | computed_4087 | 0.001339 | 0.08908 | 0.2055 | -0.1164 | 0.825 | 66.54 | False | local_nonaffine_not_event_conditioned |
| 6 | state_definition | state_k8_lag0p100_window0p200_minrun0p200 | 8 | 0.1 | 0.2 | 0.2 | 112 | cached_4081c | 0.001339 | 0.06948 | 0.1947 | -0.1252 | 0.875 | 51.89 | False | local_nonaffine_not_event_conditioned |
| 6 | state_definition | state_k8_lag0p100_window0p200_minrun0p250 | 8 | 0.1 | 0.2 | 0.25 | 100 | computed_4087 | 0.001339 | 0.1135 | 0.2408 | -0.1273 | 0.775 | 84.76 | False | local_nonaffine_not_event_conditioned |
| 6 | window | window_k8_lag0p100_window0p150_minrun0p200 | 8 | 0.1 | 0.15 | 0.2 | 112 | computed_4087 | 0.001339 | 0.07337 | 0.1371 | -0.06378 | 0.775 | 54.8 | False | local_nonaffine_not_event_conditioned |
| 6 | window | window_k8_lag0p100_window0p200_minrun0p200 | 8 | 0.1 | 0.2 | 0.2 | 112 | cached_4081c | 0.001339 | 0.06948 | 0.1947 | -0.1252 | 0.875 | 51.89 | False | local_nonaffine_not_event_conditioned |
| 6 | window | window_k8_lag0p100_window0p300_minrun0p200 | 8 | 0.1 | 0.3 | 0.2 | 112 | computed_4087 | 0.001339 | 0.02343 | 0.1758 | -0.1524 | 0.95 | 17.5 | False | local_nonaffine_not_event_conditioned |
| 8 | baseline | baseline_k10_lag0p100_window0p200_minrun0p200 | 10 | 0.1 | 0.2 | 0.2 | 84 | cached_4081c | 0.09395 | 0.01095 | 0.1971 | -0.1862 | 0.925 | 0.1166 | False | local_affine_largely_absorbs_b3_signal |
| 8 | baseline | baseline_k8_lag0p100_window0p200_minrun0p200 | 8 | 0.1 | 0.2 | 0.2 | 84 | cached_4081c | 0.09395 | 0.2907 | 0.2871 | 0.003604 | 0.5 | 3.094 | False | inconclusive |
| 8 | scale_timing | scale_k10_lag0p100_window0p200_minrun0p200 | 10 | 0.1 | 0.2 | 0.2 | 84 | cached_4081c | 0.09395 | 0.01095 | 0.1971 | -0.1862 | 0.925 | 0.1166 | False | local_affine_largely_absorbs_b3_signal |
| 8 | scale_timing | scale_k12_lag0p100_window0p200_minrun0p200 | 12 | 0.1 | 0.2 | 0.2 | 84 | computed_4087 | 0.09395 | 0.04134 | 0.1561 | -0.1147 | 0.9 | 0.44 | False | local_nonaffine_not_event_conditioned |
| 8 | scale_timing | scale_k6_lag0p100_window0p200_minrun0p200 | 6 | 0.1 | 0.2 | 0.2 | 84 | computed_4087 | 0.09395 | 0.2032 | 0.2183 | -0.0151 | 0.525 | 2.163 | False | local_nonaffine_not_event_conditioned |
| 8 | scale_timing | scale_k8_lag0p100_window0p200_minrun0p200 | 8 | 0.1 | 0.2 | 0.2 | 84 | cached_4081c | 0.09395 | 0.2907 | 0.2871 | 0.003604 | 0.5 | 3.094 | False | inconclusive |
| 8 | scale_timing | timing_k8_lag0p050_window0p200_minrun0p200 | 8 | 0.05 | 0.2 | 0.2 | 84 | computed_4087 | 0.09395 | 0.2923 | 0.3197 | -0.02742 | 0.5 | 3.111 | False | local_nonaffine_not_event_conditioned |
| 8 | scale_timing | timing_k8_lag0p100_window0p200_minrun0p200 | 8 | 0.1 | 0.2 | 0.2 | 84 | cached_4081c | 0.09395 | 0.2907 | 0.2871 | 0.003604 | 0.5 | 3.094 | False | inconclusive |
| 8 | scale_timing | timing_k8_lag0p150_window0p200_minrun0p200 | 8 | 0.15 | 0.2 | 0.2 | 84 | computed_4087 | 0.09395 | 0.1094 | 0.2626 | -0.1532 | 0.9 | 1.164 | False | local_nonaffine_not_event_conditioned |
| 8 | state_definition | state_k8_lag0p100_window0p200_minrun0p150 | 8 | 0.1 | 0.2 | 0.15 | 107 | computed_4087 | 0.09395 | 0.2542 | 0.2025 | 0.05167 | 0.375 | 2.705 | False | inconclusive |
| 8 | state_definition | state_k8_lag0p100_window0p200_minrun0p200 | 8 | 0.1 | 0.2 | 0.2 | 84 | cached_4081c | 0.09395 | 0.2907 | 0.2871 | 0.003604 | 0.5 | 3.094 | False | inconclusive |
| 8 | state_definition | state_k8_lag0p100_window0p200_minrun0p250 | 8 | 0.1 | 0.2 | 0.25 | 66 | computed_4087 | 0.09395 | 0.2912 | 0.2762 | 0.015 | 0.475 | 3.1 | False | inconclusive |
| 8 | window | window_k8_lag0p100_window0p150_minrun0p200 | 8 | 0.1 | 0.15 | 0.2 | 84 | computed_4087 | 0.09395 | 0.2081 | 0.1643 | 0.04383 | 0.4 | 2.215 | False | inconclusive |
| 8 | window | window_k8_lag0p100_window0p200_minrun0p200 | 8 | 0.1 | 0.2 | 0.2 | 84 | cached_4081c | 0.09395 | 0.2907 | 0.2871 | 0.003604 | 0.5 | 3.094 | False | inconclusive |
| 8 | window | window_k8_lag0p100_window0p300_minrun0p200 | 8 | 0.1 | 0.3 | 0.2 | 84 | computed_4087 | 0.09395 | 0.09978 | 0.3127 | -0.2129 | 0.8 | 1.062 | False | local_nonaffine_not_event_conditioned |

## Interpretation

Some failure observations pass only narrow predefined settings. These are not robust enough to merge into the survivor class, but they show the boundary is not perfectly sharp.

## Boundary

4087 can revise the meaning of the failure group, but it cannot turn a narrow
parameter rescue into a universal positive result. If a failure observation
passes only one or a few predefined settings, it remains a boundary case rather
than a full member of the 4082 robust survivor class.

## Next

`4088_bounded_408x_synthesis_with_failure_boundary`

## Artifacts

- `Output/4087/condition_rows.csv`
- `Output/4087/ob_failure_boundary_sensitivity.csv`
- `Output/4087/figures/4087_condition_gap_heatmap.png`
- `Output/4087/figures/4087_pass_count_by_family.png`
