# Node 4090B Summary

## Question

Can 4090 recover the two required inputs?

```text
1. vector-level local non-affine residual samples
2. continuous compact-density C(t) and dC/dt
```

## Why this node exists after 4090A

4090A routed the workflow forward with an unconfirmed observation-sequence
boundary. Before fitting mean-vs-variance models, 4090B checks whether the
objects needed for that model exist without redefining the upstream T1 target.

## Frozen Upstream Target

```text
T1 = local tangential non-affine residual
baseline = local affine geometry
```

## Technical Feasibility

| item | status | evidence | boundary | recommended_4090_handling |
| --- | --- | --- | --- | --- |
| vector_level_local_nonaffine_residual | available_by_recomputation | sample rows exported = 2560 using 4081 local-affine equations; current 4081 outputs save frame-level aggregates, not this vector table. | The vector unit is focal-neighborhood neighbor residual, matching the 4081 all_tangential aggregate. It is not yet a unique focal-individual residual vector. | Use this vector-level source with explicit unit label, or aggregate to focal-neighborhood before modeling. |
| continuous_compact_density_coordinate | available | C source = density_rms_z3045; min finite C fraction = 0.998; min finite dC/dt fraction = 1.000; partition evidence = available | C is a traced compact-density coordinate, not a newly optimized 4090 score. | Use density_rms_z3045 as C(t) and gradient(density_rms_smooth3045,t) as dC/dt. |
| metadata_for_recording_order_or_batch | unavailable | 4090A found no recording day/session/camera metadata in existing outputs. | Do not call observation index a confirmed acquisition batch variable. | Keep observation identity and 4088 boundary strata explicit in grouped validation. |

## Continuous State Source

Partition evidence:

```json
{
  "status": "available",
  "partition_id": "eig2",
  "eigen_rank": 2,
  "interpretive_axis": "high set higher density_rms (delta_z=1.5); high set lower r_rms (delta_z=-1.4); high set lower anisotropy (delta_z=-0.248)",
  "evidence": "3032 raw spectral partition summary traces high set to compact-density axis."
}
```

Coverage:

| ob | dataset | n_frames | t_min | t_max | dt_median | spectral_set_nonnull_fraction | density_rms_z3045_finite_fraction | density_rms_smooth3045_finite_fraction | dCdt_finite_fraction | C_primary | dCdt_source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ob1.txt | 10989 | 0.07 | 110 | 0.01 | 1 | 1 | 1 | 1 | density_rms_z3045 | gradient(density_rms_smooth3045, t) |
| 2 | Ob2.txt | 14859 | 0.07 | 148.7 | 0.01 | 1 | 1 | 1 | 1 | density_rms_z3045 | gradient(density_rms_smooth3045, t) |
| 3 | Ob3.txt | 14990 | 0.06 | 149.9 | 0.01 | 1 | 1 | 1 | 1 | density_rms_z3045 | gradient(density_rms_smooth3045, t) |
| 4 | Ob4.txt | 14952 | 0.06 | 149.9 | 0.01 | 1 | 1 | 1 | 1 | density_rms_z3045 | gradient(density_rms_smooth3045, t) |
| 5 | Ob5.txt | 14957 | 0.06 | 149.9 | 0.01 | 1 | 1 | 1 | 1 | density_rms_z3045 | gradient(density_rms_smooth3045, t) |
| 6 | Ob6.txt | 19991 | 0.05 | 199.9 | 0.01 | 1 | 0.9999 | 1 | 1 | density_rms_z3045 | gradient(density_rms_smooth3045, t) |
| 7 | Ob7.txt | 9992 | 0.04 | 99.95 | 0.01 | 1 | 0.9999 | 1 | 1 | density_rms_z3045 | gradient(density_rms_smooth3045, t) |
| 8 | Ob8.txt | 18989 | 0.07 | 189.9 | 0.01 | 1 | 1 | 1 | 1 | density_rms_z3045 | gradient(density_rms_smooth3045, t) |
| 9 | Ob9.txt | 9949 | 0.07 | 99.95 | 0.01 | 1 | 0.9983 | 1 | 1 | density_rms_z3045 | gradient(density_rms_smooth3045, t) |
| 10 | Ob10.txt | 14991 | 0.05 | 149.9 | 0.01 | 1 | 0.9999 | 1 | 1 | density_rms_z3045 | gradient(density_rms_smooth3045, t) |
| 11 | Ob11.txt | 19990 | 0.06 | 199.9 | 0.01 | 1 | 0.9999 | 1 | 1 | density_rms_z3045 | gradient(density_rms_smooth3045, t) |
| 12 | Ob12.txt | 19990 | 0.06 | 199.9 | 0.01 | 1 | 0.9999 | 1 | 1 | density_rms_z3045 | gradient(density_rms_smooth3045, t) |
| 13 | Ob13.txt | 19989 | 0.07 | 199.9 | 0.01 | 1 | 1 | 1 | 1 | density_rms_z3045 | gradient(density_rms_smooth3045, t) |
| 14 | Ob14.txt | 19989 | 0.07 | 199.9 | 0.01 | 1 | 1 | 1 | 1 | density_rms_z3045 | gradient(density_rms_smooth3045, t) |
| 15 | Ob15.txt | 19990 | 0.06 | 199.9 | 0.01 | 1 | 0.9999 | 1 | 1 | density_rms_z3045 | gradient(density_rms_smooth3045, t) |
| 16 | Ob16.txt | 19990 | 0.06 | 199.9 | 0.01 | 1 | 0.9999 | 1 | 1 | density_rms_z3045 | gradient(density_rms_smooth3045, t) |
| 17 | Ob17.txt | 19991 | 0.05 | 199.9 | 0.01 | 1 | 0.9999 | 1 | 1 | density_rms_z3045 | gradient(density_rms_smooth3045, t) |
| 18 | Ob18.txt | 19989 | 0.07 | 199.9 | 0.01 | 1 | 1 | 1 | 1 | density_rms_z3045 | gradient(density_rms_smooth3045, t) |
| 19 | Ob19.txt | 29991 | 0.05 | 299.9 | 0.01 | 1 | 1 | 1 | 1 | density_rms_z3045 | gradient(density_rms_smooth3045, t) |

## Residual Vector Sample

```json
{
  "sample_rows": 2560,
  "sample_ob": 2,
  "median_resid_tan_norm": 161.65651767109563,
  "median_condition_number": 2.2703607018505263,
  "unique_focals": 296,
  "unique_neighbors": 1227
}
```

The sample is written to `Output/4090B/residual_vector_sample.csv`.

## Gate Evaluation

```text
gate_result = B1_vector_available_with_unit_boundary_and_C_available
```

Vector-level residual samples are recomputable from 4081 equations, and C,dC are traceable from 3045. 4090 can proceed, but must label the vector unit as focal-neighborhood neighbor residual unless a unique focal-individual residual definition is implemented.

## Boundary

The currently reproducible vector unit is:

```text
focal-neighborhood neighbor residual vector
```

This matches how 4081/4088 built `all_tangential`, but it is not yet a unique
focal-individual vector. 4090 must state this explicitly, or add a separate
aggregation step that freezes how neighbor residual vectors become focal-level
observations.

## What This Does NOT Prove

| does_not_prove |
| --- |
| first-vs-second moment dominance |
| state-dependent stochastic mechanism |
| batch artifact |
| unique individual focal residual vector without additional definition |

## Decision

`B1_vector_available_with_unit_boundary_and_C_available`

## Next Node

`4090_continuous_moment_classification_with_vector_unit_note`

## Artifacts

- `Output/4090B/technical_feasibility_table.csv`
- `Output/4090B/continuous_state_coverage.csv`
- `Output/4090B/residual_vector_sample.csv`
- `Output/4090B/figures/4090B_continuous_state_trace.png`
- `Output/4090B/figures/4090B_vector_sample_tangential_norm.png`
