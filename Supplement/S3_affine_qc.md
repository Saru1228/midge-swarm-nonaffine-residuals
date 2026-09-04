# S3 Local Affine Conditioning Quality Control

## Purpose

This analysis checks whether the local affine subtraction used to define T1 is
numerically unstable or whether high T1 values are concentrated in severely
ill-conditioned local affine fits.

## Source Outputs

```text
Output/4143/local_affine_conditioning_summary.csv
Output/4143/local_affine_conditioning_summary.json
Output/4143/local_affine_conditioning_samples.csv
Output/4143/decision.json
```

## Sampling Design

For each observation and each original neighborhood scale (`k=8`, `k=10`),
frames were sampled across the recording. Local affine least-squares fits were
then checked for rank sufficiency, valid-fit fraction, condition number, and
the relationship between condition number and T1 magnitude.

## Gate

A local affine observation-scale combination passed if it satisfied:

```text
valid_fit_fraction >= 0.85
rank_screen_pass_fraction >= 0.85
median_condition_number <= 10
q95_condition_number <= 50
frac_condition_gt_100 <= 0.01
top5_t1_frac_condition_gt_100 <= 0.05
```

The overall pass gate required at least `34/38` observation-scale combinations
and at least `16/19` observations passing both k values.

## Result

```text
observation-scale combinations = 38
passed combinations = 38/38
observations passing both k values = 19/19
median valid-fit fraction = 1.0
minimum valid-fit fraction = 0.999763481551561
median condition number over combinations = 2.3674845690394064
largest q95 condition number across combinations = 6.282690016495806
maximum fraction with condition number > 100 = 0.0
median top-5 percent T1 condition number = 2.061165679743935
maximum top-5 percent T1 fraction with condition number > 100 = 0.0
```

## Interpretation

The local affine fits were broadly rank-sufficient and well-conditioned in this
sampled QC. Large T1 values were not concentrated in severely ill-conditioned
fits.

## What This Does Not Prove

```text
biological mechanism
absence of every preprocessing artifact
correctness of every residual interpretation
causal meaning of local affine subtraction
```
