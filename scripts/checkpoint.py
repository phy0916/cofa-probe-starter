"""Explicit local snapshot; never stages, commits, pushes, or calls AI."""
import argparse
import datetime as dt
import json
from pathlib import Path
import re
import subprocess
import sys
import hashlib
from evidence import private_work, state, git as read_git

ROOT = Path(__file__).resolve().parents[1]


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          capture_output=True, text=True, encoding="utf-8").stdout.strip()


def checkpoint(root, name, evidence=(), base=None):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", name):
        raise ValueError("Name: 1-64 ASCII letters, digits, _ or -; start with letter/digit")
    root = Path(root).resolve()
    private_work(root)
    if Path(git(root, "rev-parse", "--show-toplevel")).resolve() != root:
        raise ValueError("Run against a repository root, not a parent repository")
    sha = git(root, "rev-parse", "HEAD")
    captured = state(root)
    if base:
        base = git(root, "rev-parse", "--verify", "--end-of-options", base + "^{commit}")
    else:
        parents = git(root, "rev-list", "--parents", "-n", "1", sha).split()
        base = parents[1] if len(parents) > 1 else None
    # Capture state BEFORE creating documentation. Dirty files are not part of HEAD.
    status = git(root, "status", "--porcelain=v1", "--untracked-files=all")
    manifest = {
        "captured_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "head_sha": sha,
        "state": captured,
        "base_sha": base,
        "version": git(root, "describe", "--tags", "--match", "v[0-9]*", "--always") +
                   ("-dirty-" + captured["fingerprint"][:8] if captured["status"] else ""),
        "head_files": git(root, "diff-tree", "--root", "--no-commit-id",
                          "--name-status", "-r", sha),
        "working_tree_status": status,
        "scope": "HEAD/range and separate dirty diff; Python source snapshot includes untracked code; local only",
        "evidence": [],
    }
    remote = read_git(root, "config", "--get", "remote.origin.url", check=False)
    match = re.fullmatch(r"(?:https://github.com/|git@github.com:)([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?", remote)
    if match:
        url = "https://github.com/" + match[1]
        manifest["commit_url"] = url + "/commit/" + sha
        manifest["compare_url"] = url + "/compare/" + base + "..." + sha if base else None
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
        if not log.resolve().is_relative_to(root / "work" / "logs"):
            raise ValueError("Evidence log must remain inside work/logs")
        if not log.is_file() or not isinstance(record["command"], list) or type(record["exit_code"]) is not int:
            raise ValueError("Incomplete runner evidence")
        manifest["evidence"].append({
            "metadata": path.relative_to(root).as_posix(),
            "output": log.relative_to(root).as_posix(),
            "command": record["command"], "exit_code": record["exit_code"],
            "started_utc": record["started_utc"],
            "version_binding": ("MATCHED: nonignored file fingerprint only" if
                record.get("state_before", {}).get("fingerprint") == captured["fingerprint"] ==
                record.get("state_after", {}).get("fingerprint") else
                "UNVERIFIED: stale, changed during run, or legacy log; confirm tested files"),
            "output_sha256": hashlib.sha256(log.read_bytes()).hexdigest(),
        })
    folder = root / "work" / "checkpoints" / name
    folder.mkdir(parents=True, exist_ok=False)  # Never overwrite a human's notes.
    (folder / "snapshot.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Diff contents remain local; separate committed range from working tree changes.
    (folder / "committed.diff").write_text(
        git(root, "diff", "--no-ext-diff", "--no-textconv", base, sha) if base else
        git(root, "show", "--format=fuller", "--no-ext-diff", "--no-textconv", sha), encoding="utf-8")
    (folder / "working.diff").write_text(git(root, "diff", "--no-ext-diff", "--no-textconv", sha), encoding="utf-8")
    (folder / "history.txt").write_text(git(root, "log", "-20", "--format=%H %aI %s"), encoding="utf-8")
    code = []
    for item in captured["files"]:
        path = root / item["path"]
        if path.suffix == ".py" and item["kind"] == "file":
            body = path.read_text(encoding="utf-8", errors="replace")
            # Explicit limit; Codex must inspect omitted files locally when needed.
            code.append("\n## " + item["path"] + "\n" + "\n".join(
                f"{n}: {line}" for n, line in enumerate(body[:200000].splitlines(), 1)) +
                ("\nTRUNCATED: inspect original locally" if len(body) > 200000 else ""))
    (folder / "code.txt").write_text("Python source snapshot; other languages require local inspection.\n" + "\n".join(code), encoding="utf-8")
    for index, item in enumerate(evidence):
        record_path = (root / item).resolve()
        record = json.loads(record_path.read_text(encoding="utf-8"))
        (folder / f"test-{index}.json").write_text(record_path.read_text(encoding="utf-8"), encoding="utf-8")
        (folder / f"test-{index}.log").write_bytes(record_path.with_name(record["output_file"]).read_bytes())
    for source, target in (("change-record.md", "CHANGE.md"),
                           ("ai-collaboration.md", "AI_COLLABORATION.md"),
                           ("technical-checklist.md", "TECHNICAL_CHECKLIST.md")):
        body = (root / "templates" / source).read_text(encoding="utf-8")
        (folder / target).write_text(f"<!-- HEAD {sha}; evidence: snapshot.json; draft, human review required -->\n" + body, encoding="utf-8")
    from study_pack import generate
    generate(folder)
    index = ["# Local version history", "", "Commit links cover committed changes only. Dirty content is local.", ""]
    for path in sorted(folder.parent.glob("*/snapshot.json")):
        item = json.loads(path.read_text(encoding="utf-8"))
        index.append(f"- [{path.parent.name}]({path.parent.name}/STUDY_DRAFT.md): "
                     f"{item.get('version', item['head_sha'])}; {item['captured_utc']}")
    (folder.parent / "INDEX.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    return folder


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="Unique milestone, e.g. v01-input")
    parser.add_argument("--evidence", action="append", default=[], help="Runner JSON path relative to repo; repeatable")
    parser.add_argument("--base", help="Explicit earlier commit/tag for the committed range (default HEAD parent)")
    args = parser.parse_args()
    try:
        folder = checkpoint(ROOT, args.name, args.evidence, args.base)
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print(f"Checkpoint failed: {exc}", file=sys.stderr)
        return 1
    print(f"Local draft: {folder}\nNo tests run by this command. Review version binding and fill UNKNOWN fields.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
