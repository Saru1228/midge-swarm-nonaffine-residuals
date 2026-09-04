# Node 4085 Summary

## Question

When does the 4084 edge/core T1 local non-affine contrast appear
relative to compact-density transitions?

## What Else Can Be Dug Here

Before leaving 408x, there are four defensible directions:

- event-phase profile: when the 4084 edge/core contrast appears;
- phase-space projection: trajectory through variables such as
  `all_tangential`, `shell_edge_minus_core`, compact state, and possibly
  radial/density coordinates;
- signed low-to-high versus high-to-low decomposition;
- failure-boundary sensitivity for Ob1/Ob3/Ob6/Ob8.

This node runs the first one. The phase-space branch is kept as
`4085b_phase_space_projection_of_t1_edge_core_signal`, because the
temporal profile tells us which time slice should be projected.

## Inputs

- `Output/4084/per_ob/Ob*/local_spatial_metric_frame.csv`
- `Output/3045/tables/transition_events.csv`

## Method

Direction-aligned profiles are built over:

```text
relative time = [-0.5, 0.5] sec
step = 0.05 sec
matched non-event replicates = 40
phase bins = early_pre, near_pre, near_post, late_post
target variable = shell_edge_minus_core
```

Low-to-high events are aligned positive and high-to-low events negative.
The raw event-type profiles are also saved separately, but interpretation
of signed asymmetry is deferred to 4086.

## Decision

`boundary_edge_core_no_stable_phase_but_diffuse_t1_has_phase_profile`

## Main Reading

The edge/core target `shell_edge_minus_core` has no stable phase-localized profile, but secondary T1 variables do: all_tangential:near_pre (8/14). This routes interpretation toward signed/state decomposition before any phase-space claim.

```text
observations tested = 14
majority gate count = 8
target near-transition gate total = 2
target majority phases = none
secondary majority phases = all_tangential:near_pre (8/14)
```

## Target Phase Summary

| variable | phase | phase_gate_count | phase_gate_fraction | median_abs_event_minus_abs_null_z | median_event_minus_null_phase_z | majority_gate | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| shell_edge_minus_core | early_pre | 1 | 0.07143 | -0.01728 | -0.01082 | False | minority or observation-specific phase |
| shell_edge_minus_core | near_pre | 1 | 0.07143 | 0.02306 | 0.02977 | False | minority or observation-specific phase |
| shell_edge_minus_core | near_post | 1 | 0.07143 | 0.04716 | -0.0286 | False | minority or observation-specific phase |
| shell_edge_minus_core | late_post | 0 | 0 | 0.01471 | -0.03224 | False | no phase gate |

## Observation Classification

| ob | target_variable | peak_phase | peak_abs_event_minus_abs_null_z | peak_p_null_abs_ge_real_abs | phase_gate_any | event_centered_gate | phase_class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | shell_edge_minus_core | near_post | 0.1284 | 0 | True | True | post_transition_response_candidate |
| 5 | shell_edge_minus_core | early_pre | 0.1359 | 0.025 | True | False | broad_state_or_offcenter_profile_candidate |
| 7 | shell_edge_minus_core | near_post | 0.09976 | 0.1 | False | False | no_clear_phase_gate |
| 9 | shell_edge_minus_core | near_pre | 0.094 | 0.125 | False | False | no_clear_phase_gate |
| 10 | shell_edge_minus_core | near_pre | 0.06701 | 0.225 | False | False | no_clear_phase_gate |
| 11 | shell_edge_minus_core | near_post | 0.04585 | 0.125 | False | False | no_clear_phase_gate |
| 12 | shell_edge_minus_core | late_post | 0.08048 | 0.025 | False | False | no_clear_phase_gate |
| 13 | shell_edge_minus_core | near_pre | 0.03251 | 0.275 | False | False | no_clear_phase_gate |
| 14 | shell_edge_minus_core | early_pre | 0.07401 | 0.225 | False | False | no_clear_phase_gate |
| 15 | shell_edge_minus_core | near_pre | 0.1332 | 0.075 | True | True | pre_transition_buildup_candidate |
| 16 | shell_edge_minus_core | near_post | 0.06612 | 0.15 | False | False | no_clear_phase_gate |
| 17 | shell_edge_minus_core | late_post | 0.08297 | 0.025 | False | False | no_clear_phase_gate |
| 18 | shell_edge_minus_core | near_pre | 0.07086 | 0.125 | False | False | no_clear_phase_gate |
| 19 | shell_edge_minus_core | early_pre | 0.06697 | 0.025 | False | False | no_clear_phase_gate |

## Boundary

A phase profile is interpreted only if it beats matched non-event
windows. If no single phase dominates, this node routes to signed
decomposition rather than claiming pre-trigger, trigger, or relaxation.

## Next

`4086_signed_direction_and_state_decomposition`

Side branch available:

`4085b_phase_space_projection_of_t1_edge_core_signal`

## Artifacts

- `Output/4085/aggregate_profiles.csv`
- `Output/4085/phase_profile_rows.csv`
- `Output/4085/ob_phase_classification.csv`
- `Output/4085/variable_phase_summary.csv`
- `Output/4085/figures/4085_target_profiles.png`
- `Output/4085/figures/4085_target_phase_heatmap.png`
- `Output/4085/figures/4085_variable_phase_gate_counts.png`
