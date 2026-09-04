For each null replicate `b` and observation:

```text
1. Use the same observation as the real event sequence.
2. Sample pseudo-event centers only from admissible frames.
3. Exclude frames too close to true transition windows.
4. Preserve the real event-count structure used by the frozen gate.
5. Recompute the same event-control metrics at k=8 and k=10.
6. Generate 40 non-event controls per replicate-observation.
7. Apply the frozen per-scale residual-support screen.
8. Record whether the observation passes at k=8, k=10, both scales, or any scale.
9. Aggregate N_both[b] and N_any[b] across all 19 observations.
10. Estimate plus-one empirical tails against the observed counts.
```

The per-scale survival rule is a frozen screening rule, not the manuscript-level
significance test. The manuscript-level calibration is the all-observation
full-pipeline pseudo-event omnibus distribution.

## Reporting Precision

The exact plus-one value for the both-scale omnibus tail is
`0.000999000999000999`. In manuscript prose, it should be rounded to
approximately `p_emp = 0.001`, together with the more informative statement that
`0/1000` null replicates reached `N_both = 14`.
