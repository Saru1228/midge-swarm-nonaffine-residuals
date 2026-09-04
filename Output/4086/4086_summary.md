# Node 4086 Summary

## Question

Is the 4085 near-pre diffuse T1 timing profile mirrored between
low-to-high and high-to-low transitions, or is it dominated by one
transition direction?

## Inputs

- `Output/4084/per_ob/Ob*/local_spatial_metric_frame.csv`
- `Output/4085/decision.json`
- `Output/3045/tables/transition_events.csv`

## Method

For each observation, variable, phase, and transition type, 4086 compares
real phase medians against matched non-event windows with the same event
type labels.

```text
target variable = all_tangential
target phase = near_pre
non-event replicates = 40
event-type gate = abs(real-null) >= 0.12, p <= 0.25
```

Signed classes:

- `mirror_symmetric_opposite_sign`: both event types pass with balanced
  opposite signs;
- `low_to_high_dominant`;
- `high_to_low_dominant`;
- `same_direction_both_event_types`;
- `no_signed_gate`.

## Decision

`boundary_signed_direction_heterogeneous_across_observations`

## Main Reading

The near-pre diffuse T1 timing profile has signed event-type heterogeneity rather than a stable mirror or one-direction rule.

```text
observations tested = 14
majority gate count = 8
target class counts = {"mirror_symmetric_opposite_sign": 6, "no_signed_gate": 4, "low_to_high_dominant": 3, "opposite_sign_but_imbalanced": 1}
```

## Target Observation Classification

| ob | low_to_high_excess_z | high_to_low_excess_z | signed_separation_z | mirror_balance | low_to_high_gate | high_to_low_gate | signed_class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | -0.2933 | 0.3261 | -0.6194 | 0.8992 | True | True | mirror_symmetric_opposite_sign |
| 5 | -0.2486 | 0.1764 | -0.425 | 0.7097 | True | True | mirror_symmetric_opposite_sign |
| 7 | 0.08218 | 0.05446 | 0.02773 | 0.6626 | False | False | no_signed_gate |
| 9 | -0.3775 | 0.3491 | -0.7266 | 0.9249 | True | True | mirror_symmetric_opposite_sign |
| 10 | -0.1948 | 0.115 | -0.3098 | 0.5902 | False | False | no_signed_gate |
| 11 | -0.3812 | 0.2838 | -0.665 | 0.7446 | True | True | mirror_symmetric_opposite_sign |
| 12 | -0.5274 | 0.03009 | -0.5575 | 0.05705 | True | False | low_to_high_dominant |
| 13 | -0.2648 | -0.0128 | -0.252 | 0.04832 | True | False | low_to_high_dominant |
| 14 | -0.2749 | 0.3336 | -0.6086 | 0.824 | True | True | mirror_symmetric_opposite_sign |
| 15 | -0.4478 | 0.257 | -0.7048 | 0.574 | True | True | mirror_symmetric_opposite_sign |
| 16 | -0.221 | 0.1596 | -0.3806 | 0.722 | True | False | low_to_high_dominant |
| 17 | -0.07562 | 0.1429 | -0.2186 | 0.5291 | False | False | no_signed_gate |
| 18 | -0.1077 | 0.1142 | -0.2219 | 0.9426 | False | False | no_signed_gate |
| 19 | -0.3664 | 0.1365 | -0.5029 | 0.3725 | True | True | opposite_sign_but_imbalanced |

## Variable/Phase Signed Summary

| variable | phase | mirror_symmetric_count | low_to_high_dominant_count | high_to_low_dominant_count | opposite_sign_imbalanced_count | same_direction_count | no_signed_gate_count | median_low_to_high_excess_z | median_high_to_low_excess_z | majority_signed_class |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_tangential | near_pre | 6 | 3 | 0 | 1 | 0 | 4 | -0.2699 | 0.1513 | no_majority_signed_class |
| all_tangential | near_post | 3 | 4 | 4 | 0 | 0 | 3 | 0.1828 | -0.1271 | no_majority_signed_class |
| shell_edge_minus_core | near_pre | 0 | 3 | 2 | 0 | 1 | 8 | -0.01346 | -0.04715 | no_signed_gate |
| shell_edge_minus_core | near_post | 0 | 8 | 2 | 0 | 0 | 4 | -0.07323 | 0.02484 | low_to_high_dominant |

## Boundary

This node does not claim a deterministic trigger. It only asks whether
the 4085 near-pre timing profile has a stable signed decomposition.

## Next

`4085b_phase_space_projection_as_diagnostic_then_4087_failure_boundary_sensitivity`

## Artifacts

- `Output/4086/signed_event_type_phase_rows.csv`
- `Output/4086/signed_decomposition_rows.csv`
- `Output/4086/ob_signed_classification.csv`
- `Output/4086/variable_phase_signed_summary.csv`
- `Output/4086/figures/4086_target_signed_excess.png`
- `Output/4086/figures/4086_signed_class_counts.png`
