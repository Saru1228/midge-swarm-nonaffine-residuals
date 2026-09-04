# Node 4151 Summary

## Purpose

Reintegrate the 4146-4150 hardening results into the active manuscript path
without changing analysis definitions or adding a formal high-B result that was
not completed.

## Result

`pass_4151_active_manuscript_reintegrated_without_internal_smoke_language`

## Main Changes

The active LaTeX manuscript now uses `Fig1_final.pdf` through
`Fig5_final.pdf`.

The manuscript text now describes the `B=100` pseudo-event result as a
limited-resolution full-pipeline calibration rather than as a smoke-null or
formal high-resolution p-value.

The 4149 compute boundary was not inserted into the manuscript as a result.
It remains a route/status note and a future batch/overnight statistical
hardening option.

## Files Changed

```text
mypaper2/Latex/00_abstract.tex
mypaper2/Latex/Part2/02_data_trajectory_dataset.tex
mypaper2/Latex/Part3/03_methods_affine_reduction_and_controls_v2.tex
mypaper2/Latex/Part4/04_results_t1_survival_v2.tex
mypaper2/Latex/Part4/04_results_diffuse_phenotype_v2.tex
mypaper2/Latex/Part4/04_results_failed_reductions_v2.tex
mypaper2/Latex/Part4/04_results_empirical_boundary_v2.tex
mypaper2/Latex/Part5/05_discussion_limitations_future_v2.tex
mypaper2/Latex/Part5/05_conclusion_v2.tex
```

## Verification

An active-path text scan found no matches for internal smoke-null language or
old 4134 figure names in the files included by `main.tex`.

No PDF compilation was run at 4151. Compilation remains deferred until
`4154_submission_package_freeze`.

## Next

Proceed to `4152_supplement_build`.
