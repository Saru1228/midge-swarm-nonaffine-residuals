#!/usr/bin/env python3
"""4144 definition, notation, figure-source, and claim-boundary cleanup.

This node is a manuscript-facing synthesis step. It does not rerun the
scientific analyses. Instead, it turns 4141-4143 into traceable reviewer
defense tables and concrete 4145 manuscript edit targets.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4144"
TABLES = OUT / "tables"
DATE = "2026-09-02"
NODE = "4144_definition_notation_figure_cleanup"


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def ensure_dirs() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)


def write_csv(df: pd.DataFrame, filename: str) -> None:
    df.to_csv(OUT / filename, index=False)
    df.to_csv(TABLES / filename, index=False)


def fmt(value: Any, digits: int = 3) -> str:
    try:
        value_f = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(value_f):
        return "NA"
    return f"{value_f:.{digits}g}"


def md_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    if not rows:
        return "_No rows._"
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        vals: list[str] = []
        for col in columns:
            val = row.get(col, "")
            if isinstance(val, float):
                vals.append(fmt(val, 4))
            else:
                vals.append(str(val).replace("\n", " ").replace("|", "\\|"))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def get_variant(summary: pd.DataFrame, variant: str) -> dict[str, Any]:
    rows = summary.loc[summary["variant"] == variant]
    if rows.empty:
        raise ValueError(f"Missing variant {variant}")
    return rows.iloc[0].to_dict()


def get_phase(summary: pd.DataFrame, variant: str, phase: str) -> dict[str, Any]:
    rows = summary.loc[
        (summary["variant"] == variant)
        & (summary["variable"] == "all_tangential")
        & (summary["phase"] == phase)
    ]
    if rows.empty:
        raise ValueError(f"Missing phase row {variant}/{phase}")
    return rows.iloc[0].to_dict()


def build_claim_rows(inputs: dict[str, Any]) -> pd.DataFrame:
    d4141 = inputs["d4141"]
    d4142 = inputs["d4142"]
    d4143 = inputs["d4143"]
    centered = get_variant(inputs["survival_4142"], "centered_1s")
    past = get_variant(inputs["survival_4142"], "past_1s")
    none = get_variant(inputs["survival_4142"], "none_z")
    centered_near = get_phase(inputs["phase_4142"], "centered_1s", "near_pre")
    past_near = get_phase(inputs["phase_4142"], "past_1s", "near_pre")
    none_near = get_phase(inputs["phase_4142"], "none_z", "near_pre")
    m41 = d4141["primary_metrics"]
    m43 = d4143["primary_metrics"]

    rows = [
        {
            "claim_id": "C1_T1_LOCAL_NONAFFINE_SURVIVAL",
            "claim_strength_after_4144": "supported_bounded",
            "evidence_update": (
                f"Observed N_both={m41['observed_n_both']}/19 and "
                f"N_any={m41['observed_n_any']}/19; 4141 smoke null "
                f"p_both={fmt(m41['p_omnibus_both_ge_14'], 4)}, "
                f"null q95={fmt(m41['n_both_null_q95'])}, "
                f"null max={fmt(m41['n_both_null_max'])}."
            ),
            "allowed_statement": (
                "T1 is a common local tangential non-affine residual after "
                "local affine subtraction under the frozen event-control gate."
            ),
            "boundary_statement": (
                "This does not establish universality, mechanism, or a formal "
                "high-B omnibus p-value."
            ),
            "manuscript_target": "Abstract; Results T1 survival; Discussion limitations",
            "source_artifacts": "Output/4141/decision.json; Output/4141/p_omnibus.json",
        },
        {
            "claim_id": "C2_DETRENDING_BOUNDARY",
            "claim_strength_after_4144": "boundary_supported",
            "evidence_update": (
                f"Centered detrending reproduced N_both={int(centered['n_both'])}/19; "
                f"past-only gave N_both={int(past['n_both'])}/19; "
                f"no-detrend robust-z gave N_both={int(none['n_both'])}/19."
            ),
            "allowed_statement": (
                "The T1 signal is not erased by the detrending challenge, but "
                "the exact 14/19 both-scale count is tied to centered detrending."
            ),
            "boundary_statement": (
                "Do not describe the main count as fully invariant to causal "
                "past-only detrending."
            ),
            "manuscript_target": "Methods detrending; Results T1 survival; Discussion limitations",
            "source_artifacts": "Output/4142/decision.json; Output/4142/survival_variant_summary.csv",
        },
        {
            "claim_id": "C3_LOCAL_AFFINE_CONDITIONING_QC",
            "claim_strength_after_4144": "artifact_control_pass",
            "evidence_update": (
                f"{int(m43['n_combo_passes'])}/{int(m43['n_ob_k_combos'])} "
                f"observation-k combinations passed; all "
                f"{int(m43['n_observations_all_k_pass'])}/"
                f"{int(m43['n_observations'])} observations passed both k values; "
                f"median condition number={fmt(m43['median_condition_number_over_combos'])}, "
                f"max q95 condition number={fmt(m43['max_combo_q95_condition_number'])}; "
                f"fraction condition>100={fmt(m43['max_combo_frac_condition_gt_100'])}."
            ),
            "allowed_statement": (
                "The local affine subtraction used for T1 is numerically "
                "defensible in the sampled all-observation QC."
            ),
            "boundary_statement": (
                "This does not prove the biological correctness of T1 or remove "
                "all possible preprocessing artifacts."
            ),
            "manuscript_target": "Methods robustness/QC paragraph; Results T1 survival",
            "source_artifacts": (
                "Output/4143/decision.json; "
                "Output/4143/local_affine_conditioning_summary.csv"
            ),
        },
        {
            "claim_id": "C4_DIFFUSE_NEAR_PRE_TIMING",
            "claim_strength_after_4144": "descriptive_bounded",
            "evidence_update": (
                f"Near-pre all-tangential gate counts were centered "
                f"{int(centered_near['phase_gate_count'])}/14, past-only "
                f"{int(past_near['phase_gate_count'])}/14, and no-detrend "
                f"{int(none_near['phase_gate_count'])}/14."
            ),
            "allowed_statement": (
                "Near-pre timing is a moderate descriptive profile within the "
                "diffuse tangential phenotype."
            ),
            "boundary_statement": (
                "Because state-matched event-locality failed earlier, do not "
                "write near-pre timing as a causal precursor."
            ),
            "manuscript_target": "Results spatial/timing; Discussion limitations",
            "source_artifacts": "Output/4142/phase_variant_summary.csv; Output/4100/decision.json",
        },
        {
            "claim_id": "C5_SURVIVOR_CLASS_ROBUSTNESS",
            "claim_strength_after_4144": "supported_with_scope_limit",
            "evidence_update": (
                "The pre-4144 survivor class remains the scale/lag robustness "
                "scope: 14/15 survivor observations were robust to nearby "
                "scale and lag perturbations."
            ),
            "allowed_statement": (
                "Robustness is high inside the survivor class after the main "
                "survival screen."
            ),
            "boundary_statement": (
                "Do not generalize survivor-class robustness to all 19 "
                "observations."
            ),
            "manuscript_target": "Results T1 survival; evidence-to-claim table",
            "source_artifacts": "Output/4131/positive_phenomenon_atlas.csv; Output/4082/decision.json",
        },
        {
            "claim_id": "C6_NEGATIVE_REDUCTION_BOUNDARIES",
            "claim_strength_after_4144": "supported_negative_boundary",
            "evidence_update": (
                "Compact state moment closure, state-matched near-pre "
                "event-locality, and universal history-rule routes remained "
                "insufficient in the earlier 4090/4100/4121 chain."
            ),
            "allowed_statement": (
                "The paper can report tested reduction boundaries as part of "
                "the contribution."
            ),
            "boundary_statement": (
                "A failed tested reduction is not evidence that all mechanisms "
                "or all stochastic descriptions are impossible."
            ),
            "manuscript_target": "Results reduction boundaries; Discussion",
            "source_artifacts": "Output/4090/decision.json; Output/4100/decision.json; Output/4121/decision.json",
        },
    ]
    return pd.DataFrame(rows)


def build_gap_rows(inputs: dict[str, Any]) -> pd.DataFrame:
    mismatch = inputs["mismatch_4140"]
    d4141 = inputs["d4141"]
    d4142 = inputs["d4142"]
    d4143 = inputs["d4143"]
    m41 = d4141["primary_metrics"]
    m43 = d4143["primary_metrics"]

    resolutions = {
        "condition-number QC": {
            "4144_resolution": "resolved_pass",
            "evidence": (
                f"4143 passed {int(m43['n_combo_passes'])}/"
                f"{int(m43['n_ob_k_combos'])} observation-k combinations; "
                f"median condition number {fmt(m43['median_condition_number_over_combos'])}."
            ),
            "remaining_boundary": "Sampled QC only; not a proof against every preprocessing artifact.",
            "4145_action": "Add a methods/results QC sentence for local affine conditioning.",
        },
        "full-pipeline omnibus null": {
            "4144_resolution": "partially_resolved_smoke",
            "evidence": (
                f"4141 smoke null B={int(m41['n_null_replicates'])}: "
                f"observed N_both={int(m41['observed_n_both'])}, "
                f"null q95={fmt(m41['n_both_null_q95'])}, "
                f"null max={fmt(m41['n_both_null_max'])}, "
                f"plus-one p={fmt(m41['p_omnibus_both_ge_14'], 4)}."
            ),
            "remaining_boundary": "Use as runtime-validated supportive calibration, not formal inference.",
            "4145_action": "Mention as smoke-level calibration or defer formal p-value language.",
        },
        "detrending challenge": {
            "4144_resolution": "resolved_boundary",
            "evidence": (
                "4142 result: centered 14/19, past-only 11/19, no-detrend "
                "13/19 for both-scale support."
            ),
            "remaining_boundary": "Exact 14/19 count is preprocessing-sensitive.",
            "4145_action": "Soften local robustness language and state the detrending boundary.",
        },
    }

    rows: list[dict[str, Any]] = []
    for item in mismatch.to_dict(orient="records"):
        resolution = resolutions.get(item["item"], {})
        merged = dict(item)
        merged.update(resolution)
        rows.append(merged)
    return pd.DataFrame(rows)


def build_figure_manifest(inputs: dict[str, Any]) -> pd.DataFrame:
    source_map = inputs["figure_source_map"]
    latex_dir = ROOT / "mypaper2" / "Latex" / "figures"
    rows: list[dict[str, Any]] = []

    grouped = source_map.groupby(["figure_id", "final_panel_package_artifact"], dropna=False)
    for (figure_id, artifact), group in grouped:
        package_path = ROOT / str(artifact)
        latex_path = latex_dir / package_path.name
        rows.append(
            {
                "figure_id": figure_id,
                "panel_ids": ",".join(group["panel_id"].astype(str)),
                "source_nodes": "; ".join(sorted(set(group["source_node"].astype(str)))),
                "source_artifacts": "; ".join(sorted(set(group["source_artifact"].astype(str)))),
                "final_panel_package_artifact": str(artifact),
                "package_exists": package_path.exists(),
                "package_size_bytes": package_path.stat().st_size if package_path.exists() else 0,
                "latex_figure_file": rel(latex_path),
                "latex_copy_exists": latex_path.exists(),
                "latex_copy_size_bytes": latex_path.stat().st_size if latex_path.exists() else 0,
                "ready_for_manuscript": package_path.exists() and latex_path.exists(),
            }
        )

    return pd.DataFrame(rows)


def build_update_targets() -> pd.DataFrame:
    rows = [
        {
            "target_file": "mypaper2/Latex/00_abstract.tex",
            "section": "Abstract",
            "required_update": (
                "Add 4141 smoke-null, 4142 detrending-boundary, and 4143 "
                "affine-conditioning QC in concise bounded language."
            ),
            "priority": "high",
        },
        {
            "target_file": (
                "mypaper2/Latex/Part3/"
                "03_methods_affine_reduction_and_controls_v2.tex"
            ),
            "section": "Methods",
            "required_update": (
                "Describe submission-hardening checks: full-pipeline "
                "pseudo-event null, detrending challenge, and local affine "
                "conditioning QC."
            ),
            "priority": "high",
        },
        {
            "target_file": "mypaper2/Latex/Part4/04_results_t1_survival_v2.tex",
            "section": "Results: T1 survival",
            "required_update": (
                "Report 4141 smoke-null support, 4142 centered/past-only/"
                "none counts, and 4143 conditioning QC."
            ),
            "priority": "high",
        },
        {
            "target_file": "mypaper2/Latex/Part4/04_results_diffuse_phenotype_v2.tex",
            "section": "Results: diffuse phenotype",
            "required_update": (
                "Bound near-pre timing using 4142 phase counts and earlier "
                "state-matched event-locality failure."
            ),
            "priority": "medium",
        },
        {
            "target_file": "mypaper2/Latex/Part4/04_results_empirical_boundary_v2.tex",
            "section": "Evidence-to-claim table",
            "required_update": (
                "Add rows for detrending challenge and local affine "
                "conditioning QC; update T1 survival evidence."
            ),
            "priority": "high",
        },
        {
            "target_file": (
                "mypaper2/Latex/Part5/"
                "05_discussion_limitations_future_v2.tex"
            ),
            "section": "Discussion limitations",
            "required_update": (
                "Replace pending-check language with completed 4141-4143 "
                "outcomes and remaining high-B optional boundary."
            ),
            "priority": "high",
        },
    ]
    return pd.DataFrame(rows)


def write_reviewer_defense(
    claim_rows: pd.DataFrame,
    gap_rows: pd.DataFrame,
    figure_manifest: pd.DataFrame,
) -> None:
    defense_rows = [
        {
            "Reviewer concern": "Is the 14/19 survival count larger than a pipeline-level null?",
            "414x response": "4141 ran a full-pipeline pseudo-event smoke null.",
            "Evidence": (
                "Observed N_both=14; null mean=4.49, q95=8, max=11, "
                "plus-one p=0.0099 over B=100."
            ),
            "Manuscript boundary": "Call this smoke-level calibration unless B>=1000 is run.",
        },
        {
            "Reviewer concern": "Does centered detrending use future information?",
            "414x response": "4142 compared centered, past-only, and no-detrend definitions.",
            "Evidence": "N_both was 14/19, 11/19, and 13/19, respectively.",
            "Manuscript boundary": "The exact 14/19 count is centered-detrending dependent.",
        },
        {
            "Reviewer concern": "Could local affine subtraction be numerically unstable?",
            "414x response": "4143 tested rank sufficiency and condition numbers.",
            "Evidence": "38/38 observation-k combinations passed; median condition number 2.37.",
            "Manuscript boundary": "This is a numerical QC pass, not a mechanism proof.",
        },
        {
            "Reviewer concern": "Are the figures traceable to outputs?",
            "414x response": "4144 checked 4134 source mapping and LaTeX figure copies.",
            "Evidence": (
                f"{int(figure_manifest['ready_for_manuscript'].sum())}/"
                f"{len(figure_manifest)} final figure packages are present in LaTeX."
            ),
            "Manuscript boundary": "Figures remain evidence panels, not camera-ready final graphics.",
        },
    ]

    text = "\n".join(
        [
            "# 4144 Reviewer Defense Table",
            "",
            f"Node: `{NODE}`",
            f"Date: {DATE}",
            "",
            md_table(
                defense_rows,
                [
                    "Reviewer concern",
                    "414x response",
                    "Evidence",
                    "Manuscript boundary",
                ],
            ),
            "",
            "## Claim Boundary Updates",
            "",
            md_table(
                claim_rows.to_dict(orient="records"),
                [
                    "claim_id",
                    "claim_strength_after_4144",
                    "evidence_update",
                    "allowed_statement",
                    "boundary_statement",
                ],
            ),
            "",
            "## Review 007 Gap Resolution",
            "",
            md_table(
                gap_rows.to_dict(orient="records"),
                ["item", "4144_resolution", "evidence", "remaining_boundary", "4145_action"],
            ),
            "",
        ]
    )
    (OUT / "reviewer_defense_table.md").write_text(text, encoding="utf-8")


def write_summary(
    inputs: dict[str, Any],
    claim_rows: pd.DataFrame,
    gap_rows: pd.DataFrame,
    figure_manifest: pd.DataFrame,
    update_targets: pd.DataFrame,
    decision: dict[str, Any],
) -> None:
    m41 = inputs["d4141"]["primary_metrics"]
    m43 = inputs["d4143"]["primary_metrics"]
    summary = f"""# 4144 Definition, Notation, and Figure-Source Cleanup

Node: `{NODE}`  
Date: {DATE}

## Purpose

4144 did not rerun the scientific analysis. It converted the completed
submission-hardening checks into manuscript-facing claim boundaries, figure
source provenance, and 4145 edit targets.

## Main Findings

- The 4141 full-pipeline pseudo-event null is supportive at smoke scale:
  observed `N_both = {m41['observed_n_both']}/19`, null mean
  `{fmt(m41['n_both_null_mean'])}`, null q95 `{fmt(m41['n_both_null_q95'])}`,
  null max `{fmt(m41['n_both_null_max'])}`, plus-one
  `p_both = {fmt(m41['p_omnibus_both_ge_14'], 4)}` over `B = {m41['n_null_replicates']}`.
- The 4142 detrending challenge is a boundary, not a stop: centered detrending
  reproduced `14/19` both-scale support, past-only detrending reduced this to
  `11/19`, and no-detrend robust-z gave `13/19`.
- The 4143 local-affine conditioning QC passed: `{int(m43['n_combo_passes'])}/`
  `{int(m43['n_ob_k_combos'])}` observation-k combinations passed, all
  `{int(m43['n_observations_all_k_pass'])}/19` observations passed both k
  values, median condition number was `{fmt(m43['median_condition_number_over_combos'])}`,
  and no sampled fit had condition number greater than 100.
- Figure-source cleanup found `{int(figure_manifest['ready_for_manuscript'].sum())}/`
  `{len(figure_manifest)}` final figure packages available in the LaTeX figure
  directory.

## Routing Decision

`{decision['gate_result']}`

4145 should now update the manuscript rather than open a new scientific node.
The manuscript should keep three boundaries visible: 4141 is smoke-level unless
expanded to high B, the exact 14/19 count is centered-detrending dependent, and
4143 is a numerical QC pass rather than a biological mechanism result.

## Outputs

- `claim_boundary_updates.csv`
- `review007_gap_resolution.csv`
- `figure_source_manifest.csv`
- `manuscript_update_targets.csv`
- `reviewer_defense_table.md`
- `decision.json`
"""
    (OUT / "4144_summary.md").write_text(summary, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    inputs = {
        "d4141": read_json(ROOT / "Output" / "4141" / "decision.json"),
        "d4142": read_json(ROOT / "Output" / "4142" / "decision.json"),
        "d4143": read_json(ROOT / "Output" / "4143" / "decision.json"),
        "mismatch_4140": read_csv(ROOT / "Output" / "4140" / "definition_mismatches.csv"),
        "survival_4142": read_csv(ROOT / "Output" / "4142" / "survival_variant_summary.csv"),
        "phase_4142": read_csv(ROOT / "Output" / "4142" / "phase_variant_summary.csv"),
        "figure_source_map": read_csv(ROOT / "Output" / "4134" / "figure_source_map.csv"),
    }

    claim_rows = build_claim_rows(inputs)
    gap_rows = build_gap_rows(inputs)
    figure_manifest = build_figure_manifest(inputs)
    update_targets = build_update_targets()

    write_csv(claim_rows, "claim_boundary_updates.csv")
    write_csv(gap_rows, "review007_gap_resolution.csv")
    write_csv(figure_manifest, "figure_source_manifest.csv")
    write_csv(update_targets, "manuscript_update_targets.csv")

    n_gap_resolved = int((gap_rows["4144_resolution"] != "").sum())
    n_fig_ready = int(figure_manifest["ready_for_manuscript"].sum())
    n_fig_total = int(len(figure_manifest))
    has_stop = n_fig_ready != n_fig_total
    decision = {
        "node": NODE,
        "date": DATE,
        "gate_result": (
            "pass_4144_ready_for_4145_with_detrending_and_smoke_null_boundaries"
            if not has_stop
            else "boundary_4144_missing_figure_sources_before_4145"
        ),
        "primary_metrics": {
            "n_claim_boundary_updates": int(len(claim_rows)),
            "n_review007_gap_items": int(len(gap_rows)),
            "n_review007_gap_items_resolved_or_bounded": n_gap_resolved,
            "n_final_figure_packages_ready": n_fig_ready,
            "n_final_figure_packages_total": n_fig_total,
            "all_final_figure_packages_ready": not has_stop,
        },
        "manuscript_boundaries": [
            "Use 4141 as smoke-level omnibus-null calibration unless B>=1000 is run.",
            "State that the exact 14/19 both-scale count is tied to centered detrending.",
            "Use 4143 as numerical affine-fit QC rather than a mechanism claim.",
        ],
        "next": ["4145_manuscript_reintegration"],
    }

    write_reviewer_defense(claim_rows, gap_rows, figure_manifest)
    write_summary(inputs, claim_rows, gap_rows, figure_manifest, update_targets, decision)
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2), encoding="utf-8")

    print(json.dumps(decision, indent=2))


if __name__ == "__main__":
    main()
