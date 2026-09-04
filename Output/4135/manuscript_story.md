# 4135 Manuscript-style Technical Synthesis

## Working Title

**Local non-affine organization in laboratory midge swarms beyond affine geometry and low-dimensional state descriptions**

## Central Question

What components of collective midge motion remain after progressively
removing global geometry, local affine deformation, low-dimensional
state dependence, event timing, and simple recent-history
explanations?

## Core Answer

The strongest current answer is bounded but useful. Laboratory midge
swarms contain a reproducible local tangential non-affine residual
(`T1`) in most observations after local affine deformation is removed.
This residual is not universal, and it does not reduce cleanly to the
tested `C,dCdt,R` moment closure, state-matched event-local precursor,
propagation route, or universal recent-history rule.

## Narrative

Laboratory midge swarms are cohesive even though they lack the
flock-like global velocity order that would make a simple global
alignment explanation natural. The 3xxx and 4xxx exploratory routes
therefore asked a sequence of progressively narrower questions. First,
can global or local affine geometry absorb the apparent transition
signal? Second, if a local residual remains, is it stable enough to be
treated as a reproducible observable? Third, can that observable be
reduced to a small state description, an event-local precursor, or a
simple history rule?

The answer after the 413x synthesis is not a single mechanism. Instead,
the analysis isolates a reproducible phenomenon and defines its
boundaries. T1 survived local affine subtraction in 15/19
observations and in both original scale settings in
14/19 observations. Among the survivor observations,
14/15 were robust to nearby scale and
lag choices. The strongest repeated form was diffuse tangential
activity (13/14), while edge/core,
near-pre, signed, and recent-history patterns were more bounded.

The subsequent negative and boundary tests are central to the story.
The `C,dCdt,R` first/second moment closure did not improve stably under
grouped out-of-sample validation. The state-matched event-locality test
did not show robust near-pre excess at true transition timestamps.
Recent history separated T1 in some observations, but its direction and
order were not stable. Propagation was not confirmatorily tested in the
current route and should remain in the open mechanism space.

Observation heterogeneity should therefore be written as part of the
result. Robust survivors, fragile boundaries, and stable failures are
all needed to describe the empirical domain of the phenomenon. Metadata
associations can organize this heterogeneity descriptively, but they
cannot be promoted to causal explanations.

## Results Architecture

| section | figure | purpose |
| --- | --- | --- |
| Methods / Data orientation | Figure 1 | Define the raw data, affine reductions, frozen T1 observable, and event-aligned profile source. |
| Results 1 | Figure 2 | Show common but non-universal local non-affine T1 survival across observations. |
| Results 2 | Figure 3 | Show diffuse tangential activity as the most stable repeated form and bound edge/core, near-pre, and signed structure. |
| Results 3 | Figure 4A | Report the failure of the tested C,dCdt,R moment-closure reduction. |
| Results 4 | Figure 4B | Report the failure of the tested state-matched event-local near-pre excess route. |
| Results 5 | Figure 4C | Report observation-specific history separation without a universal history rule. |
| Results 6 / Discussion | Figure 5 | Treat observation heterogeneity as a mapped boundary of the result. |

## Figure Architecture

| figure_id | title | main_question | claim_status | must_not_claim |
| --- | --- | --- | --- | --- |
| Figure 1 | Data and T1 Measurement Definition | What are the data, reductions, and frozen T1 observable? | orientation_only | The schematic is a physical mechanism or a fitted interaction model. |
| Figure 2 | T1 Survival Across Observations | Does the T1 residual survive local affine subtraction across observations? | main_allowed_with_boundary | T1 survival is universal across all observations. |
| Figure 3 | Spatial and Timing Structure | What repeated form does the surviving T1 residual take? | main_allowed_with_boundary | A universal edge trigger, signed force, or sharp precursor has been identified. |
| Figure 4 | Reduction Boundaries | Which simple reductions fail or remain outside the tested route? | main_allowed_with_boundary | Stochastic dynamics, transition dynamics, propagation, or history effects do not exist. |
| Figure 5 | Observation Heterogeneity | How do positive and boundary results vary across the 19 observations? | main_allowed_with_metadata_boundary | Metadata or recording condition causally explains the classes. |

## Evidence-to-Claim Map

| claim_id | main_figure | supporting_metrics | allowed_strength | boundary | forbidden_stronger_claim |
| --- | --- | --- | --- | --- | --- |
| C1_LOCAL_NONAFFINE_SURVIVAL | Figure 2 | 15/19 any-k survival; 14/19 both-k survival | SUPPORTED_WITH_BOUNDARY | Ob1, Ob3, Ob6, Ob8 fail or remain boundary cases. | T1 is universal or causal. |
| C2_SCALE_LAG_ROBUST_SURVIVORS | Figure 2 | 14/15 robust among tested survivor observations | SUPPORTED_WITH_BOUNDARY | This is survivor-class robustness, not an all-19 claim. | Scale/lag robustness holds for all observations. |
| C3_DIFFUSE_TANGENTIAL_DOMINANCE | Figure 3 | diffuse 13/14; near-pre 8/14; signed direction consistency 0.526 | SUPPORTED_WITH_BOUNDARY | Edge/core, near-pre, and signed structures are secondary or heterogeneous. | A universal edge trigger, sharp precursor, or signed force is identified. |
| C5_NO_SIMPLE_STATE_MOMENT_CLOSURE | Figure 4A | median incremental R2 first=-0.000633, second=-0.000621; positive-ob fractions 0.211/0.158 | NOT_SUPPORTED | Only this low-dimensional moment-closure form is tested. | Stochastic dynamics or all state dependence are impossible. |
| C6_NO_EVENT_TIMESTAMP_EXCESS | Figure 4B | median event-minus-matched-control A_pre_z=-0.0329; positive-ob fraction=0.421 | NOT_SUPPORTED | Only the state-matched near-pre aggregate route is tested. | Transitions have no special dynamics. |
| C7_OBSERVATION_SPECIFIC_HISTORY_BOUNDARY | Figure 4C | 14/19 beat shuffled-history median; 6/19 beat q95; median null gap=0.0341 | BOUNDARY | Direction/order consistency fails across observations. | A universal memory, hysteresis, or causal history mechanism is proven. |
| C8_PROPAGATION_NOT_CONFIRMATORILY_TESTED | Limitations / remaining open mechanism space | route stopped before confirmatory propagation after the event-locality gate failed | NOT_TESTED | Open route, not a negative result. | No propagation exists. |

## Strongest Bounded Claim

Laboratory midge swarms exhibit a reproducible local non-affine
tangential motion signature that survives local affine geometric
subtraction in most observations, yet resists several natural
low-dimensional reductions and displays explicit observation-level
heterogeneity.

## Terminal 413x Decision

`4135` closes the 413x synthesis route. The next action should be paper
development or deliberate opening of a new branch, not an automatic
continuation of mechanism search inside 413x.
