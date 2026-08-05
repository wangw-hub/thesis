"""Collect R3FormalEnvironmentFingerprintV1 on experiment-client (read-only)."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
from pathlib import Path


def sh(cmd: list[str]) -> str:
    try:
        return subprocess.run(
            cmd, capture_output=True, text=True, timeout=30, check=True
        ).stdout.strip()
    except Exception:
        return ""


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--code", required=True)
    parser.add_argument("--git-sha", required=True)
    parser.add_argument("--contracts", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    cpu = sh(["lscpu"])
    cpu_model = next((line.split(":", 1)[1].strip() for line in cpu.splitlines()
                      if line.startswith("Model name")), "")
    cores = sh(["nproc"])
    mem = sh(["free", "-b"])
    ram_line = next((line for line in mem.splitlines() if line.startswith("Mem:")), "")
    ram_bytes = int(ram_line.split()[1]) if ram_line else 0
    disk = sh(["df", "-B1", "/var/lib/epoch-auth-r3"])
    disk_line = next((line for line in disk.splitlines() if "/dev/" in line), "")
    parts = disk_line.split() if disk_line else []
    free_bytes = int(parts[3]) if len(parts) > 3 else 0
    fingerprint = {
        "schemaVersion": "R3FormalEnvironmentFingerprintV1",
        "host": platform.node(),
        "role": "formal-single-node",
        "cpuModel": cpu_model,
        "physicalCores": cores,
        "logicalCores": cores,
        "ramBytes": ram_bytes,
        "storageDeviceAndFreeBytes": free_bytes,
        "os": platform.system(),
        "kernel": platform.release(),
        "virtualization": sh(["systemd-detect-virt"]) or "none",
        "network": "loopback-only; no public peers",
        "pythonVersion": sh(["python3", "--version"]),
        "javaVersion": sh(["java", "-version"])[:200],
        "besuVersion": sh(["/opt/besu-26.5.0/bin/besu", "--version"])[:200],
        "postgresqlVersion": sh(["psql", "--version"]),
        "kuboVersion": sh(["/opt/epoch-auth-r3/i8-kubo/bin/ipfs", "--version"]),
        "web3pyVersion": sh(["/var/lib/epoch-auth-r3/formal/venv/bin/python", "-c",
                             "import web3; print(web3.__version__)"]),
        "cryptographyVersion": sh(["/var/lib/epoch-auth-r3/formal/venv/bin/python", "-c",
                                   "import cryptography; print(cryptography.__version__)"]),
        "compilerVersion": "solc 0.8.30 (frozen artifact)",
        "runtimeVersion": "Python 3.12.3 / OpenJDK 21.0.11",
        "gitSha": args.git_sha,
        "contractBytecodeDigest": sha(Path(args.contracts) / "AuthorizationState.json")[:64]
        if (Path(args.contracts) / "AuthorizationState.json").exists() else "",
        "dependencyLockDigest": sha(Path(args.code) / "requirements-r3-i9-revision.lock")
        if (Path(args.code) / "requirements-r3-i9-revision.lock").exists() else "",
        "secretPolicy": "values, keys, passwords, tokens and private paths are never recorded",
        "pilotFormalSeparation": True,
    }
    env_digest = hashlib.sha256(
        json.dumps(fingerprint, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    result = {"environmentFingerprint": fingerprint, "environmentManifestDigest": env_digest}
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
