# Node 4141 Summary

        ## Purpose

        Estimate how unusual the observed all-observation T1 survival count is
        under a full pseudo-event event/control pipeline.

        ## Frozen Inputs

        - Contract: `Output/4140/frozen_analysis_contract.yaml`
        - Events: `Output/3045/tables/transition_events.csv`
        - B3 residual frame: `Output/4002A/processed/frame_residual_spatial_metrics.csv`
        - Local T1 definition: `Experiment/run_4081_global_vs_local_geometry_ladder.py`
        - Observed support: `Output/4081c/full_geometry_ladder_rows.csv`

        ## Exact Analysis Performed

        ```text
        mode = smoke
        null replicates = 100
        controls per observation per replicate = 40
        observations = all 19
        k values = 8,10
        lag = 0.1
        ```

        For each null replicate and observation, pseudo-event centers were
        sampled within the same observation while avoiding true transition
        windows. The same pseudo-event centers were used for k=8 and k=10 so
        that cross-scale dependence was preserved. Non-event controls preserved
        the same event-type counts and avoided true and pseudo-event windows.

        ## Primary Result

        ```text
        observed N_both = 14
        observed N_any  = 15
        null N_both mean = 4.49
        null N_both median = 4
        null N_both q95 = 8
        null N_both max = 11
        p_both_ge_14 = 0.009901
        p_any_ge_15 = 0.0396
        ```

        ## Observation-Level Result

        | ob | dataset | n_replicates | null_pass_rate_k8 | null_pass_rate_k10 | null_pass_rate_both | null_pass_rate_any | observed_k8_pass | observed_k10_pass | observed_both_pass | observed_any_pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ob1.txt | 100 | 0.38 | 0.4 | 0.21 | 0.57 | False | False | False | False |
| 2 | Ob2.txt | 100 | 0.4 | 0.36 | 0.21 | 0.55 | True | True | True | True |
| 3 | Ob3.txt | 100 | 0.4 | 0.34 | 0.21 | 0.53 | False | False | False | False |
| 4 | Ob4.txt | 100 | 0.39 | 0.31 | 0.2 | 0.5 | False | True | False | True |
| 5 | Ob5.txt | 100 | 0.33 | 0.23 | 0.14 | 0.42 | True | True | True | True |
| 6 | Ob6.txt | 100 | 0.43 | 0.48 | 0.33 | 0.58 | False | False | False | False |
| 7 | Ob7.txt | 100 | 0.41 | 0.35 | 0.19 | 0.57 | True | True | True | True |
| 8 | Ob8.txt | 100 | 0.48 | 0.4 | 0.29 | 0.59 | False | False | False | False |
| 9 | Ob9.txt | 100 | 0.32 | 0.37 | 0.18 | 0.51 | True | True | True | True |
| 10 | Ob10.txt | 100 | 0.34 | 0.31 | 0.17 | 0.48 | True | True | True | True |
| 11 | Ob11.txt | 100 | 0.18 | 0.33 | 0.12 | 0.39 | True | True | True | True |
| 12 | Ob12.txt | 100 | 0.37 | 0.31 | 0.18 | 0.5 | True | True | True | True |
| 13 | Ob13.txt | 100 | 0.54 | 0.56 | 0.41 | 0.69 | True | True | True | True |
| 14 | Ob14.txt | 100 | 0.36 | 0.38 | 0.24 | 0.5 | True | True | True | True |
| 15 | Ob15.txt | 100 | 0.36 | 0.42 | 0.22 | 0.56 | True | True | True | True |
| 16 | Ob16.txt | 100 | 0.4 | 0.43 | 0.24 | 0.59 | True | True | True | True |
| 17 | Ob17.txt | 100 | 0.34 | 0.44 | 0.22 | 0.56 | True | True | True | True |
| 18 | Ob18.txt | 100 | 0.58 | 0.46 | 0.39 | 0.65 | True | True | True | True |
| 19 | Ob19.txt | 100 | 0.49 | 0.47 | 0.34 | 0.62 | True | True | True | True |

        ## Gate Evaluation

        `smoke_complete_do_not_use_for_manuscript_p_value`

        Use this run to validate runtime and output structure; run B>=1000 before manuscript inference.

        ## What This Strengthens

        It tests the reviewer-defense question: whether a high all-observation
        survival count appears often when the whole per-observation gate is run
        on non-transition pseudo-events.

        ## What This Weakens

        If this is a smoke run, the empirical p-value is not manuscript-ready.
        It is only a runtime and pipeline validation.

        ## What This Does NOT Prove

        | does_not_prove |
| --- |
| mechanism |
| prediction |
| universal T1 law |
| detrending robustness |
| affine-fit conditioning robustness |

        ## Decision

        `smoke_complete_do_not_use_for_manuscript_p_value`

        ## Next

        | next |
| --- |
| 4141_full_B_ge_1000 |

        ## Artifacts

        - `Output/4141/omnibus_null_config.yaml`
        - `Output/4141/omnibus_replicates.csv`
        - `Output/4141/observation_replicate_passes.csv`
        - `Output/4141/N_both_distribution.csv`
        - `Output/4141/N_any_distribution.csv`
        - `Output/4141/observation_null_pass_rates.csv`
        - `Output/4141/p_omnibus.json`
        - `Output/4141/figures/`
        - `Output/4141/decision.json`
