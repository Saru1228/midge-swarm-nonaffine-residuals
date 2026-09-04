# Node 4154 Summary

## Purpose

Freeze a submission-facing manuscript package after the review-008 hardening
chain, while preserving the boundary between completed manuscript evidence and
unfinished high-replicate calibration.

## Gate Result

`pass_4154_submission_package_frozen_and_compiled`

```text
pdf_pages = 10
latex_errors = 0
undefined_control_sequence = 0
citation_warnings = 0
reference_warnings = 0
overfull_boxes = 0
underfull_boxes = 16
final_pdf_bytes = 393356
package_file_count = 37
archive_bytes = 500772
```

## What Was Frozen

- `mypaper2/Latex/main_final.pdf`: final compiled manuscript PDF.
- `mypaper2/Latex/main_final.tex`: final manuscript entrypoint.
- `mypaper2/Latex/main_final.log`: final compilation log.
- `mypaper2/Latex/bibitems.tex`: corrected manual bibliography.
- `Supplement/Supplement_submission.md`: sanitized supplement draft.
- `Output/4154/code_data_availability_statement.md`: code/data availability
  statement.
- `Output/4154/package/`: frozen copy of the final PDF, log, entrypoint,
  bibliography, supplement, active LaTeX source chain, and final figure PDFs.
- `Output/4154/mypaper2_4154_submission_package.zip`: compressed archive of the
  frozen package directory.

## Compile Audit

Two `pdflatex -interaction=nonstopmode main_final.tex` passes were run from
`mypaper2/Latex/`. The final log shows no LaTeX errors, undefined control
sequences, citation warnings, reference warnings, rerun-required label warnings,
or overfull-box warnings. Only underfull-box layout warnings remain.

## Bibliography Cleanup

The manual bibliography was checked against current public metadata and updated
for several incomplete records:

- Feng and Ouellette 2023: `J. R. Soc. Interface`, vol. 20, no. 199, Art. no.
  20220521.
- Reynolds 2018: `J. R. Soc. Interface`, vol. 15, no. 138, Art. no.
  20170806.
- Reynolds 2024: `J. R. Soc. Interface`, vol. 21, no. 219, Art. no.
  20240450.
- Sinhuber et al. 2019: `Sci. Data`, vol. 6, Art. no. 190036.

## Boundary

The manuscript does not integrate a formal high-replicate omnibus p-value. Node
4149 attempted the all-19 `B=1000` full-pipeline pseudo-event calibration but
hit an interactive compute boundary before p-value outputs were produced. This
is a compute boundary, not a statistical negative result. The completed `B=100`
run remains a limited-resolution full-pipeline calibration.

## Next

The experimental route is closed at submission-package level. The next practical
steps are manual visual inspection of the PDF, journal-specific formatting, and
an optional staged batch or overnight high-replicate calibration if a formal
omnibus p-value is needed.
