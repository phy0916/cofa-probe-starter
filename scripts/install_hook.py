"""Explicit one-time, local post-commit activation; refuses existing hooks."""
import argparse
from pathlib import Path
import shlex
import sys

from evidence import git, private_work

ROOT = Path(__file__).resolve().parents[1]
MARKER = "# cofa-evidence-hook-v1"


def install(root=ROOT):
    private_work(root)
    if git(root, "config", "--get", "core.hooksPath", check=False):
        raise ValueError("core.hooksPath already configured; use explicit checkpoint command")
    hooks = Path(git(root, "rev-parse", "--git-path", "hooks"))
    if not hooks.is_absolute():
        hooks = Path(root) / hooks
    hooks.mkdir(parents=True, exist_ok=True)
    hook = hooks / "post-commit"
    if hook.exists():
        raise ValueError("post-commit already exists; preserve it and use explicit checkpoint")
    # Git for Windows executes hook through its sh; quote Windows paths as POSIX strings.
    command = " ".join(shlex.quote(str(x).replace("\\", "/")) for x in
                       [sys.executable, Path(root) / "scripts" / "auto_checkpoint.py"])
    hook.write_text(f'#!/bin/sh\n{MARKER}\n{command}\n', encoding="utf-8", newline="\n")
    hook.chmod(0o755)
    return hook


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try:
        print("Installed local hook:", install())
    except (OSError, ValueError) as exc:
        parser.exit(1, str(exc) + "\n")
