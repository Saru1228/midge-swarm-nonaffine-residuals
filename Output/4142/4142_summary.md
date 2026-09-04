# Node 4142 Summary

## Question

Does the T1 result depend on the centered 1-second detrending used in the
frozen 4081/4084 pipeline?

## Method

The node reuses existing local T1 frame caches and raw 4084 spatial frames.
It does not redefine the local affine observable.

Three detrending variants are tested by default:

```text
centered_1s = frozen-style within-observation robust-z, centered rolling mean subtraction, robust-z again
past_1s     = same window length, but the smooth trend uses only earlier samples
none_z      = within-observation robust-z only, no smooth trend subtraction
```

For the survival gate, each variant reruns the event/control comparison for
`local_tangential_speed_mean` at `k=8` and `k=10`, using the frozen gate:

```text
gap > 0.03
p_non_event_direction_ge_event <= 0.35
local_to_B3_ratio >= 0.3
```

For the weaker phase result, the node reruns the 4085-style phase test for
`all_tangential` in the 14 both-scale survivor observations.

## Survival Results

| variant | n_observations | n_both | n_any | n_k8 | n_k10 | both_fraction | any_fraction | delta_both_vs_4081c | delta_any_vs_4081c | both_observations | any_observations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| centered_1s | 19 | 14 | 15 | 14 | 15 | 0.7368 | 0.7895 | 0 | 0 | 2,5,7,9,10,11,12,13,14,15,16,17,18,19 | 2,4,5,7,9,10,11,12,13,14,15,16,17,18,19 |
| past_1s | 19 | 11 | 16 | 12 | 15 | 0.5789 | 0.8421 | -3 | 1 | 2,7,9,10,11,12,13,14,15,16,19 | 1,2,4,7,8,9,10,11,12,13,14,15,16,17,18,19 |
| none_z | 19 | 13 | 16 | 16 | 13 | 0.6842 | 0.8421 | -1 | 1 | 2,4,9,10,11,12,13,14,15,16,17,18,19 | 2,4,5,7,8,9,10,11,12,13,14,15,16,17,18,19 |

## Near-Pre Phase Results

| variant | variable | phase | n_observations | phase_gate_count | phase_gate_fraction | median_abs_event_minus_abs_null_z | median_event_minus_null_phase_z | majority_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| centered_1s | all_tangential | near_pre | 14 | 11 | 0.7857 | 0.15 | -0.1919 | True |
| past_1s | all_tangential | near_pre | 14 | 8 | 0.5714 | 0.122 | -0.179 | True |
| none_z | all_tangential | near_pre | 14 | 12 | 0.8571 | 0.1675 | -0.2184 | True |

## Decision

`boundary_causal_detrending_reduces_core_survival`

Past-only detrending reduces the core T1 survival count; keep the T1 result but soften robustness language and inspect which observations flip.

## Boundary

This node tests detrending sensitivity only. It does not test local-affine
conditioning, formal high-B omnibus p-values, or biological mechanism.

## Next

| next |
| --- |
| 4142_flip_audit |
| 4143_local_affine_conditioning_QC |

## Artifacts

- `Output/4142/survival_detrending_rows.csv`
- `Output/4142/survival_variant_summary.csv`
- `Output/4142/phase_detrending_rows.csv`
- `Output/4142/phase_variant_summary.csv`
- `Output/4142/figures/4142_survival_detrending_variants.png`
- `Output/4142/figures/4142_near_pre_phase_detrending_variants.png`
- `Output/4142/decision.json`
