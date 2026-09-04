# 4145 Manuscript Reintegration Audit

Node: `4145_manuscript_reintegration`  
Date: 2026-09-02

## Result

`pass_4145_manuscript_reintegration_compiled`

4145 integrated the 4144 claim-boundary updates into the active `mypaper2`
LaTeX manuscript and synchronized the main English working drafts.

## Integration Checks

| Target | Integration point | Result | Missing |
| --- | --- | --- | --- |
| `mypaper2/Latex/00_abstract.tex` | abstract_414x_boundary | pass | none |
| `mypaper2/Latex/Part3/03_methods_affine_reduction_and_controls_v2.tex` | methods_submission_hardening_checks | pass | none |
| `mypaper2/Latex/Part4/04_results_t1_survival_v2.tex` | results_t1_4141_4142_4143 | pass | none |
| `mypaper2/Latex/Part4/04_results_diffuse_phenotype_v2.tex` | results_near_pre_detrending_boundary | pass | none |
| `mypaper2/Latex/Part4/04_results_empirical_boundary_v2.tex` | evidence_to_claim_table_414x_rows | pass | none |
| `mypaper2/Latex/Part5/05_discussion_limitations_future_v2.tex` | discussion_completed_checks | pass | none |
| `mypaper2/Latex/Part5/05_conclusion_v2.tex` | conclusion_414x_boundary | pass | none |

## Compile Check

- PDF: `mypaper2/Latex/main.pdf`
- Pages: `10`
- PDF size: `1275424` bytes
- LaTeX errors: `0`
- Unresolved reference/citation warnings: `0`
- Underfull warnings present: `True`

## Boundary

The manuscript now includes 4141, 4142, and 4143, but the high-B 4141
confirmation remains optional future statistical hardening. The integrated
claim is therefore: common T1 survival under the frozen local-affine pipeline,
supportive smoke-null calibration, explicit detrending sensitivity, and a
numerical affine-fit QC pass.
