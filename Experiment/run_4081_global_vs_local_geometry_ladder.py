"""4081 global-vs-local geometry ladder pilot.

This pilot tests whether local affine deformation absorbs the 4075 split
targets or whether a local non-affine residual remains. It runs on Ob1 first.

It is deliberately cautious:
- T1 transition tangential residual is the primary event-conditioned target.
- T2 residual speed/covariance activity is treated as secondary general activity.
- The node compares local non-affine metrics against matched non-event windows.
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
from run_4001_geometric_baseline_residual_audit import (  # noqa: E402
    RunConfig as BaseRunConfig,
    median_dt,
    read_events,
    read_raw_ob,
    resolve_data_dir,
)


OUT = ROOT / "Output" / "4081"
SRC_4071_OB = ROOT / "Output" / "4071" / "ob_level_effects.csv"
SRC_4074_OB = ROOT / "Output" / "4074" / "ob_level_event_conditioning.csv"
SRC_4075 = ROOT / "Output" / "4075" / "target_config_for_4080.json"

NODE = "4081_global_vs_local_geometry_ladder"
DATE = "2026-08-25"
RNG_SEED = 408101


LOCAL_VARIABLES = [
    "local_tangential_speed_mean",
    "local_edge_minus_core_tangential",
    "local_speed_rms",
    "local_velocity_cov_trace",
]


TARGET_MAP = {
    "T1_transition_tangential_residual": {
        "b3_metric": "resid_tangential_speed_mean",
        "local_metric": "local_tangential_speed_mean",
        "role": "primary_transition_target",
    },
    "T1_support_edge_core_tangential": {
        "b3_metric": "edge_minus_core_resid_tangential",
        "local_metric": "local_edge_minus_core_tangential",
        "role": "supporting_transition_spatial_metric",
    },
    "T2_general_speed_rms": {
        "b3_metric": "resid_speed_rms",
        "local_metric": "local_speed_rms",
        "role": "secondary_general_activity",
    },
    "T2_general_cov_trace": {
        "b3_metric": "resid_velocity_cov_trace",
        "local_metric": "local_velocity_cov_trace",
        "role": "secondary_general_activity",
    },
}


SUMMARY_COLUMNS = [
    "target_id",
    "role",
    "b3_metric",
    "local_metric",
    "k",
    "lag_sec",
    "b3_event_direction_abs_z",
    "b3_event_minus_non_event_direction_z",
    "local_event_direction_abs_z",
    "local_non_event_direction_abs_median_z",
    "local_event_minus_non_event_direction_z",
    "p_non_event_direction_ge_event",
    "local_to_b3_direction_ratio",
    "event_conditioned_local_gate",
    "geometry_ladder_reading",
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
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


def load_b3_refs(ob: int) -> dict[str, dict[str, float]]:
    b3_event = read_csv(SRC_4071_OB)
    b3_non = read_csv(SRC_4074_OB)
    refs: dict[str, dict[str, float]] = {}
    for row in b3_event:
        if int(float(row["ob"])) != ob:
            continue
        refs.setdefault(row["variable"], {})["event_abs"] = float(row["real_abs_direction_contrast_z"])
    for row in b3_non:
        if int(float(row["ob"])) != ob:
            continue
        refs.setdefault(row["variable"], {})["event_minus_non_event"] = float(row["direction_real_minus_non_event_z"])
    return refs


def load_ob_df(ob: int, data_dir: Path, dataset: str) -> pd.DataFrame:
    path = data_dir / dataset
    if not path.exists():
        path = data_dir / f"Ob{ob}.txt"
    return read_raw_ob(path)


def frame_arrays(frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    return frame["id"].to_numpy(dtype="int64"), frame[["x", "y", "z"]].to_numpy(dtype="float64")


def local_frame_metrics(
    ids0: np.ndarray,
    pos0: np.ndarray,
    ids1: np.ndarray,
    pos1: np.ndarray,
    k: int,
    lag_dt: float,
    rng: np.random.Generator,
    max_focals: int,
) -> dict[str, float]:
    id_to_idx0 = {int(v): i for i, v in enumerate(ids0)}
    id_to_idx1 = {int(v): i for i, v in enumerate(ids1)}
    common = np.asarray([v for v in ids0 if int(v) in id_to_idx1], dtype="int64")
    if common.size == 0:
        return {var: math.nan for var in LOCAL_VARIABLES}
    if common.size > max_focals:
        focals = rng.choice(common, size=max_focals, replace=False)
    else:
        focals = common

    center = np.nanmean(pos0, axis=0)
    radii = np.linalg.norm(pos0 - center, axis=1)
    q33 = float(np.nanquantile(radii, 1 / 3)) if np.isfinite(radii).any() else math.nan
    q67 = float(np.nanquantile(radii, 2 / 3)) if np.isfinite(radii).any() else math.nan

    residual_vels: list[np.ndarray] = []
    tangential: list[float] = []
    edge_tangential: list[float] = []
    core_tangential: list[float] = []

    for focal_id in focals:
        focal_id = int(focal_id)
        i0 = id_to_idx0[focal_id]
        i1 = id_to_idx1[focal_id]
        rel_all = pos0 - pos0[i0]
        dist = np.linalg.norm(rel_all, axis=1)
        order = np.argsort(dist)
        neigh_ids = [int(ids0[j]) for j in order if int(ids0[j]) != focal_id and int(ids0[j]) in id_to_idx1][:k]
        if len(neigh_ids) < 4:
            continue
        A = []
        B = []
        for nid in neigh_ids:
            j0 = id_to_idx0[nid]
            j1 = id_to_idx1[nid]
            r0 = pos0[j0] - pos0[i0]
            r1 = pos1[j1] - pos1[i1]
            A.append(r0)
            B.append(r1 - r0)
        A = np.asarray(A, dtype="float64")
        B = np.asarray(B, dtype="float64")
        if not (np.isfinite(A).all() and np.isfinite(B).all()):
            continue
        try:
            _, s, _ = np.linalg.svd(A, full_matrices=False)
            if s.size < 3 or s[-1] <= 1e-12:
                continue
            J, _, _, _ = np.linalg.lstsq(A, B, rcond=None)
        except np.linalg.LinAlgError:
            continue
        resid = (B - A @ J) / lag_dt
        residual_vels.extend([resid[i] for i in range(resid.shape[0]) if np.isfinite(resid[i]).all()])

        focal_rel = pos0[i0] - center
        focal_radius = float(np.linalg.norm(focal_rel))
        radial_unit = focal_rel / focal_radius if focal_radius > 1e-12 else None
        if radial_unit is None:
            continue
        radial_component = resid @ radial_unit
        tang_sq = np.maximum(np.sum(resid * resid, axis=1) - radial_component * radial_component, 0.0)
        focal_tangential = float(np.nanmean(np.sqrt(tang_sq))) if tang_sq.size else math.nan
        if np.isfinite(focal_tangential):
            tangential.append(focal_tangential)
            if np.isfinite(q67) and focal_radius >= q67:
                edge_tangential.append(focal_tangential)
            if np.isfinite(q33) and focal_radius <= q33:
                core_tangential.append(focal_tangential)

    if residual_vels:
        V = np.vstack(residual_vels)
        speed_sq = np.sum(V * V, axis=1)
        speed_rms = math.sqrt(float(np.nanmean(speed_sq))) if np.isfinite(speed_sq).any() else math.nan
        mean_v = np.nanmean(V, axis=0)
        cov_trace = float(np.nanmean(speed_sq) - np.dot(mean_v, mean_v)) if np.isfinite(speed_sq).any() else math.nan
    else:
        speed_rms = cov_trace = math.nan
    edge_mean = finite_median(edge_tangential)
    core_mean = finite_median(core_tangential)
    return {
        "local_tangential_speed_mean": finite_median(tangential),
        "local_edge_minus_core_tangential": edge_mean - core_mean if np.isfinite(edge_mean) and np.isfinite(core_mean) else math.nan,
        "local_speed_rms": speed_rms,
        "local_velocity_cov_trace": cov_trace,
    }


def build_local_metric_frame(
    ob: int,
    dataset: str,
    data_dir: Path,
    k: int,
    lag_sec: float,
    frame_stride: int,
    max_focals: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(RNG_SEED + k)
    df = load_ob_df(ob, data_dir, dataset)
    times = np.asarray(sorted(df["t"].unique()), dtype="float64")
    frames = {float(t): d.sort_values("id").copy() for t, d in df.groupby("t", sort=True)}
    dt = median_dt(times)
    lag_steps = max(1, int(round(lag_sec / dt)))
    rows = []
    idxs = np.arange(0, len(times) - lag_steps, frame_stride, dtype=int)
    for nn, idx in enumerate(idxs):
        if nn % 500 == 0:
            print(f"[4081] k={k} local metric frame {nn + 1}/{len(idxs)}", flush=True)
        t0 = float(times[idx])
        t1 = float(times[idx + lag_steps])
        ids0, pos0 = frame_arrays(frames[t0])
        ids1, pos1 = frame_arrays(frames[t1])
        metrics = local_frame_metrics(ids0, pos0, ids1, pos1, k, lag_steps * dt, rng, max_focals)
        row = {"ob": ob, "dataset": dataset, "t": t0, "k": k, "lag_sec": lag_sec, "lag_steps": lag_steps}
        row.update(metrics)
        rows.append(row)
    out = pd.DataFrame(rows)
    return add_residualized_metrics(out)


def add_residualized_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    d = frame.sort_values("t").reset_index(drop=True).copy()
    dt = median_dt(d["t"].to_numpy(dtype="float64"))
    win = max(5, int(round(1.0 / dt))) if np.isfinite(dt) and dt > 0 else 101
    if win % 2 == 0:
        win += 1
    min_periods = max(3, win // 5)
    for var in LOCAL_VARIABLES:
        z = r4002a.robust_z_safe(d[var])
        smooth = (
            pd.Series(z)
            .rolling(win, center=True, min_periods=min_periods)
            .mean()
            .interpolate(limit_direction="both")
            .to_numpy(dtype="float64")
        )
        d[f"{var}__resid4081"] = r4002a.robust_z_safe(z - smooth)
    return d


def build_arrays(frame: pd.DataFrame) -> dict[tuple[int, str], dict[str, np.ndarray]]:
    rec: dict[str, np.ndarray] = {"t": frame["t"].to_numpy(dtype="float64")}
    for var in LOCAL_VARIABLES:
        rec[var] = frame[f"{var}__resid4081"].to_numpy(dtype="float64")
    first = frame.iloc[0]
    return {(int(first["ob"]), str(first["dataset"])): rec}


def extract_features(arrays: dict[tuple[int, str], dict[str, np.ndarray]], events: pd.DataFrame, variables: list[str], prepost_sec: float) -> pd.DataFrame:
    rows = []
    for event in events.itertuples(index=False):
        rec = arrays.get((int(event.ob), str(event.dataset)))
        if rec is None:
            continue
        t = rec["t"]
        event_t = float(event.event_t)
        p0 = int(np.searchsorted(t, event_t - prepost_sec, side="left"))
        p1 = int(np.searchsorted(t, event_t, side="left"))
        q0 = int(np.searchsorted(t, event_t, side="left"))
        q1 = int(np.searchsorted(t, event_t + prepost_sec, side="right"))
        if p1 <= p0 or q1 <= q0:
            continue
        for var in variables:
            x = rec[var]
            pre = x[p0:p1]
            post = x[q0:q1]
            if not np.isfinite(pre).any() or not np.isfinite(post).any():
                continue
            pre_mean = float(np.nanmean(pre))
            post_mean = float(np.nanmean(post))
            rows.append(
                {
                    "event_id": int(event.event_id),
                    "ob": int(event.ob),
                    "dataset": str(event.dataset),
                    "event_t": event_t,
                    "event_type": str(event.event_type),
                    "variable": var,
                    "pre_mean_resid_z": pre_mean,
                    "post_mean_resid_z": post_mean,
                    "signed_delta_post_minus_pre_z": post_mean - pre_mean,
                }
            )
    return pd.DataFrame(rows)


def direction_abs(features: pd.DataFrame, variable: str) -> tuple[int, float]:
    d = features[(features["variable"] == variable) & (features["event_type"].isin(["low_to_high", "high_to_low"]))].copy()
    if d.empty:
        return 0, math.nan
    by_type = d.groupby("event_type")["signed_delta_post_minus_pre_z"].median()
    if "low_to_high" not in by_type or "high_to_low" not in by_type:
        return int(d["event_id"].nunique()), math.nan
    return int(d["event_id"].nunique()), abs(float(by_type["low_to_high"] - by_type["high_to_low"]))


def sample_non_event_times(events_ob: pd.DataFrame, t: np.ndarray, rng: np.random.Generator, prepost_sec: float, exclusion_sec: float) -> pd.DataFrame:
    t_min = float(np.nanmin(t)) + prepost_sec
    t_max = float(np.nanmax(t)) - prepost_sec
    real_times = pd.to_numeric(events_ob["event_t"], errors="coerce").to_numpy(dtype="float64")
    rows = []
    for event in events_ob.itertuples(index=False):
        sampled = math.nan
        for _ in range(1000):
            cand = float(rng.uniform(t_min, t_max))
            if real_times.size == 0 or float(np.min(np.abs(real_times - cand))) >= exclusion_sec:
                sampled = cand
                break
        if not np.isfinite(sampled):
            sampled = float(rng.uniform(t_min, t_max))
        rows.append({"event_id": int(event.event_id), "ob": int(event.ob), "dataset": str(event.dataset), "event_t": sampled, "event_type": str(event.event_type)})
    return pd.DataFrame(rows)


def write_config(args: argparse.Namespace) -> None:
    text = dedent(
        f"""\
        node: {NODE}
        date: {DATE}
        node_type: geometry_ladder_pilot
        source_target_config: Output/4075/target_config_for_4080.json
        observation: Ob{args.ob}
        k_values: {args.k}
        lag_sec: {args.lag}
        frame_stride: {args.frame_stride}
        max_focals_per_frame: {args.max_focals_per_frame}
        n_non_event_replicates: {args.n_replicates}
        """
    )
    (OUT / "config.yaml").write_text(text, encoding="utf-8")


def main() -> int:
    global NODE, OUT
    args = parse_args()
    NODE = args.node_id
    if args.output_dir:
        OUT = ROOT / args.output_dir
    target_config = read_json(SRC_4075)
    data_dir = resolve_data_dir(BaseRunConfig(data_dir=args.data_dir))
    events = read_events()
    events = events[events["ob"] == args.ob].copy().reset_index(drop=True)
    if events.empty:
        raise RuntimeError(f"No events found for Ob{args.ob}")
    dataset = str(events.iloc[0]["dataset"])
    k_values = [int(x.strip()) for x in args.k.split(",") if x.strip()]
    b3_refs = load_b3_refs(args.ob)

    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    write_config(args)

    all_rows: list[dict[str, object]] = []
    frames_written = []
    rng = np.random.default_rng(RNG_SEED)
    for k in k_values:
        frame = build_local_metric_frame(args.ob, dataset, data_dir, k, args.lag, args.frame_stride, args.max_focals_per_frame)
        frames_written.append(frame)
        arrays = build_arrays(frame)
        features = extract_features(arrays, events, LOCAL_VARIABLES, args.prepost_sec)
        rec = next(iter(arrays.values()))
        null_by_var = {var: [] for var in LOCAL_VARIABLES}
        for rep in range(args.n_replicates):
            if rep in {0, 24, args.n_replicates - 1}:
                print(f"[4081] k={k} non-event replicate {rep + 1}/{args.n_replicates}", flush=True)
            sampled = sample_non_event_times(events, rec["t"], rng, args.prepost_sec, args.exclusion_sec)
            nf = extract_features(arrays, sampled, LOCAL_VARIABLES, args.prepost_sec)
            for var in LOCAL_VARIABLES:
                _, da = direction_abs(nf, var)
                null_by_var[var].append(da)
        for target_id, target in TARGET_MAP.items():
            local_var = target["local_metric"]
            b3_metric = target["b3_metric"]
            n_events, local_abs = direction_abs(features, local_var)
            null = np.asarray(null_by_var[local_var], dtype="float64")
            null = null[np.isfinite(null)]
            null_med = float(np.median(null)) if null.size else math.nan
            p_ge = float(np.mean(null >= local_abs)) if null.size and np.isfinite(local_abs) else math.nan
            local_gap = local_abs - null_med if np.isfinite(local_abs) and np.isfinite(null_med) else math.nan
            b3_event = b3_refs.get(b3_metric, {}).get("event_abs", math.nan)
            b3_event_non = b3_refs.get(b3_metric, {}).get("event_minus_non_event", math.nan)
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
            all_rows.append(
                {
                    "target_id": target_id,
                    "role": target["role"],
                    "b3_metric": b3_metric,
                    "local_metric": local_var,
                    "k": k,
                    "lag_sec": args.lag,
                    "b3_event_direction_abs_z": b3_event,
                    "b3_event_minus_non_event_direction_z": b3_event_non,
                    "local_event_direction_abs_z": local_abs,
                    "local_non_event_direction_abs_median_z": null_med,
                    "local_event_minus_non_event_direction_z": local_gap,
                    "p_non_event_direction_ge_event": p_ge,
                    "local_to_b3_direction_ratio": ratio,
                    "event_conditioned_local_gate": gate,
                    "geometry_ladder_reading": reading,
                }
            )

    frame_all = pd.concat(frames_written, ignore_index=True)
    frame_all.to_csv(OUT / "local_nonaffine_frame_metrics.csv", index=False)
    write_csv(OUT / "geometry_ladder_pilot_summary.csv", all_rows, SUMMARY_COLUMNS)
    write_csv(OUT / "tables" / "geometry_ladder_pilot_summary.csv", all_rows, SUMMARY_COLUMNS)
    write_json(OUT / "geometry_ladder_pilot_summary.json", all_rows)
    write_summary(all_rows, target_config)
    print(f"Wrote 4081 geometry ladder pilot outputs to {OUT.relative_to(ROOT)}")
    return 0


def write_summary(rows: list[dict[str, object]], target_config: dict) -> None:
    t1_rows = [r for r in rows if r["target_id"] == "T1_transition_tangential_residual"]
    t2_rows = [r for r in rows if str(r["target_id"]).startswith("T2_")]
    t1_pass = any(bool(r["event_conditioned_local_gate"]) for r in t1_rows)
    t2_pass = any(bool(r["event_conditioned_local_gate"]) for r in t2_rows)
    if t1_pass:
        result = "support_local_nonaffine_tangential_pilot"
        next_node = "4082_scale_robustness_of_nonaffinity"
        interpretation = "The primary tangential transition target survives local-affine residualization in this observation pilot."
    else:
        result = "boundary_t1_absorbed_or_not_event_conditioned"
        next_node = "4081b_confirm_t1_absorption_or_pause_route_a"
        interpretation = "The primary tangential target does not clearly survive local-affine residualization in this observation pilot."

    decision = {
        "node": NODE,
        "question": "Does local affine deformation explain the global-affine residual targets, or does local non-affine signal survive?",
        "result": result,
        "t1_local_gate_any": t1_pass,
        "t2_local_gate_any": t2_pass,
        "interpretation": interpretation,
        "next": [next_node],
        "target_policy": target_config.get("target_policy"),
    }
    write_json(OUT / "decision.json", decision)
    text = f"""# Node {NODE} Summary

## Question

Does local affine deformation explain the global-affine residual targets, or does a local non-affine residual survive for T1/T2 separately?

## Why this node exists

4080 showed local affine fits are numerically feasible. 4081 is the first
geometry-ladder pilot after the 4075 target split.

## Frozen Target Policy

```text
T1 primary = transition tangential residual
T2 secondary = general residual activity
retired primary = radial residual, core-edge speed
```

## Baseline

`B3_global_affine` reference values come from 4071/4074 observation-level tables.

`B4_local_affine` local non-affine metrics are computed with the pilot settings.

## Null / Control

Matched non-event windows are used for the local metrics.

## Results

{md_table(rows, ["target_id", "role", "k", "b3_event_direction_abs_z", "local_event_direction_abs_z", "local_non_event_direction_abs_median_z", "local_event_minus_non_event_direction_z", "local_to_b3_direction_ratio", "event_conditioned_local_gate", "geometry_ladder_reading"])}

## Gate Evaluation

`{result}`

## Interpretation

{interpretation}

## What This Does Not Prove

This is still a single-observation pilot. It does not prove a general midge-swarm mechanism.

## Decision

`{result}`

## Next Node

`{next_node}`
"""
    summary_name = "4081b_summary.md" if NODE.startswith("4081b") else "4081_summary.md"
    (OUT / summary_name).write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ob", type=int, default=1)
    parser.add_argument("--data-dir", default=BaseRunConfig.data_dir)
    parser.add_argument("--node-id", default=NODE)
    parser.add_argument("--output-dir", default=None, help="Repository-relative output directory, e.g. Output/4081b/Ob2.")
    parser.add_argument("--k", default="8,10")
    parser.add_argument("--lag", type=float, default=0.10)
    parser.add_argument("--frame-stride", type=int, default=2)
    parser.add_argument("--max-focals-per-frame", type=int, default=24)
    parser.add_argument("--n-replicates", type=int, default=40)
    parser.add_argument("--prepost-sec", type=float, default=0.20)
    parser.add_argument("--exclusion-sec", type=float, default=0.80)
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
