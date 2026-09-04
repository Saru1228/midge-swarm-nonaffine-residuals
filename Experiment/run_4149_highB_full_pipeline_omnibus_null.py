"""Run node 4149 as a high-B wrapper around the frozen 4141 omnibus null.

The 4141 implementation owns the frozen pseudo-event pipeline. This wrapper
only redirects outputs to Output/4149, reuses the verified 4141 cache, and
records a run status file so the high-B check can be separated from the earlier
smoke run.
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

import run_4141_full_pipeline_omnibus_survival_null as r4141


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4149"
FIG = OUT / "figures"
TABLES = OUT / "tables"
STATUS_PATH = OUT / "status.json"
NODE = "4149_highB_full_pipeline_omnibus_null"
DATE = "2026-09-02"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default=r4141.BaseRunConfig.data_dir)
    parser.add_argument("--obs", default="all")
    parser.add_argument("--n-null", type=int, default=1000)
    parser.add_argument("--n-controls", type=int, default=40)
    parser.add_argument("--k", default="8,10")
    parser.add_argument("--lag", type=float, default=0.10)
    parser.add_argument("--frame-stride", type=int, default=2)
    parser.add_argument("--max-focals-per-frame", type=int, default=24)
    parser.add_argument("--prepost-sec", type=float, default=0.20)
    parser.add_argument("--exclusion-sec", type=float, default=0.80)
    parser.add_argument("--force-cache", action="store_true")
    return parser.parse_args()


def patch_4141_globals() -> None:
    r4141.OUT = OUT
    r4141.FIG = FIG
    r4141.CACHE = ROOT / "Output" / "4141" / "cache"
    r4141.NODE = NODE
    r4141.DATE = DATE


def write_4149_summary(args: argparse.Namespace) -> None:
    stats_path = OUT / "p_omnibus.json"
    decision_path = OUT / "decision.json"
    stats = json.loads(stats_path.read_text(encoding="utf-8"))
    decision = json.loads(decision_path.read_text(encoding="utf-8"))

    summary = f"""# Node 4149 Summary

## Purpose

Run the frozen 4141 full-pipeline pseudo-event omnibus null at higher null
replicate count, while preserving the same observed T1 support definition,
survival gate, k values, lag, event windows, and all-19 observation scope.

## Configuration

```text
n_null_replicates = {args.n_null}
n_controls_per_replicate_observation = {args.n_controls}
k_values = {args.k}
lag_sec = {args.lag}
frame_stride = {args.frame_stride}
max_focals_per_frame = {args.max_focals_per_frame}
prepost_sec = {args.prepost_sec}
exclusion_sec = {args.exclusion_sec}
cache_source = Output/4141/cache
output = Output/4149
```

## Primary Result

```text
observed N_both = {stats["observed_n_both"]}
observed N_any  = {stats["observed_n_any"]}
null N_both mean = {stats["n_both_null_mean"]:.6g}
null N_both median = {stats["n_both_null_median"]:.6g}
null N_both q95 = {stats["n_both_null_q95"]:.6g}
null N_both max = {stats["n_both_null_max"]:.6g}
p_both_ge_14 = {stats["p_omnibus_both_ge_14"]:.6g}
p_any_ge_15 = {stats["p_omnibus_any_ge_15"]:.6g}
```

## Gate

`{decision["main_result"]["gate_result"]}`

{decision["main_result"]["manuscript_consequence"]}

## Interpretation

This node strengthens or bounds the reviewer-facing claim that the all-observation
T1 survival count is unusual under a complete pseudo-event version of the same
pipeline. It still does not prove a biological mechanism; it tests whether the
pipeline-level pattern is readily reproduced by time-randomized pseudo-events.

## Artifacts

- `Output/4149/omnibus_null_config.yaml`
- `Output/4149/omnibus_replicates.csv`
- `Output/4149/observation_replicate_passes.csv`
- `Output/4149/observation_null_pass_rates.csv`
- `Output/4149/N_both_distribution.csv`
- `Output/4149/N_any_distribution.csv`
- `Output/4149/p_omnibus.json`
- `Output/4149/decision.json`
- `Output/4149/status.json`
- `Output/4149/figures/`
"""
    (OUT / "4149_summary.md").write_text(summary, encoding="utf-8")
    write_json(
        OUT / "omnibus_summary.json",
        {
            "node": NODE,
            "date": DATE,
            "n_null_replicates": args.n_null,
            "n_controls_per_replicate_observation": args.n_controls,
            "stats": stats,
            "decision": decision,
            "cache_source": "Output/4141/cache",
        },
    )


def main() -> int:
    args = parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    patch_4141_globals()

    write_json(
        STATUS_PATH,
        {
            "node": NODE,
            "date": DATE,
            "status": "running",
            "started_at": datetime.now().isoformat(timespec="seconds"),
            "n_null_replicates": args.n_null,
            "n_controls_per_replicate_observation": args.n_controls,
            "cache_source": "Output/4141/cache",
        },
    )

    original_argv = sys.argv[:]
    forwarded = [
        original_argv[0],
        "--data-dir",
        args.data_dir,
        "--obs",
        args.obs,
        "--n-null",
        str(args.n_null),
        "--n-controls",
        str(args.n_controls),
        "--k",
        args.k,
        "--lag",
        str(args.lag),
        "--frame-stride",
        str(args.frame_stride),
        "--max-focals-per-frame",
        str(args.max_focals_per_frame),
        "--prepost-sec",
        str(args.prepost_sec),
        "--exclusion-sec",
        str(args.exclusion_sec),
    ]
    if args.force_cache:
        forwarded.append("--force-cache")

    try:
        sys.argv = forwarded
        code = int(r4141.main())
        write_4149_summary(args)
        write_json(
            STATUS_PATH,
            {
                "node": NODE,
                "date": DATE,
                "status": "complete",
                "finished_at": datetime.now().isoformat(timespec="seconds"),
                "n_null_replicates": args.n_null,
                "n_controls_per_replicate_observation": args.n_controls,
                "cache_source": "Output/4141/cache",
                "summary": rel(OUT / "4149_summary.md"),
                "decision": rel(OUT / "decision.json"),
            },
        )
        return code
    except Exception as exc:
        write_json(
            STATUS_PATH,
            {
                "node": NODE,
                "date": DATE,
                "status": "failed",
                "finished_at": datetime.now().isoformat(timespec="seconds"),
                "error": str(exc),
                "traceback": traceback.format_exc(),
            },
        )
        raise
    finally:
        sys.argv = original_argv


if __name__ == "__main__":
    raise SystemExit(main())
