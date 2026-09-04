# 4158 Review-010 Pre-Submission Polish

Date: 2026-09-04

This node implemented the high-priority items from
`mypaper2/00_review/010.md`. It reorganized existing evidence for the final
pre-submission review and did not recompute T1, change event definitions,
change screening gates, or open a new mechanism route.

## Updated Figures

- Figure 2 now foregrounds the all-observation survival claim, the
  frozen two-scale support matrix, the completed B=1000 omnibus null,
  and the detrending survivor-count boundary.
- Figure 3 now keeps the phenotype focus and removes the radius
  correlation profile from the active main figure.

## Updated Manuscript/Supplement Text

- The title now uses the shorter JRSI-facing form:
  "Local Affine Subtraction Reveals Persistent Tangential Non-Affine Activity
  in Laboratory Midge Swarms".
- The Methods text now states that the 0.35 per-scale tail rule is a frozen
  screening component, not a conventional single-observation significance
  threshold.
- The omnibus result is reported in the main text as 0/1000 null replicates
  reaching the observed both-scale count, with plus-one empirical p
  approximately 0.001.
- The evidence-to-inference table now uses publication-facing columns:
  Test, Evidence, Supported inference, and Interpretive boundary.
- The supplement now gives the pseudo-event construction, non-event controls,
  cross-scale sharing, deterministic seed structure, detrending variants,
  state-matching details, and recent-history formula.
- The title/abstract discussion drafts under `mypaper2/01_title_abstract/`
  were synchronized to the current manuscript framing.

## Compile Audit

- Entry point: `mypaper2/Latex/main_final.tex`
- Output PDF: `mypaper2/Latex/main_final.pdf`
- PDF pages: 11
- LaTeX errors: 0
- Undefined control sequences: 0
- Citation warnings: 0
- Reference warnings: 0
- Rerun warnings: 0
- Overfull boxes: 0
- Underfull boxes: 16

## Active Figure Outputs

- Fig2: Output/4158/figures/Fig2_final.png; Output/4158/figures/Fig2_final.pdf; mypaper2/Latex/figures/Fig2_final.png; mypaper2/Latex/figures/Fig2_final.pdf
- Fig3: Output/4158/figures/Fig3_final.png; Output/4158/figures/Fig3_final.pdf; mypaper2/Latex/figures/Fig3_final.png; mypaper2/Latex/figures/Fig3_final.pdf

## Review Gate

`pass_4158_review010_pre_submission_polish_compiled`

## Remaining Boundary

This is still a bounded diagnostic paper. The current manuscript supports a
measurable local tangential non-affine residual under the tested local-affine
reduction and calibrated pseudo-event null. It does not claim a completed
biological mechanism, online prediction, universal law, or preprocessing
invariance.
