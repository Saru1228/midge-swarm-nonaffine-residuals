# Reproducibility Notes

This repository supports three reproducibility levels.

## Level 0: Verify the Frozen Release

This level does not require raw data. It verifies that the archived manuscript
package and high-B result files are internally consistent.

```bash
python tools/verify_release.py
```

Expected key outputs:

```text
availability_gate_result = pass_4157_repository_availability_integrated_and_compiled
gate_result = pass_4156_highB_integrated_submission_package_refrozen
B = 1000
observed N_both = 14
p_both_ge_14 = 0.000999000999000999
zip_bad_file = None
```

## Level 1: Rebuild the PDF

This level requires a LaTeX installation with IEEEtran and standard packages.

```bash
cd manuscript/latex
pdflatex -interaction=nonstopmode main_final.tex
pdflatex -interaction=nonstopmode main_final.tex
```

The node-4157 manuscript produced a 10-page PDF with the public repository
availability section included before the references.

## Level 2: Reaudit the Completed High-B Run

The completed high-B chunks and merged outputs are included under
`Output/4155/runs/highB_n1000_c40/`. The manuscript-facing summary files are
also copied under `Output/4156/package/highB_evidence_4155/`.

The run used deterministic chunks:

```text
total replicates = 1000
chunk size = 50
number of chunks = 20
workers used in original run = 4
controls per observation per replicate = 40
```

## Level 3: Rerun From External Trajectories

Install dependencies:

```bash
python -m venv .venv
# Windows
.venv\Scripts\python -m pip install -r requirements.txt
# macOS/Linux
.venv/bin/python -m pip install -r requirements.txt
```

Place the published trajectory files outside the repository, or under a local
ignored directory such as `data/raw/`, and pass the path explicitly:

```bash
python Experiment/run_4001_geometric_baseline_residual_audit.py --data-dir /path/to/raw_trajectories
python Experiment/run_4002a_residual_spatial_structure_audit.py --data-dir /path/to/raw_trajectories
python Experiment/run_4081c_full_observation_adjudication.py --data-dir /path/to/raw_trajectories
python Experiment/run_4140_manuscript_freeze_reproducibility_audit.py
python Experiment/run_4141_full_pipeline_omnibus_survival_null.py --cache-only --obs all --data-dir /path/to/raw_trajectories
python Experiment/run_4155_parallel_highB_omnibus_null.py --mode run --total-null 1000 --chunk-size 50 --workers 4 --n-controls 40 --data-dir /path/to/raw_trajectories
```

Some upstream tables used by the manuscript are produced by earlier route nodes
whose scripts are included in `Experiment/`. The curated `Output/` directories
store the submission-facing summaries and small tables so that the manuscript
claim can be audited without retaining every large intermediate frame table.

## Pseudo-Event Omnibus Null Algorithm

For each null replicate `b` and observation:

```text
1. Use the same observation as the real event sequence.
2. Sample pseudo-event centers only from admissible frames.
3. Exclude frames too close to true transition windows.
4. Preserve the real event-count structure used by the frozen gate.
5. Recompute the same event-control metrics at k=8 and k=10.
6. Generate 40 non-event controls per replicate-observation.
7. Apply the frozen per-scale residual-support screen.
8. Record whether the observation passes at k=8, k=10, both scales, or any scale.
9. Aggregate N_both[b] and N_any[b] across all 19 observations.
10. Estimate plus-one empirical tails against the observed counts.
```

The per-scale survival rule is a frozen screening rule, not the manuscript-level
significance test. The manuscript-level calibration is the all-observation
full-pipeline pseudo-event omnibus distribution.

## Reporting Precision

The exact plus-one value for the both-scale omnibus tail is
`0.000999000999000999`. In manuscript prose, it should be rounded to
approximately `p_emp = 0.001`, together with the more informative statement that
`0/1000` null replicates reached `N_both = 14`.

## Repository Citation

For code and derived outputs, cite the release tag used by the manuscript:

```text
https://github.com/Saru1228/midge-swarm-nonaffine-residuals
release tag: v4157-availability
```
