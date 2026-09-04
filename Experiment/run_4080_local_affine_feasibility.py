"""4080 local affine feasibility smoke test.

This node checks whether local affine deformation tensors are numerically
identifiable in the midge swarm data before using D2min/non-affine language.
It is a feasibility node only and does not claim local non-affinity.
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

from run_4001_geometric_baseline_residual_audit import (  # noqa: E402
    RunConfig as BaseRunConfig,
    median_dt,
    read_events,
    read_raw_ob,
    resolve_data_dir,
)


OUT = ROOT / "Output" / "4080"
SRC_4075 = ROOT / "Output" / "4075" / "target_config_for_4080.json"

NODE = "4080_local_affine_feasibility"
DATE = "2026-08-25"
RNG_SEED = 408001


SAMPLE_COLUMNS = [
    "ob",
    "dataset",
    "t",
    "lag_sec",
    "lag_steps",
    "k",
    "focal_id",
    "n_neighbors_requested",
    "n_neighbors_retained",
    "neighbor_retention_fraction",
    "rank",
    "condition_number",
    "valid_fit",
    "relative_residual_fraction",
    "d2min",
]


SUMMARY_COLUMNS = [
    "ob",
    "dataset",
    "k",
    "lag_sec",
    "lag_steps",
    "n_attempted",
    "valid_fit_fraction",
    "rank3_fraction",
    "median_condition_number",
    "q90_condition_number",
    "median_neighbor_retention",
    "median_relative_residual_fraction",
    "median_d2min",
    "combo_passes_feasibility_gate",
]


def read_target_config() -> dict:
    if not SRC_4075.exists():
        raise FileNotFoundError(f"Run 4075 first: missing {SRC_4075}")
    return json.loads(SRC_4075.read_text(encoding="utf-8"))


def finite_median(values: list[float]) -> float:
    arr = np.asarray(values, dtype="float64")
    arr = arr[np.isfinite(arr)]
    return float(np.median(arr)) if arr.size else math.nan


def finite_quantile(values: list[float], q: float) -> float:
    arr = np.asarray(values, dtype="float64")
    arr = arr[np.isfinite(arr)]
    return float(np.quantile(arr, q)) if arr.size else math.nan


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


def load_ob(ob: int, data_dir: Path, dataset: str | None = None) -> pd.DataFrame:
    path = data_dir / (dataset or f"Ob{ob}.txt")
    if not path.exists():
        path = data_dir / f"Ob{ob}.txt"
    return read_raw_ob(path)


def build_frame_index(df: pd.DataFrame) -> tuple[np.ndarray, dict[float, pd.DataFrame]]:
    times = np.asarray(sorted(df["t"].unique()), dtype="float64")
    frames = {float(t): d.sort_values("id").copy() for t, d in df.groupby("t", sort=True)}
    return times, frames


def frame_arrays(frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    ids = frame["id"].to_numpy(dtype="int64")
    pos = frame[["x", "y", "z"]].to_numpy(dtype="float64")
    return ids, pos


def fit_local_affine(
    ids0: np.ndarray,
    pos0: np.ndarray,
    ids1: np.ndarray,
    pos1: np.ndarray,
    focal_id: int,
    k: int,
) -> dict[str, object]:
    id_to_idx0 = {int(v): i for i, v in enumerate(ids0)}
    id_to_idx1 = {int(v): i for i, v in enumerate(ids1)}
    if focal_id not in id_to_idx0 or focal_id not in id_to_idx1:
        return {"valid_fit": False, "reason": "missing_focal"}
    i0 = id_to_idx0[focal_id]
    i1 = id_to_idx1[focal_id]
    rel = pos0 - pos0[i0]
    dist = np.linalg.norm(rel, axis=1)
    order = np.argsort(dist)
    neigh_ids = [int(ids0[j]) for j in order if int(ids0[j]) != focal_id][:k]
    retained = [nid for nid in neigh_ids if nid in id_to_idx1]
    n_retained = len(retained)
    retention = n_retained / k if k > 0 else math.nan
    if n_retained < 4:
        return {
            "valid_fit": False,
            "n_neighbors_retained": n_retained,
            "neighbor_retention_fraction": retention,
            "rank": 0,
            "condition_number": math.nan,
            "relative_residual_fraction": math.nan,
            "d2min": math.nan,
        }

    a_rows = []
    b_rows = []
    for nid in retained:
        j0 = id_to_idx0[nid]
        j1 = id_to_idx1[nid]
        r0 = pos0[j0] - pos0[i0]
        r1 = pos1[j1] - pos1[i1]
        a_rows.append(r0)
        b_rows.append(r1 - r0)
    A = np.asarray(a_rows, dtype="float64")
    B = np.asarray(b_rows, dtype="float64")
    if not (np.isfinite(A).all() and np.isfinite(B).all()):
        return {"valid_fit": False, "n_neighbors_retained": n_retained, "neighbor_retention_fraction": retention}
    try:
        _, s, _ = np.linalg.svd(A, full_matrices=False)
        rank = int(np.sum(s > max(A.shape) * np.finfo(float).eps * (s[0] if s.size else 0.0)))
        cond = float(s[0] / s[-1]) if s.size >= 3 and s[-1] > 1e-12 else math.inf
        J, _, _, _ = np.linalg.lstsq(A, B, rcond=None)
        pred = A @ J
        resid = B - pred
        resid_ss = float(np.sum(resid * resid))
        target_ss = float(np.sum(B * B))
        rel_frac = math.sqrt(resid_ss / target_ss) if target_ss > 1e-12 else math.nan
        d2min = float(np.mean(np.sum(resid * resid, axis=1)))
        valid = rank >= 3 and np.isfinite(cond) and cond < 1e6
    except np.linalg.LinAlgError:
        rank = 0
        cond = math.inf
        rel_frac = math.nan
        d2min = math.nan
        valid = False
    return {
        "valid_fit": bool(valid),
        "n_neighbors_retained": n_retained,
        "neighbor_retention_fraction": retention,
        "rank": rank,
        "condition_number": cond,
        "relative_residual_fraction": rel_frac,
        "d2min": d2min,
    }


def sample_focals(ids: np.ndarray, rng: np.random.Generator, max_focals: int) -> np.ndarray:
    if len(ids) <= max_focals:
        return ids
    return rng.choice(ids, size=max_focals, replace=False)


def run_feasibility(
    ob: int,
    dataset: str,
    data_dir: Path,
    ks: list[int],
    lag_secs: list[float],
    frame_stride: int,
    max_frames: int,
    max_focals_per_frame: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    rng = np.random.default_rng(RNG_SEED)
    df = load_ob(ob, data_dir, dataset)
    times, frames = build_frame_index(df)
    dt = median_dt(times)
    lag_steps_by_sec = {lag: max(1, int(round(lag / dt))) for lag in lag_secs}
    candidate_idx = np.arange(0, len(times), frame_stride, dtype=int)
    max_lag = max(lag_steps_by_sec.values())
    candidate_idx = candidate_idx[candidate_idx + max_lag < len(times)]
    if len(candidate_idx) > max_frames:
        candidate_idx = np.linspace(candidate_idx[0], candidate_idx[-1], max_frames, dtype=int)
        candidate_idx = np.unique(candidate_idx)

    samples: list[dict[str, object]] = []
    for ii, idx in enumerate(candidate_idx):
        if ii % 50 == 0:
            print(f"[4080] sampled frame {ii + 1}/{len(candidate_idx)}", flush=True)
        t0 = float(times[idx])
        frame0 = frames[t0]
        ids0, pos0 = frame_arrays(frame0)
        focals = sample_focals(ids0, rng, max_focals_per_frame)
        for lag_sec, lag_steps in lag_steps_by_sec.items():
            t1 = float(times[idx + lag_steps])
            ids1, pos1 = frame_arrays(frames[t1])
            for k in ks:
                for focal_id in focals:
                    fit = fit_local_affine(ids0, pos0, ids1, pos1, int(focal_id), k)
                    samples.append(
                        {
                            "ob": ob,
                            "dataset": dataset,
                            "t": t0,
                            "lag_sec": float(lag_sec),
                            "lag_steps": int(lag_steps),
                            "k": int(k),
                            "focal_id": int(focal_id),
                            "n_neighbors_requested": int(k),
                            "n_neighbors_retained": fit.get("n_neighbors_retained", 0),
                            "neighbor_retention_fraction": fit.get("neighbor_retention_fraction", math.nan),
                            "rank": fit.get("rank", 0),
                            "condition_number": fit.get("condition_number", math.nan),
                            "valid_fit": bool(fit.get("valid_fit", False)),
                            "relative_residual_fraction": fit.get("relative_residual_fraction", math.nan),
                            "d2min": fit.get("d2min", math.nan),
                        }
                    )

    summary = summarize_samples(samples)
    meta = {
        "ob": ob,
        "dataset": dataset,
        "n_frames_total": int(len(times)),
        "n_frames_sampled": int(len(candidate_idx)),
        "median_dt": float(dt),
        "ks": ks,
        "lag_secs": lag_secs,
        "lag_steps_by_sec": {str(k): int(v) for k, v in lag_steps_by_sec.items()},
        "frame_stride": frame_stride,
        "max_focals_per_frame": max_focals_per_frame,
    }
    return samples, summary, meta


def summarize_samples(samples: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    df = pd.DataFrame(samples)
    for (ob, dataset, k, lag_sec, lag_steps), d in df.groupby(["ob", "dataset", "k", "lag_sec", "lag_steps"], sort=True):
        valid = d["valid_fit"].astype(bool).to_numpy()
        rank3 = pd.to_numeric(d["rank"], errors="coerce").to_numpy(dtype="float64") >= 3
        cond = pd.to_numeric(d["condition_number"], errors="coerce").to_numpy(dtype="float64")
        retention = pd.to_numeric(d["neighbor_retention_fraction"], errors="coerce").to_numpy(dtype="float64")
        rel_frac = pd.to_numeric(d["relative_residual_fraction"], errors="coerce").to_numpy(dtype="float64")
        d2min = pd.to_numeric(d["d2min"], errors="coerce").to_numpy(dtype="float64")
        valid_cond = cond[valid & np.isfinite(cond)]
        passes = (
            float(np.mean(valid)) >= 0.70
            and float(np.mean(rank3)) >= 0.70
            and finite_median(list(valid_cond)) <= 80.0
            and finite_quantile(list(valid_cond), 0.90) <= 250.0
            and finite_median(list(retention)) >= 0.75
        )
        rows.append(
            {
                "ob": int(ob),
                "dataset": str(dataset),
                "k": int(k),
                "lag_sec": float(lag_sec),
                "lag_steps": int(lag_steps),
                "n_attempted": int(len(d)),
                "valid_fit_fraction": float(np.mean(valid)),
                "rank3_fraction": float(np.mean(rank3)),
                "median_condition_number": finite_median(list(valid_cond)),
                "q90_condition_number": finite_quantile(list(valid_cond), 0.90),
                "median_neighbor_retention": finite_median(list(retention)),
                "median_relative_residual_fraction": finite_median(list(rel_frac[valid])),
                "median_d2min": finite_median(list(d2min[valid])),
                "combo_passes_feasibility_gate": bool(passes),
            }
        )
    return rows


def write_config(args: argparse.Namespace, meta: dict[str, object]) -> None:
    text = dedent(
        f"""\
        node: {NODE}
        date: {DATE}
        node_type: local_affine_feasibility_smoke_test
        source_target_config: Output/4075/target_config_for_4080.json
        observation: Ob{args.ob}
        dataset: {meta.get("dataset")}
        k_values: {args.k}
        lag_secs: {args.lags}
        frame_stride: {args.frame_stride}
        max_frames: {args.max_frames}
        max_focals_per_frame: {args.max_focals_per_frame}
        """
    )
    (OUT / "config.yaml").write_text(text, encoding="utf-8")


def write_summary(summary: list[dict[str, object]], meta: dict[str, object], target_config: dict) -> None:
    pass_rows = [r for r in summary if bool(r["combo_passes_feasibility_gate"])]
    robust_rows = [
        r
        for r in pass_rows
        if int(r["k"]) >= 6 and float(r["lag_sec"]) in {0.05, 0.1, 0.10, 0.2, 0.20}
    ]
    has_mid_k = any(int(r["k"]) in {6, 8, 10} for r in robust_rows)
    has_two_lags = len({float(r["lag_sec"]) for r in robust_rows}) >= 2
    if len(robust_rows) >= 4 and has_mid_k and has_two_lags:
        result = "pass_local_affine_feasible"
        next_node = "4081_global_vs_local_geometry_ladder"
        interpretation = "Local affine fitting is numerically feasible for Route A, with multiple k/lag combinations passing."
    elif len(robust_rows) >= 1:
        result = "boundary_feasible_with_restricted_k_lag"
        next_node = "4081_restricted_geometry_ladder_or_4080b_replication"
        interpretation = "Local affine fitting is possible only under restricted k/lag choices; use caution before interpretation."
    else:
        result = "fail_local_affine_identifiability"
        next_node = "stop_D2min_route_due_to_identifiability"
        interpretation = "Local affine fitting is not stable enough for D2min/local non-affine claims under the pilot gate."

    decision = {
        "node": NODE,
        "question": "Are local affine fits numerically identifiable and stable enough to support a 4081 geometry ladder?",
        "result": result,
        "n_combo_passes": len(pass_rows),
        "n_restricted_robust_combo_passes": len(robust_rows),
        "meta": meta,
        "gate": "pass if multiple k>=6 and multiple lags pass valid-fit, rank, condition, and retention gates",
        "interpretation": interpretation,
        "next": [next_node],
        "target_policy_from_4075": target_config.get("target_policy"),
    }
    write_json(OUT / "decision.json", decision)

    text = f"""# Node 4080 Summary

## Question

Are local affine fits numerically identifiable and stable enough for the midge swarm data to support a 4081 geometry ladder?

## Why this node exists

4075 authorized Route A only after splitting the residual target. Before using
`D2min` or local non-affine language, 4080 checks whether local affine tensors
can be fit stably in sparse 3D swarm neighborhoods.

## Data

```text
ob = Ob{meta["ob"]}
dataset = {meta["dataset"]}
median_dt = {meta["median_dt"]:.6g} sec
frames_total = {meta["n_frames_total"]}
frames_sampled = {meta["n_frames_sampled"]}
```

## Frozen parameters

Target policy from 4075:

```text
primary = T1_transition_tangential_residual
secondary = T2_general_residual_activity
retired_primary = radial residual, core-edge speed
```

4080 itself is target-agnostic feasibility.

## Baseline

`B4_local_affine`, feasibility only.

## Null model

No event null is used in 4080. This node tests numerical identifiability, not event signal.

## Primary metrics

{md_table(summary, ["k", "lag_sec", "n_attempted", "valid_fit_fraction", "rank3_fraction", "median_condition_number", "q90_condition_number", "median_neighbor_retention", "combo_passes_feasibility_gate"])}

## Results

- Passing k/lag combinations: {len(pass_rows)}
- Robust passing combinations with k>=6: {len(robust_rows)}
- Decision: `{result}`

## Gate evaluation

`{result}`

## What this rules out

If local affine fitting had failed, D2min/non-affine interpretation would stop. With a pass, 4081 may compare global and local geometry, but still may not claim mechanism.

## What this does NOT prove

4080 does not prove local non-affinity or biological mechanism. It only says local affine fits are numerically feasible enough to test in 4081.

## Decision

`{result}`

## Next node

`{next_node}`
"""
    (OUT / "4080_summary.md").write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ob", type=int, default=1)
    parser.add_argument("--data-dir", default=BaseRunConfig.data_dir)
    parser.add_argument("--k", default="4,6,8,10,12")
    parser.add_argument("--lags", default="0.05,0.10,0.20")
    parser.add_argument("--frame-stride", type=int, default=10)
    parser.add_argument("--max-frames", type=int, default=500)
    parser.add_argument("--max-focals-per-frame", type=int, default=24)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target_config = read_target_config()
    data_dir = resolve_data_dir(BaseRunConfig(data_dir=args.data_dir))
    events = read_events()
    ob_events = events[events["ob"] == args.ob]
    dataset = str(ob_events.iloc[0]["dataset"]) if not ob_events.empty else f"Ob{args.ob}.txt"
    ks = [int(x.strip()) for x in args.k.split(",") if x.strip()]
    lags = [float(x.strip()) for x in args.lags.split(",") if x.strip()]

    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    samples, summary, meta = run_feasibility(
        ob=args.ob,
        dataset=dataset,
        data_dir=data_dir,
        ks=ks,
        lag_secs=lags,
        frame_stride=args.frame_stride,
        max_frames=args.max_frames,
        max_focals_per_frame=args.max_focals_per_frame,
    )
    write_config(args, meta)
    write_csv(OUT / "local_affine_fit_samples.csv", samples, SAMPLE_COLUMNS)
    write_csv(OUT / "local_affine_feasibility_by_k_lag.csv", summary, SUMMARY_COLUMNS)
    write_csv(OUT / "tables" / "local_affine_feasibility_by_k_lag.csv", summary, SUMMARY_COLUMNS)
    write_json(OUT / "local_affine_feasibility_by_k_lag.json", summary)
    write_summary(summary, meta, target_config)
    print(f"Wrote 4080 local-affine feasibility outputs to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
