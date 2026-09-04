"""4081c full-observation adjudication before 4082.

Ob1 and Ob2 disagreed in the local-affine geometry ladder. This node runs the
same frozen pilot over all available observations, one observation at a time,
and asks whether local non-affine survival is systematic or observation-
heterogeneous.

The script writes per-observation outputs under Output/4081c/ObX and an
aggregate summary under Output/4081c.
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
import run_4081_global_vs_local_geometry_ladder as r4081  # noqa: E402
from run_4001_geometric_baseline_residual_audit import (  # noqa: E402
    RunConfig as BaseRunConfig,
    resolve_data_dir,
)


OUT = ROOT / "Output" / "4081c"
NODE = "4081c_full_observation_adjudication_before_4082"
DATE = "2026-08-25"
RNG_SEED = 4081_0301


SUMMARY_COLUMNS = [
    "ob",
    "target_id",
    "role",
    "b3_metric",
    "local_metric",
    "k",
    "lag_sec",
    "n_events",
    "b3_event_direction_abs_z",
    "b3_non_event_direction_abs_median_z",
    "b3_event_minus_non_event_direction_z",
    "local_event_direction_abs_z",
    "local_non_event_direction_abs_median_z",
    "local_event_minus_non_event_direction_z",
    "p_non_event_direction_ge_event",
    "local_to_b3_direction_ratio",
    "event_conditioned_local_gate",
    "geometry_ladder_reading",
]


OB_CLASS_COLUMNS = [
    "ob",
    "n_events",
    "t1_gate_any",
    "t1_gate_k_values",
    "t1_median_local_to_b3_ratio",
    "t1_median_local_event_minus_non_event_z",
    "t2_gate_any",
    "t2_gate_count",
    "ob_route_a_class",
    "interpretation",
]


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


def direction_abs_from_features(features: pd.DataFrame, variable: str) -> tuple[int, float]:
    d = features[(features["variable"] == variable) & (features["event_type"].isin(["low_to_high", "high_to_low"]))].copy()
    if d.empty:
        return 0, math.nan
    by_type = d.groupby("event_type")["signed_delta_post_minus_pre_z"].median()
    if "low_to_high" not in by_type or "high_to_low" not in by_type:
        return int(d["event_id"].nunique()), math.nan
    return int(d["event_id"].nunique()), abs(float(by_type["low_to_high"] - by_type["high_to_low"]))


def compute_b3_refs(
    ob: int,
    events_ob: pd.DataFrame,
    cfg: r4002a.RunConfig,
    n_replicates: int,
    prepost_sec: float,
    exclusion_sec: float,
) -> tuple[dict[str, dict[str, float]], pd.DataFrame]:
    frame_raw = r4002a.build_frame_metrics(events_ob, cfg)
    frame = r4002a.add_residualized_metrics(frame_raw, cfg)
    arrays = r4002a.build_arrays(frame)
    features = r4002a.extract_event_features(arrays, events_ob, cfg)
    rec = next(iter(arrays.values()))
    rng = np.random.default_rng(RNG_SEED + ob)
    refs: dict[str, dict[str, float]] = {}
    b3_vars = sorted({target["b3_metric"] for target in r4081.TARGET_MAP.values()})
    null_by_var = {var: [] for var in b3_vars}
    for rep in range(n_replicates):
        sampled = r4081.sample_non_event_times(events_ob, rec["t"], rng, prepost_sec, exclusion_sec)
        nf = r4002a.extract_event_features(arrays, sampled, cfg)
        for var in b3_vars:
            _, da = direction_abs_from_features(nf, var)
            null_by_var[var].append(da)
    for var in b3_vars:
        n_events, event_abs = direction_abs_from_features(features, var)
        null = np.asarray(null_by_var[var], dtype="float64")
        null = null[np.isfinite(null)]
        null_med = float(np.median(null)) if null.size else math.nan
        refs[var] = {
            "n_events": n_events,
            "event_abs": event_abs,
            "non_event_abs_median": null_med,
            "event_minus_non_event": event_abs - null_med if np.isfinite(event_abs) and np.isfinite(null_med) else math.nan,
        }
    return refs, frame


def run_ob(
    ob: int,
    data_dir: Path,
    events_all: pd.DataFrame,
    k_values: list[int],
    lag: float,
    frame_stride: int,
    max_focals_per_frame: int,
    n_replicates: int,
    prepost_sec: float,
    exclusion_sec: float,
    force: bool,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    ob_dir = OUT / f"Ob{ob}"
    summary_path = ob_dir / "geometry_ladder_pilot_summary.csv"
    decision_path = ob_dir / "decision.json"
    if summary_path.exists() and decision_path.exists() and not force:
        with summary_path.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        decision = json.loads(decision_path.read_text(encoding="utf-8"))
        return rows, decision

    ob_dir.mkdir(parents=True, exist_ok=True)
    (ob_dir / "tables").mkdir(parents=True, exist_ok=True)
    events_ob = events_all[events_all["ob"] == ob].copy().reset_index(drop=True)
    if events_ob.empty:
        raise RuntimeError(f"No events for Ob{ob}")
    dataset = str(events_ob.iloc[0]["dataset"])
    cfg = r4002a.RunConfig(data_dir=str(data_dir), n_null=n_replicates, min_ob_gate=1)

    print(f"[4081c] Ob{ob}: computing B3 references", flush=True)
    b3_refs, _ = compute_b3_refs(ob, events_ob, cfg, n_replicates, prepost_sec, exclusion_sec)

    rows: list[dict[str, object]] = []
    rng = np.random.default_rng(RNG_SEED + 1000 + ob)
    for k in k_values:
        print(f"[4081c] Ob{ob}: computing local B4 metrics k={k}", flush=True)
        frame = r4081.build_local_metric_frame(ob, dataset, data_dir, k, lag, frame_stride, max_focals_per_frame)
        arrays = r4081.build_arrays(frame)
        features = r4081.extract_features(arrays, events_ob, r4081.LOCAL_VARIABLES, prepost_sec)
        rec = next(iter(arrays.values()))
        null_by_var = {var: [] for var in r4081.LOCAL_VARIABLES}
        for rep in range(n_replicates):
            sampled = r4081.sample_non_event_times(events_ob, rec["t"], rng, prepost_sec, exclusion_sec)
            nf = r4081.extract_features(arrays, sampled, r4081.LOCAL_VARIABLES, prepost_sec)
            for var in r4081.LOCAL_VARIABLES:
                _, da = r4081.direction_abs(nf, var)
                null_by_var[var].append(da)
        for target_id, target in r4081.TARGET_MAP.items():
            local_var = target["local_metric"]
            b3_metric = target["b3_metric"]
            n_events, local_abs = r4081.direction_abs(features, local_var)
            null = np.asarray(null_by_var[local_var], dtype="float64")
            null = null[np.isfinite(null)]
            null_med = float(np.median(null)) if null.size else math.nan
            p_ge = float(np.mean(null >= local_abs)) if null.size and np.isfinite(local_abs) else math.nan
            local_gap = local_abs - null_med if np.isfinite(local_abs) and np.isfinite(null_med) else math.nan
            b3 = b3_refs.get(b3_metric, {})
            b3_event = b3.get("event_abs", math.nan)
            ratio = local_abs / b3_event if np.isfinite(local_abs) and np.isfinite(b3_event) and b3_event > 1e-12 else math.nan
            gate = bool(np.isfinite(local_gap) and local_gap > 0.03 and np.isfinite(p_ge) and p_ge <= 0.35 and np.isfinite(ratio) and ratio >= 0.30)
            if gate:
                reading = "local_nonaffine_signal_survives_pilot"
            elif np.isfinite(ratio) and ratio < 0.30:
                reading = "local_affine_largely_absorbs_b3_signal"
            elif np.isfinite(local_gap) and local_gap <= 0:
                reading = "local_nonaffine_not_event_conditioned"
            else:
                reading = "inconclusive"
            rows.append(
                {
                    "ob": ob,
                    "target_id": target_id,
                    "role": target["role"],
                    "b3_metric": b3_metric,
                    "local_metric": local_var,
                    "k": k,
                    "lag_sec": lag,
                    "n_events": n_events,
                    "b3_event_direction_abs_z": b3_event,
                    "b3_non_event_direction_abs_median_z": b3.get("non_event_abs_median", math.nan),
                    "b3_event_minus_non_event_direction_z": b3.get("event_minus_non_event", math.nan),
                    "local_event_direction_abs_z": local_abs,
                    "local_non_event_direction_abs_median_z": null_med,
                    "local_event_minus_non_event_direction_z": local_gap,
                    "p_non_event_direction_ge_event": p_ge,
                    "local_to_b3_direction_ratio": ratio,
                    "event_conditioned_local_gate": gate,
                    "geometry_ladder_reading": reading,
                }
            )

    ob_class = classify_ob(ob, rows)
    decision = {
        "node": NODE,
        "ob": ob,
        "result": ob_class["ob_route_a_class"],
        "classification": ob_class,
        "next": ["aggregate_4081c"],
    }
    write_csv(summary_path, rows, SUMMARY_COLUMNS)
    write_csv(ob_dir / "tables" / "geometry_ladder_pilot_summary.csv", rows, SUMMARY_COLUMNS)
    write_json(ob_dir / "geometry_ladder_pilot_summary.json", rows)
    write_json(decision_path, decision)
    (ob_dir / "4081c_ob_summary.md").write_text(ob_summary_md(ob, rows, ob_class), encoding="utf-8")
    return rows, decision


def classify_ob(ob: int, rows: list[dict[str, object]]) -> dict[str, object]:
    t1 = [r for r in rows if r["target_id"] == "T1_transition_tangential_residual"]
    t2 = [r for r in rows if str(r["target_id"]).startswith("T2_")]
    t1_gates = [int(r["k"]) for r in t1 if bool(r["event_conditioned_local_gate"])]
    t2_gate_count = int(sum(bool(r["event_conditioned_local_gate"]) for r in t2))
    t1_ratios = [float(r["local_to_b3_direction_ratio"]) for r in t1]
    t1_gaps = [float(r["local_event_minus_non_event_direction_z"]) for r in t1]
    n_events = int(max([int(r["n_events"]) for r in rows], default=0))
    if len(t1_gates) >= 2:
        cls = "t1_local_nonaffine_survives_both_k"
        interp = "T1 survives local-affine residualization for both k values."
    elif len(t1_gates) == 1:
        cls = "t1_local_nonaffine_survives_one_k"
        interp = "T1 survives local-affine residualization for one k value only."
    elif finite_median(t1_ratios) < 0.30:
        cls = "t1_absorbed_by_local_affine"
        interp = "T1 local signal is small relative to B3 after local-affine residualization."
    elif finite_median(t1_gaps) <= 0:
        cls = "t1_not_event_conditioned_after_local_affine"
        interp = "T1 local signal is not stronger than matched non-event windows."
    else:
        cls = "t1_inconclusive"
        interp = "T1 local-affine result is inconclusive."
    return {
        "ob": ob,
        "n_events": n_events,
        "t1_gate_any": bool(t1_gates),
        "t1_gate_k_values": ",".join(str(x) for x in t1_gates),
        "t1_median_local_to_b3_ratio": finite_median(t1_ratios),
        "t1_median_local_event_minus_non_event_z": finite_median(t1_gaps),
        "t2_gate_any": t2_gate_count > 0,
        "t2_gate_count": t2_gate_count,
        "ob_route_a_class": cls,
        "interpretation": interp,
    }


def ob_summary_md(ob: int, rows: list[dict[str, object]], ob_class: dict[str, object]) -> str:
    return f"""# 4081c Ob{ob} Summary

## Classification

`{ob_class["ob_route_a_class"]}`

## Interpretation

{ob_class["interpretation"]}

## Target Rows

{md_table(rows, ["target_id", "k", "b3_event_direction_abs_z", "local_event_direction_abs_z", "local_non_event_direction_abs_median_z", "local_event_minus_non_event_direction_z", "local_to_b3_direction_ratio", "event_conditioned_local_gate", "geometry_ladder_reading"])}
"""


def aggregate(existing_rows: list[dict[str, object]], existing_classes: list[dict[str, object]], args: argparse.Namespace) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    write_csv(OUT / "full_geometry_ladder_rows.csv", existing_rows, SUMMARY_COLUMNS)
    write_csv(OUT / "tables" / "full_geometry_ladder_rows.csv", existing_rows, SUMMARY_COLUMNS)
    write_csv(OUT / "ob_route_a_classification.csv", existing_classes, OB_CLASS_COLUMNS)
    write_csv(OUT / "tables" / "ob_route_a_classification.csv", existing_classes, OB_CLASS_COLUMNS)
    write_json(OUT / "full_geometry_ladder_rows.json", existing_rows)
    write_json(OUT / "ob_route_a_classification.json", existing_classes)

    class_counts: dict[str, int] = {}
    for row in existing_classes:
        cls = str(row["ob_route_a_class"])
        class_counts[cls] = class_counts.get(cls, 0) + 1
    t1_survive = [r for r in existing_classes if str(r["ob_route_a_class"]).startswith("t1_local_nonaffine_survives")]
    t1_absorb = [r for r in existing_classes if r["ob_route_a_class"] == "t1_absorbed_by_local_affine"]
    t1_not_event = [r for r in existing_classes if r["ob_route_a_class"] == "t1_not_event_conditioned_after_local_affine"]
    total = len(existing_classes)
    if total == 19 and len(t1_survive) >= 10:
        result = "support_observation_heterogeneous_but_common_t1_survival"
        next_node = "4082_scale_robustness_on_surviving_observation_class"
    elif total == 19 and len(t1_survive) <= 4:
        result = "mostly_geometry_closure_or_no_local_event_conditioning"
        next_node = "route_a_bounded_geometry_closure_synthesis"
    else:
        result = "observation_heterogeneity_map"
        next_node = "4081d_explain_observation_heterogeneity_before_4082"

    decision = {
        "node": NODE,
        "result": result,
        "n_observations": total,
        "class_counts": class_counts,
        "t1_survival_observations": [r["ob"] for r in t1_survive],
        "t1_absorbed_observations": [r["ob"] for r in t1_absorb],
        "t1_not_event_conditioned_observations": [r["ob"] for r in t1_not_event],
        "parameters": {
            "k": args.k,
            "lag": args.lag,
            "n_replicates": args.n_replicates,
            "frame_stride": args.frame_stride,
        },
        "interpretation": "Full-observation adjudication of Route A local-affine survival/absorption.",
        "next": [next_node],
    }
    write_json(OUT / "decision.json", decision)

    sorted_classes = sorted(existing_classes, key=lambda r: int(r["ob"]))
    summary = f"""# Node 4081c Summary

## Question

Across all observations, does the T1 transition tangential residual survive
local-affine residualization, get absorbed by local affine geometry, or vary by
observation?

## Run

```text
obs = {args.obs}
k = {args.k}
lag = {args.lag}
n_replicates = {args.n_replicates}
```

## Decision

`{result}`

## Class Counts

```json
{json.dumps(class_counts, ensure_ascii=False, indent=2)}
```

## Observation Classification

{md_table(sorted_classes, ["ob", "n_events", "ob_route_a_class", "t1_gate_k_values", "t1_median_local_to_b3_ratio", "t1_median_local_event_minus_non_event_z", "t2_gate_count"])}

## Interpretation

This node is the full-observation adjudication requested after Ob1 and Ob2
disagreed. It should not be reduced to a pooled significance claim. The
important output is the observation-level classification pattern.

## Next

`{next_node}`
"""
    (OUT / "4081c_summary.md").write_text(summary, encoding="utf-8")


def parse_obs(arg: str, events: pd.DataFrame) -> list[int]:
    if arg.lower() in {"all", "1-19"}:
        return sorted(int(x) for x in events["ob"].dropna().unique())
    if "-" in arg and "," not in arg:
        a, b = arg.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in arg.split(",") if x.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--obs", default="all")
    parser.add_argument("--data-dir", default=BaseRunConfig.data_dir)
    parser.add_argument("--k", default="8,10")
    parser.add_argument("--lag", type=float, default=0.10)
    parser.add_argument("--frame-stride", type=int, default=2)
    parser.add_argument("--max-focals-per-frame", type=int, default=24)
    parser.add_argument("--n-replicates", type=int, default=40)
    parser.add_argument("--prepost-sec", type=float, default=0.20)
    parser.add_argument("--exclusion-sec", type=float, default=0.80)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--aggregate-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data_dir = resolve_data_dir(BaseRunConfig(data_dir=args.data_dir))
    events = r4002a.read_events()
    obs = parse_obs(args.obs, events)
    k_values = [int(x.strip()) for x in args.k.split(",") if x.strip()]
    OUT.mkdir(parents=True, exist_ok=True)

    all_rows: list[dict[str, object]] = []
    all_classes: list[dict[str, object]] = []
    if not args.aggregate_only:
        for ob in obs:
            print(f"[4081c] starting Ob{ob}", flush=True)
            rows, decision = run_ob(
                ob=ob,
                data_dir=data_dir,
                events_all=events,
                k_values=k_values,
                lag=args.lag,
                frame_stride=args.frame_stride,
                max_focals_per_frame=args.max_focals_per_frame,
                n_replicates=args.n_replicates,
                prepost_sec=args.prepost_sec,
                exclusion_sec=args.exclusion_sec,
                force=args.force,
            )
            all_rows.extend(rows)
            all_classes.append(decision["classification"])

    # Aggregate all existing requested observations. This supports resume.
    aggregate_rows: list[dict[str, object]] = []
    aggregate_classes: list[dict[str, object]] = []
    for ob in obs:
        ob_dir = OUT / f"Ob{ob}"
        summary_path = ob_dir / "geometry_ladder_pilot_summary.csv"
        decision_path = ob_dir / "decision.json"
        if not (summary_path.exists() and decision_path.exists()):
            continue
        with summary_path.open(newline="", encoding="utf-8") as f:
            aggregate_rows.extend(list(csv.DictReader(f)))
        aggregate_classes.append(json.loads(decision_path.read_text(encoding="utf-8"))["classification"])
    aggregate(aggregate_rows, aggregate_classes, args)
    print(f"Wrote 4081c outputs to {OUT.relative_to(ROOT)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
