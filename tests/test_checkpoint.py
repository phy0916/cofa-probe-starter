"""Exercise real Git snapshots and evidence boundaries; no exam assertions."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("checkpoint", ROOT / "scripts/checkpoint.py")
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)


@pytest.fixture
def repo(tmp_path):
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True)
    shutil.copytree(ROOT / "templates", tmp_path / "templates")
    (tmp_path / ".gitignore").write_text("work/\n", encoding="utf-8")
    (tmp_path / "module.txt").write_text("before", encoding="utf-8")
    cp.git(tmp_path, "add", ".")
    cp.git(tmp_path, "-c", "user.name=Toolkit test", "-c", "user.email=test@example.invalid",
           "commit", "-m", "fixture")
    return tmp_path


def test_dirty_snapshot_does_not_commit_or_stage(repo):
    sha = cp.git(repo, "rev-parse", "HEAD")
    (repo / "module.txt").write_text("after", encoding="utf-8")
    (repo / "new.txt").write_text("new", encoding="utf-8")
    status = cp.git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    folder = cp.checkpoint(repo, "v01")
    snapshot = json.loads((folder / "snapshot.json").read_text(encoding="utf-8"))
    assert snapshot["head_sha"] == sha
    assert snapshot["working_tree_status"] == status
    assert snapshot["evidence"] == []
    assert cp.git(repo, "rev-parse", "HEAD") == sha
    assert cp.git(repo, "status", "--porcelain=v1", "--untracked-files=all") == status
    assert "UNKNOWN" in (folder / "AI_COLLABORATION.md").read_text(encoding="utf-8")
    assert sha in (folder / "TECHNICAL_CHECKLIST.md").read_text(encoding="utf-8")


def test_no_overwrite_or_path_escape(repo):
    folder = cp.checkpoint(repo, "v01")
    (folder / "CHANGE.md").write_text("human notes", encoding="utf-8")
    with pytest.raises(FileExistsError):
        cp.checkpoint(repo, "v01")
    assert (folder / "CHANGE.md").read_text(encoding="utf-8") == "human notes"
    with pytest.raises(ValueError):
        cp.checkpoint(repo, "../escape")


def test_failed_test_evidence_stays_failed_and_unbound(repo):
    logs = repo / "work/logs"
    logs.mkdir(parents=True)
    (logs / "run.log").write_text("1 failed", encoding="utf-8")
    (logs / "run.json").write_text(json.dumps(dict(command=["python", "-m", "pytest"],
        exit_code=1, started_utc="2026-11-05T00:00:00+00:00", output_file="run.log")), encoding="utf-8")
    folder = cp.checkpoint(repo, "failed", ["work/logs/run.json"])
    evidence = json.loads((folder / "snapshot.json").read_text(encoding="utf-8"))["evidence"][0]
    assert evidence["exit_code"] == 1
    assert evidence["version_binding"].startswith("UNVERIFIED")


def test_invalid_evidence_creates_no_checkpoint(repo):
    with pytest.raises(ValueError):
        cp.checkpoint(repo, "bad", ["module.txt"])
    assert not (repo / "work/checkpoints/bad").exists()


def test_missing_log_not_treated_as_evidence(repo):
    logs = repo / "work/logs"
    logs.mkdir(parents=True)
    (logs / "run.json").write_text(json.dumps(dict(command=[], exit_code=0,
        started_utc="unknown", output_file="missing.log")), encoding="utf-8")
    with pytest.raises(ValueError):
        cp.checkpoint(repo, "bad", ["work/logs/run.json"])
