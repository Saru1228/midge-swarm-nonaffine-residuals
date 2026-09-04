#!/usr/bin/env python3
"""Lightweight verification for the node-4157 release package."""
from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    decision_4156 = load_json(ROOT / "Output" / "4156" / "decision.json")
    decision_4157 = load_json(ROOT / "Output" / "4157" / "decision.json")
    compile_4157 = load_json(ROOT / "Output" / "4157" / "compile_log_audit.json")
    p_omnibus = load_json(ROOT / "Output" / "4155" / "p_omnibus.json")
    availability_tex = ROOT / "manuscript" / "latex" / "06_data_code_availability.tex"
    zip_path = ROOT / "Output" / "4156" / "mypaper2_4156_submission_package.zip"
    if not zip_path.exists():
        raise FileNotFoundError(zip_path)
    if not availability_tex.exists():
        raise FileNotFoundError(availability_tex)

    with zipfile.ZipFile(zip_path, "r") as zf:
        bad = zf.testzip()
        names = set(zf.namelist())
        inner_decision = json.loads(zf.read("decision.json").decode("utf-8"))

    checks = {
        "gate_result": decision_4156.get("gate_result"),
        "inner_gate_result": inner_decision.get("gate_result"),
        "zip_bad_file": bad,
        "zip_contains_main_pdf": "main_final.pdf" in names,
        "zip_contains_highB_decision": "highB_evidence_4155/decision.json" in names,
        "B": p_omnibus.get("n_null_replicates"),
        "observed_n_both": p_omnibus.get("observed_n_both"),
        "n_both_null_max": p_omnibus.get("n_both_null_max"),
        "p_both_ge_14": p_omnibus.get("p_omnibus_both_ge_14"),
        "availability_gate_result": decision_4157.get("gate_result"),
        "availability_pdf_pages": compile_4157.get("pdf_pages"),
        "availability_overfull_boxes": compile_4157.get("overfull_boxes"),
        "availability_tex_contains_url": "https://github.com/Saru1228/midge-swarm-nonaffine-residuals"
        in availability_tex.read_text(encoding="utf-8"),
        "availability_tex_contains_tag": "v4157-availability"
        in availability_tex.read_text(encoding="utf-8"),
    }

    expected = [
        checks["gate_result"] == "pass_4156_highB_integrated_submission_package_refrozen",
        checks["inner_gate_result"] == checks["gate_result"],
        checks["zip_bad_file"] is None,
        checks["zip_contains_main_pdf"] is True,
        checks["zip_contains_highB_decision"] is True,
        checks["B"] == 1000,
        checks["observed_n_both"] == 14,
        checks["n_both_null_max"] == 12.0,
        checks["availability_gate_result"]
        == "pass_4157_repository_availability_integrated_and_compiled",
        checks["availability_pdf_pages"] == 10,
        checks["availability_overfull_boxes"] == 0,
        checks["availability_tex_contains_url"] is True,
        checks["availability_tex_contains_tag"] is True,
    ]

    print(json.dumps(checks, indent=2))
    if not all(expected):
        print("Release verification failed.", file=sys.stderr)
        return 1
    print("Release verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
