# 4134 Main Figure Plan

**Date:** 2026-08-28  
**Node:** `4134_figure_ready_evidence_panels`  
**Purpose:** Convert the completed `4130-4133` evidence and M5 review
into figure-ready evidence panels.

## Gate Result

```text
gate_result = pass_4134_figure_panel_package_ready_for_4135
figure_previews = 5
main_figures = 5
panel_rows = 16
```

## Main Figure Architecture

| figure_id | title | main_question | panel_ids | claim_status | main_claim | must_not_claim |
| --- | --- | --- | --- | --- | --- | --- |
| Figure 1 | Data and T1 Measurement Definition | What are the data, reductions, and frozen T1 observable? | 1A;1B;1C;1D | orientation_only | The analysis operates on 3D trajectories and a frozen local tangential non-affine T1 residual. | The schematic is a physical mechanism or a fitted interaction model. |
| Figure 2 | T1 Survival Across Observations | Does the T1 residual survive local affine subtraction across observations? | 2A;2B;2C | main_allowed_with_boundary | T1 survival is common across observations and robust within the survivor class. | T1 survival is universal across all observations. |
| Figure 3 | Spatial and Timing Structure | What repeated form does the surviving T1 residual take? | 3A;3B;3C | main_allowed_with_boundary | Diffuse tangential activity is the most stable repeated form. | A universal edge trigger, signed force, or sharp precursor has been identified. |
| Figure 4 | Reduction Boundaries | Which simple reductions fail or remain outside the tested route? | 4A;4B;4C | main_allowed_with_boundary | The tested C,dCdt,R moment closure and state-matched event-locality routes are not stably supported; history remains observation-specific. | Stochastic dynamics, transition dynamics, propagation, or history effects do not exist. |
| Figure 5 | Observation Heterogeneity | How do positive and boundary results vary across the 19 observations? | 5A;5B;5C | main_allowed_with_metadata_boundary | The observations form robust-survivor, fragile-boundary, and stable-failure classes that can be mapped descriptively. | Metadata or recording condition causally explains the classes. |

## Figure Preview Files

| figure_file |
| --- |
| Output/4134/figures/4134_figure1_data_t1_definition.png |
| Output/4134/figures/4134_figure2_t1_survival_across_observations.png |
| Output/4134/figures/4134_figure3_spatial_timing_structure.png |
| Output/4134/figures/4134_figure4_reduction_boundaries.png |
| Output/4134/figures/4134_figure5_observation_heterogeneity.png |

## Panel Metadata

| figure_id | panel_id | question | sample_scope | primary_metric_or_content | baseline_or_null | boundary_guard |
| --- | --- | --- | --- | --- | --- | --- |
| Figure 1 | 1A | What data are being reduced? | representative raw snapshot from Ob2; all-19 metadata context | 3D positions from one frame; dataset metadata from raw columns 0 and 4 | none; descriptive data orientation | Do not infer mechanism, interaction, or recording-condition causality from the snapshot. |
| Figure 1 | 1B | What is removed by global/local affine reduction? | definition-level concept panel | global affine / local affine / residual separation | definition schematic, no fitted mechanism | Do not present the schematic as a fitted physical model. |
| Figure 1 | 1C | What is the frozen T1 observable? | definition-level concept panel | T1 frozen definition | definition schematic, no fitted mechanism | Do not rename or redefine the target in 4134. |
| Figure 1 | 1D | How does the event-conditioned time profile look? | 4085 aggregate event-aligned profile; 14 tested observations | median real-minus-null aligned z for all_tangential | 4085 event-aligned null profile | Avoid choosing an example that hides failure observations. |
| Figure 2 | 2A | Does T1 survive local affine subtraction across all observations? | all 19 observations | 408x_T1_effect and local-affine survival flags | local affine residualization and event/non-event comparison | Do not write universal survival or omit stable failures. |
| Figure 2 | 2B | Is the survivor class stable to nearby scale and lag choices? | all 19 observations plus survivor-class robustness | T1 any-k, both-k, scale/lag, diffuse, history flags | nearby k and lag sensitivity within all-19 context | Do not generalize survivor-only robustness to all 19 observations. |
| Figure 2 | 2C | Which observations are robust, fragile, or failures? | all 19 observations | observation_class counts | predefined observation classes from 4133 | Do not treat failure classes as artifacts unless independently verified. |
| Figure 3 | 3A | What spatial/activity form is most stable? | 4131 positive atlas; node-specific denominators | positive support fractions from 4131 | node-specific event/control or survivor-subset gates | Do not write edge/core contrast as a universal trigger. |
| Figure 3 | 3B | Is near-pre timing stable? | 4085 aggregate profiles; 14 tested observations | event-aligned real-minus-null profile | 4085 aggregate event-aligned null | Do not write a sharp universal precursor. |
| Figure 3 | 3C | Is there a universal signed direction law? | 4086/4132 signed boundary classes | signed class counts / boundary status | signed event-type decomposition | Do not write universal low-to-high, high-to-low, or mirror law. |
| Figure 4 | 4A | Does C,dCdt,R provide a stable low-dimensional moment closure? | 4090 grouped OOS moment-closure metrics; 19 observations | median incremental R2 and real-minus-shift metrics | radius-only model and shifted C,dCdt null | Do not write that stochastic dynamics or all state dependence are impossible. |
| Figure 4 | 4B | Do true transition timestamps add state-matched near-pre excess? | 4100 state-matched event-local effects; 19 observations | median delta A_pre_z by observation | same-observation C,dCdt,R-matched non-event frames and shifted events | Do not write that transitions have no special dynamics. |
| Figure 4 | 4C | Does recent history become a universal rule? | 4121 same-current-state different-history effects; 19 observations | real-minus-null median abs history effect and sign | same-current-state matching and within-observation shuffled history | Do not write causal memory, hysteresis, or universal history dependence. |
| Figure 5 | 5A | How does evidence vary across observations and routes? | all 19 observations x route flags | direct observation-level evidence flags | route-specific binary gates | Do not turn route scores into a predictive classifier. |
| Figure 5 | 5B | Are descriptive metadata associations visible? | all 19 observations; descriptive metadata association | 408x_T1_effect vs mean_track_length_frames | small-n descriptive Spearman / leave-one-observation-out audit | Do not write causal metadata or recording-condition explanations. |
| Figure 5 | 5C | Which observations define the strongest positive and failure cases? | all 19 observation classes | observation-class T1-effect distribution and class summary | 4133 observation classes | Do not let examples substitute for the all-19 result. |

## Writing Rule

Each main figure should answer one question. Captions must state the
supported interpretation and the stronger claim that is not supported.
Figure 1 is an orientation/definition figure, not a mechanism figure.
