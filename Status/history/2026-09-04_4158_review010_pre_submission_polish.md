# 2026-09-04 4158 Review-010 Pre-Submission Polish

## Purpose

This snapshot records the implementation of review
`mypaper2/00_review/010.md`. The route was treated as manuscript hardening,
figure cleanup, and reproducibility polish rather than as a new exploratory
mechanism experiment.

## Main Changes

- Figure 2 was redesigned to foreground the all-observation T1 survival result,
  the frozen two-scale support matrix, the completed `B=1000` omnibus null
  histogram, and the detrending survivor-count boundary.
- Figure 3 was cleaned by removing the unused radius-correlation profile and
  the secondary sparse-dense contrast from the active phenotype figure.
- The title was shortened to:
  `Local Affine Subtraction Reveals Persistent Tangential Non-Affine Activity
  in Laboratory Midge Swarms`.
- The Methods now explicitly define the `0.35` per-scale tail rule as a frozen
  screening component rather than as a conventional single-observation
  significance threshold.
- The main-text omnibus result now emphasizes `0/1000` null replicates reaching
  the observed `14/19` both-scale count, with plus-one empirical `p≈0.001`.
- Table I was rewritten as an evidence-to-inference table with the columns
  `Test`, `Evidence`, `Supported inference`, and `Interpretive boundary`.
- The supplement was expanded with reproducibility details for pseudo-event
  construction, non-event controls, cross-scale sharing, deterministic seeds,
  detrending variants, state matching, and recent-history matching.
- The title/abstract working drafts in `mypaper2/01_title_abstract/` were
  synchronized with the active LaTeX manuscript.
- A final confirmation pass handled four remaining review-010 checks:
  sparse-dense was removed from the main figure, narrow-rescue wording was
  replaced by neutral reader-facing labels, notation/source scans passed, and
  the abstract was shortened by removing secondary counts.

## Compile Audit

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

The final abstract keeps only the primary and boundary-critical numbers:
`14/19`, `B=1000`, `p≈0.001`, `11/19`, and `13/19`. It no longer carries the
secondary `15/19`, `14/15`, or `13/14` counts.

The active compiled PDF is:

```text
mypaper2/Latex/main_final.pdf
```

## Reproducibility Release

The curated GitHub release repository was updated and pushed.

```text
repository = https://github.com/Saru1228/midge-swarm-nonaffine-residuals
tag = v4158-review010-polish
verification = python tools/verify_release.py passed
```

## Gate Result

`pass_4158_review010_pre_submission_polish_compiled`

## Boundary

No new scientific mechanism claim was added. The manuscript remains a bounded
diagnostic-residual paper: T1 is common under the tested local affine reduction
and rare under the full-pipeline pseudo-event null, but the exact survivor
count is not preprocessing-invariant and the current reductions do not close
the mechanism.

## Recommended Next Step

Proceed to manual PDF inspection and target-journal formatting. Keep new
mechanism search paused unless a reviewer or target-journal requirement
specifically demands it.
