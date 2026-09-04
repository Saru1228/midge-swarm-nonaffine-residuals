# 4148 Notation and Equation Consistency Audit

Node: `4148_notation_and_equation_consistency_audit`  
Date: 2026-09-02

## Result

`pass_4148_active_notation_consistent`

## Active LaTeX Path

| file |
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

## Checks

| check_id | result | finding |
| --- | --- | --- |
| active_path_uses_v2_core_files | pass | Active path should use the corrected v2 data/method files. |
| t1_plain_term_not_subscripted | pass | T1 is used as a named residual family, not a T_1 equation symbol. |
| t1_not_raw_velocity_or_force | pass | T1 boundary against raw velocity/force interpretation is explicit. |
| local_affine_equation_present | pass | Local affine least-squares equation is present. |
| compact_state_definitions_present | pass | C(t), dot C(t), and R(t) are defined. |
| spectral_set_publication_provenance_in_active_methods | pass | Active Methods should include enough 4147 provenance to avoid circularity. |
| near_pre_endpoint_distinction_explicit | pass | 4085 phase bins and 4100 state-matched near-pre aggregate use different endpoint conventions. |
| radius_unit_exception_defined | pass | The focal-radius versus swarm-level R exception is stated. |
| b3_ratio_defined | pass | B3 shorthand in local_to_b3_direction_ratio should be defined. |
| near_pre_main_count_not_overwritten_by_4142 | pass | 4146 near-pre main-count correction is preserved. |
| smoke_null_not_formal_high_b | pass | B=100 omnibus null remains correctly bounded. |

## Required Fixes

_No rows._

## Registry

| symbol_or_term | canonical_use | allowed_variants | disallowed_variants |
| --- | --- | --- | --- |
| T1 | Plain-text name for the local tangential non-affine residual activity family; not written as T_1 and not treated as force. | local tangential non-affine activity; T1 observable | raw speed; inferred force; T_1 |
| C(t) | Compact-density coordinate: robust-z standardized rho_rms(t) within each observation. | C; density_rms_z3045 in code | raw density without standardization |
| \dot{C}(t) | Time gradient of the one-second smoothed C(t). | dCdt in code | unsmoothed finite difference without note |
| R(t) | Swarm-size coordinate: robust-z standardized R_rms(t); vector-level moment tests use focal radius as an explicit exception. | R; r_rms_z3045 in code | focal radius without noting unit change |
| R^2_inc | Incremental predictive score, distinct from the swarm-size coordinate R(t). | incremental R^2 | R as radius score without context |
| spectral_set | Inherited transfer-operator compact-density coarse graining from 3032/3032b, not fitted from T1. | compact-density low/high labels | T1-optimized labels |
| near-pre phase bin | 4085 phase bin: [-0.25,0.00) s; event frame belongs to near-post for phase profiles. | near-pre timing | same as endpoint-inclusive 4100 window without note |
| near-pre state-matched aggregate | 4100 endpoint-inclusive aggregate: [-0.25,0.00] s; distinct from half-open phase-bin convention. | event-local near-pre activity | undifferentiated near-pre definition |
| B3 | Upstream global-affine residual baseline used only in the local-to-B3 retention ratio. | local/global-affine retention ratio | undefined B3 shorthand |

## Occurrence Table

| pattern_id | file | n_hits | lines |
| --- | --- | --- | --- |
| T1 | mypaper2/Latex/00_abstract.tex | 4 | 6,9,26,28 |
| T1 | mypaper2/Latex/01_introduction_v2.tex | 6 | 80,122,124,125,131,142 |
| T1 | mypaper2/Latex/Part2/02_data_trajectory_dataset.tex | 2 | 22,24 |
| T1 | mypaper2/Latex/Part2/02_data_t1_observable_v2.tex | 4 | 35,37,39,102 |
| C(t) | mypaper2/Latex/Part2/02_data_t1_observable_v2.tex | 2 | 17,24 |
| dotC | mypaper2/Latex/Part2/02_data_t1_observable_v2.tex | 1 | 19 |
| R(t) | mypaper2/Latex/Part2/02_data_t1_observable_v2.tex | 1 | 20 |
| R_rms | mypaper2/Latex/Part2/02_data_t1_observable_v2.tex | 3 | 5,14,21 |
| spectral_set | mypaper2/Latex/Part2/02_data_t1_observable_v2.tex | 2 | 25,31 |
| T1 | mypaper2/Latex/03_methods_v2.tex | 1 | 5 |
| T1 | mypaper2/Latex/Part3/03_methods_affine_reduction_and_controls_v2.tex | 6 | 13,29,46,57,66,81 |
| near_pre_half_open | mypaper2/Latex/Part3/03_methods_affine_reduction_and_controls_v2.tex | 1 | 77 |
| B3 | mypaper2/Latex/Part3/03_methods_affine_reduction_and_controls_v2.tex | 2 | 36,37 |
| T1 | mypaper2/Latex/Part3/03_methods_reduction_boundary_tests_v2.tex | 2 | 3,27 |
| C(t) | mypaper2/Latex/Part3/03_methods_reduction_boundary_tests_v2.tex | 1 | 8 |
| dotC | mypaper2/Latex/Part3/03_methods_reduction_boundary_tests_v2.tex | 4 | 8,16,29,43 |
| R_rms | mypaper2/Latex/Part3/03_methods_reduction_boundary_tests_v2.tex | 1 | 22 |
| R2 | mypaper2/Latex/Part3/03_methods_reduction_boundary_tests_v2.tex | 1 | 11 |
| near_pre_closed | mypaper2/Latex/Part3/03_methods_reduction_boundary_tests_v2.tex | 1 | 28 |
| endpoint_inclusive | mypaper2/Latex/Part3/03_methods_reduction_boundary_tests_v2.tex | 1 | 35 |
| T1 | mypaper2/Latex/04_results_v2.tex | 1 | 4 |
| T1 | mypaper2/Latex/Part4/04_results_t1_survival_v2.tex | 6 | 1,6,7,15,16,33 |
| T1 | mypaper2/Latex/Part4/04_results_scale_lag_robustness_v2.tex | 1 | 8 |
| T1 | mypaper2/Latex/Part4/04_results_diffuse_phenotype_v2.tex | 1 | 6 |
| T1 | mypaper2/Latex/Part4/04_results_failed_reductions_v2.tex | 2 | 8,21 |
| dotC | mypaper2/Latex/Part4/04_results_failed_reductions_v2.tex | 3 | 6,15,25 |
| R2 | mypaper2/Latex/Part4/04_results_failed_reductions_v2.tex | 1 | 15 |
| T1 | mypaper2/Latex/Part4/04_results_empirical_boundary_v2.tex | 3 | 25,42,43 |
| dotC | mypaper2/Latex/Part4/04_results_empirical_boundary_v2.tex | 1 | 47 |
| R2 | mypaper2/Latex/Part4/04_results_empirical_boundary_v2.tex | 1 | 47 |
| T1 | mypaper2/Latex/Part5/05_discussion_interpretive_value_v2.tex | 2 | 3,11 |
| T1 | mypaper2/Latex/Part5/05_discussion_context_transfer_v2.tex | 2 | 10,26 |
| T1 | mypaper2/Latex/Part5/05_discussion_limitations_future_v2.tex | 1 | 7 |
| dotC | mypaper2/Latex/Part5/05_discussion_limitations_future_v2.tex | 1 | 14 |
| T1 | mypaper2/Latex/Part5/05_conclusion_v2.tex | 1 | 11 |

## Boundary

Only active manuscript files are allowed to fail the 4148 gate. Legacy inactive
LaTeX files remain in the repository but are not part of this audit's pass/fail
decision.
