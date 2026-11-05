"""Real Git integration tests for local evidence and opt-in automation."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest
import checkpoint as cp
from evidence import git, private_work, state
from install_hook import install

SOURCE = Path(__file__).resolve().parents[1]


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo with spaces"
    root.mkdir()
    git(root, "init")
    git(root, "config", "user.name", "Toolkit test")
    git(root, "config", "user.email", "test@example.invalid")
    shutil.copytree(SOURCE / "scripts", root / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(SOURCE / "templates", root / "templates")
    (root / ".gitignore").write_text("__pycache__/\n.pytest_cache/\n", encoding="utf-8")
    (root / "sample.py").write_text("VALUE = 1\n", encoding="utf-8")
    git(root, "add", ".")
    git(root, "commit", "-m", "synthetic fixture")
    return root


def log(root, exit_code=1):
    private_work(root)
    folder = root / "work/logs"
    folder.mkdir(exist_ok=True)
    (folder / "test.log").write_text("synthetic failure\n", encoding="utf-8")
    record = dict(command=["synthetic-test"], exit_code=exit_code, started_utc="fixture",
                  output_file="test.log", state_before=state(root), state_after=state(root))
    (folder / "test.json").write_text(json.dumps(record), encoding="utf-8")
    return "work/logs/test.json"


def test_matching_failure_and_stale_log(repo):
    evidence = log(repo)
    first = cp.checkpoint(repo, "matched", [evidence])
    record = json.loads((first / "snapshot.json").read_text(encoding="utf-8"))
    assert record["evidence"][0]["exit_code"] == 1
    assert record["evidence"][0]["version_binding"].startswith("MATCHED")
    (repo / "sample.py").write_text("VALUE = 2\n", encoding="utf-8")
    second = cp.checkpoint(repo, "stale", [evidence])
    record = json.loads((second / "snapshot.json").read_text(encoding="utf-8"))
    assert record["evidence"][0]["version_binding"].startswith("UNVERIFIED")
    assert "VALUE = 2" in (second / "working.diff").read_text(encoding="utf-8")
    assert "VALUE = 2" in (second / "code.txt").read_text(encoding="utf-8")
    assert (first / "test-0.log").read_text(encoding="utf-8") == "synthetic failure\n"


def test_fingerprint_new_deleted_files_and_private_work(repo):
    before = state(repo)["fingerprint"]
    (repo / "new.py").write_text("new", encoding="utf-8")
    assert state(repo)["fingerprint"] != before
    (repo / "new.py").unlink()
    private_work(repo)
    (repo / "work/confidential.txt").write_text("synthetic private data", encoding="utf-8")
    assert state(repo)["fingerprint"] == before
    assert "work/" not in git(repo, "status", "--porcelain")
    (repo / "sample.py").unlink()
    assert state(repo)["fingerprint"] != before


def test_tracked_work_refused(repo):
    (repo / "work").mkdir()
    (repo / "work/a.txt").write_text("fixture", encoding="utf-8")
    git(repo, "add", "work/a.txt")
    with pytest.raises(ValueError, match="tracked"):
        cp.checkpoint(repo, "blocked")


def test_hook_runs_after_commit_with_spaces_and_does_not_stage(repo):
    hook = install(repo)
    with pytest.raises(ValueError, match="already exists"):
        install(repo)
    (repo / "sample.py").write_text("VALUE = 3\n", encoding="utf-8")
    git(repo, "add", "sample.py")
    git(repo, "commit", "-m", "trigger opt-in hook")
    snapshots = list((repo / "work/checkpoints").glob("*/snapshot.json"))
    assert len(snapshots) == 1
    assert json.loads(snapshots[0].read_text(encoding="utf-8"))["head_sha"] == git(repo, "rev-parse", "HEAD")
    assert git(repo, "status", "--porcelain") == ""
    assert hook.exists()


def test_hook_configuration_and_existing_hook_preserved(repo):
    git(repo, "config", "core.hooksPath", "custom-hooks")
    with pytest.raises(ValueError, match="hooksPath"):
        install(repo)
    git(repo, "config", "--unset", "core.hooksPath")
    hook = repo / ".git/hooks/post-commit"
    hook.write_text("human hook", encoding="utf-8")
    with pytest.raises(ValueError):
        install(repo)
    assert hook.read_text(encoding="utf-8") == "human hook"


def test_runner_real_failure_and_usage_error(repo):
    (repo / "test_sample.py").write_text("def test_failure():\n    assert False\n", encoding="utf-8")
    result = subprocess.run([sys.executable, str(repo / "scripts/run_tests.py"), "test_sample.py", "-q"], capture_output=True)
    assert result.returncode == 1
    result = subprocess.run([sys.executable, str(repo / "scripts/run_tests.py"), "--not-a-real-pytest-option"], capture_output=True)
    assert result.returncode == 4
    records = [json.loads(p.read_text(encoding="utf-8")) for p in (repo / "work/logs").glob("*.json")]
    assert sorted(r["exit_code"] for r in records) == [1, 4]
    assert all(r["state_before"]["fingerprint"] == r["state_after"]["fingerprint"] for r in records)


def test_tag_range_six_questions_no_invented_answers(repo):
    git(repo, "tag", "v0.1")
    folder = cp.checkpoint(repo, "v01", base="v0.1")
    snapshot = json.loads((folder / "snapshot.json").read_text(encoding="utf-8"))
    assert snapshot["version"] == "v0.1"
    assert snapshot["base_sha"] == snapshot["head_sha"]
    draft = (folder / "STUDY_DRAFT.md").read_text(encoding="utf-8")
    assert draft.count("검증된 답변: 확인 필요") == 6
    assert "확인 필요" in draft
    assert "CODEX_REVIEW.md" in draft
    assert "v01" in (folder.parent / "INDEX.md").read_text(encoding="utf-8")
