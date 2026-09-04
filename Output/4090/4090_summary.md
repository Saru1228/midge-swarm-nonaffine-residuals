# Node 4090 Summary

## Question

Does continuous compact-density state organize the frozen local non-affine T1
residual mainly as first-moment structure or as second-moment fluctuation
structure?

## Why this node exists after 408x

4088 froze a bounded T1 local non-affine tangential residual. 4090A showed an
unconfirmed early-observation proxy boundary but did not find a known raw/event
artifact that explains away T1. 4090B showed that vector-level residual samples
and C,dC are available.

## Frozen Upstream Target

```text
T1 = local tangential non-affine residual
```

## Data Scope

All 19 observations are included.

## Residual Unit Boundary

```text
residual_unit = focal-neighborhood neighbor residual vector
```

This matches the 4081/4088 `all_tangential` aggregate source, but it is not yet
a unique focal-individual residual vector.

## Continuous State Definition

```text
C(t) = density_rms_z3045
dC/dt = gradient(density_rms_smooth3045, t)
```

## Sample

```json
{
  "rows": 213696,
  "observations": 19,
  "median_rows_per_ob": 12736.0,
  "median_condition_number": 2.4631639460434815,
  "median_tan_norm": 159.02546085926912,
  "median_raw_tan_norm": 256.820373740044
}
```

## Baseline And Null

```text
baseline = radius-only binned model
state_model = C,dCdt,radius binned model
null = within-observation circular shift of C,dCdt
validation = leave-one-observation-out by observation
```

## Primary Metrics

| target_family | target | median_incremental_r2 | positive_ob_fraction | median_shift_incremental_r2 | median_real_minus_shift | real_gt_shift_fraction | pass_gate | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| first_moment | signed_tan_projection | -0.00063 | 0.2105 | -0.00022 | -0.00031 | 0.421 | False | no stable grouped OOS support |
| second_moment | log_tan_energy | -0.00062 | 0.1579 | -0.00013 | -0.00066 | 0.3684 | False | no stable grouped OOS support |

## Grouped OOS Results

| heldout_ob | target_family | target | n_train | n_test | mse_radius_baseline | mse_state_model | mse_shifted_state_model | incremental_r2_state_vs_radius | incremental_r2_shift_vs_radius | real_minus_shift_incremental_r2 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | first_moment | signed_tan_projection | 206656 | 7040 | 2.763e+04 | 2.766e+04 | 2.763e+04 | -0.00104 | 4e-05 | -0.00108 |
| 1 | second_moment | log_tan_energy | 206656 | 7040 | 2.098 | 2.101 | 2.099 | -0.00151 | -0.0002 | -0.00131 |
| 2 | first_moment | signed_tan_projection | 204160 | 9536 | 2.212e+04 | 2.211e+04 | 2.214e+04 | 0.00026 | -0.0008 | 0.00106 |
| 2 | second_moment | log_tan_energy | 204160 | 9536 | 2.102 | 2.102 | 2.102 | 0.00015 | -0.00021 | 0.00036 |
| 3 | first_moment | signed_tan_projection | 204096 | 9600 | 1.828e+04 | 1.829e+04 | 1.828e+04 | -0.00081 | 3e-05 | -0.00084 |
| 3 | second_moment | log_tan_energy | 204096 | 9600 | 1.955 | 1.957 | 1.952 | -0.001 | 0.00152 | -0.00252 |
| 4 | first_moment | signed_tan_projection | 204096 | 9600 | 1.493e+04 | 1.494e+04 | 1.495e+04 | -0.00063 | -0.00112 | 0.00049 |
| 4 | second_moment | log_tan_energy | 204096 | 9600 | 2.016 | 2.017 | 2.017 | -0.00075 | -0.00087 | 0.00011 |
| 5 | first_moment | signed_tan_projection | 204096 | 9600 | 1.477e+04 | 1.479e+04 | 1.476e+04 | -0.00095 | 0.00052 | -0.00147 |
| 5 | second_moment | log_tan_energy | 204096 | 9600 | 2.168 | 2.167 | 2.164 | 0.00026 | 0.0017 | -0.00144 |
| 6 | first_moment | signed_tan_projection | 200960 | 12736 | 1.474e+04 | 1.475e+04 | 1.475e+04 | -0.00026 | -0.0005 | 0.00024 |
| 6 | second_moment | log_tan_energy | 200960 | 12736 | 2.132 | 2.132 | 2.132 | -0.00014 | -0.00022 | 8e-05 |
| 7 | first_moment | signed_tan_projection | 207360 | 6336 | 2.234e+04 | 2.236e+04 | 2.234e+04 | -0.00082 | -0.00015 | -0.00067 |
| 7 | second_moment | log_tan_energy | 207360 | 6336 | 1.935 | 1.937 | 1.935 | -0.00083 | 2e-05 | -0.00085 |
| 8 | first_moment | signed_tan_projection | 201536 | 12160 | 1.642e+04 | 1.645e+04 | 1.643e+04 | -0.00153 | -0.00064 | -0.00089 |
| 8 | second_moment | log_tan_energy | 201536 | 12160 | 2.041 | 2.045 | 2.044 | -0.00193 | -0.0011 | -0.00083 |
| 9 | first_moment | signed_tan_projection | 207360 | 6336 | 2.409e+04 | 2.409e+04 | 2.41e+04 | 4e-05 | -0.00022 | 0.00026 |
| 9 | second_moment | log_tan_energy | 207360 | 6336 | 2.044 | 2.045 | 2.045 | -0.00046 | -0.00052 | 6e-05 |
| 10 | first_moment | signed_tan_projection | 204160 | 9536 | 2.361e+04 | 2.362e+04 | 2.362e+04 | -0.00042 | -0.0005 | 9e-05 |
| 10 | second_moment | log_tan_energy | 204160 | 9536 | 2.02 | 2.021 | 2.021 | -0.00025 | -8e-05 | -0.00017 |
| 11 | first_moment | signed_tan_projection | 200960 | 12736 | 1.542e+04 | 1.542e+04 | 1.541e+04 | -0.00049 | 0.00062 | -0.00111 |
| 11 | second_moment | log_tan_energy | 200960 | 12736 | 2.067 | 2.068 | 2.065 | -0.00031 | 0.00105 | -0.00135 |
| 12 | first_moment | signed_tan_projection | 200960 | 12736 | 2.503e+04 | 2.504e+04 | 2.503e+04 | -0.00066 | -0.00035 | -0.00031 |
| 12 | second_moment | log_tan_energy | 200960 | 12736 | 1.958 | 1.961 | 1.958 | -0.00147 | -7e-05 | -0.00139 |
| 13 | first_moment | signed_tan_projection | 200896 | 12800 | 2.211e+04 | 2.21e+04 | 2.211e+04 | 0.00059 | 3e-05 | 0.00056 |
| 13 | second_moment | log_tan_energy | 200896 | 12800 | 1.939 | 1.939 | 1.938 | -5e-05 | 0.00061 | -0.00066 |
| 14 | first_moment | signed_tan_projection | 200896 | 12800 | 2.21e+04 | 2.211e+04 | 2.211e+04 | -0.00066 | -0.00058 | -8e-05 |
| 14 | second_moment | log_tan_energy | 200896 | 12800 | 1.957 | 1.959 | 1.96 | -0.00102 | -0.0014 | 0.00038 |
| 15 | first_moment | signed_tan_projection | 200960 | 12736 | 1.994e+04 | 1.995e+04 | 1.996e+04 | -0.00012 | -0.00065 | 0.00053 |
| 15 | second_moment | log_tan_energy | 200960 | 12736 | 1.963 | 1.963 | 1.964 | 6e-05 | -0.00013 | 0.00019 |
| 16 | first_moment | signed_tan_projection | 200960 | 12736 | 1.972e+04 | 1.974e+04 | 1.972e+04 | -0.00091 | 5e-05 | -0.00097 |
| 16 | second_moment | log_tan_energy | 200960 | 12736 | 1.955 | 1.956 | 1.955 | -0.00062 | -0.00011 | -0.00051 |
| 17 | first_moment | signed_tan_projection | 200960 | 12736 | 2.344e+04 | 2.344e+04 | 2.348e+04 | 4e-05 | -0.0017 | 0.00173 |
| 17 | second_moment | log_tan_energy | 200960 | 12736 | 1.981 | 1.982 | 1.987 | -0.00038 | -0.00292 | 0.00253 |
| 18 | first_moment | signed_tan_projection | 200896 | 12800 | 2.555e+04 | 2.557e+04 | 2.556e+04 | -0.0008 | -0.00012 | -0.00068 |
| 18 | second_moment | log_tan_energy | 200896 | 12800 | 2.043 | 2.045 | 2.044 | -0.00112 | -0.00038 | -0.00074 |
| 19 | first_moment | signed_tan_projection | 194560 | 19136 | 2.766e+04 | 2.767e+04 | 2.766e+04 | -4e-05 | 0.00027 | -0.00031 |
| 19 | second_moment | log_tan_energy | 194560 | 19136 | 2.061 | 2.062 | 2.059 | -0.00092 | 0.0006 | -0.00152 |

## Dataset-level High-C Effects

| ob | dataset | n | signed_highC_minus_lowC | log_energy_highC_minus_lowC | energy_highC_minus_lowC | coherence_highC_minus_lowC | median_C | q25_C | q75_C |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ob1.txt | 7040 | -10.76 | -0.06792 | -5473 | -0.00252 | -0.00411 | -0.5806 | 0.6123 |
| 2 | Ob2.txt | 9536 | 6.966 | 0.0424 | 3322 | 0.00504 | 0.00512 | -0.6024 | 0.7712 |
| 3 | Ob3.txt | 9600 | 6.383 | 0.04604 | 3269 | 0.0008 | 0.04293 | -0.685 | 0.8833 |
| 4 | Ob4.txt | 9600 | 8.226 | 0.1318 | 3770 | 0.01092 | 0.04344 | -0.5592 | 0.7216 |
| 5 | Ob5.txt | 9600 | -0.6599 | 0.00888 | -266 | 0.01783 | -0.1329 | -0.7477 | 0.7927 |
| 6 | Ob6.txt | 12736 | 10.5 | 0.1199 | 2324 | 0.00272 | -0.02471 | -0.5745 | 0.5912 |
| 7 | Ob7.txt | 6336 | 1.517 | -0.02922 | 1056 | 0.00028 | -0.05896 | -0.59 | 0.9264 |
| 8 | Ob8.txt | 12160 | -1.984 | -0.1084 | -2485 | 0.01957 | -0.07126 | -0.582 | 0.8938 |
| 9 | Ob9.txt | 6336 | -1.174 | 0.08339 | 3366 | -0.01363 | -0.08834 | -0.8694 | 0.6899 |
| 10 | Ob10.txt | 9536 | 6.07 | 0.1125 | 4587 | 0.01353 | -0.1834 | -0.6097 | 0.8524 |
| 11 | Ob11.txt | 12736 | 7.126 | 0.00752 | 134.3 | -0.0126 | -0.03064 | -0.5608 | 0.664 |
| 12 | Ob12.txt | 12736 | -4.624 | -0.06712 | -4462 | 0.00953 | -0.03096 | -0.7085 | 0.8424 |
| 13 | Ob13.txt | 12800 | 11.12 | 0.08715 | 5813 | -0.00474 | 0.05456 | -0.7651 | 0.6533 |
| 14 | Ob14.txt | 12800 | 1.771 | 0.01128 | 1489 | 0.00017 | 0.04512 | -0.5712 | 0.6806 |
| 15 | Ob15.txt | 12736 | 7.255 | 0.1452 | 6034 | 0.02004 | -0.0035 | -0.5108 | 0.7191 |
| 16 | Ob16.txt | 12736 | 7.588 | 0.05872 | 1588 | -0.00076 | -0.0605 | -0.6373 | 0.563 |
| 17 | Ob17.txt | 12736 | -2.623 | -0.02808 | -1454 | -0.00195 | 0.01346 | -0.5143 | 0.6958 |
| 18 | Ob18.txt | 12800 | 7.023 | 0.03858 | 4776 | -0.00284 | 0.02509 | -0.5847 | 0.8146 |
| 19 | Ob19.txt | 19136 | 5.075 | 0.01844 | 1282 | 0.01505 | 0.09497 | -0.528 | 0.7993 |

## Gate Evaluation

```text
gate_result = transition_linked_but_not_lowdimensional_state_conditioned
```

Neither signed first moment nor second moment shows stable grouped OOS improvement over radius-only baseline with shifted-state separation. This routes away from low-dimensional stochastic closure.

## What This Supports

- It supports the route decision encoded in `gate_result`.
- It keeps all 19 observations as the primary scope.
- It keeps the early-observation boundary as a stratification issue, not a
  deletion rule.

## What This Rules Out

If a moment family does not pass, 4090 rules out treating that family as a
stable low-dimensional C,dC-conditioned explanation under the current sampling
and binning definition.

## What This Does NOT Prove

| does_not_prove |
| --- |
| biological force law |
| multiplicative Langevin mechanism |
| causal precursor |
| unique focal-individual residual vector |

## Decision

`transition_linked_but_not_lowdimensional_state_conditioned`

## Next Node

| next |
| --- |
| 4094_bounded_stochastic_negative_synthesis |
| consider_410x_transient_event_local_route |

## Artifacts

- `Output/4090/vector_moment_samples.csv.gz`
- `Output/4090/grouped_oos_results.csv`
- `Output/4090/primary_metrics.csv`
- `Output/4090/dataset_level_effects.csv`
- `Output/4090/state_bin_profiles.csv`
- `Output/4090/null_results.csv`
- `Output/4090/figures/4090_oos_by_observation.png`
- `Output/4090/figures/4090_dataset_highC_effects.png`
- `Output/4090/figures/4090_state_profile_heatmaps.png`
