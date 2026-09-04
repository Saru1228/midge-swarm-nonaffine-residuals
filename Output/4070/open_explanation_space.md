# 4070 Open Explanation Space

4070 does not start a new mechanism search. It names the explanation classes that remain open after the completed gates and ties each one to a specific future node.

| Open class | Why still open | Next test |
| --- | --- | --- |
| local_heterogeneous_affine_geometry | 4001 used global affine geometry; spatially varying local affine deformation has not been subtracted. | 4080 feasibility, then 4081 global-vs-local geometry ladder. |
| local_nonaffine_reorganization | If local affine deformation cannot explain the residual, D2min-style non-affine diagnostics become meaningful. | 4081 major gate B, then 4082/4083 scale and cross-dataset robustness. |
| state_dependent_stochasticity | Prior drift/Langevin closures were weak, but conditional variance or multiplicative noise was not cleanly separated from conditional mean. | 4090 conditional mean-vs-variance after residual target freeze. |
| transient_spatiotemporal_propagation | 4060 only tested stationary field-like profiles; transient lagged reorganization remains distinct. | 4100-4104 only after a frozen residual/non-affine activity variable. |
| network_level_organization | 405x weakens fixed pair-core claims but does not rule out stable network-level statistics or spectral scales. | 4110-4114 only after target residual observable freeze and geometry controls. |
| measurement_finiteN_membership_artifact | Center motion and residual signals can be affected by membership changes, velocity estimation, finite-N averaging, and event selection. | 4073 baseline/null registry and 4074 event-free audit. |
