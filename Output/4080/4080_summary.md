# Node 4080 Summary

## Question

Are local affine fits numerically identifiable and stable enough for the midge swarm data to support a 4081 geometry ladder?

## Why this node exists

4075 authorized Route A only after splitting the residual target. Before using
`D2min` or local non-affine language, 4080 checks whether local affine tensors
can be fit stably in sparse 3D swarm neighborhoods.

## Data

```text
ob = Ob1
dataset = Ob1.txt
median_dt = 0.01 sec
frames_total = 10989
frames_sampled = 500
```

## Frozen parameters

Target policy from 4075:

```text
primary = T1_transition_tangential_residual
secondary = T2_general_residual_activity
retired_primary = radial residual, core-edge speed
```

4080 itself is target-agnostic feasibility.

## Baseline

`B4_local_affine`, feasibility only.

## Null model

No event null is used in 4080. This node tests numerical identifiability, not event signal.

## Primary metrics

| k | lag_sec | n_attempted | valid_fit_fraction | rank3_fraction | median_condition_number | q90_condition_number | median_neighbor_retention | combo_passes_feasibility_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4 | 0.05 | 12000 | 0.9187 | 0.9187 | 3.584 | 9.245 | 1 | True |
| 4 | 0.1 | 12000 | 0.8558 | 0.8558 | 3.575 | 9.172 | 1 | True |
| 4 | 0.2 | 12000 | 0.7488 | 0.7488 | 3.562 | 9.086 | 1 | True |
| 6 | 0.05 | 12000 | 0.977 | 0.977 | 2.54 | 4.665 | 1 | True |
| 6 | 0.1 | 12000 | 0.9569 | 0.9569 | 2.555 | 4.756 | 1 | True |
| 6 | 0.2 | 12000 | 0.9196 | 0.9196 | 2.601 | 4.958 | 1 | True |
| 8 | 0.05 | 12000 | 0.9772 | 0.9772 | 2.177 | 3.488 | 1 | True |
| 8 | 0.1 | 12000 | 0.9586 | 0.9586 | 2.185 | 3.522 | 1 | True |
| 8 | 0.2 | 12000 | 0.9254 | 0.9254 | 2.207 | 3.631 | 1 | True |
| 10 | 0.05 | 12000 | 0.9772 | 0.9772 | 2.005 | 3.058 | 1 | True |
| 10 | 0.1 | 12000 | 0.9586 | 0.9586 | 2.014 | 3.081 | 1 | True |
| 10 | 0.2 | 12000 | 0.9256 | 0.9256 | 2.027 | 3.15 | 1 | True |
| 12 | 0.05 | 12000 | 0.9772 | 0.9772 | 1.899 | 2.804 | 1 | True |
| 12 | 0.1 | 12000 | 0.9586 | 0.9586 | 1.902 | 2.814 | 1 | True |
| 12 | 0.2 | 12000 | 0.9256 | 0.9256 | 1.911 | 2.854 | 1 | True |

## Results

- Passing k/lag combinations: 15
- Robust passing combinations with k>=6: 12
- Decision: `pass_local_affine_feasible`

## Gate evaluation

`pass_local_affine_feasible`

## What this rules out

If local affine fitting had failed, D2min/non-affine interpretation would stop. With a pass, 4081 may compare global and local geometry, but still may not claim mechanism.

## What this does NOT prove

4080 does not prove local non-affinity or biological mechanism. It only says local affine fits are numerically feasible enough to test in 4081.

## Decision

`pass_local_affine_feasible`

## Next node

`4081_global_vs_local_geometry_ladder`
