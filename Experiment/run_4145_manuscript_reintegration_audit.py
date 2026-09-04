#!/usr/bin/env python3
"""4145 manuscript reintegration audit.

This node verifies that the 4144 claim-boundary updates were integrated into
the active mypaper2 LaTeX manuscript and records the compile state.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4145"
TABLES = OUT / "tables"
DATE = "2026-09-02"
NODE = "4145_manuscript_reintegration"


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def ensure_dirs() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)


def write_csv(df: pd.DataFrame, filename: str) -> None:
    df.to_csv(OUT / filename, index=False)
    df.to_csv(TABLES / filename, index=False)


def check_patterns() -> pd.DataFrame:
    checks = [
        {
            "target_file": "mypaper2/Latex/00_abstract.tex",
            "integration_point": "abstract_414x_boundary",
            "required_patterns": [
                "pseudo-event smoke null",
                "detrending challenge",
                "38 observation-scale",
                "preprocessing-invariant",
            ],
        },
        {
            "target_file": (
                "mypaper2/Latex/Part3/"
                "03_methods_affine_reduction_and_controls_v2.tex"
            ),
            "integration_point": "methods_submission_hardening_checks",
            "required_patterns": [
                "Three post-freeze checks",
                "pseudo-event omnibus null",
                "$B=100$",
                "past-only one-second detrending",
                "condition numbers",
            ],
        },
        {
            "target_file": "mypaper2/Latex/Part4/04_results_t1_survival_v2.tex",
            "integration_point": "results_t1_4141_4142_4143",
            "required_patterns": [
                "$N_{\\mathrm{both}}=14$",
                "0.0099",
                "$11/19$",
                "$13/19$",
                "condition number greater than 100",
            ],
        },
        {
            "target_file": "mypaper2/Latex/Part4/04_results_diffuse_phenotype_v2.tex",
            "integration_point": "results_near_pre_detrending_boundary",
            "required_patterns": ["$11/14$", "$8/14$", "$12/14$", "causal online"],
        },
        {
            "target_file": "mypaper2/Latex/Part4/04_results_empirical_boundary_v2.tex",
            "integration_point": "evidence_to_claim_table_414x_rows",
            "required_patterns": [
                "Detrending challenge",
                "Affine-fit conditioning QC",
                "smoke null $p=0.0099$",
            ],
        },
        {
            "target_file": (
                "mypaper2/Latex/Part5/"
                "05_discussion_limitations_future_v2.tex"
            ),
            "integration_point": "discussion_completed_checks",
            "required_patterns": [
                "submission-hardening checks",
                "null maximum of 11",
                "higher-$B$ rerun",
                "numerical QC result",
            ],
        },
        {
            "target_file": "mypaper2/Latex/Part5/05_conclusion_v2.tex",
            "integration_point": "conclusion_414x_boundary",
            "required_patterns": [
                "smoke-null",
                "conditioning checks",
                "detrending choice",
            ],
        },
    ]
    rows: list[dict[str, Any]] = []
    for item in checks:
        path = ROOT / item["target_file"]
        text = read_text(path) if path.exists() else ""
        missing = [pat for pat in item["required_patterns"] if pat not in text]
        rows.append(
            {
                "target_file": item["target_file"],
                "integration_point": item["integration_point"],
                "exists": path.exists(),
                "n_required_patterns": len(item["required_patterns"]),
                "n_found_patterns": len(item["required_patterns"]) - len(missing),
                "missing_patterns": "; ".join(missing),
                "pass": path.exists() and not missing,
            }
        )
    return pd.DataFrame(rows)


def compile_audit() -> dict[str, Any]:
    latex_dir = ROOT / "mypaper2" / "Latex"
    log_path = latex_dir / "main.log"
    pdf_path = latex_dir / "main.pdf"
    log_text = read_text(log_path) if log_path.exists() else ""

    error_patterns = [
        r"^!",
        r"LaTeX Error",
        r"Emergency stop",
        r"Fatal error",
        r"Undefined control sequence",
    ]
    warning_patterns = [
        r"undefined references",
        r"Reference .* undefined",
        r"Citation .* undefined",
        r"Label\\(s\\) may have changed",
    ]
    errors = []
    for pat in error_patterns:
        errors.extend(re.findall(pat, log_text, flags=re.MULTILINE))
    unresolved = []
    for pat in warning_patterns:
        unresolved.extend(re.findall(pat, log_text, flags=re.IGNORECASE))
    page_match = re.search(r"Output written on main\.pdf \((\d+) pages?,", log_text)
    pages = int(page_match.group(1)) if page_match else None

    return {
        "log_file": rel(log_path),
        "pdf_file": rel(pdf_path),
        "pdf_exists": pdf_path.exists(),
        "pdf_size_bytes": pdf_path.stat().st_size if pdf_path.exists() else 0,
        "pages": pages,
        "n_latex_errors": len(errors),
        "n_unresolved_reference_or_citation_warnings": len(unresolved),
        "underfull_warnings_present": "Underfull" in log_text,
    }


def write_summary(pattern_df: pd.DataFrame, compile_info: dict[str, Any], decision: dict[str, Any]) -> None:
    passed = int(pattern_df["pass"].sum())
    total = int(len(pattern_df))
    rows_md = [
        "| Target | Integration point | Result | Missing |",
        "| --- | --- | --- | --- |",
    ]
    for row in pattern_df.to_dict(orient="records"):
        result = "pass" if row["pass"] else "boundary"
        missing = row["missing_patterns"] or "none"
        rows_md.append(
            f"| `{row['target_file']}` | {row['integration_point']} | {result} | {missing} |"
        )

    text = f"""# 4145 Manuscript Reintegration Audit

Node: `{NODE}`  
Date: {DATE}

## Result

`{decision['gate_result']}`

4145 integrated the 4144 claim-boundary updates into the active `mypaper2`
LaTeX manuscript and synchronized the main English working drafts.

## Integration Checks

{chr(10).join(rows_md)}

## Compile Check

- PDF: `{compile_info['pdf_file']}`
- Pages: `{compile_info['pages']}`
- PDF size: `{compile_info['pdf_size_bytes']}` bytes
- LaTeX errors: `{compile_info['n_latex_errors']}`
- Unresolved reference/citation warnings: `{compile_info['n_unresolved_reference_or_citation_warnings']}`
- Underfull warnings present: `{compile_info['underfull_warnings_present']}`

## Boundary

The manuscript now includes 4141, 4142, and 4143, but the high-B 4141
confirmation remains optional future statistical hardening. The integrated
claim is therefore: common T1 survival under the frozen local-affine pipeline,
supportive smoke-null calibration, explicit detrending sensitivity, and a
numerical affine-fit QC pass.
"""
    (OUT / "4145_summary.md").write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    pattern_df = check_patterns()
    compile_info = compile_audit()
    write_csv(pattern_df, "manuscript_integration_audit.csv")
    (OUT / "compile_audit.json").write_text(
        json.dumps(compile_info, indent=2), encoding="utf-8"
    )

    all_patterns_pass = bool(pattern_df["pass"].all())
    compile_pass = (
        compile_info["pdf_exists"]
        and compile_info["n_latex_errors"] == 0
        and compile_info["n_unresolved_reference_or_citation_warnings"] == 0
    )
    decision = {
        "node": NODE,
        "date": DATE,
        "gate_result": (
            "pass_4145_manuscript_reintegration_compiled"
            if all_patterns_pass and compile_pass
            else "boundary_4145_manual_review_needed"
        ),
        "primary_metrics": {
            "n_integration_checks": int(len(pattern_df)),
            "n_integration_checks_passed": int(pattern_df["pass"].sum()),
            "pdf_pages": compile_info["pages"],
            "pdf_size_bytes": compile_info["pdf_size_bytes"],
            "n_latex_errors": compile_info["n_latex_errors"],
            "n_unresolved_reference_or_citation_warnings": compile_info[
                "n_unresolved_reference_or_citation_warnings"
            ],
        },
        "changed_active_latex_files": [
            "mypaper2/Latex/00_abstract.tex",
            "mypaper2/Latex/Part3/03_methods_affine_reduction_and_controls_v2.tex",
            "mypaper2/Latex/Part4/04_results_t1_survival_v2.tex",
            "mypaper2/Latex/Part4/04_results_diffuse_phenotype_v2.tex",
            "mypaper2/Latex/Part4/04_results_empirical_boundary_v2.tex",
            "mypaper2/Latex/Part5/05_discussion_limitations_future_v2.tex",
            "mypaper2/Latex/Part5/05_conclusion_v2.tex",
        ],
        "changed_working_drafts": [
            "mypaper2/03_data_methods/draft_en.md",
            "mypaper2/04_results_local_nonaffine/draft_en.md",
            "mypaper2/05_results_reduction_boundaries/draft_en.md",
            "mypaper2/06_discussion_conclusion/draft_en.md",
        ],
        "remaining_boundaries": [
            "4141 is smoke-level with B=100 unless high-B confirmation is run.",
            "The exact 14/19 both-scale support is strongest under centered detrending.",
            "4143 supports numerical conditioning only, not biological mechanism.",
        ],
        "next": [
            "manual prose review for length and figure/table layout",
            "optional 4141 high-B confirmation",
        ],
    }
    write_summary(pattern_df, compile_info, decision)
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2), encoding="utf-8")
    print(json.dumps(decision, indent=2))


if __name__ == "__main__":
    main()
