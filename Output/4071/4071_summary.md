# Node 4071 Summary

## Question

Do the frozen 4072 residual target metrics replicate across `Ob1/Ob2/Ob3` under the frozen `B3_global_affine + N1_shifted_event` registry?

## Why this node exists

4001/4002A were strong as full-series screens, but 4070 identified a risk: the result could still be pooled or dataset-specific. 4071 checks the frozen 4072 primary metrics one observation at a time before local-affine mechanism tests.

## Data

Observations: `Ob1, Ob2, Ob3`

No all-19 run was performed. This node reuses the 4002A global-affine residual metric implementation and writes only to `Output/4071`.

## Frozen parameters

```text
primary metrics = Output/4072/primary_metrics.csv
baseline = B3_global_affine
null = N1_shifted_event
n_null = 80
```

## Baseline

`B3_global_affine`: translation plus global affine deformation subtraction.

## Null model

`N1_shifted_event`: circularly shifted event times within observation.

## Primary metrics

| variable | taxonomy_class | n_ob_valid | directional_consistency | median_real_abs_direction_contrast_z | median_null_abs_direction_contrast_z | median_real_minus_null_abs_direction_contrast_z | n_ob_effect_gt_null | metric_passes_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| resid_velocity_cov_trace | V_covariance_anisotropy | 3 | 0.6667 | 0.3413 | 0.3274 | 0.01394 | 2 | True |
| resid_speed_rms | I_magnitude_energy | 3 | 0.6667 | 0.3434 | 0.3101 | 0.03333 | 2 | True |
| resid_tangential_speed_mean | III_tangential | 3 | 0.6667 | 0.6135 | 0.271 | 0.304 | 3 | True |
| resid_radial_abs_mean | II_radial | 3 | 0.6667 | 0.1632 | 0.3178 | -0.1546 | 0 | False |
| edge_minus_core_resid_speed | VII_core_edge_contrast | 3 | 0.6667 | 0.2977 | 0.3065 | -0.008842 | 1 | False |
| edge_minus_core_resid_tangential | VII_core_edge_contrast | 3 | 0.6667 | 0.4036 | 0.3179 | 0.08573 | 2 | True |

## Results

- Metric passes: 4 / 6
- Residual-intensity anchor pass: True
- Node decision: `pass`

Passing metrics:

| variable | taxonomy_class | median_real_abs_direction_contrast_z | median_real_minus_null_abs_direction_contrast_z | n_ob_effect_gt_null |
| --- | --- | --- | --- | --- |
| resid_velocity_cov_trace | V_covariance_anisotropy | 0.3413 | 0.01394 | 2 |
| resid_speed_rms | I_magnitude_energy | 0.3434 | 0.03333 | 2 |
| resid_tangential_speed_mean | III_tangential | 0.6135 | 0.304 | 3 |
| edge_minus_core_resid_tangential | VII_core_edge_contrast | 0.4036 | 0.08573 | 2 |

Non-passing metrics:

| variable | taxonomy_class | median_real_abs_direction_contrast_z | median_real_minus_null_abs_direction_contrast_z | n_ob_effect_gt_null |
| --- | --- | --- | --- | --- |
| resid_radial_abs_mean | II_radial | 0.1632 | -0.1546 | 0 |
| edge_minus_core_resid_speed | VII_core_edge_contrast | 0.2977 | -0.008842 | 1 |

## Dataset-wise replication

See `ob_level_effects.csv`. The audit explicitly reports each observation rather than relying on pooled significance.

## Gate evaluation

`pass`

Node gate:

```text
pass: >=4/6 primary metrics pass AND at least one residual-intensity anchor passes
boundary: >=2/6 primary metrics pass
fail: otherwise
```

## What this rules out

If a metric fails here, it should not be used as a cross-dataset primary target in 408x without a new reason. The node also prevents using pooled full-series significance as the only robustness evidence.

## What this does NOT prove

4071 does not prove local non-affinity, stochasticity, propagation, or network mechanism. It only checks Ob1-Ob3 replication under the global-affine residual baseline.

## Decision

`pass`

## Next node

`4074_event_free_vs_event_conditioned_audit`
