# Node 4074 Summary

## Question

Is the frozen residual organization specific to compact-density transition events, or does it also appear in matched non-event windows?

## Why this node exists

4071 showed that the frozen residual target has enough Ob1-Ob3 support under shifted-event nulls. 4074 checks whether this is genuinely transition-conditioned, or whether comparable residual reconfiguration appears in event-free matched windows.

## Data

Observations: `Ob1, Ob2, Ob3`

No full 19-observation run was performed. This node reuses the 4002A global-affine residual metric implementation and writes only to `Output/4074`.

## Frozen parameters

```text
primary metrics = Output/4072/primary_metrics.csv
stable decision core = 4071 passing metrics
baseline = B3_global_affine
control = N5_matched_non_event_window
n_non_event_replicates = 80
```

## Baseline

`B3_global_affine`: translation plus global affine deformation subtraction.

## Null model

`N5_matched_non_event_window`: non-event windows matched within observation while preserving event-label counts for direction-contrast comparison.

## Primary metrics

| variable | is_4071_stable_core | direction_gt_non_event_count | median_direction_real_minus_non_event_z | median_p_non_event_direction_ge_real | activity_gt_non_event_count | median_activity_real_minus_non_event_z | metric_event_conditioned_gate | metric_event_free_activity_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| resid_velocity_cov_trace | True | 2 | 0.06954 | 0.4375 | 2 | 0.1491 | False | True |
| resid_speed_rms | True | 3 | 0.06535 | 0.4125 | 2 | 0.1255 | False | True |
| resid_tangential_speed_mean | True | 3 | 0.3429 | 0.1625 | 3 | 0.03348 | True | False |
| resid_radial_abs_mean | False | 0 | -0.2024 | 0.775 | 2 | 0.03205 | False | False |
| edge_minus_core_resid_speed | False | 1 | -0.01134 | 0.5125 | 2 | 0.1644 | False | True |
| edge_minus_core_resid_tangential | True | 2 | 0.04221 | 0.45 | 1 | -0.1513 | False | False |

## Results

- Stable core metrics: 4
- Stable-core event-conditioned direction gates: 1
- Stable-core event-free/general activity gates: 2
- Node decision: `boundary_mixed_event_conditioning`

Event-conditioned metrics:

| variable | is_4071_stable_core | median_direction_real_minus_non_event_z | direction_gt_non_event_count |
| --- | --- | --- | --- |
| resid_tangential_speed_mean | True | 0.3429 | 3 |

Event-free/general activity metrics:

| variable | is_4071_stable_core | median_activity_real_minus_non_event_z | activity_gt_non_event_count |
| --- | --- | --- | --- |
| resid_velocity_cov_trace | True | 0.1491 | 2 |
| resid_speed_rms | True | 0.1255 | 2 |
| edge_minus_core_resid_speed | False | 0.1644 | 2 |

## Dataset-wise replication

See `ob_level_event_conditioning.csv`.

## Gate evaluation

`boundary_mixed_event_conditioning`

## What this rules out

If a stable-core metric fails the event-conditioned gate, it should not be used as a transition-specific target in 408x without a caveat.

## What this does NOT prove

4074 does not prove local non-affinity, stochasticity, propagation, or network mechanism. It only controls event selection using matched non-event windows.

## Decision

`boundary_mixed_event_conditioning`

## Next node

`M0_review_before_4080`
