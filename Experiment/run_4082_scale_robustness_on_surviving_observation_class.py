"""4082 scale robustness on the 4081c surviving observation class.

This node tests whether the 4081c T1 local non-affine survival result is a
single-scale accident. It reuses the frozen 4081c rows for k=8,10 at lag=0.10
and computes only nearby new conditions.
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


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_DIR = ROOT / "Experiment"
if str(EXPERIMENT_DIR) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_DIR))

import run_4002a_residual_spatial_structure_audit as r4002a  # noqa: E402
import run_4081_global_vs_local_geometry_ladder as r4081  # noqa: E402
from run_4001_geometric_baseline_residual_audit import (  # noqa: E402
    RunConfig as BaseRunConfig,
    resolve_data_dir,
)


OUT = ROOT / "Output" / "4082"
SRC_4081C = ROOT / "Output" / "4081c"
NODE = "4082_scale_robustness_on_surviving_observation_class"
DATE = "2026-08-25"
RNG_SEED = 4082_0101

TARGET_ID = "T1_transition_tangential_residual"
LOCAL_METRIC = "local_tangential_speed_mean"
GAP_GATE = 0.03
P_GATE = 0.35
RATIO_GATE = 0.30

ROW_COLUMNS = [
    "ob",
    "k",
    "lag_sec",
    "axis",
    "source",
    "n_events",
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
    "n_events",
    "scale_pass_count",
    "scale_total",
    "scale_pass_fraction",
    "timing_pass_count",
    "timing_total",
    "timing_pass_fraction",
    "median_scale_gap",
    "median_timing_gap",
    "robustness_class",
    "interpretation",
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


def finite_median(values: list[float]) -> float:
    arr = np.asarray(values, dtype="float64")
    arr = arr[np.isfinite(arr)]
    return float(np.median(arr)) if arr.size else math.nan


def bool_from_csv(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def lag_label(lag: float) -> str:
    return f"{lag:.3f}".replace(".", "p")


def condition_path(ob: int, k: int, lag: float) -> Path:
    return OUT / "conditions" / f"Ob{ob}_k{k}_lag{lag_label(lag)}.json"


def read_4081c_cache() -> pd.DataFrame:
    rows = pd.read_csv(SRC_4081C / "full_geometry_ladder_rows.csv")
    rows = rows[rows["target_id"] == TARGET_ID].copy()
    for col in [
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
    ]:
        rows[col] = pd.to_numeric(rows[col], errors="coerce")
    rows["event_conditioned_local_gate"] = rows["event_conditioned_local_gate"].map(bool_from_csv)
    return rows


def survival_obs_from_4081c() -> list[int]:
    cls = pd.read_csv(SRC_4081C / "ob_route_a_classification.csv")
    cls["ob"] = pd.to_numeric(cls["ob"], errors="coerce").astype("int64")
    cls["t1_gate_any"] = cls["t1_gate_any"].map(bool_from_csv)
    return sorted(int(x) for x in cls.loc[cls["t1_gate_any"], "ob"].tolist())


def b3_event_by_ob(cache: pd.DataFrame) -> dict[int, float]:
    out: dict[int, float] = {}
    for ob, d in cache.groupby("ob", sort=True):
        vals = pd.to_numeric(d["b3_event_direction_abs_z"], errors="coerce").to_numpy(dtype="float64")
        vals = vals[np.isfinite(vals)]
        out[int(ob)] = float(np.median(vals)) if vals.size else math.nan
    return out


def gate_row(
    ob: int,
    k: int,
    lag: float,
    axis: str,
    source: str,
    n_events: int,
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
        reading = "local_nonaffine_signal_survives_pilot"
    elif np.isfinite(ratio) and ratio < RATIO_GATE:
        reading = "local_affine_largely_absorbs_b3_signal"
    elif np.isfinite(local_gap) and local_gap <= 0:
        reading = "local_nonaffine_not_event_conditioned"
    else:
        reading = "inconclusive"
    return {
        "ob": ob,
        "k": k,
        "lag_sec": lag,
        "axis": axis,
        "source": source,
        "n_events": n_events,
        "b3_event_direction_abs_z": b3_event,
        "local_event_direction_abs_z": local_abs,
        "local_non_event_direction_abs_median_z": null_med,
        "local_event_minus_non_event_direction_z": local_gap,
        "p_non_event_direction_ge_event": p_ge,
        "local_to_b3_direction_ratio": ratio,
        "event_conditioned_local_gate": gate,
        "geometry_ladder_reading": reading,
    }


def row_from_4081c_cache(cache: pd.DataFrame, ob: int, k: int, lag: float, axis: str) -> dict[str, object] | None:
    d = cache[(cache["ob"] == ob) & (cache["k"] == k) & (np.isclose(cache["lag_sec"], lag))]
    if d.empty:
        return None
    row = d.iloc[0]
    return gate_row(
        ob=ob,
        k=k,
        lag=lag,
        axis=axis,
        source="cached_4081c",
        n_events=int(row["n_events"]),
        b3_event=float(row["b3_event_direction_abs_z"]),
        local_abs=float(row["local_event_direction_abs_z"]),
        null_med=float(row["local_non_event_direction_abs_median_z"]),
        p_ge=float(row["p_non_event_direction_ge_event"]),
    )


def compute_condition(
    ob: int,
    k: int,
    lag: float,
    axis: str,
    data_dir: Path,
    events_all: pd.DataFrame,
    b3_by_ob: dict[int, float],
    frame_stride: int,
    max_focals_per_frame: int,
    n_replicates: int,
    prepost_sec: float,
    exclusion_sec: float,
    force: bool,
) -> dict[str, object]:
    path = condition_path(ob, k, lag)
    if path.exists() and not force:
        return json.loads(path.read_text(encoding="utf-8"))

    events_ob = events_all[events_all["ob"] == ob].copy().reset_index(drop=True)
    if events_ob.empty:
        raise RuntimeError(f"No events for Ob{ob}")
    dataset = str(events_ob.iloc[0]["dataset"])
    print(f"[4082] Ob{ob} k={k} lag={lag:.3f}: computing local T1 metric", flush=True)
    frame = r4081.build_local_metric_frame(ob, dataset, data_dir, k, lag, frame_stride, max_focals_per_frame)
    arrays = r4081.build_arrays(frame)
    features = r4081.extract_features(arrays, events_ob, [LOCAL_METRIC], prepost_sec)
    n_events, local_abs = r4081.direction_abs(features, LOCAL_METRIC)
    rec = next(iter(arrays.values()))
    rng = np.random.default_rng(RNG_SEED + ob * 1000 + k * 10 + int(round(lag * 1000)))
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
        k=k,
        lag=lag,
        axis=axis,
        source="computed_4082",
        n_events=int(n_events),
        b3_event=float(b3_by_ob.get(ob, math.nan)),
        local_abs=float(local_abs),
        null_med=null_med,
        p_ge=p_ge,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path, row)
    return row


def classify_ob(ob: int, rows: list[dict[str, object]], scale_k: list[int], timing_lag: list[float]) -> dict[str, object]:
    scale_rows = [
        r
        for r in rows
        if int(r["ob"]) == ob and str(r["axis"]) in {"scale", "both"} and int(r["k"]) in scale_k and abs(float(r["lag_sec"]) - 0.10) < 1e-9
    ]
    timing_rows = [
        r
        for r in rows
        if int(r["ob"]) == ob and str(r["axis"]) in {"timing", "both"} and int(r["k"]) == 8 and any(abs(float(r["lag_sec"]) - x) < 1e-9 for x in timing_lag)
    ]
    scale_pass = int(sum(bool(r["event_conditioned_local_gate"]) for r in scale_rows))
    timing_pass = int(sum(bool(r["event_conditioned_local_gate"]) for r in timing_rows))
    scale_total = len(scale_rows)
    timing_total = len(timing_rows)
    scale_frac = scale_pass / scale_total if scale_total else math.nan
    timing_frac = timing_pass / timing_total if timing_total else math.nan
    scale_gap = finite_median([float(r["local_event_minus_non_event_direction_z"]) for r in scale_rows])
    timing_gap = finite_median([float(r["local_event_minus_non_event_direction_z"]) for r in timing_rows])
    n_events = int(max([int(r["n_events"]) for r in rows if int(r["ob"]) == ob], default=0))

    if scale_pass >= 3 and timing_pass >= 2:
        cls = "robust_scale_and_timing"
        interp = "T1 survives most nearby scale and timing checks."
    elif scale_pass >= 3 and timing_pass < 2:
        cls = "scale_robust_timing_sensitive"
        interp = "T1 survives scale checks but is sensitive to lag around k=8."
    elif scale_pass < 3 and timing_pass >= 2:
        cls = "scale_sensitive_timing_robust"
        interp = "T1 survives timing checks but is sensitive to neighbor scale."
    else:
        cls = "fragile_or_boundary"
        interp = "T1 survival is weak under nearby robustness checks."
    return {
        "ob": ob,
        "n_events": n_events,
        "scale_pass_count": scale_pass,
        "scale_total": scale_total,
        "scale_pass_fraction": scale_frac,
        "timing_pass_count": timing_pass,
        "timing_total": timing_total,
        "timing_pass_fraction": timing_frac,
        "median_scale_gap": scale_gap,
        "median_timing_gap": timing_gap,
        "robustness_class": cls,
        "interpretation": interp,
    }


def make_figures(rows: pd.DataFrame, ob_classes: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt

    fig_dir = OUT / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    scale = rows[(rows["axis"].isin(["scale", "both"])) & (np.isclose(rows["lag_sec"], 0.10))].copy()
    scale_pivot = scale.pivot_table(index="k", columns="ob", values="local_event_minus_non_event_direction_z", aggfunc="first")
    fig, ax = plt.subplots(figsize=(11, 4.8), constrained_layout=True)
    im = ax.imshow(scale_pivot.to_numpy(dtype="float64"), aspect="auto", cmap="RdYlGn", vmin=-0.25, vmax=0.70)
    ax.set_title("4082 scale robustness: T1 local event-control gap")
    ax.set_xlabel("Observation")
    ax.set_ylabel("k at lag=0.10")
    ax.set_xticks(np.arange(len(scale_pivot.columns)))
    ax.set_xticklabels([f"Ob{int(x)}" for x in scale_pivot.columns], rotation=45, ha="right")
    ax.set_yticks(np.arange(len(scale_pivot.index)))
    ax.set_yticklabels([str(int(x)) for x in scale_pivot.index])
    fig.colorbar(im, ax=ax, label="event-control gap")
    fig.savefig(fig_dir / "4082_scale_gap_heatmap.png", dpi=180)
    plt.close(fig)

    timing = rows[(rows["axis"].isin(["timing", "both"])) & (rows["k"] == 8)].copy()
    timing_pivot = timing.pivot_table(index="lag_sec", columns="ob", values="local_event_minus_non_event_direction_z", aggfunc="first")
    fig, ax = plt.subplots(figsize=(11, 4.2), constrained_layout=True)
    im = ax.imshow(timing_pivot.to_numpy(dtype="float64"), aspect="auto", cmap="RdYlGn", vmin=-0.25, vmax=0.70)
    ax.set_title("4082 timing robustness: T1 local event-control gap")
    ax.set_xlabel("Observation")
    ax.set_ylabel("lag at k=8")
    ax.set_xticks(np.arange(len(timing_pivot.columns)))
    ax.set_xticklabels([f"Ob{int(x)}" for x in timing_pivot.columns], rotation=45, ha="right")
    ax.set_yticks(np.arange(len(timing_pivot.index)))
    ax.set_yticklabels([f"{x:.2f}" for x in timing_pivot.index])
    fig.colorbar(im, ax=ax, label="event-control gap")
    fig.savefig(fig_dir / "4082_timing_gap_heatmap.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 4.8), constrained_layout=True)
    x = np.arange(len(ob_classes))
    ax.bar(x - 0.18, ob_classes["scale_pass_fraction"], width=0.36, label="scale", color="#2b7a78")
    ax.bar(x + 0.18, ob_classes["timing_pass_fraction"], width=0.36, label="timing", color="#d97904")
    ax.axhline(0.75, color="#555555", linestyle="--", linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels([f"Ob{int(v)}" for v in ob_classes["ob"]], rotation=45, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("pass fraction")
    ax.set_title("4082 per-observation robustness fractions")
    ax.grid(axis="y", color="#dddddd", linewidth=0.8)
    ax.legend(frameon=False)
    fig.savefig(fig_dir / "4082_ob_robustness_fractions.png", dpi=180)
    plt.close(fig)


def parse_float_list(text: str) -> list[float]:
    return [float(x.strip()) for x in text.split(",") if x.strip()]


def parse_int_list(text: str) -> list[int]:
    return [int(x.strip()) for x in text.split(",") if x.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default=BaseRunConfig.data_dir)
    parser.add_argument("--obs", default="survivors")
    parser.add_argument("--scale-k", default="6,8,10,12")
    parser.add_argument("--timing-lag", default="0.05,0.10,0.15")
    parser.add_argument("--timing-k", type=int, default=8)
    parser.add_argument("--frame-stride", type=int, default=2)
    parser.add_argument("--max-focals-per-frame", type=int, default=24)
    parser.add_argument("--n-replicates", type=int, default=40)
    parser.add_argument("--prepost-sec", type=float, default=0.20)
    parser.add_argument("--exclusion-sec", type=float, default=0.80)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    (OUT / "conditions").mkdir(parents=True, exist_ok=True)
    data_dir = resolve_data_dir(BaseRunConfig(data_dir=args.data_dir))
    cache = read_4081c_cache()
    b3_by_ob = b3_event_by_ob(cache)
    events = r4002a.read_events()

    if args.obs == "survivors":
        obs = survival_obs_from_4081c()
    else:
        obs = parse_int_list(args.obs)
    scale_k = parse_int_list(args.scale_k)
    timing_lag = parse_float_list(args.timing_lag)

    rows: list[dict[str, object]] = []
    for ob in obs:
        # Scale axis: k varies at frozen lag=0.10.
        for k in scale_k:
            cached = row_from_4081c_cache(cache, ob, k, 0.10, "scale")
            if cached is not None and not args.force:
                cached["axis"] = "scale" if not (k == args.timing_k and any(abs(0.10 - x) < 1e-9 for x in timing_lag)) else "both"
                rows.append(cached)
                continue
            axis = "scale" if not (k == args.timing_k and any(abs(0.10 - x) < 1e-9 for x in timing_lag)) else "both"
            rows.append(
                compute_condition(
                    ob,
                    k,
                    0.10,
                    axis,
                    data_dir,
                    events,
                    b3_by_ob,
                    args.frame_stride,
                    args.max_focals_per_frame,
                    args.n_replicates,
                    args.prepost_sec,
                    args.exclusion_sec,
                    args.force,
                )
            )
        # Timing axis: lag varies at frozen k=8.
        for lag in timing_lag:
            if abs(lag - 0.10) < 1e-9:
                continue
            cached = row_from_4081c_cache(cache, ob, args.timing_k, lag, "timing")
            if cached is not None and not args.force:
                rows.append(cached)
                continue
            rows.append(
                compute_condition(
                    ob,
                    args.timing_k,
                    lag,
                    "timing",
                    data_dir,
                    events,
                    b3_by_ob,
                    args.frame_stride,
                    args.max_focals_per_frame,
                    args.n_replicates,
                    args.prepost_sec,
                    args.exclusion_sec,
                    args.force,
                )
            )

    rows = sorted(rows, key=lambda r: (int(r["ob"]), str(r["axis"]), float(r["lag_sec"]), int(r["k"])))
    classes = [classify_ob(ob, rows, scale_k, timing_lag) for ob in obs]
    classes = sorted(classes, key=lambda r: int(r["ob"]))

    write_csv(OUT / "scale_timing_condition_rows.csv", rows, ROW_COLUMNS)
    write_csv(OUT / "tables" / "scale_timing_condition_rows.csv", rows, ROW_COLUMNS)
    write_json(OUT / "scale_timing_condition_rows.json", rows)
    write_csv(OUT / "ob_scale_timing_robustness.csv", classes, OB_COLUMNS)
    write_csv(OUT / "tables" / "ob_scale_timing_robustness.csv", classes, OB_COLUMNS)
    write_json(OUT / "ob_scale_timing_robustness.json", classes)

    rows_df = pd.DataFrame(rows)
    cls_df = pd.DataFrame(classes)
    make_figures(rows_df, cls_df)

    robust_count = int((cls_df["robustness_class"] == "robust_scale_and_timing").sum())
    weak_count = int((cls_df["robustness_class"] == "fragile_or_boundary").sum())
    median_scale_frac = float(np.nanmedian(cls_df["scale_pass_fraction"].to_numpy(dtype="float64")))
    median_timing_frac = float(np.nanmedian(cls_df["timing_pass_fraction"].to_numpy(dtype="float64")))
    if robust_count >= 10 and median_scale_frac >= 0.75 and median_timing_frac >= 2 / 3:
        result = "support_scale_timing_robust_t1_survival_with_boundary_cases"
        next_node = "4082b_early_failure_condition_or_artifact_audit"
    elif robust_count >= 7:
        result = "boundary_partial_scale_timing_robustness"
        next_node = "4082b_early_failure_condition_or_artifact_audit"
    else:
        result = "boundary_scale_sensitive_nonaffinity"
        next_node = "route_a_scale_sensitive_synthesis"

    decision = {
        "node": NODE,
        "date": DATE,
        "result": result,
        "n_observations": len(obs),
        "observation_class_input": "4081c T1 survivors",
        "scale_k": scale_k,
        "scale_lag_sec": 0.10,
        "timing_k": args.timing_k,
        "timing_lag_sec": timing_lag,
        "robust_scale_and_timing_count": robust_count,
        "fragile_or_boundary_count": weak_count,
        "median_scale_pass_fraction": median_scale_frac,
        "median_timing_pass_fraction": median_timing_frac,
        "class_counts": cls_df["robustness_class"].value_counts().to_dict(),
        "interpretation": (
            "T1 survival is tested as a robustness property over nearby k and lag values, "
            "not as a new metric search."
        ),
        "next": [next_node],
        "artifacts": [
            "Output/4082/scale_timing_condition_rows.csv",
            "Output/4082/ob_scale_timing_robustness.csv",
            "Output/4082/figures/4082_scale_gap_heatmap.png",
            "Output/4082/figures/4082_timing_gap_heatmap.png",
            "Output/4082/figures/4082_ob_robustness_fractions.png",
        ],
    }
    write_json(OUT / "decision.json", decision)

    config = dedent(
        f"""\
        node: {NODE}
        date: {DATE}
        node_type: robustness
        input_node: 4081c_full_observation_adjudication_before_4082
        observations: {','.join(str(x) for x in obs)}
        scale_k: {args.scale_k}
        scale_lag_sec: 0.10
        timing_k: {args.timing_k}
        timing_lag_sec: {args.timing_lag}
        frame_stride: {args.frame_stride}
        max_focals_per_frame: {args.max_focals_per_frame}
        n_non_event_replicates: {args.n_replicates}
        """
    )
    (OUT / "config.yaml").write_text(config, encoding="utf-8")

    summary = dedent(
        f"""\
        # Node 4082 Summary

        ## Question

        Does the 4081c T1 local non-affine survival result remain under nearby
        local scale and lag choices, or is it a single-parameter accident?

        ## Inputs

        - `Output/4081c/ob_route_a_classification.csv`
        - `Output/4081c/full_geometry_ladder_rows.csv`
        - raw trajectories through the configured data directory

        ## Run

        ```text
        observations = 4081c T1 survivors ({len(obs)} observations)
        scale axis = k {scale_k} at lag 0.10 sec
        timing axis = lag {timing_lag} at k {args.timing_k}
        matched non-event replicates = {args.n_replicates}
        frame_stride = {args.frame_stride}
        ```

        Cached 4081c rows were reused for `k=8,10; lag=0.10`.

        ## Decision

        `{result}`

        ## Main Counts

        ```text
        robust scale and timing observations = {robust_count} / {len(obs)}
        fragile or boundary observations = {weak_count} / {len(obs)}
        median scale pass fraction = {median_scale_frac:.4g}
        median timing pass fraction = {median_timing_frac:.4g}
        ```

        ## Observation Robustness

        {md_table(classes, OB_COLUMNS)}

        ## Interpretation

        This node does not add new biological mechanism variables. It asks only
        whether the 4081c T1 result persists when local scale and lag are moved
        near the original setting.

        ## Next

        `{next_node}`

        ## Artifacts

        - `Output/4082/scale_timing_condition_rows.csv`
        - `Output/4082/ob_scale_timing_robustness.csv`
        - `Output/4082/figures/4082_scale_gap_heatmap.png`
        - `Output/4082/figures/4082_timing_gap_heatmap.png`
        - `Output/4082/figures/4082_ob_robustness_fractions.png`
        """
    ).lstrip()
    summary = "\n".join(line[8:] if line.startswith("        ") else line for line in summary.splitlines()) + "\n"
    (OUT / "4082_summary.md").write_text(summary, encoding="utf-8")
    print(f"Wrote 4082 outputs to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
