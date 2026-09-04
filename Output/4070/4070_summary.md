# Node 4070 Summary

## Question

What survived geometry in the 4001-4066 chain, which mechanism explanations failed, and what can be tested next without reopening metric search?

## Why this node exists

4066 concluded that the 4xxx branch should pause mechanism search. 4070 converts that branch into a bounded result map: a surviving target phenomenon, excluded or bounded mechanism stories, and a small set of open explanation classes.

## Data

No raw trajectory data were reprocessed. This synthesis uses existing summaries and EGRT decision tables from `Output/4001` through `Output/4066`.

## Frozen parameters

This node freezes the routing order, not the residual metric set:

```text
4070 -> 4072 -> 4073 -> 4071 -> 4074 -> M0 review
```

The metric and null freeze must happen in 4072 and 4073 before cross-dataset replication in 4071.

## Baseline

The main surviving baseline comparison is the 4001 translation plus global affine geometry subtraction.

## Null model

The branch primarily used shifted-event nulls, with additional density-preserving checks in 4053b. 4073 must convert these into a formal null/baseline registry.

## Primary metrics

Current target sentence:

> After removing translation plus global affine deformation, the transition-aligned affine-residual velocity observables speed_rms, velocity_cov_trace, mean_speed, and tangential_speed_mean remain robust under the original 4001 shifted-event screen across 19 observations and 1471 events; this target still requires 4072 metric freeze, 4073 null freeze, 4071 cross-dataset replication, and 408x local-affine testing.

This is strict enough to continue foundation work, but still has a caveat: local affine geometry and event-free occurrence have not yet been tested.

## Results

- Supported or method-supported entries: 3
- Boundary entries: 4
- Failed mechanism entries: 4
- Total mechanism-map entries: 12

## Dataset-wise replication

4070 does not run replication. The strongest current full-series result is 4001 over 19 observations. The unstable single-observation branch is 4020/4020B, where Ob1 and Ob2 pass with different variables and Ob3 fails.

## Gate evaluation

`passed_with_caveat`

The branch can be stated as a bounded target:

```text
After removing translation plus global affine deformation, a transition-aligned affine-residual velocity signal remains.
```

But it cannot yet be stated as:

```text
This residual is local-nonaffine, stochastic, propagating, network-driven, or biological-causal.
```

## What this rules out

See `excluded_or_bounded_claims.md`. Current excluded or bounded claims include timing-trigger edge/core redistribution, local kNN cumulants, stable one-fish redistribution, coarse residual state transition modulation, stable graph pair-core/motifs, and stationary mesoscopic residual fields.

## What this does NOT prove

4070 does not prove a new mechanism. It does not prove local non-affinity, multiplicative noise, propagation, network causality, or a biological control rule.

## Decision

`pass`: proceed to foundation freeze.

## Next node

```text
4072_residual_observable_taxonomy
4073_null_and_baseline_registry
4071_cross_dataset_baseline_audit
4074_event_free_vs_event_conditioned_audit
```

## Artifacts

- `Output/4070/mechanism_map.csv`
- `Output/4070/mechanism_map.json`
- `Output/4070/surviving_claims.md`
- `Output/4070/excluded_or_bounded_claims.md`
- `Output/4070/open_explanation_space.md`
- `Output/4070/decision.json`
