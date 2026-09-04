"""4100 state-matched event-locality challenge for 410x.

This node tests whether true compact-density transition timing contains extra
focal-centered local non-affine tangential activity after matching continuous
state within the same observation.

Primary activity comes from 4100A:

    A_i(t) aggregated to A_swarm_tangential_z(t)

Primary matching state:

    C = density_rms_z3045
    dCdt = gradient(density_rms_smooth3045, t)
    R = r_rms_z3045

The script does not define bursts and does not test propagation.
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

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4100"
DATE = "2026-08-26"
RNG_SEED = 4100_20260826

ACTIVITY_PATH = ROOT / "Output" / "4100A" / "swarm_activity_frame.csv"
EVENT_PATH = ROOT / "Output" / "3045" / "tables" / "transition_events.csv"
STATE_PATH = ROOT / "Output" / "3045" / "processed" / "frame_residual_signals.csv"

STATE_COLS = ["C", "dCdt", "R"]

EVENT_EFFECT_COLUMNS = [
    "event_id",
    "ob",
    "dataset",
    "event_t",
    "event_type",
    "event_A_pre_z",
    "event_window_frames",
    "control_A_pre_z",
    "delta_A_pre_z",
    "best_match_distance",
    "median_match_distance",
    "acceptable_match",
    "n_matches_used",
    "event_C",
    "event_dCdt",
    "event_R",
]

MATCH_COLUMNS = [
    "event_id",
    "ob",
    "dataset",
    "event_t",
    "event_type",
    "match_rank",
    "control_t",
    "match_distance",
    "abs_std_diff_C",
    "abs_std_diff_dCdt",
    "abs_std_diff_R",
    "event_A_pre_z",
    "control_A_pre_z",
    "delta_A_pre_z",
    "acceptable_event_match",
]

MATCHING_QUALITY_COLUMNS = [
    "ob",
    "dataset",
    "n_events_total",
    "n_events_with_window",
    "n_events_with_any_match",
    "n_events_acceptable",
    "acceptable_event_fraction",
    "median_best_match_distance",
    "median_abs_std_diff_C",
    "median_abs_std_diff_dCdt",
    "median_abs_std_diff_R",
    "n_control_candidates",
]

OBS_EFFECT_COLUMNS = [
    "ob",
    "dataset",
    "n_events_acceptable",
    "median_event_A_pre_z",
    "median_control_A_pre_z",
    "median_delta_A_pre_z",
    "mean_delta_A_pre_z",
    "fraction_positive_delta",
    "median_best_match_distance",
]

NULL_COLUMNS = [
    "shift_rep",
    "n_events_acceptable",
    "n_obs_usable",
    "median_ob_delta_A_pre_z",
    "mean_ob_delta_A_pre_z",
    "obs_positive_fraction",
    "total_acceptable_fraction",
]

PROFILE_COLUMNS = [
    "ob",
    "dataset",
    "lag_sec",
    "n_events",
    "event_median_A_z",
    "control_median_A_z",
    "delta_median_A_z",
]


@dataclass
class ObContext:
    ob: int
    dataset: str
    activity_t: np.ndarray
    activity_z: np.ndarray
    state_t: np.ndarray
    state_raw: dict[str, np.ndarray]
    state_center: dict[str, float]
    state_scale: dict[str, float]
    candidate_t: np.ndarray
    candidate_A_pre_z: np.ndarray
    candidate_nwin: np.ndarray
    candidate_Z: np.ndarray
    candidate_base_ok: np.ndarray
    true_event_t: np.ndarray


def ensure_dirs() -> None:
    (OUT / "figures").mkdir(parents=True, exist_ok=True)
    (OUT / "tables").mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    pd.DataFrame(rows, columns=columns).to_csv(path, index=False)


def robust_scale(values: np.ndarray) -> tuple[float, float]:
    arr = np.asarray(values, dtype="float64")
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return math.nan, math.nan
    med = float(np.nanmedian(arr))
    mad = float(np.nanmedian(np.abs(arr - med)))
    scale = 1.4826 * mad
    if not math.isfinite(scale) or scale <= 1e-12:
        scale = float(np.nanstd(arr))
    if not math.isfinite(scale) or scale <= 1e-12:
        scale = 1.0
    return med, scale


def robust_z(values: np.ndarray, center: float, scale: float) -> np.ndarray:
    return (np.asarray(values, dtype="float64") - center) / scale


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


def load_state() -> pd.DataFrame:
    state = pd.read_csv(STATE_PATH)
    state["t"] = pd.to_numeric(state["t"], errors="coerce")
    state["ob"] = pd.to_numeric(state["ob"], errors="coerce").astype("Int64")
    state["C"] = pd.to_numeric(state["density_rms_z3045"], errors="coerce")
    state["R"] = pd.to_numeric(state["r_rms_z3045"], errors="coerce")
    state["density_rms_smooth3045"] = pd.to_numeric(state["density_rms_smooth3045"], errors="coerce")
    state["dCdt"] = math.nan
    for _, idx in state.groupby("ob", sort=True).groups.items():
        d = state.loc[idx].sort_values("t")
        t = d["t"].to_numpy(dtype="float64")
        c = d["density_rms_smooth3045"].to_numpy(dtype="float64")
        vals = np.full(len(d), np.nan, dtype="float64")
        ok = np.isfinite(t) & np.isfinite(c)
        if ok.sum() >= 3:
            vals[ok] = np.gradient(c[ok], t[ok])
        state.loc[d.index, "dCdt"] = vals
    return state[["ob", "dataset", "t", "C", "dCdt", "R"]].dropna(subset=["ob", "t"])


def load_activity() -> pd.DataFrame:
    activity = pd.read_csv(ACTIVITY_PATH)
    activity["ob"] = pd.to_numeric(activity["ob"], errors="coerce").astype("Int64")
    activity["t"] = pd.to_numeric(activity["t"], errors="coerce")
    activity["A_z"] = pd.to_numeric(activity["A_swarm_tangential_z"], errors="coerce")
    return activity[["ob", "dataset", "t", "A_z"]].dropna(subset=["ob", "t", "A_z"])


def load_events() -> pd.DataFrame:
    events = pd.read_csv(EVENT_PATH)
    events["ob"] = pd.to_numeric(events["ob"], errors="coerce").astype("Int64")
    events["event_t"] = pd.to_numeric(events["event_t"], errors="coerce")
    return events.dropna(subset=["ob", "event_t"]).reset_index(drop=True)


def interp_state(ctx: ObContext, t: float) -> dict[str, float]:
    out: dict[str, float] = {}
    for col in STATE_COLS:
        vals = ctx.state_raw[col]
        tt = ctx.state_t
        ok = np.isfinite(tt) & np.isfinite(vals)
        if ok.sum() < 2 or t < float(np.nanmin(tt[ok])) or t > float(np.nanmax(tt[ok])):
            out[col] = math.nan
        else:
            out[col] = float(np.interp(t, tt[ok], vals[ok]))
    return out


def state_z(ctx: ObContext, raw: dict[str, float]) -> np.ndarray:
    return np.asarray(
        [
            (raw[col] - ctx.state_center[col]) / ctx.state_scale[col]
            if math.isfinite(raw.get(col, math.nan))
            else math.nan
            for col in STATE_COLS
        ],
        dtype="float64",
    )


def window_median(
    times: np.ndarray,
    values: np.ndarray,
    center_t: float,
    start: float,
    end: float,
    min_frames: int,
) -> tuple[float, int]:
    lo = center_t + start
    hi = center_t + end
    i0 = int(np.searchsorted(times, lo - 1e-9, side="left"))
    i1 = int(np.searchsorted(times, hi + 1e-9, side="right"))
    vals = values[i0:i1]
    vals = vals[np.isfinite(vals)]
    if vals.size < min_frames:
        return math.nan, int(vals.size)
    return float(np.nanmedian(vals)), int(vals.size)


def point_value_nearest(times: np.ndarray, values: np.ndarray, t: float, tolerance: float) -> float:
    if times.size == 0:
        return math.nan
    idx = int(np.searchsorted(times, t))
    candidates = []
    if idx < times.size:
        candidates.append(idx)
    if idx > 0:
        candidates.append(idx - 1)
    best = min(candidates, key=lambda i: abs(times[i] - t)) if candidates else -1
    if best < 0 or abs(float(times[best]) - t) > tolerance:
        return math.nan
    val = float(values[best])
    return val if math.isfinite(val) else math.nan


def min_abs_distance(times: np.ndarray, centers: np.ndarray) -> np.ndarray:
    if centers.size == 0:
        return np.full(times.shape, np.inf, dtype="float64")
    centers = np.sort(np.asarray(centers, dtype="float64"))
    idx = np.searchsorted(centers, times)
    left = np.full(times.shape, np.inf, dtype="float64")
    right = np.full(times.shape, np.inf, dtype="float64")
    ok_left = idx > 0
    ok_right = idx < centers.size
    left[ok_left] = np.abs(times[ok_left] - centers[idx[ok_left] - 1])
    right[ok_right] = np.abs(times[ok_right] - centers[idx[ok_right]])
    return np.minimum(left, right)


def build_contexts(
    activity: pd.DataFrame,
    state: pd.DataFrame,
    events: pd.DataFrame,
    *,
    near_pre_start: float,
    near_pre_end: float,
    min_window_frames: int,
    exclusion_sec: float,
) -> dict[int, ObContext]:
    contexts: dict[int, ObContext] = {}
    for ob, ad in activity.groupby("ob", sort=True):
        ob_int = int(ob)
        sd = state[state["ob"] == ob_int].sort_values("t")
        if sd.empty:
            continue
        ed = events[events["ob"] == ob_int].sort_values("event_t")
        ad = ad.sort_values("t")
        t_act = ad["t"].to_numpy(dtype="float64")
        a_z = ad["A_z"].to_numpy(dtype="float64")
        t_state = sd["t"].to_numpy(dtype="float64")
        raw = {col: sd[col].to_numpy(dtype="float64") for col in STATE_COLS}
        centers: dict[str, float] = {}
        scales: dict[str, float] = {}
        for col in STATE_COLS:
            centers[col], scales[col] = robust_scale(raw[col])

        pre_vals: list[float] = []
        pre_counts: list[int] = []
        state_rows: list[np.ndarray] = []
        provisional = ObContext(
            ob=ob_int,
            dataset=str(ad["dataset"].iloc[0]),
            activity_t=t_act,
            activity_z=a_z,
            state_t=t_state,
            state_raw=raw,
            state_center=centers,
            state_scale=scales,
            candidate_t=t_act,
            candidate_A_pre_z=np.asarray([], dtype="float64"),
            candidate_nwin=np.asarray([], dtype="int64"),
            candidate_Z=np.asarray([], dtype="float64"),
            candidate_base_ok=np.asarray([], dtype=bool),
            true_event_t=ed["event_t"].to_numpy(dtype="float64"),
        )
        for t in t_act:
            aval, nwin = window_median(t_act, a_z, float(t), near_pre_start, near_pre_end, min_window_frames)
            pre_vals.append(aval)
            pre_counts.append(nwin)
            state_rows.append(state_z(provisional, interp_state(provisional, float(t))))
        candidate_A = np.asarray(pre_vals, dtype="float64")
        candidate_n = np.asarray(pre_counts, dtype="int64")
        candidate_Z = np.vstack(state_rows) if state_rows else np.empty((0, len(STATE_COLS)))
        dist_to_events = min_abs_distance(t_act, provisional.true_event_t)
        base_ok = (
            np.isfinite(candidate_A)
            & (candidate_n >= min_window_frames)
            & np.all(np.isfinite(candidate_Z), axis=1)
            & (dist_to_events > exclusion_sec)
        )
        contexts[ob_int] = ObContext(
            ob=ob_int,
            dataset=str(ad["dataset"].iloc[0]),
            activity_t=t_act,
            activity_z=a_z,
            state_t=t_state,
            state_raw=raw,
            state_center=centers,
            state_scale=scales,
            candidate_t=t_act,
            candidate_A_pre_z=candidate_A,
            candidate_nwin=candidate_n,
            candidate_Z=candidate_Z,
            candidate_base_ok=base_ok,
            true_event_t=provisional.true_event_t,
        )
    return contexts


def match_one(
    ctx: ObContext,
    *,
    center_t: float,
    center_A: float,
    center_Z: np.ndarray,
    n_matches: int,
    max_match_distance: float,
    exclusion_sec: float,
) -> tuple[list[dict[str, float]], float, float, bool]:
    if not np.isfinite(center_A) or not np.all(np.isfinite(center_Z)):
        return [], math.nan, math.nan, False
    mask = ctx.candidate_base_ok & (np.abs(ctx.candidate_t - center_t) > exclusion_sec)
    if not mask.any():
        return [], math.nan, math.nan, False
    cand_idx = np.flatnonzero(mask)
    dz = ctx.candidate_Z[cand_idx] - center_Z.reshape(1, -1)
    dist = np.sqrt(np.sum(dz * dz, axis=1))
    ok = np.isfinite(dist)
    if not ok.any():
        return [], math.nan, math.nan, False
    cand_idx = cand_idx[ok]
    dist = dist[ok]
    order = np.argsort(dist)
    use = cand_idx[order[:n_matches]]
    use_dist = dist[order[:n_matches]]
    rows: list[dict[str, float]] = []
    for rank, (idx, d) in enumerate(zip(use, use_dist), start=1):
        diff = np.abs(ctx.candidate_Z[idx] - center_Z)
        rows.append(
            {
                "rank": float(rank),
                "control_t": float(ctx.candidate_t[idx]),
                "match_distance": float(d),
                "abs_std_diff_C": float(diff[0]),
                "abs_std_diff_dCdt": float(diff[1]),
                "abs_std_diff_R": float(diff[2]),
                "control_A_pre_z": float(ctx.candidate_A_pre_z[idx]),
                "delta_A_pre_z": float(center_A - ctx.candidate_A_pre_z[idx]),
            }
        )
    control_med = float(np.nanmedian([r["control_A_pre_z"] for r in rows])) if rows else math.nan
    best = float(use_dist[0]) if use_dist.size else math.nan
    acceptable = bool(math.isfinite(best) and best <= max_match_distance)
    return rows, control_med, best, acceptable


def real_event_matching(
    contexts: dict[int, ObContext],
    events: pd.DataFrame,
    *,
    near_pre_start: float,
    near_pre_end: float,
    min_window_frames: int,
    n_matches: int,
    max_match_distance: float,
    exclusion_sec: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    event_rows: list[dict[str, object]] = []
    match_rows: list[dict[str, object]] = []
    for row in events.to_dict("records"):
        ob = int(row["ob"])
        ctx = contexts.get(ob)
        if ctx is None:
            continue
        event_t = float(row["event_t"])
        event_A, nwin = window_median(
            ctx.activity_t,
            ctx.activity_z,
            event_t,
            near_pre_start,
            near_pre_end,
            min_window_frames,
        )
        event_raw = interp_state(ctx, event_t)
        event_Z = state_z(ctx, event_raw)
        matches, control_med, best, acceptable = match_one(
            ctx,
            center_t=event_t,
            center_A=event_A,
            center_Z=event_Z,
            n_matches=n_matches,
            max_match_distance=max_match_distance,
            exclusion_sec=exclusion_sec,
        )
        event_id = int(row["event_id"])
        delta = float(event_A - control_med) if math.isfinite(event_A) and math.isfinite(control_med) else math.nan
        event_rows.append(
            {
                "event_id": event_id,
                "ob": ob,
                "dataset": row["dataset"],
                "event_t": event_t,
                "event_type": row["event_type"],
                "event_A_pre_z": event_A,
                "event_window_frames": nwin,
                "control_A_pre_z": control_med,
                "delta_A_pre_z": delta,
                "best_match_distance": best,
                "median_match_distance": float(np.nanmedian([m["match_distance"] for m in matches])) if matches else math.nan,
                "acceptable_match": acceptable,
                "n_matches_used": len(matches),
                "event_C": event_raw["C"],
                "event_dCdt": event_raw["dCdt"],
                "event_R": event_raw["R"],
            }
        )
        for m in matches:
            match_rows.append(
                {
                    "event_id": event_id,
                    "ob": ob,
                    "dataset": row["dataset"],
                    "event_t": event_t,
                    "event_type": row["event_type"],
                    "match_rank": int(m["rank"]),
                    "control_t": m["control_t"],
                    "match_distance": m["match_distance"],
                    "abs_std_diff_C": m["abs_std_diff_C"],
                    "abs_std_diff_dCdt": m["abs_std_diff_dCdt"],
                    "abs_std_diff_R": m["abs_std_diff_R"],
                    "event_A_pre_z": event_A,
                    "control_A_pre_z": m["control_A_pre_z"],
                    "delta_A_pre_z": m["delta_A_pre_z"],
                    "acceptable_event_match": acceptable,
                }
            )
    return pd.DataFrame(event_rows, columns=EVENT_EFFECT_COLUMNS), pd.DataFrame(match_rows, columns=MATCH_COLUMNS)


def summarize_matching(events: pd.DataFrame, matches: pd.DataFrame, contexts: dict[int, ObContext]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for ob, d in events.groupby("ob", sort=True):
        ob_int = int(ob)
        m = matches[(matches["ob"] == ob_int) & (matches["match_rank"] == 1)]
        acc = d[d["acceptable_match"] == True]  # noqa: E712
        total = len(d)
        ctx = contexts.get(ob_int)
        rows.append(
            {
                "ob": ob_int,
                "dataset": str(d["dataset"].iloc[0]),
                "n_events_total": total,
                "n_events_with_window": int(np.isfinite(d["event_A_pre_z"]).sum()),
                "n_events_with_any_match": int(np.isfinite(d["best_match_distance"]).sum()),
                "n_events_acceptable": len(acc),
                "acceptable_event_fraction": len(acc) / total if total else math.nan,
                "median_best_match_distance": float(np.nanmedian(d["best_match_distance"])) if total else math.nan,
                "median_abs_std_diff_C": float(np.nanmedian(m["abs_std_diff_C"])) if not m.empty else math.nan,
                "median_abs_std_diff_dCdt": float(np.nanmedian(m["abs_std_diff_dCdt"])) if not m.empty else math.nan,
                "median_abs_std_diff_R": float(np.nanmedian(m["abs_std_diff_R"])) if not m.empty else math.nan,
                "n_control_candidates": int(ctx.candidate_base_ok.sum()) if ctx is not None else 0,
            }
        )
    return pd.DataFrame(rows, columns=MATCHING_QUALITY_COLUMNS)


def observation_effects(events: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    d0 = events[events["acceptable_match"] == True].copy()  # noqa: E712
    for ob, d in d0.groupby("ob", sort=True):
        rows.append(
            {
                "ob": int(ob),
                "dataset": str(d["dataset"].iloc[0]),
                "n_events_acceptable": len(d),
                "median_event_A_pre_z": float(np.nanmedian(d["event_A_pre_z"])),
                "median_control_A_pre_z": float(np.nanmedian(d["control_A_pre_z"])),
                "median_delta_A_pre_z": float(np.nanmedian(d["delta_A_pre_z"])),
                "mean_delta_A_pre_z": float(np.nanmean(d["delta_A_pre_z"])),
                "fraction_positive_delta": float(np.nanmean(d["delta_A_pre_z"] > 0)),
                "median_best_match_distance": float(np.nanmedian(d["best_match_distance"])),
            }
        )
    return pd.DataFrame(rows, columns=OBS_EFFECT_COLUMNS)


def shifted_null(
    contexts: dict[int, ObContext],
    events: pd.DataFrame,
    *,
    near_pre_start: float,
    near_pre_end: float,
    min_window_frames: int,
    n_matches: int,
    max_match_distance: float,
    exclusion_sec: float,
    n_shift_reps: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(RNG_SEED + 700)
    rows: list[dict[str, object]] = []
    for rep in range(n_shift_reps):
        obs_effects: list[float] = []
        obs_positive: list[bool] = []
        n_total = 0
        n_acc = 0
        for ob, ed in events.groupby("ob", sort=True):
            ctx = contexts.get(int(ob))
            if ctx is None or ctx.activity_t.size == 0:
                continue
            tmin = float(np.nanmin(ctx.activity_t))
            tmax = float(np.nanmax(ctx.activity_t))
            duration = tmax - tmin
            if duration <= abs(near_pre_start) + exclusion_sec:
                continue
            shift = float(rng.uniform(exclusion_sec, duration - exclusion_sec))
            deltas: list[float] = []
            for event_t in ed["event_t"].to_numpy(dtype="float64"):
                shifted_t = ((event_t - tmin + shift) % duration) + tmin
                n_total += 1
                if np.min(np.abs(ctx.true_event_t - shifted_t)) <= exclusion_sec:
                    continue
                center_A, nwin = window_median(
                    ctx.activity_t,
                    ctx.activity_z,
                    shifted_t,
                    near_pre_start,
                    near_pre_end,
                    min_window_frames,
                )
                if nwin < min_window_frames or not math.isfinite(center_A):
                    continue
                center_Z = state_z(ctx, interp_state(ctx, shifted_t))
                matches, control_med, _best, acceptable = match_one(
                    ctx,
                    center_t=shifted_t,
                    center_A=center_A,
                    center_Z=center_Z,
                    n_matches=n_matches,
                    max_match_distance=max_match_distance,
                    exclusion_sec=exclusion_sec,
                )
                if acceptable and matches and math.isfinite(control_med):
                    deltas.append(float(center_A - control_med))
                    n_acc += 1
            if deltas:
                obs_delta = float(np.nanmedian(deltas))
                obs_effects.append(obs_delta)
                obs_positive.append(obs_delta > 0)
        rows.append(
            {
                "shift_rep": rep,
                "n_events_acceptable": n_acc,
                "n_obs_usable": len(obs_effects),
                "median_ob_delta_A_pre_z": float(np.nanmedian(obs_effects)) if obs_effects else math.nan,
                "mean_ob_delta_A_pre_z": float(np.nanmean(obs_effects)) if obs_effects else math.nan,
                "obs_positive_fraction": float(np.mean(obs_positive)) if obs_positive else math.nan,
                "total_acceptable_fraction": n_acc / n_total if n_total else math.nan,
            }
        )
    return pd.DataFrame(rows, columns=NULL_COLUMNS)


def profile_table(
    contexts: dict[int, ObContext],
    event_effects: pd.DataFrame,
    *,
    lags: np.ndarray,
    tolerance: float,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    d0 = event_effects[event_effects["acceptable_match"] == True].copy()  # noqa: E712
    for ob, d in d0.groupby("ob", sort=True):
        ctx = contexts.get(int(ob))
        if ctx is None:
            continue
        for lag in lags:
            event_vals: list[float] = []
            control_vals: list[float] = []
            for row in d.to_dict("records"):
                ev = point_value_nearest(ctx.activity_t, ctx.activity_z, float(row["event_t"]) + float(lag), tolerance)
                # Profile uses the nearest best matched control from rank-1 rows.
                event_vals.append(ev)
            rows.append(
                {
                    "ob": int(ob),
                    "dataset": str(d["dataset"].iloc[0]),
                    "lag_sec": float(lag),
                    "n_events": int(np.isfinite(event_vals).sum()),
                    "event_median_A_z": float(np.nanmedian(event_vals)) if np.isfinite(event_vals).any() else math.nan,
                    "control_median_A_z": math.nan,
                    "delta_median_A_z": math.nan,
                }
            )
    return pd.DataFrame(rows, columns=PROFILE_COLUMNS)


def profile_table_with_controls(
    contexts: dict[int, ObContext],
    event_effects: pd.DataFrame,
    matches: pd.DataFrame,
    *,
    lags: np.ndarray,
    tolerance: float,
) -> pd.DataFrame:
    best = matches[matches["match_rank"] == 1][["event_id", "control_t"]].copy()
    d0 = event_effects[event_effects["acceptable_match"] == True].merge(best, on="event_id", how="left")  # noqa: E712
    rows: list[dict[str, object]] = []
    for ob, d in d0.groupby("ob", sort=True):
        ctx = contexts.get(int(ob))
        if ctx is None:
            continue
        for lag in lags:
            ev_vals: list[float] = []
            ct_vals: list[float] = []
            for row in d.to_dict("records"):
                ev = point_value_nearest(ctx.activity_t, ctx.activity_z, float(row["event_t"]) + float(lag), tolerance)
                ct = point_value_nearest(ctx.activity_t, ctx.activity_z, float(row["control_t"]) + float(lag), tolerance)
                ev_vals.append(ev)
                ct_vals.append(ct)
            ev_arr = np.asarray(ev_vals, dtype="float64")
            ct_arr = np.asarray(ct_vals, dtype="float64")
            ok = np.isfinite(ev_arr) & np.isfinite(ct_arr)
            event_med = float(np.nanmedian(ev_arr[ok])) if ok.any() else math.nan
            control_med = float(np.nanmedian(ct_arr[ok])) if ok.any() else math.nan
            rows.append(
                {
                    "ob": int(ob),
                    "dataset": str(d["dataset"].iloc[0]),
                    "lag_sec": float(lag),
                    "n_events": int(ok.sum()),
                    "event_median_A_z": event_med,
                    "control_median_A_z": control_med,
                    "delta_median_A_z": float(event_med - control_med)
                    if math.isfinite(event_med) and math.isfinite(control_med)
                    else math.nan,
                }
            )
    return pd.DataFrame(rows, columns=PROFILE_COLUMNS)


def classify(
    obs_effects_df: pd.DataFrame,
    matching_quality: pd.DataFrame,
    null: pd.DataFrame,
    *,
    min_effect_z: float,
    min_same_direction_fraction: float,
    min_real_beats_null_fraction: float,
    min_total_acceptable_fraction: float,
    max_median_match_distance: float,
) -> dict[str, object]:
    usable = obs_effects_df[obs_effects_df["n_events_acceptable"] > 0].copy()
    median_obs_effect = float(np.nanmedian(usable["median_delta_A_pre_z"])) if not usable.empty else math.nan
    same_direction = float(np.nanmean(usable["median_delta_A_pre_z"] > 0)) if not usable.empty else math.nan
    total_events = float(matching_quality["n_events_total"].sum()) if not matching_quality.empty else 0.0
    total_acc = float(matching_quality["n_events_acceptable"].sum()) if not matching_quality.empty else 0.0
    total_acc_frac = total_acc / total_events if total_events else math.nan
    median_match = float(np.nanmedian(matching_quality["median_best_match_distance"])) if not matching_quality.empty else math.nan
    null_vals = null["median_ob_delta_A_pre_z"].to_numpy(dtype="float64") if not null.empty else np.asarray([])
    null_vals = null_vals[np.isfinite(null_vals)]
    real_beats_null = float(np.mean(median_obs_effect > null_vals)) if null_vals.size and math.isfinite(median_obs_effect) else math.nan

    matching_ok = (
        math.isfinite(total_acc_frac)
        and total_acc_frac >= min_total_acceptable_fraction
        and math.isfinite(median_match)
        and median_match <= max_median_match_distance
    )
    effect_ok = math.isfinite(median_obs_effect) and median_obs_effect > min_effect_z
    direction_ok = math.isfinite(same_direction) and same_direction >= min_same_direction_fraction
    null_ok = math.isfinite(real_beats_null) and real_beats_null >= min_real_beats_null_fraction

    if not matching_ok:
        gate = "boundary_matching_identifiability"
        interp = (
            "State matching did not reach the pre-frozen quality gate; do not interpret "
            "event-control differences as event-locality evidence."
        )
        nxt = ["4100_matching_boundary_review"]
    elif effect_ok and direction_ok and null_ok:
        gate = "pass_robust_event_locality"
        interp = (
            "Real transition windows retain excess focal-centered local non-affine "
            "activity after same-observation C,dCdt,R matching."
        )
        nxt = ["4101_local_burst_onset_definition"]
    elif math.isfinite(median_obs_effect) and median_obs_effect > 0 and (direction_ok or null_ok):
        gate = "boundary_weak_event_locality"
        interp = (
            "Real event windows are somewhat higher than state-matched controls, but "
            "the effect does not pass all consistency/null gates."
        )
        nxt = ["4105_boundary_synthesis_or_4100_sensitivity_audit"]
    else:
        gate = "fail_event_timing_not_beyond_continuous_state"
        interp = (
            "After matching continuous compact-density state within observation, true "
            "transition timing does not show robust extra near-pre activity."
        )
        nxt = ["4105_state_matched_negative_synthesis"]

    return {
        "node": "4100_state_matched_event_locality_challenge",
        "date": DATE,
        "upstream_node": "4100A_spatial_unit_overlap_audit",
        "data_scope": "all_19_observations",
        "spatial_unit": "focal_centered_local_nonaffine_tangential_activity",
        "activity_column": "A_swarm_tangential_z",
        "activity_phase": "near_pre[-0.25,0.00]sec",
        "matching_variables": ["C_density_rms_z3045", "dCdt_gradient_density_rms_smooth3045", "R_r_rms_z3045"],
        "nulls": ["same_observation_state_matched_non_event", "within_observation_shifted_event"],
        "primary_metrics": {
            "median_observation_delta_A_pre_z": median_obs_effect,
            "same_direction_observation_fraction": same_direction,
            "real_beats_shifted_null_fraction": real_beats_null,
            "total_acceptable_event_fraction": total_acc_frac,
            "median_observation_best_match_distance": median_match,
        },
        "pre_frozen_gates": {
            "min_effect_z": min_effect_z,
            "min_same_direction_fraction": min_same_direction_fraction,
            "min_real_beats_null_fraction": min_real_beats_null_fraction,
            "min_total_acceptable_fraction": min_total_acceptable_fraction,
            "max_median_match_distance": max_median_match_distance,
        },
        "gate_result": gate,
        "interpretation": interp,
        "does_not_prove": [
            "burst localization",
            "propagation",
            "causal trigger",
            "individual residual velocity",
            "prediction before transition",
        ],
        "next": nxt,
        "artifacts": [
            "Output/4100/event_control_matches.csv",
            "Output/4100/matching_quality.csv",
            "Output/4100/event_local_effects.csv",
            "Output/4100/observation_level_effects.csv",
            "Output/4100/shifted_event_null.csv",
            "Output/4100/event_centered_profile.csv",
            "Output/4100/decision.json",
            "Output/4100/4100_summary.md",
        ],
    }


def make_figures(
    obs_effects_df: pd.DataFrame,
    matching_quality: pd.DataFrame,
    null: pd.DataFrame,
    profile: pd.DataFrame,
    decision: dict[str, object],
) -> None:
    fig, ax = plt.subplots(figsize=(11, 4.8))
    x = np.arange(len(obs_effects_df))
    colors = ["#4c78a8" if v > 0 else "#c44e52" for v in obs_effects_df["median_delta_A_pre_z"]]
    ax.bar(x, obs_effects_df["median_delta_A_pre_z"], color=colors)
    ax.axhline(0.0, color="#333333", linewidth=1.0)
    ax.axhline(0.05, color="#333333", linewidth=1.0, linestyle="--")
    ax.set_xticks(x)
    ax.set_xticklabels([f"Ob{int(v)}" for v in obs_effects_df["ob"]], rotation=45, ha="right")
    ax.set_ylabel("event - matched control near-pre A(z)")
    ax.set_title("4100 state-matched event-locality by observation")
    fig.tight_layout()
    fig.savefig(OUT / "figures" / "4100_observation_effects.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    q = matching_quality.sort_values("ob")
    x = np.arange(len(q))
    axes[0].bar(x, q["acceptable_event_fraction"], color="#59a14f")
    axes[0].axhline(0.75, color="#333333", linestyle="--", linewidth=1.0)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels([f"Ob{int(v)}" for v in q["ob"]], rotation=45, ha="right")
    axes[0].set_ylim(0, 1.05)
    axes[0].set_title("acceptable match fraction")
    axes[1].bar(x, q["median_best_match_distance"], color="#f28e2b")
    axes[1].axhline(0.75, color="#333333", linestyle="--", linewidth=1.0)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels([f"Ob{int(v)}" for v in q["ob"]], rotation=45, ha="right")
    axes[1].set_title("median best match distance")
    fig.suptitle("4100 matching quality")
    fig.tight_layout()
    fig.savefig(OUT / "figures" / "4100_matching_quality.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    vals = null["median_ob_delta_A_pre_z"].dropna().to_numpy(dtype="float64")
    if vals.size:
        ax.hist(vals, bins=18, color="#bab0ab", edgecolor="#555555")
    real = decision["primary_metrics"]["median_observation_delta_A_pre_z"]
    if isinstance(real, float) and math.isfinite(real):
        ax.axvline(real, color="#4c78a8", linewidth=2.0, label="real")
    ax.axvline(0.0, color="#333333", linewidth=1.0)
    ax.set_xlabel("median observation event-minus-control A(z)")
    ax.set_ylabel("shifted-event null count")
    ax.set_title("4100 shifted-event null")
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(OUT / "figures" / "4100_shifted_event_null.png", dpi=180)
    plt.close(fig)

    prof = profile.groupby("lag_sec", as_index=False).agg(
        event_median_A_z=("event_median_A_z", "median"),
        control_median_A_z=("control_median_A_z", "median"),
        delta_median_A_z=("delta_median_A_z", "median"),
    )
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if not prof.empty:
        ax.plot(prof["lag_sec"], prof["event_median_A_z"], marker="o", label="event", color="#4c78a8")
        ax.plot(prof["lag_sec"], prof["control_median_A_z"], marker="o", label="matched control", color="#f28e2b")
        ax.axvspan(-0.25, 0.0, color="#d9d9d9", alpha=0.35, label="near-pre")
    ax.axvline(0.0, color="#333333", linewidth=1.0)
    ax.set_xlabel("lag relative to event/control time (sec)")
    ax.set_ylabel("A_swarm_tangential_z")
    ax.set_title("4100 event-centered activity profile")
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(OUT / "figures" / "4100_event_centered_profile.png", dpi=180)
    plt.close(fig)


def write_config(args: argparse.Namespace) -> None:
    text = dedent(
        f"""\
        node: 4100_state_matched_event_locality_challenge
        date: {DATE}
        activity_source: Output/4100A/swarm_activity_frame.csv
        event_source: Output/3045/tables/transition_events.csv
        state_source: Output/3045/processed/frame_residual_signals.csv
        activity_column: A_swarm_tangential_z
        near_pre_window_sec: [{args.near_pre_start}, {args.near_pre_end}]
        profile_window_sec: [{args.profile_start}, {args.profile_end}]
        profile_step_sec: {args.profile_step}
        state_variables:
          C: density_rms_z3045
          dCdt: gradient(density_rms_smooth3045,t)
          R: r_rms_z3045
        matching:
          same_observation: true
          standardized_state_space: within_observation_robust_z
          n_matches: {args.n_matches}
          max_match_distance: {args.max_match_distance}
          exclusion_sec: {args.exclusion_sec}
          min_window_frames: {args.min_window_frames}
        shifted_event_null:
          n_shift_reps: {args.n_shift_reps}
          seed: {RNG_SEED + 700}
        gates:
          min_effect_z: {args.min_effect_z}
          min_same_direction_fraction: {args.min_same_direction_fraction}
          min_real_beats_null_fraction: {args.min_real_beats_null_fraction}
          min_total_acceptable_fraction: {args.min_total_acceptable_fraction}
          max_median_match_distance: {args.max_median_match_distance}
        """
    )
    (OUT / "config.yaml").write_text(text, encoding="utf-8")


def write_summary(
    *,
    matching_quality: pd.DataFrame,
    obs_effects_df: pd.DataFrame,
    null: pd.DataFrame,
    profile: pd.DataFrame,
    decision: dict[str, object],
) -> None:
    metrics = decision["primary_metrics"]
    profile_agg = profile.groupby("lag_sec", as_index=False).agg(
        event_median_A_z=("event_median_A_z", "median"),
        control_median_A_z=("control_median_A_z", "median"),
        delta_median_A_z=("delta_median_A_z", "median"),
        n_events=("n_events", "sum"),
    )
    profile_summary_columns = [
        "lag_sec",
        "n_events",
        "event_median_A_z",
        "control_median_A_z",
        "delta_median_A_z",
    ]
    null_summary = {
        "n_shift_reps": int(len(null)),
        "null_median": float(np.nanmedian(null["median_ob_delta_A_pre_z"])) if not null.empty else math.nan,
        "null_q05": float(np.nanquantile(null["median_ob_delta_A_pre_z"], 0.05)) if not null.empty else math.nan,
        "null_q95": float(np.nanquantile(null["median_ob_delta_A_pre_z"], 0.95)) if not null.empty else math.nan,
    }
    sections = [
        "# Node 4100 Summary",
        "## Question\n\n"
        "After matching `C,dCdt,radius` within the same observation, do true "
        "compact-density transition times still contain extra focal-centered "
        "local non-affine tangential activity?",
        "## Why This Node Exists\n\n"
        "4100A constructed the unique focal-centered activity table needed for "
        "410x and exposed the neighbor-overlap boundary. 4100 now tests the "
        "main event-locality gate before any burst or propagation analysis.",
        "## Data\n\n"
        "- Activity: `Output/4100A/swarm_activity_frame.csv`\n"
        "- Events: `Output/3045/tables/transition_events.csv`\n"
        "- State: `Output/3045/processed/frame_residual_signals.csv`\n"
        "- Scope: all 19 observations",
        "## Frozen Parameters\n\n"
        "```text\n"
        "activity = A_swarm_tangential_z\n"
        "near_pre = [-0.25, 0.00] sec\n"
        "state = C density_rms_z3045, dCdt gradient(density_rms_smooth3045,t), R r_rms_z3045\n"
        "matching = same observation nearest neighbors in robust standardized state space\n"
        "control exclusion = no true transition within +/- 0.75 sec\n"
        "```\n",
        "## Primary Metrics\n\n"
        f"- median observation delta: `{metrics['median_observation_delta_A_pre_z']:.4g}` z\n"
        f"- same-direction observation fraction: `{metrics['same_direction_observation_fraction']:.4g}`\n"
        f"- real beats shifted-event null fraction: `{metrics['real_beats_shifted_null_fraction']:.4g}`\n"
        f"- total acceptable event fraction: `{metrics['total_acceptable_event_fraction']:.4g}`\n"
        f"- median observation best-match distance: `{metrics['median_observation_best_match_distance']:.4g}`",
        "## Matching Quality\n\n" + md_table(matching_quality.to_dict("records"), MATCHING_QUALITY_COLUMNS),
        "## Observation-level Results\n\n" + md_table(obs_effects_df.to_dict("records"), OBS_EFFECT_COLUMNS),
        "## Shifted-event Null\n\n" + md_table([null_summary], ["n_shift_reps", "null_median", "null_q05", "null_q95"]),
        "## Event-centered Profile\n\n" + md_table(profile_agg.to_dict("records"), profile_summary_columns),
        "## Gate Evaluation\n\n"
        "```text\n"
        f"gate_result = {decision['gate_result']}\n"
        "```\n\n"
        f"{decision['interpretation']}",
        "## What This Supports\n\n"
        "- It directly tests whether real event timing adds information beyond "
        "matched continuous compact-density state at the swarm-activity level.\n"
        "- It separates the earlier near-pre diagnostic from a stricter "
        "state-matched event-locality claim.",
        "## What This Does Not Prove\n\n"
        + md_table([{"does_not_prove": x} for x in decision["does_not_prove"]], ["does_not_prove"]),
        "## Decision\n\n" f"`{decision['gate_result']}`",
        "## Next Node\n\n" + md_table([{"next": x} for x in decision["next"]], ["next"]),
        "## Artifacts\n\n"
        "- `Output/4100/event_control_matches.csv`\n"
        "- `Output/4100/matching_quality.csv`\n"
        "- `Output/4100/event_local_effects.csv`\n"
        "- `Output/4100/observation_level_effects.csv`\n"
        "- `Output/4100/shifted_event_null.csv`\n"
        "- `Output/4100/event_centered_profile.csv`\n"
        "- `Output/4100/figures/4100_observation_effects.png`\n"
        "- `Output/4100/figures/4100_matching_quality.png`\n"
        "- `Output/4100/figures/4100_shifted_event_null.png`\n"
        "- `Output/4100/figures/4100_event_centered_profile.png`\n"
        "- `Output/4100/decision.json`",
    ]
    (OUT / "4100_summary.md").write_text("\n\n".join(sections) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--near-pre-start", type=float, default=-0.25)
    parser.add_argument("--near-pre-end", type=float, default=0.0)
    parser.add_argument("--profile-start", type=float, default=-0.5)
    parser.add_argument("--profile-end", type=float, default=0.5)
    parser.add_argument("--profile-step", type=float, default=0.1)
    parser.add_argument("--profile-tolerance", type=float, default=0.055)
    parser.add_argument("--min-window-frames", type=int, default=2)
    parser.add_argument("--n-matches", type=int, default=5)
    parser.add_argument("--max-match-distance", type=float, default=0.75)
    parser.add_argument("--max-median-match-distance", type=float, default=0.75)
    parser.add_argument("--exclusion-sec", type=float, default=0.75)
    parser.add_argument("--n-shift-reps", type=int, default=80)
    parser.add_argument("--min-effect-z", type=float, default=0.05)
    parser.add_argument("--min-same-direction-fraction", type=float, default=0.60)
    parser.add_argument("--min-real-beats-null-fraction", type=float, default=0.60)
    parser.add_argument("--min-total-acceptable-fraction", type=float, default=0.75)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_dirs()
    write_config(args)

    activity = load_activity()
    state = load_state()
    events = load_events()
    contexts = build_contexts(
        activity,
        state,
        events,
        near_pre_start=args.near_pre_start,
        near_pre_end=args.near_pre_end,
        min_window_frames=args.min_window_frames,
        exclusion_sec=args.exclusion_sec,
    )
    event_effects, matches = real_event_matching(
        contexts,
        events,
        near_pre_start=args.near_pre_start,
        near_pre_end=args.near_pre_end,
        min_window_frames=args.min_window_frames,
        n_matches=args.n_matches,
        max_match_distance=args.max_match_distance,
        exclusion_sec=args.exclusion_sec,
    )
    matching_quality = summarize_matching(event_effects, matches, contexts)
    obs_eff = observation_effects(event_effects)
    null = shifted_null(
        contexts,
        events,
        near_pre_start=args.near_pre_start,
        near_pre_end=args.near_pre_end,
        min_window_frames=args.min_window_frames,
        n_matches=args.n_matches,
        max_match_distance=args.max_match_distance,
        exclusion_sec=args.exclusion_sec,
        n_shift_reps=args.n_shift_reps,
    )
    lags = np.round(np.arange(args.profile_start, args.profile_end + args.profile_step / 2, args.profile_step), 6)
    profile = profile_table_with_controls(
        contexts,
        event_effects,
        matches,
        lags=lags,
        tolerance=args.profile_tolerance,
    )
    decision = classify(
        obs_eff,
        matching_quality,
        null,
        min_effect_z=args.min_effect_z,
        min_same_direction_fraction=args.min_same_direction_fraction,
        min_real_beats_null_fraction=args.min_real_beats_null_fraction,
        min_total_acceptable_fraction=args.min_total_acceptable_fraction,
        max_median_match_distance=args.max_median_match_distance,
    )
    make_figures(obs_eff, matching_quality, null, profile, decision)

    event_effects.to_csv(OUT / "event_local_effects.csv", index=False)
    event_effects.to_csv(OUT / "tables" / "event_local_effects.csv", index=False)
    matches.to_csv(OUT / "event_control_matches.csv", index=False)
    matches.to_csv(OUT / "tables" / "event_control_matches.csv", index=False)
    matching_quality.to_csv(OUT / "matching_quality.csv", index=False)
    matching_quality.to_csv(OUT / "tables" / "matching_quality.csv", index=False)
    obs_eff.to_csv(OUT / "observation_level_effects.csv", index=False)
    obs_eff.to_csv(OUT / "tables" / "observation_level_effects.csv", index=False)
    null.to_csv(OUT / "shifted_event_null.csv", index=False)
    null.to_csv(OUT / "tables" / "shifted_event_null.csv", index=False)
    profile.to_csv(OUT / "event_centered_profile.csv", index=False)
    profile.to_csv(OUT / "tables" / "event_centered_profile.csv", index=False)
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2), encoding="utf-8")
    write_summary(
        matching_quality=matching_quality,
        obs_effects_df=obs_eff,
        null=null,
        profile=profile,
        decision=decision,
    )
    print(json.dumps(decision, indent=2), flush=True)
    print(f"Wrote 4100 outputs to {OUT.relative_to(ROOT)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
