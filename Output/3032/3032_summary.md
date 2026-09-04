# 3032 EGRT Transfer-Operator Metastability

## Scope

3032 follows the 3030 screen decision. Since deterministic-attractor evidence was weak while slow shape-density variables retained recurrence structure above surrogates, this node tests a weaker and more interpretable claim: the slow-variable state space may contain almost-invariant macroscopic sets.

## EGRT Node

| field | value |
| --- | --- |
| node_id | 3032_transfer_operator_metastability |
| parent | 3030_attractor_evidence_screen |
| node_type | mechanism |
| competing interpretations | stochastic/metastable macroscopic organization; coarse discretization artifact; Ob-specific persistence |
| decision | support_stochastic_metastability_branch |
| recommended next node | 3032b state-meaning and residence audit |
| boundary reading | Almost-invariant slow-variable sets are reproducible enough to extend, but this supports stochastic macroscopic organization rather than deterministic center-speed attractor geometry. |

## Inputs

- Raw macroscopic observables: `Output/3001/processed/geometric_center_observables_all.csv`
- 3030 routing decision: `Output/3030/tables/egrt_decision_summary.csv`
- 3030 variable evidence: `Output/3030/tables/variable_evidence_summary.csv`

## Methods

- Candidate variables inherited from 3030: `r_rms, density_rms, anisotropy`.
- Each variable is robust-standardized within Ob before pooling.
- The standardized slow-variable space is discretized into 4 quantile bins per variable, giving up to 64 Ulam cells.
- A pooled empirical transition operator is estimated at lag 0.1s.
- Dominant right-eigenvectors define binary spectral partitions.
- A partition passes only when one-lag retention is high, exceeds its occupancy baseline, and remains consistent across Ob.
- The best partition is compared with the 3013 quiet/outward/mobile/other classifier only as an interpretive coordinate.

## Decision Metrics

| node_id | candidate_variables | lag_sec | n_bins | n_total_cells | n_active_cells | active_coverage | top_nontrivial_eigenvalue_real | top_nontrivial_implied_timescale_sec | best_partition_id | best_partition_eigen_rank | best_partition_min_pooled_retention | best_partition_min_retention_lift | best_partition_q25_ob_retention | best_partition_frac_ob_set_lift_positive | best_partition_median_residence_sec | pass_gate | pooled_only_boundary | eg_rt_decision | recommended_next_node | boundary_reading | spectrum_top5_real |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3032_transfer_operator_metastability | r_rms, density_rms, anisotropy | 0.1 | 4 | 64 | 60 | 1 | 0.8564 | 0.6452 | eig2 | 2 | 0.8752 | 0.375 | 0.8698 | 1 | 0.13 | True | False | support_stochastic_metastability_branch | 3032b state-meaning and residence audit | Almost-invariant slow-variable sets are reproducible enough to extend, but this supports stochastic macroscopic organization rather than deterministic center-speed attractor geometry. | 1, 0.8564, 0.7981, 0.6957, 0.6573 |

## Top Spectral Partitions

| partition_id | eigen_rank | eigenvalue_real | implied_timescale_sec | min_pooled_retention | min_retention_lift | q25_ob_retention | frac_ob_set_lift_positive | median_residence_sec | interpretive_axis |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eig2 | 2 | 0.8564 | 0.6452 | 0.8752 | 0.375 | 0.8698 | 1 | 0.13 | high set higher density_rms (delta_z=1.5); high set lower r_rms (delta_z=-1.4); high set lower anisotropy (delta_z=-0.248) |
| eig3 | 3 | 0.7981 | 0.4435 | 0.8438 | 0.3437 | 0.8224 | 1 | 0.15 | high set higher anisotropy (delta_z=1.49); high set lower density_rms (delta_z=-0.243); high set higher r_rms (delta_z=0.181) |
| eig5 | 5 | 0.6573 | 0.2384 | 0.8039 | 0.3032 | 0.78 | 1 | 0.12 | high set higher anisotropy (delta_z=0.099); high set higher density_rms (delta_z=0.0642); high set lower r_rms (delta_z=-0.0625) |
| eig4 | 4 | 0.6957 | 0.2756 | 0.7657 | 0.265 | 0.7461 | 1 | 0.11 | high set higher anisotropy (delta_z=0.0465); high set higher r_rms (delta_z=0.0366); high set higher density_rms (delta_z=0.00895) |

## Best Partition Meaning

| spectral_set | n_frames | occupancy_fraction | median_center_speed | median_frac_outward | median_radial_velocity_mean | median_r_rms | median_r_rms_z | median_density_rms | median_density_rms_z | median_anisotropy | median_anisotropy_z |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| high | 167332 | 0.5002 | 57.85 | 0.5 | -0.1591 | 182.3 | -0.6531 | 1.324e-06 | 0.7263 | 2.591 | -0.1241 |
| low | 167210 | 0.4998 | 59.47 | 0.5 | 0.7019 | 205.7 | 0.6749 | 9.311e-07 | -0.6148 | 2.834 | 0.1429 |

## Coarse-State Overlap

| partition_id | n_frames | normalized_mutual_information | cramers_v | coarse_state_source |
| --- | --- | --- | --- | --- |
| eig2 | 334542 | 0.001152 | 0.04678 | 3013 classifier |

## Coarse-State Composition

| spectral_set | quiet | outward | mobile | other |
| --- | --- | --- | --- | --- |
| low | 0.2516 | 0.2934 | 0.1132 | 0.3419 |
| high | 0.2679 | 0.2878 | 0.08685 | 0.3575 |

## Outputs

- `Output/3032/3032_egrt_node.json`
- `Output/3032/tables/ulam_state_summary.csv`
- `Output/3032/tables/eigenvalue_spectrum.csv`
- `Output/3032/tables/spectral_partition_summary.csv`
- `Output/3032/tables/spectral_cell_mapping.csv`
- `Output/3032/tables/partition_retention_by_ob.csv`
- `Output/3032/tables/partition_residence_runs.csv`
- `Output/3032/tables/best_partition_interpretation.csv`
- `Output/3032/tables/coarse_state_overlap.csv`
- `Output/3032/tables/egrt_decision_summary.csv`
- `Output/3032/figures/transfer_operator_eigenvalue_spectrum.png`
- `Output/3032/figures/spectral_partition_pooled_retention.png`
- `Output/3032/figures/best_partition_retention_by_ob.png`
- `Output/3032/figures/best_partition_slow_state_scatter.png`
- `Output/3032/figures/best_partition_variable_profile.png`

## Interpretation Boundary

This node does not prove deterministic chaos. A positive gate means that the selected slow variables support a stochastic/metastable attractor-like reading: probability mass tends to remain inside a small number of macroscopic organization sets over the tested lag. It should not be written as a low-dimensional deterministic attractor unless later nodes add stronger geometric or predictive evidence.
