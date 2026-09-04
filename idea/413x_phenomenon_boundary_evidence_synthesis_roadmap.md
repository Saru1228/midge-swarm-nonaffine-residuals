# 413x 系列路线：Phenomenon-and-Boundary Evidence Synthesis

**文档类型**：Idea / EGRT Synthesis Roadmap / Manuscript Preparation Spec  
**日期**：2026-08-27  
**本版整理**：2026-08-27 implementation review after 4125  
**承接节点**：`4125_state_path_history_synthesis`  
**研究对象**：3D 摇蚊群（midge swarm）trajectory data  
**数据范围**：all 19 observations  

**上游分类**

```text
408x  bounded local non-affine tangential signal
409x  bounded stochastic-negative result
410x  T0 no event-local information beyond matched continuous state
412x  P1 observation-specific history dependence boundary
```

**413x 定位**

> 不再继续寻找新的统一机制，而是把已经完成的 positive / negative / boundary evidence 整理成一个清晰、可复核、可写入论文的“现象与边界”结果体系。

**推荐主线**

```text
4130 -> 4131 -> 4132 -> 4133 -> 4134 -> 4135
```

**执行状态（2026-08-28）**

```text
completed_chain =
    4130_definition_and_evidence_registry
    4131_robust_positive_phenomenon_atlas
    4132_negative_mechanism_boundary_atlas
    4133_observation_heterogeneity_map
    M5_REVIEW_before_4134
    4134_figure_ready_evidence_panels
    4135_manuscript_style_technical_synthesis

latest_completed_node = 4135_manuscript_style_technical_synthesis

latest_gate_result = pass_4135_manuscript_synthesis_complete_terminal_413x

4130_registry_counts =
    definitions 10
    evidence_rows 24
    claim_strength_rows 8
    metadata_audit_rows 4

4130_source_counts =
    decision_json_sources 23
    summary_only_sources 1

4131_positive_atlas =
    atlas_rows 6
    primary_positive_rows 3
    secondary_bounded_positive_rows 2
    figures 4
    gate pass_4131_positive_atlas_ready_with_secondary_boundaries

4132_negative_boundary_atlas =
    atlas_rows 8
    not_supported_rows 2
    boundary_rows 3
    not_tested_rows 1
    supported_with_boundary_geometry_rows 2
    figures 4
    gate pass_4132_negative_boundary_atlas_ready

4133_observation_heterogeneity_map =
    master_table_rows 19
    class_counts =
        robust_survivor_diffuse_positive 13
        fragile_408x_boundary 2
        stable_408x_failure 2
        fragile_survivor 1
        robust_survivor_without_diffuse_gate 1
    tested_associations 12
    moderate_or_weak_moderate_descriptive 4
    figures 5
    gate pass_4133_heterogeneity_map_ready_with_metadata_boundary

M5_REVIEW_before_4134 =
    review_gates 8
    pass_gates 6
    metadata_boundary_gates 1
    action_required_gates 1
    stop_gates 0
    figure_candidate_panels 16
    claim_review_rows 8
    overclaim_risk_rows 8
    gate pass_M5_review_enter_4134_with_actions

4134_figure_ready_evidence_panels =
    main_figures 5
    panel_metadata_rows 16
    figure_source_rows 16
    preview_figures 5
    missing_panel_sources 0
    gate pass_4134_figure_panel_package_ready_for_4135

4135_manuscript_style_technical_synthesis =
    title_candidates 5
    main_claim_rows 8
    evidence_to_claim_rows 7
    section_to_figure_rows 7
    writing_boundary_rows 7
    missing_input_sources 0
    gate pass_4135_manuscript_synthesis_complete_terminal_413x

current_boundaries =
    metadata-dependent heterogeneity can be used only as descriptive annotation
    propagation is NOT_TESTED rather than disproven
    history and signed-direction effects are observation-specific, not universal
    ob index/order proxy association is descriptive only
    mean track length association is exploratory, not causal
    Figure 1 has been built as data/definition orientation, not a mechanism
    4134 figure previews are evidence-panel package outputs, not camera-ready final publication graphics
    4135 closes the 413x synthesis route and does not automatically reopen mechanism search

next_node =
    paper_or_report_development_from_4134_4135
```

**本版执行主线**

```text
4130A  definition dictionary
4130B  evidence registry
4130C  claim strength registry
4130D  metadata source audit
        |
        v
M5.0 REVIEW
        |
        +--> if definitions inconsistent:
        |       fix registry, do not write claims
        |
        v
4131  positive phenomenon atlas
4132  negative mechanism boundary atlas
        |
        v
4133  observation heterogeneity map
        |
        v
M5 REVIEW
        |
        v
4134  figure-ready evidence panels
        |
        v
4135  manuscript-style technical synthesis
```

**实施可能性判断**

```text
overall_feasibility = high
code_risk = low_to_medium
writing_risk = medium
metadata_risk = medium_to_high
main_risk =
    overclaiming negative/boundary results
    or merging incompatible target definitions
```

---

# 0. 核心目标

413x 不是新机制路线。

它不问：

```text
还有没有一个新的模型能解释 T1？
```

它问：

> 目前关于 T1，究竟有哪些结果已经稳健成立？哪些机制已经被约束或排除？哪些 observation heterogeneity 是真实边界？这些证据如何组织成一个论文级科学故事？

413x 的终点是：

```text
evidence architecture
+
figure architecture
+
manuscript architecture
```

冻结核心对象：

```text
T1 = local tangential non-affine residual
```

当前最稳妥总表述：

> Most observations contain a transition-linked local tangential non-affine residual after local affine deformation is removed, but this residual does not reduce cleanly to a universal low-dimensional stochastic state rule, event-specific precursor, propagation process, or universal recent-history mechanism.

中文：

> 多数 observation 中，在扣除局部仿射形变后仍保留与 compact-density dynamics 相关的局部非仿射切向残余；但该残余无法稳定约化为统一的低维随机状态规则、事件特异前兆、传播过程或普适 recent-history 机制。

---

# 1. 当前证据链

```text
4xxx global geometry stage
    |
    v
408x local affine reduction
    |
    |  T1 survives in most observations
    v
409x low-dimensional moment closure
    |
    |  C,dCdt,R first/second moments fail
    v
410x state-matched event-locality
    |
    |  event timestamps not special after matching
    v
412x state-path/history
    |
    |  observation-specific separation exists
    |  but no universal direction/order
    v
413x synthesis
```

---

# 2. 节点总览

```text
4130  Results inventory / evidence registry
4131  Robust positive phenomenon atlas
4132  Negative mechanism boundary atlas
4133  Observation heterogeneity map
4134  Figure-ready evidence panels
4135  Manuscript-style technical synthesis
```

所有节点只做整理、复核、标准化、可视化和论文化。

**禁止在 413x 中新增机制模型。**

**413x 的工作类型**

```text
allowed:
   整理
   复核
   标准化
   可视化
   证据到 claim 的映射
   论文级表达

not_allowed:
   新增 residual target
   新增强机制模型
   为获得正结果重调旧 threshold
   把未测试路线写成已否定路线
```

---

# 3. Milestones

## M5.0 — Evidence Inventory Complete

所有关键节点、claim、metric、null、gate、boundary 被统一登记。

## M5.1 — Positive Phenomenon Locked

可以用 3–5 条简洁语句准确描述：

```text
what T1 is
where it survives
how robust it is
what spatial/timing structure is strongest
```

## M5.2 — Negative Boundary Locked

清楚区分：

```text
unsupported
bounded
not tested
technically invalid
```

## M5.3 — Heterogeneity Characterized

明确：

```text
which observations are robust
which are fragile
which are stable failures
which show observation-specific history effects
```

## M5.4 — Figure Set Frozen

生成：

```text
main figures
supplementary figures
evidence tables
```

## M5.5 — Manuscript Story Frozen

形成：

```text
Title candidate
Abstract skeleton
Results sections
Discussion boundaries
Limitations
Main claims
```

---

# 4. 4130 — Results Inventory / Evidence Registry

## Question

> 当前所有关键实验到底支持什么、否定什么、留下什么边界？

## Scope

优先纳入：

```text
4080–4088
4090A
4090B
4090
4094
4100A
4100
4105
4120
4121
4125
```

必要时向前补：

```text
4001
405x
4060
407x
```

但只保留与 T1 证据链直接相关的节点。

## Evidence Registry

建立：

```text
Output/4130/evidence_registry.csv
```

字段至少：

| field | meaning |
|---|---|
| node | node id |
| question | scientific question |
| target | target observable |
| data_scope | observations used |
| baseline | baseline |
| null | null model |
| primary_metric | primary metric |
| gate | predefined gate |
| result | pass/fail/boundary |
| claim_class | positive/negative/boundary/technical |
| robustness | scale/lag/observation robustness |
| supported_claim | allowed claim |
| unsupported_claim | disallowed stronger claim |
| next_route_meaning | routing consequence |
| main_artifact | source summary/output |
| figure_candidate | yes/no |

## Definition Dictionary

4130 必须先建立定义字典，否则 4131–4135 容易把不同层级的结果混写。

建立：

```text
Output/4130/definition_dictionary.csv
```

字段至少：

| field | meaning |
|---|---|
| term | variable / observable / class name |
| canonical_definition | canonical definition used in 413x |
| source_node | where the definition was frozen |
| source_file | output or script that defines it |
| unit_of_analysis | frame / focal / observation / event / pair |
| aggregation_level | individual / focal-neighborhood / swarm / observation |
| allowed_aliases | names that can be treated as same definition |
| incompatible_aliases | similar names that must not be merged |
| notes | caveats |

必须特别冻结：

```text
T1
A_swarm_tangential_z
all_tangential
shell_edge_minus_core
C
dCdt
R
h500_theta_h
event-local near-pre activity
observation-level effect strength
```

## Claim Strength Registry

建立：

```text
Output/4130/claim_strength_registry.csv
```

字段至少：

| field | meaning |
|---|---|
| claim_id | short stable id |
| claim_text | allowed claim |
| claim_strength | SUPPORTED / SUPPORTED_WITH_BOUNDARY / BOUNDARY / NOT_SUPPORTED / NOT_TESTED / TECHNICAL |
| support_nodes | supporting nodes |
| required_conditions | definitions/gates where claim is valid |
| boundary_observations | explicit exceptions |
| forbidden_stronger_claim | overclaim to avoid |
| figure_priority | main / supplement / none |

## Claim Class Vocabulary

只允许：

```text
SUPPORTED
SUPPORTED_WITH_BOUNDARY
NOT_SUPPORTED
BOUNDARY
TECHNICAL_PASS
TECHNICAL_STOP
NOT_TESTED
```

禁止模糊表述：

```text
maybe
seems
probably mechanism
```

## Claim Dependency Graph

必须生成：

```text
4001 global affine residual
        |
        v
4088 local non-affine T1
        |
        +--> 4094 no C,dCdt,R moment closure
        |
        +--> 4105 no event-local excess after state matching
        |
        +--> 4125 observation-specific history boundary
```

## Stop Rule

如果 evidence registry 中出现：

```text
same claim
supported by incompatible definitions
```

标记：

```text
definition_inconsistency
```

在 4131 前解决，不可静默合并。

## Output

```text
Output/4130/
    definition_dictionary.csv
    evidence_registry.csv
    evidence_registry.json
    claim_strength_registry.csv
    metadata_source_audit.csv
    claim_dependency_graph.md
    route_timeline.md
    4130_summary.md
```

---

# 5. 4131 — Robust Positive Phenomenon Atlas

## Question

> 如果只保留目前最稳健的正结果，T1 现象到底长什么样？

## Primary Positive Claims

### P1 — Local affine survival

> Local affine deformation does not fully remove the transition-linked tangential residual in most observations.

### P2 — Cross-observation commonality

```text
15/19 pass at >= 1 original k
14/19 pass both original k values
```

应写：

```text
common
not universal
```

### P3 — Scale/lag robustness

robust survivor class：

```text
14/15 robust
```

### P4 — Diffuse tangential dominance

```text
all_tangential stronger
than
edge-core contrast
```

### P5 — Observation-specific history sensitivity

4121：

```text
14/19 real > shuffled-history median null
```

但：

```text
direction consistency fails
```

所以只列为：

```text
secondary bounded positive
```

## Atlas Schema

每个 positive phenomenon：

```text
phenomenon_name
definition
primary metric
observation coverage
effect-size distribution
robustness
boundary cases
allowed wording
disallowed wording
best figure
```

## Positive Atlas Table

| phenomenon | support | robustness | strongest wording |
|---|---|---|---|
| local non-affine T1 survival | strong | high in survivor class | supported with boundary |
| diffuse tangential activity | strong | repeated | primary spatial/activity form |
| edge/core contrast | moderate | partial | secondary |
| near-pre timing | moderate | partial | descriptive timing |
| signed direction | heterogeneous | low | no universal sign rule |
| recent-history separation | observation-specific | boundary | descriptive only |

## Figure Candidates

```text
P1 all-19 T1 effect-size forest plot
P2 scale/lag robustness heatmap
P3 all_tangential vs shell_edge_minus_core
P4 near-pre timing profile
P5 4121 real-vs-history-shuffle distribution
```

## Output

```text
Output/4131/
    positive_phenomenon_atlas.csv
    positive_claims.md
    positive_wording_guide.md
    figures/
    4131_summary.md
```

---

# 6. 4132 — Negative Mechanism Boundary Atlas

## Question

> 哪些自然机制解释已经被当前数据和 gate 明确约束？

## 核心原则

negative result 不能写：

```text
mechanism does not exist
```

而应写：

> under the tested definition / baseline / null / validation scheme, this mechanism class did not provide a stable reduction.

## Boundary Classes

### N1 — Global affine geometry insufficient

```text
geometry baseline insufficient
```

### N2 — Local affine geometry insufficient in most observations

形成：

```text
local non-affine residual
```

### N3 — Low-dimensional state moment closure unsupported

4090：

```text
C,dCdt,R
first moment = fail
second moment = fail
```

### N4 — Event-specific precursor unsupported

4100：

```text
true transition timestamp
does not exceed
state-matched non-event
```

### N5 — Propagation route not entered

必须标：

```text
propagation = NOT TESTED CONFIRMATORILY
```

因为 4100 gate 失败后 stop-before-4101。

不能写：

```text
no propagation exists
```

### N6 — Universal recent-history rule unsupported

4121：

```text
history separation exists in some observations
BUT
sign/order not cross-observation stable
```

### N7 — Pair-core / mesoscopic field boundaries

若纳入 405x/4060，必须保留：

```text
threshold sensitivity
stationary field failure
```

## Boundary Atlas Schema

```text
mechanism_class
tested_node
tested_form
baseline
null
failure_mode
replication
what_is_ruled_out
what_remains_open
allowed_wording
forbidden_wording
```

## Example Wording

Allowed：

> A `C,dCdt,R`-conditioned low-dimensional moment closure was not stable across observations.

Forbidden：

> Stochastic dynamics do not explain midge swarms.

Allowed：

> Transition timestamps did not contain robust excess T1 activity beyond state-matched non-event moments.

Forbidden：

> Transitions have no special dynamics.

Allowed：

> Recent path direction showed observation-specific T1 separation without a universal sign/order.

Forbidden：

> History does not matter.

## Output

```text
Output/4132/
    negative_boundary_atlas.csv
    bounded_negative_claims.md
    forbidden_overclaims.md
    mechanism_space_remaining.md
    figures/
    4132_summary.md
```

---

# 7. 4133 — Observation Heterogeneity Map

## Question

> 19 个 observations 之间的 heterogeneity 到底是什么结构？

## 必须保留的 Observation Labels

```text
Ob1/Ob3 = fragile narrow-setting boundary
Ob6/Ob8 = stable 408x failures
Ob4 = fragile survivor
```

## Dataset Metadata

至少整理：

```text
observation id
dataset length
mean swarm size
mean track length
recording condition if available
```

已知数据说明中：

```text
Ob6 and Ob11 = daytime
others mainly dusk
```

当前执行要求：

```text
recording_condition
metadata_source
verification_status
```

其中 `verification_status` 只允许：

```text
VERIFIED
UNVERIFIED
MISSING
```

如果只在当前 roadmap 中出现 `Ob6/Ob11 = daytime`，而没有独立 reference/source 支撑，则必须写：

```text
verification_status = UNVERIFIED
use = descriptive_annotation_only
```

这只能用于 descriptive association，不得作为 causal conclusion。

## Observation Master Table

建立：

```text
Output/4133/observation_master_table.csv
```

字段建议：

```text
ob
dataset_length
mean_swarm_size
mean_track_length
recording_condition
recording_condition_source
recording_condition_verification_status
408x_T1_effect
408x_pass_class
408x_robustness
4084_diffuse_effect
4084_edge_core_effect
4085_near_pre_effect
4090_first_moment_gain
4090_second_moment_gain
4100_event_local_effect
4121_history_signed_effect
4121_history_abs_effect
4121_null_gap
```

## Primary Questions

### HET1

408x strong/weak observations 是否与 swarm size / track length 有关系？

### HET2

4121 history-effect magnitude 是否与 408x T1 strength 有关系？

### HET3

Ob6/Ob8 是否在多个 route 中形成 consistent failure pattern？

### HET4

early-observation pattern 是否仍存在？

如果没有真实 recording-order metadata：

```text
ob_index only proxy
```

必须明确。

## Analysis Rules

n=19，因此：

```text
no high-dimensional ML
no feature fishing
no causal metadata claims
```

允许：

```text
Spearman
Theil-Sen
leave-one-observation-out
simple scatter
rank comparison
```

## Figure Candidates

```text
H1 observation × route evidence matrix
H2 T1 effect vs swarm size
H3 T1 effect vs mean track length
H4 4121 abs history effect vs 408x T1 effect
```

## Output

```text
Output/4133/
    observation_master_table.csv
    heterogeneity_associations.csv
    leave_one_out_sensitivity.csv
    observation_classes.csv
    figures/
    4133_summary.md
```

---

# 8. 4134 — Figure-ready Evidence Panels

## Question

> 如果现在要写 paper/report，最少需要哪几张图才能完整讲清结果？

## Main Figure Architecture

### Figure 1 — Data + Geometry Reduction Concept

```text
A. 3D swarm trajectory snapshot
B. global affine vs local affine schematic
C. T1 definition
D. example time trace
```

目的：

> 告诉读者 T1 是什么。

### Figure 2 — T1 Survival Across Observations

```text
A. all-19 effect forest plot
B. k/lag robustness heatmap
C. survivor/failure classification
```

目的：

> 证明 local non-affine phenomenon common but not universal。

### Figure 3 — Spatial / Timing Structure

```text
A. all_tangential vs edge-core
B. near-pre profile
C. signed heterogeneity
```

目的：

> 说明最稳定的是 diffuse tangential activity，而不是单一 edge trigger 或统一 signed force。

### Figure 4 — Reduction Failures

```text
A. 4090 first/second moment OOS gains
B. 4100 state-matched event-locality
C. 4121 history effect vs shuffle null
```

目的：

> 核心 mechanism-boundary figure。

### Figure 5 — Observation Heterogeneity

```text
A. observation × route matrix
B. T1 strength vs dataset metadata
C. strongest positive/negative observations
```

目的：

> 把 heterogeneity 从 nuisance 变成结果。

## Supplementary Figures

```text
S1 local affine fit QC
S2 408x sensitivity
S3 4100 matching quality
S4 4120 leakage audit
S5 4121 sensitivity
S6 dataset metadata distributions
```

## Figure Rule

每张主图必须回答一个问题。

每个 panel 必须记录：

```text
question
metric
sample size
null/baseline
interpretation
```

## Figure Source Map

建立：

```text
figure_id
panel
source_node
source_file
source_metric
processing_needed
final_caption_claim
```

## Output

```text
Output/4134/
    main_figure_plan.md
    supplementary_figure_plan.md
    figure_source_map.csv
    figure_caption_drafts.md
    figures/
    4134_summary.md
```

---

# 9. 4135 — Manuscript-style Technical Synthesis

## Question

> 当前证据最适合形成怎样的一篇论文级 technical story？

## 推荐论文主问题

> **What components of collective midge motion remain after progressively removing global geometry, local affine deformation, low-dimensional state dependence, event timing, and simple recent-history explanations?**

中文：

> **在逐级扣除全局几何、局部仿射形变、低维状态依赖、事件时序和简单 recent-history 解释后，摇蚊群运动中还剩下哪些可重复的不可约组织？**

## Title Candidates

### Conservative

**Local non-affine organization in laboratory midge swarms beyond affine geometry and low-dimensional state descriptions**

### Concise

**Local non-affine collective organization in laboratory midge swarms**

### Stronger but bounded

**A robust local non-affine motion signature in disordered midge swarms resists simple low-dimensional reduction**

## Abstract Skeleton

### Background

Midge swarms show collective cohesion without flock-like global order.

### Question

Can residual collective motion be reduced to ordinary geometry or a small set of low-dimensional state variables?

### Methods

```text
global/local affine subtraction
transition-conditioned analysis
state-matched controls
grouped OOS moment classification
same-state/different-history matching
```

### Results

```text
1. local affine subtraction leaves T1 in most observations
2. T1 is robust across nearby local scales/lags
3. diffuse tangential activity is stronger than edge/core localization
4. C,dCdt,R moment closure fails
5. event timestamps add no state-matched excess
6. recent path direction gives observation-specific but non-universal separation
```

### Conclusion

> The most reproducible signal is therefore a bounded local non-affine collective observable rather than a simple universal control law.

---

# 10. Results Section Architecture

## Results 1

**A local non-affine tangential residual survives local geometry**

对应：

```text
4080–4088
```

## Results 2

**The residual is common but heterogeneous across observations**

对应：

```text
4081c
4082
4087
4133
```

## Results 3

**Its dominant structure is diffuse tangential activity rather than a stable edge/core trigger**

对应：

```text
4084–4086
```

## Results 4

**Instantaneous compact-density state does not provide a stable moment closure**

对应：

```text
4090
4094
```

## Results 5

**Transition timestamps contain no extra activity beyond matched continuous state**

对应：

```text
4100
4105
```

## Results 6

**Recent path direction shows observation-specific, not universal, dependence**

对应：

```text
4120
4121
4125
```

---

# 11. Discussion Architecture

## D1 — What is genuinely robust

```text
local non-affine T1
diffuse tangential organization
cross-observation commonality with explicit failures
```

## D2 — What simple mechanisms are constrained

```text
local affine geometry
instantaneous low-dimensional moment closure
event-specific precursor
universal recent-history rule
```

## D3 — Why observation heterogeneity matters

讨论：

```text
finite swarm size
track length
recording condition
sampling regime
```

但不要过度解释。

## D4 — What remains open

```text
higher-dimensional path dependence
network organization
external perturbation response
individual-level causal interactions
```

必须标记：

```text
not resolved here
```

---

# 12. Limitations

至少包括：

1. observational data；
2. no intervention；
3. finite 19 observations；
4. local residual activity is focal-neighborhood aggregate；
5. observation heterogeneity；
6. transition coordinate derived from compact-density variables；
7. no direct causal inference；
8. no universal mechanism identified。

---

# 13. Main Claim Registry

4135 最终只允许 3–5 条 main claims。

建议：

### Claim 1

> Local affine deformation is insufficient to remove the transition-linked tangential residual in most observations.

### Claim 2

> The surviving residual is robust across nearby local scales and lags but is not universal across all observations.

### Claim 3

> The residual is not stably reduced by `C,dCdt,R`-conditioned first/second moments.

### Claim 4

> True transition timestamps do not contain robust excess activity beyond state-matched non-event moments.

### Claim 5

> Recent state-path direction can separate T1 within some observations, but the direction/order is not universal.

---

# 14. Strongest Overall Bounded Claim

推荐：

> **Laboratory midge swarms exhibit a reproducible local non-affine tangential motion signature that survives local affine geometric subtraction in most observations, yet resists several natural low-dimensional reductions and displays explicit observation-level heterogeneity.**

中文：

> **实验室摇蚊群在多数 observation 中表现出可重复的局部非仿射切向运动信号，该信号在扣除局部仿射几何后仍然存在，但无法被多种自然的低维约化稳定解释，并呈现明确的 observation-level heterogeneity。**

---

# 15. Forbidden Overclaims

禁止：

```text
new universality class
criticality discovered
causal memory
leader-follower mechanism
propagation wave
information transfer
universal hysteresis
topological mechanism proven
new field theory established
```

除非未来有独立证据。

---

# 16. 4135 Output

```text
Output/4135/
    manuscript_story.md
    title_candidates.md
    abstract_skeleton.md
    results_outline.md
    discussion_outline.md
    limitations.md
    main_claim_registry.csv
    evidence_to_claim_map.csv
    4135_summary.md
```

---

# 17. 与原始数据论文的关系

原始数据集强调：

```text
midge swarms:
    no net polarization
    weak/global velocity order absent
    swarm remains cohesive
```

19 个 observations 在：

```text
swarm size
track length
recording duration
recording condition
```

上存在明显差异。

因此 413x 应把 observation heterogeneity 当作真实 experimental context，而不是简单噪声。

特别注意：

```text
Ob6
Ob11
```

为 daytime recordings，其余大多为 dusk。

这个 metadata 可以进入 4133 descriptive table，但样本量太小，不能做强因果结论。

---

# 18. 与旧“场论 / RG / universality”路线的关系

项目早期有：

```text
field theory
RG
universality class
topological scaling
PDE
```

等方向。

413x 当前**不应该自动把这些旧设想重新接回主线**。

当前 408x–412x 证据支持的是：

```text
bounded non-affine phenomenon
+
reduction boundaries
+
heterogeneity
```

而不是：

```text
fixed point
universal critical exponent
hydrodynamic field equation
```

如果未来重新开启 RG / field route，必须从 413x 整理出的 robust observable 出发，重新定义可证伪问题。

---

# 19. Agent 执行顺序

```text
STEP 1
4130
build definition dictionary
build evidence registry
build claim strength registry
build metadata source audit

----- M5.0 REVIEW -----

IF definitions inconsistent:
    fix 4130 registry
    do not enter 4131/4132

IF claim strength ambiguous:
    downgrade to BOUNDARY or NOT_TESTED
    do not promote to main claim

STEP 2
4131
positive phenomenon atlas

STEP 3
4132
negative mechanism boundary atlas

STEP 4
4133
observation heterogeneity map

----- M5 REVIEW -----

IF heterogeneity depends on unverified metadata:
    keep as descriptive annotation
    do not make regime claim

IF a positive figure depends on survivor-only selection:
    move to supplement or rewrite with all-19 context

STEP 5
4134
freeze paper-ready figures

STEP 6
4135
write manuscript-style synthesis
```

---

# 20. Stop Conditions

## STOP-A

若 4130 发现：

```text
definitions inconsistent
```

先修 registry，不进入 4131。

## STOP-B

若某个 claimed positive result 只有：

```text
single observation
single threshold
single metric
```

降级为 exploratory，不进入 main figure。

## STOP-C

若 heterogeneity association 仅由 1 个 observation 驱动：

```text
do not make regime claim
```

## STOP-D

4135 完成后：

```text
do not automatically open 414x mechanism search
```

除非出现新的明确理论问题。

---

# 21. 明确禁止事项

1. 不要新增机制模型。
2. 不要新增 residual target。
3. 不要重新调 408x threshold。
4. 不要为 paper story 删除 negative observations。
5. 不要 survivor-only 写主结果。
6. 不要把 `NOT TESTED` 写成 `NOT SUPPORTED`。
7. 不要把 `NOT SUPPORTED` 写成“机制不存在”。
8. 不要 pooled significance 掩盖 observation heterogeneity。
9. 不要用 Ob index 代替真实 recording metadata。
10. 不要把 daytime/dusk 的 2-vs-17 imbalance 做成强结论。
11. 不要重新打开 attractor / propagation / pair-core / Langevin rescue。
12. 不要把 observation-specific history effect 强行 pooled 成 universal rule。
13. 不要把早期 RG / universality speculation 写进 main claim。
14. 不要为了图好看删 failure observations。
15. 不要写 causal language。

---

# 22. 统一 Output 结构

```text
Output/4130/
Output/4131/
Output/4132/
Output/4133/
Output/4134/
Output/4135/
```

每个 node：

```text
config.yaml
source_map.csv
decision.json
<node>_summary.md
figures/
tables/
```

---

# 23. Evidence-to-Claim Map

最终必须生成：

```text
Output/4135/evidence_to_claim_map.csv
```

字段：

```text
claim_id
claim_text
supporting_nodes
supporting_metrics
nulls
boundary_observations
robustness
forbidden_stronger_claim
main_figure
supplementary_figure
```

---

# 24. 最终 manuscript-ready 图逻辑

```text
Figure 1
What is T1?

Figure 2
Does T1 survive local geometry?
YES, in most observations

Figure 3
What form does T1 take?
Diffuse tangential > edge/core

Figure 4
Can simple low-dimensional mechanisms explain it?
No stable closure / event-local / universal history rule

Figure 5
How heterogeneous is it?
Explicit observation-level boundary
```

---

# 25. 最终 Scientific Narrative

> Laboratory midge swarms do not exhibit flock-like global order, but their motion contains reproducible local structure. After progressively removing global and local affine deformation, a local tangential non-affine residual remains in most observations. This residual is robust to nearby local scales and lags, yet is heterogeneous across observations. It is not captured by a simple `C,dCdt,R` moment closure, is not specifically enhanced at true transition timestamps after state matching, and does not obey a universal recent-history rule. The resulting picture is therefore one of a bounded, reproducible non-affine collective observable with explicit reduction limits, rather than a single universal low-dimensional mechanism.

中文：

> 实验室摇蚊群虽然缺乏类似鸟群或鱼群的全局速度有序，但其局部运动中仍存在可重复的组织结构。逐级扣除全局和局部仿射形变后，多数 observation 中仍保留局部非仿射切向残余。该残余对邻域尺度和时间 lag 具有一定稳健性，但在 observation 之间表现出明确异质性。进一步分析表明，它不能被 `C,dCdt,R` 条件下的简单 first/second moment closure 稳定解释；真实 transition timestamp 在 state matching 后也不表现出额外 near-pre 活动；recent state-path direction 虽在部分 observation 中可分离 T1，但不存在普适方向规律。因此，当前最稳妥的结论不是一个统一低维机制，而是一个具有明确边界、可重复的局部非仿射 collective observable。

---

# 26. 当前推荐决策

```text
current_node = 4135_manuscript_style_technical_synthesis

current_status = completed

latest_gate_result = pass_4135_manuscript_synthesis_complete_terminal_413x

next_node = paper_or_report_development_from_4134_4135

primary_goal =
    use the completed 413x synthesis for paper/report development or deliberate new-branch planning

new_mechanism_search_allowed = false

new_target_search_allowed = false

all_19_observations_required = true

completed_outputs =
    definition_dictionary
    evidence_registry
    claim_strength_registry
    metadata_source_audit
    positive_phenomenon_atlas
    positive_claims_from_4130
    positive_figure_plan
    negative_boundary_atlas
    bounded_negative_claims
    forbidden_overclaims
    mechanism_space_remaining
    observation_master_table
    heterogeneity_associations
    leave_one_out_sensitivity
    observation_classes
    m5_gate_review
    main_vs_supplement_figure_candidates
    claim_storyline_review
    overclaim_risk_register
    4134_action_checklist
    figure_source_map
    panel_metadata
    main_figure_manifest
    main_figure_plan
    supplementary_figure_plan
    figure_caption_drafts
    4134 figure previews
    title_candidates
    manuscript_story
    abstract_skeleton
    results_outline
    discussion_outline
    limitations
    main_claim_registry
    evidence_to_claim_map
    section_to_figure_map
    writing_boundary_checklist

pending_outputs =
    none inside 413x synthesis route

metadata_boundary =
    daytime/dusk and observation-order explanations remain descriptive only

mechanism_boundary =
    no stable C,dCdt,R moment closure
    no robust state-matched event-timestamp precursor
    propagation route not confirmatorily tested

heterogeneity_boundary =
    13 robust_survivor_diffuse_positive observations
    2 fragile_408x_boundary observations
    2 stable_408x_failure observations
    1 fragile_survivor observation
    1 robust_survivor_without_diffuse_gate observation
    strongest associations remain descriptive because n=19 and metadata are limited

main_scientific_product =
    bounded_reproducible_local_nonaffine_collective_observable_with_explicit_reduction_limits
```

---

# 27. 一句话总结

> **413x 不再继续追逐新的机制，而是把 408x–412x 已经形成的“local non-affine positive phenomenon + low-dimensional reduction failures + observation-specific boundaries”整理成一个可复核、可画图、可写论文的完整证据体系。**
