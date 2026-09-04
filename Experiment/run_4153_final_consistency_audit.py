"""Node 4153 final consistency audit for the active manuscript package."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from textwrap import dedent
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Output" / "4153"
TABLES = OUT / "tables"
LATEX = ROOT / "mypaper2" / "Latex"
SUPPLEMENT = ROOT / "Supplement"
DATE = "2026-09-02"
NODE = "4153_final_consistency_audit"


def ensure_dirs() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv_pair(name: str, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    for path in [OUT / name, TABLES / name]:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row.get(field, "") for field in fieldnames})


def md_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    if not rows:
        return "_No rows._"
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        vals = [str(row.get(col, "")).replace("\n", " ").replace("|", "\\|") for col in columns]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def resolve_tex_path(source: Path, input_name: str) -> Path:
    candidate = source.parent / input_name
    if candidate.suffix:
        return candidate
    return candidate.with_suffix(".tex")


def collect_active_tex() -> list[Path]:
    main = LATEX / "main.tex"
    ordered: list[Path] = []
    seen: set[Path] = set()

    def visit(path: Path) -> None:
        path = path.resolve()
        if path in seen:
            return
        seen.add(path)
        ordered.append(path)
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"\\input\{([^}]+)\}", text):
            child = resolve_tex_path(path, match.group(1))
            if child.exists():
                visit(child)

    visit(main)
    return ordered


def read_documents(paths: list[Path]) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            docs.append({"path": rel(path), "lineno": lineno, "line": line})
    return docs


def search_lines(docs: list[dict[str, Any]], pattern: str, flags: int = re.IGNORECASE) -> list[dict[str, Any]]:
    rx = re.compile(pattern, flags)
    return [row for row in docs if rx.search(row["line"])]


def number_audit(docs: list[dict[str, Any]], supplement_docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    combined = docs + supplement_docs
    expectations = [
        ("primary_both_scale", r"(14\s+of\s+19|14/19)", "primary T1 both-scale count"),
        ("primary_any_scale", r"(15\s+of\s+19|15/19)", "primary T1 any-scale count"),
        ("survivor_scale_lag", r"(14\s+of\s+15|14/15)", "survivor-class scale/lag robustness"),
        ("diffuse_tangential", r"(13\s+of\s+14|13/14)", "diffuse all-tangential support"),
        ("near_pre_main", r"(8\s+of\s+14|8/14)", "main near-pre phase-localization count"),
        ("past_only_both", r"(11\s+of\s+19|11/19)", "past-only detrending both-scale count"),
        ("none_z_both", r"(13\s+of\s+19|13/19)", "no-rolling detrending both-scale count"),
        ("omnibus_B100", r"B\s*=?\s*100", "limited-resolution omnibus replicate count"),
        ("omnibus_p", r"0\.0099", "limited-resolution omnibus plus-one p-value"),
        ("affine_median_cond", r"2\.37", "median local affine condition number"),
        ("affine_q95_cond", r"6\.28", "largest q95 local affine condition number"),
        ("event_locality_median", r"-0\.033|-0\.032887", "state-matched near-pre median effect"),
        ("history_q95", r"(6\s+of\s+19|6/19)", "recent-history q95 boundary count"),
    ]
    rows: list[dict[str, Any]] = []
    for item, pattern, meaning in expectations:
        hits_active = search_lines(docs, pattern)
        hits_combined = search_lines(combined, pattern)
        status = "pass" if hits_active else ("supplement_only" if hits_combined else "fix_required")
        example = ""
        if hits_active:
            first = hits_active[0]
            example = f"{first['path']}:{first['lineno']}: {first['line'].strip()}"
        elif hits_combined:
            first = hits_combined[0]
            example = f"{first['path']}:{first['lineno']}: {first['line'].strip()}"
        rows.append(
            {
                "item": item,
                "meaning": meaning,
                "status": status,
                "active_hits": len(hits_active),
                "combined_hits": len(hits_combined),
                "example": example,
            }
        )
    return rows


def claim_audit(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    checks = [
        ("universal_t1", r"\buniversal\b.*\bT1\b|\bT1\b.*\buniversal\b", "review"),
        ("formal_highB_claim", r"formal(?:ly)? calibrated at high \$?B|formal high", "review"),
        ("preprocessing_invariance", r"preprocessing-invariant", "review"),
        ("no_special_dynamics", r"no special dynamics", "review"),
        ("stochastic_impossible", r"stochastic dynamics are impossible", "review"),
        ("memory_rule", r"universal memory|memory rule", "review"),
        ("causal_metadata", r"causal recording|causal metadata|recording-condition explanation", "review"),
    ]
    negation = re.compile(r"\b(not|no|does not|do not|did not|cannot|should not|unsupported|rather than|without)\b", re.I)
    rows: list[dict[str, Any]] = []
    for item, pattern, severity in checks:
        hits = search_lines(docs, pattern)
        for hit in hits:
            line = hit["line"].strip()
            status = "pass_bounded_context" if negation.search(line) else severity
            rows.append(
                {
                    "item": item,
                    "status": status,
                    "path": hit["path"],
                    "lineno": hit["lineno"],
                    "line": line,
                }
            )
        if not hits:
            rows.append({"item": item, "status": "pass_absent", "path": "", "lineno": "", "line": ""})
    return rows


def terminology_audit(docs: list[dict[str, Any]], supplement_docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    forbidden_active = [
        ("smoke_language", r"\bsmoke\b"),
        ("old_figure_names", r"4134_figure"),
        ("internal_nodes_active", r"\b(408x|4134|414x|415x|Node 41\d{2})\b"),
        ("draft_label_active", r"\bdraft\b|main\(2\)"),
        ("raw_windows_path", r"D:\\ExperimentOutput"),
    ]
    for item, pattern in forbidden_active:
        hits = search_lines(docs, pattern)
        rows.append(
            {
                "scope": "active_manuscript",
                "item": item,
                "status": "pass" if not hits else "fix_required",
                "hits": len(hits),
                "example": "" if not hits else f"{hits[0]['path']}:{hits[0]['lineno']}: {hits[0]['line'].strip()}",
            }
        )
    supplement_checks = [
        ("smoke_language", r"\bsmoke\b"),
        ("old_figure_names", r"4134_figure"),
        ("draft_label", r"\bdraft\b|main\(2\)"),
    ]
    for item, pattern in supplement_checks:
        hits = search_lines(supplement_docs, pattern)
        rows.append(
            {
                "scope": "supplement",
                "item": item,
                "status": "pass" if not hits else "review",
                "hits": len(hits),
                "example": "" if not hits else f"{hits[0]['path']}:{hits[0]['lineno']}: {hits[0]['line'].strip()}",
            }
        )
    return rows


def causal_language_audit(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    terms = r"\b(cause|causal|trigger|drive|driven|mechanism|prediction|predict|memory|leader|information transfer|propagation)\b"
    negation = re.compile(r"\b(not|no|does not|do not|did not|cannot|should not|unsupported|rather than|without|outside|not tested)\b", re.I)
    rows: list[dict[str, Any]] = []
    for hit in search_lines(docs, terms):
        line = hit["line"].strip()
        status = "pass_bounded_context" if negation.search(line) else "review"
        rows.append({"status": status, "path": hit["path"], "lineno": hit["lineno"], "line": line})
    if not rows:
        rows.append({"status": "pass_absent", "path": "", "lineno": "", "line": ""})
    return rows


def figure_text_consistency(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    full_text = "\n".join(row["line"] for row in docs)
    expected = [f"figures/Fig{i}_final.pdf" for i in range(1, 6)]
    rows: list[dict[str, Any]] = []
    for fig in expected:
        rows.append(
            {
                "item": fig,
                "status": "pass" if fig in full_text else "fix_required",
                "evidence": "active includegraphics found" if fig in full_text else "missing from active includegraphics",
            }
        )
    old_hits = search_lines(docs, r"4134_figure")
    rows.append(
        {
            "item": "old_4134_figure_references",
            "status": "pass" if not old_hits else "fix_required",
            "evidence": "none in active path" if not old_hits else f"{old_hits[0]['path']}:{old_hits[0]['lineno']}",
        }
    )
    return rows


def reference_audit(active_paths: list[Path]) -> list[dict[str, Any]]:
    cite_labels: set[str] = set()
    for path in active_paths:
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"\\cite\{([^}]+)\}", text):
            for label in match.group(1).split(","):
                cite_labels.add(label.strip())
    bib_path = LATEX / "bibitems.tex"
    bib_text = bib_path.read_text(encoding="utf-8") if bib_path.exists() else ""
    bib_labels = set(re.findall(r"\\bibitem\{([^}]+)\}", bib_text))
    rows: list[dict[str, Any]] = []
    for label in sorted(cite_labels):
        rows.append(
            {
                "item": "cited_label",
                "label": label,
                "status": "pass" if label in bib_labels else "stop_missing_bibitem",
                "evidence": "found in bibitems" if label in bib_labels else "missing from bibitems",
            }
        )
    for label in sorted(bib_labels - cite_labels):
        rows.append({"item": "unused_bibitem", "label": label, "status": "review_unused", "evidence": "bibitem is not cited in active path"})
    if not rows:
        rows.append({"item": "no_citations_detected", "label": "", "status": "review", "evidence": "no citation labels were found"})
    return rows


def summarize_status(*tables: list[dict[str, Any]]) -> tuple[str, int, int]:
    flat = [row for table in tables for row in table]
    stop = sum(1 for row in flat if str(row.get("status", "")).startswith("stop"))
    fix = sum(1 for row in flat if str(row.get("status", "")) == "fix_required")
    gate = "pass_4153_final_consistency_audit_clean" if stop == 0 and fix == 0 else "boundary_4153_consistency_fixes_required"
    return gate, stop, fix


def main() -> None:
    ensure_dirs()
    active_paths = collect_active_tex()
    supplement_paths = sorted(SUPPLEMENT.glob("*.md")) if SUPPLEMENT.exists() else []
    docs = read_documents(active_paths)
    supplement_docs = read_documents(supplement_paths)

    number_rows = number_audit(docs, supplement_docs)
    claim_rows = claim_audit(docs)
    term_rows = terminology_audit(docs, supplement_docs)
    causal_rows = causal_language_audit(docs)
    fig_rows = figure_text_consistency(docs)
    ref_rows = reference_audit(active_paths)

    write_csv_pair("number_audit.csv", number_rows, ["item", "meaning", "status", "active_hits", "combined_hits", "example"])
    write_csv_pair("claim_audit.csv", claim_rows, ["item", "status", "path", "lineno", "line"])
    write_csv_pair("terminology_audit.csv", term_rows, ["scope", "item", "status", "hits", "example"])
    write_csv_pair("causal_language_audit.csv", causal_rows, ["status", "path", "lineno", "line"])
    write_csv_pair("figure_text_consistency.csv", fig_rows, ["item", "status", "evidence"])
    write_csv_pair("reference_audit.csv", ref_rows, ["item", "label", "status", "evidence"])

    gate, stop, fix = summarize_status(number_rows, claim_rows, term_rows, causal_rows, fig_rows, ref_rows)
    review = sum(
        1
        for table in [number_rows, claim_rows, term_rows, causal_rows, fig_rows, ref_rows]
        for row in table
        if "review" in str(row.get("status", ""))
    )
    decision = {
        "node": NODE,
        "date": DATE,
        "gate_result": gate,
        "primary_metrics": {
            "n_active_tex_files": len(active_paths),
            "n_supplement_files": len(supplement_paths),
            "n_stop_items": stop,
            "n_fix_required_items": fix,
            "n_review_items": review,
        },
        "next": "4154_submission_package_freeze" if gate.startswith("pass") else "repair 4153 fix_required items before 4154",
    }
    write_json(OUT / "decision.json", decision)

    summary = dedent(
        f"""\
        # Node 4153 Summary

        ## Purpose

        Audit the active manuscript and technical supplement for number,
        claim, terminology, causal-language, figure-text, and reference
        consistency.

        ## Gate Result

        `{gate}`

        ```text
        active_tex_files = {len(active_paths)}
        supplement_files = {len(supplement_paths)}
        stop_items = {stop}
        fix_required_items = {fix}
        review_items = {review}
        ```

        ## Active TeX Path

        {md_table([{"path": rel(path)} for path in active_paths], ["path"])}

        ## Number Audit

        {md_table(number_rows, ["item", "status", "active_hits", "combined_hits", "example"])}

        ## Figure/Text Audit

        {md_table(fig_rows, ["item", "status", "evidence"])}

        ## Reference Audit

        {md_table(ref_rows, ["item", "label", "status", "evidence"])}

        ## Interpretation

        Stop-level and fix-required items block 4154. Review-only items should
        be inspected but do not block the freeze if they are bounded negations,
        unsupported-claim labels, or unused bibliography entries intentionally
        retained.
        """
    )
    (OUT / "final_audit_summary.md").write_text(summary, encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
