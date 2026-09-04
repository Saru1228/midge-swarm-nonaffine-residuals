# 4146 Near-Pre Definition Audit

Node: `4146_near_pre_definition_audit`  
Date: 2026-09-02

## Question

Why do the current materials contain both `4085` near-pre support of `8/14`
and `4142` centered near-pre support of `11/14`?

## Result

`pass_4146_discrepancy_explained_by_gate_and_null_definition`

The two numbers are not conflicting estimates of one frozen definition.
They use the same observation set, same `all_tangential` variable, same
near-pre window, and effectively identical real event values, but they differ
in the event-control gate and pseudo-event sampler.

## Source-Level Counts

| source_id | reported_phase_gate_count | count_under_4085_gate | count_under_4142_gate | reported_abs_gap_gate | reported_p_gate | null_sampler |
| --- | --- | --- | --- | --- | --- | --- |
| 4085_original | 8 | 8 | 11 | 0.12 | 0.25 | run_4081.sample_non_event_times |
| 4142_centered_1s | 11 | 9 | 11 | 0.03 | 0.35 | run_4141.sample_like_events |
| 4142_past_1s | 8 | 7 | 8 | 0.03 | 0.35 | run_4141.sample_like_events |
| 4142_none_z | 12 | 9 | 12 | 0.03 | 0.35 | run_4141.sample_like_events |

## Definition Comparison

| dimension | same | 4085_value | 4142_centered_value | interpretation |
| --- | --- | --- | --- | --- |
| tested_observation_set | True | 2,5,7,9,10,11,12,13,14,15,16,17,18,19 | 2,5,7,9,10,11,12,13,14,15,16,17,18,19 | same denominator and observation set |
| variable | True | all_tangential | all_tangential | same reported variable |
| phase_window | True | [-0.25, 0.00) s | [-0.25, 0.00) s | same near-pre timing bin |
| real_event_values | True | cached real phase values | recomputed centered real phase values | max absolute real-value difference = 3e-15 |
| abs_gap_gate | False | 0.12 | 0.03 | 4085 is stricter on effect-size excess |
| p_gate | False | 0.25 | 0.35 | 4142 is looser on the pseudo-event tail condition |
| null_sampler | False | run_4081.sample_non_event_times | run_4141.sample_like_events | same real events, different pseudo-event controls |

## Key Diagnostic

- 4085 reported `8/14`; recomputing the 4085 gate on 4085 rows also gives
  `8/14`.
- Applying the looser 4142 gate to the same 4085 rows gives `11/14`.
- 4142 centered reported `11/14`; applying the stricter 4085 gate to those
  rows gives `9/14`.
- The maximum absolute difference between the 4085 and 4142-centered real
  near-pre event values is `3e-15`.

## Manuscript Decision

Use the original 4085 `8/14` as the main-text near-pre timing count. Treat the
4142 centered/past/no-rolling near-pre counts as detrending-specific
sensitivity evidence, not as a replacement for the original phase-localization
definition.

## Boundary

This audit resolves a definitional inconsistency. It does not decide whether
near-pre timing is mechanistic, because the earlier state-matched
event-locality route did not preserve a robust near-pre excess.
