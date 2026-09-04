"""4085b phase-space projection of the T1 edge/core signal.

This diagnostic node follows 4085/4086. It does not claim an attractor. It
projects event-aligned trajectories into a small state space:

    compactness proxy x diffuse local non-affinity x edge/core contrast

The purpose is to visualize whether the 4085 timing and 4086 signed
heterogeneity have a coherent geometric form before routing to failure-boundary
or synthesis nodes.
"""

from __future__ import annotations

import argparse
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
OUT = ROOT / "Output" / "4085b"
SRC_4084 = ROOT / "Output" / "4084"
SRC_4085 = ROOT / "Output" / "4085"
SRC_4086 = ROOT / "Output" / "4086"
FRAME_3045 = ROOT / "Output" / "3045" / "processed" / "frame_residual_signals.csv"
NODE = "4085b_phase_space_projection_of_t1_edge_core_signal"
DATE = "2026-08-26"

VARIABLES = [
    "all_tangential",
    "shell_edge_minus_core",
    "shell_core_tangential",
    "shell_edge_tangential",
]

SAMPLE_COLUMNS = [
    "event_id",
    "ob",
    "dataset",
    "event_t",
    "event_type",
    "relative_time_sec",
    "abs_time_sec",
    "compact_density_resid_z",
    "radius_resid_z",
    "all_tangential",
    "shell_edge_minus_core",
    "shell_core_tangential",
    "shell_edge_tangential",
    "signed_class",
]

TRAJECTORY_COLUMNS = [
    "event_type",
    "relative_time_sec",
    "n_ob",
    "compact_density_resid_z",
    "radius_resid_z",
    "all_tangential",
    "shell_edge_minus_core",
    "shell_core_tangential",
    "shell_edge_tangential",
]

METRIC_COLUMNS = [
    "metric",
    "value",
    "interpretation",
]


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in columns})


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def finite_median(values: pd.Series | np.ndarray | list[float]) -> float:
    arr = np.asarray(values, dtype="float64")
    arr = arr[np.isfinite(arr)]
    return float(np.median(arr)) if arr.size else math.nan


def md_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    if not rows:
        return "_No rows._"
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


def read_obs(arg: str) -> list[int]:
    if arg.lower() in {"4084", "4085", "robust", "robust-survivors"}:
        d = pd.read_csv(SRC_4084 / "ob_spatial_taxonomy.csv")
        d["ob"] = pd.to_numeric(d["ob"], errors="coerce").astype("int64")
        return sorted(int(x) for x in d["ob"].tolist())
    if "-" in arg and "," not in arg:
        a, b = arg.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in arg.split(",") if x.strip()]


def load_signed_classes() -> dict[int, str]:
    path = SRC_4086 / "ob_signed_classification.csv"
    if not path.exists():
        return {}
    d = pd.read_csv(path)
    d["ob"] = pd.to_numeric(d["ob"], errors="coerce").astype("int64")
    return {int(row.ob): str(row.signed_class) for row in d.itertuples(index=False)}


def load_frame_3045(obs: list[int]) -> dict[int, pd.DataFrame]:
    if not FRAME_3045.exists():
        raise FileNotFoundError(f"Missing compact-state frame table: {FRAME_3045}")
    usecols = ["ob", "dataset", "t", "density_rms_resid3045", "r_rms_resid3045"]
    d = pd.read_csv(FRAME_3045, usecols=usecols)
    d["ob"] = pd.to_numeric(d["ob"], errors="coerce").astype("int64")
    out: dict[int, pd.DataFrame] = {}
    for ob in obs:
        out[ob] = d[d["ob"].eq(ob)].sort_values("t").reset_index(drop=True)
    return out


def pivot_event_samples(ob: int) -> pd.DataFrame:
    path = SRC_4085 / "per_ob" / f"Ob{ob}" / "event_aligned_samples.csv"
    if not path.exists():
        raise FileNotFoundError(f"Run 4085 first; missing {path}")
    d = pd.read_csv(path)
    d = d[d["variable"].isin(VARIABLES)].copy()
    pivot = d.pivot_table(
        index=["event_id", "ob", "dataset", "event_t", "event_type", "relative_time_sec"],
        columns="variable",
        values="value_z",
        aggfunc="median",
    ).reset_index()
    pivot.columns.name = None
    return pivot


def add_compact_coordinates(samples: pd.DataFrame, frame: pd.DataFrame) -> pd.DataFrame:
    out = samples.copy()
    out["abs_time_sec"] = pd.to_numeric(out["event_t"], errors="coerce") + pd.to_numeric(out["relative_time_sec"], errors="coerce")
    t = frame["t"].to_numpy(dtype="float64")
    if t.size < 2:
        out["compact_density_resid_z"] = math.nan
        out["radius_resid_z"] = math.nan
        return out
    target = out["abs_time_sec"].to_numpy(dtype="float64")
    for src, dst in [
        ("density_rms_resid3045", "compact_density_resid_z"),
        ("r_rms_resid3045", "radius_resid_z"),
    ]:
        x = pd.to_numeric(frame[src], errors="coerce").to_numpy(dtype="float64")
        ok = np.isfinite(t) & np.isfinite(x)
        if int(ok.sum()) < 2:
            out[dst] = math.nan
            continue
        y = np.full(target.shape, np.nan, dtype="float64")
        valid = (target >= np.nanmin(t[ok])) & (target <= np.nanmax(t[ok]))
        y[valid] = np.interp(target[valid], t[ok], x[ok])
        out[dst] = y
    return out


def build_samples(obs: list[int]) -> pd.DataFrame:
    frames = load_frame_3045(obs)
    signed = load_signed_classes()
    parts = []
    for ob in obs:
        print(f"[4085b] Ob{ob}: building phase-space samples", flush=True)
        samples = pivot_event_samples(ob)
        samples = add_compact_coordinates(samples, frames[ob])
        samples["signed_class"] = signed.get(ob, "")
        parts.append(samples)
    out = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
    for col in SAMPLE_COLUMNS:
        if col not in out.columns:
            out[col] = math.nan if col not in {"signed_class", "event_type", "dataset"} else ""
    return out[SAMPLE_COLUMNS].sort_values(["ob", "event_id", "relative_time_sec"]).reset_index(drop=True)


def build_ob_balanced_trajectory(samples: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = [
        "compact_density_resid_z",
        "radius_resid_z",
        "all_tangential",
        "shell_edge_minus_core",
        "shell_core_tangential",
        "shell_edge_tangential",
    ]
    per_ob = (
        samples.groupby(["ob", "event_type", "relative_time_sec"], as_index=False)[numeric_cols]
        .median(numeric_only=True)
        .dropna(subset=["relative_time_sec"])
    )
    rows: list[dict[str, object]] = []
    for (event_type, rel_t), g in per_ob.groupby(["event_type", "relative_time_sec"], sort=True):
        row = {
            "event_type": event_type,
            "relative_time_sec": float(rel_t),
            "n_ob": int(g["ob"].nunique()),
        }
        for col in numeric_cols:
            row[col] = finite_median(g[col])
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["event_type", "relative_time_sec"]).reset_index(drop=True)


def phase_mean(traj: pd.DataFrame, event_type: str, rel_lo: float, rel_hi: float, variable: str) -> float:
    d = traj[
        traj["event_type"].eq(event_type)
        & (traj["relative_time_sec"] >= rel_lo)
        & (traj["relative_time_sec"] <= rel_hi)
    ]
    return finite_median(d[variable])


def signed_area(x: np.ndarray, y: np.ndarray) -> float:
    ok = np.isfinite(x) & np.isfinite(y)
    x = x[ok]
    y = y[ok]
    if x.size < 3:
        return math.nan
    return float(0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))


def compute_metrics(traj: pd.DataFrame) -> list[dict[str, object]]:
    l_pre = phase_mean(traj, "low_to_high", -0.25, 0.00, "all_tangential")
    h_pre = phase_mean(traj, "high_to_low", -0.25, 0.00, "all_tangential")
    l_edge_pre = phase_mean(traj, "low_to_high", -0.25, 0.00, "shell_edge_minus_core")
    h_edge_pre = phase_mean(traj, "high_to_low", -0.25, 0.00, "shell_edge_minus_core")
    rows = [
        {
            "metric": "near_pre_all_tangential_low_to_high",
            "value": l_pre,
            "interpretation": "ob-balanced median low-to-high all_tangential in near-pre phase",
        },
        {
            "metric": "near_pre_all_tangential_high_to_low",
            "value": h_pre,
            "interpretation": "ob-balanced median high-to-low all_tangential in near-pre phase",
        },
        {
            "metric": "near_pre_all_tangential_signed_separation",
            "value": l_pre - h_pre if np.isfinite(l_pre) and np.isfinite(h_pre) else math.nan,
            "interpretation": "low-to-high minus high-to-low separation in the diffuse timing coordinate",
        },
        {
            "metric": "near_pre_edge_core_low_to_high",
            "value": l_edge_pre,
            "interpretation": "ob-balanced median low-to-high edge/core contrast in near-pre phase",
        },
        {
            "metric": "near_pre_edge_core_high_to_low",
            "value": h_edge_pre,
            "interpretation": "ob-balanced median high-to-low edge/core contrast in near-pre phase",
        },
    ]
    for event_type in ["low_to_high", "high_to_low"]:
        d = traj[traj["event_type"].eq(event_type)].sort_values("relative_time_sec")
        rows.append(
            {
                "metric": f"phase_space_loop_area_all_vs_edge_{event_type}",
                "value": signed_area(
                    d["all_tangential"].to_numpy(dtype="float64"),
                    d["shell_edge_minus_core"].to_numpy(dtype="float64"),
                ),
                "interpretation": "diagnostic 2D loop area, not an attractor metric",
            }
        )
    return rows


def make_figures(samples: pd.DataFrame, traj: pd.DataFrame) -> None:
    fig_dir = OUT / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    colors = {"low_to_high": "#2f6f9f", "high_to_low": "#b45f5f"}

    fig, ax = plt.subplots(figsize=(7.2, 6.2), constrained_layout=True)
    for event_type, d in traj.groupby("event_type", sort=True):
        d = d.sort_values("relative_time_sec")
        ax.plot(d["all_tangential"], d["shell_edge_minus_core"], color=colors.get(event_type, "#555555"), lw=2, label=event_type)
        sc = ax.scatter(
            d["all_tangential"],
            d["shell_edge_minus_core"],
            c=d["relative_time_sec"],
            cmap="coolwarm",
            s=40,
            edgecolor="#222222",
            linewidth=0.4,
            zorder=3,
        )
        if len(d) >= 2:
            ax.annotate("", xy=(d["all_tangential"].iloc[-1], d["shell_edge_minus_core"].iloc[-1]), xytext=(d["all_tangential"].iloc[-2], d["shell_edge_minus_core"].iloc[-2]), arrowprops={"arrowstyle": "->", "color": colors.get(event_type, "#555555")})
    ax.axhline(0, color="#999999", linewidth=0.8)
    ax.axvline(0, color="#999999", linewidth=0.8)
    ax.set_xlabel("all_tangential local non-affinity (z)")
    ax.set_ylabel("shell_edge_minus_core contrast (z)")
    ax.set_title("4085b phase-space projection: diffuse vs edge/core")
    ax.legend(frameon=False)
    fig.colorbar(sc, ax=ax, label="relative time (sec)")
    fig.savefig(fig_dir / "4085b_all_tangential_vs_edge_core_phase_space.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 6.2), constrained_layout=True)
    for event_type, d in traj.groupby("event_type", sort=True):
        d = d.sort_values("relative_time_sec")
        ax.plot(d["compact_density_resid_z"], d["all_tangential"], color=colors.get(event_type, "#555555"), lw=2, label=event_type)
        ax.scatter(
            d["compact_density_resid_z"],
            d["all_tangential"],
            c=d["relative_time_sec"],
            cmap="coolwarm",
            s=40,
            edgecolor="#222222",
            linewidth=0.4,
            zorder=3,
        )
    ax.axhline(0, color="#999999", linewidth=0.8)
    ax.axvline(0, color="#999999", linewidth=0.8)
    ax.set_xlabel("compact density residual z")
    ax.set_ylabel("all_tangential local non-affinity (z)")
    ax.set_title("4085b compactness vs diffuse local non-affinity")
    ax.legend(frameon=False)
    fig.savefig(fig_dir / "4085b_compactness_vs_all_tangential.png", dpi=180)
    plt.close(fig)

    fig = plt.figure(figsize=(8.2, 6.4), constrained_layout=True)
    ax = fig.add_subplot(111, projection="3d")
    for event_type, d in traj.groupby("event_type", sort=True):
        d = d.sort_values("relative_time_sec")
        ax.plot(
            d["compact_density_resid_z"],
            d["all_tangential"],
            d["shell_edge_minus_core"],
            color=colors.get(event_type, "#555555"),
            lw=2,
            label=event_type,
        )
        ax.scatter(
            d["compact_density_resid_z"],
            d["all_tangential"],
            d["shell_edge_minus_core"],
            c=d["relative_time_sec"],
            cmap="coolwarm",
            s=28,
            depthshade=False,
        )
    ax.set_xlabel("compact density resid z")
    ax.set_ylabel("all_tangential")
    ax.set_zlabel("edge-core")
    ax.set_title("4085b 3D diagnostic projection")
    ax.legend(frameon=False)
    fig.savefig(fig_dir / "4085b_3d_phase_space_projection.png", dpi=180)
    plt.close(fig)


def decide(metrics: list[dict[str, object]]) -> dict[str, object]:
    lookup = {row["metric"]: float(row["value"]) for row in metrics}
    sep = lookup.get("near_pre_all_tangential_signed_separation", math.nan)
    if np.isfinite(sep) and abs(sep) >= 0.25:
        result = "diagnostic_phase_space_supports_signed_diffuse_near_pre_separation"
        interpretation = (
            "The phase-space projection visually supports 4086's signed diffuse near-pre separation, "
            "but it remains a diagnostic projection rather than attractor evidence."
        )
    else:
        result = "diagnostic_phase_space_weak_signed_separation"
        interpretation = (
            "The phase-space projection does not add strong signed separation beyond the 4086 tables."
        )
    return {
        "node": NODE,
        "date": DATE,
        "result": result,
        "interpretation": interpretation,
        "attractor_claim": "not_supported_or_tested",
        "next": ["4087_failure_boundary_sensitivity_or_4088_bounded_synthesis"],
        "artifacts": [
            "Output/4085b/phase_space_event_samples.csv",
            "Output/4085b/phase_space_trajectory_by_event_type.csv",
            "Output/4085b/phase_space_metrics.csv",
            "Output/4085b/figures/4085b_all_tangential_vs_edge_core_phase_space.png",
            "Output/4085b/figures/4085b_compactness_vs_all_tangential.png",
            "Output/4085b/figures/4085b_3d_phase_space_projection.png",
        ],
    }


def write_config(args: argparse.Namespace, obs: list[int]) -> None:
    text = dedent(
        f"""\
        node: {NODE}
        date: {DATE}
        node_type: diagnostic_projection
        input_nodes:
          - 4085_event_phase_profile_of_t1_signal
          - 4086_signed_direction_and_state_decomposition
        observations: {','.join(str(x) for x in obs)}
        compact_coordinate: density_rms_resid3045
        variables: {','.join(VARIABLES)}
        attractor_test: false
        """
    )
    (OUT / "config.yaml").write_text(text, encoding="utf-8")


def write_summary(decision: dict[str, object], metrics: list[dict[str, object]]) -> None:
    text = dedent(
        f"""\
        # Node 4085b Summary

        ## Question

        What does the 4085/4086 signal look like as a low-dimensional diagnostic
        phase-space projection?

        ## Important Scope Limit

        This is not an attractor test. It does not estimate dimension,
        recurrence, Lyapunov exponents, or invariant sets. It is only a
        projection of event-aligned trajectories into a small interpretable
        coordinate system.

        ## Coordinates

        ```text
        x = compact_density_resid_z from Output/3045
        y = all_tangential local non-affinity from Output/4085
        z = shell_edge_minus_core from Output/4085
        color = relative time around transition
        line groups = low_to_high and high_to_low
        ```

        ## Decision

        `{decision["result"]}`

        ## Main Reading

        {decision["interpretation"]}

        ## Metrics

        {md_table(metrics, METRIC_COLUMNS)}

        ## Next

        `{decision["next"][0]}`

        ## Artifacts

        - `Output/4085b/phase_space_event_samples.csv`
        - `Output/4085b/phase_space_trajectory_by_event_type.csv`
        - `Output/4085b/phase_space_metrics.csv`
        - `Output/4085b/figures/4085b_all_tangential_vs_edge_core_phase_space.png`
        - `Output/4085b/figures/4085b_compactness_vs_all_tangential.png`
        - `Output/4085b/figures/4085b_3d_phase_space_projection.png`
        """
    ).lstrip()
    summary = "\n".join(line[8:] if line.startswith("        ") else line for line in text.splitlines()) + "\n"
    (OUT / "4085b_summary.md").write_text(summary, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--obs", default="4084")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    obs = read_obs(args.obs)
    write_config(args, obs)
    samples = build_samples(obs)
    traj = build_ob_balanced_trajectory(samples)
    metrics = compute_metrics(traj)
    decision = decide(metrics)

    samples.to_csv(OUT / "phase_space_event_samples.csv", index=False)
    samples.to_csv(OUT / "tables" / "phase_space_event_samples.csv", index=False)
    traj.to_csv(OUT / "phase_space_trajectory_by_event_type.csv", index=False)
    traj.to_csv(OUT / "tables" / "phase_space_trajectory_by_event_type.csv", index=False)
    write_csv(OUT / "phase_space_metrics.csv", metrics, METRIC_COLUMNS)
    write_csv(OUT / "tables" / "phase_space_metrics.csv", metrics, METRIC_COLUMNS)
    write_json(OUT / "decision.json", decision)
    make_figures(samples, traj)
    write_summary(decision, metrics)
    print(f"Wrote 4085b outputs to {OUT.relative_to(ROOT)}")
    print(json.dumps(decision, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
