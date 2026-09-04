#!/usr/bin/env python3
"""4155 parallel high-B full-pipeline omnibus null.

This node makes the 4149 high-B check executable by splitting the complete
all-observation pseudo-event omnibus null into deterministic chunks. Each chunk
can be run independently, resumed, and merged into a final B-level calibration.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from typing import Any

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_DIR = ROOT / "Experiment"
if str(EXPERIMENT_DIR) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_DIR))

import run_4141_full_pipeline_omnibus_survival_null as r4141  # noqa: E402


NODE = "4155_parallel_highB_omnibus_null"
DATE = "2026-09-02"
BASE_SEED = 4155_20260902
OUT_BASE = ROOT / "Output" / "4155"
SOURCE_CACHE = ROOT / "Output" / "4141" / "cache"


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def run_root(args: argparse.Namespace) -> Path:
    return OUT_BASE / "runs" / args.run_name


def chunks_dir(args: argparse.Namespace) -> Path:
    return run_root(args) / "chunks"


def tables_dir(args: argparse.Namespace) -> Path:
    return run_root(args) / "tables"


def figures_dir(args: argparse.Namespace) -> Path:
    return run_root(args) / "figures"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in columns})


def md_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    if not rows:
        return "_No rows._"
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        vals = [str(row.get(col, "")).replace("\n", " ").replace("|", "\\|") for col in columns]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def patch_4141_globals(out: Path) -> None:
    r4141.OUT = out
    r4141.FIG = out / "figures"
    r4141.CACHE = SOURCE_CACHE
    r4141.NODE = NODE
    r4141.DATE = DATE


def chunk_plan(total_null: int, chunk_size: int) -> list[tuple[int, int]]:
    if total_null <= 0:
        raise ValueError("--total-null must be positive")
    if chunk_size <= 0:
        raise ValueError("--chunk-size must be positive")
    return [(start, min(total_null, start + chunk_size - 1)) for start in range(1, total_null + 1, chunk_size)]


def chunk_name(start: int, end: int) -> str:
    return f"chunk_{start:04d}_{end:04d}"


def chunk_status_path(args: argparse.Namespace, start: int, end: int) -> Path:
    return chunks_dir(args) / chunk_name(start, end) / "status.json"


def chunk_complete(args: argparse.Namespace, start: int, end: int) -> bool:
    path = chunk_status_path(args, start, end)
    if not path.exists():
        return False
    try:
        status = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    if status.get("status") != "complete":
        return False
    cdir = path.parent
    return (cdir / "omnibus_replicates.csv").exists() and (cdir / "observation_replicate_passes.csv").exists()


def load_contexts(args: argparse.Namespace) -> dict[int, dict[str, Any]]:
    patch_4141_globals(run_root(args))
    data_dir = r4141.resolve_data_dir(r4141.BaseRunConfig(data_dir=args.data_dir))
    events_all = r4141.read_events()
    requested_obs = r4141.parse_obs(args.obs, events_all)
    all_obs = sorted(int(x) for x in events_all["ob"].dropna().unique())
    if requested_obs != all_obs:
        raise ValueError("4155 high-B inference is frozen to all observations.")
    events = events_all[events_all["ob"].isin(requested_obs)].copy().reset_index(drop=True)
    b3_arrays = r4141.read_b3_arrays()
    contexts = r4141.build_contexts(
        events,
        data_dir,
        b3_arrays,
        k_values=[8, 10],
        lag_sec=args.lag,
        frame_stride=args.frame_stride,
        max_focals=args.max_focals_per_frame,
        force_cache=args.force_cache,
    )
    return contexts


def prepare_record(rec: dict[str, np.ndarray], variable: str) -> dict[str, np.ndarray]:
    t = np.asarray(rec["t"], dtype="float64")
    x = np.asarray(rec[variable], dtype="float64")
    finite = np.isfinite(x)
    x0 = np.where(finite, x, 0.0)
    count = finite.astype("float64")
    return {
        "t": t,
        "prefix_sum": np.r_[0.0, np.cumsum(x0)],
        "prefix_count": np.r_[0.0, np.cumsum(count)],
    }


def window_mean(prepared: dict[str, np.ndarray], left: int, right: int) -> float:
    if right <= left:
        return math.nan
    c = float(prepared["prefix_count"][right] - prepared["prefix_count"][left])
    if c <= 0:
        return math.nan
    s = float(prepared["prefix_sum"][right] - prepared["prefix_sum"][left])
    return s / c


def window_means(prepared: dict[str, np.ndarray], left: np.ndarray, right: np.ndarray) -> np.ndarray:
    left = np.asarray(left, dtype="int64")
    right = np.asarray(right, dtype="int64")
    count = prepared["prefix_count"][right] - prepared["prefix_count"][left]
    total = prepared["prefix_sum"][right] - prepared["prefix_sum"][left]
    out = np.full(left.shape, np.nan, dtype="float64")
    valid = (right > left) & (count > 0)
    out[valid] = total[valid] / count[valid]
    return out


def direction_abs_fast(prepared: dict[str, np.ndarray], events: pd.DataFrame, prepost_sec: float) -> tuple[int, float]:
    t = prepared["t"]
    by_type: dict[str, list[float]] = {"low_to_high": [], "high_to_low": []}
    valid_event_ids: set[int] = set()
    for event in events.itertuples(index=False):
        event_type = str(event.event_type)
        if event_type not in by_type:
            continue
        event_t = float(event.event_t)
        p0 = int(np.searchsorted(t, event_t - prepost_sec, side="left"))
        p1 = int(np.searchsorted(t, event_t, side="left"))
        q0 = int(np.searchsorted(t, event_t, side="left"))
        q1 = int(np.searchsorted(t, event_t + prepost_sec, side="right"))
        pre_mean = window_mean(prepared, p0, p1)
        post_mean = window_mean(prepared, q0, q1)
        if not math.isfinite(pre_mean) or not math.isfinite(post_mean):
            continue
        by_type[event_type].append(post_mean - pre_mean)
        valid_event_ids.add(int(event.event_id))
    if not by_type["low_to_high"] or not by_type["high_to_low"]:
        return len(valid_event_ids), math.nan
    contrast = float(np.median(by_type["low_to_high"]) - np.median(by_type["high_to_low"]))
    return len(valid_event_ids), abs(contrast)


def direction_abs_from_times(
    prepared: dict[str, np.ndarray],
    event_times: np.ndarray,
    event_type_codes: np.ndarray,
    prepost_sec: float,
) -> tuple[int, float]:
    t = prepared["t"]
    times = np.asarray(event_times, dtype="float64")
    codes = np.asarray(event_type_codes, dtype="int8")
    p0 = np.searchsorted(t, times - prepost_sec, side="left")
    p1 = np.searchsorted(t, times, side="left")
    q0 = np.searchsorted(t, times, side="left")
    q1 = np.searchsorted(t, times + prepost_sec, side="right")
    pre = window_means(prepared, p0, p1)
    post = window_means(prepared, q0, q1)
    delta = post - pre
    valid = np.isfinite(delta) & ((codes == 0) | (codes == 1))
    if not np.any(valid):
        return 0, math.nan
    low = delta[valid & (codes == 0)]
    high = delta[valid & (codes == 1)]
    if low.size == 0 or high.size == 0:
        return int(np.sum(valid)), math.nan
    contrast = float(np.median(low) - np.median(high))
    return int(np.sum(valid)), abs(contrast)


def complement_intervals_fast(t_min: float, t_max: float, avoid_times: np.ndarray, exclusion_sec: float) -> list[tuple[float, float]]:
    avoid = np.asarray(avoid_times, dtype="float64")
    avoid = np.sort(avoid[np.isfinite(avoid)])
    if avoid.size == 0:
        return [(t_min, t_max)] if t_max > t_min else []
    lows = np.maximum(t_min, avoid - exclusion_sec)
    highs = np.minimum(t_max, avoid + exclusion_sec)
    valid = highs > lows
    lows = lows[valid]
    highs = highs[valid]
    if lows.size == 0:
        return [(t_min, t_max)] if t_max > t_min else []
    merged: list[list[float]] = []
    for lo, hi in zip(lows, highs):
        lo_f = float(lo)
        hi_f = float(hi)
        if not merged or lo_f > merged[-1][1]:
            merged.append([lo_f, hi_f])
        else:
            merged[-1][1] = max(merged[-1][1], hi_f)
    allowed: list[tuple[float, float]] = []
    cursor = t_min
    for lo, hi in merged:
        if lo > cursor:
            allowed.append((cursor, lo))
        cursor = max(cursor, hi)
    if cursor < t_max:
        allowed.append((cursor, t_max))
    return allowed


def sample_from_intervals_fast(intervals: list[tuple[float, float]], rng: np.random.Generator) -> float:
    if not intervals:
        return math.nan
    lengths = np.fromiter((hi - lo for lo, hi in intervals), dtype="float64", count=len(intervals))
    total = float(np.sum(lengths))
    if not math.isfinite(total) or total <= 0:
        return math.nan
    draw = float(rng.uniform(0.0, total))
    cumulative = np.cumsum(lengths)
    idx = int(np.searchsorted(cumulative, draw, side="right"))
    idx = min(idx, len(intervals) - 1)
    lo, hi = intervals[idx]
    return float(rng.uniform(lo, hi))


def subtract_interval(intervals: list[tuple[float, float]], block_lo: float, block_hi: float) -> list[tuple[float, float]]:
    if block_hi <= block_lo or not intervals:
        return intervals
    out: list[tuple[float, float]] = []
    for lo, hi in intervals:
        if block_hi <= lo or block_lo >= hi:
            out.append((lo, hi))
            continue
        if block_lo > lo:
            out.append((lo, min(block_lo, hi)))
        if block_hi < hi:
            out.append((max(block_hi, lo), hi))
    return [(lo, hi) for lo, hi in out if hi > lo]


def sample_times_like_fast(
    ctx: dict[str, Any],
    rng: np.random.Generator,
    avoid_times: np.ndarray,
    prepost_sec: float,
    exclusion_sec: float,
) -> np.ndarray:
    t_axis = np.asarray(ctx["time_axis"], dtype="float64")
    t_axis = t_axis[np.isfinite(t_axis)]
    t_min = float(np.nanmin(t_axis)) + prepost_sec
    t_max = float(np.nanmax(t_axis)) - prepost_sec
    base_avoid = np.asarray(avoid_times, dtype="float64")
    sampled = np.empty(int(ctx["n_events"]), dtype="float64")
    base_intervals = complement_intervals_fast(t_min, t_max, base_avoid, exclusion_sec)
    active_intervals = list(base_intervals)
    for idx in range(sampled.size):
        value = sample_from_intervals_fast(active_intervals, rng)
        if not math.isfinite(value):
            value = sample_from_intervals_fast(base_intervals, rng)
        if not math.isfinite(value):
            value = float(rng.uniform(t_min, t_max))
        sampled[idx] = value
        active_intervals = subtract_interval(active_intervals, value - exclusion_sec, value + exclusion_sec)
    return sampled


def prepare_fast_contexts(contexts: dict[int, dict[str, Any]]) -> dict[int, dict[str, Any]]:
    out: dict[int, dict[str, Any]] = {}
    for ob, ctx in contexts.items():
        b3_rec = next(iter(ctx["b3_arrays"].values()))
        local_prepared = {}
        for k, arrays in ctx["local_by_k"].items():
            local_rec = next(iter(arrays.values()))
            local_prepared[int(k)] = prepare_record(local_rec, r4141.LOCAL_VARIABLE)
        events = ctx["events"].reset_index(drop=True).copy()
        event_types = events["event_type"].astype(str).to_numpy()
        type_codes = np.full(event_types.shape, -1, dtype="int8")
        type_codes[event_types == "low_to_high"] = 0
        type_codes[event_types == "high_to_low"] = 1
        out[int(ob)] = {
            "ob": int(ob),
            "dataset": ctx["dataset"],
            "events": events,
            "event_type_codes": type_codes,
            "true_times": pd.to_numeric(events["event_t"], errors="coerce").to_numpy(dtype="float64"),
            "time_axis": np.asarray(ctx["time_axis"], dtype="float64"),
            "n_events": int(len(events)),
            "b3": prepare_record(b3_rec, r4141.B3_VARIABLE),
            "local_by_k": local_prepared,
        }
    return out


def validate_fast_equivalence(args: argparse.Namespace, contexts: dict[int, dict[str, Any]]) -> dict[str, Any]:
    fast_contexts = prepare_fast_contexts(contexts)
    rng = np.random.default_rng(BASE_SEED + 17)
    rows: list[dict[str, Any]] = []
    max_abs_diff = 0.0
    for ob in sorted(contexts)[: min(4, len(contexts))]:
        ctx = contexts[ob]
        fctx = fast_contexts[ob]
        true_times = pd.to_numeric(ctx["events"]["event_t"], errors="coerce").to_numpy(dtype="float64")
        pseudo = r4141.sample_like_events(
            ctx["events"],
            ctx["time_axis"],
            rng,
            args.prepost_sec,
            args.exclusion_sec,
            avoid_times=true_times,
            event_id_offset=990_000_000 + ob * 10_000,
        )
        for label, old_rec, new_rec, variable in [
            ("b3", next(iter(ctx["b3_arrays"].values())), fctx["b3"], r4141.B3_VARIABLE),
            ("k8", next(iter(ctx["local_by_k"][8].values())), fctx["local_by_k"][8], r4141.LOCAL_VARIABLE),
            ("k10", next(iter(ctx["local_by_k"][10].values())), fctx["local_by_k"][10], r4141.LOCAL_VARIABLE),
        ]:
            _, old_abs = r4141.direction_abs_from_record(old_rec, pseudo, variable, args.prepost_sec)
            _, new_abs = direction_abs_fast(new_rec, pseudo, args.prepost_sec)
            diff = abs(old_abs - new_abs) if math.isfinite(old_abs) and math.isfinite(new_abs) else 0.0
            max_abs_diff = max(max_abs_diff, diff)
            rows.append({"ob": ob, "record": label, "old_abs": old_abs, "fast_abs": new_abs, "abs_diff": diff})
    out = {
        "status": "pass" if max_abs_diff <= 1e-10 else "fail",
        "max_abs_diff": max_abs_diff,
        "n_checks": len(rows),
    }
    write_csv(run_root(args) / "fast_equivalence_check.csv", rows, ["ob", "record", "old_abs", "fast_abs", "abs_diff"])
    write_csv(tables_dir(args) / "fast_equivalence_check.csv", rows, ["ob", "record", "old_abs", "fast_abs", "abs_diff"])
    write_json(run_root(args) / "fast_equivalence_check.json", out)
    return out


def run_replicate(
    fast_contexts: dict[int, dict[str, Any]],
    rep: int,
    n_controls: int,
    prepost_sec: float,
    exclusion_sec: float,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    rng = np.random.default_rng(BASE_SEED + rep * 1_000_003)
    n_both = 0
    n_any = 0
    valid_b3 = 0
    valid_k = {8: 0, 10: 0}
    ob_rows: list[dict[str, Any]] = []

    for ob in sorted(fast_contexts):
        ctx = fast_contexts[ob]
        true_times = np.asarray(ctx["true_times"], dtype="float64")
        pseudo_times = sample_times_like_fast(ctx, rng, true_times, prepost_sec, exclusion_sec)
        avoid_control = np.r_[true_times, pseudo_times]
        controls = [
            sample_times_like_fast(ctx, rng, avoid_control, prepost_sec, exclusion_sec)
            for c in range(n_controls)
        ]

        _, b3_abs = direction_abs_from_times(ctx["b3"], pseudo_times, ctx["event_type_codes"], prepost_sec)
        if math.isfinite(b3_abs):
            valid_b3 += 1

        row: dict[str, Any] = {
            "replicate": rep,
            "ob": ob,
            "dataset": ctx["dataset"],
            "n_events": int(ctx["n_events"]),
            "b3_event_direction_abs_z": b3_abs,
        }
        any_pass = False
        both_pass = True
        for k in [8, 10]:
            _, local_abs = direction_abs_from_times(ctx["local_by_k"][k], pseudo_times, ctx["event_type_codes"], prepost_sec)
            if math.isfinite(local_abs):
                valid_k[k] += 1
            control_abs = [
                direction_abs_from_times(ctx["local_by_k"][k], c_times, ctx["event_type_codes"], prepost_sec)[1]
                for c_times in controls
            ]
            gv = r4141.gate_values(local_abs, control_abs, b3_abs)
            prefix = f"k{k}"
            row[f"{prefix}_local_event_direction_abs_z"] = local_abs
            row[f"{prefix}_local_non_event_direction_abs_median_z"] = gv["local_non_event_direction_abs_median_z"]
            row[f"{prefix}_local_event_minus_non_event_direction_z"] = gv["local_event_minus_non_event_direction_z"]
            row[f"{prefix}_p_non_event_direction_ge_event"] = gv["p_non_event_direction_ge_event"]
            row[f"{prefix}_local_to_b3_direction_ratio"] = gv["local_to_b3_direction_ratio"]
            row[f"{prefix}_pass"] = bool(gv["pass"])
            any_pass = any_pass or bool(gv["pass"])
            both_pass = both_pass and bool(gv["pass"])
        row["both_pass"] = bool(both_pass)
        row["any_pass"] = bool(any_pass)
        if both_pass:
            n_both += 1
        if any_pass:
            n_any += 1
        ob_rows.append(row)

    aggregate = {
        "replicate": rep,
        "n_both": n_both,
        "n_any": n_any,
        "n_obs_tested": len(fast_contexts),
        "n_obs_with_valid_b3": valid_b3,
        "n_obs_with_valid_k8": valid_k[8],
        "n_obs_with_valid_k10": valid_k[10],
    }
    return aggregate, ob_rows


def worker(args: argparse.Namespace) -> int:
    out = run_root(args)
    cdir = chunks_dir(args) / chunk_name(args.rep_start, args.rep_end)
    cdir.mkdir(parents=True, exist_ok=True)
    status_path = cdir / "status.json"
    if chunk_complete(args, args.rep_start, args.rep_end) and not args.force:
        return 0
    write_json(
        status_path,
        {
            "node": NODE,
            "run_name": args.run_name,
            "status": "running",
            "started_at": now(),
            "rep_start": args.rep_start,
            "rep_end": args.rep_end,
            "n_controls": args.n_controls,
        },
    )
    contexts = load_contexts(args)
    fast_contexts = prepare_fast_contexts(contexts)
    aggregate_rows: list[dict[str, Any]] = []
    ob_pass_rows: list[dict[str, Any]] = []
    started = time.time()
    for rep in range(args.rep_start, args.rep_end + 1):
        aggregate, ob_rows = run_replicate(
            fast_contexts,
            rep=rep,
            n_controls=args.n_controls,
            prepost_sec=args.prepost_sec,
            exclusion_sec=args.exclusion_sec,
        )
        aggregate_rows.append(aggregate)
        ob_pass_rows.extend(ob_rows)
        if rep == args.rep_start or rep == args.rep_end or (rep - args.rep_start + 1) % max(1, args.chunk_progress_interval) == 0:
            write_json(
                status_path,
                {
                    "node": NODE,
                    "run_name": args.run_name,
                    "status": "running",
                    "started_at": datetime.fromtimestamp(started).isoformat(timespec="seconds"),
                    "updated_at": now(),
                    "rep_start": args.rep_start,
                    "rep_end": args.rep_end,
                    "last_completed_replicate": rep,
                    "progress": (rep - args.rep_start + 1) / (args.rep_end - args.rep_start + 1),
                },
            )
    write_csv(cdir / "omnibus_replicates.csv", aggregate_rows, r4141.REPLICATE_COLUMNS)
    write_csv(cdir / "observation_replicate_passes.csv", ob_pass_rows, r4141.OBS_PASS_COLUMNS)
    write_json(
        status_path,
        {
            "node": NODE,
            "run_name": args.run_name,
            "status": "complete",
            "started_at": datetime.fromtimestamp(started).isoformat(timespec="seconds"),
            "finished_at": now(),
            "rep_start": args.rep_start,
            "rep_end": args.rep_end,
            "n_replicates": args.rep_end - args.rep_start + 1,
            "elapsed_sec": time.time() - started,
            "aggregate_csv": rel(cdir / "omnibus_replicates.csv"),
            "observation_csv": rel(cdir / "observation_replicate_passes.csv"),
        },
    )
    write_json(out / "latest_worker_complete.json", {"chunk": chunk_name(args.rep_start, args.rep_end), "finished_at": now()})
    return 0


def read_completed_chunks(args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame, list[dict[str, Any]]]:
    aggregate_parts: list[pd.DataFrame] = []
    pass_parts: list[pd.DataFrame] = []
    status_rows: list[dict[str, Any]] = []
    for start, end in chunk_plan(args.total_null, args.chunk_size):
        cdir = chunks_dir(args) / chunk_name(start, end)
        status_path = cdir / "status.json"
        status = {}
        if status_path.exists():
            try:
                status = json.loads(status_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                status = {"status": "invalid_json"}
        complete = chunk_complete(args, start, end)
        status_rows.append(
            {
                "chunk": chunk_name(start, end),
                "rep_start": start,
                "rep_end": end,
                "status": status.get("status", "missing"),
                "complete": complete,
                "elapsed_sec": status.get("elapsed_sec", ""),
            }
        )
        if complete:
            aggregate_parts.append(pd.read_csv(cdir / "omnibus_replicates.csv"))
            pass_parts.append(pd.read_csv(cdir / "observation_replicate_passes.csv"))
    aggregate = pd.concat(aggregate_parts, ignore_index=True) if aggregate_parts else pd.DataFrame(columns=r4141.REPLICATE_COLUMNS)
    ob_pass = pd.concat(pass_parts, ignore_index=True) if pass_parts else pd.DataFrame(columns=r4141.OBS_PASS_COLUMNS)
    return aggregate, ob_pass, status_rows


def write_top_level_latest(args: argparse.Namespace, decision: dict[str, Any]) -> None:
    write_json(
        OUT_BASE / "latest_run.json",
        {
            "node": NODE,
            "date": DATE,
            "run_name": args.run_name,
            "run_path": rel(run_root(args)),
            "decision": decision.get("main_result", {}).get("gate_result", decision.get("gate_result", "")),
            "updated_at": now(),
        },
    )


def merge(args: argparse.Namespace) -> int:
    out = run_root(args)
    patch_4141_globals(out)
    out.mkdir(parents=True, exist_ok=True)
    tables_dir(args).mkdir(parents=True, exist_ok=True)
    figures_dir(args).mkdir(parents=True, exist_ok=True)

    aggregate, ob_pass, chunk_rows = read_completed_chunks(args)
    write_csv(out / "chunk_status.csv", chunk_rows, ["chunk", "rep_start", "rep_end", "status", "complete", "elapsed_sec"])
    write_csv(tables_dir(args) / "chunk_status.csv", chunk_rows, ["chunk", "rep_start", "rep_end", "status", "complete", "elapsed_sec"])
    completed_reps = int(aggregate["replicate"].nunique()) if not aggregate.empty else 0
    missing_chunks = [row["chunk"] for row in chunk_rows if not row["complete"]]

    if completed_reps == 0:
        write_json(
            out / "decision.json",
            {
                "node": NODE,
                "run_name": args.run_name,
                "gate_result": "incomplete_no_completed_chunks",
                "completed_replicates": 0,
                "requested_replicates": args.total_null,
                "missing_chunks": missing_chunks,
            },
        )
        return 2

    aggregate = aggregate.sort_values("replicate", kind="mergesort").drop_duplicates("replicate", keep="first")
    ob_pass = ob_pass.sort_values(["replicate", "ob"], kind="mergesort").drop_duplicates(["replicate", "ob"], keep="first")
    observed = r4141.observed_pass_lookup()
    stats, pass_rates, r4141_decision = r4141.summarize_results(
        aggregate,
        ob_pass,
        observed,
        completed_reps,
        args.n_controls,
        smoke=False,
    )
    complete = completed_reps >= args.total_null and not missing_chunks
    is_operational_smoke = args.total_null < 100 or args.n_controls < 40
    if not complete:
        gate = "partial_highB_checkpoint"
    elif is_operational_smoke:
        gate = "operational_smoke_complete_not_inference"
    else:
        gate = r4141_decision["main_result"]["gate_result"]
    decision = {
        "node": NODE,
        "date": DATE,
        "run_name": args.run_name,
        "gate_result": gate,
        "requested_replicates": args.total_null,
        "completed_replicates": completed_reps,
        "chunk_size": args.chunk_size,
        "workers": args.workers,
        "n_controls_per_replicate_observation": args.n_controls,
        "complete": complete,
        "operational_smoke": is_operational_smoke,
        "missing_chunks": missing_chunks,
        "primary_metrics": stats,
        "main_result": r4141_decision["main_result"],
        "boundary": "partial checkpoint only; do not use as formal high-B p-value"
        if not complete
        else ("operational smoke only; replicate/control counts are too small for inference" if is_operational_smoke else ""),
        "next": "complete missing chunks then rerun --mode merge" if not complete else "optional manuscript wording update if accepted",
    }

    aggregate_rows = aggregate.to_dict(orient="records")
    pass_rows = ob_pass.to_dict(orient="records")
    r4141.write_csv(out / "omnibus_replicates.csv", aggregate_rows, r4141.REPLICATE_COLUMNS)
    r4141.write_csv(tables_dir(args) / "omnibus_replicates.csv", aggregate_rows, r4141.REPLICATE_COLUMNS)
    r4141.write_csv(out / "observation_replicate_passes.csv", pass_rows, r4141.OBS_PASS_COLUMNS)
    r4141.write_csv(tables_dir(args) / "observation_replicate_passes.csv", pass_rows, r4141.OBS_PASS_COLUMNS)
    r4141.write_csv(out / "observation_null_pass_rates.csv", pass_rates, r4141.PASS_RATE_COLUMNS)
    r4141.write_csv(tables_dir(args) / "observation_null_pass_rates.csv", pass_rates, r4141.PASS_RATE_COLUMNS)
    r4141.write_csv(
        out / "N_both_distribution.csv",
        r4141.distribution_rows(pd.to_numeric(aggregate["n_both"], errors="coerce").dropna().to_numpy(dtype="float64"), "n_both"),
        ["n_both", "count", "fraction"],
    )
    r4141.write_csv(
        out / "N_any_distribution.csv",
        r4141.distribution_rows(pd.to_numeric(aggregate["n_any"], errors="coerce").dropna().to_numpy(dtype="float64"), "n_any"),
        ["n_any", "count", "fraction"],
    )
    r4141.write_json(out / "p_omnibus.json", stats)
    r4141.write_json(out / "decision.json", decision)
    r4141.make_figures(aggregate, pd.DataFrame(pass_rates), stats, smoke=False)

    config = {
        "node": NODE,
        "date": DATE,
        "run_name": args.run_name,
        "mode": "parallel_chunked_highB",
        "total_null": args.total_null,
        "completed_replicates": completed_reps,
        "chunk_size": args.chunk_size,
        "workers": args.workers,
        "n_controls_per_replicate_observation": args.n_controls,
        "cache_source": rel(SOURCE_CACHE),
        "rng_design": "deterministic per-replicate seed BASE_SEED + replicate * 1000003",
        "pipeline": {
            "k_values": [8, 10],
            "lag_sec": args.lag,
            "frame_stride": args.frame_stride,
            "max_focals_per_frame": args.max_focals_per_frame,
            "prepost_sec": args.prepost_sec,
            "exclusion_sec": args.exclusion_sec,
        },
        "observed": {"n_both": r4141.OBSERVED_N_BOTH, "n_any": r4141.OBSERVED_N_ANY},
    }
    write_json(out / "run_config.json", config)

    summary = dedent(
        f"""\
        # Node 4155 Parallel High-B Omnibus Null

        ## Purpose

        Convert the failed monolithic 4149 high-B run into a deterministic,
        chunked, resumable, and parallel high-B calibration.

        ## Gate Result

        `{gate}`

        ```text
        requested_replicates = {args.total_null}
        completed_replicates = {completed_reps}
        chunk_size = {args.chunk_size}
        workers = {args.workers}
        n_controls_per_replicate_observation = {args.n_controls}
        observed N_both = {r4141.OBSERVED_N_BOTH}
        observed N_any = {r4141.OBSERVED_N_ANY}
        p_both_ge_14 = {stats["p_omnibus_both_ge_14"]:.6g}
        p_any_ge_15 = {stats["p_omnibus_any_ge_15"]:.6g}
        null N_both mean = {stats["n_both_null_mean"]:.6g}
        null N_both q95 = {stats["n_both_null_q95"]:.6g}
        null N_both max = {stats["n_both_null_max"]:.6g}
        ```

        ## Method

        Each replicate is assigned a deterministic independent seed, so chunks
        can be run in any order and resumed without changing already-completed
        replicate values. The pipeline keeps the frozen 4141 event definition,
        pseudo-event construction, non-event controls, survival gate, k values,
        lag, and all-19 observation scope. The only computational change is
        chunking plus a prefix-sum implementation of the same event-window mean
        calculation.

        ## Chunk Status

        {md_table(chunk_rows, ["chunk", "rep_start", "rep_end", "status", "complete", "elapsed_sec"])}

        ## Observation Null Pass Rates

        {md_table(pass_rates, r4141.PASS_RATE_COLUMNS)}

        ## Boundary

        {"This run is an operational smoke test only; do not use it as a scientific p-value." if is_operational_smoke else ("No missing chunks; this is a completed high-B calibration." if complete else "This is a partial checkpoint. Do not use it as a formal high-B p-value until all chunks complete.")}

        ## Artifacts

        - `{rel(out / "run_config.json")}`
        - `{rel(out / "chunk_status.csv")}`
        - `{rel(out / "omnibus_replicates.csv")}`
        - `{rel(out / "observation_replicate_passes.csv")}`
        - `{rel(out / "observation_null_pass_rates.csv")}`
        - `{rel(out / "N_both_distribution.csv")}`
        - `{rel(out / "N_any_distribution.csv")}`
        - `{rel(out / "p_omnibus.json")}`
        - `{rel(out / "decision.json")}`
        - `{rel(out / "figures")}`
        """
    ).lstrip()
    summary = "\n".join(line[8:] if line.startswith("        ") else line for line in summary.splitlines()) + "\n"
    (out / "4155_summary.md").write_text(summary, encoding="utf-8")
    (OUT_BASE / "4155_summary.md").write_text(summary, encoding="utf-8")
    write_top_level_latest(args, decision)
    print(json.dumps(decision, ensure_ascii=False, indent=2), flush=True)
    return 0 if complete else 3


def run_manager(args: argparse.Namespace) -> int:
    out = run_root(args)
    for path in [out, chunks_dir(args), tables_dir(args), figures_dir(args), OUT_BASE]:
        path.mkdir(parents=True, exist_ok=True)
    write_json(
        out / "manager_status.json",
        {
            "node": NODE,
            "run_name": args.run_name,
            "status": "starting",
            "started_at": now(),
            "total_null": args.total_null,
            "chunk_size": args.chunk_size,
            "workers": args.workers,
            "n_controls": args.n_controls,
        },
    )

    contexts = load_contexts(args)
    fast_check = validate_fast_equivalence(args, contexts)
    if fast_check["status"] != "pass":
        write_json(out / "manager_status.json", {"node": NODE, "run_name": args.run_name, "status": "failed_fast_validation", "fast_check": fast_check})
        return 4

    chunks = [(s, e) for s, e in chunk_plan(args.total_null, args.chunk_size) if args.force or not chunk_complete(args, s, e)]
    write_json(
        out / "manager_status.json",
        {
            "node": NODE,
            "run_name": args.run_name,
            "status": "running_workers",
            "started_at": now(),
            "total_null": args.total_null,
            "chunk_size": args.chunk_size,
            "workers": args.workers,
            "n_chunks_total": len(chunk_plan(args.total_null, args.chunk_size)),
            "n_chunks_to_run": len(chunks),
            "fast_equivalence_check": fast_check,
        },
    )

    procs: list[tuple[int, int, subprocess.Popen[Any], Path]] = []
    remaining = chunks[:]
    completed = 0
    failed: list[dict[str, Any]] = []
    command_base = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--mode",
        "worker",
        "--run-name",
        args.run_name,
        "--total-null",
        str(args.total_null),
        "--chunk-size",
        str(args.chunk_size),
        "--n-controls",
        str(args.n_controls),
        "--data-dir",
        args.data_dir,
        "--obs",
        args.obs,
        "--lag",
        str(args.lag),
        "--frame-stride",
        str(args.frame_stride),
        "--max-focals-per-frame",
        str(args.max_focals_per_frame),
        "--prepost-sec",
        str(args.prepost_sec),
        "--exclusion-sec",
        str(args.exclusion_sec),
        "--chunk-progress-interval",
        str(args.chunk_progress_interval),
    ]
    if args.force_cache:
        command_base.append("--force-cache")
    if args.force:
        command_base.append("--force")

    while remaining or procs:
        while remaining and len(procs) < args.workers:
            start, end = remaining.pop(0)
            cdir = chunks_dir(args) / chunk_name(start, end)
            cdir.mkdir(parents=True, exist_ok=True)
            log_path = cdir / "worker.log"
            cmd = command_base + ["--rep-start", str(start), "--rep-end", str(end)]
            log_fh = log_path.open("w", encoding="utf-8")
            proc = subprocess.Popen(cmd, cwd=str(ROOT), stdout=log_fh, stderr=subprocess.STDOUT)
            log_fh.close()
            procs.append((start, end, proc, log_path))
        time.sleep(args.poll_sec)
        still_running: list[tuple[int, int, subprocess.Popen[Any], Path]] = []
        for start, end, proc, log_path in procs:
            code = proc.poll()
            if code is None:
                still_running.append((start, end, proc, log_path))
                continue
            if code == 0:
                completed += 1
            else:
                failed.append({"chunk": chunk_name(start, end), "returncode": code, "log": rel(log_path)})
        procs = still_running
        done_count = sum(1 for s, e in chunk_plan(args.total_null, args.chunk_size) if chunk_complete(args, s, e))
        write_json(
            out / "manager_status.json",
            {
                "node": NODE,
                "run_name": args.run_name,
                "status": "running_workers" if (remaining or procs) else "workers_finished",
                "updated_at": now(),
                "total_null": args.total_null,
                "chunk_size": args.chunk_size,
                "workers": args.workers,
                "running_chunks": [chunk_name(s, e) for s, e, _, _ in procs],
                "remaining_to_launch": len(remaining),
                "chunks_completed_this_invocation": completed,
                "chunks_complete_total": done_count,
                "failed": failed,
            },
        )
        if failed and not args.continue_on_worker_fail:
            break

    if failed and not args.continue_on_worker_fail:
        for _, _, proc, _ in procs:
            if proc.poll() is None:
                proc.terminate()
        write_json(out / "manager_status.json", {"node": NODE, "run_name": args.run_name, "status": "failed", "failed": failed, "updated_at": now()})
        return 5

    merge_code = merge(args)
    decision_path = out / "decision.json"
    decision = json.loads(decision_path.read_text(encoding="utf-8")) if decision_path.exists() else {}
    write_json(
        out / "manager_status.json",
        {
            "node": NODE,
            "run_name": args.run_name,
            "status": "complete" if merge_code == 0 else "partial_or_failed_merge",
            "updated_at": now(),
            "total_null": args.total_null,
            "chunk_size": args.chunk_size,
            "workers": args.workers,
            "chunks_complete_total": sum(1 for s, e in chunk_plan(args.total_null, args.chunk_size) if chunk_complete(args, s, e)),
            "merge_return_code": merge_code,
            "decision": decision.get("gate_result", ""),
            "completed_replicates": decision.get("completed_replicates", ""),
        },
    )
    return merge_code


def status(args: argparse.Namespace) -> int:
    aggregate, _ob_pass, chunk_rows = read_completed_chunks(args)
    completed_reps = int(aggregate["replicate"].nunique()) if not aggregate.empty else 0
    payload = {
        "node": NODE,
        "run_name": args.run_name,
        "status": "complete" if completed_reps >= args.total_null and all(row["complete"] for row in chunk_rows) else "partial",
        "requested_replicates": args.total_null,
        "completed_replicates": completed_reps,
        "chunk_rows": chunk_rows,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2), flush=True)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["run", "worker", "merge", "status"], default="run")
    parser.add_argument("--run-name", default="highB_n1000_c40")
    parser.add_argument("--total-null", type=int, default=1000)
    parser.add_argument("--chunk-size", type=int, default=50)
    parser.add_argument("--workers", type=int, default=max(1, min(4, (os.cpu_count() or 2) - 1)))
    parser.add_argument("--n-controls", type=int, default=40)
    parser.add_argument("--data-dir", default=r4141.BaseRunConfig.data_dir)
    parser.add_argument("--obs", default="all")
    parser.add_argument("--lag", type=float, default=0.10)
    parser.add_argument("--frame-stride", type=int, default=2)
    parser.add_argument("--max-focals-per-frame", type=int, default=24)
    parser.add_argument("--prepost-sec", type=float, default=0.20)
    parser.add_argument("--exclusion-sec", type=float, default=0.80)
    parser.add_argument("--rep-start", type=int, default=1)
    parser.add_argument("--rep-end", type=int, default=1)
    parser.add_argument("--chunk-progress-interval", type=int, default=10)
    parser.add_argument("--poll-sec", type=float, default=5.0)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--force-cache", action="store_true")
    parser.add_argument("--continue-on-worker-fail", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.mode == "worker":
        return worker(args)
    if args.mode == "merge":
        return merge(args)
    if args.mode == "status":
        return status(args)
    return run_manager(args)


if __name__ == "__main__":
    raise SystemExit(main())
