# 4147 spectral_set Publication Provenance

Node: `4147_spectral_set_publication_provenance`  
Date: 2026-09-02

## Result

`pass_4147_spectral_set_publication_provenance_ready`

The low/high `spectral_set` labels used by the manuscript are reconstructable
from upstream macroscopic variables and are not fitted from T1.

## Provenance Chain

```text
3001 geometric center observables
  -> 3032 transfer-operator spectral partition
  -> 3032b frame_spectral_labels.csv
  -> 3041/3041b propagated frame macrostate table
  -> 3045 transition_events.csv
  -> 4081/4084/414x local-affine T1 analyses
```

## Selected Partition

| spectral_set | n_cells | stationary_mass_sum | pooled_retention | retention_lift | exit_probability |
| --- | --- | --- | --- | --- | --- |
| low | 32 | 0.5003 | 0.8753 | 0.375 | 0.1247 |
| high | 28 | 0.4997 | 0.8752 | 0.3754 | 0.1248 |

## Label and Event Counts

| source_id | label_column | n_rows | n_observations | n_low | n_high | n_unavailable_or_other |
| --- | --- | --- | --- | --- | --- | --- |
| 3032b_frame_spectral_labels | spectral_set | 334542 | 19 | 167210 | 167332 | 0 |
| 3041b_frame_macrostate_candidates | spectral_set | 334568 | 19 | 167210 | 167332 | 26 |
| 3041b_compact_density_2 | compact_density_2 | 334568 | 19 | 167210 | 167332 | 26 |
| 3045_transition_events | event_type | 1471 | 19 | 750 | 721 | 0 |

Transition-event counts:

```text
{"high_to_low": 750, "low_to_high": 721}
```

## Propagation Checks

| check_id | metric | value | pass | notes |
| --- | --- | --- | --- | --- |
| 3032b_to_3041b_spectral_set_match | fraction_equal | 1 | True | Frame-level spectral_set labels are preserved into 3041b. |
| 3032b_to_3041b_compact_density_2_match | fraction_equal | 1 | True | compact_density_2 is a copy of spectral_set for low/high frames. |
| 3045_transition_state_labels | all_from_to_low_high_and_switch | 1 | True | Transition events switch between low and high. |
| 3045_transition_persistence_filter | all_prev_next_duration_ge_0p20s | 1 | True | Both adjacent state runs satisfy the 0.20 s persistence screen. |

## T1 Independence Scan

| script | stage | n_t1_term_hits | hit_terms | t1_independence_pass_for_label_construction |
| --- | --- | --- | --- | --- |
| Experiment/run_3032_transfer_operator_metastability.py | label_construction | 0 |  | True |
| Experiment/run_3032b_state_meaning_residence_audit.py | label_materialization | 0 |  | True |
| Experiment/run_3041_anisotropic_layer_residence.py | label_propagation | 0 |  | True |
| Experiment/run_3041b_coarse_graining_closure_audit.py | label_propagation | 0 |  | True |
| Experiment/run_3045_residual_event_trigger_search.py | event_detection_and_downstream_residual_search | 0 |  | True |

## Source Code Map

| stage | role | script | line | artifact |
| --- | --- | --- | --- | --- |
| 3032_input | macroscopic input table | Experiment/run_3032_transfer_operator_metastability.py | 30 | Output/3032/3032_egrt_node.json |
| 3032_variables | slow variables | Experiment/run_3032_transfer_operator_metastability.py | 38 | Output/3032/tables/egrt_decision_summary.csv |
| 3032_discretization | quantile Ulam cells | Experiment/run_3032_transfer_operator_metastability.py | 221 | Output/3032/tables/ulam_bin_edges.json |
| 3032_transfer_operator | empirical lagged transition matrix | Experiment/run_3032_transfer_operator_metastability.py | 266 | Output/3032/tables/spectral_partition_summary.csv |
| 3032_spectral_partition | eigenvector split into low/high sets | Experiment/run_3032_transfer_operator_metastability.py | 371 | Output/3032/tables/spectral_cell_mapping.csv |
| 3032_best_partition | selected partition | Experiment/run_3032_transfer_operator_metastability.py | 1023 | Output/3032/tables/egrt_decision_summary.csv |
| 3032b_materialization | frame-level spectral labels | Experiment/run_3032b_state_meaning_residence_audit.py | 772 | Output/3032b/processed/frame_spectral_labels.csv |
| 3041_propagation | attach labels to layer metrics | Experiment/run_3041_anisotropic_layer_residence.py | 32 | Output/3041/processed/frame_layer_metrics.csv |
| 3041b_propagation | propagate compact_density_2 | Experiment/run_3041b_coarse_graining_closure_audit.py | 196 | Output/3041b/processed/frame_macrostate_candidates.csv |
| 3045_event_detection | detect low/high run switches | Experiment/run_3045_residual_event_trigger_search.py | 212 | Output/3045/tables/transition_events.csv |

## Interpretation Table

| spectral_set | n_frames | occupancy_fraction | median_r_rms_z | median_density_rms_z | median_anisotropy_z |
| --- | --- | --- | --- | --- | --- |
| high | 167332 | 0.5002 | -0.6531 | 0.7263 | -0.1241 |
| low | 167210 | 0.4998 | 0.6749 | -0.6148 | 0.1429 |

## Boundary

This audit supports provenance and non-circularity of the compact-density
labels. It does not prove that the two-state spectral partition is the only or
best biological state representation. In the manuscript it should be described
as an inherited compact-density coarse graining used to define events.
