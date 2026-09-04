# Node 4121 Summary

## Question

Do frames with the same instantaneous `C,dCdt,R` state but different recent C-R path direction show different T1 activity?

## Why This Node Exists After 4120

4120 showed that recent path features are measurable, but also showed history-current leakage. Therefore 4121 uses same-observation current-state matching before interpreting any history effect.

## Frozen Definitions

```text
target = A_swarm_tangential_z
current_state = C,dCdt,R
history = h500_theta_h
axis_angle_h500_rad = -0.809307
state_distance <= 0.50
history_angle_difference >= 90 deg
temporal_separation >= 1.0 sec
null = within-observation theta_h shuffle with pair recomputation
```

## Primary Metrics

| n_obs_sufficient | median_pairs | median_state_dist | median_abs_signed_effect | direction_consistency | real_beats_null_fraction | median_real_minus_null |
| --- | --- | --- | --- | --- | --- | --- |
| 19 | 4723 | 0.2973 | 0.07629 | 0.5263 | 0.7368 | 0.03414 |

## Observation-level Effects

| ob | dataset | n_frames_total | n_frames_valid | usable_frame_fraction | n_state_pairs | n_contrasting_pairs | n_selected_pairs | sufficient_pairs | n_unique_frames_in_pairs | paired_frame_fraction | median_state_distance | q95_state_distance | median_theta_diff_deg | median_temporal_sep_sec | median_abs_delta_A_z | median_signed_axis_delta_A_z | mean_signed_axis_delta_A_z | fraction_signed_positive | null_median_abs_signed_axis_delta_A_z | null_q95_abs_signed_axis_delta_A_z | real_minus_null_median_abs_effect | real_beats_null_median_abs | real_beats_null_q95_abs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ob1.txt | 1098 | 1081 | 0.9845 | 11240 | 3455 | 2040 | True | 773 | 0.7151 | 0.3375 | 0.4805 | 145.1 | 29.7 | 0.9204 | -0.06569 | -0.101 | 0.4794 | 0.0506 | 0.123 | 0.01509 | True | False |
| 2 | Ob2.txt | 1485 | 1457 | 0.9811 | 20631 | 7647 | 3392 | True | 1120 | 0.7687 | 0.3225 | 0.4821 | 150.9 | 36.15 | 0.925 | -0.1001 | -0.08372 | 0.4714 | 0.0365 | 0.1033 | 0.06358 | True | False |
| 3 | Ob3.txt | 1498 | 1476 | 0.9853 | 32220 | 10548 | 4064 | True | 1178 | 0.7981 | 0.2973 | 0.4703 | 160.5 | 32.6 | 0.9855 | 0.08514 | 0.08206 | 0.5236 | 0.04396 | 0.1254 | 0.04117 | True | False |
| 4 | Ob4.txt | 1494 | 1448 | 0.9692 | 31267 | 11192 | 3831 | True | 1165 | 0.8046 | 0.2878 | 0.4743 | 165.9 | 31.4 | 0.8902 | -0.01861 | 0.000934 | 0.4941 | 0.04148 | 0.119 | -0.02288 | False | False |
| 5 | Ob5.txt | 1494 | 1430 | 0.9572 | 37593 | 13503 | 4269 | True | 1200 | 0.8392 | 0.2644 | 0.4637 | 166.3 | 29.6 | 0.981 | -0.1738 | -0.1479 | 0.4587 | 0.04968 | 0.1247 | 0.1241 | True | True |
| 6 | Ob6.txt | 1998 | 1935 | 0.9685 | 64420 | 21915 | 5998 | True | 1650 | 0.8527 | 0.26 | 0.4638 | 159.6 | 42.8 | 0.9079 | 0.004854 | 0.002492 | 0.5012 | 0.02768 | 0.0949 | -0.02282 | False | False |
| 7 | Ob7.txt | 998 | 984 | 0.986 | 12042 | 3904 | 1964 | True | 698 | 0.7093 | 0.333 | 0.4834 | 151.7 | 23.7 | 0.957 | -0.1025 | -0.04834 | 0.4725 | 0.05635 | 0.1484 | 0.04614 | True | False |
| 8 | Ob8.txt | 1898 | 1846 | 0.9726 | 51583 | 18634 | 5634 | True | 1519 | 0.8229 | 0.2831 | 0.4711 | 159.3 | 37.5 | 0.9502 | -0.2214 | -0.1732 | 0.4409 | 0.0359 | 0.09601 | 0.1855 | True | True |
| 9 | Ob9.txt | 990 | 968 | 0.9778 | 7888 | 2874 | 1804 | True | 721 | 0.7448 | 0.3534 | 0.4851 | 146.2 | 26.9 | 0.9629 | -0.2191 | -0.2742 | 0.4307 | 0.04911 | 0.1276 | 0.17 | True | True |
| 10 | Ob10.txt | 1498 | 1474 | 0.984 | 26048 | 8650 | 3655 | True | 1138 | 0.772 | 0.3146 | 0.4776 | 151.1 | 34.7 | 0.9045 | -0.06652 | -0.03 | 0.4804 | 0.03623 | 0.1038 | 0.03029 | True | False |
| 11 | Ob11.txt | 1997 | 1922 | 0.9624 | 56899 | 19073 | 5238 | True | 1449 | 0.7539 | 0.2754 | 0.4677 | 167.7 | 33.9 | 0.926 | 0.04427 | 0.0473 | 0.5132 | 0.03803 | 0.1065 | 0.006242 | True | False |
| 12 | Ob12.txt | 1997 | 1965 | 0.984 | 32531 | 11808 | 4723 | True | 1463 | 0.7445 | 0.3158 | 0.4783 | 149 | 30 | 0.9162 | 0.1407 | 0.1592 | 0.5384 | 0.03248 | 0.09771 | 0.1082 | True | True |
| 13 | Ob13.txt | 1998 | 1960 | 0.981 | 40090 | 13656 | 5077 | True | 1444 | 0.7367 | 0.2998 | 0.4751 | 149.1 | 40.8 | 1.01 | -0.01104 | -0.02793 | 0.4962 | 0.04084 | 0.1266 | -0.0298 | False | False |
| 14 | Ob14.txt | 1998 | 1968 | 0.985 | 39958 | 14400 | 5250 | True | 1580 | 0.8028 | 0.3054 | 0.4741 | 149.4 | 40.05 | 0.9696 | -0.07629 | -0.05272 | 0.481 | 0.04215 | 0.1333 | 0.03414 | True | False |
| 15 | Ob15.txt | 1997 | 1940 | 0.9715 | 44001 | 16071 | 5050 | True | 1485 | 0.7655 | 0.2871 | 0.4697 | 158.1 | 45.6 | 0.8935 | 0.139 | 0.1308 | 0.5414 | 0.03522 | 0.102 | 0.1038 | True | True |
| 16 | Ob16.txt | 1997 | 1938 | 0.9705 | 52315 | 18380 | 5800 | True | 1618 | 0.8349 | 0.2802 | 0.4683 | 168.1 | 30.3 | 0.956 | 0.03518 | 0.02199 | 0.511 | 0.03481 | 0.1174 | 0.0003614 | True | False |
| 17 | Ob17.txt | 1998 | 1922 | 0.962 | 60061 | 19944 | 5575 | True | 1550 | 0.8065 | 0.2683 | 0.4671 | 165.3 | 39.8 | 0.982 | 0.1417 | 0.1381 | 0.5361 | 0.04104 | 0.09001 | 0.1006 | True | True |
| 18 | Ob18.txt | 1998 | 1949 | 0.9755 | 33639 | 11682 | 4667 | True | 1411 | 0.724 | 0.3158 | 0.4783 | 163 | 27.7 | 0.9498 | 0.002144 | 0.03031 | 0.5012 | 0.0364 | 0.09949 | -0.03426 | False | False |
| 19 | Ob19.txt | 2998 | 2937 | 0.9797 | 109916 | 35593 | 8516 | True | 2353 | 0.8012 | 0.2745 | 0.4699 | 164.9 | 50.2 | 0.9324 | 0.007941 | 0.03359 | 0.5032 | 0.02991 | 0.08716 | -0.02197 | False | False |

## Largest Absolute Observation Effects

| ob | dataset | n_selected_pairs | median_signed_axis_delta_A_z | null_median_abs_signed_axis_delta_A_z | real_minus_null_median_abs_effect |
| --- | --- | --- | --- | --- | --- |
| 8 | Ob8.txt | 5634 | -0.2214 | 0.0359 | 0.1855 |
| 9 | Ob9.txt | 1804 | -0.2191 | 0.04911 | 0.17 |
| 5 | Ob5.txt | 4269 | -0.1738 | 0.04968 | 0.1241 |
| 17 | Ob17.txt | 5575 | 0.1417 | 0.04104 | 0.1006 |
| 12 | Ob12.txt | 4723 | 0.1407 | 0.03248 | 0.1082 |
| 15 | Ob15.txt | 5050 | 0.139 | 0.03522 | 0.1038 |
| 7 | Ob7.txt | 1964 | -0.1025 | 0.05635 | 0.04614 |
| 2 | Ob2.txt | 3392 | -0.1001 | 0.0365 | 0.06358 |

## Matching Quality

| ob | dataset | n_frames_valid | n_state_pairs_within_primary_radius | n_contrasting_pairs_before_anchor_cap | n_selected_pairs | anchor_count_with_pair | anchor_fraction_with_pair | median_state_distance | q95_state_distance | median_theta_diff_deg | min_temporal_sep_sec |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ob1.txt | 1081 | 11240 | 3455 | 2040 | 629 | 0.5819 | 0.3375 | 0.4805 | 145.1 | 1 |
| 2 | Ob2.txt | 1457 | 20631 | 7647 | 3392 | 936 | 0.6424 | 0.3225 | 0.4821 | 150.9 | 1 |
| 3 | Ob3.txt | 1476 | 32220 | 10548 | 4064 | 1042 | 0.706 | 0.2973 | 0.4703 | 160.5 | 1 |
| 4 | Ob4.txt | 1448 | 31267 | 11192 | 3831 | 1027 | 0.7093 | 0.2878 | 0.4743 | 165.9 | 1 |
| 5 | Ob5.txt | 1430 | 37593 | 13503 | 4269 | 1066 | 0.7455 | 0.2644 | 0.4637 | 166.3 | 1 |
| 6 | Ob6.txt | 1935 | 64420 | 21915 | 5998 | 1498 | 0.7742 | 0.26 | 0.4638 | 159.6 | 1 |
| 7 | Ob7.txt | 984 | 12042 | 3904 | 1964 | 600 | 0.6098 | 0.333 | 0.4834 | 151.7 | 1 |
| 8 | Ob8.txt | 1846 | 51583 | 18634 | 5634 | 1383 | 0.7492 | 0.2831 | 0.4711 | 159.3 | 1 |
| 9 | Ob9.txt | 968 | 7888 | 2874 | 1804 | 545 | 0.563 | 0.3534 | 0.4851 | 146.2 | 1 |
| 10 | Ob10.txt | 1474 | 26048 | 8650 | 3655 | 971 | 0.6588 | 0.3146 | 0.4776 | 151.1 | 1 |
| 11 | Ob11.txt | 1922 | 56899 | 19073 | 5238 | 1331 | 0.6925 | 0.2754 | 0.4677 | 167.7 | 1 |
| 12 | Ob12.txt | 1965 | 32531 | 11808 | 4723 | 1256 | 0.6392 | 0.3158 | 0.4783 | 149 | 1 |
| 13 | Ob13.txt | 1960 | 40090 | 13656 | 5077 | 1258 | 0.6418 | 0.2998 | 0.4751 | 149.1 | 1 |
| 14 | Ob14.txt | 1968 | 39958 | 14400 | 5250 | 1380 | 0.7012 | 0.3054 | 0.4741 | 149.4 | 1 |
| 15 | Ob15.txt | 1940 | 44001 | 16071 | 5050 | 1339 | 0.6902 | 0.2871 | 0.4697 | 158.1 | 1 |
| 16 | Ob16.txt | 1938 | 52315 | 18380 | 5800 | 1471 | 0.759 | 0.2802 | 0.4683 | 168.1 | 1 |
| 17 | Ob17.txt | 1922 | 60061 | 19944 | 5575 | 1371 | 0.7133 | 0.2683 | 0.4671 | 165.3 | 1 |
| 18 | Ob18.txt | 1949 | 33639 | 11682 | 4667 | 1246 | 0.6393 | 0.3158 | 0.4783 | 163 | 1 |
| 19 | Ob19.txt | 2937 | 109916 | 35593 | 8516 | 2157 | 0.7344 | 0.2745 | 0.4699 | 164.9 | 1 |

## Primary h=0.50 Sensitivity

| history_window_sec | state_distance_threshold | history_angle_threshold_deg | axis_angle_rad | n_observations | n_observations_sufficient | total_selected_pairs | median_selected_pairs_per_ob | median_state_distance | median_theta_diff_deg | median_abs_ob_signed_effect | median_ob_signed_effect | direction_consistency_fraction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.5 | 0.35 | 60 | -0.8093 | 19 | 19 | 61366 | 3253 | 0.2398 | 157.1 | 0.08024 | 0.001238 | 0.5263 |
| 0.5 | 0.35 | 90 | -0.8093 | 19 | 19 | 57628 | 3172 | 0.2436 | 159.6 | 0.102 | 0.0007175 | 0.5263 |
| 0.5 | 0.35 | 120 | -0.8093 | 19 | 19 | 53200 | 2836 | 0.2468 | 161.4 | 0.1143 | 0.00909 | 0.5263 |
| 0.5 | 0.5 | 60 | -0.8093 | 19 | 19 | 90283 | 5129 | 0.2905 | 157.2 | 0.06001 | -0.01836 | 0.5263 |
| 0.5 | 0.5 | 90 | -0.8093 | 19 | 19 | 86547 | 4723 | 0.2973 | 159.3 | 0.07629 | -0.01104 | 0.5263 |
| 0.5 | 0.5 | 120 | -0.8093 | 19 | 19 | 81587 | 4472 | 0.3046 | 161.3 | 0.08418 | -0.01087 | 0.5263 |
| 0.5 | 0.75 | 60 | -0.8093 | 19 | 19 | 116676 | 6780 | 0.3382 | 157.4 | 0.05749 | -0.01121 | 0.5263 |
| 0.5 | 0.75 | 90 | -0.8093 | 19 | 19 | 114018 | 6583 | 0.3483 | 159.3 | 0.06678 | -0.02754 | 0.6842 |
| 0.5 | 0.75 | 120 | -0.8093 | 19 | 19 | 110158 | 6272 | 0.3615 | 161.4 | 0.06492 | -0.01544 | 0.6842 |

## Gate Evaluation

```text
gate_result = boundary_observation_specific_history_dependence
```

Some history-conditioned separation is visible, but the effect is not strong enough across all gate criteria to claim robust same-state history dependence.

## What This Supports

- It directly tests recent path direction after matching current state.
- It separates technical identifiability from a history-dependence claim.
- It provides the required gate for deciding whether 4122 is allowed.

## What This Does Not Prove

| does_not_prove |
| --- |
| causal memory mechanism |
| thermodynamic hysteresis |
| transition trigger |
| out-of-sample history gain |
| network propagation |

## Decision

`boundary_observation_specific_history_dependence`

## Next Node

| next |
| --- |
| 4125_observation_specific_history_synthesis |

## Artifacts

- `Output/4121/state_matched_history_pairs.csv`
- `Output/4121/matching_quality.csv`
- `Output/4121/observation_level_effects.csv`
- `Output/4121/history_shuffle_null.csv`
- `Output/4121/sensitivity.csv`
- `Output/4121/figures/4121_primary_matching_and_effects.png`
- `Output/4121/figures/4121_real_vs_shuffle_null.png`
- `Output/4121/figures/4121_sensitivity_heatmap_h500.png`
- `Output/4121/figures/4121_match_coverage_scatter.png`
- `Output/4121/decision.json`
