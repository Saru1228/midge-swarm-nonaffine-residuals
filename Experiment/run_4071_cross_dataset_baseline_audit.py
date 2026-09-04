"""4071 cross-dataset baseline audit.

This node replicates the frozen 4072 affine-residual target metrics on Ob1,
Ob2, and Ob3 using the registered 4073 controls:

- baseline: B3 global affine residuals
- null/control: N1 shifted-event nulls

It reuses the 4002A residual-spatial metric code but writes only to
Output/4071, leaving the original 4002A outputs untouched.
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


OUT = ROOT / "Output" / "4071"
SOURCE_PRIMARY = ROOT / "Output" / "4072" / "primary_metrics.csv"

NODE = "4071_cross_dataset_baseline_audit"
DATE = "2026-08-25"


SUMMARY_COLUMNS = [
    "variable",
    "taxonomy_class",
    "family",
    "n_ob_valid",
    "directional_consistency",
    "median_real_abs_direction_contrast_z",
    "median_null_abs_direction_contrast_z",
    "median_real_minus_null_abs_direction_contrast_z",
    "n_ob_effect_gt_null",
    "effect_gt_null_fraction",
    "metric_passes_gate",
]


OB_COLUMNS = [
    "ob",
    "variable",
    "taxonomy_class",
    "family",
    "n_events",
    "real_low_to_high_delta_z",
    "real_high_to_low_delta_z",
    "real_direction_contrast_z",
    "real_abs_direction_contrast_z",
    "null_abs_median_direction_contrast_z",
    "real_minus_null_abs_direction_contrast_z",
    "p_null_abs_direction_ge_real",
    "effect_gt_null",
]


def read_primary_metrics() -> list[dict[str, str]]:
    if not SOURCE_PRIMARY.exists():
        raise FileNotFoundError(f"Missing 4072 primary metrics: {SOURCE_PRIMARY}")
    with SOURCE_PRIMARY.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def finite_median(values: list[float]) -> float:
    arr = np.asarray(values, dtype="float64")
    arr = arr[np.isfinite(arr)]
    return float(np.median(arr)) if arr.size else math.nan


def sign_consistency(values: list[float]) -> float:
    arr = np.asarray(values, dtype="float64")
    arr = arr[np.isfinite(arr)]
    arr = arr[np.abs(arr) > 1e-12]
    if arr.size == 0:
        return math.nan
    return float(max(np.mean(arr > 0), np.mean(arr < 0)))


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


def ob_real_summary(features: pd.DataFrame, primary: list[dict[str, str]], ob: int) -> pd.DataFrame:
    d = features[(features["ob"] == ob) & (features["variable"].isin([p["variable"] for p in primary]))].copy()
    return r4002a.summarize_direction(d, prefix="real")


def null_summary_for_ob(
    arrays: dict[tuple[int, str], dict[str, np.ndarray]],
    events: pd.DataFrame,
    ob: int,
    cfg: r4002a.RunConfig,
    primary_vars: set[str],
) -> pd.DataFrame:
    events_ob = events[events["ob"] == ob].copy().reset_index(drop=True)
    keys = {(int(row.ob), str(row.dataset)) for row in events_ob.itertuples(index=False)}
    arrays_ob = {key: value for key, value in arrays.items() if key in keys}
    null = r4002a.run_nulls(arrays_ob, events_ob, cfg)
    return null[null["variable"].isin(primary_vars)].copy()


def compare_ob(
    real: pd.DataFrame,
    null: pd.DataFrame,
    primary_meta: dict[str, dict[str, str]],
    ob: int,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for variable, meta in primary_meta.items():
        d_real = real[real["variable"] == variable]
        if d_real.empty:
            continue
        rec = d_real.iloc[0]
        d_null = null[null["variable"] == variable]
        real_abs = float(rec.get("real_abs_median_direction_contrast_z", math.nan))
        null_abs = d_null["null_abs_median_direction_contrast_z"].astype(float).to_numpy()
        null_abs = null_abs[np.isfinite(null_abs)]
        null_med = float(np.median(null_abs)) if null_abs.size else math.nan
        p_ge = float(np.mean(null_abs >= real_abs)) if null_abs.size and np.isfinite(real_abs) else math.nan
        gap = real_abs - null_med if np.isfinite(real_abs) and np.isfinite(null_med) else math.nan
        rows.append(
            {
                "ob": ob,
                "variable": variable,
                "taxonomy_class": meta.get("taxonomy_class", ""),
                "family": meta.get("family", ""),
                "n_events": int(rec.get("n_events", 0)),
                "real_low_to_high_delta_z": float(rec.get("real_median_low_to_high_delta_z", math.nan)),
                "real_high_to_low_delta_z": float(rec.get("real_median_high_to_low_delta_z", math.nan)),
                "real_direction_contrast_z": float(rec.get("real_median_direction_contrast_z", math.nan)),
                "real_abs_direction_contrast_z": real_abs,
                "null_abs_median_direction_contrast_z": null_med,
                "real_minus_null_abs_direction_contrast_z": gap,
                "p_null_abs_direction_ge_real": p_ge,
                "effect_gt_null": bool(np.isfinite(gap) and gap > 0),
            }
        )
    return rows


def summarize_metrics(ob_rows: list[dict[str, object]], primary: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    by_var = {p["variable"]: p for p in primary}
    for variable, meta in by_var.items():
        d = [r for r in ob_rows if r["variable"] == variable]
        effects = [float(r["real_abs_direction_contrast_z"]) for r in d]
        nulls = [float(r["null_abs_median_direction_contrast_z"]) for r in d]
        gaps = [float(r["real_minus_null_abs_direction_contrast_z"]) for r in d]
        dirs = [float(r["real_direction_contrast_z"]) for r in d]
        n_valid = len(d)
        n_gt = int(sum(bool(r["effect_gt_null"]) for r in d))
        directional = sign_consistency(dirs)
        med_effect = finite_median(effects)
        med_null = finite_median(nulls)
        med_gap = finite_median(gaps)
        passes = (
            n_valid >= 3
            and np.isfinite(directional)
            and directional >= (2.0 / 3.0)
            and n_gt >= 2
            and np.isfinite(med_effect)
            and med_effect >= 0.12
            and np.isfinite(med_gap)
            and med_gap > 0
        )
        rows.append(
            {
                "variable": variable,
                "taxonomy_class": meta.get("taxonomy_class", ""),
                "family": meta.get("family", ""),
                "n_ob_valid": n_valid,
                "directional_consistency": directional,
                "median_real_abs_direction_contrast_z": med_effect,
                "median_null_abs_direction_contrast_z": med_null,
                "median_real_minus_null_abs_direction_contrast_z": med_gap,
                "n_ob_effect_gt_null": n_gt,
                "effect_gt_null_fraction": n_gt / n_valid if n_valid else math.nan,
                "metric_passes_gate": passes,
            }
        )
    return rows


def write_config(obs: list[int], n_null: int) -> None:
    text = dedent(
        f"""\
        node: {NODE}
        date: {DATE}
        node_type: cross_dataset_replication
        source_primary_metrics: Output/4072/primary_metrics.csv
        baseline: B3_global_affine
        null: N1_shifted_event
        observations: {",".join(str(x) for x in obs)}
        n_null: {n_null}
        no_new_primary_metrics: true
        next_if_pass: 4074_event_free_vs_event_conditioned_audit
        next_if_boundary: 4074_event_free_vs_event_conditioned_audit_or_M0_boundary_review
        next_if_fail: stop_main_residual_mechanism_program_or_reclassify_as_dataset_specific
        """
    )
    (OUT / "config.yaml").write_text(text, encoding="utf-8")


def write_summary(
    summary_rows: list[dict[str, object]],
    ob_rows: list[dict[str, object]],
    obs: list[int],
    n_null: int,
) -> None:
    pass_count = int(sum(bool(r["metric_passes_gate"]) for r in summary_rows))
    anchor_vars = {"resid_velocity_cov_trace", "resid_speed_rms"}
    anchor_pass = any(bool(r["metric_passes_gate"]) for r in summary_rows if r["variable"] in anchor_vars)
    node_result = "pass" if pass_count >= 4 and anchor_pass else "boundary" if pass_count >= 2 else "fail"
    next_node = "4074_event_free_vs_event_conditioned_audit" if node_result in {"pass", "boundary"} else "M0_boundary_review"
    decision = {
        "node": NODE,
        "question": "Do the frozen 4072 residual target metrics replicate across Ob1/Ob2/Ob3 under B3 + N1?",
        "result": node_result,
        "n_primary_metrics": len(summary_rows),
        "n_metric_passes": pass_count,
        "anchor_pass": anchor_pass,
        "gate": "node pass if >=4/6 primary metrics pass and at least one residual-intensity anchor passes; boundary if >=2/6 pass",
        "metric_gate": "per metric: valid in 3 obs, directional_consistency >= 2/3, effect_gt_null in >=2 obs, median_abs_effect >= 0.12, median_gap > 0",
        "observations": obs,
        "n_null": n_null,
        "interpretation": (
            "The frozen residual target has enough Ob1-Ob3 support to continue foundation work."
            if node_result == "pass"
            else "The frozen residual target is only partially supported across Ob1-Ob3."
            if node_result == "boundary"
            else "The frozen residual target does not replicate across Ob1-Ob3 under the current gate."
        ),
        "next": [next_node],
    }
    write_json(OUT / "decision.json", decision)

    pass_rows = [r for r in summary_rows if bool(r["metric_passes_gate"])]
    fail_rows = [r for r in summary_rows if not bool(r["metric_passes_gate"])]
    text = dedent(
        f"""\
        # Node 4071 Summary

        ## Question

        Do the frozen 4072 residual target metrics replicate across `Ob1/Ob2/Ob3` under the frozen `B3_global_affine + N1_shifted_event` registry?

        ## Why this node exists

        4001/4002A were strong as full-series screens, but 4070 identified a risk: the result could still be pooled or dataset-specific. 4071 checks the frozen 4072 primary metrics one observation at a time before local-affine mechanism tests.

        ## Data

        Observations: `{", ".join("Ob" + str(x) for x in obs)}`

        No all-19 run was performed. This node reuses the 4002A global-affine residual metric implementation and writes only to `Output/4071`.

        ## Frozen parameters

        ```text
        primary metrics = Output/4072/primary_metrics.csv
        baseline = B3_global_affine
        null = N1_shifted_event
        n_null = {n_null}
        ```

        ## Baseline

        `B3_global_affine`: translation plus global affine deformation subtraction.

        ## Null model

        `N1_shifted_event`: circularly shifted event times within observation.

        ## Primary metrics

        {md_table(summary_rows, ["variable", "taxonomy_class", "n_ob_valid", "directional_consistency", "median_real_abs_direction_contrast_z", "median_null_abs_direction_contrast_z", "median_real_minus_null_abs_direction_contrast_z", "n_ob_effect_gt_null", "metric_passes_gate"])}

        ## Results

        - Metric passes: {pass_count} / {len(summary_rows)}
        - Residual-intensity anchor pass: {anchor_pass}
        - Node decision: `{node_result}`

        Passing metrics:

        {md_table(pass_rows, ["variable", "taxonomy_class", "median_real_abs_direction_contrast_z", "median_real_minus_null_abs_direction_contrast_z", "n_ob_effect_gt_null"])}

        Non-passing metrics:

        {md_table(fail_rows, ["variable", "taxonomy_class", "median_real_abs_direction_contrast_z", "median_real_minus_null_abs_direction_contrast_z", "n_ob_effect_gt_null"])}

        ## Dataset-wise replication

        See `ob_level_effects.csv`. The audit explicitly reports each observation rather than relying on pooled significance.

        ## Gate evaluation

        `{node_result}`

        Node gate:

        ```text
        pass: >=4/6 primary metrics pass AND at least one residual-intensity anchor passes
        boundary: >=2/6 primary metrics pass
        fail: otherwise
        ```

        ## What this rules out

        If a metric fails here, it should not be used as a cross-dataset primary target in 408x without a new reason. The node also prevents using pooled full-series significance as the only robustness evidence.

        ## What this does NOT prove

        4071 does not prove local non-affinity, stochasticity, propagation, or network mechanism. It only checks Ob1-Ob3 replication under the global-affine residual baseline.

        ## Decision

        `{node_result}`

        ## Next node

        `{next_node}`
        """
    )
    # The inserted Markdown tables begin at column 0, so textwrap.dedent cannot
    # remove the function-body indentation from the surrounding prose. Strip the
    # fixed prose indent after interpolation to keep the summary renderable.
    text = "\n".join(line[8:] if line.startswith("        ") else line for line in text.splitlines()) + "\n"
    (OUT / "4071_summary.md").write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--obs", default="1,2,3", help="Comma-separated observation ids.")
    parser.add_argument("--n-null", type=int, default=80)
    parser.add_argument("--data-dir", default=r4002a.RunConfig.data_dir)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    obs = [int(x.strip()) for x in args.obs.split(",") if x.strip()]
    primary = read_primary_metrics()
    primary_vars = {row["variable"] for row in primary}
    primary_meta = {row["variable"]: row for row in primary}

    cfg = r4002a.RunConfig(data_dir=args.data_dir, n_null=args.n_null, min_ob_gate=1)
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    write_config(obs, args.n_null)

    events = r4002a.read_events()
    events = events[events["ob"].isin(obs)].copy().reset_index(drop=True)
    if events.empty:
        raise RuntimeError(f"No events found for observations: {obs}")
    print(f"[4071] events: {len(events)} across observations {obs}", flush=True)

    frame_raw = r4002a.build_frame_metrics(events, cfg)
    frame = r4002a.add_residualized_metrics(frame_raw, cfg)
    arrays = r4002a.build_arrays(frame)
    features = r4002a.extract_event_features(arrays, events, cfg)
    features = features[features["variable"].isin(primary_vars)].copy()

    ob_rows: list[dict[str, object]] = []
    for ob in obs:
        print(f"[4071] shifted nulls for Ob{ob}", flush=True)
        real = ob_real_summary(features, primary, ob)
        null = null_summary_for_ob(arrays, events, ob, cfg, primary_vars)
        ob_rows.extend(compare_ob(real, null, primary_meta, ob))

    summary_rows = summarize_metrics(ob_rows, primary)

    write_csv(OUT / "ob_level_effects.csv", ob_rows, OB_COLUMNS)
    write_csv(OUT / "metric_replication_summary.csv", summary_rows, SUMMARY_COLUMNS)
    write_csv(OUT / "tables" / "ob_level_effects.csv", ob_rows, OB_COLUMNS)
    write_csv(OUT / "tables" / "metric_replication_summary.csv", summary_rows, SUMMARY_COLUMNS)
    write_json(OUT / "ob_level_effects.json", ob_rows)
    write_json(OUT / "metric_replication_summary.json", summary_rows)
    write_summary(summary_rows, ob_rows, obs, args.n_null)
    print(f"Wrote 4071 cross-dataset audit outputs to {OUT.relative_to(ROOT)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
