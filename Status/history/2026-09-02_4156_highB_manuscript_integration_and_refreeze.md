# 2026-09-02 - 4156 high-B manuscript integration and refreeze

## Purpose

Node 4156 integrated the completed 4155 `B=1000` full-pipeline pseudo-event
omnibus calibration into the submission-facing manuscript and refroze the final
package.

## Gate Result

`pass_4156_highB_integrated_submission_package_refrozen`

## Main Evidence Integrated

The source high-B result was:

```text
run_name = highB_n1000_c40
B = 1000
controls per observation per replicate = 40
completed chunks = 20/20
observed N_both = 14/19
null N_both mean = 4.38
null N_both q95 = 7
null N_both q99 = 9
null N_both max = 12
plus-one p_both_ge_14 = 0.000999000999000999
observed N_any = 15/19
plus-one p_any_ge_15 = 0.02197802197802198
```

The both-scale result is now manuscript-facing null evidence: no null replicate
reached the observed both-scale count.

## Manuscript and Supplement Changes

Updated the abstract, Methods, Results, evidence-to-claim table, Discussion,
Conclusion, submission supplement, and current English/Chinese working drafts.

The old `B=100`, `0.0099`, smoke-null, limited-resolution, null-max-11, and
higher-replicate-future wording was removed from the active submission-facing
paths and current drafts checked by node 4156.

## Compile and Package Verification

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
package_file_count = 54
archive_bytes = 516593
zip_bad_file = None
```

## Outputs

- `Output/4156/4156_summary.md`
- `Output/4156/decision.json`
- `Output/4156/compile_log_audit.csv`
- `Output/4156/manuscript_highB_update_audit.csv`
- `Output/4156/submission_package_manifest.csv`
- `Output/4156/package/`
- `Output/4156/mypaper2_4156_submission_package.zip`
- `idea/4156_highB_manuscript_integration_and_refreeze_result.md`

## Boundary

The remaining limitation is not the omnibus-null replicate count. The high-B
result strengthens the main survival claim but does not establish mechanism,
causality, universality, attractor status, or preprocessing invariance.

## Next

At manuscript level, inspect the 10-page PDF manually and apply journal-specific
formatting. At research level, move toward comparative application or
observation-class stratification rather than another immediate omnibus-null run.
