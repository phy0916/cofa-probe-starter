"""Validate structure, never infer whether a requirement is actually met."""
import csv
from pathlib import Path
import sys

FIELDS = {"id", "source", "requirement", "acceptance", "implementation", "test", "evidence", "status"}
STATUSES = {"open", "in_progress", "blocked", "verified"}

def validate(path):
    errors = []
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if set(reader.fieldnames or []) != FIELDS:
            return ["Expected columns: " + ", ".join(sorted(FIELDS))]
        rows = list(reader)
    if not rows:
        errors.append("No requirements recorded; blank template is not completion.")
    seen = set()
    for line, row in enumerate(rows, 2):
        if None in row or any(v is None for v in row.values()):
            errors.append(f"Line {line}: malformed CSV row")
            continue
        row = {k: v.strip() for k, v in row.items()}
        for key in ("id", "source", "requirement", "acceptance"):
            if not row[key]:
                errors.append(f"Line {line}: missing {key}")
        if row["id"] in seen:
            errors.append(f"Line {line}: duplicate id")
        seen.add(row["id"])
        if row["status"] not in STATUSES:
            errors.append(f"Line {line}: invalid status")
        if row["status"] == "verified":
            for key in ("implementation", "test", "evidence"):
                if not row[key]:
                    errors.append(f"Line {line}: verified needs {key}")
    return errors

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/check_traceability.py PATH.csv")
        sys.exit(2)
    try:
        errors = validate(sys.argv[1])
    except (OSError, UnicodeError, csv.Error) as exc:
        print(str(exc))
        sys.exit(2)
    print("\n".join(errors) if errors else "Structure valid; functional correctness not evaluated.")
    sys.exit(1 if errors else 0)
