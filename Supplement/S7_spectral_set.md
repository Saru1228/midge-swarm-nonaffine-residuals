# S7 `spectral_set` Construction

## Purpose

This section records the provenance of the low/high compact-density labels
used in state-matched analyses. The goal is to make the labels reconstructable
without reading the old experiment scripts.

## Source Outputs

```text
Output/4147/spectral_set_provenance.md
Output/4147/spectral_set_algorithm.md
Output/4147/source_code_map.csv
Output/4147/example_label_trace.csv
Output/4147/selected_partition_summary.csv
Output/4147/label_distribution.csv
Output/4147/label_propagation_checks.csv
Output/4147/t1_independence_scan.csv
Output/4147/supplement_method.tex
```

## Construction Summary

The `spectral_set` labels were inherited from an upstream transfer-operator
compact-density coarse graining. The candidate variables were robust
standardized:

```text
r_rms
density_rms
anisotropy
```

The selected partition used a 4-bin Ulam grid in each variable, producing
64 total cells and 60 active cells. The selected split was `eig2`, based on
the leading nontrivial transfer-operator eigenfunction.

## Main Provenance Metrics

```text
lag = 0.10 s
top nontrivial eigenvalue = 0.8564307275942583
minimum pooled retention = 0.8751650955023956
minimum retention lift = 0.3750263483202336
frame labels = 334542
observations with labels = 19
low labels = 167210
high labels = 167332
transition events linked to labels = 1471
label propagation checks passed = true
T1 independence scan passed = true
```

The high set was more compact and denser in the selected coordinates, whereas
the low set was more expanded and lower density.

## Independence From T1

The label construction used compact-density variables upstream of T1. The
4147 audit found no use of T1 terms in the construction or materialization
scripts for the selected `spectral_set` labels.

## Interpretation

The `spectral_set` labels can be described as inherited transfer-operator
compact-density labels. They should not be described as thresholds fitted from
T1 or as labels discovered to optimize the T1 result.

## What This Does Not Prove

```text
closed Markov model
biological attractor
mechanism for T1
T1-optimized state partition
```
