        # Node 4072 Summary

        ## Question

        Which affine-residual velocity observables are primary targets, which are secondary diagnostics, and which should be retired before cross-dataset replication?

        ## Why this node exists

        4070 produced a strict target sentence but did not freeze the metric set. 4072 prevents metric search in 4071/408x by selecting a small, interpretable residual-observable taxonomy before seeing new replication outcomes.

        ## Data

        Source table:

        `Output/4002A/tables/residual_structure_direction_null_comparison.csv`

        No raw trajectories were reprocessed.

        ## Frozen parameters

        ```text
        primary_target_metrics <= 6
        secondary_diagnostics <= 12
        no new primary metrics during 4071 replication
        ```

        ## Baseline

        4002A affine residuals after the 4001 translation plus global affine subtraction.

        ## Null model

        4002A shifted-event nulls are inherited here only for metric selection. 4073 must still formalize which nulls are used in future tests.

        ## Primary metrics

        | primary_rank | variable | taxonomy_class | family | real_abs_median_direction_contrast_z | direction_contrast_sign_consistency | reason |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | resid_velocity_cov_trace | V_covariance_anisotropy | residual_intensity | 0.5790683828287234 | 0.8947368421052632 | Strongest affine-residual velocity dispersion/covariance survivor; bridges 4001 velocity_cov_trace and 408x residual-energy tests. |
| 2 | resid_speed_rms | I_magnitude_energy | residual_intensity | 0.5521874570287999 | 0.8947368421052632 | Direct residual speed magnitude/energy target; interpretable for local-affine residual energy ladders. |
| 3 | resid_tangential_speed_mean | III_tangential | tangential_swirl | 0.42423763470043996 | 0.9473684210526315 | Strong tangential residual survivor with highest sign consistency among main kinematic metrics. |
| 4 | resid_radial_abs_mean | II_radial | radial | 0.25353491385556093 | 0.7894736842105263 | Radial residual magnitude survivor; keeps inward/outward geometry distinct from tangential motion. |
| 5 | edge_minus_core_resid_speed | VII_core_edge_contrast | edge_core | 0.21931037986054489 | 0.7368421052631579 | Primary core-edge residual speed contrast; interpretable spatial redistribution metric. |
| 6 | edge_minus_core_resid_tangential | VII_core_edge_contrast | edge_core | 0.20076853076448825 | 0.7894736842105263 | Core-edge tangential residual contrast; complements speed contrast without adding a new family. |

        ## Secondary diagnostics

        | variable | taxonomy_class | family | real_abs_median_direction_contrast_z | direction_survives_gate | reason |
| --- | --- | --- | --- | --- | --- |
| radius_resid_speed_corr | VI_spatial_heterogeneity | edge_core | 0.265240969900851 | False | Spatial-gradient diagnostic. It has notable effect size but did not satisfy the full survivor gate, so it remains secondary. |
| resid_inward_fraction | II_radial | radial | 0.08896765499369855 | False | Directional radial fraction diagnostic; lower gate support than radial absolute magnitude. |
| resid_radial_velocity_mean | II_radial | radial | 0.08465227196832814 | False | Signed radial residual diagnostic; kept secondary because sign can be sensitive to event definition. |
| radius_resid_tangential_corr | VI_spatial_heterogeneity | edge_core | 0.07725644479727736 | False | Tangential spatial-gradient diagnostic retained only for sensitivity/context. |
| resid_tangential_fraction | III_tangential | tangential_swirl | 0.04049912048058646 | False | Tangential direction fraction diagnostic; lower support than tangential speed mean. |

        ## Retired or negative controls

        | variable | taxonomy_class | family | real_abs_median_direction_contrast_z | direction_survives_gate | reason |
| --- | --- | --- | --- | --- | --- |
| resid_polarization | IV_directional_alignment | residual_order | 0.010855626490185004 | False | Residual order/alignment did not survive 4002A; global residual alignment should not drive the next route. |

        ## Dataset-wise replication

        Not run in 4072. These metric roles must be used unchanged in 4071.

        ## Gate evaluation

        `pass`: primary=6, secondary=5, retired=1.

        ## What this rules out

        The next branch should not use global residual polarization/order as a primary target, and should not add individual-distribution tail metrics from 4020/4020B unless a new node explicitly reopens that route.

        ## What this does NOT prove

        4072 does not prove robustness, local non-affinity, stochasticity, propagation, or network mechanism. It only freezes observables.

        ## Decision

        `pass`: proceed to 4073 null/baseline registry.

        ## Next node

        `4073_null_and_baseline_registry`
