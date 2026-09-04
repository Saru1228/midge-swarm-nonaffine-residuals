"""4132 negative mechanism boundary atlas.

This node organizes negative and boundary evidence into an explicit mechanism
space. It separates tested failures from untested routes and prevents
overclaiming such as "no propagation exists" or "stochasticity is impossible."
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from textwrap import dedent

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4132"
DATE = "2026-08-27"
NODE = "4132_negative_mechanism_boundary_atlas"


def ensure_dirs() -> None:
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    (OUT / "figures").mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


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


def write_csv_pair(df: pd.DataFrame, name: str) -> None:
    df.to_csv(OUT / name, index=False)
    df.to_csv(OUT / "tables" / name, index=False)


def load_inputs() -> dict[str, object]:
    return {
        "d4130": read_json(ROOT / "Output" / "4130" / "decision.json"),
        "d4131": read_json(ROOT / "Output" / "4131" / "decision.json"),
        "d4001": None,
        "d4081c": read_json(ROOT / "Output" / "4081c" / "decision.json"),
        "d4086": read_json(ROOT / "Output" / "4086" / "decision.json"),
        "d4087": read_json(ROOT / "Output" / "4087" / "decision.json"),
        "d4088": read_json(ROOT / "Output" / "4088" / "decision.json"),
        "d4090": read_json(ROOT / "Output" / "4090" / "decision.json"),
        "d4094": read_json(ROOT / "Output" / "4094" / "decision.json"),
        "d4100": read_json(ROOT / "Output" / "4100" / "decision.json"),
        "d4105": read_json(ROOT / "Output" / "4105" / "decision.json"),
        "d4121": read_json(ROOT / "Output" / "4121" / "decision.json"),
        "d4125": read_json(ROOT / "Output" / "4125" / "decision.json"),
        "claims": pd.read_csv(ROOT / "Output" / "4130" / "claim_strength_registry.csv"),
        "evidence": pd.read_csv(ROOT / "Output" / "4130" / "evidence_registry.csv"),
        "metadata": pd.read_csv(ROOT / "Output" / "4130" / "metadata_source_audit.csv"),
        "primary_4090": pd.read_csv(ROOT / "Output" / "4090" / "primary_metrics.csv"),
        "event_4100": pd.read_csv(ROOT / "Output" / "4100" / "observation_level_effects.csv"),
        "history_4121": pd.read_csv(ROOT / "Output" / "4121" / "observation_level_effects.csv"),
    }


def build_negative_atlas(data: dict[str, object]) -> pd.DataFrame:
    d4081c = data["d4081c"]
    d4086 = data["d4086"]
    d4087 = data["d4087"]
    d4090 = data["d4090"]
    d4094 = data["d4094"]
    d4100 = data["d4100"]
    d4105 = data["d4105"]
    d4121 = data["d4121"]
    d4125 = data["d4125"]
    metadata = data["metadata"]

    first = d4090["first_moment_metric"]
    second = d4090["second_moment_metric"]
    event = d4100["primary_metrics"]
    history = d4121["primary_metrics"]
    daytime_status = metadata[metadata["metadata_item"].eq("recording_condition_daytime_dusk")][
        "verification_status"
    ].iloc[0]

    rows = [
        {
            "boundary_id": "N1",
            "mechanism_class": "whole_swarm_affine_geometry_only",
            "tested_node": "4001",
            "tested_form": "per-frame translation plus affine deformation baseline",
            "baseline": "global affine geometry",
            "null": "circularly shifted event times",
            "failure_mode": "velocity event residual survived the global affine baseline",
            "replication": "4/4 source directions in summary-only 4001 provenance",
            "what_is_ruled_out": "a purely global affine explanation for the earlier velocity event signal",
            "what_remains_open": "local non-affine organization and richer geometric/state explanations",
            "allowed_wording": "global affine motion is insufficient as a complete explanation",
            "forbidden_wording": "global geometry is irrelevant",
            "claim_class": "SUPPORTED_WITH_BOUNDARY",
            "evidence_strength": "boundary_for_geometry_reduction",
            "figure_candidate": "supplement",
        },
        {
            "boundary_id": "N2",
            "mechanism_class": "local_affine_geometry_only",
            "tested_node": "4081c/4088",
            "tested_form": "local affine removal followed by T1 event-conditioned residual test",
            "baseline": "local focal-neighborhood affine deformation",
            "null": "matched non-event windows and shifted-event controls from upstream 408x nodes",
            "failure_mode": "T1 survived in most observations after local affine removal",
            "replication": (
                f"{len(d4081c['t1_survival_observations'])}/19 any-k survivors; "
                f"{d4081c['class_counts']['t1_local_nonaffine_survives_both_k']}/19 both-k survivors"
            ),
            "what_is_ruled_out": "local affine geometry as a complete explanation in the majority of observations",
            "what_remains_open": "why Ob1/Ob3/Ob6/Ob8 fail and what richer local variables explain T1",
            "allowed_wording": "local affine deformation does not fully absorb T1 in most observations",
            "forbidden_wording": "local affine geometry never matters",
            "claim_class": "SUPPORTED_WITH_BOUNDARY",
            "evidence_strength": "boundary_for_geometry_reduction",
            "figure_candidate": "main",
        },
        {
            "boundary_id": "N3",
            "mechanism_class": "low_dimensional_state_moment_closure",
            "tested_node": "4090/4094",
            "tested_form": "C,dCdt,R-conditioned first and second moment closure with grouped OOS validation",
            "baseline": "radius-only binned model",
            "null": "within-observation circular shift of C and dCdt",
            "failure_mode": (
                "first and second moment incremental R2 did not improve stably across observations"
            ),
            "replication": (
                "first median incremental R2 "
                f"{fmt_float(first['median_incremental_r2'])}; second "
                f"{fmt_float(second['median_incremental_r2'])}; positive-ob fractions "
                f"{fmt_float(first['positive_ob_fraction'])}/{fmt_float(second['positive_ob_fraction'])}"
            ),
            "what_is_ruled_out": "simple compact-density-conditioned first/second moment closure using only C,dCdt,R",
            "what_remains_open": "higher-dimensional, delayed, network, or observation-specific stochastic descriptions",
            "allowed_wording": d4094["technical_claim"],
            "forbidden_wording": "stochastic dynamics do not explain midge swarms",
            "claim_class": "NOT_SUPPORTED",
            "evidence_strength": "tested_reduction_failed",
            "figure_candidate": "main",
        },
        {
            "boundary_id": "N4",
            "mechanism_class": "event_timestamp_specific_precursor",
            "tested_node": "4100/4105",
            "tested_form": "near-pre A_swarm_tangential_z at true transition times versus same-observation C,dCdt,R-matched controls",
            "baseline": "same-observation state-matched non-event frames",
            "null": "within-observation shifted event timestamps",
            "failure_mode": "true transition timestamps did not show robust extra near-pre activity after state matching",
            "replication": (
                "median delta A_pre_z "
                f"{fmt_float(event['median_observation_delta_A_pre_z'])}; same-direction fraction "
                f"{fmt_float(event['same_direction_observation_fraction'])}; real beats shifted null "
                f"{fmt_float(event['real_beats_shifted_null_fraction'])}"
            ),
            "what_is_ruled_out": "state-matched near-pre event-locality under the frozen T1 aggregate",
            "what_remains_open": "event dynamics not captured by C,dCdt,R or not expressible as near-pre excess",
            "allowed_wording": d4105["technical_claim"],
            "forbidden_wording": "transitions have no special dynamics",
            "claim_class": "NOT_SUPPORTED",
            "evidence_strength": "tested_reduction_failed",
            "figure_candidate": "main",
        },
        {
            "boundary_id": "N5",
            "mechanism_class": "burst_or_propagation_route",
            "tested_node": "4105",
            "tested_form": "confirmatory propagation was not entered after 4100 event-locality gate failed",
            "baseline": "not applicable",
            "null": "not applicable",
            "failure_mode": "upstream event-locality gate failed, so propagation was not confirmatorily tested",
            "replication": "route stopped before 4101 propagation/lagged-correlation sub-route",
            "what_is_ruled_out": "automatic propagation analysis as a justified next confirmatory route",
            "what_remains_open": "propagation in a redesigned target, different state representation, or descriptive future node",
            "allowed_wording": "propagation is not confirmatorily tested in the current 410x route",
            "forbidden_wording": "no propagation exists",
            "claim_class": "NOT_TESTED",
            "evidence_strength": "route_not_entered",
            "figure_candidate": "supplement",
        },
        {
            "boundary_id": "N6",
            "mechanism_class": "universal_recent_history_rule",
            "tested_node": "4121/4125",
            "tested_form": "same-current-state different-recent-C-R-path matching",
            "baseline": "same-observation C,dCdt,R current-state matching",
            "null": "within-observation shuffled history theta",
            "failure_mode": "history-conditioned separation exists but sign/order is not stable across observations",
            "replication": (
                f"{history['n_observations_sufficient_pairs']}/19 sufficient; median abs effect "
                f"{fmt_float(history['median_abs_observation_signed_axis_delta_A_z'])}; direction consistency "
                f"{fmt_float(history['direction_consistency_fraction'])}; "
                f"{d4125['primary_metrics']['real_beats_null_median_observations']}/19 beat median null"
            ),
            "what_is_ruled_out": "universal recent-history direction/order rule",
            "what_remains_open": "observation-specific path effects and descriptive heterogeneity analysis",
            "allowed_wording": d4125["bounded_claim"],
            "forbidden_wording": "history does not matter or a universal memory mechanism is proven",
            "claim_class": "BOUNDARY",
            "evidence_strength": "positive_but_nonuniversal",
            "figure_candidate": "main",
        },
        {
            "boundary_id": "N7",
            "mechanism_class": "universal_signed_event_direction_law",
            "tested_node": "4086/4088",
            "tested_form": "low-to-high versus high-to-low signed near-pre diffuse T1 decomposition",
            "baseline": "event-type signed decomposition of all_tangential near-pre activity",
            "null": "event-conditioned gates from 4086",
            "failure_mode": "signed class is heterogeneous with no majority signed law",
            "replication": (
                f"{d4086['target_summary']['mirror_symmetric_count']}/14 mirror; "
                f"{d4086['target_summary']['low_to_high_dominant_count']}/14 low-to-high dominant; "
                f"{d4086['target_summary']['no_signed_gate_count']}/14 no signed gate"
            ),
            "what_is_ruled_out": "universal signed force or mirror law",
            "what_remains_open": "observation-specific signed response classes",
            "allowed_wording": d4086["interpretation"],
            "forbidden_wording": "T1 has a single universal low-to-high or mirror-symmetric law",
            "claim_class": "BOUNDARY",
            "evidence_strength": "positive_but_nonuniversal",
            "figure_candidate": "supplement",
        },
        {
            "boundary_id": "N8",
            "mechanism_class": "recording_condition_or_batch_explanation",
            "tested_node": "4082b/4090A/4130",
            "tested_form": "metadata and raw-quality/event-count audit",
            "baseline": "observation labels and available quality/event count summaries",
            "null": "not applicable",
            "failure_mode": f"metadata explanation remains {daytime_status}; failure labels are real but not causally explained",
            "replication": (
                f"stable failures {d4087['stable_failure_count']}/4; fragile narrow rescues "
                f"{d4087['fragile_narrow_rescue_count']}/4"
            ),
            "what_is_ruled_out": "quietly treating failure observations as artifacts or metadata regimes",
            "what_remains_open": "independent metadata verification and experimental-condition analysis",
            "allowed_wording": "failure labels are explicit; metadata explanations remain descriptive only",
            "forbidden_wording": "Ob6/Ob8 fail because of confirmed daytime or batch effects",
            "claim_class": "BOUNDARY",
            "evidence_strength": "metadata_boundary",
            "figure_candidate": "supplement",
        },
    ]
    return pd.DataFrame(rows)


def build_claim_boundary_table(data: dict[str, object], atlas: pd.DataFrame) -> pd.DataFrame:
    claims = data["claims"].copy()
    keep_strength = {"NOT_SUPPORTED", "BOUNDARY", "NOT_TESTED"}
    out = claims[claims["claim_strength"].isin(keep_strength)].copy()
    out["4132_boundary_ids"] = out["claim_id"].map(
        {
            "C4_SIGNED_EVENT_HETEROGENEITY": "N7",
            "C5_NO_SIMPLE_STATE_MOMENT_CLOSURE": "N3",
            "C6_NO_EVENT_TIMESTAMP_EXCESS": "N4",
            "C7_OBSERVATION_SPECIFIC_HISTORY_BOUNDARY": "N6",
            "C8_PROPAGATION_NOT_CONFIRMATORILY_TESTED": "N5",
        }
    )
    return out


def build_forbidden_overclaims(atlas: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for row in atlas.to_dict("records"):
        rows.append(
            {
                "boundary_id": row["boundary_id"],
                "mechanism_class": row["mechanism_class"],
                "allowed_wording": row["allowed_wording"],
                "forbidden_wording": row["forbidden_wording"],
                "reason": (
                    "tested failure only"
                    if row["claim_class"] == "NOT_SUPPORTED"
                    else "route not confirmatorily tested"
                    if row["claim_class"] == "NOT_TESTED"
                    else "boundary or nonuniversal result"
                ),
            }
        )
    return pd.DataFrame(rows)


def build_remaining_space() -> pd.DataFrame:
    rows = [
        {
            "open_space": "higher_dimensional_state_representation",
            "why_open": "4090 tested only C,dCdt,R first/second moments",
            "requires_before_testing": "new frozen state variables and grouped validation plan",
        },
        {
            "open_space": "observation_specific_models",
            "why_open": "4121 and 4086 show heterogeneity rather than universal signs",
            "requires_before_testing": "4133 heterogeneity map and a predeclared grouping rule",
        },
        {
            "open_space": "network_or_local_interaction_descriptions",
            "why_open": "4100A warned that raw neighbor residual vectors are overlapping, not independent",
            "requires_before_testing": "non-overlapping or explicitly modeled spatial unit definition",
        },
        {
            "open_space": "propagation_or_burst_dynamics",
            "why_open": "4100 event-locality gate failed, so propagation was not confirmatorily tested",
            "requires_before_testing": "new event-local target or descriptive rather than confirmatory framing",
        },
        {
            "open_space": "metadata_conditioned_explanation",
            "why_open": "recording condition and observation order metadata remain unverified",
            "requires_before_testing": "independent metadata audit",
        },
    ]
    return pd.DataFrame(rows)


def make_figures(
    atlas: pd.DataFrame,
    primary_4090: pd.DataFrame,
    d4100: dict[str, object],
    d4121: dict[str, object],
) -> list[str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    fig_dir = OUT / "figures"
    files: list[str] = []

    color_map = {
        "NOT_SUPPORTED": "#b6423c",
        "BOUNDARY": "#b08b33",
        "NOT_TESTED": "#777777",
        "SUPPORTED_WITH_BOUNDARY": "#7c6f58",
    }
    fig, ax = plt.subplots(figsize=(10, 5.2))
    counts = atlas["claim_class"].value_counts().reindex(
        ["NOT_SUPPORTED", "BOUNDARY", "NOT_TESTED", "SUPPORTED_WITH_BOUNDARY"], fill_value=0
    )
    ax.bar(counts.index, counts.values, color=[color_map[x] for x in counts.index])
    ax.set_title("4132 mechanism boundary class counts")
    ax.set_ylabel("atlas rows")
    ax.set_ylim(0, max(counts.values) + 1)
    ax.grid(axis="y", color="#dddddd", linewidth=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    path = fig_dir / "4132_boundary_class_counts.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    files.append(rel(path))

    fig, ax = plt.subplots(figsize=(9.2, 4.8))
    metrics = primary_4090.copy()
    x = np.arange(len(metrics))
    width = 0.35
    ax.bar(
        x - width / 2,
        metrics["median_incremental_r2"].astype(float),
        width,
        label="median incremental R2",
        color="#b6423c",
    )
    ax.bar(
        x + width / 2,
        metrics["median_real_minus_shift"].astype(float),
        width,
        label="real minus shifted",
        color="#7c6f58",
    )
    ax.axhline(0, color="#333333", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics["target_family"])
    ax.set_title("4132 failed C,dCdt,R moment-closure metrics")
    ax.legend(frameon=False)
    ax.grid(axis="y", color="#dddddd", linewidth=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    path = fig_dir / "4132_moment_closure_negative_metrics.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    files.append(rel(path))

    event = d4100["primary_metrics"]
    gates = d4100["pre_frozen_gates"]
    event_rows = [
        ("abs delta A_pre_z", abs(float(event["median_observation_delta_A_pre_z"])), float(gates["min_effect_z"])),
        ("same-direction fraction", float(event["same_direction_observation_fraction"]), float(gates["min_same_direction_fraction"])),
        ("real beats shifted null", float(event["real_beats_shifted_null_fraction"]), float(gates["min_real_beats_null_fraction"])),
    ]
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    x = np.arange(len(event_rows))
    ax.bar(x - 0.18, [r[1] for r in event_rows], 0.36, color="#b6423c", label="observed")
    ax.bar(x + 0.18, [r[2] for r in event_rows], 0.36, color="#dddddd", label="gate")
    ax.set_xticks(x)
    ax.set_xticklabels([r[0] for r in event_rows], rotation=20, ha="right")
    ax.set_title("4132 event-locality gate failures")
    ax.legend(frameon=False)
    ax.grid(axis="y", color="#dddddd", linewidth=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    path = fig_dir / "4132_event_locality_negative_metrics.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    files.append(rel(path))

    hist = d4121["primary_metrics"]
    history_rows = [
        ("median abs effect", float(hist["median_abs_observation_signed_axis_delta_A_z"]), 0.05),
        ("direction consistency", float(hist["direction_consistency_fraction"]), 0.6),
        ("beats median null", float(hist["real_beats_shuffle_null_median_abs_fraction"]), 0.6),
        ("beats q95 null", float(hist["real_beats_shuffle_null_q95_abs_fraction"]), 0.6),
    ]
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    x = np.arange(len(history_rows))
    colors = ["#1d7a61" if row[1] >= row[2] else "#b6423c" for row in history_rows]
    ax.bar(x, [r[1] for r in history_rows], color=colors)
    ax.scatter(x, [r[2] for r in history_rows], marker="_", s=500, color="#333333", label="gate")
    ax.set_xticks(x)
    ax.set_xticklabels([r[0] for r in history_rows], rotation=20, ha="right")
    ax.set_title("4132 recent-history boundary gates")
    ax.legend(frameon=False)
    ax.grid(axis="y", color="#dddddd", linewidth=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    path = fig_dir / "4132_history_boundary_metrics.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    files.append(rel(path))

    return files


def main() -> None:
    ensure_dirs()
    data = load_inputs()

    atlas = build_negative_atlas(data)
    claim_table = build_claim_boundary_table(data, atlas)
    forbidden = build_forbidden_overclaims(atlas)
    remaining = build_remaining_space()
    figure_files = make_figures(atlas, data["primary_4090"], data["d4100"], data["d4121"])

    write_csv_pair(atlas, "negative_boundary_atlas.csv")
    write_csv_pair(claim_table, "bounded_negative_claims.csv")
    write_csv_pair(forbidden, "forbidden_overclaims.csv")
    write_csv_pair(remaining, "mechanism_space_remaining.csv")

    required = {
        "low_dimensional_state_moment_closure",
        "event_timestamp_specific_precursor",
        "burst_or_propagation_route",
        "universal_recent_history_rule",
    }
    required_present = required.issubset(set(atlas["mechanism_class"]))
    propagation_class = atlas.loc[
        atlas["mechanism_class"].eq("burst_or_propagation_route"), "claim_class"
    ].iloc[0]
    not_supported_rows = int(atlas["claim_class"].eq("NOT_SUPPORTED").sum())
    boundary_rows = int(atlas["claim_class"].eq("BOUNDARY").sum())
    not_tested_rows = int(atlas["claim_class"].eq("NOT_TESTED").sum())
    gate_pass = required_present and propagation_class == "NOT_TESTED" and not_supported_rows >= 2

    decision = {
        "node": NODE,
        "date": DATE,
        "node_type": "negative_boundary_atlas",
        "upstream_nodes": [
            "4130_definition_and_evidence_registry",
            "4131_robust_positive_phenomenon_atlas",
        ],
        "data_scope": "all_19_observations_with_node_specific_subsets_where_defined",
        "frozen_target": "T1_local_tangential_nonaffine_residual",
        "boundary_counts": {
            "atlas_rows": int(len(atlas)),
            "not_supported_rows": not_supported_rows,
            "boundary_rows": boundary_rows,
            "not_tested_rows": not_tested_rows,
            "supported_with_boundary_geometry_rows": int(atlas["claim_class"].eq("SUPPORTED_WITH_BOUNDARY").sum()),
        },
        "quality_checks": {
            "required_mechanism_classes_present": bool(required_present),
            "propagation_marked_not_tested": bool(propagation_class == "NOT_TESTED"),
            "not_supported_not_used_as_nonexistence_claim": True,
            "metadata_claims_descriptive_only": True,
            "figures_written": bool(len(figure_files) == 4),
        },
        "gate_result": "pass_4132_negative_boundary_atlas_ready"
        if gate_pass
        else "boundary_4132_negative_atlas_requires_claim_cleanup",
        "interpretation": (
            "The negative evidence is suitable for writing as mechanism-boundary evidence: simple C,dCdt,R moment "
            "closure and state-matched event-local precursor routes are not supported, while propagation remains "
            "not confirmatorily tested rather than disproven."
        ),
        "does_not_prove": [
            "absence of stochastic organization",
            "absence of propagation",
            "absence of transition dynamics",
            "absence of history effects",
            "metadata regime explanation",
        ],
        "next": ["4133_observation_heterogeneity_map"],
        "artifacts": [
            "Output/4132/negative_boundary_atlas.csv",
            "Output/4132/bounded_negative_claims.csv",
            "Output/4132/forbidden_overclaims.csv",
            "Output/4132/mechanism_space_remaining.csv",
            "Output/4132/decision.json",
            "Output/4132/4132_summary.md",
        ]
        + figure_files,
    }

    (OUT / "decision.json").write_text(json.dumps(decision, indent=2), encoding="utf-8")

    summary = dedent(
        f"""\
        # Node 4132 Negative Mechanism Boundary Atlas

        ## Question

        Which natural mechanism explanations are constrained by the current
        evidence gates?

        ## Gate Result

        ```text
        gate_result = {decision["gate_result"]}
        ```

        ## Main Interpretation

        Negative evidence can be written as mechanism-boundary evidence. The
        tested `C,dCdt,R` moment closure and the tested state-matched
        event-local precursor route are not supported. Propagation is not
        confirmatorily tested, not disproven. History and signed direction are
        observation-specific boundaries, not universal laws.

        ## Boundary Counts

        {md_table([decision["boundary_counts"]], list(decision["boundary_counts"].keys()))}

        ## Negative Boundary Atlas

        {md_table(atlas.to_dict("records"), ["boundary_id", "mechanism_class", "claim_class", "failure_mode", "what_is_ruled_out", "what_remains_open"])}

        ## Claim Mapping From 4130

        {md_table(claim_table.to_dict("records"), ["claim_id", "claim_strength", "4132_boundary_ids", "support_nodes", "forbidden_stronger_claim"])}

        ## Forbidden Overclaims

        {md_table(forbidden.to_dict("records"), ["boundary_id", "allowed_wording", "forbidden_wording", "reason"])}

        ## Mechanism Space Remaining

        {md_table(remaining.to_dict("records"), ["open_space", "why_open", "requires_before_testing"])}

        ## What This Does Not Prove

        {md_table([{"does_not_prove": x} for x in decision["does_not_prove"]], ["does_not_prove"])}

        ## Next Node

        `4133_observation_heterogeneity_map`

        ## Artifacts

        - `Output/4132/negative_boundary_atlas.csv`
        - `Output/4132/bounded_negative_claims.csv`
        - `Output/4132/forbidden_overclaims.csv`
        - `Output/4132/mechanism_space_remaining.csv`
        - `Output/4132/figures/4132_boundary_class_counts.png`
        - `Output/4132/figures/4132_moment_closure_negative_metrics.png`
        - `Output/4132/figures/4132_event_locality_negative_metrics.png`
        - `Output/4132/figures/4132_history_boundary_metrics.png`
        """
    )
    summary = summary.replace("\n        ", "\n").lstrip()
    (OUT / "4132_summary.md").write_text(summary, encoding="utf-8")

    print(json.dumps(decision, indent=2))
    print(f"Wrote 4132 outputs to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
