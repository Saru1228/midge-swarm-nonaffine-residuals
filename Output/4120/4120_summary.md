# Node 4120 Summary

## Question

Can the project compute a stable recent C-R state-path representation before testing whether T1 contains history information beyond the instantaneous `C,dCdt,R` state?

## Why This Node Exists After 4105

4105 stopped the event-timestamp burst/propagation route because true transition timing did not add robust near-pre activity after matching `C,dCdt,R`. 4120 reframes the next question around recent state path, but first checks whether path variables are numerically identifiable.

## Frozen Inputs

```text
current_state = C density_rms_z3045, dCdt gradient(density_rms_smooth3045,t), R r_rms_z3045
path_coordinates = density_rms_smooth3045, r_rms_smooth3045
activity = A_swarm_tangential_z from 4100A
primary_history_window = 0.50 sec
sensitivity_windows = 0.25, 0.50, 0.75 sec
```


## Primary Metrics

| obs_path_coverage_ge_0p90 | obs_theta_valid_ge_0p90 | min_current_state_finite_fraction | min_dRdt_finite_fraction | max_q99_abs_dRdt | median_primary_path_length | median_abs_turning_proxy_rad | max_abs_spearman_history_current_corr |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 19 | 19 | 1 | 1 | 3.868 | 0.5139 | 0.1916 | 0.8937 |

## Observation Coverage

| ob | dataset | n_frames | median_dt_sec | finite_current_state_fraction | finite_activity_fraction | finite_dRdt_fraction | primary_path_feature_coverage | primary_theta_valid_fraction | primary_turning_valid_fraction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ob1.txt | 1098 | 0.1 | 1 | 1 | 1 | 0.9945 | 0.9845 | 0.9645 |
| 2 | Ob2.txt | 1485 | 0.1 | 1 | 1 | 1 | 0.996 | 0.9811 | 0.9657 |
| 3 | Ob3.txt | 1498 | 0.1 | 1 | 1 | 1 | 0.9967 | 0.9853 | 0.964 |
| 4 | Ob4.txt | 1494 | 0.1 | 1 | 1 | 1 | 0.9967 | 0.9692 | 0.9137 |
| 5 | Ob5.txt | 1494 | 0.1 | 1 | 1 | 1 | 0.9967 | 0.9572 | 0.9036 |
| 6 | Ob6.txt | 1998 | 0.1 | 1 | 1 | 1 | 0.998 | 0.9685 | 0.9284 |
| 7 | Ob7.txt | 998 | 0.1 | 1 | 1 | 1 | 0.996 | 0.986 | 0.9609 |
| 8 | Ob8.txt | 1898 | 0.1 | 1 | 1 | 1 | 0.9968 | 0.9726 | 0.9362 |
| 9 | Ob9.txt | 990 | 0.1 | 1 | 1 | 1 | 0.9939 | 0.9778 | 0.9535 |
| 10 | Ob10.txt | 1498 | 0.1 | 1 | 1 | 1 | 0.9973 | 0.984 | 0.9619 |
| 11 | Ob11.txt | 1997 | 0.1 | 1 | 1 | 1 | 0.998 | 0.9624 | 0.9044 |
| 12 | Ob12.txt | 1997 | 0.1 | 1 | 1 | 1 | 0.998 | 0.984 | 0.9614 |
| 13 | Ob13.txt | 1998 | 0.1 | 1 | 1 | 1 | 0.997 | 0.981 | 0.9575 |
| 14 | Ob14.txt | 1998 | 0.1 | 1 | 1 | 1 | 0.997 | 0.985 | 0.9675 |
| 15 | Ob15.txt | 1997 | 0.1 | 1 | 1 | 1 | 0.998 | 0.9715 | 0.9469 |
| 16 | Ob16.txt | 1997 | 0.1 | 1 | 1 | 1 | 0.998 | 0.9705 | 0.9189 |
| 17 | Ob17.txt | 1998 | 0.1 | 1 | 1 | 1 | 0.998 | 0.962 | 0.9139 |
| 18 | Ob18.txt | 1998 | 0.1 | 1 | 1 | 1 | 0.997 | 0.9755 | 0.9379 |
| 19 | Ob19.txt | 2998 | 0.1 | 1 | 1 | 1 | 0.9987 | 0.9797 | 0.941 |

## Primary h=0.50 sec QC

| ob | dataset | history_window_sec | n_frames | finite_current_state_fraction | finite_activity_fraction | finite_dRdt_fraction | path_feature_coverage | theta_valid_fraction | turning_valid_fraction | median_path_length | q05_path_length | q95_path_length | theta_resultant_length | median_abs_turning_proxy_rad | q95_abs_turning_proxy_rad | median_path_velocity_norm | q99_abs_dRdt |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ob1.txt | 0.5 | 1098 | 1 | 1 | 1 | 0.9945 | 0.9845 | 0.9645 | 0.5189 | 0.1206 | 1.458 | 0.006393 | 0.3065 | 2.702 | 1.167 | 3.529 |
| 2 | Ob2.txt | 0.5 | 1485 | 1 | 1 | 1 | 0.996 | 0.9811 | 0.9657 | 0.5044 | 0.09183 | 1.351 | 0.01612 | 0.2768 | 2.796 | 1.196 | 3.045 |
| 3 | Ob3.txt | 0.5 | 1498 | 1 | 1 | 1 | 0.9967 | 0.9853 | 0.964 | 0.5139 | 0.09264 | 1.357 | 0.01395 | 0.2226 | 2.954 | 1.193 | 3.077 |
| 4 | Ob4.txt | 0.5 | 1494 | 1 | 1 | 1 | 0.9967 | 0.9692 | 0.9137 | 0.4311 | 0.06434 | 1.356 | 0.07254 | 0.1692 | 3.004 | 1.028 | 3.162 |
| 5 | Ob5.txt | 0.5 | 1494 | 1 | 1 | 1 | 0.9967 | 0.9572 | 0.9036 | 0.4806 | 0.05813 | 1.365 | 0.008405 | 0.1424 | 2.998 | 1.122 | 3.167 |
| 6 | Ob6.txt | 0.5 | 1998 | 1 | 1 | 1 | 0.998 | 0.9685 | 0.9284 | 0.4632 | 0.06949 | 1.32 | 0.02134 | 0.1632 | 2.908 | 1.097 | 3.868 |
| 7 | Ob7.txt | 0.5 | 998 | 1 | 1 | 1 | 0.996 | 0.986 | 0.9609 | 0.5764 | 0.1076 | 1.607 | 0.02449 | 0.2539 | 2.882 | 1.321 | 3.335 |
| 8 | Ob8.txt | 0.5 | 1898 | 1 | 1 | 1 | 0.9968 | 0.9726 | 0.9362 | 0.4867 | 0.08057 | 1.407 | 0.02528 | 0.1916 | 2.96 | 1.117 | 2.979 |
| 9 | Ob9.txt | 0.5 | 990 | 1 | 1 | 1 | 0.9939 | 0.9778 | 0.9535 | 0.4739 | 0.1068 | 1.359 | 0.01775 | 0.3295 | 2.761 | 1.106 | 3.309 |
| 10 | Ob10.txt | 0.5 | 1498 | 1 | 1 | 1 | 0.9973 | 0.984 | 0.9619 | 0.519 | 0.1022 | 1.382 | 0.01252 | 0.2684 | 2.837 | 1.17 | 2.986 |
| 11 | Ob11.txt | 0.5 | 1997 | 1 | 1 | 1 | 0.998 | 0.9624 | 0.9044 | 0.552 | 0.06273 | 1.872 | 0.02017 | 0.1135 | 3.075 | 1.25 | 3.468 |
| 12 | Ob12.txt | 0.5 | 1997 | 1 | 1 | 1 | 0.998 | 0.984 | 0.9614 | 0.5144 | 0.09806 | 1.655 | 0.0212 | 0.2691 | 2.828 | 1.153 | 3.485 |
| 13 | Ob13.txt | 0.5 | 1998 | 1 | 1 | 1 | 0.997 | 0.981 | 0.9575 | 0.5232 | 0.08997 | 1.662 | 0.01433 | 0.2309 | 2.837 | 1.166 | 3.597 |
| 14 | Ob14.txt | 0.5 | 1998 | 1 | 1 | 1 | 0.997 | 0.985 | 0.9675 | 0.4756 | 0.09882 | 1.424 | 0.02027 | 0.2709 | 2.758 | 1.103 | 3.392 |
| 15 | Ob15.txt | 0.5 | 1997 | 1 | 1 | 1 | 0.998 | 0.9715 | 0.9469 | 0.4987 | 0.07601 | 1.598 | 0.02962 | 0.1662 | 2.931 | 1.13 | 3.315 |
| 16 | Ob16.txt | 0.5 | 1997 | 1 | 1 | 1 | 0.998 | 0.9705 | 0.9189 | 0.4874 | 0.06911 | 1.421 | 0.007816 | 0.1263 | 3.016 | 1.138 | 3.003 |
| 17 | Ob17.txt | 0.5 | 1998 | 1 | 1 | 1 | 0.998 | 0.962 | 0.9139 | 0.516 | 0.06486 | 1.579 | 0.008161 | 0.1002 | 3.067 | 1.192 | 3.081 |
| 18 | Ob18.txt | 0.5 | 1998 | 1 | 1 | 1 | 0.997 | 0.9755 | 0.9379 | 0.5414 | 0.08303 | 1.642 | 0.006053 | 0.1662 | 2.955 | 1.218 | 3.371 |
| 19 | Ob19.txt | 0.5 | 2998 | 1 | 1 | 1 | 0.9987 | 0.9797 | 0.941 | 0.5313 | 0.0866 | 1.525 | 0.01163 | 0.1318 | 2.996 | 1.246 | 3.444 |

## History-window Sensitivity

| history_window_sec | n_observations | obs_path_coverage_ge_0p90 | median_path_feature_coverage | min_path_feature_coverage | median_theta_valid_fraction | min_theta_valid_fraction | median_path_length | median_abs_turning_proxy_rad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.25 | 19 | 19 | 0.9985 | 0.997 | 0.9374 | 0.9023 | 0.2777 | 0.1128 |
| 0.5 | 19 | 19 | 0.997 | 0.9939 | 0.9778 | 0.9572 | 0.5139 | 0.1916 |
| 0.75 | 19 | 19 | 0.996 | 0.9919 | 0.9858 | 0.9746 | 0.6983 | 0.3096 |

## State Leakage Audit

Largest absolute Spearman correlations are shown for auditing only. 4121 must still match current `C,dCdt,R` before interpreting history effects.

| ob | dataset | history_window_sec | history_feature | current_state | spearman_corr | pearson_corr | n |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ob1.txt | 0.5 | dC_h | dCdt | 0.7585 | 0.7779 | 1092 |
| 7 | Ob7.txt | 0.5 | dC_h | dCdt | 0.7389 | 0.7574 | 994 |
| 18 | Ob18.txt | 0.5 | dC_h | dCdt | 0.7357 | 0.7459 | 1992 |
| 10 | Ob10.txt | 0.5 | dC_h | dCdt | 0.7296 | 0.7401 | 1494 |
| 13 | Ob13.txt | 0.5 | dC_h | dCdt | 0.725 | 0.739 | 1992 |
| 6 | Ob6.txt | 0.5 | dC_h | dCdt | 0.7191 | 0.729 | 1994 |
| 7 | Ob7.txt | 0.5 | dR_h | dCdt | -0.7135 | -0.7211 | 994 |
| 14 | Ob14.txt | 0.5 | dC_h | dCdt | 0.7097 | 0.7261 | 1992 |
| 12 | Ob12.txt | 0.5 | dC_h | dCdt | 0.7089 | 0.7204 | 1993 |
| 17 | Ob17.txt | 0.5 | dC_h | dCdt | 0.7088 | 0.7254 | 1994 |
| 9 | Ob9.txt | 0.5 | dC_h | dCdt | 0.7084 | 0.7264 | 984 |
| 11 | Ob11.txt | 0.5 | dC_h | dCdt | 0.7057 | 0.7297 | 1993 |

## Gate Evaluation

```text
gate_result = pass_state_path_features_feasible_with_leakage_audit
```

State-path features are technically identifiable at the primary 0.50 sec history window. History-current correlations are recorded as leakage audits and must be controlled by 4121 current-state matching.

## What This Supports

- A primary C-R recent path representation can be frozen for 4121 if the gate passed.
- The path direction `theta_h` and turning proxy are measured on smoothed state coordinates, reducing raw derivative noise.

## What This Does Not Prove

| does_not_prove |
| --- |
| history dependence of T1 |
| same-state different-history effect |
| hysteresis-like path dependence |
| OOS history gain |
| causal memory mechanism |

## Decision

`pass_state_path_features_feasible_with_leakage_audit`

## Next Node

| next |
| --- |
| 4121_same_current_state_different_history_matched_test |

## Artifacts

- `Output/4120/state_path_frame.csv`
- `Output/4120/path_feature_qc.csv`
- `Output/4120/history_window_sensitivity.csv`
- `Output/4120/state_leakage_audit.csv`
- `Output/4120/observation_coverage.csv`
- `Output/4120/figures/4120_primary_qc_by_observation.png`
- `Output/4120/figures/4120_path_length_distribution.png`
- `Output/4120/figures/4120_theta_h_polar_hist.png`
- `Output/4120/figures/4120_state_leakage_heatmap.png`
- `Output/4120/decision.json`
