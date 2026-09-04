# Node 4149 Boundary Summary

## Purpose

Run the frozen 4141 full-pipeline pseudo-event omnibus null at a higher
replicate count while preserving the same observed T1 definition, survival
gate, k values, lag, pseudo-event construction, and all-19 observation scope.

## Attempted Run

```text
n_null_replicates = 1000
n_controls_per_replicate_observation = 40
k_values = 8,10
lag_sec = 0.1
frame_stride = 2
max_focals_per_frame = 24
cache_source = Output/4141/cache
output = Output/4149
interactive_timeout_sec = 1800
```

The cache manifest was written, confirming that the node reused the existing
4141 local T1 cache. The run did not reach `p_omnibus.json`,
`omnibus_replicates.csv`, or figure output before the 30-minute interactive
timeout. A residual Python process from this run was stopped.

## Boundary Decision

`boundary_4149_highB_requires_batch_or_overnight_run`

This is a compute boundary, not a statistical negative result. The only
completed full-pipeline omnibus estimate remains the 4141 smoke run:

```text
B = 100
observed N_both = 14/19
observed N_any = 15/19
p_both_ge_14 = 0.009900990099009901
p_any_ge_15 = 0.039603960396039604
```

## Manuscript Consequence

Do not present a formal high-B p-value from 4149. The current manuscript can
refer to the completed 4141 smoke-level omnibus null only if it is clearly
described as limited-resolution pipeline validation. A formal high-B p-value
should be treated as a separate batch or overnight robustness task.

## Next

Continue to `4150_final_figure_cleanup` under the no-per-node-compilation
policy. If formal p-value resolution later becomes necessary, rerun 4149 with
progress logging as a staged batch job, for example `B=250`, then `B=500`, then
`B=1000`.
