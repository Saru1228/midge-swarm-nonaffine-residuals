"""4090B residual-vector and continuous-state feasibility check.

This is a technical gate before 4090. It checks whether the frozen 4088 T1
observable can be connected to vector-level local non-affine residual samples
and whether the continuous compact-density coordinate C(t), dC/dt can be traced
from upstream 3032/3045 artifacts.
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

import run_4081_global_vs_local_geometry_ladder as r4081  # noqa: E402
from run_4001_geometric_baseline_residual_audit import (  # noqa: E402
    RunConfig as BaseRunConfig,
    median_dt,
    resolve_data_dir,
)


OUT = ROOT / "Output" / "4090B"
DATE = "2026-08-26"
NODE = "4090B_residual_vector_and_continuous_state_feasibility_check"

SRC_4090A_DECISION = ROOT / "Output" / "4090A" / "decision.json"
SRC_4088_DECISION = ROOT / "Output" / "4088" / "decision.json"
SRC_3045_FRAME = ROOT / "Output" / "3045" / "processed" / "frame_residual_signals.csv"
SRC_3032_PARTITION = ROOT / "Output" / "3032" / "processed" / "raw_spectral_partition_summary.csv"

VECTOR_SAMPLE_COLUMNS = [
    "ob",
    "dataset",
    "t",
    "t1",
    "k",
    "lag_sec",
    "lag_dt",
    "focal_id",
    "neighbor_id",
    "focal_radius",
    "neighbor_rank",
    "condition_number",
    "resid_vx",
    "resid_vy",
    "resid_vz",
    "resid_radial",
    "resid_tan_vx",
    "resid_tan_vy",
    "resid_tan_vz",
    "resid_tan_norm",
    "resid_norm_sq",
]

STATE_COVERAGE_COLUMNS = [
    "ob",
    "dataset",
    "n_frames",
    "t_min",
    "t_max",
    "dt_median",
    "spectral_set_nonnull_fraction",
    "density_rms_z3045_finite_fraction",
    "density_rms_smooth3045_finite_fraction",
    "dCdt_finite_fraction",
    "C_primary",
    "dCdt_source",
]

FEASIBILITY_COLUMNS = [
    "item",
    "status",
    "evidence",
    "boundary",
    "recommended_4090_handling",
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


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(to_jsonable(data), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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


def finite_fraction(values: pd.Series | np.ndarray) -> float:
    arr = np.asarray(values, dtype="float64")
    if arr.size == 0:
        return math.nan
    return float(np.isfinite(arr).mean())


def load_state_frame() -> pd.DataFrame:
    needed = {
        "ob",
        "dataset",
        "t",
        "spectral_set",
        "density_rms",
        "density_rms_z3045",
        "density_rms_smooth3045",
        "r_rms_z3045",
        "r_rms_smooth3045",
    }
    if not SRC_3045_FRAME.exists():
        raise FileNotFoundError(f"Missing continuous state source: {SRC_3045_FRAME}")
    df = pd.read_csv(SRC_3045_FRAME, usecols=lambda c: c in needed, low_memory=False)
    df["ob"] = pd.to_numeric(df["ob"], errors="coerce")
    df["t"] = pd.to_numeric(df["t"], errors="coerce")
    for col in ["density_rms", "density_rms_z3045", "density_rms_smooth3045", "r_rms_z3045", "r_rms_smooth3045"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["ob", "t"]).copy()
    df["ob"] = df["ob"].astype("int64")
    return df.sort_values(["ob", "t"], kind="mergesort").reset_index(drop=True)


def add_state_derivative(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["dCdt_density_rms_smooth3045"] = math.nan
    for ob, idx in out.groupby("ob", sort=True).groups.items():
        d = out.loc[idx].sort_values("t")
        t = d["t"].to_numpy(dtype="float64")
        c = d["density_rms_smooth3045"].to_numpy(dtype="float64")
        ok = np.isfinite(t) & np.isfinite(c)
        vals = np.full(len(d), math.nan, dtype="float64")
        if int(ok.sum()) >= 3:
            vals[ok] = np.gradient(c[ok], t[ok])
        out.loc[d.index, "dCdt_density_rms_smooth3045"] = vals
    return out


def state_coverage(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for ob, d in df.groupby("ob", sort=True):
        t = d["t"].to_numpy(dtype="float64")
        rows.append(
            {
                "ob": int(ob),
                "dataset": str(d["dataset"].iloc[0]),
                "n_frames": int(len(d)),
                "t_min": float(np.nanmin(t)),
                "t_max": float(np.nanmax(t)),
                "dt_median": median_dt(t),
                "spectral_set_nonnull_fraction": float(d["spectral_set"].notna().mean()),
                "density_rms_z3045_finite_fraction": finite_fraction(d["density_rms_z3045"]),
                "density_rms_smooth3045_finite_fraction": finite_fraction(d["density_rms_smooth3045"]),
                "dCdt_finite_fraction": finite_fraction(d["dCdt_density_rms_smooth3045"]),
                "C_primary": "density_rms_z3045",
                "dCdt_source": "gradient(density_rms_smooth3045, t)",
            }
        )
    return pd.DataFrame(rows)


def partition_evidence() -> dict[str, object]:
    if not SRC_3032_PARTITION.exists():
        return {
            "status": "missing",
            "evidence": f"missing {SRC_3032_PARTITION.relative_to(ROOT)}",
        }
    df = pd.read_csv(SRC_3032_PARTITION)
    if df.empty:
        return {"status": "empty", "evidence": "partition summary is empty"}
    row = df.iloc[0].to_dict()
    return {
        "status": "available",
        "partition_id": row.get("partition_id", ""),
        "eigen_rank": row.get("eigen_rank", ""),
        "interpretive_axis": row.get("interpretive_axis", ""),
        "evidence": "3032 raw spectral partition summary traces high set to compact-density axis.",
    }


def build_residual_vector_sample(
    *,
    ob: int,
    data_dir: Path,
    k: int,
    lag_sec: float,
    frame_stride: int,
    max_frames: int,
    max_focals: int,
) -> pd.DataFrame:
    dataset = f"Ob{ob}.txt"
    df = r4081.load_ob_df(ob, data_dir, dataset)
    times = np.asarray(sorted(df["t"].unique()), dtype="float64")
    frames = {float(t): d.sort_values("id").copy() for t, d in df.groupby("t", sort=True)}
    dt = median_dt(times)
    lag_steps = max(1, int(round(lag_sec / dt)))
    idxs = np.arange(0, len(times) - lag_steps, frame_stride, dtype=int)
    if len(idxs) > max_frames:
        idxs = np.linspace(0, len(idxs) - 1, max_frames).round().astype(int)
        idxs = np.unique(np.arange(0, len(times) - lag_steps, frame_stride, dtype=int)[idxs])
    rng = np.random.default_rng(4090_002 + ob * 100 + k)
    rows: list[dict[str, object]] = []
    for idx in idxs:
        t0 = float(times[idx])
        t1 = float(times[idx + lag_steps])
        ids0, pos0 = r4081.frame_arrays(frames[t0])
        ids1, pos1 = r4081.frame_arrays(frames[t1])
        id_to_idx0 = {int(v): i for i, v in enumerate(ids0)}
        id_to_idx1 = {int(v): i for i, v in enumerate(ids1)}
        common = np.asarray([v for v in ids0 if int(v) in id_to_idx1], dtype="int64")
        if common.size == 0:
            continue
        focals = rng.choice(common, size=min(max_focals, common.size), replace=False) if common.size > max_focals else common
        center = np.nanmean(pos0, axis=0)
        for focal_id in focals:
            focal_id = int(focal_id)
            i0 = id_to_idx0[focal_id]
            i1 = id_to_idx1[focal_id]
            rel_all = pos0 - pos0[i0]
            dist = np.linalg.norm(rel_all, axis=1)
            order = np.argsort(dist)
            neigh_ids = [int(ids0[j]) for j in order if int(ids0[j]) != focal_id and int(ids0[j]) in id_to_idx1][:k]
            if len(neigh_ids) < 4:
                continue
            a_rows = []
            b_rows = []
            kept_ids = []
            for nid in neigh_ids:
                j0 = id_to_idx0[nid]
                j1 = id_to_idx1[nid]
                r0 = pos0[j0] - pos0[i0]
                r1 = pos1[j1] - pos1[i1]
                a_rows.append(r0)
                b_rows.append(r1 - r0)
                kept_ids.append(nid)
            A = np.asarray(a_rows, dtype="float64")
            B = np.asarray(b_rows, dtype="float64")
            if not (np.isfinite(A).all() and np.isfinite(B).all()):
                continue
            try:
                _, s, _ = np.linalg.svd(A, full_matrices=False)
                if s.size < 3 or s[-1] <= 1e-12:
                    continue
                cond = float(s[0] / s[-1])
                J, _, _, _ = np.linalg.lstsq(A, B, rcond=None)
            except np.linalg.LinAlgError:
                continue
            resid = (B - A @ J) / (lag_steps * dt)
            focal_rel = pos0[i0] - center
            focal_radius = float(np.linalg.norm(focal_rel))
            if not math.isfinite(focal_radius) or focal_radius <= 1e-12:
                continue
            radial_unit = focal_rel / focal_radius
            radial = resid @ radial_unit
            tan = resid - radial[:, None] * radial_unit[None, :]
            tan_norm = np.sqrt(np.maximum(np.sum(tan * tan, axis=1), 0.0))
            norm_sq = np.sum(resid * resid, axis=1)
            for rank, nid in enumerate(kept_ids, start=1):
                rv = resid[rank - 1]
                tv = tan[rank - 1]
                if not (np.isfinite(rv).all() and np.isfinite(tv).all()):
                    continue
                rows.append(
                    {
                        "ob": ob,
                        "dataset": dataset,
                        "t": t0,
                        "t1": t1,
                        "k": k,
                        "lag_sec": lag_sec,
                        "lag_dt": lag_steps * dt,
                        "focal_id": focal_id,
                        "neighbor_id": int(nid),
                        "focal_radius": focal_radius,
                        "neighbor_rank": rank,
                        "condition_number": cond,
                        "resid_vx": float(rv[0]),
                        "resid_vy": float(rv[1]),
                        "resid_vz": float(rv[2]),
                        "resid_radial": float(radial[rank - 1]),
                        "resid_tan_vx": float(tv[0]),
                        "resid_tan_vy": float(tv[1]),
                        "resid_tan_vz": float(tv[2]),
                        "resid_tan_norm": float(tan_norm[rank - 1]),
                        "resid_norm_sq": float(norm_sq[rank - 1]),
                    }
                )
    return pd.DataFrame(rows)


def make_figures(state_df: pd.DataFrame, sample: pd.DataFrame) -> None:
    fig_dir = OUT / "figures"
    fig, ax = plt.subplots(figsize=(9, 4.8), constrained_layout=True)
    d = state_df[state_df["ob"] == int(sample["ob"].iloc[0])].copy() if not sample.empty else state_df[state_df["ob"] == 2]
    ax.plot(d["t"], d["density_rms_z3045"], color="#4c78a8", linewidth=0.9, label="density_rms_z3045")
    ax.plot(d["t"], d["density_rms_smooth3045"], color="#f58518", linewidth=1.1, label="density_rms_smooth3045")
    ax.set_xlabel("time")
    ax.set_ylabel("C(t)")
    ax.set_title("4090B continuous compact-density coordinate trace")
    ax.grid(color="#dddddd", linewidth=0.8)
    ax.legend(frameon=False)
    fig.savefig(fig_dir / "4090B_continuous_state_trace.png", dpi=180)
    plt.close(fig)

    if not sample.empty:
        fig, ax = plt.subplots(figsize=(7.2, 4.8), constrained_layout=True)
        ax.hist(sample["resid_tan_norm"], bins=40, color="#1f9d55", edgecolor="#ffffff")
        ax.set_xlabel("resid_tan_norm")
        ax.set_ylabel("count")
        ax.set_title("4090B vector-level residual sample")
        ax.grid(axis="y", color="#dddddd", linewidth=0.8)
        fig.savefig(fig_dir / "4090B_vector_sample_tangential_norm.png", dpi=180)
        plt.close(fig)


def feasibility_table(
    *,
    sample: pd.DataFrame,
    coverage: pd.DataFrame,
    partition: dict[str, object],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    vector_status = "available_by_recomputation" if not sample.empty else "unavailable"
    rows.append(
        {
            "item": "vector_level_local_nonaffine_residual",
            "status": vector_status,
            "evidence": (
                f"sample rows exported = {len(sample)} using 4081 local-affine equations; "
                "current 4081 outputs save frame-level aggregates, not this vector table."
            ),
            "boundary": (
                "The vector unit is focal-neighborhood neighbor residual, matching the 4081 all_tangential aggregate. "
                "It is not yet a unique focal-individual residual vector."
            ),
            "recommended_4090_handling": (
                "Use this vector-level source with explicit unit label, or aggregate to focal-neighborhood before modeling."
            ),
        }
    )
    min_c = float(coverage["density_rms_z3045_finite_fraction"].min()) if not coverage.empty else math.nan
    min_dc = float(coverage["dCdt_finite_fraction"].min()) if not coverage.empty else math.nan
    state_status = "available" if math.isfinite(min_c) and min_c >= 0.95 and math.isfinite(min_dc) and min_dc >= 0.95 else "partial"
    rows.append(
        {
            "item": "continuous_compact_density_coordinate",
            "status": state_status,
            "evidence": (
                f"C source = density_rms_z3045; min finite C fraction = {min_c:.3f}; "
                f"min finite dC/dt fraction = {min_dc:.3f}; partition evidence = {partition.get('status')}"
            ),
            "boundary": "C is a traced compact-density coordinate, not a newly optimized 4090 score.",
            "recommended_4090_handling": "Use density_rms_z3045 as C(t) and gradient(density_rms_smooth3045,t) as dC/dt.",
        }
    )
    rows.append(
        {
            "item": "metadata_for_recording_order_or_batch",
            "status": "unavailable",
            "evidence": "4090A found no recording day/session/camera metadata in existing outputs.",
            "boundary": "Do not call observation index a confirmed acquisition batch variable.",
            "recommended_4090_handling": "Keep observation identity and 4088 boundary strata explicit in grouped validation.",
        }
    )
    return rows


def decide(rows: list[dict[str, object]]) -> dict[str, object]:
    status = {row["item"]: row["status"] for row in rows}
    if status.get("vector_level_local_nonaffine_residual") == "unavailable":
        gate = "B2_vector_residual_unavailable"
        next_node = "proxy_only_or_rebuild_4081_vector_export_before_4090"
        interp = "Strict moment classification should stop until vector-level residuals can be exported."
    elif status.get("continuous_compact_density_coordinate") in {"available", "partial"}:
        gate = "B1_vector_available_with_unit_boundary_and_C_available"
        next_node = "4090_continuous_moment_classification_with_vector_unit_note"
        interp = (
            "Vector-level residual samples are recomputable from 4081 equations, and C,dC are traceable from 3045. "
            "4090 can proceed, but must label the vector unit as focal-neighborhood neighbor residual unless a "
            "unique focal-individual residual definition is implemented."
        )
    else:
        gate = "B2_continuous_state_unavailable"
        next_node = "reconstruct_compact_state_before_4090"
        interp = "C,dC cannot be traced reliably; 4090 should not proceed as a continuous-state test."
    return {
        "node": NODE,
        "date": DATE,
        "node_type": "technical_gate",
        "upstream_node": "4090A_observation_regime_boundary_audit",
        "gate_result": gate,
        "interpretation": interp,
        "next": [next_node],
        "does_not_prove": [
            "first-vs-second moment dominance",
            "state-dependent stochastic mechanism",
            "batch artifact",
            "unique individual focal residual vector without additional definition",
        ],
        "artifacts": [
            "Output/4090B/technical_feasibility_table.csv",
            "Output/4090B/continuous_state_coverage.csv",
            "Output/4090B/residual_vector_sample.csv",
            "Output/4090B/figures/4090B_continuous_state_trace.png",
            "Output/4090B/figures/4090B_vector_sample_tangential_norm.png",
            "Output/4090B/4090B_summary.md",
        ],
    }


def write_summary(
    *,
    feasibility: list[dict[str, object]],
    coverage: pd.DataFrame,
    sample: pd.DataFrame,
    partition: dict[str, object],
    decision: dict[str, object],
) -> None:
    coverage_display = coverage.copy()
    for col in coverage_display.columns:
        if pd.api.types.is_numeric_dtype(coverage_display[col]):
            coverage_display[col] = coverage_display[col].round(4)
    sample_stats = {
        "sample_rows": int(len(sample)),
        "sample_ob": int(sample["ob"].iloc[0]) if not sample.empty else "",
        "median_resid_tan_norm": float(sample["resid_tan_norm"].median()) if not sample.empty else math.nan,
        "median_condition_number": float(sample["condition_number"].median()) if not sample.empty else math.nan,
        "unique_focals": int(sample["focal_id"].nunique()) if not sample.empty else 0,
        "unique_neighbors": int(sample["neighbor_id"].nunique()) if not sample.empty else 0,
    }
    text = f"""# Node 4090B Summary

## Question

Can 4090 recover the two required inputs?

```text
1. vector-level local non-affine residual samples
2. continuous compact-density C(t) and dC/dt
```

## Why this node exists after 4090A

4090A routed the workflow forward with an unconfirmed observation-sequence
boundary. Before fitting mean-vs-variance models, 4090B checks whether the
objects needed for that model exist without redefining the upstream T1 target.

## Frozen Upstream Target

```text
T1 = local tangential non-affine residual
baseline = local affine geometry
```

## Technical Feasibility

{md_table(feasibility, FEASIBILITY_COLUMNS)}

## Continuous State Source

Partition evidence:

```json
{json.dumps(to_jsonable(partition), ensure_ascii=False, indent=2)}
```

Coverage:

{md_table(coverage_display.to_dict("records"), STATE_COVERAGE_COLUMNS)}

## Residual Vector Sample

```json
{json.dumps(to_jsonable(sample_stats), ensure_ascii=False, indent=2)}
```

The sample is written to `Output/4090B/residual_vector_sample.csv`.

## Gate Evaluation

```text
gate_result = {decision["gate_result"]}
```

{decision["interpretation"]}

## Boundary

The currently reproducible vector unit is:

```text
focal-neighborhood neighbor residual vector
```

This matches how 4081/4088 built `all_tangential`, but it is not yet a unique
focal-individual vector. 4090 must state this explicitly, or add a separate
aggregation step that freezes how neighbor residual vectors become focal-level
observations.

## What This Does NOT Prove

{md_table([{"does_not_prove": x} for x in decision["does_not_prove"]], ["does_not_prove"])}

## Decision

`{decision["gate_result"]}`

## Next Node

`{decision["next"][0]}`

## Artifacts

- `Output/4090B/technical_feasibility_table.csv`
- `Output/4090B/continuous_state_coverage.csv`
- `Output/4090B/residual_vector_sample.csv`
- `Output/4090B/figures/4090B_continuous_state_trace.png`
- `Output/4090B/figures/4090B_vector_sample_tangential_norm.png`
"""
    (OUT / "4090B_summary.md").write_text(text, encoding="utf-8")


def write_config(args: argparse.Namespace) -> None:
    text = dedent(
        f"""\
        node: {NODE}
        date: {DATE}
        node_type: technical_gate
        upstream_node: 4090A_observation_regime_boundary_audit
        sample_observation: {args.sample_ob}
        k: {args.k}
        lag_sec: {args.lag_sec}
        frame_stride: {args.frame_stride}
        max_frames: {args.max_frames}
        max_focals: {args.max_focals}
        C_primary: density_rms_z3045
        dCdt_source: gradient(density_rms_smooth3045,t)
        """
    )
    (OUT / "config.yaml").write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default=BaseRunConfig.data_dir)
    parser.add_argument("--sample-ob", type=int, default=2)
    parser.add_argument("--k", type=int, default=8)
    parser.add_argument("--lag-sec", type=float, default=0.10)
    parser.add_argument("--frame-stride", type=int, default=100)
    parser.add_argument("--max-frames", type=int, default=40)
    parser.add_argument("--max-focals", type=int, default=8)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_dirs()
    write_config(args)
    data_dir = resolve_data_dir(BaseRunConfig(data_dir=args.data_dir))

    state_df = add_state_derivative(load_state_frame())
    coverage = state_coverage(state_df)
    partition = partition_evidence()
    sample = build_residual_vector_sample(
        ob=args.sample_ob,
        data_dir=data_dir,
        k=args.k,
        lag_sec=args.lag_sec,
        frame_stride=args.frame_stride,
        max_frames=args.max_frames,
        max_focals=args.max_focals,
    )
    feasibility = feasibility_table(sample=sample, coverage=coverage, partition=partition)
    decision = decide(feasibility)
    make_figures(state_df, sample)

    write_csv(OUT / "technical_feasibility_table.csv", feasibility, FEASIBILITY_COLUMNS)
    write_csv(OUT / "tables" / "technical_feasibility_table.csv", feasibility, FEASIBILITY_COLUMNS)
    write_csv(OUT / "continuous_state_coverage.csv", coverage.to_dict("records"), STATE_COVERAGE_COLUMNS)
    write_csv(OUT / "tables" / "continuous_state_coverage.csv", coverage.to_dict("records"), STATE_COVERAGE_COLUMNS)
    write_csv(OUT / "residual_vector_sample.csv", sample.to_dict("records"), VECTOR_SAMPLE_COLUMNS)
    write_csv(OUT / "tables" / "residual_vector_sample.csv", sample.to_dict("records"), VECTOR_SAMPLE_COLUMNS)
    write_json(OUT / "technical_feasibility_table.json", feasibility)
    write_json(OUT / "continuous_state_coverage.json", coverage.to_dict("records"))
    write_json(OUT / "decision.json", decision)
    write_summary(feasibility=feasibility, coverage=coverage, sample=sample, partition=partition, decision=decision)
    print(json.dumps(to_jsonable(decision), ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
