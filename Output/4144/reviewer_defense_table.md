# 4144 Reviewer Defense Table

Node: `4144_definition_notation_figure_cleanup`
Date: 2026-09-02

| Reviewer concern | 414x response | Evidence | Manuscript boundary |
| --- | --- | --- | --- |
| Is the 14/19 survival count larger than a pipeline-level null? | 4141 ran a full-pipeline pseudo-event smoke null. | Observed N_both=14; null mean=4.49, q95=8, max=11, plus-one p=0.0099 over B=100. | Call this smoke-level calibration unless B>=1000 is run. |
| Does centered detrending use future information? | 4142 compared centered, past-only, and no-detrend definitions. | N_both was 14/19, 11/19, and 13/19, respectively. | The exact 14/19 count is centered-detrending dependent. |
| Could local affine subtraction be numerically unstable? | 4143 tested rank sufficiency and condition numbers. | 38/38 observation-k combinations passed; median condition number 2.37. | This is a numerical QC pass, not a mechanism proof. |
| Are the figures traceable to outputs? | 4144 checked 4134 source mapping and LaTeX figure copies. | 5/5 final figure packages are present in LaTeX. | Figures remain evidence panels, not camera-ready final graphics. |

## Claim Boundary Updates

| claim_id | claim_strength_after_4144 | evidence_update | allowed_statement | boundary_statement |
| --- | --- | --- | --- | --- |
| C1_T1_LOCAL_NONAFFINE_SURVIVAL | supported_bounded | Observed N_both=14/19 and N_any=15/19; 4141 smoke null p_both=0.009901, null q95=8, null max=11. | T1 is a common local tangential non-affine residual after local affine subtraction under the frozen event-control gate. | This does not establish universality, mechanism, or a formal high-B omnibus p-value. |
| C2_DETRENDING_BOUNDARY | boundary_supported | Centered detrending reproduced N_both=14/19; past-only gave N_both=11/19; no-detrend robust-z gave N_both=13/19. | The T1 signal is not erased by the detrending challenge, but the exact 14/19 both-scale count is tied to centered detrending. | Do not describe the main count as fully invariant to causal past-only detrending. |
| C3_LOCAL_AFFINE_CONDITIONING_QC | artifact_control_pass | 38/38 observation-k combinations passed; all 19/19 observations passed both k values; median condition number=2.37, max q95 condition number=6.28; fraction condition>100=0. | The local affine subtraction used for T1 is numerically defensible in the sampled all-observation QC. | This does not prove the biological correctness of T1 or remove all possible preprocessing artifacts. |
| C4_DIFFUSE_NEAR_PRE_TIMING | descriptive_bounded | Near-pre all-tangential gate counts were centered 11/14, past-only 8/14, and no-detrend 12/14. | Near-pre timing is a moderate descriptive profile within the diffuse tangential phenotype. | Because state-matched event-locality failed earlier, do not write near-pre timing as a causal precursor. |
| C5_SURVIVOR_CLASS_ROBUSTNESS | supported_with_scope_limit | The pre-4144 survivor class remains the scale/lag robustness scope: 14/15 survivor observations were robust to nearby scale and lag perturbations. | Robustness is high inside the survivor class after the main survival screen. | Do not generalize survivor-class robustness to all 19 observations. |
| C6_NEGATIVE_REDUCTION_BOUNDARIES | supported_negative_boundary | Compact state moment closure, state-matched near-pre event-locality, and universal history-rule routes remained insufficient in the earlier 4090/4100/4121 chain. | The paper can report tested reduction boundaries as part of the contribution. | A failed tested reduction is not evidence that all mechanisms or all stochastic descriptions are impossible. |

## Review 007 Gap Resolution

| item | 4144_resolution | evidence | remaining_boundary | 4145_action |
| --- | --- | --- | --- | --- |
| condition-number QC | resolved_pass | 4143 passed 38/38 observation-k combinations; median condition number 2.37. | Sampled QC only; not a proof against every preprocessing artifact. | Add a methods/results QC sentence for local affine conditioning. |
| full-pipeline omnibus null | partially_resolved_smoke | 4141 smoke null B=100: observed N_both=14, null q95=8, null max=11, plus-one p=0.009901. | Use as runtime-validated supportive calibration, not formal inference. | Mention as smoke-level calibration or defer formal p-value language. |
| detrending challenge | resolved_boundary | 4142 result: centered 14/19, past-only 11/19, no-detrend 13/19 for both-scale support. | Exact 14/19 count is preprocessing-sensitive. | Soften local robustness language and state the detrending boundary. |
