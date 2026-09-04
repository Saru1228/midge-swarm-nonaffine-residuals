# 2026-09-02 4155 Parallel High-B Omnibus Null

## Summary

Node `4155_parallel_highB_omnibus_null` converted the 4149 high-B compute
boundary into a completed chunked, resumable, parallel `B=1000` omnibus
pseudo-event calibration.

## Gate Result

`strong_pass_omnibus_null`

## Run Configuration

```text
run_name = highB_n1000_c40
requested_replicates = 1000
completed_replicates = 1000
chunk_size = 50
workers = 4
n_controls_per_replicate_observation = 40
completed_chunks = 20/20
worker_failures = 0
```

The fast prefix-sum event-window implementation passed equivalence validation
against the original slicing implementation:

```text
max_abs_diff = 1.5404344466674047e-14
n_checks = 12
```

## Primary Result

```text
observed N_both = 14/19
observed N_any = 15/19
p_both_ge_14 = 0.000999000999000999
p_any_ge_15 = 0.02197802197802198
null N_both mean = 4.38
null N_both q95 = 7
null N_both max = 12
null N_any mean = 10.223
null N_any q95 = 14
null N_any max = 17
```

No both-scale null replicate reached the observed 14-observation count.

## Interpretation

This result resolves the 4149 compute boundary and supports using a completed
`B=1000` full-pipeline pseudo-event calibration in the manuscript. It remains a
null-calibration result, not a mechanism proof. Existing boundaries about
detrending sensitivity, observation heterogeneity, and failed compact-state or
history reductions remain unchanged.

## Artifacts

- `Experiment/run_4155_parallel_highB_omnibus_null.py`
- `Output/4155/4155_summary.md`
- `Output/4155/decision.json`
- `Output/4155/p_omnibus.json`
- `Output/4155/chunk_status.csv`
- `Output/4155/observation_null_pass_rates.csv`
- `Output/4155/runs/highB_n1000_c40/`
- `idea/4155_parallel_highB_omnibus_null_result_and_routing.md`

## Next

Open `4156_highB_manuscript_integration_and_refreeze` if the completed high-B
result should replace the previous limited-resolution wording in the manuscript
and supplement.
