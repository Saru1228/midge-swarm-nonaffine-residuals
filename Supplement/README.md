# Supplementary Materials

This directory collects the supporting analyses for the current midge-swarm
T1 manuscript. The supplement is organized around the evidence chain rather
than around experiment-node numbers, but each section lists the source outputs
needed for traceability.

## Sections

| section | topic | main role |
| --- | --- | --- |
| S1 | Full-pipeline omnibus calibration | Observation-level pseudo-event calibration of the 14/19 both-scale count |
| S2 | Detrending challenge | Sensitivity of survival and timing counts to centered, past-only, and no-rolling preprocessing |
| S3 | Local affine conditioning QC | Numerical check that local affine fits are rank-sufficient and well-conditioned |
| S4 | Scale and lag sensitivity | Survivor-class robustness under nearby neighborhood scale and temporal lag choices |
| S5 | Compact-state and event-locality tests | Negative reduction tests using `(C, dC/dt, R)` state matching |
| S6 | Recent-history matching | Same-current-state / different-history boundary analysis |
| S7 | `spectral_set` construction | Provenance of low/high compact-density labels |
| S8 | Parameter registry | Frozen parameters, gates, and source paths |

## Current Boundary

The completed omnibus calibration now uses `B=1000` null replicates and 40
non-event controls per observation per replicate. The original monolithic
high-B attempt reached an interactive compute boundary, but the later chunked
parallel run completed all `1000/1000` replicates and resolved that boundary.
