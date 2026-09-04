# 4140 spectral_set Provenance

## Summary

The current manuscript's low/high transition events are inherited labels, not
new labels fitted from T1. The chain is:

```text
3032 transfer-operator spectral partition
  -> 3032b frame_spectral_labels.csv
  -> 3041 frame_layer_metrics.csv
  -> 3041b frame_macrostate_candidates.csv
  -> 3045 transition_events.csv
```

## Source Node

- Source node: `3032_transfer_operator_metastability`
- Source script: `Experiment/run_3032_transfer_operator_metastability.py:371`
- Best partition from 3032 decision: `eig2`
- Candidate variables recorded in 3032 decision: `r_rms, density_rms, anisotropy`
- Mapping file: `Output/3032/tables/spectral_cell_mapping.csv`
- Bin-edge file: `Output/3032/tables/ulam_bin_edges.json`

## Label Materialization

- Materialization script: `Experiment/run_3032b_state_meaning_residence_audit.py:772`
- Frame label file: `Output/3032b/processed/frame_spectral_labels.csv`
- Label observations: `19`
- Label counts: `{"high": 167332, "low": 167210}`
- Available mapping partitions: `eig2, eig3, eig4, eig5`

## Downstream Consumption

- 3041 reads labels from `Output/3032b/processed/frame_spectral_labels.csv` using `Experiment/run_3041_anisotropic_layer_residence.py:32`.
- 3041b propagates `spectral_set` into `Output/3041b/processed/frame_macrostate_candidates.csv`.
- 3045 reads `Output/3041b/processed/frame_macrostate_candidates.csv` and detects low/high switches using `Experiment/run_3045_residual_event_trigger_search.py:212`.
- 3045 transition events: `Output/3045/tables/transition_events.csv`
- 3045 event counts: `{"high_to_low": 750, "low_to_high": 721}`

## Independence From T1

The `spectral_set` construction is upstream of the 4081/4081c local-affine T1
observable. The provenance chain uses slow macroscopic variables and transfer
operator partitioning before the T1 residual family is introduced. This
supports treating transition labels as inherited state labels, not as labels
optimized on T1 survival.

## Current Limitation

The manuscript now states the inherited-label logic, but a reader still needs a
supplement-style method to reconstruct the full 3032/3032b spectral partition
without reading old experiment scripts. This should be handled in 4144.
