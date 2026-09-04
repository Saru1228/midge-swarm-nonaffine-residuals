"""4082b early failure condition or artifact audit.

4081c/4081d found that Ob1/3/6/8 fail the T1 local-affine event-specificity
gate, while Ob9-Ob19 all pass. 4082 then showed robust scale/timing survival for
14/15 surviving observations. This node asks whether the early failure class is
explained by simple event-structure or raw-trajectory quality features.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import sys
from pathlib import Path
from textwrap import dedent

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_DIR = ROOT / "Experiment"
if str(EXPERIMENT_DIR) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_DIR))

from run_4001_geometric_baseline_residual_audit import (  # noqa: E402
    RunConfig as BaseRunConfig,
    median_dt,
    read_raw_ob,
    resolve_data_dir,
)


OUT = ROOT / "Output" / "4082b"
SRC_4081D = ROOT / "Output" / "4081d" / "heterogeneity_features.csv"
SRC_4082 = ROOT / "Output" / "4082" / "ob_scale_timing_robustness.csv"
NODE = "4082b_early_failure_condition_or_artifact_audit"
DATE = "2026-08-25"


FEATURE_COLUMNS = [
    "ob",
    "dataset",
    "failure_group",
    "survival_group",
    "robustness_class",
    "early_ob_le_8",
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
    "n_events",
    "event_rate_per_sec",
    "median_prev_duration_sec",
    "median_next_duration_sec",
    "t1_median_local_to_b3_ratio",
    "t1_median_local_event_minus_non_event_z",
    "t1_k8_local_event_direction_abs_z",
    "t1_k8_local_non_event_direction_abs_median_z",
    "t1_k10_local_event_direction_abs_z",
    "t1_k10_local_non_event_direction_abs_median_z",
    "t2_gate_count",
    "scale_pass_fraction",
    "timing_pass_fraction",
]

CONTRAST_COLUMNS = [
    "feature",
    "feature_family",
    "failure_median",
    "survivor_median",
    "median_difference_failure_minus_survivor",
    "failure_q25",
    "failure_q75",
    "survivor_q25",
    "survivor_q75",
    "exact_permutation_p_two_sided",
    "interpretation",
]


RAW_FEATURES = [
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

EVENT_FEATURES = [
    "n_events",
    "event_rate_per_sec",
    "median_prev_duration_sec",
    "median_next_duration_sec",
]

RESULT_FEATURES = [
    "ob",
    "early_ob_le_8",
    "t1_median_local_to_b3_ratio",
    "t1_median_local_event_minus_non_event_z",
    "t1_k8_local_event_direction_abs_z",
    "t1_k8_local_non_event_direction_abs_median_z",
    "t1_k10_local_event_direction_abs_z",
    "t1_k10_local_non_event_direction_abs_median_z",
    "t2_gate_count",
]


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in columns})


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def md_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        vals = []
        for col in columns:
            val = row.get(col, "")
            if isinstance(val, float):
                vals.append("NA" if not np.isfinite(val) else f"{val:.4g}")
            else:
                vals.append(str(val).replace("\n", " ").replace("|", "\\|"))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def exact_group_permutation_p(values: np.ndarray, group: np.ndarray) -> float:
    values = np.asarray(values, dtype="float64")
    group = np.asarray(group, dtype=bool)
    ok = np.isfinite(values)
    values = values[ok]
    group = group[ok]
    n = len(values)
    n_true = int(group.sum())
    if n_true == 0 or n_true == n:
        return math.nan
    observed = float(np.median(values[group]) - np.median(values[~group]))
    count = 0
    extreme = 0
    for combo in itertools.combinations(range(n), n_true):
        mask = np.zeros(n, dtype=bool)
        mask[list(combo)] = True
        diff = float(np.median(values[mask]) - np.median(values[~mask]))
        count += 1
        if abs(diff) >= abs(observed) - 1e-12:
            extreme += 1
    return float(extreme / count) if count else math.nan


def quantiles(values: pd.Series) -> tuple[float, float, float]:
    arr = pd.to_numeric(values, errors="coerce").to_numpy(dtype="float64")
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return math.nan, math.nan, math.nan
    return tuple(float(x) for x in np.quantile(arr, [0.25, 0.50, 0.75]))


def raw_quality_for_ob(ob: int, dataset: str, data_dir: Path, sample_frames: int) -> dict[str, object]:
    path = data_dir / dataset
    if not path.exists():
        path = data_dir / f"Ob{ob}.txt"
    cache_path = OUT / "raw_quality" / f"Ob{ob}_raw_quality.json"
    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))

    print(f"[4082b] Ob{ob}: reading raw trajectory quality", flush=True)
    df = read_raw_ob(path)
    times = np.asarray(sorted(df["t"].unique()), dtype="float64")
    dt = median_dt(times)
    frame_counts = df.groupby("t", sort=False)["id"].nunique()
    speed = np.sqrt(np.maximum(df["vx"] ** 2 + df["vy"] ** 2 + df["vz"] ** 2, 0.0)).to_numpy(dtype="float64")

    track_counts = df.groupby("id", sort=False)["t"].count()
    track_span = df.groupby("id", sort=False)["t"].agg(lambda s: float(np.nanmax(s) - np.nanmin(s)))
    continuity_numer = 0
    continuity_denom = 0
    if np.isfinite(dt) and dt > 0:
        for _, s in df.groupby("id", sort=False)["t"]:
            arr = np.asarray(s, dtype="float64")
            if arr.size < 2:
                continue
            diffs = np.diff(np.sort(arr))
            continuity_numer += int(np.sum(diffs <= 1.5 * dt))
            continuity_denom += int(diffs.size)

    if len(times) > sample_frames:
        sample_idx = np.linspace(0, len(times) - 1, sample_frames).round().astype(int)
        sample_times = set(float(times[i]) for i in np.unique(sample_idx))
        d_radius = df[df["t"].isin(sample_times)].copy()
    else:
        d_radius = df.copy()
    radii_medians: list[float] = []
    radii_q90: list[float] = []
    for _, g in d_radius.groupby("t", sort=False):
        pos = g[["x", "y", "z"]].to_numpy(dtype="float64")
        if pos.shape[0] < 3:
            continue
        center = np.nanmean(pos, axis=0)
        radii = np.linalg.norm(pos - center, axis=1)
        if np.isfinite(radii).any():
            radii_medians.append(float(np.nanmedian(radii)))
            radii_q90.append(float(np.nanquantile(radii, 0.90)))

    median_radius = float(np.nanmedian(radii_medians)) if radii_medians else math.nan
    radius_cv = (
        float(np.nanstd(radii_medians, ddof=1) / median_radius)
        if len(radii_medians) > 1 and np.isfinite(median_radius) and abs(median_radius) > 1e-12
        else math.nan
    )
    out = {
        "ob": ob,
        "dataset": dataset,
        "file_size_mb": float(path.stat().st_size / (1024 * 1024)) if path.exists() else math.nan,
        "duration_sec": float(np.nanmax(times) - np.nanmin(times)) if times.size else math.nan,
        "n_frames": int(times.size),
        "median_dt_sec": float(dt),
        "unique_ids": int(df["id"].nunique()),
        "median_individuals_per_frame": float(np.nanmedian(frame_counts)),
        "q10_individuals_per_frame": float(np.nanquantile(frame_counts, 0.10)),
        "q90_individuals_per_frame": float(np.nanquantile(frame_counts, 0.90)),
        "median_track_length_frames": float(np.nanmedian(track_counts)),
        "median_track_span_sec": float(np.nanmedian(track_span)),
        "track_continuity_fraction": float(continuity_numer / continuity_denom) if continuity_denom else math.nan,
        "median_raw_speed": float(np.nanmedian(speed)) if speed.size else math.nan,
        "q95_raw_speed": float(np.nanquantile(speed, 0.95)) if speed.size else math.nan,
        "median_swarm_radius": median_radius,
        "q90_swarm_radius": float(np.nanmedian(radii_q90)) if radii_q90 else math.nan,
        "swarm_radius_cv": radius_cv,
    }
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(cache_path, out)
    return out


def build_features(data_dir: Path, sample_frames: int) -> pd.DataFrame:
    h = pd.read_csv(SRC_4081D)
    h["ob"] = pd.to_numeric(h["ob"], errors="coerce").astype("int64")
    h["failure_group"] = h["ob_group"].eq("not_event_conditioned")
    h["survival_group"] = h["ob_group"].eq("survive")
    h["early_ob_le_8"] = (h["ob"] <= 8).astype(int)
    for col in [
        "n_events",
        "event_rate_per_sec",
        "median_prev_duration_sec",
        "median_next_duration_sec",
        "t1_median_local_to_b3_ratio",
        "t1_median_local_event_minus_non_event_z",
        "t1_k8_local_event_direction_abs_z",
        "t1_k8_local_non_event_direction_abs_median_z",
        "t1_k10_local_event_direction_abs_z",
        "t1_k10_local_non_event_direction_abs_median_z",
        "t2_gate_count",
    ]:
        h[col] = pd.to_numeric(h[col], errors="coerce")

    if SRC_4082.exists():
        r = pd.read_csv(SRC_4082)
        r["ob"] = pd.to_numeric(r["ob"], errors="coerce").astype("int64")
        for col in ["scale_pass_fraction", "timing_pass_fraction"]:
            r[col] = pd.to_numeric(r[col], errors="coerce")
        h = h.merge(r[["ob", "robustness_class", "scale_pass_fraction", "timing_pass_fraction"]], on="ob", how="left")
    else:
        h["robustness_class"] = ""
        h["scale_pass_fraction"] = math.nan
        h["timing_pass_fraction"] = math.nan

    raw_rows = [raw_quality_for_ob(int(row.ob), str(row.dataset), data_dir, sample_frames) for row in h.itertuples(index=False)]
    raw = pd.DataFrame(raw_rows)
    out = h.merge(raw.drop(columns=["dataset"], errors="ignore"), on="ob", how="left")
    out["robustness_class"] = out["robustness_class"].fillna("")
    return out.sort_values("ob").reset_index(drop=True)


def feature_family(feature: str) -> str:
    if feature in RAW_FEATURES:
        return "raw_trajectory_quality"
    if feature in EVENT_FEATURES:
        return "event_structure"
    if feature in RESULT_FEATURES:
        return "result_or_gate_context"
    return "other"


def build_contrasts(features: pd.DataFrame) -> pd.DataFrame:
    group = features["failure_group"].to_numpy(dtype=bool)
    rows: list[dict[str, object]] = []
    for feature in RAW_FEATURES + EVENT_FEATURES + RESULT_FEATURES:
        values = pd.to_numeric(features[feature], errors="coerce")
        fail_q = quantiles(values[features["failure_group"]])
        surv_q = quantiles(values[features["survival_group"]])
        p = exact_group_permutation_p(values.to_numpy(dtype="float64"), group)
        diff = fail_q[1] - surv_q[1] if np.isfinite(fail_q[1]) and np.isfinite(surv_q[1]) else math.nan
        fam = feature_family(feature)
        if fam == "result_or_gate_context":
            interp = "describes the outcome split; not an independent artifact explanation"
        elif p <= 0.05:
            interp = "candidate condition/artifact clue"
        elif p <= 0.15:
            interp = "weak routing clue"
        else:
            interp = "no clear failure-group separation"
        rows.append(
            {
                "feature": feature,
                "feature_family": fam,
                "failure_median": fail_q[1],
                "survivor_median": surv_q[1],
                "median_difference_failure_minus_survivor": diff,
                "failure_q25": fail_q[0],
                "failure_q75": fail_q[2],
                "survivor_q25": surv_q[0],
                "survivor_q75": surv_q[2],
                "exact_permutation_p_two_sided": p,
                "interpretation": interp,
            }
        )
    return pd.DataFrame(rows).sort_values("exact_permutation_p_two_sided", na_position="last").reset_index(drop=True)


def make_figures(features: pd.DataFrame, contrasts: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt

    fig_dir = OUT / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    colors = np.where(features["failure_group"], "#b23a48", np.where(features["robustness_class"] == "fragile_or_boundary", "#d97904", "#1f9d55"))

    fig, axes = plt.subplots(4, 1, figsize=(11, 11), sharex=True, constrained_layout=True)
    plot_cols = [
        ("t1_median_local_event_minus_non_event_z", "T1 event-control gap"),
        ("event_rate_per_sec", "event rate/sec"),
        ("median_individuals_per_frame", "median individuals/frame"),
        ("track_continuity_fraction", "track continuity"),
    ]
    for ax, (col, label) in zip(axes, plot_cols):
        ax.bar(features["ob"], pd.to_numeric(features[col], errors="coerce"), color=colors)
        ax.set_ylabel(label)
        ax.grid(axis="y", color="#dddddd", linewidth=0.8)
        if col == "t1_median_local_event_minus_non_event_z":
            ax.axhline(0, color="#444444", linewidth=1)
    axes[0].set_title("4082b early failure audit overview")
    axes[-1].set_xlabel("Observation")
    axes[-1].set_xticks(features["ob"])
    handles = [
        plt.Line2D([0], [0], marker="s", linestyle="", color="#b23a48", label="failure Ob1/3/6/8"),
        plt.Line2D([0], [0], marker="s", linestyle="", color="#d97904", label="weak survivor Ob4"),
        plt.Line2D([0], [0], marker="s", linestyle="", color="#1f9d55", label="robust survivor"),
    ]
    axes[0].legend(handles=handles, frameon=False, loc="upper left")
    fig.savefig(fig_dir / "4082b_failure_audit_overview.png", dpi=180)
    plt.close(fig)

    raw_event = contrasts[contrasts["feature_family"].isin(["raw_trajectory_quality", "event_structure"])].head(12).copy()
    fig, ax = plt.subplots(figsize=(9, 6), constrained_layout=True)
    y = np.arange(len(raw_event))
    ax.barh(y - 0.18, raw_event["failure_median"], height=0.36, color="#b23a48", label="failure")
    ax.barh(y + 0.18, raw_event["survivor_median"], height=0.36, color="#1f9d55", label="survivor")
    ax.set_yticks(y)
    ax.set_yticklabels(raw_event["feature"])
    ax.invert_yaxis()
    ax.set_title("Raw/event feature contrasts sorted by exact permutation p")
    ax.set_xlabel("median value")
    ax.grid(axis="x", color="#dddddd", linewidth=0.8)
    ax.legend(frameon=False)
    fig.savefig(fig_dir / "4082b_raw_event_feature_contrasts.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.5, 5.5), constrained_layout=True)
    ax.scatter(
        features["median_individuals_per_frame"],
        features["event_rate_per_sec"],
        c=colors,
        s=80,
        edgecolor="#222222",
        linewidth=0.6,
    )
    for row in features.itertuples(index=False):
        ax.text(row.median_individuals_per_frame, row.event_rate_per_sec, f" Ob{int(row.ob)}", fontsize=8, va="center")
    ax.set_xlabel("median individuals per frame")
    ax.set_ylabel("event rate per sec")
    ax.set_title("Failure cases are not separated by simple N/event-rate alone")
    ax.grid(color="#dddddd", linewidth=0.8)
    ax.legend(handles=handles, frameon=False, loc="best")
    fig.savefig(fig_dir / "4082b_event_rate_vs_group_size.png", dpi=180)
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default=BaseRunConfig.data_dir)
    parser.add_argument("--sample-frames", type=int, default=2500)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    data_dir = resolve_data_dir(BaseRunConfig(data_dir=args.data_dir))

    features = build_features(data_dir, args.sample_frames)
    contrasts = build_contrasts(features)
    make_figures(features, contrasts)

    write_csv(OUT / "failure_audit_features.csv", features.to_dict("records"), FEATURE_COLUMNS)
    write_csv(OUT / "tables" / "failure_audit_features.csv", features.to_dict("records"), FEATURE_COLUMNS)
    write_json(OUT / "failure_audit_features.json", features.to_dict("records"))
    write_csv(OUT / "failure_audit_feature_contrasts.csv", contrasts.to_dict("records"), CONTRAST_COLUMNS)
    write_csv(OUT / "tables" / "failure_audit_feature_contrasts.csv", contrasts.to_dict("records"), CONTRAST_COLUMNS)
    write_json(OUT / "failure_audit_feature_contrasts.json", contrasts.to_dict("records"))

    failure_obs = [int(x) for x in features.loc[features["failure_group"], "ob"].tolist()]
    survivor_obs = [int(x) for x in features.loc[features["survival_group"], "ob"].tolist()]
    robust_survivor_obs = [
        int(x)
        for x in features.loc[(features["survival_group"]) & (features["robustness_class"] == "robust_scale_and_timing"), "ob"].tolist()
    ]
    raw_best = contrasts[contrasts["feature_family"] == "raw_trajectory_quality"].head(5)
    event_best = contrasts[contrasts["feature_family"] == "event_structure"].head(5)
    raw_strong = raw_best[pd.to_numeric(raw_best["exact_permutation_p_two_sided"], errors="coerce") <= 0.05]
    event_strong = event_best[pd.to_numeric(event_best["exact_permutation_p_two_sided"], errors="coerce") <= 0.05]

    if len(raw_strong) > 0:
        result = "support_possible_raw_condition_or_quality_split"
        next_node = "inspect_metadata_or_quality_control_for_failure_observations"
    elif len(event_strong) > 0:
        result = "support_event_structure_difference_for_failure_observations"
        next_node = "state_definition_sensitivity_for_failure_observations"
    else:
        result = "boundary_early_failure_not_explained_by_basic_quality_or_event_counts"
        next_node = "bounded_408x_synthesis_or_metadata_deep_audit"

    decision = {
        "node": NODE,
        "date": DATE,
        "result": result,
        "failure_observations": failure_obs,
        "survivor_observations": survivor_obs,
        "robust_survivor_observations": robust_survivor_obs,
        "raw_quality_strong_clues": raw_strong["feature"].tolist(),
        "event_structure_strong_clues": event_strong["feature"].tolist(),
        "interpretation": (
            "The audit separates independent condition/artifact clues from the T1 gate variables "
            "that define the failure outcome itself."
        ),
        "boundary": (
            "If raw/event features do not strongly separate the failure group, the early concentration "
            "remains an unexplained batch/condition boundary rather than a resolved artifact."
        ),
        "next": [next_node],
        "artifacts": [
            "Output/4082b/failure_audit_features.csv",
            "Output/4082b/failure_audit_feature_contrasts.csv",
            "Output/4082b/figures/4082b_failure_audit_overview.png",
            "Output/4082b/figures/4082b_raw_event_feature_contrasts.png",
            "Output/4082b/figures/4082b_event_rate_vs_group_size.png",
        ],
    }
    write_json(OUT / "decision.json", decision)

    config = dedent(
        f"""\
        node: {NODE}
        date: {DATE}
        node_type: artifact-control
        input_nodes:
          - 4081d_explain_observation_heterogeneity_before_4082
          - 4082_scale_robustness_on_surviving_observation_class
        failure_observations: {','.join(str(x) for x in failure_obs)}
        survivor_observations: {','.join(str(x) for x in survivor_obs)}
        sample_frames_for_radius_quality: {args.sample_frames}
        """
    )
    (OUT / "config.yaml").write_text(config, encoding="utf-8")

    display_cols = [
        "ob",
        "failure_group",
        "robustness_class",
        "n_events",
        "event_rate_per_sec",
        "median_individuals_per_frame",
        "track_continuity_fraction",
        "median_raw_speed",
        "median_swarm_radius",
        "t1_median_local_event_minus_non_event_z",
    ]
    contrast_display = [
        "feature",
        "feature_family",
        "failure_median",
        "survivor_median",
        "median_difference_failure_minus_survivor",
        "exact_permutation_p_two_sided",
        "interpretation",
    ]
    summary = dedent(
        f"""\
        # Node 4082b Summary

        ## Question

        Why do Ob1/Ob3/Ob6/Ob8 fail the local-affine T1 event-specificity gate,
        while most later observations pass?

        ## Inputs

        - `Output/4081d/heterogeneity_features.csv`
        - `Output/4082/ob_scale_timing_robustness.csv`
        - raw trajectory files from the configured data directory

        ## Decision

        `{result}`

        ## Main Reading

        Failure observations:

        ```text
        {', '.join('Ob' + str(x) for x in failure_obs)}
        ```

        Robust survivor observations after 4082:

        ```text
        {', '.join('Ob' + str(x) for x in robust_survivor_obs)}
        ```

        ## Audit Features

        {md_table(features[display_cols].round(4).to_dict("records"), display_cols)}

        ## Strongest Contrasts

        {md_table(contrasts[contrast_display].head(14).to_dict("records"), contrast_display)}

        ## Interpretation

        This audit should not be read as a mechanism discovery step. It asks
        whether the failure class has an obvious condition/artifact explanation.

        - T1 gate-derived variables sharply separate failure and survivor groups;
          that is expected and not independent evidence.
        - Raw trajectory and event-structure variables are treated as more useful
          artifact/condition clues.
        - If those raw/event variables do not separate clearly, the correct
          route is to keep the early-observation boundary visible rather than
          claiming it is solved.

        ## Next

        `{next_node}`

        ## Artifacts

        - `Output/4082b/failure_audit_features.csv`
        - `Output/4082b/failure_audit_feature_contrasts.csv`
        - `Output/4082b/figures/4082b_failure_audit_overview.png`
        - `Output/4082b/figures/4082b_raw_event_feature_contrasts.png`
        - `Output/4082b/figures/4082b_event_rate_vs_group_size.png`
        """
    ).lstrip()
    summary = "\n".join(line[8:] if line.startswith("        ") else line for line in summary.splitlines()) + "\n"
    (OUT / "4082b_summary.md").write_text(summary, encoding="utf-8")
    print(f"Wrote 4082b outputs to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
