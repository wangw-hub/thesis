"""Execute the approved controlled fault sequence for the formal chain."""

from __future__ import annotations

import json
import subprocess
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RPC_URL = "http://192.168.6.133:8645"


def ssh(host: str, command: str) -> dict:
    result = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", host, command],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    return {"exit_code": result.returncode, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}


def rpc(method: str, params: list | None = None) -> object:
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params or []}).encode()
    request = urllib.request.Request(RPC_URL, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=5) as response:
        data = json.loads(response.read())
    if "error" in data:
        raise RuntimeError(data["error"])
    return data["result"]


def height() -> int:
    return int(rpc("eth_blockNumber"), 16)


def main() -> None:
    result: dict[str, object] = {"started_at_unix": int(time.time())}

    before = height()
    result["validator_stop"] = ssh(
        "besu-validator-4", "sudo -n systemctl stop besu-formal.service"
    )
    time.sleep(10)
    during = height()
    result["validator_start"] = ssh(
        "besu-validator-4",
        "sudo -n systemctl start besu-formal.service; sleep 5; systemctl is-active besu-formal.service",
    )
    time.sleep(6)
    after = height()
    result["validator_fault"] = {
        "before_height": before,
        "during_height": during,
        "after_height": after,
        "continued_production": during > before,
        "recovered": result["validator_start"]["stdout"].splitlines()[-1:] == ["active"],
    }
    if not result["validator_fault"]["continued_production"] or not result["validator_fault"]["recovered"]:
        raise RuntimeError("validator fault acceptance failed")

    result["rpc_stop"] = ssh(
        "experiment-client", "sudo -n systemctl stop besu-formal-rpc.service"
    )
    time.sleep(8)
    issuer_log = ssh(
        "experiment-client",
        "journalctl -u epoch-auth-issuer.service -n 8 --no-pager -o cat",
    )
    issuer_state = ssh(
        "experiment-client", "systemctl is-active epoch-auth-issuer.service || true"
    )
    result["rpc_fault"] = {
        "issuer_log": issuer_log,
        "issuer_state": issuer_state,
        "fail_closed_observed": issuer_state["stdout"] != "active"
        or ('"healthy": false' in issuer_log["stdout"] and '"fail_closed": true' in issuer_log["stdout"]),
    }
    result["rpc_start"] = ssh(
        "experiment-client",
        "sudo -n systemctl start besu-formal-rpc.service; sleep 10; sudo -n systemctl start epoch-auth-issuer.service epoch-auth-verifier-1.service epoch-auth-verifier-2.service; systemctl is-active besu-formal-rpc.service",
    )
    if not result["rpc_fault"]["fail_closed_observed"]:
        raise RuntimeError("issuer did not fail closed during RPC outage")

    result["postgres_stop"] = ssh(
        "experiment-client", "sudo -n systemctl stop postgresql"
    )
    time.sleep(8)
    verifier_log = ssh(
        "experiment-client",
        "journalctl -u epoch-auth-verifier-1.service -u epoch-auth-verifier-2.service -n 12 --no-pager -o cat",
    )
    verifier_state = ssh(
        "experiment-client",
        "systemctl is-active epoch-auth-verifier-1.service epoch-auth-verifier-2.service || true",
    )
    result["postgres_fault"] = {
        "verifier_log": verifier_log,
        "verifier_state": verifier_state,
        "fail_closed_observed": "inactive" in verifier_state["stdout"]
        or "failed" in verifier_state["stdout"]
        or ('"healthy": false' in verifier_log["stdout"] and '"fail_closed": true' in verifier_log["stdout"]),
    }
    result["postgres_start"] = ssh(
        "experiment-client",
        "sudo -n systemctl start postgresql; sleep 8; sudo -n systemctl start epoch-auth-verifier-1.service epoch-auth-verifier-2.service; systemctl is-active postgresql",
    )
    if not result["postgres_fault"]["fail_closed_observed"]:
        raise RuntimeError("verifiers did not fail closed during PostgreSQL outage")

    rows_before = ssh(
        "experiment-client",
        "sudo -n -u postgres psql -At -d epoch_auth -c \"SELECT count(*) FROM consumed_nonces WHERE chain_id=2026072901\"",
    )
    result["verifier_restart"] = ssh(
        "experiment-client",
        "sudo -n systemctl restart epoch-auth-verifier-1.service; sleep 6; systemctl is-active epoch-auth-verifier-1.service",
    )
    rows_after = ssh(
        "experiment-client",
        "sudo -n -u postgres psql -At -d epoch_auth -c \"SELECT count(*) FROM consumed_nonces WHERE chain_id=2026072901\"",
    )
    result["verifier_recovery"] = {
        "rows_before": rows_before,
        "rows_after": rows_after,
        "nonce_persisted": rows_before["stdout"] == rows_after["stdout"],
        "service_active": result["verifier_restart"]["stdout"].splitlines()[-1:] == ["active"],
    }
    if not result["verifier_recovery"]["nonce_persisted"] or not result["verifier_recovery"]["service_active"]:
        raise RuntimeError("verifier restart persistence failed")
    result["finished_at_unix"] = int(time.time())
    target = ROOT / "evidence" / "f10"
    target.mkdir(parents=True, exist_ok=True)
    (target / "controlled-faults.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {
                "validator_continued": True,
                "rpc_fail_closed": True,
                "postgres_fail_closed": True,
                "verifier_nonce_persisted": True,
            }
        )
    )


if __name__ == "__main__":
    main()
