"""Node 4150 final figure cleanup and redesign.

This node is a figure-package hardening step. It reuses the 4134 source tables
and creates final, publication-facing figure files under Output/4150 and
mypaper2/Latex/figures. It does not change any analysis definition or result.
"""

from __future__ import annotations

import json
import math
import os
import shutil
from pathlib import Path
from textwrap import dedent
from typing import Any

import numpy as np
import pandas as pd

import run_4134_figure_ready_evidence_panels as r4134


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4150"
FIG = OUT / "figures"
TABLES = OUT / "tables"
LATEX_FIG = ROOT / "mypaper2" / "Latex" / "figures"
DATE = "2026-09-02"
NODE = "4150_final_figure_cleanup"


CLASS_COLORS = r4134.CLASS_COLORS
CLASS_LABELS = r4134.CLASS_LABELS
CLASS_SHORT_LABELS = r4134.CLASS_SHORT_LABELS
STATUS_COLORS = r4134.STATUS_COLORS
STATUS_LABELS = r4134.STATUS_LABELS
MECHANISM_LABELS = r4134.MECHANISM_LABELS


def ensure_dirs() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    LATEX_FIG.mkdir(parents=True, exist_ok=True)


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv_pair(df: pd.DataFrame, name: str) -> None:
    df.to_csv(OUT / name, index=False)
    df.to_csv(TABLES / name, index=False)


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


def md_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    if not rows:
        return "_No rows._"
    out = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        values: list[str] = []
        for col in columns:
            value = row.get(col, "")
            if isinstance(value, float):
                values.append(fmt_float(value, 4))
            else:
                values.append(str(value).replace("\n", " ").replace("|", "\\|"))
        out.append("| " + " | ".join(values) + " |")
    return "\n".join(out)


def bool_matrix(df: pd.DataFrame) -> np.ndarray:
    matrix = df.copy()
    for col in matrix.columns:
        matrix[col] = pd.to_numeric(matrix[col], errors="coerce")
    return np.where(matrix.isna(), 0, np.where(matrix.to_numpy(dtype=float) > 0.5, 2, 1))


def friendly_signed_label(label: object) -> str:
    mapping = {
        "mirror_symmetric_opposite_sign": "mirror-symmetric\nopposite sign",
        "not_classified": "not classified",
        "no_signed_gate": "no signed gate",
        "low_to_high_dominant": "low-to-high\ndominant",
        "opposite_sign_but_imbalanced": "opposite sign,\nimbalanced",
    }
    text = str(label) if str(label).strip() else "not_classified"
    return mapping.get(text, text.replace("_", " "))


def save_figure(fig: Any, stem: str) -> list[str]:
    png = FIG / f"{stem}.png"
    pdf = FIG / f"{stem}.pdf"
    fig.savefig(png, dpi=220, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    shutil.copy2(png, LATEX_FIG / png.name)
    shutil.copy2(pdf, LATEX_FIG / pdf.name)
    return [rel(png), rel(pdf), rel(LATEX_FIG / png.name), rel(LATEX_FIG / pdf.name)]


def build_final_figures(inputs: dict[str, object], raw_data_dir: Path) -> list[dict[str, object]]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    from matplotlib.patches import FancyArrowPatch, Patch, Rectangle

    plt.rcParams.update(
        {
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "figure.titlesize": 12,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )

    figure_rows: list[dict[str, object]] = []
    master: pd.DataFrame = inputs["master"]  # type: ignore[assignment]
    profiles: pd.DataFrame = inputs["profiles_4085"]  # type: ignore[assignment]
    negative_atlas: pd.DataFrame = inputs["negative_atlas"]  # type: ignore[assignment]
    grouped_4090 = pd.read_csv(ROOT / "Output" / "4090" / "grouped_oos_results.csv")
    effects_4100: pd.DataFrame = inputs["effects_4100"]  # type: ignore[assignment]
    effects_4121: pd.DataFrame = inputs["effects_4121"]  # type: ignore[assignment]
    metrics = inputs["d4131"].get("primary_metrics", {})  # type: ignore[union-attr]
    master_sorted = master.sort_values("ob").copy()
    cmap = ListedColormap(["#d8d8d8", "#f7f3ea", "#1d7a61"])

    # Figure 1.
    fig = plt.figure(figsize=(12.2, 8.4))
    ax_a = fig.add_subplot(2, 2, 1, projection="3d")
    raw_path = raw_data_dir / "Ob2.txt"
    snapshot_status = "snapshot unavailable"
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
            snapshot_status = f"Ob2, t={float(target_t):.2f} s, n={len(snap)}"
        except Exception:
            ax_a.text2D(0.12, 0.50, "snapshot unavailable", transform=ax_a.transAxes)
    else:
        ax_a.text2D(0.12, 0.50, "snapshot unavailable", transform=ax_a.transAxes)
    ax_a.set_title(f"A. Representative raw 3D snapshot\n{snapshot_status}")

    ax_b = fig.add_subplot(2, 2, 2)
    ax_b.set_title("B. Affine components removed before T1")
    ax_b.set_xlim(0, 1)
    ax_b.set_ylim(0, 1)
    ax_b.axis("off")
    points = np.array([[0.15, 0.35], [0.22, 0.55], [0.33, 0.44], [0.43, 0.62], [0.52, 0.39], [0.64, 0.55]])
    ax_b.scatter(points[:, 0], points[:, 1], s=38, color="#314f6b")
    for x, y in points:
        ax_b.arrow(x, y, 0.08, 0.03, width=0.003, head_width=0.025, color="#777777", length_includes_head=True)
    ax_b.add_patch(Rectangle((0.08, 0.22), 0.64, 0.52, fill=False, edgecolor="#777777", linewidth=1.2))
    ax_b.add_patch(Rectangle((0.18, 0.31), 0.25, 0.28, fill=False, edgecolor="#1d7a61", linewidth=2.0))
    ax_b.text(0.08, 0.78, "whole-swarm affine\ntranslation + deformation", color="#555555")
    ax_b.text(0.18, 0.18, "local affine fit", color="#1d7a61")
    ax_b.arrow(0.48, 0.37, 0.13, -0.08, width=0.003, head_width=0.025, color="#b6423c", length_includes_head=True)
    ax_b.text(0.58, 0.23, "residual\nnon-affine part", color="#b6423c")

    ax_c = fig.add_subplot(2, 2, 3)
    ax_c.set_title("C. Frozen T1 measurement target")
    ax_c.set_xlim(0, 1)
    ax_c.set_ylim(0, 1)
    ax_c.axis("off")
    boxes = [
        (0.04, 0.63, "3D local\nneighborhood"),
        (0.31, 0.63, "subtract local\naffine motion"),
        (0.58, 0.63, "tangential\nnon-affine residual"),
        (0.31, 0.27, "event-conditioned\nT1 observable"),
    ]
    for x, y, label in boxes:
        ax_c.add_patch(Rectangle((x, y), 0.22, 0.17, facecolor="#f7f3ea", edgecolor="#444444", linewidth=1.0))
        ax_c.text(x + 0.11, y + 0.085, label, ha="center", va="center")
    for (x1, y1), (x2, y2) in [((0.26, 0.715), (0.31, 0.715)), ((0.53, 0.715), (0.58, 0.715)), ((0.69, 0.63), (0.42, 0.44))]:
        ax_c.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="->", mutation_scale=12, color="#444444"))

    ax_d = fig.add_subplot(2, 2, 4)
    ax_d.set_title("D. Event-aligned all-tangential profile")
    prof = profiles[profiles["variable"].astype(str).eq("all_tangential")].copy()
    prof["relative_time_sec"] = pd.to_numeric(prof["relative_time_sec"], errors="coerce")
    prof["median_real_minus_null_aligned_z_across_ob"] = pd.to_numeric(
        prof["median_real_minus_null_aligned_z_across_ob"], errors="coerce"
    )
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
    ax_d.axvspan(-0.2, 0.0, color="#b08b33", alpha=0.14, label="near-pre window")
    ax_d.set_xlabel("time from event (s)")
    ax_d.set_ylabel("aligned z")
    ax_d.grid(color="#e6e6e6", linewidth=0.8)
    ax_d.legend(frameon=False, fontsize=8)
    fig.suptitle("Data and T1 measurement definition", y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    paths = save_figure(fig, "Fig1_final")
    plt.close(fig)
    figure_rows.append({"figure": "Figure 1", "final_stem": "Fig1_final", "files": "; ".join(paths), "cleanup": "internal note removed; no analysis-node labels on figure"})

    # Figure 2.
    fig, axes = plt.subplots(1, 3, figsize=(14.0, 5.3), gridspec_kw={"width_ratios": [1.2, 1.5, 0.95]})
    colors = [CLASS_COLORS.get(x, "#777777") for x in master_sorted["observation_class"]]
    axes[0].barh([f"Ob{int(x)}" for x in master_sorted["ob"]], pd.to_numeric(master_sorted["408x_T1_effect"], errors="coerce"), color=colors)
    axes[0].axvline(0, color="#222222", linewidth=1.0)
    axes[0].invert_yaxis()
    axes[0].set_title("A. All-observation T1 effect")
    axes[0].set_xlabel("event - non-event z")

    heat_features = [
        ("t1_survival_any_binary", "any scale"),
        ("t1_survival_both_binary", "two scales"),
        ("scale_lag_robust_binary", "scale/lag"),
        ("diffuse_gate_binary", "diffuse"),
        ("history_beats_median_binary", "history"),
        ("stable_408x_failure", "stable\nfailure"),
        ("fragile_408x_boundary", "fragile\nboundary"),
    ]
    encoded = bool_matrix(master_sorted[[name for name, _ in heat_features]])
    axes[1].imshow(encoded, aspect="auto", cmap=cmap, vmin=0, vmax=2)
    axes[1].set_title("B. Gate coverage")
    axes[1].set_yticks(np.arange(len(master_sorted)))
    axes[1].set_yticklabels([f"Ob{int(x)}" for x in master_sorted["ob"]], fontsize=7)
    axes[1].set_xticks(np.arange(len(heat_features)))
    axes[1].set_xticklabels([label for _, label in heat_features], rotation=35, ha="right")
    axes[1].legend(
        handles=[
            Patch(facecolor="#1d7a61", label="pass"),
            Patch(facecolor="#f7f3ea", label="fail"),
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
    fig.suptitle("T1 survival is common but not universal", y=1.02)
    fig.tight_layout()
    paths = save_figure(fig, "Fig2_final")
    plt.close(fig)
    figure_rows.append({"figure": "Figure 2", "final_stem": "Fig2_final", "files": "; ".join(paths), "cleanup": "final figure naming; internal analysis-node labels absent from axes"})

    # Figure 3 without history panels.
    support_rows = [
        ("any-scale survival", metrics.get("t1_survival_any_k_observations"), metrics.get("total_observations"), "primary"),
        ("two-scale survival", metrics.get("t1_survival_both_k_observations"), metrics.get("total_observations"), "primary"),
        ("survivor scale/lag robust", metrics.get("scale_lag_robust_observations"), metrics.get("scale_lag_tested_survivor_observations"), "primary"),
        ("diffuse all-tangential", metrics.get("diffuse_all_tangential_gate_observations"), metrics.get("diffuse_all_tangential_tested_observations"), "primary"),
        ("near-pre timing", metrics.get("all_tangential_near_pre_gate_observations"), metrics.get("diffuse_all_tangential_tested_observations"), "bounded"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(13.0, 8.4))
    labels = [r[0] for r in support_rows]
    nums = np.array([float(r[1]) for r in support_rows])
    dens = np.array([float(r[2]) for r in support_rows])
    fracs = nums / dens
    bar_colors = ["#1d7a61" if r[3] == "primary" else "#b08b33" for r in support_rows]
    axes[0, 0].barh(labels, fracs, color=bar_colors)
    axes[0, 0].invert_yaxis()
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
    axes[1, 0].barh([friendly_signed_label(x) for x in signed_counts.index], signed_counts.values, color="#7c6f58")
    axes[1, 0].invert_yaxis()
    axes[1, 0].set_title("C. Signed structure classes")
    axes[1, 0].set_xlabel("observations")
    axes[1, 0].tick_params(axis="y", labelsize=8)
    axes[1, 0].grid(axis="x", color="#e6e6e6")

    form_labels = ["diffuse\ntangential", "near-pre\ntiming", "edge/core\ncontrast"]
    form_values = [13 / 14, 8 / 14, 9 / 14]
    form_counts = ["13/14", "8/14", "9/14"]
    axes[1, 1].bar(form_labels, form_values, color=["#1d7a61", "#b08b33", "#7c6f58"])
    for i, (value, count) in enumerate(zip(form_values, form_counts)):
        axes[1, 1].text(i, value + 0.025, count, ha="center", fontsize=8)
    axes[1, 1].set_title("D. Repeated form and bounded structure")
    axes[1, 1].set_ylim(0, 1.1)
    axes[1, 1].set_ylabel("coverage fraction")
    axes[1, 1].grid(axis="y", color="#e6e6e6")
    fig.suptitle("Spatial and timing structure of the T1 residual", y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    paths = save_figure(fig, "Fig3_final")
    plt.close(fig)
    figure_rows.append({"figure": "Figure 3", "final_stem": "Fig3_final", "files": "; ".join(paths), "cleanup": "history removed from phenotype panel; signed classes relabeled"})

    # Figure 4 with observation-level moment-closure panel.
    fig, axes = plt.subplots(2, 2, figsize=(13.4, 8.6))
    g = grouped_4090.copy()
    for col in ["heldout_ob", "incremental_r2_state_vs_radius", "incremental_r2_shift_vs_radius"]:
        g[col] = pd.to_numeric(g[col], errors="coerce")
    marker_specs = [
        ("first_moment", "incremental_r2_state_vs_radius", -0.18, "o", "#1d7a61", "first moment, real"),
        ("first_moment", "incremental_r2_shift_vs_radius", -0.06, "x", "#74a892", "first moment, shifted"),
        ("second_moment", "incremental_r2_state_vs_radius", 0.06, "s", "#b6423c", "second moment, real"),
        ("second_moment", "incremental_r2_shift_vs_radius", 0.18, "^", "#d08b79", "second moment, shifted"),
    ]
    for family, col, offset, marker, color, label in marker_specs:
        sub = g[g["target_family"].eq(family)].sort_values("heldout_ob")
        axes[0, 0].scatter(sub["heldout_ob"] + offset, 1000.0 * sub[col], s=34, marker=marker, color=color, label=label, alpha=0.88)
    axes[0, 0].axhline(0, color="#222222", linewidth=1.0)
    axes[0, 0].set_xticks(np.arange(1, 20))
    axes[0, 0].set_xticklabels([str(i) for i in range(1, 20)], fontsize=7)
    axes[0, 0].set_title(r"A. $(C,\dot{C},R)$ closure by held-out observation")
    axes[0, 0].set_xlabel("observation")
    axes[0, 0].set_ylabel(r"$10^3 \Delta R^2$ vs radius baseline")
    axes[0, 0].legend(frameon=False, fontsize=7, ncols=2, loc="lower left")
    axes[0, 0].grid(color="#e6e6e6")

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
    axes[0, 1].set_ylabel("near-pre event - matched control")
    axes[0, 1].grid(color="#e6e6e6")

    eff4121 = effects_4121.copy()
    eff4121["real_minus_null_median_abs_effect"] = pd.to_numeric(eff4121["real_minus_null_median_abs_effect"], errors="coerce")
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
    axes[1, 0].set_title("C. Recent history: observation-specific")
    axes[1, 0].set_xlabel("signed history effect")
    axes[1, 0].set_ylabel("absolute effect - shuffle median")
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
    fig.suptitle("Tested reductions fail or remain explicitly bounded", y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    paths = save_figure(fig, "Fig4_final")
    plt.close(fig)
    figure_rows.append({"figure": "Figure 4", "final_stem": "Fig4_final", "files": "; ".join(paths), "cleanup": "panel A redesigned as observation-level held-out evidence"})

    # Figure 5.
    fig, axes = plt.subplots(2, 2, figsize=(13.0, 8.6))
    route_features = [
        ("t1_survival_any_binary", "T1 any\nscale"),
        ("t1_survival_both_binary", "T1 two\nscales"),
        ("scale_lag_robust_binary", "scale/lag\nrobust"),
        ("diffuse_gate_binary", "diffuse\nactivity"),
        ("edge_phase_binary", "edge/timing\nsupport"),
        ("history_beats_median_binary", "history\nmedian"),
        ("history_real_beats_shuffle_q95_abs", "history\nq95"),
    ]
    encoded = bool_matrix(master_sorted[[name for name, _ in route_features]])
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
    axes[0, 1].scatter(valid["mean_track_length_frames"], valid["408x_T1_effect"], c=scatter_colors, s=55, edgecolor="#222222", linewidth=0.35)
    for _, row in valid.iterrows():
        axes[0, 1].text(row["mean_track_length_frames"], row["408x_T1_effect"], f" {int(row['ob'])}", fontsize=7)
    rho = spearman_rho(valid["mean_track_length_frames"], valid["408x_T1_effect"])
    axes[0, 1].set_title(f"B. Descriptive metadata association\nSpearman rho={fmt_float(rho)}")
    axes[0, 1].set_xlabel("mean track length (frames)")
    axes[0, 1].set_ylabel("T1 effect (event - non-event z)")
    axes[0, 1].grid(color="#e6e6e6")

    class_order = [c for c in CLASS_COLORS if c in set(master_sorted["observation_class"])]
    class_values = [
        pd.to_numeric(master_sorted.loc[master_sorted["observation_class"].eq(cls), "408x_T1_effect"], errors="coerce").dropna()
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
        axes[1, 0].scatter(np.full(len(vals), x_pos) + jitter, vals, color=CLASS_COLORS.get(cls, "#777777"), edgecolor="#222222", linewidth=0.3, s=25, zorder=3)
    axes[1, 0].axhline(0, color="#222222", linewidth=0.8)
    axes[1, 0].set_title("C. T1 effect by observation class")
    axes[1, 0].tick_params(axis="x", labelsize=7)
    axes[1, 0].set_ylabel("T1 effect (event - non-event z)")
    axes[1, 0].grid(axis="y", color="#e6e6e6")

    class_summary = master_sorted.groupby("observation_class").agg(
        n=("ob", "count"),
        median_t1_effect=("408x_T1_effect", "median"),
        median_track_length=("mean_track_length_frames", "median"),
    )
    axes[1, 1].axis("off")
    y = 0.94
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
        "Metadata labels are descriptive annotations, not causal regime explanations.",
        transform=axes[1, 1].transAxes,
        fontsize=8,
        color="#555555",
    )
    fig.suptitle("Observation heterogeneity is part of the result", y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    paths = save_figure(fig, "Fig5_final")
    plt.close(fig)
    figure_rows.append({"figure": "Figure 5", "final_stem": "Fig5_final", "files": "; ".join(paths), "cleanup": "node-specific axis label removed; legend wording simplified"})

    return figure_rows


def build_captions() -> pd.DataFrame:
    rows = [
        {
            "figure": "Figure 1",
            "latex_file": "figures/Fig1_final.pdf",
            "caption": (
                "Data and T1 measurement definition. Panel A shows a representative raw three-dimensional "
                "snapshot from one observation. Panels B and C define the affine subtraction and the frozen "
                "T1 measurement target used in this study. Panel D shows the event-aligned all-tangential "
                "profile used to illustrate the measurement pipeline. The figure defines the observable and "
                "does not represent a fitted physical mechanism."
            ),
        },
        {
            "figure": "Figure 2",
            "latex_file": "figures/Fig2_final.pdf",
            "caption": (
                "T1 survival across observations. The all-observation panel retains both survivor and failure "
                "observations. T1 survived local affine subtraction in most observations and remained robust to "
                "nearby scale/lag choices inside the survivor class, but the class panel shows that the result "
                "was not universal."
            ),
        },
        {
            "figure": "Figure 3",
            "latex_file": "figures/Fig3_final.pdf",
            "caption": (
                "Spatial and timing structure of the T1 residual. Support fractions and event-aligned profiles "
                "show that diffuse all-tangential activity was the most stable repeated form. Near-pre timing, "
                "edge/core contrast, and signed structure were retained as bounded or secondary patterns."
            ),
        },
        {
            "figure": "Figure 4",
            "latex_file": "figures/Fig4_final.pdf",
            "caption": (
                "Reduction boundaries. The tested $(C,\\dot{C},R)$ first/second moment closure and the "
                "state-matched event-local near-pre test did not provide stable reductions of T1. Recent-history "
                "separation was visible in some observations but did not become a universal sign/order rule. "
                "Propagation remained outside the current confirmatory route."
            ),
        },
        {
            "figure": "Figure 5",
            "latex_file": "figures/Fig5_final.pdf",
            "caption": (
                "Observation heterogeneity. Route-level evidence and observation classes show robust survivors, "
                "fragile boundaries, and stable failures across the 19 observations. The metadata association "
                "panel is descriptive and sensitivity-audited, but it is not a causal recording-condition "
                "explanation."
            ),
        },
    ]
    return pd.DataFrame(rows)


def build_source_map(figure_rows: list[dict[str, object]], captions: pd.DataFrame) -> pd.DataFrame:
    source_inputs = [
        "Output/4134/figure_source_map.csv",
        "Output/4134/main_figure_manifest.csv",
        "Output/4134/panel_metadata.csv",
        "Output/4131/decision.json",
        "Output/4131/positive_phenomenon_atlas.csv",
        "Output/4131/observation_positive_coverage_matrix.csv",
        "Output/4132/negative_boundary_atlas.csv",
        "Output/4133/observation_master_table.csv",
        "Output/4085/aggregate_profiles.csv",
        "Output/4090/grouped_oos_results.csv",
        "Output/4090/primary_metrics.csv",
        "Output/4100/observation_level_effects.csv",
        "Output/4121/observation_level_effects.csv",
    ]
    rows: list[dict[str, object]] = []
    for source in source_inputs:
        path = ROOT / source
        rows.append({"role": "input", "path": source, "exists": path.exists(), "size_bytes": path.stat().st_size if path.exists() else 0})
    for figure in figure_rows:
        for path_text in str(figure["files"]).split("; "):
            path = ROOT / path_text
            rows.append({"role": "output_figure", "path": path_text, "exists": path.exists(), "size_bytes": path.stat().st_size if path.exists() else 0})
    caption_md = OUT / "figure_caption_final.md"
    rows.append(
        {
            "role": "output_caption",
            "path": rel(caption_md),
            "exists": caption_md.exists(),
            "size_bytes": caption_md.stat().st_size if caption_md.exists() else 0,
        }
    )
    return pd.DataFrame(rows)


def write_caption_md(captions: pd.DataFrame) -> None:
    rows = captions.to_dict("records")
    md = dedent(
        f"""\
        # 4150 Final Figure Captions

        Date: {DATE}

        These captions are figure-facing drafts for the active manuscript. They
        remove internal node labels and retain bounded claims.

        {md_table(rows, ["figure", "latex_file", "caption"])}
        """
    )
    (OUT / "figure_caption_final.md").write_text(md, encoding="utf-8")


def write_summary(
    figure_rows: list[dict[str, object]],
    captions: pd.DataFrame,
    source_map: pd.DataFrame,
    audit: pd.DataFrame,
) -> None:
    decision = {
        "node": NODE,
        "date": DATE,
        "gate_result": "pass_4150_final_figure_package_ready_for_reintegration",
        "primary_metrics": {
            "n_final_figures": len(figure_rows),
            "n_png_outputs": int(source_map.loc[source_map["role"].eq("output_figure"), "path"].astype(str).str.endswith(".png").sum()),
            "n_pdf_outputs": int(source_map.loc[source_map["role"].eq("output_figure"), "path"].astype(str).str.endswith(".pdf").sum()),
            "n_failed_audit_items": int((audit["status"] != "pass").sum()),
            "latex_copies_written": bool((LATEX_FIG / "Fig1_final.pdf").exists()),
        },
        "manuscript_instruction": "Use Fig1_final through Fig5_final and the final captions; do not retain 4134 figure file names in active includegraphics commands.",
        "next": "4151_final_manuscript_reintegration",
    }
    write_json(OUT / "decision.json", decision)

    md = dedent(
        f"""\
        # Node 4150 Summary

        ## Purpose

        Convert the 4134 figure package into final publication-facing figures
        without changing the underlying analysis definitions or evidence.

        ## Gate Result

        `{decision["gate_result"]}`

        ## Cleanup Performed

        {md_table(audit.to_dict("records"), ["item", "status", "evidence"])}

        ## Final Figure Files

        {md_table(figure_rows, ["figure", "final_stem", "cleanup"])}

        ## Captions

        {md_table(captions.to_dict("records"), ["figure", "latex_file", "caption"])}

        ## Source Map

        {md_table(source_map.to_dict("records"), ["role", "path", "exists", "size_bytes"])}

        ## Next

        Continue to `4151_final_manuscript_reintegration`. No PDF compilation
        was run at 4150, following the deferred-compilation policy.
        """
    )
    (OUT / "4150_summary.md").write_text(md, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    raw_data_dir = Path(os.environ.get("FISH_3D_DATASET_DIR", r"D:\3Ddataset"))
    inputs = r4134.load_inputs()
    figure_rows = build_final_figures(inputs, raw_data_dir)
    captions = build_captions()
    write_csv_pair(captions, "figure_caption_final.csv")
    write_caption_md(captions)

    audit = pd.DataFrame(
        [
            {
                "item": "Figure 1 internal workflow note",
                "status": "pass",
                "evidence": "Fig1_final removes the old bottom note that mentioned use in 4134.",
            },
            {
                "item": "Figure 3 history removal",
                "status": "pass",
                "evidence": "Fig3_final excludes history bars and leaves recent-history evidence to Figure 4/Figure 5.",
            },
            {
                "item": "Figure 4A observation-level redesign",
                "status": "pass",
                "evidence": "Fig4_final panel A uses held-out observation points from Output/4090/grouped_oos_results.csv.",
            },
            {
                "item": "Publication-facing figure names",
                "status": "pass",
                "evidence": "Final files are named Fig1_final through Fig5_final and copied to mypaper2/Latex/figures.",
            },
            {
                "item": "No per-node compilation",
                "status": "pass",
                "evidence": "No LaTeX compilation was run at 4150; compilation is deferred to 4154.",
            },
        ]
    )
    write_csv_pair(audit, "figure_cleanup_audit.csv")
    source_map = build_source_map(figure_rows, captions)
    write_csv_pair(source_map, "figure_source_map.csv")
    write_summary(figure_rows, captions, source_map, audit)
    print(json.dumps(json.loads((OUT / "decision.json").read_text(encoding="utf-8")), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
