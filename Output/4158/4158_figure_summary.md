# 4158 Review-010 Pre-Submission Polish

Date: 2026-09-04

This node implemented the high-priority items from
`mypaper2/00_review/010.md`. It reorganized existing evidence for the
final pre-submission review and did not recompute T1, change event
definitions, change screening gates, or open a new mechanism route.

## Updated Figures

- Figure 2 now foregrounds the all-observation survival claim, the
  frozen two-scale support matrix, the completed B=1000 omnibus null,
  and the detrending survivor-count boundary.
- Figure 3 now keeps the phenotype focus and removes the radius
  correlation and sparse-dense profiles from the active main figure.

## Active Figure Decisions

- Sparse-dense was removed from the main Figure 3 profile panel because
  the current manuscript does not develop it as an independent result.
  The diagnostic remains available in the upstream profile source.
- Observation classes use neutral labels: robust survivor with diffuse
  support, robust survivor without diffuse support, one-scale survivor,
  fragile boundary, and stable non-survivor.

## Active Figure Outputs

- Fig2: Output/4158/figures/Fig2_final.png; Output/4158/figures/Fig2_final.pdf; mypaper2/Latex/figures/Fig2_final.png; mypaper2/Latex/figures/Fig2_final.pdf
- Fig3: Output/4158/figures/Fig3_final.png; Output/4158/figures/Fig3_final.pdf; mypaper2/Latex/figures/Fig3_final.png; mypaper2/Latex/figures/Fig3_final.pdf

## Review Gate

`pass_4158_review010_pre_submission_polish_compiled`

## Final Confirmation Points

| point | decision | result |
| --- | --- | --- |
| sparse-dense | Remove from the main Figure 3 profile panel | The contrast remains available in upstream source data, but it is not shown as a main result because the manuscript does not develop a stable sparse-dense claim. |
| narrow rescue | Rename in reader-facing text | Active labels now use one-scale survivor, fragile boundary, stable non-survivor, robust survivor with diffuse support, and robust survivor without diffuse support. |
| notation/source audit | Pass after cleanup | Active text and Supplement use reader-facing $C(t)$, $\dot C(t)$, $R(t)$ / $S(t)$ notation; old terms and old release tags were not found in active paths. |
| Abstract numeric density | Reduced | The abstract keeps the primary 14/19 result, B=1000 omnibus calibration, p approximately 0.001, and detrending-boundary counts, but removes secondary 15/19, 14/15, and 13/14 counts. |

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

## Repository Release

- Repository: https://github.com/Saru1228/midge-swarm-nonaffine-residuals
- Release tag: `v4158-review010-polish`
- Release verification: `python tools/verify_release.py` passed
