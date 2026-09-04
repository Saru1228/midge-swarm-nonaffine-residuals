#!/usr/bin/env python3
"""Experiment 4030: coarse-grained stochastic state-transition pilot.

4030 follows the mixed 4020/4020B result. It stops looking for one stable
edge/core residual metric and instead asks a coarser stochastic question:

    Does a high/low residual-state bin modulate compact-state transition
    probabilities in one observation?

This is a single-observation pilot. It uses affine-residual one-fish state
metrics produced by 4020 and compact high/low labels from 3045.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from run_4001_geometric_baseline_residual_audit import safe_float


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4030" / "Ob3"
FIG = OUT / "figures"
TAB = OUT / "tables"
PROC = OUT / "processed"
COMPACT_FRAME = ROOT / "Output" / "3045" / "processed" / "frame_residual_signals.csv"

RNG_SEED = 403001


@dataclass(frozen=True)
class RunConfig:
    pilot_ob: int = 3
    state_frame_metrics: str = r"Output\4020B\Ob3\processed\frame_one_fish_state_metrics.csv"
    output_subdir: str = r"4030\Ob3"
    lag_sec: float = 0.20
    n_null: int = 64
    min_cell_count: int = 100
    modulation_gate: float = 0.030
    real_minus_null_gate: float = 0.015
    null_p_gate: float = 0.15
    min_survivors_for_expand: int = 2


def ensure_dirs() -> None:
    for path in (OUT, FIG, TAB, PROC):
        path.mkdir(parents=True, exist_ok=True)


def out_rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


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


def median_dt(times: np.ndarray) -> float:
    t = np.unique(np.asarray(times, dtype="float64"))
    t = t[np.isfinite(t)]
    if t.size < 2:
        return math.nan
    return safe_float(np.nanmedian(np.diff(t)))


def load_merged_frame(cfg: RunConfig) -> pd.DataFrame:
    state_path = ROOT / cfg.state_frame_metrics
    if not state_path.exists():
        raise FileNotFoundError(f"Missing 4020 state frame metrics: {state_path}")
    if not COMPACT_FRAME.exists():
        raise FileNotFoundError(f"Missing compact frame labels: {COMPACT_FRAME}")

    state = pd.read_csv(state_path)
    state = state[state["ob"].astype(int) == int(cfg.pilot_ob)].copy()
    compact = pd.read_csv(COMPACT_FRAME)
    compact = compact[compact["ob"].astype(int) == int(cfg.pilot_ob)].copy()
    if state.empty or compact.empty:
        raise ValueError(f"No frame rows for Ob{cfg.pilot_ob}")

    for df in (state, compact):
        df["t_key"] = pd.to_numeric(df["t"], errors="coerce").round(5)
        df["dataset"] = df["dataset"].astype(str)
    compact = compact[["ob", "dataset", "t_key", "spectral_set"]].copy()
    merged = state.merge(compact, on=["ob", "dataset", "t_key"], how="inner")
    merged = merged[merged["spectral_set"].isin(["low", "high"])].copy()
    merged = merged.sort_values("t", kind="mergesort").reset_index(drop=True)
    if merged.empty:
        raise ValueError("No merged compact-state rows after joining 4020 and 3045 frames")
    return merged


def residual_variables(frame: pd.DataFrame) -> list[str]:
    cols = [col for col in frame.columns if col.endswith("__resid4020")]
    return [col.removesuffix("__resid4020") for col in cols]


def prob(mask: np.ndarray, target: np.ndarray) -> float:
    mask = np.asarray(mask, dtype=bool)
    if int(mask.sum()) == 0:
        return math.nan
    return float(np.mean(target[mask]))


def modulation_for_bin(current: np.ndarray, next_state: np.ndarray, high_bin: np.ndarray) -> dict[str, float]:
    cur_low = current == "low"
    cur_high = current == "high"
    next_high = next_state == "high"
    next_low = next_state == "low"

    cells = {
        "low_bin_high": cur_low & high_bin,
        "low_bin_low": cur_low & ~high_bin,
        "high_bin_high": cur_high & high_bin,
        "high_bin_low": cur_high & ~high_bin,
    }
    p_up_highbin = prob(cells["low_bin_high"], next_high)
    p_up_lowbin = prob(cells["low_bin_low"], next_high)
    p_down_highbin = prob(cells["high_bin_high"], next_low)
    p_down_lowbin = prob(cells["high_bin_low"], next_low)
    up_gap = p_up_highbin - p_up_lowbin if np.isfinite(p_up_highbin) and np.isfinite(p_up_lowbin) else math.nan
    down_gap = p_down_highbin - p_down_lowbin if np.isfinite(p_down_highbin) and np.isfinite(p_down_lowbin) else math.nan

    abs_up = abs(up_gap) if np.isfinite(up_gap) else math.nan
    abs_down = abs(down_gap) if np.isfinite(down_gap) else math.nan
    if np.isfinite(abs_up) and (not np.isfinite(abs_down) or abs_up >= abs_down):
        dominant = "low_to_high"
        dominant_gap = up_gap
        abs_modulation = abs_up
    elif np.isfinite(abs_down):
        dominant = "high_to_low"
        dominant_gap = down_gap
        abs_modulation = abs_down
    else:
        dominant = ""
        dominant_gap = math.nan
        abs_modulation = math.nan

    return {
        "n_low_bin_high": int(cells["low_bin_high"].sum()),
        "n_low_bin_low": int(cells["low_bin_low"].sum()),
        "n_high_bin_high": int(cells["high_bin_high"].sum()),
        "n_high_bin_low": int(cells["high_bin_low"].sum()),
        "p_up_given_resid_high": safe_float(p_up_highbin),
        "p_up_given_resid_low": safe_float(p_up_lowbin),
        "p_down_given_resid_high": safe_float(p_down_highbin),
        "p_down_given_resid_low": safe_float(p_down_lowbin),
        "up_gap": safe_float(up_gap),
        "down_gap": safe_float(down_gap),
        "dominant_transition": dominant,
        "dominant_gap": safe_float(dominant_gap),
        "abs_transition_modulation": safe_float(abs_modulation),
        "min_cell_count": int(min(v.sum() for v in cells.values())),
    }


def real_modulation(frame: pd.DataFrame, cfg: RunConfig) -> pd.DataFrame:
    dt = median_dt(frame["t"].to_numpy(dtype="float64"))
    lag_steps = max(1, int(round(cfg.lag_sec / dt))) if np.isfinite(dt) and dt > 0 else 20
    d = frame.copy()
    d["next_spectral_set"] = d["spectral_set"].shift(-lag_steps)
    d = d[d["next_spectral_set"].isin(["low", "high"])].copy()
    current = d["spectral_set"].astype(str).to_numpy()
    next_state = d["next_spectral_set"].astype(str).to_numpy()

    rows = []
    for var in residual_variables(d):
        x = pd.to_numeric(d[f"{var}__resid4020"], errors="coerce").to_numpy(dtype="float64")
        finite = x[np.isfinite(x)]
        if finite.size < 10:
            continue
        med = float(np.median(finite))
        high_bin = x > med
        high_bin[~np.isfinite(x)] = False
        rec = modulation_for_bin(current, next_state, high_bin)
        rec.update(
            {
                "variable": var,
                "n_frames": int(len(d)),
                "lag_sec": float(cfg.lag_sec),
                "lag_steps": int(lag_steps),
                "residual_bin_median": safe_float(med),
            }
        )
        rows.append(rec)
    return pd.DataFrame(rows).sort_values("abs_transition_modulation", ascending=False)


def null_modulation(frame: pd.DataFrame, cfg: RunConfig) -> pd.DataFrame:
    rng = np.random.default_rng(RNG_SEED)
    dt = median_dt(frame["t"].to_numpy(dtype="float64"))
    lag_steps = max(1, int(round(cfg.lag_sec / dt))) if np.isfinite(dt) and dt > 0 else 20
    d = frame.copy()
    d["next_spectral_set"] = d["spectral_set"].shift(-lag_steps)
    d = d[d["next_spectral_set"].isin(["low", "high"])].copy()
    current = d["spectral_set"].astype(str).to_numpy()
    next_state = d["next_spectral_set"].astype(str).to_numpy()
    n = len(d)

    rows = []
    for replicate in range(1, cfg.n_null + 1):
        shift = int(rng.integers(max(1, int(0.10 * n)), max(2, int(0.90 * n))))
        for var in residual_variables(d):
            x = pd.to_numeric(d[f"{var}__resid4020"], errors="coerce").to_numpy(dtype="float64")
            finite = x[np.isfinite(x)]
            if finite.size < 10:
                continue
            med = float(np.median(finite))
            high_bin = x > med
            high_bin[~np.isfinite(x)] = False
            shifted_bin = np.roll(high_bin, shift)
            rec = modulation_for_bin(current, next_state, shifted_bin)
            rows.append(
                {
                    "replicate": int(replicate),
                    "variable": var,
                    "null_abs_transition_modulation": safe_float(rec["abs_transition_modulation"]),
                }
            )
        if replicate == 1 or replicate % 16 == 0 or replicate == cfg.n_null:
            print(f"[4030] shifted residual-bin null replicate {replicate}/{cfg.n_null}", flush=True)
    return pd.DataFrame(rows)


def compare_to_null(real: pd.DataFrame, null: pd.DataFrame, cfg: RunConfig) -> pd.DataFrame:
    rows = []
    for rec in real.itertuples(index=False):
        vals = null.loc[null["variable"] == rec.variable, "null_abs_transition_modulation"].to_numpy(dtype="float64")
        vals = vals[np.isfinite(vals)]
        real_abs = safe_float(rec.abs_transition_modulation)
        null_med = float(np.median(vals)) if vals.size else math.nan
        gap = real_abs - null_med if np.isfinite(real_abs) and np.isfinite(null_med) else math.nan
        p = float((1 + np.sum(vals >= real_abs)) / (len(vals) + 1)) if vals.size else math.nan
        gate = bool(
            rec.min_cell_count >= cfg.min_cell_count
            and np.isfinite(real_abs)
            and real_abs >= cfg.modulation_gate
            and np.isfinite(gap)
            and gap >= cfg.real_minus_null_gate
            and np.isfinite(p)
            and p <= cfg.null_p_gate
        )
        row = rec._asdict()
        row.update(
            {
                "null_abs_transition_modulation": null_med,
                "real_minus_null_abs_transition_modulation": gap,
                "p_null_abs_transition_ge_real": p,
                "pilot_survives_gate": gate,
            }
        )
        rows.append(row)
    return pd.DataFrame(rows).sort_values("real_minus_null_abs_transition_modulation", ascending=False)


def decision_summary(comparison: pd.DataFrame, cfg: RunConfig) -> pd.DataFrame:
    survivors = comparison[comparison["pilot_survives_gate"]].copy() if not comparison.empty else pd.DataFrame()
    if len(survivors) >= cfg.min_survivors_for_expand:
        decision = "pilot_support_coarse_state_transition_modulation"
        next_node = "4030b single-observation replication"
        boundary = "Multiple residual bins modulate coarse compact-state transition probabilities beyond shifted-bin nulls."
    elif len(survivors) == 1:
        decision = "boundary_single_coarse_state_modulation_variable"
        next_node = "pause full run; optionally test one adjacent observation"
        boundary = "Only one residual bin passes; not enough for broad coarse-state claim."
    else:
        decision = "weak_coarse_state_transition_modulation_pilot"
        next_node = "4040 4xxx synthesis and pause"
        boundary = "No residual coarse state modulates compact-state transitions beyond shifted-bin null gates."

    return pd.DataFrame(
        [
            {
                "node_id": "4030_coarse_grained_stochastic_state_transition_pilot",
                "node_type": "single-observation stochastic coarse-graining pilot",
                "pilot_ob": int(cfg.pilot_ob),
                "n_surviving_variables": int(len(survivors)),
                "surviving_variables": ", ".join(survivors["variable"].astype(str).tolist()) if not survivors.empty else "",
                "eg_rt_decision": decision,
                "recommended_next_node": next_node,
                "boundary_reading": boundary,
            }
        ]
    )


def make_figures(comparison: pd.DataFrame) -> None:
    if comparison.empty:
        return
    d = comparison.sort_values("real_minus_null_abs_transition_modulation", ascending=True)
    fig, ax = plt.subplots(figsize=(9.2, max(4.6, 0.34 * len(d) + 1.6)))
    y = np.arange(len(d))
    colors = ["#4c78a8" if gate else "#8795a1" for gate in d["pilot_survives_gate"]]
    bars = ax.barh(y, d["real_minus_null_abs_transition_modulation"], color=colors, alpha=0.9)
    for bar, gate in zip(bars, d["pilot_survives_gate"]):
        if bool(gate):
            ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, " *", va="center", ha="left", fontsize=12)
    ax.axvline(0.0, color="#222222", linewidth=0.8)
    ax.axvline(0.015, color="#777777", linewidth=0.7, linestyle="--")
    ax.set_yticks(y)
    ax.set_yticklabels(d["variable"])
    ax.set_xlabel("real - shifted-bin transition modulation")
    ax.set_title("4030 coarse residual-state transition modulation pilot")
    fig.tight_layout()
    fig.savefig(FIG / "coarse_state_transition_modulation_screen.png", dpi=180)
    plt.close(fig)


def write_node_schema(decision: pd.DataFrame, cfg: RunConfig) -> None:
    rec = decision.iloc[0].to_dict()
    node = {
        "node_id": "4030_coarse_grained_stochastic_state_transition_pilot",
        "series": "4xxx",
        "node_type": "single-observation stochastic coarse-graining pilot",
        "parent_node": "4020B_selective_single_observation_replication",
        "question": "Does a high/low residual-state bin modulate compact-state transition probabilities in one observation?",
        "competing_interpretations": [
            "H_coarse_state: residual states affect compact-state transition probabilities at a coarse stochastic level",
            "H_metric_instability: 4020 variables differ because only coarse residual state matters",
            "H_shift_null: circularly shifted residual bins produce comparable transition modulation",
        ],
        "input_artifacts": [
            cfg.state_frame_metrics,
            "Output/3045/processed/frame_residual_signals.csv",
        ],
        "method": [
            f"run pilot on Ob{cfg.pilot_ob}",
            "bin each residual state metric into high/low by its within-ob median",
            f"look ahead {cfg.lag_sec} seconds to compact high/low state",
            "compare transition probability modulation against circularly shifted residual-bin nulls",
        ],
        "pass_gate": {
            "cell_count": f"minimum cell count >= {cfg.min_cell_count}",
            "modulation": f"absolute transition modulation >= {cfg.modulation_gate}",
            "null_gap": f"real-null modulation gap >= {cfg.real_minus_null_gate}",
            "null_p": f"p <= {cfg.null_p_gate}",
        },
        "outputs": [
            out_rel(TAB / "coarse_state_transition_modulation_comparison.csv"),
            out_rel(TAB / "egrt_decision_summary.csv"),
            out_rel(OUT / "4030_summary.md"),
        ],
        "provenance": {"script": "Experiment/run_4030_coarse_grained_stochastic_state_transition_pilot.py", "config": asdict(cfg), "decision": rec},
    }
    (OUT / "4030_egrt_node.json").write_text(json.dumps(node, ensure_ascii=False, indent=2), encoding="utf-8")


def write_summary(comparison: pd.DataFrame, decision: pd.DataFrame, cfg: RunConfig) -> None:
    rec = decision.iloc[0]
    survivors = comparison[comparison["pilot_survives_gate"]].copy() if not comparison.empty else pd.DataFrame()
    top = comparison.sort_values("real_minus_null_abs_transition_modulation", ascending=False).head(8) if not comparison.empty else pd.DataFrame()
    text = f"""# 4030 Coarse-Grained Stochastic State-Transition Pilot

## Scope

4030 follows the mixed `4020/4020B` result. It tests whether residual-state
metrics are more useful after coarse-graining into high/low stochastic states.

Plain-language question:

> If a residual state is high rather than low, does the compact state become
> more likely to switch within the next `{cfg.lag_sec}` seconds?

## EGRT Node

| field | value |
| --- | --- |
| node_id | 4030_coarse_grained_stochastic_state_transition_pilot |
| parent | 4020B_selective_single_observation_replication |
| node_type | single-observation stochastic coarse-graining pilot |
| pilot observation | Ob{cfg.pilot_ob} |
| decision | {rec.eg_rt_decision} |
| recommended next node | {rec.recommended_next_node} |
| boundary reading | {rec.boundary_reading} |

## Methods

- Load affine-residual one-fish state metrics from `{cfg.state_frame_metrics}`.
- Merge compact high/low labels from `Output/3045/processed/frame_residual_signals.csv`.
- Bin each residual variable into high/low by within-ob median.
- Estimate compact-state transition probability after `{cfg.lag_sec}` sec.
- Compare real modulation with `{cfg.n_null}` circularly shifted residual-bin nulls.

## Decision Metrics

{dataframe_to_markdown(decision)}

## Pilot-Surviving Variables

{dataframe_to_markdown(survivors)}

## Top Rows

{dataframe_to_markdown(top)}

## Interpretation

This is still a pilot. A positive result means the route should replicate one
observation at a time; a weak result means the 4xxx branch should synthesize and
pause rather than keep searching for a mechanism.

## Outputs

- `{out_rel(OUT / "4030_egrt_node.json")}`
- `{out_rel(TAB / "coarse_state_transition_modulation_comparison.csv")}`
- `{out_rel(TAB / "egrt_decision_summary.csv")}`
- `{out_rel(FIG / "coarse_state_transition_modulation_screen.png")}`
"""
    (OUT / "4030_summary.md").write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-ob", type=int, default=RunConfig.pilot_ob)
    parser.add_argument("--state-frame-metrics", default=RunConfig.state_frame_metrics)
    parser.add_argument("--output-subdir", default=RunConfig.output_subdir)
    parser.add_argument("--lag-sec", type=float, default=RunConfig.lag_sec)
    parser.add_argument("--n-null", type=int, default=RunConfig.n_null)
    parser.add_argument("--quick", action="store_true", help="Use 24 shifted-bin null replicates.")
    return parser.parse_args()


def main() -> int:
    global OUT, FIG, TAB, PROC
    args = parse_args()
    subdir = Path(args.output_subdir)
    if subdir.is_absolute() or ".." in subdir.parts:
        raise ValueError("--output-subdir must be a safe relative path under Output/")
    OUT = ROOT / "Output" / subdir
    FIG = OUT / "figures"
    TAB = OUT / "tables"
    PROC = OUT / "processed"

    cfg = RunConfig(
        pilot_ob=args.pilot_ob,
        state_frame_metrics=args.state_frame_metrics,
        output_subdir=args.output_subdir,
        lag_sec=args.lag_sec,
        n_null=24 if args.quick else args.n_null,
    )
    ensure_dirs()
    pd.DataFrame([asdict(cfg)]).to_csv(PROC / "run_config.csv", index=False)

    frame = load_merged_frame(cfg)
    print(f"[4030] merged Ob{cfg.pilot_ob}: {len(frame)} frames", flush=True)
    real = real_modulation(frame, cfg)
    null = null_modulation(frame, cfg)
    comparison = compare_to_null(real, null, cfg)
    decision = decision_summary(comparison, cfg)
    make_figures(comparison)

    frame.to_csv(PROC / "merged_compact_residual_state_frame.csv", index=False)
    real.to_csv(TAB / "real_coarse_state_transition_modulation.csv", index=False)
    null.to_csv(TAB / "shift_null_coarse_state_transition_modulation.csv", index=False)
    comparison.to_csv(TAB / "coarse_state_transition_modulation_comparison.csv", index=False)
    decision.to_csv(TAB / "egrt_decision_summary.csv", index=False)
    write_node_schema(decision, cfg)
    write_summary(comparison, decision, cfg)

    print(decision.to_string(index=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
