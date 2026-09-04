"""4121 same-current-state / different-history matched test.

This node tests whether the frozen T1 activity differs between frames that
share nearly the same instantaneous C,dCdt,R state but have contrasting recent
C-R state-path directions.

It uses the state-path frame table created by 4120. The primary history feature
is h=0.50 sec theta_h. No event labels are used in the primary matching.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent

import numpy as np
import pandas as pd

try:
    from scipy.spatial import cKDTree
except Exception as exc:  # pragma: no cover - runtime dependency check
    cKDTree = None
    SCIPY_IMPORT_ERROR = exc
else:
    SCIPY_IMPORT_ERROR = None

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4121"
DATE = "2026-08-27"
RNG_SEED = 4121_20260827

STATE_PATH_FRAME = ROOT / "Output" / "4120" / "state_path_frame.csv"

NODE = "4121_same_current_state_different_history_matched_test"
UPSTREAM_NODE = "4120_state_path_feasibility_coordinate_freeze"
ACTIVITY_COL = "A_swarm_tangential_z"
STATE_COLS = ["C", "dCdt", "R"]

PAIR_COLUMNS = [
    "ob",
    "dataset",
    "pair_id",
    "i_local",
    "j_local",
    "t_i",
    "t_j",
    "temporal_sep_sec",
    "state_distance",
    "abs_std_diff_C",
    "abs_std_diff_dCdt",
    "abs_std_diff_R",
    "theta_i",
    "theta_j",
    "theta_diff_deg",
    "axis_score_i",
    "axis_score_j",
    "A_i",
    "A_j",
    "abs_delta_A_z",
    "signed_axis_delta_A_z",
    "axis_high_t",
    "axis_low_t",
]

OBS_COLUMNS = [
    "ob",
    "dataset",
    "n_frames_total",
    "n_frames_valid",
    "usable_frame_fraction",
    "n_state_pairs",
    "n_contrasting_pairs",
    "n_selected_pairs",
    "sufficient_pairs",
    "n_unique_frames_in_pairs",
    "paired_frame_fraction",
    "median_state_distance",
    "q95_state_distance",
    "median_theta_diff_deg",
    "median_temporal_sep_sec",
    "median_abs_delta_A_z",
    "median_signed_axis_delta_A_z",
    "mean_signed_axis_delta_A_z",
    "fraction_signed_positive",
    "null_median_abs_signed_axis_delta_A_z",
    "null_q95_abs_signed_axis_delta_A_z",
    "real_minus_null_median_abs_effect",
    "real_beats_null_median_abs",
    "real_beats_null_q95_abs",
]

NULL_COLUMNS = [
    "ob",
    "dataset",
    "shuffle_rep",
    "n_selected_pairs",
    "sufficient_pairs",
    "median_signed_axis_delta_A_z",
    "median_abs_signed_axis_delta_A_z",
    "median_abs_delta_A_z",
]

MATCHING_QC_COLUMNS = [
    "ob",
    "dataset",
    "n_frames_valid",
    "n_state_pairs_within_primary_radius",
    "n_contrasting_pairs_before_anchor_cap",
    "n_selected_pairs",
    "anchor_count_with_pair",
    "anchor_fraction_with_pair",
    "median_state_distance",
    "q95_state_distance",
    "median_theta_diff_deg",
    "min_temporal_sep_sec",
]

SENS_COLUMNS = [
    "history_window_sec",
    "state_distance_threshold",
    "history_angle_threshold_deg",
    "axis_angle_rad",
    "n_observations",
    "n_observations_sufficient",
    "total_selected_pairs",
    "median_selected_pairs_per_ob",
    "median_state_distance",
    "median_theta_diff_deg",
    "median_abs_ob_signed_effect",
    "median_ob_signed_effect",
    "direction_consistency_fraction",
]


@dataclass
class ObData:
    ob: int
    dataset: str
    n_total: int
    local_index: np.ndarray
    t: np.ndarray
    a: np.ndarray
    state_raw: np.ndarray
    state_z: np.ndarray
    theta_by_h: dict[int, np.ndarray]
    valid_by_h: dict[int, np.ndarray]
    pair_i: np.ndarray
    pair_j: np.ndarray
    pair_dist: np.ndarray
    pair_dt: np.ndarray
    pair_absdiff: np.ndarray


@dataclass
class PairSelection:
    pair_i: np.ndarray
    pair_j: np.ndarray
    state_dist: np.ndarray
    temporal_sep: np.ndarray
    theta_diff: np.ndarray
    axis_score_i: np.ndarray
    axis_score_j: np.ndarray
    abs_delta_a: np.ndarray
    signed_axis_delta_a: np.ndarray
    pair_absdiff: np.ndarray


def ensure_dirs() -> None:
    (OUT / "figures").mkdir(parents=True, exist_ok=True)
    (OUT / "tables").mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, df: pd.DataFrame, columns: list[str] | None = None) -> None:
    if columns is not None:
        df = df.reindex(columns=columns)
    df.to_csv(path, index=False)


def robust_scale(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    arr = np.asarray(values, dtype="float64")
    med = np.nanmedian(arr, axis=0)
    mad = np.nanmedian(np.abs(arr - med.reshape(1, -1)), axis=0)
    scale = 1.4826 * mad
    bad = ~np.isfinite(scale) | (scale <= 1e-12)
    if np.any(bad):
        fallback = np.nanstd(arr, axis=0)
        scale[bad] = fallback[bad]
    bad = ~np.isfinite(scale) | (scale <= 1e-12)
    scale[bad] = 1.0
    return med, scale


def parse_bool(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False)
    return series.astype(str).str.lower().isin(["true", "1", "yes"])


def circular_abs_diff(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.abs(np.angle(np.exp(1j * (a - b))))


def axial_orientation(theta: np.ndarray) -> float:
    vals = np.asarray(theta, dtype="float64")
    vals = vals[np.isfinite(vals)]
    if vals.size == 0:
        return math.nan
    return float(0.5 * math.atan2(float(np.nanmean(np.sin(2 * vals))), float(np.nanmean(np.cos(2 * vals)))))


def safe_float(value: object) -> float:
    try:
        out = float(value)
    except Exception:
        return math.nan
    return out if math.isfinite(out) else math.nan


def md_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in rows:
        vals: list[str] = []
        for col in columns:
            val = row.get(col, "")
            if isinstance(val, (float, np.floating)):
                vals.append("NA" if not math.isfinite(float(val)) else f"{float(val):.4g}")
            else:
                vals.append(str(val).replace("\n", " ").replace("|", "\\|"))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def load_frame() -> pd.DataFrame:
    if not STATE_PATH_FRAME.exists():
        raise FileNotFoundError(f"Missing 4120 frame file: {STATE_PATH_FRAME}")
    df = pd.read_csv(STATE_PATH_FRAME)
    for col in ["ob", "t", ACTIVITY_COL, *STATE_COLS]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["ob"] = df["ob"].astype("Int64")
    for h_ms in [250, 500, 750]:
        df[f"h{h_ms}_theta_h"] = pd.to_numeric(df[f"h{h_ms}_theta_h"], errors="coerce")
        df[f"h{h_ms}_theta_valid"] = parse_bool(df[f"h{h_ms}_theta_valid"])
        df[f"h{h_ms}_path_feature_valid"] = parse_bool(df[f"h{h_ms}_path_feature_valid"])
    return df.dropna(subset=["ob", "t"]).sort_values(["ob", "t"]).reset_index(drop=True)


def valid_mask_for_h(df: pd.DataFrame, h_ms: int) -> pd.Series:
    return (
        np.isfinite(df[ACTIVITY_COL])
        & np.isfinite(df["C"])
        & np.isfinite(df["dCdt"])
        & np.isfinite(df["R"])
        & np.isfinite(df[f"h{h_ms}_theta_h"])
        & df[f"h{h_ms}_theta_valid"]
        & df[f"h{h_ms}_path_feature_valid"]
    )


def build_ob_data(
    df: pd.DataFrame,
    *,
    max_state_distance: float,
    min_temporal_sep_sec: float,
) -> dict[int, ObData]:
    if cKDTree is None:
        raise RuntimeError(f"scipy.spatial.cKDTree unavailable: {SCIPY_IMPORT_ERROR}")

    obs: dict[int, ObData] = {}
    primary_possible = valid_mask_for_h(df, 500)
    for ob, raw in df.groupby("ob", sort=True):
        ob_int = int(ob)
        valid = raw[primary_possible.loc[raw.index]].copy()
        if valid.empty:
            continue
        state_raw = valid[STATE_COLS].to_numpy(dtype="float64")
        center, scale = robust_scale(state_raw)
        state_z = (state_raw - center.reshape(1, -1)) / scale.reshape(1, -1)
        finite = np.all(np.isfinite(state_z), axis=1)
        valid = valid.iloc[np.flatnonzero(finite)].copy()
        state_raw = state_raw[finite]
        state_z = state_z[finite]
        local_index = np.arange(len(valid), dtype="int64")
        t = valid["t"].to_numpy(dtype="float64")
        a = valid[ACTIVITY_COL].to_numpy(dtype="float64")
        theta_by_h = {
            h: valid[f"h{h}_theta_h"].to_numpy(dtype="float64")
            for h in [250, 500, 750]
        }
        valid_by_h = {
            h: (
                np.isfinite(theta_by_h[h])
                & valid[f"h{h}_theta_valid"].to_numpy(dtype=bool)
                & valid[f"h{h}_path_feature_valid"].to_numpy(dtype=bool)
            )
            for h in [250, 500, 750]
        }

        tree = cKDTree(state_z)
        pairs = tree.query_pairs(r=max_state_distance, output_type="ndarray")
        if pairs.size == 0:
            pair_i = np.asarray([], dtype="int64")
            pair_j = np.asarray([], dtype="int64")
            pair_dist = np.asarray([], dtype="float64")
            pair_dt = np.asarray([], dtype="float64")
            pair_absdiff = np.empty((0, 3), dtype="float64")
        else:
            pair_i = pairs[:, 0].astype("int64")
            pair_j = pairs[:, 1].astype("int64")
            pair_dt = np.abs(t[pair_j] - t[pair_i])
            keep = pair_dt >= min_temporal_sep_sec
            pair_i = pair_i[keep]
            pair_j = pair_j[keep]
            pair_dt = pair_dt[keep]
            pair_absdiff = np.abs(state_z[pair_j] - state_z[pair_i])
            pair_dist = np.sqrt(np.sum(pair_absdiff * pair_absdiff, axis=1))

        obs[ob_int] = ObData(
            ob=ob_int,
            dataset=str(valid["dataset"].iloc[0]),
            n_total=len(raw),
            local_index=local_index,
            t=t,
            a=a,
            state_raw=state_raw,
            state_z=state_z,
            theta_by_h=theta_by_h,
            valid_by_h=valid_by_h,
            pair_i=pair_i,
            pair_j=pair_j,
            pair_dist=pair_dist,
            pair_dt=pair_dt,
            pair_absdiff=pair_absdiff,
        )
    return obs


def select_pairs(
    ob: ObData,
    *,
    theta: np.ndarray,
    axis_angle: float,
    state_distance_threshold: float,
    history_angle_threshold_deg: float,
    min_temporal_sep_sec: float,
    max_pairs_per_anchor: int,
    max_pairs_per_ob: int,
    rng: np.random.Generator | None,
) -> PairSelection:
    n_pairs = ob.pair_i.size
    if n_pairs == 0 or not math.isfinite(axis_angle):
        empty = np.asarray([], dtype="float64")
        empty_int = np.asarray([], dtype="int64")
        return PairSelection(empty_int, empty_int, empty, empty, empty, empty, empty, empty, empty, np.empty((0, 3)))

    pi = ob.pair_i
    pj = ob.pair_j
    valid = (
        (ob.pair_dist <= state_distance_threshold)
        & (ob.pair_dt >= min_temporal_sep_sec)
        & np.isfinite(theta[pi])
        & np.isfinite(theta[pj])
    )
    if not np.any(valid):
        empty = np.asarray([], dtype="float64")
        empty_int = np.asarray([], dtype="int64")
        return PairSelection(empty_int, empty_int, empty, empty, empty, empty, empty, empty, empty, np.empty((0, 3)))

    angle_diff = circular_abs_diff(theta[pi], theta[pj])
    valid &= angle_diff >= math.radians(history_angle_threshold_deg)
    idx = np.flatnonzero(valid)
    if idx.size == 0:
        empty = np.asarray([], dtype="float64")
        empty_int = np.asarray([], dtype="int64")
        return PairSelection(empty_int, empty_int, empty, empty, empty, empty, empty, empty, empty, np.empty((0, 3)))

    # Nearest contrasted-history matches per anchor reduce domination by dense state regions.
    order = np.lexsort((ob.pair_dist[idx], pi[idx]))
    idx = idx[order]
    keep = np.zeros(idx.size, dtype=bool)
    current_anchor = -1
    used_for_anchor = 0
    for pos, candidate_idx in enumerate(idx):
        anchor = int(pi[candidate_idx])
        if anchor != current_anchor:
            current_anchor = anchor
            used_for_anchor = 0
        if used_for_anchor < max_pairs_per_anchor:
            keep[pos] = True
            used_for_anchor += 1
    idx = idx[keep]
    if idx.size > max_pairs_per_ob:
        if rng is None:
            idx = idx[:max_pairs_per_ob]
        else:
            idx = np.sort(rng.choice(idx, size=max_pairs_per_ob, replace=False))

    sel_i = pi[idx]
    sel_j = pj[idx]
    sel_angle = angle_diff[idx]
    axis_score = np.cos(theta - axis_angle)
    score_i = axis_score[sel_i]
    score_j = axis_score[sel_j]
    a_i = ob.a[sel_i]
    a_j = ob.a[sel_j]
    abs_delta = np.abs(a_i - a_j)
    signed = np.where(score_i >= score_j, a_i - a_j, a_j - a_i)
    return PairSelection(
        pair_i=sel_i,
        pair_j=sel_j,
        state_dist=ob.pair_dist[idx],
        temporal_sep=ob.pair_dt[idx],
        theta_diff=sel_angle,
        axis_score_i=score_i,
        axis_score_j=score_j,
        abs_delta_a=abs_delta,
        signed_axis_delta_a=signed,
        pair_absdiff=ob.pair_absdiff[idx],
    )


def selection_summary(
    ob: ObData,
    sel: PairSelection,
    *,
    min_pairs_per_ob: int,
    n_contrasting_before_cap: int,
    min_temporal_sep_sec: float,
) -> dict[str, object]:
    n = sel.pair_i.size
    unique_frames = int(np.unique(np.concatenate([sel.pair_i, sel.pair_j])).size) if n else 0
    signed = sel.signed_axis_delta_a[np.isfinite(sel.signed_axis_delta_a)]
    return {
        "ob": ob.ob,
        "dataset": ob.dataset,
        "n_frames_total": ob.n_total,
        "n_frames_valid": int(ob.t.size),
        "usable_frame_fraction": float(ob.t.size / ob.n_total) if ob.n_total else math.nan,
        "n_state_pairs": int(np.sum((ob.pair_dist <= 0.50) & (ob.pair_dt >= min_temporal_sep_sec))),
        "n_contrasting_pairs": int(n_contrasting_before_cap),
        "n_selected_pairs": int(n),
        "sufficient_pairs": bool(n >= min_pairs_per_ob),
        "n_unique_frames_in_pairs": unique_frames,
        "paired_frame_fraction": float(unique_frames / ob.t.size) if ob.t.size else math.nan,
        "median_state_distance": float(np.nanmedian(sel.state_dist)) if n else math.nan,
        "q95_state_distance": float(np.nanquantile(sel.state_dist, 0.95)) if n else math.nan,
        "median_theta_diff_deg": float(np.nanmedian(np.degrees(sel.theta_diff))) if n else math.nan,
        "median_temporal_sep_sec": float(np.nanmedian(sel.temporal_sep)) if n else math.nan,
        "median_abs_delta_A_z": float(np.nanmedian(sel.abs_delta_a)) if n else math.nan,
        "median_signed_axis_delta_A_z": float(np.nanmedian(signed)) if signed.size else math.nan,
        "mean_signed_axis_delta_A_z": float(np.nanmean(signed)) if signed.size else math.nan,
        "fraction_signed_positive": float(np.nanmean(signed > 0)) if signed.size else math.nan,
        "null_median_abs_signed_axis_delta_A_z": math.nan,
        "null_q95_abs_signed_axis_delta_A_z": math.nan,
        "real_minus_null_median_abs_effect": math.nan,
        "real_beats_null_median_abs": math.nan,
        "real_beats_null_q95_abs": math.nan,
    }


def count_contrasting_before_cap(
    ob: ObData,
    theta: np.ndarray,
    *,
    state_distance_threshold: float,
    history_angle_threshold_deg: float,
    min_temporal_sep_sec: float,
) -> int:
    if ob.pair_i.size == 0:
        return 0
    pi = ob.pair_i
    pj = ob.pair_j
    valid = (
        (ob.pair_dist <= state_distance_threshold)
        & (ob.pair_dt >= min_temporal_sep_sec)
        & np.isfinite(theta[pi])
        & np.isfinite(theta[pj])
    )
    if not np.any(valid):
        return 0
    angle_diff = circular_abs_diff(theta[pi], theta[pj])
    valid &= angle_diff >= math.radians(history_angle_threshold_deg)
    return int(np.sum(valid))


def primary_analysis(
    obs: dict[int, ObData],
    *,
    axis_angle: float,
    state_distance_threshold: float,
    history_angle_threshold_deg: float,
    history_window_ms: int,
    history_window_sec: float,
    min_pairs_per_ob: int,
    max_pairs_per_anchor: int,
    max_pairs_per_ob: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    pair_rows: list[dict[str, object]] = []
    obs_rows: list[dict[str, object]] = []
    qc_rows: list[dict[str, object]] = []
    pair_id = 0
    min_temporal_sep_sec = max(1.0, 2.0 * history_window_sec)

    for ob_id, ob in obs.items():
        rng = np.random.default_rng(RNG_SEED + ob_id)
        theta = ob.theta_by_h[history_window_ms]
        n_contrast = count_contrasting_before_cap(
            ob,
            theta,
            state_distance_threshold=state_distance_threshold,
            history_angle_threshold_deg=history_angle_threshold_deg,
            min_temporal_sep_sec=min_temporal_sep_sec,
        )
        sel = select_pairs(
            ob,
            theta=theta,
            axis_angle=axis_angle,
            state_distance_threshold=state_distance_threshold,
            history_angle_threshold_deg=history_angle_threshold_deg,
            min_temporal_sep_sec=min_temporal_sep_sec,
            max_pairs_per_anchor=max_pairs_per_anchor,
            max_pairs_per_ob=max_pairs_per_ob,
            rng=rng,
        )
        obs_rows.append(
            selection_summary(
                ob,
                sel,
                min_pairs_per_ob=min_pairs_per_ob,
                n_contrasting_before_cap=n_contrast,
                min_temporal_sep_sec=min_temporal_sep_sec,
            )
        )
        anchor_count = int(np.unique(sel.pair_i).size) if sel.pair_i.size else 0
        qc_rows.append(
            {
                "ob": ob.ob,
                "dataset": ob.dataset,
                "n_frames_valid": int(ob.t.size),
                "n_state_pairs_within_primary_radius": int(
                    np.sum((ob.pair_dist <= state_distance_threshold) & (ob.pair_dt >= min_temporal_sep_sec))
                ),
                "n_contrasting_pairs_before_anchor_cap": n_contrast,
                "n_selected_pairs": int(sel.pair_i.size),
                "anchor_count_with_pair": anchor_count,
                "anchor_fraction_with_pair": float(anchor_count / ob.t.size) if ob.t.size else math.nan,
                "median_state_distance": float(np.nanmedian(sel.state_dist)) if sel.pair_i.size else math.nan,
                "q95_state_distance": float(np.nanquantile(sel.state_dist, 0.95)) if sel.pair_i.size else math.nan,
                "median_theta_diff_deg": float(np.nanmedian(np.degrees(sel.theta_diff))) if sel.pair_i.size else math.nan,
                "min_temporal_sep_sec": min_temporal_sep_sec,
            }
        )
        for k in range(sel.pair_i.size):
            i = int(sel.pair_i[k])
            j = int(sel.pair_j[k])
            score_i = float(sel.axis_score_i[k])
            score_j = float(sel.axis_score_j[k])
            if score_i >= score_j:
                high_t = float(ob.t[i])
                low_t = float(ob.t[j])
            else:
                high_t = float(ob.t[j])
                low_t = float(ob.t[i])
            pair_rows.append(
                {
                    "ob": ob.ob,
                    "dataset": ob.dataset,
                    "pair_id": pair_id,
                    "i_local": i,
                    "j_local": j,
                    "t_i": float(ob.t[i]),
                    "t_j": float(ob.t[j]),
                    "temporal_sep_sec": float(sel.temporal_sep[k]),
                    "state_distance": float(sel.state_dist[k]),
                    "abs_std_diff_C": float(sel.pair_absdiff[k, 0]),
                    "abs_std_diff_dCdt": float(sel.pair_absdiff[k, 1]),
                    "abs_std_diff_R": float(sel.pair_absdiff[k, 2]),
                    "theta_i": float(theta[i]),
                    "theta_j": float(theta[j]),
                    "theta_diff_deg": float(math.degrees(sel.theta_diff[k])),
                    "axis_score_i": score_i,
                    "axis_score_j": score_j,
                    "A_i": float(ob.a[i]),
                    "A_j": float(ob.a[j]),
                    "abs_delta_A_z": float(sel.abs_delta_a[k]),
                    "signed_axis_delta_A_z": float(sel.signed_axis_delta_a[k]),
                    "axis_high_t": high_t,
                    "axis_low_t": low_t,
                }
            )
            pair_id += 1
    return (
        pd.DataFrame(pair_rows, columns=PAIR_COLUMNS),
        pd.DataFrame(obs_rows, columns=OBS_COLUMNS),
        pd.DataFrame(qc_rows, columns=MATCHING_QC_COLUMNS),
    )


def shuffle_null(
    obs: dict[int, ObData],
    *,
    axis_angle: float,
    state_distance_threshold: float,
    history_angle_threshold_deg: float,
    history_window_ms: int,
    history_window_sec: float,
    min_pairs_per_ob: int,
    max_pairs_per_anchor: int,
    max_pairs_per_ob: int,
    n_shuffle_reps: int,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    min_temporal_sep_sec = max(1.0, 2.0 * history_window_sec)
    for ob_id, ob in obs.items():
        theta = ob.theta_by_h[history_window_ms].copy()
        valid_theta = np.flatnonzero(np.isfinite(theta))
        for rep in range(n_shuffle_reps):
            rng = np.random.default_rng(RNG_SEED + 100_000 + ob_id * 1000 + rep)
            shuffled = theta.copy()
            shuffled[valid_theta] = rng.permutation(shuffled[valid_theta])
            sel = select_pairs(
                ob,
                theta=shuffled,
                axis_angle=axis_angle,
                state_distance_threshold=state_distance_threshold,
                history_angle_threshold_deg=history_angle_threshold_deg,
                min_temporal_sep_sec=min_temporal_sep_sec,
                max_pairs_per_anchor=max_pairs_per_anchor,
                max_pairs_per_ob=max_pairs_per_ob,
                rng=rng,
            )
            signed = sel.signed_axis_delta_a[np.isfinite(sel.signed_axis_delta_a)]
            rows.append(
                {
                    "ob": ob.ob,
                    "dataset": ob.dataset,
                    "shuffle_rep": rep,
                    "n_selected_pairs": int(sel.pair_i.size),
                    "sufficient_pairs": bool(sel.pair_i.size >= min_pairs_per_ob),
                    "median_signed_axis_delta_A_z": float(np.nanmedian(signed)) if signed.size else math.nan,
                    "median_abs_signed_axis_delta_A_z": float(abs(np.nanmedian(signed))) if signed.size else math.nan,
                    "median_abs_delta_A_z": float(np.nanmedian(sel.abs_delta_a)) if sel.pair_i.size else math.nan,
                }
            )
    return pd.DataFrame(rows, columns=NULL_COLUMNS)


def attach_null_summary(obs_effects: pd.DataFrame, null: pd.DataFrame) -> pd.DataFrame:
    out = obs_effects.copy()
    out["real_beats_null_median_abs"] = pd.Series(pd.NA, index=out.index, dtype="boolean")
    out["real_beats_null_q95_abs"] = pd.Series(pd.NA, index=out.index, dtype="boolean")
    for ob, nd in null.groupby("ob", sort=True):
        good = nd[nd["sufficient_pairs"] == True].copy()  # noqa: E712
        if good.empty:
            continue
        vals = good["median_abs_signed_axis_delta_A_z"].to_numpy(dtype="float64")
        vals = vals[np.isfinite(vals)]
        if vals.size == 0:
            continue
        idx = out.index[out["ob"] == int(ob)]
        if idx.empty:
            continue
        real = safe_float(out.loc[idx[0], "median_signed_axis_delta_A_z"])
        real_abs = abs(real) if math.isfinite(real) else math.nan
        null_med = float(np.nanmedian(vals))
        null_q95 = float(np.nanquantile(vals, 0.95))
        out.loc[idx, "null_median_abs_signed_axis_delta_A_z"] = null_med
        out.loc[idx, "null_q95_abs_signed_axis_delta_A_z"] = null_q95
        out.loc[idx, "real_minus_null_median_abs_effect"] = real_abs - null_med if math.isfinite(real_abs) else math.nan
        out.loc[idx, "real_beats_null_median_abs"] = bool(math.isfinite(real_abs) and real_abs > null_med)
        out.loc[idx, "real_beats_null_q95_abs"] = bool(math.isfinite(real_abs) and real_abs > null_q95)
    return out


def run_sensitivity(
    obs: dict[int, ObData],
    axes_by_h: dict[int, float],
    *,
    history_windows_ms: list[int],
    state_distances: list[float],
    angle_thresholds_deg: list[float],
    min_pairs_per_ob: int,
    max_pairs_per_anchor: int,
    max_pairs_per_ob: int,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for h_ms in history_windows_ms:
        h_sec = h_ms / 1000.0
        min_temporal_sep_sec = max(1.0, 2.0 * h_sec)
        axis_angle = axes_by_h[h_ms]
        for state_dist in state_distances:
            for angle_deg in angle_thresholds_deg:
                obs_signed: list[float] = []
                obs_state_dist: list[float] = []
                obs_theta_diff: list[float] = []
                n_pairs: list[int] = []
                for ob_id, ob in obs.items():
                    theta = ob.theta_by_h[h_ms]
                    rng = np.random.default_rng(RNG_SEED + 200_000 + ob_id + int(h_ms * 10 + state_dist * 100 + angle_deg))
                    sel = select_pairs(
                        ob,
                        theta=theta,
                        axis_angle=axis_angle,
                        state_distance_threshold=state_dist,
                        history_angle_threshold_deg=angle_deg,
                        min_temporal_sep_sec=min_temporal_sep_sec,
                        max_pairs_per_anchor=max_pairs_per_anchor,
                        max_pairs_per_ob=max_pairs_per_ob,
                        rng=rng,
                    )
                    n_pairs.append(int(sel.pair_i.size))
                    if sel.pair_i.size >= min_pairs_per_ob:
                        signed = sel.signed_axis_delta_a[np.isfinite(sel.signed_axis_delta_a)]
                        if signed.size:
                            obs_signed.append(float(np.nanmedian(signed)))
                            obs_state_dist.append(float(np.nanmedian(sel.state_dist)))
                            obs_theta_diff.append(float(np.nanmedian(np.degrees(sel.theta_diff))))
                signed_arr = np.asarray(obs_signed, dtype="float64")
                signed_arr = signed_arr[np.isfinite(signed_arr)]
                if signed_arr.size:
                    frac_pos = float(np.nanmean(signed_arr > 0))
                    frac_neg = float(np.nanmean(signed_arr < 0))
                    direction_consistency = max(frac_pos, frac_neg)
                    median_signed = float(np.nanmedian(signed_arr))
                    median_abs_signed = float(np.nanmedian(np.abs(signed_arr)))
                else:
                    direction_consistency = math.nan
                    median_signed = math.nan
                    median_abs_signed = math.nan
                rows.append(
                    {
                        "history_window_sec": h_sec,
                        "state_distance_threshold": state_dist,
                        "history_angle_threshold_deg": angle_deg,
                        "axis_angle_rad": axis_angle,
                        "n_observations": len(obs),
                        "n_observations_sufficient": int(np.sum(np.asarray(n_pairs) >= min_pairs_per_ob)),
                        "total_selected_pairs": int(np.sum(n_pairs)),
                        "median_selected_pairs_per_ob": float(np.nanmedian(n_pairs)) if n_pairs else math.nan,
                        "median_state_distance": float(np.nanmedian(obs_state_dist)) if obs_state_dist else math.nan,
                        "median_theta_diff_deg": float(np.nanmedian(obs_theta_diff)) if obs_theta_diff else math.nan,
                        "median_abs_ob_signed_effect": median_abs_signed,
                        "median_ob_signed_effect": median_signed,
                        "direction_consistency_fraction": direction_consistency,
                    }
                )
    return pd.DataFrame(rows, columns=SENS_COLUMNS)


def evaluate_gate(
    obs_effects: pd.DataFrame,
    *,
    min_pairs_per_ob: int,
    min_obs_fraction_sufficient: float,
    min_abs_effect_z: float,
    min_direction_consistency_fraction: float,
    min_real_beats_null_fraction: float,
) -> dict[str, object]:
    total_obs = int(len(obs_effects))
    sufficient = obs_effects[obs_effects["sufficient_pairs"] == True].copy()  # noqa: E712
    n_sufficient = int(len(sufficient))
    min_obs_count = int(math.ceil(total_obs * min_obs_fraction_sufficient)) if total_obs else 0
    signed = sufficient["median_signed_axis_delta_A_z"].to_numpy(dtype="float64")
    signed = signed[np.isfinite(signed)]
    median_signed = float(np.nanmedian(signed)) if signed.size else math.nan
    median_abs_signed = float(np.nanmedian(np.abs(signed))) if signed.size else math.nan
    frac_pos = float(np.nanmean(signed > 0)) if signed.size else math.nan
    frac_neg = float(np.nanmean(signed < 0)) if signed.size else math.nan
    direction_consistency = max(frac_pos, frac_neg) if math.isfinite(frac_pos) and math.isfinite(frac_neg) else math.nan
    real_beats = sufficient["real_beats_null_median_abs"].dropna()
    real_beats_fraction = float(np.nanmean(real_beats.astype(bool))) if len(real_beats) else math.nan
    real_beats_q95 = sufficient["real_beats_null_q95_abs"].dropna()
    real_beats_q95_fraction = float(np.nanmean(real_beats_q95.astype(bool))) if len(real_beats_q95) else math.nan
    median_null = float(np.nanmedian(sufficient["null_median_abs_signed_axis_delta_A_z"])) if not sufficient.empty else math.nan
    median_real_minus_null = (
        float(np.nanmedian(sufficient["real_minus_null_median_abs_effect"])) if not sufficient.empty else math.nan
    )
    median_state_distance = float(np.nanmedian(sufficient["median_state_distance"])) if not sufficient.empty else math.nan
    median_pairs = float(np.nanmedian(sufficient["n_selected_pairs"])) if not sufficient.empty else math.nan
    paired_frame_fraction = float(np.nanmedian(sufficient["paired_frame_fraction"])) if not sufficient.empty else math.nan

    matching_ok = n_sufficient >= min_obs_count
    effect_ok = math.isfinite(median_abs_signed) and median_abs_signed > min_abs_effect_z
    direction_ok = (
        math.isfinite(direction_consistency)
        and direction_consistency >= min_direction_consistency_fraction
    )
    null_ok = (
        math.isfinite(real_beats_fraction)
        and real_beats_fraction >= min_real_beats_null_fraction
    )

    if not matching_ok:
        gate = "boundary_history_contrast_identifiability"
        interp = (
            "Contrasting recent-history matches were not sufficiently identifiable across observations."
        )
        next_nodes = ["4125_history_identifiability_synthesis"]
    elif effect_ok and direction_ok and null_ok:
        gate = "pass_same_state_history_dependence"
        interp = (
            "Matched current-state pairs show history-direction T1 separation that is consistent across observations "
            "and exceeds the shuffled-history null under the pre-frozen primary gate."
        )
        next_nodes = ["4122_approach_departure_directional_asymmetry"]
    elif effect_ok or null_ok:
        gate = "boundary_observation_specific_history_dependence"
        interp = (
            "Some history-conditioned separation is visible, but the effect is not strong enough across all gate criteria "
            "to claim robust same-state history dependence."
        )
        next_nodes = ["4125_observation_specific_history_synthesis"]
    else:
        gate = "fail_no_same_state_history_dependence"
        interp = (
            "After matching instantaneous C,dCdt,R, contrasting recent state-path direction does not provide a stable "
            "T1 separation under the primary test."
        )
        next_nodes = ["4125_no_path_history_information_synthesis"]

    return {
        "node": NODE,
        "date": DATE,
        "node_type": "primary_gate",
        "upstream_node": UPSTREAM_NODE,
        "data_scope": "all_19_observations",
        "frozen_target": "T1_local_tangential_nonaffine_residual",
        "activity_column": ACTIVITY_COL,
        "current_state": [
            "C_density_rms_z3045",
            "dCdt_gradient_density_rms_smooth3045",
            "R_r_rms_z3045",
        ],
        "history_feature": "h500_theta_h",
        "matching_method": "same_observation_current_state_matched_frame_pairs",
        "primary_thresholds": {
            "history_window_sec": 0.50,
            "state_distance_threshold": 0.50,
            "history_angle_threshold_deg": 90.0,
            "min_temporal_sep_sec": 1.0,
            "max_pairs_per_anchor": 5,
            "max_pairs_per_ob": 10000,
            "min_pairs_per_ob": min_pairs_per_ob,
        },
        "nulls": [
            "within_observation_history_theta_shuffle_recompute_contrasting_pairs",
        ],
        "primary_metrics": {
            "n_observations_total": total_obs,
            "n_observations_sufficient_pairs": n_sufficient,
            "min_observations_required": min_obs_count,
            "median_selected_pairs_per_sufficient_observation": median_pairs,
            "median_paired_frame_fraction": paired_frame_fraction,
            "median_state_distance": median_state_distance,
            "median_observation_signed_axis_delta_A_z": median_signed,
            "median_abs_observation_signed_axis_delta_A_z": median_abs_signed,
            "direction_consistency_fraction": direction_consistency,
            "real_beats_shuffle_null_median_abs_fraction": real_beats_fraction,
            "real_beats_shuffle_null_q95_abs_fraction": real_beats_q95_fraction,
            "median_shuffle_null_abs_signed_axis_delta_A_z": median_null,
            "median_real_minus_shuffle_null_abs_effect": median_real_minus_null,
        },
        "pre_frozen_gates": {
            "min_obs_fraction_sufficient": min_obs_fraction_sufficient,
            "min_abs_effect_z": min_abs_effect_z,
            "min_direction_consistency_fraction": min_direction_consistency_fraction,
            "min_real_beats_null_fraction": min_real_beats_null_fraction,
        },
        "gate_result": gate,
        "interpretation": interp,
        "does_not_prove": [
            "causal memory mechanism",
            "thermodynamic hysteresis",
            "transition trigger",
            "out-of-sample history gain",
            "network propagation",
        ],
        "next": next_nodes,
        "artifacts": [
            "Output/4121/state_matched_history_pairs.csv",
            "Output/4121/matching_quality.csv",
            "Output/4121/observation_level_effects.csv",
            "Output/4121/history_shuffle_null.csv",
            "Output/4121/sensitivity.csv",
            "Output/4121/figures/",
            "Output/4121/decision.json",
            "Output/4121/4121_summary.md",
        ],
    }


def make_figures(
    obs_effects: pd.DataFrame,
    matching_qc: pd.DataFrame,
    null: pd.DataFrame,
    sensitivity: pd.DataFrame,
) -> None:
    if obs_effects.empty:
        return

    fig, axes = plt.subplots(2, 2, figsize=(14, 8), constrained_layout=True)
    x = np.arange(len(obs_effects))
    labels = [f"Ob{int(v)}" for v in obs_effects["ob"]]
    axes[0, 0].bar(x, obs_effects["n_selected_pairs"], color="#4e79a7")
    axes[0, 0].axhline(100, color="black", ls="--", lw=1)
    axes[0, 0].set_title("selected contrasted-history pairs")
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=45, ha="right")
    axes[0, 0].set_ylabel("pairs")

    axes[0, 1].bar(x, obs_effects["median_state_distance"], color="#59a14f")
    axes[0, 1].axhline(0.50, color="black", ls="--", lw=1)
    axes[0, 1].set_title("median current-state distance")
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=45, ha="right")

    axes[1, 0].bar(x, obs_effects["median_theta_diff_deg"], color="#f28e2b")
    axes[1, 0].axhline(90, color="black", ls="--", lw=1)
    axes[1, 0].set_title("median history angle difference")
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(labels, rotation=45, ha="right")
    axes[1, 0].set_ylabel("deg")

    colors = ["#4e79a7" if v >= 0 else "#e15759" for v in obs_effects["median_signed_axis_delta_A_z"]]
    axes[1, 1].bar(x, obs_effects["median_signed_axis_delta_A_z"], color=colors)
    axes[1, 1].axhline(0, color="black", lw=1)
    axes[1, 1].axhline(0.05, color="black", ls="--", lw=1)
    axes[1, 1].axhline(-0.05, color="black", ls="--", lw=1)
    axes[1, 1].set_title("axis-signed T1 separation")
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(labels, rotation=45, ha="right")
    axes[1, 1].set_ylabel("z")
    fig.suptitle("4121 primary same-state / different-history QC")
    fig.savefig(OUT / "figures" / "4121_primary_matching_and_effects.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 5), constrained_layout=True)
    real_abs = np.abs(obs_effects["median_signed_axis_delta_A_z"].to_numpy(dtype="float64"))
    null_med = obs_effects["null_median_abs_signed_axis_delta_A_z"].to_numpy(dtype="float64")
    null_q95 = obs_effects["null_q95_abs_signed_axis_delta_A_z"].to_numpy(dtype="float64")
    ax.bar(x - 0.2, real_abs, width=0.4, label="real |signed effect|", color="#4e79a7")
    ax.bar(x + 0.2, null_med, width=0.4, label="shuffle null median", color="#bab0ac")
    ax.scatter(x, null_q95, marker="_", s=120, color="black", label="shuffle null q95")
    ax.axhline(0.05, color="black", ls="--", lw=1, label="0.05 z gate")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_ylabel("|axis-signed median effect|")
    ax.set_title("4121 real effect vs shuffled-history null")
    ax.legend(frameon=False)
    fig.savefig(OUT / "figures" / "4121_real_vs_shuffle_null.png", dpi=180)
    plt.close(fig)

    primary_sens = sensitivity[
        (np.isclose(sensitivity["history_window_sec"], 0.5))
    ].copy()
    if not primary_sens.empty:
        pivot = primary_sens.pivot(
            index="history_angle_threshold_deg",
            columns="state_distance_threshold",
            values="median_abs_ob_signed_effect",
        )
        fig, ax = plt.subplots(figsize=(7, 5), constrained_layout=True)
        im = ax.imshow(pivot.to_numpy(dtype="float64"), origin="lower", aspect="auto", cmap="viridis")
        ax.set_xticks(np.arange(len(pivot.columns)))
        ax.set_xticklabels([f"{v:g}" for v in pivot.columns])
        ax.set_yticks(np.arange(len(pivot.index)))
        ax.set_yticklabels([f"{v:g}" for v in pivot.index])
        ax.set_xlabel("state distance threshold")
        ax.set_ylabel("history angle threshold (deg)")
        ax.set_title("4121 h=0.50 sensitivity: median abs signed effect")
        for iy in range(len(pivot.index)):
            for ix in range(len(pivot.columns)):
                val = pivot.to_numpy(dtype="float64")[iy, ix]
                if math.isfinite(val):
                    ax.text(ix, iy, f"{val:.3f}", ha="center", va="center", color="white" if val < np.nanmax(pivot.to_numpy(dtype="float64")) * 0.65 else "black")
        fig.colorbar(im, ax=ax, label="z")
        fig.savefig(OUT / "figures" / "4121_sensitivity_heatmap_h500.png", dpi=180)
        plt.close(fig)

    if not matching_qc.empty:
        fig, ax = plt.subplots(figsize=(10, 5), constrained_layout=True)
        ax.scatter(
            matching_qc["anchor_fraction_with_pair"],
            obs_effects["paired_frame_fraction"],
            s=np.maximum(20, np.sqrt(obs_effects["n_selected_pairs"].to_numpy(dtype="float64")) * 2),
            color="#76b7b2",
            edgecolor="black",
            linewidth=0.4,
        )
        for _, row in matching_qc.iterrows():
            ob = int(row["ob"])
            oe = obs_effects[obs_effects["ob"] == ob]
            if oe.empty:
                continue
            ax.text(row["anchor_fraction_with_pair"], float(oe["paired_frame_fraction"].iloc[0]), f"Ob{ob}", fontsize=8)
        ax.set_xlabel("anchor fraction with selected match")
        ax.set_ylabel("unique paired frame fraction")
        ax.set_title("4121 contrasted-history match coverage")
        fig.savefig(OUT / "figures" / "4121_match_coverage_scatter.png", dpi=180)
        plt.close(fig)


def write_config(args: argparse.Namespace, axes_by_h: dict[int, float]) -> None:
    lines = [
        f"node: {NODE}",
        f"date: {DATE}",
        f"input: {STATE_PATH_FRAME.relative_to(ROOT).as_posix()}",
        "current_state:",
        "  - C",
        "  - dCdt",
        "  - R",
        f"activity: {ACTIVITY_COL}",
        "history_axes_rad:",
    ]
    for h, val in axes_by_h.items():
        lines.append(f"  h{h}: {val}")
    lines.extend(
        [
            "primary:",
            f"  history_window_sec: {args.history_window_sec}",
            f"  state_distance_threshold: {args.state_distance_threshold}",
            f"  history_angle_threshold_deg: {args.history_angle_threshold_deg}",
            f"  min_temporal_sep_sec: {max(1.0, 2.0 * args.history_window_sec)}",
            f"  max_pairs_per_anchor: {args.max_pairs_per_anchor}",
            f"  max_pairs_per_ob: {args.max_pairs_per_ob}",
            f"  min_pairs_per_ob: {args.min_pairs_per_ob}",
            f"  n_shuffle_reps: {args.n_shuffle_reps}",
            "gates:",
            f"  min_obs_fraction_sufficient: {args.min_obs_fraction_sufficient}",
            f"  min_abs_effect_z: {args.min_abs_effect_z}",
            f"  min_direction_consistency_fraction: {args.min_direction_consistency_fraction}",
            f"  min_real_beats_null_fraction: {args.min_real_beats_null_fraction}",
        ]
    )
    (OUT / "config.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_hypotheses() -> None:
    text = dedent(
        """
        node: 4121_same_current_state_different_history_matched_test
        primary_hypothesis:
          H412_1: >
            T1 differs between frames with matched current C,dCdt,R but contrasting
            recent C-R path direction theta_h at h=0.50 sec.
        primary_target: A_swarm_tangential_z
        primary_history_feature: h500_theta_h
        primary_null:
          N0: within-observation history-theta shuffle with pair recomputation
        interpretation_rule:
          pass: >
            Only if matching coverage, effect size, direction consistency, and
            shuffled-history null criteria all pass.
          fail: >
            Stop 412x low-dimensional recent-history expansion and route to 4125.
        """
    ).strip()
    (OUT / "frozen_hypotheses.yaml").write_text(text + "\n", encoding="utf-8")


def write_summary(
    decision: dict[str, object],
    obs_effects: pd.DataFrame,
    matching_qc: pd.DataFrame,
    null: pd.DataFrame,
    sensitivity: pd.DataFrame,
    axes_by_h: dict[int, float],
) -> None:
    metrics = decision["primary_metrics"]
    top_obs = obs_effects.copy()
    if not top_obs.empty:
        top_obs["abs_effect"] = np.abs(top_obs["median_signed_axis_delta_A_z"])
        top_obs = top_obs.sort_values("abs_effect", ascending=False).head(8)
    sens_primary = sensitivity[
        np.isclose(sensitivity["history_window_sec"], 0.5)
    ].sort_values(["state_distance_threshold", "history_angle_threshold_deg"])

    parts = [
        "# Node 4121 Summary",
        "## Question\n\n"
        "Do frames with the same instantaneous `C,dCdt,R` state but different recent C-R path direction show different T1 activity?",
        "## Why This Node Exists After 4120\n\n"
        "4120 showed that recent path features are measurable, but also showed history-current leakage. "
        "Therefore 4121 uses same-observation current-state matching before interpreting any history effect.",
        "## Frozen Definitions\n\n"
        "```text\n"
        "target = A_swarm_tangential_z\n"
        "current_state = C,dCdt,R\n"
        "history = h500_theta_h\n"
        f"axis_angle_h500_rad = {axes_by_h[500]:.6g}\n"
        "state_distance <= 0.50\n"
        "history_angle_difference >= 90 deg\n"
        "temporal_separation >= 1.0 sec\n"
        "null = within-observation theta_h shuffle with pair recomputation\n"
        "```",
        "## Primary Metrics\n\n"
        + md_table(
            [
                {
                    "n_obs_sufficient": metrics["n_observations_sufficient_pairs"],
                    "median_pairs": metrics["median_selected_pairs_per_sufficient_observation"],
                    "median_state_dist": metrics["median_state_distance"],
                    "median_abs_signed_effect": metrics["median_abs_observation_signed_axis_delta_A_z"],
                    "direction_consistency": metrics["direction_consistency_fraction"],
                    "real_beats_null_fraction": metrics["real_beats_shuffle_null_median_abs_fraction"],
                    "median_real_minus_null": metrics["median_real_minus_shuffle_null_abs_effect"],
                }
            ],
            [
                "n_obs_sufficient",
                "median_pairs",
                "median_state_dist",
                "median_abs_signed_effect",
                "direction_consistency",
                "real_beats_null_fraction",
                "median_real_minus_null",
            ],
        ),
        "## Observation-level Effects\n\n" + md_table(obs_effects.to_dict("records"), OBS_COLUMNS),
        "## Largest Absolute Observation Effects\n\n"
        + md_table(
            top_obs.to_dict("records"),
            [
                "ob",
                "dataset",
                "n_selected_pairs",
                "median_signed_axis_delta_A_z",
                "null_median_abs_signed_axis_delta_A_z",
                "real_minus_null_median_abs_effect",
            ],
        ),
        "## Matching Quality\n\n" + md_table(matching_qc.to_dict("records"), MATCHING_QC_COLUMNS),
        "## Primary h=0.50 Sensitivity\n\n" + md_table(sens_primary.to_dict("records"), SENS_COLUMNS),
        "## Gate Evaluation\n\n"
        "```text\n"
        f"gate_result = {decision['gate_result']}\n"
        "```\n\n"
        f"{decision['interpretation']}",
        "## What This Supports\n\n"
        "- It directly tests recent path direction after matching current state.\n"
        "- It separates technical identifiability from a history-dependence claim.\n"
        "- It provides the required gate for deciding whether 4122 is allowed.",
        "## What This Does Not Prove\n\n"
        + md_table([{"does_not_prove": x} for x in decision["does_not_prove"]], ["does_not_prove"]),
        "## Decision\n\n" f"`{decision['gate_result']}`",
        "## Next Node\n\n" + md_table([{"next": x} for x in decision["next"]], ["next"]),
        "## Artifacts\n\n"
        "- `Output/4121/state_matched_history_pairs.csv`\n"
        "- `Output/4121/matching_quality.csv`\n"
        "- `Output/4121/observation_level_effects.csv`\n"
        "- `Output/4121/history_shuffle_null.csv`\n"
        "- `Output/4121/sensitivity.csv`\n"
        "- `Output/4121/figures/4121_primary_matching_and_effects.png`\n"
        "- `Output/4121/figures/4121_real_vs_shuffle_null.png`\n"
        "- `Output/4121/figures/4121_sensitivity_heatmap_h500.png`\n"
        "- `Output/4121/figures/4121_match_coverage_scatter.png`\n"
        "- `Output/4121/decision.json`",
    ]
    (OUT / "4121_summary.md").write_text("\n\n".join(parts) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-window-sec", type=float, default=0.50)
    parser.add_argument("--state-distance-threshold", type=float, default=0.50)
    parser.add_argument("--history-angle-threshold-deg", type=float, default=90.0)
    parser.add_argument("--max-state-distance-for-cache", type=float, default=0.75)
    parser.add_argument("--max-pairs-per-anchor", type=int, default=5)
    parser.add_argument("--max-pairs-per-ob", type=int, default=10000)
    parser.add_argument("--min-pairs-per-ob", type=int, default=100)
    parser.add_argument("--n-shuffle-reps", type=int, default=100)
    parser.add_argument("--min-obs-fraction-sufficient", type=float, default=0.75)
    parser.add_argument("--min-abs-effect-z", type=float, default=0.05)
    parser.add_argument("--min-direction-consistency-fraction", type=float, default=0.60)
    parser.add_argument("--min-real-beats-null-fraction", type=float, default=0.60)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_dirs()
    write_hypotheses()

    frame = load_frame()
    axes_by_h: dict[int, float] = {}
    for h in [250, 500, 750]:
        mask = valid_mask_for_h(frame, h)
        axes_by_h[h] = axial_orientation(frame.loc[mask, f"h{h}_theta_h"].to_numpy(dtype="float64"))
    write_config(args, axes_by_h)

    min_temporal_for_cache = min(max(1.0, 2.0 * h / 1000.0) for h in [250, 500, 750])
    obs = build_ob_data(
        frame,
        max_state_distance=args.max_state_distance_for_cache,
        min_temporal_sep_sec=min_temporal_for_cache,
    )

    history_ms = int(round(args.history_window_sec * 1000))
    if history_ms not in axes_by_h:
        raise ValueError(f"Unsupported history window: {args.history_window_sec}")

    pairs, obs_effects, matching_qc = primary_analysis(
        obs,
        axis_angle=axes_by_h[history_ms],
        state_distance_threshold=args.state_distance_threshold,
        history_angle_threshold_deg=args.history_angle_threshold_deg,
        history_window_ms=history_ms,
        history_window_sec=args.history_window_sec,
        min_pairs_per_ob=args.min_pairs_per_ob,
        max_pairs_per_anchor=args.max_pairs_per_anchor,
        max_pairs_per_ob=args.max_pairs_per_ob,
    )
    null = shuffle_null(
        obs,
        axis_angle=axes_by_h[history_ms],
        state_distance_threshold=args.state_distance_threshold,
        history_angle_threshold_deg=args.history_angle_threshold_deg,
        history_window_ms=history_ms,
        history_window_sec=args.history_window_sec,
        min_pairs_per_ob=args.min_pairs_per_ob,
        max_pairs_per_anchor=args.max_pairs_per_anchor,
        max_pairs_per_ob=args.max_pairs_per_ob,
        n_shuffle_reps=args.n_shuffle_reps,
    )
    obs_effects = attach_null_summary(obs_effects, null)
    sensitivity = run_sensitivity(
        obs,
        axes_by_h,
        history_windows_ms=[250, 500, 750],
        state_distances=[0.35, 0.50, 0.75],
        angle_thresholds_deg=[60.0, 90.0, 120.0],
        min_pairs_per_ob=args.min_pairs_per_ob,
        max_pairs_per_anchor=args.max_pairs_per_anchor,
        max_pairs_per_ob=args.max_pairs_per_ob,
    )
    decision = evaluate_gate(
        obs_effects,
        min_pairs_per_ob=args.min_pairs_per_ob,
        min_obs_fraction_sufficient=args.min_obs_fraction_sufficient,
        min_abs_effect_z=args.min_abs_effect_z,
        min_direction_consistency_fraction=args.min_direction_consistency_fraction,
        min_real_beats_null_fraction=args.min_real_beats_null_fraction,
    )

    write_csv(OUT / "state_matched_history_pairs.csv", pairs, PAIR_COLUMNS)
    write_csv(OUT / "matching_quality.csv", matching_qc, MATCHING_QC_COLUMNS)
    write_csv(OUT / "observation_level_effects.csv", obs_effects, OBS_COLUMNS)
    write_csv(OUT / "history_shuffle_null.csv", null, NULL_COLUMNS)
    write_csv(OUT / "sensitivity.csv", sensitivity, SENS_COLUMNS)
    write_csv(OUT / "tables" / "matching_quality.csv", matching_qc, MATCHING_QC_COLUMNS)
    write_csv(OUT / "tables" / "observation_level_effects.csv", obs_effects, OBS_COLUMNS)
    write_csv(OUT / "tables" / "history_shuffle_null.csv", null, NULL_COLUMNS)
    write_csv(OUT / "tables" / "sensitivity.csv", sensitivity, SENS_COLUMNS)
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2), encoding="utf-8")
    make_figures(obs_effects, matching_qc, null, sensitivity)
    write_summary(decision, obs_effects, matching_qc, null, sensitivity, axes_by_h)

    print(json.dumps(decision, indent=2))
    print(f"Wrote 4121 outputs to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
