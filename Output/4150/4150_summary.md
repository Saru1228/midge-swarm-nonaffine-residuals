        # Node 4150 Summary

        ## Purpose

        Convert the 4134 figure package into final publication-facing figures
        without changing the underlying analysis definitions or evidence.

        ## Gate Result

        `pass_4150_final_figure_package_ready_for_reintegration`

        ## Cleanup Performed

        | item | status | evidence |
| --- | --- | --- |
| Figure 1 internal workflow note | pass | Fig1_final removes the old bottom note that mentioned use in 4134. |
| Figure 3 history removal | pass | Fig3_final excludes history bars and leaves recent-history evidence to Figure 4/Figure 5. |
| Figure 4A observation-level redesign | pass | Fig4_final panel A uses held-out observation points from Output/4090/grouped_oos_results.csv. |
| Publication-facing figure names | pass | Final files are named Fig1_final through Fig5_final and copied to mypaper2/Latex/figures. |
| No per-node compilation | pass | No LaTeX compilation was run at 4150; compilation is deferred to 4154. |

        ## Final Figure Files

        | figure | final_stem | cleanup |
| --- | --- | --- |
| Figure 1 | Fig1_final | internal note removed; no analysis-node labels on figure |
| Figure 2 | Fig2_final | final figure naming; internal analysis-node labels absent from axes |
| Figure 3 | Fig3_final | history removed from phenotype panel; signed classes relabeled |
| Figure 4 | Fig4_final | panel A redesigned as observation-level held-out evidence |
| Figure 5 | Fig5_final | node-specific axis label removed; legend wording simplified |

        ## Captions

        | figure | latex_file | caption |
| --- | --- | --- |
| Figure 1 | figures/Fig1_final.pdf | Data and T1 measurement definition. Panel A shows a representative raw three-dimensional snapshot from one observation. Panels B and C define the affine subtraction and the frozen T1 measurement target used in this study. Panel D shows the event-aligned all-tangential profile used to illustrate the measurement pipeline. The figure defines the observable and does not represent a fitted physical mechanism. |
| Figure 2 | figures/Fig2_final.pdf | T1 survival across observations. The all-observation panel retains both survivor and failure observations. T1 survived local affine subtraction in most observations and remained robust to nearby scale/lag choices inside the survivor class, but the class panel shows that the result was not universal. |
| Figure 3 | figures/Fig3_final.pdf | Spatial and timing structure of the T1 residual. Support fractions and event-aligned profiles show that diffuse all-tangential activity was the most stable repeated form. Near-pre timing, edge/core contrast, and signed structure were retained as bounded or secondary patterns. |
| Figure 4 | figures/Fig4_final.pdf | Reduction boundaries. The tested $(C,\dot{C},R)$ first/second moment closure and the state-matched event-local near-pre test did not provide stable reductions of T1. Recent-history separation was visible in some observations but did not become a universal sign/order rule. Propagation remained outside the current confirmatory route. |
| Figure 5 | figures/Fig5_final.pdf | Observation heterogeneity. Route-level evidence and observation classes show robust survivors, fragile boundaries, and stable failures across the 19 observations. The metadata association panel is descriptive and sensitivity-audited, but it is not a causal recording-condition explanation. |

        ## Source Map

        | role | path | exists | size_bytes |
| --- | --- | --- | --- |
| input | Output/4134/figure_source_map.csv | True | 9158 |
| input | Output/4134/main_figure_manifest.csv | True | 1990 |
| input | Output/4134/panel_metadata.csv | True | 8986 |
| input | Output/4131/decision.json | True | 2527 |
| input | Output/4131/positive_phenomenon_atlas.csv | True | 3288 |
| input | Output/4131/observation_positive_coverage_matrix.csv | True | 6550 |
| input | Output/4132/negative_boundary_atlas.csv | True | 5968 |
| input | Output/4133/observation_master_table.csv | True | 23974 |
| input | Output/4085/aggregate_profiles.csv | True | 22768 |
| input | Output/4090/grouped_oos_results.csv | True | 6753 |
| input | Output/4090/primary_metrics.csv | True | 522 |
| input | Output/4100/observation_level_effects.csv | True | 2681 |
| input | Output/4121/observation_level_effects.csv | True | 6385 |
| output_figure | Output/4150/figures/Fig1_final.png | True | 438699 |
| output_figure | Output/4150/figures/Fig1_final.pdf | True | 21052 |
| output_figure | mypaper2/Latex/figures/Fig1_final.png | True | 438699 |
| output_figure | mypaper2/Latex/figures/Fig1_final.pdf | True | 21052 |
| output_figure | Output/4150/figures/Fig2_final.png | True | 195424 |
| output_figure | Output/4150/figures/Fig2_final.pdf | True | 16847 |
| output_figure | mypaper2/Latex/figures/Fig2_final.png | True | 195424 |
| output_figure | mypaper2/Latex/figures/Fig2_final.pdf | True | 16847 |
| output_figure | Output/4150/figures/Fig3_final.png | True | 295978 |
| output_figure | Output/4150/figures/Fig3_final.pdf | True | 17061 |
| output_figure | mypaper2/Latex/figures/Fig3_final.png | True | 295978 |
| output_figure | mypaper2/Latex/figures/Fig3_final.pdf | True | 17061 |
| output_figure | Output/4150/figures/Fig4_final.png | True | 314996 |
| output_figure | Output/4150/figures/Fig4_final.pdf | True | 26298 |
| output_figure | mypaper2/Latex/figures/Fig4_final.png | True | 314996 |
| output_figure | mypaper2/Latex/figures/Fig4_final.pdf | True | 26298 |
| output_figure | Output/4150/figures/Fig5_final.png | True | 349408 |
| output_figure | Output/4150/figures/Fig5_final.pdf | True | 28400 |
| output_figure | mypaper2/Latex/figures/Fig5_final.png | True | 349408 |
| output_figure | mypaper2/Latex/figures/Fig5_final.pdf | True | 28400 |
| output_caption | Output/4150/figure_caption_final.md | True | 2094 |

        ## Next

        Continue to `4151_final_manuscript_reintegration`. No PDF compilation
        was run at 4150, following the deferred-compilation policy.
