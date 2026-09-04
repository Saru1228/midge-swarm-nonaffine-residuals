# S4 Scale and Lag Sensitivity

## Purpose

This analysis asks whether the T1 survival decision depends narrowly on one
neighborhood scale or one temporal lag.

## Source Outputs

```text
Output/4131/decision.json
Output/4131/observation_positive_coverage_matrix.csv
Output/4131/positive_phenomenon_atlas.csv
Output/4131/figures/4131_observation_coverage_matrix.png
Output/4150/figures/Fig2_final.pdf
```

## Primary Counts

```text
T1 any-scale survival = 15/19 observations
T1 two-scale survival = 14/19 observations
survivor-class scale/lag robustness = 14/15 observations
```

The two-scale count uses the original neighborhood sizes `k=8` and `k=10`.
The scale/lag robustness result is reported within the survivor class, not as
a claim over all 19 observations.

## Interpretation

The T1 signal is not restricted to a single original scale in most survivor
observations. However, the robustness claim is conditional on the survivor
class and should not be generalized to all observations.

## What This Does Not Prove

```text
universal T1 survival
optimality of k=8 or k=10
scale-free law
preprocessing-invariant exact observation count
```
