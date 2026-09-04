# Node 4134 Figure-ready Evidence Panels

## Question

If this project is now written as a paper or technical report, which
figures are needed to tell the bounded evidence story without
overclaiming?

## Gate Result

```text
gate_result = pass_4134_figure_panel_package_ready_for_4135
```

## Main Interpretation

The figure package is ready for `4135` manuscript-style synthesis.
The generated panels are not a new experiment; they are a structured
conversion of existing 4130-4133 evidence into a figure-ready
architecture. The package keeps the main result bounded: T1 is common
and reproducible in most observations, while several simple reductions
fail or remain explicitly outside the tested route.

## Main Figure Manifest

| figure_id | title | main_question | preview_artifact | claim_status | must_not_claim |
| --- | --- | --- | --- | --- | --- |
| Figure 1 | Data and T1 Measurement Definition | What are the data, reductions, and frozen T1 observable? | Output/4134/figures/4134_figure1_data_t1_definition.png | orientation_only | The schematic is a physical mechanism or a fitted interaction model. |
| Figure 2 | T1 Survival Across Observations | Does the T1 residual survive local affine subtraction across observations? | Output/4134/figures/4134_figure2_t1_survival_across_observations.png | main_allowed_with_boundary | T1 survival is universal across all observations. |
| Figure 3 | Spatial and Timing Structure | What repeated form does the surviving T1 residual take? | Output/4134/figures/4134_figure3_spatial_timing_structure.png | main_allowed_with_boundary | A universal edge trigger, signed force, or sharp precursor has been identified. |
| Figure 4 | Reduction Boundaries | Which simple reductions fail or remain outside the tested route? | Output/4134/figures/4134_figure4_reduction_boundaries.png | main_allowed_with_boundary | Stochastic dynamics, transition dynamics, propagation, or history effects do not exist. |
| Figure 5 | Observation Heterogeneity | How do positive and boundary results vary across the 19 observations? | Output/4134/figures/4134_figure5_observation_heterogeneity.png | main_allowed_with_metadata_boundary | Metadata or recording condition causally explains the classes. |

## Panel Count By Figure

| figure_id | n_panels |
| --- | --- |
| Figure 1 | 4 |
| Figure 2 | 3 |
| Figure 3 | 3 |
| Figure 4 | 3 |
| Figure 5 | 3 |

## Source Audit

| role | path | exists | size_bytes |
| --- | --- | --- | --- |
| input | Experiment/run_4134_figure_ready_evidence_panels.py | True | 57494 |
| input | Output/4133_M5_review_before_4134/decision.json | True | 2405 |
| input | Output/4133_M5_review_before_4134/main_vs_supplement_figure_candidates.csv | True | 5673 |
| input | Output/4133_M5_review_before_4134/claim_storyline_review.csv | True | 3113 |
| input | Output/4130/definition_dictionary.csv | True | 3329 |
| input | Output/4130/claim_strength_registry.csv | True | 2761 |
| input | Output/4131/positive_phenomenon_atlas.csv | True | 3288 |
| input | Output/4131/observation_positive_coverage_matrix.csv | True | 6550 |
| input | Output/4132/negative_boundary_atlas.csv | True | 5968 |
| input | Output/4133/observation_master_table.csv | True | 23974 |
| input | Output/4133/observation_classes.csv | True | 3478 |
| input | Output/4085/aggregate_profiles.csv | True | 22768 |
| input | Output/4090/primary_metrics.csv | True | 522 |
| input | Output/4100/observation_level_effects.csv | True | 2681 |
| input | Output/4121/observation_level_effects.csv | True | 6385 |
| input_raw_snapshot_source | data/raw\Ob2.txt | True | 79022088 |

## What This Does Not Prove

| does_not_prove |
| --- |
| camera-ready publication graphics |
| a new mechanism |
| causal metadata explanation |
| propagation absence |
| universal history mechanism |
| universal T1 survival |

## Next Node

`4135_manuscript_style_technical_synthesis`

## Artifacts

- `Output/4134/figure_source_map.csv`
- `Output/4134/panel_metadata.csv`
- `Output/4134/main_figure_manifest.csv`
- `Output/4134/main_figure_plan.md`
- `Output/4134/supplementary_figure_plan.md`
- `Output/4134/figure_caption_drafts.md`
- `Output/4134/figures/4134_figure1_data_t1_definition.png`
- `Output/4134/figures/4134_figure2_t1_survival_across_observations.png`
- `Output/4134/figures/4134_figure3_spatial_timing_structure.png`
- `Output/4134/figures/4134_figure4_reduction_boundaries.png`
- `Output/4134/figures/4134_figure5_observation_heterogeneity.png`
