        # Node 4155 Parallel High-B Omnibus Null

        ## Purpose

        Convert the failed monolithic 4149 high-B run into a deterministic,
        chunked, resumable, and parallel high-B calibration.

        ## Gate Result

        `operational_smoke_complete_not_inference`

        ```text
        requested_replicates = 8
        completed_replicates = 8
        chunk_size = 2
        workers = 2
        n_controls_per_replicate_observation = 40
        observed N_both = 14
        observed N_any = 15
        p_both_ge_14 = 0.111111
        p_any_ge_15 = 0.111111
        null N_both mean = 3.875
        null N_both q95 = 5
        null N_both max = 5
        ```

        ## Method

        Each replicate is assigned a deterministic independent seed, so chunks
        can be run in any order and resumed without changing already-completed
        replicate values. The pipeline keeps the frozen 4141 event definition,
        pseudo-event construction, non-event controls, survival gate, k values,
        lag, and all-19 observation scope. The only computational change is
        chunking plus a prefix-sum implementation of the same event-window mean
        calculation.

        ## Chunk Status

        | chunk | rep_start | rep_end | status | complete | elapsed_sec |
| --- | --- | --- | --- | --- | --- |
| chunk_0001_0002 | 1 | 2 | complete | True | 2.196760416030884 |
| chunk_0003_0004 | 3 | 4 | complete | True | 2.1356847286224365 |
| chunk_0005_0006 | 5 | 6 | complete | True | 2.14139986038208 |
| chunk_0007_0008 | 7 | 8 | complete | True | 1.9904165267944336 |

        ## Observation Null Pass Rates

        | ob | dataset | n_replicates | null_pass_rate_k8 | null_pass_rate_k10 | null_pass_rate_both | null_pass_rate_any | observed_k8_pass | observed_k10_pass | observed_both_pass | observed_any_pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ob1.txt | 8 | 0.25 | 0.25 | 0.0 | 0.5 | False | False | False | False |
| 2 | Ob2.txt | 8 | 0.375 | 0.625 | 0.25 | 0.75 | True | True | True | True |
| 3 | Ob3.txt | 8 | 0.25 | 0.375 | 0.125 | 0.5 | False | False | False | False |
| 4 | Ob4.txt | 8 | 0.375 | 0.375 | 0.25 | 0.5 | False | True | False | True |
| 5 | Ob5.txt | 8 | 0.375 | 0.375 | 0.125 | 0.625 | True | True | True | True |
| 6 | Ob6.txt | 8 | 0.625 | 0.5 | 0.25 | 0.875 | False | False | False | False |
| 7 | Ob7.txt | 8 | 0.25 | 0.375 | 0.125 | 0.5 | True | True | True | True |
| 8 | Ob8.txt | 8 | 0.5 | 0.5 | 0.375 | 0.625 | False | False | False | False |
| 9 | Ob9.txt | 8 | 0.5 | 0.375 | 0.25 | 0.625 | True | True | True | True |
| 10 | Ob10.txt | 8 | 0.625 | 0.375 | 0.25 | 0.75 | True | True | True | True |
| 11 | Ob11.txt | 8 | 0.125 | 0.375 | 0.125 | 0.375 | True | True | True | True |
| 12 | Ob12.txt | 8 | 0.0 | 0.0 | 0.0 | 0.0 | True | True | True | True |
| 13 | Ob13.txt | 8 | 0.625 | 0.625 | 0.375 | 0.875 | True | True | True | True |
| 14 | Ob14.txt | 8 | 0.375 | 0.5 | 0.25 | 0.625 | True | True | True | True |
| 15 | Ob15.txt | 8 | 0.5 | 0.5 | 0.25 | 0.75 | True | True | True | True |
| 16 | Ob16.txt | 8 | 0.375 | 0.25 | 0.25 | 0.375 | True | True | True | True |
| 17 | Ob17.txt | 8 | 0.625 | 0.5 | 0.5 | 0.625 | True | True | True | True |
| 18 | Ob18.txt | 8 | 0.125 | 0.375 | 0.125 | 0.375 | True | True | True | True |
| 19 | Ob19.txt | 8 | 0.125 | 0.25 | 0.0 | 0.375 | True | True | True | True |

        ## Boundary

        This run is an operational smoke test only; do not use it as a scientific p-value.

        ## Artifacts

        - `Output/4155/runs/benchmark_n8_c40_interval/run_config.json`
        - `Output/4155/runs/benchmark_n8_c40_interval/chunk_status.csv`
        - `Output/4155/runs/benchmark_n8_c40_interval/omnibus_replicates.csv`
        - `Output/4155/runs/benchmark_n8_c40_interval/observation_replicate_passes.csv`
        - `Output/4155/runs/benchmark_n8_c40_interval/observation_null_pass_rates.csv`
        - `Output/4155/runs/benchmark_n8_c40_interval/N_both_distribution.csv`
        - `Output/4155/runs/benchmark_n8_c40_interval/N_any_distribution.csv`
        - `Output/4155/runs/benchmark_n8_c40_interval/p_omnibus.json`
        - `Output/4155/runs/benchmark_n8_c40_interval/decision.json`
        - `Output/4155/runs/benchmark_n8_c40_interval/figures`
