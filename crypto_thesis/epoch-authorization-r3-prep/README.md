# epoch-authorization

Local minimum prototype for the thesis chapter on Epoch-bound and user-key-bound
capability authorization.

The prototype supports both an in-memory confirmed-state abstraction and a
controlled, real Besu QBFT state backend. Its measurements are not formal
alliance-chain performance results.

Two policy executors share the same state, CAP1/CAP2 encoding, Ed25519 signatures,
nonce store, validation order, and request workload:

- `Baseline-I`: binary search over canonical intervals `I*`.
- `Proposed-C`: leaf-to-root membership over the derived dyadic cover `C(P)`.

`C(P)` is a falsifiable candidate interface. It is not assumed to outperform
`I*`.

Run:

```powershell
python -m pytest
```

## Besu controlled network

The validated local topology is four QBFT validators plus one non-validating
RPC node. Prepare and start the pinned Besu 26.5.0 release with:

```powershell
& .\blockchain\besu\scripts\start-local.ps1
& .\blockchain\besu\scripts\health.ps1
$env:PYTHONPATH = "src"
python scripts\deploy_besu.py
python scripts\besu_semantic_check.py
```

`docker-compose.yml` defines the equivalent pinned container topology and
passes `docker compose config`. The image execution path is not marked as
validated because this host's Docker registry downloads returned corrupted
short reads. See `研究内容二Besu受控实现验收报告.md` for the precise boundary.
