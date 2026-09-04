# Node 4100 Summary

## Question

After matching `C,dCdt,radius` within the same observation, do true compact-density transition times still contain extra focal-centered local non-affine tangential activity?

## Why This Node Exists

4100A constructed the unique focal-centered activity table needed for 410x and exposed the neighbor-overlap boundary. 4100 now tests the main event-locality gate before any burst or propagation analysis.

## Data

- Activity: `Output/4100A/swarm_activity_frame.csv`
- Events: `Output/3045/tables/transition_events.csv`
- State: `Output/3045/processed/frame_residual_signals.csv`
- Scope: all 19 observations

## Frozen Parameters

```text
activity = A_swarm_tangential_z
near_pre = [-0.25, 0.00] sec
state = C density_rms_z3045, dCdt gradient(density_rms_smooth3045,t), R r_rms_z3045
matching = same observation nearest neighbors in robust standardized state space
control exclusion = no true transition within +/- 0.75 sec
```


## Primary Metrics

- median observation delta: `-0.03289` z
- same-direction observation fraction: `0.4211`
- real beats shifted-event null fraction: `0.275`
- total acceptable event fraction: `0.9796`
- median observation best-match distance: `0.1763`

## Matching Quality

| ob | dataset | n_events_total | n_events_with_window | n_events_with_any_match | n_events_acceptable | acceptable_event_fraction | median_best_match_distance | median_abs_std_diff_C | median_abs_std_diff_dCdt | median_abs_std_diff_R | n_control_candidates |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ob1.txt | 28 | 28 | 28 | 27 | 0.9643 | 0.1946 | 0.05546 | 0.1112 | 0.0754 | 740 |
| 2 | Ob2.txt | 43 | 43 | 43 | 43 | 1 | 0.2037 | 0.09332 | 0.06597 | 0.0691 | 929 |
| 3 | Ob3.txt | 40 | 40 | 40 | 40 | 1 | 0.1476 | 0.08048 | 0.07527 | 0.04838 | 991 |
| 4 | Ob4.txt | 58 | 58 | 58 | 55 | 0.9483 | 0.1689 | 0.0647 | 0.06201 | 0.08231 | 847 |
| 5 | Ob5.txt | 93 | 93 | 93 | 92 | 0.9892 | 0.1831 | 0.08729 | 0.08387 | 0.0694 | 512 |
| 6 | Ob6.txt | 112 | 112 | 112 | 112 | 1 | 0.1471 | 0.05667 | 0.06014 | 0.07852 | 850 |
| 7 | Ob7.txt | 33 | 33 | 33 | 33 | 1 | 0.2187 | 0.1001 | 0.07447 | 0.08991 | 576 |
| 8 | Ob8.txt | 84 | 84 | 84 | 83 | 0.9881 | 0.14 | 0.05513 | 0.05878 | 0.0608 | 952 |
| 9 | Ob9.txt | 37 | 36 | 36 | 36 | 0.973 | 0.2861 | 0.0931 | 0.1772 | 0.1106 | 577 |
| 10 | Ob10.txt | 36 | 36 | 36 | 36 | 1 | 0.1298 | 0.0725 | 0.06651 | 0.05391 | 1058 |
| 11 | Ob11.txt | 119 | 119 | 119 | 115 | 0.9664 | 0.1585 | 0.03916 | 0.069 | 0.06956 | 779 |
| 12 | Ob12.txt | 91 | 91 | 91 | 87 | 0.956 | 0.2325 | 0.1023 | 0.08597 | 0.1016 | 990 |
| 13 | Ob13.txt | 102 | 102 | 102 | 96 | 0.9412 | 0.1949 | 0.08577 | 0.07327 | 0.09808 | 895 |
| 14 | Ob14.txt | 47 | 47 | 47 | 47 | 1 | 0.143 | 0.07798 | 0.04686 | 0.08061 | 1421 |
| 15 | Ob15.txt | 96 | 96 | 96 | 93 | 0.9688 | 0.1838 | 0.08 | 0.08921 | 0.09186 | 931 |
| 16 | Ob16.txt | 84 | 84 | 84 | 83 | 0.9881 | 0.1395 | 0.07575 | 0.05078 | 0.07234 | 1052 |
| 17 | Ob17.txt | 122 | 122 | 122 | 120 | 0.9836 | 0.1763 | 0.07541 | 0.0776 | 0.07901 | 781 |
| 18 | Ob18.txt | 103 | 103 | 103 | 100 | 0.9709 | 0.2181 | 0.09406 | 0.1094 | 0.08061 | 912 |
| 19 | Ob19.txt | 143 | 143 | 143 | 143 | 1 | 0.1398 | 0.07424 | 0.06554 | 0.06617 | 1378 |

## Observation-level Results

| ob | dataset | n_events_acceptable | median_event_A_pre_z | median_control_A_pre_z | median_delta_A_pre_z | mean_delta_A_pre_z | fraction_positive_delta | median_best_match_distance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ob1.txt | 27 | 0.04941 | 0.1528 | -0.03289 | 0.0307 | 0.4815 | 0.1929 |
| 2 | Ob2.txt | 43 | 0.1898 | 0.1307 | 0.09667 | 0.2343 | 0.5814 | 0.2037 |
| 3 | Ob3.txt | 40 | -0.0471 | -0.01457 | -0.0939 | -0.04847 | 0.4 | 0.1476 |
| 4 | Ob4.txt | 55 | -0.1561 | 0.3215 | -0.3365 | -0.3073 | 0.3636 | 0.1651 |
| 5 | Ob5.txt | 92 | 0.0849 | -0.09032 | -0.05805 | 0.1009 | 0.4674 | 0.1824 |
| 6 | Ob6.txt | 112 | -0.03528 | -0.1055 | 0.03201 | 0.06714 | 0.5268 | 0.1471 |
| 7 | Ob7.txt | 33 | 0.02201 | -0.1319 | 0.05559 | 0.1832 | 0.5455 | 0.2187 |
| 8 | Ob8.txt | 83 | -0.145 | 0.01397 | -0.1388 | -0.1126 | 0.4578 | 0.1384 |
| 9 | Ob9.txt | 36 | 0.1297 | 0.2761 | -0.1619 | -0.06975 | 0.4722 | 0.2861 |
| 10 | Ob10.txt | 36 | -0.01067 | 0.002637 | 0.05903 | -0.04996 | 0.5278 | 0.1298 |
| 11 | Ob11.txt | 115 | 0.01413 | -0.04726 | 0.06067 | 0.08463 | 0.513 | 0.1461 |
| 12 | Ob12.txt | 87 | -0.1008 | 0.08147 | -0.1915 | -0.1774 | 0.3793 | 0.2181 |
| 13 | Ob13.txt | 96 | 0.04525 | -0.0563 | 0.1882 | 0.1385 | 0.5938 | 0.1894 |
| 14 | Ob14.txt | 47 | 0.006741 | 0.01795 | -0.1609 | -0.117 | 0.4468 | 0.143 |
| 15 | Ob15.txt | 93 | -0.08882 | 0.1169 | -0.301 | -0.1077 | 0.4086 | 0.177 |
| 16 | Ob16.txt | 83 | -0.03481 | -0.04675 | 0.05874 | -0.01962 | 0.5422 | 0.1379 |
| 17 | Ob17.txt | 120 | -0.07443 | 0.02707 | 0.08743 | 0.08031 | 0.525 | 0.1744 |
| 18 | Ob18.txt | 100 | 0.04016 | 0.1552 | -0.01802 | -0.05346 | 0.49 | 0.2173 |
| 19 | Ob19.txt | 143 | -0.06032 | -0.03991 | -0.08571 | -0.0336 | 0.4476 | 0.1398 |

## Shifted-event Null

| n_shift_reps | null_median | null_q05 | null_q95 |
| --- | --- | --- | --- |
| 80 | 0.007356 | -0.07075 | 0.1036 |

## Event-centered Profile

| lag_sec | n_events | event_median_A_z | control_median_A_z | delta_median_A_z |
| --- | --- | --- | --- | --- |
| -0.5 | 1435 | 0.0337 | -0.0478 | 0.01644 |
| -0.4 | 1436 | 0.01421 | 0.03459 | -0.02038 |
| -0.3 | 1437 | -0.06066 | 0.08808 | -0.1679 |
| -0.2 | 1439 | 0.007004 | 0.08871 | -0.1116 |
| -0.1 | 1441 | -0.05097 | 0.05882 | -0.05661 |
| -0 | 1441 | -0.04907 | 0.09234 | -0.187 |
| 0.1 | 1440 | -0.00146 | -0.001099 | -0.046 |
| 0.2 | 1439 | 0.07005 | 0.1002 | 0.1222 |
| 0.3 | 1438 | 0.01736 | -0.02188 | 0.1153 |
| 0.4 | 1436 | 0.001381 | -0.00854 | 0.02462 |
| 0.5 | 1434 | -0.02592 | 0.004786 | 0.02552 |

## Gate Evaluation

```text
gate_result = fail_event_timing_not_beyond_continuous_state
```

After matching continuous compact-density state within observation, true transition timing does not show robust extra near-pre activity.

## What This Supports

- It directly tests whether real event timing adds information beyond matched continuous compact-density state at the swarm-activity level.
- It separates the earlier near-pre diagnostic from a stricter state-matched event-locality claim.

## What This Does Not Prove

| does_not_prove |
| --- |
| burst localization |
| propagation |
| causal trigger |
| individual residual velocity |
| prediction before transition |

## Decision

`fail_event_timing_not_beyond_continuous_state`

## Next Node

| next |
| --- |
| 4105_state_matched_negative_synthesis |

## Artifacts

- `Output/4100/event_control_matches.csv`
- `Output/4100/matching_quality.csv`
- `Output/4100/event_local_effects.csv`
- `Output/4100/observation_level_effects.csv`
- `Output/4100/shifted_event_null.csv`
- `Output/4100/event_centered_profile.csv`
- `Output/4100/figures/4100_observation_effects.png`
- `Output/4100/figures/4100_matching_quality.png`
- `Output/4100/figures/4100_shifted_event_null.png`
- `Output/4100/figures/4100_event_centered_profile.png`
- `Output/4100/decision.json`
