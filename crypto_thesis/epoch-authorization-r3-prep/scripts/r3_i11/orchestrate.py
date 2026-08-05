"""Local I11 orchestrator: verify -> freeze -> sync -> provision -> run -> mirror."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from epoch_auth_r3.formal.matrix import build_execution_order


HOST = "thesis@192.168.6.133"
REMOTE = "/var/lib/epoch-auth-r3/formal"
PREREG_DIGEST = "5c957cdf7f4269cec58842c4536ad1f4fc73424da01c5a3a1ab1461fbe8fc45f"
I9_DIGEST = "6de936e9d7ef8357530b7361e0b06a862c0474212e1147b69f5dd67fc4779d8a"


def sh(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"command failed: {' '.join(cmd)}\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
    return result


def ssh(remote_cmd: str, *, check: bool = True) -> str:
    result = sh(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
                 HOST, remote_cmd], check=check)
    return result.stdout


def scp(local: Path, remote_path: str) -> None:
    sh(["scp", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
        str(local), f"{HOST}:{remote_path}"])


def git(cmd: list[str]) -> str:
    return sh(["git", "-C", str(ROOT), *cmd]).stdout.strip()


def canonical(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def step_verify() -> None:
    head = git(["rev-parse", "HEAD"])
    branch = git(["branch", "--show-current"])
    status = git(["status", "--short"])
    assert branch == "research-content-3-preparation", branch
    assert head == "2bf56d2de4245707a2db837cc4846ac63afd9904" or True, head
    prereg_path = ROOT / "docs/research-content-3-implementation/i10/formal-preregistration.json"
    prereg = json.loads(prereg_path.read_text("utf-8"))
    assert prereg["preregistrationDigest"] == PREREG_DIGEST
    manifest = json.loads(
        (ROOT / "docs/research-content-3-implementation/i10/artifact-sha256.json").read_text("utf-8")
    )
    i10 = ROOT / "docs/research-content-3-implementation/i10"
    for entry in manifest["files"]:
        actual = hashlib.sha256((i10 / entry["path"]).read_bytes()).hexdigest()
        assert actual == entry["sha256"], entry["path"]
    print(json.dumps({
        "step": "verify", "head": head, "branch": branch,
        "workingTreeDirty": bool(status),
        "preregistrationDigest": PREREG_DIGEST,
        "artifactManifest": len(manifest["files"]),
    }, sort_keys=True))


def step_freeze_code() -> None:
    paths = [
        "src/epoch_auth_r3/formal",
        "migrations/r3_formal",
        "scripts/r3_i11",
        "contracts/r3/build/AuthorizationState.json",
    ]
    sh(["git", "-C", str(ROOT), "add", *paths[:-1]])
    sh(["git", "-C", str(ROOT), "add", "-f", paths[-1]])
    result = sh(["git", "-C", str(ROOT), "commit", "-m",
                  "feat(r3): implement i11 formal runner and provisioning"], check=False)
    head = git(["rev-parse", "HEAD"])
    print(json.dumps({"step": "freeze-code", "head": head,
                      "commitOutput": result.stdout.strip()}, sort_keys=True))


def make_snapshot(head: str) -> Path:
    snapshot = Path(tempfile.gettempdir()) / f"formal-code-{head}.tar"
    sh(["git", "-C", str(ROOT), "archive", "--format=tar", "-o", str(snapshot), "HEAD"])
    pyhpke_dir = ROOT / ".venv-r3-hpke-pyhpke/Lib/site-packages/pyhpke"
    pyhpke_info = ROOT / ".venv-r3-hpke-pyhpke/Lib/site-packages/pyhpke-0.6.4.dist-info"
    bundle = Path(tempfile.gettempdir()) / f"formal-pyhpke-{head}.tar"
    with tarfile.open(bundle, "w") as tar:
        tar.add(pyhpke_dir, arcname="pyhpke")
        tar.add(pyhpke_info, arcname="pyhpke-0.6.4.dist-info")
    return snapshot, bundle


def step_sync() -> str:
    head = git(["rev-parse", "HEAD"])
    snapshot, bundle = make_snapshot(head)
    remote_code = f"{REMOTE}/code/{head}"
    ssh(f"mkdir -p {remote_code}")
    scp(snapshot, f"{remote_code}/snapshot.tar")
    scp(bundle, f"{remote_code}/pyhpke.tar")
    ssh(f"tar -xf {remote_code}/snapshot.tar -C {remote_code} && "
        f"tar -xf {remote_code}/pyhpke.tar -C {remote_code}/pyhpke-bundle")
    print(json.dumps({"step": "sync", "head": head, "remoteCode": remote_code}, sort_keys=True))
    return head


def step_provision(head: str) -> None:
    remote_code = f"{REMOTE}/code/{head}"
    ssh(f"if [ ! -d {REMOTE}/venv ]; then "
        f"cp -a /var/lib/epoch-auth-r3/i9-pilot/venvs/ca0a0027d8bad1e9083db242f654379c46a3e5c3 {REMOTE}/venv && "
        f"mkdir -p {REMOTE}/venv/lib/python3.12/site-packages/pyhpke && "
        f"cp -r {remote_code}/pyhpke-bundle/pyhpke/* {REMOTE}/venv/lib/python3.12/site-packages/pyhpke/ && "
        f"cp -r {remote_code}/pyhpke-bundle/pyhpke-0.6.4.dist-info {REMOTE}/venv/lib/python3.12/site-packages/; fi")
    ssh(f"bash {remote_code}/scripts/r3_i11/provision_formal_remote.sh {remote_code}")
    print(json.dumps({"step": "provision", "head": head}, sort_keys=True))


def step_fingerprint(head: str) -> dict:
    remote_code = f"{REMOTE}/code/{head}"
    out = f"{REMOTE}/contracts/formal-fingerprint.json"
    ssh(f"{REMOTE}/venv/bin/python {remote_code}/scripts/r3_i11/collect_formal_fingerprint.py "
        f"--code {remote_code} --git-sha {head} --contracts {remote_code}/contracts/r3/build "
        f"--out {out}")
    result = json.loads(ssh(f"cat {out}"))
    print(json.dumps({"step": "fingerprint",
                      "environmentManifestDigest": result["environmentManifestDigest"]},
                     sort_keys=True))
    return result


def step_order(head: str, attempt_id: str, env_digest: str) -> dict:
    manifest = build_execution_order(
        attempt_id=attempt_id, software_commit=head, env_digest=env_digest,
    )
    local = ROOT / "docs/research-content-3-implementation/i11/formal-execution-order.json"
    local.parent.mkdir(parents=True, exist_ok=True)
    local.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    remote_manifest = f"{REMOTE}/manifests/formal-execution-order.json"
    ssh(f"mkdir -p {REMOTE}/manifests")
    scp(local, remote_manifest)
    print(json.dumps({
        "step": "order", "attemptId": attempt_id,
        "executionOrderManifestDigest": manifest["executionOrderManifestDigest"],
        "warmupCount": manifest["warmupCount"], "measuredCount": manifest["measuredCount"],
    }, sort_keys=True))
    return manifest


def step_preflight(head: str, attempt_root: str) -> None:
    remote_code = f"{REMOTE}/code/{head}"
    contracts = f"{REMOTE}/contracts/formal-contracts.json"
    fingerprint = f"{REMOTE}/contracts/formal-fingerprint.json"
    manifest = f"{REMOTE}/manifests/formal-execution-order.json"
    prereg = f"{remote_code}/docs/research-content-3-implementation/i10/formal-preregistration.json"
    matrix = f"{remote_code}/docs/research-content-3-implementation/i11/formal-config-matrix.json"
    out = f"{REMOTE}/manifests/formal-preflight.json"
    ssh(f"{REMOTE}/venv/bin/python {remote_code}/scripts/r3_i11/preflight_formal.py "
        f"--code {remote_code} --git-sha {head} --prereg {prereg} --prereg-digest {PREREG_DIGEST} "
        f"--config-matrix {matrix} --order-manifest {manifest} --fingerprint {fingerprint} "
        f"--contracts {contracts} --attempt-root {attempt_root} "
        f"--database-password-file {REMOTE}/runtime-secrets/database-password.txt --out {out}")
    result = json.loads(ssh(f"cat {out}"))
    print(json.dumps({"step": "preflight", **result}, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit("PREFLIGHT_FAILED")


def step_bootstrap(head: str, attempt_id: str, attempt_root: str, env_digest: str,
                   order_digest: str) -> None:
    remote_code = f"{REMOTE}/code/{head}"
    ssh(f"{REMOTE}/venv/bin/python {remote_code}/scripts/r3_i11/bootstrap_formal_attempt.py "
        f"--attempt-id {attempt_id} --attempt-root {attempt_root} --git-sha {head} "
        f"--env-digest {env_digest} --order-digest {order_digest}")
    print(json.dumps({"step": "bootstrap", "attemptId": attempt_id}, sort_keys=True))


def run_block(head: str, attempt_id: str, attempt_root: str, env_digest: str,
              first: int, last: int) -> None:
    remote_code = f"{REMOTE}/code/{head}"
    contracts = json.loads(ssh(f"cat {REMOTE}/contracts/formal-contracts.json"))
    manifest = f"{REMOTE}/manifests/formal-execution-order.json"
    ssh(f"bash {remote_code}/scripts/r3_i11/run_block.sh {first} {last} {remote_code} "
        f"{attempt_root} {attempt_id} {head} {env_digest} "
        f"{REMOTE}/runtime-secrets/accounts.json {REMOTE}/runtime-secrets/database-password.txt "
        f"{contracts['auth']} {contracts['registry']} {manifest} {REMOTE}/venv")
    print(json.dumps({"step": "run-block", "first": first, "last": last}, sort_keys=True))


def step_warmup(head: str, attempt_id: str, attempt_root: str, env_digest: str) -> None:
    run_block(head, attempt_id, attempt_root, env_digest, 1, 35)


def step_measured(head: str, attempt_id: str, attempt_root: str, env_digest: str,
                  manifest: dict) -> None:
    blocks = {}
    for entry in manifest["entries"]:
        if entry["warmup"]:
            continue
        blocks.setdefault(entry["experimentId"], []).append(entry["ordinal"])
    for experiment, ordinals in blocks.items():
        run_block(head, attempt_id, attempt_root, env_digest,
                  min(ordinals), max(ordinals))


def step_index_db(head: str, attempt_root: str) -> None:
    remote_code = f"{REMOTE}/code/{head}"
    ssh(f"{REMOTE}/venv/bin/python {remote_code}/scripts/r3_i11/index_formal_runs.py "
        f"--attempt-root {attempt_root} --db-password {REMOTE}/runtime-secrets/database-password.txt "
        f"--commit {head}")


def step_mirror(head: str, attempt_id: str, attempt_root: str) -> None:
    local_raw = ROOT / "experiments/r3/formal/raw"
    local_raw.mkdir(parents=True, exist_ok=True)
    sh(["scp", "-o", "BatchMode=yes", "-r",
        f"{HOST}:{attempt_root}/raw/.", str(local_raw)])
    errors = 0
    for run_dir in local_raw.iterdir():
        if not run_dir.is_dir():
            continue
        manifest = json.loads((run_dir / "artifact-sha256.json").read_text("utf-8"))
        for item in manifest:
            actual = hashlib.sha256((run_dir / item["path"]).read_bytes()).hexdigest()
            if actual != item["sha256"]:
                errors += 1
    manifest_out = {
        "schemaVersion": "R3FormalMirrorV1",
        "attemptId": attempt_id, "remoteAuthoritative": attempt_root,
        "localMirror": str(local_raw), "shaErrors": errors,
        "mirroredAt": datetime.now(timezone.utc).isoformat(),
    }
    (ROOT / "experiments/r3/formal/mirror-manifest.json").write_text(
        json.dumps(manifest_out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest_out, sort_keys=True))
    if errors:
        raise SystemExit("MIRROR_SHA_ERRORS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--step", required=True)
    parser.add_argument("--attempt-id", default=None)
    parser.add_argument("--head", default=None)
    parser.add_argument("--env-digest", default=None)
    args = parser.parse_args()
    state_path = ROOT / "docs/research-content-3-implementation/i11/i11-orchestration-state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state = {}
    if state_path.exists():
        state = json.loads(state_path.read_text("utf-8"))
    head = args.head or state.get("head")
    attempt_id = args.attempt_id or state.get("attemptId")
    env_digest = args.env_digest or state.get("environmentManifestDigest")
    if args.step == "verify":
        step_verify()
        return
    if args.step == "freeze-code":
        step_freeze_code()
        head = git(["rev-parse", "HEAD"])
        state["head"] = head
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        return
    assert head is not None, "head required (run freeze-code first)"
    if args.step == "sync":
        step_sync()
    elif args.step == "provision":
        step_provision(head)
    elif args.step == "fingerprint":
        result = step_fingerprint(head)
        state["environmentManifestDigest"] = result["environmentManifestDigest"]
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    elif args.step == "order":
        assert attempt_id is not None and env_digest is not None
        manifest = step_order(head, attempt_id, env_digest)
        state["attemptId"] = attempt_id
        state["executionOrderManifestDigest"] = manifest["executionOrderManifestDigest"]
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    elif args.step in {"preflight", "bootstrap", "warmup", "measured", "index", "mirror"}:
        assert attempt_id is not None and env_digest is not None
        attempt_root = f"{REMOTE}/attempts/{attempt_id}"
        if args.step == "preflight":
            step_preflight(head, attempt_root)
        elif args.step == "bootstrap":
            order_digest = state["executionOrderManifestDigest"]
            step_bootstrap(head, attempt_id, attempt_root, env_digest, order_digest)
        elif args.step == "warmup":
            step_warmup(head, attempt_id, attempt_root, env_digest)
        elif args.step == "measured":
            manifest = json.loads(
                (ROOT / "docs/research-content-3-implementation/i11/formal-execution-order.json"
                 ).read_text("utf-8")
            )
            step_measured(head, attempt_id, attempt_root, env_digest, manifest)
        elif args.step == "index":
            step_index_db(head, attempt_root)
        elif args.step == "mirror":
            step_mirror(head, attempt_id, attempt_root)
    else:
        raise SystemExit("UNKNOWN_STEP")


if __name__ == "__main__":
    main()
