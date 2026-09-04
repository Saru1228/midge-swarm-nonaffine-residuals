# Node 4140 Summary

## Purpose

Freeze the current manuscript analysis contract and check whether the main T1
claim can be traced to existing scripts and outputs before running 4141/4142/4143.

## Exact Analysis Performed

- Read the 007 paper-defense roadmap.
- Checked whether 414x experiments already existed: none were found.
- Mapped active manuscript definitions to code and output artifacts.
- Recomputed the observed support counts from `Output/4081c` tables.
- Traced `spectral_set` provenance from 3032/3032b through 3045.
- Separated true definition mismatches from planned robustness gaps.

## Primary Result

```text
N_both_observed = 14 / 19
N_any_observed  = 15 / 19
stop-level mismatches = 0
boundary/planned items = 3
gate_result = pass_with_pre_submission_boundary_items
```

## Observation-Level Result

- Both-scale survivor observations: `[2, 5, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]`
- Any-scale survivor observations: `[2, 4, 5, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]`
- Non-survivor observations: `[1, 3, 6, 8]`

## Gate Evaluation

No stop-level paper-code mismatch was found for the currently frozen T1
definition and survival counts.

The audit does identify three planned pre-submission gaps:

- full-pipeline omnibus null is not yet run;
- alternative detrending challenge is not yet run;
- affine condition-number QC is not yet run.

These are not silent definition changes. They are the next hardening tests.

## What This Strengthens

4140 strengthens the project by making the current analysis contract explicit:
the manuscript claim can now be mapped to concrete code files, output tables,
and fixed thresholds.

## What This Weakens

4140 does not make the 14/19 count statistically calibrated. Existing 4081c
non-event replicates are part of the survival gate but are not the same thing
as the 4141 full-pipeline omnibus null.

## What This Does NOT Prove

| does_not_prove |
| --- |
| full-pipeline global significance of 14/19 |
| detrending invariance |
| well-conditioned local affine fits across all focal samples |
| mechanism, prediction, or universality |

## Decision

`pass_with_pre_submission_boundary_items`

## Next

| next |
| --- |
| 4141_full_pipeline_omnibus_survival_null_smoke |
| 4142_detrending_challenge |
| 4143_affine_fit_qc |

## Artifacts

- `Output/4140/frozen_analysis_contract.yaml`
- `Output/4140/reproducibility_registry.csv`
- `Output/4140/spectral_set_provenance.md`
- `Output/4140/code_source_map.csv`
- `Output/4140/definition_mismatches.csv`
- `Output/4140/decision.json`
