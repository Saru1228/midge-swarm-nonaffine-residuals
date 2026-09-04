# 4156 High-B Manuscript Integration and Refreeze Plan

Date: 2026-09-02

## Node

`4156_highB_manuscript_integration_and_refreeze`

## Question

How should the completed `B=1000` high-B omnibus calibration be integrated into
the manuscript without overstating the result?

## Inputs

- `Output/4155/decision.json`
- `Output/4155/p_omnibus.json`
- `Output/4155/N_both_distribution.csv`
- `Output/4155/N_any_distribution.csv`
- `Output/4155/observation_null_pass_rates.csv`
- `Output/4155/4155_summary.md`
- Current active LaTeX manuscript under `mypaper2/Latex/`
- Submission-facing supplement `Supplement/Supplement_submission.md`

## Required Manuscript Updates

1. Abstract:
   replace limited-resolution calibration language with the completed
   `B=1000` result.

2. Methods:
   describe the high-B omnibus pseudo-event calibration as chunked/resumable
   execution of the same frozen pipeline, not as a new statistical design.

3. Results:
   report `p_both_ge_14 = 0.000999` and `p_any_ge_15 = 0.02198`, emphasizing
   that no null replicate reached the observed both-scale count.

4. Supplement S1:
   replace the B=100-only description with the completed B=1000 result and
   mention the previous 4149 boundary only if useful for computational
   provenance.

5. Frozen package:
   recompile `main_final.tex`, refresh `Output/4154/package/` or create a new
   `Output/4156/package/`, and regenerate the zip archive.

## Wording Boundary

Allowed:

```text
The observed 14/19 both-scale survival count was rare under a completed
B=1000 full-pipeline pseudo-event calibration.
```

Not allowed:

```text
The high-B result proves the biological mechanism.
The T1 signal is universal.
The result is preprocessing-invariant.
The pseudo-event calibration resolves detrending sensitivity.
```

## Gate

```text
pass = manuscript and supplement updated, PDF recompiles without unresolved
       citations/references, and final package is refreshed
boundary = result is integrated but causes page/layout pressure
stop = high-B wording conflicts with detrending or mechanism boundaries
```

## Result

`pass_4156_highB_integrated_submission_package_refrozen`

The completed 4155 high-B calibration was integrated into the active
submission-facing manuscript, current working drafts, and submission supplement.
The manuscript now reports the `B=1000` full-pipeline pseudo-event calibration
as supportive null evidence:

```text
observed N_both = 14/19
null N_both mean = 4.38
null N_both q95 = 7
null N_both q99 = 9
null N_both max = 12
plus-one p_both_ge_14 = 0.000999000999000999

observed N_any = 15/19
plus-one p_any_ge_15 = 0.02197802197802198
```

The active submission-facing path and current working drafts have zero hits for
the old `B=100`, `0.0099`, smoke-null, limited-resolution, null-max-11, and
higher-replicate-future wording checked by node 4156.

The manuscript was recompiled twice from `mypaper2/Latex/main_final.tex`.
Compilation passed with `0` LaTeX errors, `0` undefined control sequences, `0`
citation warnings, `0` reference warnings, `0` rerun warnings, and `0` overfull
boxes. The PDF remains 10 pages; only underfull-box layout warnings remain.

Frozen outputs:

- `Output/4156/4156_summary.md`
- `Output/4156/decision.json`
- `Output/4156/compile_log_audit.csv`
- `Output/4156/manuscript_highB_update_audit.csv`
- `Output/4156/submission_package_manifest.csv`
- `Output/4156/package/`
- `Output/4156/mypaper2_4156_submission_package.zip`

The remaining boundary is interpretive, not computational: the high-B null
calibration strengthens the main survival result, but it does not prove a
mechanism, causal event trigger, universality, or preprocessing invariance.
