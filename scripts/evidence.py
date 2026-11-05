"""Local-only evidence helpers. No network, staging, commit, or AI inference."""
import hashlib
import json
from pathlib import Path
import subprocess


def git(root, *args, check=True):
    result = subprocess.run(["git", "-C", str(root), *args], check=check,
                            capture_output=True, encoding="utf-8", errors="replace")
    return result.stdout.rstrip("\r\n")


def private_work(root):
    root = Path(root).resolve()
    if Path(git(root, "rev-parse", "--show-toplevel")).resolve() != root:
        raise ValueError("Expected repository root")
    # Ignore is not protection for already tracked files. Refuse rather than untrack.
    if git(root, "ls-files", "--", "work"):
        raise ValueError("work/ contains tracked files; choose a clean local workspace")
    exclude = Path(git(root, "rev-parse", "--git-path", "info/exclude"))
    if not exclude.is_absolute():
        exclude = root / exclude
    exclude.parent.mkdir(parents=True, exist_ok=True)
    old = exclude.read_text(encoding="utf-8") if exclude.exists() else ""
    if "/work/" not in old.splitlines():
        with exclude.open("a", encoding="utf-8") as handle:
            handle.write("\n/work/\n")
    work = root / "work"
    if work.is_symlink() or (work.exists() and work.resolve() != work):
        raise ValueError("work/ must be a real local directory")
    work.mkdir(exist_ok=True)
    return work


def state(root):
    """Hash exact nonignored tracked/untracked files, including deletions and paths.

    Ignored inputs/dependencies are outside the binding; this is not a signed attestation.
    """
    names = sorted(set(git(root, "ls-files", "-z", "--cached", "--others",
                           "--exclude-standard").split("\0")) - {""})
    digest = hashlib.sha256()
    files = []
    for name in names:
        if name.startswith("work/"):
            continue
        path = Path(root) / name
        if path.is_symlink():
            content = str(path.readlink()).encode("utf-8")
            kind = "symlink"
        elif path.is_file():
            content = path.read_bytes()
            kind = "file"
        else:
            content, kind = b"", "missing-or-submodule"
        sha = hashlib.sha256(content).hexdigest()
        digest.update(json.dumps([name, kind, sha], ensure_ascii=False).encode("utf-8"))
        files.append({"path": name, "kind": kind, "sha256": sha})
    return {"head": git(root, "rev-parse", "HEAD"),
            "fingerprint": digest.hexdigest(), "files": files,
            "status": git(root, "status", "--porcelain=v1", "--untracked-files=all"),
            "binding_scope": "nonignored tracked/untracked files; excludes work/, ignored inputs, environment and submodule contents"}
