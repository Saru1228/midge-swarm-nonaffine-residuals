# Node 4085b Summary

## Question

What does the 4085/4086 signal look like as a low-dimensional diagnostic
phase-space projection?

## Important Scope Limit

This is not an attractor test. It does not estimate dimension,
recurrence, Lyapunov exponents, or invariant sets. It is only a
projection of event-aligned trajectories into a small interpretable
coordinate system.

## Coordinates

```text
x = compact_density_resid_z from Output/3045
y = all_tangential local non-affinity from Output/4085
z = shell_edge_minus_core from Output/4085
color = relative time around transition
line groups = low_to_high and high_to_low
```

## Decision

`diagnostic_phase_space_supports_signed_diffuse_near_pre_separation`

## Main Reading

The phase-space projection visually supports 4086's signed diffuse near-pre separation, but it remains a diagnostic projection rather than attractor evidence.

## Metrics

| metric | value | interpretation |
| --- | --- | --- |
| near_pre_all_tangential_low_to_high | -0.1567 | ob-balanced median low-to-high all_tangential in near-pre phase |
| near_pre_all_tangential_high_to_low | 0.1318 | ob-balanced median high-to-low all_tangential in near-pre phase |
| near_pre_all_tangential_signed_separation | -0.2885 | low-to-high minus high-to-low separation in the diffuse timing coordinate |
| near_pre_edge_core_low_to_high | 0.04554 | ob-balanced median low-to-high edge/core contrast in near-pre phase |
| near_pre_edge_core_high_to_low | -0.05553 | ob-balanced median high-to-low edge/core contrast in near-pre phase |
| phase_space_loop_area_all_vs_edge_low_to_high | 0.004061 | diagnostic 2D loop area, not an attractor metric |
| phase_space_loop_area_all_vs_edge_high_to_low | 0.005255 | diagnostic 2D loop area, not an attractor metric |

## Next

`4087_failure_boundary_sensitivity_or_4088_bounded_synthesis`

## Artifacts

- `Output/4085b/phase_space_event_samples.csv`
- `Output/4085b/phase_space_trajectory_by_event_type.csv`
- `Output/4085b/phase_space_metrics.csv`
- `Output/4085b/figures/4085b_all_tangential_vs_edge_core_phase_space.png`
- `Output/4085b/figures/4085b_compactness_vs_all_tangential.png`
- `Output/4085b/figures/4085b_3d_phase_space_projection.png`
