"""Run pytest without a shell; keep local evidence and exact exit status."""
import datetime as dt
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]

def main(args=None):
    args = sys.argv[1:] if args is None else args
    folder = ROOT / "work" / "logs"
    folder.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stem = folder / (stamp + "-" + uuid.uuid4().hex[:8])
    command = [sys.executable, "-m", "pytest", *args]
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    # Inherit environment for pytest compatibility; do not record environment values.
    with stem.with_suffix(".log").open("w", encoding="utf-8") as log:
        result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                text=True, check=False)
    try:
        version = importlib.metadata.version("pytest")
    except importlib.metadata.PackageNotFoundError:
        version = None
    stem.with_suffix(".json").write_text(json.dumps({
        "started_utc": started,
        "finished_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "command": command, "python": sys.version.split()[0], "pytest": version,
        "exit_code": result.returncode, "output_file": stem.name + ".log"
    }, indent=2), encoding="utf-8")
    print(stem.with_suffix(".log").read_text(encoding="utf-8"))
    print("Local evidence:", stem.with_suffix(".json"))
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
