"""Read-only check. Never installs or updates tools."""
import importlib.metadata
import json
import platform
import shutil
import sys

if __name__ == "__main__":
    try:
        pytest_version = importlib.metadata.version("pytest")
    except importlib.metadata.PackageNotFoundError:
        pytest_version = None
    print(json.dumps({"python": platform.python_version(), "pytest": pytest_version,
                      "git_available": bool(shutil.which("git"))}, indent=2))
    sys.exit(0 if sys.version_info >= (3, 10) and pytest_version else 1)
