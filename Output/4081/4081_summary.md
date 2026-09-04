# Node 4081 Summary

## Question

Does local affine deformation explain the global-affine residual targets, or does a local non-affine residual survive for T1/T2 separately?

## Why this node exists

4080 showed local affine fits are numerically feasible. 4081 is the first
geometry-ladder pilot after the 4075 target split.

## Frozen Target Policy

```text
T1 primary = transition tangential residual
T2 secondary = general residual activity
retired primary = radial residual, core-edge speed
```

## Baseline

`B3_global_affine` reference values come from 4071/4074 Ob1 tables.

`B4_local_affine` local non-affine metrics are computed with the pilot settings.

## Null / Control

Matched non-event windows are used for the local metrics.

## Results

| target_id | role | k | b3_ob1_event_direction_abs_z | local_event_direction_abs_z | local_non_event_direction_abs_median_z | local_event_minus_non_event_direction_z | local_to_b3_direction_ratio | event_conditioned_local_gate | geometry_ladder_reading |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T1_transition_tangential_residual | primary_transition_target | 8 | 0.711 | 0.2646 | 0.3311 | -0.0665 | 0.3721 | False | local_nonaffine_not_event_conditioned |
| T1_support_edge_core_tangential | supporting_transition_spatial_metric | 8 | 0.05478 | 0.155 | 0.2298 | -0.07486 | 2.829 | False | local_nonaffine_not_event_conditioned |
| T2_general_speed_rms | secondary_general_activity | 8 | 0.9709 | 0.1786 | 0.2295 | -0.05093 | 0.184 | False | local_affine_largely_absorbs_b3_signal |
| T2_general_cov_trace | secondary_general_activity | 8 | 1.016 | 0.1104 | 0.1892 | -0.07885 | 0.1087 | False | local_affine_largely_absorbs_b3_signal |
| T1_transition_tangential_residual | primary_transition_target | 10 | 0.711 | 0.1736 | 0.2529 | -0.07932 | 0.2441 | False | local_affine_largely_absorbs_b3_signal |
| T1_support_edge_core_tangential | supporting_transition_spatial_metric | 10 | 0.05478 | 0.009987 | 0.2206 | -0.2106 | 0.1823 | False | local_affine_largely_absorbs_b3_signal |
| T2_general_speed_rms | secondary_general_activity | 10 | 0.9709 | 0.03738 | 0.2763 | -0.2389 | 0.0385 | False | local_affine_largely_absorbs_b3_signal |
| T2_general_cov_trace | secondary_general_activity | 10 | 1.016 | 0.08518 | 0.2672 | -0.182 | 0.08388 | False | local_affine_largely_absorbs_b3_signal |

## Gate Evaluation

`boundary_t1_absorbed_or_not_event_conditioned`

## Interpretation

The primary tangential target does not clearly survive local-affine residualization in this Ob1 pilot.

## What This Does Not Prove

4081 is still an Ob1 pilot. It does not prove a general midge-swarm mechanism.

## Decision

`boundary_t1_absorbed_or_not_event_conditioned`

## Next Node

`4081b_confirm_t1_absorption_or_pause_route_a`
