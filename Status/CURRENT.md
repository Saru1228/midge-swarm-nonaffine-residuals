# Current Project Status

Last updated: 2026-09-04

## 1. Current role of this file

This file records the latest actionable state of the project.

- `CODEX_START_HERE.md` is the stable onboarding entry.
- `Status/CURRENT.md` is the frequently updated operational status.
- `Status/history/` stores dated stage snapshots when the project meaningfully
  changes direction.

## 2. Current project focus

The `413x` phenomenon-and-boundary synthesis route for the midge swarm
exploratory experiments is complete. The `4146-4154` submission-hardening route
for the `mypaper2` manuscript after review `mypaper2/00_review/008.md` closed
at package-freeze level. The optional post-freeze `4155` high-B calibration has
completed, `4156` integrated that result into the manuscript and refroze the
submission package, `4157` linked the manuscript to the public GitHub
reproducibility repository, and `4158` implemented the review-010
pre-submission figure/text polish.

Latest reproducibility repository release:

- GitHub repository:
  `https://github.com/Saru1228/midge-swarm-nonaffine-residuals`
- Local release checkout:
  `C:\Users\Saru\Desktop\TUAT\ResearchSampleCode\midge-swarm-nonaffine-residuals`
- Release commit:
  current `v4158-review010-polish` tag target
- Release tag:
  `v4158-review010-polish`
- Contents:
  selected manuscript-facing scripts, final `4156` manuscript package,
  completed `4155` high-B omnibus output, `4157` manuscript availability
  integration, `4158` review-010 figure/text polish, curated upstream
  summaries/tables, supplement drafts, final PDF/LaTeX source, and
  `tools/verify_release.py`.

Latest 2026-09-04 4158 status:

- Review `mypaper2/00_review/010.md` was implemented as a final
  pre-submission polish node rather than as a new mechanism experiment.
- Figure 2 was redesigned to foreground the all-observation T1 survival claim,
  the frozen two-scale support matrix, the completed `B=1000` omnibus null
  histogram, and the detrending survivor-count boundary.
- Figure 3 was cleaned so the active phenotype figure no longer carries the
  unused radius-correlation profile.
- The manuscript title now uses the shorter JRSI-facing form:
  `Local Affine Subtraction Reveals Persistent Tangential Non-Affine Activity
  in Laboratory Midge Swarms`.
- The Methods text now explicitly states that the `0.35` per-scale tail rule is
  a frozen screening component rather than a conventional single-observation
  significance threshold.
- The omnibus result is reported in the main text as `0/1000` null replicates
  reaching the observed `14/19` both-scale count, with plus-one empirical
  `p≈0.001`.
- The evidence-to-inference table now uses publication-facing columns:
  `Test`, `Evidence`, `Supported inference`, and `Interpretive boundary`.
- The supplement now contains the key reproducibility details for pseudo-event
  construction, non-event controls, cross-scale sharing, deterministic seeds,
  detrending variants, state matching, and recent-history matching.
- `mypaper2/Latex/main_final.tex` was recompiled twice after the review-010
  polish. The updated PDF is `11` pages, with `0` LaTeX errors, `0` undefined
  control sequences, `0` citation warnings, `0` reference warnings, `0` rerun
  warnings, and `0` overfull boxes. Only `16` underfull-box layout warnings
  remain.
- The curated GitHub reproducibility repository was updated and pushed with tag
  `v4158-review010-polish`. Its lightweight `python tools/verify_release.py`
  check passed after the update.
- `4158` is a manuscript/figure/reproducibility-polish node. It does not add a
  new scientific mechanism claim. The scientific claim boundary from `4156`
  remains unchanged.

Latest 2026-09-04 4157 status:

- `4157` added an unnumbered `Data and Code Availability` section to the
  active `mypaper2` LaTeX manuscript immediately before the references.
- The manuscript now cites the public reproducibility repository:
  `https://github.com/Saru1228/midge-swarm-nonaffine-residuals`, release tag
  `v4157-availability`.
- The section states that the raw three-dimensional midge-swarm trajectories are
  external published data and are not redistributed in the code repository.
- The open-ended Future Work wording in the Discussion was replaced by two
  bounded directions: comparative application to other weakly ordered
  collectives, and perturbation/richer-measurement experiments to identify what
  generates T1.
- `mypaper2/Latex/main_final.tex` was recompiled twice after the availability
  integration. The updated PDF remains `10` pages, with `0` LaTeX errors, `0`
  undefined control sequences, `0` citation warnings, `0` reference warnings,
  `0` rerun warnings, and `0` overfull boxes. Only `16` underfull-box layout
  warnings remain.
- The curated GitHub reproducibility repository was updated and pushed with tag
  `v4157-availability`. Its lightweight
  `python tools/verify_release.py` check passed after the update.
- `4157` is a manuscript and reproducibility-linking node, not a new scientific
  experiment. The scientific claim boundary from `4156` remains unchanged.

Latest 2026-09-02 414x status:

- `4140` froze definitions, checked reproducibility pointers, and found no
  stop-level definition mismatch.
- `4141` completed a strict limited-resolution full-pipeline omnibus
  pseudo-event run across all 19 observations after cache construction.
- The completed `4141` run used `n_null_replicates = 100` and
  `n_controls_per_replicate_observation = 40`.
- Observed support remained `N_both = 14/19` and `N_any = 15/19`.
- The `N_both` null distribution had mean `4.49`, q95 `8`, max `11`, and
  `p_both_ge_14 = 0.00990099`.
- The `N_any` null distribution had mean `10.36`, q95 `14`, max `16`, and
  `p_any_ge_15 = 0.03960396`.
- The both-scale result is the stronger reviewer-defense result; the any-scale
  result is supportive but less specific.
- This is still limited-resolution evidence, not a manuscript-ready formal
  high-replicate p-value, because `B=100` has limited p-value resolution.
- The `B>=1000` limitation in the original 4141/4149 implementation was later
  resolved by the chunked parallel 4155 implementation.
- `4142` completed a detrending challenge. The centered 1-second run reproduced
  `14/19` both-scale support; the past-only 1-second run reduced the stricter
  both-scale count to `11/19`; no-detrending robust-z gave `13/19`.
- `4142` is therefore a boundary rather than a stop: the T1 signal is not
  erased, but the manuscript should not claim that the exact `14/19`
  both-scale count is fully invariant to causal detrending.
- `4142` also found that the weaker `all_tangential` near-pre profile remains
  majority-supported under past-only detrending (`8/14`), but this timing
  profile should remain descriptive rather than causal.
- `4143` completed all-observation local-affine conditioning QC and passed:
  `38/38` observation/k combinations passed, all `19/19` observations passed
  both k values, median condition number across combos was `2.37`, max q95
  condition number was `6.28`, and no sampled fit had condition number greater
  than `100`.
- `4144` completed definition/notation/figure-source cleanup. It resolved or
  bounded all three review-007 gap items, produced six claim-boundary updates,
  and confirmed that all `5/5` final 4134 figure packages are present in the
  active LaTeX figure directory.
- `4145` integrated `4141-4144` into the active `mypaper2` manuscript and
  synchronized the English working drafts for Methods, Results, and
  Discussion/Conclusion.
- The active `mypaper2/Latex/main.pdf` was compiled twice after integration.
  The current draft is `10` pages, with `0` LaTeX errors and `0` unresolved
  reference/citation warnings. Only underfull-box layout warnings remain.
- This 4145 recommendation was superseded first by review 008 and then by the
  completed 4155 high-B run.
- Review `mypaper2/00_review/008.md` was read as the next submission-ready
  direction. A response was saved at `mypaper2/00_review/008_response.md`, and
  an executable route was saved at
  `idea/4146_4154_submission_hardening_route_from_review008.md`.
- `4146` completed the near-pre definition audit. The apparent `8/14` versus
  `11/14` discrepancy is explained by different gate and pseudo-event control
  definitions, not by a contradiction in the real event values. The original
  4085 `8/14` remains the main-text near-pre phase-localization count; 4142
  near-pre counts are now treated as sensitivity evidence only.
- The active Results text and English working draft were updated accordingly,
  and `mypaper2/Latex/main.pdf` was recompiled twice. The current PDF is 10
  pages, with no LaTeX errors and no unresolved reference/citation warnings;
  only underfull-box warnings remain.
- The recommended immediate next node from review 008 is now
  `4147_spectral_set_publication_provenance`, followed by notation cleanup
  before final reintegration.
- `4147` completed the `spectral_set` publication-provenance audit. The labels
  are reconstructable from the upstream 3032/3032b transfer-operator route
  using `r_rms`, `density_rms`, and `anisotropy`; the selected partition is
  `eig2`; label propagation passed; and label construction is T1-independent.
- Per the updated workflow preference, no PDF compilation was run after 4147.
  Compilation is now deferred until the final 4154 freeze unless a high-risk
  LaTeX structural edit requires an earlier syntax check.
- The recommended immediate next node is now
  `4148_notation_and_equation_consistency_audit`.
- `4148` completed the active-manuscript notation and equation consistency
  audit. The first pass found three fix-required but non-stop issues:
  `spectral_set` provenance in Methods, the undefined `B3` shorthand, and the
  near-pre endpoint distinction between 4085 and 4100. All three were corrected
  in active LaTeX files, and the final rerun passed with `0` stop failures and
  `0` fix-required items.
- No PDF compilation was run after 4148; compilation remains deferred until
  `4154_submission_package_freeze`.
- `4149` attempted a higher-replicate all-19 full-pipeline omnibus null
  (`B=1000`, `controls=40`) using the frozen 4141 implementation and existing
  `Output/4141/cache`.
- `4149` reached a compute boundary: the run did not produce p-value outputs
  within a 30-minute interactive limit, and the residual Python process was
  stopped. This is not a statistical negative result.
- At the 4149 point, the completed `4141` B=100 result remained the only
  completed all-19 omnibus null estimate. This was later superseded by 4155.
- `4150` completed final figure cleanup. It generated `Fig1_final` through
  `Fig5_final`, copied PNG/PDF versions into `mypaper2/Latex/figures`, removed
  the internal workflow note from Figure 1, removed recent-history evidence
  from the phenotype Figure 3, redesigned Figure 4A as observation-level
  held-out moment-closure evidence, and updated active LaTeX figure references
  to the final PDF files.
- No PDF compilation was run after 4150; compilation remains deferred until
  `4154_submission_package_freeze`.
- `4151` completed final manuscript reintegration. The active manuscript now
  describes the `B=100` pseudo-event result as limited-resolution
  pipeline-level calibration rather than as old internal terminology or formal
  high-B evidence. The 4149 compute boundary is kept out of the manuscript result
  text.
- Active-path text scan found no remaining `smoke` language, old 4134 figure
  filenames, or obvious internal draft labels in the files included by
  `main.tex`.
- No PDF compilation was run after 4151; compilation remains deferred until
  `4154_submission_package_freeze`.
- `4152` completed a technical supplement draft under `Supplement/`, with S1
  omnibus calibration, S2 detrending, S3 local affine QC, S4 scale/lag, S5
  state matching, S6 recent-history matching, S7 `spectral_set` construction,
  and S8 parameter registry.
- A technical supplement was kept for project traceability, and a sanitized
  journal-facing `Supplement/Supplement_submission.md` was produced before the
  4154 package freeze.
- No PDF compilation was run after 4152; compilation remains deferred until
  `4154_submission_package_freeze`.
- `4153` completed the final consistency audit across active LaTeX and the
  technical supplement. It found `0` stop items and `0` fix-required items.
  The `15` review-only items were manually cleared as bounded or negated
  contexts.
- `4154` completed the submission package freeze. `main_final.pdf` compiled as
  a 10-page final manuscript with `0` LaTeX errors, `0` unresolved
  citation/reference warnings, `0` overfull-box warnings, and `16`
  underfull-box layout warnings.
- `Output/4154/package/` now contains 37 frozen files, including the final PDF,
  final entrypoint, compile log, bibliography, active LaTeX source chain,
  final figure PDFs, submission-facing supplement, manifest, and code/data
  availability statement.
- `Output/4154/mypaper2_4154_submission_package.zip` archives this frozen
  package for easier transfer.
- `4155` completed the optional post-freeze high-B omnibus calibration using a
  chunked, resumable, parallel implementation.
- The completed `4155` run used `B = 1000`, `chunk_size = 50`, `workers = 4`,
  and `n_controls_per_replicate_observation = 40`.
- All `20/20` chunks completed with `0` worker failures. The fast prefix-sum
  event-window calculation passed equivalence validation against the original
  slicing implementation with maximum absolute difference
  `1.54e-14`.
- The `B=1000` result is `strong_pass_omnibus_null`: observed
  `N_both = 14/19` had `p_both_ge_14 = 0.000999000999000999`; observed
  `N_any = 15/19` had `p_any_ge_15 = 0.02197802197802198`.
- The both-scale null distribution had mean `4.38`, median `4`, q95 `7`, q99
  `9`, and max `12`; no null replicate reached the observed both-scale count.
- `4156` integrated the completed high-B result into the abstract, Methods,
  Results, evidence-to-claim table, Discussion, Conclusion, submission
  supplement, and current working drafts.
- `mypaper2/Latex/main_final.tex` was recompiled twice after 4156 integration.
  The final PDF remains `10` pages, with `0` LaTeX errors, `0` undefined
  control sequences, `0` citation warnings, `0` reference warnings, `0`
  rerun warnings, and `0` overfull boxes. Only `17` underfull-box layout
  warnings remain.
- `Output/4156/package/` contains the refreshed frozen package, including the
  final PDF, active LaTeX source chain, submission supplement, and 4155 high-B
  evidence files.
- `Output/4156/mypaper2_4156_submission_package.zip` passed zip integrity
  testing and supersedes the 4154 package as the latest frozen manuscript
  package.

Latest 4141 snapshot:

- `Status/history/2026-09-02_4141_stepwise_omnibus_null_smoke.md`

Latest 4142/4143 snapshot:

- `Status/history/2026-09-02_4142_4143_submission_hardening.md`

Latest 4144/4145 snapshot:

- `Status/history/2026-09-02_4144_4145_manuscript_reintegration.md`

Latest 4141 routing note:

- `idea/4141_full_pipeline_omnibus_survival_null_result_and_routing.md`

Latest 4142/4143 routing notes:

- `idea/4142_detrending_challenge_result_and_routing.md`
- `idea/4143_local_affine_conditioning_qc_result_and_routing.md`

Latest 4144/4145 routing notes:

- `idea/4144_definition_notation_figure_cleanup_result_and_routing.md`
- `idea/4145_manuscript_reintegration_result_and_routing.md`

Latest 4146 routing note:

- `idea/4146_near_pre_definition_audit_result_and_routing.md`

Latest 4146 snapshot:

- `Status/history/2026-09-02_4146_near_pre_definition_audit.md`

Latest 4147 routing note:

- `idea/4147_spectral_set_publication_provenance_result_and_routing.md`

Latest 4147 snapshot:

- `Status/history/2026-09-02_4147_spectral_set_publication_provenance.md`

Latest 4148 routing note:

- `idea/4148_notation_and_equation_consistency_result_and_routing.md`

Latest 4148 snapshot:

- `Status/history/2026-09-02_4148_notation_and_equation_consistency.md`

Latest 4149 routing note:

- `idea/4149_highB_full_pipeline_omnibus_null_boundary_and_routing.md`

Latest 4149 snapshot:

- `Status/history/2026-09-02_4149_highB_omnibus_compute_boundary.md`

Latest 4150 routing note:

- `idea/4150_final_figure_cleanup_result_and_routing.md`

Latest 4150 snapshot:

- `Status/history/2026-09-02_4150_final_figure_cleanup.md`

Latest 4151 routing note:

- `idea/4151_final_manuscript_reintegration_result_and_routing.md`

Latest 4151 snapshot:

- `Status/history/2026-09-02_4151_final_manuscript_reintegration.md`

Latest 4152 routing note:

- `idea/4152_supplement_build_result_and_routing.md`

Latest 4152 snapshot:

- `Status/history/2026-09-02_4152_supplement_build.md`

Latest 4153 routing note:

- `idea/4153_final_consistency_audit_result_and_routing.md`

Latest 4153 snapshot:

- `Status/history/2026-09-02_4153_final_consistency_audit.md`

Latest 4154 routing note:

- `idea/4154_submission_package_freeze_result.md`

Latest 4154 snapshot:

- `Status/history/2026-09-02_4154_submission_package_freeze.md`

Latest 4155 routing note:

- `idea/4155_parallel_highB_omnibus_null_result_and_routing.md`

Latest 4155 snapshot:

- `Status/history/2026-09-02_4155_parallel_highB_omnibus_null.md`

Latest review-008 routing note:

- `idea/4146_4154_submission_hardening_route_from_review008.md`

Latest 4141 archived output:

- `Output/4141/runs/smoke_n100_c40/`

Latest 2026-08-31 paper2 status:

- Sections 02-06 were reviewed for current manuscript consistency, with special
  attention to the corrected T1 definition, unified Results logic, and updated
  Discussion/Conclusion framing.
- `mypaper2/01_title_abstract/draft_zh.md` and
  `mypaper2/01_title_abstract/draft_en.md` were revised to v2.
- The active working title is now:
  `Local Tangential Non-Affine Activity Persists in Laboratory Midge Swarms
  Beyond Affine Geometry and Compact-State Reductions`.
- The abstract now uses 14/19 both-scale survival as the primary anchor,
  retains 15/19 any-scale survival as support, includes 14/15 survivor-class
  robustness, and frames T1 as a measurable local residual layer rather than a
  completed mechanism.
- `mypaper2/05_results_reduction_boundaries/draft_en.md` was updated to v2 so
  the English Results drafts match the unified Results logic.
- The LaTeX manuscript was synchronized to the current v2 structure:
  `04_results_v2.tex` and `05_discussion_conclusion_v2.tex` are now active in
  `main.tex`.
- `pdflatex -interaction=nonstopmode main.tex` was run twice from
  `mypaper2/Latex/`; `main.pdf` compiles successfully as a 9-page draft.
- Log check found no LaTeX errors, undefined citations, or unresolved
  cross-reference warnings; remaining notices are underfull-box layout
  warnings.
- Detailed latest snapshot:
  `Status/history/2026-08-31_mypaper2_title_abstract_latex_v2_compile.md`.

Previous 2026-08-31 paper2 status:

- `mypaper2/06_discussion_conclusion/draft_en.md` was rewritten as Discussion
  and Conclusion Draft v2 from the Chinese v2 logic.
- The English v2 draft foregrounds the main interpretive claim: T1 is valuable
  because it marks a measurable local residual layer after ordinary local
  affine geometry has been removed, not because it proves a complete mechanism.
- It now includes sections on why the result is interesting, relation to
  existing midge-swarm work, relevance to other collective-motion systems,
  positive/negative results as a joint contribution, alternative
  interpretations, limitations, broad future work, and a candidate conclusion.
- LaTeX Discussion/Conclusion files have not yet been synchronized with this
  English draft.
- Detailed latest snapshot:
  `Status/history/2026-08-31_mypaper2_discussion_conclusion_english_v2.md`.

Previous 2026-08-31 paper2 status:

- Review `mypaper2/00_review/005.md` was read as a Discussion/Conclusion
  framing review.
- A direct response was written at `mypaper2/00_review/005_response.md`.
- `mypaper2/06_discussion_conclusion/draft_zh.md` was revised to v2.
- The revised 06 Chinese draft now foregrounds why the result is interesting:
  T1 marks a measurable local residual layer after ordinary local affine
  geometry has been removed, rather than a completed swarm mechanism.
- It adds a careful relation to non-uniform spatial sampling, existing
  low-dimensional/stochastic midge-swarm work, fish-school and other
  collective-motion analogies, alternative explanations, limitations, and
  broad future-work categories.
- Detailed latest snapshot:
  `Status/history/2026-08-31_mypaper2_discussion_conclusion_chinese_v2.md`.

Previous 2026-08-31 paper2 status:

- A unified Chinese Results logic map was added at
  `mypaper2/00_overview/results_unified_logic_zh.md`.
- `mypaper2/04_results_local_nonaffine/draft_zh.md` and
  `mypaper2/05_results_reduction_boundaries/draft_zh.md` were reframed as
  Part I and Part II of one Results chain:
  existence -> robustness -> phenotype -> failed reductions -> empirical
  boundary.
- This update keeps 04 and 05 as separate discussion files for readability,
  but treats them as one manuscript Results section.
- Detailed latest snapshot:
  `Status/history/2026-08-31_mypaper2_results_unified_chinese_logic.md`.

Previous 2026-08-31 paper2 status:

- The English Data/Methods working draft was updated at
  `mypaper2/03_data_methods/draft_en.md`.
- The active LaTeX manuscript now uses `mypaper2/Latex/02_data_v2.tex` and
  `mypaper2/Latex/03_methods_v2.tex`.
- Section 02/03 now consistently defines T1 as focal-neighborhood local
  tangential non-affine activity computed from finite-lag relative neighbor
  displacement residuals after equal-weight local affine deformation removal.
- `mypaper2/Latex/01_introduction_v2.tex` received a minimal consistency pass
  so its conceptual T1 definition no longer describes a raw focal velocity
  residual.
- `pdflatex -interaction=nonstopmode main.tex` was run twice from
  `mypaper2/Latex/`; `main.pdf` compiles successfully as a 9-page draft.
- Log check found no LaTeX errors, undefined citations, or unresolved
  cross-reference warnings; remaining notices are underfull-box layout warnings.
- Detailed latest snapshot:
  `Status/history/2026-08-31_mypaper2_data_methods_english_latex_v2.md`.

Previous 2026-08-31 paper2 status:

- Review `mypaper2/00_review/003.md` was read as a methods-precision audit for
  the third manuscript section.
- A direct response was written at `mypaper2/00_review/003_response.md`.
- `mypaper2/03_data_methods/draft_zh.md` was revised from Data/Methods Chinese
  v2 to v3.
- The key correction is that frozen T1 should not be described as a raw focal
  individual velocity residual. It is a focal-neighborhood local tangential
  non-affine activity computed from finite-lag relative neighbor displacement
  residuals after equal-weight local affine deformation has been removed.
- The v3 draft now records code-confirmed implementation details for kNN
  neighborhoods, equal-weight local affine fitting, unsigned versus signed T1
  quantities, `C`/`dCdt`/`R` definitions, transition-event rules, event windows,
  non-event controls, state-matched controls, grouped leave-one-observation-out
  validation, and 413x observation-level support wording.
- Detailed latest snapshot:
  `Status/history/2026-08-31_mypaper2_review003_data_methods_v3.md`.

Latest 2026-08-30 paper2 status:

- `mypaper2/03_data_methods/draft_zh.md` was rewritten as Data/Methods Chinese
  v2 to match the updated Introduction v3 / LaTeX Introduction v2 logic.
- The revised Data/Methods draft now treats the analysis as a reproducible
  explanatory-test chain: raw trajectories, local affine baseline, T1 residual,
  robustness, spatial/timing form, explanatory-variable sufficiency tests, and
  observation-level boundaries.
- It adds method-facing definitions for local affine velocity fitting,
  non-affine residuals, tangential T1, event-window aggregation, scale/lag
  robustness, state-matched event-locality, recent-history tests, and
  observation heterogeneity.
- It also lists implementation details that must be checked before final
  English Methods notation is frozen.
- Detailed latest snapshot:
  `Status/history/2026-08-30_mypaper2_data_methods_chinese_v2.md`.

Previous 2026-08-30 paper2 status:

- The Chinese Introduction v3 logic has now been translated into the active
  LaTeX manuscript as `mypaper2/Latex/01_introduction_v2.tex`.
- `mypaper2/Latex/main.tex` now inputs `01_introduction_v2` instead of
  `01_introduction_v1`.
- The new English Introduction includes parallel related work, non-affine
  residual methodology, the candidate-explanation chain, a first formula-level
  T1 definition, and a bounded contribution statement.
- `pdflatex -interaction=nonstopmode main.tex` was run twice from
  `mypaper2/Latex/`; `main.pdf` compiles successfully as an 8-page draft.
- No undefined citation/reference or LaTeX error was found in the checked log;
  remaining warnings are existing underfull-box layout warnings.
- Detailed latest snapshot:
  `Status/history/2026-08-30_mypaper2_latex_introduction_v2_compile.md`.

Previous 2026-08-30 paper2 status:

- `mypaper2/02_introduction/draft_zh.md` was rewritten as Introduction Chinese
  v3 after review `mypaper2/00_review/002.md`.
- The revised chapter keeps Related Work inside the Introduction, but organizes
  it as parallel literature directions: trajectory/spatial organization,
  macroscopic/statistical-physics descriptions, Langevin stochastic dynamics,
  perturbation/correlation studies, and non-affine residual methodology.
- A readable first formula for T1 was added, including local affine velocity
  fitting, non-affine residual definition, tangential projection, and
  event-window aggregation.
- Non-affine residual references were added to
  `mypaper2/08_references/core_references_zh.md` and
  `mypaper2/Latex/bibitems.tex`.
- The manuscript-facing language now emphasizes whether explanatory variables
  are sufficient to account for T1, rather than relying heavily on
  closure/reduction terminology.
- Detailed latest snapshot:
  `Status/history/2026-08-30_mypaper2_introduction_chinese_v3.md`.

Previous 2026-08-30 paper2 status:

- `mypaper2/02_introduction/draft_zh.md` was rewritten as Introduction Chinese
  v2 after review `mypaper2/00_review/001.md`.
- The revised chapter now uses a longer structure: weakly ordered midge swarms,
  related work, transition from global descriptions to local residuals, local
  affine motion as a kinematic null model, T1, and contribution boundaries.
- The "non-rigid body" phrasing has been replaced with a local kinematic
  null-model framing.
- EGRT/gate terminology remains outside the manuscript-facing text.
- Detailed snapshot:
  `Status/history/2026-08-30_mypaper2_introduction_chinese_v2.md`.

Previous 2026-08-28 paper2 status:

- A Chinese section-by-section discussion layer has been added before expanding
  the next English version.
- The recommended discussion entry is
  `mypaper2/00_overview/chinese_discussion_map.md`, followed by the `draft_zh.md`
  files in each section folder.
- Detailed Chinese-draft snapshot:
  `Status/history/2026-08-28_mypaper2_chinese_section_discussion_drafts.md`.
- The next recommended discussion target is
  `mypaper2/01_title_abstract/draft_zh.md`, because title and abstract decide
  whether the paper is framed as a phenomenon-boundary paper, a
  reduction-boundary paper, or a balanced combination.

Previous 2026-08-28 paper2 status:

- `mypaper2/` was initialized using the organizational pattern of `mypaper/`.
- The new manuscript workspace includes Markdown planning folders, a modular
  LaTeX draft, copied 4134 preview figures, and a copied bibliography file.
- The working title is:
  `Local Non-Affine Organization in Laboratory Midge Swarms Beyond Affine Geometry and Low-Dimensional State Descriptions`.
- The manuscript argument is built around a bounded empirical claim: T1 is a
  local tangential non-affine residual that survives local affine subtraction in
  most observations, but should not be upgraded into a universal mechanism.
- The LaTeX entry point is `mypaper2/Latex/main.tex`.
- `mypaper2/Latex/main.pdf` compiles successfully with `pdflatex`.
- The compiled draft is 7 pages; references and figure labels resolve; only
  minor underfull-box warnings remain.
- Detailed latest snapshot:
  `Status/history/2026-08-28_mypaper2_initial_manuscript_draft_status.md`.

Previous 2026-08-28 413x status:

- `4135_manuscript_style_technical_synthesis` was executed successfully after
  `4134`.
- The 4135 gate result is
  `pass_4135_manuscript_synthesis_complete_terminal_413x`.
- 4135 produced 5 title candidates, 8 main-claim registry rows, 7
  evidence-to-claim rows, 7 section-to-figure rows, 7 writing-boundary rows,
  and manuscript-style Markdown modules.
- The main writing outputs are `manuscript_story.md`,
  `abstract_skeleton.md`, `results_outline.md`, `discussion_outline.md`, and
  `limitations.md` under `Output/4135/`.
- The recommended working title is:
  `Local non-affine organization in laboratory midge swarms beyond affine geometry and low-dimensional state descriptions`.
- The `413x` synthesis route is now terminally complete. It should not
  automatically reopen mechanism search inside `413x`.
- Recommended next actions are paper/report development from `Output/4135`,
  final visual redesign from `Output/4134`, or deliberate opening of a new
  branch outside `413x`.
- Detailed latest snapshot:
  `Status/history/2026-08-28_4135_manuscript_style_technical_synthesis_status.md`.

Earlier 2026-08-28 status:

- `4134_figure_ready_evidence_panels` was executed successfully after the M5
  review.
- The 4134 gate result is
  `pass_4134_figure_panel_package_ready_for_4135`.
- 4134 produced 5 main figure-preview files, 16 panel metadata rows, 16 figure
  source-map rows, 5 figure-manifest rows, caption drafts, a main figure plan,
  and a supplementary figure plan.
- Figure 1 has now been built as a data/definition orientation figure using an
  Ob2 raw-data snapshot, the 4130 frozen definitions, and the 4085
  all-tangential event-aligned profile source.
- Figures 2-5 organize the positive phenomenon, spatial/timing structure,
  reduction boundaries, and observation heterogeneity.
- No panel sources are missing, and the generated preview figures are non-empty.
- These are figure-ready evidence-package previews, not final camera-ready
  publication graphics.
- The route may now enter `4135_manuscript_style_technical_synthesis`.
- Detailed latest snapshot:
  `Status/history/2026-08-28_4134_figure_ready_evidence_panels_status.md`.

Earlier M5 2026-08-28 status:

- `M5_REVIEW_before_4134` was executed successfully after `4130-4133`.
- The M5 gate result is `pass_M5_review_enter_4134_with_actions`.
- M5 reviewed 8 gates: 6 passed directly, 1 retained an explicit metadata
  boundary, 1 requires action inside `4134`, and 0 stopped the route.
- The review produced 16 figure-candidate panels, 8 claim-review rows, 8
  overclaim-risk rows, and a 7-step `4134` action checklist.
- The route may now enter `4134_figure_ready_evidence_panels`.
- The key required action is to build Figure 1 as a data/definition
  orientation figure; it is not already available as a final artifact.
- Main-figure claims are allowed only with boundary wording: T1 survival is
  common rather than universal; `C,dCdt,R` and event-locality are tested
  reduction failures rather than mechanism nonexistence claims; history is
  observation-specific rather than a universal memory rule.
- `C4_SIGNED_EVENT_HETEROGENEITY` is routed to supplement or a small boundary
  annotation.
- `C8_PROPAGATION_NOT_CONFIRMATORILY_TESTED` is routed to limitations or
  remaining open mechanism space, not a main result figure.
- Metadata-dependent heterogeneity claims remain descriptive only.
- Detailed snapshot:
  `Status/history/2026-08-28_M5_review_before_4134_status.md`.

Latest 2026-08-27 status:

- `4130_definition_and_evidence_registry` was executed successfully.
- `4131_robust_positive_phenomenon_atlas` was executed successfully.
- `4132_negative_mechanism_boundary_atlas` was executed successfully.
- `4133_observation_heterogeneity_map` was executed successfully.
- The 4130 gate result is
  `pass_4130_registry_ready_with_metadata_boundary`.
- The 4131 gate result is
  `pass_4131_positive_atlas_ready_with_secondary_boundaries`.
- The 4132 gate result is
  `pass_4132_negative_boundary_atlas_ready`.
- The 4133 gate result is
  `pass_4133_heterogeneity_map_ready_with_metadata_boundary`.
- The registry contains 10 definitions, 24 evidence rows, 8 claim-strength
  rows, and 4 metadata audit rows.
- The frozen positive object is `T1`: transition-linked local tangential
  non-affine residual after local affine deformation is removed.
- The allowed claim is bounded: most observations contain a reproducible local
  non-affine tangential residual, but it is not a universal mechanism.
- The positive atlas gives 6 phenomenon rows and 4 figure candidates.
- The negative boundary atlas gives 8 mechanism-boundary rows and 4 figure
  candidates.
- The heterogeneity map gives a 19-row observation master table, 12 descriptive
  associations, and 5 figure candidates.
- Negative/boundary results remain central: no stable `C,dCdt,R` moment
  closure, no robust event-timestamp excess after state matching, and no
  universal recent-history rule.
- Propagation remains `NOT_TESTED`, not disproven.
- The strongest descriptive heterogeneity associations are observation-index
  proxy vs T1 effect, T1 effect vs mean track length, stable failure vs route
  score, and history abs effect vs route score.
- Metadata-dependent heterogeneity claims, especially daytime/dusk and
  observation-order explanations, remain descriptive only.
- This status was superseded on 2026-08-28 by the successful
  `M5_REVIEW_before_4134`.
- Detailed snapshot:
  `Status/history/2026-08-27_4133_heterogeneity_map_status.md`.

Previous 2026-07-13 paper status:

The practical focus was manuscript-first polishing for the ISIS2026-style paper
under `mypaper/Latex/`.

The current paper title is:

> Switching and Mixing Maintain Midge Swarm Organization

The current compiled draft is:

- `mypaper/Latex/main.pdf`
- 6 pages
- compiles with two `pdflatex` passes
- no LaTeX errors or unresolved references
- only minor underfull-box warnings remain

Latest 2026-07-13 status:

- The post-paper follow-up direction was clarified: continue using the existing
  midge swarm dataset, but deepen the analysis through more explanatory
  macroscopic, mesoscopic, and local variables.
- The research question for the follow-up is now framed as variable
  explanation rather than variable accumulation: which variables best explain
  how midge swarm organization is dynamically maintained?
- A macro-variable literature pack was organized under
  `Reference/03_bibliography/papers/02_topic_collections/collective_variables_macro_observables/`,
  with a paper matrix, variable taxonomy, reading guide, and BibTeX starter
  file.
- The first-stage follow-up variables are planned around three groups:
  shape/density, dynamic neighbor networks, and layer exchange/radial flux.
- Advisor-report materials were created and cleaned into
  `Discussion/teacher_report_macro_variables_2026-07-13/`, including an
  English HTML outline and an English oral script.
- The detailed dated snapshot is
  `Status/history/2026-07-13_macro_variable_followup_and_teacher_report.md`.

Previous 2026-07-01 status:

- The active manuscript remains a 6-page compiled draft after a conservative
  page-budget pass. The retained compression is limited to shortened
  macroscopic-variable range descriptions and a light tightening of the later
  M1 method text and D1 caption.
- Displayed formulas in the active Methods/Data subsections were converted to
  numbered `equation` environments where appropriate.
- The first indicator function in the correlation-sum definition now includes
  an explicit definition of `\mathbf{1}(\cdot)`.
- The M1 global low-dimensionality method now clarifies delay embedding,
  Theiler-window exclusion, the meaning of scaling-fit `R^2`, and the role of
  surrogate comparisons as auxiliary controls rather than formal hypothesis
  tests.
- The macro-observable definitions now state concise value ranges and
  interpretation for `R(t)`, `M(t)`, `P(t)`, `E(t)`, and
  `p_inner(t)`.
- The M2 Results now report the macrostate residence-duration range
  explicitly: 0.64--1.51 s across the nine state subclasses.
- The M2 robustness wording was changed to `Robustness and sensitivity
  analyses`.
- The limitations section now frames `D_2(m)` as a conservative screen rather
  than an exhaustive nonlinear-dynamics identification, with Lyapunov-exponent
  and prediction-based diagnostics left as supplementary or future analyses.
- The active method figures now use the latest image sources:
  `mypaper/Latex/figures/d1.png` and `mypaper/Latex/figures/d2.png`.

Previous 2026-06-30 status:

- The former Fig. 2 spatial-stratification schematic was removed from the
  active manuscript because Fig. 1 already shows the raw frame and inner/outer
  relabeled representation.
- The paper structure was adjusted so `Data` is included within
  `\section{Methods}`. The Methods section now contains the trajectory
  dataset/preprocessing subsection, macroscopic observables, and the three
  analysis methods.
- The M3 `k`-sensitivity result is now included in the existing M3 Results
  subsection as a robustness sentence rather than a new result block.
- The first paragraph of the M3 method was tightened so the `k=8` rationale
  and sensitivity-grid description are concise and nonrepetitive.
- The compiled PDF remains 6 pages after these edits.
- A pure-text English-Chinese sentence-level review workspace was created under
  `Discussion/modules_2026-06-30/` and built to
  `Discussion/index_2026-06-30_bilingual_review.html`. It contains 214
  sentence-review cards with local note boxes and no embedded manuscript
  figures.

Previous 2026-06-24 status:

- M3 `k` sensitivity was tested in experiment `2009`.
- The core grid `k = [4, 6, 8, 10, 12, 16, 20]` passed.
- The pooled chance-corrected renewal time stayed subsecond across the grid,
  with all/all median values from about 0.38 to 0.60 s.
- The M3 method now states this robustness check directly, without adding a
  new Results subsection.
- Methods displayed-equation punctuation was polished.
- The compiled PDF remains 6 pages.

## 3. Current manuscript structure

The active LaTeX entry point is `mypaper/Latex/main.tex`.

It currently inputs:

- `00_abstract`
- `01_introduction_v3`
- `02_data_v2`
- `03_methods_v2`
- `04_results_04_05_v1`
- `05_discussion_conclusion_v3`
- `bibitems`

The active section folders are:

- `Part2/`
  - trajectory dataset/preprocessing
  - macroscopic observables
- `Part3/`
  - Methods
  - global low-dimensionality screening
  - macrostate residence and escape
  - local-neighborhood renewal
- `Part4/`
  - Results
  - global screening
  - coarse-grained state switching
  - neighbor mixing
  - the former separate joint-interpretation paragraph is now integrated into
    the neighbor-mixing results
- `Part5/`
  - Discussion and conclusion
  - main contribution
  - limitations
  - future work

## 4. Current scientific interpretation

The active manuscript logic is:

1. The data do not support a single global low-dimensional attractor as the
   main explanation of stable core-periphery organization.
2. Coarse-grained macrostates show structured residence and age-dependent
   escape.
3. Local neighbor identities renew rapidly beneath that macrostate persistence.
4. The `2009` sensitivity check shows that the M3 result is not a `k=8`
   artifact over the tested range.
5. The best current interpretation is multiscale dynamic maintenance:
   macrostate organization persists while local membership is continually
   renewed.

The low-dimensionality result should be treated as a conservative negative
screen. Local log-log scaling intervals in the correlation sum allow
correlation dimensions to be estimated, but they are not sufficient evidence
for a fractal attractor. Support for a global low-dimensional closure would
require robust saturation of `D_2(m)` and clear separation from surrogate
controls; the current results do not satisfy those criteria.

## 5. M2 reinforcement state

The `2002-2008` series strengthened the coarse-grained state-switching result.

Key takeaways:

- residence-age effects are supported by bootstrap uncertainty;
- `M_state` and `R_state` show the strongest observation-wise consistency;
- state-definition sensitivity checks pass across the compact smoothing,
  threshold, and segment-length grid;
- pre-escape changes are only locally supported;
- the geometric same-mean memoryless null is rejected for only part of the
  state set;
- therefore, M2 is stronger than a descriptive observation, but it does not
  replace M3.

The manuscript now uses M2 and M3 as complementary positive analyses:

- state-switching analysis: how coarse-grained macrostates persist and escape;
- neighbor-mixing analysis: whether that persistence requires fixed local
  membership.

## 6. Current 413x discussion boundaries

The 413x route should keep four boundaries explicit:

- lack of a universal mechanism does not mean the swarm lacks reproducible local
  structure;
- `T1` is a bounded collective observable, not a proven individual-level force;
- `NOT_SUPPORTED` means a tested reduction failed, while `NOT_TESTED` means the
  question remains outside the current evidence gate;
- metadata annotations cannot be upgraded into recording-condition explanations
  until the source metadata are independently verified.

## 7. Current recommended next step

If no new direction is specified, continue from the completed 4158 review-010
pre-submission polish in this order:

1. manually inspect `mypaper2/Latex/main_final.pdf` for figure placement,
   column breaks, table readability, and last-page balance;
2. optionally archive the GitHub release with a DOI after GitHub-Zenodo
   archiving is enabled;
3. apply journal-specific formatting once a target venue is chosen;
4. keep new mechanism search paused until the manuscript claim boundary is
   stable;
5. if continuing the research program rather than preparing submission, move to
   comparative application or observation-class stratification.

## 8. Detailed latest snapshot

The latest detailed snapshot is:

- `Status/history/2026-09-04_4158_review010_pre_submission_polish.md`
- `Status/history/2026-09-04_4157_repository_availability_manuscript_polish.md`
- `Status/history/2026-09-02_4156_highB_manuscript_integration_and_refreeze.md`

The latest 414x outputs are:

- `Output/4140/4140_summary.md`
- `Output/4140/frozen_analysis_contract.yaml`
- `Output/4141/4141_summary.md`
- `Output/4141/p_omnibus.json`
- `Output/4141/runs/smoke_n100_c40/`
- `idea/4141_full_pipeline_omnibus_survival_null_result_and_routing.md`
- `Output/4142/4142_summary.md`
- `Output/4142/decision.json`
- `idea/4142_detrending_challenge_result_and_routing.md`
- `Output/4143/4143_summary.md`
- `Output/4143/decision.json`
- `idea/4143_local_affine_conditioning_qc_result_and_routing.md`
- `Output/4144/4144_summary.md`
- `Output/4144/decision.json`
- `Output/4144/claim_boundary_updates.csv`
- `Output/4144/review007_gap_resolution.csv`
- `Output/4144/figure_source_manifest.csv`
- `idea/4144_definition_notation_figure_cleanup_result_and_routing.md`
- `Output/4145/4145_summary.md`
- `Output/4145/decision.json`
- `Output/4145/manuscript_integration_audit.csv`
- `Output/4146/4146_summary.md`
- `Output/4146/discrepancy_decision.json`
- `Output/4146/near_pre_definition_audit.csv`
- `idea/4146_near_pre_definition_audit_result_and_routing.md`
- `Output/4147/4147_summary.md`
- `Output/4147/decision.json`
- `Output/4147/spectral_set_provenance.md`
- `Output/4147/supplement_method.tex`
- `idea/4147_spectral_set_publication_provenance_result_and_routing.md`
- `Output/4148/4148_summary.md`
- `Output/4148/decision.json`
- `Output/4148/notation_registry.csv`
- `Output/4148/notation_errors.csv`
- `idea/4148_notation_and_equation_consistency_result_and_routing.md`
- `Output/4145/compile_audit.json`
- `idea/4145_manuscript_reintegration_result_and_routing.md`
- `Output/4149/4149_boundary_summary.md`
- `idea/4149_highB_full_pipeline_omnibus_null_boundary_and_routing.md`
- `Output/4150/4150_summary.md`
- `Output/4150/decision.json`
- `Output/4150/figure_source_map.csv`
- `idea/4150_final_figure_cleanup_result_and_routing.md`
- `Output/4151/4151_summary.md`
- `Output/4151/decision.json`
- `Output/4151/active_text_audit.csv`
- `idea/4151_final_manuscript_reintegration_result_and_routing.md`
- `Output/4152/4152_summary.md`
- `Output/4152/decision.json`
- `Output/4152/supplement_index.csv`
- `idea/4152_supplement_build_result_and_routing.md`
- `Output/4153/final_audit_summary.md`
- `Output/4153/decision.json`
- `Output/4153/review_item_resolution.csv`
- `idea/4153_final_consistency_audit_result_and_routing.md`
- `Output/4154/4154_summary.md`
- `Output/4154/decision.json`
- `Output/4154/compile_log_audit.csv`
- `Output/4154/submission_package_manifest.csv`
- `Output/4154/package/`
- `Output/4154/mypaper2_4154_submission_package.zip`
- `idea/4154_submission_package_freeze_result.md`
- `Experiment/run_4155_parallel_highB_omnibus_null.py`
- `Output/4155/4155_summary.md`
- `Output/4155/decision.json`
- `Output/4155/p_omnibus.json`
- `Output/4155/chunk_status.csv`
- `Output/4155/observation_null_pass_rates.csv`
- `Output/4155/runs/highB_n1000_c40/`
- `idea/4155_parallel_highB_omnibus_null_result_and_routing.md`
- `idea/4156_highB_manuscript_integration_and_refreeze_plan.md`
- `Output/4156/4156_summary.md`
- `Output/4156/decision.json`
- `Output/4156/compile_log_audit.csv`
- `Output/4156/manuscript_highB_update_audit.csv`
- `Output/4156/submission_package_manifest.csv`
- `Output/4156/package/`
- `Output/4156/mypaper2_4156_submission_package.zip`
- `idea/4156_highB_manuscript_integration_and_refreeze_result.md`
- `Output/4157/4157_summary.md`
- `Output/4157/decision.json`
- `Output/4157/compile_log_audit.csv`
- `Output/4157/code_data_availability_statement.md`
- `Experiment/run_4158_review010_pre_submission_polish.py`
- `Output/4158/4158_figure_summary.md`
- `Output/4158/decision.json`
- `Output/4158/compile_log_audit.csv`
- `Output/4158/figures/Fig2_final.pdf`
- `Output/4158/figures/Fig3_final.pdf`
- `idea/4158_review010_pre_submission_polish_result.md`
- `mypaper2/Latex/06_data_code_availability.tex`
- GitHub release checkout:
  `C:\Users\Saru\Desktop\TUAT\ResearchSampleCode\midge-swarm-nonaffine-residuals`
- GitHub release tag:
  `v4158-review010-polish`

The previous 414x detailed snapshot is:

- `Status/history/2026-09-02_4142_4143_submission_hardening.md`
- `Status/history/2026-09-02_4141_stepwise_omnibus_null_smoke.md`
- `Status/history/2026-09-01_4140_4141_submission_hardening_start.md`

The latest review response is:

- `mypaper2/00_review/008_response.md`

The previous review response is:

- `mypaper2/00_review/007_response.md`

The latest compiled paper is:

- `mypaper2/Latex/main_final.pdf`

The previous manuscript detailed snapshot is:

- `Status/history/2026-08-31_mypaper2_title_abstract_latex_v2_compile.md`

The previous data-methods snapshot is:

- `Status/history/2026-08-31_mypaper2_review003_data_methods_v3.md`

## 9. Current submission-readiness boundary

After review 007 and the 414x hardening checks, the manuscript is intentionally
framed as a bounded
diagnostic empirical paper:

- it supports a reproducible local tangential non-affine residual in most
  recordings;
- it does not claim a completed mechanism, online prediction, attractor proof,
  or universal law;
- compact-state, event-timing, and recent-history reductions are reported as
  tested but insufficient explanations;
- observation identity is the grouping and replication unit, with 19 separate
  recordings rather than 19 independent biological populations.

After the 4158 review-010 polish, the remaining pre-submission additions are
now narrower:

1. review the integrated 11-page draft for prose length, figure placement,
   table readability, and final-page balance;
2. optionally create a DOI archive for the GitHub release;
3. apply journal-specific formatting once a target venue is chosen;
4. keep new mechanism search paused until the manuscript claim boundary is
   stable;
5. treat another omnibus-null rerun as optional, not as the current bottleneck.

## 10. Legacy 413x pointers

The latest detailed snapshot is:

- `Status/history/2026-08-31_mypaper2_review003_data_methods_v3.md`

The latest 413x roadmap is:

- `idea/413x_phenomenon_boundary_evidence_synthesis_roadmap.md`

The latest 4130 routing note is:

- `idea/4130_definition_and_evidence_registry_result_and_routing.md`

The latest 4131/4132 routing notes are:

- `idea/4131_positive_phenomenon_atlas_result_and_routing.md`
- `idea/4132_negative_mechanism_boundary_atlas_result_and_routing.md`

The latest 4133 routing note is:

- `idea/4133_observation_heterogeneity_map_result_and_routing.md`

The latest M5 routing note is:

- `idea/4133_M5_review_before_4134_result_and_routing.md`

The latest 4134 routing note is:

- `idea/4134_figure_ready_evidence_panels_result_and_routing.md`

The latest 4135 routing note is:

- `idea/4135_manuscript_style_technical_synthesis_result_and_routing.md`
