"""4135 manuscript-style technical synthesis.

This terminal 413x synthesis node turns the figure-ready evidence package into
manuscript-style text modules and evidence-to-claim tables. It does not reopen
mechanism search; it freezes the bounded story supported by 4130-4134.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from textwrap import dedent

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4135"
DATE = "2026-08-28"
NODE = "4135_manuscript_style_technical_synthesis"


def ensure_dirs() -> None:
    (OUT / "tables").mkdir(parents=True, exist_ok=True)


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def write_csv_pair(df: pd.DataFrame, name: str) -> None:
    df.to_csv(OUT / name, index=False)
    df.to_csv(OUT / "tables" / name, index=False)


def md_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    if not rows:
        return "_No rows._"
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        values: list[str] = []
        for col in columns:
            value = row.get(col, "")
            if isinstance(value, float):
                if math.isfinite(value):
                    values.append(f"{value:.4g}")
                else:
                    values.append("NA")
            else:
                values.append(str(value).replace("\n", " ").replace("|", "\\|"))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def fmt(value: object, digits: int = 3) -> str:
    try:
        value_f = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(value_f):
        return "NA"
    return f"{value_f:.{digits}g}"


def load_inputs() -> dict[str, object]:
    return {
        "d4130": read_json(ROOT / "Output" / "4130" / "decision.json"),
        "d4131": read_json(ROOT / "Output" / "4131" / "decision.json"),
        "d4132": read_json(ROOT / "Output" / "4132" / "decision.json"),
        "d4133": read_json(ROOT / "Output" / "4133" / "decision.json"),
        "d4134": read_json(ROOT / "Output" / "4134" / "decision.json"),
        "claim_registry": read_csv(ROOT / "Output" / "4130" / "claim_strength_registry.csv"),
        "m5_claim_review": read_csv(ROOT / "Output" / "4133_M5_review_before_4134" / "claim_storyline_review.csv"),
        "figure_manifest": read_csv(ROOT / "Output" / "4134" / "main_figure_manifest.csv"),
        "panel_metadata": read_csv(ROOT / "Output" / "4134" / "panel_metadata.csv"),
        "caption_drafts": read_csv(ROOT / "Output" / "4134" / "figure_caption_drafts.csv"),
        "master": read_csv(ROOT / "Output" / "4133" / "observation_master_table.csv"),
        "primary_4090": read_csv(ROOT / "Output" / "4090" / "primary_metrics.csv"),
        "effects_4100": read_csv(ROOT / "Output" / "4100" / "observation_level_effects.csv"),
        "effects_4121": read_csv(ROOT / "Output" / "4121" / "observation_level_effects.csv"),
        "associations": read_csv(ROOT / "Output" / "4133" / "heterogeneity_associations.csv"),
    }


def summary_metrics(inputs: dict[str, object]) -> dict[str, object]:
    d4131: dict[str, object] = inputs["d4131"]  # type: ignore[assignment]
    d4133: dict[str, object] = inputs["d4133"]  # type: ignore[assignment]
    primary_4090: pd.DataFrame = inputs["primary_4090"]  # type: ignore[assignment]
    effects_4100: pd.DataFrame = inputs["effects_4100"]  # type: ignore[assignment]
    effects_4121: pd.DataFrame = inputs["effects_4121"]  # type: ignore[assignment]
    metrics = dict(d4131.get("primary_metrics", {}))
    primary_4090 = primary_4090.copy()
    effects_4100 = effects_4100.copy()
    effects_4121 = effects_4121.copy()
    primary_4090["median_incremental_r2"] = pd.to_numeric(primary_4090["median_incremental_r2"], errors="coerce")
    primary_4090["positive_ob_fraction"] = pd.to_numeric(primary_4090["positive_ob_fraction"], errors="coerce")
    effects_4100["median_delta_A_pre_z"] = pd.to_numeric(effects_4100["median_delta_A_pre_z"], errors="coerce")
    effects_4121["real_beats_null_median_abs"] = effects_4121["real_beats_null_median_abs"].astype(str).str.lower().eq("true")
    effects_4121["real_beats_null_q95_abs"] = effects_4121["real_beats_null_q95_abs"].astype(str).str.lower().eq("true")
    effects_4121["median_signed_axis_delta_A_z"] = pd.to_numeric(effects_4121["median_signed_axis_delta_A_z"], errors="coerce")
    effects_4121["real_minus_null_median_abs_effect"] = pd.to_numeric(
        effects_4121["real_minus_null_median_abs_effect"], errors="coerce"
    )
    first = primary_4090[primary_4090["target_family"].astype(str).eq("first_moment")].iloc[0]
    second = primary_4090[primary_4090["target_family"].astype(str).eq("second_moment")].iloc[0]
    return {
        "t1_any": int(metrics["t1_survival_any_k_observations"]),
        "t1_both": int(metrics["t1_survival_both_k_observations"]),
        "total_ob": int(metrics["total_observations"]),
        "scale_robust": int(metrics["scale_lag_robust_observations"]),
        "scale_tested": int(metrics["scale_lag_tested_survivor_observations"]),
        "diffuse": int(metrics["diffuse_all_tangential_gate_observations"]),
        "diffuse_tested": int(metrics["diffuse_all_tangential_tested_observations"]),
        "near_pre": int(metrics["all_tangential_near_pre_gate_observations"]),
        "history_median": int(metrics["history_real_beats_shuffle_median_observations"]),
        "history_direction_consistency": float(metrics["history_direction_consistency_fraction"]),
        "first_moment_r2": float(first["median_incremental_r2"]),
        "second_moment_r2": float(second["median_incremental_r2"]),
        "first_moment_positive_fraction": float(first["positive_ob_fraction"]),
        "second_moment_positive_fraction": float(second["positive_ob_fraction"]),
        "event_local_median_delta": float(effects_4100["median_delta_A_pre_z"].median()),
        "event_local_positive_fraction": float((effects_4100["median_delta_A_pre_z"] > 0).mean()),
        "history_q95": int(effects_4121["real_beats_null_q95_abs"].sum()),
        "history_median_effect": float(effects_4121["real_minus_null_median_abs_effect"].median()),
        "history_signed_positive_fraction": float((effects_4121["median_signed_axis_delta_A_z"] > 0).mean()),
        "class_counts": d4133.get("class_counts", {}),
        "association_counts": d4133.get("association_counts", {}),
    }


def build_title_candidates() -> pd.DataFrame:
    rows = [
        {
            "title_id": "T1",
            "title": "Local non-affine organization in laboratory midge swarms beyond affine geometry and low-dimensional state descriptions",
            "style": "conservative",
            "strength": "best_overall_fit",
            "risk": "long but accurate",
        },
        {
            "title_id": "T2",
            "title": "A bounded local non-affine motion signature in laboratory midge swarms",
            "style": "concise",
            "strength": "clear and modest",
            "risk": "less explicit about negative reductions",
        },
        {
            "title_id": "T3",
            "title": "A local non-affine residual in midge swarms survives affine reduction but resists simple state closure",
            "style": "mechanism-boundary",
            "strength": "states both positive and negative result",
            "risk": "slightly technical",
        },
        {
            "title_id": "T4",
            "title": "Mapping reproducible local residual motion and reduction limits in disordered midge swarms",
            "style": "synthesis",
            "strength": "matches 413x evidence synthesis",
            "risk": "less direct about T1",
        },
        {
            "title_id": "T5",
            "title": "Common but non-universal local non-affine motion in laboratory midge swarms",
            "style": "result-forward",
            "strength": "highly readable",
            "risk": "does not mention tested mechanism boundaries",
        },
    ]
    return pd.DataFrame(rows)


def build_main_claim_registry(claim_review: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for record in claim_review.to_dict("records"):
        claim_id = str(record.get("claim_id", ""))
        if claim_id == "C8_PROPAGATION_NOT_CONFIRMATORILY_TESTED":
            manuscript_role = "limitations_or_open_route"
        elif str(record.get("m5_status", "")).startswith("SUPPLEMENT"):
            manuscript_role = "supplementary_boundary"
        else:
            manuscript_role = "main_result_with_boundary"
        rows.append(
            {
                "claim_id": claim_id,
                "claim_strength": record.get("claim_strength", ""),
                "manuscript_role": manuscript_role,
                "recommended_location": record.get("recommended_4134_location", ""),
                "allowed_wording": record.get("allowed_claim_text", ""),
                "required_conditions": record.get("required_conditions", ""),
                "boundary_observations": record.get("boundary_observations", ""),
                "forbidden_stronger_claim": record.get("forbidden_stronger_claim", ""),
            }
        )
    return pd.DataFrame(rows)


def build_evidence_to_claim_map(m: dict[str, object]) -> pd.DataFrame:
    rows = [
        {
            "claim_id": "C1_LOCAL_NONAFFINE_SURVIVAL",
            "claim_text": "Local affine deformation is insufficient to remove the transition-linked tangential residual in most observations.",
            "main_figure": "Figure 2",
            "supporting_nodes": "4081c;4082;4088;4131;4133;4134",
            "supporting_metrics": f"{m['t1_any']}/{m['total_ob']} any-k survival; {m['t1_both']}/{m['total_ob']} both-k survival",
            "baseline_or_null": "local affine subtraction plus event/non-event and shifted-event controls from 408x",
            "boundary": "Ob1, Ob3, Ob6, Ob8 fail or remain boundary cases.",
            "allowed_strength": "SUPPORTED_WITH_BOUNDARY",
            "forbidden_stronger_claim": "T1 is universal or causal.",
        },
        {
            "claim_id": "C2_SCALE_LAG_ROBUST_SURVIVORS",
            "claim_text": "Within the survivor class, T1 survival is robust across nearby local scales and lags.",
            "main_figure": "Figure 2",
            "supporting_nodes": "4082;4088;4131;4134",
            "supporting_metrics": f"{m['scale_robust']}/{m['scale_tested']} robust among tested survivor observations",
            "baseline_or_null": "predefined nearby k and lag sensitivity grid",
            "boundary": "This is survivor-class robustness, not an all-19 claim.",
            "allowed_strength": "SUPPORTED_WITH_BOUNDARY",
            "forbidden_stronger_claim": "Scale/lag robustness holds for all observations.",
        },
        {
            "claim_id": "C3_DIFFUSE_TANGENTIAL_DOMINANCE",
            "claim_text": "The most stable repeated form is diffuse tangential activity rather than a universal edge/core or signed trigger.",
            "main_figure": "Figure 3",
            "supporting_nodes": "4084;4085;4086;4131;4132;4134",
            "supporting_metrics": f"diffuse {m['diffuse']}/{m['diffuse_tested']}; near-pre {m['near_pre']}/{m['diffuse_tested']}; signed direction consistency {fmt(m['history_direction_consistency'])}",
            "baseline_or_null": "event-aligned real-minus-null profiles and signed event-type decomposition",
            "boundary": "Edge/core, near-pre, and signed structures are secondary or heterogeneous.",
            "allowed_strength": "SUPPORTED_WITH_BOUNDARY",
            "forbidden_stronger_claim": "A universal edge trigger, sharp precursor, or signed force is identified.",
        },
        {
            "claim_id": "C5_NO_SIMPLE_STATE_MOMENT_CLOSURE",
            "claim_text": "A C,dCdt,R-conditioned first/second moment closure is not stable across observations under grouped validation.",
            "main_figure": "Figure 4A",
            "supporting_nodes": "4090;4094;4132;4134",
            "supporting_metrics": f"median incremental R2 first={fmt(m['first_moment_r2'])}, second={fmt(m['second_moment_r2'])}; positive-ob fractions {fmt(m['first_moment_positive_fraction'])}/{fmt(m['second_moment_positive_fraction'])}",
            "baseline_or_null": "radius-only baseline and shifted C,dCdt null",
            "boundary": "Only this low-dimensional moment-closure form is tested.",
            "allowed_strength": "NOT_SUPPORTED",
            "forbidden_stronger_claim": "Stochastic dynamics or all state dependence are impossible.",
        },
        {
            "claim_id": "C6_NO_EVENT_TIMESTAMP_EXCESS",
            "claim_text": "True transition timestamps do not add robust near-pre T1 activity beyond matched continuous state.",
            "main_figure": "Figure 4B",
            "supporting_nodes": "4100;4105;4132;4134",
            "supporting_metrics": f"median event-minus-matched-control A_pre_z={fmt(m['event_local_median_delta'])}; positive-ob fraction={fmt(m['event_local_positive_fraction'])}",
            "baseline_or_null": "same-observation C,dCdt,R-matched non-event frames and shifted events",
            "boundary": "Only the state-matched near-pre aggregate route is tested.",
            "allowed_strength": "NOT_SUPPORTED",
            "forbidden_stronger_claim": "Transitions have no special dynamics.",
        },
        {
            "claim_id": "C7_OBSERVATION_SPECIFIC_HISTORY_BOUNDARY",
            "claim_text": "Recent path direction can separate T1 in some observations, but it does not form a universal sign/order rule.",
            "main_figure": "Figure 4C",
            "supporting_nodes": "4121;4125;4131;4132;4134",
            "supporting_metrics": f"{m['history_median']}/{m['total_ob']} beat shuffled-history median; {m['history_q95']}/{m['total_ob']} beat q95; median null gap={fmt(m['history_median_effect'])}",
            "baseline_or_null": "same-current-state matching and within-observation shuffled history",
            "boundary": "Direction/order consistency fails across observations.",
            "allowed_strength": "BOUNDARY",
            "forbidden_stronger_claim": "A universal memory, hysteresis, or causal history mechanism is proven.",
        },
        {
            "claim_id": "C8_PROPAGATION_NOT_CONFIRMATORILY_TESTED",
            "claim_text": "Propagation remains outside the current confirmatory route.",
            "main_figure": "Limitations / remaining open mechanism space",
            "supporting_nodes": "4105;4132;4134",
            "supporting_metrics": "route stopped before confirmatory propagation after the event-locality gate failed",
            "baseline_or_null": "not applicable",
            "boundary": "Open route, not a negative result.",
            "allowed_strength": "NOT_TESTED",
            "forbidden_stronger_claim": "No propagation exists.",
        },
    ]
    return pd.DataFrame(rows)


def build_section_to_figure_map() -> pd.DataFrame:
    rows = [
        {
            "section": "Methods / Data orientation",
            "figure": "Figure 1",
            "purpose": "Define the raw data, affine reductions, frozen T1 observable, and event-aligned profile source.",
        },
        {
            "section": "Results 1",
            "figure": "Figure 2",
            "purpose": "Show common but non-universal local non-affine T1 survival across observations.",
        },
        {
            "section": "Results 2",
            "figure": "Figure 3",
            "purpose": "Show diffuse tangential activity as the most stable repeated form and bound edge/core, near-pre, and signed structure.",
        },
        {
            "section": "Results 3",
            "figure": "Figure 4A",
            "purpose": "Report the failure of the tested C,dCdt,R moment-closure reduction.",
        },
        {
            "section": "Results 4",
            "figure": "Figure 4B",
            "purpose": "Report the failure of the tested state-matched event-local near-pre excess route.",
        },
        {
            "section": "Results 5",
            "figure": "Figure 4C",
            "purpose": "Report observation-specific history separation without a universal history rule.",
        },
        {
            "section": "Results 6 / Discussion",
            "figure": "Figure 5",
            "purpose": "Treat observation heterogeneity as a mapped boundary of the result.",
        },
    ]
    return pd.DataFrame(rows)


def build_writing_boundary_checklist() -> pd.DataFrame:
    rows = [
        {
            "check_id": "W1",
            "required_wording": "most observations",
            "avoid_wording": "all observations / universal",
            "reason": "T1 survival has explicit failures and boundary cases.",
        },
        {
            "check_id": "W2",
            "required_wording": "tested reduction did not provide a stable explanation",
            "avoid_wording": "mechanism does not exist",
            "reason": "Negative mechanism results are definition-bound tests.",
        },
        {
            "check_id": "W3",
            "required_wording": "state-matched near-pre aggregate route",
            "avoid_wording": "transitions have no special dynamics",
            "reason": "4100 tested one event-local formulation only.",
        },
        {
            "check_id": "W4",
            "required_wording": "observation-specific history separation",
            "avoid_wording": "universal memory or hysteresis",
            "reason": "Direction/order consistency fails across observations.",
        },
        {
            "check_id": "W5",
            "required_wording": "descriptive metadata association",
            "avoid_wording": "recording condition explains failure",
            "reason": "Metadata verification is incomplete and n=19 is small.",
        },
        {
            "check_id": "W6",
            "required_wording": "propagation remains not confirmatorily tested",
            "avoid_wording": "no propagation exists",
            "reason": "The propagation route was not entered after the 4100 gate.",
        },
        {
            "check_id": "W7",
            "required_wording": "bounded collective observable",
            "avoid_wording": "individual-level causal force",
            "reason": "T1 is a focal-neighborhood aggregate residual.",
        },
    ]
    return pd.DataFrame(rows)


def write_title_candidates(titles: pd.DataFrame) -> None:
    text = dedent(
        f"""\
        # 4135 Title Candidates

        **Recommended title:**  
        **Local non-affine organization in laboratory midge swarms beyond affine geometry and low-dimensional state descriptions**

        This is the safest title because it states the positive object
        (`local non-affine organization`) and the tested reduction boundary
        (`affine geometry and low-dimensional state descriptions`) without
        claiming a universal mechanism.

        ## Candidate Table

        {md_table(titles.to_dict("records"), ["title_id", "title", "style", "strength", "risk"])}
        """
    )
    (OUT / "title_candidates.md").write_text(text.replace("\n        ", "\n").lstrip(), encoding="utf-8")


def write_abstract_skeleton(m: dict[str, object]) -> None:
    text = dedent(
        f"""\
        # 4135 Abstract Skeleton

        ## Unstructured Abstract Draft

        Laboratory midge swarms remain cohesive despite lacking flock-like
        global velocity order. This study asked whether transition-linked
        local motion in such swarms can be absorbed by affine geometry or by a
        small set of low-dimensional state variables. We progressively
        subtracted global and local affine deformation, defined a frozen local
        tangential non-affine residual (`T1`), and tested its robustness across
        19 observations using event-conditioned controls, sensitivity checks,
        grouped out-of-sample moment closure, state-matched event-locality, and
        same-state different-history matching. T1 survived local affine
        subtraction in {m["t1_any"]}/{m["total_ob"]} observations and in both
        original local-scale settings in {m["t1_both"]}/{m["total_ob"]};
        within the survivor class, {m["scale_robust"]}/{m["scale_tested"]}
        observations were robust to nearby scale and lag choices. The most
        stable repeated form was diffuse tangential activity
        ({m["diffuse"]}/{m["diffuse_tested"]}), whereas near-pre timing,
        edge/core contrast, and signed direction were more bounded. A
        `C,dCdt,R`-conditioned first/second moment closure was not stable
        across observations, and true transition timestamps did not show
        robust near-pre excess beyond state-matched non-event frames. Recent
        path direction separated T1 in some observations
        ({m["history_median"]}/{m["total_ob"]} above the shuffled-history
        median), but did not yield a universal sign/order rule. These results
        support a bounded interpretation: midge swarms contain a reproducible
        local non-affine collective observable with explicit observation-level
        heterogeneity and reduction limits, rather than a single universal
        low-dimensional mechanism.

        ## Structured Skeleton

        **Background:** Midge swarms are cohesive but weakly ordered globally.  
        **Objective:** Test whether local transition-linked motion is removed
        by affine geometry or simple state descriptions.  
        **Methods:** Global/local affine subtraction, event-conditioned T1,
        scale/lag robustness, grouped OOS moment closure, state-matched
        event-locality, and same-state different-history matching.  
        **Results:** T1 survived in most observations; diffuse tangential
        activity was the most stable form; `C,dCdt,R`, event-locality, and
        universal-history reductions were not supported as simple mechanisms.  
        **Conclusion:** The strongest result is a bounded local non-affine
        observable with explicit heterogeneity and reduction boundaries.
        """
    )
    (OUT / "abstract_skeleton.md").write_text(text.replace("\n        ", "\n").lstrip(), encoding="utf-8")


def write_results_outline(m: dict[str, object], section_map: pd.DataFrame) -> None:
    text = dedent(
        f"""\
        # 4135 Results Outline

        ## Results 1: A frozen local non-affine T1 observable

        Figure 1 defines the measurement chain. The analysis begins from 3D
        individual trajectories, subtracts affine components, and keeps the
        transition-linked local tangential non-affine residual as the frozen
        `T1` observable. This figure should be read as a data and measurement
        orientation, not as a fitted physical model.

        ## Results 2: T1 survives local affine subtraction in most observations

        Figure 2 shows that T1 survival is common but not universal. T1 survived
        at least one original local-scale setting in {m["t1_any"]}/{m["total_ob"]}
        observations and both original local-scale settings in
        {m["t1_both"]}/{m["total_ob"]} observations. The all-19 display is
        essential because Ob1, Ob3, Ob6, and Ob8 remain failure or boundary
        cases.

        ## Results 3: The most stable form is diffuse tangential activity

        Figure 3 shows that the strongest repeated spatial/activity form is
        diffuse tangential activity ({m["diffuse"]}/{m["diffuse_tested"]}).
        Near-pre timing ({m["near_pre"]}/{m["diffuse_tested"]}), edge/core
        contrast, and signed event-type structure are retained as bounded
        secondary patterns. This supports a spatially diffuse residual rather
        than a universal edge trigger or one-direction signed law.

        ## Results 4: A simple C,dCdt,R moment closure is not supported

        Figure 4A reports the grouped out-of-sample test of a low-dimensional
        first/second moment closure. The median incremental R2 values were
        {fmt(m["first_moment_r2"])} for the first moment and
        {fmt(m["second_moment_r2"])} for the second moment. These values do
        not support a stable `C,dCdt,R` closure under the tested model family.

        ## Results 5: Transition timestamps do not add robust state-matched near-pre excess

        Figure 4B compares true transition timestamps with same-observation
        `C,dCdt,R`-matched non-event frames. The median event-minus-control
        near-pre effect was {fmt(m["event_local_median_delta"])}, with a
        positive-observation fraction of {fmt(m["event_local_positive_fraction"])}.
        This does not support the tested event-local precursor interpretation.

        ## Results 6: Recent history is observation-specific rather than universal

        Figure 4C shows that same-current-state different-history matching
        produced real effects above the shuffled-history median in
        {m["history_median"]}/{m["total_ob"]} observations, but only
        {m["history_q95"]}/{m["total_ob"]} exceeded the q95 null. Direction and
        order were not stable across observations. The result is therefore a
        bounded history-dependence boundary rather than a universal memory rule.

        ## Results 7: Heterogeneity is part of the result

        Figure 5 maps robust survivors, fragile boundaries, stable failures,
        and descriptive metadata associations across all 19 observations. The
        heterogeneity map prevents the positive result from being written as a
        pooled universal effect and prevents failure observations from being
        treated as removable artifacts.

        ## Section-to-Figure Map

        {md_table(section_map.to_dict("records"), ["section", "figure", "purpose"])}
        """
    )
    (OUT / "results_outline.md").write_text(text.replace("\n        ", "\n").lstrip(), encoding="utf-8")


def write_discussion_outline() -> None:
    text = dedent(
        """\
        # 4135 Discussion Outline

        ## D1. What is robust

        The robust product of the 3xxx/4xxx exploration is not a complete
        mechanism. It is a bounded collective observable: a local tangential
        non-affine residual that survives local affine subtraction in most
        observations. The strongest spatial form is diffuse tangential activity.

        ## D2. What is constrained

        Several natural reductions were tested and did not provide stable
        explanations under their definitions. Local affine geometry was
        insufficient in most observations; `C,dCdt,R` did not provide stable
        first/second moment closure; true transition timestamps did not add
        robust state-matched near-pre excess; and recent history did not become
        a universal sign/order rule.

        ## D3. Why the negative results are useful

        The negative results narrow the interpretation without making an
        absence claim. They show that the observed T1 signal cannot simply be
        absorbed into several low-cost explanatory routes. This makes the
        remaining object more precise: it is local, non-affine, tangential,
        transition-linked, reproducible in most observations, and explicitly
        heterogeneous.

        ## D4. Why heterogeneity should remain visible

        Observation heterogeneity is not a nuisance to hide. It is part of the
        empirical boundary of the result. The robust-survivor observations
        define the reproducible positive phenomenon, while fragile and stable
        failure observations define where that phenomenon does not generalize.
        Metadata associations may help organize the observations, but they
        remain descriptive until independently verified.

        ## D5. What remains open

        Higher-dimensional state variables, delayed or path-dependent models,
        network-level organization, propagation under a redesigned target, and
        individual-level causal interactions remain open. These routes should
        be treated as future branches, not as conclusions of the current 413x
        synthesis.

        ## D6. One defensible interpretation

        Taken together, the evidence suggests that laboratory midge swarms
        contain reproducible local organization even when global order and
        affine geometric motion are weak or removed. The most defensible claim
        is therefore not that a universal mechanism has been found, but that a
        bounded non-affine collective observable has been isolated and mapped
        together with its reduction limits.
        """
    )
    (OUT / "discussion_outline.md").write_text(text.replace("\n        ", "\n").lstrip(), encoding="utf-8")


def write_limitations() -> None:
    rows = [
        {
            "limitation_id": "L1",
            "limitation": "The dataset is observational; no intervention was performed.",
            "implication": "The analysis cannot establish individual-level causal forces.",
        },
        {
            "limitation_id": "L2",
            "limitation": "The main cross-observation scope is 19 observations.",
            "implication": "Heterogeneity associations are descriptive and small-n.",
        },
        {
            "limitation_id": "L3",
            "limitation": "T1 is a focal-neighborhood aggregate residual.",
            "implication": "It should not be equated with a single-insect behavioral rule.",
        },
        {
            "limitation_id": "L4",
            "limitation": "`C,dCdt,R` is only one low-dimensional state representation.",
            "implication": "Failure of this closure does not rule out all stochastic or state-dependent models.",
        },
        {
            "limitation_id": "L5",
            "limitation": "The event-locality test used a state-matched near-pre aggregate.",
            "implication": "It does not rule out other transition dynamics.",
        },
        {
            "limitation_id": "L6",
            "limitation": "The confirmatory propagation route was not entered.",
            "implication": "Propagation remains `NOT_TESTED`, not disproven.",
        },
        {
            "limitation_id": "L7",
            "limitation": "History effects are observation-specific.",
            "implication": "They do not support a universal memory or hysteresis mechanism.",
        },
        {
            "limitation_id": "L8",
            "limitation": "Recording-condition metadata are not independently verified for causal use.",
            "implication": "Daytime/dusk and observation-order explanations must remain annotations.",
        },
        {
            "limitation_id": "L9",
            "limitation": "Figures 4134 are evidence-panel previews.",
            "implication": "Final publication graphics still require format-specific redesign.",
        },
        {
            "limitation_id": "L10",
            "limitation": "The 413x route is a synthesis route, not a new mechanism search.",
            "implication": "New attractor, Langevin, propagation, or field/RG routes should be separate future branches.",
        },
    ]
    df = pd.DataFrame(rows)
    write_csv_pair(df, "limitations_table.csv")
    text = dedent(
        f"""\
        # 4135 Limitations

        The current study has several limitations. They do not invalidate the
        bounded positive result, but they define how the result should be read.

        {md_table(rows, ["limitation_id", "limitation", "implication"])}
        """
    )
    (OUT / "limitations.md").write_text(text.replace("\n        ", "\n").lstrip(), encoding="utf-8")


def write_manuscript_story(
    m: dict[str, object],
    titles: pd.DataFrame,
    claim_map: pd.DataFrame,
    section_map: pd.DataFrame,
    figure_manifest: pd.DataFrame,
) -> None:
    text = dedent(
        f"""\
        # 4135 Manuscript-style Technical Synthesis

        ## Working Title

        **{titles.iloc[0]["title"]}**

        ## Central Question

        What components of collective midge motion remain after progressively
        removing global geometry, local affine deformation, low-dimensional
        state dependence, event timing, and simple recent-history
        explanations?

        ## Core Answer

        The strongest current answer is bounded but useful. Laboratory midge
        swarms contain a reproducible local tangential non-affine residual
        (`T1`) in most observations after local affine deformation is removed.
        This residual is not universal, and it does not reduce cleanly to the
        tested `C,dCdt,R` moment closure, state-matched event-local precursor,
        propagation route, or universal recent-history rule.

        ## Narrative

        Laboratory midge swarms are cohesive even though they lack the
        flock-like global velocity order that would make a simple global
        alignment explanation natural. The 3xxx and 4xxx exploratory routes
        therefore asked a sequence of progressively narrower questions. First,
        can global or local affine geometry absorb the apparent transition
        signal? Second, if a local residual remains, is it stable enough to be
        treated as a reproducible observable? Third, can that observable be
        reduced to a small state description, an event-local precursor, or a
        simple history rule?

        The answer after the 413x synthesis is not a single mechanism. Instead,
        the analysis isolates a reproducible phenomenon and defines its
        boundaries. T1 survived local affine subtraction in {m["t1_any"]}/{m["total_ob"]}
        observations and in both original scale settings in
        {m["t1_both"]}/{m["total_ob"]} observations. Among the survivor observations,
        {m["scale_robust"]}/{m["scale_tested"]} were robust to nearby scale and
        lag choices. The strongest repeated form was diffuse tangential
        activity ({m["diffuse"]}/{m["diffuse_tested"]}), while edge/core,
        near-pre, signed, and recent-history patterns were more bounded.

        The subsequent negative and boundary tests are central to the story.
        The `C,dCdt,R` first/second moment closure did not improve stably under
        grouped out-of-sample validation. The state-matched event-locality test
        did not show robust near-pre excess at true transition timestamps.
        Recent history separated T1 in some observations, but its direction and
        order were not stable. Propagation was not confirmatorily tested in the
        current route and should remain in the open mechanism space.

        Observation heterogeneity should therefore be written as part of the
        result. Robust survivors, fragile boundaries, and stable failures are
        all needed to describe the empirical domain of the phenomenon. Metadata
        associations can organize this heterogeneity descriptively, but they
        cannot be promoted to causal explanations.

        ## Results Architecture

        {md_table(section_map.to_dict("records"), ["section", "figure", "purpose"])}

        ## Figure Architecture

        {md_table(figure_manifest.to_dict("records"), ["figure_id", "title", "main_question", "claim_status", "must_not_claim"])}

        ## Evidence-to-Claim Map

        {md_table(claim_map.to_dict("records"), ["claim_id", "main_figure", "supporting_metrics", "allowed_strength", "boundary", "forbidden_stronger_claim"])}

        ## Strongest Bounded Claim

        Laboratory midge swarms exhibit a reproducible local non-affine
        tangential motion signature that survives local affine geometric
        subtraction in most observations, yet resists several natural
        low-dimensional reductions and displays explicit observation-level
        heterogeneity.

        ## Terminal 413x Decision

        `4135` closes the 413x synthesis route. The next action should be paper
        development or deliberate opening of a new branch, not an automatic
        continuation of mechanism search inside 413x.
        """
    )
    (OUT / "manuscript_story.md").write_text(text.replace("\n        ", "\n").lstrip(), encoding="utf-8")


def write_source_map(output_names: list[str]) -> pd.DataFrame:
    inputs = [
        "Experiment/run_4135_manuscript_style_technical_synthesis.py",
        "Output/4130/decision.json",
        "Output/4130/claim_strength_registry.csv",
        "Output/4131/decision.json",
        "Output/4132/decision.json",
        "Output/4133/decision.json",
        "Output/4134/decision.json",
        "Output/4134/main_figure_manifest.csv",
        "Output/4134/panel_metadata.csv",
        "Output/4134/figure_caption_drafts.csv",
        "Output/4090/primary_metrics.csv",
        "Output/4100/observation_level_effects.csv",
        "Output/4121/observation_level_effects.csv",
    ]
    rows: list[dict[str, object]] = []
    for path in inputs:
        p = ROOT / path
        rows.append(
            {
                "role": "input",
                "path": path,
                "exists": p.exists(),
                "size_bytes": p.stat().st_size if p.exists() else 0,
            }
        )
    for name in output_names:
        p = OUT / name
        rows.append(
            {
                "role": "output",
                "path": rel(p),
                "exists": p.exists(),
                "size_bytes": p.stat().st_size if p.exists() else 0,
            }
        )
    df = pd.DataFrame(rows)
    write_csv_pair(df, "source_map.csv")
    return df


def write_summary(decision: dict[str, object], claim_map: pd.DataFrame, source_map: pd.DataFrame) -> None:
    text = dedent(
        f"""\
        # Node 4135 Manuscript-style Technical Synthesis

        ## Gate Result

        ```text
        gate_result = {decision["gate_result"]}
        ```

        ## Main Product

        `4135` converts the 4134 figure architecture into manuscript-style
        technical writing modules. It closes the 413x synthesis route and does
        not open a new mechanism branch.

        ## Counts

        ```text
        title_candidates = {decision["counts"]["title_candidates"]}
        main_claim_rows = {decision["counts"]["main_claim_rows"]}
        evidence_to_claim_rows = {decision["counts"]["evidence_to_claim_rows"]}
        section_to_figure_rows = {decision["counts"]["section_to_figure_rows"]}
        writing_boundary_rows = {decision["counts"]["writing_boundary_rows"]}
        ```

        ## Evidence-to-Claim Map

        {md_table(claim_map.to_dict("records"), ["claim_id", "main_figure", "allowed_strength", "supporting_metrics", "forbidden_stronger_claim"])}

        ## Source Audit

        {md_table(source_map.to_dict("records"), ["role", "path", "exists", "size_bytes"])}

        ## Next

        The 413x synthesis route is complete. The next step should be either:

        - paper/report development using the `Output/4135` manuscript modules;
        - final visual redesign of the `Output/4134` figure previews;
        - or a deliberately named new branch outside 413x.
        """
    )
    (OUT / "4135_summary.md").write_text(text.replace("\n        ", "\n").lstrip(), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    inputs = load_inputs()
    metrics = summary_metrics(inputs)

    titles = build_title_candidates()
    main_claim_registry = build_main_claim_registry(inputs["m5_claim_review"])  # type: ignore[arg-type]
    claim_map = build_evidence_to_claim_map(metrics)
    section_map = build_section_to_figure_map()
    writing_checklist = build_writing_boundary_checklist()

    write_csv_pair(titles, "title_candidates.csv")
    write_csv_pair(main_claim_registry, "main_claim_registry.csv")
    write_csv_pair(claim_map, "evidence_to_claim_map.csv")
    write_csv_pair(section_map, "section_to_figure_map.csv")
    write_csv_pair(writing_checklist, "writing_boundary_checklist.csv")

    write_title_candidates(titles)
    write_abstract_skeleton(metrics)
    write_results_outline(metrics, section_map)
    write_discussion_outline()
    write_limitations()
    write_manuscript_story(metrics, titles, claim_map, section_map, inputs["figure_manifest"])  # type: ignore[arg-type]

    output_names = [
        "title_candidates.csv",
        "main_claim_registry.csv",
        "evidence_to_claim_map.csv",
        "section_to_figure_map.csv",
        "writing_boundary_checklist.csv",
        "limitations_table.csv",
        "title_candidates.md",
        "abstract_skeleton.md",
        "results_outline.md",
        "discussion_outline.md",
        "limitations.md",
        "manuscript_story.md",
    ]
    source_map = write_source_map(output_names)

    missing_sources = int(
        (
            (source_map["role"].eq("input"))
            & ((~source_map["exists"].astype(bool)) | (pd.to_numeric(source_map["size_bytes"], errors="coerce").fillna(0) <= 0))
        ).sum()
    )
    output_files_ok = bool(
        source_map[source_map["role"].eq("output")]["exists"].astype(bool).all()
        and (pd.to_numeric(source_map[source_map["role"].eq("output")]["size_bytes"], errors="coerce").fillna(0) > 0).all()
    )
    decision = {
        "node": NODE,
        "date": DATE,
        "node_type": "terminal_synthesis",
        "upstream_node": "4134_figure_ready_evidence_panels",
        "data_scope": "all_19_observations_as_synthesized_in_4130_4134",
        "new_experiment_run": False,
        "new_target_or_mechanism_introduced": False,
        "counts": {
            "title_candidates": len(titles),
            "main_claim_rows": len(main_claim_registry),
            "evidence_to_claim_rows": len(claim_map),
            "section_to_figure_rows": len(section_map),
            "writing_boundary_rows": len(writing_checklist),
            "missing_input_sources": missing_sources,
        },
        "quality_checks": {
            "upstream_4134_passed": str(inputs["d4134"].get("gate_result", "")).startswith("pass_"),  # type: ignore[union-attr]
            "source_inputs_present": missing_sources == 0,
            "manuscript_story_written": (OUT / "manuscript_story.md").exists(),
            "abstract_skeleton_written": (OUT / "abstract_skeleton.md").exists(),
            "results_outline_written": (OUT / "results_outline.md").exists(),
            "discussion_outline_written": (OUT / "discussion_outline.md").exists(),
            "limitations_written": (OUT / "limitations.md").exists(),
            "evidence_to_claim_map_written": (OUT / "evidence_to_claim_map.csv").exists(),
            "output_files_nonempty": output_files_ok,
            "propagation_kept_not_tested": True,
            "metadata_kept_descriptive": True,
            "history_kept_observation_specific": True,
            "terminal_413x_no_auto_mechanism_search": True,
        },
        "gate_result": "pass_4135_manuscript_synthesis_complete_terminal_413x"
        if missing_sources == 0 and output_files_ok
        else "boundary_4135_synthesis_needs_source_or_output_repair",
        "interpretation": (
            "The 413x route now has a paper/report-ready technical story: a bounded local non-affine T1 observable, "
            "positive evidence with explicit observation boundaries, and tested reduction failures without overclaiming."
        ),
        "does_not_prove": [
            "new mechanism",
            "universal T1 law",
            "causal metadata explanation",
            "propagation absence",
            "universal history mechanism",
            "camera-ready paper",
        ],
        "next": [
            "paper_or_report_development_from_4134_4135",
            "optional_final_figure_redesign",
            "optional_new_branch_outside_413x_if_user_explicitly_chooses",
        ],
        "artifacts": [
            "Output/4135/title_candidates.csv",
            "Output/4135/main_claim_registry.csv",
            "Output/4135/evidence_to_claim_map.csv",
            "Output/4135/section_to_figure_map.csv",
            "Output/4135/writing_boundary_checklist.csv",
            "Output/4135/limitations_table.csv",
            "Output/4135/title_candidates.md",
            "Output/4135/abstract_skeleton.md",
            "Output/4135/results_outline.md",
            "Output/4135/discussion_outline.md",
            "Output/4135/limitations.md",
            "Output/4135/manuscript_story.md",
            "Output/4135/source_map.csv",
            "Output/4135/decision.json",
            "Output/4135/4135_summary.md",
        ],
    }
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2), encoding="utf-8")
    source_map = write_source_map(output_names + ["source_map.csv", "decision.json"])
    write_summary(decision, claim_map, source_map)

    print(json.dumps(decision, indent=2))
    print(f"Wrote 4135 outputs to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
