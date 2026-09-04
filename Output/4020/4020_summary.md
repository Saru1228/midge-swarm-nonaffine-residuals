# 4020 One-Fish Residual State Redistribution Pilot

## Scope

4020 follows `4003_residual_velocity_synthesis`. It uses the new pilot-first
rule and runs only `Ob1` by default.

Plain-language question:

> After removing ordinary group geometry, do the fish with stronger residual
> speed/radial/tangential states shift across core/mid/edge regions around
> compact-density transitions?

## EGRT Node

| field | value |
| --- | --- |
| node_id | 4020_one_fish_residual_state_redistribution_audit |
| parent | 4003_residual_velocity_synthesis |
| node_type | single-observation pilot screen |
| pilot observation | Ob1 |
| decision | pilot_support_one_fish_residual_state_redistribution_signal |
| recommended next node | 4020b selective multi-ob expansion |
| boundary reading | Single-observation pilot found multiple state-redistribution variables above shifted-event null gates. |

## Methods

- Fit the per-frame affine geometric baseline.
- Compute one-fish affine residual states.
- Split fish into core/mid/edge radial shells.
- Measure residual energy shares, edge-core residual state differences, top
  residual-fish location, and residual concentration.
- Remove a `1.0` sec smooth trend within the pilot
  observation.
- Compare transition post-minus-pre direction contrasts against `64`
  shifted-event null replicates.

Pilot gate:

- event count >= `20`;
- real-null direction gap >= `0.15`;
- shifted-null p <= `0.15`;
- oriented positive event fraction >= `0.55`;
- at least `2` survivors needed before multi-ob
  expansion.

## Decision Metrics

| node_id | node_type | pilot_ob | n_surviving_variables | surviving_variables | surviving_families | eg_rt_decision | recommended_next_node | boundary_reading |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4020_one_fish_residual_state_redistribution_audit | single-observation pilot screen | 1 | 2 | edge_minus_core_radial_abs_q75, edge_minus_core_speed_q75 | shell_radial_state: edge_minus_core_radial_abs_q75; shell_residual_speed: edge_minus_core_speed_q75 | pilot_support_one_fish_residual_state_redistribution_signal | 4020b selective multi-ob expansion | Single-observation pilot found multiple state-redistribution variables above shifted-event null gates. |

## Pilot-Surviving Variables

| variable | family | n_ob | n_events | real_median_low_to_high_delta_z | real_median_high_to_low_delta_z | real_median_direction_contrast_z | real_abs_median_direction_contrast_z | real_median_oriented_delta_z | real_oriented_positive_fraction | null_abs_median_direction_contrast_z | real_minus_null_abs_direction_contrast_z | p_null_abs_direction_ge_real | pilot_survives_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| edge_minus_core_radial_abs_q75 | shell_radial_state | 1 | 28 | 0.2745 | -0.6227 | 0.8971 | 0.8971 | 0.3919 | 0.6786 | 0.2441 | 0.653 | 0.04615 | True |
| edge_minus_core_speed_q75 | shell_residual_speed | 1 | 28 | 0.4741 | -0.4079 | 0.8819 | 0.8819 | 0.4079 | 0.5714 | 0.3178 | 0.5642 | 0.07692 | True |

## Top Direction/Null Rows

| variable | family | n_ob | n_events | real_median_low_to_high_delta_z | real_median_high_to_low_delta_z | real_median_direction_contrast_z | real_abs_median_direction_contrast_z | real_median_oriented_delta_z | real_oriented_positive_fraction | null_abs_median_direction_contrast_z | real_minus_null_abs_direction_contrast_z | p_null_abs_direction_ge_real | pilot_survives_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| top_tangential_radius_mean_z | high_residual_fish_location | 1 | 28 | -0.3248 | 0.7192 | -1.044 | 1.044 | -0.4722 | 0.3571 | 0.2329 | 0.8111 | 0.06154 | False |
| edge_minus_core_radial_abs_q75 | shell_radial_state | 1 | 28 | 0.2745 | -0.6227 | 0.8971 | 0.8971 | 0.3919 | 0.6786 | 0.2441 | 0.653 | 0.04615 | True |
| edge_minus_core_speed_q75 | shell_residual_speed | 1 | 28 | 0.4741 | -0.4079 | 0.8819 | 0.8819 | 0.4079 | 0.5714 | 0.3178 | 0.5642 | 0.07692 | True |
| edge_minus_core_radial_abs_mean | shell_radial_state | 1 | 28 | 0.1873 | -0.4871 | 0.6743 | 0.6743 | 0.3422 | 0.5357 | 0.2953 | 0.379 | 0.2154 | False |
| edge_high_speed_fraction_minus_core | high_residual_fish_location | 1 | 28 | 0.3937 | -0.2643 | 0.6579 | 0.6579 | 0.3366 | 0.6071 | 0.3026 | 0.3554 | 0.1538 | False |
| top_speed_radius_mean_z | high_residual_fish_location | 1 | 28 | -0.1591 | 0.4573 | -0.6164 | 0.6164 | -0.2653 | 0.3929 | 0.2925 | 0.3239 | 0.2 | False |
| edge_minus_core_speed_mean | shell_residual_speed | 1 | 28 | 0.1665 | -0.4334 | 0.5999 | 0.5999 | 0.3721 | 0.5714 | 0.3002 | 0.2997 | 0.2462 | False |
| core_energy_share | residual_energy_distribution | 1 | 28 | -0.2957 | 0.2241 | -0.5198 | 0.5198 | -0.2241 | 0.3929 | 0.3123 | 0.2075 | 0.3231 | False |

## Interpretation

This is a pilot, not a full-series confirmation. A positive result only
supports expanding selectively. A weak result should be recorded as a boundary
and routed to the next node instead of spending time on a full 19-observation
run.

## Outputs

- `Output/4020/4020_egrt_node.json`
- `Output/4020/tables/one_fish_state_direction_null_comparison.csv`
- `Output/4020/tables/egrt_decision_summary.csv`
- `Output/4020/figures/one_fish_state_direction_screen.png`
- `Output/4020/figures/one_fish_state_aligned_profiles.png`
