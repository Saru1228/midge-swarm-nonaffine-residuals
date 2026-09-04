# Node 4135 Manuscript-style Technical Synthesis

## Gate Result

```text
gate_result = pass_4135_manuscript_synthesis_complete_terminal_413x
```

## Main Product

`4135` converts the 4134 figure architecture into manuscript-style
technical writing modules. It closes the 413x synthesis route and does
not open a new mechanism branch.

## Counts

```text
title_candidates = 5
main_claim_rows = 8
evidence_to_claim_rows = 7
section_to_figure_rows = 7
writing_boundary_rows = 7
```

## Evidence-to-Claim Map

| claim_id | main_figure | allowed_strength | supporting_metrics | forbidden_stronger_claim |
| --- | --- | --- | --- | --- |
| C1_LOCAL_NONAFFINE_SURVIVAL | Figure 2 | SUPPORTED_WITH_BOUNDARY | 15/19 any-k survival; 14/19 both-k survival | T1 is universal or causal. |
| C2_SCALE_LAG_ROBUST_SURVIVORS | Figure 2 | SUPPORTED_WITH_BOUNDARY | 14/15 robust among tested survivor observations | Scale/lag robustness holds for all observations. |
| C3_DIFFUSE_TANGENTIAL_DOMINANCE | Figure 3 | SUPPORTED_WITH_BOUNDARY | diffuse 13/14; near-pre 8/14; signed direction consistency 0.526 | A universal edge trigger, sharp precursor, or signed force is identified. |
| C5_NO_SIMPLE_STATE_MOMENT_CLOSURE | Figure 4A | NOT_SUPPORTED | median incremental R2 first=-0.000633, second=-0.000621; positive-ob fractions 0.211/0.158 | Stochastic dynamics or all state dependence are impossible. |
| C6_NO_EVENT_TIMESTAMP_EXCESS | Figure 4B | NOT_SUPPORTED | median event-minus-matched-control A_pre_z=-0.0329; positive-ob fraction=0.421 | Transitions have no special dynamics. |
| C7_OBSERVATION_SPECIFIC_HISTORY_BOUNDARY | Figure 4C | BOUNDARY | 14/19 beat shuffled-history median; 6/19 beat q95; median null gap=0.0341 | A universal memory, hysteresis, or causal history mechanism is proven. |
| C8_PROPAGATION_NOT_CONFIRMATORILY_TESTED | Limitations / remaining open mechanism space | NOT_TESTED | route stopped before confirmatory propagation after the event-locality gate failed | No propagation exists. |

## Source Audit

| role | path | exists | size_bytes |
| --- | --- | --- | --- |
| input | Experiment/run_4135_manuscript_style_technical_synthesis.py | True | 45408 |
| input | Output/4130/decision.json | True | 1914 |
| input | Output/4130/claim_strength_registry.csv | True | 2761 |
| input | Output/4131/decision.json | True | 2527 |
| input | Output/4132/decision.json | True | 1977 |
| input | Output/4133/decision.json | True | 2395 |
| input | Output/4134/decision.json | True | 2704 |
| input | Output/4134/main_figure_manifest.csv | True | 1990 |
| input | Output/4134/panel_metadata.csv | True | 8969 |
| input | Output/4134/figure_caption_drafts.csv | True | 2501 |
| input | Output/4090/primary_metrics.csv | True | 522 |
| input | Output/4100/observation_level_effects.csv | True | 2681 |
| input | Output/4121/observation_level_effects.csv | True | 6385 |
| output | Output/4135/title_candidates.csv | True | 847 |
| output | Output/4135/main_claim_registry.csv | True | 2977 |
| output | Output/4135/evidence_to_claim_map.csv | True | 3095 |
| output | Output/4135/section_to_figure_map.csv | True | 797 |
| output | Output/4135/writing_boundary_checklist.csv | True | 918 |
| output | Output/4135/limitations_table.csv | True | 1310 |
| output | Output/4135/title_candidates.md | True | 1389 |
| output | Output/4135/abstract_skeleton.md | True | 2390 |
| output | Output/4135/results_outline.md | True | 3643 |
| output | Output/4135/discussion_outline.md | True | 2356 |
| output | Output/4135/limitations.md | True | 1579 |
| output | Output/4135/manuscript_story.md | True | 7360 |
| output | Output/4135/source_map.csv | True | 1326 |
| output | Output/4135/decision.json | True | 2413 |

## Next

The 413x synthesis route is complete. The next step should be either:

- paper/report development using the `Output/4135` manuscript modules;
- final visual redesign of the `Output/4134` figure previews;
- or a deliberately named new branch outside 413x.
