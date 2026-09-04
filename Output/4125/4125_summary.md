# Node 4125 State-path / History Synthesis

## Classification

`P1_observation_specific_history_dependence_boundary`

## Plain-language Result

The recent path of the swarm through the compact-density state plane is measurable, and it sometimes separates T1 after matching the current state. However, the direction of that separation changes across observations. This makes the result useful as an observation-specific boundary, not as a stable mechanism.

## Evidence Chain

| node | question | result | meaning |
| --- | --- | --- | --- |
| 4120 | Can recent state-path features be measured? | pass_state_path_features_feasible_with_leakage_audit | technical pass; leakage requires state matching |
| 4121 | Same current state, different path direction? | boundary_observation_specific_history_dependence | visible but direction-inconsistent history separation |

## Primary 4121 Metrics

| n_obs_sufficient | median_abs_effect | direction_consistency | real_beats_null_fraction | pos_obs | neg_obs |
| --- | --- | --- | --- | --- | --- |
| 19 | 0.07629 | 0.5263 | 0.7368 | 9 | 10 |

## Strongest Observation-specific Effects

| ob | dataset | n_selected_pairs | median_signed_axis_delta_A_z | null_median_abs_signed_axis_delta_A_z | real_minus_null_median_abs_effect | effect_direction |
| --- | --- | --- | --- | --- | --- | --- |
| 8 | Ob8.txt | 5634 | -0.2214 | 0.0359 | 0.1855 | axis_negative_higher |
| 9 | Ob9.txt | 1804 | -0.2191 | 0.04911 | 0.17 | axis_negative_higher |
| 5 | Ob5.txt | 4269 | -0.1738 | 0.04968 | 0.1241 | axis_negative_higher |
| 17 | Ob17.txt | 5575 | 0.1417 | 0.04104 | 0.1006 | axis_positive_higher |
| 12 | Ob12.txt | 4723 | 0.1407 | 0.03248 | 0.1082 | axis_positive_higher |
| 15 | Ob15.txt | 5050 | 0.139 | 0.03522 | 0.1038 | axis_positive_higher |
| 7 | Ob7.txt | 1964 | -0.1025 | 0.05635 | 0.04614 | axis_negative_higher |
| 2 | Ob2.txt | 3392 | -0.1001 | 0.0365 | 0.06358 | axis_negative_higher |

## Route Decision

Do not continue to 4122/4123 as confirmatory primary nodes under the current gate. A later descriptive node may inspect why Ob5/8/9 and Ob12/15/17 have opposite signs, but that would be a heterogeneity analysis rather than a robust history-mechanism claim.

## Bounded Claim

Recent C-R path direction can be measured and produces observation-specific T1 separations after same-current-state matching, but the sign/order is not stable enough to claim a universal history dependence mechanism.

## What This Does Not Support

| does_not_support |
| --- |
| robust same-state history dependence |
| approach/departure hysteresis route as primary confirmatory analysis |
| grouped OOS history-gain modeling |
| network propagation mechanism |
| causal memory mechanism |

## Artifacts

- `Output/4120/4120_summary.md`
- `Output/4121/4121_summary.md`
- `Output/4125/decision.json`
- `Output/4125/tables/strongest_observation_effects.csv`
- `Output/4125/tables/4121_primary_sensitivity_h500.csv`
