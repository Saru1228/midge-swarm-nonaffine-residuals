"""4084 spatial taxonomy of the T1 local non-affine signal.

4081c/4082 established that the T1 local non-affine tangential residual
survives local affine subtraction in most observations. This node asks a
narrower descriptive question: where does that signal live spatially?

The experiment keeps the 4081/4082 event definition and local-affine residual
settings, then decomposes the local tangential residual by radial shell and by
local kNN-distance density. It compares real transition windows against matched
non-event windows, one observation at a time.
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

import run_4002a_residual_spatial_structure_audit as r4002a  # noqa: E402
import run_4081_global_vs_local_geometry_ladder as r4081  # noqa: E402
from run_4001_geometric_baseline_residual_audit import (  # noqa: E402
    RunConfig as BaseRunConfig,
    median_dt,
    read_raw_ob,
    resolve_data_dir,
)


OUT = ROOT / "Output" / "4084"
NODE = "4084_spatial_taxonomy_of_t1_local_nonaffine_signal"
DATE = "2026-08-25"
RNG_SEED = 4084_0101

LOCAL_VARIABLES = [
    "all_tangential",
    "shell_core_tangential",
    "shell_middle_tangential",
    "shell_edge_tangential",
    "shell_edge_minus_core",
    "shell_middle_minus_core",
    "shell_radius_corr_tangential",
    "density_dense_tangential",
    "density_middle_tangential",
    "density_sparse_tangential",
    "density_sparse_minus_dense",
    "density_knn_distance_corr_tangential",
]

VARIABLE_FAMILY = {
    "all_tangential": "diffuse_baseline",
    "shell_core_tangential": "radial_level",
    "shell_middle_tangential": "radial_level",
    "shell_edge_tangential": "radial_level",
    "shell_edge_minus_core": "radial_contrast",
    "shell_middle_minus_core": "radial_contrast",
    "shell_radius_corr_tangential": "radial_gradient",
    "density_dense_tangential": "density_level",
    "density_middle_tangential": "density_level",
    "density_sparse_tangential": "density_level",
    "density_sparse_minus_dense": "density_contrast",
    "density_knn_distance_corr_tangential": "density_gradient",
}

SPATIAL_CONTRAST_FAMILIES = {
    "radial_contrast",
    "radial_gradient",
    "density_contrast",
    "density_gradient",
}

ROW_COLUMNS = [
    "ob",
    "variable",
    "family",
    "k",
    "lag_sec",
    "n_events",
    "real_low_to_high_delta_z",
    "real_high_to_low_delta_z",
    "real_direction_contrast_z",
    "real_abs_direction_contrast_z",
    "non_event_abs_direction_median_z",
    "event_minus_non_event_abs_direction_z",
    "p_non_event_abs_direction_ge_event",
    "event_conditioned_gate",
]

OB_COLUMNS = [
    "ob",
    "n_events",
    "diffuse_baseline_gate",
    "n_spatial_contrast_gates",
    "best_spatial_variable",
    "best_spatial_family",
    "best_spatial_gap_z",
    "best_level_variable",
    "best_level_family",
    "best_level_gap_z",
    "ob_spatial_class",
    "interpretation",
]

VARIABLE_COLUMNS = [
    "variable",
    "family",
    "n_ob_tested",
    "gate_count",
    "gate_fraction",
    "median_event_minus_non_event_abs_direction_z",
    "median_real_abs_direction_contrast_z",
    "signed_direction_sign_consistency",
    "majority_gate",
    "interpretation",
]


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in columns})


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def finite_median(values: list[float] | np.ndarray | pd.Series) -> float:
    arr = np.asarray(values, dtype="float64")
    arr = arr[np.isfinite(arr)]
    return float(np.median(arr)) if arr.size else math.nan


def finite_quantile(values: list[float] | np.ndarray | pd.Series, q: float) -> float:
    arr = np.asarray(values, dtype="float64")
    arr = arr[np.isfinite(arr)]
    return float(np.quantile(arr, q)) if arr.size else math.nan


def mean_or_nan(values: list[float] | np.ndarray) -> float:
    arr = np.asarray(values, dtype="float64")
    arr = arr[np.isfinite(arr)]
    return float(np.mean(arr)) if arr.size else math.nan


def sign_consistency(values: list[float] | np.ndarray | pd.Series) -> float:
    arr = np.asarray(values, dtype="float64")
    arr = arr[np.isfinite(arr)]
    signs = np.sign(arr)
    signs = signs[signs != 0]
    if not signs.size:
        return math.nan
    vals, counts = np.unique(signs, return_counts=True)
    return float(np.max(counts) / signs.size)


def corr_or_nan(a: list[float] | np.ndarray, b: list[float] | np.ndarray) -> float:
    aa = np.asarray(a, dtype="float64")
    bb = np.asarray(b, dtype="float64")
    ok = np.isfinite(aa) & np.isfinite(bb)
    if int(ok.sum()) < 5:
        return math.nan
    aa = aa[ok]
    bb = bb[ok]
    if float(np.nanstd(aa)) <= 1e-12 or float(np.nanstd(bb)) <= 1e-12:
        return math.nan
    return float(np.corrcoef(aa, bb)[0, 1])


def md_table(rows: list[dict[str, object]], columns: list[str]) -> str:
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
                vals.append("NA" if not np.isfinite(val) else f"{val:.4g}")
            else:
                vals.append(str(val).replace("\n", " ").replace("|", "\\|"))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def bool_from_csv(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def parse_int_list(text: str) -> list[int]:
    return [int(x.strip()) for x in text.split(",") if x.strip()]


def lag_label(lag: float) -> str:
    return f"{lag:.3f}".replace(".", "p")


def cache_path(ob: int, k: int, lag: float, frame_stride: int, max_focals: int) -> Path:
    return OUT / "cache" / f"Ob{ob}_k{k}_lag{lag_label(lag)}_stride{frame_stride}_focals{max_focals}.csv"


def load_ob_df(ob: int, data_dir: Path, dataset: str) -> pd.DataFrame:
    path = data_dir / dataset
    if not path.exists():
        path = data_dir / f"Ob{ob}.txt"
    return read_raw_ob(path)


def frame_arrays(frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    return frame["id"].to_numpy(dtype="int64"), frame[["x", "y", "z"]].to_numpy(dtype="float64")


def local_spatial_metrics(
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
    common = np.asarray([int(v) for v in ids0 if int(v) in id_to_idx1], dtype="int64")
    if common.size == 0:
        return empty_frame_metric()
    if common.size > max_focals:
        focals = rng.choice(common, size=max_focals, replace=False)
    else:
        focals = common

    center = np.nanmean(pos0, axis=0)
    radii_all = np.linalg.norm(pos0 - center, axis=1)
    q33_r = finite_quantile(radii_all, 1 / 3)
    q67_r = finite_quantile(radii_all, 2 / 3)

    focal_rows: list[dict[str, float]] = []
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
        neighbor_dists = []
        for nid in neigh_ids:
            j0 = id_to_idx0[nid]
            j1 = id_to_idx1[nid]
            r0 = pos0[j0] - pos0[i0]
            r1 = pos1[j1] - pos1[i1]
            A.append(r0)
            B.append(r1 - r0)
            neighbor_dists.append(float(np.linalg.norm(r0)))
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
        if not np.isfinite(resid).all():
            continue

        focal_rel = pos0[i0] - center
        focal_radius = float(np.linalg.norm(focal_rel))
        if not np.isfinite(focal_radius) or focal_radius <= 1e-12:
            continue
        radial_unit = focal_rel / focal_radius
        radial_component = resid @ radial_unit
        tang_sq = np.maximum(np.sum(resid * resid, axis=1) - radial_component * radial_component, 0.0)
        tangential = np.sqrt(tang_sq)
        focal_tangential = mean_or_nan(tangential)
        if not np.isfinite(focal_tangential):
            continue
        kth_distance = float(max(neighbor_dists)) if neighbor_dists else math.nan
        if not np.isfinite(kth_distance):
            continue
        if np.isfinite(q33_r) and focal_radius <= q33_r:
            shell = 0
        elif np.isfinite(q67_r) and focal_radius >= q67_r:
            shell = 2
        else:
            shell = 1
        focal_rows.append(
            {
                "tangential": focal_tangential,
                "radius": focal_radius,
                "shell": float(shell),
                "kth_distance": kth_distance,
            }
        )

    if not focal_rows:
        return empty_frame_metric()

    focal = pd.DataFrame(focal_rows)
    dense_q33 = finite_quantile(focal["kth_distance"], 1 / 3)
    dense_q67 = finite_quantile(focal["kth_distance"], 2 / 3)
    dense = focal["kth_distance"].to_numpy(dtype="float64") <= dense_q33 if np.isfinite(dense_q33) else np.zeros(len(focal), dtype=bool)
    sparse = focal["kth_distance"].to_numpy(dtype="float64") >= dense_q67 if np.isfinite(dense_q67) else np.zeros(len(focal), dtype=bool)
    middle_density = ~(dense | sparse)
    core = focal["shell"].to_numpy(dtype="float64") == 0
    middle_shell = focal["shell"].to_numpy(dtype="float64") == 1
    edge = focal["shell"].to_numpy(dtype="float64") == 2
    tang = focal["tangential"].to_numpy(dtype="float64")
    kth = focal["kth_distance"].to_numpy(dtype="float64")
    radius = focal["radius"].to_numpy(dtype="float64")

    core_t = mean_or_nan(tang[core])
    middle_t = mean_or_nan(tang[middle_shell])
    edge_t = mean_or_nan(tang[edge])
    dense_t = mean_or_nan(tang[dense])
    density_middle_t = mean_or_nan(tang[middle_density])
    sparse_t = mean_or_nan(tang[sparse])
    out = {
        "n_focals_used": int(len(focal)),
        "all_tangential": mean_or_nan(tang),
        "shell_core_tangential": core_t,
        "shell_middle_tangential": middle_t,
        "shell_edge_tangential": edge_t,
        "shell_edge_minus_core": edge_t - core_t if np.isfinite(edge_t) and np.isfinite(core_t) else math.nan,
        "shell_middle_minus_core": middle_t - core_t if np.isfinite(middle_t) and np.isfinite(core_t) else math.nan,
        "shell_radius_corr_tangential": corr_or_nan(radius, tang),
        "density_dense_tangential": dense_t,
        "density_middle_tangential": density_middle_t,
        "density_sparse_tangential": sparse_t,
        "density_sparse_minus_dense": sparse_t - dense_t if np.isfinite(sparse_t) and np.isfinite(dense_t) else math.nan,
        "density_knn_distance_corr_tangential": corr_or_nan(kth, tang),
    }
    return out


def empty_frame_metric() -> dict[str, float]:
    out = {"n_focals_used": 0}
    for var in LOCAL_VARIABLES:
        out[var] = math.nan
    return out


def build_spatial_metric_frame(
    ob: int,
    dataset: str,
    data_dir: Path,
    k: int,
    lag_sec: float,
    frame_stride: int,
    max_focals: int,
    force: bool,
) -> pd.DataFrame:
    path = cache_path(ob, k, lag_sec, frame_stride, max_focals)
    if path.exists() and not force:
        return pd.read_csv(path)

    rng = np.random.default_rng(RNG_SEED + ob * 1000 + k)
    df = load_ob_df(ob, data_dir, dataset)
    times = np.asarray(sorted(df["t"].unique()), dtype="float64")
    frames = {float(t): d.sort_values("id").copy() for t, d in df.groupby("t", sort=True)}
    dt = median_dt(times)
    lag_steps = max(1, int(round(lag_sec / dt)))
    idxs = np.arange(0, len(times) - lag_steps, frame_stride, dtype=int)
    rows = []
    for nn, idx in enumerate(idxs):
        if nn == 0 or (nn + 1) % 500 == 0 or nn + 1 == len(idxs):
            print(f"[4084] Ob{ob} k={k}: local spatial frame {nn + 1}/{len(idxs)}", flush=True)
        t0 = float(times[idx])
        t1 = float(times[idx + lag_steps])
        ids0, pos0 = frame_arrays(frames[t0])
        ids1, pos1 = frame_arrays(frames[t1])
        metrics = local_spatial_metrics(ids0, pos0, ids1, pos1, k, lag_steps * dt, rng, max_focals)
        row = {"ob": ob, "dataset": dataset, "t": t0, "k": k, "lag_sec": lag_sec, "lag_steps": lag_steps}
        row.update(metrics)
        rows.append(row)

    out = pd.DataFrame(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(path, index=False)
    return out


def add_residualized_metrics(frame: pd.DataFrame, smooth_window_sec: float) -> pd.DataFrame:
    d = frame.sort_values("t").reset_index(drop=True).copy()
    dt = median_dt(d["t"].to_numpy(dtype="float64"))
    win = max(5, int(round(smooth_window_sec / dt))) if np.isfinite(dt) and dt > 0 else 101
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
        d[f"{var}__resid4084"] = r4002a.robust_z_safe(z - smooth)
    return d


def build_arrays(frame: pd.DataFrame) -> dict[tuple[int, str], dict[str, np.ndarray]]:
    rec: dict[str, np.ndarray] = {"t": frame["t"].to_numpy(dtype="float64")}
    for var in LOCAL_VARIABLES:
        rec[var] = frame[f"{var}__resid4084"].to_numpy(dtype="float64")
    first = frame.iloc[0]
    return {(int(first["ob"]), str(first["dataset"])): rec}


def extract_features(
    arrays: dict[tuple[int, str], dict[str, np.ndarray]],
    events: pd.DataFrame,
    variables: list[str],
    prepost_sec: float,
) -> pd.DataFrame:
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
                    "family": VARIABLE_FAMILY[var],
                    "pre_mean_resid_z": pre_mean,
                    "post_mean_resid_z": post_mean,
                    "signed_delta_post_minus_pre_z": post_mean - pre_mean,
                }
            )
    return pd.DataFrame(rows)


def direction_summary(features: pd.DataFrame, variable: str) -> tuple[int, float, float, float, float]:
    d = features[(features["variable"] == variable) & (features["event_type"].isin(["low_to_high", "high_to_low"]))].copy()
    if d.empty:
        return 0, math.nan, math.nan, math.nan, math.nan
    by_type = d.groupby("event_type")["signed_delta_post_minus_pre_z"].median()
    if "low_to_high" not in by_type or "high_to_low" not in by_type:
        return int(d["event_id"].nunique()), math.nan, math.nan, math.nan, math.nan
    low_to_high = float(by_type["low_to_high"])
    high_to_low = float(by_type["high_to_low"])
    contrast = low_to_high - high_to_low
    return int(d["event_id"].nunique()), low_to_high, high_to_low, contrast, abs(contrast)


def sample_non_event_times(
    events_ob: pd.DataFrame,
    t: np.ndarray,
    rng: np.random.Generator,
    prepost_sec: float,
    exclusion_sec: float,
) -> pd.DataFrame:
    return r4081.sample_non_event_times(events_ob, t, rng, prepost_sec, exclusion_sec)


def summarize_ob_variable(
    ob: int,
    variable: str,
    features: pd.DataFrame,
    null_values: list[float],
    k: int,
    lag_sec: float,
    gap_gate: float,
    p_gate: float,
) -> dict[str, object]:
    n_events, low_to_high, high_to_low, direction, direction_abs = direction_summary(features, variable)
    null = np.asarray(null_values, dtype="float64")
    null = null[np.isfinite(null)]
    null_med = float(np.median(null)) if null.size else math.nan
    p_ge = float(np.mean(null >= direction_abs)) if null.size and np.isfinite(direction_abs) else math.nan
    gap = direction_abs - null_med if np.isfinite(direction_abs) and np.isfinite(null_med) else math.nan
    gate = bool(np.isfinite(gap) and gap > gap_gate and np.isfinite(p_ge) and p_ge <= p_gate)
    return {
        "ob": ob,
        "variable": variable,
        "family": VARIABLE_FAMILY[variable],
        "k": k,
        "lag_sec": lag_sec,
        "n_events": n_events,
        "real_low_to_high_delta_z": low_to_high,
        "real_high_to_low_delta_z": high_to_low,
        "real_direction_contrast_z": direction,
        "real_abs_direction_contrast_z": direction_abs,
        "non_event_abs_direction_median_z": null_med,
        "event_minus_non_event_abs_direction_z": gap,
        "p_non_event_abs_direction_ge_event": p_ge,
        "event_conditioned_gate": gate,
    }


def robust_survivors_from_4082b() -> list[int]:
    path = ROOT / "Output" / "4082b" / "decision.json"
    if path.exists():
        decision = json.loads(path.read_text(encoding="utf-8"))
        values = decision.get("robust_survivor_observations", [])
        if values:
            return [int(x) for x in values]
    path2 = ROOT / "Output" / "4082" / "ob_scale_timing_robustness.csv"
    if not path2.exists():
        raise FileNotFoundError("Missing 4082/4082b outputs; cannot infer robust survivor observations.")
    d = pd.read_csv(path2)
    d["ob"] = pd.to_numeric(d["ob"], errors="coerce").astype("int64")
    return sorted(int(x) for x in d.loc[d["robustness_class"].eq("robust_scale_and_timing"), "ob"].tolist())


def parse_obs(arg: str, events: pd.DataFrame) -> list[int]:
    if arg.lower() in {"robust", "robust-survivors", "survivors"}:
        return robust_survivors_from_4082b()
    if arg.lower() in {"all", "1-19"}:
        return sorted(int(x) for x in events["ob"].dropna().unique())
    if "-" in arg and "," not in arg:
        a, b = arg.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return parse_int_list(arg)


def run_ob(
    ob: int,
    data_dir: Path,
    events_all: pd.DataFrame,
    k: int,
    lag_sec: float,
    frame_stride: int,
    max_focals_per_frame: int,
    n_replicates: int,
    prepost_sec: float,
    exclusion_sec: float,
    smooth_window_sec: float,
    gap_gate: float,
    p_gate: float,
    force: bool,
) -> tuple[list[dict[str, object]], dict[str, object], pd.DataFrame]:
    rows_path = OUT / "per_ob" / f"Ob{ob}" / "spatial_taxonomy_rows.csv"
    decision_path = OUT / "per_ob" / f"Ob{ob}" / "decision.json"
    processed_path = OUT / "per_ob" / f"Ob{ob}" / "local_spatial_metric_frame.csv"
    if rows_path.exists() and decision_path.exists() and processed_path.exists() and not force:
        rows = list(csv.DictReader(rows_path.open(newline="", encoding="utf-8")))
        decision = json.loads(decision_path.read_text(encoding="utf-8"))
        frame = pd.read_csv(processed_path)
        return rows, decision, frame

    ob_dir = OUT / "per_ob" / f"Ob{ob}"
    ob_dir.mkdir(parents=True, exist_ok=True)
    events_ob = events_all[events_all["ob"] == ob].copy().reset_index(drop=True)
    if events_ob.empty:
        raise RuntimeError(f"No events for Ob{ob}")
    dataset = str(events_ob.iloc[0]["dataset"])

    print(f"[4084] Ob{ob}: building spatial local-affine metrics", flush=True)
    frame_raw = build_spatial_metric_frame(ob, dataset, data_dir, k, lag_sec, frame_stride, max_focals_per_frame, force)
    frame = add_residualized_metrics(frame_raw, smooth_window_sec)
    arrays = build_arrays(frame)
    features = extract_features(arrays, events_ob, LOCAL_VARIABLES, prepost_sec)
    rec = next(iter(arrays.values()))

    null_by_var = {var: [] for var in LOCAL_VARIABLES}
    rng = np.random.default_rng(RNG_SEED + ob)
    for rep in range(n_replicates):
        if rep == 0 or rep + 1 == n_replicates or (rep + 1) % 20 == 0:
            print(f"[4084] Ob{ob}: non-event replicate {rep + 1}/{n_replicates}", flush=True)
        sampled = sample_non_event_times(events_ob, rec["t"], rng, prepost_sec, exclusion_sec)
        nf = extract_features(arrays, sampled, LOCAL_VARIABLES, prepost_sec)
        for var in LOCAL_VARIABLES:
            _, _, _, _, da = direction_summary(nf, var)
            null_by_var[var].append(da)

    rows = [
        summarize_ob_variable(ob, var, features, null_by_var[var], k, lag_sec, gap_gate, p_gate)
        for var in LOCAL_VARIABLES
    ]
    ob_summary = classify_ob(rows)
    write_csv(rows_path, rows, ROW_COLUMNS)
    write_json(ob_dir / "spatial_taxonomy_rows.json", rows)
    frame.to_csv(processed_path, index=False)
    write_json(
        decision_path,
        {
            "node": NODE,
            "ob": ob,
            "result": ob_summary["ob_spatial_class"],
            "classification": ob_summary,
            "next": ["aggregate_4084"],
        },
    )
    return rows, {"classification": ob_summary}, frame


def classify_ob(rows: list[dict[str, object]]) -> dict[str, object]:
    d = pd.DataFrame(rows)
    d["event_conditioned_gate"] = d["event_conditioned_gate"].map(bool_from_csv)
    d["event_minus_non_event_abs_direction_z"] = pd.to_numeric(d["event_minus_non_event_abs_direction_z"], errors="coerce")
    d["n_events"] = pd.to_numeric(d["n_events"], errors="coerce")
    ob = int(pd.to_numeric(d["ob"], errors="coerce").iloc[0])
    diffuse_gate = bool(d.loc[d["variable"].eq("all_tangential"), "event_conditioned_gate"].any())
    spatial = d[d["family"].isin(SPATIAL_CONTRAST_FAMILIES)].copy()
    spatial_gates = spatial[spatial["event_conditioned_gate"]].copy()
    levels = d[d["family"].isin(["radial_level", "density_level"])].copy()
    level_gates = levels[levels["event_conditioned_gate"]].copy()

    best_spatial = (
        spatial.sort_values("event_minus_non_event_abs_direction_z", ascending=False).iloc[0].to_dict()
        if not spatial.empty
        else {}
    )
    best_level = (
        levels.sort_values("event_minus_non_event_abs_direction_z", ascending=False).iloc[0].to_dict()
        if not levels.empty
        else {}
    )

    if len(spatial_gates) >= 1 and diffuse_gate:
        cls = "localized_or_gradient_signal_candidate"
        interp = "At least one direct spatial contrast/gradient is event-conditioned in this observation."
    elif len(level_gates) >= 1 and diffuse_gate:
        cls = "level_specific_but_no_direct_contrast"
        interp = "Some spatial levels pass, but direct contrast/gradient variables do not pass."
    elif diffuse_gate:
        cls = "diffuse_without_spatial_taxonomy"
        interp = "The global local-tangential signal passes, but spatial decomposition does not localize it."
    else:
        cls = "no_clear_t1_spatial_signal_in_this_node"
        interp = "The 4084 processing did not reproduce an event-conditioned diffuse or localized signal."

    return {
        "ob": ob,
        "n_events": int(np.nanmax(d["n_events"].to_numpy(dtype="float64"))) if len(d) else 0,
        "diffuse_baseline_gate": diffuse_gate,
        "n_spatial_contrast_gates": int(len(spatial_gates)),
        "best_spatial_variable": best_spatial.get("variable", ""),
        "best_spatial_family": best_spatial.get("family", ""),
        "best_spatial_gap_z": float(best_spatial.get("event_minus_non_event_abs_direction_z", math.nan)),
        "best_level_variable": best_level.get("variable", ""),
        "best_level_family": best_level.get("family", ""),
        "best_level_gap_z": float(best_level.get("event_minus_non_event_abs_direction_z", math.nan)),
        "ob_spatial_class": cls,
        "interpretation": interp,
    }


def aggregate_variable(rows: list[dict[str, object]], n_ob: int) -> list[dict[str, object]]:
    d = pd.DataFrame(rows)
    if d.empty:
        return []
    d["event_conditioned_gate"] = d["event_conditioned_gate"].map(bool_from_csv)
    for col in [
        "event_minus_non_event_abs_direction_z",
        "real_abs_direction_contrast_z",
        "real_direction_contrast_z",
    ]:
        d[col] = pd.to_numeric(d[col], errors="coerce")
    out = []
    majority_n = int(math.floor(n_ob / 2) + 1)
    for (var, fam), g in d.groupby(["variable", "family"], sort=True):
        gates = g[g["event_conditioned_gate"]]
        gate_count = int(len(gates))
        sign_cons = sign_consistency(gates["real_direction_contrast_z"]) if gate_count else math.nan
        majority = bool(gate_count >= majority_n)
        if majority and fam in SPATIAL_CONTRAST_FAMILIES and np.isfinite(sign_cons) and sign_cons >= 0.65:
            interp = "majority spatial contrast/gradient candidate"
        elif majority and fam in SPATIAL_CONTRAST_FAMILIES:
            interp = "majority count but signed spatial direction is inconsistent"
        elif majority:
            interp = "majority event-conditioned level/diffuse signal"
        elif gate_count > 0:
            interp = "minority or observation-specific signal"
        else:
            interp = "no event-conditioned gate"
        out.append(
            {
                "variable": var,
                "family": fam,
                "n_ob_tested": n_ob,
                "gate_count": gate_count,
                "gate_fraction": gate_count / n_ob if n_ob else math.nan,
                "median_event_minus_non_event_abs_direction_z": finite_median(g["event_minus_non_event_abs_direction_z"]),
                "median_real_abs_direction_contrast_z": finite_median(g["real_abs_direction_contrast_z"]),
                "signed_direction_sign_consistency": sign_cons,
                "majority_gate": majority,
                "interpretation": interp,
            }
        )
    return sorted(out, key=lambda r: (int(r["gate_count"]), float(r["median_event_minus_non_event_abs_direction_z"])), reverse=True)


def make_figures(rows: pd.DataFrame, ob_classes: pd.DataFrame, variables: pd.DataFrame) -> None:
    fig_dir = OUT / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    if not rows.empty:
        pivot = rows.pivot_table(
            index="variable",
            columns="ob",
            values="event_minus_non_event_abs_direction_z",
            aggfunc="first",
        )
        order = variables["variable"].tolist() if not variables.empty else pivot.index.tolist()
        pivot = pivot.reindex([v for v in order if v in pivot.index])
        fig, ax = plt.subplots(figsize=(11.5, max(4.5, 0.36 * len(pivot) + 1.2)), constrained_layout=True)
        im = ax.imshow(pivot.to_numpy(dtype="float64"), aspect="auto", cmap="RdYlGn", vmin=-0.25, vmax=0.70)
        ax.set_title("4084 spatial taxonomy: event-control direction gap")
        ax.set_xlabel("Observation")
        ax.set_ylabel("Spatial variable")
        ax.set_xticks(np.arange(len(pivot.columns)))
        ax.set_xticklabels([f"Ob{int(x)}" for x in pivot.columns], rotation=45, ha="right")
        ax.set_yticks(np.arange(len(pivot.index)))
        ax.set_yticklabels(pivot.index)
        fig.colorbar(im, ax=ax, label="event - non-event abs direction gap (z)")
        fig.savefig(fig_dir / "4084_spatial_gap_heatmap.png", dpi=180)
        plt.close(fig)

    if not variables.empty:
        d = variables.sort_values(["gate_count", "median_event_minus_non_event_abs_direction_z"], ascending=True)
        colors = [
            "#2f6f9f" if fam in SPATIAL_CONTRAST_FAMILIES else "#7f8f35" if fam.endswith("level") else "#7b5ea7"
            for fam in d["family"]
        ]
        fig, ax = plt.subplots(figsize=(9.4, max(4.5, 0.34 * len(d) + 1.4)), constrained_layout=True)
        y = np.arange(len(d))
        ax.barh(y, d["gate_count"], color=colors)
        ax.set_yticks(y)
        ax.set_yticklabels(d["variable"])
        ax.set_xlabel("number of observations passing event-conditioned gate")
        ax.set_title("4084 replicated spatial candidates")
        majority_line = math.floor(float(d["n_ob_tested"].iloc[0]) / 2) + 1 if len(d) else 1
        ax.axvline(majority_line, color="#444444", linestyle="--", linewidth=1)
        ax.grid(axis="x", color="#dddddd", linewidth=0.8)
        fig.savefig(fig_dir / "4084_variable_gate_counts.png", dpi=180)
        plt.close(fig)

    if not ob_classes.empty:
        fig, ax = plt.subplots(figsize=(9.0, 4.8), constrained_layout=True)
        colors = {
            "localized_or_gradient_signal_candidate": "#2f6f9f",
            "level_specific_but_no_direct_contrast": "#7f8f35",
            "diffuse_without_spatial_taxonomy": "#d97904",
            "no_clear_t1_spatial_signal_in_this_node": "#777777",
        }
        ax.bar(
            ob_classes["ob"].astype(int),
            pd.to_numeric(ob_classes["n_spatial_contrast_gates"], errors="coerce"),
            color=[colors.get(str(x), "#777777") for x in ob_classes["ob_spatial_class"]],
        )
        ax.set_xticks(ob_classes["ob"].astype(int))
        ax.set_xlabel("Observation")
        ax.set_ylabel("spatial contrast/gradient gates")
        ax.set_title("4084 per-observation spatial localization evidence")
        ax.grid(axis="y", color="#dddddd", linewidth=0.8)
        fig.savefig(fig_dir / "4084_ob_spatial_classes.png", dpi=180)
        plt.close(fig)


def decide(variable_rows: list[dict[str, object]], ob_rows: list[dict[str, object]], n_ob: int) -> dict[str, object]:
    vars_df = pd.DataFrame(variable_rows)
    obs_df = pd.DataFrame(ob_rows)
    majority_n = int(math.floor(n_ob / 2) + 1)
    spatial_majority = vars_df[
        (vars_df["family"].isin(SPATIAL_CONTRAST_FAMILIES))
        & (vars_df["gate_count"].astype(int) >= majority_n)
        & (pd.to_numeric(vars_df["signed_direction_sign_consistency"], errors="coerce") >= 0.65)
    ].copy()
    level_majority = vars_df[
        (vars_df["family"].isin(["radial_level", "density_level"]))
        & (vars_df["gate_count"].astype(int) >= majority_n)
    ].copy()
    diffuse = vars_df[vars_df["variable"].eq("all_tangential")].copy()
    diffuse_count = int(diffuse["gate_count"].iloc[0]) if not diffuse.empty else 0
    localized_obs = int((obs_df["ob_spatial_class"] == "localized_or_gradient_signal_candidate").sum()) if not obs_df.empty else 0

    if n_ob < 5:
        result = "pilot_spatial_taxonomy_screen_only"
        next_node = "expand_4084_to_robust_survivor_observations"
        interpretation = (
            "Fewer than five observations were tested, so this run is a screen only. "
            "Use it to decide whether to expand, not as replicated spatial evidence."
        )
    elif not spatial_majority.empty:
        best = spatial_majority.sort_values(
            ["gate_count", "median_event_minus_non_event_abs_direction_z"], ascending=False
        ).iloc[0]
        result = "support_replicated_edge_core_spatial_contrast_with_boundaries"
        next_node = "4085_event_phase_profile_of_t1_signal"
        interpretation = (
            f"`{best['variable']}` provides a majority-replicated direct spatial contrast/gradient. "
            "This supports an edge/core spatial contrast with boundaries, not a full universal spatial taxonomy. "
            "Continue by asking when this spatially structured signal appears around the transition."
        )
    elif not level_majority.empty and diffuse_count >= majority_n:
        best = level_majority.sort_values(
            ["gate_count", "median_event_minus_non_event_abs_direction_z"], ascending=False
        ).iloc[0]
        result = "boundary_level_specific_but_no_direct_spatial_contrast"
        next_node = "4085_event_phase_profile_of_t1_signal"
        interpretation = (
            f"`{best['variable']}` passes in a majority, but no direct contrast/gradient does. "
            "Treat this as weak localization and move to timing before making a spatial claim."
        )
    elif diffuse_count >= majority_n:
        result = "boundary_diffuse_t1_signal_without_stable_spatial_taxonomy"
        next_node = "4085_event_phase_profile_of_t1_signal"
        interpretation = (
            "The diffuse local-tangential signal is replicated, but 4084 does not localize it. "
            "The next defensible move is event-phase profiling, not propagation modeling."
        )
    else:
        result = "boundary_4084_processing_does_not_reproduce_stable_t1_signal"
        next_node = "4085_event_phase_profile_or_review_4084_metric_definition"
        interpretation = (
            "4084 did not reproduce a stable diffuse or localized signal under this spatial decomposition. "
            "This is a boundary on the current local spatial-taxonomy metric."
        )

    return {
        "node": NODE,
        "date": DATE,
        "result": result,
        "n_observations": n_ob,
        "majority_gate_count": majority_n,
        "diffuse_baseline_gate_count": diffuse_count,
        "localized_observation_count": localized_obs,
        "majority_spatial_candidates": spatial_majority["variable"].astype(str).tolist() if not spatial_majority.empty else [],
        "majority_level_candidates": level_majority["variable"].astype(str).tolist() if not level_majority.empty else [],
        "interpretation": interpretation,
        "next": [next_node],
        "artifacts": [
            "Output/4084/spatial_taxonomy_condition_rows.csv",
            "Output/4084/ob_spatial_taxonomy.csv",
            "Output/4084/variable_spatial_taxonomy.csv",
            "Output/4084/figures/4084_spatial_gap_heatmap.png",
            "Output/4084/figures/4084_variable_gate_counts.png",
            "Output/4084/figures/4084_ob_spatial_classes.png",
        ],
    }


def write_config(args: argparse.Namespace, obs: list[int]) -> None:
    text = dedent(
        f"""\
        node: {NODE}
        date: {DATE}
        node_type: mechanism
        input_nodes:
          - 4081c_full_observation_adjudication_before_4082
          - 4082_scale_robustness_on_surviving_observation_class
          - 4082b_early_failure_condition_or_artifact_audit
        observations: {','.join(str(x) for x in obs)}
        observation_policy: robust survivors from 4082b unless overridden
        k: {args.k}
        lag_sec: {args.lag}
        frame_stride: {args.frame_stride}
        max_focals_per_frame: {args.max_focals_per_frame}
        smooth_window_sec: {args.smooth_window_sec}
        n_non_event_replicates: {args.n_replicates}
        prepost_sec: {args.prepost_sec}
        exclusion_sec: {args.exclusion_sec}
        gap_gate_z: {args.gap_gate}
        p_gate: {args.p_gate}
        """
    )
    (OUT / "config.yaml").write_text(text, encoding="utf-8")


def write_summary(
    decision: dict[str, object],
    ob_rows: list[dict[str, object]],
    variable_rows: list[dict[str, object]],
    args: argparse.Namespace,
) -> None:
    ob_display = [
        "ob",
        "n_events",
        "diffuse_baseline_gate",
        "n_spatial_contrast_gates",
        "best_spatial_variable",
        "best_spatial_gap_z",
        "best_level_variable",
        "best_level_gap_z",
        "ob_spatial_class",
    ]
    var_display = [
        "variable",
        "family",
        "gate_count",
        "gate_fraction",
        "median_event_minus_non_event_abs_direction_z",
        "signed_direction_sign_consistency",
        "majority_gate",
        "interpretation",
    ]
    text = dedent(
        f"""\
        # Node 4084 Summary

        ## Question

        Where in the swarm does the robust T1 local non-affine event signal live:
        core, edge, radial shell gradient, local-density condition, or diffuse field?

        ## Inputs

        - `Output/4082b/decision.json`
        - transition events from `Output/3045/tables/transition_events.csv`
        - raw trajectories through the configured data directory

        ## Method

        For each observation, 4084 keeps the 4081/4082 local-affine setup:

        ```text
        k = {args.k}
        lag = {args.lag} sec
        frame_stride = {args.frame_stride}
        max_focals_per_frame = {args.max_focals_per_frame}
        matched non-event replicates = {args.n_replicates}
        ```

        It then decomposes the focal-neighborhood tangential residual by:

        - radial shell: core / middle / edge;
        - local density proxy: low / middle / high kNN distance;
        - direct contrasts or gradients: edge-minus-core, sparse-minus-dense,
          radius correlation, and kNN-distance correlation.

        ## Decision

        `{decision["result"]}`

        ## Main Reading

        {decision["interpretation"]}

        ```text
        observations tested = {decision["n_observations"]}
        majority gate count = {decision["majority_gate_count"]}
        diffuse baseline gate count = {decision["diffuse_baseline_gate_count"]}
        localized observation count = {decision["localized_observation_count"]}
        ```

        ## Variable-Level Summary

        {md_table(variable_rows, var_display)}

        ## Observation-Level Summary

        {md_table(ob_rows, ob_display)}

        ## Boundary

        A direct spatial taxonomy is supported only by contrast/gradient
        variables, not by a shell-level variable alone. If only shell or density
        levels pass, the safer reading is that the signal is present in those
        regions but not yet localized by a clean spatial contrast.

        ## Next

        `{decision["next"][0]}`

        ## Artifacts

        - `Output/4084/spatial_taxonomy_condition_rows.csv`
        - `Output/4084/ob_spatial_taxonomy.csv`
        - `Output/4084/variable_spatial_taxonomy.csv`
        - `Output/4084/figures/4084_spatial_gap_heatmap.png`
        - `Output/4084/figures/4084_variable_gate_counts.png`
        - `Output/4084/figures/4084_ob_spatial_classes.png`
        """
    ).lstrip()
    summary = "\n".join(line[8:] if line.startswith("        ") else line for line in text.splitlines()) + "\n"
    (OUT / "4084_summary.md").write_text(summary, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default=BaseRunConfig.data_dir)
    parser.add_argument("--obs", default="robust")
    parser.add_argument("--k", type=int, default=8)
    parser.add_argument("--lag", type=float, default=0.10)
    parser.add_argument("--frame-stride", type=int, default=2)
    parser.add_argument("--max-focals-per-frame", type=int, default=24)
    parser.add_argument("--n-replicates", type=int, default=40)
    parser.add_argument("--prepost-sec", type=float, default=0.20)
    parser.add_argument("--exclusion-sec", type=float, default=0.80)
    parser.add_argument("--smooth-window-sec", type=float, default=1.00)
    parser.add_argument("--gap-gate", type=float, default=0.03)
    parser.add_argument("--p-gate", type=float, default=0.35)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    data_dir = resolve_data_dir(BaseRunConfig(data_dir=args.data_dir))
    events = r4002a.read_events()
    obs = parse_obs(args.obs, events)
    write_config(args, obs)

    all_rows: list[dict[str, object]] = []
    ob_rows: list[dict[str, object]] = []
    for ob in obs:
        rows, decision, _ = run_ob(
            ob=ob,
            data_dir=data_dir,
            events_all=events,
            k=args.k,
            lag_sec=args.lag,
            frame_stride=args.frame_stride,
            max_focals_per_frame=args.max_focals_per_frame,
            n_replicates=args.n_replicates,
            prepost_sec=args.prepost_sec,
            exclusion_sec=args.exclusion_sec,
            smooth_window_sec=args.smooth_window_sec,
            gap_gate=args.gap_gate,
            p_gate=args.p_gate,
            force=args.force,
        )
        all_rows.extend(rows)
        ob_rows.append(decision["classification"])

    variable_rows = aggregate_variable(all_rows, len(obs))
    decision = decide(variable_rows, ob_rows, len(obs))

    write_csv(OUT / "spatial_taxonomy_condition_rows.csv", all_rows, ROW_COLUMNS)
    write_csv(OUT / "tables" / "spatial_taxonomy_condition_rows.csv", all_rows, ROW_COLUMNS)
    write_json(OUT / "spatial_taxonomy_condition_rows.json", all_rows)
    write_csv(OUT / "ob_spatial_taxonomy.csv", ob_rows, OB_COLUMNS)
    write_csv(OUT / "tables" / "ob_spatial_taxonomy.csv", ob_rows, OB_COLUMNS)
    write_json(OUT / "ob_spatial_taxonomy.json", ob_rows)
    write_csv(OUT / "variable_spatial_taxonomy.csv", variable_rows, VARIABLE_COLUMNS)
    write_csv(OUT / "tables" / "variable_spatial_taxonomy.csv", variable_rows, VARIABLE_COLUMNS)
    write_json(OUT / "variable_spatial_taxonomy.json", variable_rows)
    write_json(OUT / "decision.json", decision)

    make_figures(pd.DataFrame(all_rows), pd.DataFrame(ob_rows), pd.DataFrame(variable_rows))
    write_summary(decision, ob_rows, variable_rows, args)
    print(f"Wrote 4084 outputs to {OUT.relative_to(ROOT)}")
    print(json.dumps(decision, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
