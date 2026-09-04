# 4158 Review-010 Pre-Submission Polish

Date: 2026-09-04

## Purpose

This node implements the final pre-submission hardening checklist from
`mypaper2/00_review/010.md`. The review explicitly recommended manuscript
hardening rather than new mechanism experiments.

## What Changed

- Figure 2 was redesigned to show the main survival evidence, the frozen
  two-scale support matrix, the B=1000 omnibus null histogram, and the
  detrending survivor-count comparison.
- Figure 3 was cleaned so it stays focused on the T1 phenotype and no longer
  carries the unused radius-correlation profile.
- The Methods text now explicitly separates the 0.35 frozen screening rule
  from manuscript-level statistical inference.
- The main text now reports the omnibus result as 0/1000 null replicates
  reaching the observed both-scale count, with plus-one empirical p
  approximately 0.001.
- The evidence table now uses publication-facing columns:
  Test, Evidence, Supported inference, and Interpretive boundary.
- The supplement now contains the key reproducibility details for the
  pseudo-event sampler, non-event controls, detrending variants, state matching,
  and recent-history formula.
- The title/abstract discussion drafts were synchronized to the current
  manuscript framing.

## Compile Result

`mypaper2/Latex/main_final.tex` was compiled twice.

```text
pdf_pages = 11
latex_errors = 0
undefined_control_sequence = 0
citation_warnings = 0
reference_warnings = 0
rerun_warnings = 0
overfull_boxes = 0
underfull_boxes = 16
```

## Gate Result

`pass_4158_review010_pre_submission_polish_compiled`

## Interpretation

The manuscript now better exposes the strongest evidence chain:

```text
local affine subtraction
-> T1 survives in most observations
-> observed both-scale count = 14/19
-> B=1000 full-pipeline pseudo-event omnibus
-> 0/1000 null replicates reached 14
-> plus-one empirical p approximately 0.001
-> alternative detrending preserves majority-level support but not the exact count
-> diagnostic residual layer, not completed mechanism
```

## Boundary

No new scientific claim was added. The route should not reopen graph,
propagation, RG, or mechanism searches before submission unless a reviewer or
target-journal format specifically requires it.
