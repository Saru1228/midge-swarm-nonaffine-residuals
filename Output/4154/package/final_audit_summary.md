        # Node 4153 Summary

        ## Purpose

        Audit the active manuscript and technical supplement for number,
        claim, terminology, causal-language, figure-text, and reference
        consistency.

        ## Gate Result

        `pass_4153_final_consistency_audit_clean`

        ```text
        active_tex_files = 21
        supplement_files = 9
        stop_items = 0
        fix_required_items = 0
        review_items = 15
        ```

        Manual inspection of the review-only items found bounded or negated
        contexts only; see `Output/4153/review_item_resolution.csv`.

        ## Active TeX Path

        | path |
| --- |
| mypaper2/Latex/main.tex |
| mypaper2/Latex/00_abstract.tex |
| mypaper2/Latex/01_introduction_v2.tex |
| mypaper2/Latex/02_data_v2.tex |
| mypaper2/Latex/Part2/02_data_trajectory_dataset.tex |
| mypaper2/Latex/Part2/02_data_t1_observable_v2.tex |
| mypaper2/Latex/03_methods_v2.tex |
| mypaper2/Latex/Part3/03_methods_affine_reduction_and_controls_v2.tex |
| mypaper2/Latex/Part3/03_methods_reduction_boundary_tests_v2.tex |
| mypaper2/Latex/04_results_v2.tex |
| mypaper2/Latex/Part4/04_results_t1_survival_v2.tex |
| mypaper2/Latex/Part4/04_results_scale_lag_robustness_v2.tex |
| mypaper2/Latex/Part4/04_results_diffuse_phenotype_v2.tex |
| mypaper2/Latex/Part4/04_results_failed_reductions_v2.tex |
| mypaper2/Latex/Part4/04_results_empirical_boundary_v2.tex |
| mypaper2/Latex/05_discussion_conclusion_v2.tex |
| mypaper2/Latex/Part5/05_discussion_interpretive_value_v2.tex |
| mypaper2/Latex/Part5/05_discussion_context_transfer_v2.tex |
| mypaper2/Latex/Part5/05_discussion_limitations_future_v2.tex |
| mypaper2/Latex/Part5/05_conclusion_v2.tex |
| mypaper2/Latex/bibitems.tex |

        ## Number Audit

        | item | status | active_hits | combined_hits | example |
| --- | --- | --- | --- | --- |
| primary_both_scale | pass | 8 | 16 | mypaper2/Latex/00_abstract.tex:9: two-scale consistency requirement, T1 survived in 14 of 19 observations; under |
| primary_any_scale | pass | 2 | 5 | mypaper2/Latex/00_abstract.tex:10: a more permissive any-scale criterion, it survived in 15 of 19 observations. |
| survivor_scale_lag | pass | 2 | 3 | mypaper2/Latex/00_abstract.tex:18: preprocessing-invariant. Within the survivor class, 14 of 15 observations |
| diffuse_tangential | pass | 2 | 2 | mypaper2/Latex/00_abstract.tex:20: repeatable phenotype was diffuse tangential activity, supported in 13 of 14 |
| near_pre_main | pass | 1 | 4 | mypaper2/Latex/Part4/04_results_diffuse_phenotype_v2.tex:36: original $8/14$ phase-localization count. Thus, the near-pre profile remained a |
| past_only_both | pass | 4 | 5 | mypaper2/Latex/00_abstract.tex:16: both-scale support to 11 of 19 under past-only detrending and 13 of 19 without |
| none_z_both | pass | 4 | 5 | mypaper2/Latex/00_abstract.tex:16: both-scale support to 11 of 19 under past-only detrending and 13 of 19 without |
| omnibus_B100 | pass | 5 | 10 | mypaper2/Latex/00_abstract.tex:12: the observed both-scale count ($B=100$, null maximum 11, plus-one |
| omnibus_p | pass | 3 | 4 | mypaper2/Latex/00_abstract.tex:13: $p=0.0099$), and local-affine conditioning quality control found |
| affine_median_cond | pass | 2 | 2 | mypaper2/Latex/Part4/04_results_t1_survival_v2.tex:40: 19 observations passed both $k$ values, the median condition number was 2.37, |
| affine_q95_cond | pass | 1 | 2 | mypaper2/Latex/Part4/04_results_t1_survival_v2.tex:41: the largest q95 condition number across combinations was 6.28, and no sampled |
| event_locality_median | pass | 2 | 3 | mypaper2/Latex/Part4/04_results_failed_reductions_v2.tex:26: event-minus-control near-pre effect was approximately $-0.033$, and the |
| history_q95 | pass | 1 | 5 | mypaper2/Latex/Part4/04_results_empirical_boundary_v2.tex:49: Recent history & 14/19 above median shuffle, 6/19 above q95 & History effects are observation-specific & A universal memory rule is proven \\ |

        ## Figure/Text Audit

        | item | status | evidence |
| --- | --- | --- |
| figures/Fig1_final.pdf | pass | active includegraphics found |
| figures/Fig2_final.pdf | pass | active includegraphics found |
| figures/Fig3_final.pdf | pass | active includegraphics found |
| figures/Fig4_final.pdf | pass | active includegraphics found |
| figures/Fig5_final.pdf | pass | active includegraphics found |
| old_4134_figure_references | pass | none in active path |

        ## Reference Audit

        | item | label | status | evidence |
| --- | --- | --- | --- |
| cited_label | cerbino2021_disentangling | pass | found in bibitems |
| cited_label | chikkadi2012_nonaffine | pass | found in bibitems |
| cited_label | falk1998_viscoplastic | pass | found in bibitems |
| cited_label | feng2023_sampling | pass | found in bibitems |
| cited_label | lee2013_epithelial | pass | found in bibitems |
| cited_label | reynolds2017_velocity_gravity | pass | found in bibitems |
| cited_label | reynolds2018_langevin | pass | found in bibitems |
| cited_label | reynolds2021_intrinsic | pass | found in bibitems |
| cited_label | reynolds2021_thermodynamic | pass | found in bibitems |
| cited_label | reynolds2024_spatial | pass | found in bibitems |
| cited_label | sinhuber2019_dataset | pass | found in bibitems |
| cited_label | sinhuber2021_eos | pass | found in bibitems |
| cited_label | vandervaart2020_perturbations | pass | found in bibitems |

        ## Interpretation

        Stop-level and fix-required items block 4154. Review-only items should
        be inspected but do not block the freeze if they are bounded negations,
        unsupported-claim labels, or unused bibliography entries intentionally
        retained.
