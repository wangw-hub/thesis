# I3 Reproducibility Report

- Platform: Windows development worktree.
- Python: isolated `.venv-r3-hpke-pyhpke`, Python 3.13.x.
- Dependency baseline: `requirements-r3-i1-v2.lock`.
- Commands run independently to avoid duplicate pytest module names:
  - `python -m pytest tests/r3/i1 -q --confcutdir=tests/r3/i1`
  - `python -m pytest tests/r3/i2 -q --confcutdir=tests/r3/i2`
  - `python -m pytest tests/r3/i3 -q --confcutdir=tests/r3/i3`
- I3 result: 48 passed, 0 failed.
- Tests use temporary directories, fixed nonsecret test material and no external services.
- No throughput, latency, memory or comparative performance conclusion was generated.

