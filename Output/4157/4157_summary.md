# 4157 Repository Availability Manuscript Polish

Date: 2026-09-04

## Objective

Integrate the public reproducibility repository into the manuscript in a
standard paper style and close remaining placeholder-style future-work wording
in the active text.

## Manuscript Updates

- Added an unnumbered `Data and Code Availability` section after the
  Discussion/Conclusion and before the references.
- Added `\usepackage{url}` to both active LaTeX entry points so the GitHub
  repository URL is typeset safely.
- Updated `main_final.tex` and `main.tex` to input
  `06_data_code_availability.tex`.
- Replaced the earlier open-ended future-work paragraph with two bounded
  directions:
  1. comparative applications to other weakly ordered collectives;
  2. perturbation or richer-measurement experiments to determine what generates
     the T1 residual layer.
- Updated the English and Chinese Discussion/Conclusion working drafts so the
  Markdown drafts and active LaTeX manuscript remain synchronized.

## Repository Availability Statement

The manuscript now points to:

`https://github.com/Saru1228/midge-swarm-nonaffine-residuals`

with release tag:

`v4157-availability`

The raw three-dimensional trajectory files are described as external published
data and are not redistributed in the release repository. The repository
contains the curated code, frozen configurations, derived summary outputs,
final manuscript artifacts, the completed `B=1000` pseudo-event calibration,
and a lightweight verification script.

## Compile Audit

The updated `mypaper2/Latex/main_final.tex` was compiled twice with
`pdflatex -interaction=nonstopmode`.

- PDF exists: yes
- Pages: 10
- PDF bytes: 396241
- LaTeX errors: 0
- Undefined control sequences: 0
- Citation warnings: 0
- Reference warnings: 0
- Rerun warnings: 0
- Overfull boxes: 0
- Underfull boxes: 16

The underfull boxes are layout-quality warnings only and do not indicate a
compilation failure.

## Decision

Gate result:

`pass_4157_repository_availability_integrated_and_compiled`

This node supersedes the previous post-freeze availability placeholder while
preserving the scientific boundary from 4156: the high-B omnibus result
strengthens the diagnostic T1 residual-layer claim, but it does not prove a
mechanism, causality, universality, or preprocessing invariance.

## Recommended Next Step

For submission preparation, the next step is manual visual inspection of the
10-page PDF, followed by journal-specific formatting and, if desired, DOI
archiving such as Zenodo. For scientific continuation, the next route should be
comparative application or observation-class stratification rather than another
immediate omnibus-null rerun.
