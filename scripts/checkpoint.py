"""Explicit local snapshot; never stages, commits, pushes, or calls AI."""
import argparse
import datetime as dt
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          capture_output=True, text=True, encoding="utf-8").stdout.strip()


def checkpoint(root, name, evidence=()):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", name):
        raise ValueError("Name: 1-64 ASCII letters, digits, _ or -; start with letter/digit")
    root = Path(root).resolve()
    if Path(git(root, "rev-parse", "--show-toplevel")).resolve() != root:
        raise ValueError("Run against a repository root, not a parent repository")
    sha = git(root, "rev-parse", "HEAD")
    # Capture state BEFORE creating documentation. Dirty files are not part of HEAD.
    status = git(root, "status", "--porcelain=v1", "--untracked-files=all")
    manifest = {
        "captured_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "head_sha": sha,
        "head_files": git(root, "diff-tree", "--root", "--no-commit-id",
                          "--name-status", "-r", sha),
        "working_tree_status": status,
        "scope": "HEAD plus separately listed uncommitted paths; no uncommitted content archived",
        "evidence": [],
    }
    for item in evidence:
        path = (root / item).resolve()
        # Accept only the existing runner's local metadata/output pair.
        if not path.is_relative_to(root / "work" / "logs") or path.suffix != ".json":
            raise ValueError("Evidence must be a work/logs/*.json runner record")
        record = json.loads(path.read_text(encoding="utf-8"))
        output = record["output_file"]
        if not isinstance(output, str) or Path(output).name != output:
            raise ValueError("Evidence output_file must be a basename")
        log = path.with_name(output)
        if not log.is_file() or not isinstance(record["command"], list) or type(record["exit_code"]) is not int:
            raise ValueError("Incomplete runner evidence")
        manifest["evidence"].append({
            "metadata": path.relative_to(root).as_posix(),
            "output": log.relative_to(root).as_posix(),
            "command": record["command"], "exit_code": record["exit_code"],
            "started_utc": record["started_utc"],
            "version_binding": "UNVERIFIED: confirm tested files match this checkpoint",
        })
    folder = root / "work" / "checkpoints" / name
    folder.mkdir(parents=True, exist_ok=False)  # Never overwrite a human's notes.
    (folder / "snapshot.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for source, target in (("change-record.md", "CHANGE.md"),
                           ("ai-collaboration.md", "AI_COLLABORATION.md"),
                           ("technical-checklist.md", "TECHNICAL_CHECKLIST.md")):
        body = (root / "templates" / source).read_text(encoding="utf-8")
        (folder / target).write_text(f"<!-- HEAD {sha}; evidence: snapshot.json; draft, human review required -->\n" + body, encoding="utf-8")
    return folder


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="Unique milestone, e.g. v01-input")
    parser.add_argument("--evidence", action="append", default=[], help="Runner JSON path relative to repo; repeatable")
    args = parser.parse_args()
    try:
        folder = checkpoint(ROOT, args.name, args.evidence)
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print(f"Checkpoint failed: {exc}", file=sys.stderr)
        return 1
    print(f"Local draft: {folder}\nNo tests run by this command. Review version binding and fill UNKNOWN fields.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
