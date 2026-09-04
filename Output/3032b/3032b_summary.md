# 3032b EGRT State-Meaning and Residence Audit

## Scope

3032 found a positive transfer-operator partition. 3032b audits whether that partition should be treated as a meaningful metastable state or as a shallow consequence of smooth slow-variable persistence.

## EGRT Node

| field | value |
| --- | --- |
| node_id | 3032b_state_meaning_residence_audit |
| parent | 3032_transfer_operator_metastability |
| node_type | mechanism |
| decision | boundary_shallow_but_persistent_organization |
| recommended next node | 3032c smooth-autocorrelation/null-model audit |
| boundary reading | The partition is interpretable and remains above baseline at longer lags, but individual residence runs are short; test whether smooth autocorrelation explains the result. |

## Decision Metrics

| node_id | parent_node | parent_decision | best_partition_id | strongest_state_space_variable | strongest_delta_high_minus_low_z | strongest_variable_sign_consistency | meaning_pass | median_residence_sec | q75_residence_sec | residence_pass | long_lag_sec | long_lag_median_q25_retention | long_lag_median_q25_retention_lift | long_lag_pass | coarse_state_nmi | coarse_state_independent | eg_rt_decision | recommended_next_node | boundary_reading |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3032b_state_meaning_residence_audit | 3032_transfer_operator_metastability | support_stochastic_metastability_branch | eig2 | density_rms | 1.341 | 1 | True | 0.13 | 0.54 | False | 0.5 | 0.6721 | 0.1719 | True | 0.001152 | True | boundary_shallow_but_persistent_organization | 3032c smooth-autocorrelation/null-model audit | The partition is interpretable and remains above baseline at longer lags, but individual residence runs are short; test whether smooth autocorrelation explains the result. |

## Emission Meaning

| variable | role | delta_high_minus_low_z | median_ob_delta_z | frac_ob_same_sign | frac_ob_abs_delta_ge_0p5 |
| --- | --- | --- | --- | --- | --- |
| density_rms | 3032_state_space | 1.341 | 1.349 | 1 | 1 |
| r_rms | 3032_state_space | -1.328 | -1.345 | 1 | 1 |
| anisotropy | 3032_state_space | -0.267 | -0.3232 | 1 | 0.05263 |
| polarization | external_emission | -0.02838 | -0.02539 | 0.6316 | 0 |
| radial_velocity_mean | external_emission | -0.02743 | -0.0293 | 0.7368 | 0 |
| milling | external_emission | -0.02562 | -0.02181 | 0.6842 | 0 |
| center_speed | external_emission | -0.02348 | -0.01977 | 0.7368 | 0 |
| speed_mean | external_emission | 0.006137 | 0.01135 | 0.5263 | 0 |
| kinetic_energy | external_emission | -0.005139 | 0.02468 | 0.4737 | 0 |
| n | external_emission | 0 | 0.2248 | 0.4211 | 0.3158 |
| frac_outward | external_emission | 0 | 0 | 0.6316 | 0 |
| p_inner | external_emission | 0 | 0.1102 | 0 | 0.05263 |

## Residence Summary

| spectral_set | n_runs | median_run_duration_sec | q75_run_duration_sec | q90_run_duration_sec | q95_run_duration_sec | mean_run_duration_sec | frac_runs_ge_0p1s | frac_runs_ge_0p2s | frac_runs_ge_0p5s | frac_runs_ge_1p0s | frac_runs_ge_2p0s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| high | 3633 | 0.14 | 0.56 | 1.33 | 1.93 | 0.4606 | 0.5557 | 0.4297 | 0.2692 | 0.1462 | 0.04707 |
| low | 3638 | 0.13 | 0.52 | 1.3 | 2.09 | 0.4596 | 0.5371 | 0.4109 | 0.2543 | 0.1369 | 0.05278 |
| all | 7271 | 0.13 | 0.54 | 1.31 | 1.995 | 0.4601 | 0.5464 | 0.4203 | 0.2617 | 0.1415 | 0.04992 |

## Retention Decay

| lag_sec | spectral_set | median_retention | q25_retention | q75_retention | median_retention_lift | q25_retention_lift | frac_ob_lift_positive | median_mass | median_origin_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.05 | high | 0.9244 | 0.9112 | 0.9293 | 0.4234 | 0.4106 | 1 | 0.5 | 9890 |
| 0.05 | low | 0.924 | 0.9112 | 0.9296 | 0.425 | 0.4117 | 1 | 0.5 | 9935 |
| 0.1 | high | 0.8771 | 0.8706 | 0.8836 | 0.3767 | 0.3696 | 1 | 0.5 | 9886 |
| 0.1 | low | 0.8776 | 0.8704 | 0.8837 | 0.3776 | 0.3709 | 1 | 0.5 | 9930 |
| 0.2 | high | 0.8142 | 0.8036 | 0.8211 | 0.3153 | 0.3043 | 1 | 0.5 | 9884 |
| 0.2 | low | 0.8163 | 0.8038 | 0.8205 | 0.3139 | 0.3029 | 1 | 0.5 | 9920 |
| 0.5 | high | 0.6943 | 0.6729 | 0.6968 | 0.1938 | 0.172 | 1 | 0.5 | 9882 |
| 0.5 | low | 0.6929 | 0.6713 | 0.6998 | 0.1926 | 0.1719 | 1 | 0.5 | 9909 |
| 1 | high | 0.5864 | 0.574 | 0.6245 | 0.08633 | 0.07346 | 1 | 0.5 | 9882 |
| 1 | low | 0.5901 | 0.5742 | 0.6184 | 0.08811 | 0.07463 | 1 | 0.5 | 9867 |

## Coarse-State Overlap

| n_frames | normalized_mutual_information | cramers_v | coarse_state_source |
| --- | --- | --- | --- |
| 334542 | 0.001152 | 0.04678 | 3013 classifier |

## Coarse-State Composition

| spectral_set | quiet | outward | mobile | other |
| --- | --- | --- | --- | --- |
| low | 0.2516 | 0.2934 | 0.1132 | 0.3419 |
| high | 0.2679 | 0.2878 | 0.08685 | 0.3575 |

## Outputs

- `Output/3032b/3032b_egrt_node.json`
- `Output/3032b/tables/emission_effect_summary.csv`
- `Output/3032b/tables/emission_effect_by_ob.csv`
- `Output/3032b/tables/residence_runs.csv`
- `Output/3032b/tables/residence_summary.csv`
- `Output/3032b/tables/lag_retention_by_ob.csv`
- `Output/3032b/tables/lag_retention_summary.csv`
- `Output/3032b/tables/two_state_transition_summary.csv`
- `Output/3032b/tables/coarse_state_overlap.csv`
- `Output/3032b/tables/egrt_decision_summary.csv`
- `Output/3032b/figures/emission_effects_high_minus_low.png`
- `Output/3032b/figures/residence_duration_by_set.png`
- `Output/3032b/figures/retention_decay_by_lag.png`
- `Output/3032b/figures/coarse_state_composition.png`
- `Output/3032b/figures/compact_density_axis_scatter.png`

## Interpretation Boundary

3032b separates two claims. The partition can be meaningful as a compact-density organization axis even if it is not a deep metastable basin. Strong residence would justify a more ambitious state-process model. Shallow residence redirects the branch toward null-model auditing or a narrower descriptive claim.
