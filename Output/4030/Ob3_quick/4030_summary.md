# 4030 Coarse-Grained Stochastic State-Transition Pilot

## Scope

4030 follows the mixed `4020/4020B` result. It tests whether residual-state
metrics are more useful after coarse-graining into high/low stochastic states.

Plain-language question:

> If a residual state is high rather than low, does the compact state become
> more likely to switch within the next `0.2` seconds?

## EGRT Node

| field | value |
| --- | --- |
| node_id | 4030_coarse_grained_stochastic_state_transition_pilot |
| parent | 4020B_selective_single_observation_replication |
| node_type | single-observation stochastic coarse-graining pilot |
| pilot observation | Ob3 |
| decision | weak_coarse_state_transition_modulation_pilot |
| recommended next node | 4040 4xxx synthesis and pause |
| boundary reading | No residual coarse state modulates compact-state transitions beyond shifted-bin null gates. |

## Methods

- Load affine-residual one-fish state metrics from `Output\4020B\Ob3\processed\frame_one_fish_state_metrics.csv`.
- Merge compact high/low labels from `Output/3045/processed/frame_residual_signals.csv`.
- Bin each residual variable into high/low by within-ob median.
- Estimate compact-state transition probability after `0.2` sec.
- Compare real modulation with `24` circularly shifted residual-bin nulls.

## Decision Metrics

| node_id | node_type | pilot_ob | n_surviving_variables | surviving_variables | eg_rt_decision | recommended_next_node | boundary_reading |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 4030_coarse_grained_stochastic_state_transition_pilot | single-observation stochastic coarse-graining pilot | 3 | 0 |  | weak_coarse_state_transition_modulation_pilot | 4040 4xxx synthesis and pause | No residual coarse state modulates compact-state transitions beyond shifted-bin null gates. |

## Pilot-Surviving Variables

_No rows._

## Top Rows

| n_low_bin_high | n_low_bin_low | n_high_bin_high | n_high_bin_low | p_up_given_resid_high | p_up_given_resid_low | p_down_given_resid_high | p_down_given_resid_low | up_gap | down_gap | dominant_transition | dominant_gap | abs_transition_modulation | min_cell_count | variable | n_frames | lag_sec | lag_steps | residual_bin_median | null_abs_transition_modulation | real_minus_null_abs_transition_modulation | p_null_abs_transition_ge_real | pilot_survives_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3846 | 3628 | 3639 | 3857 | 0.2374 | 0.2042 | 0.2135 | 0.2295 | 0.03314 | -0.01593 | low_to_high | 0.03314 | 0.03314 | 3628 | edge_minus_core_radial_abs_mean | 14970 | 0.2 | 20 | 0.0002105 | 0.01788 | 0.01527 | 0.24 | False |
| 3864 | 3610 | 3621 | 3875 | 0.2355 | 0.2061 | 0.219 | 0.2243 | 0.02941 | -0.005258 | low_to_high | 0.02941 | 0.02941 | 3610 | edge_energy_share | 14970 | 0.2 | 20 | -0.0001606 | 0.01892 | 0.01049 | 0.32 | False |
| 3717 | 3757 | 3768 | 3728 | 0.2074 | 0.235 | 0.2274 | 0.2159 | -0.0276 | 0.01151 | low_to_high | -0.0276 | 0.0276 | 3717 | edge_minus_core_tangential_mean | 14970 | 0.2 | 20 | -0.001654 | 0.02153 | 0.006077 | 0.32 | False |
| 3769 | 3705 | 3716 | 3780 | 0.2083 | 0.2345 | 0.2322 | 0.2114 | -0.02627 | 0.02086 | low_to_high | -0.02627 | 0.02627 | 3705 | resid_energy_shell_entropy | 14970 | 0.2 | 20 | 0.0003082 | 0.02321 | 0.00306 | 0.4 | False |
| 3751 | 3723 | 3734 | 3762 | 0.2079 | 0.2348 | 0.2349 | 0.2087 | -0.02681 | 0.0262 | low_to_high | -0.02681 | 0.02681 | 3723 | edge_minus_core_tangential_q75 | 14970 | 0.2 | 20 | -0.0001143 | 0.02449 | 0.00232 | 0.32 | False |
| 3772 | 3702 | 3713 | 3783 | 0.2113 | 0.2315 | 0.2268 | 0.2168 | -0.0202 | 0.01001 | low_to_high | -0.0202 | 0.0202 | 3702 | top_tangential_radius_mean_z | 14970 | 0.2 | 20 | -0.0005307 | 0.02278 | -0.002577 | 0.64 | False |
| 3689 | 3785 | 3796 | 3700 | 0.2301 | 0.2127 | 0.215 | 0.2286 | 0.01746 | -0.01369 | low_to_high | 0.01746 | 0.01746 | 3689 | core_energy_share | 14970 | 0.2 | 20 | -0.0002963 | 0.02006 | -0.002594 | 0.6 | False |
| 3869 | 3605 | 3616 | 3880 | 0.2287 | 0.2133 | 0.2146 | 0.2284 | 0.01543 | -0.01375 | low_to_high | 0.01543 | 0.01543 | 3605 | edge_minus_core_radial_abs_q75 | 14970 | 0.2 | 20 | -0.0003858 | 0.01893 | -0.003506 | 0.64 | False |

## Interpretation

This is still a pilot. A positive result means the route should replicate one
observation at a time; a weak result means the 4xxx branch should synthesize and
pause rather than keep searching for a mechanism.

## Outputs

- `Output/4030/Ob3_quick/4030_egrt_node.json`
- `Output/4030/Ob3_quick/tables/coarse_state_transition_modulation_comparison.csv`
- `Output/4030/Ob3_quick/tables/egrt_decision_summary.csv`
- `Output/4030/Ob3_quick/figures/coarse_state_transition_modulation_screen.png`
