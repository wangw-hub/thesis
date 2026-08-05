"""Collect final public service, chain, and configuration evidence."""

from __future__ import annotations

import hashlib
import json
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
CHAIN = ROOT / "infra" / "besu-qbft-multihost" / "formal-authorization-chain"
HOSTS = [
    "besu-validator-1",
    "besu-validator-2",
    "besu-validator-3",
    "besu-validator-4",
    "experiment-client",
]
FORMAL_GENESIS = "7d431f01aab7d0c55c58c09346ee1f9a43475322a4aca304cfbb172b9b32add4"


def ssh(host: str, command: str) -> str:
    result = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", host, command],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def rpc(method: str, params: list) -> object:
    payload = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1})
    script = (
        "python3 -c 'import json,urllib.request;"
        f"p={json.dumps(payload)}.encode();"
        "r=urllib.request.urlopen(urllib.request.Request("
        "\"http://192.168.6.133:8645\",data=p,"
        "headers={\"Content-Type\":\"application/json\"}),timeout=10);"
        "print(r.read().decode())'"
    )
    return json.loads(ssh("experiment-client", script))["result"]


def main() -> None:
    hosts = {}
    for host in HOSTS:
        service = "besu-formal-rpc.service" if host == "experiment-client" else "besu-formal.service"
        hosts[host] = {
            "formal_service": ssh(host, f"systemctl is-active {service}"),
            "old_service": ssh(host, "systemctl is-enabled besu.service 2>/dev/null || true"),
            "genesis_sha256": ssh(
                host, "sudo -n sha256sum /etc/besu-formal/genesis.json | cut -d' ' -f1"
            ),
            "besu_version": ssh(host, "/opt/besu/bin/besu --version"),
            "java_version": ssh(host, "java -version 2>&1 | head -1"),
        }
    before = int(rpc("eth_blockNumber", []), 16)
    time.sleep(6)
    after = int(rpc("eth_blockNumber", []), 16)
    validators = rpc("qbft_getValidatorsByBlockNumber", ["latest"])
    evidence = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "chain_id": int(rpc("eth_chainId", []), 16),
        "peer_count": int(rpc("net_peerCount", []), 16),
        "validators": validators,
        "block_before": before,
        "block_after": after,
        "blocks_growing": after > before,
        "hosts": hosts,
        "all_formal_services_active": all(v["formal_service"] == "active" for v in hosts.values()),
        "all_old_services_disabled": all(v["old_service"] == "disabled" for v in hosts.values()),
        "all_genesis_hashes_match": all(
            v["genesis_sha256"] == FORMAL_GENESIS for v in hosts.values()
        ),
        "accepted": (
            int(rpc("eth_chainId", []), 16) == 2026072901
            and int(rpc("net_peerCount", []), 16) == 4
            and len(validators) == 4
            and after > before
            and all(v["formal_service"] == "active" for v in hosts.values())
            and all(v["genesis_sha256"] == FORMAL_GENESIS for v in hosts.values())
        ),
    }
    target = CHAIN / "evidence" / "f13" / "final-live-health.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    files = []
    for path in sorted(CHAIN.rglob("*")):
        if not path.is_file() or "private" in path.parts or path.name == "artifact-sha256.json":
            continue
        files.append(
            {
                "path": path.relative_to(CHAIN).as_posix(),
                "size": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    index = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "FUNDING_REVIEW_ONLY": False,
        "formal_chain_id": 2026072901,
        "file_count": len(files),
        "files": files,
    }
    (CHAIN / "artifact-sha256.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"accepted": evidence["accepted"], "block": after, "files": len(files)}))


if __name__ == "__main__":
    main()
