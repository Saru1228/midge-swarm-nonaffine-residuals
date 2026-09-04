"""4075 M0 review before 4080.

This synthesis node resolves the 4074 boundary. It decides which target(s)
should be carried into Route A local-affine feasibility and which metrics should
be downgraded or retired.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4075"

NODE = "4075_m0_review_before_4080"
DATE = "2026-08-25"

SRC_4071_DECISION = ROOT / "Output" / "4071" / "decision.json"
SRC_4071_SUMMARY = ROOT / "Output" / "4071" / "metric_replication_summary.csv"
SRC_4074_DECISION = ROOT / "Output" / "4074" / "decision.json"
SRC_4074_SUMMARY = ROOT / "Output" / "4074" / "event_conditioning_summary.csv"


TARGET_COLUMNS = [
    "target_id",
    "target_role",
    "primary_metrics",
    "supporting_metrics",
    "source_evidence",
    "interpretation",
    "route_a_question",
    "decision",
    "next_node_use",
]


TARGETS = [
    {
        "target_id": "T1_transition_tangential_residual",
        "target_role": "primary_route_a_target",
        "primary_metrics": "resid_tangential_speed_mean",
        "supporting_metrics": "edge_minus_core_resid_tangential",
        "source_evidence": "4071 pass; 4074 event-conditioned direction gate passes for resid_tangential_speed_mean; median real-minus-non-event direction gap = 0.3429; effect greater than non-event in 3/3 observations.",
        "interpretation": "This is the clearest transition-conditioned residual signal after global affine subtraction.",
        "route_a_question": "Does local affine deformation explain the transition-conditioned tangential residual, or does a local non-affine tangential residual survive?",
        "decision": "carry_forward_as_primary",
        "next_node_use": "4080 feasibility is allowed; 4081 should evaluate this as the main event-conditioned target.",
    },
    {
        "target_id": "T2_general_residual_activity",
        "target_role": "secondary_route_a_target",
        "primary_metrics": "resid_velocity_cov_trace; resid_speed_rms",
        "supporting_metrics": "",
        "source_evidence": "4071 pass for both residual-intensity anchors; 4074 event-conditioned direction gates fail, but general activity gates pass for both.",
        "interpretation": "These metrics are robust residual activity/intensity signals, but not clean transition-specific direction signals.",
        "route_a_question": "Does local affine deformation absorb broad residual activity, or does general local non-affine activity remain outside transition selection?",
        "decision": "carry_forward_as_secondary_general_activity",
        "next_node_use": "4080 feasibility may include these for fit diagnostics; 4081 should analyze them separately from transition-specific targets.",
    },
    {
        "target_id": "T3_radial_residual",
        "target_role": "retired_primary",
        "primary_metrics": "resid_radial_abs_mean",
        "supporting_metrics": "",
        "source_evidence": "4071 fails; 4074 fails event-conditioned comparison.",
        "interpretation": "Radial residual magnitude is not supported as a stable Ob1-Ob3 primary target.",
        "route_a_question": "No Route A primary question.",
        "decision": "retire_from_primary_route",
        "next_node_use": "Use only as optional diagnostic if already cheap.",
    },
    {
        "target_id": "T4_core_edge_speed",
        "target_role": "retired_primary",
        "primary_metrics": "edge_minus_core_resid_speed",
        "supporting_metrics": "",
        "source_evidence": "4071 fails; 4074 fails event-conditioned comparison, though general activity gate appears in 4074 as non-stable context.",
        "interpretation": "Core-edge residual speed should not be treated as a stable primary target.",
        "route_a_question": "No Route A primary question.",
        "decision": "retire_from_primary_route",
        "next_node_use": "Use only as optional diagnostic if already cheap.",
    },
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in columns})


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def md_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        vals = []
        for col in columns:
            vals.append(str(row.get(col, "")).replace("\n", " ").replace("|", "\\|"))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def write_config() -> None:
    text = dedent(
        f"""\
        node: {NODE}
        date: {DATE}
        node_type: M0_synthesis_and_route_decision
        input_nodes:
          - 4071_cross_dataset_baseline_audit
          - 4074_event_free_vs_event_conditioned_audit
        no_trajectory_reprocessing: true
        decision: split_target_enter_4080_feasibility
        next_node: 4080_local_affine_feasibility
        """
    )
    (OUT / "config.yaml").write_text(text, encoding="utf-8")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tables").mkdir(parents=True, exist_ok=True)

    d4071 = read_json(SRC_4071_DECISION)
    d4074 = read_json(SRC_4074_DECISION)
    s4071 = read_csv(SRC_4071_SUMMARY)
    s4074 = read_csv(SRC_4074_SUMMARY)

    decision = {
        "node": NODE,
        "question": "After 4074 split the target, should Route A enter 4080, and what exactly should 408x test?",
        "result": "split_target_enter_4080_feasibility",
        "inputs": {
            "4071_result": d4071.get("result"),
            "4074_result": d4074.get("result"),
            "4071_metric_passes": d4071.get("n_metric_passes"),
            "4074_stable_core_event_conditioned_count": d4074.get("stable_core_event_conditioned_count"),
            "4074_stable_core_activity_gate_count": d4074.get("stable_core_activity_gate_count"),
        },
        "primary_route_a_target": "T1_transition_tangential_residual",
        "secondary_route_a_target": "T2_general_residual_activity",
        "retired_primary_targets": ["T3_radial_residual", "T4_core_edge_speed"],
        "next": ["4080_local_affine_feasibility"],
        "4080_instruction": "Run feasibility only. Do not yet claim local non-affinity. Check whether local affine fits are numerically identifiable for the data and lags.",
        "4081_instruction": "If 4080 passes, evaluate T1 and T2 separately in the geometry ladder; do not merge them into one residual target.",
        "interpretation": "4074 is a boundary, but it is not a stop. It routes 408x toward split targets: a narrow transition-conditioned tangential target and a broader general residual-activity target.",
    }

    target_config = {
        "route_a_allowed": True,
        "next_node": "4080_local_affine_feasibility",
        "target_policy": "split_targets",
        "targets": TARGETS,
        "global_constraints": [
            "Do not treat residual velocity as a single phenomenon after 4074.",
            "Do not use radial residual magnitude or core-edge residual speed as primary Route A claims.",
            "4080 is feasibility only; 4081 is the first geometry-ladder interpretation node.",
            "T1 is transition-conditioned; T2 is general residual activity and must not be described as transition-specific.",
        ],
    }

    write_config()
    write_csv(OUT / "m0_target_decision.csv", TARGETS, TARGET_COLUMNS)
    write_csv(OUT / "tables" / "m0_target_decision.csv", TARGETS, TARGET_COLUMNS)
    write_json(OUT / "decision.json", decision)
    write_json(OUT / "target_config_for_4080.json", target_config)

    summary = f"""# Node 4075 Summary

## Question

After 4074 split the target, should Route A enter 4080, and what exactly should 408x test?

## Why this node exists

4074 produced a boundary, not a clean pass. Stopping there would leave the next
experiment underspecified. This M0 review decides whether the boundary should
stop the route or refine the target before local-affine testing.

## Inputs

- `Output/4071/decision.json`
- `Output/4071/metric_replication_summary.csv`
- `Output/4074/decision.json`
- `Output/4074/event_conditioning_summary.csv`

## Evidence Summary

4071:

```text
result = {d4071.get("result")}
metric_passes = {d4071.get("n_metric_passes")} / {d4071.get("n_primary_metrics")}
anchor_pass = {d4071.get("anchor_pass")}
```

4074:

```text
result = {d4074.get("result")}
stable_core_event_conditioned_count = {d4074.get("stable_core_event_conditioned_count")} / {d4074.get("n_stable_core_metrics")}
stable_core_activity_gate_count = {d4074.get("stable_core_activity_gate_count")} / {d4074.get("n_stable_core_metrics")}
```

## Target Decision

{md_table(TARGETS, ["target_id", "target_role", "primary_metrics", "supporting_metrics", "decision", "next_node_use"])}

## Main Interpretation

4074 should not stop the 4xxx program, but it does stop the idea that all
affine-residual velocity metrics form one transition-specific target.

The target must split:

1. `T1_transition_tangential_residual`
   - primary metric: `resid_tangential_speed_mean`;
   - supporting metric: `edge_minus_core_resid_tangential`;
   - this is the primary Route A target.

2. `T2_general_residual_activity`
   - primary metrics: `resid_velocity_cov_trace`, `resid_speed_rms`;
   - this is a secondary general-activity target, not a transition-specific
     mechanism claim.

Retired from primary Route A claims:

```text
resid_radial_abs_mean
edge_minus_core_resid_speed
```

## Gate Evaluation

`split_target_enter_4080_feasibility`

Reason:

- 4071 gives enough cross-observation support to continue.
- 4074 shows mixed event conditioning, but at least one stable-core metric is
  clearly event-conditioned.
- The boundary can be resolved by splitting targets rather than stopping the
  route or merging phenomena.

## What This Rules Out

Do not enter 408x with a single undifferentiated residual target.

Do not write:

```text
the full affine-residual velocity organization is transition-specific
```

Write instead:

```text
the transition-conditioned component is mainly tangential;
residual intensity/covariance is broader general residual activity.
```

## What This Does Not Prove

4075 does not prove local non-affinity. It only authorizes a feasibility test.

## Decision

`split_target_enter_4080_feasibility`

## Next Node

`4080_local_affine_feasibility`

4080 should test whether local affine fitting is identifiable and stable. It
should not yet interpret biological mechanism.
"""

    (OUT / "4075_summary.md").write_text(summary, encoding="utf-8")
    print(f"Wrote 4075 M0 review outputs to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
