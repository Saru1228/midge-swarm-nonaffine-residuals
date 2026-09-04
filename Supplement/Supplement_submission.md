# Supplementary Material

## S1. Full-Pipeline Pseudo-Event Calibration

The omnibus calibration asked whether the observed number of T1-surviving
observations could be reproduced by pseudo-events passed through the same
analysis pipeline as the real transitions. Pseudo-event centers were sampled
within the same observation while avoiding true transition windows. Non-event
controls were also sampled within the same observation and avoided both true
and pseudo-event windows.

The survival gate was identical to the main analysis: the local event-control
excess had to exceed `0.03` robust-z units, the empirical non-event tail
fraction had to be no greater than `0.35`, and the local/global-affine
retention ratio had to be at least `0.30`. The primary omnibus statistic was
the number of observations passing the gate at both original neighborhood
scales. The `0.35` threshold was a frozen screening component, not a
conventional single-observation significance threshold.

For each observation and replicate, the pseudo-event count and low-to-high /
high-to-low event-type sequence matched the true event template. Candidate
centers were sampled within the same recording after excluding the event-window
margin and true transition centers with a `0.80 s` exclusion half-width.
Pseudo-events were sampled sequentially without mutual overlap when feasible;
if this became infeasible, the sampler fell back to true-event exclusion only,
and finally to uniform admissible sampling. The same pseudo-event realization
was used for `k=8` and `k=10`. Each replicate-observation generated 40
same-observation non-event control sets that avoided true and pseudo-event
centers. The high-replicate run used deterministic per-replicate seeds and was
merged from 20 chunks of 50 replicates.

The completed calibration used `B=1000` null replicates and 40 non-event
controls per observation per replicate. The observed both-scale count was
`14/19`, whereas the null distribution had mean `4.38`, median `4`, q95 `7`,
q99 `9`, and maximum `12`. No both-scale null replicate reached the observed
count; the plus-one empirical value was `1/(1000+1)`, reported in the main
text as approximately `0.001`. The observed any-scale count was `15/19`; the
corresponding null distribution had mean `10.223`, median `10`, q95 `14`, q99
`15`, and maximum `17`, with plus-one empirical p-value `0.022`.

This result is reported as high-replicate pipeline-level calibration. It does
not constitute evidence for a completed biological mechanism.

## S2. Detrending Challenge

The preprocessing sensitivity analysis compared three variants. The frozen
variant subtracted a one-second centered rolling mean and then robust-z
standardized the residual. The causal variant subtracted a one-second
past-only rolling mean. The third variant skipped rolling detrending and used
robust-z standardization only.

Under the frozen centered variant, both-scale support was `14/19` and any-scale
support was `15/19`. Under past-only detrending, both-scale support dropped to
`11/19` while any-scale support was `16/19`. Without rolling detrending,
both-scale support was `13/19` and any-scale support was `16/19`.

The signal was therefore not erased by alternative preprocessing, but the
exact `14/19` both-scale count was not preprocessing-invariant. The main text
uses the centered definition as the frozen primary analysis and reports the
other variants as sensitivity checks.

Near-pre timing was also sensitive to definition. In the detrending-specific
phase summary, near-pre support for the all-tangential variable was `11/14`
under centered detrending, `8/14` under past-only detrending, and `12/14`
without rolling detrending. These sensitivity counts are not replacements for
the main phase-localization count because the gate and pseudo-event sampler
were not identical.

## S3. Local Affine Conditioning Quality Control

Local affine conditioning was checked for every observation at both original
neighborhood scales. The quality-control screen required high valid-fit and
rank-sufficient fractions, low median and q95 condition numbers, and no
concentration of the largest T1 samples in severely ill-conditioned fits.

All `38/38` observation-scale combinations passed the screen, and all `19/19`
observations passed both neighborhood scales. The median valid-fit fraction
was `1.0`, and the minimum valid-fit fraction was `0.999763481551561`. The
median condition number across combinations was `2.3674845690394064`, the
largest q95 condition number was `6.282690016495806`, and no sampled fit had
condition number greater than `100`. The median condition number among the
top five percent of T1 samples was `2.061165679743935`.

This quality-control result supports the numerical defensibility of the local
affine subtraction. It does not by itself establish a biological mechanism.

## S4. Scale and Lag Sensitivity

The primary survival analysis used two original neighborhood scales, `k=8` and
`k=10`, with default lag `0.10 s`. T1 survived at either scale in `15/19`
observations and at both scales in `14/19` observations. Within the survivor
class, `14/15` observations remained stable under nearby scale and temporal
lag choices.

The scale/lag result is therefore a survivor-class robustness result. It
should not be generalized to all observations.

## S5. Compact-State and Event-Locality Tests

The compact-state reduction tested whether T1 could be stably summarized by
the low-dimensional state vector `(C, dC/dt, R)`, where `C` is the
compact-density coordinate, `dC/dt` is its smoothed temporal gradient, and `R`
is the swarm-scale radius coordinate.

Grouped out-of-sample moment-closure tests did not support a stable reduction.
For the first-moment target, the median incremental `R2` was
`-0.0006327793`, the positive-observation fraction was `0.2105263158`, and
the median real-minus-shift increment was `-0.0003082888`. For the
second-moment target, the median incremental `R2` was `-0.0006213903`, the
positive-observation fraction was `0.1578947368`, and the median
real-minus-shift increment was `-0.0006586480`.

The event-locality test matched true transition frames to non-event frames in
the same observation with similar `(C, dC/dt, R)` state. The median
event-minus-control near-pre effect was `-0.03288737643286521`, the
same-direction observation fraction was `0.42105263157894735`, and the real
effect exceeded the shifted-event null in `0.275` of tested comparisons. The
total acceptable event fraction was `0.9796057104010877`, with median best
match distance `0.17630717293908968`.

Matching used Euclidean distance in robust-standardized `(C, dC/dt, R)` space.
Candidate controls were ranked by distance, up to five nearest matches were
retained, and an event was accepted only when the best match distance was at
most `0.75`. Controls were not removed after use, so a non-event frame could in
principle match more than one true event.

These results show that the tested compact-state moment closure and
state-matched event-locality route did not provide stable reductions of T1.
They do not rule out richer state variables, delayed models, network features,
or transition dynamics in general.

## S6. Recent-History Matching

The recent-history test asked whether frames with similar current state but
different recent paths showed different T1. Current state was matched within
observation using `(C, dC/dt, R)`. The primary history feature was the recent
path direction over `0.50 s`; paired frames required a history-angle contrast
of at least `90` degrees and temporal separation of at least `1.0 s`.

For a history window `h`, the recent path vector was
`Delta X_h(t) = [C(t)-C(t-h), R(t)-R(t-h)]`; the history angle was the angle of
this vector in the `C-R` plane. The primary setting used `h=0.50 s`, current
state distance threshold `0.50`, up to five nearest contrasted-history pairs
per anchor, and at most 10000 pairs per observation.

All `19/19` observations had sufficient matched pairs. The median number of
selected pairs per sufficient observation was `4723`, the median paired-frame
fraction was `0.7720488466757124`, and the median state distance was
`0.2972932945091832`.

The median signed history-axis T1 difference was
`-0.011040047877916181`, while the median absolute signed difference was
`0.07628898491170816`. The direction consistency fraction was
`0.5263157894736842`. Absolute history effects exceeded the shuffled-history
median in `14/19` observations but exceeded the q95 shuffled threshold in only
`6/19` observations.

Recent history was therefore informative in an observation-specific way, but
it did not define a universal memory rule.

## S7. Low/High Compact-Density Labels

Low/high compact-density labels were inherited from an upstream
transfer-operator coarse graining based on robust-standardized `r_rms`,
`density_rms`, and `anisotropy`. The selected partition used a 4-bin Ulam grid
in each variable, producing 64 total cells and 60 active cells. The selected
split was based on the leading nontrivial transfer-operator eigenfunction.

The lag was `0.10 s`, the leading nontrivial eigenvalue was
`0.8564307275942583`, the minimum pooled retention was
`0.8751650955023956`, and the minimum retention lift was
`0.3750263483202336`. The final labels covered `334542` frames across all 19
observations, with `167210` low labels and `167332` high labels.

The label construction used compact-density variables upstream of the T1
analysis and did not use T1 values. These labels should therefore be described
as inherited compact-density labels, not as thresholds optimized for T1.

## S8. Frozen Parameters

The dataset consists of 19 laboratory observations of three-dimensional
Chironomus riparius swarm trajectories sampled at 100 Hz. Observation identity
was the grouping unit in cross-observation analyses.

The primary T1 observable used neighborhood sizes `k=8` and `k=10`, lag
`0.10 s`, retained only neighbors present at both the reference and lagged
frames, required at least four retained neighbors, fitted local affine
deformation by equal-weight least squares, and projected the resulting
non-affine finite-lag residual onto the local tangential direction.

Primary pre/post summaries used `[-0.20,0)` s and `[0,0.20]` s windows relative
to each transition. Non-event control centers were required to be at least
`0.80 s` away from true transitions, and 40 non-event replicates were used.
Event-aligned profiles covered `[-0.50,0.50]` s in `0.05 s` steps.

The state-matched event-locality test used `(C, dC/dt, R)`, up to five matches
per event, maximum state-match distance `0.75`, and 80 shifted-event null
replicates. The recent-history test used current-state distance threshold
`0.50`, history window `0.50 s`, history-angle contrast threshold `90`
degrees, minimum temporal separation `1.0 s`, and within-observation history
shuffle controls.
