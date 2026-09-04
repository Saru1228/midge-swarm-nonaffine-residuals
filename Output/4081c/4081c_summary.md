# Node 4081c Summary

## Question

Across all observations, does the T1 transition tangential residual survive
local-affine residualization, get absorbed by local affine geometry, or vary by
observation?

## Run

```text
obs = 1-19
k = 8,10
lag = 0.1
n_replicates = 40
```

## Decision

`support_observation_heterogeneous_but_common_t1_survival`

## Class Counts

```json
{
  "t1_not_event_conditioned_after_local_affine": 4,
  "t1_local_nonaffine_survives_both_k": 14,
  "t1_local_nonaffine_survives_one_k": 1
}
```

## Observation Classification

| ob | n_events | ob_route_a_class | t1_gate_k_values | t1_median_local_to_b3_ratio | t1_median_local_event_minus_non_event_z | t2_gate_count |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 28 | t1_not_event_conditioned_after_local_affine |  | 0.3081 | -0.0189 | 0 |
| 2 | 43 | t1_local_nonaffine_survives_both_k | 8,10 | 0.8905 | 0.3596 | 4 |
| 3 | 40 | t1_not_event_conditioned_after_local_affine |  | 0.4612 | -0.1775 | 2 |
| 4 | 58 | t1_local_nonaffine_survives_one_k | 10 | 0.5667 | 0.03849 | 4 |
| 5 | 93 | t1_local_nonaffine_survives_both_k | 8,10 | 0.8399 | 0.1828 | 4 |
| 6 | 112 | t1_not_event_conditioned_after_local_affine |  | 37.25 | -0.1299 | 0 |
| 7 | 33 | t1_local_nonaffine_survives_both_k | 8,10 | 1.097 | 0.1723 | 0 |
| 8 | 84 | t1_not_event_conditioned_after_local_affine |  | 1.605 | -0.09128 | 2 |
| 9 | 36 | t1_local_nonaffine_survives_both_k | 8,10 | 2.1 | 0.4661 | 4 |
| 10 | 36 | t1_local_nonaffine_survives_both_k | 8,10 | 1.202 | 0.363 | 4 |
| 11 | 119 | t1_local_nonaffine_survives_both_k | 8,10 | 1.724 | 0.6009 | 4 |
| 12 | 91 | t1_local_nonaffine_survives_both_k | 8,10 | 2.815 | 0.315 | 4 |
| 13 | 102 | t1_local_nonaffine_survives_both_k | 8,10 | 1.506 | 0.517 | 4 |
| 14 | 47 | t1_local_nonaffine_survives_both_k | 8,10 | 0.984 | 0.3732 | 4 |
| 15 | 96 | t1_local_nonaffine_survives_both_k | 8,10 | 1.53 | 0.6945 | 4 |
| 16 | 84 | t1_local_nonaffine_survives_both_k | 8,10 | 2.277 | 0.5399 | 4 |
| 17 | 122 | t1_local_nonaffine_survives_both_k | 8,10 | 2.003 | 0.2287 | 4 |
| 18 | 103 | t1_local_nonaffine_survives_both_k | 8,10 | 0.6995 | 0.2802 | 4 |
| 19 | 143 | t1_local_nonaffine_survives_both_k | 8,10 | 1.53 | 0.642 | 4 |

## Interpretation

This node is the full-observation adjudication requested after Ob1 and Ob2
disagreed. It should not be reduced to a pooled significance claim. The
important output is the observation-level classification pattern.

## Next

`4082_scale_robustness_on_surviving_observation_class`
