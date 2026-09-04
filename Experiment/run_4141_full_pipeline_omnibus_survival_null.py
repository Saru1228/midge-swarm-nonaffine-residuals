#!/usr/bin/env python3
"""4141 full-pipeline omnibus survival null.

This submission-hardening node asks whether the observed all-observation T1
survival count (14/19 both-scale, 15/19 any-scale) is unusual when the full
per-observation event/control gate is rerun on pseudo-event times.

The local-affine T1 definition, preprocessing, thresholds, and observation
scope are inherited from the 4140 frozen analysis contract and 4081c.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from textwrap import dedent
from typing import Any

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


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


OUT = ROOT / "Output" / "4141"
FIG = OUT / "figures"
CACHE = OUT / "cache"

NODE = "4141_full_pipeline_omnibus_survival_null"
DATE = "2026-09-01"
RNG_SEED = 4141_20260901

EVENT_PATH = ROOT / "Output" / "3045" / "tables" / "transition_events.csv"
B3_FRAME_PATH = ROOT / "Output" / "4002A" / "processed" / "frame_residual_spatial_metrics.csv"
OBSERVED_PATH = ROOT / "Output" / "4081c" / "full_geometry_ladder_rows.csv"
CONTRACT_PATH = ROOT / "Output" / "4140" / "frozen_analysis_contract.yaml"

TARGET_ID = "T1_transition_tangential_residual"
B3_VARIABLE = "resid_tangential_speed_mean"
LOCAL_VARIABLE = "local_tangential_speed_mean"

GAP_GATE = 0.03
P_GATE = 0.35
RATIO_GATE = 0.30
OBSERVED_N_BOTH = 14
OBSERVED_N_ANY = 15

REPLICATE_COLUMNS = [
    "replicate",
    "n_both",
    "n_any",
    "n_obs_tested",
    "n_obs_with_valid_b3",
    "n_obs_with_valid_k8",
    "n_obs_with_valid_k10",
]

OBS_PASS_COLUMNS = [
    "replicate",
    "ob",
    "dataset",
    "n_events",
    "b3_event_direction_abs_z",
    "k8_local_event_direction_abs_z",
    "k8_local_non_event_direction_abs_median_z",
    "k8_local_event_minus_non_event_direction_z",
    "k8_p_non_event_direction_ge_event",
    "k8_local_to_b3_direction_ratio",
    "k8_pass",
    "k10_local_event_direction_abs_z",
    "k10_local_non_event_direction_abs_median_z",
    "k10_local_event_minus_non_event_direction_z",
    "k10_p_non_event_direction_ge_event",
    "k10_local_to_b3_direction_ratio",
    "k10_pass",
    "both_pass",
    "any_pass",
]

PASS_RATE_COLUMNS = [
    "ob",
    "dataset",
    "n_replicates",
    "null_pass_rate_k8",
    "null_pass_rate_k10",
    "null_pass_rate_both",
    "null_pass_rate_any",
    "observed_k8_pass",
    "observed_k10_pass",
    "observed_both_pass",
    "observed_any_pass",
]


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def ensure_dirs() -> None:
    for path in (OUT, FIG, CACHE, OUT / "tables"):
        path.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in columns})


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def md_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    if not rows:
        return "_No rows._"
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        vals: list[str] = []
        for col in columns:
            val = row.get(col, "")
            if isinstance(val, float):
                vals.append("NA" if not math.isfinite(val) else f"{val:.4g}")
            else:
                vals.append(str(val).replace("\n", " ").replace("|", "\\|"))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def finite_median(values: list[float] | np.ndarray | pd.Series) -> float:
    arr = np.asarray(values, dtype="float64")
    arr = arr[np.isfinite(arr)]
    return float(np.median(arr)) if arr.size else math.nan


def finite_quantile(values: list[float] | np.ndarray | pd.Series, q: float) -> float:
    arr = np.asarray(values, dtype="float64")
    arr = arr[np.isfinite(arr)]
    return float(np.quantile(arr, q)) if arr.size else math.nan


def safe_float(value: Any) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return math.nan
    return out if math.isfinite(out) else math.nan


def direction_abs(features: pd.DataFrame, variable: str) -> tuple[int, float]:
    d = features[(features["variable"] == variable) & (features["event_type"].isin(["low_to_high", "high_to_low"]))].copy()
    if d.empty:
        return 0, math.nan
    by_type = d.groupby("event_type")["signed_delta_post_minus_pre_z"].median()
    if "low_to_high" not in by_type or "high_to_low" not in by_type:
        return int(d["event_id"].nunique()), math.nan
    return int(d["event_id"].nunique()), abs(float(by_type["low_to_high"] - by_type["high_to_low"]))


def direction_abs_from_record(
    rec: dict[str, np.ndarray],
    events: pd.DataFrame,
    variable: str,
    prepost_sec: float,
) -> tuple[int, float]:
    t = np.asarray(rec["t"], dtype="float64")
    x = np.asarray(rec[variable], dtype="float64")
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
        if p1 <= p0 or q1 <= q0:
            continue
        pre = x[p0:p1]
        post = x[q0:q1]
        if not np.isfinite(pre).any() or not np.isfinite(post).any():
            continue
        delta = float(np.nanmean(post) - np.nanmean(pre))
        if not math.isfinite(delta):
            continue
        by_type[event_type].append(delta)
        valid_event_ids.add(int(event.event_id))
    if not by_type["low_to_high"] or not by_type["high_to_low"]:
        return len(valid_event_ids), math.nan
    contrast = float(np.median(by_type["low_to_high"]) - np.median(by_type["high_to_low"]))
    return len(valid_event_ids), abs(contrast)


def bool_from_csv(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def read_events() -> pd.DataFrame:
    if not EVENT_PATH.exists():
        raise FileNotFoundError(f"Missing {rel(EVENT_PATH)}; run 3045 first.")
    events = pd.read_csv(EVENT_PATH)
    for col in ["event_id", "ob", "event_t"]:
        events[col] = pd.to_numeric(events[col], errors="coerce")
    events = events.dropna(subset=["event_id", "ob", "dataset", "event_t", "event_type"]).copy()
    events["event_id"] = events["event_id"].astype("int64")
    events["ob"] = events["ob"].astype("int64")
    return events.sort_values(["ob", "event_t"], kind="mergesort").reset_index(drop=True)


def read_b3_arrays() -> dict[tuple[int, str], dict[str, np.ndarray]]:
    if not B3_FRAME_PATH.exists():
        raise FileNotFoundError(f"Missing {rel(B3_FRAME_PATH)}; run 4002A first.")
    frame = pd.read_csv(B3_FRAME_PATH)
    return r4002a.build_arrays(frame)


def lag_label(lag: float) -> str:
    return f"{lag:.3f}".replace(".", "p")


def local_cache_path(ob: int, k: int, lag_sec: float, frame_stride: int, max_focals: int) -> Path:
    return CACHE / f"Ob{ob}_k{k}_lag{lag_label(lag_sec)}_stride{frame_stride}_focals{max_focals}.csv"


def load_or_build_local_frame(
    ob: int,
    dataset: str,
    data_dir: Path,
    k: int,
    lag_sec: float,
    frame_stride: int,
    max_focals: int,
    force: bool,
) -> pd.DataFrame:
    path = local_cache_path(ob, k, lag_sec, frame_stride, max_focals)
    if path.exists() and not force:
        return pd.read_csv(path)
    print(f"[4141] building local T1 cache Ob{ob} k={k}", flush=True)
    frame = r4081.build_local_metric_frame(ob, dataset, data_dir, k, lag_sec, frame_stride, max_focals)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)
    return frame


def sample_like_events(
    template_events: pd.DataFrame,
    t_axis: np.ndarray,
    rng: np.random.Generator,
    prepost_sec: float,
    exclusion_sec: float,
    avoid_times: np.ndarray,
    event_id_offset: int,
) -> pd.DataFrame:
    def complement_intervals(avoid_times_in: np.ndarray) -> list[tuple[float, float]]:
        avoid_local = np.asarray(avoid_times_in, dtype="float64")
        avoid_local = avoid_local[np.isfinite(avoid_local)]
        if avoid_local.size == 0:
            return [(t_min, t_max)] if t_max > t_min else []
        blocked = []
        for center in np.sort(avoid_local):
            lo = max(t_min, float(center) - exclusion_sec)
            hi = min(t_max, float(center) + exclusion_sec)
            if hi > lo:
                blocked.append((lo, hi))
        if not blocked:
            return [(t_min, t_max)] if t_max > t_min else []
        merged: list[list[float]] = []
        for lo, hi in blocked:
            if not merged or lo > merged[-1][1]:
                merged.append([lo, hi])
            else:
                merged[-1][1] = max(merged[-1][1], hi)
        allowed: list[tuple[float, float]] = []
        cursor = t_min
        for lo, hi in merged:
            if lo > cursor:
                allowed.append((cursor, lo))
            cursor = max(cursor, hi)
        if cursor < t_max:
            allowed.append((cursor, t_max))
        return allowed

    def sample_from_intervals(intervals: list[tuple[float, float]]) -> float:
        lengths = np.asarray([hi - lo for lo, hi in intervals], dtype="float64")
        total = float(np.sum(lengths))
        if not math.isfinite(total) or total <= 0:
            return math.nan
        draw = float(rng.uniform(0.0, total))
        acc = 0.0
        for (lo, hi), length in zip(intervals, lengths):
            if draw <= acc + float(length):
                return float(rng.uniform(lo, hi))
            acc += float(length)
        lo, hi = intervals[-1]
        return float(rng.uniform(lo, hi))

    t = np.asarray(t_axis, dtype="float64")
    t = t[np.isfinite(t)]
    if t.size < 3:
        raise ValueError("Time axis too short for pseudo-event sampling.")
    t_min = float(np.nanmin(t)) + prepost_sec
    t_max = float(np.nanmax(t)) - prepost_sec
    avoid = np.asarray(avoid_times, dtype="float64")
    avoid = avoid[np.isfinite(avoid)]
    rows: list[dict[str, Any]] = []
    sampled_so_far: list[float] = []
    for local_idx, event in enumerate(template_events.itertuples(index=False), start=1):
        sampled = sample_from_intervals(complement_intervals(np.r_[avoid, np.asarray(sampled_so_far, dtype="float64")]))
        if not math.isfinite(sampled):
            # Fall back to preserving the true-event exclusion even if pseudo-events
            # become dense in short recordings.
            sampled = sample_from_intervals(complement_intervals(avoid))
        if not math.isfinite(sampled):
            sampled = float(rng.uniform(t_min, t_max))
        sampled_so_far.append(sampled)
        rows.append(
            {
                "event_id": int(event_id_offset + local_idx),
                "ob": int(event.ob),
                "dataset": str(event.dataset),
                "event_t": sampled,
                "event_type": str(event.event_type),
            }
        )
    return pd.DataFrame(rows)


def local_features(
    local_arrays: dict[tuple[int, str], dict[str, np.ndarray]],
    events: pd.DataFrame,
    prepost_sec: float,
) -> pd.DataFrame:
    return r4081.extract_features(local_arrays, events, [LOCAL_VARIABLE], prepost_sec)


def b3_features(
    b3_arrays: dict[tuple[int, str], dict[str, np.ndarray]],
    events: pd.DataFrame,
    prepost_sec: float,
) -> pd.DataFrame:
    cfg = r4002a.RunConfig(prepost_window_sec=prepost_sec)
    return r4002a.extract_event_features(b3_arrays, events, cfg)


def gate_values(local_abs: float, control_abs_values: list[float], b3_abs: float) -> dict[str, Any]:
    controls = np.asarray(control_abs_values, dtype="float64")
    controls = controls[np.isfinite(controls)]
    null_med = float(np.median(controls)) if controls.size else math.nan
    p_ge = float(np.mean(controls >= local_abs)) if controls.size and math.isfinite(local_abs) else math.nan
    gap = local_abs - null_med if math.isfinite(local_abs) and math.isfinite(null_med) else math.nan
    ratio = local_abs / b3_abs if math.isfinite(local_abs) and math.isfinite(b3_abs) and b3_abs > 1e-12 else math.nan
    passed = bool(
        math.isfinite(gap)
        and gap > GAP_GATE
        and math.isfinite(p_ge)
        and p_ge <= P_GATE
        and math.isfinite(ratio)
        and ratio >= RATIO_GATE
    )
    return {
        "local_non_event_direction_abs_median_z": null_med,
        "local_event_minus_non_event_direction_z": gap,
        "p_non_event_direction_ge_event": p_ge,
        "local_to_b3_direction_ratio": ratio,
        "pass": passed,
    }


def observed_pass_lookup() -> dict[int, dict[str, bool]]:
    rows = pd.read_csv(OBSERVED_PATH)
    rows = rows[rows["target_id"].astype(str) == TARGET_ID].copy()
    rows["event_conditioned_local_gate"] = rows["event_conditioned_local_gate"].map(bool_from_csv)
    rows["ob"] = pd.to_numeric(rows["ob"], errors="coerce").astype("Int64")
    rows["k"] = pd.to_numeric(rows["k"], errors="coerce").astype("Int64")
    out: dict[int, dict[str, bool]] = {}
    for ob, d in rows.groupby("ob", sort=True):
        k8 = bool(d[(d["k"] == 8) & (d["event_conditioned_local_gate"])].shape[0])
        k10 = bool(d[(d["k"] == 10) & (d["event_conditioned_local_gate"])].shape[0])
        out[int(ob)] = {
            "observed_k8_pass": k8,
            "observed_k10_pass": k10,
            "observed_both_pass": k8 and k10,
            "observed_any_pass": k8 or k10,
        }
    return out


def build_contexts(
    events: pd.DataFrame,
    data_dir: Path,
    b3_arrays: dict[tuple[int, str], dict[str, np.ndarray]],
    k_values: list[int],
    lag_sec: float,
    frame_stride: int,
    max_focals: int,
    force_cache: bool,
) -> dict[int, dict[str, Any]]:
    contexts: dict[int, dict[str, Any]] = {}
    for ob, events_ob in events.groupby("ob", sort=True):
        ob_int = int(ob)
        dataset = str(events_ob["dataset"].iloc[0])
        local_by_k: dict[int, dict[tuple[int, str], dict[str, np.ndarray]]] = {}
        time_axis: np.ndarray | None = None
        for k in k_values:
            frame = load_or_build_local_frame(
                ob_int,
                dataset,
                data_dir,
                k,
                lag_sec,
                frame_stride,
                max_focals,
                force_cache,
            )
            arrays = r4081.build_arrays(frame)
            local_by_k[k] = arrays
            if time_axis is None:
                time_axis = frame["t"].to_numpy(dtype="float64")
        b3_key = (ob_int, dataset)
        if b3_key not in b3_arrays:
            raise KeyError(f"Missing B3 array for {b3_key}")
        contexts[ob_int] = {
            "ob": ob_int,
            "dataset": dataset,
            "events": events_ob.sort_values("event_t").reset_index(drop=True),
            "time_axis": np.asarray(time_axis, dtype="float64"),
            "local_by_k": local_by_k,
            "b3_arrays": {b3_key: b3_arrays[b3_key]},
        }
    return contexts


def parse_obs(arg: str, events: pd.DataFrame) -> list[int]:
    if arg.lower() in {"all", "1-19"}:
        return sorted(int(x) for x in events["ob"].dropna().unique())
    if "-" in arg and "," not in arg:
        a, b = arg.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in arg.split(",") if x.strip()]


def write_cache_manifest(contexts: dict[int, dict[str, Any]], args: argparse.Namespace) -> None:
    rows = []
    for ob, ctx in sorted(contexts.items()):
        for k in [8, 10]:
            path = local_cache_path(ob, k, args.lag, args.frame_stride, args.max_focals_per_frame)
            rows.append(
                {
                    "ob": ob,
                    "dataset": ctx["dataset"],
                    "k": k,
                    "cache_path": rel(path),
                    "exists": path.exists(),
                    "bytes": path.stat().st_size if path.exists() else 0,
                }
            )
    write_csv(OUT / "cache_manifest.csv", rows, ["ob", "dataset", "k", "cache_path", "exists", "bytes"])
    write_csv(OUT / "tables" / "cache_manifest.csv", rows, ["ob", "dataset", "k", "cache_path", "exists", "bytes"])


def run_replicates(
    contexts: dict[int, dict[str, Any]],
    n_null: int,
    n_controls: int,
    prepost_sec: float,
    exclusion_sec: float,
    k_values: list[int],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    aggregate_rows: list[dict[str, Any]] = []
    ob_pass_rows: list[dict[str, Any]] = []
    rng = np.random.default_rng(RNG_SEED)
    for rep in range(1, n_null + 1):
        if rep == 1 or rep % max(1, n_null // 10) == 0 or rep == n_null:
            print(f"[4141] null replicate {rep}/{n_null}", flush=True)
        n_both = 0
        n_any = 0
        valid_b3 = 0
        valid_k = {k: 0 for k in k_values}
        for ob in sorted(contexts):
            ctx = contexts[ob]
            events_ob = ctx["events"]
            true_times = pd.to_numeric(events_ob["event_t"], errors="coerce").to_numpy(dtype="float64")
            pseudo = sample_like_events(
                events_ob,
                ctx["time_axis"],
                rng,
                prepost_sec,
                exclusion_sec,
                avoid_times=true_times,
                event_id_offset=rep * 1_000_000 + ob * 10_000,
            )
            avoid_control = np.r_[true_times, pseudo["event_t"].to_numpy(dtype="float64")]
            controls = [
                sample_like_events(
                    events_ob,
                    ctx["time_axis"],
                    rng,
                    prepost_sec,
                    exclusion_sec,
                    avoid_times=avoid_control,
                    event_id_offset=rep * 1_000_000 + ob * 10_000 + (c + 1) * 100,
                )
                for c in range(n_controls)
            ]

            b3_rec = next(iter(ctx["b3_arrays"].values()))
            _, b3_abs = direction_abs_from_record(b3_rec, pseudo, B3_VARIABLE, prepost_sec)
            if math.isfinite(b3_abs):
                valid_b3 += 1

            row: dict[str, Any] = {
                "replicate": rep,
                "ob": ob,
                "dataset": ctx["dataset"],
                "n_events": int(len(events_ob)),
                "b3_event_direction_abs_z": b3_abs,
            }
            any_pass = False
            both_pass = True
            for k in k_values:
                local_rec = next(iter(ctx["local_by_k"][k].values()))
                _, local_abs = direction_abs_from_record(local_rec, pseudo, LOCAL_VARIABLE, prepost_sec)
                if math.isfinite(local_abs):
                    valid_k[k] += 1
                control_abs = [
                    direction_abs_from_record(local_rec, c_events, LOCAL_VARIABLE, prepost_sec)[1]
                    for c_events in controls
                ]
                gv = gate_values(local_abs, control_abs, b3_abs)
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
            ob_pass_rows.append(row)
        aggregate_rows.append(
            {
                "replicate": rep,
                "n_both": n_both,
                "n_any": n_any,
                "n_obs_tested": len(contexts),
                "n_obs_with_valid_b3": valid_b3,
                "n_obs_with_valid_k8": valid_k.get(8, 0),
                "n_obs_with_valid_k10": valid_k.get(10, 0),
            }
        )
    return aggregate_rows, ob_pass_rows


def distribution_rows(values: np.ndarray, value_name: str) -> list[dict[str, Any]]:
    rows = []
    vals, counts = np.unique(values.astype(int), return_counts=True)
    total = int(np.sum(counts))
    for val, count in zip(vals, counts):
        rows.append({value_name: int(val), "count": int(count), "fraction": float(count / total) if total else math.nan})
    return rows


def summarize_results(
    aggregate: pd.DataFrame,
    ob_pass: pd.DataFrame,
    observed_lookup: dict[int, dict[str, bool]],
    n_null: int,
    n_controls: int,
    smoke: bool,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    n_both = pd.to_numeric(aggregate["n_both"], errors="coerce").to_numpy(dtype="float64")
    n_any = pd.to_numeric(aggregate["n_any"], errors="coerce").to_numpy(dtype="float64")
    p_both = float((1 + np.sum(n_both >= OBSERVED_N_BOTH)) / (len(n_both) + 1))
    p_any = float((1 + np.sum(n_any >= OBSERVED_N_ANY)) / (len(n_any) + 1))

    pass_rates: list[dict[str, Any]] = []
    for ob, d in ob_pass.groupby("ob", sort=True):
        obs = observed_lookup.get(int(ob), {})
        pass_rates.append(
            {
                "ob": int(ob),
                "dataset": str(d["dataset"].iloc[0]),
                "n_replicates": int(d["replicate"].nunique()),
                "null_pass_rate_k8": float(d["k8_pass"].astype(bool).mean()),
                "null_pass_rate_k10": float(d["k10_pass"].astype(bool).mean()),
                "null_pass_rate_both": float(d["both_pass"].astype(bool).mean()),
                "null_pass_rate_any": float(d["any_pass"].astype(bool).mean()),
                "observed_k8_pass": bool(obs.get("observed_k8_pass", False)),
                "observed_k10_pass": bool(obs.get("observed_k10_pass", False)),
                "observed_both_pass": bool(obs.get("observed_both_pass", False)),
                "observed_any_pass": bool(obs.get("observed_any_pass", False)),
            }
        )

    stats = {
        "n_null_replicates": int(len(n_both)),
        "n_controls_per_replicate_observation": int(n_controls),
        "smoke_only": bool(smoke),
        "observed_n_both": OBSERVED_N_BOTH,
        "observed_n_any": OBSERVED_N_ANY,
        "p_omnibus_both_ge_14": p_both,
        "p_omnibus_any_ge_15": p_any,
        "n_both_null_mean": float(np.nanmean(n_both)),
        "n_both_null_median": finite_median(n_both),
        "n_both_null_q90": finite_quantile(n_both, 0.90),
        "n_both_null_q95": finite_quantile(n_both, 0.95),
        "n_both_null_q99": finite_quantile(n_both, 0.99),
        "n_both_null_max": float(np.nanmax(n_both)),
        "n_any_null_mean": float(np.nanmean(n_any)),
        "n_any_null_median": finite_median(n_any),
        "n_any_null_q90": finite_quantile(n_any, 0.90),
        "n_any_null_q95": finite_quantile(n_any, 0.95),
        "n_any_null_q99": finite_quantile(n_any, 0.99),
        "n_any_null_max": float(np.nanmax(n_any)),
    }

    if smoke:
        gate_result = "smoke_complete_do_not_use_for_manuscript_p_value"
        consequence = "Use this run to validate runtime and output structure; run B>=1000 before manuscript inference."
    elif p_both <= 0.01:
        gate_result = "strong_pass_omnibus_null"
        consequence = "Observed 14/19 both-scale count is rare under the complete null pipeline."
    elif p_both <= 0.05:
        gate_result = "pass_omnibus_null"
        consequence = "Observed 14/19 both-scale count is unlikely under the complete null pipeline."
    elif p_both <= 0.10:
        gate_result = "boundary_omnibus_null"
        consequence = "Soften all-observation significance language; descriptive survival may remain."
    else:
        gate_result = "fail_omnibus_null"
        consequence = "Do not claim 14/19 is globally surprising; retain only common descriptive survival if other gates remain valid."

    decision = {
        "node": NODE,
        "date": DATE,
        "purpose": "Calibrate the observed both-scale T1 survival count against a full pseudo-event pipeline null.",
        "analysis_scope": "all_19_observations",
        "primary_metrics": stats,
        "nulls": [
            "same_observation_pseudo_event_times_avoiding_true_transition_windows",
            "same_observation_non_event_controls_preserving_event_type_counts",
        ],
        "predefined_thresholds": {
            "local_event_minus_non_event_direction_z": "> 0.03",
            "p_non_event_direction_ge_event": "<= 0.35",
            "local_to_b3_direction_ratio": ">= 0.30",
            "strong_pass": "p_both <= 0.01",
            "pass": "0.01 < p_both <= 0.05",
            "boundary": "0.05 < p_both <= 0.10",
            "fail": "p_both > 0.10",
        },
        "main_result": {
            "gate_result": gate_result,
            "manuscript_consequence": consequence,
        },
        "observation_heterogeneity": {
            "max_null_both_pass_rate": max((safe_float(r["null_pass_rate_both"]) for r in pass_rates), default=math.nan),
            "max_null_any_pass_rate": max((safe_float(r["null_pass_rate_any"]) for r in pass_rates), default=math.nan),
        },
        "does_not_prove": [
            "mechanism",
            "prediction",
            "universal T1 law",
            "detrending robustness",
            "affine-fit conditioning robustness",
        ],
        "next": ["4141_full_B_ge_1000" if smoke else "4142_detrending_challenge"],
    }
    return stats, pass_rates, decision


def make_figures(aggregate: pd.DataFrame, pass_rates: pd.DataFrame, stats: dict[str, Any], smoke: bool) -> None:
    suffix = "_smoke" if smoke else ""
    plt.style.use("default")

    fig, ax = plt.subplots(figsize=(6.5, 4.0))
    vals = pd.to_numeric(aggregate["n_both"], errors="coerce").dropna().astype(int)
    bins = np.arange(vals.min() - 0.5, max(vals.max(), OBSERVED_N_BOTH) + 1.5, 1)
    ax.hist(vals, bins=bins, color="#5b8db8", edgecolor="white")
    ax.axvline(OBSERVED_N_BOTH, color="#b84a4a", linewidth=2, label=f"observed {OBSERVED_N_BOTH}")
    ax.set_xlabel("null both-scale survivor count")
    ax.set_ylabel("replicates")
    title = "4141 smoke null: N_both" if smoke else "4141 omnibus null: N_both"
    ax.set_title(title)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / f"4141_N_both_distribution{suffix}.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.5, 4.0))
    vals = pd.to_numeric(aggregate["n_any"], errors="coerce").dropna().astype(int)
    bins = np.arange(vals.min() - 0.5, max(vals.max(), OBSERVED_N_ANY) + 1.5, 1)
    ax.hist(vals, bins=bins, color="#6c9a5b", edgecolor="white")
    ax.axvline(OBSERVED_N_ANY, color="#b84a4a", linewidth=2, label=f"observed {OBSERVED_N_ANY}")
    ax.set_xlabel("null any-scale survivor count")
    ax.set_ylabel("replicates")
    title = "4141 smoke null: N_any" if smoke else "4141 omnibus null: N_any"
    ax.set_title(title)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / f"4141_N_any_distribution{suffix}.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    d = pass_rates.sort_values("ob")
    x = np.arange(len(d))
    ax.bar(x - 0.18, d["null_pass_rate_k8"], width=0.18, color="#5b8db8", label="k=8")
    ax.bar(x, d["null_pass_rate_k10"], width=0.18, color="#9b6a9e", label="k=10")
    ax.bar(x + 0.18, d["null_pass_rate_both"], width=0.18, color="#555555", label="both")
    ax.set_xticks(x)
    ax.set_xticklabels([f"Ob{int(v)}" for v in d["ob"]], rotation=60, ha="right", fontsize=8)
    ax.set_ylabel("null pass rate")
    ax.set_ylim(0, min(1.0, max(0.05, float(d[["null_pass_rate_k8", "null_pass_rate_k10", "null_pass_rate_both"]].max().max()) * 1.25)))
    ax.set_title("Observation-wise null pass rates")
    ax.legend(frameon=False, ncols=3, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / f"4141_observation_null_pass_rates{suffix}.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(5.8, 4.0))
    d = pass_rates.copy()
    d["observed_class"] = np.where(d["observed_both_pass"], "observed both", np.where(d["observed_any_pass"], "observed one", "observed no"))
    classes = ["observed no", "observed one", "observed both"]
    values = [float(d.loc[d["observed_class"] == c, "null_pass_rate_both"].mean()) if (d["observed_class"] == c).any() else math.nan for c in classes]
    ax.bar(classes, values, color=["#777777", "#c49a4a", "#5b8db8"])
    ax.set_ylabel("mean null both-pass rate")
    ax.set_title("Observed class vs null permissiveness")
    fig.tight_layout()
    fig.savefig(FIG / f"4141_observed_class_vs_null_pass{suffix}.png", dpi=180)
    plt.close(fig)


def write_outputs(
    aggregate_rows: list[dict[str, Any]],
    ob_pass_rows: list[dict[str, Any]],
    pass_rates: list[dict[str, Any]],
    stats: dict[str, Any],
    decision: dict[str, Any],
    args: argparse.Namespace,
) -> None:
    aggregate = pd.DataFrame(aggregate_rows)
    ob_pass = pd.DataFrame(ob_pass_rows)
    pass_rates_df = pd.DataFrame(pass_rates, columns=PASS_RATE_COLUMNS)
    smoke = bool(args.smoke)

    write_csv(OUT / "omnibus_replicates.csv", aggregate_rows, REPLICATE_COLUMNS)
    write_csv(OUT / "tables" / "omnibus_replicates.csv", aggregate_rows, REPLICATE_COLUMNS)
    write_csv(OUT / "observation_replicate_passes.csv", ob_pass_rows, OBS_PASS_COLUMNS)
    write_csv(OUT / "tables" / "observation_replicate_passes.csv", ob_pass_rows, OBS_PASS_COLUMNS)
    write_csv(OUT / "observation_null_pass_rates.csv", pass_rates, PASS_RATE_COLUMNS)
    write_csv(OUT / "tables" / "observation_null_pass_rates.csv", pass_rates, PASS_RATE_COLUMNS)
    write_csv(
        OUT / "N_both_distribution.csv",
        distribution_rows(pd.to_numeric(aggregate["n_both"], errors="coerce").dropna().to_numpy(dtype="float64"), "n_both"),
        ["n_both", "count", "fraction"],
    )
    write_csv(
        OUT / "N_any_distribution.csv",
        distribution_rows(pd.to_numeric(aggregate["n_any"], errors="coerce").dropna().to_numpy(dtype="float64"), "n_any"),
        ["n_any", "count", "fraction"],
    )
    write_json(OUT / "p_omnibus.json", stats)
    write_json(OUT / "decision.json", decision)

    config = f"""node: {NODE}
date: {DATE}
input_contract: {rel(CONTRACT_PATH)}
analysis_scope: all_19_observations
mode: {"smoke" if smoke else "full"}
n_null_replicates: {args.n_null}
n_controls_per_replicate_observation: {args.n_controls}
k_values: {args.k}
lag_sec: {args.lag}
frame_stride: {args.frame_stride}
max_focals_per_frame: {args.max_focals_per_frame}
prepost_sec: {args.prepost_sec}
exclusion_sec: {args.exclusion_sec}
observed_n_both: {OBSERVED_N_BOTH}
observed_n_any: {OBSERVED_N_ANY}
survival_gate:
  local_event_minus_non_event_direction_z: "> {GAP_GATE}"
  p_non_event_direction_ge_event: "<= {P_GATE}"
  local_to_b3_direction_ratio: ">= {RATIO_GATE}"
null_design:
  pseudo_events: same_observation_uniform_times_avoiding_true_transition_windows
  controls: same_observation_uniform_times_avoiding_true_and_pseudo_event_windows
  event_type_counts: preserved_from_real_events
"""
    (OUT / "omnibus_null_config.yaml").write_text(config, encoding="utf-8")

    make_figures(aggregate, pass_rates_df, stats, smoke)

    summary = dedent(
        f"""\
        # Node 4141 Summary

        ## Purpose

        Estimate how unusual the observed all-observation T1 survival count is
        under a full pseudo-event event/control pipeline.

        ## Frozen Inputs

        - Contract: `Output/4140/frozen_analysis_contract.yaml`
        - Events: `Output/3045/tables/transition_events.csv`
        - B3 residual frame: `Output/4002A/processed/frame_residual_spatial_metrics.csv`
        - Local T1 definition: `Experiment/run_4081_global_vs_local_geometry_ladder.py`
        - Observed support: `Output/4081c/full_geometry_ladder_rows.csv`

        ## Exact Analysis Performed

        ```text
        mode = {"smoke" if smoke else "full"}
        null replicates = {args.n_null}
        controls per observation per replicate = {args.n_controls}
        observations = all 19
        k values = {args.k}
        lag = {args.lag}
        ```

        For each null replicate and observation, pseudo-event centers were
        sampled within the same observation while avoiding true transition
        windows. The same pseudo-event centers were used for k=8 and k=10 so
        that cross-scale dependence was preserved. Non-event controls preserved
        the same event-type counts and avoided true and pseudo-event windows.

        ## Primary Result

        ```text
        observed N_both = {OBSERVED_N_BOTH}
        observed N_any  = {OBSERVED_N_ANY}
        null N_both mean = {stats["n_both_null_mean"]:.4g}
        null N_both median = {stats["n_both_null_median"]:.4g}
        null N_both q95 = {stats["n_both_null_q95"]:.4g}
        null N_both max = {stats["n_both_null_max"]:.4g}
        p_both_ge_14 = {stats["p_omnibus_both_ge_14"]:.4g}
        p_any_ge_15 = {stats["p_omnibus_any_ge_15"]:.4g}
        ```

        ## Observation-Level Result

        {md_table(pass_rates, PASS_RATE_COLUMNS)}

        ## Gate Evaluation

        `{decision["main_result"]["gate_result"]}`

        {decision["main_result"]["manuscript_consequence"]}

        ## What This Strengthens

        It tests the reviewer-defense question: whether a high all-observation
        survival count appears often when the whole per-observation gate is run
        on non-transition pseudo-events.

        ## What This Weakens

        If this is a smoke run, the empirical p-value is not manuscript-ready.
        It is only a runtime and pipeline validation.

        ## What This Does NOT Prove

        {md_table([{"does_not_prove": x} for x in decision["does_not_prove"]], ["does_not_prove"])}

        ## Decision

        `{decision["main_result"]["gate_result"]}`

        ## Next

        {md_table([{"next": x} for x in decision["next"]], ["next"])}

        ## Artifacts

        - `Output/4141/omnibus_null_config.yaml`
        - `Output/4141/omnibus_replicates.csv`
        - `Output/4141/observation_replicate_passes.csv`
        - `Output/4141/N_both_distribution.csv`
        - `Output/4141/N_any_distribution.csv`
        - `Output/4141/observation_null_pass_rates.csv`
        - `Output/4141/p_omnibus.json`
        - `Output/4141/figures/`
        - `Output/4141/decision.json`
        """
    ).lstrip()
    (OUT / "4141_summary.md").write_text(summary, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default=BaseRunConfig.data_dir)
    parser.add_argument("--obs", default="all", help="Use all for inference; subsets are allowed only with --cache-only.")
    parser.add_argument("--n-null", type=int, default=100)
    parser.add_argument("--n-controls", type=int, default=40)
    parser.add_argument("--k", default="8,10")
    parser.add_argument("--lag", type=float, default=0.10)
    parser.add_argument("--frame-stride", type=int, default=2)
    parser.add_argument("--max-focals-per-frame", type=int, default=24)
    parser.add_argument("--prepost-sec", type=float, default=0.20)
    parser.add_argument("--exclusion-sec", type=float, default=0.80)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--cache-only", action="store_true")
    parser.add_argument("--force-cache", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_dirs()
    if not CONTRACT_PATH.exists():
        raise FileNotFoundError("Run 4140 first; missing Output/4140/frozen_analysis_contract.yaml")
    data_dir = resolve_data_dir(BaseRunConfig(data_dir=args.data_dir))
    k_values = [int(x.strip()) for x in args.k.split(",") if x.strip()]
    if k_values != [8, 10]:
        raise ValueError("4141 manuscript hardening is frozen to k=8,10.")
    events_all = read_events()
    requested_obs = parse_obs(args.obs, events_all)
    all_obs = sorted(int(x) for x in events_all["ob"].dropna().unique())
    if not args.cache_only and requested_obs != all_obs:
        raise ValueError("4141 inference requires all observations. Use --cache-only for subset cache building.")
    events = events_all[events_all["ob"].isin(requested_obs)].copy().reset_index(drop=True)
    b3_arrays = read_b3_arrays()
    contexts = build_contexts(
        events,
        data_dir,
        b3_arrays,
        k_values=k_values,
        lag_sec=args.lag,
        frame_stride=args.frame_stride,
        max_focals=args.max_focals_per_frame,
        force_cache=args.force_cache,
    )
    write_cache_manifest(contexts, args)
    if args.cache_only:
        partial = {
            "node": NODE,
            "date": DATE,
            "status": "cache_only_complete",
            "observations": requested_obs,
            "message": "Local T1 caches were built or verified. No omnibus null inference was run.",
            "next": ["run all-observation smoke with --smoke --n-null 100 after all caches exist"],
        }
        write_json(OUT / "cache_only_decision.json", partial)
        print(json.dumps(partial, ensure_ascii=False, indent=2), flush=True)
        print(f"Wrote 4141 cache manifest to {rel(OUT / 'cache_manifest.csv')}", flush=True)
        return 0
    aggregate_rows, ob_pass_rows = run_replicates(
        contexts,
        n_null=args.n_null,
        n_controls=args.n_controls,
        prepost_sec=args.prepost_sec,
        exclusion_sec=args.exclusion_sec,
        k_values=k_values,
    )
    aggregate = pd.DataFrame(aggregate_rows)
    ob_pass = pd.DataFrame(ob_pass_rows)
    observed = observed_pass_lookup()
    stats, pass_rates, decision = summarize_results(aggregate, ob_pass, observed, args.n_null, args.n_controls, args.smoke)
    write_outputs(aggregate_rows, ob_pass_rows, pass_rates, stats, decision, args)
    print(json.dumps(decision, ensure_ascii=False, indent=2), flush=True)
    print(f"Wrote 4141 outputs to {rel(OUT)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
