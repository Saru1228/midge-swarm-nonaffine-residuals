# Node 4132 Negative Mechanism Boundary Atlas

## Question

Which natural mechanism explanations are constrained by the current
evidence gates?

## Gate Result

```text
gate_result = pass_4132_negative_boundary_atlas_ready
```

## Main Interpretation

Negative evidence can be written as mechanism-boundary evidence. The
tested `C,dCdt,R` moment closure and the tested state-matched
event-local precursor route are not supported. Propagation is not
confirmatorily tested, not disproven. History and signed direction are
observation-specific boundaries, not universal laws.

## Boundary Counts

| atlas_rows | not_supported_rows | boundary_rows | not_tested_rows | supported_with_boundary_geometry_rows |
| --- | --- | --- | --- | --- |
| 8 | 2 | 3 | 1 | 2 |

## Negative Boundary Atlas

| boundary_id | mechanism_class | claim_class | failure_mode | what_is_ruled_out | what_remains_open |
| --- | --- | --- | --- | --- | --- |
| N1 | whole_swarm_affine_geometry_only | SUPPORTED_WITH_BOUNDARY | velocity event residual survived the global affine baseline | a purely global affine explanation for the earlier velocity event signal | local non-affine organization and richer geometric/state explanations |
| N2 | local_affine_geometry_only | SUPPORTED_WITH_BOUNDARY | T1 survived in most observations after local affine removal | local affine geometry as a complete explanation in the majority of observations | why Ob1/Ob3/Ob6/Ob8 fail and what richer local variables explain T1 |
| N3 | low_dimensional_state_moment_closure | NOT_SUPPORTED | first and second moment incremental R2 did not improve stably across observations | simple compact-density-conditioned first/second moment closure using only C,dCdt,R | higher-dimensional, delayed, network, or observation-specific stochastic descriptions |
| N4 | event_timestamp_specific_precursor | NOT_SUPPORTED | true transition timestamps did not show robust extra near-pre activity after state matching | state-matched near-pre event-locality under the frozen T1 aggregate | event dynamics not captured by C,dCdt,R or not expressible as near-pre excess |
| N5 | burst_or_propagation_route | NOT_TESTED | upstream event-locality gate failed, so propagation was not confirmatorily tested | automatic propagation analysis as a justified next confirmatory route | propagation in a redesigned target, different state representation, or descriptive future node |
| N6 | universal_recent_history_rule | BOUNDARY | history-conditioned separation exists but sign/order is not stable across observations | universal recent-history direction/order rule | observation-specific path effects and descriptive heterogeneity analysis |
| N7 | universal_signed_event_direction_law | BOUNDARY | signed class is heterogeneous with no majority signed law | universal signed force or mirror law | observation-specific signed response classes |
| N8 | recording_condition_or_batch_explanation | BOUNDARY | metadata explanation remains UNVERIFIED; failure labels are real but not causally explained | quietly treating failure observations as artifacts or metadata regimes | independent metadata verification and experimental-condition analysis |

## Claim Mapping From 4130

| claim_id | claim_strength | 4132_boundary_ids | support_nodes | forbidden_stronger_claim |
| --- | --- | --- | --- | --- |
| C4_SIGNED_EVENT_HETEROGENEITY | BOUNDARY | N7 | 4086;4088 | A universal signed force or mirror law is supported. |
| C5_NO_SIMPLE_STATE_MOMENT_CLOSURE | NOT_SUPPORTED | N3 | 4090;4094 | Stochastic dynamics or all state dependence are impossible. |
| C6_NO_EVENT_TIMESTAMP_EXCESS | NOT_SUPPORTED | N4 | 4100;4105 | Transitions have no special dynamics. |
| C7_OBSERVATION_SPECIFIC_HISTORY_BOUNDARY | BOUNDARY | N6 | 4120;4121;4125 | A robust universal history dependence or causal memory mechanism is supported. |
| C8_PROPAGATION_NOT_CONFIRMATORILY_TESTED | NOT_TESTED | N5 | 4100;4105;4125 | No propagation exists. |

## Forbidden Overclaims

| boundary_id | allowed_wording | forbidden_wording | reason |
| --- | --- | --- | --- |
| N1 | global affine motion is insufficient as a complete explanation | global geometry is irrelevant | boundary or nonuniversal result |
| N2 | local affine deformation does not fully absorb T1 in most observations | local affine geometry never matters | boundary or nonuniversal result |
| N3 | T1 remains a transition-linked local non-affine tangential residual from 4088, but the current compact-density state variables C,dCdt,radius do not provide a stable low-dimensional first- or second-moment explanation across observations. | stochastic dynamics do not explain midge swarms | tested failure only |
| N4 | Most observations contain a transition-linked local non-affine tangential residual after local affine deformation is removed, but the 4100 state-matched test shows that true transition timing does not add robust near-pre focal-centered activity beyond matched C,dCdt,R continuous state. | transitions have no special dynamics | tested failure only |
| N5 | propagation is not confirmatorily tested in the current 410x route | no propagation exists | route not confirmatorily tested |
| N6 | Recent C-R path direction can be measured and produces observation-specific T1 separations after same-current-state matching, but the sign/order is not stable enough to claim a universal history dependence mechanism. | history does not matter or a universal memory mechanism is proven | boundary or nonuniversal result |
| N7 | The near-pre diffuse T1 timing profile has signed event-type heterogeneity rather than a stable mirror or one-direction rule. | T1 has a single universal low-to-high or mirror-symmetric law | boundary or nonuniversal result |
| N8 | failure labels are explicit; metadata explanations remain descriptive only | Ob6/Ob8 fail because of confirmed daytime or batch effects | boundary or nonuniversal result |

## Mechanism Space Remaining

| open_space | why_open | requires_before_testing |
| --- | --- | --- |
| higher_dimensional_state_representation | 4090 tested only C,dCdt,R first/second moments | new frozen state variables and grouped validation plan |
| observation_specific_models | 4121 and 4086 show heterogeneity rather than universal signs | 4133 heterogeneity map and a predeclared grouping rule |
| network_or_local_interaction_descriptions | 4100A warned that raw neighbor residual vectors are overlapping, not independent | non-overlapping or explicitly modeled spatial unit definition |
| propagation_or_burst_dynamics | 4100 event-locality gate failed, so propagation was not confirmatorily tested | new event-local target or descriptive rather than confirmatory framing |
| metadata_conditioned_explanation | recording condition and observation order metadata remain unverified | independent metadata audit |

## What This Does Not Prove

| does_not_prove |
| --- |
| absence of stochastic organization |
| absence of propagation |
| absence of transition dynamics |
| absence of history effects |
| metadata regime explanation |

## Next Node

`4133_observation_heterogeneity_map`

## Artifacts

- `Output/4132/negative_boundary_atlas.csv`
- `Output/4132/bounded_negative_claims.csv`
- `Output/4132/forbidden_overclaims.csv`
- `Output/4132/mechanism_space_remaining.csv`
- `Output/4132/figures/4132_boundary_class_counts.png`
- `Output/4132/figures/4132_moment_closure_negative_metrics.png`
- `Output/4132/figures/4132_event_locality_negative_metrics.png`
- `Output/4132/figures/4132_history_boundary_metrics.png`
