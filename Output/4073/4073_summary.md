        # Node 4073 Summary

        ## Question

        Which baseline and null models are allowed for each future node, what does each preserve, and what does each destroy?

        ## Why this node exists

        4072 froze the primary residual metrics. 4073 freezes the baseline/null vocabulary so that 4071 replication and 408x local-affine tests do not change controls after seeing results.

        ## Data

        No raw trajectories were reprocessed. This is a registry/synthesis node derived from the 4070-4072 roadmap and completed 4xxx evidence.

        ## Frozen parameters

        Baselines:

        | baseline_id | name | class | primary_use | status |
| --- | --- | --- | --- | --- |
| B0 | identity_measurement_audit | artifact_control | Required diagnostic layer before strong mechanism claims. | registered_required_artifact_layer |
| B1 | translation | geometric_baseline | First rung of 4081 geometry ladder. | registered |
| B2 | global_rigid | geometric_baseline | Second rung of 4081 geometry ladder. | registered |
| B3 | global_affine | geometric_baseline | Current 4001/4002A baseline and 4071 replication baseline. | registered_current_target_baseline |
| B4 | local_affine | geometric_baseline | 4080 feasibility and 4081 major geometry-irreducibility gate. | registered_not_yet_computed |

        Nulls and controls:

        | null_id | name | class | primary_use | status |
| --- | --- | --- | --- | --- |
| N1 | time_shift_or_shifted_event | temporal_null | 4071 replication of 4001/4002A style event-conditioned residual signals. | registered_current_primary_event_null |
| N2 | phase_or_spectrum_preserving_temporal_null | temporal_smooth_null | Guard against smooth time-series artifacts in 4074, 4090, and 4101. | registered_required_for_smooth_time_series_claims |
| N3 | identity_permutation | identity_history_null | Membership/history artifact control and graph-history checks. | registered |
| N4 | neighbor_or_geometry_matched_null | geometry_matched_null | Required for core/edge, density, local-affine, and graph claims. | registered_required_for_geometry_sensitive_claims |
| N5 | matched_non_event_window | sampling_window_control | 4074 event-free versus event-conditioned audit. | registered_for_event_selection_control |

        ## Baseline

        The current target baseline remains `B3_global_affine`. Route A must explicitly compare `B1 -> B2 -> B3 -> B4`.

        ## Null model

        The current replication null is `N1_time_shift_or_shifted_event`. Smooth temporal and geometry-sensitive claims require `N2` and/or `N4`.

        ## Primary metrics

        Use only the 4072 primary metrics in 4071:

        ```text
        resid_velocity_cov_trace
        resid_speed_rms
        resid_tangential_speed_mean
        resid_radial_abs_mean
        edge_minus_core_resid_speed
        edge_minus_core_resid_tangential
        ```

        ## Results

        Future-node registry:

        | future_node | required_primary_metrics | required_baselines | required_nulls_or_controls | forbidden_shortcut | entry_condition |
| --- | --- | --- | --- | --- | --- |
| 4071_cross_dataset_baseline_audit | 4072 primary metrics only | B3 | N1; report dataset-wise effects and sign consistency | Do not add or replace primary metrics after seeing Ob2/Ob3. | 4072 and 4073 completed. |
| 4074_event_free_vs_event_conditioned_audit | 4072 primary metrics; secondary diagnostics only as context | B0,B3 | N1,N2,N5 | Do not define events using the same downstream propagation metric. | 4071 completed or explicitly skipped for a documented reason. |
| 4080_local_affine_feasibility | not metric-driven; fit-quality diagnostics first | B4 feasibility only | condition-number and neighbor-turnover diagnostics | Do not interpret D2min if local affine fits are numerically unstable. | 4072/4073 completed; 4071 does not collapse the target. |
| 4081_global_vs_local_geometry_ladder | 4072 primary metrics | B1,B2,B3,B4 | N4 geometry-matched null if claiming non-affine residual beyond local geometry | Do not claim non-affinity from B3 residual alone. | 4080 feasibility pass. |
| 4090_conditional_mean_vs_variance | 4072 metrics or 408x local-nonaffine metric if Route A survives | B3 or B4, depending on Route A result | N1,N2,N4; out-of-sample mean-vs-variance comparison | Do not treat correlation or in-sample fit gain as force/mechanism. | M1 review says residual survives the relevant geometry baseline. |
| 410x_transient_propagation | Frozen residual/non-affine activity metric | B3 or B4 | N1,N2,N5; matched non-burst windows | Do not call lagged correlation a wave without stable lag-distance structure and replication. | Frozen burst/activity definition from 4072 or 408x. |
| 411x_network_organization | Frozen residual/non-affine activity metric | B0,B3 or B4 | N3,N4 plus degree/geometry preserving graph controls | Do not infer biological interaction from a single graph edge or metric. | 4072/4073 completed and target residual variable frozen; preferably after Route A. |

        ## Dataset-wise replication

        Not run in 4073. Replication starts in 4071 using 4072 metrics and this registry.

        ## Gate evaluation

        `pass`: baselines=5, nulls=5, future-node rules=7.

        ## What this rules out

        4071 cannot add new primary metrics, and 4081 cannot claim non-affinity from the global-affine residual alone. Graph or stochastic claims must use geometry-sensitive controls when relevant.

        ## What this does NOT prove

        4073 does not prove residual robustness or any mechanism. It only freezes controls.

        ## Decision

        `pass`: proceed to 4071 cross-dataset baseline audit.

        ## Next node

        `4071_cross_dataset_baseline_audit`
