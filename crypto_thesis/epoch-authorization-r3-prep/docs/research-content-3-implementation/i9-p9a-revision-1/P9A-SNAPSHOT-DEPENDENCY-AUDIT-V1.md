# P9ASnapshotDependencyAuditV1

Entry points audited:

- `scripts/r3_i9/bootstrap_revision6_attempt.py`;
- `scripts/r3_i9/run_revised_remote_pilot.py`;
- `scripts/r3_i9/preflight_application_name.py`;
- `scripts/r3_i9/preflight_composite_read.py`;
- `scripts/r3_i9/preflight_revision8_transaction.py`;
- `tests/r3/i9/`.

The Python import graph requires `src/epoch_auth_r3/`. The I9 pytest collection loads root `tests/conftest.py`, which imports `src/epoch_auth/` and the separately frozen remote `time-policy` dependency. Runtime file-read analysis found one repository ABI dependency, `contracts/r3/build/HeaderRegistryV1.json`. Database schema tests and controlled preflight require SQL under `migrations/`. Package metadata and the three R3 lock files are retained for dependency provenance. `AGENTS.md` is retained as the minimal execution-governance boundary.

The isolated-chain admission run additionally proved that `run_revised_remote_pilot.py` imports `_anchor` and `_signed_tx` from `scripts/r3_i5/deploy_and_validate.py` at module-load time. That single tracked helper module is therefore a required transitive runtime dependency; the rest of `scripts/r3_i5/` remains excluded.

Allowlisted snapshot roots/files:

- `AGENTS.md`;
- `pyproject.toml`;
- `requirements-r3-i1-v2.lock`;
- `requirements-r3-i4.lock`;
- `requirements-r3-i9-revision.lock`;
- `src/epoch_auth/**/*.py`;
- `src/epoch_auth_r3/**/*.py`;
- the five audited `scripts/r3_i9/*.py` entry/preflight files;
- `scripts/r3_i5/deploy_and_validate.py`, solely for the P9-A runner's imported anchor and signed-transaction helpers;
- `tests/conftest.py` and `tests/r3/i9/*.py`;
- `contracts/r3/build/HeaderRegistryV1.json`;
- `migrations/**/*.sql`.

Every file must also be tracked by the frozen Git commit. Cache files, bytecode and untracked files are excluded even below allowlisted directories.

Explicitly excluded categories: thesis/manuscript sources, DOCX/PDF/LaTeX assets, `docs/`, historical `experiments/`, raw attempts, reports, figures/images, historical logs, database dumps, Besu data, Kubo repositories, `node_modules`, virtual environments, caches, build/dist outputs except the single frozen ABI, Git metadata/objects, private keys, ROOT_KEK, passwords, tokens, SSH material, credentials, Body plaintext and CK.

Classification result: every included path maps to runtime, preflight, test, dependency, ABI, migration, package or governance purpose. `UNCLASSIFIED=0`. No secret-bearing path is allowed.
