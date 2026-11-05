"""Post-commit fallback: capture evidence only, never run tests or AI."""
import datetime as dt
import sys
import uuid

from checkpoint import ROOT, checkpoint

if __name__ == "__main__":
    try:
        name = "commit-" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]
        logs = sorted((ROOT / "work/logs").glob("*.json"), key=lambda p: p.stat().st_mtime)
        folder = checkpoint(ROOT, name, [str(logs[-1].relative_to(ROOT))] if logs else [])
        print("Local checkpoint:", folder, "\nCodex: complete CODEX_REVIEW.md; tests were not run by this hook.")
    except Exception as exc:
        print("Checkpoint failed AFTER commit; commit already exists. Run checkpoint.py manually:", exc, file=sys.stderr)
        sys.exit(1)
