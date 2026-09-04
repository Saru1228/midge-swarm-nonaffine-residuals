"""4120 state-path feasibility / coordinate freeze.

This node starts the 412x route after the 4105 state-matched negative
synthesis. It does not test history dependence. It only checks whether recent
C-R state-path features can be computed stably enough to enter 4121.

Current state is frozen as:

    C    = density_rms_z3045
    dCdt = gradient(density_rms_smooth3045, t)
    R    = r_rms_z3045

Path features are computed from smoothed C and R traces to avoid interpreting
raw frame noise as path direction:

    C_path = density_rms_smooth3045
    R_path = r_rms_smooth3045
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from textwrap import dedent

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4120"
DATE = "2026-08-27"

STATE_PATH = ROOT / "Output" / "3045" / "processed" / "frame_residual_signals.csv"
ACTIVITY_PATH = ROOT / "Output" / "4100A" / "swarm_activity_frame.csv"

WINDOWS = [0.25, 0.50, 0.75]
PRIMARY_H = 0.50

BASE_COLUMNS = [
    "ob",
    "dataset",
    "t",
    "A_swarm_tangential_z",
    "C",
    "dCdt",
    "R",
    "C_path",
    "R_path",
    "dRdt",
    "path_velocity_norm",
    "theta_v",
    "theta_v_valid",
]

QC_COLUMNS = [
    "ob",
    "dataset",
    "history_window_sec",
    "n_frames",
    "finite_current_state_fraction",
    "finite_activity_fraction",
    "finite_dRdt_fraction",
    "path_feature_coverage",
    "theta_valid_fraction",
    "turning_valid_fraction",
    "median_path_length",
    "q05_path_length",
    "q95_path_length",
    "theta_resultant_length",
    "median_abs_turning_proxy_rad",
    "q95_abs_turning_proxy_rad",
    "median_path_velocity_norm",
    "q99_abs_dRdt",
]

SENS_COLUMNS = [
    "history_window_sec",
    "n_observations",
    "obs_path_coverage_ge_0p90",
    "median_path_feature_coverage",
    "min_path_feature_coverage",
    "median_theta_valid_fraction",
    "min_theta_valid_fraction",
    "median_path_length",
    "median_abs_turning_proxy_rad",
]

COVERAGE_COLUMNS = [
    "ob",
    "dataset",
    "n_frames",
    "median_dt_sec",
    "finite_current_state_fraction",
    "finite_activity_fraction",
    "finite_dRdt_fraction",
    "primary_path_feature_coverage",
    "primary_theta_valid_fraction",
    "primary_turning_valid_fraction",
]

LEAK_COLUMNS = [
    "ob",
    "dataset",
    "history_window_sec",
    "history_feature",
    "current_state",
    "spearman_corr",
    "pearson_corr",
    "n",
]


def ensure_dirs() -> None:
    (OUT / "figures").mkdir(parents=True, exist_ok=True)
    (OUT / "tables").mkdir(parents=True, exist_ok=True)


def win_tag(h: float) -> str:
    return f"h{int(round(h * 1000)):03d}"


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


def interp_sorted(t_src: np.ndarray, y_src: np.ndarray, t_dst: np.ndarray) -> np.ndarray:
    ok = np.isfinite(t_src) & np.isfinite(y_src)
    out = np.full(t_dst.shape, np.nan, dtype="float64")
    if ok.sum() < 2:
        return out
    lo = float(np.nanmin(t_src[ok]))
    hi = float(np.nanmax(t_src[ok]))
    inside = np.isfinite(t_dst) & (t_dst >= lo) & (t_dst <= hi)
    out[inside] = np.interp(t_dst[inside], t_src[ok], y_src[ok])
    return out


def angle_diff(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.arctan2(np.sin(a - b), np.cos(a - b))


def angle_between_vectors(v1x: np.ndarray, v1y: np.ndarray, v2x: np.ndarray, v2y: np.ndarray) -> np.ndarray:
    cross = v1x * v2y - v1y * v2x
    dot = v1x * v2x + v1y * v2y
    return np.arctan2(cross, dot)


def finite_fraction(values: np.ndarray) -> float:
    arr = np.asarray(values)
    return float(np.isfinite(arr).mean()) if arr.size else math.nan


def circular_resultant_length(theta: np.ndarray) -> float:
    arr = np.asarray(theta, dtype="float64")
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return math.nan
    return float(np.sqrt(np.nanmean(np.cos(arr)) ** 2 + np.nanmean(np.sin(arr)) ** 2))


def corr_pair(x: np.ndarray, y: np.ndarray, method: str) -> tuple[float, int]:
    d = pd.DataFrame({"x": x, "y": y}).replace([np.inf, -np.inf], np.nan).dropna()
    if len(d) < 20:
        return math.nan, int(len(d))
    val = d["x"].corr(d["y"], method=method)
    return (float(val) if pd.notna(val) else math.nan), int(len(d))


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
    state["ob"] = pd.to_numeric(state["ob"], errors="coerce").astype("Int64")
    state["t"] = pd.to_numeric(state["t"], errors="coerce")
    state["C"] = pd.to_numeric(state["density_rms_z3045"], errors="coerce")
    state["R"] = pd.to_numeric(state["r_rms_z3045"], errors="coerce")
    state["C_path"] = pd.to_numeric(state["density_rms_smooth3045"], errors="coerce")
    state["R_path"] = pd.to_numeric(state["r_rms_smooth3045"], errors="coerce")
    state["dCdt"] = math.nan
    state["dRdt"] = math.nan
    for _, idx in state.groupby("ob", sort=True).groups.items():
        d = state.loc[idx].sort_values("t")
        t = d["t"].to_numpy(dtype="float64")
        c = d["C_path"].to_numpy(dtype="float64")
        r = d["R_path"].to_numpy(dtype="float64")
        dcdt = np.full(len(d), np.nan, dtype="float64")
        drdt = np.full(len(d), np.nan, dtype="float64")
        ok_c = np.isfinite(t) & np.isfinite(c)
        ok_r = np.isfinite(t) & np.isfinite(r)
        if ok_c.sum() >= 3:
            dcdt[ok_c] = np.gradient(c[ok_c], t[ok_c])
        if ok_r.sum() >= 3:
            drdt[ok_r] = np.gradient(r[ok_r], t[ok_r])
        state.loc[d.index, "dCdt"] = dcdt
        state.loc[d.index, "dRdt"] = drdt
    cols = ["ob", "dataset", "t", "C", "dCdt", "R", "C_path", "R_path", "dRdt"]
    return state[cols].dropna(subset=["ob", "t"]).reset_index(drop=True)


def load_activity() -> pd.DataFrame:
    activity = pd.read_csv(ACTIVITY_PATH)
    activity["ob"] = pd.to_numeric(activity["ob"], errors="coerce").astype("Int64")
    activity["t"] = pd.to_numeric(activity["t"], errors="coerce")
    activity["A_swarm_tangential_z"] = pd.to_numeric(activity["A_swarm_tangential_z"], errors="coerce")
    return activity[["ob", "dataset", "t", "A_swarm_tangential_z"]].dropna(subset=["ob", "t"])


def build_state_path_frame(*, min_path_length: float, min_velocity_norm: float) -> pd.DataFrame:
    state = load_state()
    activity = load_activity()
    rows: list[pd.DataFrame] = []
    for ob, ad in activity.groupby("ob", sort=True):
        ob_int = int(ob)
        sd = state[state["ob"] == ob_int].sort_values("t")
        if sd.empty:
            continue
        ad = ad.sort_values("t").copy()
        t_state = sd["t"].to_numpy(dtype="float64")
        t = ad["t"].to_numpy(dtype="float64")
        out = pd.DataFrame(
            {
                "ob": ob_int,
                "dataset": str(ad["dataset"].iloc[0]),
                "t": t,
                "A_swarm_tangential_z": ad["A_swarm_tangential_z"].to_numpy(dtype="float64"),
            }
        )
        for col in ["C", "dCdt", "R", "C_path", "R_path", "dRdt"]:
            out[col] = interp_sorted(t_state, sd[col].to_numpy(dtype="float64"), t)
        out["path_velocity_norm"] = np.sqrt(out["dCdt"].to_numpy(dtype="float64") ** 2 + out["dRdt"].to_numpy(dtype="float64") ** 2)
        out["theta_v"] = np.arctan2(out["dRdt"].to_numpy(dtype="float64"), out["dCdt"].to_numpy(dtype="float64"))
        out["theta_v_valid"] = (out["path_velocity_norm"].to_numpy(dtype="float64") >= min_velocity_norm) & np.isfinite(out["theta_v"])

        c_now = out["C_path"].to_numpy(dtype="float64")
        r_now = out["R_path"].to_numpy(dtype="float64")
        for h in WINDOWS:
            tag = win_tag(h)
            c_prev = interp_sorted(t_state, sd["C_path"].to_numpy(dtype="float64"), t - h)
            r_prev = interp_sorted(t_state, sd["R_path"].to_numpy(dtype="float64"), t - h)
            c_mid = interp_sorted(t_state, sd["C_path"].to_numpy(dtype="float64"), t - h / 2.0)
            r_mid = interp_sorted(t_state, sd["R_path"].to_numpy(dtype="float64"), t - h / 2.0)
            d_c = c_now - c_prev
            d_r = r_now - r_prev
            early_c = c_mid - c_prev
            early_r = r_mid - r_prev
            late_c = c_now - c_mid
            late_r = r_now - r_mid
            path_len = np.sqrt(d_c * d_c + d_r * d_r)
            early_len = np.sqrt(early_c * early_c + early_r * early_r)
            late_len = np.sqrt(late_c * late_c + late_r * late_r)
            theta = np.arctan2(d_r, d_c)
            turning = angle_between_vectors(early_c, early_r, late_c, late_r)
            finite_path = np.isfinite(d_c) & np.isfinite(d_r) & np.isfinite(path_len)
            theta_valid = finite_path & (path_len >= min_path_length)
            turning_valid = (
                theta_valid
                & np.isfinite(turning)
                & (early_len >= min_path_length / 2.0)
                & (late_len >= min_path_length / 2.0)
            )
            out[f"{tag}_dC"] = d_c
            out[f"{tag}_dR"] = d_r
            out[f"{tag}_path_length"] = path_len
            out[f"{tag}_theta_h"] = np.where(theta_valid, theta, np.nan)
            out[f"{tag}_path_feature_valid"] = finite_path
            out[f"{tag}_theta_valid"] = theta_valid
            out[f"{tag}_turning_proxy"] = np.where(turning_valid, turning, np.nan)
            out[f"{tag}_turning_valid"] = turning_valid
        rows.append(out)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def summarize_qc(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    qc_rows: list[dict[str, object]] = []
    coverage_rows: list[dict[str, object]] = []
    leakage_rows: list[dict[str, object]] = []
    for ob, d in frame.groupby("ob", sort=True):
        d = d.sort_values("t")
        current_ok = np.isfinite(d[["C", "dCdt", "R"]].to_numpy(dtype="float64")).all(axis=1)
        finite_activity = np.isfinite(d["A_swarm_tangential_z"].to_numpy(dtype="float64"))
        finite_drdt = np.isfinite(d["dRdt"].to_numpy(dtype="float64"))
        dt = np.diff(d["t"].to_numpy(dtype="float64"))
        primary_tag = win_tag(PRIMARY_H)
        coverage_rows.append(
            {
                "ob": int(ob),
                "dataset": str(d["dataset"].iloc[0]),
                "n_frames": len(d),
                "median_dt_sec": float(np.nanmedian(dt)) if dt.size else math.nan,
                "finite_current_state_fraction": float(current_ok.mean()) if len(d) else math.nan,
                "finite_activity_fraction": float(finite_activity.mean()) if len(d) else math.nan,
                "finite_dRdt_fraction": float(finite_drdt.mean()) if len(d) else math.nan,
                "primary_path_feature_coverage": float(d[f"{primary_tag}_path_feature_valid"].mean()) if len(d) else math.nan,
                "primary_theta_valid_fraction": float(d[f"{primary_tag}_theta_valid"].mean()) if len(d) else math.nan,
                "primary_turning_valid_fraction": float(d[f"{primary_tag}_turning_valid"].mean()) if len(d) else math.nan,
            }
        )
        for h in WINDOWS:
            tag = win_tag(h)
            theta = d[f"{tag}_theta_h"].to_numpy(dtype="float64")
            path_len = d[f"{tag}_path_length"].to_numpy(dtype="float64")
            turning = d[f"{tag}_turning_proxy"].to_numpy(dtype="float64")
            path_valid = d[f"{tag}_path_feature_valid"].to_numpy(dtype=bool)
            theta_valid = d[f"{tag}_theta_valid"].to_numpy(dtype=bool)
            turning_valid = d[f"{tag}_turning_valid"].to_numpy(dtype=bool)
            qc_rows.append(
                {
                    "ob": int(ob),
                    "dataset": str(d["dataset"].iloc[0]),
                    "history_window_sec": h,
                    "n_frames": len(d),
                    "finite_current_state_fraction": float(current_ok.mean()) if len(d) else math.nan,
                    "finite_activity_fraction": float(finite_activity.mean()) if len(d) else math.nan,
                    "finite_dRdt_fraction": float(finite_drdt.mean()) if len(d) else math.nan,
                    "path_feature_coverage": float(path_valid.mean()) if len(d) else math.nan,
                    "theta_valid_fraction": float(theta_valid.mean()) if len(d) else math.nan,
                    "turning_valid_fraction": float(turning_valid.mean()) if len(d) else math.nan,
                    "median_path_length": float(np.nanmedian(path_len)) if np.isfinite(path_len).any() else math.nan,
                    "q05_path_length": float(np.nanquantile(path_len[np.isfinite(path_len)], 0.05)) if np.isfinite(path_len).any() else math.nan,
                    "q95_path_length": float(np.nanquantile(path_len[np.isfinite(path_len)], 0.95)) if np.isfinite(path_len).any() else math.nan,
                    "theta_resultant_length": circular_resultant_length(theta),
                    "median_abs_turning_proxy_rad": float(np.nanmedian(np.abs(turning))) if np.isfinite(turning).any() else math.nan,
                    "q95_abs_turning_proxy_rad": float(np.nanquantile(np.abs(turning[np.isfinite(turning)]), 0.95)) if np.isfinite(turning).any() else math.nan,
                    "median_path_velocity_norm": float(np.nanmedian(d["path_velocity_norm"])) if np.isfinite(d["path_velocity_norm"]).any() else math.nan,
                    "q99_abs_dRdt": float(np.nanquantile(np.abs(d["dRdt"].dropna()), 0.99)) if d["dRdt"].notna().any() else math.nan,
                }
            )
            feature_map = {
                "dC_h": d[f"{tag}_dC"].to_numpy(dtype="float64"),
                "dR_h": d[f"{tag}_dR"].to_numpy(dtype="float64"),
                "path_length": d[f"{tag}_path_length"].to_numpy(dtype="float64"),
                "cos_theta_h": np.cos(theta),
                "sin_theta_h": np.sin(theta),
                "turning_proxy": turning,
            }
            for feat, vals in feature_map.items():
                for state_col in ["C", "dCdt", "R"]:
                    pear, n1 = corr_pair(vals, d[state_col].to_numpy(dtype="float64"), "pearson")
                    spear, n2 = corr_pair(vals, d[state_col].to_numpy(dtype="float64"), "spearman")
                    leakage_rows.append(
                        {
                            "ob": int(ob),
                            "dataset": str(d["dataset"].iloc[0]),
                            "history_window_sec": h,
                            "history_feature": feat,
                            "current_state": state_col,
                            "spearman_corr": spear,
                            "pearson_corr": pear,
                            "n": max(n1, n2),
                        }
                    )
    qc = pd.DataFrame(qc_rows, columns=QC_COLUMNS)
    coverage = pd.DataFrame(coverage_rows, columns=COVERAGE_COLUMNS)
    leakage = pd.DataFrame(leakage_rows, columns=LEAK_COLUMNS)
    sens_rows: list[dict[str, object]] = []
    for h, d in qc.groupby("history_window_sec", sort=True):
        sens_rows.append(
            {
                "history_window_sec": float(h),
                "n_observations": int(len(d)),
                "obs_path_coverage_ge_0p90": int((d["path_feature_coverage"] >= 0.90).sum()),
                "median_path_feature_coverage": float(np.nanmedian(d["path_feature_coverage"])),
                "min_path_feature_coverage": float(np.nanmin(d["path_feature_coverage"])),
                "median_theta_valid_fraction": float(np.nanmedian(d["theta_valid_fraction"])),
                "min_theta_valid_fraction": float(np.nanmin(d["theta_valid_fraction"])),
                "median_path_length": float(np.nanmedian(d["median_path_length"])),
                "median_abs_turning_proxy_rad": float(np.nanmedian(d["median_abs_turning_proxy_rad"])),
            }
        )
    sensitivity = pd.DataFrame(sens_rows, columns=SENS_COLUMNS)
    return qc, sensitivity, leakage, coverage


def decide(
    qc: pd.DataFrame,
    sensitivity: pd.DataFrame,
    leakage: pd.DataFrame,
    coverage: pd.DataFrame,
    *,
    min_obs_coverage_count: int,
    min_coverage_fraction: float,
    max_abs_drdt_q99: float,
) -> dict[str, object]:
    primary = qc[np.isclose(qc["history_window_sec"], PRIMARY_H)].copy()
    sens_primary = sensitivity[np.isclose(sensitivity["history_window_sec"], PRIMARY_H)].copy()
    obs_cov_ok = int((primary["path_feature_coverage"] >= min_coverage_fraction).sum()) if not primary.empty else 0
    theta_cov_ok = int((primary["theta_valid_fraction"] >= min_coverage_fraction).sum()) if not primary.empty else 0
    min_current = float(np.nanmin(coverage["finite_current_state_fraction"])) if not coverage.empty else math.nan
    min_drdt = float(np.nanmin(coverage["finite_dRdt_fraction"])) if not coverage.empty else math.nan
    max_drdt = float(np.nanmax(primary["q99_abs_dRdt"])) if not primary.empty else math.nan
    max_abs_leak = float(np.nanmax(np.abs(leakage["spearman_corr"]))) if not leakage.empty else math.nan
    median_len = float(np.nanmedian(primary["median_path_length"])) if not primary.empty else math.nan
    median_turn = float(np.nanmedian(primary["median_abs_turning_proxy_rad"])) if not primary.empty else math.nan

    coverage_ok = obs_cov_ok >= min_obs_coverage_count and theta_cov_ok >= min_obs_coverage_count
    derivative_ok = math.isfinite(max_drdt) and max_drdt <= max_abs_drdt_q99 and min_drdt >= 0.95
    current_ok = math.isfinite(min_current) and min_current >= 0.95

    if coverage_ok and derivative_ok and current_ok:
        gate = "pass_state_path_features_feasible_with_leakage_audit"
        interp = (
            "State-path features are technically identifiable at the primary 0.50 sec "
            "history window. History-current correlations are recorded as leakage "
            "audits and must be controlled by 4121 current-state matching."
        )
        nxt = ["4121_same_current_state_different_history_matched_test"]
    else:
        gate = "technical_stop_state_path_not_identifiable"
        interp = (
            "The primary state-path representation did not meet the frozen coverage "
            "or derivative-stability gate; do not run 4121 without revising the "
            "representation as a new node."
        )
        nxt = ["4125_technical_synthesis"]

    return {
        "node": "4120_state_path_feasibility_coordinate_freeze",
        "date": DATE,
        "node_type": "technical_gate",
        "upstream_node": "4105_state_matched_negative_synthesis",
        "data_scope": "all_19_observations",
        "frozen_target": "T1_local_tangential_nonaffine_residual",
        "activity_column": "A_swarm_tangential_z",
        "current_state": ["C_density_rms_z3045", "dCdt_gradient_density_rms_smooth3045", "R_r_rms_z3045"],
        "path_coordinates": ["density_rms_smooth3045", "r_rms_smooth3045"],
        "primary_history_window_sec": PRIMARY_H,
        "sensitivity_history_windows_sec": WINDOWS,
        "primary_history_features": ["DeltaC_h", "DeltaR_h", "path_length", "theta_h", "theta_v", "turning_proxy"],
        "stability_thresholds": {
            "min_path_feature_coverage": min_coverage_fraction,
            "min_obs_coverage_count": min_obs_coverage_count,
            "max_abs_dRdt_q99": max_abs_drdt_q99,
        },
        "primary_metrics": {
            "obs_path_coverage_ge_0p90": obs_cov_ok,
            "obs_theta_valid_ge_0p90": theta_cov_ok,
            "min_current_state_finite_fraction": min_current,
            "min_dRdt_finite_fraction": min_drdt,
            "max_q99_abs_dRdt": max_drdt,
            "median_primary_path_length": median_len,
            "median_abs_turning_proxy_rad": median_turn,
            "max_abs_spearman_history_current_corr": max_abs_leak,
        },
        "gate_result": gate,
        "interpretation": interp,
        "does_not_prove": [
            "history dependence of T1",
            "same-state different-history effect",
            "hysteresis-like path dependence",
            "OOS history gain",
            "causal memory mechanism",
        ],
        "next": nxt,
        "artifacts": [
            "Output/4120/state_path_frame.csv",
            "Output/4120/path_feature_qc.csv",
            "Output/4120/history_window_sensitivity.csv",
            "Output/4120/state_leakage_audit.csv",
            "Output/4120/observation_coverage.csv",
            "Output/4120/figures/",
            "Output/4120/decision.json",
            "Output/4120/4120_summary.md",
        ],
    }


def make_figures(frame: pd.DataFrame, qc: pd.DataFrame, sensitivity: pd.DataFrame, leakage: pd.DataFrame) -> None:
    primary = qc[np.isclose(qc["history_window_sec"], PRIMARY_H)].sort_values("ob")
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    x = np.arange(len(primary))
    axes[0].bar(x, primary["path_feature_coverage"], color="#4c78a8")
    axes[0].axhline(0.90, color="#333333", linestyle="--", linewidth=1.0)
    axes[0].set_ylim(0, 1.05)
    axes[0].set_title("path feature coverage")
    axes[1].bar(x, primary["theta_valid_fraction"], color="#59a14f")
    axes[1].axhline(0.90, color="#333333", linestyle="--", linewidth=1.0)
    axes[1].set_ylim(0, 1.05)
    axes[1].set_title("theta_h valid fraction")
    axes[2].bar(x, primary["median_path_length"], color="#f28e2b")
    axes[2].set_title("median path length")
    for ax in axes:
        ax.set_xticks(x)
        ax.set_xticklabels([f"Ob{int(v)}" for v in primary["ob"]], rotation=45, ha="right")
    fig.suptitle("4120 primary h=0.50 sec path QC")
    fig.tight_layout()
    fig.savefig(OUT / "figures" / "4120_primary_qc_by_observation.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    for h in WINDOWS:
        tag = win_tag(h)
        vals = frame[f"{tag}_path_length"].dropna().to_numpy(dtype="float64")
        if vals.size:
            sample = vals if vals.size <= 10000 else np.random.default_rng(4120).choice(vals, size=10000, replace=False)
            ax.hist(sample, bins=60, alpha=0.35, label=f"h={h:.2f}s", density=True)
    ax.set_xlabel("path length in smoothed C-R state")
    ax.set_ylabel("density")
    ax.set_title("4120 path length distributions")
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(OUT / "figures" / "4120_path_length_distribution.png", dpi=180)
    plt.close(fig)

    tag = win_tag(PRIMARY_H)
    theta = frame[f"{tag}_theta_h"].dropna().to_numpy(dtype="float64")
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection="polar")
    if theta.size:
        ax.hist(theta, bins=36, color="#4c78a8", alpha=0.75)
    ax.set_title("4120 theta_h distribution, h=0.50 sec")
    fig.tight_layout()
    fig.savefig(OUT / "figures" / "4120_theta_h_polar_hist.png", dpi=180)
    plt.close(fig)

    leak = leakage[np.isclose(leakage["history_window_sec"], PRIMARY_H)].copy()
    if not leak.empty:
        agg = (
            leak.groupby(["history_feature", "current_state"], as_index=False)["spearman_corr"]
            .apply(lambda s: float(np.nanmedian(np.abs(s))))
            .rename(columns={"spearman_corr": "median_abs_spearman"})
        )
        pivot = agg.pivot(index="history_feature", columns="current_state", values="median_abs_spearman")
        fig, ax = plt.subplots(figsize=(7, 4.8))
        im = ax.imshow(pivot.to_numpy(dtype="float64"), vmin=0, vmax=1, cmap="magma")
        ax.set_xticks(np.arange(len(pivot.columns)))
        ax.set_xticklabels(pivot.columns)
        ax.set_yticks(np.arange(len(pivot.index)))
        ax.set_yticklabels(pivot.index)
        ax.set_title("4120 median |Spearman| leakage audit, h=0.50 sec")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        fig.tight_layout()
        fig.savefig(OUT / "figures" / "4120_state_leakage_heatmap.png", dpi=180)
        plt.close(fig)


def write_config(args: argparse.Namespace) -> None:
    text = dedent(
        f"""\
        node: 4120_state_path_feasibility_coordinate_freeze
        date: {DATE}
        upstream_node: 4105_state_matched_negative_synthesis
        state_source: Output/3045/processed/frame_residual_signals.csv
        activity_source: Output/4100A/swarm_activity_frame.csv
        current_state:
          C: density_rms_z3045
          dCdt: gradient(density_rms_smooth3045,t)
          R: r_rms_z3045
        path_coordinates:
          C_path: density_rms_smooth3045
          R_path: r_rms_smooth3045
        history_windows_sec: {WINDOWS}
        primary_history_window_sec: {PRIMARY_H}
        min_path_length_for_angle: {args.min_path_length}
        min_velocity_norm_for_theta_v: {args.min_velocity_norm}
        min_path_feature_coverage_gate: {args.min_coverage_fraction}
        min_obs_coverage_count_gate: {args.min_obs_coverage_count}
        max_abs_dRdt_q99_gate: {args.max_abs_drdt_q99}
        """
    )
    (OUT / "config.yaml").write_text(text, encoding="utf-8")
    hypotheses = dedent(
        """\
        node: 4120_state_path_feasibility_coordinate_freeze
        purpose: >
          Freeze a technically stable C-R state-path representation before
          testing any history dependence.
        not_tested_here:
          - T1 history dependence
          - same-state different-history effect
          - OOS history gain
        pass_gate: >
          Most observations must have >=90% primary path feature and theta
          coverage, current-state and dRdt coverage must be high, and dRdt must
          not show catastrophic derivative magnitude.
        next_if_pass: 4121_same_current_state_different_history_matched_test
        next_if_fail: 4125_technical_synthesis
        """
    )
    (OUT / "frozen_hypotheses.yaml").write_text(hypotheses, encoding="utf-8")


def write_summary(
    *,
    qc: pd.DataFrame,
    sensitivity: pd.DataFrame,
    leakage: pd.DataFrame,
    coverage: pd.DataFrame,
    decision: dict[str, object],
) -> None:
    primary = qc[np.isclose(qc["history_window_sec"], PRIMARY_H)].copy()
    leak_primary = leakage[np.isclose(leakage["history_window_sec"], PRIMARY_H)].copy()
    top_leaks = (
        leak_primary.assign(abs_spearman=lambda d: np.abs(d["spearman_corr"]))
        .sort_values("abs_spearman", ascending=False)
        .head(12)
    )
    sections = [
        "# Node 4120 Summary",
        "## Question\n\n"
        "Can the project compute a stable recent C-R state-path representation "
        "before testing whether T1 contains history information beyond the "
        "instantaneous `C,dCdt,R` state?",
        "## Why This Node Exists After 4105\n\n"
        "4105 stopped the event-timestamp burst/propagation route because true "
        "transition timing did not add robust near-pre activity after matching "
        "`C,dCdt,R`. 4120 reframes the next question around recent state path, "
        "but first checks whether path variables are numerically identifiable.",
        "## Frozen Inputs\n\n"
        "```text\n"
        "current_state = C density_rms_z3045, dCdt gradient(density_rms_smooth3045,t), R r_rms_z3045\n"
        "path_coordinates = density_rms_smooth3045, r_rms_smooth3045\n"
        "activity = A_swarm_tangential_z from 4100A\n"
        "primary_history_window = 0.50 sec\n"
        "sensitivity_windows = 0.25, 0.50, 0.75 sec\n"
        "```\n",
        "## Primary Metrics\n\n" + md_table([decision["primary_metrics"]], list(decision["primary_metrics"].keys())),
        "## Observation Coverage\n\n" + md_table(coverage.to_dict("records"), COVERAGE_COLUMNS),
        "## Primary h=0.50 sec QC\n\n" + md_table(primary.to_dict("records"), QC_COLUMNS),
        "## History-window Sensitivity\n\n" + md_table(sensitivity.to_dict("records"), SENS_COLUMNS),
        "## State Leakage Audit\n\n"
        "Largest absolute Spearman correlations are shown for auditing only. "
        "4121 must still match current `C,dCdt,R` before interpreting history effects.\n\n"
        + md_table(top_leaks.to_dict("records"), LEAK_COLUMNS),
        "## Gate Evaluation\n\n"
        "```text\n"
        f"gate_result = {decision['gate_result']}\n"
        "```\n\n"
        f"{decision['interpretation']}",
        "## What This Supports\n\n"
        "- A primary C-R recent path representation can be frozen for 4121 if "
        "the gate passed.\n"
        "- The path direction `theta_h` and turning proxy are measured on "
        "smoothed state coordinates, reducing raw derivative noise.",
        "## What This Does Not Prove\n\n"
        + md_table([{"does_not_prove": x} for x in decision["does_not_prove"]], ["does_not_prove"]),
        "## Decision\n\n" f"`{decision['gate_result']}`",
        "## Next Node\n\n" + md_table([{"next": x} for x in decision["next"]], ["next"]),
        "## Artifacts\n\n"
        "- `Output/4120/state_path_frame.csv`\n"
        "- `Output/4120/path_feature_qc.csv`\n"
        "- `Output/4120/history_window_sensitivity.csv`\n"
        "- `Output/4120/state_leakage_audit.csv`\n"
        "- `Output/4120/observation_coverage.csv`\n"
        "- `Output/4120/figures/4120_primary_qc_by_observation.png`\n"
        "- `Output/4120/figures/4120_path_length_distribution.png`\n"
        "- `Output/4120/figures/4120_theta_h_polar_hist.png`\n"
        "- `Output/4120/figures/4120_state_leakage_heatmap.png`\n"
        "- `Output/4120/decision.json`",
    ]
    (OUT / "4120_summary.md").write_text("\n\n".join(sections) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-path-length", type=float, default=0.05)
    parser.add_argument("--min-velocity-norm", type=float, default=0.05)
    parser.add_argument("--min-coverage-fraction", type=float, default=0.90)
    parser.add_argument("--min-obs-coverage-count", type=int, default=15)
    parser.add_argument("--max-abs-drdt-q99", type=float, default=1000.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_dirs()
    write_config(args)
    frame = build_state_path_frame(
        min_path_length=args.min_path_length,
        min_velocity_norm=args.min_velocity_norm,
    )
    qc, sensitivity, leakage, coverage = summarize_qc(frame)
    decision = decide(
        qc,
        sensitivity,
        leakage,
        coverage,
        min_obs_coverage_count=args.min_obs_coverage_count,
        min_coverage_fraction=args.min_coverage_fraction,
        max_abs_drdt_q99=args.max_abs_drdt_q99,
    )
    make_figures(frame, qc, sensitivity, leakage)

    frame.to_csv(OUT / "state_path_frame.csv", index=False)
    qc.to_csv(OUT / "path_feature_qc.csv", index=False)
    qc.to_csv(OUT / "tables" / "path_feature_qc.csv", index=False)
    sensitivity.to_csv(OUT / "history_window_sensitivity.csv", index=False)
    sensitivity.to_csv(OUT / "tables" / "history_window_sensitivity.csv", index=False)
    leakage.to_csv(OUT / "state_leakage_audit.csv", index=False)
    leakage.to_csv(OUT / "tables" / "state_leakage_audit.csv", index=False)
    coverage.to_csv(OUT / "observation_coverage.csv", index=False)
    coverage.to_csv(OUT / "tables" / "observation_coverage.csv", index=False)
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2), encoding="utf-8")
    write_summary(qc=qc, sensitivity=sensitivity, leakage=leakage, coverage=coverage, decision=decision)
    print(json.dumps(decision, indent=2), flush=True)
    print(f"Wrote 4120 outputs to {OUT.relative_to(ROOT)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
