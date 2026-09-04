# 标题与摘要中文讨论稿 v3

## 1. 本部分的写作目的

在 02-06 的当前版本中，文章主线已经比最初更清楚：

> 本文不是证明一个完整的摇蚊群机制，而是识别一个在局部仿射几何扣除后仍然可测、在多数观测中出现、但不能被当前简单状态/事件/历史变量稳定解释的局部切向非仿射活动。

因此，01 的标题和摘要也需要相应调整。它不应该把文章写成单纯的方法论文，也不应该把结果写成普适机制发现。更合适的身份是：

> 一篇现象识别与解释边界论文：先分离一个可测的局部残差层，再说明它常见但不普适、可测但未闭合。

## 2. 当前推荐标题

中文理解版：

> 局部仿射扣除揭示实验室摇蚊群中持续存在的局部切向非仿射活动

英文工作标题：

> Local Affine Subtraction Reveals Persistent Tangential Non-Affine Activity in Laboratory Midge Swarms

这个标题比旧标题更适合当前投稿前版本。它有三个优点：

1. `Local affine subtraction` 把方法核心放在标题最前面，读者能立刻知道我们先扣除了普通局部几何。
2. `reveals persistent tangential non-affine activity` 强调主要正结果是“扣除后仍然可见”，不是直接声称机制。
3. 标题比旧版更短，更适合 JRSI 风格；紧致状态约简和解释边界放在摘要与正文中展开。

需要注意的是，标题里的 `reveals` 不应理解为发现了一个完整机制，而是指：在本文测试的局部仿射扣除下，T1 仍然作为一个可测残差层出现。

## 3. 备选标题

### 方向 A：更短、更稳

> Local Tangential Non-Affine Activity Persists in Laboratory Midge Swarms After Local Affine Subtraction

优点是短。缺点是边界不够清楚，读者不一定知道本文强调的是“扣除后仍然存在”。

### 方向 B：更强调残差层

> A Measurable Local Residual Layer in Laboratory Midge Swarms After Affine Subtraction

优点是很贴近 06 的主线。缺点是标题里没有出现 `non-affine` 和 `tangential`，可能不够具体。

### 方向 C：更强调现象边界

> Common but Non-Universal Local Non-Affine Motion in Laboratory Midge Swarms

优点是边界很清楚。缺点是标题显得更像结果总结，方法层次和 compact-state reduction 不明显。

## 4. 摘要中文版本

实验室摇蚊群在缺少强全局速度对齐的情况下仍然保持凝聚，因此适合用来研究一个基本问题：当普通几何运动被扣除后，群体运动中是否还保留可测的局部组织。这个问题很重要，因为在非刚体生物群体中，不同位置的个体速度本来就可能不同；只有先允许局部旋转、伸缩、压缩和剪切等几何变形，剩余运动才更有解释价值。

本文重新分析了 19 个 *Chironomus riparius* 实验室摇蚊群的三维轨迹数据。我们定义了一个局部切向非仿射活动量 T1。T1 不是原始个体速度，也不是推断出的力；它由焦点个体邻域中的有限滞后相对邻居位移计算得到，在等权局部仿射变形被拟合并扣除后，再取相对于群体中心径向方向的切向残差活动。

结果显示，在冻结的 centered-detrending 定义和双尺度一致性要求下，T1 在 14/19 个观测中存活。进一步的 full-pipeline pseudo-event omnibus calibration 显示，1000 次零假设重复中没有一次达到这一双尺度存活数，plus-one empirical p 约为 0.001；局部仿射拟合的 conditioning quality control 也显示拟合数值状态健康。不过，detrending challenge 同时说明精确的 14/19 不能被理解为预处理不变结论：past-only detrending 下双尺度支持为 11/19，不做 rolling detrending 时为 13/19。因此，比较稳妥的说法是多数观测中存在可测残差，而不是固定的 14/19 普适规律。在幸存类观测中，对邻近尺度和时间滞后扰动的支持保持稳定。T1 最稳定的重复形态是弥散性切向活动；相比之下，near-pre timing、edge/core contrast 和 signed event-type structure 都更弱或更异质。

进一步的解释检验没有把 T1 稳定约简到简单变量上。紧致状态变量没有在 grouped out-of-sample 的一阶或二阶矩预测中提供稳定增益；真实转变时间在状态匹配控制后也没有显示稳定的 near-pre excess；近期历史在部分观测中有信息，但没有形成普适记忆律。总体而言，本文将 T1 识别为一个介于原始个体轨迹和低维群体状态之间的可测局部残差层。它是常见但不普适的经验对象，而不是一个完成的机制解释。

## 5. 英文摘要工作版

> Laboratory midge swarms remain cohesive without strong global velocity alignment, making them useful for asking which components of collective motion remain after ordinary local geometry is removed. We re-analyzed nineteen three-dimensional trajectories of *Chironomus riparius* swarms and defined T1 as a local tangential non-affine activity computed from focal-neighborhood relative displacements after local affine deformation was fitted and subtracted. Under a frozen centered-detrending definition and a two-scale consistency requirement, T1 survived in 14 of 19 observations. A completed full-pipeline pseudo-event calibration found that none of 1000 null replicates reached this count (plus-one empirical p approximately 0.001), and local-affine conditioning quality control found well-conditioned fits. However, a detrending challenge reduced both-scale support to 11 of 19 under past-only detrending and 13 of 19 without rolling detrending, so the exact 14 of 19 count should not be read as preprocessing-invariant. Within the survivor class, support remained stable under nearby scale and temporal-lag perturbations. The most repeatable phenotype was diffuse tangential activity, whereas near-pre timing, edge/core contrast, and signed event-type structure were weaker or more heterogeneous. Compact state variables did not provide stable grouped out-of-sample improvement for first- or second-moment prediction, and true transition timestamps did not add robust near-pre excess after state-matched controls. Recent state-path history was informative in some observations but did not define a universal memory rule. These results identify T1 as a measurable local residual layer between raw individual trajectories and low-dimensional swarm state. The contribution is therefore diagnostic rather than mechanistic: T1 is common under the tested local affine reduction, but not universal or fully explained by the reductions examined here.

## 6. 当前 01 的写作判断

当前 01 应该突出三个信号：

1. 研究对象：实验室摇蚊群中的局部切向非仿射活动。
2. 主结果：T1 在冻结主分析中 14/19 双尺度存活，B=1000 omnibus null 支持该计数不是容易由 pseudo-events 复现。
3. 贡献边界：它是一个可测残差层，不是完整机制；14/19 的精确计数不具有预处理不变性，当前简单状态、事件时间和历史变量也没有稳定解释它。
