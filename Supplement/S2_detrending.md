# S2 Detrending Challenge

## Purpose

This analysis asks whether the T1 survival result depends strongly on the
centered detrending used in the frozen pipeline.

## Source Outputs

```text
Output/4142/survival_variant_summary.csv
Output/4142/survival_variant_summary.json
Output/4142/phase_variant_summary.csv
Output/4142/phase_variant_summary.json
Output/4142/decision.json
Output/4146/near_pre_definition_audit.csv
Output/4146/source_trace.md
```

## Variants

```text
centered_1s: subtract a one-second centered rolling mean, then robust-z.
past_1s: subtract a one-second past-only rolling mean, then robust-z.
none_z: skip rolling detrending and use robust-z standardization only.
```

In the first two variants, the input trace was robust-z standardized, the
one-second rolling mean was subtracted, and the residual trace was robust-z
standardized again. In the `none_z` variant, no rolling subtraction was applied;
the trace was robust-z standardized only.

## Survival Result

| variant | observations | both-scale support | any-scale support | interpretation |
| --- | ---: | ---: | ---: | --- |
| centered_1s | 19 | 14/19 | 15/19 | Reproduces the frozen primary count |
| past_1s | 19 | 11/19 | 16/19 | Majority-level support remains, but the exact both-scale count drops |
| none_z | 19 | 13/19 | 16/19 | Majority-level support remains without rolling detrending |

The result is therefore not erased by detrending alternatives, but the exact
`14/19` both-scale count is strongest under the frozen centered definition.

## Near-Pre Timing Sensitivity

For the all-tangential near-pre phase summary in 4142:

| variant | near-pre phase support | median abs event-minus-null z | median signed event-minus-null z |
| --- | ---: | ---: | ---: |
| centered_1s | 11/14 | 0.1499508146 | -0.1918738917 |
| past_1s | 8/14 | 0.1220495834 | -0.1789533555 |
| none_z | 12/14 | 0.1675332231 | -0.2184067537 |

Node 4146 showed that the main-text `8/14` near-pre result and the 4142
near-pre counts are not the same metric. The manuscript keeps the original
phase-localization `8/14` count as the main timing result and treats the 4142
counts as sensitivity evidence.

## Interpretation

The detrending challenge supports a bounded claim: T1 is present at majority
level under multiple preprocessing choices, but the exact survivor count and
some timing summaries are preprocessing-sensitive.

## What This Does Not Prove

```text
online prediction
causal precursor
preprocessing-invariant 14/19 support
universal timing law
```
