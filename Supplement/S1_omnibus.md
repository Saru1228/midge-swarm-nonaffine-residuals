# S1 Full-Pipeline Omnibus Calibration

## Purpose

This analysis checks whether the observed all-observation T1 survival count is
readily reproduced by pseudo-events run through the same local-affine T1
pipeline and survival gate.

## Source Outputs

```text
Output/4140/frozen_analysis_contract.yaml
Output/4141/omnibus_null_config.yaml
Output/4141/omnibus_replicates.csv
Output/4141/observation_replicate_passes.csv
Output/4141/observation_null_pass_rates.csv
Output/4141/N_both_distribution.csv
Output/4141/N_any_distribution.csv
Output/4141/p_omnibus.json
Output/4149/4149_boundary_summary.md
Output/4155/runs/highB_n1000_c40/
Output/4155/p_omnibus.json
Output/4155/chunk_status.csv
Output/4155/observation_null_pass_rates.csv
```

## Frozen Design

The null preserved the observation identity and the event-type count structure.
Pseudo-event centers were sampled within the same observation while avoiding
true transition windows. Non-event controls were sampled within the same
observation and avoided true and pseudo-event windows.

For each observation and replicate, the number of pseudo-events matched the
number of true transition events in that observation. The low-to-high and
high-to-low event-type labels were also copied from the true event template, so
event-type counts were preserved. Candidate centers were sampled from the
recording interval after removing the pre/post margin used by the event window.
True transition centers were excluded with a `0.80 s` exclusion half-width.
Pseudo-events were sampled sequentially without mutual overlap whenever enough
admissible time remained; if the sequential exclusion became infeasible in a
short or dense recording, the sampler fell back to the true-event exclusion
only, and finally to uniform sampling within the admissible recording interval.
The same pseudo-event realization was used for `k=8` and `k=10` so that
cross-scale dependence was preserved.

For the non-event controls, each replicate-observation generated 40 control
sets. Each control set preserved the same number and type order as the event
template, and control centers avoided both the true transition centers and the
pseudo-event centers. Controls were generated independently for each
replicate-observation. The random seed was deterministic by replicate:
`BASE_SEED + replicate * 1000003`.

The survival gate was unchanged:

```text
local_event_minus_non_event_direction_z > 0.03
p_non_event_direction_ge_event <= 0.35
local_to_b3_direction_ratio >= 0.30
```

The `0.35` criterion is an empirical non-event tail fraction used as a frozen
screening component. It is not a conventional single-observation significance
threshold. The all-observation inference is the separately calibrated omnibus
count `N_both`.

The main statistic was the number of observations that passed the survival
gate at both original neighborhood scales:

```text
N_both = sum_ob I(pass_k8 and pass_k10)
```

Algorithm sketch:

```text
for b in 1..B:
    for observation in 1..19:
        construct pseudo-event centers under the frozen admissibility rules
        preserve the true event count and low/high event-type sequence
        generate 40 same-observation non-event control sets
        compute the frozen event-control metrics at k=8
        compute the frozen event-control metrics at k=10
        apply the frozen per-scale screening rule
        record whether the observation passes both scales

    N_both[b] = number of observations passing both k=8 and k=10
```

## Completed Calibration Result

```text
B = 1000
controls per observation per replicate = 40
observed N_both = 14/19
observed N_any = 15/19
null N_both mean = 4.38
null N_both median = 4
null N_both q95 = 7
null N_both q99 = 9
null N_both max = 12
plus-one p(N_both >= 14) = 0.000999000999000999

null N_any mean = 10.223
null N_any median = 10
null N_any q95 = 14
null N_any q99 = 15
null N_any max = 17
plus-one p(N_any >= 15) = 0.02197802197802198
```

No both-scale null replicate reached the observed `14/19` count. The plus-one
Monte Carlo estimate is therefore `1/(1000+1)`.

## High-Replicate Execution

The original monolithic high-B attempt reached an interactive compute boundary.
The completed run resolved this by splitting `B=1000` into 20 chunks of 50
replicates and running four workers in parallel. Each replicate used a
deterministic independent seed, so completed chunks could be resumed and merged
without changing previously generated replicate values. A prefix-sum
event-window implementation was validated against the original slicing
implementation before the high-B run:

```text
max_abs_diff = 1.5404344466674047e-14
n_checks = 12
```

## Interpretation

The completed result supports the statement that the observed `14/19`
both-scale count was rare under a high-replicate full-pipeline pseudo-event
calibration. The any-scale result is also above the upper tail but is less
specific because the any-scale criterion is more permissive.

## What This Does Not Prove

```text
biological mechanism
online prediction
universal T1 law
preprocessing invariance
artifact-free interpretation
```
