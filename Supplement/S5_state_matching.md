# S5 Compact-State and Event-Locality Tests

## Purpose

This supplement section records two negative reduction tests: whether compact
state variables provide stable first/second moment closure for T1, and whether
true transition timestamps add near-pre activity beyond matched compact state.

## Source Outputs

```text
Output/4090/primary_metrics.csv
Output/4090/grouped_oos_results.csv
Output/4100/observation_level_effects.csv
Output/4100/matching_quality.csv
Output/4100/shifted_event_null.csv
Output/4100/decision.json
Output/4150/figures/Fig4_final.pdf
```

## State Variables

The tested compact state was:

```text
S(t) = (C(t), dC/dt, R(t))
```

where `C(t)` is the compact-density coordinate, `dC/dt` its smoothed temporal
gradient, and `R(t)` the swarm-scale radius coordinate used in the frozen
state-matching route.

## Moment-Closure Result

| target family | target | median incremental R2 | positive-observation fraction | median real-minus-shift | interpretation |
| --- | --- | ---: | ---: | ---: | --- |
| first_moment | signed_tan_projection | -0.0006327793 | 0.2105263158 | -0.0003082888 | no stable grouped OOS support |
| second_moment | log_tan_energy | -0.0006213903 | 0.1578947368 | -0.0006586480 | no stable grouped OOS support |

The redesigned Figure 4A displays the held-out observation-level increments
rather than only the aggregate bars.

## State-Matched Event-Locality Result

The event-locality test matched true transition frames to same-observation
non-event frames in `(C, dC/dt, R)` space and asked whether true transition
timestamps showed additional near-pre T1 activity.

Matching used Euclidean distance in robust-standardized `(C, dC/dt, R)` space.
Candidate non-event controls were excluded if they occurred within `0.75 s` of
a true transition, ranked by state distance, and retained up to the five nearest
matches. An event was accepted only when its best match distance was at most
`0.75`. Controls were not removed after use, so the same non-event frame could
in principle match multiple true events. Distance ties were not given a special
random rule; they followed the deterministic numerical ordering returned by
the implementation.

```text
median observation event-minus-control near-pre effect = -0.03288737643286521
same-direction observation fraction = 0.42105263157894735
real beats shifted-null fraction = 0.275
total acceptable event fraction = 0.9796057104010877
median best-match distance = 0.17630717293908968
```

## Interpretation

The tested compact-state moment closure and the tested state-matched
event-locality route were not supported. This bounds two simple reductions of
T1, but it does not rule out richer state variables, delayed models, network
features, or transition dynamics in general.

## What This Does Not Prove

```text
absence of stochastic dynamics
absence of transition-specific dynamics
absence of propagation
complete mechanism exclusion
```
