"""4100A spatial-unit / overlap audit for transient non-affine route.

This node starts the 410x route after 4094. It does not test propagation.
It checks whether the 4090B vector unit can be converted into one unique
focal-centered local non-affine tangential activity per frame and focal.

The primary output is a focal-centered aggregate:

    A_i(t) = median_j ||u_NA_ij,tan(t)||^2

where j runs over the local-affine neighbors of focal i. The script also audits
how much neighbor-overlap exists in the underlying representation and whether
the resulting swarm aggregate is consistent with the earlier 4084
all_tangential frame aggregate where that reference is available.
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

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_DIR = ROOT / "Experiment"
if str(EXPERIMENT_DIR) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_DIR))

import run_4081_global_vs_local_geometry_ladder as r4081  # noqa: E402
from run_4001_geometric_baseline_residual_audit import (  # noqa: E402
    RunConfig as BaseRunConfig,
    median_dt,
    read_events,
    read_raw_ob,
    resolve_data_dir,
)


OUT = ROOT / "Output" / "4100A"
NODE = "4100A_spatial_unit_overlap_audit"
DATE = "2026-08-26"
RNG_SEED = 4100_0101

SRC_4084_PER_OB = ROOT / "Output" / "4084" / "per_ob"

FOCAL_COLUMNS = [
    "ob",
    "dataset",
    "t",
    "k",
    "lag_sec",
    "lag_dt",
    "focal_id",
    "n_neighbors",
    "condition_number",
    "focal_radius",
    "kth_neighbor_distance",
    "activity_energy_median",
    "activity_energy_mean",
    "activity_tangential_norm_median",
    "activity_tangential_norm_mean",
]

QC_COLUMNS = [
    "ob",
    "dataset",
    "n_sampled_frames",
    "n_valid_frames",
    "valid_frame_fraction",
    "n_focal_activity_rows",
    "duplicate_focal_frame_rows",
    "median_focals_per_valid_frame",
    "median_condition_number",
    "median_activity_energy_median",
    "median_activity_tangential_norm_median",
    "median_neighbor_slots_per_frame",
    "median_unique_neighbors_per_frame",
    "median_neighbor_overlap_ratio",
    "median_fraction_multimembership_neighbors",
]

OVERLAP_COLUMNS = [
    "ob",
    "dataset",
    "t",
    "n_focals",
    "neighbor_slots",
    "unique_neighbors",
    "neighbor_overlap_ratio",
    "max_memberships_per_neighbor",
    "fraction_multimembership_neighbors",
]

AGG_COLUMNS = [
    "ob",
    "dataset",
    "t",
    "n_focals",
    "A_swarm_energy_median",
    "A_swarm_energy_mean",
    "A_swarm_tangential_median",
    "A_swarm_tangential_mean",
    "A_swarm_tangential_z",
]

REPRO_COLUMNS = [
    "ob",
    "dataset",
    "n_events",
    "n_controls",
    "near_pre_event_median_z",
    "near_pre_control_median_z",
    "near_pre_event_minus_control_z",
    "agg_vs_4084_pearson",
    "agg_vs_4084_spearman",
    "agg_vs_4084_n",
    "qualitative_reproduction",
]


def ensure_dirs() -> None:
    for path in (OUT, OUT / "tables", OUT / "figures", OUT / "cache"):
        path.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in columns})


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(to_jsonable(data), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def to_jsonable(obj: object) -> object:
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_jsonable(v) for v in obj]
    if isinstance(obj, tuple):
        return [to_jsonable(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        val = float(obj)
        return None if not math.isfinite(val) else val
    if isinstance(obj, float):
        return None if not math.isfinite(obj) else obj
    return obj


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


def finite_median(values: pd.Series | np.ndarray | list[float]) -> float:
    arr = np.asarray(values, dtype="float64")
    arr = arr[np.isfinite(arr)]
    return float(np.median(arr)) if arr.size else math.nan


def corr_or_nan(x: np.ndarray, y: np.ndarray, *, rank: bool = False) -> float:
    x = np.asarray(x, dtype="float64")
    y = np.asarray(y, dtype="float64")
    mask = np.isfinite(x) & np.isfinite(y)
    if int(mask.sum()) < 3:
        return math.nan
    x = x[mask]
    y = y[mask]
    if rank:
        x = pd.Series(x).rank(method="average").to_numpy(dtype="float64")
        y = pd.Series(y).rank(method="average").to_numpy(dtype="float64")
    if np.nanstd(x) <= 1e-12 or np.nanstd(y) <= 1e-12:
        return math.nan
    return float(np.corrcoef(x, y)[0, 1])


def robust_z(values: np.ndarray) -> np.ndarray:
    x = np.asarray(values, dtype="float64")
    med = np.nanmedian(x)
    mad = np.nanmedian(np.abs(x - med))
    scale = 1.4826 * mad
    if not np.isfinite(scale) or scale <= 1e-12:
        scale = np.nanstd(x)
    if not np.isfinite(scale) or scale <= 1e-12:
        return np.full(x.shape, np.nan, dtype="float64")
    return (x - med) / scale


def parse_obs(text: str, events: pd.DataFrame) -> list[int]:
    lower = text.lower()
    if lower in {"pilot", "default"}:
        return [1, 2, 6, 15]
    if lower in {"all", "1-19"}:
        return sorted(int(x) for x in events["ob"].dropna().unique())
    if "-" in text and "," not in text:
        a, b = text.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in text.split(",") if x.strip()]


def load_ob_df(ob: int, data_dir: Path, dataset: str) -> pd.DataFrame:
    path = data_dir / dataset
    if not path.exists():
        path = data_dir / f"Ob{ob}.txt"
    return read_raw_ob(path)


def frame_arrays(frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    return frame["id"].to_numpy(dtype="int64"), frame[["x", "y", "z"]].to_numpy(dtype="float64")


def focal_activity_for_frame(
    ids0: np.ndarray,
    pos0: np.ndarray,
    ids1: np.ndarray,
    pos1: np.ndarray,
    *,
    ob: int,
    dataset: str,
    t0: float,
    k: int,
    lag_sec: float,
    lag_dt: float,
    max_focals: int,
    rng: np.random.Generator,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    id_to_idx0 = {int(v): i for i, v in enumerate(ids0)}
    id_to_idx1 = {int(v): i for i, v in enumerate(ids1)}
    common = np.asarray([int(v) for v in ids0 if int(v) in id_to_idx1], dtype="int64")
    if common.size == 0:
        return [], empty_overlap_row(ob, dataset, t0)
    if common.size > max_focals:
        focals = rng.choice(common, size=max_focals, replace=False)
    else:
        focals = common

    center = np.nanmean(pos0, axis=0)
    rows: list[dict[str, object]] = []
    neighbor_memberships: dict[int, int] = {}

    for focal_id_raw in focals:
        focal_id = int(focal_id_raw)
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
        neighbor_dists = []
        for nid in neigh_ids:
            j0 = id_to_idx0[nid]
            j1 = id_to_idx1[nid]
            r0 = pos0[j0] - pos0[i0]
            r1 = pos1[j1] - pos1[i1]
            A.append(r0)
            B.append(r1 - r0)
            neighbor_dists.append(float(np.linalg.norm(r0)))
            neighbor_memberships[nid] = neighbor_memberships.get(nid, 0) + 1
        A = np.asarray(A, dtype="float64")
        B = np.asarray(B, dtype="float64")
        if not (np.isfinite(A).all() and np.isfinite(B).all()):
            continue
        try:
            _, s, _ = np.linalg.svd(A, full_matrices=False)
            if s.size < 3 or s[-1] <= 1e-12:
                continue
            condition_number = float(s[0] / s[-1]) if s[-1] > 0 else math.nan
            J, _, _, _ = np.linalg.lstsq(A, B, rcond=None)
        except np.linalg.LinAlgError:
            continue
        resid = (B - A @ J) / lag_dt
        if not np.isfinite(resid).all():
            continue
        focal_rel = pos0[i0] - center
        focal_radius = float(np.linalg.norm(focal_rel))
        if not np.isfinite(focal_radius) or focal_radius <= 1e-12:
            continue
        radial_unit = focal_rel / focal_radius
        radial_component = resid @ radial_unit
        tang_sq = np.maximum(np.sum(resid * resid, axis=1) - radial_component * radial_component, 0.0)
        tang_norm = np.sqrt(tang_sq)
        if not np.isfinite(tang_sq).any():
            continue
        rows.append(
            {
                "ob": ob,
                "dataset": dataset,
                "t": t0,
                "k": k,
                "lag_sec": lag_sec,
                "lag_dt": lag_dt,
                "focal_id": focal_id,
                "n_neighbors": len(neigh_ids),
                "condition_number": condition_number,
                "focal_radius": focal_radius,
                "kth_neighbor_distance": max(neighbor_dists) if neighbor_dists else math.nan,
                "activity_energy_median": float(np.nanmedian(tang_sq)),
                "activity_energy_mean": float(np.nanmean(tang_sq)),
                "activity_tangential_norm_median": float(np.nanmedian(tang_norm)),
                "activity_tangential_norm_mean": float(np.nanmean(tang_norm)),
            }
        )

    overlap = overlap_row(ob, dataset, t0, rows, neighbor_memberships)
    return rows, overlap


def empty_overlap_row(ob: int, dataset: str, t0: float) -> dict[str, object]:
    return {
        "ob": ob,
        "dataset": dataset,
        "t": t0,
        "n_focals": 0,
        "neighbor_slots": 0,
        "unique_neighbors": 0,
        "neighbor_overlap_ratio": math.nan,
        "max_memberships_per_neighbor": 0,
        "fraction_multimembership_neighbors": math.nan,
    }


def overlap_row(
    ob: int,
    dataset: str,
    t0: float,
    focal_rows: list[dict[str, object]],
    memberships: dict[int, int],
) -> dict[str, object]:
    slots = int(sum(int(r.get("n_neighbors", 0)) for r in focal_rows))
    unique = int(len(memberships))
    multi = [v for v in memberships.values() if v > 1]
    return {
        "ob": ob,
        "dataset": dataset,
        "t": t0,
        "n_focals": int(len(focal_rows)),
        "neighbor_slots": slots,
        "unique_neighbors": unique,
        "neighbor_overlap_ratio": (slots / unique) if unique > 0 else math.nan,
        "max_memberships_per_neighbor": int(max(memberships.values())) if memberships else 0,
        "fraction_multimembership_neighbors": (len(multi) / unique) if unique > 0 else math.nan,
    }


def cache_path(ob: int, k: int, lag_sec: float, frame_stride: int, max_focals: int) -> Path:
    lag_label = f"{lag_sec:.3f}".replace(".", "p")
    return OUT / "cache" / f"Ob{ob}_k{k}_lag{lag_label}_stride{frame_stride}_focals{max_focals}_focal_activity.csv.gz"


def build_focal_activity_for_ob(
    *,
    ob: int,
    dataset: str,
    data_dir: Path,
    k: int,
    lag_sec: float,
    frame_stride: int,
    max_focals: int,
    force: bool,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    focal_path = cache_path(ob, k, lag_sec, frame_stride, max_focals)
    overlap_path = Path(str(focal_path).replace("_focal_activity.csv.gz", "_overlap.csv"))
    if focal_path.exists() and overlap_path.exists() and not force:
        return pd.read_csv(focal_path), pd.read_csv(overlap_path)

    rng = np.random.default_rng(RNG_SEED + ob * 1000 + k)
    df = load_ob_df(ob, data_dir, dataset)
    times = np.asarray(sorted(df["t"].unique()), dtype="float64")
    frames = {float(t): d.sort_values("id").copy() for t, d in df.groupby("t", sort=True)}
    dt = median_dt(times)
    lag_steps = max(1, int(round(lag_sec / dt)))
    idxs = np.arange(0, len(times) - lag_steps, frame_stride, dtype=int)

    focal_rows: list[dict[str, object]] = []
    overlap_rows: list[dict[str, object]] = []
    for nn, idx in enumerate(idxs):
        if nn == 0 or (nn + 1) % 250 == 0 or nn + 1 == len(idxs):
            print(f"[4100A] Ob{ob}: focal activity frame {nn + 1}/{len(idxs)}", flush=True)
        t0 = float(times[idx])
        t1 = float(times[idx + lag_steps])
        ids0, pos0 = frame_arrays(frames[t0])
        ids1, pos1 = frame_arrays(frames[t1])
        rows, overlap = focal_activity_for_frame(
            ids0,
            pos0,
            ids1,
            pos1,
            ob=ob,
            dataset=dataset,
            t0=t0,
            k=k,
            lag_sec=lag_sec,
            lag_dt=lag_steps * dt,
            max_focals=max_focals,
            rng=rng,
        )
        focal_rows.extend(rows)
        overlap_rows.append(overlap)

    focal = pd.DataFrame(focal_rows)
    overlap = pd.DataFrame(overlap_rows)
    focal_path.parent.mkdir(parents=True, exist_ok=True)
    focal.to_csv(focal_path, index=False, compression="gzip")
    overlap.to_csv(overlap_path, index=False)
    return focal, overlap


def aggregate_focal_activity(focal: pd.DataFrame) -> pd.DataFrame:
    if focal.empty:
        return pd.DataFrame(columns=AGG_COLUMNS)
    rows = []
    for (ob, dataset, t), g in focal.groupby(["ob", "dataset", "t"], sort=True):
        rows.append(
            {
                "ob": int(ob),
                "dataset": str(dataset),
                "t": float(t),
                "n_focals": int(len(g)),
                "A_swarm_energy_median": float(np.nanmedian(g["activity_energy_median"])),
                "A_swarm_energy_mean": float(np.nanmean(g["activity_energy_mean"])),
                "A_swarm_tangential_median": float(np.nanmedian(g["activity_tangential_norm_median"])),
                "A_swarm_tangential_mean": float(np.nanmean(g["activity_tangential_norm_mean"])),
            }
        )
    out = pd.DataFrame(rows).sort_values(["ob", "t"]).reset_index(drop=True)
    out["A_swarm_tangential_z"] = math.nan
    for ob, idx in out.groupby("ob", sort=True).groups.items():
        vals = out.loc[idx, "A_swarm_tangential_median"].to_numpy(dtype="float64")
        out.loc[idx, "A_swarm_tangential_z"] = robust_z(vals)
    return out[AGG_COLUMNS]


def qc_for_ob(focal: pd.DataFrame, overlap: pd.DataFrame, *, ob: int, dataset: str) -> dict[str, object]:
    sampled_frames = int(len(overlap))
    valid_frames = int((pd.to_numeric(overlap.get("n_focals", pd.Series(dtype=float)), errors="coerce") > 0).sum())
    dupes = 0
    if not focal.empty:
        dupes = int(focal.duplicated(subset=["ob", "t", "focal_id"]).sum())
        per_frame = focal.groupby("t")["focal_id"].nunique()
    else:
        per_frame = pd.Series(dtype=float)
    return {
        "ob": ob,
        "dataset": dataset,
        "n_sampled_frames": sampled_frames,
        "n_valid_frames": valid_frames,
        "valid_frame_fraction": valid_frames / sampled_frames if sampled_frames else math.nan,
        "n_focal_activity_rows": int(len(focal)),
        "duplicate_focal_frame_rows": dupes,
        "median_focals_per_valid_frame": finite_median(per_frame),
        "median_condition_number": finite_median(focal["condition_number"]) if not focal.empty else math.nan,
        "median_activity_energy_median": finite_median(focal["activity_energy_median"]) if not focal.empty else math.nan,
        "median_activity_tangential_norm_median": finite_median(focal["activity_tangential_norm_median"]) if not focal.empty else math.nan,
        "median_neighbor_slots_per_frame": finite_median(overlap["neighbor_slots"]) if not overlap.empty else math.nan,
        "median_unique_neighbors_per_frame": finite_median(overlap["unique_neighbors"]) if not overlap.empty else math.nan,
        "median_neighbor_overlap_ratio": finite_median(overlap["neighbor_overlap_ratio"]) if not overlap.empty else math.nan,
        "median_fraction_multimembership_neighbors": finite_median(overlap["fraction_multimembership_neighbors"]) if not overlap.empty else math.nan,
    }


def compare_with_4084(ob: int, agg: pd.DataFrame) -> tuple[float, float, int]:
    ref_path = SRC_4084_PER_OB / f"Ob{ob}" / "local_spatial_metric_frame.csv"
    if not ref_path.exists() or agg.empty:
        return math.nan, math.nan, 0
    ref = pd.read_csv(ref_path)
    if "all_tangential" not in ref.columns:
        return math.nan, math.nan, 0
    a = agg[agg["ob"] == ob][["t", "A_swarm_tangential_median"]].copy()
    r = ref[["t", "all_tangential"]].copy()
    a["t_key"] = pd.to_numeric(a["t"], errors="coerce").round(3)
    r["t_key"] = pd.to_numeric(r["t"], errors="coerce").round(3)
    merged = a.merge(r, on="t_key", how="inner", suffixes=("_4100A", "_4084"))
    if len(merged) < 3:
        return math.nan, math.nan, int(len(merged))
    x = merged["A_swarm_tangential_median"].to_numpy(dtype="float64")
    y = merged["all_tangential"].to_numpy(dtype="float64")
    return corr_or_nan(x, y), corr_or_nan(x, y, rank=True), int(len(merged))


def window_median(frame: pd.DataFrame, center: float, lo: float, hi: float) -> float:
    d = frame[(frame["t"] >= center + lo) & (frame["t"] <= center + hi)].copy()
    if d.empty:
        return math.nan
    return finite_median(d["A_swarm_tangential_z"])


def event_reproduction_for_ob(
    *,
    ob: int,
    dataset: str,
    agg: pd.DataFrame,
    events_ob: pd.DataFrame,
    near_pre: tuple[float, float],
    prepost_sec: float,
    exclusion_sec: float,
    n_control_reps: int,
) -> dict[str, object]:
    frame = agg[agg["ob"] == ob].sort_values("t").copy()
    if frame.empty or events_ob.empty:
        pearson, spearman, n_ref = compare_with_4084(ob, agg)
        return {
            "ob": ob,
            "dataset": dataset,
            "n_events": 0,
            "n_controls": 0,
            "near_pre_event_median_z": math.nan,
            "near_pre_control_median_z": math.nan,
            "near_pre_event_minus_control_z": math.nan,
            "agg_vs_4084_pearson": pearson,
            "agg_vs_4084_spearman": spearman,
            "agg_vs_4084_n": n_ref,
            "qualitative_reproduction": "unavailable",
        }
    event_vals = [
        window_median(frame, float(row.event_t), near_pre[0], near_pre[1])
        for row in events_ob.itertuples(index=False)
    ]
    event_vals = [v for v in event_vals if np.isfinite(v)]

    rng = np.random.default_rng(RNG_SEED + ob * 17)
    t = frame["t"].to_numpy(dtype="float64")
    control_vals: list[float] = []
    for _ in range(n_control_reps):
        sampled = r4081.sample_non_event_times(events_ob, t, rng, prepost_sec, exclusion_sec)
        for row in sampled.itertuples(index=False):
            val = window_median(frame, float(row.event_t), near_pre[0], near_pre[1])
            if np.isfinite(val):
                control_vals.append(val)
    event_med = finite_median(event_vals)
    control_med = finite_median(control_vals)
    gap = event_med - control_med if np.isfinite(event_med) and np.isfinite(control_med) else math.nan
    pearson, spearman, n_ref = compare_with_4084(ob, agg)
    if np.isfinite(spearman) and spearman >= 0.70 and np.isfinite(gap):
        q = "aggregate_consistent_with_4084"
    elif n_ref == 0 and np.isfinite(gap):
        q = "event_profile_only_no_4084_reference"
    elif np.isfinite(spearman):
        q = "weak_aggregate_consistency"
    else:
        q = "unavailable"
    return {
        "ob": ob,
        "dataset": dataset,
        "n_events": int(len(event_vals)),
        "n_controls": int(len(control_vals)),
        "near_pre_event_median_z": event_med,
        "near_pre_control_median_z": control_med,
        "near_pre_event_minus_control_z": gap,
        "agg_vs_4084_pearson": pearson,
        "agg_vs_4084_spearman": spearman,
        "agg_vs_4084_n": n_ref,
        "qualitative_reproduction": q,
    }


def decide(qc: pd.DataFrame, reproduction: pd.DataFrame, *, obs: list[int]) -> dict[str, object]:
    valid_frac = pd.to_numeric(qc["valid_frame_fraction"], errors="coerce")
    dupes = pd.to_numeric(qc["duplicate_focal_frame_rows"], errors="coerce")
    med_focals = pd.to_numeric(qc["median_focals_per_valid_frame"], errors="coerce")
    spearman = pd.to_numeric(reproduction["agg_vs_4084_spearman"], errors="coerce")
    has_ref = pd.to_numeric(reproduction["agg_vs_4084_n"], errors="coerce") >= 20
    good_ref = (spearman >= 0.70) & has_ref

    uniqueness_ok = bool((dupes.fillna(0) == 0).all())
    coverage_ok = bool((valid_frac >= 0.80).all() and (med_focals >= 8).all())
    ref_available_count = int(has_ref.sum())
    ref_good_count = int(good_ref.sum())
    all_19 = len(obs) == 19 and set(obs) == set(range(1, 20))
    scope = "all_19_observations" if all_19 else f"pilot_observations_{','.join(str(x) for x in obs)}"
    pass_gate = (
        "pass_unique_focal_activity_with_overlap_boundary"
        if all_19
        else "pilot_pass_unique_focal_activity_with_overlap_boundary"
    )

    if uniqueness_ok and coverage_ok and (ref_available_count == 0 or ref_good_count >= max(1, math.ceil(0.50 * ref_available_count))):
        gate = pass_gate
        next_nodes = (
            ["4100_state_matched_event_locality_challenge"]
            if all_19
            else ["4100A_all19_or_4100_state_matched_event_locality_after_density_sampling_choice"]
        )
        run_label = "all-19 run" if all_19 else "pilot"
        interpretation = (
            f"The {run_label} constructs unique focal-centered activity rows with adequate coverage. "
            "Underlying neighbor overlap remains nontrivial, so later spatial correlation must use "
            "the focal aggregate rather than raw neighbor residual vectors."
        )
    elif not uniqueness_ok or not coverage_ok:
        gate = "technical_boundary_spatial_unit_or_coverage"
        next_nodes = ["stop_410x_until_spatial_unit_is_revised"]
        interpretation = "The pilot does not yet provide a reliable unique focal-centered activity unit."
    else:
        gate = "representation_dependency_boundary"
        next_nodes = ["revise_focal_activity_definition_before_4100"]
        interpretation = (
            "The focal-centered activity can be constructed, but agreement with the upstream 4084 "
            "aggregate is not strong enough where a 4084 reference is available."
        )

    return {
        "node": NODE,
        "date": DATE,
        "node_type": "technical_gate",
        "upstream_node": "4094_bounded_stochastic_negative_synthesis",
        "data_scope": scope,
        "spatial_unit": "focal_centered_local_nonaffine_tangential_activity",
        "activity_definition": "A_i(t)=median_j ||u_NA_ij,tan(t)||^2",
        "gate_result": gate,
        "uniqueness_ok": uniqueness_ok,
        "coverage_ok": coverage_ok,
        "ref_available_count": ref_available_count,
        "ref_good_count": ref_good_count,
        "interpretation": interpretation,
        "does_not_prove": [
            "state-matched event-locality",
            "burst localization",
            "propagation",
            "causal trigger",
            "unique individual residual velocity rather than focal-neighborhood activity",
        ],
        "next": next_nodes,
        "artifacts": [
            "Output/4100A/focal_activity.csv.gz",
            "Output/4100A/focal_activity_qc.csv",
            "Output/4100A/overlap_audit.csv",
            "Output/4100A/swarm_activity_frame.csv",
            "Output/4100A/upstream_reproduction.csv",
            "Output/4100A/figures/4100A_qc_overview.png",
            "Output/4100A/figures/4100A_aggregate_vs_4084.png",
            "Output/4100A/figures/4100A_near_pre_reproduction.png",
            "Output/4100A/4100A_summary.md",
        ],
    }


def make_figures(qc: pd.DataFrame, reproduction: pd.DataFrame, agg: pd.DataFrame) -> None:
    fig_dir = OUT / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4), constrained_layout=True)
    x = np.arange(len(qc))
    labels = [f"Ob{int(o)}" for o in qc["ob"]]
    axes[0].bar(x, pd.to_numeric(qc["valid_frame_fraction"], errors="coerce"), color="#4c78a8")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels, rotation=35, ha="right")
    axes[0].set_ylim(0, 1.05)
    axes[0].set_title("valid frame fraction")
    axes[1].bar(x, pd.to_numeric(qc["median_focals_per_valid_frame"], errors="coerce"), color="#59a14f")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels, rotation=35, ha="right")
    axes[1].set_title("median focals / frame")
    axes[2].bar(x, pd.to_numeric(qc["median_neighbor_overlap_ratio"], errors="coerce"), color="#f28e2b")
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(labels, rotation=35, ha="right")
    axes[2].set_title("neighbor overlap ratio")
    fig.suptitle("4100A focal-centered activity QC")
    fig.savefig(fig_dir / "4100A_qc_overview.png", dpi=180)
    plt.close(fig)

    refs = reproduction[pd.to_numeric(reproduction["agg_vs_4084_n"], errors="coerce") > 0].copy()
    if not refs.empty:
        fig, ax = plt.subplots(figsize=(7, 4.2), constrained_layout=True)
        xx = np.arange(len(refs))
        ax.bar(xx, pd.to_numeric(refs["agg_vs_4084_spearman"], errors="coerce"), color="#4c78a8")
        ax.axhline(0.70, color="#333333", lw=1, ls="--")
        ax.set_xticks(xx)
        ax.set_xticklabels([f"Ob{int(o)}" for o in refs["ob"]], rotation=35, ha="right")
        ax.set_ylim(-1, 1)
        ax.set_ylabel("Spearman vs 4084 all_tangential")
        ax.set_title("4100A aggregate consistency with 4084")
        fig.savefig(fig_dir / "4100A_aggregate_vs_4084.png", dpi=180)
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4.2), constrained_layout=True)
    xx = np.arange(len(reproduction))
    ax.bar(xx, pd.to_numeric(reproduction["near_pre_event_minus_control_z"], errors="coerce"), color="#b07aa1")
    ax.axhline(0, color="#333333", lw=1)
    ax.set_xticks(xx)
    ax.set_xticklabels([f"Ob{int(o)}" for o in reproduction["ob"]], rotation=35, ha="right")
    ax.set_ylabel("near-pre event - non-event (z)")
    ax.set_title("4100A near-pre reproduction diagnostic")
    fig.savefig(fig_dir / "4100A_near_pre_reproduction.png", dpi=180)
    plt.close(fig)

    if not agg.empty:
        fig, ax = plt.subplots(figsize=(9, 4.5), constrained_layout=True)
        for ob, d in agg.groupby("ob", sort=True):
            ax.plot(d["t"], d["A_swarm_tangential_z"], lw=0.8, label=f"Ob{int(ob)}")
        ax.set_xlabel("time (sec)")
        ax.set_ylabel("A_swarm tangential z")
        ax.set_title("4100A swarm activity traces")
        ax.legend(ncol=2, fontsize=8)
        fig.savefig(fig_dir / "4100A_swarm_activity_traces.png", dpi=180)
        plt.close(fig)


def write_config(args: argparse.Namespace, obs: list[int]) -> None:
    text = dedent(
        f"""\
        node: {NODE}
        date: {DATE}
        node_type: technical_gate
        upstream_node: 4094_bounded_stochastic_negative_synthesis
        observations: {','.join(str(x) for x in obs)}
        k: {args.k}
        lag_sec: {args.lag_sec}
        frame_stride: {args.frame_stride}
        max_focals_per_frame: {args.max_focals_per_frame}
        near_pre_window_sec: [{args.near_pre_start}, {args.near_pre_end}]
        non_event_replicates: {args.n_control_reps}
        exclusion_sec: {args.exclusion_sec}
        activity_unit: focal_centered_local_nonaffine_tangential_activity
        activity_definition: median_neighbor_tangential_energy
        output_note: focal_activity.csv.gz is used instead of parquet to avoid optional parquet dependencies
        """
    )
    (OUT / "config.yaml").write_text(text, encoding="utf-8")


def write_summary(
    *,
    qc: pd.DataFrame,
    reproduction: pd.DataFrame,
    decision: dict[str, object],
    obs: list[int],
) -> None:
    all_19 = obs == list(range(1, 20))
    scope_intro = (
        "This run covers all 19 observations."
        if all_19
        else "This run is a pilot over the following observations."
    )
    if all_19:
        scope_note = (
            "This is the primary technical-gate scope for 4100A, because "
            "410x inherits the all-observation validation requirement after "
            "4088 and 4094."
        )
    else:
        scope_note = (
            "The default pilot intentionally includes a robust survivor "
            "(`Ob2`), a strong robust survivor (`Ob15`), a stable failure "
            "(`Ob6`), and a fragile boundary observation (`Ob1`)."
        )

    does_not_prove_table = "\n".join(
        ["| does_not_prove |", "| --- |"]
        + [f"| {item} |" for item in decision["does_not_prove"]]
    )
    next_table = "\n".join(
        ["| next |", "| --- |"] + [f"| {item} |" for item in decision["next"]]
    )

    sections = [
        "# Node 4100A Summary",
        "## Question\n\n"
        "Can the 410x route construct a unique focal-centered local non-affine "
        "tangential activity unit before testing event-locality or propagation?",
        "## Why This Node Exists After 4094\n\n"
        "4094 routed the workflow away from low-dimensional `C,dCdt,radius` "
        "moment closure and toward transient/event-local organization. However, "
        "4090B showed that the available vector unit is a focal-neighborhood "
        "neighbor residual vector. Directly computing spatial correlations on "
        "those overlapping neighbor vectors could create pseudo-correlation. "
        "4100A therefore audits the representation before any propagation "
        "analysis.",
        "## Data Scope\n\n"
        f"{scope_intro}\n\n"
        "```text\n"
        f"{', '.join(f'Ob{x}' for x in obs)}\n"
        "```\n\n"
        f"{scope_note}",
        "## Spatial Unit\n\n"
        "```text\n"
        "focal_centered_local_nonaffine_tangential_activity\n"
        "```\n\n"
        "Primary activity:\n\n"
        "```text\n"
        "A_i(t) = median_j ||u_NA_ij,tan(t)||^2\n"
        "```\n\n"
        "The naming remains focal-centered activity, not individual residual "
        "velocity, because each value aggregates neighbor residual vectors "
        "around a focal individual.",
        "## Main QC\n\n" + md_table(qc.to_dict("records"), QC_COLUMNS),
        "## Upstream Reproduction Diagnostic\n\n"
        + md_table(reproduction.to_dict("records"), REPRO_COLUMNS),
        "## Gate Evaluation\n\n"
        "```text\n"
        f"gate_result = {decision['gate_result']}\n"
        "```\n\n"
        f"{decision['interpretation']}",
        "## What This Supports\n\n"
        "- It tests whether a unique `(observation, frame, focal_id)` activity "
        "table can be constructed.\n"
        "- It quantifies the underlying neighbor-overlap issue.\n"
        "- It checks whether the focal-centered aggregate is consistent with "
        "the earlier 4084 `all_tangential` aggregate where a reference exists.",
        "## What This Does Not Prove\n\n" + does_not_prove_table,
        "## Decision\n\n" f"`{decision['gate_result']}`",
        "## Next Node\n\n" + next_table,
        "## Artifacts\n\n"
        "- `Output/4100A/focal_activity.csv.gz`\n"
        "- `Output/4100A/focal_activity_qc.csv`\n"
        "- `Output/4100A/overlap_audit.csv`\n"
        "- `Output/4100A/swarm_activity_frame.csv`\n"
        "- `Output/4100A/upstream_reproduction.csv`\n"
        "- `Output/4100A/figures/4100A_qc_overview.png`\n"
        "- `Output/4100A/figures/4100A_aggregate_vs_4084.png`\n"
        "- `Output/4100A/figures/4100A_near_pre_reproduction.png`\n"
        "- `Output/4100A/decision.json`",
    ]
    text = "\n\n".join(sections) + "\n"
    (OUT / "4100A_summary.md").write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--obs", default="pilot", help="'pilot', 'all', range like 1-19, or comma list")
    parser.add_argument("--k", type=int, default=8)
    parser.add_argument("--lag-sec", type=float, default=0.10)
    parser.add_argument("--frame-stride", type=int, default=10)
    parser.add_argument("--max-focals-per-frame", type=int, default=24)
    parser.add_argument("--near-pre-start", type=float, default=-0.25)
    parser.add_argument("--near-pre-end", type=float, default=0.0)
    parser.add_argument("--prepost-sec", type=float, default=0.25)
    parser.add_argument("--exclusion-sec", type=float, default=0.75)
    parser.add_argument("--n-control-reps", type=int, default=20)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    ensure_dirs()
    args = parse_args()
    cfg = BaseRunConfig()
    data_dir = resolve_data_dir(cfg)
    events = read_events()
    obs = parse_obs(args.obs, events)
    write_config(args, obs)

    all_focal: list[pd.DataFrame] = []
    all_overlap: list[pd.DataFrame] = []
    qc_rows: list[dict[str, object]] = []
    repro_rows: list[dict[str, object]] = []
    all_agg: list[pd.DataFrame] = []

    for ob in obs:
        events_ob = events[events["ob"] == ob].copy().reset_index(drop=True)
        if events_ob.empty:
            print(f"[4100A] Ob{ob}: no events, skipping", flush=True)
            continue
        dataset = str(events_ob.iloc[0]["dataset"])
        focal, overlap = build_focal_activity_for_ob(
            ob=ob,
            dataset=dataset,
            data_dir=data_dir,
            k=args.k,
            lag_sec=args.lag_sec,
            frame_stride=args.frame_stride,
            max_focals=args.max_focals_per_frame,
            force=args.force,
        )
        agg = aggregate_focal_activity(focal)
        qc_rows.append(qc_for_ob(focal, overlap, ob=ob, dataset=dataset))
        repro_rows.append(
            event_reproduction_for_ob(
                ob=ob,
                dataset=dataset,
                agg=agg,
                events_ob=events_ob,
                near_pre=(args.near_pre_start, args.near_pre_end),
                prepost_sec=args.prepost_sec,
                exclusion_sec=args.exclusion_sec,
                n_control_reps=args.n_control_reps,
            )
        )
        all_focal.append(focal)
        all_overlap.append(overlap)
        all_agg.append(agg)

    focal_df = pd.concat(all_focal, ignore_index=True) if all_focal else pd.DataFrame(columns=FOCAL_COLUMNS)
    overlap_df = pd.concat(all_overlap, ignore_index=True) if all_overlap else pd.DataFrame(columns=OVERLAP_COLUMNS)
    agg_df = pd.concat(all_agg, ignore_index=True) if all_agg else pd.DataFrame(columns=AGG_COLUMNS)
    qc_df = pd.DataFrame(qc_rows)
    repro_df = pd.DataFrame(repro_rows)
    decision = decide(qc_df, repro_df, obs=obs)

    focal_df.to_csv(OUT / "focal_activity.csv.gz", index=False, compression="gzip")
    overlap_df.to_csv(OUT / "overlap_audit.csv", index=False)
    agg_df.to_csv(OUT / "swarm_activity_frame.csv", index=False)
    write_csv(OUT / "focal_activity_qc.csv", qc_df.to_dict("records"), QC_COLUMNS)
    write_csv(OUT / "tables" / "focal_activity_qc.csv", qc_df.to_dict("records"), QC_COLUMNS)
    write_csv(OUT / "tables" / "overlap_audit.csv", overlap_df.to_dict("records"), OVERLAP_COLUMNS)
    write_csv(OUT / "tables" / "swarm_activity_frame.csv", agg_df.to_dict("records"), AGG_COLUMNS)
    write_csv(OUT / "upstream_reproduction.csv", repro_df.to_dict("records"), REPRO_COLUMNS)
    write_csv(OUT / "tables" / "upstream_reproduction.csv", repro_df.to_dict("records"), REPRO_COLUMNS)
    write_json(OUT / "decision.json", decision)
    make_figures(qc_df, repro_df, agg_df)
    write_summary(qc=qc_df, reproduction=repro_df, decision=decision, obs=obs)

    print(json.dumps(to_jsonable(decision), ensure_ascii=False, indent=2), flush=True)
    print(f"Wrote 4100A outputs to {OUT.relative_to(ROOT)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
