"""4074 event-free versus event-conditioned audit.

This node asks whether the frozen residual organization is specific to
compact-density transition windows or also appears in matched non-event windows.

It uses:
- 4072 primary metrics
- 4071-passing metrics as the stable decision core
- B3 global affine residuals
- N5 matched non-event windows
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from textwrap import dedent

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_DIR = ROOT / "Experiment"
if str(EXPERIMENT_DIR) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_DIR))

import run_4002a_residual_spatial_structure_audit as r4002a  # noqa: E402


OUT = ROOT / "Output" / "4074"
SOURCE_PRIMARY = ROOT / "Output" / "4072" / "primary_metrics.csv"
SOURCE_4071 = ROOT / "Output" / "4071" / "metric_replication_summary.csv"

NODE = "4074_event_free_vs_event_conditioned_audit"
DATE = "2026-08-25"
RNG_SEED = 407401


OB_COLUMNS = [
    "ob",
    "variable",
    "taxonomy_class",
    "family",
    "is_4071_stable_core",
    "n_events",
    "real_direction_abs_contrast_z",
    "non_event_direction_abs_median_z",
    "direction_real_minus_non_event_z",
    "p_non_event_direction_ge_real",
    "direction_gt_non_event",
    "real_abs_activity_delta_z",
    "non_event_abs_activity_median_z",
    "activity_real_minus_non_event_z",
    "p_non_event_activity_ge_real",
    "activity_gt_non_event",
]


SUMMARY_COLUMNS = [
    "variable",
    "taxonomy_class",
    "family",
    "is_4071_stable_core",
    "n_ob_valid",
    "direction_gt_non_event_count",
    "median_direction_real_minus_non_event_z",
    "median_p_non_event_direction_ge_real",
    "activity_gt_non_event_count",
    "median_activity_real_minus_non_event_z",
    "median_p_non_event_activity_ge_real",
    "metric_event_conditioned_gate",
    "metric_event_free_activity_gate",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in columns})


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def finite_median(values: list[float]) -> float:
    arr = np.asarray(values, dtype="float64")
    arr = arr[np.isfinite(arr)]
    return float(np.median(arr)) if arr.size else math.nan


def md_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        vals = []
        for col in columns:
            val = row.get(col, "")
            if isinstance(val, float):
                vals.append("NA" if not np.isfinite(val) else f"{val:.4g}")
            else:
                vals.append(str(val).replace("\n", " ").replace("|", "\\|"))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def sample_non_event_times(
    events_ob: pd.DataFrame,
    rec: dict[str, np.ndarray],
    rng: np.random.Generator,
    exclusion_sec: float,
    prepost_window_sec: float,
) -> pd.DataFrame:
    t = np.asarray(rec["t"], dtype="float64")
    finite_t = t[np.isfinite(t)]
    if finite_t.size < 2:
        raise RuntimeError("No valid time range for non-event sampling.")
    t_min = float(np.nanmin(finite_t)) + prepost_window_sec
    t_max = float(np.nanmax(finite_t)) - prepost_window_sec
    real_times = pd.to_numeric(events_ob["event_t"], errors="coerce").to_numpy(dtype="float64")
    real_times = real_times[np.isfinite(real_times)]
    rows = []
    for event in events_ob.itertuples(index=False):
        sampled = math.nan
        for _ in range(1000):
            cand = float(rng.uniform(t_min, t_max))
            if real_times.size == 0 or float(np.min(np.abs(real_times - cand))) >= exclusion_sec:
                sampled = cand
                break
        if not np.isfinite(sampled):
            # Fallback: circular shift by at least exclusion_sec if the recording is dense with events.
            span = max(t_max - t_min, prepost_window_sec * 4)
            shift = float(rng.uniform(exclusion_sec, max(exclusion_sec * 2, span)))
            sampled = ((float(event.event_t) - t_min + shift) % span) + t_min
        rows.append(
            {
                "event_id": int(event.event_id),
                "ob": int(event.ob),
                "dataset": str(event.dataset),
                "event_t": sampled,
                "event_type": str(event.event_type),
            }
        )
    return pd.DataFrame(rows)


def direction_summary(features: pd.DataFrame, variable: str) -> dict[str, float]:
    d = r4002a.summarize_direction(features[features["variable"] == variable], prefix="real")
    if d.empty:
        return {
            "n_events": 0,
            "direction_abs": math.nan,
            "low_to_high": math.nan,
            "high_to_low": math.nan,
        }
    rec = d.iloc[0]
    return {
        "n_events": int(rec.get("n_events", 0)),
        "direction_abs": float(rec.get("real_abs_median_direction_contrast_z", math.nan)),
        "low_to_high": float(rec.get("real_median_low_to_high_delta_z", math.nan)),
        "high_to_low": float(rec.get("real_median_high_to_low_delta_z", math.nan)),
    }


def activity_summary(features: pd.DataFrame, variable: str) -> float:
    d = features[features["variable"] == variable].copy()
    if d.empty:
        return math.nan
    x = pd.to_numeric(d["signed_delta_post_minus_pre_z"], errors="coerce").abs().to_numpy(dtype="float64")
    x = x[np.isfinite(x)]
    return float(np.median(x)) if x.size else math.nan


def write_config(obs: list[int], n_replicates: int, exclusion_sec: float) -> None:
    text = dedent(
        f"""\
        node: {NODE}
        date: {DATE}
        node_type: event_selection_artifact_control
        source_primary_metrics: Output/4072/primary_metrics.csv
        source_stable_core: Output/4071/metric_replication_summary.csv
        baseline: B3_global_affine
        null_or_control: N5_matched_non_event_window
        observations: {",".join(str(x) for x in obs)}
        n_non_event_replicates: {n_replicates}
        exclusion_sec: {exclusion_sec}
        next_if_pass: 4080_local_affine_feasibility
        next_if_boundary: M0_review_or_4080_with_caveat
        next_if_fail: M0_boundary_review
        """
    )
    (OUT / "config.yaml").write_text(text, encoding="utf-8")


def main() -> int:
    args = parse_args()
    obs = [int(x.strip()) for x in args.obs.split(",") if x.strip()]
    primary = read_csv(SOURCE_PRIMARY)
    primary_vars = [row["variable"] for row in primary]
    primary_meta = {row["variable"]: row for row in primary}
    stable_rows = read_csv(SOURCE_4071)
    stable_core = {row["variable"] for row in stable_rows if str(row.get("metric_passes_gate", "")).lower() == "true"}

    cfg = r4002a.RunConfig(data_dir=args.data_dir, n_null=args.n_replicates, min_ob_gate=1)
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    write_config(obs, args.n_replicates, args.exclusion_sec)

    events = r4002a.read_events()
    events = events[events["ob"].isin(obs)].copy().reset_index(drop=True)
    if events.empty:
        raise RuntimeError(f"No events found for observations: {obs}")
    print(f"[4074] events: {len(events)} across observations {obs}", flush=True)

    frame_raw = r4002a.build_frame_metrics(events, cfg)
    frame = r4002a.add_residualized_metrics(frame_raw, cfg)
    arrays = r4002a.build_arrays(frame)
    features = r4002a.extract_event_features(arrays, events, cfg)
    features = features[features["variable"].isin(primary_vars)].copy()

    rng = np.random.default_rng(RNG_SEED)
    ob_rows: list[dict[str, object]] = []

    for ob in obs:
        events_ob = events[events["ob"] == ob].copy().reset_index(drop=True)
        if events_ob.empty:
            continue
        key = (int(ob), str(events_ob.iloc[0]["dataset"]))
        rec = arrays.get(key)
        if rec is None:
            continue
        real_ob = features[features["ob"] == ob].copy()
        null_dir: dict[str, list[float]] = {var: [] for var in primary_vars}
        null_act: dict[str, list[float]] = {var: [] for var in primary_vars}
        print(f"[4074] matched non-event replicates for Ob{ob}", flush=True)
        for rep in range(args.n_replicates):
            if rep in {0, 24, 49, 74, args.n_replicates - 1}:
                print(f"[4074] Ob{ob} non-event replicate {rep + 1}/{args.n_replicates}", flush=True)
            sampled = sample_non_event_times(events_ob, rec, rng, args.exclusion_sec, cfg.prepost_window_sec)
            sampled_features = r4002a.extract_event_features(arrays, sampled, cfg)
            sampled_features = sampled_features[sampled_features["variable"].isin(primary_vars)].copy()
            for var in primary_vars:
                null_dir[var].append(direction_summary(sampled_features, var)["direction_abs"])
                null_act[var].append(activity_summary(sampled_features, var))

        for var in primary_vars:
            meta = primary_meta[var]
            real_dir = direction_summary(real_ob, var)
            real_act = activity_summary(real_ob, var)
            nd = np.asarray(null_dir[var], dtype="float64")
            nd = nd[np.isfinite(nd)]
            na = np.asarray(null_act[var], dtype="float64")
            na = na[np.isfinite(na)]
            null_dir_med = float(np.median(nd)) if nd.size else math.nan
            null_act_med = float(np.median(na)) if na.size else math.nan
            real_dir_abs = real_dir["direction_abs"]
            dir_gap = real_dir_abs - null_dir_med if np.isfinite(real_dir_abs) and np.isfinite(null_dir_med) else math.nan
            act_gap = real_act - null_act_med if np.isfinite(real_act) and np.isfinite(null_act_med) else math.nan
            p_dir = float(np.mean(nd >= real_dir_abs)) if nd.size and np.isfinite(real_dir_abs) else math.nan
            p_act = float(np.mean(na >= real_act)) if na.size and np.isfinite(real_act) else math.nan
            ob_rows.append(
                {
                    "ob": ob,
                    "variable": var,
                    "taxonomy_class": meta.get("taxonomy_class", ""),
                    "family": meta.get("family", ""),
                    "is_4071_stable_core": var in stable_core,
                    "n_events": real_dir["n_events"],
                    "real_direction_abs_contrast_z": real_dir_abs,
                    "non_event_direction_abs_median_z": null_dir_med,
                    "direction_real_minus_non_event_z": dir_gap,
                    "p_non_event_direction_ge_real": p_dir,
                    "direction_gt_non_event": bool(np.isfinite(dir_gap) and dir_gap > 0),
                    "real_abs_activity_delta_z": real_act,
                    "non_event_abs_activity_median_z": null_act_med,
                    "activity_real_minus_non_event_z": act_gap,
                    "p_non_event_activity_ge_real": p_act,
                    "activity_gt_non_event": bool(np.isfinite(act_gap) and act_gap > 0),
                }
            )

    summary_rows = summarize(ob_rows, primary, stable_core)
    write_csv(OUT / "ob_level_event_conditioning.csv", ob_rows, OB_COLUMNS)
    write_csv(OUT / "event_conditioning_summary.csv", summary_rows, SUMMARY_COLUMNS)
    write_csv(OUT / "tables" / "ob_level_event_conditioning.csv", ob_rows, OB_COLUMNS)
    write_csv(OUT / "tables" / "event_conditioning_summary.csv", summary_rows, SUMMARY_COLUMNS)
    write_json(OUT / "ob_level_event_conditioning.json", ob_rows)
    write_json(OUT / "event_conditioning_summary.json", summary_rows)
    write_summary(summary_rows, ob_rows, obs, args.n_replicates, stable_core)
    print(f"Wrote 4074 event-conditioning audit outputs to {OUT.relative_to(ROOT)}", flush=True)
    return 0


def summarize(
    ob_rows: list[dict[str, object]],
    primary: list[dict[str, str]],
    stable_core: set[str],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for meta in primary:
        var = meta["variable"]
        d = [r for r in ob_rows if r["variable"] == var]
        direction_gaps = [float(r["direction_real_minus_non_event_z"]) for r in d]
        direction_ps = [float(r["p_non_event_direction_ge_real"]) for r in d]
        activity_gaps = [float(r["activity_real_minus_non_event_z"]) for r in d]
        activity_ps = [float(r["p_non_event_activity_ge_real"]) for r in d]
        direction_count = int(sum(bool(r["direction_gt_non_event"]) for r in d))
        activity_count = int(sum(bool(r["activity_gt_non_event"]) for r in d))
        med_dir_gap = finite_median(direction_gaps)
        med_act_gap = finite_median(activity_gaps)
        med_p_dir = finite_median(direction_ps)
        med_p_act = finite_median(activity_ps)
        direction_gate = len(d) >= 3 and direction_count >= 2 and np.isfinite(med_dir_gap) and med_dir_gap > 0.03 and np.isfinite(med_p_dir) and med_p_dir <= 0.35
        activity_gate = len(d) >= 3 and activity_count >= 2 and np.isfinite(med_act_gap) and med_act_gap > 0.03 and np.isfinite(med_p_act) and med_p_act <= 0.35
        rows.append(
            {
                "variable": var,
                "taxonomy_class": meta.get("taxonomy_class", ""),
                "family": meta.get("family", ""),
                "is_4071_stable_core": var in stable_core,
                "n_ob_valid": len(d),
                "direction_gt_non_event_count": direction_count,
                "median_direction_real_minus_non_event_z": med_dir_gap,
                "median_p_non_event_direction_ge_real": med_p_dir,
                "activity_gt_non_event_count": activity_count,
                "median_activity_real_minus_non_event_z": med_act_gap,
                "median_p_non_event_activity_ge_real": med_p_act,
                "metric_event_conditioned_gate": direction_gate,
                "metric_event_free_activity_gate": activity_gate,
            }
        )
    return rows


def write_summary(
    summary_rows: list[dict[str, object]],
    ob_rows: list[dict[str, object]],
    obs: list[int],
    n_replicates: int,
    stable_core: set[str],
) -> None:
    core_rows = [r for r in summary_rows if bool(r["is_4071_stable_core"])]
    event_conditioned_count = int(sum(bool(r["metric_event_conditioned_gate"]) for r in core_rows))
    activity_count = int(sum(bool(r["metric_event_free_activity_gate"]) for r in core_rows))
    core_total = len(core_rows)
    if core_total and event_conditioned_count >= 3:
        result = "pass_event_conditioned"
        interpretation = "Most stable-core metrics are stronger in real transition windows than matched non-event windows."
        next_node = "4080_local_affine_feasibility"
    elif core_total and event_conditioned_count >= 1:
        result = "boundary_mixed_event_conditioning"
        interpretation = "Some stable-core metrics are event-conditioned, but the evidence is mixed."
        next_node = "M0_review_before_4080"
    elif core_total and activity_count >= 2:
        result = "boundary_event_free_residual_activity"
        interpretation = "Residual activity appears in matched non-event windows too; the target may be a more general residual activity phenomenon rather than transition-specific organization."
        next_node = "M0_review_reframe_before_4080"
    else:
        result = "fail_event_conditioned_target"
        interpretation = "The stable core does not separate real transition windows from matched non-event windows under this audit."
        next_node = "M0_boundary_review"

    decision = {
        "node": NODE,
        "question": "Is the frozen residual organization specific to compact-density transition events, or also present in matched non-event windows?",
        "result": result,
        "stable_core_metrics": sorted(stable_core),
        "stable_core_event_conditioned_count": event_conditioned_count,
        "stable_core_activity_gate_count": activity_count,
        "n_stable_core_metrics": core_total,
        "gate": "pass if >=3 stable-core metrics pass event-conditioned direction gate; boundary if mixed or if activity is event-free/general",
        "observations": obs,
        "n_non_event_replicates": n_replicates,
        "interpretation": interpretation,
        "next": [next_node],
    }
    write_json(OUT / "decision.json", decision)

    passing = [r for r in summary_rows if bool(r["metric_event_conditioned_gate"])]
    activity = [r for r in summary_rows if bool(r["metric_event_free_activity_gate"])]
    text = f"""# Node 4074 Summary

## Question

Is the frozen residual organization specific to compact-density transition events, or does it also appear in matched non-event windows?

## Why this node exists

4071 showed that the frozen residual target has enough Ob1-Ob3 support under shifted-event nulls. 4074 checks whether this is genuinely transition-conditioned, or whether comparable residual reconfiguration appears in event-free matched windows.

## Data

Observations: `{", ".join("Ob" + str(x) for x in obs)}`

No full 19-observation run was performed. This node reuses the 4002A global-affine residual metric implementation and writes only to `Output/4074`.

## Frozen parameters

```text
primary metrics = Output/4072/primary_metrics.csv
stable decision core = 4071 passing metrics
baseline = B3_global_affine
control = N5_matched_non_event_window
n_non_event_replicates = {n_replicates}
```

## Baseline

`B3_global_affine`: translation plus global affine deformation subtraction.

## Null model

`N5_matched_non_event_window`: non-event windows matched within observation while preserving event-label counts for direction-contrast comparison.

## Primary metrics

{md_table(summary_rows, ["variable", "is_4071_stable_core", "direction_gt_non_event_count", "median_direction_real_minus_non_event_z", "median_p_non_event_direction_ge_real", "activity_gt_non_event_count", "median_activity_real_minus_non_event_z", "metric_event_conditioned_gate", "metric_event_free_activity_gate"])}

## Results

- Stable core metrics: {core_total}
- Stable-core event-conditioned direction gates: {event_conditioned_count}
- Stable-core event-free/general activity gates: {activity_count}
- Node decision: `{result}`

Event-conditioned metrics:

{md_table(passing, ["variable", "is_4071_stable_core", "median_direction_real_minus_non_event_z", "direction_gt_non_event_count"])}

Event-free/general activity metrics:

{md_table(activity, ["variable", "is_4071_stable_core", "median_activity_real_minus_non_event_z", "activity_gt_non_event_count"])}

## Dataset-wise replication

See `ob_level_event_conditioning.csv`.

## Gate evaluation

`{result}`

## What this rules out

If a stable-core metric fails the event-conditioned gate, it should not be used as a transition-specific target in 408x without a caveat.

## What this does NOT prove

4074 does not prove local non-affinity, stochasticity, propagation, or network mechanism. It only controls event selection using matched non-event windows.

## Decision

`{result}`

## Next node

`{next_node}`
"""
    (OUT / "4074_summary.md").write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--obs", default="1,2,3")
    parser.add_argument("--n-replicates", type=int, default=80)
    parser.add_argument("--exclusion-sec", type=float, default=0.80)
    parser.add_argument("--data-dir", default=r4002a.RunConfig.data_dir)
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
