# 4001 Geometric Baseline Residual Audit

## Scope

4001 starts the 4xxx line. The question is whether the 3045c velocity event
signal is an extra coordination signal, or mostly a geometric inevitability of
non-rigid group deformation.

## Plain-Language Baseline

For every frame, we ask how much of each fish's velocity can be explained by
where it is inside the group:

- the whole group translating;
- the group rotating;
- the group expanding or contracting;
- the group stretching or shearing.

All of those are captured by a per-frame affine model:

`velocity = group_center_velocity + relative_position * A`

The remaining velocity is `affine_resid`.

## EGRT Node

| field | value |
| --- | --- |
| node_id | 4001_geometric_baseline_residual_audit |
| parent | 3045d_velocity_timing_audit |
| node_type | artifact-control / baseline audit |
| decision | support_extra_affine_residual_velocity_coordination |
| recommended next node | 4002 residual coordination structure audit |
| boundary reading | Velocity event signal survives after subtracting translation plus affine deformation, supporting an extra coordination route. |

## Methods

- Selected variables from 3045c direction survivors: `speed_rms, velocity_cov_trace, mean_speed, tangential_speed_mean`.
- Components: `raw`, `affine_pred`, `affine_resid`.
- Smooth trend removal: `1.0` sec centered rolling mean.
- Event feature: post-minus-pre residual change around 3045 persistent transitions.
- Direction alignment: low-to-high positive, high-to-low negative.
- Null: circularly shifted event times within each observation.
- Null replicates: `160`.

## Decision Metrics

| node_id | node_type | n_raw_direction_survivors | n_affine_pred_direction_survivors | n_affine_resid_direction_survivors | raw_surviving_variables | affine_pred_surviving_variables | affine_resid_surviving_variables | median_affine_pred_to_raw_abs_ratio_for_raw_survivors | median_affine_resid_to_raw_abs_ratio_for_raw_survivors | aligned_affine_r2_delta_z | eg_rt_decision | recommended_next_node | boundary_reading |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4001_geometric_baseline_residual_audit | artifact-control / baseline audit | 4 | 1 | 4 | speed_rms, velocity_cov_trace, mean_speed, tangential_speed_mean | mean_speed | speed_rms, velocity_cov_trace, mean_speed, tangential_speed_mean | 0.5964 | 0.9554 | 0.03288 | support_extra_affine_residual_velocity_coordination | 4002 residual coordination structure audit | Velocity event signal survives after subtracting translation plus affine deformation, supporting an extra coordination route. |

## Component Retention Summary

| variable | raw_abs_direction_contrast_z | affine_pred_abs_direction_contrast_z | affine_resid_abs_direction_contrast_z | affine_pred_to_raw_abs_ratio | affine_resid_to_raw_abs_ratio | raw_survives_gate | affine_pred_survives_gate | affine_resid_survives_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| speed_rms | 0.873 | 0.4146 | 0.5522 | 0.4749 | 0.6325 | True | False | True |
| velocity_cov_trace | 0.6354 | 0.4643 | 0.5791 | 0.7307 | 0.9113 | True | False | True |
| mean_speed | 0.5391 | 0.3138 | 0.5388 | 0.5821 | 0.9995 | True | True | True |
| tangential_speed_mean | 0.3701 | 0.226 | 0.4242 | 0.6107 | 1.146 | True | False | True |

## Direction Null Comparison

| component | variable | metric_key | n_ob | n_events | real_median_low_to_high_delta_z | real_median_high_to_low_delta_z | real_median_direction_contrast_z | real_abs_median_direction_contrast_z | direction_contrast_sign_consistency | null_abs_median_direction_contrast_z | real_minus_null_abs_direction_contrast_z | p_null_abs_direction_ge_real | direction_survives_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| affine_pred | mean_speed | affine_pred__mean_speed | 19 | 1471 | 0.05459 | -0.1992 | 0.3138 | 0.3138 | 0.7368 | 0.05857 | 0.2552 | 0.006211 | True |
| affine_resid | mean_speed | affine_resid__mean_speed | 19 | 1471 | 0.2189 | -0.2601 | 0.5388 | 0.5388 | 0.8947 | 0.07022 | 0.4686 | 0.006211 | True |
| raw | mean_speed | raw__mean_speed | 19 | 1471 | 0.3347 | -0.2913 | 0.5391 | 0.5391 | 0.8947 | 0.05459 | 0.4845 | 0.006211 | True |
| affine_pred | speed_rms | affine_pred__speed_rms | 19 | 1471 | 0.07811 | -0.1825 | 0.4146 | 0.4146 | 0.6316 | 0.06495 | 0.3496 | 0.006211 | False |
| affine_resid | speed_rms | affine_resid__speed_rms | 19 | 1471 | 0.2786 | -0.3206 | 0.5522 | 0.5522 | 0.8947 | 0.06617 | 0.486 | 0.006211 | True |
| raw | speed_rms | raw__speed_rms | 19 | 1471 | 0.2261 | -0.4386 | 0.873 | 0.873 | 0.8421 | 0.07101 | 0.802 | 0.006211 | True |
| affine_pred | tangential_speed_mean | affine_pred__tangential_speed_mean | 19 | 1471 | 0.08096 | -0.1479 | 0.226 | 0.226 | 0.6316 | 0.06284 | 0.1632 | 0.01242 | False |
| affine_resid | tangential_speed_mean | affine_resid__tangential_speed_mean | 19 | 1471 | 0.1792 | -0.201 | 0.4242 | 0.4242 | 0.9474 | 0.05876 | 0.3655 | 0.006211 | True |
| raw | tangential_speed_mean | raw__tangential_speed_mean | 19 | 1471 | 0.1785 | -0.2795 | 0.3701 | 0.3701 | 0.8947 | 0.06146 | 0.3086 | 0.006211 | True |
| affine_pred | velocity_cov_trace | affine_pred__velocity_cov_trace | 19 | 1471 | 0.1712 | -0.2819 | 0.4643 | 0.4643 | 0.6842 | 0.06129 | 0.403 | 0.006211 | False |
| affine_resid | velocity_cov_trace | affine_resid__velocity_cov_trace | 19 | 1471 | 0.2593 | -0.3315 | 0.5791 | 0.5791 | 0.8947 | 0.06449 | 0.5146 | 0.006211 | True |
| raw | velocity_cov_trace | raw__velocity_cov_trace | 19 | 1471 | 0.3017 | -0.4057 | 0.6354 | 0.6354 | 0.8421 | 0.0651 | 0.5703 | 0.006211 | True |

## Geometry Event Summary

| metric | n_ob | n_events | median_aligned_delta_z | q25_aligned_delta_z | q75_aligned_delta_z | sign_consistency |
| --- | --- | --- | --- | --- | --- | --- |
| affine_r2_centered | 19 | 1471 | 0.03288 | -0.1096 | 0.1839 | 0.5263 |
| affine_trace_rate | 19 | 1471 | 0.0242 | -0.1384 | 0.06394 | 0.5789 |
| affine_residual_rms_fraction | 19 | 1471 | -0.05536 | -0.1818 | 0.09763 | 0.5789 |

## Interpretation

If `affine_resid` keeps the transition-aligned signal, the speed result cannot
be dismissed as ordinary shape change. If `affine_resid` loses the signal while
`affine_pred` or low residual-retention ratios explain it, the safer reading is
that the earlier speed result is mainly a byproduct of non-rigid group geometry.

## Outputs

- `Output/4001/4001_egrt_node.json`
- `Output/4001/tables/component_direction_null_comparison.csv`
- `Output/4001/tables/component_retention_summary.csv`
- `Output/4001/tables/geometric_event_summary.csv`
- `Output/4001/tables/egrt_decision_summary.csv`
- `Output/4001/figures/component_direction_signal_allocation.png`
- `Output/4001/figures/affine_residual_retention_ratios.png`
- `Output/4001/figures/component_aligned_velocity_profiles.png`
