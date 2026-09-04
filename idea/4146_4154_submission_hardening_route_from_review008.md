# 4146-4154 Submission-Hardening Route from Review 008

Date: 2026-09-02

## Route Role

This route converts `mypaper2/00_review/008.md` into an executable
submission-hardening chain.

It is not a new mechanism-search branch. It preserves the frozen T1 definition
and survival gate, resolves remaining correctness/provenance issues, then
prepares the manuscript and supplement for submission.

## Current Evidence State

Already integrated through `4145`:

```text
T1 both-scale support: 14/19 under frozen centered detrending
T1 any-scale support: 15/19
survivor-class scale/lag robustness: 14/15
diffuse all-tangential support: 13/14
near-pre descriptive support: 8/14 under original 4085 source
4141 limited-resolution full-pipeline calibration: B=100, null max=11,
plus-one p=0.0099
4142 detrending challenge: centered 14/19, past-only 11/19, no rolling 13/19
4143 affine QC: 38/38 observation-scale combinations passed
```

Completed after this route was drafted:

```text
4146 near-pre audit: 8/14 vs 11/14 is explained by different phase-gate
and pseudo-event-control definitions. The manuscript should keep 4085 8/14
as the main near-pre phase-localization count and treat 4142 near-pre counts
as sensitivity evidence only.
```

Current bounded claim:

```text
T1 is common under the frozen local-affine pipeline, but exact observation
counts and some timing features are preprocessing-sensitive. The result is a
diagnostic residual layer, not a completed mechanism.
```

## Compilation Policy

Starting after 4146, do not compile the PDF after every node. Continue through
`4147-4154` with machine-readable outputs, route notes, and manuscript patches
as needed. Compile only at `4154_submission_package_freeze`, unless a LaTeX
structural edit creates a clear syntax risk that must be checked immediately.

## Execution Order

### 4146 - Near-Pre Definition Audit

Status:

```text
completed: pass_4146_discrepancy_explained_by_gate_and_null_definition
```

Question:

```text
Why does the manuscript have 4085 near-pre 8/14 and 4142 centered near-pre 11/14?
```

Outputs:

```text
Output/4146/near_pre_definition_audit.csv
Output/4146/source_trace.md
Output/4146/discrepancy_decision.json
Output/4146/manuscript_replacement_text.md
```

Gate:

```text
pass = discrepancy explained by different metric/gate/subset/preprocessing
boundary = denominator or source mismatch requires wording restriction
stop = same metric but inconsistent result, requiring code/cache investigation
```

### 4147 - spectral_set Publication Provenance

Status:

```text
completed: pass_4147_spectral_set_publication_provenance_ready
```

Question:

```text
Can an external reader reconstruct the low/high spectral_set labels without
reading old experiment scripts?
```

Outputs:

```text
Output/4147/spectral_set_provenance.md
Output/4147/spectral_set_algorithm.md
Output/4147/source_code_map.csv
Output/4147/example_label_trace.csv
Output/4147/supplement_method.tex
```

Gate:

```text
pass = spectral_set source, inputs, partition, label assignment, persistence
       use, and T1-independence are documented
boundary = chain is documented but some low-level reconstruction detail remains
stop = spectral_set used T1 or creates circularity not disclosed
```

### 4148 - Notation and Equation Consistency Audit

Status:

```text
completed: pass_4148_active_notation_consistent
```

Question:

```text
Are C(t), dot C(t), R(t), T1, affine residuals, lag, and event-window
notations consistent across manuscript, captions, tables, and final figures?
```

Outputs:

```text
Output/4148/notation_registry.csv
Output/4148/notation_errors.csv
Output/4148/equation_consistency_check.md
Output/4148/corrected_equations.tex
```

Completed fixes:

```text
spectral_set provenance added to active Methods
B3 shorthand defined as the upstream global-affine residual baseline
near-pre endpoint-inclusive 4100 aggregate distinguished from half-open 4085 phase bins
```

Gate:

```text
pass = active manuscript and figure-generation labels use consistent notation
boundary = old inactive files retain old notation but active path is clean
stop = active manuscript contains contradictory equations or wrong state vector
```

### 4149 - High-B Full-Pipeline Omnibus Null

Status:

```text
boundary: boundary_4149_highB_requires_batch_or_overnight_run
```

Question:

```text
Does the observed 14/19 both-scale count remain unlikely under the complete
pseudo-event null pipeline at higher B?
```

Run rule:

```text
Do not change T1 definition, k, lag, survival gate, pseudo-event construction,
non-event exclusion, or all-19 observation scope.
Archive formal runs under Output/4141/runs/ or Output/4149/.
```

Recommended stages:

```text
B=1000 minimum formal check
B=5000 preferred final check if compute is affordable
```

Outputs:

```text
Output/4149/omnibus_config.yaml
Output/4149/omnibus_replicates.csv
Output/4149/N_both_distribution.csv
Output/4149/N_any_distribution.csv
Output/4149/observation_null_pass_rates.csv
Output/4149/omnibus_summary.json
Output/4149/figures/omnibus_histogram.png
Output/4149/omnibus_summary.md
```

Gate:

```text
strong = p_omnibus <= 0.01
moderate = 0.01 < p_omnibus <= 0.05
boundary = 0.05 < p_omnibus <= 0.10
fail = p_omnibus > 0.10
```

Boundary outcome:

```text
An attempted B=1000, controls=40 all-19 run reused Output/4141/cache but did
not reach p-value outputs within a 30-minute interactive limit. Treat this as
a compute boundary, not as a statistical negative result. Keep the completed
B=100 run as limited-resolution pipeline validation unless a separate
batch/overnight high-B job is scheduled.
```

### 4150 - Final Figure Cleanup and Redesign

Status:

```text
completed: pass_4150_final_figure_package_ready_for_reintegration
```

Question:

```text
Do the figures use publication-facing labels, readable layout, consistent
observation order, and source-traceable numbers?
```

Required changes:

```text
remove internal Figure 1 note
remove history from Figure 3 phenotype panel
redesign Figure 4A as observation-level evidence if practical
standardize class colors, fonts, labels, and denominator notation
```

Completed changes:

```text
Fig1_final removes the internal 4134 workflow note.
Fig3_final removes recent-history evidence from the phenotype panel.
Fig4_final redraws panel A as observation-level held-out moment-closure points.
Fig5_final removes node-specific axis wording and keeps metadata descriptive.
Active LaTeX includegraphics commands now point to Fig1_final-Fig5_final.
```

Outputs:

```text
Output/4150/figures/Fig1_final.pdf
Output/4150/figures/Fig2_final.pdf
Output/4150/figures/Fig3_final.pdf
Output/4150/figures/Fig4_final.pdf
Output/4150/figures/Fig5_final.pdf
Output/4150/figure_source_map.csv
Output/4150/figure_caption_final.md
```

### 4151 - Final Manuscript Reintegration

Status:

```text
completed: pass_4151_active_manuscript_reintegrated_without_internal_smoke_language
```

Question:

```text
Are 4146-4150 results integrated into the active manuscript without duplicate
or internal planning language?
```

Focus:

```text
Abstract: final high-B p if available; no smoke wording if high-B is done
Methods: exact spectral_set, T1, survival gate, detrending, QC, omnibus details
Results: one clean result chain, no repeated 414x paragraphs
Discussion: common but not preprocessing-invariant; diagnostic not mechanism
Limitations: only real remaining limitations
```

Completed changes:

```text
Active figure references now use Fig1_final-Fig5_final.
B=100 omnibus evidence is described as limited-resolution pseudo-event
calibration, not as a smoke null or formal high-B p-value.
4149 compute boundary is kept out of the manuscript result text.
```

### 4152 - Supplement Build

Status:

```text
completed: pass_4152_technical_supplement_draft_built
```

Question:

```text
Can a reader inspect or reproduce the main supporting analyses without
overloading the main text?
```

Supplement modules:

```text
S1 Full omnibus null
S2 Detrending challenge
S3 Local affine conditioning QC
S4 Scale/lag sensitivity
S5 State-matching QC
S6 History matching / shuffle null
S7 spectral_set construction
S8 Full parameter registry
```

Completed sections:

```text
Supplement/README.md
Supplement/S1_omnibus.md
Supplement/S2_detrending.md
Supplement/S3_affine_qc.md
Supplement/S4_scale_lag.md
Supplement/S5_state_matching.md
Supplement/S6_history.md
Supplement/S7_spectral_set.md
Supplement/S8_parameter_registry.md
```

### 4153 - Final Consistency Audit

Status:

```text
completed: pass_4153_final_consistency_audit_clean
```

Question:

```text
Are numbers, claims, terminology, causal language, figures, captions, and
references internally consistent?
```

Outputs:

```text
Output/4153/number_audit.csv
Output/4153/claim_audit.csv
Output/4153/terminology_audit.csv
Output/4153/causal_language_audit.csv
Output/4153/figure_text_consistency.csv
Output/4153/reference_audit.csv
Output/4153/final_audit_summary.md
```

Completed audit:

```text
active_tex_files = 21
supplement_files = 9
stop_items = 0
fix_required_items = 0
review_items = 15, manually cleared as bounded or negated contexts
```

### 4154 - Submission Package Freeze

Status:

```text
completed: pass_4154_submission_package_frozen_and_compiled
```

Question:

```text
Can the final manuscript package be frozen without internal experiment labels
or draft naming?
```

Outputs:

```text
mypaper2/Latex/main_final.tex
mypaper2/Latex/main_final.pdf
Supplement/
final code/data availability statement
```

Completed freeze:

```text
mypaper2/Latex/main_final.pdf compiles as a 10-page final manuscript.
Final log audit: 0 LaTeX errors, 0 citation warnings, 0 reference warnings,
0 overfull boxes, and 16 underfull-box layout warnings.
Output/4154/package contains 37 frozen files, including the final PDF, log,
entrypoint, bibliography, active LaTeX source chain, final figure PDFs,
submission-facing supplement, manifest, and code/data availability statement.
```

## Stop Rules

- Do not open new mechanism-search experiments inside this route.
- Do not change T1 definition or survival gate.
- Do not tune pseudo-event null settings to improve high-B p.
- Do not rescue the past-only detrending count by parameter adjustment.
- Do not remove failed observations.
- Do not describe `14/19` as preprocessing-invariant.
- Do not use frame-level p-values as replacements for observation-level
  evidence.
- Do not retain internal labels such as `408x`, `4134`, or `414x` in the final
  submission text.

## Route State

Current state:

```text
closed at 4154_submission_package_freeze
```

Recommended next action:

```text
manual PDF inspection, target-journal formatting, and optional staged high-B
batch calibration if a formal omnibus p-value is required.
```

## Post-Freeze Addendum: 4155

After the 4154 freeze, the optional high-B branch was reopened as
`4155_parallel_highB_omnibus_null`. The monolithic 4149 compute boundary was
resolved by a chunked, resumable, parallel implementation.

```text
B = 1000
controls per observation per replicate = 40
chunks = 20 x 50 replicates
workers = 4
completed = 1000/1000
gate = strong_pass_omnibus_null
p_both_ge_14 = 0.000999000999000999
p_any_ge_15 = 0.02197802197802198
```

This means the 4154 frozen manuscript is no longer the strongest available
version if the high-B result is accepted into the paper. The appropriate next
node is `4156_highB_manuscript_integration_and_refreeze`.
