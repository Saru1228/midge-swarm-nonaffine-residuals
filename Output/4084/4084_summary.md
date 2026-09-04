# Node 4084 Summary

## Question

Where in the swarm does the robust T1 local non-affine event signal live:
core, edge, radial shell gradient, local-density condition, or diffuse field?

## Inputs

- `Output/4082b/decision.json`
- transition events from `Output/3045/tables/transition_events.csv`
- raw trajectories through the configured data directory

## Method

For each observation, 4084 keeps the 4081/4082 local-affine setup:

```text
k = 8
lag = 0.1 sec
frame_stride = 2
max_focals_per_frame = 24
matched non-event replicates = 40
```

It then decomposes the focal-neighborhood tangential residual by:

- radial shell: core / middle / edge;
- local density proxy: low / middle / high kNN distance;
- direct contrasts or gradients: edge-minus-core, sparse-minus-dense,
  radius correlation, and kNN-distance correlation.

## Decision

`support_replicated_edge_core_spatial_contrast_with_boundaries`

## Main Reading

`shell_edge_minus_core` provides a majority-replicated direct spatial contrast/gradient. This supports an edge/core spatial contrast with boundaries, not a full universal spatial taxonomy. Continue by asking when this spatially structured signal appears around the transition.

```text
observations tested = 14
majority gate count = 8
diffuse baseline gate count = 13
localized observation count = 12
```

## Variable-Level Summary

| variable | family | gate_count | gate_fraction | median_event_minus_non_event_abs_direction_z | signed_direction_sign_consistency | majority_gate | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| density_dense_tangential | density_level | 14 | 1 | 0.3375 | 0.9286 | True | majority event-conditioned level/diffuse signal |
| all_tangential | diffuse_baseline | 13 | 0.9286 | 0.4711 | 1 | True | majority event-conditioned level/diffuse signal |
| density_middle_tangential | density_level | 13 | 0.9286 | 0.3274 | 1 | True | majority event-conditioned level/diffuse signal |
| shell_core_tangential | radial_level | 12 | 0.8571 | 0.4089 | 1 | True | majority event-conditioned level/diffuse signal |
| shell_middle_tangential | radial_level | 11 | 0.7857 | 0.3604 | 1 | True | majority event-conditioned level/diffuse signal |
| shell_radius_corr_tangential | radial_gradient | 11 | 0.7857 | 0.2245 | 0.6364 | True | majority count but signed spatial direction is inconsistent |
| density_sparse_tangential | density_level | 11 | 0.7857 | 0.1559 | 1 | True | majority event-conditioned level/diffuse signal |
| shell_edge_tangential | radial_level | 10 | 0.7143 | 0.2785 | 1 | True | majority event-conditioned level/diffuse signal |
| shell_edge_minus_core | radial_contrast | 9 | 0.6429 | 0.105 | 0.7778 | True | majority spatial contrast/gradient candidate |
| density_knn_distance_corr_tangential | density_gradient | 7 | 0.5 | 0.07399 | 0.5714 | False | minority or observation-specific signal |
| density_sparse_minus_dense | density_contrast | 6 | 0.4286 | 0.05896 | 0.6667 | False | minority or observation-specific signal |
| shell_middle_minus_core | radial_contrast | 5 | 0.3571 | 0.02797 | 0.8 | False | minority or observation-specific signal |

## Observation-Level Summary

| ob | n_events | diffuse_baseline_gate | n_spatial_contrast_gates | best_spatial_variable | best_spatial_gap_z | best_level_variable | best_level_gap_z | ob_spatial_class |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 43 | True | 3 | shell_edge_minus_core | 0.2816 | density_middle_tangential | 0.3643 | localized_or_gradient_signal_candidate |
| 5 | 93 | True | 5 | shell_radius_corr_tangential | 0.4046 | shell_core_tangential | 0.4096 | localized_or_gradient_signal_candidate |
| 7 | 33 | False | 3 | shell_edge_minus_core | 0.4216 | density_sparse_tangential | 0.7294 | no_clear_t1_spatial_signal_in_this_node |
| 9 | 36 | True | 4 | shell_radius_corr_tangential | 0.6203 | density_dense_tangential | 0.7754 | localized_or_gradient_signal_candidate |
| 10 | 36 | True | 4 | shell_radius_corr_tangential | 0.5863 | shell_core_tangential | 0.4566 | localized_or_gradient_signal_candidate |
| 11 | 119 | True | 3 | shell_middle_minus_core | 0.2626 | shell_core_tangential | 0.8369 | localized_or_gradient_signal_candidate |
| 12 | 91 | True | 1 | density_sparse_minus_dense | 0.2081 | shell_middle_tangential | 0.3463 | localized_or_gradient_signal_candidate |
| 13 | 102 | True | 2 | shell_radius_corr_tangential | 0.3758 | shell_middle_tangential | 0.4412 | localized_or_gradient_signal_candidate |
| 14 | 47 | True | 2 | density_sparse_minus_dense | 0.3752 | shell_core_tangential | 0.8687 | localized_or_gradient_signal_candidate |
| 15 | 96 | True | 4 | shell_edge_minus_core | 0.5318 | shell_core_tangential | 0.9305 | localized_or_gradient_signal_candidate |
| 16 | 84 | True | 0 | shell_middle_minus_core | -0.1127 | shell_edge_tangential | 0.8115 | level_specific_but_no_direct_contrast |
| 17 | 122 | True | 2 | density_knn_distance_corr_tangential | 0.1314 | shell_core_tangential | 0.4315 | localized_or_gradient_signal_candidate |
| 18 | 103 | True | 2 | density_knn_distance_corr_tangential | 0.1079 | shell_core_tangential | 0.258 | localized_or_gradient_signal_candidate |
| 19 | 143 | True | 3 | shell_radius_corr_tangential | 0.3164 | shell_core_tangential | 0.6096 | localized_or_gradient_signal_candidate |

## Boundary

A direct spatial taxonomy is supported only by contrast/gradient
variables, not by a shell-level variable alone. If only shell or density
levels pass, the safer reading is that the signal is present in those
regions but not yet localized by a clean spatial contrast.

## Next

`4085_event_phase_profile_of_t1_signal`

## Artifacts

- `Output/4084/spatial_taxonomy_condition_rows.csv`
- `Output/4084/ob_spatial_taxonomy.csv`
- `Output/4084/variable_spatial_taxonomy.csv`
- `Output/4084/figures/4084_spatial_gap_heatmap.png`
- `Output/4084/figures/4084_variable_gate_counts.png`
- `Output/4084/figures/4084_ob_spatial_classes.png`
