# Node 4156 Summary

## Purpose

Integrate the completed `B=1000` high-replicate full-pipeline pseudo-event
omnibus calibration from node 4155 into the submission-facing manuscript and
refreeze the manuscript package.

## Gate Result

`pass_4156_highB_integrated_submission_package_refrozen`

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
```

## Integrated High-B Evidence

The completed 4155 run used `B=1000` null replicates and 40 non-event controls
per observation per replicate. It split the run into deterministic chunks and
merged all 20 chunks after completion.

Primary result:

```text
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

Interpretation: the both-scale survival count is rare under the completed
pseudo-event null pipeline. This strengthens the observation-level null
calibration, but it does not prove mechanism, causality, universality, or
preprocessing invariance.

## Manuscript Updates

Updated manuscript-facing wording in the abstract, Methods, Results, empirical
boundary table, Discussion, Conclusion, and submission supplement. The old
`B=100`, `0.0099`, smoke-null, limited-resolution, and higher-replicate-future
language is absent from the active submission-facing paths and current working
drafts scanned by this node.

## Compile Audit

Two `pdflatex -interaction=nonstopmode main_final.tex` passes were run from
`mypaper2/Latex/`. The final log shows no LaTeX errors, undefined control
sequences, citation warnings, reference warnings, rerun-required label warnings,
or overfull-box warnings. Only underfull-box layout warnings remain.

## What Was Frozen

- `Output/4156/package/main_final.pdf`: compiled manuscript PDF.
- `Output/4156/package/main_final.tex`: final manuscript entrypoint.
- `Output/4156/package/main_final.log`: final compilation log.
- `Output/4156/package/active_latex/`: active LaTeX source chain and final figure PDFs.
- `Output/4156/package/Supplement_submission.md`: submission-facing supplement draft.
- `Output/4156/package/highB_evidence_4155/`: completed high-B calibration evidence.
- `Output/4156/mypaper2_4156_submission_package.zip`: compressed frozen package.

## Next

At manuscript level, the next practical checks are manual PDF visual inspection
and journal-specific formatting. At research level, the next useful branch is
comparative application or observation-class stratification; another immediate
omnibus-null rerun is no longer the main bottleneck.
