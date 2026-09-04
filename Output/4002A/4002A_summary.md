# 4002A Residual Spatial-Structure Audit

## Scope

4001 showed that velocity event signals survive an affine geometric baseline.
4002A asks what kind of affine-residual velocity structure remains.

Plain-language question:

> After removing ordinary school deformation, is the leftover velocity signal
> located at the edge, radial, tangential/swirl-like, or globally ordered?

## EGRT Node

| field | value |
| --- | --- |
| node_id | 4002a_residual_spatial_structure_audit |
| parent | 4001_geometric_baseline_residual_audit |
| node_type | mechanism screen |
| decision | support_residual_edge_core_structure_signal |
| recommended next node | 4002b edge/core residual localization audit |
| boundary reading | Residual affine-subtracted velocities have shifted-null robust spatial-structure signals; route to the strongest interpretable family. |

## Methods

- Per frame, fit and subtract the affine velocity baseline from 4001.
- Compute affine-residual spatial metrics:
  - edge/core residual speed and tangential differences;
  - radius-residual speed correlations;
  - residual radial motion;
  - residual tangential and angular-momentum coherence;
  - residual speed intensity and residual polarization.
- Remove a `1.0` sec smooth trend within each observation.
- Compare post-minus-pre transition changes with `160` shifted-event null replicates.

## Decision Metrics

| node_id | node_type | n_surviving_variables | n_edge_core_survivors | n_radial_survivors | n_tangential_swirl_survivors | n_residual_intensity_survivors | n_residual_order_survivors | surviving_variables | eg_rt_decision | recommended_next_node | boundary_reading |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4002a_residual_spatial_structure_audit | mechanism screen | 6 | 2 | 1 | 1 | 2 | 0 | resid_velocity_cov_trace, resid_speed_rms, resid_tangential_speed_mean, resid_radial_abs_mean, edge_minus_core_resid_speed, edge_minus_core_resid_tangential | support_residual_edge_core_structure_signal | 4002b edge/core residual localization audit | Residual affine-subtracted velocities have shifted-null robust spatial-structure signals; route to the strongest interpretable family. |

## Surviving Variables

| variable | family | n_ob | n_events | real_median_low_to_high_delta_z | real_median_high_to_low_delta_z | real_median_direction_contrast_z | real_abs_median_direction_contrast_z | direction_contrast_sign_consistency | null_abs_median_direction_contrast_z | real_minus_null_abs_direction_contrast_z | p_null_abs_direction_ge_real | direction_survives_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| resid_velocity_cov_trace | residual_intensity | 19 | 1471 | 0.2593 | -0.3315 | 0.5791 | 0.5791 | 0.8947 | 0.0702 | 0.5089 | 0.006211 | True |
| resid_speed_rms | residual_intensity | 19 | 1471 | 0.2786 | -0.3206 | 0.5522 | 0.5522 | 0.8947 | 0.07344 | 0.4788 | 0.006211 | True |
| resid_tangential_speed_mean | tangential_swirl | 19 | 1471 | 0.1792 | -0.201 | 0.4242 | 0.4242 | 0.9474 | 0.06828 | 0.356 | 0.006211 | True |
| resid_radial_abs_mean | radial | 19 | 1471 | 0.151 | -0.08377 | 0.2535 | 0.2535 | 0.7895 | 0.05272 | 0.2008 | 0.01863 | True |
| edge_minus_core_resid_speed | edge_core | 19 | 1471 | -0.1057 | 0.05148 | -0.2193 | 0.2193 | 0.7368 | 0.07513 | 0.1442 | 0.03727 | True |
| edge_minus_core_resid_tangential | edge_core | 19 | 1471 | -0.09635 | 0.05861 | -0.2008 | 0.2008 | 0.7895 | 0.07026 | 0.1305 | 0.04969 | True |

## Full Direction Null Comparison

| variable | family | n_ob | n_events | real_median_low_to_high_delta_z | real_median_high_to_low_delta_z | real_median_direction_contrast_z | real_abs_median_direction_contrast_z | direction_contrast_sign_consistency | null_abs_median_direction_contrast_z | real_minus_null_abs_direction_contrast_z | p_null_abs_direction_ge_real | direction_survives_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| resid_velocity_cov_trace | residual_intensity | 19 | 1471 | 0.2593 | -0.3315 | 0.5791 | 0.5791 | 0.8947 | 0.0702 | 0.5089 | 0.006211 | True |
| resid_speed_rms | residual_intensity | 19 | 1471 | 0.2786 | -0.3206 | 0.5522 | 0.5522 | 0.8947 | 0.07344 | 0.4788 | 0.006211 | True |
| resid_tangential_speed_mean | tangential_swirl | 19 | 1471 | 0.1792 | -0.201 | 0.4242 | 0.4242 | 0.9474 | 0.06828 | 0.356 | 0.006211 | True |
| resid_radial_abs_mean | radial | 19 | 1471 | 0.151 | -0.08377 | 0.2535 | 0.2535 | 0.7895 | 0.05272 | 0.2008 | 0.01863 | True |
| radius_resid_speed_corr | edge_core | 19 | 1471 | -0.2172 | 0.04366 | -0.2652 | 0.2652 | 0.6842 | 0.07061 | 0.1946 | 0.006211 | False |
| edge_minus_core_resid_speed | edge_core | 19 | 1471 | -0.1057 | 0.05148 | -0.2193 | 0.2193 | 0.7368 | 0.07513 | 0.1442 | 0.03727 | True |
| edge_minus_core_resid_tangential | edge_core | 19 | 1471 | -0.09635 | 0.05861 | -0.2008 | 0.2008 | 0.7895 | 0.07026 | 0.1305 | 0.04969 | True |
| resid_inward_fraction | radial | 19 | 1471 | 0.01704 | -0.08049 | 0.08897 | 0.08897 | 0.5789 | 0.05632 | 0.03265 | 0.3106 | False |
| resid_radial_velocity_mean | radial | 19 | 1471 | 0.1481 | -0.04669 | 0.08465 | 0.08465 | 0.6316 | 0.06402 | 0.02063 | 0.3602 | False |
| radius_resid_tangential_corr | edge_core | 19 | 1471 | 0.03211 | 0.02067 | -0.07726 | 0.07726 | 0.6316 | 0.06691 | 0.01035 | 0.441 | False |
| resid_tangential_fraction | tangential_swirl | 19 | 1471 | -0.08323 | -0.05872 | 0.0405 | 0.0405 | 0.5263 | 0.06239 | -0.02189 | 0.6646 | False |
| resid_polarization | residual_order | 19 | 1471 | 0.0007401 | 0.001783 | -0.01086 | 0.01086 | 0.5789 | 0.06885 | -0.05799 | 0.913 | False |

## Interpretation

4002A is a route-selection node. It should not be treated as a final mechanism
claim. A surviving family means that the 4xxx route can now ask a narrower
question about that residual structure.

## Outputs

- `Output/4002A/4002A_egrt_node.json`
- `Output/4002A/tables/residual_structure_direction_null_comparison.csv`
- `Output/4002A/tables/egrt_decision_summary.csv`
- `Output/4002A/figures/residual_structure_direction_screen.png`
- `Output/4002A/figures/residual_structure_aligned_profiles.png`
