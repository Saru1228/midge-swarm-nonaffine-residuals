# S6 Recent-History Matching

## Purpose

This analysis asks whether recent path history separates T1 after the current
compact state has been matched within each observation.

## Source Outputs

```text
Output/4121/state_matched_history_pairs.csv
Output/4121/matching_quality.csv
Output/4121/observation_level_effects.csv
Output/4121/history_shuffle_null.csv
Output/4121/sensitivity.csv
Output/4121/decision.json
Output/4150/figures/Fig4_final.pdf
Output/4150/figures/Fig5_final.pdf
```

## Primary Matching Design

```text
current state = (C, dC/dt, R)
history feature = h500_theta_h
history window = 0.50 s
state distance threshold = 0.50
history angle contrast threshold = 90 degrees
minimum temporal separation = 1.0 s
maximum pairs per anchor = 5
maximum pairs per observation = 10000
minimum pairs per observation = 100
null = within-observation history-theta shuffle with pair recomputation
```

## Result

```text
observations with sufficient matched pairs = 19/19
median selected pairs per sufficient observation = 4723
median paired-frame fraction = 0.7720488466757124
median state distance = 0.2972932945091832
median signed history-axis delta A_z = -0.011040047877916181
median absolute signed history-axis delta A_z = 0.07628898491170816
direction consistency fraction = 0.5263157894736842
real beats shuffled median absolute effect = 14/19
real beats shuffled q95 absolute effect = 6/19
median shuffled-null absolute signed delta A_z = 0.03803189509177676
median real-minus-shuffled absolute effect = 0.03414293122320826
```

## Interpretation

Recent history contained observation-specific information: many observations
exceeded the shuffled median in absolute effect, but the sign/order was not
stable and only a minority exceeded the q95 shuffled threshold. Therefore this
is a boundary result, not a universal memory mechanism.

## What This Does Not Prove

```text
causal memory
thermodynamic hysteresis
transition trigger
out-of-sample history gain
network propagation
```
