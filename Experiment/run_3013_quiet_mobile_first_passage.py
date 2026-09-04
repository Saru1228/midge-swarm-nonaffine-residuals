#!/usr/bin/env python3
"""Experiment 3013: quiet-to-mobile first-passage analysis for 3xxx states."""
from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "Output" / "3010" / "processed" / "stochastic_state_variables.csv"
OUT = ROOT / "Output" / "3013"
FIG = OUT / "figures"
TAB = OUT / "tables"
PROC = OUT / "processed"

STATE_ORDER = ["quiet", "outward", "mobile", "other"]


@dataclass(frozen=True)
class RunConfig:
    quiet_speed_quantile: float = 0.50
    quiet_outward_quantile: float = 0.50
    mobile_speed_quantile: float = 0.90
    outward_quantile: float = 0.75
    min_quiet_sec: float = 0.20
    max_follow_sec: float = 5.00
    transition_lag_sec: float = 0.05


def ensure_dirs() -> None:
    for path in (OUT, FIG, TAB, PROC):
        path.mkdir(parents=True, exist_ok=True)


def finite_median(values: np.ndarray) -> float:
    values = np.asarray(values, dtype="float64")
    values = values[np.isfinite(values)]
    return float(np.median(values)) if values.size else math.nan


def dataframe_to_markdown(df: pd.DataFrame, max_rows: int | None = None) -> str:
    if max_rows is not None:
        df = df.head(max_rows)
    if df.empty:
        return "_No rows._"
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df.iterrows():
        vals = []
        for col in cols:
            val = row[col]
            if isinstance(val, float):
                vals.append("NA" if not np.isfinite(val) else f"{val:.4g}")
            else:
                vals.append(str(val))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def read_input() -> pd.DataFrame:
    if not IN.exists():
        raise FileNotFoundError("Run 3010 first; missing Output/3010/processed/stochastic_state_variables.csv")
    usecols = [
        "dataset",
        "ob",
        "t",
        "dt",
        "center_speed",
        "radial_velocity_mean",
        "frac_outward",
        "center_speed_z",
        "radial_velocity_mean_z",
        "frac_outward_z",
    ]
    return pd.read_csv(IN, usecols=usecols).sort_values(["ob", "t"], kind="mergesort").reset_index(drop=True)


def median_dt(d: pd.DataFrame) -> float:
    dt = float(d["dt"].median(skipna=True))
    if not np.isfinite(dt) or dt <= 0:
        dt = float(np.nanmedian(np.diff(d["t"].to_numpy(dtype="float64"))))
    return dt


def contiguous_true_runs(mask: np.ndarray) -> list[tuple[int, int]]:
    mask = np.asarray(mask, dtype=bool)
    runs = []
    i = 0
    n = len(mask)
    while i < n:
        if not mask[i]:
            i += 1
            continue
        start = i
        while i < n and mask[i]:
            i += 1
        runs.append((start, i))
    return runs


def classify_states(d: pd.DataFrame, config: RunConfig) -> tuple[np.ndarray, dict[str, float]]:
    speed = d["center_speed"].to_numpy(dtype="float64")
    radial = d["radial_velocity_mean"].to_numpy(dtype="float64")
    outward_frac = d["frac_outward"].to_numpy(dtype="float64")
    speed_q_quiet = float(np.nanquantile(speed, config.quiet_speed_quantile))
    speed_q_mobile = float(np.nanquantile(speed, config.mobile_speed_quantile))
    frac_q_quiet = float(np.nanquantile(outward_frac, config.quiet_outward_quantile))
    frac_q_out = float(np.nanquantile(outward_frac, config.outward_quantile))
    radial_q_out = float(np.nanquantile(radial, config.outward_quantile))
    quiet = (speed <= speed_q_quiet) & (outward_frac <= frac_q_quiet)
    mobile = speed >= speed_q_mobile
    outward = ((outward_frac >= frac_q_out) | (radial >= radial_q_out)) & ~mobile & ~quiet
    state = np.full(len(d), "other", dtype=object)
    state[quiet] = "quiet"
    state[outward] = "outward"
    state[mobile] = "mobile"
    thresholds = {
        "quiet_speed_threshold": speed_q_quiet,
        "mobile_speed_threshold": speed_q_mobile,
        "quiet_frac_outward_threshold": frac_q_quiet,
        "outward_frac_threshold": frac_q_out,
        "outward_radial_velocity_threshold": radial_q_out,
    }
    return state, thresholds


def first_passage_events(df: pd.DataFrame, config: RunConfig) -> pd.DataFrame:
    rows = []
    for (ob, dataset), d in df.groupby(["ob", "dataset"], sort=True):
        d = d.sort_values("t").reset_index(drop=True)
        dt = median_dt(d)
        if not np.isfinite(dt) or dt <= 0:
            continue
        min_quiet_frames = max(1, int(round(config.min_quiet_sec / dt)))
        max_follow_frames = max(1, int(round(config.max_follow_sec / dt)))
        state, thresholds = classify_states(d, config)
        quiet_runs = contiguous_true_runs(state == "quiet")
        event_id = 0
        for start, end in quiet_runs:
            quiet_len = end - start
            if quiet_len < min_quiet_frames:
                continue
            follow_start = start
            follow_end = min(len(d), start + max_follow_frames + 1)
            future = state[follow_start:follow_end]
            mobile_rel = np.flatnonzero(future == "mobile")
            outward_rel = np.flatnonzero(future == "outward")
            reached = mobile_rel.size > 0
            mobile_idx = int(follow_start + mobile_rel[0]) if reached else -1
            if reached:
                outward_before = outward_rel[outward_rel < mobile_rel[0]]
            else:
                outward_before = outward_rel
            visited_outward = outward_before.size > 0
            first_outward_idx = int(follow_start + outward_before[0]) if visited_outward else -1
            fpt_sec = float((mobile_idx - follow_start) * dt) if reached else math.nan
            first_outward_sec = float((first_outward_idx - follow_start) * dt) if visited_outward else math.nan
            channel = "outward_before_mobile" if reached and visited_outward else "mobile_without_outward" if reached else "censored_after_outward" if visited_outward else "censored_no_outward"
            rows.append(
                {
                    "dataset": str(dataset),
                    "ob": int(ob),
                    "episode_local_id": int(event_id),
                    "start_frame": int(start),
                    "start_t": float(d["t"].iloc[start]),
                    "quiet_duration_sec": float(quiet_len * dt),
                    "follow_limit_sec": float((follow_end - follow_start - 1) * dt),
                    "reached_mobile": bool(reached),
                    "fpt_sec": fpt_sec,
                    "visited_outward_before_mobile_or_censor": bool(visited_outward),
                    "first_outward_sec": first_outward_sec,
                    "channel": channel,
                    **thresholds,
                }
            )
            event_id += 1
    return pd.DataFrame(rows)


def summarize_events(events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if events.empty:
        return pd.DataFrame(), pd.DataFrame()
    rows = []
    for (ob, dataset), d in events.groupby(["ob", "dataset"], sort=True):
        reached = d[d["reached_mobile"]]
        outward = d[d["visited_outward_before_mobile_or_censor"]]
        no_outward = d[~d["visited_outward_before_mobile_or_censor"]]
        rows.append(
            {
                "ob": int(ob),
                "dataset": str(dataset),
                "n_quiet_episodes": int(len(d)),
                "n_reached_mobile": int(len(reached)),
                "mobile_probability": float(len(reached) / len(d)) if len(d) else math.nan,
                "median_fpt_sec": finite_median(reached["fpt_sec"].to_numpy(dtype="float64")),
                "n_with_outward": int(len(outward)),
                "mobile_probability_with_outward": float(outward["reached_mobile"].mean()) if len(outward) else math.nan,
                "n_without_outward": int(len(no_outward)),
                "mobile_probability_without_outward": float(no_outward["reached_mobile"].mean()) if len(no_outward) else math.nan,
                "median_first_outward_sec": finite_median(outward["first_outward_sec"].to_numpy(dtype="float64")) if len(outward) else math.nan,
            }
        )
    by_ob = pd.DataFrame(rows)
    overall_rows = []
    for label, d in [("all", events), ("with_outward", events[events["visited_outward_before_mobile_or_censor"]]), ("without_outward", events[~events["visited_outward_before_mobile_or_censor"]])]:
        reached = d[d["reached_mobile"]]
        overall_rows.append(
            {
                "group": label,
                "n_episodes": int(len(d)),
                "n_reached_mobile": int(len(reached)),
                "mobile_probability": float(len(reached) / len(d)) if len(d) else math.nan,
                "median_fpt_sec": finite_median(reached["fpt_sec"].to_numpy(dtype="float64")),
                "q25_fpt_sec": float(np.nanquantile(reached["fpt_sec"], 0.25)) if len(reached) else math.nan,
                "q75_fpt_sec": float(np.nanquantile(reached["fpt_sec"], 0.75)) if len(reached) else math.nan,
            }
        )
    overall = pd.DataFrame(overall_rows)
    return by_ob, overall


def transition_matrix(df: pd.DataFrame, config: RunConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    occupancy_rows = []
    for (ob, dataset), d in df.groupby(["ob", "dataset"], sort=True):
        d = d.sort_values("t").reset_index(drop=True)
        dt = median_dt(d)
        if not np.isfinite(dt) or dt <= 0:
            continue
        lag = max(1, int(round(config.transition_lag_sec / dt)))
        state, _ = classify_states(d, config)
        if len(state) <= lag:
            continue
        origin = state[:-lag]
        dest = state[lag:]
        for st in STATE_ORDER:
            occupancy_rows.append(
                {
                    "ob": int(ob),
                    "dataset": str(dataset),
                    "state": st,
                    "occupancy_fraction": float(np.mean(state == st)),
                }
            )
        for a in STATE_ORDER:
            mask = origin == a
            denom = int(mask.sum())
            for b in STATE_ORDER:
                count = int(np.sum(mask & (dest == b)))
                rows.append(
                    {
                        "ob": int(ob),
                        "dataset": str(dataset),
                        "from_state": a,
                        "to_state": b,
                        "lag_sec": float(lag * dt),
                        "count": count,
                        "origin_count": denom,
                        "transition_probability": float(count / denom) if denom else math.nan,
                        "transition_rate_per_sec": float(count / denom / (lag * dt)) if denom and lag * dt > 0 else math.nan,
                    }
                )
    trans = pd.DataFrame(rows)
    occ = pd.DataFrame(occupancy_rows)
    summary = (
        trans.groupby(["from_state", "to_state"], as_index=False)
        .agg(
            n_ob=("ob", "nunique"),
            median_transition_probability=("transition_probability", "median"),
            median_transition_rate_per_sec=("transition_rate_per_sec", "median"),
        )
        .sort_values(["from_state", "to_state"])
    )
    occ_summary = (
        occ.groupby("state", as_index=False)
        .agg(n_ob=("ob", "nunique"), median_occupancy_fraction=("occupancy_fraction", "median"))
        .sort_values("state")
    )
    return summary.merge(occ_summary, left_on="from_state", right_on="state", how="left").drop(columns=["state"]), trans


def plot_fpt(events: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    for label, color, mask in [
        ("with outward", "#4c78a8", events["visited_outward_before_mobile_or_censor"]),
        ("without outward", "#f58518", ~events["visited_outward_before_mobile_or_censor"]),
    ]:
        d = events[mask & events["reached_mobile"]]
        vals = np.sort(d["fpt_sec"].dropna().to_numpy(dtype="float64"))
        if vals.size == 0:
            continue
        survival = 1.0 - np.arange(1, vals.size + 1) / vals.size
        ax.step(vals, survival, where="post", lw=1.8, label=f"{label} (n={vals.size})", color=color)
    ax.set_xlabel("first-passage time to mobile (s)")
    ax.set_ylabel("empirical survival among reached episodes")
    ax.set_title("3013 quiet-to-mobile first-passage times")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG / "first_passage_survival_by_outward_visit.png", dpi=180)
    plt.close(fig)


def plot_transition_heatmap(trans_summary: pd.DataFrame) -> None:
    mat = np.full((len(STATE_ORDER), len(STATE_ORDER)), np.nan)
    for i, a in enumerate(STATE_ORDER):
        for j, b in enumerate(STATE_ORDER):
            d = trans_summary[(trans_summary["from_state"] == a) & (trans_summary["to_state"] == b)]
            if not d.empty:
                mat[i, j] = float(d["median_transition_probability"].iloc[0])
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    im = ax.imshow(mat, cmap="viridis", aspect="auto")
    ax.set_xticks(np.arange(len(STATE_ORDER)))
    ax.set_xticklabels(STATE_ORDER, rotation=30, ha="right")
    ax.set_yticks(np.arange(len(STATE_ORDER)))
    ax.set_yticklabels(STATE_ORDER)
    ax.set_xlabel("to state")
    ax.set_ylabel("from state")
    ax.set_title("3013 coarse transition probabilities")
    for i in range(len(STATE_ORDER)):
        for j in range(len(STATE_ORDER)):
            if np.isfinite(mat[i, j]):
                ax.text(j, i, f"{mat[i, j]:.2f}", ha="center", va="center", color="white" if mat[i, j] > 0.5 else "black", fontsize=8)
    fig.colorbar(im, ax=ax, label="median probability over lag")
    fig.tight_layout()
    fig.savefig(FIG / "coarse_state_transition_heatmap.png", dpi=180)
    plt.close(fig)


def write_summary(by_ob: pd.DataFrame, overall: pd.DataFrame, trans_summary: pd.DataFrame, config: RunConfig) -> None:
    with_out = overall[overall["group"] == "with_outward"]
    without = overall[overall["group"] == "without_outward"]
    p_with = float(with_out["mobile_probability"].iloc[0]) if not with_out.empty else math.nan
    p_without = float(without["mobile_probability"].iloc[0]) if not without.empty else math.nan
    ratio = p_with / p_without if np.isfinite(p_with) and np.isfinite(p_without) and p_without > 0 else math.nan
    supports_path = np.isfinite(ratio) and ratio >= 1.5
    next_step = "3014 diffusion-vs-master-equation model choice" if supports_path else "3013b basin-definition sensitivity"
    reading = (
        f"Outward-region visits increase quiet-to-mobile passage probability by a factor of about {ratio:.2f}, supporting a coarse first-passage pathway."
        if supports_path
        else "Outward-region visits do not clearly separate quiet-to-mobile passage probability under this basin definition; a basin-definition sensitivity check is needed before model selection."
    )
    text = f"""# 3013 Quiet-Mobile First Passage

## Scope

This module treats center-speed burst as a first-passage event from a quiet basin to a mobile basin, rather than as a framewise prediction target.

## Basin Definitions

- Quiet: center speed <= within-Ob {config.quiet_speed_quantile:.0%} quantile and `frac_outward` <= within-Ob {config.quiet_outward_quantile:.0%} quantile
- Mobile: center speed >= within-Ob {config.mobile_speed_quantile:.0%} quantile
- Outward transition region: `frac_outward` or `radial_velocity_mean` >= within-Ob {config.outward_quantile:.0%} quantile
- Minimum quiet duration: {config.min_quiet_sec:.2f}s
- Follow-up limit: {config.max_follow_sec:.2f}s

## Main Reading

{reading}

Recommended next linked experiment: `{next_step}`.

## Overall First-Passage Summary

{dataframe_to_markdown(overall)}

## By-Ob First-Passage Summary

{dataframe_to_markdown(by_ob, max_rows=25)}

## Coarse Transition Matrix Summary

{dataframe_to_markdown(trans_summary)}

## Interpretation Boundary

This module depends on basin definitions. It supports first-passage framing if outward-state visits consistently raise the probability or speed of reaching mobile, but it does not prove that outward motion causes mobile motion. The transition matrix is a coarse master-equation candidate, not yet a validated generative model.
"""
    (OUT / "3013_summary.md").write_text(text, encoding="utf-8")
    pd.DataFrame(
        [
            {
                "mobile_probability_with_outward": p_with,
                "mobile_probability_without_outward": p_without,
                "outward_mobile_probability_ratio": ratio,
                "supports_outward_first_passage_path": supports_path,
                "recommended_next_experiment": next_step,
            }
        ]
    ).to_csv(PROC / "decision_summary.csv", index=False)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-quiet-sec", type=float, default=0.20)
    parser.add_argument("--max-follow-sec", type=float, default=5.00)
    parser.add_argument("--mobile-speed-quantile", type=float, default=0.90)
    args = parser.parse_args()
    config = RunConfig(
        min_quiet_sec=args.min_quiet_sec,
        max_follow_sec=args.max_follow_sec,
        mobile_speed_quantile=args.mobile_speed_quantile,
    )
    ensure_dirs()
    print("[3013] reading 3010 state table", flush=True)
    df = read_input()
    print("[3013] first-passage episodes", flush=True)
    events = first_passage_events(df, config)
    by_ob, overall = summarize_events(events)
    print("[3013] transition matrix", flush=True)
    trans_summary, trans_by_ob = transition_matrix(df, config)

    events.to_csv(TAB / "quiet_mobile_first_passage_events.csv", index=False)
    by_ob.to_csv(TAB / "quiet_mobile_first_passage_by_ob.csv", index=False)
    overall.to_csv(TAB / "quiet_mobile_first_passage_overall.csv", index=False)
    trans_by_ob.to_csv(TAB / "coarse_state_transition_by_ob.csv", index=False)
    trans_summary.to_csv(TAB / "coarse_state_transition_summary.csv", index=False)
    pd.DataFrame([config.__dict__]).to_csv(PROC / "run_config.csv", index=False)

    plot_fpt(events)
    plot_transition_heatmap(trans_summary)
    write_summary(by_ob, overall, trans_summary, config)
    print("[3013] done")
    print(f"[3013] summary: {OUT / '3013_summary.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
