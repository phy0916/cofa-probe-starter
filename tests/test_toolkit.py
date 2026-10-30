"""Toolkit tests only: these do not validate any exam deliverable."""
import csv
import importlib.util
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("trace", ROOT / "scripts/check_traceability.py")
trace = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trace)

def write_rows(tmp_path, rows):
    path = tmp_path / "requirements.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=sorted(trace.FIELDS))
        writer.writeheader()
        writer.writerows(rows)
    return path

def row():
    return dict(id="R1", source="mock requirement", requirement="placeholder",
                acceptance="observable criterion", implementation="file:line",
                test="test identifier", evidence="local log reference", status="verified")

def test_blank_template_not_complete(tmp_path):
    assert trace.validate(write_rows(tmp_path, []))

def test_verified_requires_evidence(tmp_path):
    item = row()
    item["evidence"] = ""
    assert any("evidence" in e for e in trace.validate(write_rows(tmp_path, [item])))

def test_duplicate_ids_rejected(tmp_path):
    assert any("duplicate" in e for e in trace.validate(write_rows(tmp_path, [row(), row()])))

def test_complete_structure(tmp_path):
    assert trace.validate(write_rows(tmp_path, [row()])) == []

def test_invalid_status(tmp_path):
    item = row()
    item["status"] = "passed"
    assert trace.validate(write_rows(tmp_path, [item]))

def test_missing_file_exit_code(tmp_path):
    result = subprocess.run([sys.executable, str(ROOT / "scripts/check_traceability.py"),
                             str(tmp_path / "missing.csv")], capture_output=True)
    assert result.returncode == 2
