# 4002B Edge/Core Residual Timing Audit

## Scope

4002A found edge/core residual redistribution after subtracting affine geometry.
4002B asks whether that redistribution is early enough to be a trigger
candidate or mainly event/post coupled.

## EGRT Node

| field | value |
| --- | --- |
| node_id | 4002b_edge_core_timing_audit |
| parent | 4002a_residual_spatial_structure_audit |
| node_type | timing robustness |
| decision | weak_edge_core_residual_timing_signal |
| recommended next node | pause edge/core timing route |
| boundary reading | 4002A edge/core signal does not survive timing-window shifted null gates. |

## Selected Variables

| variable | family | real_median_direction_contrast_z | orientation |
| --- | --- | --- | --- |
| edge_minus_core_resid_speed | edge_core | -0.2193 | -1 |
| edge_minus_core_resid_tangential | edge_core | -0.2008 | -1 |

## Methods

- Input frame metrics: `Output/4002A/processed/frame_residual_spatial_metrics.csv`.
- Selected 4002A edge/core survivors and oriented them so positive means the
  event-direction-consistent edge/core change.
- Timing windows:
  - baseline: `(-0.7, -0.45)` seconds
  - pre: `(-0.3, -0.05)` seconds
  - event: `(-0.05, 0.05)` seconds
  - post: `(0.05, 0.3)` seconds
  - follow: `(0.35, 0.6)` seconds
- Null replicates: `160` shifted-event replicates.

## Decision Metrics

| node_id | node_type | n_pretrigger_variables | n_event_or_post_variables | n_follow_variables | pretrigger_variables | event_or_post_variables | follow_variables | eg_rt_decision | recommended_next_node | boundary_reading |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4002b_edge_core_timing_audit | timing robustness | 0 | 0 | 0 |  |  |  | weak_edge_core_residual_timing_signal | pause edge/core timing route | 4002A edge/core signal does not survive timing-window shifted null gates. |

## Timing Null Comparison

| variable | n_ob | n_events | real_pre_to_post_abs_ratio | real_pre_minus_baseline_z | null_median_pre_minus_baseline_z | real_minus_null_pre_minus_baseline_z | p_null_ge_real_pre_minus_baseline_z | sign_consistency_pre_minus_baseline_z | gate_pre_minus_baseline_z | real_event_minus_baseline_z | null_median_event_minus_baseline_z | real_minus_null_event_minus_baseline_z | p_null_ge_real_event_minus_baseline_z | sign_consistency_event_minus_baseline_z | gate_event_minus_baseline_z | real_post_minus_baseline_z | null_median_post_minus_baseline_z | real_minus_null_post_minus_baseline_z | p_null_ge_real_post_minus_baseline_z | sign_consistency_post_minus_baseline_z | gate_post_minus_baseline_z | real_follow_minus_baseline_z | null_median_follow_minus_baseline_z | real_minus_null_follow_minus_baseline_z | p_null_ge_real_follow_minus_baseline_z | sign_consistency_follow_minus_baseline_z | gate_follow_minus_baseline_z | real_post_minus_pre_z | null_median_post_minus_pre_z | real_minus_null_post_minus_pre_z | p_null_ge_real_post_minus_pre_z | sign_consistency_post_minus_pre_z | gate_post_minus_pre_z | pretrigger_gate | event_or_post_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| edge_minus_core_resid_speed | 19 | 1469 | 5.796 | -0.05611 | -0.002587 | -0.05352 | 0.8075 | 0.5789 | False | 0.01708 | 0.005894 | 0.01119 | 0.4161 | 0.5263 | False | 0.00968 | 0.0001459 | 0.009534 | 0.3913 | 0.6316 | False | -0.02694 | 0.005253 | -0.03219 | 0.7578 | 0.5263 | False | 0.1172 | 0.0006505 | 0.1165 | 0.01863 | 0.6316 | False | False | False |
| edge_minus_core_resid_tangential | 19 | 1469 | 1.383 | -0.06413 | 0.002625 | -0.06675 | 0.882 | 0.5789 | False | -0.01421 | -0.005042 | -0.009172 | 0.559 | 0.5789 | False | 0.04636 | -0.007581 | 0.05394 | 0.1056 | 0.7895 | False | 0.009178 | -0.003897 | 0.01308 | 0.4037 | 0.5263 | False | 0.1442 | -0.002388 | 0.1466 | 0.006211 | 0.7368 | True | False | False |

## Interpretation

If pre windows fail but event/post windows pass, edge/core residual
redistribution should be treated as transition-coupled, not as a validated
pre-transition trigger.

## Outputs

- `Output/4002B/4002B_egrt_node.json`
- `Output/4002B/tables/edge_core_timing_null_comparison.csv`
- `Output/4002B/tables/egrt_decision_summary.csv`
- `Output/4002B/figures/edge_core_timing_window_changes.png`
- `Output/4002B/figures/edge_core_aligned_timing_profiles.png`
