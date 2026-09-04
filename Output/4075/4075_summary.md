# Node 4075 Summary

## Question

After 4074 split the target, should Route A enter 4080, and what exactly should 408x test?

## Why this node exists

4074 produced a boundary, not a clean pass. Stopping there would leave the next
experiment underspecified. This M0 review decides whether the boundary should
stop the route or refine the target before local-affine testing.

## Inputs

- `Output/4071/decision.json`
- `Output/4071/metric_replication_summary.csv`
- `Output/4074/decision.json`
- `Output/4074/event_conditioning_summary.csv`

## Evidence Summary

4071:

```text
result = pass
metric_passes = 4 / 6
anchor_pass = True
```

4074:

```text
result = boundary_mixed_event_conditioning
stable_core_event_conditioned_count = 1 / 4
stable_core_activity_gate_count = 2 / 4
```

## Target Decision

| target_id | target_role | primary_metrics | supporting_metrics | decision | next_node_use |
| --- | --- | --- | --- | --- | --- |
| T1_transition_tangential_residual | primary_route_a_target | resid_tangential_speed_mean | edge_minus_core_resid_tangential | carry_forward_as_primary | 4080 feasibility is allowed; 4081 should evaluate this as the main event-conditioned target. |
| T2_general_residual_activity | secondary_route_a_target | resid_velocity_cov_trace; resid_speed_rms |  | carry_forward_as_secondary_general_activity | 4080 feasibility may include these for fit diagnostics; 4081 should analyze them separately from transition-specific targets. |
| T3_radial_residual | retired_primary | resid_radial_abs_mean |  | retire_from_primary_route | Use only as optional diagnostic if already cheap. |
| T4_core_edge_speed | retired_primary | edge_minus_core_resid_speed |  | retire_from_primary_route | Use only as optional diagnostic if already cheap. |

## Main Interpretation

4074 should not stop the 4xxx program, but it does stop the idea that all
affine-residual velocity metrics form one transition-specific target.

The target must split:

1. `T1_transition_tangential_residual`
   - primary metric: `resid_tangential_speed_mean`;
   - supporting metric: `edge_minus_core_resid_tangential`;
   - this is the primary Route A target.

2. `T2_general_residual_activity`
   - primary metrics: `resid_velocity_cov_trace`, `resid_speed_rms`;
   - this is a secondary general-activity target, not a transition-specific
     mechanism claim.

Retired from primary Route A claims:

```text
resid_radial_abs_mean
edge_minus_core_resid_speed
```

## Gate Evaluation

`split_target_enter_4080_feasibility`

Reason:

- 4071 gives enough cross-observation support to continue.
- 4074 shows mixed event conditioning, but at least one stable-core metric is
  clearly event-conditioned.
- The boundary can be resolved by splitting targets rather than stopping the
  route or merging phenomena.

## What This Rules Out

Do not enter 408x with a single undifferentiated residual target.

Do not write:

```text
the full affine-residual velocity organization is transition-specific
```

Write instead:

```text
the transition-conditioned component is mainly tangential;
residual intensity/covariance is broader general residual activity.
```

## What This Does Not Prove

4075 does not prove local non-affinity. It only authorizes a feasibility test.

## Decision

`split_target_enter_4080_feasibility`

## Next Node

`4080_local_affine_feasibility`

4080 should test whether local affine fitting is identifiable and stable. It
should not yet interpret biological mechanism.
