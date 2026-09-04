# 4156 High-B Manuscript Integration and Refreeze Result

Date: 2026-09-02

## Node

`4156_highB_manuscript_integration_and_refreeze`

## Question

After node 4155 completed the `B=1000` full-pipeline pseudo-event omnibus null,
can this result be integrated into the manuscript and frozen package without
overstating the evidence?

## Gate Result

`pass_4156_highB_integrated_submission_package_refrozen`

## Source Evidence

The integrated high-B result comes from:

- `Output/4155/decision.json`
- `Output/4155/p_omnibus.json`
- `Output/4155/chunk_status.csv`
- `Output/4155/N_both_distribution.csv`
- `Output/4155/N_any_distribution.csv`
- `Output/4155/observation_null_pass_rates.csv`
- `Output/4155/4155_summary.md`

Primary high-B metrics:

```text
B = 1000
controls per observation per replicate = 40
completed chunks = 20/20
worker failures = 0

observed N_both = 14/19
null N_both mean = 4.38
null N_both median = 4
null N_both q95 = 7
null N_both q99 = 9
null N_both max = 12
plus-one p_both_ge_14 = 0.000999000999000999

observed N_any = 15/19
null N_any mean = 10.223
null N_any median = 10
null N_any q95 = 14
null N_any q99 = 15
null N_any max = 17
plus-one p_any_ge_15 = 0.02197802197802198
```

## Manuscript Changes

Updated the active submission-facing manuscript in:

- `mypaper2/Latex/00_abstract.tex`
- `mypaper2/Latex/Part3/03_methods_affine_reduction_and_controls_v2.tex`
- `mypaper2/Latex/Part4/04_results_t1_survival_v2.tex`
- `mypaper2/Latex/Part4/04_results_empirical_boundary_v2.tex`
- `mypaper2/Latex/Part5/05_discussion_limitations_future_v2.tex`
- `mypaper2/Latex/Part5/05_conclusion_v2.tex`

Updated the submission supplement and working drafts in:

- `Supplement/README.md`
- `Supplement/S1_omnibus.md`
- `Supplement/S8_parameter_registry.md`
- `Supplement/Supplement_submission.md`
- `mypaper2/03_data_methods/draft_en.md`
- `mypaper2/04_results_local_nonaffine/draft_en.md`
- `mypaper2/05_results_reduction_boundaries/draft_en.md`
- `mypaper2/06_discussion_conclusion/draft_en.md`
- `mypaper2/06_discussion_conclusion/draft_zh.md`

The old limited-resolution `B=100` wording was replaced by the completed
`B=1000` result. The manuscript still keeps the detrending, heterogeneity, and
mechanism boundaries explicit.

## Verification

Two `pdflatex -interaction=nonstopmode main_final.tex` passes were run from
`mypaper2/Latex/`.

```text
pdf_pages = 10
latex_errors = 0
undefined_control_sequence = 0
citation_warnings = 0
reference_warnings = 0
rerun_warnings = 0
overfull_boxes = 0
underfull_boxes = 17
final_pdf_bytes = 395114
old_language_hits_active_submission = 0
old_language_hits_current_drafts = 0
zip_bad_file = None
zip_file_count = 54
```

## Frozen Outputs

- `Output/4156/4156_summary.md`
- `Output/4156/decision.json`
- `Output/4156/compile_log_audit.csv`
- `Output/4156/manuscript_highB_update_audit.csv`
- `Output/4156/submission_package_manifest.csv`
- `Output/4156/package/`
- `Output/4156/mypaper2_4156_submission_package.zip`

The frozen package contains the final compiled PDF, active LaTeX source chain,
final figure PDFs, bibliography, submission supplement, code/data availability
statement, and 4155 high-B evidence files.

## Interpretation

The completed high-B null calibration supports the claim that the observed
both-scale T1 survival count is rare under the current pseudo-event pipeline.
It upgrades the earlier B=100 calibration from a limited-resolution support
item to a stronger manuscript-facing null result.

The result does not prove that T1 is a causal mechanism, universal law,
attractor signature, or preprocessing-invariant biological trigger. Those remain
outside the current evidence gate.

## Next

Manuscript-level next step:

- manually inspect the integrated 10-page PDF for table readability, column
  breaks, figure placement, and final-page balance;
- apply journal-specific formatting once a target journal is chosen.

Research-level next step:

- prioritize comparative application or observation-class stratification;
- do not spend the next node on another omnibus-null rerun unless a reviewer or
  target venue specifically requires a still higher replicate count.
