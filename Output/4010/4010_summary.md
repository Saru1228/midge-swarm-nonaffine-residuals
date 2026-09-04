# 4010 Empirical Residual Cumulant Audit

## Scope

4010 translates the Boltzmann molecule/cumulant reference into an empirical
fish-school test. It asks whether affine-residual velocity correlations survive
a one-fish conditional baseline.

Plain-language question:

> If we preserve what individual fish residual velocities look like in each
> radial shell of each frame, do real neighboring fish still show extra
> transition-linked correlation?

## EGRT Node

| field | value |
| --- | --- |
| node_id | 4010_empirical_residual_cumulant_audit |
| parent | 4004_boltzmann_molecule_cumulant_reframe |
| node_type | cumulant / factorization audit |
| decision | weak_empirical_residual_cumulant_signal |
| recommended next node | pause 4010 cumulant route |
| boundary reading | No observed or empirical-cumulant pair variable survives shifted-event null gates. |

## Methods

- Per frame, fit the affine geometric baseline and compute residual velocities.
- Build an undirected kNN spatial graph with `k=6`.
- Split fish into `3` radial shells within each frame.
- For each local pair metric, compute:
  - observed kNN pair statistic;
  - expected value under shell-conditioned one-fish independence;
  - empirical cumulant = observed - expected.
- Slow-trend remove metrics within each observation.
- Compare transition post-minus-pre direction contrasts against `160`
  shifted-event null replicates.

## Decision Metrics

| node_id | node_type | n_surviving_variables | n_empirical_cumulant_survivors | n_observed_pair_survivors | n_one_fish_baseline_survivors | empirical_cumulant_surviving_variables | observed_pair_surviving_variables | one_fish_baseline_surviving_variables | eg_rt_decision | recommended_next_node | boundary_reading |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4010_empirical_residual_cumulant_audit | cumulant / factorization audit | 0 | 0 | 0 | 0 |  |  |  | weak_empirical_residual_cumulant_signal | pause 4010 cumulant route | No observed or empirical-cumulant pair variable survives shifted-event null gates. |

## Surviving Variables

_No rows._

## Full Direction Null Comparison

| variable | family | n_ob | n_events | real_median_low_to_high_delta_z | real_median_high_to_low_delta_z | real_median_direction_contrast_z | real_abs_median_direction_contrast_z | direction_contrast_sign_consistency | null_abs_median_direction_contrast_z | real_minus_null_abs_direction_contrast_z | p_null_abs_direction_ge_real | direction_survives_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| knn_resid_alignment_observed | observed_pair | 19 | 1471 | -0.1145 | 0.01874 | -0.09928 | 0.09928 | 0.6316 | 0.0638 | 0.03548 | 0.2981 | False |
| knn_resid_radial_cov_expected | one_fish_conditional_baseline | 19 | 1471 | -0.04699 | 0.1416 | -0.05803 | 0.05803 | 0.6316 | 0.05492 | 0.003115 | 0.472 | False |
| knn_resid_speed_cov_expected | one_fish_conditional_baseline | 19 | 1471 | -0.04699 | 0.1416 | -0.05803 | 0.05803 | 0.6316 | 0.05492 | 0.003115 | 0.472 | False |
| knn_resid_tangential_cov_expected | one_fish_conditional_baseline | 19 | 1471 | -0.04699 | 0.1416 | -0.05803 | 0.05803 | 0.6316 | 0.05492 | 0.003115 | 0.472 | False |
| knn_resid_radial_cov_cumulant | empirical_cumulant | 19 | 1471 | -0.03955 | -0.08582 | 0.04295 | 0.04295 | 0.5789 | 0.06532 | -0.02237 | 0.6398 | False |
| knn_resid_tangential_cov_observed | observed_pair | 19 | 1471 | 0.03399 | -0.002611 | -0.03505 | 0.03505 | 0.5263 | 0.05844 | -0.02339 | 0.6832 | False |
| knn_resid_speed_cov_cumulant | empirical_cumulant | 19 | 1471 | 0.06756 | 0.07854 | 0.02696 | 0.02696 | 0.5263 | 0.05699 | -0.03004 | 0.7205 | False |
| knn_resid_radial_cov_observed | observed_pair | 19 | 1471 | -0.05542 | -0.05414 | 0.02651 | 0.02651 | 0.5263 | 0.05768 | -0.03117 | 0.7826 | False |
| knn_resid_alignment_expected | one_fish_conditional_baseline | 19 | 1471 | -0.1406 | -0.007021 | 0.007547 | 0.007547 | 0.5263 | 0.05614 | -0.04859 | 0.9379 | False |
| knn_resid_speed_cov_observed | observed_pair | 19 | 1471 | 0.04229 | 0.1178 | -0.006388 | 0.006388 | 0.5789 | 0.05648 | -0.05009 | 0.9255 | False |
| knn_resid_alignment_cumulant | empirical_cumulant | 19 | 1471 | -0.03758 | 0.0175 | -0.004781 | 0.004781 | 0.5789 | 0.05937 | -0.05459 | 0.9503 | False |
| knn_resid_tangential_cov_cumulant | empirical_cumulant | 19 | 1471 | 0.02454 | -0.02148 | -0.004497 | 0.004497 | 0.5263 | 0.06084 | -0.05635 | 0.9752 | False |

## Interpretation

If empirical cumulants survive, the transition-linked residual signal is not
just a one-fish shell-distribution effect. This supports moving toward
interaction-history graph tests. If observed pair statistics survive but
cumulants do not, the molecule-graph route should pause.

## Outputs

- `Output/4010/4010_egrt_node.json`
- `Output/4010/tables/empirical_cumulant_direction_null_comparison.csv`
- `Output/4010/tables/egrt_decision_summary.csv`
- `Output/4010/figures/empirical_cumulant_direction_screen.png`
- `Output/4010/figures/empirical_cumulant_aligned_profiles.png`
