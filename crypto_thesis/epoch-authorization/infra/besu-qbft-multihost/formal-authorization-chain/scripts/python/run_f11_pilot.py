"""Run the frozen 108-configuration formal-chain PILOT_ONLY workload."""

from __future__ import annotations

import hashlib
import json
import os
import random
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from time_policy.compiler import compile_policy
from time_policy.models import Interval
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
import psutil

PROJECT_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from epoch_auth.baseline_i import BaselineIExecutor
from epoch_auth.cache import (
    AuthorizationCacheContext,
    LruTtlCache,
    evaluate_baseline_cached,
    evaluate_proposed_cached,
)
from epoch_auth.issuer import CapabilityIssuer
from epoch_auth.models import (
    AuthorizationRequest,
    Operation,
    ResourceState,
    ResourceStatus,
    UserState,
    UserStatus,
)
from epoch_auth.proposed_c import ProposedCExecutor
from epoch_auth.state_store import PolicyRepository
from epoch_auth.verifier import CapabilityVerifier
from experiments.multihost.recorder import AppendOnlyRecorder

ROOT = Path(__file__).resolve().parents[2]
SECRET_ROOT = Path(r"D:\Research\crypto_thesis\secrets\formal-authorization-chain-2026072901")
CHAIN_ID = 2026072901
CONTRACT = bytes.fromhex("9ef44cf538d0df457ba77c556d8785e48bfc436d")
RPC_URL = "http://192.168.6.133:8645"


class FrozenStore:
    def __init__(self, resource: ResourceState, user: UserState) -> None:
        self.resource = resource
        self.user = user

    def get_authorization_state(self, resource_id: str, user_id: str):
        return (
            self.resource if resource_id == self.resource.resource_id else None,
            self.user if user_id == self.user.user_id else None,
        )


class BridgeNonceStore:
    def __init__(self, verifier_id: str) -> None:
        self.verifier_id = verifier_id
        self.lock = threading.Lock()
        self.counter = 0
        self.process = subprocess.Popen(
            [
                "ssh", "-o", "BatchMode=yes", "experiment-client",
                "sudo -n -u epoch-auth python3 /opt/epoch-auth-formal/nonce_bridge.py",
            ],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8",
        )

    def consume_once(self, resource_id: str, epoch: int, nonce: bytes) -> bool:
        with self.lock:
            self.counter += 1
            request = {
                "id": self.counter, "resource_id": resource_id, "epoch": epoch,
                "nonce": nonce.hex(), "verifier_id": self.verifier_id,
            }
            self.process.stdin.write(json.dumps(request) + "\n")
            self.process.stdin.flush()
            response = json.loads(self.process.stdout.readline())
            if response.get("error"):
                raise RuntimeError("PostgreSQL nonce bridge unavailable")
            return bool(response["accepted"])

    def close(self) -> None:
        if self.process.stdin:
            self.process.stdin.close()
        self.process.terminate()
        self.process.wait(timeout=10)


class CachedExecutor:
    def __init__(self, method: str, context: AuthorizationCacheContext) -> None:
        self.method = method
        self.context = context
        self.cache = LruTtlCache(256, 60_000_000_000)
        self.base = BaselineIExecutor() if method == "B1" else ProposedCExecutor()

    def evaluate(self, policy, timestamp):
        if self.method == "B1":
            return evaluate_baseline_cached(policy, timestamp, self.context, self.cache).match
        return evaluate_proposed_cached(policy, timestamp, self.context, self.cache).match

    def validate_binding(self, policy, timestamp, node, version):
        return self.base.validate_binding(policy, timestamp, node, version)


def main() -> None:
    git_sha = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    run_id = f"pilot_multihost_20260729_{git_sha}"
    run_root = PROJECT_ROOT / "experiments" / "runs" / run_id
    for directory in ("manifest", "configs", "workloads", "raw", "processed", "logs", "node-evidence", "database-evidence", "reports"):
        (run_root / directory).mkdir(parents=True, exist_ok=True)
    raw_path = run_root / "raw" / "pilot.jsonl"
    recorder = AppendOnlyRecorder(raw_path)
    completed_keys = set()
    if raw_path.exists():
        for line in raw_path.read_text(encoding="utf-8").splitlines():
            item = json.loads(line)
            completed_keys.add((item["sample_id"], item["method"]))
    process = psutil.Process(os.getpid())
    workloads = [
        json.loads(line)
        for line in (PROJECT_ROOT / "experiments" / "multihost" / "workloads" / "pilot.jsonl").read_text().splitlines()
        if json.loads(line)["policy"]["U"] == 1024
    ]
    if len(workloads) != 27:
        raise RuntimeError(f"expected 27 representative workloads, got {len(workloads)}")
    issuer_key = Ed25519PrivateKey.from_private_bytes(
        (SECRET_ROOT / "services" / "issuer-1" / "ed25519-private.raw").read_bytes()
    )
    user_public = (SECRET_ROOT / "services" / "user-1" / "ed25519-public.raw").read_bytes()
    web3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={"timeout": 10}))
    web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    rpc_lock = threading.Lock()
    attempt_token = str(time.time_ns())
    bridges = [BridgeNonceStore("Verifier-1"), BridgeNonceStore("Verifier-2")]
    origin = datetime(2026, 7, 29, tzinfo=UTC)
    sample_count = len(completed_keys)
    config_count = 0
    try:
        for workload in workloads:
            data = workload["policy"]
            policy = compile_policy(
                [Interval(left, right) for left, right in data["normalized_policy"]],
                time_origin=origin, delta=timedelta(minutes=1), domain_size=data["U"],
            )
            allowed_slots = [
                slot for interval in policy.intervals for slot in range(interval.left, interval.right)
            ]
            for method in ("B0", "B1", "C0", "C1"):
                config_count += 1
                resource_id = f"pilot-{workload['workload_id']}-{method}"
                user_id = "authorization-user-001"
                resource = ResourceState(
                    resource_id, "formal-owner", policy.digest, 1, ResourceStatus.ACTIVE, 1
                )
                user = UserState(user_id, hashlib.sha256(user_public).digest(), UserStatus.ACTIVE, 1)
                store = FrozenStore(resource, user)
                context = AuthorizationCacheContext(
                    CHAIN_ID, CONTRACT, resource_id, policy.digest, 1, 1,
                    user.user_key_id, 1, int(Operation.READ),
                )
                executor = (
                    BaselineIExecutor() if method == "B0"
                    else ProposedCExecutor() if method == "C0"
                    else CachedExecutor(method, context)
                )
                policies = PolicyRepository()
                policies.add(policy)
                issuer = CapabilityIssuer(
                    issuer_id="Issuer-1", signing_key=issuer_key, state_store=store,
                    policies=policies, executor=executor, chain_id=CHAIN_ID,
                    contract_address=CONTRACT,
                )
                verifiers = [
                    CapabilityVerifier(
                        issuer_public_key=issuer_key.public_key(), state_store=store,
                        policies=policies, nonce_store=bridge, executor=executor,
                        chain_id=CHAIN_ID, contract_address=CONTRACT,
                    )
                    for bridge in bridges
                ]
                locality = workload["request_locality"]
                concurrency = int(workload["concurrency"])
                rng = random.Random(data["seed"] + config_count)

                def choose_slot(index: int) -> int:
                    if locality == "uniform":
                        return allowed_slots[rng.randrange(len(allowed_slots))]
                    if locality == "interval_hotspot":
                        interval = policy.intervals[0]
                        return interval.left + index % interval.length
                    node = max(policy.cover, key=lambda item: item.size)
                    return node.start + index % node.size

                def sample_block():
                    start = time.monotonic_ns()
                    last_error = None
                    for _ in range(5):
                        try:
                            with rpc_lock:
                                block = web3.eth.get_block("latest")
                            return block, time.monotonic_ns() - start
                        except Exception as exc:
                            last_error = exc
                            time.sleep(0.5)
                    raise RuntimeError("RPC block sample failed") from last_error

                def one_request(round_index: int, index: int, record: bool, block, chain_ns):
                    nonlocal sample_count
                    sample_id = f"S-{config_count:03d}-{round_index:02d}-{index:02d}"
                    if record and (sample_id, method) in completed_keys:
                        return
                    slot = choose_slot(index)
                    now = int(origin.timestamp()) + slot * 60
                    nonce = hashlib.sha256(
                        f"{run_id}|{config_count}|{round_index}|{index}|{'' if record else attempt_token}".encode()
                    ).digest()[:16]
                    request = AuthorizationRequest(
                        resource_id, user_id, user_public, Operation.READ, now, 30, nonce
                    )
                    match_start = time.monotonic_ns()
                    executor.evaluate(policy, now)
                    match_ns = time.monotonic_ns() - match_start
                    issue_start = time.monotonic_ns()
                    issued = issuer.issue(request)
                    issue_ns = time.monotonic_ns() - issue_start
                    verify_start = time.monotonic_ns()
                    verified = verifiers[index % 2].verify(
                        issued.capability, user_id=user_id, user_public_key=user_public,
                        operation=Operation.READ, now=now,
                    )
                    verify_ns = time.monotonic_ns() - verify_start
                    if not issued.accepted or not verified.accepted:
                        raise RuntimeError("PILOT_ONLY semantic decision failure")
                    if record:
                        sample_count += 1
                        cache_stats = executor.cache.stats() if isinstance(executor, CachedExecutor) else None
                        recorder.append(
                            {
                                "experiment_id": "R2-PILOT", "run_id": run_id,
                                "sample_id": sample_id,
                                "method": method, "backend": "Besu-QBFT+PostgreSQL",
                                "cache_mode": method in ("B1", "C1"), "policy_id": data["sample_id"],
                                "U": data["U"], "rho": data["actual_coverage"], "F": data["actual_fragmentation"],
                                "k": len(policy.intervals), "c": len(policy.cover),
                                "request_locality": locality, "concurrency": concurrency,
                                "request_type": "normal", "expected_decision": True,
                                "actual_decision": True, "rejection_code": None,
                                "cache_hit": bool(cache_stats and cache_stats.hits > 0),
                                "cache_item_count": cache_stats.entries if cache_stats else 0,
                                "match_ns": match_ns, "chain_read_ns": chain_ns,
                                "issue_ns": issue_ns, "verify_ns": verify_ns,
                                "end_to_end_ns": chain_ns + issue_ns + verify_ns,
                                "token_bytes": len(issued.capability.payload_bytes) + len(issued.capability.signature),
                                "cpu": time.process_time_ns(), "memory": process.memory_info().rss,
                                "rpc_endpoint": RPC_URL, "rpc_error": False, "database_error": False,
                                "block_number": block["number"], "block_hash": block["hash"].hex(),
                                "chain_id": CHAIN_ID, "contract_address": "0x" + CONTRACT.hex(),
                                "gasUsed": 0, "baseFeePerGas": int(block["baseFeePerGas"]),
                                "request_id": nonce.hex(), "git_commit": git_sha,
                                "config_hash": workload["config_hash"], "timestamp": int(time.time()),
                                "label": "PILOT_ONLY", "PILOT_ONLY": True,
                            }
                        )
                        completed_keys.add((sample_id, method))

                block, chain_ns = sample_block()
                for warmup in range(3):
                    with ThreadPoolExecutor(max_workers=concurrency) as pool:
                        list(pool.map(lambda i: one_request(-warmup - 1, i, False, block, chain_ns), range(concurrency)))
                for repeat in range(5):
                    with ThreadPoolExecutor(max_workers=concurrency) as pool:
                        list(pool.map(lambda i: one_request(repeat, i, True, block, chain_ns), range(concurrency)))
    finally:
        for bridge in bridges:
            bridge.close()
    sample_count = sum(1 for _ in raw_path.open(encoding="utf-8"))
    manifest = {
        "PILOT_ONLY": True, "formal_result": False, "run_id": run_id,
        "expected_configurations": 108, "completed_configurations": config_count,
        "record_count": sample_count, "warmup_rounds": 3, "measurement_rounds": 5,
        "methods": ["B0", "B1", "C0", "C1"],
    }
    (run_root / "manifest" / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    raw = run_root / "raw" / "pilot.jsonl"
    digest = hashlib.sha256(raw.read_bytes()).hexdigest()
    (run_root / "raw" / "pilot.jsonl.sha256").write_text(digest + "  pilot.jsonl\n")
    print(json.dumps({**manifest, "raw_sha256": digest}))


if __name__ == "__main__":
    main()
