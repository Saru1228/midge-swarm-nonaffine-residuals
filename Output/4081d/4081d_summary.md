# Node 4081d Summary

## Question

4081c found that Ob1 and Ob2 were not simply contradictory cases. Across
all 19 observations, what observation-level pattern explains the split?

## Inputs

- `Output/4081c/ob_route_a_classification.csv`
- `Output/4081c/full_geometry_ladder_rows.csv`
- `Output/3045/tables/transition_events.csv`

## Main Result

`support_common_t1_survival_with_early_observation_boundary`

In plain language: most observations retain a transition-linked local
tangential residual after subtracting local affine motion. The exceptions
are not random-looking across observation index: Ob1, Ob3, Ob6, and Ob8
fail, while Ob9-Ob19 all pass.

## Counts

```text
total observations = 19
T1 survives at least one k = 15
T1 survives both k = 14
T1 survives one k = 1
T1 not event-conditioned after local affine = 4
```

A rough sign-test-style comparison against a half-survival null gives
`p = 0.01921`. This should be treated as descriptive, because the
19 observations may not be fully independent.

The four non-survival observations all lie in Ob1-Ob8. If four failure
positions were randomly placed among 19 observations, the probability
that all four land in the first eight is `0.01806`. This is
a useful routing clue, not a final causal explanation.

## Observation Features

| ob | dataset | ob_group | n_events | event_rate_per_sec | median_prev_duration_sec | median_next_duration_sec | t1_gate_k_values | t1_median_local_to_b3_ratio | t1_median_local_event_minus_non_event_z | t1_k8_local_event_direction_abs_z | t1_k8_local_non_event_direction_abs_median_z | t1_k10_local_event_direction_abs_z | t1_k10_local_non_event_direction_abs_median_z | t2_gate_count | ob_route_a_class |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ob1.txt | not_event_conditioned | 28 | 0.2667 | 0.69 | 0.745 | NA | 0.3081 | -0.0189 | 0.2646 | 0.2228 | 0.1736 | 0.2532 | 0 | t1_not_event_conditioned_after_local_affine |
| 2 | Ob2.txt | survive | 43 | 0.3076 | 0.54 | 0.63 | 8,10 | 0.8905 | 0.3596 | 0.4935 | 0.1861 | 0.599 | 0.1873 | 4 | t1_local_nonaffine_survives_both_k |
| 3 | Ob3.txt | not_event_conditioned | 40 | 0.2731 | 0.56 | 0.55 | NA | 0.4612 | -0.1775 | 0.1207 | 0.3603 | 0.1563 | 0.2716 | 2 | t1_not_event_conditioned_after_local_affine |
| 4 | Ob4.txt | survive | 58 | 0.4017 | 0.565 | 0.71 | 10 | 0.5667 | 0.0385 | 0.1147 | 0.1926 | 0.3341 | 0.1793 | 4 | t1_local_nonaffine_survives_one_k |
| 5 | Ob5.txt | survive | 93 | 0.6322 | 0.73 | 0.64 | 8,10 | 0.8399 | 0.1828 | 0.3753 | 0.193 | 0.3373 | 0.154 | 4 | t1_local_nonaffine_survives_both_k |
| 6 | Ob6.txt | not_event_conditioned | 112 | 0.5697 | 0.645 | 0.645 | NA | 37.25 | -0.1299 | 0.0695 | 0.1947 | 0.0303 | 0.1648 | 0 | t1_not_event_conditioned_after_local_affine |
| 7 | Ob7.txt | survive | 33 | 0.3589 | 0.76 | 0.59 | 8,10 | 1.097 | 0.1723 | 0.4794 | 0.2588 | 0.4618 | 0.3377 | 0 | t1_local_nonaffine_survives_both_k |
| 8 | Ob8.txt | not_event_conditioned | 84 | 0.4538 | 0.745 | 0.76 | NA | 1.605 | -0.0913 | 0.2907 | 0.2871 | 0.011 | 0.1971 | 2 | t1_not_event_conditioned_after_local_affine |
| 9 | Ob9.txt | survive | 36 | 0.3826 | 0.6 | 0.67 | 8,10 | 2.1 | 0.4661 | 0.768 | 0.2829 | 0.7157 | 0.2687 | 4 | t1_local_nonaffine_survives_both_k |
| 10 | Ob10.txt | survive | 36 | 0.256 | 0.81 | 0.745 | 8,10 | 1.202 | 0.363 | 0.5743 | 0.3264 | 0.8041 | 0.3259 | 4 | t1_local_nonaffine_survives_both_k |
| 11 | Ob11.txt | survive | 119 | 0.6048 | 0.72 | 0.72 | 8,10 | 1.724 | 0.6009 | 0.8263 | 0.2046 | 0.7712 | 0.1911 | 4 | t1_local_nonaffine_survives_both_k |
| 12 | Ob12.txt | survive | 91 | 0.4853 | 0.71 | 0.72 | 8,10 | 2.815 | 0.315 | 0.4499 | 0.1984 | 0.6177 | 0.2391 | 4 | t1_local_nonaffine_survives_both_k |
| 13 | Ob13.txt | survive | 102 | 0.5296 | 0.695 | 0.64 | 8,10 | 1.506 | 0.517 | 0.5796 | 0.1491 | 0.8098 | 0.2063 | 4 | t1_local_nonaffine_survives_both_k |
| 14 | Ob14.txt | survive | 47 | 0.2528 | 0.67 | 0.72 | 8,10 | 0.984 | 0.3732 | 0.6837 | 0.2124 | 0.5047 | 0.2296 | 4 | t1_local_nonaffine_survives_both_k |
| 15 | Ob15.txt | survive | 96 | 0.486 | 0.805 | 0.635 | 8,10 | 1.53 | 0.6945 | 1.063 | 0.242 | 0.7406 | 0.1723 | 4 | t1_local_nonaffine_survives_both_k |
| 16 | Ob16.txt | survive | 84 | 0.4356 | 0.595 | 0.595 | 8,10 | 2.277 | 0.5399 | 0.5137 | 0.1992 | 0.9728 | 0.2075 | 4 | t1_local_nonaffine_survives_both_k |
| 17 | Ob17.txt | survive | 122 | 0.6214 | 0.78 | 0.69 | 8,10 | 2.003 | 0.2287 | 0.3546 | 0.1517 | 0.4375 | 0.1829 | 4 | t1_local_nonaffine_survives_both_k |
| 18 | Ob18.txt | survive | 103 | 0.5429 | 0.68 | 0.7 | 8,10 | 0.6995 | 0.2802 | 0.419 | 0.1936 | 0.4792 | 0.1441 | 4 | t1_local_nonaffine_survives_both_k |
| 19 | Ob19.txt | survive | 143 | 0.4809 | 0.67 | 0.81 | 8,10 | 1.53 | 0.642 | 0.7096 | 0.1426 | 0.8823 | 0.1653 | 4 | t1_local_nonaffine_survives_both_k |

## Strongest Feature Contrasts

| feature | plain_label | not_event_q25 | not_event_median | not_event_q75 | survive_q25 | survive_median | survive_q75 | median_difference_survive_minus_not_event | exact_permutation_p_two_sided | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| t1_median_local_event_minus_non_event_z | T1 local event-control gap median | -0.1418 | -0.1106 | -0.07319 | 0.2545 | 0.363 | 0.5285 | 0.4736 | 0.002064 | exploratory; small n; gate-derived feature |
| t1_k10_local_event_direction_abs_z | T1 local event abs, k10 | 0.02545 | 0.09326 | 0.1606 | 0.4705 | 0.6177 | 0.7877 | 0.5244 | 0.002064 | exploratory; small n; gate-derived feature |
| t1_k8_local_event_direction_abs_z | T1 local event abs, k8 | 0.1079 | 0.1926 | 0.2711 | 0.4344 | 0.5137 | 0.6966 | 0.3211 | 0.01703 | exploratory; small n; gate-derived feature |
| t1_k8_b3_event_direction_abs_z | T1 B3 event abs, k8 row | 0.0708 | 0.1971 | 0.4029 | 0.3747 | 0.4612 | 0.5814 | 0.2641 | 0.01935 | exploratory; small n; gate-derived feature |
| t2_gate_count | secondary T2 gate count | 0 | 1 | 2 | 4 | 4 | 4 | 3 | 0.02657 | exploratory; small n |
| ob | observation index | 2.5 | 4.5 | 6.5 | 8 | 12 | 15.5 | 7.5 | 0.06398 | exploratory; small n |
| t1_k8_local_non_event_direction_abs_median_z | T1 local non-event abs, k8 | 0.2157 | 0.2549 | 0.3054 | 0.1894 | 0.1984 | 0.2272 | -0.05652 | 0.08824 | exploratory; small n; gate-derived feature |
| event_rate_per_sec | transition event rate | 0.2715 | 0.3635 | 0.4828 | 0.3708 | 0.4809 | 0.5363 | 0.1175 | 0.235 | exploratory; small n |

## Interpretation

4081c/4081d changes the story from "Ob1 and Ob2 disagree" to a clearer
statistical map:

- The common pattern is positive: 15/19 observations retain the T1 local
  non-affine event-conditioned signal.
- The negative cases are not "local affine explains everything." They
  are better read as "after local affine correction, the remaining local
  tangential residual is not specifically higher at transition events
  than at matched non-events."
- The non-survival cases concentrate in early observations. This makes
  a batch/condition/artifact audit necessary before a stronger biological
  claim.

## Next

- `4082_scale_robustness_on_surviving_observation_class`: check whether
  the 15/19 survival result is robust to scale (`k`), lag, and matching
  choices.
- `4082b_early_failure_condition_or_artifact_audit`: compare Ob1/3/6/8
  against the surviving observations using event density, state-duration
  structure, trajectory quality, and recording/batch metadata if
  available.

## Artifacts

- `Output/4081d/heterogeneity_features.csv`
- `Output/4081d/feature_contrasts.csv`
- `Output/4081d/figures/4081d_observation_route_map.png`
- `Output/4081d/figures/4081d_t1_ratio_vs_event_specificity.png`
- `Output/4081d/figures/4081d_feature_contrasts.png`
