#!/usr/bin/env python3
"""Experiment 3032c: smooth-autocorrelation null audit for 3032b.

3032b found an interpretable but shallow compact-density partition. This node
tests whether its retention is stronger than nulls that preserve smooth
single-variable autocorrelation or linear multivariate cross-correlation.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Experiment"))

from run_3032b_state_meaning_residence_audit import (  # noqa: E402
    EMISSION_VARIABLES,
    RunConfig as AuditConfig,
    assign_cells_from_edges,
    attach_partition_labels,
    candidate_variables,
    lag_retention,
    read_edges,
    read_input,
    read_mapping,
    residence_runs,
    residence_summary,
    standardize_columns,
)
from run_3032_transfer_operator_metastability import (  # noqa: E402
    SET_ORDER,
    dataframe_to_markdown,
    finite_median,
    finite_quantile,
    safe_float,
)


OUT = ROOT / "Output" / "3032c"
DECISION_3032B = ROOT / "Output" / "3032b" / "tables" / "egrt_decision_summary.csv"
FIG = OUT / "figures"
TAB = OUT / "tables"
PROC = OUT / "processed"
RNG_SEED = 30323


@dataclass(frozen=True)
class RunConfig:
    n_surrogates: int = 24
    lags_sec: tuple[float, ...] = (0.05, 0.10, 0.20, 0.50, 1.00)
    long_lag_sec: float = 0.50
    n_bins: int = 4
    smooth_null_gap_gate: float = 0.05
    smooth_null_p_gate: float = 0.10
    explained_gap_gate: float = 0.03
    scatter_jitter: float = 0.045


def ensure_dirs() -> None:
    for path in (OUT, FIG, TAB, PROC):
        path.mkdir(parents=True, exist_ok=True)


def read_parent_decision() -> dict[str, object]:
    if not DECISION_3032B.exists():
        raise FileNotFoundError("Run 3032b first; missing Output/3032b/tables/egrt_decision_summary.csv")
    df = pd.read_csv(DECISION_3032B)
    if df.empty:
        raise ValueError("3032b decision table is empty")
    return df.iloc[0].to_dict()


def rank_match(source: np.ndarray, target: np.ndarray) -> np.ndarray:
    source = np.asarray(source, dtype="float64")
    target = np.asarray(target, dtype="float64")
    order = np.argsort(source, kind="mergesort")
    matched = np.empty_like(source, dtype="float64")
    matched[order] = np.sort(target)
    return matched


def phase_surrogate_group(
    d: pd.DataFrame,
    variables: list[str],
    rng: np.random.Generator,
    coupled: bool,
) -> pd.DataFrame:
    out = d.copy()
    n = len(d)
    if n < 20:
        return out
    common_phase = None
    if coupled:
        common_phase = rng.uniform(0.0, 2.0 * math.pi, len(np.fft.rfft(np.zeros(n))))
        common_phase[0] = 0.0
        if n % 2 == 0:
            common_phase[-1] = 0.0
    for var in variables:
        zcol = f"{var}_z"
        x = pd.to_numeric(d[zcol], errors="coerce").to_numpy(dtype="float64")
        if np.sum(np.isfinite(x)) < 20:
            continue
        x = pd.Series(x).interpolate(limit_direction="both").to_numpy(dtype="float64")
        centered = x - float(np.mean(x))
        fft = np.fft.rfft(centered)
        if coupled:
            phases = common_phase
        else:
            phases = rng.uniform(0.0, 2.0 * math.pi, len(fft))
            phases[0] = 0.0
            if n % 2 == 0:
                phases[-1] = 0.0
        y = np.fft.irfft(np.abs(fft) * np.exp(1j * (np.angle(fft) + phases)), n=n)
        y = rank_match(y, x)
        out[zcol] = y
    return out


def make_continuous_surrogate(
    df: pd.DataFrame,
    variables: list[str],
    edges: dict[str, list[float]],
    mapping: pd.DataFrame,
    cfg: RunConfig,
    rng: np.random.Generator,
    surrogate_type: str,
) -> pd.DataFrame:
    pieces = []
    coupled = surrogate_type == "coupled_phase_rank"
    for (_ob, _dataset), d in df.groupby(["ob", "dataset"], sort=True):
        pieces.append(phase_surrogate_group(d.sort_values("t").reset_index(drop=True), variables, rng, coupled=coupled))
    zdf = pd.concat(pieces, ignore_index=True)
    zdf = assign_cells_from_edges(zdf, variables, edges, cfg.n_bins)
    labeled = attach_partition_labels(zdf, mapping)
    return labeled[labeled["spectral_set"].isin(SET_ORDER)].reset_index(drop=True)


def make_label_shuffle(real_df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    pieces = []
    for (_ob, _dataset), d in real_df.groupby(["ob", "dataset"], sort=True):
        d = d.sort_values("t").copy()
        labels = d["spectral_set"].to_numpy(dtype=object).copy()
        rng.shuffle(labels)
        d["spectral_set"] = labels
        pieces.append(d)
    return pd.concat(pieces, ignore_index=True)


def metric_from_lag_summary(lag_summary: pd.DataFrame, lag_sec: float, column: str) -> float:
    d = lag_summary[np.isclose(lag_summary["lag_sec"], lag_sec)]
    return finite_median(d[column]) if not d.empty and column in d.columns else math.nan


def metric_from_residence(summary: pd.DataFrame, row_name: str, column: str) -> float:
    d = summary[summary["spectral_set"] == row_name]
    return safe_float(d[column].iloc[0]) if not d.empty and column in d.columns else math.nan


def summarize_one_dataset(
    df: pd.DataFrame,
    audit_cfg: AuditConfig,
    label: str,
    replicate: int,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, float]]:
    _detail, lag_summary = lag_retention(df, audit_cfg)
    runs = residence_runs(df)
    res = residence_summary(runs, audit_cfg)
    lag_summary = lag_summary.copy()
    lag_summary["surrogate_type"] = label
    lag_summary["replicate"] = int(replicate)
    res = res.copy()
    res["surrogate_type"] = label
    res["replicate"] = int(replicate)
    metrics = {
        "long_lag_q25_lift_median_sets": metric_from_lag_summary(lag_summary, audit_cfg.long_lag_sec, "q25_retention_lift"),
        "long_lag_q25_retention_median_sets": metric_from_lag_summary(lag_summary, audit_cfg.long_lag_sec, "q25_retention"),
        "lag0p1_q25_lift_median_sets": metric_from_lag_summary(lag_summary, 0.10, "q25_retention_lift"),
        "lag1p0_q25_lift_median_sets": metric_from_lag_summary(lag_summary, 1.00, "q25_retention_lift"),
        "median_residence_all": metric_from_residence(res, "all", "median_run_duration_sec"),
        "q75_residence_all": metric_from_residence(res, "all", "q75_run_duration_sec"),
        "q90_residence_all": metric_from_residence(res, "all", "q90_run_duration_sec"),
    }
    return lag_summary, res, metrics


def compare_nulls(real_metrics: dict[str, float], surrogate_metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for metric, real_value in real_metrics.items():
        for surrogate_type, d in surrogate_metrics.groupby("surrogate_type", sort=True):
            vals = pd.to_numeric(d[metric], errors="coerce").to_numpy(dtype="float64")
            vals = vals[np.isfinite(vals)]
            if vals.size == 0:
                rows.append(
                    {
                        "metric": metric,
                        "surrogate_type": surrogate_type,
                        "real_value": real_value,
                        "null_n": 0,
                        "null_median": math.nan,
                        "null_q75": math.nan,
                        "null_q95": math.nan,
                        "real_minus_null_median": math.nan,
                        "p_null_ge_real": math.nan,
                    }
                )
                continue
            p_ge = float((np.sum(vals >= real_value) + 1) / (len(vals) + 1)) if np.isfinite(real_value) else math.nan
            rows.append(
                {
                    "metric": metric,
                    "surrogate_type": surrogate_type,
                    "real_value": real_value,
                    "null_n": int(len(vals)),
                    "null_median": float(np.median(vals)),
                    "null_q75": float(np.quantile(vals, 0.75)),
                    "null_q95": float(np.quantile(vals, 0.95)),
                    "null_max": float(np.max(vals)),
                    "real_minus_null_median": real_value - float(np.median(vals)) if np.isfinite(real_value) else math.nan,
                    "p_null_ge_real": p_ge,
                }
            )
    return pd.DataFrame(rows)


def decision_summary(
    parent_decision: dict[str, object],
    real_metrics: dict[str, float],
    comparison: pd.DataFrame,
    cfg: RunConfig,
) -> pd.DataFrame:
    metric = "long_lag_q25_lift_median_sets"
    coupled = comparison[(comparison["metric"] == metric) & (comparison["surrogate_type"] == "coupled_phase_rank")]
    independent = comparison[(comparison["metric"] == metric) & (comparison["surrogate_type"] == "independent_phase_rank")]
    shuffle = comparison[(comparison["metric"] == metric) & (comparison["surrogate_type"] == "label_shuffle")]
    real_value = real_metrics.get(metric, math.nan)
    coupled_gap = safe_float(coupled["real_minus_null_median"].iloc[0]) if not coupled.empty else math.nan
    coupled_p = safe_float(coupled["p_null_ge_real"].iloc[0]) if not coupled.empty else math.nan
    coupled_q75 = safe_float(coupled["null_q75"].iloc[0]) if not coupled.empty else math.nan
    coupled_q95 = safe_float(coupled["null_q95"].iloc[0]) if not coupled.empty else math.nan
    independent_gap = safe_float(independent["real_minus_null_median"].iloc[0]) if not independent.empty else math.nan
    shuffle_gap = safe_float(shuffle["real_minus_null_median"].iloc[0]) if not shuffle.empty else math.nan

    survives_coupled = (
        np.isfinite(real_value)
        and np.isfinite(coupled_q95)
        and real_value > coupled_q95
        and np.isfinite(coupled_gap)
        and coupled_gap >= cfg.smooth_null_gap_gate
        and np.isfinite(coupled_p)
        and coupled_p <= cfg.smooth_null_p_gate
    )
    explained_by_coupled = (
        np.isfinite(coupled_gap)
        and coupled_gap <= cfg.explained_gap_gate
    ) or (np.isfinite(coupled_q75) and np.isfinite(real_value) and real_value <= coupled_q75)

    if survives_coupled:
        decision = "survives_smooth_null_extend_cautiously"
        next_node = "3032d local transition mechanism audit"
        boundary = "The compact-density partition exceeds smooth multivariate phase nulls, so a local transition-mechanism audit is justified."
    elif explained_by_coupled:
        decision = "stop_strong_metastability_claim_smooth_null_sufficient"
        next_node = "return to synthesis: compact-density slow mode, not strong metastable attractor"
        boundary = "The retention of the compact-density partition is explainable by smooth autocorrelation/cross-correlation nulls; do not claim a strong metastable attractor."
    else:
        decision = "boundary_ambiguous_smooth_null"
        next_node = "optional robustness with stricter multivariate surrogates"
        boundary = "The real partition is above simple nulls but not cleanly beyond the smooth multivariate null."

    return pd.DataFrame(
        [
            {
                "node_id": "3032c_smooth_null_audit",
                "parent_node": "3032b_state_meaning_residence_audit",
                "parent_decision": str(parent_decision.get("eg_rt_decision", "")),
                "metric": metric,
                "real_long_lag_q25_lift": real_value,
                "coupled_phase_null_median_gap": coupled_gap,
                "coupled_phase_null_q75": coupled_q75,
                "coupled_phase_null_q95": coupled_q95,
                "coupled_phase_p_null_ge_real": coupled_p,
                "independent_phase_null_median_gap": independent_gap,
                "label_shuffle_null_median_gap": shuffle_gap,
                "survives_coupled_phase_gate": bool(survives_coupled),
                "explained_by_coupled_phase": bool(explained_by_coupled),
                "eg_rt_decision": decision,
                "recommended_next_node": next_node,
                "boundary_reading": boundary,
            }
        ]
    )


def write_node_schema(decision: pd.DataFrame, cfg: RunConfig) -> None:
    rec = decision.iloc[0].to_dict()
    node = {
        "node_id": "3032c_smooth_null_audit",
        "series": "303x",
        "node_type": "artifact-control",
        "parent_node": "3032b_state_meaning_residence_audit",
        "question": "Is the compact-density partition retention stronger than smooth autocorrelation nulls?",
        "competing_interpretations": [
            "true metastable compact-density state",
            "smooth autocorrelation and linear cross-correlation",
            "occupancy-only label persistence artifact",
        ],
        "method": [
            "label-shuffle null preserving only spectral-set occupancy",
            "independent phase-rank null preserving each slow variable's marginal distribution and power spectrum",
            "coupled phase-rank null preserving common linear smooth structure across slow variables",
            f"{cfg.n_surrogates} replicates per null",
            f"primary metric: q25 retention lift at {cfg.long_lag_sec}s, median over low/high sets",
        ],
        "pass_gate": {
            "real_above_coupled_q95": True,
            "real_minus_coupled_median": f">= {cfg.smooth_null_gap_gate}",
            "p_null_ge_real": f"<= {cfg.smooth_null_p_gate}",
        },
        "next_if_pass": "3032d local transition mechanism audit",
        "next_if_fail": "synthesis: compact-density slow mode, not strong metastable attractor",
        "outputs": [
            "Output/3032c/tables/null_comparison_summary.csv",
            "Output/3032c/tables/surrogate_metric_summary.csv",
            "Output/3032c/tables/egrt_decision_summary.csv",
            "Output/3032c/3032c_summary.md",
        ],
        "provenance": {
            "script": "Experiment/run_3032c_smooth_null_audit.py",
            "decision": rec,
        },
    }
    (OUT / "3032c_egrt_node.json").write_text(json.dumps(node, ensure_ascii=False, indent=2), encoding="utf-8")


def make_figures(
    real_lag: pd.DataFrame,
    surrogate_lag: pd.DataFrame,
    comparison: pd.DataFrame,
    surrogate_metrics: pd.DataFrame,
    cfg: RunConfig,
) -> None:
    metric = "long_lag_q25_lift_median_sets"
    d = surrogate_metrics[["surrogate_type", "replicate", metric]].copy()
    if not d.empty:
        order = ["label_shuffle", "independent_phase_rank", "coupled_phase_rank"]
        data = [d[d["surrogate_type"] == name][metric].dropna().to_numpy(dtype="float64") for name in order]
        fig, ax = plt.subplots(figsize=(8.2, 4.8))
        ax.boxplot(data, tick_labels=order, showfliers=False)
        rng = np.random.default_rng(RNG_SEED)
        for i, vals in enumerate(data, start=1):
            if len(vals):
                x = i + rng.uniform(-cfg.scatter_jitter, cfg.scatter_jitter, len(vals))
                ax.scatter(x, vals, s=16, alpha=0.45, color="#555555", linewidths=0)
        real_value = safe_float(comparison[comparison["metric"] == metric]["real_value"].iloc[0]) if not comparison.empty else math.nan
        if np.isfinite(real_value):
            ax.axhline(real_value, color="#c23b22", linewidth=1.3, label="real")
        ax.set_ylabel(f"q25 retention lift at {cfg.long_lag_sec:g}s")
        ax.set_title("3032c smooth-null comparison")
        ax.tick_params(axis="x", rotation=15)
        ax.legend(frameon=False)
        fig.tight_layout()
        fig.savefig(FIG / "long_lag_lift_null_comparison.png", dpi=180)
        plt.close(fig)

    if not real_lag.empty and not surrogate_lag.empty:
        fig, ax = plt.subplots(figsize=(8.2, 5.0))
        real = real_lag.groupby("lag_sec", as_index=False)["q25_retention_lift"].median()
        ax.plot(real["lag_sec"], real["q25_retention_lift"], marker="o", color="#c23b22", label="real")
        colors = {
            "label_shuffle": "#8a8a8a",
            "independent_phase_rank": "#4c78a8",
            "coupled_phase_rank": "#f58518",
        }
        for stype, d_stype in surrogate_lag.groupby("surrogate_type", sort=True):
            med = d_stype.groupby("lag_sec", as_index=False)["q25_retention_lift"].median()
            ax.plot(med["lag_sec"], med["q25_retention_lift"], marker="o", color=colors.get(stype, "#666666"), label=stype)
        ax.axhline(0.0, color="#222222", linewidth=0.7)
        ax.axvline(cfg.long_lag_sec, color="#777777", linestyle="--", linewidth=0.8)
        ax.set_xlabel("lag (s)")
        ax.set_ylabel("median q25 retention lift")
        ax.set_title("3032c retention-lift decay vs nulls")
        ax.legend(frameon=False)
        fig.tight_layout()
        fig.savefig(FIG / "retention_lift_decay_vs_nulls.png", dpi=180)
        plt.close(fig)


def write_summary(
    decision: pd.DataFrame,
    comparison: pd.DataFrame,
    real_metrics: dict[str, float],
    cfg: RunConfig,
) -> None:
    rec = decision.iloc[0]
    primary = comparison[comparison["metric"] == "long_lag_q25_lift_median_sets"].copy()
    summary = f"""# 3032c EGRT Smooth-Null Audit

## Scope

3032b showed that the 3032 partition is interpretable but shallow. 3032c tests whether the observed retention exceeds null models that preserve smoothness in the slow variables.

## EGRT Node

| field | value |
| --- | --- |
| node_id | 3032c_smooth_null_audit |
| parent | 3032b_state_meaning_residence_audit |
| node_type | artifact-control |
| decision | {rec['eg_rt_decision']} |
| recommended next node | {rec['recommended_next_node']} |
| boundary reading | {rec['boundary_reading']} |

## Nulls

- `label_shuffle`: preserves only low/high occupancy inside each Ob.
- `independent_phase_rank`: preserves each slow variable's marginal distribution and approximate power spectrum, but breaks cross-variable phase coupling.
- `coupled_phase_rank`: applies common phase shifts to the slow-variable spectra before rank matching, preserving a stronger smooth multivariate linear null.

## Decision Metrics

{dataframe_to_markdown(decision)}

## Primary Null Comparison

{dataframe_to_markdown(primary)}

## All Null Metrics

{dataframe_to_markdown(comparison)}

## Real Metric Values

{dataframe_to_markdown(pd.DataFrame([real_metrics]))}

## Outputs

- `Output/3032c/3032c_egrt_node.json`
- `Output/3032c/tables/null_comparison_summary.csv`
- `Output/3032c/tables/surrogate_metric_summary.csv`
- `Output/3032c/tables/surrogate_lag_summary.csv`
- `Output/3032c/tables/surrogate_residence_summary.csv`
- `Output/3032c/tables/egrt_decision_summary.csv`
- `Output/3032c/figures/long_lag_lift_null_comparison.png`
- `Output/3032c/figures/retention_lift_decay_vs_nulls.png`

## Interpretation Boundary

If the real compact-density partition is not above the coupled phase-rank null, the strongest supported statement is a descriptive slow compactness mode with smooth persistence. That is weaker than a metastable attractor claim and should terminate this 3032 branch unless a new observable basis is introduced.
"""
    (OUT / "3032c_summary.md").write_text(summary, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-surrogates", type=int, default=RunConfig.n_surrogates)
    parser.add_argument("--quick", action="store_true", help="Use 6 surrogate replicates.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cfg = RunConfig(n_surrogates=6 if args.quick else args.n_surrogates)
    audit_cfg = AuditConfig(lags_sec=cfg.lags_sec, long_lag_sec=cfg.long_lag_sec)
    ensure_dirs()
    parent_decision = read_parent_decision()
    if str(parent_decision.get("eg_rt_decision", "")) not in {
        "boundary_shallow_but_persistent_organization",
        "extend_metastable_state_branch",
    }:
        raise RuntimeError("3032b did not route to a smooth-null audit.")
    variables = candidate_variables(parent_decision)
    best_partition_id = str(parent_decision.get("best_partition_id", "eig2"))
    edges = read_edges()
    mapping = read_mapping(best_partition_id)

    raw = read_input(variables)
    standardized = standardize_columns(raw, sorted(set(EMISSION_VARIABLES + variables)))
    base = assign_cells_from_edges(standardized, variables, edges, cfg.n_bins)
    real_df = attach_partition_labels(base, mapping)
    real_df = real_df[real_df["spectral_set"].isin(SET_ORDER)].reset_index(drop=True)
    real_lag, real_res, real_metrics = summarize_one_dataset(real_df, audit_cfg, "real", 0)

    rng = np.random.default_rng(RNG_SEED)
    lag_tables = []
    res_tables = []
    metric_rows = []
    for replicate in range(1, cfg.n_surrogates + 1):
        for surrogate_type in ["label_shuffle", "independent_phase_rank", "coupled_phase_rank"]:
            if surrogate_type == "label_shuffle":
                sdf = make_label_shuffle(real_df, rng)
            else:
                sdf = make_continuous_surrogate(base, variables, edges, mapping, cfg, rng, surrogate_type)
            lag_summary, res_summary, metrics = summarize_one_dataset(sdf, audit_cfg, surrogate_type, replicate)
            lag_tables.append(lag_summary)
            res_tables.append(res_summary)
            metric_rows.append({"surrogate_type": surrogate_type, "replicate": replicate, **metrics})

    surrogate_lag = pd.concat(lag_tables, ignore_index=True) if lag_tables else pd.DataFrame()
    surrogate_res = pd.concat(res_tables, ignore_index=True) if res_tables else pd.DataFrame()
    surrogate_metrics = pd.DataFrame(metric_rows)
    comparison = compare_nulls(real_metrics, surrogate_metrics)
    decision = decision_summary(parent_decision, real_metrics, comparison, cfg)

    real_lag.to_csv(TAB / "real_lag_summary.csv", index=False)
    real_res.to_csv(TAB / "real_residence_summary.csv", index=False)
    pd.DataFrame([real_metrics]).to_csv(TAB / "real_metric_values.csv", index=False)
    surrogate_lag.to_csv(TAB / "surrogate_lag_summary.csv", index=False)
    surrogate_res.to_csv(TAB / "surrogate_residence_summary.csv", index=False)
    surrogate_metrics.to_csv(TAB / "surrogate_metric_summary.csv", index=False)
    comparison.to_csv(TAB / "null_comparison_summary.csv", index=False)
    comparison.to_csv(PROC / "null_comparison_summary.csv", index=False)
    decision.to_csv(TAB / "egrt_decision_summary.csv", index=False)
    decision.to_csv(PROC / "egrt_decision_summary.csv", index=False)

    write_node_schema(decision, cfg)
    make_figures(real_lag, surrogate_lag, comparison, surrogate_metrics, cfg)
    write_summary(decision, comparison, real_metrics, cfg)
    print(decision.to_string(index=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
