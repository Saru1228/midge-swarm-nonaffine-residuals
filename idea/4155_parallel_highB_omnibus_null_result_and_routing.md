# 4155 Parallel High-B Omnibus Null Result and Routing

Date: 2026-09-02

## Node

`4155_parallel_highB_omnibus_null`

## Question

Can the previously blocked high-B omnibus pseudo-event calibration be made
executable at `B=1000`, while preserving the frozen T1 definition and the
all-19 observation gate?

## Computational Change

The statistical design was kept fixed relative to 4141:

- all 19 observations;
- observed counts `N_both = 14/19` and `N_any = 15/19`;
- k values `8` and `10`;
- lag `0.10 s`;
- pre/post event window `0.20 s`;
- exclusion window `0.80 s`;
- `40` non-event controls per observation per replicate;
- same pseudo-event and non-event-control logic.

The execution strategy was changed:

- `B=1000` was split into 20 chunks of 50 replicates;
- 4 workers were launched in parallel;
- each replicate received a deterministic independent seed;
- each chunk wrote its own status, aggregate rows, and observation rows;
- completed chunks could be resumed and merged without rerunning;
- event-window means were computed with prefix sums;
- pseudo-event/control sampling was optimized by dynamic interval subtraction.

## Validation

The fast event-window implementation was checked against the original slicing
implementation:

```text
fast_equivalence_status = pass
max_abs_diff = 1.5404344466674047e-14
n_checks = 12
```

An operational benchmark with `B=8`, `controls=40`, `workers=2` completed in
approximately 16 seconds after optimization. The pre-optimization version of
the same benchmark took approximately 158 seconds.

## High-B Run

```text
run_name = highB_n1000_c40
requested_replicates = 1000
completed_replicates = 1000
chunk_size = 50
workers = 4
n_controls_per_replicate_observation = 40
completed_chunks = 20/20
worker_failures = 0
mean_chunk_elapsed_sec = 139.881
```

## Primary Result

```text
observed N_both = 14
observed N_any = 15
null N_both mean = 4.38
null N_both median = 4
null N_both q95 = 7
null N_both q99 = 9
null N_both max = 12
p_both_ge_14 = 0.000999000999000999

null N_any mean = 10.223
null N_any median = 10
null N_any q95 = 14
null N_any q99 = 15
null N_any max = 17
p_any_ge_15 = 0.02197802197802198
```

No `N_both` null replicate reached the observed `14/19` both-scale count, so
the plus-one Monte Carlo estimate is `1/(1000+1) = 0.000999`.

## Gate

`strong_pass_omnibus_null`

This resolves the 4149 compute boundary. The stronger both-scale observation
count is rare under the complete pseudo-event null pipeline at `B=1000`.

## Interpretation

The high-B run strengthens the reviewer-facing claim that the all-observation
T1 survival count is not easily reproduced by time-randomized pseudo-events.
It does not prove a biological mechanism, prediction, attractor, or universal
law. The detrending and observation-heterogeneity boundaries remain active.

## Routing

Next node:

```text
4156_highB_manuscript_integration_and_refreeze
```

Reason:

```text
The 4154 frozen manuscript package predates the completed B=1000 result.
If this result is accepted into the paper, the Abstract, Methods, Results,
Supplement S1, and final frozen package should be updated and recompiled.
```

## Artifacts

- `Experiment/run_4155_parallel_highB_omnibus_null.py`
- `Output/4155/4155_summary.md`
- `Output/4155/decision.json`
- `Output/4155/p_omnibus.json`
- `Output/4155/chunk_status.csv`
- `Output/4155/N_both_distribution.csv`
- `Output/4155/N_any_distribution.csv`
- `Output/4155/observation_null_pass_rates.csv`
- `Output/4155/runs/highB_n1000_c40/`
