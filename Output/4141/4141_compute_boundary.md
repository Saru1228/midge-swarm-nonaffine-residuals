# 4141 Compute Boundary

## Context

Review 007 requested a full-pipeline omnibus survival null for the observed
T1 count:

```text
N_both_observed = 14 / 19
N_any_observed  = 15 / 19
```

The 4141 implementation was created as:

- `Experiment/run_4141_full_pipeline_omnibus_survival_null.py`

## Attempted Run

Command:

```powershell
python Experiment\run_4141_full_pipeline_omnibus_survival_null.py --smoke --n-null 100
```

The run began by building missing local T1 cache files required for strict
all-observation null inference.

Completed before stopping:

- `Output/4141/cache/Ob1_k8_lag0p100_stride2_focals24.csv`

The process had entered:

- `Ob1 k=10`

and was intentionally stopped.

## Reason For Stopping

The strict 4141 smoke cannot use existing 4081c summary rows or 4084 spatial
caches as a substitute for the 4081c T1 time series. It must evaluate the same
T1 gate on pseudo-event centers at both k=8 and k=10. This requires local T1
time-series caches for all 19 observations and both k values.

The observed runtime shows that cache construction is a batch job, not a short
interactive smoke test.

## What Was Not Produced

No completed omnibus null replicate table was produced.

Do not use this partial run as:

- `p_omnibus`;
- evidence for or against the 14/19 global count;
- manuscript-level inference.

## Operational Routing

Next recommended command pattern:

```powershell
python Experiment\run_4141_full_pipeline_omnibus_survival_null.py --cache-only --obs 1-5
python Experiment\run_4141_full_pipeline_omnibus_survival_null.py --cache-only --obs 6-10
python Experiment\run_4141_full_pipeline_omnibus_survival_null.py --cache-only --obs 11-15
python Experiment\run_4141_full_pipeline_omnibus_survival_null.py --cache-only --obs 16-19
python Experiment\run_4141_full_pipeline_omnibus_survival_null.py --smoke --n-null 100
```

After smoke runtime is acceptable:

```powershell
python Experiment\run_4141_full_pipeline_omnibus_survival_null.py --n-null 1000
```

## Decision

```text
status = implementation_ready_cache_batch_required
boundary = compute/runtime, not definition mismatch
next = 4141 cache batch
```

