# 3032c EGRT Smooth-Null Audit

## Scope

3032b showed that the 3032 partition is interpretable but shallow. 3032c tests whether the observed retention exceeds null models that preserve smoothness in the slow variables.

## EGRT Node

| field | value |
| --- | --- |
| node_id | 3032c_smooth_null_audit |
| parent | 3032b_state_meaning_residence_audit |
| node_type | artifact-control |
| decision | stop_strong_metastability_claim_smooth_null_sufficient |
| recommended next node | return to synthesis: compact-density slow mode, not strong metastable attractor |
| boundary reading | The retention of the compact-density partition is explainable by smooth autocorrelation/cross-correlation nulls; do not claim a strong metastable attractor. |

## Nulls

- `label_shuffle`: preserves only low/high occupancy inside each Ob.
- `independent_phase_rank`: preserves each slow variable's marginal distribution and approximate power spectrum, but breaks cross-variable phase coupling.
- `coupled_phase_rank`: applies common phase shifts to the slow-variable spectra before rank matching, preserving a stronger smooth multivariate linear null.

## Decision Metrics

| node_id | parent_node | parent_decision | metric | real_long_lag_q25_lift | coupled_phase_null_median_gap | coupled_phase_null_q75 | coupled_phase_null_q95 | coupled_phase_p_null_ge_real | independent_phase_null_median_gap | label_shuffle_null_median_gap | survives_coupled_phase_gate | explained_by_coupled_phase | eg_rt_decision | recommended_next_node | boundary_reading |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3032c_smooth_null_audit | 3032b_state_meaning_residence_audit | boundary_shallow_but_persistent_organization | long_lag_q25_lift_median_sets | 0.1719 | 0.01512 | 0.1604 | 0.1622 | 0.04 | 0.03562 | 0.1739 | False | True | stop_strong_metastability_claim_smooth_null_sufficient | return to synthesis: compact-density slow mode, not strong metastable attractor | The retention of the compact-density partition is explainable by smooth autocorrelation/cross-correlation nulls; do not claim a strong metastable attractor. |

## Primary Null Comparison

| metric | surrogate_type | real_value | null_n | null_median | null_q75 | null_q95 | null_max | real_minus_null_median | p_null_ge_real |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| long_lag_q25_lift_median_sets | coupled_phase_rank | 0.1719 | 24 | 0.1568 | 0.1604 | 0.1622 | 0.1661 | 0.01512 | 0.04 |
| long_lag_q25_lift_median_sets | independent_phase_rank | 0.1719 | 24 | 0.1363 | 0.1396 | 0.1425 | 0.1438 | 0.03562 | 0.04 |
| long_lag_q25_lift_median_sets | label_shuffle | 0.1719 | 24 | -0.002029 | -0.001301 | -0.0003817 | 0.0007261 | 0.1739 | 0.04 |

## All Null Metrics

| metric | surrogate_type | real_value | null_n | null_median | null_q75 | null_q95 | null_max | real_minus_null_median | p_null_ge_real |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| long_lag_q25_lift_median_sets | coupled_phase_rank | 0.1719 | 24 | 0.1568 | 0.1604 | 0.1622 | 0.1661 | 0.01512 | 0.04 |
| long_lag_q25_lift_median_sets | independent_phase_rank | 0.1719 | 24 | 0.1363 | 0.1396 | 0.1425 | 0.1438 | 0.03562 | 0.04 |
| long_lag_q25_lift_median_sets | label_shuffle | 0.1719 | 24 | -0.002029 | -0.001301 | -0.0003817 | 0.0007261 | 0.1739 | 0.04 |
| long_lag_q25_retention_median_sets | coupled_phase_rank | 0.6721 | 24 | 0.6561 | 0.6603 | 0.6621 | 0.6664 | 0.01601 | 0.04 |
| long_lag_q25_retention_median_sets | independent_phase_rank | 0.6721 | 24 | 0.6355 | 0.6386 | 0.6431 | 0.6441 | 0.03666 | 0.04 |
| long_lag_q25_retention_median_sets | label_shuffle | 0.6721 | 24 | 0.4977 | 0.4988 | 0.4998 | 0.5004 | 0.1744 | 0.04 |
| lag0p1_q25_lift_median_sets | coupled_phase_rank | 0.3702 | 24 | 0.3451 | 0.3479 | 0.3516 | 0.3523 | 0.02511 | 0.04 |
| lag0p1_q25_lift_median_sets | independent_phase_rank | 0.3702 | 24 | 0.3213 | 0.3232 | 0.3301 | 0.3312 | 0.04896 | 0.04 |
| lag0p1_q25_lift_median_sets | label_shuffle | 0.3702 | 24 | -0.002547 | -0.001493 | -0.0004536 | 0.0007007 | 0.3728 | 0.04 |
| lag1p0_q25_lift_median_sets | coupled_phase_rank | 0.07405 | 24 | 0.06388 | 0.06866 | 0.07142 | 0.075 | 0.01017 | 0.08 |
| lag1p0_q25_lift_median_sets | independent_phase_rank | 0.07405 | 24 | 0.05301 | 0.05692 | 0.06015 | 0.06149 | 0.02103 | 0.04 |
| lag1p0_q25_lift_median_sets | label_shuffle | 0.07405 | 24 | -0.002264 | -0.001679 | -0.000558 | -0.0002007 | 0.07631 | 0.04 |
| median_residence_all | coupled_phase_rank | 0.13 | 24 | 0.04 | 0.04 | 0.04 | 0.04 | 0.09 | 0.04 |
| median_residence_all | independent_phase_rank | 0.13 | 24 | 0.03 | 0.03 | 0.03 | 0.03 | 0.1 | 0.04 |
| median_residence_all | label_shuffle | 0.13 | 24 | 0.015 | 0.02 | 0.02 | 0.02 | 0.115 | 0.04 |
| q75_residence_all | coupled_phase_rank | 0.54 | 24 | 0.16 | 0.16 | 0.16 | 0.16 | 0.38 | 0.04 |
| q75_residence_all | independent_phase_rank | 0.54 | 24 | 0.12 | 0.13 | 0.13 | 0.13 | 0.42 | 0.04 |
| q75_residence_all | label_shuffle | 0.54 | 24 | 0.02 | 0.0225 | 0.03 | 0.03 | 0.52 | 0.04 |
| q90_residence_all | coupled_phase_rank | 1.31 | 24 | 0.67 | 0.68 | 0.69 | 0.7 | 0.64 | 0.04 |
| q90_residence_all | independent_phase_rank | 1.31 | 24 | 0.49 | 0.5 | 0.517 | 0.52 | 0.82 | 0.04 |
| q90_residence_all | label_shuffle | 1.31 | 24 | 0.04 | 0.04 | 0.04 | 0.04 | 1.27 | 0.04 |

## Real Metric Values

| long_lag_q25_lift_median_sets | long_lag_q25_retention_median_sets | lag0p1_q25_lift_median_sets | lag1p0_q25_lift_median_sets | median_residence_all | q75_residence_all | q90_residence_all |
| --- | --- | --- | --- | --- | --- | --- |
| 0.1719 | 0.6721 | 0.3702 | 0.07405 | 0.13 | 0.54 | 1.31 |

## Outputs

- `Output/3032c/3032c_egrt_node.json`
- `Output/3032c/tables/null_comparison_summary.csv`
- `Output/3032c/tables/surrogate_metric_summary.csv`
- `Output/3032c/tables/surrogate_lag_summary.csv`
- `Output/3032c/tables/surrogate_residence_summary.csv`
- `Output/3032c/tables/egrt_decision_summary.csv`
- `Output/3032c/figures/long_lag_lift_null_comparison.png`
- `Output/3032c/figures/retention_lift_decay_vs_nulls.png`

## Interpretation Boundary

If the real compact-density partition is not above the coupled phase-rank null, the strongest supported statement is a descriptive slow compactness mode with smooth persistence. That is weaker than a metastable attractor claim and should terminate this 3032 branch unless a new observable basis is introduced.
