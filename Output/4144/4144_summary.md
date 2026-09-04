# 4144 Definition, Notation, and Figure-Source Cleanup

Node: `4144_definition_notation_figure_cleanup`  
Date: 2026-09-02

## Purpose

4144 did not rerun the scientific analysis. It converted the completed
submission-hardening checks into manuscript-facing claim boundaries, figure
source provenance, and 4145 edit targets.

## Main Findings

- The 4141 full-pipeline pseudo-event null is supportive at smoke scale:
  observed `N_both = 14/19`, null mean
  `4.49`, null q95 `8`,
  null max `11`, plus-one
  `p_both = 0.009901` over `B = 100`.
- The 4142 detrending challenge is a boundary, not a stop: centered detrending
  reproduced `14/19` both-scale support, past-only detrending reduced this to
  `11/19`, and no-detrend robust-z gave `13/19`.
- The 4143 local-affine conditioning QC passed: `38/`
  `38` observation-k combinations passed, all
  `19/19` observations passed both k
  values, median condition number was `2.37`,
  and no sampled fit had condition number greater than 100.
- Figure-source cleanup found `5/`
  `5` final figure packages available in the LaTeX figure
  directory.

## Routing Decision

`pass_4144_ready_for_4145_with_detrending_and_smoke_null_boundaries`

4145 should now update the manuscript rather than open a new scientific node.
The manuscript should keep three boundaries visible: 4141 is smoke-level unless
expanded to high B, the exact 14/19 count is centered-detrending dependent, and
4143 is a numerical QC pass rather than a biological mechanism result.

## Outputs

- `claim_boundary_updates.csv`
- `review007_gap_resolution.csv`
- `figure_source_manifest.csv`
- `manuscript_update_targets.csv`
- `reviewer_defense_table.md`
- `decision.json`
