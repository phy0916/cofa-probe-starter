# Package verification

2026-10-30: Windows, Python 3.13.5, pytest 9.1.1.
- Environment check passed.
- Toolkit tests: 6 passed.
- Runner usage-error check: pytest exit 4 preserved; JSON evidence also recorded 4.
- Initial run could not write to the restricted system temp directory; rerun with approved access passed.
- Tests validate toolkit bookkeeping only, not an exam task or model performance.
- ZIP is built from an explicit source-file list; local work, logs, caches and credentials are excluded.
- Initial ZIP was prepared locally before GitHub authentication. Publication is a separate step.
