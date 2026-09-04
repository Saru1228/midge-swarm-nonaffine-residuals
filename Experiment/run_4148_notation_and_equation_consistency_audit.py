#!/usr/bin/env python3
"""4148 notation and equation consistency audit.

This node checks only the active mypaper2 LaTeX path. Inactive legacy files are
reported separately only when useful, but they do not fail the manuscript gate.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4148"
TABLES = OUT / "tables"
DATE = "2026-09-02"
NODE = "4148_notation_and_equation_consistency_audit"
LATEX = ROOT / "mypaper2" / "Latex"
MAIN = LATEX / "main.tex"


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def ensure_dirs() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_csv(df: pd.DataFrame, filename: str) -> None:
    df.to_csv(OUT / filename, index=False)
    df.to_csv(TABLES / filename, index=False)


def write_json(obj: dict[str, Any], filename: str) -> None:
    (OUT / filename).write_text(json.dumps(obj, indent=2), encoding="utf-8")


def fmt(value: Any, digits: int = 4) -> str:
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
        vals = []
        for col in columns:
            val = row.get(col, "")
            if isinstance(val, float):
                vals.append(fmt(val))
            else:
                vals.append(str(val).replace("\n", " ").replace("|", "\\|"))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def resolve_input(path: Path, include: str) -> Path:
    candidate = (path.parent / include).with_suffix(".tex")
    if candidate.exists():
        return candidate.resolve()
    candidate = (LATEX / include).with_suffix(".tex")
    return candidate.resolve()


def active_tex_files() -> list[Path]:
    seen: set[Path] = set()
    ordered: list[Path] = []

    def visit(path: Path) -> None:
        path = path.resolve()
        if path in seen or not path.exists():
            return
        seen.add(path)
        ordered.append(path)
        text = read_text(path)
        for match in re.finditer(r"\\input\{([^}]+)\}", text):
            visit(resolve_input(path, match.group(1)))

    visit(MAIN)
    return ordered


def line_hits(path: Path, pattern: str) -> list[int]:
    rx = re.compile(pattern)
    hits = []
    for i, line in enumerate(read_text(path).splitlines(), start=1):
        if rx.search(line):
            hits.append(i)
    return hits


def build_registry(active: list[Path]) -> pd.DataFrame:
    rows = [
        {
            "symbol_or_term": "T1",
            "canonical_use": (
                "Plain-text name for the local tangential non-affine residual "
                "activity family; not written as T_1 and not treated as force."
            ),
            "required_in_active_text": "T1 is not a raw individual velocity",
            "allowed_variants": "local tangential non-affine activity; T1 observable",
            "disallowed_variants": "raw speed; inferred force; T_1",
            "primary_source": "Output/4130/definition_dictionary.csv",
        },
        {
            "symbol_or_term": "C(t)",
            "canonical_use": (
                "Compact-density coordinate: robust-z standardized "
                "rho_rms(t) within each observation."
            ),
            "required_in_active_text": "compact-density coordinate $C(t)$",
            "allowed_variants": "C; density_rms_z3045 in code",
            "disallowed_variants": "raw density without standardization",
            "primary_source": "mypaper2/Latex/Part2/02_data_t1_observable_v2.tex",
        },
        {
            "symbol_or_term": "\\dot{C}(t)",
            "canonical_use": "Time gradient of the one-second smoothed C(t).",
            "required_in_active_text": "\\dot{C}(t)",
            "allowed_variants": "dCdt in code",
            "disallowed_variants": "unsmoothed finite difference without note",
            "primary_source": "Output/4130/definition_dictionary.csv",
        },
        {
            "symbol_or_term": "R(t)",
            "canonical_use": (
                "Swarm-size coordinate: robust-z standardized R_rms(t); "
                "vector-level moment tests use focal radius as an explicit exception."
            ),
            "required_in_active_text": "radius variable depended on the unit of analysis",
            "allowed_variants": "R; r_rms_z3045 in code",
            "disallowed_variants": "focal radius without noting unit change",
            "primary_source": "Output/4130/definition_dictionary.csv",
        },
        {
            "symbol_or_term": "R^2_inc",
            "canonical_use": (
                "Incremental predictive score, distinct from the swarm-size "
                "coordinate R(t)."
            ),
            "required_in_active_text": "R^2_{\\mathrm{inc}}",
            "allowed_variants": "incremental R^2",
            "disallowed_variants": "R as radius score without context",
            "primary_source": "mypaper2/Latex/Part3/03_methods_reduction_boundary_tests_v2.tex",
        },
        {
            "symbol_or_term": "spectral_set",
            "canonical_use": (
                "Inherited transfer-operator compact-density coarse graining "
                "from 3032/3032b, not fitted from T1."
            ),
            "required_in_active_text": "transfer-operator compact-density coarse-graining",
            "allowed_variants": "compact-density low/high labels",
            "disallowed_variants": "T1-optimized labels",
            "primary_source": "Output/4147/spectral_set_provenance.md",
        },
        {
            "symbol_or_term": "near-pre phase bin",
            "canonical_use": (
                "4085 phase bin: [-0.25,0.00) s; event frame belongs to "
                "near-post for phase profiles."
            ),
            "required_in_active_text": "near-pre $[-0.25,0.00)$",
            "allowed_variants": "near-pre timing",
            "disallowed_variants": "same as endpoint-inclusive 4100 window without note",
            "primary_source": "Experiment/run_4085_event_phase_profile_of_t1_signal.py",
        },
        {
            "symbol_or_term": "near-pre state-matched aggregate",
            "canonical_use": (
                "4100 endpoint-inclusive aggregate: [-0.25,0.00] s; distinct "
                "from half-open phase-bin convention."
            ),
            "required_in_active_text": "endpoint-inclusive",
            "allowed_variants": "event-local near-pre activity",
            "disallowed_variants": "undifferentiated near-pre definition",
            "primary_source": "Experiment/run_4100_state_matched_event_locality_challenge.py",
        },
        {
            "symbol_or_term": "B3",
            "canonical_use": (
                "Upstream global-affine residual baseline used only in the "
                "local-to-B3 retention ratio."
            ),
            "required_in_active_text": "B3 denotes the upstream global-affine residual baseline",
            "allowed_variants": "local/global-affine retention ratio",
            "disallowed_variants": "undefined B3 shorthand",
            "primary_source": "Output/4073/null_and_baseline_registry.csv",
        },
    ]

    active_paths = {rel(p) for p in active}
    for row in rows:
        row["primary_source_active"] = row["primary_source"] in active_paths
    return pd.DataFrame(rows)


def build_occurrences(active: list[Path]) -> pd.DataFrame:
    patterns = {
        "T1": r"\bT1\b",
        "T_1": r"T_1",
        "C(t)": r"C\(t\)",
        "dotC": r"\\dot\{C\}",
        "R(t)": r"R\(t\)",
        "R_rms": r"R_\{\\mathrm\{rms\}\}",
        "R2": r"R\^2",
        "spectral_set": r"spectral\\_set|spectral_set",
        "near_pre_half_open": r"\[-0\.25,0\.00\)",
        "near_pre_closed": r"\[-0\.25,0\.00\]",
        "endpoint_inclusive": r"endpoint-inclusive",
        "B3": r"\bB3\b|local\\_to\\_b3|local_to_b3",
    }
    rows: list[dict[str, Any]] = []
    for path in active:
        text = read_text(path)
        for name, pattern in patterns.items():
            hits = line_hits(path, pattern)
            if hits:
                rows.append(
                    {
                        "pattern_id": name,
                        "file": rel(path),
                        "n_hits": int(len(hits)),
                        "lines": ",".join(str(x) for x in hits[:20]),
                    }
                )
    return pd.DataFrame(rows)


def active_text(active: list[Path]) -> str:
    return "\n".join(read_text(p) for p in active)


def has(text: str, pattern: str) -> bool:
    return bool(re.search(pattern, text, flags=re.MULTILINE | re.DOTALL))


def build_checks(active: list[Path]) -> pd.DataFrame:
    text = active_text(active)
    active_names = [rel(p) for p in active]
    checks = [
        {
            "check_id": "active_path_uses_v2_core_files",
            "severity": "stop",
            "pass": (
                "mypaper2/Latex/Part2/02_data_t1_observable_v2.tex" in active_names
                and "mypaper2/Latex/Part3/03_methods_affine_reduction_and_controls_v2.tex"
                in active_names
                and "mypaper2/Latex/Part3/03_methods_reduction_boundary_tests_v2.tex"
                in active_names
            ),
            "finding": "Active path should use the corrected v2 data/method files.",
            "fix": "Update main include files if false.",
        },
        {
            "check_id": "t1_plain_term_not_subscripted",
            "severity": "fix_required",
            "pass": not has(text, r"T_1|\$T1\$"),
            "finding": "T1 is used as a named residual family, not a T_1 equation symbol.",
            "fix": "Replace T_1/$T1$ variants with plain T1 unless a new symbol is defined.",
        },
        {
            "check_id": "t1_not_raw_velocity_or_force",
            "severity": "stop",
            "pass": has(text, r"not a raw individual velocity, an inferred force, or a behavioral\s+rule"),
            "finding": "T1 boundary against raw velocity/force interpretation is explicit.",
            "fix": "Restore explicit T1 boundary wording in Data/Observables.",
        },
        {
            "check_id": "local_affine_equation_present",
            "severity": "stop",
            "pass": has(text, r"\\hat\{\\mathbf\{J\}\}_i\(t\).*?\\arg\\min_\{\\mathbf\{J\}\}"),
            "finding": "Local affine least-squares equation is present.",
            "fix": "Restore the local affine equation.",
        },
        {
            "check_id": "compact_state_definitions_present",
            "severity": "stop",
            "pass": (
                has(text, r"compact-density coordinate \$C\(t\)\$")
                and has(text, r"\\dot\{C\}\(t\).*?time gradient")
                and has(text, r"swarm-size coordinate \$R\(t\)\$")
            ),
            "finding": "C(t), dot C(t), and R(t) are defined.",
            "fix": "Restore compact state coordinate definitions.",
        },
        {
            "check_id": "spectral_set_publication_provenance_in_active_methods",
            "severity": "fix_required",
            "pass": (
                has(text, r"transfer-operator\s+compact-density\s+coarse-graining")
                and "r\\_rms" in text
                and "density\\_rms" in text
                and "anisotropy" in text
                and "eig2" in text
                and has(text, r"not fitted from T1|constructed upstream of T1")
            ),
            "finding": "Active Methods should include enough 4147 provenance to avoid circularity.",
            "fix": (
                "Add one concise Methods sentence naming r_rms, density_rms, "
                "anisotropy, eig2, and T1-independence."
            ),
        },
        {
            "check_id": "near_pre_endpoint_distinction_explicit",
            "severity": "fix_required",
            "pass": (
                has(text, r"near-pre \$\[-0\.25,0\.00\)\$")
                and has(text, r"endpoint-inclusive")
                and has(text, r"half-open phase-bin convention")
            ),
            "finding": (
                "4085 phase bins and 4100 state-matched near-pre aggregate use "
                "different endpoint conventions."
            ),
            "fix": "State the distinction explicitly in Methods.",
        },
        {
            "check_id": "radius_unit_exception_defined",
            "severity": "stop",
            "pass": has(text, r"The radius variable depended on the unit of analysis"),
            "finding": "The focal-radius versus swarm-level R exception is stated.",
            "fix": "Restore unit-of-analysis boundary for radius covariate.",
        },
        {
            "check_id": "b3_ratio_defined",
            "severity": "fix_required",
            "pass": has(text, r"B3 denotes the upstream global-affine residual baseline"),
            "finding": "B3 shorthand in local_to_b3_direction_ratio should be defined.",
            "fix": "Add a short definition before the survival-gate threshold list.",
        },
        {
            "check_id": "near_pre_main_count_not_overwritten_by_4142",
            "severity": "stop",
            "pass": not has(text, r"near-pre all-tangential\s+gate counts were \$11/14\$"),
            "finding": "4146 near-pre main-count correction is preserved.",
            "fix": "Keep 4142 near-pre counts as sensitivity evidence only.",
        },
        {
            "check_id": "smoke_null_not_formal_high_b",
            "severity": "stop",
            "pass": has(text, r"smoke-level calibration") and has(text, r"higher-\$B\$ rerun"),
            "finding": "B=100 omnibus null remains correctly bounded.",
            "fix": "Do not describe B=100 as final high-resolution p-value.",
        },
    ]
    rows: list[dict[str, Any]] = []
    for item in checks:
        result = "pass" if item["pass"] else item["severity"]
        rows.append({**item, "result": result})
    return pd.DataFrame(rows)


def write_corrected_equations() -> None:
    text = r"""% 4148 corrected Methods snippets for final reintegration.

% spectral_set provenance sentence
The \texttt{spectral\_set} labels came from an upstream transfer-operator
compact-density coarse-graining of robust-standardized \texttt{r\_rms},
\texttt{density\_rms}, and \texttt{anisotropy}. The selected \texttt{eig2}
partition separated a more compact high-density state from a less compact
low-density state and was constructed upstream of T1, not fitted from T1.

% B3 shorthand sentence
Here, B3 denotes the upstream global-affine residual baseline, so the
\texttt{local\_to\_b3\_direction\_ratio} screen required the local residual to
remain non-negligible relative to that global-affine reference.

% near-pre endpoint distinction
This endpoint-inclusive state-matched window follows the 4100 implementation
and is distinct from the half-open phase-bin convention used for event-aligned
profiles, where the transition frame was assigned to the near-post bin.
"""
    (OUT / "corrected_equations.tex").write_text(text, encoding="utf-8")


def write_summary(
    registry: pd.DataFrame,
    checks: pd.DataFrame,
    occurrences: pd.DataFrame,
    decision: dict[str, Any],
    active: list[Path],
) -> None:
    failed = checks[~checks["pass"]].copy()
    failed_rows = failed[
        ["check_id", "severity", "finding", "fix"]
    ].to_dict(orient="records")
    check_rows = checks[
        ["check_id", "result", "finding"]
    ].to_dict(orient="records")
    text = f"""# 4148 Notation and Equation Consistency Audit

Node: `{NODE}`  
Date: {DATE}

## Result

`{decision['gate_result']}`

## Active LaTeX Path

{md_table([{"file": rel(p)} for p in active], ["file"])}

## Checks

{md_table(check_rows, ["check_id", "result", "finding"])}

## Required Fixes

{md_table(failed_rows, ["check_id", "severity", "finding", "fix"])}

## Registry

{md_table(registry.to_dict(orient="records"), [
    "symbol_or_term",
    "canonical_use",
    "allowed_variants",
    "disallowed_variants",
])}

## Occurrence Table

{md_table(occurrences.to_dict(orient="records"), [
    "pattern_id",
    "file",
    "n_hits",
    "lines",
])}

## Boundary

Only active manuscript files are allowed to fail the 4148 gate. Legacy inactive
LaTeX files remain in the repository but are not part of this audit's pass/fail
decision.
"""
    (OUT / "equation_consistency_check.md").write_text(text, encoding="utf-8")
    (OUT / "4148_summary.md").write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    active = active_tex_files()
    registry = build_registry(active)
    occurrences = build_occurrences(active)
    checks = build_checks(active)

    write_csv(registry, "notation_registry.csv")
    write_csv(occurrences, "notation_occurrences.csv")
    write_csv(checks, "notation_errors.csv")
    write_corrected_equations()

    n_stop_fail = int(((~checks["pass"]) & (checks["severity"] == "stop")).sum())
    n_fix_required = int(((~checks["pass"]) & (checks["severity"] == "fix_required")).sum())
    decision = {
        "node": NODE,
        "date": DATE,
        "gate_result": (
            "pass_4148_active_notation_consistent"
            if n_stop_fail == 0 and n_fix_required == 0
            else (
                "boundary_4148_fix_required_before_final_compile"
                if n_stop_fail == 0
                else "stop_4148_active_notation_contradiction"
            )
        ),
        "primary_metrics": {
            "n_active_tex_files": int(len(active)),
            "n_registry_terms": int(len(registry)),
            "n_checks": int(len(checks)),
            "n_stop_failures": n_stop_fail,
            "n_fix_required": n_fix_required,
        },
        "next": (
            "4150_final_figure_cleanup"
            if n_stop_fail == 0 and n_fix_required == 0
            else "apply_4148_corrected_equations_then_rerun"
        ),
    }
    write_json(decision, "decision.json")
    write_summary(registry, checks, occurrences, decision, active)
    print(json.dumps(decision, indent=2))


if __name__ == "__main__":
    main()
