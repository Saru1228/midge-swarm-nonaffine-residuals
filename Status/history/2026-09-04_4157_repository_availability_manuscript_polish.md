# 4157 Repository Availability Manuscript Polish

Date: 2026-09-04

## Objective

Add a standard paper-style data/code availability statement to the end of the
`mypaper2` manuscript and align the manuscript with the public GitHub
reproducibility repository.

## Actions

- Added `mypaper2/Latex/06_data_code_availability.tex`.
- Added `\usepackage{url}` to the active LaTeX entry points.
- Added `\input{06_data_code_availability}` before the bibliography in both
  `mypaper2/Latex/main_final.tex` and `mypaper2/Latex/main.tex`.
- Updated the Discussion Future Work paragraph so it no longer contains
  placeholder-style future repository wording.
- Updated the English and Chinese Discussion/Conclusion working drafts.
- Created `Output/4157/` with the compile audit, decision file, summary, and
  standalone availability statement.
- Updated and pushed the curated GitHub reproducibility repository:
  `https://github.com/Saru1228/midge-swarm-nonaffine-residuals`.

## Compile Audit

The updated `mypaper2/Latex/main_final.tex` was compiled twice with
`pdflatex -interaction=nonstopmode`.

- PDF pages: 10
- PDF bytes: 396241
- LaTeX errors: 0
- Undefined control sequences: 0
- Citation warnings: 0
- Reference warnings: 0
- Rerun warnings: 0
- Overfull boxes: 0
- Underfull boxes: 16

## Repository Release

The public repository was updated and pushed with release tag:

`v4157-availability`

The repository check passed:

`python tools/verify_release.py`

The check verifies the frozen `4155` high-B omnibus result, the `4156` package,
and the new `4157` availability-section integration.

## Decision

Gate result:

`pass_4157_repository_availability_integrated_and_compiled`

This node completes the paper-end availability integration. It does not change
the scientific claim: the manuscript supports a reproducible local tangential
non-affine residual layer in most recordings, while remaining bounded against
claims of mechanism, causality, universality, or preprocessing invariance.

## Next

The next submission-facing step is manual visual inspection of the 10-page PDF,
then journal-specific formatting and optional DOI archiving. The next
scientific step, if reopened, should be comparative application or
observation-class stratification rather than another immediate omnibus-null
rerun.
