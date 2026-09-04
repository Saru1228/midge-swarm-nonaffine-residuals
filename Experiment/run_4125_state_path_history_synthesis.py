"""4125 technical synthesis for the 412x state-path/history route."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4125"
DATE = "2026-08-27"


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


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def classify(decision_4120: dict[str, object], decision_4121: dict[str, object]) -> tuple[str, str, list[str]]:
    gate_4120 = str(decision_4120.get("gate_result", ""))
    gate_4121 = str(decision_4121.get("gate_result", ""))
    if not gate_4120.startswith("pass"):
        return (
            "P0_technical_stop_state_path_not_identifiable",
            "Recent C-R state path was not technically identifiable, so history dependence was not tested.",
            [],
        )
    if gate_4121 == "pass_same_state_history_dependence":
        return (
            "P2_path_direction_dependence_candidate",
            "Same-current-state different-history matching passed; 4122 approach/departure is authorized.",
            ["4122_approach_departure_directional_asymmetry"],
        )
    if gate_4121 == "boundary_observation_specific_history_dependence":
        return (
            "P1_observation_specific_history_dependence_boundary",
            "History-conditioned T1 separation is visible in several observations, but it does not form a stable cross-observation direction rule.",
            [],
        )
    if gate_4121 == "boundary_history_contrast_identifiability":
        return (
            "P0_history_contrast_identifiability_boundary",
            "Same-state contrasting-history pairs were not sufficiently identifiable across observations.",
            [],
        )
    return (
        "P0_no_same_state_history_dependence",
        "Recent path direction adds little beyond the matched instantaneous state under the tested representation.",
        [],
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tables").mkdir(parents=True, exist_ok=True)

    d4120 = load_json(ROOT / "Output" / "4120" / "decision.json")
    d4121 = load_json(ROOT / "Output" / "4121" / "decision.json")
    obs = pd.read_csv(ROOT / "Output" / "4121" / "observation_level_effects.csv")
    sens = pd.read_csv(ROOT / "Output" / "4121" / "sensitivity.csv")

    cls, interpretation, next_nodes = classify(d4120, d4121)
    obs["abs_effect"] = np.abs(obs["median_signed_axis_delta_A_z"])
    obs["effect_direction"] = np.where(obs["median_signed_axis_delta_A_z"] >= 0, "axis_positive_higher", "axis_negative_higher")
    strongest = obs.sort_values("abs_effect", ascending=False).head(8)
    positive_count = int((obs["median_signed_axis_delta_A_z"] > 0).sum())
    negative_count = int((obs["median_signed_axis_delta_A_z"] < 0).sum())
    null_beat_count = int(obs["real_beats_null_median_abs"].astype(str).str.lower().eq("true").sum())
    q95_beat_count = int(obs["real_beats_null_q95_abs"].astype(str).str.lower().eq("true").sum())

    primary_metrics = d4121["primary_metrics"]
    synthesis = {
        "node": "4125_state_path_history_synthesis",
        "date": DATE,
        "node_type": "technical_synthesis",
        "upstream_nodes": [
            "4120_state_path_feasibility_coordinate_freeze",
            "4121_same_current_state_different_history_matched_test",
        ],
        "classification": cls,
        "interpretation": interpretation,
        "route_decision": "stop_before_4122_unless_reopened_as_descriptive_observation_specific_analysis"
        if not next_nodes
        else "continue_to_4122",
        "primary_metrics": {
            "4120_gate": d4120.get("gate_result"),
            "4121_gate": d4121.get("gate_result"),
            "n_observations_sufficient_pairs": primary_metrics.get("n_observations_sufficient_pairs"),
            "median_abs_observation_signed_axis_delta_A_z": primary_metrics.get(
                "median_abs_observation_signed_axis_delta_A_z"
            ),
            "direction_consistency_fraction": primary_metrics.get("direction_consistency_fraction"),
            "real_beats_shuffle_null_median_abs_fraction": primary_metrics.get(
                "real_beats_shuffle_null_median_abs_fraction"
            ),
            "positive_effect_observations": positive_count,
            "negative_effect_observations": negative_count,
            "real_beats_null_median_observations": null_beat_count,
            "real_beats_null_q95_observations": q95_beat_count,
        },
        "bounded_claim": (
            "Recent C-R path direction can be measured and produces observation-specific T1 separations after "
            "same-current-state matching, but the sign/order is not stable enough to claim a universal history "
            "dependence mechanism."
        ),
        "does_not_support": [
            "robust same-state history dependence",
            "approach/departure hysteresis route as primary confirmatory analysis",
            "grouped OOS history-gain modeling",
            "network propagation mechanism",
            "causal memory mechanism",
        ],
        "next": next_nodes,
        "artifacts": [
            "Output/4125/decision.json",
            "Output/4125/4125_summary.md",
            "Output/4125/tables/strongest_observation_effects.csv",
            "Output/4125/tables/4121_primary_sensitivity_h500.csv",
        ],
    }

    strongest.to_csv(OUT / "tables" / "strongest_observation_effects.csv", index=False)
    sens[np.isclose(sens["history_window_sec"], 0.5)].to_csv(
        OUT / "tables" / "4121_primary_sensitivity_h500.csv", index=False
    )
    (OUT / "decision.json").write_text(json.dumps(synthesis, indent=2), encoding="utf-8")

    summary_parts = [
        "# Node 4125 State-path / History Synthesis",
        "## Classification\n\n" f"`{cls}`",
        "## Plain-language Result\n\n"
        "The recent path of the swarm through the compact-density state plane is measurable, and it sometimes separates T1 after matching the current state. "
        "However, the direction of that separation changes across observations. This makes the result useful as an observation-specific boundary, not as a stable mechanism.",
        "## Evidence Chain\n\n"
        + md_table(
            [
                {
                    "node": "4120",
                    "question": "Can recent state-path features be measured?",
                    "result": d4120.get("gate_result"),
                    "meaning": "technical pass; leakage requires state matching",
                },
                {
                    "node": "4121",
                    "question": "Same current state, different path direction?",
                    "result": d4121.get("gate_result"),
                    "meaning": "visible but direction-inconsistent history separation",
                },
            ],
            ["node", "question", "result", "meaning"],
        ),
        "## Primary 4121 Metrics\n\n"
        + md_table(
            [
                {
                    "n_obs_sufficient": primary_metrics.get("n_observations_sufficient_pairs"),
                    "median_abs_effect": primary_metrics.get("median_abs_observation_signed_axis_delta_A_z"),
                    "direction_consistency": primary_metrics.get("direction_consistency_fraction"),
                    "real_beats_null_fraction": primary_metrics.get("real_beats_shuffle_null_median_abs_fraction"),
                    "pos_obs": positive_count,
                    "neg_obs": negative_count,
                }
            ],
            [
                "n_obs_sufficient",
                "median_abs_effect",
                "direction_consistency",
                "real_beats_null_fraction",
                "pos_obs",
                "neg_obs",
            ],
        ),
        "## Strongest Observation-specific Effects\n\n"
        + md_table(
            strongest.to_dict("records"),
            [
                "ob",
                "dataset",
                "n_selected_pairs",
                "median_signed_axis_delta_A_z",
                "null_median_abs_signed_axis_delta_A_z",
                "real_minus_null_median_abs_effect",
                "effect_direction",
            ],
        ),
        "## Route Decision\n\n"
        "Do not continue to 4122/4123 as confirmatory primary nodes under the current gate. "
        "A later descriptive node may inspect why Ob5/8/9 and Ob12/15/17 have opposite signs, but that would be a heterogeneity analysis rather than a robust history-mechanism claim.",
        "## Bounded Claim\n\n" + synthesis["bounded_claim"],
        "## What This Does Not Support\n\n"
        + md_table([{"does_not_support": x} for x in synthesis["does_not_support"]], ["does_not_support"]),
        "## Artifacts\n\n"
        "- `Output/4120/4120_summary.md`\n"
        "- `Output/4121/4121_summary.md`\n"
        "- `Output/4125/decision.json`\n"
        "- `Output/4125/tables/strongest_observation_effects.csv`\n"
        "- `Output/4125/tables/4121_primary_sensitivity_h500.csv`",
    ]
    (OUT / "4125_summary.md").write_text("\n\n".join(summary_parts) + "\n", encoding="utf-8")
    print(json.dumps(synthesis, indent=2))
    print(f"Wrote 4125 outputs to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
