"""4131 robust positive phenomenon atlas.

This node converts the frozen 4130 registry plus completed 408x/412x tables
into a positive-phenomenon atlas. It does not introduce a new target, rerun old
thresholds, or claim a new mechanism.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from textwrap import dedent

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4131"
DATE = "2026-08-27"
NODE = "4131_robust_positive_phenomenon_atlas"


def ensure_dirs() -> None:
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    (OUT / "figures").mkdir(parents=True, exist_ok=True)


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def as_bool(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().isin(["true", "1", "yes"])


def as_nullable_bool(series: pd.Series) -> pd.Series:
    out = as_bool(series).astype("boolean")
    out[series.isna()] = pd.NA
    return out


def true_count(series: pd.Series) -> int:
    return int(series.fillna(False).astype(bool).sum())


def fmt_float(value: object, digits: int = 3) -> str:
    try:
        value_f = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(value_f):
        return "NA"
    return f"{value_f:.{digits}g}"


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


def write_csv_pair(df: pd.DataFrame, name: str) -> None:
    df.to_csv(OUT / name, index=False)
    df.to_csv(OUT / "tables" / name, index=False)


def load_inputs() -> dict[str, object]:
    return {
        "d4130": read_json(ROOT / "Output" / "4130" / "decision.json"),
        "d4081c": read_json(ROOT / "Output" / "4081c" / "decision.json"),
        "d4082": read_json(ROOT / "Output" / "4082" / "decision.json"),
        "d4084": read_json(ROOT / "Output" / "4084" / "decision.json"),
        "d4085": read_json(ROOT / "Output" / "4085" / "decision.json"),
        "d4121": read_json(ROOT / "Output" / "4121" / "decision.json"),
        "d4125": read_json(ROOT / "Output" / "4125" / "decision.json"),
        "definitions": pd.read_csv(ROOT / "Output" / "4130" / "definition_dictionary.csv"),
        "claims": pd.read_csv(ROOT / "Output" / "4130" / "claim_strength_registry.csv"),
        "evidence": pd.read_csv(ROOT / "Output" / "4130" / "evidence_registry.csv"),
        "route_a": pd.read_csv(ROOT / "Output" / "4081c" / "ob_route_a_classification.csv"),
        "robust": pd.read_csv(ROOT / "Output" / "4082" / "ob_scale_timing_robustness.csv"),
        "spatial_ob": pd.read_csv(ROOT / "Output" / "4084" / "ob_spatial_taxonomy.csv"),
        "spatial_var": pd.read_csv(ROOT / "Output" / "4084" / "variable_spatial_taxonomy.csv"),
        "phase_ob": pd.read_csv(ROOT / "Output" / "4085" / "ob_phase_classification.csv"),
        "phase_var": pd.read_csv(ROOT / "Output" / "4085" / "variable_phase_summary.csv"),
        "history_ob": pd.read_csv(ROOT / "Output" / "4121" / "observation_level_effects.csv"),
    }


def build_observation_coverage(data: dict[str, object]) -> pd.DataFrame:
    route_a = data["route_a"].copy()
    robust = data["robust"].copy()
    spatial = data["spatial_ob"].copy()
    phase = data["phase_ob"].copy()
    history = data["history_ob"].copy()

    for df in [route_a, robust, spatial, phase, history]:
        df["ob"] = df["ob"].astype(int)

    coverage = pd.DataFrame({"ob": np.arange(1, 20)})
    coverage = coverage.merge(
        route_a[
            [
                "ob",
                "n_events",
                "t1_gate_any",
                "ob_route_a_class",
                "t1_median_local_to_b3_ratio",
                "t1_median_local_event_minus_non_event_z",
            ]
        ],
        on="ob",
        how="left",
    )
    coverage["t1_survival_any_k"] = as_nullable_bool(coverage["t1_gate_any"])
    coverage["t1_survival_both_k"] = coverage["ob_route_a_class"].eq(
        "t1_local_nonaffine_survives_both_k"
    ).astype("boolean")

    coverage = coverage.merge(
        robust[["ob", "robustness_class", "scale_pass_fraction", "timing_pass_fraction", "median_scale_gap"]],
        on="ob",
        how="left",
    )
    coverage["scale_lag_robust"] = coverage["robustness_class"].eq("robust_scale_and_timing").astype("boolean")
    coverage.loc[coverage["robustness_class"].isna(), "scale_lag_robust"] = pd.NA

    coverage = coverage.merge(
        spatial[
            [
                "ob",
                "diffuse_baseline_gate",
                "n_spatial_contrast_gates",
                "best_spatial_variable",
                "best_spatial_gap_z",
                "ob_spatial_class",
            ]
        ],
        on="ob",
        how="left",
    )
    coverage["diffuse_all_tangential_gate"] = as_nullable_bool(coverage["diffuse_baseline_gate"])
    coverage["localized_or_gradient_candidate"] = coverage["ob_spatial_class"].eq(
        "localized_or_gradient_signal_candidate"
    ).astype("boolean")
    coverage.loc[coverage["ob_spatial_class"].isna(), "localized_or_gradient_candidate"] = pd.NA

    coverage = coverage.merge(
        phase[["ob", "peak_phase", "phase_gate_any", "event_centered_gate", "phase_class"]],
        on="ob",
        how="left",
    )
    coverage["edge_core_phase_gate"] = as_nullable_bool(coverage["phase_gate_any"])
    coverage["edge_core_event_centered_gate"] = as_nullable_bool(coverage["event_centered_gate"])

    coverage = coverage.merge(
        history[
            [
                "ob",
                "median_signed_axis_delta_A_z",
                "real_minus_null_median_abs_effect",
                "real_beats_null_median_abs",
                "real_beats_null_q95_abs",
            ]
        ],
        on="ob",
        how="left",
    )
    coverage["history_real_beats_shuffle_median_abs"] = as_nullable_bool(coverage["real_beats_null_median_abs"])
    coverage["history_real_beats_shuffle_q95_abs"] = as_nullable_bool(coverage["real_beats_null_q95_abs"])
    coverage["history_effect_direction"] = np.where(
        coverage["median_signed_axis_delta_A_z"].astype(float) >= 0,
        "axis_positive_higher",
        "axis_negative_higher",
    )

    ordered_cols = [
        "ob",
        "n_events",
        "t1_survival_any_k",
        "t1_survival_both_k",
        "scale_lag_robust",
        "diffuse_all_tangential_gate",
        "localized_or_gradient_candidate",
        "edge_core_phase_gate",
        "edge_core_event_centered_gate",
        "history_real_beats_shuffle_median_abs",
        "history_real_beats_shuffle_q95_abs",
        "history_effect_direction",
        "ob_route_a_class",
        "robustness_class",
        "ob_spatial_class",
        "phase_class",
        "t1_median_local_to_b3_ratio",
        "t1_median_local_event_minus_non_event_z",
        "scale_pass_fraction",
        "timing_pass_fraction",
        "median_scale_gap",
        "best_spatial_variable",
        "best_spatial_gap_z",
        "peak_phase",
        "median_signed_axis_delta_A_z",
        "real_minus_null_median_abs_effect",
    ]
    return coverage[ordered_cols]


def build_atlas(data: dict[str, object], coverage: pd.DataFrame) -> pd.DataFrame:
    d4081c = data["d4081c"]
    d4082 = data["d4082"]
    d4084 = data["d4084"]
    d4085 = data["d4085"]
    d4121 = data["d4121"]
    d4125 = data["d4125"]
    route_a = data["route_a"]
    spatial_var = data["spatial_var"]
    phase_var = data["phase_var"]
    history_ob = data["history_ob"]

    t1_any = true_count(coverage["t1_survival_any_k"])
    t1_both = true_count(coverage["t1_survival_both_k"])
    robust_count = true_count(coverage["scale_lag_robust"])
    all_tang = spatial_var[spatial_var["variable"].eq("all_tangential")].iloc[0]
    edge_core = spatial_var[spatial_var["variable"].eq("shell_edge_minus_core")].iloc[0]
    all_near_pre = phase_var[
        phase_var["variable"].eq("all_tangential") & phase_var["phase"].eq("near_pre")
    ].iloc[0]
    history_metrics = d4121["primary_metrics"]
    history_ob["abs_history_effect"] = history_ob["median_signed_axis_delta_A_z"].abs()

    rows = [
        {
            "phenomenon_name": "global_affine_residual_survival",
            "definition": "Event-linked velocity residual remains after removing whole-swarm affine geometry.",
            "primary_metric": "4/4 raw direction survivors retained; median affine/raw abs ratio 0.9554",
            "observation_coverage": "4/4 source directions in 4001 summary",
            "effect_size_distribution": "summary-only provenance",
            "robustness": "supported with boundary; source is summary-only",
            "boundary_cases": "not yet a local T1 mechanism",
            "allowed_wording": "whole-swarm affine motion is insufficient as a full explanation",
            "disallowed_wording": "global affine test proves local mechanism",
            "best_figure": "4131_positive_support_bars.png",
            "claim_strength": "SUPPORTED_WITH_BOUNDARY",
            "atlas_role": "upstream_motivation",
        },
        {
            "phenomenon_name": "local_nonaffine_t1_survival",
            "definition": "T1 survives local affine deformation removal in most observations.",
            "primary_metric": f"{t1_any}/19 any-k survival; {t1_both}/19 both-k survival",
            "observation_coverage": f"{t1_any}/19",
            "effect_size_distribution": (
                "median local/global residual ratio "
                f"{fmt_float(route_a['t1_median_local_to_b3_ratio'].median())}; "
                "median event-control gap z "
                f"{fmt_float(route_a['t1_median_local_event_minus_non_event_z'].median())}"
            ),
            "robustness": "common across observations, not universal",
            "boundary_cases": "Ob1/Ob3/Ob6/Ob8 fail; Ob4 one-k survivor",
            "allowed_wording": "T1 local non-affine residual is common after local affine removal",
            "disallowed_wording": "T1 is universal or causal",
            "best_figure": "4131_observation_coverage_matrix.png",
            "claim_strength": "SUPPORTED_WITH_BOUNDARY",
            "atlas_role": "primary_positive",
        },
        {
            "phenomenon_name": "scale_lag_robust_survivor_class",
            "definition": "The 4081c survivor class remains positive under nearby k and lag choices.",
            "primary_metric": f"{robust_count}/{int(d4082['n_observations'])} robust scale and timing",
            "observation_coverage": f"{robust_count}/{int(d4082['n_observations'])} survivor observations",
            "effect_size_distribution": (
                "median scale pass fraction "
                f"{fmt_float(d4082['median_scale_pass_fraction'])}; median timing pass fraction "
                f"{fmt_float(d4082['median_timing_pass_fraction'])}"
            ),
            "robustness": "high inside survivor class",
            "boundary_cases": "Ob4 fragile_or_boundary",
            "allowed_wording": "robust among survivor observations",
            "disallowed_wording": "robust across all 19 observations",
            "best_figure": "4131_observation_coverage_matrix.png",
            "claim_strength": "SUPPORTED_WITH_BOUNDARY",
            "atlas_role": "primary_positive",
        },
        {
            "phenomenon_name": "diffuse_tangential_activity",
            "definition": "Diffuse all-tangential local non-affine activity is the strongest repeated spatial/activity form.",
            "primary_metric": (
                f"all_tangential gates {int(all_tang['gate_count'])}/{int(all_tang['n_ob_tested'])}; "
                f"near_pre gates {int(all_near_pre['phase_gate_count'])}/{int(all_near_pre['n_ob_tested'])}"
            ),
            "observation_coverage": f"{int(all_tang['gate_count'])}/{int(all_tang['n_ob_tested'])}",
            "effect_size_distribution": (
                "spatial median event-control abs direction z "
                f"{fmt_float(all_tang['median_event_minus_non_event_abs_direction_z'])}; "
                "near-pre median abs event-null z "
                f"{fmt_float(all_near_pre['median_abs_event_minus_abs_null_z'])}"
            ),
            "robustness": "repeated spatially; phase timing is moderate",
            "boundary_cases": "near-pre timing is 8/14, not all-observation",
            "allowed_wording": "primary repeated activity form is diffuse tangential",
            "disallowed_wording": "there is a sharp universal precursor",
            "best_figure": "4131_spatial_phase_positive_summary.png",
            "claim_strength": "SUPPORTED_WITH_BOUNDARY",
            "atlas_role": "primary_positive",
        },
        {
            "phenomenon_name": "edge_core_contrast_secondary",
            "definition": "Edge-minus-core contrast appears in a majority but is weaker and phase-unstable.",
            "primary_metric": (
                f"shell_edge_minus_core gates {int(edge_core['gate_count'])}/{int(edge_core['n_ob_tested'])}; "
                f"target near-transition gate total {int(d4085['target_near_transition_gate_total'])}"
            ),
            "observation_coverage": f"{int(edge_core['gate_count'])}/{int(edge_core['n_ob_tested'])}",
            "effect_size_distribution": (
                "median spatial contrast z "
                f"{fmt_float(edge_core['median_event_minus_non_event_abs_direction_z'])}; "
                "signed consistency "
                f"{fmt_float(edge_core['signed_direction_sign_consistency'])}"
            ),
            "robustness": "moderate as spatial contrast, weak as phase-localized profile",
            "boundary_cases": "target has no stable majority phase",
            "allowed_wording": "secondary bounded spatial contrast",
            "disallowed_wording": "edge/core contrast is the main transition trigger",
            "best_figure": "4131_spatial_phase_positive_summary.png",
            "claim_strength": "SUPPORTED_WITH_BOUNDARY",
            "atlas_role": "secondary_positive",
        },
        {
            "phenomenon_name": "observation_specific_history_separation",
            "definition": "Recent C-R path direction can separate T1 within some observations under same-current-state matching.",
            "primary_metric": (
                f"{int(history_metrics['n_observations_sufficient_pairs'])}/19 sufficient pairs; "
                f"{int(d4125['primary_metrics']['real_beats_null_median_observations'])}/19 beat shuffle median; "
                "direction consistency "
                f"{fmt_float(history_metrics['direction_consistency_fraction'])}"
            ),
            "observation_coverage": "19/19 sufficient pairs; 14/19 beat median shuffle null",
            "effect_size_distribution": (
                "median abs signed effect z "
                f"{fmt_float(history_metrics['median_abs_observation_signed_axis_delta_A_z'])}; "
                "median real-minus-null abs effect "
                f"{fmt_float(history_metrics['median_real_minus_shuffle_null_abs_effect'])}"
            ),
            "robustness": "observation-specific; sign/order fails as a universal rule",
            "boundary_cases": "positive and negative signed groups are split 9 vs 10",
            "allowed_wording": "secondary bounded positive heterogeneity signal",
            "disallowed_wording": "universal memory, hysteresis, or causal history mechanism",
            "best_figure": "4131_history_secondary_positive.png",
            "claim_strength": "BOUNDARY",
            "atlas_role": "secondary_bounded_positive",
        },
    ]
    return pd.DataFrame(rows)


def build_positive_claims(data: dict[str, object], atlas: pd.DataFrame) -> pd.DataFrame:
    claims = data["claims"].copy()
    keep = {
        "C1_LOCAL_NONAFFINE_SURVIVAL",
        "C2_SCALE_LAG_ROBUST_SURVIVORS",
        "C3_DIFFUSE_TANGENTIAL_DOMINANCE",
        "C7_OBSERVATION_SPECIFIC_HISTORY_BOUNDARY",
    }
    out = claims[claims["claim_id"].isin(keep)].copy()
    out["4131_role"] = out["claim_id"].map(
        {
            "C1_LOCAL_NONAFFINE_SURVIVAL": "primary_positive",
            "C2_SCALE_LAG_ROBUST_SURVIVORS": "primary_positive",
            "C3_DIFFUSE_TANGENTIAL_DOMINANCE": "primary_positive",
            "C7_OBSERVATION_SPECIFIC_HISTORY_BOUNDARY": "secondary_bounded_positive",
        }
    )
    out["atlas_rows"] = out["claim_id"].map(
        {
            "C1_LOCAL_NONAFFINE_SURVIVAL": "local_nonaffine_t1_survival",
            "C2_SCALE_LAG_ROBUST_SURVIVORS": "scale_lag_robust_survivor_class",
            "C3_DIFFUSE_TANGENTIAL_DOMINANCE": "diffuse_tangential_activity;edge_core_contrast_secondary",
            "C7_OBSERVATION_SPECIFIC_HISTORY_BOUNDARY": "observation_specific_history_separation",
        }
    )
    return out


def build_figure_plan(atlas: pd.DataFrame) -> pd.DataFrame:
    rows = [
        {
            "figure_id": "Fig4131A",
            "file": "Output/4131/figures/4131_observation_coverage_matrix.png",
            "role": "main",
            "content": "observation-by-observation coverage for T1 survival, robustness, spatial, phase, and history-positive flags",
            "source_tables": "Output/4131/observation_positive_coverage_matrix.csv",
            "allowed_caption_claim": "positive evidence is common but bounded at the observation level",
        },
        {
            "figure_id": "Fig4131B",
            "file": "Output/4131/figures/4131_positive_support_bars.png",
            "role": "main",
            "content": "support fractions for each positive phenomenon row",
            "source_tables": "Output/4131/positive_phenomenon_atlas.csv",
            "allowed_caption_claim": "strongest positive evidence is T1 survival and scale/lag robustness within survivor observations",
        },
        {
            "figure_id": "Fig4131C",
            "file": "Output/4131/figures/4131_spatial_phase_positive_summary.png",
            "role": "main",
            "content": "spatial variable gate fractions and phase gate fractions",
            "source_tables": "Output/4084/variable_spatial_taxonomy.csv;Output/4085/variable_phase_summary.csv",
            "allowed_caption_claim": "diffuse all-tangential activity is more stable than edge/core phase localization",
        },
        {
            "figure_id": "Fig4131D",
            "file": "Output/4131/figures/4131_history_secondary_positive.png",
            "role": "supplement",
            "content": "observation-level history real-minus-null effects and sign split",
            "source_tables": "Output/4121/observation_level_effects.csv",
            "allowed_caption_claim": "history separation is visible but observation-specific",
        },
    ]
    return pd.DataFrame(rows)


def parse_fraction(text: str) -> float:
    text = str(text).split(" ")[0]
    if "/" not in text:
        return np.nan
    num, den = text.split("/", 1)
    try:
        return float(num) / float(den)
    except ValueError:
        return np.nan


def make_figures(
    coverage: pd.DataFrame,
    atlas: pd.DataFrame,
    spatial_var: pd.DataFrame,
    phase_var: pd.DataFrame,
    history_ob: pd.DataFrame,
) -> list[str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    from matplotlib.colors import ListedColormap

    files: list[str] = []
    fig_dir = OUT / "figures"

    feature_cols = [
        "t1_survival_any_k",
        "t1_survival_both_k",
        "scale_lag_robust",
        "diffuse_all_tangential_gate",
        "localized_or_gradient_candidate",
        "edge_core_phase_gate",
        "history_real_beats_shuffle_median_abs",
    ]
    matrix = coverage[feature_cols].copy()
    display = matrix.astype(float)
    for col in feature_cols:
        display.loc[coverage[col].isna(), col] = np.nan
    display = display.to_numpy()
    encoded = np.where(np.isnan(display), 0, np.where(display > 0.5, 2, 1))
    cmap = ListedColormap(["#d8d8d8", "#f4f1ea", "#1d7a61"])
    fig, ax = plt.subplots(figsize=(10.5, 6.2))
    ax.imshow(encoded, aspect="auto", cmap=cmap, vmin=0, vmax=2)
    ax.set_yticks(np.arange(len(coverage)))
    ax.set_yticklabels([f"Ob{int(x)}" for x in coverage["ob"]], fontsize=8)
    ax.set_xticks(np.arange(len(feature_cols)))
    ax.set_xticklabels(
        [
            "T1 any k",
            "T1 both k",
            "scale/lag",
            "diffuse",
            "spatial",
            "edge phase",
            "history>shuffle",
        ],
        rotation=35,
        ha="right",
    )
    ax.set_title("4131 positive evidence coverage by observation")
    ax.set_xlabel("positive evidence flag")
    ax.set_ylabel("observation")
    ax.legend(
        handles=[
            Patch(facecolor="#1d7a61", label="pass"),
            Patch(facecolor="#f4f1ea", label="fail"),
            Patch(facecolor="#d8d8d8", label="not tested"),
        ],
        loc="upper left",
        bbox_to_anchor=(1.01, 1.0),
        frameon=False,
    )
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()
    path = fig_dir / "4131_observation_coverage_matrix.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    files.append(rel(path))

    support = atlas.copy()
    support["support_fraction"] = support["observation_coverage"].map(parse_fraction)
    fig, ax = plt.subplots(figsize=(9.4, 4.8))
    colors = [
        "#1d7a61" if role == "primary_positive" else "#7c6f58" if role == "secondary_positive" else "#b08b33"
        for role in support["atlas_role"]
    ]
    ax.barh(support["phenomenon_name"], support["support_fraction"], color=colors)
    ax.set_xlim(0, 1.05)
    ax.set_xlabel("support fraction in tested observation set")
    ax.set_title("4131 positive phenomenon support fractions")
    ax.grid(axis="x", color="#dddddd", linewidth=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    path = fig_dir / "4131_positive_support_bars.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    files.append(rel(path))

    spatial_focus = spatial_var[
        spatial_var["variable"].isin(
            [
                "all_tangential",
                "shell_edge_minus_core",
                "density_dense_tangential",
                "shell_core_tangential",
                "shell_edge_tangential",
            ]
        )
    ].copy()
    phase_focus = phase_var[
        phase_var["variable"].isin(["all_tangential", "shell_edge_minus_core"])
        & phase_var["phase"].isin(["early_pre", "near_pre", "near_post", "late_post"])
    ].copy()
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    axes[0].barh(
        spatial_focus["variable"],
        spatial_focus["gate_fraction"].astype(float),
        color="#1d7a61",
    )
    axes[0].set_xlim(0, 1.05)
    axes[0].set_title("spatial/activity gate fraction")
    axes[0].grid(axis="x", color="#dddddd", linewidth=0.8)
    pivot = phase_focus.pivot(index="variable", columns="phase", values="phase_gate_fraction").fillna(0.0)
    pivot = pivot[["early_pre", "near_pre", "near_post", "late_post"]]
    axes[1].imshow(pivot.to_numpy(dtype=float), aspect="auto", cmap="YlGn", vmin=0, vmax=1)
    axes[1].set_yticks(np.arange(len(pivot.index)))
    axes[1].set_yticklabels(pivot.index)
    axes[1].set_xticks(np.arange(len(pivot.columns)))
    axes[1].set_xticklabels(pivot.columns, rotation=35, ha="right")
    axes[1].set_title("phase gate fraction")
    for ax in axes:
        ax.set_axisbelow(True)
    fig.suptitle("4131 diffuse tangential versus edge/core positive structure", y=1.02)
    fig.tight_layout()
    path = fig_dir / "4131_spatial_phase_positive_summary.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    files.append(rel(path))

    hist = history_ob.copy()
    hist["ob"] = hist["ob"].astype(int)
    hist["real_minus_null_median_abs_effect"] = hist["real_minus_null_median_abs_effect"].astype(float)
    hist["median_signed_axis_delta_A_z"] = hist["median_signed_axis_delta_A_z"].astype(float)
    hist = hist.sort_values("ob")
    fig, ax = plt.subplots(figsize=(10, 4.5))
    colors = np.where(hist["median_signed_axis_delta_A_z"] >= 0, "#1d7a61", "#b6423c")
    ax.bar([f"Ob{x}" for x in hist["ob"]], hist["real_minus_null_median_abs_effect"], color=colors)
    ax.axhline(0, color="#333333", linewidth=0.8)
    ax.set_title("4131 secondary history-positive evidence by observation")
    ax.set_ylabel("real minus shuffled median abs effect")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", color="#dddddd", linewidth=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    path = fig_dir / "4131_history_secondary_positive.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    files.append(rel(path))
    return files


def main() -> None:
    ensure_dirs()
    data = load_inputs()

    coverage = build_observation_coverage(data)
    atlas = build_atlas(data, coverage)
    positive_claims = build_positive_claims(data, atlas)
    figure_plan = build_figure_plan(atlas)
    figure_files = make_figures(
        coverage,
        atlas,
        data["spatial_var"].copy(),
        data["phase_var"].copy(),
        data["history_ob"].copy(),
    )

    write_csv_pair(coverage, "observation_positive_coverage_matrix.csv")
    write_csv_pair(atlas, "positive_phenomenon_atlas.csv")
    write_csv_pair(positive_claims, "positive_claims_from_4130.csv")
    write_csv_pair(figure_plan, "positive_figure_plan.csv")

    required_primary = {
        "local_nonaffine_t1_survival",
        "scale_lag_robust_survivor_class",
        "diffuse_tangential_activity",
    }
    primary_present = required_primary.issubset(set(atlas["phenomenon_name"]))
    primary_positive = atlas[atlas["atlas_role"].eq("primary_positive")]
    no_unbounded_primary = primary_positive["claim_strength"].isin(["SUPPORTED", "SUPPORTED_WITH_BOUNDARY"]).all()
    t1_any_count = true_count(coverage["t1_survival_any_k"])
    robust_count = true_count(coverage["scale_lag_robust"])
    diffuse_count = true_count(coverage["diffuse_all_tangential_gate"])
    history_median_count = true_count(coverage["history_real_beats_shuffle_median_abs"])
    gate_pass = primary_present and t1_any_count >= 14 and robust_count >= 13 and diffuse_count >= 12

    decision = {
        "node": NODE,
        "date": DATE,
        "node_type": "positive_atlas",
        "upstream_node": "4130_definition_and_evidence_registry",
        "data_scope": "all_19_observations_with_survivor_class_subsets_where_defined",
        "frozen_target": "T1_local_tangential_nonaffine_residual",
        "registry_source": "Output/4130",
        "primary_positive_phenomena": sorted(required_primary),
        "secondary_bounded_positive": ["edge_core_contrast_secondary", "observation_specific_history_separation"],
        "primary_metrics": {
            "t1_survival_any_k_observations": t1_any_count,
            "t1_survival_both_k_observations": true_count(coverage["t1_survival_both_k"]),
            "total_observations": 19,
            "scale_lag_robust_observations": robust_count,
            "scale_lag_tested_survivor_observations": int(data["d4082"]["n_observations"]),
            "diffuse_all_tangential_gate_observations": diffuse_count,
            "diffuse_all_tangential_tested_observations": int(data["d4084"]["n_observations"]),
            "all_tangential_near_pre_gate_observations": int(
                data["phase_var"][
                    data["phase_var"]["variable"].eq("all_tangential")
                    & data["phase_var"]["phase"].eq("near_pre")
                ]["phase_gate_count"].iloc[0]
            ),
            "history_real_beats_shuffle_median_observations": history_median_count,
            "history_direction_consistency_fraction": data["d4121"]["primary_metrics"][
                "direction_consistency_fraction"
            ],
        },
        "quality_checks": {
            "primary_positive_rows_present": bool(primary_present),
            "no_unbounded_primary_claims": bool(no_unbounded_primary),
            "figures_written": bool(len(figure_files) == 4),
            "uses_frozen_4130_target": True,
            "metadata_dependent_claims_used": False,
        },
        "gate_result": "pass_4131_positive_atlas_ready_with_secondary_boundaries"
        if gate_pass
        else "boundary_4131_positive_atlas_insufficient_primary_support",
        "interpretation": (
            "The positive evidence can be presented as a bounded atlas: T1 survival is common, robust inside the "
            "survivor class, and most stable as diffuse tangential activity. Edge/core and history signals remain "
            "secondary and explicitly bounded."
        ),
        "does_not_prove": [
            "universal T1 mechanism",
            "causal trigger",
            "prediction rule",
            "stable edge/core phase trigger",
            "universal history dependence",
        ],
        "next": ["4132_negative_mechanism_boundary_atlas"],
        "artifacts": [
            "Output/4131/positive_phenomenon_atlas.csv",
            "Output/4131/observation_positive_coverage_matrix.csv",
            "Output/4131/positive_claims_from_4130.csv",
            "Output/4131/positive_figure_plan.csv",
            "Output/4131/decision.json",
            "Output/4131/4131_summary.md",
        ]
        + figure_files,
    }

    (OUT / "decision.json").write_text(json.dumps(decision, indent=2), encoding="utf-8")

    summary = dedent(
        f"""\
        # Node 4131 Robust Positive Phenomenon Atlas

        ## Question

        If only the robust positive evidence is retained, what does the T1
        phenomenon look like?

        ## Gate Result

        ```text
        gate_result = {decision["gate_result"]}
        ```

        ## Main Interpretation

        The positive result is a bounded atlas, not a mechanism claim. T1
        survival after local affine removal is common across observations,
        robustness is high inside the survivor class, and the clearest repeated
        spatial/activity form is diffuse tangential activity. Edge/core contrast
        and recent-history separation remain secondary bounded positives.

        ## Primary Metrics

        {md_table([decision["primary_metrics"]], list(decision["primary_metrics"].keys()))}

        ## Positive Phenomenon Atlas

        {md_table(atlas.to_dict("records"), ["phenomenon_name", "primary_metric", "observation_coverage", "robustness", "boundary_cases", "atlas_role"])}

        ## Positive Claims Imported From 4130

        {md_table(positive_claims.to_dict("records"), ["claim_id", "claim_strength", "4131_role", "support_nodes", "forbidden_stronger_claim"])}

        ## Figure Plan

        {md_table(figure_plan.to_dict("records"), ["figure_id", "role", "content", "allowed_caption_claim", "file"])}

        ## What This Does Not Prove

        {md_table([{"does_not_prove": x} for x in decision["does_not_prove"]], ["does_not_prove"])}

        ## Next Node

        `4132_negative_mechanism_boundary_atlas`

        ## Artifacts

        - `Output/4131/positive_phenomenon_atlas.csv`
        - `Output/4131/observation_positive_coverage_matrix.csv`
        - `Output/4131/positive_claims_from_4130.csv`
        - `Output/4131/positive_figure_plan.csv`
        - `Output/4131/figures/4131_observation_coverage_matrix.png`
        - `Output/4131/figures/4131_positive_support_bars.png`
        - `Output/4131/figures/4131_spatial_phase_positive_summary.png`
        - `Output/4131/figures/4131_history_secondary_positive.png`
        """
    )
    summary = summary.replace("\n        ", "\n").lstrip()
    (OUT / "4131_summary.md").write_text(summary, encoding="utf-8")

    print(json.dumps(decision, indent=2))
    print(f"Wrote 4131 outputs to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
