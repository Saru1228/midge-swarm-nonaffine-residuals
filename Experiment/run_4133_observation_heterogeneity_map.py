"""4133 observation heterogeneity map.

This node maps how the positive and boundary evidence varies across the 19
observations. It is descriptive and exploratory: no new target, no new
mechanism model, no high-dimensional feature search, and no causal metadata
claim.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
from textwrap import dedent

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4133"
DATE = "2026-08-27"
NODE = "4133_observation_heterogeneity_map"
RAW_DATA_DIR = Path(os.environ.get("MIDGE_DATA_ROOT", os.environ.get("MIDGE_DATA_ROOT", os.environ.get("FISH_3D_DATASET_DIR", "data/raw"))))


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


def write_csv_pair(df: pd.DataFrame, name: str) -> None:
    df.to_csv(OUT / name, index=False)
    df.to_csv(OUT / "tables" / name, index=False)


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


def to_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in columns:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def bool_to_float(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().map({"true": 1.0, "false": 0.0})


def compute_raw_metadata() -> pd.DataFrame:
    cached = OUT / "raw_metadata_by_ob.csv"
    if cached.exists():
        return pd.read_csv(cached)

    rows: list[dict[str, object]] = []
    for ob in range(1, 20):
        path = RAW_DATA_DIR / f"Ob{ob}.txt"
        if not path.exists():
            rows.append(
                {
                    "ob": ob,
                    "dataset": f"Ob{ob}.txt",
                    "raw_metadata_status": "MISSING",
                    "raw_metadata_source": str(path),
                }
            )
            continue

        row_count = 0
        track_ids: set[int] = set()
        frame_times: set[float] = set()
        min_time = math.inf
        max_time = -math.inf
        for chunk in pd.read_csv(path, header=None, usecols=[0, 4], chunksize=1_000_000):
            ids = pd.to_numeric(chunk[0], errors="coerce").dropna().astype(np.int64)
            times = pd.to_numeric(chunk[4], errors="coerce").dropna().astype(float)
            row_count += int(len(chunk))
            track_ids.update(ids.unique().tolist())
            rounded_times = np.round(times.to_numpy(dtype=float), 6)
            frame_times.update(rounded_times.tolist())
            if len(times):
                min_time = min(min_time, float(times.min()))
                max_time = max(max_time, float(times.max()))

        n_frames = len(frame_times)
        n_tracks = len(track_ids)
        duration = max_time - min_time if math.isfinite(min_time) and math.isfinite(max_time) else np.nan
        rows.append(
            {
                "ob": ob,
                "dataset": f"Ob{ob}.txt",
                "raw_metadata_status": "VERIFIED_FROM_RAW_COLUMNS_0_AND_4",
                "raw_metadata_source": str(path),
                "raw_row_count": row_count,
                "raw_n_frames": n_frames,
                "raw_n_tracks": n_tracks,
                "dataset_length_sec": duration,
                "mean_swarm_size": row_count / n_frames if n_frames else np.nan,
                "mean_track_length_frames": row_count / n_tracks if n_tracks else np.nan,
                "mean_track_length_sec": (row_count / n_tracks) * 0.01 if n_tracks else np.nan,
            }
        )

    df = pd.DataFrame(rows)
    df.to_csv(cached, index=False)
    df.to_csv(OUT / "tables" / "raw_metadata_by_ob.csv", index=False)
    return df


def load_inputs() -> dict[str, object]:
    return {
        "d4130": read_json(ROOT / "Output" / "4130" / "decision.json"),
        "d4131": read_json(ROOT / "Output" / "4131" / "decision.json"),
        "d4132": read_json(ROOT / "Output" / "4132" / "decision.json"),
        "coverage": pd.read_csv(ROOT / "Output" / "4131" / "observation_positive_coverage_matrix.csv"),
        "negative_atlas": pd.read_csv(ROOT / "Output" / "4132" / "negative_boundary_atlas.csv"),
        "spatial_rows": pd.read_csv(ROOT / "Output" / "4084" / "spatial_taxonomy_condition_rows.csv"),
        "phase_rows": pd.read_csv(ROOT / "Output" / "4085" / "phase_profile_rows.csv"),
        "signed_rows": pd.read_csv(ROOT / "Output" / "4086" / "ob_signed_classification.csv"),
        "failure_rows": pd.read_csv(ROOT / "Output" / "4087" / "ob_failure_boundary_sensitivity.csv"),
        "moment_oos": pd.read_csv(ROOT / "Output" / "4090" / "grouped_oos_results.csv"),
        "event_local": pd.read_csv(ROOT / "Output" / "4100" / "observation_level_effects.csv"),
        "history": pd.read_csv(ROOT / "Output" / "4121" / "observation_level_effects.csv"),
        "matching_4121": pd.read_csv(ROOT / "Output" / "4121" / "matching_quality.csv"),
        "transition_meta": pd.read_csv(ROOT / "Output" / "3032" / "tables" / "transition_metadata_by_ob.csv"),
        "metadata_audit": pd.read_csv(ROOT / "Output" / "4130" / "metadata_source_audit.csv"),
    }


def recording_condition_for_ob(ob: int) -> tuple[str, str, str, str]:
    if ob in {6, 11}:
        condition = "daytime"
    else:
        condition = "mainly_dusk"
    return (
        condition,
        "idea/413x_phenomenon_boundary_evidence_synthesis_roadmap.md",
        "UNVERIFIED",
        "descriptive_annotation_only",
    )


def build_master_table(data: dict[str, object], raw_meta: pd.DataFrame) -> pd.DataFrame:
    coverage = data["coverage"].copy()
    coverage["ob"] = coverage["ob"].astype(int)
    coverage = to_numeric(
        coverage,
        [
            "n_events",
            "t1_median_local_to_b3_ratio",
            "t1_median_local_event_minus_non_event_z",
            "scale_pass_fraction",
            "timing_pass_fraction",
            "median_scale_gap",
            "best_spatial_gap_z",
            "median_signed_axis_delta_A_z",
            "real_minus_null_median_abs_effect",
        ],
    )
    coverage["t1_survival_any_binary"] = bool_to_float(coverage["t1_survival_any_k"])
    coverage["t1_survival_both_binary"] = bool_to_float(coverage["t1_survival_both_k"])
    coverage["scale_lag_robust_binary"] = bool_to_float(coverage["scale_lag_robust"])
    coverage["diffuse_gate_binary"] = bool_to_float(coverage["diffuse_all_tangential_gate"])
    coverage["edge_phase_binary"] = bool_to_float(coverage["edge_core_phase_gate"])
    coverage["history_beats_median_binary"] = bool_to_float(coverage["history_real_beats_shuffle_median_abs"])

    raw_meta["ob"] = raw_meta["ob"].astype(int)
    transition_meta = data["transition_meta"].copy()
    transition_meta["ob"] = transition_meta["ob"].astype(int)
    transition_meta = to_numeric(transition_meta, ["dt_sec", "transition_count"])

    spatial_rows = data["spatial_rows"].copy()
    spatial_rows["ob"] = spatial_rows["ob"].astype(int)
    spatial_rows = to_numeric(
        spatial_rows,
        ["event_minus_non_event_abs_direction_z", "real_abs_direction_contrast_z"],
    )
    all_tang = spatial_rows[spatial_rows["variable"].eq("all_tangential")][
        ["ob", "event_minus_non_event_abs_direction_z", "real_abs_direction_contrast_z"]
    ].rename(
        columns={
            "event_minus_non_event_abs_direction_z": "4084_diffuse_effect",
            "real_abs_direction_contrast_z": "4084_diffuse_abs_direction_contrast",
        }
    )
    edge_core = spatial_rows[spatial_rows["variable"].eq("shell_edge_minus_core")][
        ["ob", "event_minus_non_event_abs_direction_z", "real_abs_direction_contrast_z"]
    ].rename(
        columns={
            "event_minus_non_event_abs_direction_z": "4084_edge_core_effect",
            "real_abs_direction_contrast_z": "4084_edge_core_abs_direction_contrast",
        }
    )

    phase_rows = data["phase_rows"].copy()
    phase_rows["ob"] = phase_rows["ob"].astype(int)
    phase_rows = to_numeric(phase_rows, ["abs_event_minus_abs_null_z", "event_minus_null_phase_z"])
    near_pre = phase_rows[phase_rows["variable"].eq("all_tangential") & phase_rows["phase"].eq("near_pre")][
        ["ob", "abs_event_minus_abs_null_z", "event_minus_null_phase_z"]
    ].rename(
        columns={
            "abs_event_minus_abs_null_z": "4085_near_pre_abs_effect",
            "event_minus_null_phase_z": "4085_near_pre_signed_effect",
        }
    )

    signed_rows = data["signed_rows"].copy()
    signed_rows["ob"] = signed_rows["ob"].astype(int)
    signed_rows = to_numeric(signed_rows, ["signed_separation_z", "mirror_balance"])
    signed_rows = signed_rows[["ob", "signed_class", "signed_separation_z", "mirror_balance"]]

    moment = data["moment_oos"].copy()
    moment["heldout_ob"] = moment["heldout_ob"].astype(int)
    moment = to_numeric(moment, ["incremental_r2_state_vs_radius", "real_minus_shift_incremental_r2"])
    first = moment[moment["target_family"].eq("first_moment")][
        ["heldout_ob", "incremental_r2_state_vs_radius", "real_minus_shift_incremental_r2"]
    ].rename(
        columns={
            "heldout_ob": "ob",
            "incremental_r2_state_vs_radius": "4090_first_moment_gain",
            "real_minus_shift_incremental_r2": "4090_first_moment_real_minus_shift",
        }
    )
    second = moment[moment["target_family"].eq("second_moment")][
        ["heldout_ob", "incremental_r2_state_vs_radius", "real_minus_shift_incremental_r2"]
    ].rename(
        columns={
            "heldout_ob": "ob",
            "incremental_r2_state_vs_radius": "4090_second_moment_gain",
            "real_minus_shift_incremental_r2": "4090_second_moment_real_minus_shift",
        }
    )

    event_local = data["event_local"].copy()
    event_local["ob"] = event_local["ob"].astype(int)
    event_local = to_numeric(event_local, ["median_delta_A_pre_z", "fraction_positive_delta", "median_best_match_distance"])
    event_local = event_local[
        ["ob", "median_delta_A_pre_z", "fraction_positive_delta", "median_best_match_distance"]
    ].rename(
        columns={
            "median_delta_A_pre_z": "4100_event_local_effect",
            "fraction_positive_delta": "4100_event_local_fraction_positive",
            "median_best_match_distance": "4100_event_match_distance",
        }
    )

    history = data["history"].copy()
    history["ob"] = history["ob"].astype(int)
    history = to_numeric(
        history,
        [
            "median_signed_axis_delta_A_z",
            "real_minus_null_median_abs_effect",
            "null_median_abs_signed_axis_delta_A_z",
            "n_selected_pairs",
            "paired_frame_fraction",
        ],
    )
    history = history[
        [
            "ob",
            "median_signed_axis_delta_A_z",
            "real_minus_null_median_abs_effect",
            "null_median_abs_signed_axis_delta_A_z",
            "n_selected_pairs",
            "paired_frame_fraction",
        ]
    ].rename(
        columns={
            "median_signed_axis_delta_A_z": "4121_history_signed_effect",
            "real_minus_null_median_abs_effect": "4121_null_gap",
            "null_median_abs_signed_axis_delta_A_z": "4121_shuffle_median_abs_effect",
            "n_selected_pairs": "4121_selected_pairs",
            "paired_frame_fraction": "4121_paired_frame_fraction",
        }
    )
    history["4121_history_abs_effect"] = history["4121_history_signed_effect"].abs()

    failure = data["failure_rows"].copy()
    failure["ob"] = failure["ob"].astype(int)
    failure = failure[["ob", "failure_boundary_class", "any_rescue"]]

    master = pd.DataFrame({"ob": np.arange(1, 20)})
    for df in [
        raw_meta,
        transition_meta[["ob", "dt_sec", "transition_count"]],
        coverage,
        all_tang,
        edge_core,
        near_pre,
        signed_rows,
        first,
        second,
        event_local,
        history,
        failure,
    ]:
        master = master.merge(df, on="ob", how="left")

    conditions = master["ob"].map(lambda x: recording_condition_for_ob(int(x)))
    master["recording_condition"] = [x[0] for x in conditions]
    master["recording_condition_source"] = [x[1] for x in conditions]
    master["recording_condition_verification_status"] = [x[2] for x in conditions]
    master["recording_condition_allowed_use"] = [x[3] for x in conditions]
    master["ob_index_order_proxy_status"] = "UNVERIFIED"
    master["ob_index_order_proxy_allowed_use"] = "descriptive_rank_proxy_only"

    master["408x_T1_effect"] = master["t1_median_local_event_minus_non_event_z"]
    master["408x_pass_class"] = master["ob_route_a_class"]
    master["408x_robustness"] = master["robustness_class"]
    master["route_positive_score"] = master[
        [
            "t1_survival_any_binary",
            "t1_survival_both_binary",
            "scale_lag_robust_binary",
            "diffuse_gate_binary",
            "edge_phase_binary",
            "history_beats_median_binary",
        ]
    ].apply(lambda row: pd.to_numeric(row, errors="coerce").fillna(0).sum(), axis=1)
    master["stable_408x_failure"] = master["failure_boundary_class"].eq(
        "stable_failure_under_predefined_sensitivity"
    )
    master["fragile_408x_boundary"] = master["failure_boundary_class"].eq("fragile_narrow_setting_rescue")
    master["robust_survivor"] = master["408x_robustness"].eq("robust_scale_and_timing")
    master["fragile_survivor"] = master["408x_robustness"].eq("fragile_or_boundary")

    return master


def classify_observations(master: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for row in master.to_dict("records"):
        ob = int(row["ob"])
        if bool(row.get("stable_408x_failure")):
            cls = "stable_408x_failure"
        elif bool(row.get("fragile_408x_boundary")):
            cls = "fragile_408x_boundary"
        elif bool(row.get("fragile_survivor")):
            cls = "fragile_survivor"
        elif bool(row.get("robust_survivor")) and str(row.get("diffuse_all_tangential_gate")).lower() == "true":
            cls = "robust_survivor_diffuse_positive"
        elif bool(row.get("robust_survivor")):
            cls = "robust_survivor_without_diffuse_gate"
        else:
            cls = "unclassified_boundary"
        flags = []
        if ob in {6, 11}:
            flags.append("daytime_annotation_unverified")
        if ob in {1, 3, 6, 8}:
            flags.append("408x_failure_or_boundary")
        if ob == 4:
            flags.append("scale_lag_fragile")
        if str(row.get("history_real_beats_shuffle_median_abs")).lower() == "true":
            flags.append("history_beats_median_shuffle")
        rows.append(
            {
                "ob": ob,
                "observation_class": cls,
                "route_positive_score": row.get("route_positive_score"),
                "408x_pass_class": row.get("408x_pass_class"),
                "408x_robustness": row.get("408x_robustness"),
                "failure_boundary_class": row.get("failure_boundary_class"),
                "signed_class": row.get("signed_class"),
                "recording_condition": row.get("recording_condition"),
                "recording_condition_verification_status": row.get(
                    "recording_condition_verification_status"
                ),
                "boundary_flags": ";".join(flags),
            }
        )
    return pd.DataFrame(rows)


def spearman_rho(x: pd.Series, y: pd.Series) -> float:
    valid = pd.concat([x, y], axis=1).dropna()
    if len(valid) < 4:
        return np.nan
    rx = valid.iloc[:, 0].rank(method="average")
    ry = valid.iloc[:, 1].rank(method="average")
    return float(rx.corr(ry))


def spearman_pvalue(x: pd.Series, y: pd.Series) -> float:
    valid = pd.concat([x, y], axis=1).dropna()
    if len(valid) < 4:
        return np.nan
    try:
        from scipy.stats import spearmanr

        return float(spearmanr(valid.iloc[:, 0], valid.iloc[:, 1], nan_policy="omit").pvalue)
    except Exception:
        return np.nan


def association_label(rho: float, n: int) -> str:
    if not math.isfinite(rho) or n < 8:
        return "insufficient"
    ar = abs(rho)
    if ar >= 0.6:
        return "moderate_descriptive_association"
    if ar >= 0.4:
        return "weak_to_moderate_descriptive_association"
    return "weak_or_no_descriptive_association"


def build_associations(master: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    specs = [
        ("HET1", "mean_swarm_size", "408x_T1_effect", "T1 effect vs swarm size"),
        ("HET1", "mean_track_length_frames", "408x_T1_effect", "T1 effect vs mean track length"),
        ("HET1", "dataset_length_sec", "408x_T1_effect", "T1 effect vs dataset length"),
        ("HET1", "n_events", "408x_T1_effect", "T1 effect vs event count"),
        ("HET2", "408x_T1_effect", "4121_history_abs_effect", "history abs effect vs T1 effect"),
        ("HET2", "408x_T1_effect", "4121_null_gap", "history null gap vs T1 effect"),
        ("HET2", "route_positive_score", "4121_history_abs_effect", "history abs effect vs route score"),
        ("HET3", "stable_408x_failure_binary", "route_positive_score", "stable failure vs route score"),
        ("HET3", "stable_408x_failure_binary", "4100_event_local_effect", "stable failure vs event-local effect"),
        ("HET4", "ob", "408x_T1_effect", "ob index proxy vs T1 effect"),
        ("HET4", "ob", "route_positive_score", "ob index proxy vs route score"),
        ("HET4", "ob", "4121_history_abs_effect", "ob index proxy vs history abs effect"),
    ]
    working = master.copy()
    working["stable_408x_failure_binary"] = working["stable_408x_failure"].astype(float)
    numeric_cols = sorted(set([x for _, x, _, _ in specs] + [y for _, _, y, _ in specs]))
    working = to_numeric(working, numeric_cols)

    assoc_rows: list[dict[str, object]] = []
    loo_rows: list[dict[str, object]] = []
    for question, x_col, y_col, desc in specs:
        cols = list(dict.fromkeys([x_col, y_col, "ob"]))
        valid = working[cols].dropna(subset=[x_col, y_col])
        rho = spearman_rho(valid[x_col], valid[y_col])
        pvalue = spearman_pvalue(valid[x_col], valid[y_col])
        loo_values = []
        for ob in valid["ob"].unique():
            loo_valid = valid[valid["ob"] != ob]
            loo_rho = spearman_rho(loo_valid[x_col], loo_valid[y_col])
            loo_values.append((int(ob), loo_rho))
            loo_rows.append(
                {
                    "question": question,
                    "association": desc,
                    "x": x_col,
                    "y": y_col,
                    "left_out_ob": int(ob),
                    "rho_without_ob": loo_rho,
                    "rho_full": rho,
                    "abs_change": abs(loo_rho - rho) if math.isfinite(loo_rho) and math.isfinite(rho) else np.nan,
                }
            )
        finite_loo = [(ob, val) for ob, val in loo_values if math.isfinite(val)]
        influential = ""
        max_change = np.nan
        if finite_loo and math.isfinite(rho):
            changes = [(ob, abs(val - rho)) for ob, val in finite_loo]
            influential, max_change = max(changes, key=lambda z: z[1])
        assoc_rows.append(
            {
                "question": question,
                "association": desc,
                "x": x_col,
                "y": y_col,
                "n": int(len(valid)),
                "spearman_rho": rho,
                "spearman_pvalue_descriptive": pvalue,
                "loo_rho_min": min([val for _, val in finite_loo], default=np.nan),
                "loo_rho_max": max([val for _, val in finite_loo], default=np.nan),
                "max_abs_loo_change": max_change,
                "most_influential_ob": influential,
                "association_label": association_label(rho, int(len(valid))),
                "allowed_interpretation": "descriptive_small_n_only",
            }
        )
    return pd.DataFrame(assoc_rows), pd.DataFrame(loo_rows)


def make_figures(master: pd.DataFrame, associations: pd.DataFrame) -> list[str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    from matplotlib.patches import Patch

    files: list[str] = []
    fig_dir = OUT / "figures"

    features = [
        "t1_survival_any_binary",
        "scale_lag_robust_binary",
        "diffuse_gate_binary",
        "edge_phase_binary",
        "history_beats_median_binary",
        "stable_408x_failure",
        "fragile_408x_boundary",
    ]
    mat = master[features].copy()
    for col in features:
        mat[col] = pd.to_numeric(mat[col], errors="coerce")
    encoded = np.where(mat.isna(), 0, np.where(mat.to_numpy(dtype=float) > 0.5, 2, 1))
    cmap = ListedColormap(["#d8d8d8", "#f4f1ea", "#1d7a61"])
    fig, ax = plt.subplots(figsize=(10.8, 6.2))
    ax.imshow(encoded, aspect="auto", cmap=cmap, vmin=0, vmax=2)
    ax.set_yticks(np.arange(len(master)))
    ax.set_yticklabels([f"Ob{int(x)}" for x in master["ob"]], fontsize=8)
    ax.set_xticks(np.arange(len(features)))
    ax.set_xticklabels(
        [
            "T1",
            "scale/lag",
            "diffuse",
            "edge phase",
            "history",
            "stable fail",
            "fragile fail",
        ],
        rotation=35,
        ha="right",
    )
    ax.legend(
        handles=[
            Patch(facecolor="#1d7a61", label="flag true"),
            Patch(facecolor="#f4f1ea", label="flag false"),
            Patch(facecolor="#d8d8d8", label="not tested"),
        ],
        loc="upper left",
        bbox_to_anchor=(1.01, 1.0),
        frameon=False,
    )
    ax.set_title("4133 observation x route heterogeneity matrix")
    fig.tight_layout()
    path = fig_dir / "4133_observation_route_matrix.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    files.append(rel(path))

    def scatter_plot(x: str, y: str, fname: str, title: str) -> None:
        fig, ax = plt.subplots(figsize=(6.4, 5.0))
        valid = master[[x, y, "ob", "stable_408x_failure", "fragile_408x_boundary"]].dropna()
        colors = np.where(
            valid["stable_408x_failure"].astype(bool),
            "#b6423c",
            np.where(valid["fragile_408x_boundary"].astype(bool), "#b08b33", "#1d7a61"),
        )
        ax.scatter(valid[x], valid[y], c=colors, s=55, edgecolor="#222222", linewidth=0.4)
        for _, row in valid.iterrows():
            ax.text(row[x], row[y], f" {int(row['ob'])}", fontsize=8, va="center")
        rho = spearman_rho(valid[x], valid[y])
        ax.set_title(f"{title}\nSpearman rho={fmt_float(rho)}")
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        ax.grid(color="#dddddd", linewidth=0.8)
        ax.set_axisbelow(True)
        fig.tight_layout()
        path = fig_dir / fname
        fig.savefig(path, dpi=180)
        plt.close(fig)
        files.append(rel(path))

    scatter_plot("mean_swarm_size", "408x_T1_effect", "4133_t1_effect_vs_mean_swarm_size.png", "T1 effect vs mean swarm size")
    scatter_plot(
        "mean_track_length_frames",
        "408x_T1_effect",
        "4133_t1_effect_vs_mean_track_length.png",
        "T1 effect vs mean track length",
    )
    scatter_plot(
        "408x_T1_effect",
        "4121_history_abs_effect",
        "4133_history_abs_vs_t1_effect.png",
        "history abs effect vs T1 effect",
    )

    fig, ax = plt.subplots(figsize=(10.0, 4.8))
    class_colors = {
        "stable_408x_failure": "#b6423c",
        "fragile_408x_boundary": "#b08b33",
        "fragile_survivor": "#7c6f58",
        "robust_survivor_diffuse_positive": "#1d7a61",
        "robust_survivor_without_diffuse_gate": "#74a892",
        "unclassified_boundary": "#777777",
    }
    colors = [class_colors.get(x, "#777777") for x in master["observation_class"]]
    ax.bar([f"Ob{int(x)}" for x in master["ob"]], master["route_positive_score"], color=colors)
    ax.set_title("4133 route-positive score by observation class")
    ax.set_ylabel("positive route score")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", color="#dddddd", linewidth=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    path = fig_dir / "4133_route_score_by_observation_class.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    files.append(rel(path))

    return files


def main() -> None:
    ensure_dirs()
    raw_meta = compute_raw_metadata()
    data = load_inputs()
    master = build_master_table(data, raw_meta)
    classes = classify_observations(master)
    master = master.merge(classes[["ob", "observation_class"]], on="ob", how="left")
    associations, loo = build_associations(master)
    figure_files = make_figures(master, associations)

    write_csv_pair(master, "observation_master_table.csv")
    write_csv_pair(classes, "observation_classes.csv")
    write_csv_pair(associations, "heterogeneity_associations.csv")
    write_csv_pair(loo, "leave_one_out_sensitivity.csv")

    class_counts = classes["observation_class"].value_counts().to_dict()
    moderate = associations[
        associations["association_label"].isin(
            ["moderate_descriptive_association", "weak_to_moderate_descriptive_association"]
        )
    ].sort_values("spearman_rho", key=lambda s: s.abs(), ascending=False)

    gate_pass = len(master) == 19 and len(associations) == 12 and len(figure_files) == 5
    decision = {
        "node": NODE,
        "date": DATE,
        "node_type": "observation_heterogeneity_map",
        "upstream_nodes": [
            "4131_robust_positive_phenomenon_atlas",
            "4132_negative_mechanism_boundary_atlas",
        ],
        "data_scope": "all_19_observations",
        "raw_data_dir": str(RAW_DATA_DIR),
        "master_table_rows": int(len(master)),
        "class_counts": {str(k): int(v) for k, v in class_counts.items()},
        "association_counts": {
            "tested_associations": int(len(associations)),
            "moderate_or_weak_moderate_descriptive": int(len(moderate)),
        },
        "metadata_status": {
            "raw_column_0_4_metadata": "VERIFIED_FROM_RAW_COLUMNS_0_AND_4"
            if raw_meta["raw_metadata_status"].eq("VERIFIED_FROM_RAW_COLUMNS_0_AND_4").all()
            else "PARTIAL_OR_MISSING",
            "recording_condition_daytime_dusk": "UNVERIFIED",
            "observation_index_as_order_proxy": "UNVERIFIED",
        },
        "quality_checks": {
            "all_19_master_rows": bool(len(master) == 19),
            "raw_metadata_cached": bool((OUT / "raw_metadata_by_ob.csv").exists()),
            "recording_condition_not_used_as_causal": True,
            "ob_index_marked_proxy_only": True,
            "figures_written": bool(len(figure_files) == 5),
        },
        "gate_result": "pass_4133_heterogeneity_map_ready_with_metadata_boundary"
        if gate_pass
        else "boundary_4133_heterogeneity_map_incomplete",
        "interpretation": (
            "Observation-level heterogeneity can be mapped descriptively. Robust survivor, fragile boundary, stable "
            "failure, signed-history, and metadata-annotation dimensions can be compared, but the n=19 associations "
            "are exploratory and metadata-dependent patterns remain non-causal."
        ),
        "does_not_prove": [
            "metadata regime explanation",
            "causal source of Ob6/Ob8 failure",
            "universal subgroup law",
            "predictive observation classifier",
            "new mechanism",
        ],
        "next": ["4134_figure_ready_evidence_panels"],
        "artifacts": [
            "Output/4133/raw_metadata_by_ob.csv",
            "Output/4133/observation_master_table.csv",
            "Output/4133/heterogeneity_associations.csv",
            "Output/4133/leave_one_out_sensitivity.csv",
            "Output/4133/observation_classes.csv",
            "Output/4133/decision.json",
            "Output/4133/4133_summary.md",
        ]
        + figure_files,
    }
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2), encoding="utf-8")

    summary = dedent(
        f"""\
        # Node 4133 Observation Heterogeneity Map

        ## Question

        What structure is visible across the 19 observations after the positive
        and negative/boundary atlases are fixed?

        ## Gate Result

        ```text
        gate_result = {decision["gate_result"]}
        ```

        ## Main Interpretation

        Observation-level heterogeneity can be mapped descriptively. The main
        classes are robust survivor/diffuse-positive observations, fragile
        408x boundaries, stable 408x failures, and a fragile survivor. The
        association tests are small-n descriptive checks only.

        ## Class Counts

        {md_table([{"observation_class": k, "count": v} for k, v in class_counts.items()], ["observation_class", "count"])}

        ## Strongest Descriptive Associations

        {md_table(moderate.head(8).to_dict("records"), ["question", "association", "n", "spearman_rho", "spearman_pvalue_descriptive", "loo_rho_min", "loo_rho_max", "association_label"])}

        ## Metadata Status

        {md_table([decision["metadata_status"]], list(decision["metadata_status"].keys()))}

        ## Observation Classes

        {md_table(classes.to_dict("records"), ["ob", "observation_class", "route_positive_score", "408x_pass_class", "408x_robustness", "failure_boundary_class", "recording_condition", "recording_condition_verification_status", "boundary_flags"])}

        ## What This Does Not Prove

        {md_table([{"does_not_prove": x} for x in decision["does_not_prove"]], ["does_not_prove"])}

        ## Next Node

        `4134_figure_ready_evidence_panels`

        ## Artifacts

        - `Output/4133/raw_metadata_by_ob.csv`
        - `Output/4133/observation_master_table.csv`
        - `Output/4133/heterogeneity_associations.csv`
        - `Output/4133/leave_one_out_sensitivity.csv`
        - `Output/4133/observation_classes.csv`
        - `Output/4133/figures/4133_observation_route_matrix.png`
        - `Output/4133/figures/4133_t1_effect_vs_mean_swarm_size.png`
        - `Output/4133/figures/4133_t1_effect_vs_mean_track_length.png`
        - `Output/4133/figures/4133_history_abs_vs_t1_effect.png`
        - `Output/4133/figures/4133_route_score_by_observation_class.png`
        """
    )
    summary = summary.replace("\n        ", "\n").lstrip()
    (OUT / "4133_summary.md").write_text(summary, encoding="utf-8")

    print(json.dumps(decision, indent=2))
    print(f"Wrote 4133 outputs to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
