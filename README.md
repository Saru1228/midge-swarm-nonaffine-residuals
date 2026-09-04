# Midge Swarm Nonaffine Residuals

Reproducible analysis package for the manuscript:

**Local affine subtraction reveals persistent tangential non-affine activity in laboratory midge swarms**

This repository contains the curated code, frozen manuscript artifacts, selected
summary outputs, and high-replicate null-calibration results used for the
submission-facing version polished at node `4158`. It is intentionally smaller
than the full working directory: raw trajectory data, large intermediate frame
tables, temporary caches, and exploratory dead-end artifacts are not bundled.

Historical local data paths in copied provenance outputs have been sanitized to
`data/raw` for public release. Pass the actual raw-data directory explicitly with
`--data-dir`.

## Main Result

Under the frozen centered pipeline, `14/19` observations met the both-scale T1
residual-support criterion. In the completed full-pipeline pseudo-event omnibus
null calibration, `B=1000` null replicates were run with 40 non-event controls
per observation per replicate. No null replicate reached the observed both-scale
count.

```text
observed N_both = 14/19
null N_both mean = 4.38
null N_both q95 = 7
null N_both q99 = 9
null N_both max = 12
plus-one empirical p_both_ge_14 = 0.000999000999000999
```

For manuscript prose, this is reported as approximately `p_emp = 0.001`. The
result supports a diagnostic residual layer, not a completed mechanism, causal
trigger, universal law, or preprocessing-invariant claim.

## Repository Contents

```text
Experiment/              Selected Python scripts for the manuscript-facing analysis
Output/4155/             Completed B=1000 high-B omnibus null run
Output/4156/             Final integrated manuscript freeze and package audit
Output/4157/             Manuscript availability-section polish and compile audit
Output/4158/             Review-010 figure/text polish and compile audit
Output/<other ids>/      Curated summaries and small tables from upstream nodes
Supplement/              Technical and submission-facing supplement drafts
manuscript/              Convenience copy of final PDF and active LaTeX source
docs/                    Reproducibility notes and pseudo-event algorithm details
Status/                  Current project status and final freeze snapshots
idea/                    Selected route and result notes
tools/verify_release.py  Lightweight integrity check for the frozen release
```

## Quick Verification Without Raw Data

From the repository root:

```bash
python tools/verify_release.py
```

This checks the frozen `4155`, `4156`, and `4158` metrics, verifies the packaged
zip, and confirms that the manuscript contains the repository availability
statement.

## Rebuilding the Manuscript PDF

If `pdflatex` is installed:

```bash
cd manuscript/latex
pdflatex -interaction=nonstopmode main_final.tex
pdflatex -interaction=nonstopmode main_final.tex
```

The node-4158 manuscript compiled as an 11-page PDF with no LaTeX errors, unresolved
citations, unresolved references, rerun warnings, or overfull boxes.

## Full Computational Rerun

A full rerun requires the external raw three-dimensional midge-swarm trajectory
files. See `DATA.md` and `REPRODUCIBILITY.md` for the expected data layout,
software environment, and staged commands.

The key high-B rerun entry point is:

```bash
python Experiment/run_4155_parallel_highB_omnibus_null.py --mode run --total-null 1000 --chunk-size 50 --workers 4 --n-controls 40 --data-dir /path/to/raw_trajectories
```

For a quick operational check only, use a much smaller replicate count and do
not treat it as statistical evidence.

## License

The repository uses the MIT License for code and documentation. Raw trajectory
data are external and retain their original terms.
