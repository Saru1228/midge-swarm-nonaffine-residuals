# 4147 spectral_set Algorithm

Date: 2026-09-02

## Reconstruction Steps

1. Start from `Output/3001/processed/geometric_center_observables_all.csv`.
2. Select the 3032 slow-variable basis:
   `r_rms, density_rms, anisotropy`.
3. Within each observation, robust-z standardize each slow variable using the
   median and IQR-based scale.
4. Pool the standardized frames and split each slow variable into
   `4` quantile bins.
5. Encode the three binned coordinates as one Ulam cell. With three variables
   and four bins per variable, the full grid has `64`
   possible cells; `60` were active.
6. Count empirical transitions between active Ulam cells at lag
   `0.1` s within each observation.
7. Row-normalize the count matrix to obtain an empirical transfer operator.
8. Compute right eigenvectors of that operator. For each nontrivial candidate
   eigenvector, split active cells at the stationary-mass weighted median.
9. Select the best partition by the 3032 gate metrics. The selected partition
   is `eig2`, eigen-rank `2`.
10. Materialize frame labels by mapping each frame's Ulam cell through the
    selected cell-to-set table.
11. Define transition events as switches between adjacent low/high runs,
    retaining only switches for which both adjacent runs last at least `0.20 s`.

## Quantile Edges

| variable | quantile_edges_z |
| --- | --- |
| r_rms | -0.664004, 7.73826e-05, 0.679194 |
| density_rms | -0.614568, 0, 0.72653 |
| anisotropy | -0.571281, 0, 0.772515 |

## Selected Partition Summary

| spectral_set | n_cells | stationary_mass_sum | pooled_retention | retention_lift | exit_probability |
| --- | --- | --- | --- | --- | --- |
| low | 32 | 0.5003 | 0.8753 | 0.375 | 0.1247 |
| high | 28 | 0.4997 | 0.8752 | 0.3754 | 0.1248 |

## Interpretation

The 3032 selected partition is a compact-density partition. In the selected
`eig2` partition, the high set has higher `density_rms`, lower
`r_rms`, and lower `anisotropy` than the low set according to the 3032
interpretive axis.
