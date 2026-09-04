# Node 4155 Parallel High-B Omnibus Null

## Purpose

Convert the failed monolithic 4149 high-B run into a deterministic,
chunked, resumable, and parallel high-B calibration.

## Gate Result

`strong_pass_omnibus_null`

```text
requested_replicates = 1000
completed_replicates = 1000
chunk_size = 50
workers = 4
n_controls_per_replicate_observation = 40
observed N_both = 14
observed N_any = 15
p_both_ge_14 = 0.000999001
p_any_ge_15 = 0.021978
null N_both mean = 4.38
null N_both q95 = 7
null N_both max = 12
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
| chunk_0001_0050 | 1 | 50 | complete | True | 137.19290471076965 |
| chunk_0051_0100 | 51 | 100 | complete | True | 138.39293313026428 |
| chunk_0101_0150 | 101 | 150 | complete | True | 138.4406635761261 |
| chunk_0151_0200 | 151 | 200 | complete | True | 137.42809772491455 |
| chunk_0201_0250 | 201 | 250 | complete | True | 141.05656743049622 |
| chunk_0251_0300 | 251 | 300 | complete | True | 140.97616934776306 |
| chunk_0301_0350 | 301 | 350 | complete | True | 141.4807116985321 |
| chunk_0351_0400 | 351 | 400 | complete | True | 141.94014382362366 |
| chunk_0401_0450 | 401 | 450 | complete | True | 139.87770748138428 |
| chunk_0451_0500 | 451 | 500 | complete | True | 139.40435361862183 |
| chunk_0501_0550 | 501 | 550 | complete | True | 139.00886607170105 |
| chunk_0551_0600 | 551 | 600 | complete | True | 139.92157125473022 |
| chunk_0601_0650 | 601 | 650 | complete | True | 139.08856177330017 |
| chunk_0651_0700 | 651 | 700 | complete | True | 139.3499755859375 |
| chunk_0701_0750 | 701 | 750 | complete | True | 139.80450582504272 |
| chunk_0751_0800 | 751 | 800 | complete | True | 140.32017135620117 |
| chunk_0801_0850 | 801 | 850 | complete | True | 139.62347269058228 |
| chunk_0851_0900 | 851 | 900 | complete | True | 141.0731167793274 |
| chunk_0901_0950 | 901 | 950 | complete | True | 141.4530131816864 |
| chunk_0951_1000 | 951 | 1000 | complete | True | 141.78622150421143 |

## Observation Null Pass Rates

| ob | dataset | n_replicates | null_pass_rate_k8 | null_pass_rate_k10 | null_pass_rate_both | null_pass_rate_any | observed_k8_pass | observed_k10_pass | observed_both_pass | observed_any_pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ob1.txt | 1000 | 0.357 | 0.334 | 0.167 | 0.524 | False | False | False | False |
| 2 | Ob2.txt | 1000 | 0.383 | 0.371 | 0.213 | 0.541 | True | True | True | True |
| 3 | Ob3.txt | 1000 | 0.347 | 0.348 | 0.193 | 0.502 | False | False | False | False |
| 4 | Ob4.txt | 1000 | 0.379 | 0.352 | 0.218 | 0.513 | False | True | False | True |
| 5 | Ob5.txt | 1000 | 0.322 | 0.336 | 0.189 | 0.469 | True | True | True | True |
| 6 | Ob6.txt | 1000 | 0.347 | 0.36 | 0.218 | 0.489 | False | False | False | False |
| 7 | Ob7.txt | 1000 | 0.396 | 0.349 | 0.223 | 0.522 | True | True | True | True |
| 8 | Ob8.txt | 1000 | 0.409 | 0.368 | 0.23 | 0.547 | False | False | False | False |
| 9 | Ob9.txt | 1000 | 0.375 | 0.339 | 0.194 | 0.52 | True | True | True | True |
| 10 | Ob10.txt | 1000 | 0.378 | 0.386 | 0.206 | 0.558 | True | True | True | True |
| 11 | Ob11.txt | 1000 | 0.288 | 0.365 | 0.172 | 0.481 | True | True | True | True |
| 12 | Ob12.txt | 1000 | 0.368 | 0.367 | 0.235 | 0.5 | True | True | True | True |
| 13 | Ob13.txt | 1000 | 0.543 | 0.549 | 0.403 | 0.689 | True | True | True | True |
| 14 | Ob14.txt | 1000 | 0.385 | 0.372 | 0.226 | 0.531 | True | True | True | True |
| 15 | Ob15.txt | 1000 | 0.365 | 0.375 | 0.217 | 0.523 | True | True | True | True |
| 16 | Ob16.txt | 1000 | 0.355 | 0.347 | 0.204 | 0.498 | True | True | True | True |
| 17 | Ob17.txt | 1000 | 0.396 | 0.402 | 0.231 | 0.567 | True | True | True | True |
| 18 | Ob18.txt | 1000 | 0.505 | 0.528 | 0.378 | 0.655 | True | True | True | True |
| 19 | Ob19.txt | 1000 | 0.421 | 0.436 | 0.263 | 0.594 | True | True | True | True |

## Boundary

No missing chunks; this is a completed high-B calibration.

## Artifacts

- `Output/4155/runs/highB_n1000_c40/run_config.json`
- `Output/4155/runs/highB_n1000_c40/chunk_status.csv`
- `Output/4155/runs/highB_n1000_c40/omnibus_replicates.csv`
- `Output/4155/runs/highB_n1000_c40/observation_replicate_passes.csv`
- `Output/4155/runs/highB_n1000_c40/observation_null_pass_rates.csv`
- `Output/4155/runs/highB_n1000_c40/N_both_distribution.csv`
- `Output/4155/runs/highB_n1000_c40/N_any_distribution.csv`
- `Output/4155/runs/highB_n1000_c40/p_omnibus.json`
- `Output/4155/runs/highB_n1000_c40/decision.json`
- `Output/4155/runs/highB_n1000_c40/figures`
