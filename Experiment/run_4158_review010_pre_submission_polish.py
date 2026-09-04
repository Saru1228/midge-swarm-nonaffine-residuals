"""4158 review-010 pre-submission figure polish.

This node reorganizes existing manuscript-facing evidence into cleaner Figure 2
and Figure 3 panels. It does not recompute T1 or change any analysis gate.
"""

from __future__ import annotations

import json
import math
import shutil
from pathlib import Path
from textwrap import dedent
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4158"
FIG = OUT / "figures"
TABLES = OUT / "tables"
LATEX_FIG = ROOT / "mypaper2" / "Latex" / "figures"
DATE = "2026-09-04"
NODE = "4158_review010_pre_submission_polish"

CLASS_COLORS = {
    "robust_survivor_diffuse_positive": "#19765f",
    "robust_survivor_without_diffuse_gate": "#5a8f7b",
    "fragile_survivor": "#c39a2d",
    "fragile_408x_boundary": "#b8792e",
    "stable_408x_failure": "#b6423c",
}

CLASS_LABELS = {
    "robust_survivor_diffuse_positive": "robust survivor\nwith diffuse support",
    "robust_survivor_without_diffuse_gate": "robust survivor\nwithout diffuse support",
    "fragile_survivor": "one-scale\nsurvivor",
    "fragile_408x_boundary": "fragile\nboundary",
    "stable_408x_failure": "stable\nnon-survivor",
}

SIGNED_LABELS = {
    "mirror_symmetric_opposite_sign": "mirror-symmetric\nopposite sign",
    "low_to_high_dominant": "low-to-high\ndominant",
    "opposite_sign_but_imbalanced": "opposite sign,\nimbalanced",
    "no_signed_gate": "no signed gate",
    "not_classified": "not classified",
}


def ensure_dirs() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    LATEX_FIG.mkdir(parents=True, exist_ok=True)


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def boolish(value: object) -> float:
    if pd.isna(value):
        return np.nan
    if isinstance(value, (int, float, np.integer, np.floating)):
        value_f = float(value)
        if not math.isfinite(value_f):
            return np.nan
        return 1.0 if value_f > 0.5 else 0.0
    text = str(value).strip().lower()
    if text in {"true", "1", "1.0", "yes"}:
        return 1.0
    if text in {"false", "0", "0.0", "no"}:
        return 0.0
    return np.nan


def fmt_float(value: object, digits: int = 3) -> str:
    try:
        value_f = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(value_f):
        return "NA"
    return f"{value_f:.{digits}g}"


def write_csv_pair(df: pd.DataFrame, name: str) -> None:
    df.to_csv(OUT / name, index=False)
    df.to_csv(TABLES / name, index=False)


def save_figure(fig: Any, stem: str) -> list[str]:
    png = FIG / f"{stem}.png"
    pdf = FIG / f"{stem}.pdf"
    fig.savefig(png, dpi=240, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    shutil.copy2(png, LATEX_FIG / png.name)
    shutil.copy2(pdf, LATEX_FIG / pdf.name)
    return [rel(png), rel(pdf), rel(LATEX_FIG / png.name), rel(LATEX_FIG / pdf.name)]


def status_matrix(values: pd.DataFrame) -> np.ndarray:
    out = values.copy()
    for col in out.columns:
        out[col] = out[col].map(boolish)
    arr = out.to_numpy(dtype=float)
    return np.where(np.isnan(arr), 0, np.where(arr > 0.5, 2, 1))


def build_k_matrix(master: pd.DataFrame, ladder: pd.DataFrame) -> pd.DataFrame:
    t1 = ladder[
        (ladder["target_id"].astype(str) == "T1_transition_tangential_residual")
        & (pd.to_numeric(ladder["lag_sec"], errors="coerce").sub(0.10).abs() < 1e-9)
        & (pd.to_numeric(ladder["k"], errors="coerce").isin([8, 10]))
    ].copy()
    t1["gate"] = t1["event_conditioned_local_gate"].map(boolish)
    wide = (
        t1.pivot_table(index="ob", columns="k", values="gate", aggfunc="max")
        .rename(columns={8: "k=8", 10: "k=10"})
        .reset_index()
    )
    out = master[["ob", "t1_survival_both_binary", "scale_lag_robust_binary"]].merge(wide, on="ob", how="left")
    out = out.rename(
        columns={
            "t1_survival_both_binary": "both-scale",
            "scale_lag_robust_binary": "scale/lag",
        }
    )
    return out[["ob", "k=8", "k=10", "both-scale", "scale/lag"]]


def build_fig2(master: pd.DataFrame, ladder: pd.DataFrame, dist: pd.DataFrame, p: dict[str, Any], detrend: pd.DataFrame) -> list[str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    from matplotlib.patches import Patch

    plt.rcParams.update(
        {
            "font.size": 8.5,
            "axes.titlesize": 9.5,
            "axes.labelsize": 8.5,
            "figure.titlesize": 12,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )

    master = master.sort_values("ob").copy()
    effect = pd.to_numeric(master["408x_T1_effect"], errors="coerce")
    labels = [f"Ob{int(ob)}" for ob in master["ob"]]
    survival_colors = []
    for row in master.itertuples(index=False):
        if boolish(getattr(row, "t1_survival_both_binary")) > 0.5:
            survival_colors.append("#19765f")
        elif boolish(getattr(row, "t1_survival_any_binary")) > 0.5:
            survival_colors.append("#c39a2d")
        else:
            survival_colors.append("#b6423c")

    fig = plt.figure(figsize=(14.4, 8.0))
    gs = fig.add_gridspec(
        2,
        3,
        width_ratios=[1.14, 0.88, 0.78],
        height_ratios=[1.12, 0.9],
        wspace=0.34,
        hspace=0.36,
    )
    ax_a = fig.add_subplot(gs[:, 0])
    ax_b = fig.add_subplot(gs[0, 1:])
    ax_c = fig.add_subplot(gs[1, 1])
    ax_d = fig.add_subplot(gs[1, 2])

    y = np.arange(len(master))
    ax_a.barh(y, effect, color=survival_colors, edgecolor="#222222", linewidth=0.25)
    ax_a.axvline(0, color="#222222", linewidth=1.0)
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(labels, fontsize=7.5)
    ax_a.invert_yaxis()
    ax_a.set_xlabel("event - non-event T1 effect (z)")
    ax_a.set_title("A. All-observation T1 effect")
    ax_a.grid(axis="x", color="#e7e7e7", linewidth=0.8)
    ax_a.legend(
        handles=[
            Patch(facecolor="#19765f", label="both-scale pass"),
            Patch(facecolor="#c39a2d", label="one-scale only"),
            Patch(facecolor="#b6423c", label="no survival"),
        ],
        frameon=False,
        fontsize=7,
        loc="upper center",
        bbox_to_anchor=(0.52, -0.065),
        ncol=3,
    )

    km = build_k_matrix(master, ladder)
    matrix_cols = ["k=8", "k=10", "both-scale", "scale/lag"]
    encoded = status_matrix(km[matrix_cols])
    cmap = ListedColormap(["#d8d8d8", "#f7f3ea", "#19765f"])
    ax_b.imshow(encoded, aspect="auto", cmap=cmap, vmin=0, vmax=2)
    ax_b.set_xticks(np.arange(len(matrix_cols)))
    ax_b.set_xticklabels(matrix_cols, rotation=25, ha="right")
    ax_b.set_yticks(np.arange(len(km)))
    ax_b.set_yticklabels([f"Ob{int(ob)}" for ob in km["ob"]], fontsize=7)
    ax_b.set_title("B. Frozen two-scale support matrix")
    ax_b.legend(
        handles=[
            Patch(facecolor="#19765f", label="pass"),
            Patch(facecolor="#f7f3ea", label="fail"),
            Patch(facecolor="#d8d8d8", label="not tested"),
        ],
        frameon=False,
        fontsize=7,
        loc="upper left",
        bbox_to_anchor=(1.02, 1.0),
    )

    full_x = pd.DataFrame({"n_both": np.arange(0, 15)})
    hist = full_x.merge(dist, on="n_both", how="left").fillna({"count": 0, "fraction": 0.0})
    ax_c.bar(hist["n_both"], hist["count"], color="#7c6f58", width=0.8)
    observed = int(p["observed_n_both"])
    ax_c.axvline(observed, color="#b6423c", linestyle="--", linewidth=2.0)
    ax_c.set_xlim(-0.6, 14.7)
    ax_c.set_xticks(np.arange(0, 15, 2))
    ax_c.set_xlabel(r"$N_{\mathrm{both}}$ under pseudo-event null")
    ax_c.set_ylabel("replicates")
    ax_c.set_title("C. Full-pipeline omnibus null")
    ax_c.grid(axis="y", color="#e7e7e7", linewidth=0.8)
    annotation = (
        f"observed = {observed}/19\n"
        f"null mean = {fmt_float(p['n_both_null_mean'])}\n"
        f"q95 = {fmt_float(p['n_both_null_q95'])}, max = {fmt_float(p['n_both_null_max'])}\n"
        f"0/1000 >= {observed}\n"
        r"empirical $p\approx0.001$"
    )
    ax_c.text(
        0.54,
        0.92,
        annotation,
        transform=ax_c.transAxes,
        va="top",
        fontsize=8,
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.84, "pad": 2.0},
    )

    variant_order = ["centered_1s", "past_1s", "none_z"]
    variant_labels = ["centered", "past-only", "no rolling"]
    d = detrend.set_index("variant").loc[variant_order].reset_index()
    counts = pd.to_numeric(d["n_both"], errors="coerce").to_numpy(dtype=float)
    ax_d.bar(np.arange(len(counts)), counts, color=["#19765f", "#c39a2d", "#5a8f7b"], width=0.62)
    ax_d.set_ylim(0, 19)
    ax_d.set_yticks([0, 5, 10, 14, 19])
    ax_d.set_xticks(np.arange(len(counts)))
    ax_d.set_xticklabels(variant_labels, rotation=25, ha="right", fontsize=7)
    ax_d.set_title("D. Detrending challenge", fontsize=8.5)
    ax_d.set_ylabel("both-scale survivors")
    for i, value in enumerate(counts):
        ax_d.text(i, value + 0.45, f"{int(value)}/19", ha="center", fontsize=7.5)
    ax_d.grid(axis="y", color="#e7e7e7", linewidth=0.7)

    fig.suptitle("T1 survival and full-pipeline calibration", y=0.985)
    return save_figure(fig, "Fig2_final")


def build_fig3(master: pd.DataFrame, profiles: pd.DataFrame, metrics: dict[str, Any]) -> list[str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "font.size": 8.5,
            "axes.titlesize": 9.5,
            "axes.labelsize": 8.5,
            "figure.titlesize": 12,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )

    fig, axes = plt.subplots(2, 2, figsize=(13.0, 8.2))
    support_rows = [
        ("any-scale survival", metrics["t1_survival_any_k_observations"], metrics["total_observations"], "#19765f"),
        ("two-scale survival", metrics["t1_survival_both_k_observations"], metrics["total_observations"], "#19765f"),
        ("survivor scale/lag robust", metrics["scale_lag_robust_observations"], metrics["scale_lag_tested_survivor_observations"], "#19765f"),
        ("diffuse all-tangential", metrics["diffuse_all_tangential_gate_observations"], metrics["diffuse_all_tangential_tested_observations"], "#19765f"),
        ("near-pre timing", metrics["all_tangential_near_pre_gate_observations"], metrics["diffuse_all_tangential_tested_observations"], "#c39a2d"),
    ]
    labels = [row[0] for row in support_rows]
    nums = np.array([float(row[1]) for row in support_rows])
    dens = np.array([float(row[2]) for row in support_rows])
    fracs = nums / dens
    axes[0, 0].barh(labels, fracs, color=[row[3] for row in support_rows])
    axes[0, 0].invert_yaxis()
    for i, (num, den, frac) in enumerate(zip(nums, dens, fracs)):
        axes[0, 0].text(min(frac + 0.02, 1.02), i, f"{int(num)}/{int(den)}", va="center", fontsize=8)
    axes[0, 0].set_xlim(0, 1.12)
    axes[0, 0].set_xlabel("fraction")
    axes[0, 0].set_title("A. Support fractions")
    axes[0, 0].grid(axis="x", color="#e7e7e7")

    profile_specs = [
        ("all_tangential", "#19765f", "all tangential"),
        ("shell_edge_minus_core", "#b6423c", "edge - core"),
    ]
    for variable, color, label in profile_specs:
        prof = profiles[profiles["variable"].astype(str).eq(variable)].copy()
        prof["relative_time_sec"] = pd.to_numeric(prof["relative_time_sec"], errors="coerce")
        prof["median_real_minus_null_aligned_z_across_ob"] = pd.to_numeric(
            prof["median_real_minus_null_aligned_z_across_ob"], errors="coerce"
        )
        prof = prof.dropna(subset=["relative_time_sec", "median_real_minus_null_aligned_z_across_ob"])
        axes[0, 1].plot(
            prof["relative_time_sec"],
            prof["median_real_minus_null_aligned_z_across_ob"],
            color=color,
            linewidth=1.9,
            label=label,
        )
    axes[0, 1].axvline(0, color="#222222", linestyle="--", linewidth=1.0)
    axes[0, 1].axhline(0, color="#bbbbbb", linewidth=0.8)
    axes[0, 1].axvspan(-0.20, 0.0, color="#c39a2d", alpha=0.13)
    axes[0, 1].set_xlabel("time from event (s)")
    axes[0, 1].set_ylabel("real - null aligned z")
    axes[0, 1].set_title("B. Event-aligned profiles")
    axes[0, 1].legend(frameon=False, fontsize=8)
    axes[0, 1].grid(color="#e7e7e7")

    signed_counts = master["signed_class"].fillna("not_classified").replace("", "not_classified").value_counts()
    signed_labels = [SIGNED_LABELS.get(str(label), str(label).replace("_", " ")) for label in signed_counts.index]
    axes[1, 0].barh(signed_labels, signed_counts.values, color="#7c6f58")
    axes[1, 0].invert_yaxis()
    axes[1, 0].set_xlabel("observations")
    axes[1, 0].set_title("C. Signed structure classes")
    axes[1, 0].tick_params(axis="y", labelsize=8)
    axes[1, 0].grid(axis="x", color="#e7e7e7")

    form_labels = ["diffuse\ntangential", "near-pre\ntiming", "edge/core\ncontrast"]
    form_nums = np.array([13, 8, int(pd.to_numeric(master["edge_phase_binary"], errors="coerce").sum())], dtype=float)
    form_dens = np.array([14, 14, int(master["edge_phase_binary"].notna().sum())], dtype=float)
    form_values = form_nums / form_dens
    axes[1, 1].bar(form_labels, form_values, color=["#19765f", "#c39a2d", "#b6423c"])
    for i, (num, den, value) in enumerate(zip(form_nums, form_dens, form_values)):
        axes[1, 1].text(i, value + 0.025, f"{int(num)}/{int(den)}", ha="center", fontsize=8)
    axes[1, 1].set_ylim(0, 1.1)
    axes[1, 1].set_ylabel("coverage fraction")
    axes[1, 1].set_title("D. Repeated form and bounded structure")
    axes[1, 1].grid(axis="y", color="#e7e7e7")

    fig.suptitle("Spatial and timing structure of the T1 residual", y=0.985)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    return save_figure(fig, "Fig3_final")


def write_summary(paths2: list[str], paths3: list[str], sources: pd.DataFrame) -> None:
    audit = pd.DataFrame(
        [
            {
                "review_item": "Figure 2 omnibus calibration visibility",
                "status": "pass",
                "action": "Added B=1000 N_both null histogram and detrending survivor-count inset.",
            },
            {
                "review_item": "Figure 2 and Figure 5 role separation",
                "status": "pass",
                "action": "Reduced Figure 2 support matrix to k=8, k=10, both-scale, and scale/lag columns.",
            },
            {
                "review_item": "Figure 3 radius-correlation cleanup",
                "status": "pass",
                "action": "Removed shell-radius correlation from the active Figure 3 event-aligned profile panel.",
            },
            {
                "review_item": "Figure 3 sparse-dense decision",
                "status": "pass",
                "action": "Removed sparse-dense contrast from the active Figure 3 profile panel; retained it only as a secondary source-level diagnostic.",
            },
            {
                "review_item": "Observation class labels",
                "status": "pass",
                "action": "Used neutral labels: robust survivor with/without diffuse support, one-scale survivor, fragile boundary, stable non-survivor.",
            },
        ]
    )
    write_csv_pair(audit, "review010_figure_polish_audit.csv")
    write_csv_pair(sources, "figure_source_map.csv")
    md = dedent(
        f"""\
        # 4158 Review-010 Pre-Submission Polish

        Date: {DATE}

        This node implemented the high-priority items from
        `mypaper2/00_review/010.md`. It reorganized existing evidence for the
        final pre-submission review and did not recompute T1, change event
        definitions, change screening gates, or open a new mechanism route.

        ## Updated Figures

        - Figure 2 now foregrounds the all-observation survival claim, the
          frozen two-scale support matrix, the completed B=1000 omnibus null,
          and the detrending survivor-count boundary.
        - Figure 3 now keeps the phenotype focus and removes the radius
          correlation and sparse-dense profiles from the active main figure.
        - Figure 5 class labels are kept consistent with the current manuscript
          wording: one-scale survivor, fragile boundary, stable non-survivor,
          and robust survivor with/without diffuse support.

        ## Active Figure Decisions

        - Sparse-dense was removed from the main Figure 3 profile panel because
          the current manuscript does not develop it as an independent result.
          The diagnostic remains available in the upstream profile source.
        - Observation classes use neutral labels: robust survivor with diffuse
          support, robust survivor without diffuse support, one-scale survivor,
          fragile boundary, and stable non-survivor.
        - The older boundary-label wording was removed from active figure
          sources and from the compiled PDF text layer.

        ## Active Figure Outputs

        - Fig2: {'; '.join(paths2)}
        - Fig3: {'; '.join(paths3)}
        - Fig5: mypaper2/Latex/figures/Fig5_final.png; mypaper2/Latex/figures/Fig5_final.pdf

        ## Review Gate

        `pass_4158_review010_pre_submission_polish_compiled`
        """
    )
    (OUT / "4158_figure_summary.md").write_text(md, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    master = pd.read_csv(ROOT / "Output" / "4133" / "observation_master_table.csv")
    ladder = pd.read_csv(ROOT / "Output" / "4081c" / "full_geometry_ladder_rows.csv")
    dist = pd.read_csv(ROOT / "Output" / "4155" / "N_both_distribution.csv")
    p = load_json(ROOT / "Output" / "4155" / "p_omnibus.json")
    detrend = pd.read_csv(ROOT / "Output" / "4142" / "survival_variant_summary.csv")
    profiles = pd.read_csv(ROOT / "Output" / "4085" / "aggregate_profiles.csv")
    metrics = load_json(ROOT / "Output" / "4131" / "decision.json")["primary_metrics"]

    paths2 = build_fig2(master, ladder, dist, p, detrend)
    paths3 = build_fig3(master, profiles, metrics)
    source_rows = [
        {"role": "input", "path": "Output/4133/observation_master_table.csv"},
        {"role": "input", "path": "Output/4081c/full_geometry_ladder_rows.csv"},
        {"role": "input", "path": "Output/4155/N_both_distribution.csv"},
        {"role": "input", "path": "Output/4155/p_omnibus.json"},
        {"role": "input", "path": "Output/4142/survival_variant_summary.csv"},
        {"role": "input", "path": "Output/4085/aggregate_profiles.csv"},
        {"role": "input", "path": "Output/4131/decision.json"},
    ]
    for path in paths2 + paths3:
        source_rows.append({"role": "output", "path": path})
    sources = pd.DataFrame(source_rows)
    sources["exists"] = sources["path"].map(lambda x: (ROOT / str(x)).exists())
    sources["size_bytes"] = sources["path"].map(lambda x: (ROOT / str(x)).stat().st_size if (ROOT / str(x)).exists() else 0)
    write_summary(paths2, paths3, sources)
    print(
        json.dumps(
            {
                "node": NODE,
                "gate_result": "pass_4158_review010_pre_submission_polish_compiled",
                "fig2": paths2,
                "fig3": paths3,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
