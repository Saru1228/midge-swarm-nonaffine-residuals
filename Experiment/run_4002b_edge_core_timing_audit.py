#!/usr/bin/env python3
"""Experiment 4002B: edge/core residual timing audit.

4002A found that affine-residual velocities include edge/core redistribution.
4002B asks whether that edge/core residual redistribution appears before the
compact-density transition, at the transition, or mainly after it.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4002B"
FIG = OUT / "figures"
TAB = OUT / "tables"
PROC = OUT / "processed"

EVENTS_3045 = ROOT / "Output" / "3045" / "tables" / "transition_events.csv"
FRAME_4002A = ROOT / "Output" / "4002A" / "processed" / "frame_residual_spatial_metrics.csv"
COMPARISON_4002A = ROOT / "Output" / "4002A" / "tables" / "residual_structure_direction_null_comparison.csv"

RNG_SEED = 400202
WINDOWS = {
    "baseline": (-0.70, -0.45),
    "pre": (-0.30, -0.05),
    "event": (-0.05, 0.05),
    "post": (0.05, 0.30),
    "follow": (0.35, 0.60),
}


@dataclass(frozen=True)
class RunConfig:
    n_null: int = 160
    timing_gap_gate_z: float = 0.10
    null_p_gate: float = 0.10
    min_ob_gate: int = 12
    pre_to_post_ratio_gate: float = 0.50
    min_pretrigger_variables: int = 1
    min_event_or_post_variables: int = 1


def ensure_dirs() -> None:
    for path in (OUT, FIG, TAB, PROC):
        path.mkdir(parents=True, exist_ok=True)


def safe_float(value: object) -> float:
    try:
        out = float(value)
    except Exception:
        return math.nan
    return out if np.isfinite(out) else math.nan


def finite_median(values: Iterable[float]) -> float:
    arr = np.asarray(list(values), dtype="float64")
    arr = arr[np.isfinite(arr)]
    return float(np.median(arr)) if arr.size else math.nan


def sign_consistency(values: Iterable[float]) -> float:
    arr = np.asarray(list(values), dtype="float64")
    arr = arr[np.isfinite(arr)]
    signs = np.sign(arr)
    signs = signs[signs != 0]
    if not signs.size:
        return math.nan
    counts = pd.Series(signs).value_counts()
    return float(counts.iloc[0] / signs.size)


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


def read_events() -> pd.DataFrame:
    events = pd.read_csv(EVENTS_3045)
    for col in ["event_id", "ob", "event_t"]:
        events[col] = pd.to_numeric(events[col], errors="coerce")
    events = events.dropna(subset=["event_id", "ob", "dataset", "event_t", "event_type"]).copy()
    events["event_id"] = events["event_id"].astype("int64")
    events["ob"] = events["ob"].astype("int64")
    return events.sort_values(["ob", "event_t"], kind="mergesort").reset_index(drop=True)


def selected_edge_core_variables() -> pd.DataFrame:
    comparison = pd.read_csv(COMPARISON_4002A)
    edge = comparison[comparison["family"].astype(str).eq("edge_core")].copy()
    if "direction_survives_gate" in edge.columns:
        selected = edge[edge["direction_survives_gate"].astype(bool)].copy()
    else:
        selected = edge.head(0).copy()
    if selected.empty:
        selected = edge.sort_values("real_minus_null_abs_direction_contrast_z", ascending=False).head(2).copy()
    selected["orientation"] = np.sign(pd.to_numeric(selected["real_median_direction_contrast_z"], errors="coerce"))
    selected.loc[selected["orientation"] == 0, "orientation"] = 1.0
    return selected[["variable", "family", "real_median_direction_contrast_z", "orientation"]].reset_index(drop=True)


def read_frame_metrics(variables: list[str]) -> pd.DataFrame:
    needed = {"ob", "dataset", "t", *[f"{var}__resid4002a" for var in variables]}
    frame = pd.read_csv(FRAME_4002A, usecols=lambda c: c in needed)
    missing = sorted(needed - set(frame.columns))
    if missing:
        raise ValueError(f"Missing columns in {FRAME_4002A}: {missing}")
    for col in frame.columns:
        if col != "dataset":
            frame[col] = pd.to_numeric(frame[col], errors="coerce")
    frame["ob"] = frame["ob"].astype("int64")
    return frame.sort_values(["ob", "t"], kind="mergesort").reset_index(drop=True)


def build_arrays(frame: pd.DataFrame, variables: list[str]) -> dict[tuple[int, str], dict[str, np.ndarray]]:
    arrays: dict[tuple[int, str], dict[str, np.ndarray]] = {}
    for (ob, dataset), d0 in frame.groupby(["ob", "dataset"], sort=True):
        d = d0.sort_values("t").reset_index(drop=True)
        rec: dict[str, np.ndarray] = {"t": d["t"].to_numpy(dtype="float64")}
        for var in variables:
            rec[var] = d[f"{var}__resid4002a"].to_numpy(dtype="float64")
        arrays[(int(ob), str(dataset))] = rec
    return arrays


def event_direction_sign(event_type: str) -> float:
    if event_type == "low_to_high":
        return 1.0
    if event_type == "high_to_low":
        return -1.0
    return math.nan


def window_mean(t: np.ndarray, x: np.ndarray, event_t: float, lo: float, hi: float) -> float:
    i0 = int(np.searchsorted(t, event_t + lo, side="left"))
    i1 = int(np.searchsorted(t, event_t + hi, side="right"))
    if i1 <= i0:
        return math.nan
    vals = x[i0:i1]
    return safe_float(np.nanmean(vals)) if np.isfinite(vals).any() else math.nan


def extract_timing_features(
    arrays: dict[tuple[int, str], dict[str, np.ndarray]],
    events: pd.DataFrame,
    variables: list[str],
    orientations: dict[str, float],
) -> pd.DataFrame:
    rows = []
    for event in events.itertuples(index=False):
        event_sign = event_direction_sign(str(event.event_type))
        if not np.isfinite(event_sign):
            continue
        rec = arrays.get((int(event.ob), str(event.dataset)))
        if rec is None:
            continue
        t = rec["t"]
        event_t = float(event.event_t)
        for var in variables:
            orient = orientations.get(var, 1.0)
            x = rec[var] * event_sign * orient
            vals = {name: window_mean(t, x, event_t, *bounds) for name, bounds in WINDOWS.items()}
            if not np.isfinite(vals["baseline"]):
                continue
            rows.append(
                {
                    "event_id": int(event.event_id),
                    "ob": int(event.ob),
                    "dataset": str(event.dataset),
                    "event_t": event_t,
                    "event_type": str(event.event_type),
                    "variable": var,
                    "baseline_aligned_z": vals["baseline"],
                    "pre_aligned_z": vals["pre"],
                    "event_aligned_z": vals["event"],
                    "post_aligned_z": vals["post"],
                    "follow_aligned_z": vals["follow"],
                    "pre_minus_baseline_z": vals["pre"] - vals["baseline"] if np.isfinite(vals["pre"]) else math.nan,
                    "event_minus_baseline_z": vals["event"] - vals["baseline"] if np.isfinite(vals["event"]) else math.nan,
                    "post_minus_baseline_z": vals["post"] - vals["baseline"] if np.isfinite(vals["post"]) else math.nan,
                    "follow_minus_baseline_z": vals["follow"] - vals["baseline"] if np.isfinite(vals["follow"]) else math.nan,
                    "post_minus_pre_z": vals["post"] - vals["pre"] if np.isfinite(vals["post"]) and np.isfinite(vals["pre"]) else math.nan,
                }
            )
    return pd.DataFrame(rows)


def summarize_timing(features: pd.DataFrame, prefix: str = "real") -> pd.DataFrame:
    if features.empty:
        return pd.DataFrame()
    metrics = [
        "pre_minus_baseline_z",
        "event_minus_baseline_z",
        "post_minus_baseline_z",
        "follow_minus_baseline_z",
        "post_minus_pre_z",
    ]
    by_ob = features.groupby(["ob", "variable"], as_index=False).agg(
        n_events=("event_id", "nunique"),
        **{metric: (metric, "median") for metric in metrics},
    )
    rows = []
    for variable, d in by_ob.groupby("variable", sort=True):
        row = {"variable": variable, "n_ob": int(d["ob"].nunique()), "n_events": int(d["n_events"].sum())}
        for metric in metrics:
            row[f"{prefix}_median_{metric}"] = finite_median(d[metric])
            row[f"{prefix}_sign_consistency_{metric}"] = sign_consistency(d[metric])
        post = abs(row[f"{prefix}_median_post_minus_baseline_z"])
        pre = abs(row[f"{prefix}_median_pre_minus_baseline_z"])
        row[f"{prefix}_pre_to_post_abs_ratio"] = pre / post if np.isfinite(pre) and np.isfinite(post) and post > 1e-12 else math.nan
        rows.append(row)
    return pd.DataFrame(rows).sort_values(f"{prefix}_median_post_minus_baseline_z", ascending=False)


def shifted_events(events: pd.DataFrame, arrays: dict[tuple[int, str], dict[str, np.ndarray]], rng: np.random.Generator) -> pd.DataFrame:
    parts = []
    for (ob, dataset), d0 in events.groupby(["ob", "dataset"], sort=True):
        rec = arrays.get((int(ob), str(dataset)))
        if rec is None:
            continue
        t = rec["t"]
        if t.size < 2:
            continue
        t_min = float(np.nanmin(t))
        t_max = float(np.nanmax(t))
        span = t_max - t_min
        if not np.isfinite(span) or span <= 0:
            continue
        shift = float(rng.uniform(0.10 * span, 0.90 * span))
        d = d0.copy()
        d["event_t"] = ((pd.to_numeric(d["event_t"], errors="coerce") - t_min + shift) % span) + t_min
        parts.append(d)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


def run_nulls(
    arrays: dict[tuple[int, str], dict[str, np.ndarray]],
    events: pd.DataFrame,
    variables: list[str],
    orientations: dict[str, float],
    cfg: RunConfig,
) -> pd.DataFrame:
    rng = np.random.default_rng(RNG_SEED)
    rows = []
    for replicate in range(1, cfg.n_null + 1):
        shifted = shifted_events(events, arrays, rng)
        features = extract_timing_features(arrays, shifted, variables, orientations)
        summary = summarize_timing(features, prefix="null")
        summary["replicate"] = int(replicate)
        rows.append(summary)
        if replicate == 1 or replicate % 25 == 0 or replicate == cfg.n_null:
            print(f"[4002B] null replicate {replicate}/{cfg.n_null}", flush=True)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def compare_timing_to_null(real: pd.DataFrame, null: pd.DataFrame, cfg: RunConfig) -> pd.DataFrame:
    metrics = [
        "pre_minus_baseline_z",
        "event_minus_baseline_z",
        "post_minus_baseline_z",
        "follow_minus_baseline_z",
        "post_minus_pre_z",
    ]
    rows = []
    for rec in real.itertuples(index=False):
        variable = rec.variable
        d = null[null["variable"] == variable]
        row = {
            "variable": variable,
            "n_ob": int(rec.n_ob),
            "n_events": int(rec.n_events),
            "real_pre_to_post_abs_ratio": safe_float(getattr(rec, "real_pre_to_post_abs_ratio")),
        }
        for metric in metrics:
            real_val = safe_float(getattr(rec, f"real_median_{metric}"))
            null_vals = d[f"null_median_{metric}"].to_numpy(dtype="float64") if not d.empty and f"null_median_{metric}" in d else np.array([])
            null_vals = null_vals[np.isfinite(null_vals)]
            null_med = float(np.median(null_vals)) if null_vals.size else math.nan
            gap = real_val - null_med if np.isfinite(real_val) and np.isfinite(null_med) else math.nan
            p_ge = float((1 + np.sum(null_vals >= real_val)) / (len(null_vals) + 1)) if null_vals.size else math.nan
            row[f"real_{metric}"] = real_val
            row[f"null_median_{metric}"] = null_med
            row[f"real_minus_null_{metric}"] = gap
            row[f"p_null_ge_real_{metric}"] = p_ge
            row[f"sign_consistency_{metric}"] = safe_float(getattr(rec, f"real_sign_consistency_{metric}"))
            row[f"gate_{metric}"] = bool(
                rec.n_ob >= cfg.min_ob_gate
                and np.isfinite(gap)
                and gap >= cfg.timing_gap_gate_z
                and np.isfinite(p_ge)
                and p_ge <= cfg.null_p_gate
                and row[f"sign_consistency_{metric}"] >= 0.70
            )
        row["pretrigger_gate"] = bool(
            row["gate_pre_minus_baseline_z"]
            and row["real_pre_to_post_abs_ratio"] >= cfg.pre_to_post_ratio_gate
        )
        row["event_or_post_gate"] = bool(row["gate_event_minus_baseline_z"] or row["gate_post_minus_baseline_z"])
        rows.append(row)
    return pd.DataFrame(rows).sort_values("real_minus_null_pre_minus_baseline_z", ascending=False)


def decision_summary(comparison: pd.DataFrame, cfg: RunConfig) -> pd.DataFrame:
    pre_vars = comparison[comparison["pretrigger_gate"]]["variable"].astype(str).tolist() if not comparison.empty else []
    event_post_vars = comparison[comparison["event_or_post_gate"]]["variable"].astype(str).tolist() if not comparison.empty else []
    follow_vars = comparison[comparison["gate_follow_minus_baseline_z"]]["variable"].astype(str).tolist() if not comparison.empty else []
    if len(pre_vars) >= cfg.min_pretrigger_variables:
        decision = "support_pretransition_edge_core_residual_candidate"
        next_node = "4002c predictive edge/core residual audit"
        boundary = "Edge/core residual redistribution is detectable before transitions under shifted-event timing gates."
    elif len(event_post_vars) >= cfg.min_event_or_post_variables:
        decision = "boundary_edge_core_residual_transition_coupled_not_pretrigger"
        next_node = "4002c shell-definition robustness or synthesize residual-spatial boundary"
        boundary = "Edge/core residual redistribution is tied to event/post windows but does not pass pretransition trigger gates."
    elif len(follow_vars) >= cfg.min_event_or_post_variables:
        decision = "boundary_edge_core_residual_lagging_response"
        next_node = "pause edge/core trigger route"
        boundary = "Edge/core residual redistribution mainly follows transitions."
    else:
        decision = "weak_edge_core_residual_timing_signal"
        next_node = "pause edge/core timing route"
        boundary = "4002A edge/core signal does not survive timing-window shifted null gates."
    return pd.DataFrame(
        [
            {
                "node_id": "4002b_edge_core_timing_audit",
                "node_type": "timing robustness",
                "n_pretrigger_variables": int(len(pre_vars)),
                "n_event_or_post_variables": int(len(event_post_vars)),
                "n_follow_variables": int(len(follow_vars)),
                "pretrigger_variables": ", ".join(pre_vars),
                "event_or_post_variables": ", ".join(event_post_vars),
                "follow_variables": ", ".join(follow_vars),
                "eg_rt_decision": decision,
                "recommended_next_node": next_node,
                "boundary_reading": boundary,
            }
        ]
    )


def aligned_profiles(
    arrays: dict[tuple[int, str], dict[str, np.ndarray]],
    events: pd.DataFrame,
    variables: list[str],
    orientations: dict[str, float],
) -> pd.DataFrame:
    rel_grid = np.round(np.arange(-0.75, 0.76, 0.05), 5)
    rows = []
    for var in variables:
        samples = []
        for event in events.itertuples(index=False):
            event_sign = event_direction_sign(str(event.event_type))
            rec = arrays.get((int(event.ob), str(event.dataset)))
            if rec is None or not np.isfinite(event_sign):
                continue
            t = rec["t"]
            x = rec[var] * event_sign * orientations.get(var, 1.0)
            target = float(event.event_t) + rel_grid
            valid = (target >= np.nanmin(t)) & (target <= np.nanmax(t))
            y = np.full(rel_grid.shape, np.nan, dtype="float64")
            if np.any(valid):
                y[valid] = np.interp(target[valid], t, x)
            samples.append(y)
        if not samples:
            continue
        mat = np.vstack(samples)
        med = np.nanmedian(mat, axis=0)
        q25 = np.nanquantile(mat, 0.25, axis=0)
        q75 = np.nanquantile(mat, 0.75, axis=0)
        for rel_t, m, lo, hi in zip(rel_grid, med, q25, q75):
            rows.append(
                {
                    "variable": var,
                    "relative_time_sec": float(rel_t),
                    "median_aligned_resid_z": safe_float(m),
                    "q25_aligned_resid_z": safe_float(lo),
                    "q75_aligned_resid_z": safe_float(hi),
                    "n_events": int(len(samples)),
                }
            )
    return pd.DataFrame(rows)


def make_figures(comparison: pd.DataFrame, profiles: pd.DataFrame) -> None:
    if not comparison.empty:
        d = comparison.sort_values("real_pre_minus_baseline_z", ascending=True)
        y = np.arange(len(d))
        fig, ax = plt.subplots(figsize=(8.2, 3.8))
        ax.barh(y - 0.22, d["real_pre_minus_baseline_z"], height=0.22, label="pre", color="#4c78a8")
        ax.barh(y, d["real_event_minus_baseline_z"], height=0.22, label="event", color="#8b6f2d")
        ax.barh(y + 0.22, d["real_post_minus_baseline_z"], height=0.22, label="post", color="#b55d60")
        ax.axvline(0.0, color="#222222", linewidth=0.8)
        ax.set_yticks(y)
        ax.set_yticklabels(d["variable"])
        ax.set_xlabel("direction-aligned change vs baseline (z)")
        ax.set_title("4002B edge/core residual timing")
        ax.legend(frameon=False)
        fig.tight_layout()
        fig.savefig(FIG / "edge_core_timing_window_changes.png", dpi=180)
        plt.close(fig)

    if not profiles.empty:
        variables = list(dict.fromkeys(profiles["variable"].tolist()))
        fig, axes = plt.subplots(len(variables), 1, figsize=(8.4, max(3.0, 2.4 * len(variables))), sharex=True)
        if len(variables) == 1:
            axes = [axes]
        for ax, var in zip(axes, variables):
            d = profiles[profiles["variable"] == var].sort_values("relative_time_sec")
            ax.plot(d["relative_time_sec"], d["median_aligned_resid_z"], color="#4c78a8", lw=1.8)
            ax.fill_between(d["relative_time_sec"], d["q25_aligned_resid_z"], d["q75_aligned_resid_z"], color="#4c78a8", alpha=0.16)
            ax.axvline(0.0, color="#222222", linewidth=0.8)
            ax.axhline(0.0, color="#999999", linewidth=0.7)
            ax.set_ylabel(var)
            ax.grid(alpha=0.20)
        axes[0].set_title("4002B direction-aligned edge/core residual profiles")
        axes[-1].set_xlabel("time relative to transition (sec)")
        fig.tight_layout()
        fig.savefig(FIG / "edge_core_aligned_timing_profiles.png", dpi=180)
        plt.close(fig)


def write_node_schema(decision: pd.DataFrame, selected: pd.DataFrame, cfg: RunConfig) -> None:
    rec = decision.iloc[0].to_dict()
    node = {
        "node_id": "4002b_edge_core_timing_audit",
        "series": "4xxx",
        "node_type": "timing robustness",
        "parent_node": "4002a_residual_spatial_structure_audit",
        "question": "Does edge/core residual redistribution precede compact-density transitions or mainly align with event/post windows?",
        "competing_interpretations": [
            "H_pretrigger: edge/core residual redistribution appears before transition",
            "H_event_coupled: edge/core redistribution appears at or after transition",
            "H_shift_null: shifted event times show comparable timing changes",
        ],
        "input_artifacts": [
            "Output/4002A/processed/frame_residual_spatial_metrics.csv",
            "Output/4002A/tables/residual_structure_direction_null_comparison.csv",
            "Output/3045/tables/transition_events.csv",
        ],
        "method": [
            "select 4002A edge/core direction survivors",
            "orient variables by their 4002A direction contrast",
            "compare baseline, pre, event, post, and follow windows",
            f"compare with {cfg.n_null} circularly shifted event-time nulls",
        ],
        "selected_variables": selected.to_dict("records"),
        "outputs": [
            "Output/4002B/tables/edge_core_timing_null_comparison.csv",
            "Output/4002B/tables/egrt_decision_summary.csv",
            "Output/4002B/4002B_summary.md",
        ],
        "provenance": {"script": "Experiment/run_4002b_edge_core_timing_audit.py", "config": asdict(cfg), "decision": rec},
    }
    (OUT / "4002B_egrt_node.json").write_text(json.dumps(node, ensure_ascii=False, indent=2), encoding="utf-8")


def write_summary(selected: pd.DataFrame, comparison: pd.DataFrame, decision: pd.DataFrame, cfg: RunConfig) -> None:
    rec = decision.iloc[0]
    text = f"""# 4002B Edge/Core Residual Timing Audit

## Scope

4002A found edge/core residual redistribution after subtracting affine geometry.
4002B asks whether that redistribution is early enough to be a trigger
candidate or mainly event/post coupled.

## EGRT Node

| field | value |
| --- | --- |
| node_id | 4002b_edge_core_timing_audit |
| parent | 4002a_residual_spatial_structure_audit |
| node_type | timing robustness |
| decision | {rec['eg_rt_decision']} |
| recommended next node | {rec['recommended_next_node']} |
| boundary reading | {rec['boundary_reading']} |

## Selected Variables

{dataframe_to_markdown(selected)}

## Methods

- Input frame metrics: `Output/4002A/processed/frame_residual_spatial_metrics.csv`.
- Selected 4002A edge/core survivors and oriented them so positive means the
  event-direction-consistent edge/core change.
- Timing windows:
  - baseline: `{WINDOWS['baseline']}` seconds
  - pre: `{WINDOWS['pre']}` seconds
  - event: `{WINDOWS['event']}` seconds
  - post: `{WINDOWS['post']}` seconds
  - follow: `{WINDOWS['follow']}` seconds
- Null replicates: `{cfg.n_null}` shifted-event replicates.

## Decision Metrics

{dataframe_to_markdown(decision)}

## Timing Null Comparison

{dataframe_to_markdown(comparison)}

## Interpretation

If pre windows fail but event/post windows pass, edge/core residual
redistribution should be treated as transition-coupled, not as a validated
pre-transition trigger.

## Outputs

- `Output/4002B/4002B_egrt_node.json`
- `Output/4002B/tables/edge_core_timing_null_comparison.csv`
- `Output/4002B/tables/egrt_decision_summary.csv`
- `Output/4002B/figures/edge_core_timing_window_changes.png`
- `Output/4002B/figures/edge_core_aligned_timing_profiles.png`
"""
    (OUT / "4002B_summary.md").write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-null", type=int, default=RunConfig.n_null)
    parser.add_argument("--quick", action="store_true", help="Use 40 shifted-event null replicates.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cfg = RunConfig(n_null=40 if args.quick else args.n_null)
    ensure_dirs()
    selected = selected_edge_core_variables()
    variables = selected["variable"].astype(str).tolist()
    orientations = dict(zip(selected["variable"].astype(str), pd.to_numeric(selected["orientation"], errors="coerce")))
    events = read_events()
    frame = read_frame_metrics(variables)
    arrays = build_arrays(frame, variables)
    features = extract_timing_features(arrays, events, variables, orientations)
    real_summary = summarize_timing(features, prefix="real")
    null_summary = run_nulls(arrays, events, variables, orientations, cfg)
    comparison = compare_timing_to_null(real_summary, null_summary, cfg)
    decision = decision_summary(comparison, cfg)
    profiles = aligned_profiles(arrays, events, variables, orientations)

    features.to_csv(TAB / "edge_core_timing_features.csv", index=False)
    real_summary.to_csv(TAB / "real_edge_core_timing_summary.csv", index=False)
    null_summary.to_csv(TAB / "shift_null_edge_core_timing_summary.csv", index=False)
    comparison.to_csv(TAB / "edge_core_timing_null_comparison.csv", index=False)
    decision.to_csv(TAB / "egrt_decision_summary.csv", index=False)
    selected.to_csv(TAB / "selected_edge_core_variables.csv", index=False)
    profiles.to_csv(TAB / "edge_core_aligned_timing_profiles.csv", index=False)
    pd.DataFrame([asdict(cfg)]).to_csv(PROC / "run_config.csv", index=False)

    make_figures(comparison, profiles)
    write_node_schema(decision, selected, cfg)
    write_summary(selected, comparison, decision, cfg)
    print(decision.to_string(index=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
