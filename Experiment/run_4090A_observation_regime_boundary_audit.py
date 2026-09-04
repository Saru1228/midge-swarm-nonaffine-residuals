"""4090A observation-regime / batch boundary audit after 4088.

This node uses frozen 408x observation-level outputs to ask whether T1 local
tangential non-affine effect strength is strongly tracked by basic observation
regime, raw-quality, event-structure, or metadata variables. It does not
recompute local-affine trajectory metrics and does not redefine the T1 score.
"""

from __future__ import annotations

import csv
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
OUT = ROOT / "Output" / "4090A"
DATE = "2026-08-26"
NODE = "4090A_observation_regime_boundary_audit"

SRC_4081C_CLASS = ROOT / "Output" / "4081c" / "tables" / "ob_route_a_classification.csv"
SRC_4082_ROBUST = ROOT / "Output" / "4082" / "tables" / "ob_scale_timing_robustness.csv"
SRC_4082B_FEATURES = ROOT / "Output" / "4082b" / "tables" / "failure_audit_features.csv"
SRC_4087_BOUNDARY = ROOT / "Output" / "4087" / "tables" / "ob_failure_boundary_sensitivity.csv"
SRC_4088_DECISION = ROOT / "Output" / "4088" / "decision.json"


RAW_COVARIATES = [
    "file_size_mb",
    "duration_sec",
    "n_frames",
    "median_dt_sec",
    "unique_ids",
    "median_individuals_per_frame",
    "q10_individuals_per_frame",
    "q90_individuals_per_frame",
    "median_track_length_frames",
    "median_track_span_sec",
    "track_continuity_fraction",
    "median_raw_speed",
    "q95_raw_speed",
    "median_swarm_radius",
    "q90_swarm_radius",
    "swarm_radius_cv",
]

EVENT_COVARIATES = [
    "n_events",
    "event_rate_per_sec",
    "median_prev_duration_sec",
    "median_next_duration_sec",
]

SEQUENCE_COVARIATES = [
    "ob_index_proxy",
    "early_ob_le_8",
]

TARGETS = [
    ("t1_effect_z", "t1_median_local_event_minus_non_event_z"),
    ("t1_local_to_b3_ratio", "t1_median_local_to_b3_ratio"),
    ("t1_k8_event_abs_z", "t1_k8_local_event_direction_abs_z"),
    ("t1_predefined_pass_fraction", "t1_predefined_pass_fraction"),
]

OBS_TABLE_COLUMNS = [
    "ob",
    "dataset",
    "metadata_available",
    "recording_order_confirmed",
    "ob_index_proxy",
    "early_ob_le_8",
    "t1_gate_any",
    "t1_gate_k_values",
    "t1_4088_class",
    "t1_median_local_event_minus_non_event_z",
    "t1_median_local_to_b3_ratio",
    "t1_predefined_pass_fraction",
    "scale_pass_fraction",
    "timing_pass_fraction",
    "failure_boundary_class",
    "median_individuals_per_frame",
    "median_raw_speed",
    "median_swarm_radius",
    "n_events",
    "event_rate_per_sec",
    "duration_sec",
    "unique_ids",
    "track_continuity_fraction",
]

EFFECT_TABLE_COLUMNS = [
    "ob",
    "dataset",
    "t1_4088_class",
    "t1_effect_z",
    "t1_local_to_b3_ratio",
    "t1_k8_event_abs_z",
    "t1_k10_event_abs_z",
    "t1_predefined_pass_fraction",
    "t2_gate_count",
]

ASSOCIATION_COLUMNS = [
    "target",
    "covariate",
    "covariate_family",
    "n",
    "spearman_rho",
    "permutation_p_two_sided",
    "theil_sen_slope",
    "theil_sen_iqr_delta",
    "loo_slope_min",
    "loo_slope_max",
    "loo_slope_sign_stability",
    "interpretation",
]

LOO_COLUMNS = [
    "target",
    "covariate",
    "left_out_ob",
    "spearman_rho_loo",
    "theil_sen_slope_loo",
]


def ensure_dirs() -> None:
    for path in (OUT, OUT / "tables", OUT / "figures"):
        path.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in columns})


def write_json(path: Path, data: object) -> None:
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
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    return obj


def md_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        vals: list[str] = []
        for col in columns:
            val = row.get(col, "")
            if isinstance(val, float):
                vals.append("NA" if not math.isfinite(val) else f"{val:.4g}")
            else:
                vals.append(str(val).replace("\n", " ").replace("|", "\\|"))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def bool_from_csv(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def to_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in columns:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def rank_array(x: np.ndarray) -> np.ndarray:
    return pd.Series(x).rank(method="average").to_numpy(dtype="float64")


def pearson_r(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype="float64")
    y = np.asarray(y, dtype="float64")
    ok = np.isfinite(x) & np.isfinite(y)
    x = x[ok]
    y = y[ok]
    if x.size < 3 or np.nanstd(x) <= 1e-12 or np.nanstd(y) <= 1e-12:
        return math.nan
    x = x - np.mean(x)
    y = y - np.mean(y)
    denom = math.sqrt(float(np.sum(x * x) * np.sum(y * y)))
    return float(np.sum(x * y) / denom) if denom > 0 else math.nan


def spearman_rho(x: np.ndarray, y: np.ndarray) -> float:
    ok = np.isfinite(x) & np.isfinite(y)
    if int(ok.sum()) < 3:
        return math.nan
    return pearson_r(rank_array(x[ok]), rank_array(y[ok]))


def stable_seed(text: str) -> int:
    value = 0
    for ch in text:
        value = (value * 131 + ord(ch)) % 1_000_000_007
    return int(value % 1_000_000)


def spearman_permutation_p(x: np.ndarray, y: np.ndarray, *, seed: int, n_perm: int = 4000) -> float:
    ok = np.isfinite(x) & np.isfinite(y)
    x = np.asarray(x[ok], dtype="float64")
    y = np.asarray(y[ok], dtype="float64")
    if x.size < 4:
        return math.nan
    observed = spearman_rho(x, y)
    if not math.isfinite(observed):
        return math.nan
    rng = np.random.default_rng(seed)
    rx = rank_array(x)
    ry = rank_array(y)
    extreme = 0
    for _ in range(n_perm):
        perm = rng.permutation(ry)
        val = pearson_r(rx, perm)
        if math.isfinite(val) and abs(val) >= abs(observed) - 1e-12:
            extreme += 1
    return float((extreme + 1) / (n_perm + 1))


def theil_sen_slope(x: np.ndarray, y: np.ndarray) -> float:
    ok = np.isfinite(x) & np.isfinite(y)
    x = np.asarray(x[ok], dtype="float64")
    y = np.asarray(y[ok], dtype="float64")
    slopes: list[float] = []
    for i in range(len(x)):
        dx = x[i + 1 :] - x[i]
        dy = y[i + 1 :] - y[i]
        valid = np.abs(dx) > 1e-12
        if np.any(valid):
            slopes.extend((dy[valid] / dx[valid]).tolist())
    if not slopes:
        return math.nan
    return float(np.median(np.asarray(slopes, dtype="float64")))


def covariate_family(name: str) -> str:
    if name in RAW_COVARIATES:
        return "raw_trajectory_quality"
    if name in EVENT_COVARIATES:
        return "event_structure"
    if name in SEQUENCE_COVARIATES:
        return "observation_sequence_proxy"
    return "other"


def load_observation_table() -> pd.DataFrame:
    if not SRC_4082B_FEATURES.exists():
        raise FileNotFoundError(f"Missing required 4082b feature table: {SRC_4082B_FEATURES}")
    features = pd.read_csv(SRC_4082B_FEATURES)
    features["ob"] = pd.to_numeric(features["ob"], errors="coerce").astype("int64")
    features["ob_index_proxy"] = features["ob"]
    features["metadata_available"] = False
    features["recording_order_confirmed"] = False

    cls = pd.read_csv(SRC_4081C_CLASS)
    cls["ob"] = pd.to_numeric(cls["ob"], errors="coerce").astype("int64")
    cls["t1_gate_any"] = cls["t1_gate_any"].map(bool_from_csv)
    cls = cls[["ob", "t1_gate_any", "t1_gate_k_values", "ob_route_a_class"]]
    table = features.merge(cls, on="ob", how="left", suffixes=("", "_cls"))
    if "t1_gate_k_values_cls" in table.columns:
        table["t1_gate_k_values"] = table["t1_gate_k_values_cls"].where(
            table["t1_gate_k_values_cls"].notna(), table.get("t1_gate_k_values")
        )
    if "ob_route_a_class_cls" in table.columns:
        table["ob_route_a_class"] = table["ob_route_a_class_cls"].where(
            table["ob_route_a_class_cls"].notna(), table.get("ob_route_a_class")
        )

    robust = pd.read_csv(SRC_4082_ROBUST) if SRC_4082_ROBUST.exists() else pd.DataFrame()
    if not robust.empty:
        robust["ob"] = pd.to_numeric(robust["ob"], errors="coerce").astype("int64")
        robust = to_numeric(
            robust,
            ["scale_pass_count", "scale_total", "timing_pass_count", "timing_total", "scale_pass_fraction", "timing_pass_fraction"],
        )
        table = table.merge(
            robust[
                [
                    "ob",
                    "scale_pass_count",
                    "scale_total",
                    "timing_pass_count",
                    "timing_total",
                    "scale_pass_fraction",
                    "timing_pass_fraction",
                    "robustness_class",
                ]
            ],
            on="ob",
            how="left",
            suffixes=("", "_4082"),
        )
        if "robustness_class_4082" in table.columns:
            table["robustness_class"] = table["robustness_class_4082"].where(
                table["robustness_class_4082"].notna(), table.get("robustness_class")
            )

    boundary = pd.read_csv(SRC_4087_BOUNDARY) if SRC_4087_BOUNDARY.exists() else pd.DataFrame()
    if not boundary.empty:
        boundary["ob"] = pd.to_numeric(boundary["ob"], errors="coerce").astype("int64")
        boundary = to_numeric(
            boundary,
            [
                "baseline_pass_count",
                "baseline_total",
                "scale_timing_pass_count",
                "scale_timing_total",
                "window_pass_count",
                "window_total",
                "state_definition_pass_count",
                "state_definition_total",
            ],
        )
        table = table.merge(boundary, on="ob", how="left", suffixes=("", "_4087"))
    else:
        table["failure_boundary_class"] = ""

    table = to_numeric(
        table,
        RAW_COVARIATES
        + EVENT_COVARIATES
        + [
            "early_ob_le_8",
            "t1_median_local_to_b3_ratio",
            "t1_median_local_event_minus_non_event_z",
            "t1_k8_local_event_direction_abs_z",
            "t1_k8_local_non_event_direction_abs_median_z",
            "t1_k10_local_event_direction_abs_z",
            "t1_k10_local_non_event_direction_abs_median_z",
            "t2_gate_count",
            "scale_pass_fraction",
            "timing_pass_fraction",
            "scale_pass_count",
            "scale_total",
            "timing_pass_count",
            "timing_total",
            "scale_timing_pass_count",
            "scale_timing_total",
            "window_pass_count",
            "window_total",
            "state_definition_pass_count",
            "state_definition_total",
        ],
    )

    pass_count = table[["scale_pass_count", "timing_pass_count"]].sum(axis=1, min_count=1)
    pass_total = table[["scale_total", "timing_total"]].sum(axis=1, min_count=1)
    failure_pass_count = table[["scale_timing_pass_count", "window_pass_count", "state_definition_pass_count"]].sum(
        axis=1, min_count=1
    )
    failure_pass_total = table[["scale_timing_total", "window_total", "state_definition_total"]].sum(axis=1, min_count=1)
    table["t1_predefined_pass_fraction"] = pass_count / pass_total
    failure_fraction = failure_pass_count / failure_pass_total
    table.loc[table["t1_predefined_pass_fraction"].isna(), "t1_predefined_pass_fraction"] = failure_fraction
    table["t1_predefined_pass_fraction"] = table["t1_predefined_pass_fraction"].fillna(0.0)

    def classify(row: pd.Series) -> str:
        b = str(row.get("failure_boundary_class", ""))
        r = str(row.get("robustness_class", ""))
        if b and b != "nan":
            return b
        if r == "robust_scale_and_timing":
            return "robust_survivor"
        if r == "fragile_or_boundary":
            return "fragile_survivor"
        if bool(row.get("t1_gate_any", False)):
            return "survivor_not_robustness_tested"
        return "baseline_failure_no_4087_class"

    table["t1_4088_class"] = table.apply(classify, axis=1)
    return table.sort_values("ob").reset_index(drop=True)


def association_rows(table: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    loo_rows: list[dict[str, object]] = []
    covariates = SEQUENCE_COVARIATES + RAW_COVARIATES + EVENT_COVARIATES
    for target_name, target_col in TARGETS:
        y = pd.to_numeric(table[target_col], errors="coerce").to_numpy(dtype="float64")
        for cov in covariates:
            x = pd.to_numeric(table[cov], errors="coerce").to_numpy(dtype="float64")
            ok = np.isfinite(x) & np.isfinite(y)
            n = int(ok.sum())
            rho = spearman_rho(x, y)
            seed = 4090_000 + stable_seed(f"{target_name}:{cov}")
            p = spearman_permutation_p(x, y, seed=seed)
            slope = theil_sen_slope(x, y)
            x_ok = x[ok]
            iqr = float(np.nanquantile(x_ok, 0.75) - np.nanquantile(x_ok, 0.25)) if n else math.nan
            iqr_delta = slope * iqr if math.isfinite(slope) and math.isfinite(iqr) else math.nan
            slopes = []
            for ob in table["ob"].tolist():
                mask = table["ob"].to_numpy(dtype="int64") != int(ob)
                rho_loo = spearman_rho(x[mask], y[mask])
                slope_loo = theil_sen_slope(x[mask], y[mask])
                if math.isfinite(slope_loo):
                    slopes.append(slope_loo)
                loo_rows.append(
                    {
                        "target": target_name,
                        "covariate": cov,
                        "left_out_ob": int(ob),
                        "spearman_rho_loo": rho_loo,
                        "theil_sen_slope_loo": slope_loo,
                    }
                )
            slope_min = float(np.nanmin(slopes)) if slopes else math.nan
            slope_max = float(np.nanmax(slopes)) if slopes else math.nan
            if slopes and math.isfinite(slope):
                sign = 1 if slope > 0 else -1 if slope < 0 else 0
                if sign == 0:
                    sign_stability = math.nan
                else:
                    sign_stability = float(np.mean([(s > 0 and sign > 0) or (s < 0 and sign < 0) for s in slopes]))
            else:
                sign_stability = math.nan
            fam = covariate_family(cov)
            if fam == "observation_sequence_proxy":
                interp = "sequence proxy; not confirmed metadata"
            elif abs(rho) >= 0.70 and p <= 0.05 and (not math.isfinite(sign_stability) or sign_stability >= 0.80):
                interp = "strong routing clue"
            elif abs(rho) >= 0.55 and p <= 0.12:
                interp = "moderate routing clue"
            else:
                interp = "no strong association"
            rows.append(
                {
                    "target": target_name,
                    "covariate": cov,
                    "covariate_family": fam,
                    "n": n,
                    "spearman_rho": rho,
                    "permutation_p_two_sided": p,
                    "theil_sen_slope": slope,
                    "theil_sen_iqr_delta": iqr_delta,
                    "loo_slope_min": slope_min,
                    "loo_slope_max": slope_max,
                    "loo_slope_sign_stability": sign_stability,
                    "interpretation": interp,
                }
            )
    assoc = pd.DataFrame(rows).sort_values(
        ["target", "permutation_p_two_sided", "spearman_rho"], ascending=[True, True, False], na_position="last"
    )
    loo = pd.DataFrame(loo_rows)
    return assoc.reset_index(drop=True), loo.reset_index(drop=True)


def make_figures(table: pd.DataFrame, assoc: pd.DataFrame) -> None:
    fig_dir = OUT / "figures"
    class_colors = {
        "robust_survivor": "#1f9d55",
        "fragile_survivor": "#d97904",
        "fragile_narrow_setting_rescue": "#9a6fb0",
        "stable_failure_under_predefined_sensitivity": "#b23a48",
        "baseline_failure_no_4087_class": "#777777",
        "survivor_not_robustness_tested": "#4c78a8",
    }
    colors = [class_colors.get(str(v), "#777777") for v in table["t1_4088_class"]]

    fig, axes = plt.subplots(4, 1, figsize=(11, 11), sharex=True, constrained_layout=True)
    plot_cols = [
        ("t1_median_local_event_minus_non_event_z", "T1 event-control gap"),
        ("t1_median_local_to_b3_ratio", "T1 local/B3 ratio"),
        ("median_individuals_per_frame", "median N/frame"),
        ("median_raw_speed", "median raw speed"),
    ]
    for ax, (col, label) in zip(axes, plot_cols):
        ax.bar(table["ob"], pd.to_numeric(table[col], errors="coerce"), color=colors)
        ax.set_ylabel(label)
        ax.grid(axis="y", color="#dddddd", linewidth=0.8)
        if col == "t1_median_local_event_minus_non_event_z":
            ax.axhline(0, color="#444444", linewidth=1)
    axes[0].set_title("4090A observation-regime table")
    axes[-1].set_xlabel("Observation")
    axes[-1].set_xticks(table["ob"])
    handles = [
        plt.Line2D([0], [0], marker="s", linestyle="", color=color, label=label)
        for label, color in class_colors.items()
        if label in set(table["t1_4088_class"].astype(str))
    ]
    axes[0].legend(handles=handles, frameon=False, fontsize=8, loc="upper left")
    fig.savefig(fig_dir / "4090A_observation_regime_overview.png", dpi=180)
    plt.close(fig)

    top_covs = [
        "ob_index_proxy",
        "median_raw_speed",
        "median_individuals_per_frame",
        "median_swarm_radius",
        "event_rate_per_sec",
        "n_events",
    ]
    fig, axes = plt.subplots(2, 3, figsize=(13, 7), constrained_layout=True)
    y = pd.to_numeric(table["t1_median_local_event_minus_non_event_z"], errors="coerce")
    for ax, cov in zip(axes.ravel(), top_covs):
        x = pd.to_numeric(table[cov], errors="coerce")
        ax.scatter(x, y, c=colors, s=70, edgecolor="#222222", linewidth=0.5)
        for row in table.itertuples(index=False):
            ax.text(getattr(row, cov), row.t1_median_local_event_minus_non_event_z, f" {int(row.ob)}", fontsize=7)
        ax.axhline(0, color="#666666", linewidth=0.8)
        ax.set_xlabel(cov)
        ax.set_ylabel("T1 gap")
        ax.grid(color="#dddddd", linewidth=0.7)
    fig.suptitle("4090A primary T1 effect vs candidate regime covariates")
    fig.savefig(fig_dir / "4090A_t1_effect_vs_covariates.png", dpi=180)
    plt.close(fig)

    primary = assoc[assoc["target"] == "t1_effect_z"].copy()
    primary["abs_rho"] = primary["spearman_rho"].abs()
    primary = primary.sort_values("abs_rho", ascending=False).head(18)
    fig, ax = plt.subplots(figsize=(9, 6.5), constrained_layout=True)
    y_pos = np.arange(len(primary))
    bar_colors = primary["covariate_family"].map(
        {
            "observation_sequence_proxy": "#6c5b7b",
            "raw_trajectory_quality": "#4c78a8",
            "event_structure": "#f58518",
        }
    ).fillna("#777777")
    ax.barh(y_pos, primary["spearman_rho"], color=bar_colors)
    ax.axvline(0, color="#444444", linewidth=1)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(primary["covariate"])
    ax.invert_yaxis()
    ax.set_xlabel("Spearman rho with T1 event-control gap")
    ax.set_title("4090A strongest observation-level associations")
    ax.grid(axis="x", color="#dddddd", linewidth=0.8)
    fig.savefig(fig_dir / "4090A_primary_association_ranking.png", dpi=180)
    plt.close(fig)


def decide(assoc: pd.DataFrame, table: pd.DataFrame) -> dict[str, object]:
    primary = assoc[assoc["target"] == "t1_effect_z"].copy()
    known = primary[primary["covariate_family"].isin(["raw_trajectory_quality", "event_structure"])]
    strong_known = known[
        (known["spearman_rho"].abs() >= 0.70)
        & (known["permutation_p_two_sided"] <= 0.05)
        & (known["loo_slope_sign_stability"].fillna(0.0) >= 0.80)
    ]
    dominant_known = known[
        (known["spearman_rho"].abs() >= 0.85)
        & (known["permutation_p_two_sided"] <= 0.01)
        & (known["loo_slope_sign_stability"].fillna(0.0) >= 0.90)
    ]
    sequence = primary[primary["covariate_family"] == "observation_sequence_proxy"]
    strong_sequence = sequence[
        (sequence["spearman_rho"].abs() >= 0.70)
        & (sequence["permutation_p_two_sided"] <= 0.05)
        & (sequence["loo_slope_sign_stability"].fillna(0.0) >= 0.75)
    ]

    metadata_available = bool(table["metadata_available"].any())
    if metadata_available and len(dominant_known) > 0:
        gate = "R2_acquisition_or_quality_artifact_boundary"
        interpretation = (
            "A known metadata/raw-quality covariate nearly dominates T1 effect strength. "
            "Pause biological interpretation until the regime correction branch is defined."
        )
        next_node = "measurement_regime_correction_branch_before_4090"
    elif len(strong_known) > 0:
        gate = "R1_known_raw_or_event_regime_clue"
        features = ", ".join(str(x) for x in strong_known["covariate"].tolist())
        interpretation = (
            f"T1 effect strength has strong association with predefined raw/event covariate(s): {features}. "
            "4090 should include these variables as mandatory stratification or controls."
        )
        next_node = "4090B_then_4090_with_mandatory_regime_stratification"
    elif len(strong_sequence) > 0:
        gate = "R1_unconfirmed_observation_sequence_proxy"
        features = ", ".join(str(x) for x in strong_sequence["covariate"].tolist())
        interpretation = (
            f"T1 effect strength is strongly associated with observation sequence proxy variable(s): {features}. "
            "Because metadata are unavailable, this is a routing boundary rather than proof of batch artifact. "
            "4090 should keep observation identity and survivor/failure stratification explicit."
        )
        next_node = "4090B_then_4090_with_observation_identity_and_boundary_strata"
    else:
        gate = "R0_no_strong_observation_regime_association"
        interpretation = (
            "No predefined raw/event/sequence covariate strongly tracks primary T1 effect strength. "
            "Proceed to 4090B and 4090 without adding a special regime correction branch."
        )
        next_node = "4090B_residual_vector_and_continuous_state_feasibility_check"

    return {
        "node": NODE,
        "date": DATE,
        "node_type": "artifact-control",
        "upstream_node": "4088_bounded_408x_synthesis_with_failure_boundary",
        "upstream_target": "T1_local_tangential_nonaffine_residual",
        "data_scope": "all_19_observations",
        "metadata_available": metadata_available,
        "recording_order_confirmed": False,
        "gate_result": gate,
        "strong_known_covariates": strong_known["covariate"].tolist(),
        "dominant_known_covariates": dominant_known["covariate"].tolist(),
        "strong_sequence_proxy_covariates": strong_sequence["covariate"].tolist(),
        "interpretation": interpretation,
        "does_not_prove": [
            "batch artifact, because recording metadata are unavailable",
            "biological mechanism",
            "causal explanation of Ob6/Ob8 stable failures",
            "first-vs-second moment structure",
        ],
        "next": [next_node],
        "artifacts": [
            "Output/4090A/observation_regime_table.csv",
            "Output/4090A/t1_continuous_effects.csv",
            "Output/4090A/covariate_association_table.csv",
            "Output/4090A/leave_one_out_sensitivity.csv",
            "Output/4090A/figures/4090A_observation_regime_overview.png",
            "Output/4090A/figures/4090A_t1_effect_vs_covariates.png",
            "Output/4090A/figures/4090A_primary_association_ranking.png",
            "Output/4090A/4090A_summary.md",
        ],
    }


def write_config() -> None:
    text = dedent(
        f"""\
        node: {NODE}
        date: {DATE}
        node_type: artifact-control
        input_nodes:
          - 4081c_full_observation_adjudication
          - 4082_scale_robustness_on_surviving_observation_class
          - 4082b_early_failure_condition_or_artifact_audit
          - 4087_failure_boundary_sensitivity
          - 4088_bounded_408x_synthesis_with_failure_boundary
        primary_target: t1_median_local_event_minus_non_event_z
        data_scope: all_19_observations
        grouped_inference_unit: observation
        metadata_policy: metadata_unavailable_do_not_guess
        gate:
          R0: no strong observation-level regime association
          R1: strong known or proxy regime clue; condition/stratify in 4090
          R2: T1 nearly explained by known acquisition/batch artifact; pause biological interpretation
        """
    )
    (OUT / "config.yaml").write_text(text, encoding="utf-8")


def write_summary(table: pd.DataFrame, assoc: pd.DataFrame, decision: dict[str, object]) -> None:
    primary = assoc[assoc["target"] == "t1_effect_z"].copy()
    primary["abs_rho"] = primary["spearman_rho"].abs()
    top = primary.sort_values("abs_rho", ascending=False).head(12)
    known = primary[primary["covariate_family"].isin(["raw_trajectory_quality", "event_structure"])].copy()
    known["abs_rho"] = known["spearman_rho"].abs()
    top_known = known.sort_values("abs_rho", ascending=False).head(10)
    display_table = table[OBS_TABLE_COLUMNS].copy()
    for col in display_table.columns:
        if pd.api.types.is_numeric_dtype(display_table[col]):
            display_table[col] = display_table[col].round(4)
    effect_rows = []
    for row in table.itertuples(index=False):
        effect_rows.append(
            {
                "ob": int(row.ob),
                "class": row.t1_4088_class,
                "T1_gap": round(float(row.t1_median_local_event_minus_non_event_z), 4),
                "local_B3": round(float(row.t1_median_local_to_b3_ratio), 4),
                "pass_fraction": round(float(row.t1_predefined_pass_fraction), 4),
            }
        )

    text = f"""# Node 4090A Summary

## Question

Does the frozen 4088 T1 effect strength mainly track observation-level regime,
batch/recording order, raw trajectory quality, event structure, or metadata?

## Why this node exists after 408x

4088 froze a bounded positive result:

```text
T1 = local tangential non-affine residual
```

with boundary cases Ob1/Ob3/Ob6/Ob8 and fragile Ob4. Before 4090 tries to
classify first-vs-second moment structure, 4090A checks whether the all-19 T1
heterogeneity is mostly an observation-regime issue.

## Inputs

- `Output/4081c/tables/ob_route_a_classification.csv`
- `Output/4082/tables/ob_scale_timing_robustness.csv`
- `Output/4082b/tables/failure_audit_features.csv`
- `Output/4087/tables/ob_failure_boundary_sensitivity.csv`
- `Output/4088/decision.json`

## Metadata

```text
metadata_available = {decision["metadata_available"]}
recording_order_confirmed = {decision["recording_order_confirmed"]}
```

Observation number is therefore treated only as an `ob_index_proxy`, not as
confirmed acquisition order or batch metadata.

## Data Scope

All 19 observations are included. Survivor-only modeling is not used.

## Primary Target

```text
t1_effect_z = t1_median_local_event_minus_non_event_z
```

Secondary effect views are `t1_local_to_b3_ratio`, `t1_k8_event_abs_z`, and
`t1_predefined_pass_fraction`.

## Main Observation Table

{md_table(display_table.to_dict("records"), OBS_TABLE_COLUMNS)}

## T1 Effect Snapshot

{md_table(effect_rows, ["ob", "class", "T1_gap", "local_B3", "pass_fraction"])}

## Strongest Primary Associations

{md_table(top[ASSOCIATION_COLUMNS].round(4).to_dict("records"), ASSOCIATION_COLUMNS)}

## Strongest Raw/Event Associations

{md_table(top_known[ASSOCIATION_COLUMNS].round(4).to_dict("records"), ASSOCIATION_COLUMNS)}

## Gate Evaluation

```text
gate_result = {decision["gate_result"]}
```

{decision["interpretation"]}

## What This Supports

- 4090 should not ignore observation identity or the 4088 failure/boundary class.
- Metadata are unavailable, so an observation-sequence association cannot be
  promoted to a confirmed batch artifact.
- Known raw/event covariates should be treated as routing clues only when their
  association is strong and leave-one-out stable.

## What This Rules Out

4090A does not find enough evidence to delete Ob1/Ob3/Ob6/Ob8 as bad data.
They remain part of the all-19 primary scope.

## What This Does NOT Prove

{md_table([{"does_not_prove": x} for x in decision["does_not_prove"]], ["does_not_prove"])}

## Decision

`{decision["gate_result"]}`

## Next Node

`{decision["next"][0]}`

## Artifacts

- `Output/4090A/observation_regime_table.csv`
- `Output/4090A/t1_continuous_effects.csv`
- `Output/4090A/covariate_association_table.csv`
- `Output/4090A/leave_one_out_sensitivity.csv`
- `Output/4090A/figures/4090A_observation_regime_overview.png`
- `Output/4090A/figures/4090A_t1_effect_vs_covariates.png`
- `Output/4090A/figures/4090A_primary_association_ranking.png`
"""
    (OUT / "4090A_summary.md").write_text(text, encoding="utf-8")


def main() -> int:
    ensure_dirs()
    write_config()
    table = load_observation_table()
    assoc, loo = association_rows(table)
    make_figures(table, assoc)
    decision = decide(assoc, table)

    effect_rows = []
    for row in table.itertuples(index=False):
        effect_rows.append(
            {
                "ob": int(row.ob),
                "dataset": row.dataset,
                "t1_4088_class": row.t1_4088_class,
                "t1_effect_z": row.t1_median_local_event_minus_non_event_z,
                "t1_local_to_b3_ratio": row.t1_median_local_to_b3_ratio,
                "t1_k8_event_abs_z": row.t1_k8_local_event_direction_abs_z,
                "t1_k10_event_abs_z": row.t1_k10_local_event_direction_abs_z,
                "t1_predefined_pass_fraction": row.t1_predefined_pass_fraction,
                "t2_gate_count": row.t2_gate_count,
            }
        )

    obs_rows = table.to_dict("records")
    write_csv(OUT / "observation_regime_table.csv", obs_rows, OBS_TABLE_COLUMNS)
    write_csv(OUT / "tables" / "observation_regime_table.csv", obs_rows, OBS_TABLE_COLUMNS)
    write_csv(OUT / "t1_continuous_effects.csv", effect_rows, EFFECT_TABLE_COLUMNS)
    write_csv(OUT / "tables" / "t1_continuous_effects.csv", effect_rows, EFFECT_TABLE_COLUMNS)
    write_csv(OUT / "covariate_association_table.csv", assoc.to_dict("records"), ASSOCIATION_COLUMNS)
    write_csv(OUT / "tables" / "covariate_association_table.csv", assoc.to_dict("records"), ASSOCIATION_COLUMNS)
    write_csv(OUT / "leave_one_out_sensitivity.csv", loo.to_dict("records"), LOO_COLUMNS)
    write_csv(OUT / "tables" / "leave_one_out_sensitivity.csv", loo.to_dict("records"), LOO_COLUMNS)
    write_json(OUT / "observation_regime_table.json", obs_rows)
    write_json(OUT / "covariate_association_table.json", assoc.to_dict("records"))
    write_json(OUT / "decision.json", decision)
    write_summary(table, assoc, decision)

    print(json.dumps(to_jsonable(decision), ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
