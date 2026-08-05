"""I11FormalPreflightV1: fail-closed checks before any warm-up RUN."""
from __future__ import annotations

import argparse
import hashlib
import json
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path

from web3 import Web3

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from epoch_auth_r3.formal.matrix import ORDER_DOMAIN


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(name: str, passed: bool, detail: str = "") -> dict:
    return {"item": name, "status": "PASS" if passed else "FAIL", "detail": detail}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--code", required=True)
    parser.add_argument("--git-sha", required=True)
    parser.add_argument("--prereg", required=True)
    parser.add_argument("--prereg-digest", required=True)
    parser.add_argument("--config-matrix", required=True)
    parser.add_argument("--order-manifest", required=True)
    parser.add_argument("--fingerprint", required=True)
    parser.add_argument("--contracts", required=True)
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--database-password-file", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    checks: list[dict] = []

    checks.append(check("execution_host", socket.gethostname() == "experiment-client",
                        socket.gethostname()))
    checks.append(check("git_clean_execution_sha", len(args.git_sha) == 40, args.git_sha))
    prereg = json.loads(Path(args.prereg).read_text("utf-8"))
    checks.append(check(
        "preregistration_digest",
        prereg.get("preregistrationDigest") == args.prereg_digest,
        prereg.get("preregistrationDigest", ""),
    ))
    matrix = json.loads(Path(args.config_matrix).read_text("utf-8"))
    checks.append(check(
        "config_matrix",
        matrix.get("measuredConfigs") == 29 and matrix.get("warmupConfigs") == 35,
        f"measured={matrix.get('measuredConfigs')} warmup={matrix.get('warmupConfigs')}",
    ))
    order = json.loads(Path(args.order_manifest).read_text("utf-8"))
    checks.append(check(
        "execution_order_manifest",
        order.get("warmupCount") == 35 and order.get("measuredCount") == 145
        and order.get("totalRuns") == 180,
        f"warmup={order.get('warmupCount')} measured={order.get('measuredCount')}",
    ))
    fingerprint = json.loads(Path(args.fingerprint).read_text("utf-8"))
    env = fingerprint["environmentFingerprint"]
    checks.append(check("environment_fingerprint",
                        env.get("schemaVersion") == "R3FormalEnvironmentFingerprintV1"
                        and env.get("host") == "experiment-client"
                        and env.get("pilotFormalSeparation") is True,
                        f"digest={fingerprint['environmentManifestDigest'][:16]}..."))
    checks.append(check("disk_space", int(env.get("storageDeviceAndFreeBytes", 0)) > 1.2 * 10**9,
                        f"{env.get('storageDeviceAndFreeBytes')} bytes free"))
    checks.append(check("ram", int(env.get("ramBytes", 0)) > 2 * 10**9,
                        f"{env.get('ramBytes')} bytes"))
    contracts = json.loads(Path(args.contracts).read_text("utf-8"))
    checks.append(check(
        "formal_chain_identity",
        contracts.get("chainId") == 2026080201
        and contracts.get("auth", "").startswith("0x")
        and contracts.get("registry", "").startswith("0x"),
        f"chainId={contracts.get('chainId')} auth={contracts.get('auth')} "
        f"registry={contracts.get('registry')}",
    ))
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:18546", request_kwargs={"timeout": 5}))
    checks.append(check("chain_rpc", w3.is_connected() and w3.eth.chain_id == 2026080201,
                        f"connected={w3.is_connected()} chainId={w3.eth.chain_id if w3.is_connected() else 'n/a'}"))
    checks.append(check(
        "contract_addresses_resolve",
        w3.is_connected() and w3.eth.get_code(contracts["auth"]) != b""
        and w3.eth.get_code(contracts["registry"]) != b"",
        "both contracts have bytecode",
    ))
    checks.append(check("clock_validity",
                        abs((datetime.now(timezone.utc) - datetime.fromisoformat(
                            prereg.get("createdAt", "1970-01-01T00:00:00+00:00")
                        ).astimezone(timezone.utc)).total_seconds()) < 7 * 86400,
                        "wall clock within 7 days of preregistration"))
    checks.append(check("no_pilot_asset_mix",
                        "i9-pilot" not in str(Path(args.attempt_root))
                        and "2026073005" not in json.dumps(contracts)
                        and "r3_i5" not in json.dumps(contracts),
                        "no Pilot identities referenced"))
    db_password = Path(args.database_password_file).read_text("utf-8").strip()
    checks.append(check("secret_boundary",
                        len(db_password) >= 32
                        and oct(Path(args.database_password_file).stat().st_mode & 0o777) == "0o600",
                        "external 0600 secret file"))
    canonical = hashlib.sha256(
        ORDER_DOMAIN
        + json.dumps(order["entries"], sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    checks.append(check(
        "execution_order_frozen",
        order.get("executionOrderManifestDigest") == canonical,
        "manifest digest self-consistent",
    ))
    failed = [c for c in checks if c["status"] != "PASS"]
    result = {
        "schemaVersion": "I11FormalPreflightV1",
        "total": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "checks": checks,
        "status": "PASS" if not failed else "FAIL",
        "checkedAt": datetime.now(timezone.utc).isoformat(),
    }
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
