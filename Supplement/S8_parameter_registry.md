# S8 Parameter Registry

## Purpose

This section records the frozen parameters and gates used by the current
manuscript path.

## Dataset

```text
recordings = 19 laboratory Chironomus riparius swarm observations
sampling rate = 100 Hz
replication/grouping unit = observation
primary raw data path = user-provided local dataset, accessed through code as a configurable data directory
```

The observations are separate recordings of the same laboratory swarm system.
They are not treated as 19 independent biological populations.

## T1 Definition

```text
neighborhood sizes for primary survival = k=8 and k=10
default lag = 0.10 s
neighbor inclusion = present at reference frame and finite-lag frame
minimum retained neighbors = 4
local affine fit = equal-weight least squares on finite-lag relative displacements
residual = finite-lag displacement residual divided by lag duration
projection = tangential component relative to swarm-centered radial direction
```

## Event and Control Windows

```text
pre window = [-0.20, 0) s
post window = [0, 0.20] s
non-event exclusion from true transitions = 0.80 s
non-event replicates = 40
event-aligned profile range = [-0.50, 0.50] s
event-aligned profile step = 0.05 s
phase bins:
  early-pre = [-0.50, -0.25) s
  near-pre = [-0.25, 0.00) s
  near-post = [0.00, 0.25] s
  late-post = (0.25, 0.50] s
```

The 4100 state-matched near-pre aggregate used an endpoint-inclusive
`[-0.25, 0.00]` window. This is intentionally distinguished from the
half-open 4085 phase-bin convention.

## Standardization and Detrending

```text
primary preprocessing = robust-z within observation
slow-trend removal = one-second centered rolling mean subtraction
post-detrending standardization = robust-z within observation
sensitivity variants = one-second past-only detrending and no-rolling robust-z
```

Because the primary detrending uses a centered window, event-aligned time
profiles are interpreted descriptively rather than as online prediction.

## Survival Gate

```text
local_event_minus_non_event_direction_z > 0.03
p_non_event_direction_ge_event <= 0.35
local_to_b3_direction_ratio >= 0.30
both-scale support = pass at both k=8 and k=10
any-scale support = pass at at least one of k=8 or k=10
```

Here, `B3` denotes the upstream global-affine residual baseline.

## State-Matched Event-Locality Parameters

```text
state variables = (C, dC/dt, R)
matches per event = up to 5
maximum state-match distance = 0.75
minimum total acceptable event fraction = 0.75
shifted-event null replicates = 80
```

## Recent-History Parameters

```text
current state = (C, dC/dt, R)
history window = 0.50 s
state distance threshold = 0.50
history angle contrast threshold = 90 degrees
minimum temporal separation = 1.0 s
within-observation history shuffle replicates = 100
```

## Figure Package

```text
final figure source = Output/4150/figures/
active manuscript copies = mypaper2/Latex/figures/Fig1_final.pdf through Fig5_final.pdf
```

## Main Source Nodes

```text
4141/4155 omnibus calibration
4142 detrending challenge
4143 local affine conditioning QC
4146 near-pre definition audit
4147 spectral_set provenance
4148 notation consistency audit
4150 final figure cleanup
4151 manuscript reintegration
```
