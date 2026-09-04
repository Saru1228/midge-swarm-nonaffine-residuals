"""4081d explain observation heterogeneity before 4082.

This node reads the completed 4081c full-observation adjudication and asks what
simple observation-level pattern explains the pass/fail split. It is a
lightweight synthesis step: no trajectory-level local-affine metrics are
recomputed here.
"""

from __future__ import annotations

import csv
import itertools
import json
import math
from pathlib import Path
from textwrap import dedent

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "Output" / "4081c"
OUT = ROOT / "Output" / "4081d"
EVENTS = ROOT / "Output" / "3045" / "tables" / "transition_events.csv"
NODE = "4081d_explain_observation_heterogeneity_before_4082"
DATE = "2026-08-25"


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in columns})


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def bool_from_csv(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def exact_binomial_two_sided(k: int, n: int, p: float = 0.5) -> float:
    probs = [math.comb(n, i) * (p**i) * ((1.0 - p) ** (n - i)) for i in range(n + 1)]
    observed = probs[k]
    return float(sum(prob for prob in probs if prob <= observed + 1e-15))


def exact_group_permutation_p(values: np.ndarray, group: np.ndarray) -> float:
    """Two-sided exact p for median difference under fixed group sizes."""
    values = np.asarray(values, dtype="float64")
    group = np.asarray(group, dtype=bool)
    ok = np.isfinite(values)
    values = values[ok]
    group = group[ok]
    n = len(values)
    n_true = int(group.sum())
    if n_true == 0 or n_true == n:
        return math.nan
    observed = float(np.median(values[group]) - np.median(values[~group]))
    count = 0
    extreme = 0
    idx = range(n)
    for combo in itertools.combinations(idx, n_true):
        mask = np.zeros(n, dtype=bool)
        mask[list(combo)] = True
        diff = float(np.median(values[mask]) - np.median(values[~mask]))
        count += 1
        if abs(diff) >= abs(observed) - 1e-12:
            extreme += 1
    return float(extreme / count) if count else math.nan


def quantiles(values: pd.Series) -> tuple[float, float, float]:
    arr = pd.to_numeric(values, errors="coerce").to_numpy(dtype="float64")
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return math.nan, math.nan, math.nan
    return tuple(float(x) for x in np.quantile(arr, [0.25, 0.50, 0.75]))


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


def build_features(classes: pd.DataFrame, rows: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    cls = classes.copy()
    cls["ob"] = pd.to_numeric(cls["ob"], errors="coerce").astype("int64")
    cls["n_events"] = pd.to_numeric(cls["n_events"], errors="coerce")
    cls["t1_gate_any_bool"] = cls["t1_gate_any"].map(bool_from_csv)
    cls["t2_gate_any_bool"] = cls["t2_gate_any"].map(bool_from_csv)
    cls["t2_gate_count"] = pd.to_numeric(cls["t2_gate_count"], errors="coerce")
    cls["t1_median_local_to_b3_ratio"] = pd.to_numeric(cls["t1_median_local_to_b3_ratio"], errors="coerce")
    cls["t1_median_local_event_minus_non_event_z"] = pd.to_numeric(
        cls["t1_median_local_event_minus_non_event_z"], errors="coerce"
    )

    t1 = rows[rows["target_id"] == "T1_transition_tangential_residual"].copy()
    for col in [
        "ob",
        "k",
        "b3_event_direction_abs_z",
        "b3_event_minus_non_event_direction_z",
        "local_event_direction_abs_z",
        "local_non_event_direction_abs_median_z",
        "local_event_minus_non_event_direction_z",
        "p_non_event_direction_ge_event",
        "local_to_b3_direction_ratio",
    ]:
        t1[col] = pd.to_numeric(t1[col], errors="coerce")
    t1["event_conditioned_local_gate_bool"] = t1["event_conditioned_local_gate"].map(bool_from_csv)
    wide = t1.pivot_table(
        index="ob",
        columns="k",
        values=[
            "b3_event_direction_abs_z",
            "b3_event_minus_non_event_direction_z",
            "local_event_direction_abs_z",
            "local_non_event_direction_abs_median_z",
            "local_event_minus_non_event_direction_z",
            "p_non_event_direction_ge_event",
            "local_to_b3_direction_ratio",
            "event_conditioned_local_gate_bool",
        ],
        aggfunc="first",
    )
    wide.columns = [f"t1_k{int(k)}_{name}" for name, k in wide.columns]
    wide = wide.reset_index()

    event_summary = (
        events.assign(
            ob=pd.to_numeric(events["ob"], errors="coerce"),
            event_t=pd.to_numeric(events["event_t"], errors="coerce"),
            prev_duration_sec=pd.to_numeric(events["prev_duration_sec"], errors="coerce"),
            next_duration_sec=pd.to_numeric(events["next_duration_sec"], errors="coerce"),
        )
        .groupby("ob", sort=True)
        .agg(
            dataset=("dataset", "first"),
            first_event_t=("event_t", "min"),
            last_event_t=("event_t", "max"),
            median_prev_duration_sec=("prev_duration_sec", "median"),
            median_next_duration_sec=("next_duration_sec", "median"),
            low_to_high_events=("event_type", lambda s: int((s == "low_to_high").sum())),
            high_to_low_events=("event_type", lambda s: int((s == "high_to_low").sum())),
        )
        .reset_index()
    )
    event_summary["event_span_sec"] = event_summary["last_event_t"] - event_summary["first_event_t"]
    event_summary["event_rate_per_sec"] = cls.set_index("ob")["n_events"].reindex(event_summary["ob"]).to_numpy() / event_summary[
        "event_span_sec"
    ].replace(0, np.nan)

    features = cls.merge(wide, on="ob", how="left").merge(event_summary, on="ob", how="left")
    features["ob_group"] = np.where(features["t1_gate_any_bool"], "survive", "not_event_conditioned")
    return features.sort_values("ob").reset_index(drop=True)


def feature_contrasts(features: pd.DataFrame) -> list[dict[str, object]]:
    candidates = [
        ("ob", "observation index"),
        ("n_events", "transition event count"),
        ("event_rate_per_sec", "transition event rate"),
        ("median_prev_duration_sec", "median previous-state duration"),
        ("median_next_duration_sec", "median next-state duration"),
        ("t2_gate_count", "secondary T2 gate count"),
        ("t1_median_local_to_b3_ratio", "T1 local/B3 ratio median"),
        ("t1_median_local_event_minus_non_event_z", "T1 local event-control gap median"),
        ("t1_k8_b3_event_direction_abs_z", "T1 B3 event abs, k8 row"),
        ("t1_k8_local_event_direction_abs_z", "T1 local event abs, k8"),
        ("t1_k8_local_non_event_direction_abs_median_z", "T1 local non-event abs, k8"),
        ("t1_k10_local_event_direction_abs_z", "T1 local event abs, k10"),
        ("t1_k10_local_non_event_direction_abs_median_z", "T1 local non-event abs, k10"),
    ]
    group = features["t1_gate_any_bool"].to_numpy(dtype=bool)
    rows: list[dict[str, object]] = []
    for col, label in candidates:
        if col not in features.columns:
            continue
        values = pd.to_numeric(features[col], errors="coerce")
        fail_q = quantiles(values[~features["t1_gate_any_bool"]])
        pass_q = quantiles(values[features["t1_gate_any_bool"]])
        p_perm = exact_group_permutation_p(values.to_numpy(dtype="float64"), group)
        rows.append(
            {
                "feature": col,
                "plain_label": label,
                "not_event_q25": fail_q[0],
                "not_event_median": fail_q[1],
                "not_event_q75": fail_q[2],
                "survive_q25": pass_q[0],
                "survive_median": pass_q[1],
                "survive_q75": pass_q[2],
                "median_difference_survive_minus_not_event": pass_q[1] - fail_q[1]
                if np.isfinite(pass_q[1]) and np.isfinite(fail_q[1])
                else math.nan,
                "exact_permutation_p_two_sided": p_perm,
                "note": "exploratory; small n; gate-derived feature" if col.startswith("t1_") else "exploratory; small n",
            }
        )
    return rows


def make_figures(features: pd.DataFrame, contrasts: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt

    fig_dir = OUT / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    colors = np.where(features["t1_gate_any_bool"], "#1f9d55", "#b23a48")
    labels = np.where(features["t1_gate_any_bool"], "survive", "not event-conditioned")

    fig, axes = plt.subplots(3, 1, figsize=(11, 10), sharex=True, constrained_layout=True)
    axes[0].bar(features["ob"], features["t1_median_local_event_minus_non_event_z"], color=colors)
    axes[0].axhline(0, color="#444444", linewidth=1)
    axes[0].set_ylabel("T1 local event-control gap")
    axes[0].set_title("4081d observation-level route map")
    ratio = pd.to_numeric(features["t1_median_local_to_b3_ratio"], errors="coerce").to_numpy(dtype="float64")
    log_ratio = np.log10(np.clip(ratio, 1e-6, None))
    axes[1].bar(features["ob"], log_ratio, color=colors)
    axes[1].axhline(np.log10(0.30), color="#666666", linewidth=1, linestyle="--")
    axes[1].axhline(0, color="#aaaaaa", linewidth=0.8)
    axes[1].set_ylabel("log10 T1 local / B3")
    axes[2].bar(features["ob"], features["t2_gate_count"], color=colors)
    axes[2].set_ylabel("T2 gate count")
    axes[2].set_xlabel("Observation")
    for ax in axes:
        ax.grid(axis="y", color="#dddddd", linewidth=0.8)
        ax.set_xticks(features["ob"])
    handles = [
        plt.Line2D([0], [0], marker="s", linestyle="", color="#1f9d55", label="T1 survives"),
        plt.Line2D([0], [0], marker="s", linestyle="", color="#b23a48", label="T1 not event-conditioned"),
    ]
    axes[0].legend(handles=handles, loc="upper left", frameon=False)
    fig.savefig(fig_dir / "4081d_observation_route_map.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.5, 6.0), constrained_layout=True)
    ax.scatter(
        log_ratio,
        features["t1_median_local_event_minus_non_event_z"],
        c=colors,
        s=80,
        edgecolor="#222222",
        linewidth=0.6,
    )
    ax.axhline(0, color="#444444", linewidth=1)
    ax.axvline(np.log10(0.30), color="#666666", linewidth=1, linestyle="--")
    for row, label in zip(features.itertuples(index=False), labels):
        x = math.log10(max(float(row.t1_median_local_to_b3_ratio), 1e-6))
        ax.text(
            x,
            row.t1_median_local_event_minus_non_event_z,
            f" Ob{int(row.ob)}",
            fontsize=8,
            va="center",
        )
    ax.set_xlabel("log10 T1 local / B3 ratio")
    ax.set_ylabel("T1 local event-control gap")
    ax.set_title("Local residual strength is distinct from event specificity")
    ax.grid(color="#dddddd", linewidth=0.8)
    ax.legend(handles=handles, loc="lower right", frameon=False)
    fig.savefig(fig_dir / "4081d_t1_ratio_vs_event_specificity.png", dpi=180)
    plt.close(fig)

    top = contrasts.sort_values("exact_permutation_p_two_sided").head(8).copy()
    fig, ax = plt.subplots(figsize=(9, 5.5), constrained_layout=True)
    y = np.arange(len(top))
    width = 0.36
    ax.barh(y - width / 2, top["not_event_median"], height=width, color="#b23a48", label="not event-conditioned")
    ax.barh(y + width / 2, top["survive_median"], height=width, color="#1f9d55", label="survive")
    ax.set_yticks(y)
    ax.set_yticklabels(top["plain_label"])
    ax.invert_yaxis()
    ax.set_xlabel("Median")
    ax.set_title("Feature contrasts for the observation split")
    ax.grid(axis="x", color="#dddddd", linewidth=0.8)
    ax.legend(frameon=False)
    fig.savefig(fig_dir / "4081d_feature_contrasts.png", dpi=180)
    plt.close(fig)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    classes = pd.read_csv(SRC / "ob_route_a_classification.csv")
    rows = pd.read_csv(SRC / "full_geometry_ladder_rows.csv")
    events = pd.read_csv(EVENTS)

    features = build_features(classes, rows, events)
    contrasts = pd.DataFrame(feature_contrasts(features))
    n_total = int(len(features))
    n_survive = int(features["t1_gate_any_bool"].sum())
    n_fail = n_total - n_survive
    both_k = int((features["ob_route_a_class"] == "t1_local_nonaffine_survives_both_k").sum())
    one_k = int((features["ob_route_a_class"] == "t1_local_nonaffine_survives_one_k").sum())
    fail_obs = [int(x) for x in features.loc[~features["t1_gate_any_bool"], "ob"].tolist()]
    pass_obs = [int(x) for x in features.loc[features["t1_gate_any_bool"], "ob"].tolist()]
    p_binom = exact_binomial_two_sided(n_survive, n_total, 0.5)
    p_fail_first8 = math.comb(8, n_fail) / math.comb(n_total, n_fail) if n_fail <= 8 else math.nan

    feature_columns = [
        "ob",
        "dataset",
        "ob_group",
        "n_events",
        "event_rate_per_sec",
        "median_prev_duration_sec",
        "median_next_duration_sec",
        "t1_gate_k_values",
        "t1_median_local_to_b3_ratio",
        "t1_median_local_event_minus_non_event_z",
        "t1_k8_local_event_direction_abs_z",
        "t1_k8_local_non_event_direction_abs_median_z",
        "t1_k10_local_event_direction_abs_z",
        "t1_k10_local_non_event_direction_abs_median_z",
        "t2_gate_count",
        "ob_route_a_class",
    ]
    write_csv(OUT / "heterogeneity_features.csv", features.to_dict("records"), feature_columns)
    write_csv(OUT / "tables" / "heterogeneity_features.csv", features.to_dict("records"), feature_columns)

    contrast_columns = [
        "feature",
        "plain_label",
        "not_event_q25",
        "not_event_median",
        "not_event_q75",
        "survive_q25",
        "survive_median",
        "survive_q75",
        "median_difference_survive_minus_not_event",
        "exact_permutation_p_two_sided",
        "note",
    ]
    contrast_rows = contrasts.to_dict("records")
    write_csv(OUT / "feature_contrasts.csv", contrast_rows, contrast_columns)
    write_csv(OUT / "tables" / "feature_contrasts.csv", contrast_rows, contrast_columns)

    make_figures(features, contrasts)

    decision = {
        "node": NODE,
        "date": DATE,
        "result": "support_common_t1_survival_with_early_observation_boundary",
        "n_observations": n_total,
        "t1_survive_any_k": n_survive,
        "t1_survive_both_k": both_k,
        "t1_survive_one_k": one_k,
        "t1_not_event_conditioned": n_fail,
        "survive_observations": pass_obs,
        "not_event_conditioned_observations": fail_obs,
        "rough_binomial_two_sided_p_vs_half_survival": p_binom,
        "failure_concentration_p_if_failure_positions_random": p_fail_first8,
        "interpretation": (
            "The full set supports common T1 local-nonaffine survival, but the failures are "
            "concentrated in early observations and are better described as loss of event "
            "specificity after local-affine residualization, not as simple local-affine absorption."
        ),
        "boundary": (
            "Do not make a pooled universal claim before checking why Ob1/3/6/8 fail and why "
            "Ob9-Ob19 all pass under the same frozen gate."
        ),
        "next": [
            "4082_scale_robustness_on_surviving_observation_class",
            "4082b_early_failure_condition_or_artifact_audit",
        ],
        "artifacts": [
            "Output/4081d/heterogeneity_features.csv",
            "Output/4081d/feature_contrasts.csv",
            "Output/4081d/figures/4081d_observation_route_map.png",
            "Output/4081d/figures/4081d_t1_ratio_vs_event_specificity.png",
            "Output/4081d/figures/4081d_feature_contrasts.png",
        ],
    }
    write_json(OUT / "decision.json", decision)

    key_contrasts = contrasts.sort_values("exact_permutation_p_two_sided").head(8).to_dict("records")
    summary = dedent(
        f"""\
        # Node 4081d Summary

        ## Question

        4081c found that Ob1 and Ob2 were not simply contradictory cases. Across
        all 19 observations, what observation-level pattern explains the split?

        ## Inputs

        - `Output/4081c/ob_route_a_classification.csv`
        - `Output/4081c/full_geometry_ladder_rows.csv`
        - `Output/3045/tables/transition_events.csv`

        ## Main Result

        `support_common_t1_survival_with_early_observation_boundary`

        In plain language: most observations retain a transition-linked local
        tangential residual after subtracting local affine motion. The exceptions
        are not random-looking across observation index: Ob1, Ob3, Ob6, and Ob8
        fail, while Ob9-Ob19 all pass.

        ## Counts

        ```text
        total observations = {n_total}
        T1 survives at least one k = {n_survive}
        T1 survives both k = {both_k}
        T1 survives one k = {one_k}
        T1 not event-conditioned after local affine = {n_fail}
        ```

        A rough sign-test-style comparison against a half-survival null gives
        `p = {p_binom:.4g}`. This should be treated as descriptive, because the
        19 observations may not be fully independent.

        The four non-survival observations all lie in Ob1-Ob8. If four failure
        positions were randomly placed among 19 observations, the probability
        that all four land in the first eight is `{p_fail_first8:.4g}`. This is
        a useful routing clue, not a final causal explanation.

        ## Observation Features

        {md_table(features[feature_columns].round(4).to_dict("records"), feature_columns)}

        ## Strongest Feature Contrasts

        {md_table(key_contrasts, contrast_columns)}

        ## Interpretation

        4081c/4081d changes the story from "Ob1 and Ob2 disagree" to a clearer
        statistical map:

        - The common pattern is positive: 15/19 observations retain the T1 local
          non-affine event-conditioned signal.
        - The negative cases are not "local affine explains everything." They
          are better read as "after local affine correction, the remaining local
          tangential residual is not specifically higher at transition events
          than at matched non-events."
        - The non-survival cases concentrate in early observations. This makes
          a batch/condition/artifact audit necessary before a stronger biological
          claim.

        ## Next

        - `4082_scale_robustness_on_surviving_observation_class`: check whether
          the 15/19 survival result is robust to scale (`k`), lag, and matching
          choices.
        - `4082b_early_failure_condition_or_artifact_audit`: compare Ob1/3/6/8
          against the surviving observations using event density, state-duration
          structure, trajectory quality, and recording/batch metadata if
          available.

        ## Artifacts

        - `Output/4081d/heterogeneity_features.csv`
        - `Output/4081d/feature_contrasts.csv`
        - `Output/4081d/figures/4081d_observation_route_map.png`
        - `Output/4081d/figures/4081d_t1_ratio_vs_event_specificity.png`
        - `Output/4081d/figures/4081d_feature_contrasts.png`
        """
    ).lstrip()
    summary = "\n".join(line[8:] if line.startswith("        ") else line for line in summary.splitlines()) + "\n"
    (OUT / "4081d_summary.md").write_text(summary, encoding="utf-8")
    print(f"Wrote 4081d outputs to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
