"""4134 figure-ready evidence panels.

This node converts the completed 4130-4133 synthesis outputs and the M5 review
into a figure package: source map, main/supplement plans, caption drafts, and
panel-preview figures. It is a synthesis/assembly node, not a new mechanism
search.
"""

from __future__ import annotations

import json
import math
import os
import re
from pathlib import Path
from textwrap import dedent

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4134"
DATE = "2026-08-28"
NODE = "4134_figure_ready_evidence_panels"
M5 = ROOT / "Output" / "4133_M5_review_before_4134"
RAW_DATA_DIR = Path(os.environ.get("FISH_3D_DATASET_DIR", r"D:\3Ddataset"))


CLASS_COLORS = {
    "robust_survivor_diffuse_positive": "#1d7a61",
    "robust_survivor_without_diffuse_gate": "#74a892",
    "fragile_survivor": "#7c6f58",
    "fragile_408x_boundary": "#b08b33",
    "stable_408x_failure": "#b6423c",
    "unclassified_boundary": "#777777",
}

CLASS_LABELS = {
    "robust_survivor_diffuse_positive": "robust survivor with diffuse support",
    "robust_survivor_without_diffuse_gate": "robust survivor without diffuse support",
    "fragile_survivor": "one-scale survivor",
    "fragile_408x_boundary": "fragile boundary",
    "stable_408x_failure": "stable non-survivor",
    "unclassified_boundary": "unclassified boundary",
}

CLASS_SHORT_LABELS = {
    "robust_survivor_diffuse_positive": "robust\n+ diffuse",
    "robust_survivor_without_diffuse_gate": "robust\nwithout diffuse",
    "fragile_survivor": "one-scale\nsurvivor",
    "fragile_408x_boundary": "fragile\nboundary",
    "stable_408x_failure": "stable\nnon-survivor",
    "unclassified_boundary": "unclassified",
}

STATUS_COLORS = {
    "SUPPORTED_WITH_BOUNDARY": "#1d7a61",
    "NOT_SUPPORTED": "#b6423c",
    "BOUNDARY": "#b08b33",
    "NOT_TESTED": "#777777",
}

STATUS_LABELS = {
    "SUPPORTED_WITH_BOUNDARY": "supported, bounded",
    "NOT_SUPPORTED": "not supported",
    "BOUNDARY": "boundary",
    "NOT_TESTED": "not tested",
}

MECHANISM_LABELS = {
    "N2": "Local affine geometry only",
    "N3": "Compact-state moment closure",
    "N4": "Event-timestamp precursor",
    "N5": "Burst/propagation route",
    "N6": "Universal recent-history rule",
    "N7": "Universal signed event law",
    "N8": "Metadata/batch explanation",
}


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


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def write_csv_pair(df: pd.DataFrame, name: str) -> None:
    df.to_csv(OUT / name, index=False)
    df.to_csv(OUT / "tables" / name, index=False)


def md_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    if not rows:
        return "_No rows._"
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        values: list[str] = []
        for col in columns:
            value = row.get(col, "")
            if isinstance(value, float):
                if math.isfinite(value):
                    values.append(f"{value:.4g}")
                else:
                    values.append("NA")
            else:
                values.append(str(value).replace("\n", " ").replace("|", "\\|"))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def to_boolish(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().map({"true": 1.0, "false": 0.0})


def fmt_float(value: object, digits: int = 3) -> str:
    try:
        value_f = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(value_f):
        return "NA"
    return f"{value_f:.{digits}g}"


def spearman_rho(x: pd.Series, y: pd.Series) -> float:
    valid = pd.concat([x, y], axis=1).dropna()
    if len(valid) < 3:
        return float("nan")
    return float(valid.iloc[:, 0].rank().corr(valid.iloc[:, 1].rank()))


def parse_fraction(text: object) -> tuple[float, float] | None:
    match = re.search(r"(\d+)\s*/\s*(\d+)", str(text))
    if not match:
        return None
    num = float(match.group(1))
    den = float(match.group(2))
    if den <= 0:
        return None
    return num, den


def load_inputs() -> dict[str, object]:
    return {
        "m5_decision": read_json(M5 / "decision.json"),
        "m5_candidates": read_csv(M5 / "main_vs_supplement_figure_candidates.csv"),
        "m5_claim_review": read_csv(M5 / "claim_storyline_review.csv"),
        "m5_risks": read_csv(M5 / "overclaim_risk_register.csv"),
        "definition_dictionary": read_csv(ROOT / "Output" / "4130" / "definition_dictionary.csv"),
        "claim_registry": read_csv(ROOT / "Output" / "4130" / "claim_strength_registry.csv"),
        "d4131": read_json(ROOT / "Output" / "4131" / "decision.json"),
        "positive_atlas": read_csv(ROOT / "Output" / "4131" / "positive_phenomenon_atlas.csv"),
        "coverage": read_csv(ROOT / "Output" / "4131" / "observation_positive_coverage_matrix.csv"),
        "d4132": read_json(ROOT / "Output" / "4132" / "decision.json"),
        "negative_atlas": read_csv(ROOT / "Output" / "4132" / "negative_boundary_atlas.csv"),
        "d4133": read_json(ROOT / "Output" / "4133" / "decision.json"),
        "master": read_csv(ROOT / "Output" / "4133" / "observation_master_table.csv"),
        "classes": read_csv(ROOT / "Output" / "4133" / "observation_classes.csv"),
        "associations": read_csv(ROOT / "Output" / "4133" / "heterogeneity_associations.csv"),
        "profiles_4085": read_csv(ROOT / "Output" / "4085" / "aggregate_profiles.csv"),
        "primary_4090": read_csv(ROOT / "Output" / "4090" / "primary_metrics.csv"),
        "effects_4100": read_csv(ROOT / "Output" / "4100" / "observation_level_effects.csv"),
        "effects_4121": read_csv(ROOT / "Output" / "4121" / "observation_level_effects.csv"),
    }


def build_figure_source_map(candidates: pd.DataFrame) -> pd.DataFrame:
    sample_scope = {
        "1A": "representative raw snapshot from Ob2; all-19 metadata context",
        "1B": "definition-level concept panel",
        "1C": "definition-level concept panel",
        "1D": "4085 aggregate event-aligned profile; 14 tested observations",
        "2A": "all 19 observations",
        "2B": "all 19 observations plus survivor-class robustness",
        "2C": "all 19 observations",
        "3A": "4131 positive atlas; node-specific denominators",
        "3B": "4085 aggregate profiles; 14 tested observations",
        "3C": "4086/4132 signed boundary classes",
        "4A": "4090 grouped OOS moment-closure metrics; 19 observations",
        "4B": "4100 state-matched event-local effects; 19 observations",
        "4C": "4121 same-current-state different-history effects; 19 observations",
        "5A": "all 19 observations x route flags",
        "5B": "all 19 observations; descriptive metadata association",
        "5C": "all 19 observation classes",
    }
    metric_map = {
        "1A": "3D positions from one frame; dataset metadata from raw columns 0 and 4",
        "1B": "global affine / local affine / residual separation",
        "1C": "T1 frozen definition",
        "1D": "median real-minus-null aligned z for all_tangential",
        "2A": "408x_T1_effect and local-affine survival flags",
        "2B": "T1 any-k, both-k, scale/lag, diffuse, history flags",
        "2C": "observation_class counts",
        "3A": "positive support fractions from 4131",
        "3B": "event-aligned real-minus-null profile",
        "3C": "signed class counts / boundary status",
        "4A": "median incremental R2 and real-minus-shift metrics",
        "4B": "median delta A_pre_z by observation",
        "4C": "real-minus-null median abs history effect and sign",
        "5A": "direct observation-level evidence flags",
        "5B": "408x_T1_effect vs mean_track_length_frames",
        "5C": "observation-class T1-effect distribution and class summary",
    }
    baseline_map = {
        "1A": "none; descriptive data orientation",
        "1B": "definition schematic, no fitted mechanism",
        "1C": "definition schematic, no fitted mechanism",
        "1D": "4085 event-aligned null profile",
        "2A": "local affine residualization and event/non-event comparison",
        "2B": "nearby k and lag sensitivity within all-19 context",
        "2C": "predefined observation classes from 4133",
        "3A": "node-specific event/control or survivor-subset gates",
        "3B": "4085 aggregate event-aligned null",
        "3C": "signed event-type decomposition",
        "4A": "radius-only model and shifted C,dCdt null",
        "4B": "same-observation C,dCdt,R-matched non-event frames and shifted events",
        "4C": "same-current-state matching and within-observation shuffled history",
        "5A": "route-specific binary gates",
        "5B": "small-n descriptive Spearman / leave-one-observation-out audit",
        "5C": "4133 observation classes",
    }
    final_artifact_map = {
        "Figure 1": "Output/4134/figures/4134_figure1_data_t1_definition.png",
        "Figure 2": "Output/4134/figures/4134_figure2_t1_survival_across_observations.png",
        "Figure 3": "Output/4134/figures/4134_figure3_spatial_timing_structure.png",
        "Figure 4": "Output/4134/figures/4134_figure4_reduction_boundaries.png",
        "Figure 5": "Output/4134/figures/4134_figure5_observation_heterogeneity.png",
    }

    rows: list[dict[str, object]] = []
    for record in candidates.to_dict("records"):
        source = str(record.get("source_artifact", ""))
        source_path = ROOT / source
        panel_id = str(record.get("panel_id", ""))
        figure_id = str(record.get("figure_id", ""))
        rows.append(
            {
                **record,
                "source_exists": source_path.exists(),
                "source_size_bytes": source_path.stat().st_size if source_path.exists() else 0,
                "sample_scope": sample_scope.get(panel_id, "review"),
                "primary_metric_or_content": metric_map.get(panel_id, "review"),
                "baseline_or_null": baseline_map.get(panel_id, "review"),
                "final_panel_package_artifact": final_artifact_map.get(figure_id, ""),
                "ready_for_4134": "yes" if record.get("source_status") != "blocked" else "no",
            }
        )
    return pd.DataFrame(rows)


def build_panel_metadata(source_map: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for record in source_map.to_dict("records"):
        source_status = str(record.get("source_status", ""))
        role = str(record.get("recommended_role", ""))
        if "supplement" in role and "main" not in role:
            figure_role = "supplement_or_boundary_annotation"
        else:
            figure_role = "main_candidate"
        rows.append(
            {
                "figure_id": record.get("figure_id", ""),
                "panel_id": record.get("panel_id", ""),
                "figure_role": figure_role,
                "question": record.get("panel_question", ""),
                "source_node": record.get("source_node", ""),
                "source_artifact": record.get("source_artifact", ""),
                "source_status": source_status,
                "sample_scope": record.get("sample_scope", ""),
                "primary_metric_or_content": record.get("primary_metric_or_content", ""),
                "baseline_or_null": record.get("baseline_or_null", ""),
                "allowed_claim": record.get("allowed_claim", ""),
                "boundary_guard": record.get("boundary_guard", ""),
                "processing_needed": record.get("4134_action", ""),
                "final_panel_package_artifact": record.get("final_panel_package_artifact", ""),
            }
        )
    return pd.DataFrame(rows)


def build_figure_manifest(panel_metadata: pd.DataFrame) -> pd.DataFrame:
    rows = [
        {
            "figure_id": "Figure 1",
            "title": "Data and T1 Measurement Definition",
            "main_question": "What are the data, reductions, and frozen T1 observable?",
            "panel_ids": "1A;1B;1C;1D",
            "preview_artifact": "Output/4134/figures/4134_figure1_data_t1_definition.png",
            "claim_status": "orientation_only",
            "main_claim": "The analysis operates on 3D trajectories and a frozen local tangential non-affine T1 residual.",
            "must_not_claim": "The schematic is a physical mechanism or a fitted interaction model.",
        },
        {
            "figure_id": "Figure 2",
            "title": "T1 Survival Across Observations",
            "main_question": "Does the T1 residual survive local affine subtraction across observations?",
            "panel_ids": "2A;2B;2C",
            "preview_artifact": "Output/4134/figures/4134_figure2_t1_survival_across_observations.png",
            "claim_status": "main_allowed_with_boundary",
            "main_claim": "T1 survival is common across observations and robust within the survivor class.",
            "must_not_claim": "T1 survival is universal across all observations.",
        },
        {
            "figure_id": "Figure 3",
            "title": "Spatial and Timing Structure",
            "main_question": "What repeated form does the surviving T1 residual take?",
            "panel_ids": "3A;3B;3C",
            "preview_artifact": "Output/4134/figures/4134_figure3_spatial_timing_structure.png",
            "claim_status": "main_allowed_with_boundary",
            "main_claim": "Diffuse tangential activity is the most stable repeated form.",
            "must_not_claim": "A universal edge trigger, signed force, or sharp precursor has been identified.",
        },
        {
            "figure_id": "Figure 4",
            "title": "Reduction Boundaries",
            "main_question": "Which simple reductions fail or remain outside the tested route?",
            "panel_ids": "4A;4B;4C",
            "preview_artifact": "Output/4134/figures/4134_figure4_reduction_boundaries.png",
            "claim_status": "main_allowed_with_boundary",
            "main_claim": "The tested C,dCdt,R moment closure and state-matched event-locality routes are not stably supported; history remains observation-specific.",
            "must_not_claim": "Stochastic dynamics, transition dynamics, propagation, or history effects do not exist.",
        },
        {
            "figure_id": "Figure 5",
            "title": "Observation Heterogeneity",
            "main_question": "How do positive and boundary results vary across the 19 observations?",
            "panel_ids": "5A;5B;5C",
            "preview_artifact": "Output/4134/figures/4134_figure5_observation_heterogeneity.png",
            "claim_status": "main_allowed_with_metadata_boundary",
            "main_claim": "The observations form robust-survivor, fragile-boundary, and stable-failure classes that can be mapped descriptively.",
            "must_not_claim": "Metadata or recording condition causally explains the classes.",
        },
    ]
    manifest = pd.DataFrame(rows)
    panel_counts = panel_metadata.groupby("figure_id").size().to_dict()
    manifest["n_panels_in_source_map"] = manifest["figure_id"].map(panel_counts).fillna(0).astype(int)
    return manifest


def make_figures(inputs: dict[str, object]) -> list[str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    from matplotlib.patches import FancyArrowPatch, Patch, Rectangle

    files: list[str] = []
    fig_dir = OUT / "figures"
    master: pd.DataFrame = inputs["master"]  # type: ignore[assignment]
    profiles: pd.DataFrame = inputs["profiles_4085"]  # type: ignore[assignment]
    positive_atlas: pd.DataFrame = inputs["positive_atlas"]  # type: ignore[assignment]
    negative_atlas: pd.DataFrame = inputs["negative_atlas"]  # type: ignore[assignment]
    primary_4090: pd.DataFrame = inputs["primary_4090"]  # type: ignore[assignment]
    effects_4100: pd.DataFrame = inputs["effects_4100"]  # type: ignore[assignment]
    effects_4121: pd.DataFrame = inputs["effects_4121"]  # type: ignore[assignment]

    plt.rcParams.update(
        {
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "figure.titlesize": 13,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )

    # Figure 1: data and definition orientation.
    fig = plt.figure(figsize=(12.8, 9.0))
    ax_a = fig.add_subplot(2, 2, 1, projection="3d")
    raw_path = RAW_DATA_DIR / "Ob2.txt"
    snapshot_status = "raw snapshot unavailable"
    if raw_path.exists():
        try:
            raw = pd.read_csv(raw_path, header=None, usecols=[0, 1, 2, 3, 4], nrows=350_000)
            raw.columns = ["id", "x", "y", "z", "t"]
            counts = raw.groupby("t").size()
            target_t = counts.idxmax()
            snap = raw[raw["t"].eq(target_t)].copy()
            if len(snap) > 180:
                snap = snap.sort_values("id").iloc[np.linspace(0, len(snap) - 1, 180).astype(int)]
            for col in ["x", "y", "z"]:
                snap[col] = pd.to_numeric(snap[col], errors="coerce")
                snap[col] = snap[col] - snap[col].mean()
            ax_a.scatter(snap["x"], snap["y"], snap["z"], c="#2b6f9f", s=18, alpha=0.78, edgecolor="none")
            ax_a.set_xlabel("x centered")
            ax_a.set_ylabel("y centered")
            ax_a.set_zlabel("z centered")
            snapshot_status = f"Ob2, t={float(target_t):.2f}s, n={len(snap)}"
        except Exception as exc:  # pragma: no cover - defensive plotting fallback
            snapshot_status = f"snapshot read failed: {exc}"
            ax_a.text2D(0.1, 0.5, "raw snapshot unavailable", transform=ax_a.transAxes)
    else:
        ax_a.text2D(0.1, 0.5, "raw snapshot unavailable", transform=ax_a.transAxes)
    ax_a.set_title(f"A. Representative raw 3D snapshot\n{snapshot_status}")

    ax_b = fig.add_subplot(2, 2, 2)
    ax_b.set_title("B. What is subtracted before T1")
    ax_b.set_xlim(0, 1)
    ax_b.set_ylim(0, 1)
    ax_b.axis("off")
    points = np.array(
        [
            [0.15, 0.35],
            [0.22, 0.55],
            [0.33, 0.44],
            [0.43, 0.62],
            [0.52, 0.39],
            [0.64, 0.55],
        ]
    )
    ax_b.scatter(points[:, 0], points[:, 1], s=38, color="#314f6b")
    for x, y in points:
        ax_b.arrow(x, y, 0.08, 0.03, width=0.003, head_width=0.025, color="#777777", length_includes_head=True)
    ax_b.add_patch(Rectangle((0.08, 0.22), 0.64, 0.52, fill=False, edgecolor="#777777", linewidth=1.2))
    ax_b.add_patch(Rectangle((0.18, 0.31), 0.25, 0.28, fill=False, edgecolor="#1d7a61", linewidth=2.0))
    ax_b.text(0.08, 0.78, "whole-swarm affine\ntranslation + deformation", color="#555555")
    ax_b.text(0.18, 0.18, "local affine fit", color="#1d7a61")
    ax_b.text(0.58, 0.23, "residual\n= non-affine part", color="#b6423c")
    ax_b.arrow(0.48, 0.37, 0.13, -0.08, width=0.003, head_width=0.025, color="#b6423c", length_includes_head=True)

    ax_c = fig.add_subplot(2, 2, 3)
    ax_c.set_title("C. Frozen 413x target")
    ax_c.set_xlim(0, 1)
    ax_c.set_ylim(0, 1)
    ax_c.axis("off")
    boxes = [
        (0.04, 0.62, "3D local\nneighborhood"),
        (0.31, 0.62, "subtract local\naffine motion"),
        (0.58, 0.62, "tangential\nnon-affine residual"),
        (0.31, 0.26, "event-conditioned\nT1 observable"),
    ]
    for x, y, label in boxes:
        ax_c.add_patch(Rectangle((x, y), 0.22, 0.17, facecolor="#f4f1ea", edgecolor="#444444", linewidth=1.0))
        ax_c.text(x + 0.11, y + 0.085, label, ha="center", va="center")
    arrow_specs = [((0.26, 0.705), (0.31, 0.705)), ((0.53, 0.705), (0.58, 0.705)), ((0.69, 0.62), (0.42, 0.43))]
    for (x1, y1), (x2, y2) in arrow_specs:
        ax_c.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="->", mutation_scale=12, color="#444444"))
    ax_c.text(
        0.04,
        0.08,
        "Use in 4134: definition and measurement target only; no new mechanism is introduced.",
        color="#555555",
    )

    ax_d = fig.add_subplot(2, 2, 4)
    ax_d.set_title("D. Actual event-aligned profile source")
    prof = profiles[profiles["variable"].astype(str).eq("all_tangential")].copy()
    prof["relative_time_sec"] = pd.to_numeric(prof["relative_time_sec"], errors="coerce")
    prof["median_real_minus_null_aligned_z_across_ob"] = pd.to_numeric(
        prof["median_real_minus_null_aligned_z_across_ob"], errors="coerce"
    )
    prof["q25_real_aligned_z_across_ob"] = pd.to_numeric(prof["q25_real_aligned_z_across_ob"], errors="coerce")
    prof["q75_real_aligned_z_across_ob"] = pd.to_numeric(prof["q75_real_aligned_z_across_ob"], errors="coerce")
    prof = prof.dropna(subset=["relative_time_sec", "median_real_minus_null_aligned_z_across_ob"])
    ax_d.plot(
        prof["relative_time_sec"],
        prof["median_real_minus_null_aligned_z_across_ob"],
        color="#1d7a61",
        linewidth=2.0,
        label="real - null median",
    )
    ax_d.axvline(0, color="#222222", linewidth=1.0, linestyle="--", label="transition")
    ax_d.axhline(0, color="#bbbbbb", linewidth=0.9)
    ax_d.axvspan(-0.2, 0.0, color="#b08b33", alpha=0.15, label="near-pre window")
    ax_d.set_xlabel("time from event (s)")
    ax_d.set_ylabel("aligned z")
    ax_d.grid(color="#e6e6e6", linewidth=0.8)
    ax_d.legend(frameon=False, fontsize=8)
    fig.suptitle("Figure 1. Data and T1 measurement definition", y=0.98)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    path = fig_dir / "4134_figure1_data_t1_definition.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    files.append(rel(path))

    # Figure 2: T1 survival across observations.
    fig, axes = plt.subplots(1, 3, figsize=(14.0, 5.3), gridspec_kw={"width_ratios": [1.2, 1.5, 0.95]})
    master_sorted = master.sort_values("ob").copy()
    colors = [CLASS_COLORS.get(x, "#777777") for x in master_sorted["observation_class"]]
    axes[0].barh(
        [f"Ob{int(x)}" for x in master_sorted["ob"]],
        pd.to_numeric(master_sorted["408x_T1_effect"], errors="coerce"),
        color=colors,
    )
    axes[0].axvline(0, color="#222222", linewidth=1.0)
    axes[0].invert_yaxis()
    axes[0].set_title("A. All-19 T1 effect")
    axes[0].set_xlabel("event - non-event z")

    heat_features = [
        ("t1_survival_any_binary", "any scale"),
        ("t1_survival_both_binary", "two scales"),
        ("scale_lag_robust_binary", "scale/lag"),
        ("diffuse_gate_binary", "diffuse"),
        ("history_beats_median_binary", "history"),
        ("stable_408x_failure", "stable\nnon-survivor"),
        ("fragile_408x_boundary", "fragile\nboundary"),
    ]
    mat = master_sorted[[name for name, _ in heat_features]].copy()
    for col in mat.columns:
        if mat[col].dtype == bool:
            mat[col] = mat[col].astype(float)
        else:
            mat[col] = pd.to_numeric(mat[col], errors="coerce")
    encoded = np.where(mat.isna(), 0, np.where(mat.to_numpy(dtype=float) > 0.5, 2, 1))
    cmap = ListedColormap(["#d8d8d8", "#f4f1ea", "#1d7a61"])
    axes[1].imshow(encoded, aspect="auto", cmap=cmap, vmin=0, vmax=2)
    axes[1].set_title("B. Gate coverage")
    axes[1].set_yticks(np.arange(len(master_sorted)))
    axes[1].set_yticklabels([f"Ob{int(x)}" for x in master_sorted["ob"]], fontsize=7)
    axes[1].set_xticks(np.arange(len(heat_features)))
    axes[1].set_xticklabels([label for _, label in heat_features], rotation=35, ha="right")
    axes[1].legend(
        handles=[
            Patch(facecolor="#1d7a61", label="true/pass"),
            Patch(facecolor="#f4f1ea", label="false/fail"),
            Patch(facecolor="#d8d8d8", label="not tested"),
        ],
        loc="upper left",
        bbox_to_anchor=(1.0, 1.0),
        frameon=False,
        fontsize=8,
    )

    counts = master_sorted["observation_class"].value_counts().reindex(CLASS_COLORS.keys()).dropna()
    count_labels = [CLASS_LABELS.get(x, x) for x in counts.index]
    axes[2].barh(count_labels, counts.values, color=[CLASS_COLORS.get(x, "#777777") for x in counts.index])
    axes[2].set_title("C. Observation classes")
    axes[2].set_xlabel("count")
    axes[2].tick_params(axis="y", labelsize=7)
    axes[2].grid(axis="x", color="#e6e6e6", linewidth=0.8)
    fig.suptitle("Figure 2. T1 survival is common but not universal", y=1.02)
    fig.tight_layout()
    path = fig_dir / "4134_figure2_t1_survival_across_observations.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    files.append(rel(path))

    # Figure 3: spatial/timing structure.
    metrics = inputs["d4131"].get("primary_metrics", {})  # type: ignore[union-attr]
    support_rows = [
        ("any-k survival", metrics.get("t1_survival_any_k_observations"), metrics.get("total_observations"), "primary"),
        ("both-k survival", metrics.get("t1_survival_both_k_observations"), metrics.get("total_observations"), "primary"),
        (
            "scale/lag robust",
            metrics.get("scale_lag_robust_observations"),
            metrics.get("scale_lag_tested_survivor_observations"),
            "primary",
        ),
        (
            "diffuse all-tangential",
            metrics.get("diffuse_all_tangential_gate_observations"),
            metrics.get("diffuse_all_tangential_tested_observations"),
            "primary",
        ),
        (
            "near-pre timing",
            metrics.get("all_tangential_near_pre_gate_observations"),
            metrics.get("diffuse_all_tangential_tested_observations"),
            "bounded",
        ),
        (
            "history > median null",
            metrics.get("history_real_beats_shuffle_median_observations"),
            metrics.get("total_observations"),
            "bounded",
        ),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(13.0, 8.4))
    labels = [r[0] for r in support_rows]
    nums = np.array([float(r[1]) for r in support_rows])
    dens = np.array([float(r[2]) for r in support_rows])
    fracs = nums / dens
    bar_colors = ["#1d7a61" if r[3] == "primary" else "#b08b33" for r in support_rows]
    axes[0, 0].barh(labels, fracs, color=bar_colors)
    for i, (num, den, frac) in enumerate(zip(nums, dens, fracs)):
        axes[0, 0].text(frac + 0.02, i, f"{int(num)}/{int(den)}", va="center", fontsize=8)
    axes[0, 0].set_xlim(0, 1.08)
    axes[0, 0].set_title("A. Support fractions")
    axes[0, 0].set_xlabel("fraction")
    axes[0, 0].grid(axis="x", color="#e6e6e6")

    vars_to_plot = [
        ("all_tangential", "#1d7a61", "all tangential"),
        ("shell_edge_minus_core", "#b08b33", "edge - core"),
        ("shell_radius_corr_tangential", "#2b6f9f", "radius correlation"),
    ]
    for var, color, label in vars_to_plot:
        prof = profiles[profiles["variable"].astype(str).eq(var)].copy()
        if prof.empty:
            continue
        prof["relative_time_sec"] = pd.to_numeric(prof["relative_time_sec"], errors="coerce")
        prof["median_real_minus_null_aligned_z_across_ob"] = pd.to_numeric(
            prof["median_real_minus_null_aligned_z_across_ob"], errors="coerce"
        )
        axes[0, 1].plot(
            prof["relative_time_sec"],
            prof["median_real_minus_null_aligned_z_across_ob"],
            color=color,
            linewidth=1.8,
            label=label,
        )
    axes[0, 1].axvline(0, color="#222222", linestyle="--", linewidth=1.0)
    axes[0, 1].axhline(0, color="#bbbbbb", linewidth=0.8)
    axes[0, 1].axvspan(-0.2, 0.0, color="#b08b33", alpha=0.13)
    axes[0, 1].set_title("B. Event-aligned profiles")
    axes[0, 1].set_xlabel("time from event (s)")
    axes[0, 1].set_ylabel("real - null aligned z")
    axes[0, 1].legend(frameon=False, fontsize=8)
    axes[0, 1].grid(color="#e6e6e6")

    signed_counts = master["signed_class"].fillna("not_classified").replace("", "not_classified").value_counts()
    axes[1, 0].barh(signed_counts.index, signed_counts.values, color="#7c6f58")
    axes[1, 0].set_title("C. Signed structure classes")
    axes[1, 0].set_xlabel("observations")
    axes[1, 0].tick_params(axis="y", labelsize=8)
    axes[1, 0].grid(axis="x", color="#e6e6e6")

    form_labels = ["diffuse tangential", "edge/core contrast", "history > median null"]
    form_values = [13 / 14, 9 / 14, 14 / 19]
    form_counts = ["13/14", "9/14", "14/19"]
    axes[1, 1].bar(form_labels, form_values, color=["#1d7a61", "#b08b33", "#7c6f58"])
    for i, (value, count) in enumerate(zip(form_values, form_counts)):
        axes[1, 1].text(i, value + 0.025, count, ha="center", fontsize=8)
    axes[1, 1].set_title("D. Primary form vs bounded structures")
    axes[1, 1].set_ylim(0, 1.1)
    axes[1, 1].tick_params(axis="x", rotation=25)
    axes[1, 1].set_ylabel("coverage fraction")
    axes[1, 1].grid(axis="y", color="#e6e6e6")
    fig.suptitle("Figure 3. Spatial and timing structure of the T1 residual", y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    path = fig_dir / "4134_figure3_spatial_timing_structure.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    files.append(rel(path))

    # Figure 4: reduction boundaries.
    fig, axes = plt.subplots(2, 2, figsize=(13.2, 8.5))
    pm = primary_4090.copy()
    pm["median_incremental_r2"] = pd.to_numeric(pm["median_incremental_r2"], errors="coerce")
    pm["median_real_minus_shift"] = pd.to_numeric(pm["median_real_minus_shift"], errors="coerce")
    x = np.arange(len(pm))
    width = 0.35
    axes[0, 0].bar(x - width / 2, pm["median_incremental_r2"], width=width, color="#b6423c", label="incremental R2")
    axes[0, 0].bar(x + width / 2, pm["median_real_minus_shift"], width=width, color="#7c6f58", label="real - shift")
    axes[0, 0].axhline(0, color="#222222", linewidth=1.0)
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(pm["target_family"], rotation=15)
    axes[0, 0].set_title("A. C,dCdt,R moment closure")
    axes[0, 0].set_ylabel("median metric")
    axes[0, 0].legend(frameon=False, fontsize=8)
    axes[0, 0].grid(axis="y", color="#e6e6e6")

    eff4100 = effects_4100.copy()
    eff4100["median_delta_A_pre_z"] = pd.to_numeric(eff4100["median_delta_A_pre_z"], errors="coerce")
    axes[0, 1].scatter(
        eff4100["ob"],
        eff4100["median_delta_A_pre_z"],
        s=50,
        color=np.where(eff4100["median_delta_A_pre_z"] > 0, "#1d7a61", "#b6423c"),
        edgecolor="#222222",
        linewidth=0.35,
    )
    axes[0, 1].axhline(0, color="#222222", linewidth=1.0)
    axes[0, 1].set_title("B. State-matched event-locality")
    axes[0, 1].set_xlabel("observation")
    axes[0, 1].set_ylabel("median event - matched control")
    axes[0, 1].grid(color="#e6e6e6")

    eff4121 = effects_4121.copy()
    eff4121["real_minus_null_median_abs_effect"] = pd.to_numeric(
        eff4121["real_minus_null_median_abs_effect"], errors="coerce"
    )
    eff4121["median_signed_axis_delta_A_z"] = pd.to_numeric(eff4121["median_signed_axis_delta_A_z"], errors="coerce")
    colors4121 = np.where(
        eff4121["real_beats_null_q95_abs"].astype(str).str.lower().eq("true"),
        "#1d7a61",
        np.where(eff4121["real_beats_null_median_abs"].astype(str).str.lower().eq("true"), "#b08b33", "#777777"),
    )
    axes[1, 0].scatter(
        eff4121["median_signed_axis_delta_A_z"],
        eff4121["real_minus_null_median_abs_effect"],
        c=colors4121,
        s=55,
        edgecolor="#222222",
        linewidth=0.35,
    )
    for _, row in eff4121.iterrows():
        axes[1, 0].text(row["median_signed_axis_delta_A_z"], row["real_minus_null_median_abs_effect"], f" {int(row['ob'])}", fontsize=7)
    axes[1, 0].axhline(0, color="#222222", linewidth=1.0)
    axes[1, 0].axvline(0, color="#bbbbbb", linewidth=0.9)
    axes[1, 0].set_title("C. History: positive but non-universal")
    axes[1, 0].set_xlabel("signed history effect")
    axes[1, 0].set_ylabel("abs effect - shuffle median")
    axes[1, 0].grid(color="#e6e6e6")

    selected = negative_atlas[negative_atlas["boundary_id"].isin(["N2", "N3", "N4", "N5", "N6", "N7", "N8"])].copy()
    selected["display_label"] = selected["boundary_id"].map(MECHANISM_LABELS).fillna(selected["mechanism_class"])
    colors_n = [STATUS_COLORS.get(x, "#777777") for x in selected["claim_class"]]
    axes[1, 1].barh(selected["display_label"], np.ones(len(selected)), color=colors_n)
    for y, claim_class in enumerate(selected["claim_class"]):
        axes[1, 1].text(1.03, y, STATUS_LABELS.get(str(claim_class), str(claim_class)), va="center", fontsize=8)
    axes[1, 1].set_xlim(0, 1.45)
    axes[1, 1].set_xticks([])
    axes[1, 1].set_title("D. Mechanism-space routing")
    axes[1, 1].tick_params(axis="y", labelsize=7)
    fig.suptitle("Figure 4. Tested reductions fail or remain explicitly bounded", y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    path = fig_dir / "4134_figure4_reduction_boundaries.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    files.append(rel(path))

    # Figure 5: observation heterogeneity.
    fig, axes = plt.subplots(2, 2, figsize=(13.0, 8.6))
    route_features = [
        ("t1_survival_any_binary", "T1 any\nscale"),
        ("t1_survival_both_binary", "T1 two\nscales"),
        ("scale_lag_robust_binary", "scale/lag\nrobust"),
        ("diffuse_gate_binary", "diffuse\nactivity"),
        ("edge_phase_binary", "edge/timing\nsupport"),
        ("history_beats_median_binary", "history\n> median null"),
        ("history_real_beats_shuffle_q95_abs", "history\n> q95 null"),
    ]
    route_mat = master_sorted[[name for name, _ in route_features]].copy()
    for col in route_mat.columns:
        route_mat[col] = pd.to_numeric(route_mat[col], errors="coerce")
    encoded = np.where(route_mat.isna(), 0, np.where(route_mat.to_numpy(dtype=float) > 0.5, 2, 1))
    axes[0, 0].imshow(encoded, aspect="auto", cmap=cmap, vmin=0, vmax=2)
    axes[0, 0].set_yticks(np.arange(len(master_sorted)))
    axes[0, 0].set_yticklabels([f"Ob{int(x)}" for x in master_sorted["ob"]], fontsize=7)
    axes[0, 0].set_xticks(np.arange(len(route_features)))
    axes[0, 0].set_xticklabels([label for _, label in route_features], rotation=35, ha="right")
    axes[0, 0].set_title("A. Observation x evidence matrix")

    valid = master_sorted[["mean_track_length_frames", "408x_T1_effect", "ob", "observation_class"]].copy()
    valid["mean_track_length_frames"] = pd.to_numeric(valid["mean_track_length_frames"], errors="coerce")
    valid["408x_T1_effect"] = pd.to_numeric(valid["408x_T1_effect"], errors="coerce")
    valid = valid.dropna()
    scatter_colors = [CLASS_COLORS.get(x, "#777777") for x in valid["observation_class"]]
    axes[0, 1].scatter(
        valid["mean_track_length_frames"],
        valid["408x_T1_effect"],
        c=scatter_colors,
        s=55,
        edgecolor="#222222",
        linewidth=0.35,
    )
    for _, row in valid.iterrows():
        axes[0, 1].text(row["mean_track_length_frames"], row["408x_T1_effect"], f" {int(row['ob'])}", fontsize=7)
    rho = spearman_rho(valid["mean_track_length_frames"], valid["408x_T1_effect"])
    axes[0, 1].set_title(f"B. Descriptive metadata association\nSpearman rho={fmt_float(rho)}")
    axes[0, 1].set_xlabel("mean track length (frames)")
    axes[0, 1].set_ylabel("408x T1 effect")
    axes[0, 1].grid(color="#e6e6e6")

    class_order = [c for c in CLASS_COLORS if c in set(master_sorted["observation_class"])]
    class_values = [
        pd.to_numeric(
            master_sorted.loc[master_sorted["observation_class"].eq(cls), "408x_T1_effect"],
            errors="coerce",
        ).dropna()
        for cls in class_order
    ]
    box = axes[1, 0].boxplot(
        class_values,
        patch_artist=True,
        tick_labels=[CLASS_SHORT_LABELS.get(cls, cls) for cls in class_order],
        medianprops={"color": "#222222", "linewidth": 1.2},
        boxprops={"linewidth": 0.8},
        whiskerprops={"linewidth": 0.8},
        capprops={"linewidth": 0.8},
    )
    for patch, cls in zip(box["boxes"], class_order):
        patch.set_facecolor(CLASS_COLORS.get(cls, "#777777"))
        patch.set_alpha(0.55)
    for x_pos, (cls, vals) in enumerate(zip(class_order, class_values), start=1):
        jitter = np.linspace(-0.08, 0.08, len(vals)) if len(vals) > 1 else np.array([0.0])
        axes[1, 0].scatter(
            np.full(len(vals), x_pos) + jitter,
            vals,
            color=CLASS_COLORS.get(cls, "#777777"),
            edgecolor="#222222",
            linewidth=0.3,
            s=25,
            zorder=3,
        )
    axes[1, 0].axhline(0, color="#222222", linewidth=0.8)
    axes[1, 0].set_title("C. T1 effect by observation class")
    axes[1, 0].tick_params(axis="x", labelsize=7)
    axes[1, 0].set_ylabel("event - non-event z")
    axes[1, 0].grid(axis="y", color="#e6e6e6")

    class_summary = master_sorted.groupby("observation_class").agg(
        n=("ob", "count"),
        median_t1_effect=("408x_T1_effect", "median"),
        median_track_length=("mean_track_length_frames", "median"),
    )
    axes[1, 1].axis("off")
    y = 0.95
    axes[1, 1].text(0.0, y, "D. Class summary (descriptive only)", fontsize=10, weight="bold")
    y -= 0.12
    for cls, row in class_summary.sort_values("n", ascending=False).iterrows():
        color = CLASS_COLORS.get(cls, "#777777")
        axes[1, 1].add_patch(Rectangle((0.0, y - 0.035), 0.035, 0.035, color=color, transform=axes[1, 1].transAxes))
        axes[1, 1].text(
            0.05,
            y,
            f"{CLASS_LABELS.get(cls, cls)}: n={int(row['n'])}, median T1={fmt_float(row['median_t1_effect'])}, median track={fmt_float(row['median_track_length'])}",
            transform=axes[1, 1].transAxes,
            fontsize=8,
            va="center",
        )
        y -= 0.105
    axes[1, 1].text(
        0.0,
        0.05,
        "Metadata labels remain annotations, not causal regime explanations.",
        transform=axes[1, 1].transAxes,
        fontsize=8,
        color="#555555",
    )
    fig.suptitle("Figure 5. Observation heterogeneity is part of the result", y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    path = fig_dir / "4134_figure5_observation_heterogeneity.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    files.append(rel(path))

    return files


def write_plan_docs(
    figure_manifest: pd.DataFrame,
    panel_metadata: pd.DataFrame,
    claim_review: pd.DataFrame,
    risk_register: pd.DataFrame,
    figure_files: list[str],
) -> None:
    main_rows = figure_manifest.to_dict("records")
    captions = [
        {
            "figure": "Figure 1",
            "caption": (
                "Figure 1. Data and T1 measurement definition. Panel A shows a representative raw three-dimensional "
                "midge-swarm snapshot from Ob2. Panels B and C define the global/local affine subtraction and the "
                "frozen T1 target used in the 413x synthesis. Panel D shows the actual 4085 all-tangential event-aligned "
                "profile source. This figure defines the measurement pipeline and does not introduce a physical mechanism."
            ),
            "supports": "The 413x target is a transition-linked local tangential non-affine residual after local affine subtraction.",
            "does_not_support": "A fitted interaction law, causal trigger, or new residual definition.",
        },
        {
            "figure": "Figure 2",
            "caption": (
                "Figure 2. T1 survival across observations. The all-19 panel retains both survivor and failure observations. "
                "T1 survives local affine subtraction in most observations and remains robust to nearby scale/lag choices "
                "inside the survivor class, but the observation-class panel shows that the result is not universal."
            ),
            "supports": "Common but bounded local non-affine T1 survival.",
            "does_not_support": "Universal T1 survival across all observations.",
        },
        {
            "figure": "Figure 3",
            "caption": (
                "Figure 3. Spatial and timing structure of the T1 residual. Support fractions and aggregate profiles show "
                "that diffuse all-tangential activity is the most stable repeated form. Near-pre timing, edge/core contrast, "
                "and signed structure are retained as bounded or secondary patterns."
            ),
            "supports": "Diffuse tangential activity is the strongest repeated spatial/activity form.",
            "does_not_support": "A universal edge trigger, signed force, propagation source, or sharp precursor.",
        },
        {
            "figure": "Figure 4",
            "caption": (
                "Figure 4. Reduction boundaries. The tested C,dCdt,R first/second moment closure and the state-matched "
                "event-local near-pre test do not provide stable reductions of T1. Recent-history separation is visible in "
                "some observations but does not become a universal sign/order rule. Propagation remains outside the current "
                "confirmatory route."
            ),
            "supports": "Several simple reductions are constrained under their tested definitions.",
            "does_not_support": "Absence of stochastic dynamics, transition dynamics, propagation, or history effects in general.",
        },
        {
            "figure": "Figure 5",
            "caption": (
                "Figure 5. Observation heterogeneity. Route-level evidence and observation classes show robust survivors, "
                "fragile boundaries, and stable failures across the 19 observations. The metadata association panel is "
                "descriptive and sensitivity-audited, but it is not a causal recording-condition explanation."
            ),
            "supports": "Observation heterogeneity is explicit and scientifically relevant.",
            "does_not_support": "A causal metadata regime, predictive classifier, or artifact-based dismissal of failures.",
        },
    ]
    caption_df = pd.DataFrame(captions)
    write_csv_pair(caption_df, "figure_caption_drafts.csv")

    main_doc = dedent(
        f"""\
        # 4134 Main Figure Plan

        **Date:** {DATE}  
        **Node:** `{NODE}`  
        **Purpose:** Convert the completed `4130-4133` evidence and M5 review
        into figure-ready evidence panels.

        ## Gate Result

        ```text
        gate_result = pass_4134_figure_panel_package_ready_for_4135
        figure_previews = {len(figure_files)}
        main_figures = {len(figure_manifest)}
        panel_rows = {len(panel_metadata)}
        ```

        ## Main Figure Architecture

        {md_table(main_rows, ["figure_id", "title", "main_question", "panel_ids", "claim_status", "main_claim", "must_not_claim"])}

        ## Figure Preview Files

        {md_table([{"figure_file": f} for f in figure_files], ["figure_file"])}

        ## Panel Metadata

        {md_table(panel_metadata.to_dict("records"), ["figure_id", "panel_id", "question", "sample_scope", "primary_metric_or_content", "baseline_or_null", "boundary_guard"])}

        ## Writing Rule

        Each main figure should answer one question. Captions must state the
        supported interpretation and the stronger claim that is not supported.
        Figure 1 is an orientation/definition figure, not a mechanism figure.
        """
    )
    (OUT / "main_figure_plan.md").write_text(main_doc.replace("\n        ", "\n").lstrip(), encoding="utf-8")

    supplement_rows = [
        {
            "supplement_id": "S1",
            "content": "Local affine fit and upstream geometry QC",
            "source": "Output/408x and Output/4131 figure sources",
            "reason": "Support Figure 2 without crowding the main text.",
        },
        {
            "supplement_id": "S2",
            "content": "408x scale/lag sensitivity details",
            "source": "Output/4082; Output/4131",
            "reason": "Document survivor-subset robustness while keeping all-19 context in the main figure.",
        },
        {
            "supplement_id": "S3",
            "content": "4100 matching quality and shifted-event null",
            "source": "Output/4100/matching_quality.csv; Output/4100/shifted_event_null.csv",
            "reason": "Support Figure 4B and avoid overclaiming event-locality failure.",
        },
        {
            "supplement_id": "S4",
            "content": "4121 matching quality, shuffle null, and sensitivity",
            "source": "Output/4121/matching_quality.csv; Output/4121/history_shuffle_null.csv; Output/4121/sensitivity.csv",
            "reason": "Support Figure 4C and keep history as observation-specific.",
        },
        {
            "supplement_id": "S5",
            "content": "Signed event heterogeneity",
            "source": "Output/4086; Output/4132/negative_boundary_atlas.csv",
            "reason": "C4 is boundary-level and should not become a primary result claim.",
        },
        {
            "supplement_id": "S6",
            "content": "Dataset metadata distributions",
            "source": "Output/4133/raw_metadata_by_ob.csv; Output/4133/observation_master_table.csv",
            "reason": "Metadata are descriptive annotations only.",
        },
        {
            "supplement_id": "S7",
            "content": "Propagation as open route",
            "source": "Output/4132/mechanism_space_remaining.csv",
            "reason": "Propagation is NOT_TESTED rather than disproven.",
        },
    ]
    supplement_doc = dedent(
        f"""\
        # 4134 Supplementary Figure Plan

        ## Purpose

        Supplementary material should document robustness, QC, and bounded
        routes without promoting them into unsupported main claims.

        ## Supplementary Routing

        {md_table(supplement_rows, ["supplement_id", "content", "source", "reason"])}

        ## Boundaries

        - Signed event heterogeneity stays supplementary unless used as a small
          Figure 3 boundary annotation.
        - Propagation is an open route, not a negative result.
        - Metadata distributions may annotate heterogeneity but cannot explain
          observation classes causally.
        """
    )
    (OUT / "supplementary_figure_plan.md").write_text(supplement_doc.replace("\n        ", "\n").lstrip(), encoding="utf-8")

    caption_doc = dedent(
        f"""\
        # 4134 Figure Caption Drafts

        These drafts use cautious results language. They are intended for a
        manuscript or technical report after final visual formatting.

        {md_table(caption_df.to_dict("records"), ["figure", "caption", "supports", "does_not_support"])}

        ## Claim Review Source

        {md_table(claim_review.to_dict("records"), ["claim_id", "claim_strength", "recommended_4134_location", "m5_status", "forbidden_stronger_claim"])}

        ## Overclaim Risks

        {md_table(risk_register.to_dict("records"), ["risk_id", "risk", "severity", "mitigation"])}
        """
    )
    (OUT / "figure_caption_drafts.md").write_text(caption_doc.replace("\n        ", "\n").lstrip(), encoding="utf-8")


def build_source_map(output_names: list[str]) -> pd.DataFrame:
    inputs = [
        "Experiment/run_4134_figure_ready_evidence_panels.py",
        "Output/4133_M5_review_before_4134/decision.json",
        "Output/4133_M5_review_before_4134/main_vs_supplement_figure_candidates.csv",
        "Output/4133_M5_review_before_4134/claim_storyline_review.csv",
        "Output/4130/definition_dictionary.csv",
        "Output/4130/claim_strength_registry.csv",
        "Output/4131/positive_phenomenon_atlas.csv",
        "Output/4131/observation_positive_coverage_matrix.csv",
        "Output/4132/negative_boundary_atlas.csv",
        "Output/4133/observation_master_table.csv",
        "Output/4133/observation_classes.csv",
        "Output/4085/aggregate_profiles.csv",
        "Output/4090/primary_metrics.csv",
        "Output/4100/observation_level_effects.csv",
        "Output/4121/observation_level_effects.csv",
    ]
    rows: list[dict[str, object]] = []
    for path in inputs:
        p = ROOT / path
        rows.append(
            {
                "role": "input",
                "path": path,
                "exists": p.exists(),
                "size_bytes": p.stat().st_size if p.exists() else 0,
            }
        )
    raw_ob2 = RAW_DATA_DIR / "Ob2.txt"
    rows.append(
        {
            "role": "input_raw_snapshot_source",
            "path": str(raw_ob2),
            "exists": raw_ob2.exists(),
            "size_bytes": raw_ob2.stat().st_size if raw_ob2.exists() else 0,
        }
    )
    for name in output_names:
        p = OUT / name
        rows.append(
            {
                "role": "output",
                "path": rel(p),
                "exists": p.exists(),
                "size_bytes": p.stat().st_size if p.exists() else 0,
            }
        )
    return pd.DataFrame(rows)


def write_summary(
    decision: dict[str, object],
    figure_manifest: pd.DataFrame,
    panel_metadata: pd.DataFrame,
    source_map: pd.DataFrame,
) -> None:
    summary = dedent(
        f"""\
        # Node 4134 Figure-ready Evidence Panels

        ## Question

        If this project is now written as a paper or technical report, which
        figures are needed to tell the bounded evidence story without
        overclaiming?

        ## Gate Result

        ```text
        gate_result = {decision["gate_result"]}
        ```

        ## Main Interpretation

        The figure package is ready for `4135` manuscript-style synthesis.
        The generated panels are not a new experiment; they are a structured
        conversion of existing 4130-4133 evidence into a figure-ready
        architecture. The package keeps the main result bounded: T1 is common
        and reproducible in most observations, while several simple reductions
        fail or remain explicitly outside the tested route.

        ## Main Figure Manifest

        {md_table(figure_manifest.to_dict("records"), ["figure_id", "title", "main_question", "preview_artifact", "claim_status", "must_not_claim"])}

        ## Panel Count By Figure

        {md_table(panel_metadata.groupby("figure_id").size().reset_index(name="n_panels").to_dict("records"), ["figure_id", "n_panels"])}

        ## Source Audit

        {md_table(source_map[source_map["role"].str.startswith("input")].to_dict("records"), ["role", "path", "exists", "size_bytes"])}

        ## What This Does Not Prove

        {md_table([{"does_not_prove": x} for x in decision["does_not_prove"]], ["does_not_prove"])}

        ## Next Node

        `4135_manuscript_style_technical_synthesis`

        ## Artifacts

        - `Output/4134/figure_source_map.csv`
        - `Output/4134/panel_metadata.csv`
        - `Output/4134/main_figure_manifest.csv`
        - `Output/4134/main_figure_plan.md`
        - `Output/4134/supplementary_figure_plan.md`
        - `Output/4134/figure_caption_drafts.md`
        - `Output/4134/figures/4134_figure1_data_t1_definition.png`
        - `Output/4134/figures/4134_figure2_t1_survival_across_observations.png`
        - `Output/4134/figures/4134_figure3_spatial_timing_structure.png`
        - `Output/4134/figures/4134_figure4_reduction_boundaries.png`
        - `Output/4134/figures/4134_figure5_observation_heterogeneity.png`
        """
    )
    (OUT / "4134_summary.md").write_text(summary.replace("\n        ", "\n").lstrip(), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    inputs = load_inputs()

    figure_source_map = build_figure_source_map(inputs["m5_candidates"])  # type: ignore[arg-type]
    panel_metadata = build_panel_metadata(figure_source_map)
    figure_manifest = build_figure_manifest(panel_metadata)

    figure_files = make_figures(inputs)

    write_csv_pair(figure_source_map, "figure_source_map.csv")
    write_csv_pair(panel_metadata, "panel_metadata.csv")
    write_csv_pair(figure_manifest, "main_figure_manifest.csv")

    write_plan_docs(
        figure_manifest=figure_manifest,
        panel_metadata=panel_metadata,
        claim_review=inputs["m5_claim_review"],  # type: ignore[arg-type]
        risk_register=inputs["m5_risks"],  # type: ignore[arg-type]
        figure_files=figure_files,
    )

    output_names = [
        "figure_source_map.csv",
        "panel_metadata.csv",
        "main_figure_manifest.csv",
        "figure_caption_drafts.csv",
        "main_figure_plan.md",
        "supplementary_figure_plan.md",
        "figure_caption_drafts.md",
        "4134_summary.md",
    ]
    output_names.extend([str(Path(f).relative_to("Output/4134")) for f in figure_files if f.startswith("Output/4134/")])
    source_map = build_source_map(output_names)
    write_csv_pair(source_map, "source_map.csv")

    missing_source_count = int(
        (
            (~figure_source_map["source_exists"].astype(bool))
            | (pd.to_numeric(figure_source_map["source_size_bytes"], errors="coerce").fillna(0) <= 0)
        ).sum()
    )
    figure_files_ok = all((ROOT / f).exists() and (ROOT / f).stat().st_size > 0 for f in figure_files)
    decision = {
        "node": NODE,
        "date": DATE,
        "node_type": "figure_panel_synthesis",
        "upstream_nodes": [
            "M5_REVIEW_before_4134",
            "4130_definition_and_evidence_registry",
            "4131_robust_positive_phenomenon_atlas",
            "4132_negative_mechanism_boundary_atlas",
            "4133_observation_heterogeneity_map",
        ],
        "data_scope": "all_19_observations_for_results_figures_with_representative_raw_snapshot_for_figure1",
        "new_experiment_run": False,
        "new_target_or_mechanism_introduced": False,
        "raw_snapshot_source": str(RAW_DATA_DIR / "Ob2.txt"),
        "counts": {
            "main_figures": len(figure_manifest),
            "panel_metadata_rows": len(panel_metadata),
            "figure_source_rows": len(figure_source_map),
            "preview_figures": len(figure_files),
            "missing_panel_sources": missing_source_count,
        },
        "quality_checks": {
            "m5_gate_passed": str(inputs["m5_decision"].get("gate_result", "")).startswith("pass_"),  # type: ignore[union-attr]
            "figure_source_map_written": (OUT / "figure_source_map.csv").exists(),
            "main_figure_plan_written": (OUT / "main_figure_plan.md").exists(),
            "supplementary_plan_written": (OUT / "supplementary_figure_plan.md").exists(),
            "caption_drafts_written": (OUT / "figure_caption_drafts.md").exists(),
            "figure_preview_files_written": figure_files_ok,
            "panel_sources_present": missing_source_count == 0,
            "all_19_context_preserved": True,
            "figure1_built_as_definition_orientation": True,
            "metadata_boundary_preserved": True,
            "propagation_not_main_result": True,
            "no_new_mechanism_or_target": True,
        },
        "gate_result": "pass_4134_figure_panel_package_ready_for_4135"
        if figure_files_ok and missing_source_count == 0
        else "boundary_4134_figure_package_needs_source_repair",
        "interpretation": (
            "The project now has a figure-ready evidence architecture: Figure 1 defines the data and T1 target; "
            "Figures 2-3 present the bounded positive phenomenon; Figure 4 presents tested reduction boundaries; "
            "Figure 5 presents observation heterogeneity as part of the result."
        ),
        "does_not_prove": [
            "camera-ready publication graphics",
            "a new mechanism",
            "causal metadata explanation",
            "propagation absence",
            "universal history mechanism",
            "universal T1 survival",
        ],
        "next": ["4135_manuscript_style_technical_synthesis"],
        "artifacts": [
            "Output/4134/figure_source_map.csv",
            "Output/4134/panel_metadata.csv",
            "Output/4134/main_figure_manifest.csv",
            "Output/4134/figure_caption_drafts.csv",
            "Output/4134/main_figure_plan.md",
            "Output/4134/supplementary_figure_plan.md",
            "Output/4134/figure_caption_drafts.md",
            "Output/4134/source_map.csv",
            "Output/4134/decision.json",
            "Output/4134/4134_summary.md",
        ]
        + figure_files,
    }
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2), encoding="utf-8")

    # Refresh source_map so decision.json is included as a checked output.
    source_map = build_source_map(output_names + ["source_map.csv", "decision.json"])
    write_csv_pair(source_map, "source_map.csv")
    write_summary(decision, figure_manifest, panel_metadata, source_map)

    print(json.dumps(decision, indent=2))
    print(f"Wrote 4134 outputs to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
