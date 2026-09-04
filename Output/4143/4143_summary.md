# Node 4143 Summary

## Question

Are the local affine fits used in T1 rank-sufficient and well-conditioned across
all 19 observations, and are high T1 values mainly produced by ill-conditioned
fits?

## Method

The node samples raw trajectory frames from each observation, fits the same
local affine model used by the 4081 T1 definition, and records per-focal fit
quality:

```text
k = 8, 10
lag = 0.10 sec
max frames per observation = sampled, not exhaustive
max focals per frame = sampled, not exhaustive
```

The QC table reports rank-screen pass rate, valid-fit fraction, condition
number quantiles, and whether the top 5% of focal T1 samples are concentrated
in condition number > 100 fits.

## Overall Decision

`pass_local_affine_conditioning_qc`

Local affine fits are broadly rank-sufficient and well-conditioned; large T1 samples are not concentrated in severely ill-conditioned fits.

## Primary Metrics

| n_ob_k_combos | n_combo_passes | n_observations | n_observations_all_k_pass | median_valid_fit_fraction | min_valid_fit_fraction | median_condition_number_over_combos | max_combo_q95_condition_number | max_combo_frac_condition_gt_100 | median_top5_t1_condition_number | max_top5_t1_frac_condition_gt_100 | median_spearman_log_condition_vs_log_t1 | max_abs_spearman_log_condition_vs_log_t1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 38 | 38 | 19 | 19 | 1 | 0.9998 | 2.367 | 6.283 | 0 | 2.061 | 0 | -0.1383 | 0.1944 |

## Compact Observation/K Summary

| ob | k | valid_fit_fraction | median_condition_number | q95_condition_number | frac_condition_gt_100 | top5_t1_median_condition_number | top5_t1_frac_condition_gt_100 | spearman_log_condition_vs_log_t1 | combo_passes_qc_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 8 | 1 | 2.167 | 4.02 | 0 | 2.091 | 0 | -0.06877 | True |
| 1 | 10 | 1 | 1.972 | 3.432 | 0 | 1.889 | 0 | -0.08645 | True |
| 2 | 8 | 1 | 2.231 | 4.4 | 0 | 2.068 | 0 | -0.1182 | True |
| 2 | 10 | 1 | 2.077 | 3.879 | 0 | 1.874 | 0 | -0.155 | True |
| 3 | 8 | 1 | 2.334 | 4.832 | 0 | 2.079 | 0 | -0.1408 | True |
| 3 | 10 | 1 | 2.175 | 4.341 | 0 | 1.908 | 0 | -0.1882 | True |
| 4 | 8 | 1 | 2.625 | 5.989 | 0 | 2.188 | 0 | -0.1284 | True |
| 4 | 10 | 1 | 2.447 | 5.331 | 0 | 2.046 | 0 | -0.1646 | True |
| 5 | 8 | 1 | 2.588 | 6.154 | 0 | 2.196 | 0 | -0.165 | True |
| 5 | 10 | 1 | 2.419 | 5.44 | 0 | 2.008 | 0 | -0.1944 | True |
| 6 | 8 | 0.9998 | 2.645 | 5.926 | 0 | 2.269 | 0 | -0.1477 | True |
| 6 | 10 | 0.9998 | 2.505 | 5.459 | 0 | 2.155 | 0 | -0.1715 | True |
| 7 | 8 | 1 | 2.276 | 4.507 | 0 | 2.025 | 0 | -0.1131 | True |
| 7 | 10 | 1 | 2.102 | 3.876 | 0 | 1.926 | 0 | -0.145 | True |
| 8 | 8 | 1 | 2.689 | 5.953 | 0 | 2.311 | 0 | -0.09986 | True |
| 8 | 10 | 1 | 2.521 | 5.26 | 0 | 2.162 | 0 | -0.1301 | True |
| 9 | 8 | 0.9999 | 2.217 | 4.27 | 0 | 2.019 | 0 | -0.1037 | True |
| 9 | 10 | 0.9999 | 2.07 | 3.754 | 0 | 1.892 | 0 | -0.1311 | True |
| 10 | 8 | 1 | 2.171 | 4.116 | 0 | 1.997 | 0 | -0.0973 | True |
| 10 | 10 | 1 | 2.005 | 3.478 | 0 | 1.868 | 0 | -0.1362 | True |
| 11 | 8 | 0.9998 | 2.768 | 6.283 | 0 | 2.326 | 0 | -0.1206 | True |
| 11 | 10 | 0.9998 | 2.626 | 5.493 | 0 | 2.162 | 0 | -0.1748 | True |
| 12 | 8 | 0.9998 | 2.425 | 4.759 | 0 | 2.074 | 0 | -0.1096 | True |
| 12 | 10 | 0.9998 | 2.293 | 4.234 | 0 | 1.919 | 0 | -0.1408 | True |
| 13 | 8 | 1 | 2.324 | 4.495 | 0 | 2.055 | 0 | -0.1206 | True |
| 13 | 10 | 1 | 2.17 | 3.914 | 0 | 1.858 | 0 | -0.1728 | True |
| 14 | 8 | 1 | 2.231 | 4.331 | 0 | 2.026 | 0 | -0.1141 | True |
| 14 | 10 | 1 | 2.083 | 3.759 | 0 | 1.851 | 0 | -0.1535 | True |
| 15 | 8 | 0.9998 | 2.719 | 5.776 | 0 | 2.323 | 0 | -0.1317 | True |
| 15 | 10 | 0.9998 | 2.56 | 5.203 | 0 | 2.187 | 0 | -0.1308 | True |
| 16 | 8 | 1 | 2.405 | 5.209 | 0 | 2.183 | 0 | -0.1408 | True |
| 16 | 10 | 1 | 2.228 | 4.779 | 0 | 1.961 | 0 | -0.1773 | True |
| 17 | 8 | 0.9998 | 2.817 | 6.18 | 0 | 2.55 | 0 | -0.08777 | True |
| 17 | 10 | 0.9998 | 2.824 | 5.776 | 0 | 2.483 | 0 | -0.1403 | True |
| 18 | 8 | 1 | 2.568 | 5.601 | 0 | 2.26 | 0 | -0.137 | True |
| 18 | 10 | 1 | 2.458 | 5.028 | 0 | 2.135 | 0 | -0.154 | True |
| 19 | 8 | 0.9999 | 2.401 | 5.115 | 0 | 2.045 | 0 | -0.1396 | True |
| 19 | 10 | 0.9999 | 2.241 | 4.524 | 0 | 1.89 | 0 | -0.1885 | True |

## Boundary

This node tests numerical conditioning of local affine subtraction only. It
does not prove a biological mechanism and does not replace the detrending or
omnibus-null checks.

## Next

| next |
| --- |
| 4144_definition_notation_figure_cleanup |

## Artifacts

- `Output/4143/local_affine_conditioning_samples.csv`
- `Output/4143/local_affine_conditioning_summary.csv`
- `Output/4143/decision.json`
- `Output/4143/figures/4143_q95_condition_by_observation.png`
- `Output/4143/figures/4143_median_t1_vs_condition.png`
