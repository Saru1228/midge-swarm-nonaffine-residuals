#!/usr/bin/env python3
"""4143 local-affine conditioning QC.

This submission-hardening node checks whether the local-affine subtraction
used by T1 is numerically defensible across all 19 observations, and whether
large local tangential residuals are concentrated in ill-conditioned local
affine fits.
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

import run_4080_local_affine_feasibility as r4080  # noqa: E402
from run_4001_geometric_baseline_residual_audit import (  # noqa: E402
    RunConfig as BaseRunConfig,
    median_dt,
    resolve_data_dir,
)


OUT = ROOT / "Output" / "4143"
FIG = OUT / "figures"
TABLES = OUT / "tables"

NODE = "4143_local_affine_conditioning_qc"
DATE = "2026-09-02"
RNG_SEED = 4143_20260902

EVENT_PATH = ROOT / "Output" / "3045" / "tables" / "transition_events.csv"

SAMPLE_COLUMNS = [
    "ob",
    "dataset",
    "t",
    "lag_sec",
    "lag_steps",
    "k",
    "focal_id",
    "n_neighbors_requested",
    "n_neighbors_retained",
    "neighbor_retention_fraction",
    "rank_eps",
    "rank_screen_pass",
    "smallest_singular_value",
    "condition_number",
    "valid_fit",
    "relative_residual_fraction",
    "d2min",
    "focal_tangential_mean",
    "focal_tangential_median",
    "nearest_event_distance_sec",
    "in_event_window",
]

SUMMARY_COLUMNS = [
    "ob",
    "dataset",
    "k",
    "lag_sec",
    "lag_steps",
    "n_attempted",
    "n_valid",
    "valid_fit_fraction",
    "rank_screen_pass_fraction",
    "median_neighbor_retention",
    "median_condition_number",
    "q90_condition_number",
    "q95_condition_number",
    "q99_condition_number",
    "max_condition_number",
    "frac_condition_gt_10",
    "frac_condition_gt_30",
    "frac_condition_gt_100",
    "median_relative_residual_fraction",
    "median_d2min",
    "median_focal_tangential_mean",
    "top5_t1_median_condition_number",
    "rest95_t1_median_condition_number",
    "top5_t1_frac_condition_gt_100",
    "spearman_log_condition_vs_log_t1",
    "event_window_fraction",
    "event_window_valid_fit_fraction",
    "event_window_median_condition_number",
    "non_event_window_median_condition_number",
    "combo_passes_qc_gate",
]


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def ensure_dirs() -> None:
    for path in (OUT, FIG, TABLES):
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
        vals = []
        for col in columns:
            val = row.get(col, "")
            if isinstance(val, float):
                vals.append("NA" if not math.isfinite(val) else f"{val:.4g}")
            else:
                vals.append(str(val).replace("\n", " ").replace("|", "\\|"))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def finite_median(values: Any) -> float:
    arr = np.asarray(values, dtype="float64")
    arr = arr[np.isfinite(arr)]
    return float(np.median(arr)) if arr.size else math.nan


def finite_quantile(values: Any, q: float) -> float:
    arr = np.asarray(values, dtype="float64")
    arr = arr[np.isfinite(arr)]
    return float(np.quantile(arr, q)) if arr.size else math.nan


def finite_mean(values: Any) -> float:
    arr = np.asarray(values, dtype="float64")
    arr = arr[np.isfinite(arr)]
    return float(np.mean(arr)) if arr.size else math.nan


def bool_from_csv(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def parse_int_list(text: str) -> list[int]:
    if text.lower() in {"all", "1-19"}:
        return list(range(1, 20))
    if "-" in text and "," not in text:
        a, b = text.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in text.split(",") if x.strip()]


def read_events() -> pd.DataFrame:
    if not EVENT_PATH.exists():
        raise FileNotFoundError(f"Missing {rel(EVENT_PATH)}")
    events = pd.read_csv(EVENT_PATH)
    for col in ["event_id", "ob", "event_t"]:
        events[col] = pd.to_numeric(events[col], errors="coerce")
    events = events.dropna(subset=["event_id", "ob", "dataset", "event_t", "event_type"]).copy()
    events["event_id"] = events["event_id"].astype("int64")
    events["ob"] = events["ob"].astype("int64")
    return events.sort_values(["ob", "event_t"], kind="mergesort").reset_index(drop=True)


def nearest_event_distance(t0: float, event_times: np.ndarray) -> float:
    event_times = np.asarray(event_times, dtype="float64")
    event_times = event_times[np.isfinite(event_times)]
    if event_times.size == 0:
        return math.nan
    return float(np.min(np.abs(event_times - t0)))


def fit_local_affine_with_t1(
    ids0: np.ndarray,
    pos0: np.ndarray,
    ids1: np.ndarray,
    pos1: np.ndarray,
    focal_id: int,
    k: int,
    lag_dt: float,
    swarm_center: np.ndarray,
) -> dict[str, Any]:
    id_to_idx0 = {int(v): i for i, v in enumerate(ids0)}
    id_to_idx1 = {int(v): i for i, v in enumerate(ids1)}
    if focal_id not in id_to_idx0 or focal_id not in id_to_idx1:
        return {
            "n_neighbors_retained": 0,
            "neighbor_retention_fraction": 0.0,
            "rank_eps": 0,
            "rank_screen_pass": False,
            "smallest_singular_value": math.nan,
            "condition_number": math.nan,
            "valid_fit": False,
            "relative_residual_fraction": math.nan,
            "d2min": math.nan,
            "focal_tangential_mean": math.nan,
            "focal_tangential_median": math.nan,
        }

    i0 = id_to_idx0[focal_id]
    i1 = id_to_idx1[focal_id]
    rel_all = pos0 - pos0[i0]
    dist = np.linalg.norm(rel_all, axis=1)
    order = np.argsort(dist)
    neigh_ids = [int(ids0[j]) for j in order if int(ids0[j]) != focal_id and int(ids0[j]) in id_to_idx1][:k]
    retained = len(neigh_ids)
    retention = retained / k if k > 0 else math.nan
    if retained < 4:
        return {
            "n_neighbors_retained": int(retained),
            "neighbor_retention_fraction": retention,
            "rank_eps": 0,
            "rank_screen_pass": False,
            "smallest_singular_value": math.nan,
            "condition_number": math.nan,
            "valid_fit": False,
            "relative_residual_fraction": math.nan,
            "d2min": math.nan,
            "focal_tangential_mean": math.nan,
            "focal_tangential_median": math.nan,
        }

    a_rows = []
    b_rows = []
    for nid in neigh_ids:
        j0 = id_to_idx0[nid]
        j1 = id_to_idx1[nid]
        r0 = pos0[j0] - pos0[i0]
        r1 = pos1[j1] - pos1[i1]
        a_rows.append(r0)
        b_rows.append(r1 - r0)
    A = np.asarray(a_rows, dtype="float64")
    B = np.asarray(b_rows, dtype="float64")
    if not (np.isfinite(A).all() and np.isfinite(B).all()):
        return {
            "n_neighbors_retained": int(retained),
            "neighbor_retention_fraction": retention,
            "rank_eps": 0,
            "rank_screen_pass": False,
            "smallest_singular_value": math.nan,
            "condition_number": math.nan,
            "valid_fit": False,
            "relative_residual_fraction": math.nan,
            "d2min": math.nan,
            "focal_tangential_mean": math.nan,
            "focal_tangential_median": math.nan,
        }

    try:
        _, singular, _ = np.linalg.svd(A, full_matrices=False)
        eps_threshold = max(A.shape) * np.finfo(float).eps * (singular[0] if singular.size else 0.0)
        rank_eps = int(np.sum(singular > eps_threshold))
        smallest = float(singular[-1]) if singular.size else math.nan
        rank_screen_pass = bool(singular.size >= 3 and smallest > 1e-12)
        cond = float(singular[0] / singular[-1]) if rank_screen_pass else math.inf
        if not rank_screen_pass:
            raise np.linalg.LinAlgError("rank screen failed")
        J, _, _, _ = np.linalg.lstsq(A, B, rcond=None)
    except np.linalg.LinAlgError:
        return {
            "n_neighbors_retained": int(retained),
            "neighbor_retention_fraction": retention,
            "rank_eps": rank_eps if "rank_eps" in locals() else 0,
            "rank_screen_pass": False,
            "smallest_singular_value": smallest if "smallest" in locals() else math.nan,
            "condition_number": cond if "cond" in locals() else math.nan,
            "valid_fit": False,
            "relative_residual_fraction": math.nan,
            "d2min": math.nan,
            "focal_tangential_mean": math.nan,
            "focal_tangential_median": math.nan,
        }

    residual = B - A @ J
    resid_vel = residual / lag_dt
    resid_ss = float(np.sum(residual * residual))
    target_ss = float(np.sum(B * B))
    rel_frac = math.sqrt(resid_ss / target_ss) if target_ss > 1e-12 else math.nan
    d2min = float(np.mean(np.sum(residual * residual, axis=1)))

    focal_rel = pos0[i0] - swarm_center
    focal_radius = float(np.linalg.norm(focal_rel))
    if math.isfinite(focal_radius) and focal_radius > 1e-12:
        radial_unit = focal_rel / focal_radius
        radial_component = resid_vel @ radial_unit
        tang_sq = np.maximum(np.sum(resid_vel * resid_vel, axis=1) - radial_component * radial_component, 0.0)
        tang = np.sqrt(tang_sq)
        focal_tangential_mean = finite_mean(tang)
        focal_tangential_median = finite_median(tang)
    else:
        focal_tangential_mean = math.nan
        focal_tangential_median = math.nan

    return {
        "n_neighbors_retained": int(retained),
        "neighbor_retention_fraction": retention,
        "rank_eps": int(rank_eps),
        "rank_screen_pass": bool(rank_screen_pass),
        "smallest_singular_value": float(smallest),
        "condition_number": float(cond),
        "valid_fit": bool(rank_screen_pass and math.isfinite(cond)),
        "relative_residual_fraction": rel_frac,
        "d2min": d2min,
        "focal_tangential_mean": focal_tangential_mean,
        "focal_tangential_median": focal_tangential_median,
    }


def sample_focals(common_ids: np.ndarray, rng: np.random.Generator, max_focals: int) -> np.ndarray:
    common_ids = np.asarray(common_ids, dtype="int64")
    if common_ids.size <= max_focals:
        return common_ids
    return rng.choice(common_ids, size=max_focals, replace=False)


def run_observation(
    *,
    ob: int,
    dataset: str,
    data_dir: Path,
    event_times: np.ndarray,
    k_values: list[int],
    lag_sec: float,
    frame_stride: int,
    max_frames: int,
    max_focals: int,
    event_window_sec: float,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rng = np.random.default_rng(RNG_SEED + ob)
    df = r4080.load_ob(ob, data_dir, dataset)
    times, frames = r4080.build_frame_index(df)
    dt = median_dt(times)
    lag_steps = max(1, int(round(lag_sec / dt))) if math.isfinite(dt) and dt > 0 else 10
    candidate_idx = np.arange(0, len(times) - lag_steps, frame_stride, dtype=int)
    if candidate_idx.size > max_frames:
        candidate_idx = np.linspace(candidate_idx[0], candidate_idx[-1], max_frames, dtype=int)
        candidate_idx = np.unique(candidate_idx)

    rows: list[dict[str, Any]] = []
    for ii, idx in enumerate(candidate_idx):
        if ii == 0 or (ii + 1) % 75 == 0 or ii + 1 == len(candidate_idx):
            print(f"[4143] Ob{ob} frame {ii + 1}/{len(candidate_idx)}", flush=True)
        t0 = float(times[idx])
        t1 = float(times[idx + lag_steps])
        ids0, pos0 = r4080.frame_arrays(frames[t0])
        ids1, pos1 = r4080.frame_arrays(frames[t1])
        id_to_idx1 = {int(v): i for i, v in enumerate(ids1)}
        common = np.asarray([int(v) for v in ids0 if int(v) in id_to_idx1], dtype="int64")
        if common.size == 0:
            continue
        focals = sample_focals(common, rng, max_focals)
        center = np.nanmean(pos0, axis=0)
        dist_to_event = nearest_event_distance(t0, event_times)
        in_event = bool(math.isfinite(dist_to_event) and dist_to_event <= event_window_sec)
        for k in k_values:
            for focal_id in focals:
                fit = fit_local_affine_with_t1(
                    ids0,
                    pos0,
                    ids1,
                    pos1,
                    int(focal_id),
                    int(k),
                    lag_steps * dt,
                    center,
                )
                rows.append(
                    {
                        "ob": int(ob),
                        "dataset": dataset,
                        "t": t0,
                        "lag_sec": float(lag_sec),
                        "lag_steps": int(lag_steps),
                        "k": int(k),
                        "focal_id": int(focal_id),
                        "n_neighbors_requested": int(k),
                        "n_neighbors_retained": fit["n_neighbors_retained"],
                        "neighbor_retention_fraction": fit["neighbor_retention_fraction"],
                        "rank_eps": fit["rank_eps"],
                        "rank_screen_pass": fit["rank_screen_pass"],
                        "smallest_singular_value": fit["smallest_singular_value"],
                        "condition_number": fit["condition_number"],
                        "valid_fit": fit["valid_fit"],
                        "relative_residual_fraction": fit["relative_residual_fraction"],
                        "d2min": fit["d2min"],
                        "focal_tangential_mean": fit["focal_tangential_mean"],
                        "focal_tangential_median": fit["focal_tangential_median"],
                        "nearest_event_distance_sec": dist_to_event,
                        "in_event_window": in_event,
                    }
                )
    meta = {
        "ob": ob,
        "dataset": dataset,
        "n_frames_total": int(len(times)),
        "n_frames_sampled": int(len(candidate_idx)),
        "median_dt": float(dt),
        "lag_steps": int(lag_steps),
        "n_rows": int(len(rows)),
    }
    return rows, meta


def spearman_corr(x: Any, y: Any) -> float:
    d = pd.DataFrame({"x": x, "y": y}).replace([np.inf, -np.inf], np.nan).dropna()
    if len(d) < 5:
        return math.nan
    return float(d["x"].rank(method="average").corr(d["y"].rank(method="average")))


def summarize_samples(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    d = pd.DataFrame(rows)
    if d.empty:
        return []
    d["valid_fit"] = d["valid_fit"].map(bool_from_csv)
    d["rank_screen_pass"] = d["rank_screen_pass"].map(bool_from_csv)
    d["in_event_window"] = d["in_event_window"].map(bool_from_csv)
    numeric_cols = [
        "condition_number",
        "neighbor_retention_fraction",
        "relative_residual_fraction",
        "d2min",
        "focal_tangential_mean",
    ]
    for col in numeric_cols:
        d[col] = pd.to_numeric(d[col], errors="coerce")
    summary: list[dict[str, Any]] = []
    for (ob, dataset, k, lag_sec, lag_steps), g in d.groupby(["ob", "dataset", "k", "lag_sec", "lag_steps"], sort=True):
        valid = g[g["valid_fit"]].copy()
        cond = valid["condition_number"].replace([np.inf, -np.inf], np.nan).dropna()
        t1 = valid["focal_tangential_mean"].replace([np.inf, -np.inf], np.nan)
        valid_t1 = valid[np.isfinite(t1)].copy()
        if not valid_t1.empty:
            cutoff = float(valid_t1["focal_tangential_mean"].quantile(0.95))
            top = valid_t1[valid_t1["focal_tangential_mean"] >= cutoff]
            rest = valid_t1[valid_t1["focal_tangential_mean"] < cutoff]
            top_cond = pd.to_numeric(top["condition_number"], errors="coerce").replace([np.inf, -np.inf], np.nan)
            rest_cond = pd.to_numeric(rest["condition_number"], errors="coerce").replace([np.inf, -np.inf], np.nan)
            log_cond = np.log10(np.maximum(valid_t1["condition_number"].to_numpy(dtype="float64"), 1e-12))
            log_t1 = np.log1p(np.maximum(valid_t1["focal_tangential_mean"].to_numpy(dtype="float64"), 0.0))
            corr = spearman_corr(log_cond, log_t1)
        else:
            top_cond = pd.Series(dtype="float64")
            rest_cond = pd.Series(dtype="float64")
            corr = math.nan

        event = g[g["in_event_window"]]
        event_valid = event[event["valid_fit"]]
        non_event_valid = g[(~g["in_event_window"]) & g["valid_fit"]]
        q95 = finite_quantile(cond, 0.95)
        frac_gt100 = float(np.mean(cond > 100.0)) if len(cond) else math.nan
        top_frac_gt100 = float(np.mean(top_cond > 100.0)) if len(top_cond) else math.nan
        combo_pass = bool(
            finite_mean(g["valid_fit"].astype(float)) >= 0.85
            and finite_mean(g["rank_screen_pass"].astype(float)) >= 0.85
            and finite_median(cond) <= 10.0
            and q95 <= 50.0
            and (math.isnan(frac_gt100) or frac_gt100 <= 0.01)
            and (math.isnan(top_frac_gt100) or top_frac_gt100 <= 0.05)
        )
        summary.append(
            {
                "ob": int(ob),
                "dataset": str(dataset),
                "k": int(k),
                "lag_sec": float(lag_sec),
                "lag_steps": int(lag_steps),
                "n_attempted": int(len(g)),
                "n_valid": int(len(valid)),
                "valid_fit_fraction": finite_mean(g["valid_fit"].astype(float)),
                "rank_screen_pass_fraction": finite_mean(g["rank_screen_pass"].astype(float)),
                "median_neighbor_retention": finite_median(g["neighbor_retention_fraction"]),
                "median_condition_number": finite_median(cond),
                "q90_condition_number": finite_quantile(cond, 0.90),
                "q95_condition_number": q95,
                "q99_condition_number": finite_quantile(cond, 0.99),
                "max_condition_number": float(np.nanmax(cond)) if len(cond) else math.nan,
                "frac_condition_gt_10": float(np.mean(cond > 10.0)) if len(cond) else math.nan,
                "frac_condition_gt_30": float(np.mean(cond > 30.0)) if len(cond) else math.nan,
                "frac_condition_gt_100": frac_gt100,
                "median_relative_residual_fraction": finite_median(valid["relative_residual_fraction"]),
                "median_d2min": finite_median(valid["d2min"]),
                "median_focal_tangential_mean": finite_median(valid["focal_tangential_mean"]),
                "top5_t1_median_condition_number": finite_median(top_cond),
                "rest95_t1_median_condition_number": finite_median(rest_cond),
                "top5_t1_frac_condition_gt_100": top_frac_gt100,
                "spearman_log_condition_vs_log_t1": corr,
                "event_window_fraction": finite_mean(g["in_event_window"].astype(float)),
                "event_window_valid_fit_fraction": finite_mean(event["valid_fit"].astype(float)) if len(event) else math.nan,
                "event_window_median_condition_number": finite_median(event_valid["condition_number"]),
                "non_event_window_median_condition_number": finite_median(non_event_valid["condition_number"]),
                "combo_passes_qc_gate": combo_pass,
            }
        )
    return summary


def overall_metrics(summary: list[dict[str, Any]]) -> dict[str, Any]:
    d = pd.DataFrame(summary)
    if d.empty:
        return {}
    d["combo_passes_qc_gate"] = d["combo_passes_qc_gate"].map(bool_from_csv)
    for col in SUMMARY_COLUMNS:
        if col not in {"ob", "dataset", "combo_passes_qc_gate"}:
            d[col] = pd.to_numeric(d[col], errors="coerce")
    per_ob = d.groupby("ob")["combo_passes_qc_gate"].all()
    return {
        "n_ob_k_combos": int(len(d)),
        "n_combo_passes": int(d["combo_passes_qc_gate"].sum()),
        "n_observations": int(d["ob"].nunique()),
        "n_observations_all_k_pass": int(per_ob.sum()),
        "median_valid_fit_fraction": finite_median(d["valid_fit_fraction"]),
        "min_valid_fit_fraction": float(d["valid_fit_fraction"].min()),
        "median_condition_number_over_combos": finite_median(d["median_condition_number"]),
        "max_combo_q95_condition_number": float(d["q95_condition_number"].max()),
        "max_combo_frac_condition_gt_100": float(d["frac_condition_gt_100"].max()),
        "median_top5_t1_condition_number": finite_median(d["top5_t1_median_condition_number"]),
        "max_top5_t1_frac_condition_gt_100": float(d["top5_t1_frac_condition_gt_100"].max()),
        "median_spearman_log_condition_vs_log_t1": finite_median(d["spearman_log_condition_vs_log_t1"]),
        "max_abs_spearman_log_condition_vs_log_t1": float(np.nanmax(np.abs(d["spearman_log_condition_vs_log_t1"]))),
    }


def decide(summary: list[dict[str, Any]], meta: list[dict[str, Any]]) -> dict[str, Any]:
    metrics = overall_metrics(summary)
    n_combo = int(metrics.get("n_ob_k_combos", 0))
    n_pass = int(metrics.get("n_combo_passes", 0))
    n_ob_all = int(metrics.get("n_observations_all_k_pass", 0))
    max_frac_gt100 = float(metrics.get("max_combo_frac_condition_gt_100", math.nan))
    max_top_frac_gt100 = float(metrics.get("max_top5_t1_frac_condition_gt_100", math.nan))
    median_corr = float(metrics.get("median_spearman_log_condition_vs_log_t1", math.nan))

    if n_combo and n_pass >= 34 and n_ob_all >= 16 and max_frac_gt100 <= 0.01 and max_top_frac_gt100 <= 0.05:
        gate_result = "pass_local_affine_conditioning_qc"
        interpretation = (
            "Local affine fits are broadly rank-sufficient and well-conditioned; "
            "large T1 samples are not concentrated in severely ill-conditioned fits."
        )
        next_nodes = ["4144_definition_notation_figure_cleanup"]
    elif n_combo and n_pass >= 28:
        gate_result = "boundary_local_affine_conditioning_mostly_ok_with_observation_exceptions"
        interpretation = (
            "Most local affine fits are numerically defensible, but some observation/k "
            "exceptions should be reported or checked before manuscript reintegration."
        )
        next_nodes = ["4143_exception_audit", "4144_definition_notation_figure_cleanup"]
    else:
        gate_result = "fail_local_affine_conditioning_qc"
        interpretation = (
            "The local affine fit QC is not strong enough for the current T1 wording; "
            "revise the claim boundary before manuscript reintegration."
        )
        next_nodes = ["revise_T1_local_affine_claim_boundary"]

    return {
        "node": NODE,
        "date": DATE,
        "question": "Are local affine fits rank-sufficient and well-conditioned, and are high T1 values driven by ill-conditioned fits?",
        "gate_result": gate_result,
        "interpretation": interpretation,
        "primary_metrics": metrics,
        "sampling_meta": meta,
        "gate": {
            "combo_pass": [
                "valid_fit_fraction >= 0.85",
                "rank_screen_pass_fraction >= 0.85",
                "median_condition_number <= 10",
                "q95_condition_number <= 50",
                "frac_condition_gt_100 <= 0.01",
                "top5_t1_frac_condition_gt_100 <= 0.05",
            ],
            "overall_pass": "at least 34/38 ob-k combos and at least 16/19 observations pass both k values",
        },
        "does_not_prove": [
            "biological mechanism",
            "correctness of the T1 phenomenon by itself",
            "formal 4141 p-value",
            "detrending robustness",
            "absence of all preprocessing artifacts",
        ],
        "next": next_nodes,
        "diagnostic_notes": {
            "median_spearman_log_condition_vs_log_t1": median_corr,
            "max_combo_frac_condition_gt_100": max_frac_gt100,
            "max_top5_t1_frac_condition_gt_100": max_top_frac_gt100,
        },
    }


def make_figures(summary: pd.DataFrame) -> None:
    if summary.empty:
        return
    d = summary.sort_values(["ob", "k"]).copy()
    fig, ax = plt.subplots(figsize=(8.6, 4.6), constrained_layout=True)
    for k, color, dx in [(8, "#4c78a8", -0.17), (10, "#9b6a9e", 0.17)]:
        sub = d[d["k"] == k]
        x = np.arange(len(sub)) + dx
        ax.bar(x, sub["q95_condition_number"], width=0.32, color=color, label=f"k={k}")
    ax.axhline(50, color="#333333", linestyle="--", linewidth=1.0, label="q95 gate")
    obs = sorted(d["ob"].unique())
    ax.set_xticks(np.arange(len(obs)))
    ax.set_xticklabels([f"Ob{int(ob)}" for ob in obs], rotation=60, ha="right", fontsize=8)
    ax.set_ylabel("q95 condition number")
    ax.set_title("4143 local affine conditioning by observation")
    ax.legend(frameon=False, fontsize=8, ncols=3)
    fig.savefig(FIG / "4143_q95_condition_by_observation.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.0, 4.5), constrained_layout=True)
    ax.scatter(
        summary["median_condition_number"],
        summary["median_focal_tangential_mean"],
        c=summary["k"].map({8: "#4c78a8", 10: "#9b6a9e"}),
        s=48,
        alpha=0.9,
        edgecolor="white",
        linewidth=0.6,
    )
    ax.set_xlabel("median condition number")
    ax.set_ylabel("median focal tangential residual")
    ax.set_title("4143 median T1 vs median conditioning")
    ax.grid(color="#dddddd", linewidth=0.7)
    fig.savefig(FIG / "4143_median_t1_vs_condition.png", dpi=180)
    plt.close(fig)


def write_config(args: argparse.Namespace, obs: list[int], data_dir: Path) -> None:
    text = dedent(
        f"""\
        node: {NODE}
        date: {DATE}
        node_type: submission_hardening_numerical_qc
        data_dir: {data_dir}
        events: Output/3045/tables/transition_events.csv
        observations: {obs}
        k_values: {args.k}
        lag_sec: {args.lag}
        frame_stride: {args.frame_stride}
        max_frames_per_observation: {args.max_frames}
        max_focals_per_frame: {args.max_focals_per_frame}
        event_window_sec: {args.event_window_sec}
        """
    )
    (OUT / "config.yaml").write_text(text, encoding="utf-8")


def write_summary(decision: dict[str, Any], summary: list[dict[str, Any]]) -> None:
    compact_cols = [
        "ob",
        "k",
        "valid_fit_fraction",
        "median_condition_number",
        "q95_condition_number",
        "frac_condition_gt_100",
        "top5_t1_median_condition_number",
        "top5_t1_frac_condition_gt_100",
        "spearman_log_condition_vs_log_t1",
        "combo_passes_qc_gate",
    ]
    text = f"""# Node 4143 Summary

## Question

Are the local affine fits used in T1 rank-sufficient and well-conditioned across
all 19 observations, and are high T1 values mainly produced by ill-conditioned
fits?

## Method

The node samples raw trajectory frames from each observation, fits the same
local affine model used by the 4081 T1 definition, and records per-focal fit
quality:

```text
k = 8, 10
lag = 0.10 sec
max frames per observation = sampled, not exhaustive
max focals per frame = sampled, not exhaustive
```

The QC table reports rank-screen pass rate, valid-fit fraction, condition
number quantiles, and whether the top 5% of focal T1 samples are concentrated
in condition number > 100 fits.

## Overall Decision

`{decision["gate_result"]}`

{decision["interpretation"]}

## Primary Metrics

{md_table([decision["primary_metrics"]], list(decision["primary_metrics"].keys()))}

## Compact Observation/K Summary

{md_table(summary, compact_cols)}

## Boundary

This node tests numerical conditioning of local affine subtraction only. It
does not prove a biological mechanism and does not replace the detrending or
omnibus-null checks.

## Next

{md_table([{"next": x} for x in decision["next"]], ["next"])}

## Artifacts

- `Output/4143/local_affine_conditioning_samples.csv`
- `Output/4143/local_affine_conditioning_summary.csv`
- `Output/4143/decision.json`
- `Output/4143/figures/4143_q95_condition_by_observation.png`
- `Output/4143/figures/4143_median_t1_vs_condition.png`
"""
    (OUT / "4143_summary.md").write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--obs", default="all")
    parser.add_argument("--data-dir", default=BaseRunConfig.data_dir)
    parser.add_argument("--k", default="8,10")
    parser.add_argument("--lag", type=float, default=0.10)
    parser.add_argument("--frame-stride", type=int, default=20)
    parser.add_argument("--max-frames", type=int, default=300)
    parser.add_argument("--max-focals-per-frame", type=int, default=24)
    parser.add_argument("--event-window-sec", type=float, default=0.20)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_dirs()
    obs = parse_int_list(args.obs)
    k_values = parse_int_list(args.k)
    data_dir = resolve_data_dir(BaseRunConfig(data_dir=args.data_dir))
    events = read_events()
    write_config(args, obs, data_dir)

    all_rows: list[dict[str, Any]] = []
    meta: list[dict[str, Any]] = []
    for ob in obs:
        events_ob = events[events["ob"].eq(ob)].copy()
        if events_ob.empty:
            raise RuntimeError(f"No transition events for Ob{ob}")
        dataset = str(events_ob["dataset"].iloc[0])
        event_times = pd.to_numeric(events_ob["event_t"], errors="coerce").to_numpy(dtype="float64")
        print(f"[4143] loading Ob{ob} ({dataset})", flush=True)
        rows, ob_meta = run_observation(
            ob=ob,
            dataset=dataset,
            data_dir=data_dir,
            event_times=event_times,
            k_values=k_values,
            lag_sec=args.lag,
            frame_stride=args.frame_stride,
            max_frames=args.max_frames,
            max_focals=args.max_focals_per_frame,
            event_window_sec=args.event_window_sec,
        )
        all_rows.extend(rows)
        meta.append(ob_meta)

    summary = summarize_samples(all_rows)
    write_csv(OUT / "local_affine_conditioning_samples.csv", all_rows, SAMPLE_COLUMNS)
    write_csv(TABLES / "local_affine_conditioning_samples.csv", all_rows, SAMPLE_COLUMNS)
    write_csv(OUT / "local_affine_conditioning_summary.csv", summary, SUMMARY_COLUMNS)
    write_csv(TABLES / "local_affine_conditioning_summary.csv", summary, SUMMARY_COLUMNS)
    write_json(OUT / "local_affine_conditioning_summary.json", summary)

    summary_df = pd.DataFrame(summary)
    make_figures(summary_df)
    decision = decide(summary, meta)
    write_json(OUT / "decision.json", decision)
    write_summary(decision, summary)
    print(json.dumps(decision, ensure_ascii=False, indent=2), flush=True)
    print(f"Wrote 4143 outputs to {rel(OUT)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
