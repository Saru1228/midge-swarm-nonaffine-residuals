"""4087 failure-boundary sensitivity for local non-affine T1 failures.

This node tests whether the 4081c non-survival observations (Ob1/3/6/8)
remain negative under predefined sensitivity checks. It deliberately keeps the
same T1 metric and gate used by 4081/4082; only the neighborhood scale/lag,
event window length, and compact-state persistence definition are varied.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from textwrap import dedent

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_DIR = ROOT / "Experiment"
if str(EXPERIMENT_DIR) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_DIR))

import run_3045_residual_event_trigger_search as r3045  # noqa: E402
import run_4081_global_vs_local_geometry_ladder as r4081  # noqa: E402
from run_4001_geometric_baseline_residual_audit import (  # noqa: E402
    RunConfig as BaseRunConfig,
    resolve_data_dir,
)


OUT = ROOT / "Output" / "4087"
SRC_4081C = ROOT / "Output" / "4081c"
SRC_3045_FRAME = ROOT / "Output" / "3045" / "processed" / "frame_residual_signals.csv"

NODE = "4087_failure_boundary_sensitivity"
DATE = "2026-08-26"
RNG_SEED = 4087_0101

TARGET_ID = "T1_transition_tangential_residual"
LOCAL_METRIC = "local_tangential_speed_mean"
GAP_GATE = 0.03
P_GATE = 0.35
RATIO_GATE = 0.30

ROW_COLUMNS = [
    "ob",
    "sensitivity_family",
    "sensitivity_id",
    "k",
    "lag_sec",
    "prepost_sec",
    "min_run_sec",
    "n_events",
    "source",
    "b3_event_direction_abs_z",
    "local_event_direction_abs_z",
    "local_non_event_direction_abs_median_z",
    "local_event_minus_non_event_direction_z",
    "p_non_event_direction_ge_event",
    "local_to_b3_direction_ratio",
    "event_conditioned_local_gate",
    "geometry_ladder_reading",
]

OB_COLUMNS = [
    "ob",
    "baseline_pass_count",
    "baseline_total",
    "scale_timing_pass_count",
    "scale_timing_total",
    "window_pass_count",
    "window_total",
    "state_definition_pass_count",
    "state_definition_total",
    "any_rescue",
    "rescue_settings",
    "median_nonbaseline_gap",
    "failure_boundary_class",
    "interpretation",
]


def ensure_dirs() -> None:
    for path in (OUT, OUT / "tables", OUT / "figures", OUT / "cache", OUT / "conditions"):
        path.mkdir(parents=True, exist_ok=True)


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


def finite_median(values: list[float]) -> float:
    arr = np.asarray(values, dtype="float64")
    arr = arr[np.isfinite(arr)]
    return float(np.median(arr)) if arr.size else math.nan


def bool_from_csv(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def parse_int_list(text: str) -> list[int]:
    return [int(x.strip()) for x in text.split(",") if x.strip()]


def parse_float_list(text: str) -> list[float]:
    return [float(x.strip()) for x in text.split(",") if x.strip()]


def num_label(value: float) -> str:
    return f"{value:.3f}".replace(".", "p")


def condition_cache_path(ob: int, sensitivity_id: str) -> Path:
    clean = sensitivity_id.replace("=", "").replace(".", "p").replace(",", "_")
    return OUT / "conditions" / f"Ob{ob}_{clean}.json"


def frame_cache_path(ob: int, k: int, lag: float) -> Path:
    return OUT / "cache" / f"frame_Ob{ob}_k{k}_lag{num_label(lag)}.csv"


def read_4081c_t1_cache() -> pd.DataFrame:
    path = SRC_4081C / "full_geometry_ladder_rows.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing 4081c cache: {path}")
    rows = pd.read_csv(path)
    rows = rows[rows["target_id"] == TARGET_ID].copy()
    numeric_cols = [
        "ob",
        "k",
        "lag_sec",
        "n_events",
        "b3_event_direction_abs_z",
        "local_event_direction_abs_z",
        "local_non_event_direction_abs_median_z",
        "local_event_minus_non_event_direction_z",
        "p_non_event_direction_ge_event",
        "local_to_b3_direction_ratio",
    ]
    for col in numeric_cols:
        rows[col] = pd.to_numeric(rows[col], errors="coerce")
    rows["event_conditioned_local_gate"] = rows["event_conditioned_local_gate"].map(bool_from_csv)
    return rows


def failure_obs_from_4081c() -> list[int]:
    path = SRC_4081C / "ob_route_a_classification.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing 4081c classification: {path}")
    cls = pd.read_csv(path)
    cls["ob"] = pd.to_numeric(cls["ob"], errors="coerce").astype("int64")
    cls["t1_gate_any"] = cls["t1_gate_any"].map(bool_from_csv)
    return sorted(int(x) for x in cls.loc[~cls["t1_gate_any"], "ob"].tolist())


def b3_event_by_ob(cache: pd.DataFrame) -> dict[int, float]:
    out: dict[int, float] = {}
    for ob, d in cache.groupby("ob", sort=True):
        vals = pd.to_numeric(d["b3_event_direction_abs_z"], errors="coerce").to_numpy(dtype="float64")
        vals = vals[np.isfinite(vals)]
        out[int(ob)] = float(np.median(vals)) if vals.size else math.nan
    return out


def gate_row(
    *,
    ob: int,
    sensitivity_family: str,
    sensitivity_id: str,
    k: int,
    lag: float,
    prepost_sec: float,
    min_run_sec: float,
    n_events: int,
    source: str,
    b3_event: float,
    local_abs: float,
    null_med: float,
    p_ge: float,
) -> dict[str, object]:
    local_gap = local_abs - null_med if np.isfinite(local_abs) and np.isfinite(null_med) else math.nan
    ratio = local_abs / b3_event if np.isfinite(local_abs) and np.isfinite(b3_event) and b3_event > 1e-12 else math.nan
    gate = bool(
        np.isfinite(local_gap)
        and local_gap > GAP_GATE
        and np.isfinite(p_ge)
        and p_ge <= P_GATE
        and np.isfinite(ratio)
        and ratio >= RATIO_GATE
    )
    if gate:
        reading = "local_nonaffine_signal_survives_gate"
    elif np.isfinite(ratio) and ratio < RATIO_GATE:
        reading = "local_affine_largely_absorbs_b3_signal"
    elif np.isfinite(local_gap) and local_gap <= 0:
        reading = "local_nonaffine_not_event_conditioned"
    else:
        reading = "inconclusive"
    return {
        "ob": ob,
        "sensitivity_family": sensitivity_family,
        "sensitivity_id": sensitivity_id,
        "k": k,
        "lag_sec": lag,
        "prepost_sec": prepost_sec,
        "min_run_sec": min_run_sec,
        "n_events": int(n_events),
        "source": source,
        "b3_event_direction_abs_z": b3_event,
        "local_event_direction_abs_z": local_abs,
        "local_non_event_direction_abs_median_z": null_med,
        "local_event_minus_non_event_direction_z": local_gap,
        "p_non_event_direction_ge_event": p_ge,
        "local_to_b3_direction_ratio": ratio,
        "event_conditioned_local_gate": gate,
        "geometry_ladder_reading": reading,
    }


def row_from_4081c_cache(
    cache: pd.DataFrame,
    ob: int,
    sensitivity_family: str,
    sensitivity_id: str,
    k: int,
    lag: float,
    prepost_sec: float,
    min_run_sec: float,
) -> dict[str, object] | None:
    d = cache[(cache["ob"] == ob) & (cache["k"] == k) & (np.isclose(cache["lag_sec"], lag))]
    if d.empty:
        return None
    row = d.iloc[0]
    return gate_row(
        ob=ob,
        sensitivity_family=sensitivity_family,
        sensitivity_id=sensitivity_id,
        k=k,
        lag=lag,
        prepost_sec=prepost_sec,
        min_run_sec=min_run_sec,
        n_events=int(row["n_events"]),
        source="cached_4081c",
        b3_event=float(row["b3_event_direction_abs_z"]),
        local_abs=float(row["local_event_direction_abs_z"]),
        null_med=float(row["local_non_event_direction_abs_median_z"]),
        p_ge=float(row["p_non_event_direction_ge_event"]),
    )


def read_state_frame() -> pd.DataFrame:
    if not SRC_3045_FRAME.exists():
        raise FileNotFoundError(f"Missing 3045 processed frame: {SRC_3045_FRAME}")
    needed = {"ob", "dataset", "t", "spectral_set"}
    df = pd.read_csv(SRC_3045_FRAME, usecols=lambda c: c in needed, low_memory=False)
    missing = sorted(needed - set(df.columns))
    if missing:
        raise ValueError(f"Missing columns in {SRC_3045_FRAME}: {missing}")
    df["ob"] = pd.to_numeric(df["ob"], errors="coerce")
    df["t"] = pd.to_numeric(df["t"], errors="coerce")
    df = df.dropna(subset=["ob", "t"]).copy()
    df["ob"] = df["ob"].astype("int64")
    return df.sort_values(["ob", "t"], kind="mergesort").reset_index(drop=True)


def events_for_min_run(state_frame: pd.DataFrame, min_run_sec: float) -> pd.DataFrame:
    cfg = r3045.RunConfig(min_run_sec=min_run_sec)
    events = r3045.detect_transition_events(state_frame, cfg)
    if events.empty:
        return events
    for col in ["event_id", "ob", "event_t"]:
        events[col] = pd.to_numeric(events[col], errors="coerce")
    events = events.dropna(subset=["event_id", "ob", "event_t", "dataset", "event_type"]).copy()
    events["event_id"] = events["event_id"].astype("int64")
    events["ob"] = events["ob"].astype("int64")
    return events.sort_values(["ob", "event_t"], kind="mergesort").reset_index(drop=True)


def get_local_metric_frame(
    *,
    ob: int,
    k: int,
    lag: float,
    data_dir: Path,
    frame_stride: int,
    max_focals_per_frame: int,
    force: bool,
) -> pd.DataFrame:
    path = frame_cache_path(ob, k, lag)
    if path.exists() and not force:
        return pd.read_csv(path)
    dataset = f"Ob{ob}.txt"
    print(f"[4087] building frame Ob{ob} k={k} lag={lag:.3f}", flush=True)
    frame = r4081.build_local_metric_frame(ob, dataset, data_dir, k, lag, frame_stride, max_focals_per_frame)
    frame.to_csv(path, index=False)
    return frame


def compute_condition(
    *,
    ob: int,
    sensitivity_family: str,
    sensitivity_id: str,
    k: int,
    lag: float,
    prepost_sec: float,
    min_run_sec: float,
    events: pd.DataFrame,
    data_dir: Path,
    b3_by_ob: dict[int, float],
    frame_stride: int,
    max_focals_per_frame: int,
    n_replicates: int,
    exclusion_sec: float,
    force: bool,
) -> dict[str, object]:
    path = condition_cache_path(ob, sensitivity_id)
    if path.exists() and not force:
        return json.loads(path.read_text(encoding="utf-8"))

    events_ob = events[events["ob"] == ob].copy().reset_index(drop=True)
    if events_ob.empty:
        row = gate_row(
            ob=ob,
            sensitivity_family=sensitivity_family,
            sensitivity_id=sensitivity_id,
            k=k,
            lag=lag,
            prepost_sec=prepost_sec,
            min_run_sec=min_run_sec,
            n_events=0,
            source="computed_4087_no_events",
            b3_event=float(b3_by_ob.get(ob, math.nan)),
            local_abs=math.nan,
            null_med=math.nan,
            p_ge=math.nan,
        )
        write_json(path, row)
        return row

    frame = get_local_metric_frame(
        ob=ob,
        k=k,
        lag=lag,
        data_dir=data_dir,
        frame_stride=frame_stride,
        max_focals_per_frame=max_focals_per_frame,
        force=force,
    )
    arrays = r4081.build_arrays(frame)
    features = r4081.extract_features(arrays, events_ob, [LOCAL_METRIC], prepost_sec)
    n_events, local_abs = r4081.direction_abs(features, LOCAL_METRIC)
    rec = next(iter(arrays.values()))
    seed = RNG_SEED + ob * 1000 + k * 100 + int(round(lag * 1000)) + int(round(prepost_sec * 1000)) + int(round(min_run_sec * 1000))
    rng = np.random.default_rng(seed)
    null_vals = []
    for _ in range(n_replicates):
        sampled = r4081.sample_non_event_times(events_ob, rec["t"], rng, prepost_sec, exclusion_sec)
        nf = r4081.extract_features(arrays, sampled, [LOCAL_METRIC], prepost_sec)
        _, da = r4081.direction_abs(nf, LOCAL_METRIC)
        null_vals.append(da)
    null = np.asarray(null_vals, dtype="float64")
    null = null[np.isfinite(null)]
    null_med = float(np.median(null)) if null.size else math.nan
    p_ge = float(np.mean(null >= local_abs)) if null.size and np.isfinite(local_abs) else math.nan
    row = gate_row(
        ob=ob,
        sensitivity_family=sensitivity_family,
        sensitivity_id=sensitivity_id,
        k=k,
        lag=lag,
        prepost_sec=prepost_sec,
        min_run_sec=min_run_sec,
        n_events=int(n_events),
        source="computed_4087",
        b3_event=float(b3_by_ob.get(ob, math.nan)),
        local_abs=float(local_abs),
        null_med=null_med,
        p_ge=p_ge,
    )
    write_json(path, row)
    return row


def build_condition_rows(
    *,
    obs: list[int],
    data_dir: Path,
    cache_4081c: pd.DataFrame,
    b3_by_ob: dict[int, float],
    state_frame: pd.DataFrame,
    scale_k: list[int],
    timing_lag: list[float],
    window_prepost: list[float],
    min_run_values: list[float],
    frame_stride: int,
    max_focals_per_frame: int,
    n_replicates: int,
    exclusion_sec: float,
    force: bool,
) -> list[dict[str, object]]:
    events_by_min_run = {float(v): events_for_min_run(state_frame, float(v)) for v in sorted(set([0.20, *min_run_values]))}
    baseline_events = events_by_min_run[0.20]
    rows: list[dict[str, object]] = []

    for ob in obs:
        # Baseline rows from 4081c give the original failure state.
        for k in [8, 10]:
            sid = f"baseline_k{k}_lag0p100_window0p200_minrun0p200"
            cached = row_from_4081c_cache(cache_4081c, ob, "baseline", sid, k, 0.10, 0.20, 0.20)
            if cached is not None:
                rows.append(cached)

        # 4082-like robustness grid applied to the failure observations.
        for k in scale_k:
            sid = f"scale_k{k}_lag0p100_window0p200_minrun0p200"
            cached = row_from_4081c_cache(cache_4081c, ob, "scale_timing", sid, k, 0.10, 0.20, 0.20)
            if cached is not None and not force:
                rows.append(cached)
                continue
            rows.append(
                compute_condition(
                    ob=ob,
                    sensitivity_family="scale_timing",
                    sensitivity_id=sid,
                    k=k,
                    lag=0.10,
                    prepost_sec=0.20,
                    min_run_sec=0.20,
                    events=baseline_events,
                    data_dir=data_dir,
                    b3_by_ob=b3_by_ob,
                    frame_stride=frame_stride,
                    max_focals_per_frame=max_focals_per_frame,
                    n_replicates=n_replicates,
                    exclusion_sec=exclusion_sec,
                    force=force,
                )
            )
        for lag in timing_lag:
            sid = f"timing_k8_lag{num_label(lag)}_window0p200_minrun0p200"
            cached = row_from_4081c_cache(cache_4081c, ob, "scale_timing", sid, 8, lag, 0.20, 0.20)
            if cached is not None and not force:
                rows.append(cached)
                continue
            rows.append(
                compute_condition(
                    ob=ob,
                    sensitivity_family="scale_timing",
                    sensitivity_id=sid,
                    k=8,
                    lag=lag,
                    prepost_sec=0.20,
                    min_run_sec=0.20,
                    events=baseline_events,
                    data_dir=data_dir,
                    b3_by_ob=b3_by_ob,
                    frame_stride=frame_stride,
                    max_focals_per_frame=max_focals_per_frame,
                    n_replicates=n_replicates,
                    exclusion_sec=exclusion_sec,
                    force=force,
                )
            )

        # Event-window sensitivity with the original state definition.
        for prepost in window_prepost:
            sid = f"window_k8_lag0p100_window{num_label(prepost)}_minrun0p200"
            cached = row_from_4081c_cache(cache_4081c, ob, "window", sid, 8, 0.10, prepost, 0.20) if abs(prepost - 0.20) < 1e-9 else None
            if cached is not None and not force:
                rows.append(cached)
                continue
            rows.append(
                compute_condition(
                    ob=ob,
                    sensitivity_family="window",
                    sensitivity_id=sid,
                    k=8,
                    lag=0.10,
                    prepost_sec=prepost,
                    min_run_sec=0.20,
                    events=baseline_events,
                    data_dir=data_dir,
                    b3_by_ob=b3_by_ob,
                    frame_stride=frame_stride,
                    max_focals_per_frame=max_focals_per_frame,
                    n_replicates=n_replicates,
                    exclusion_sec=exclusion_sec,
                    force=force,
                )
            )

        # Compact-state persistence sensitivity with the original metric/window.
        for min_run in min_run_values:
            sid = f"state_k8_lag0p100_window0p200_minrun{num_label(min_run)}"
            cached = row_from_4081c_cache(cache_4081c, ob, "state_definition", sid, 8, 0.10, 0.20, min_run) if abs(min_run - 0.20) < 1e-9 else None
            if cached is not None and not force:
                rows.append(cached)
                continue
            rows.append(
                compute_condition(
                    ob=ob,
                    sensitivity_family="state_definition",
                    sensitivity_id=sid,
                    k=8,
                    lag=0.10,
                    prepost_sec=0.20,
                    min_run_sec=min_run,
                    events=events_by_min_run[float(min_run)],
                    data_dir=data_dir,
                    b3_by_ob=b3_by_ob,
                    frame_stride=frame_stride,
                    max_focals_per_frame=max_focals_per_frame,
                    n_replicates=n_replicates,
                    exclusion_sec=exclusion_sec,
                    force=force,
                )
            )

    # Remove duplicate baseline-equivalent rows within each family.
    return sorted(rows, key=lambda r: (int(r["ob"]), str(r["sensitivity_family"]), str(r["sensitivity_id"])))


def classify_ob(ob: int, rows: list[dict[str, object]]) -> dict[str, object]:
    d = [r for r in rows if int(r["ob"]) == ob]
    groups = {}
    for family in ["baseline", "scale_timing", "window", "state_definition"]:
        g = [r for r in d if str(r["sensitivity_family"]) == family]
        groups[family] = g
    counts = {
        family: (
            int(sum(bool(r["event_conditioned_local_gate"]) for r in g)),
            len(g),
        )
        for family, g in groups.items()
    }
    nonbaseline = [r for r in d if str(r["sensitivity_family"]) != "baseline"]
    rescue_rows = [r for r in nonbaseline if bool(r["event_conditioned_local_gate"])]
    rescue_settings = ", ".join(str(r["sensitivity_id"]) for r in rescue_rows)
    median_gap = finite_median([float(r["local_event_minus_non_event_direction_z"]) for r in nonbaseline])
    scale_pass, scale_total = counts["scale_timing"]
    window_pass, window_total = counts["window"]
    state_pass, state_total = counts["state_definition"]
    any_rescue = bool(rescue_rows)

    if not any_rescue:
        cls = "stable_failure_under_predefined_sensitivity"
        interp = "The observation remains negative across the predefined sensitivity checks."
    elif scale_pass >= 3:
        cls = "scale_timing_definition_sensitive_rescue"
        interp = "The observation becomes positive under multiple nearby scale/lag settings."
    elif window_pass >= 2:
        cls = "event_window_definition_sensitive_rescue"
        interp = "The observation becomes positive under multiple event-window choices."
    elif state_pass >= 2:
        cls = "state_definition_sensitive_rescue"
        interp = "The observation becomes positive under multiple compact-state persistence choices."
    else:
        cls = "fragile_narrow_setting_rescue"
        interp = "The observation has only sparse narrow-setting rescues and remains a boundary case."

    return {
        "ob": ob,
        "baseline_pass_count": counts["baseline"][0],
        "baseline_total": counts["baseline"][1],
        "scale_timing_pass_count": scale_pass,
        "scale_timing_total": scale_total,
        "window_pass_count": window_pass,
        "window_total": window_total,
        "state_definition_pass_count": state_pass,
        "state_definition_total": state_total,
        "any_rescue": any_rescue,
        "rescue_settings": rescue_settings,
        "median_nonbaseline_gap": median_gap,
        "failure_boundary_class": cls,
        "interpretation": interp,
    }


def make_figures(rows: pd.DataFrame, ob_classes: pd.DataFrame) -> None:
    fig_dir = OUT / "figures"
    plot_rows = rows[rows["sensitivity_family"] != "baseline"].copy()
    if not plot_rows.empty:
        order = (
            plot_rows[["sensitivity_family", "sensitivity_id"]]
            .drop_duplicates()
            .sort_values(["sensitivity_family", "sensitivity_id"])
        )
        order["label"] = order["sensitivity_family"] + "\n" + order["sensitivity_id"]
        label_lookup = dict(zip(order["sensitivity_id"], order["label"]))
        pivot = plot_rows.pivot_table(
            index="sensitivity_id",
            columns="ob",
            values="local_event_minus_non_event_direction_z",
            aggfunc="first",
        ).reindex(order["sensitivity_id"])
        fig, ax = plt.subplots(figsize=(10.5, max(5.5, 0.36 * len(pivot))), constrained_layout=True)
        im = ax.imshow(pivot.to_numpy(dtype="float64"), aspect="auto", cmap="RdYlGn", vmin=-0.30, vmax=0.35)
        ax.set_title("4087 failure observations: event-control gap")
        ax.set_xlabel("Observation")
        ax.set_ylabel("Sensitivity setting")
        ax.set_xticks(np.arange(len(pivot.columns)))
        ax.set_xticklabels([f"Ob{int(x)}" for x in pivot.columns])
        ax.set_yticks(np.arange(len(pivot.index)))
        ax.set_yticklabels([label_lookup.get(x, x) for x in pivot.index], fontsize=7)
        fig.colorbar(im, ax=ax, label="event-control gap")
        fig.savefig(fig_dir / "4087_condition_gap_heatmap.png", dpi=180)
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.4, 4.8), constrained_layout=True)
    x = np.arange(len(ob_classes))
    width = 0.25
    ax.bar(x - width, ob_classes["scale_timing_pass_count"], width=width, label="scale/lag", color="#2b7a78")
    ax.bar(x, ob_classes["window_pass_count"], width=width, label="window", color="#d97904")
    ax.bar(x + width, ob_classes["state_definition_pass_count"], width=width, label="state definition", color="#5c5c8a")
    ax.set_xticks(x)
    ax.set_xticklabels([f"Ob{int(v)}" for v in ob_classes["ob"]])
    ax.set_ylabel("passing settings")
    ax.set_title("4087 sensitivity rescues by observation")
    ax.grid(axis="y", color="#dddddd", linewidth=0.8)
    ax.legend(frameon=False)
    fig.savefig(fig_dir / "4087_pass_count_by_family.png", dpi=180)
    plt.close(fig)


def write_config(args: argparse.Namespace, obs: list[int]) -> None:
    config = dedent(
        f"""\
        node: {NODE}
        date: {DATE}
        node_type: robustness
        input_node: 4081c_full_observation_adjudication
        observations: {','.join(str(x) for x in obs)}
        target_id: {TARGET_ID}
        local_metric: {LOCAL_METRIC}
        gate:
          local_event_minus_non_event_direction_z: "> {GAP_GATE}"
          p_non_event_direction_ge_event: "<= {P_GATE}"
          local_to_b3_direction_ratio: ">= {RATIO_GATE}"
        scale_k: {args.scale_k}
        timing_lag_sec: {args.timing_lag}
        window_prepost_sec: {args.window_prepost}
        min_run_sec: {args.min_run_sec}
        frame_stride: {args.frame_stride}
        max_focals_per_frame: {args.max_focals_per_frame}
        n_non_event_replicates: {args.n_replicates}
        """
    )
    (OUT / "config.yaml").write_text(config, encoding="utf-8")


def write_summary(
    *,
    rows: list[dict[str, object]],
    classes: list[dict[str, object]],
    decision: dict[str, object],
) -> None:
    text = f"""# Node 4087 Summary

## Question

Can Ob1/Ob3/Ob6/Ob8 become T1 local non-affine survival cases under a
principled sensitivity test, or are they genuinely different from the robust
survivor class?

## Scope

This node does not search for new metrics. It keeps:

```text
target = {TARGET_ID}
local metric = {LOCAL_METRIC}
gate = gap > {GAP_GATE}, p <= {P_GATE}, local/B3 ratio >= {RATIO_GATE}
```

Only three predefined sensitivity families are tested:

- the 4082-like scale/lag grid applied to the failure observations;
- event pre/post window length;
- compact low/high state persistence threshold.

## Decision

`{decision["result"]}`

## Main Counts

```text
stable failure observations = {decision["stable_failure_count"]} / {decision["n_observations"]}
fragile narrow-setting rescues = {decision["fragile_narrow_rescue_count"]} / {decision["n_observations"]}
definition-sensitive rescues = {decision["definition_sensitive_rescue_count"]} / {decision["n_observations"]}
```

## Observation Boundary Classes

{md_table(classes, OB_COLUMNS)}

## Condition Rows

{md_table(rows, ROW_COLUMNS)}

## Interpretation

{decision["interpretation"]}

## Boundary

4087 can revise the meaning of the failure group, but it cannot turn a narrow
parameter rescue into a universal positive result. If a failure observation
passes only one or a few predefined settings, it remains a boundary case rather
than a full member of the 4082 robust survivor class.

## Next

`{decision["next"][0]}`

## Artifacts

- `Output/4087/condition_rows.csv`
- `Output/4087/ob_failure_boundary_sensitivity.csv`
- `Output/4087/figures/4087_condition_gap_heatmap.png`
- `Output/4087/figures/4087_pass_count_by_family.png`
"""
    (OUT / "4087_summary.md").write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default=BaseRunConfig.data_dir)
    parser.add_argument("--obs", default="failures", help="'failures' or comma-separated observation numbers.")
    parser.add_argument("--scale-k", default="6,8,10,12")
    parser.add_argument("--timing-lag", default="0.05,0.10,0.15")
    parser.add_argument("--window-prepost", default="0.15,0.20,0.30")
    parser.add_argument("--min-run-sec", default="0.15,0.20,0.25")
    parser.add_argument("--frame-stride", type=int, default=2)
    parser.add_argument("--max-focals-per-frame", type=int, default=24)
    parser.add_argument("--n-replicates", type=int, default=40)
    parser.add_argument("--exclusion-sec", type=float, default=0.80)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_dirs()
    data_dir = resolve_data_dir(BaseRunConfig(data_dir=args.data_dir))
    cache_4081c = read_4081c_t1_cache()
    b3_by_ob = b3_event_by_ob(cache_4081c)
    state_frame = read_state_frame()

    obs = failure_obs_from_4081c() if args.obs == "failures" else parse_int_list(args.obs)
    scale_k = parse_int_list(args.scale_k)
    timing_lag = parse_float_list(args.timing_lag)
    window_prepost = parse_float_list(args.window_prepost)
    min_run_values = parse_float_list(args.min_run_sec)

    write_config(args, obs)
    rows = build_condition_rows(
        obs=obs,
        data_dir=data_dir,
        cache_4081c=cache_4081c,
        b3_by_ob=b3_by_ob,
        state_frame=state_frame,
        scale_k=scale_k,
        timing_lag=timing_lag,
        window_prepost=window_prepost,
        min_run_values=min_run_values,
        frame_stride=args.frame_stride,
        max_focals_per_frame=args.max_focals_per_frame,
        n_replicates=args.n_replicates,
        exclusion_sec=args.exclusion_sec,
        force=args.force,
    )
    classes = [classify_ob(ob, rows) for ob in obs]
    classes = sorted(classes, key=lambda r: int(r["ob"]))

    write_csv(OUT / "condition_rows.csv", rows, ROW_COLUMNS)
    write_csv(OUT / "tables" / "condition_rows.csv", rows, ROW_COLUMNS)
    write_json(OUT / "condition_rows.json", rows)
    write_csv(OUT / "ob_failure_boundary_sensitivity.csv", classes, OB_COLUMNS)
    write_csv(OUT / "tables" / "ob_failure_boundary_sensitivity.csv", classes, OB_COLUMNS)
    write_json(OUT / "ob_failure_boundary_sensitivity.json", classes)

    rows_df = pd.DataFrame(rows)
    cls_df = pd.DataFrame(classes)
    make_figures(rows_df, cls_df)

    stable_count = int((cls_df["failure_boundary_class"] == "stable_failure_under_predefined_sensitivity").sum())
    fragile_count = int((cls_df["failure_boundary_class"] == "fragile_narrow_setting_rescue").sum())
    definition_sensitive_count = int(
        cls_df["failure_boundary_class"].isin(
            [
                "scale_timing_definition_sensitive_rescue",
                "event_window_definition_sensitive_rescue",
                "state_definition_sensitive_rescue",
            ]
        ).sum()
    )
    if definition_sensitive_count >= 2:
        result = "boundary_failure_group_partly_definition_sensitive"
        interpretation = (
            "At least two failure observations can be rescued by predefined settings, so the early-failure boundary "
            "is partly a definition/window issue and should be kept as a subclass rather than a hard negative class."
        )
        next_node = "4088_bounded_408x_synthesis_with_failure_subclass"
    elif stable_count == len(obs):
        result = "support_stable_failure_boundary_under_predefined_sensitivity"
        interpretation = (
            "The failure observations remain negative across the predefined checks. This supports treating Ob1/Ob3/Ob6/Ob8 "
            "as a real boundary of the 408x positive class, not as a simple window or threshold artifact."
        )
        next_node = "4088_bounded_408x_synthesis"
    else:
        result = "boundary_failure_group_mostly_stable_with_fragile_rescues"
        interpretation = (
            "Some failure observations pass only narrow predefined settings. These are not robust enough to merge into "
            "the survivor class, but they show the boundary is not perfectly sharp."
        )
        next_node = "4088_bounded_408x_synthesis_with_failure_boundary"

    decision = {
        "node": NODE,
        "date": DATE,
        "result": result,
        "n_observations": len(obs),
        "observations": obs,
        "stable_failure_count": stable_count,
        "fragile_narrow_rescue_count": fragile_count,
        "definition_sensitive_rescue_count": definition_sensitive_count,
        "class_counts": cls_df["failure_boundary_class"].value_counts().to_dict(),
        "interpretation": interpretation,
        "next": [next_node],
        "artifacts": [
            "Output/4087/condition_rows.csv",
            "Output/4087/ob_failure_boundary_sensitivity.csv",
            "Output/4087/figures/4087_condition_gap_heatmap.png",
            "Output/4087/figures/4087_pass_count_by_family.png",
        ],
    }
    write_json(OUT / "decision.json", decision)
    write_summary(rows=rows, classes=classes, decision=decision)
    print(json.dumps(decision, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
