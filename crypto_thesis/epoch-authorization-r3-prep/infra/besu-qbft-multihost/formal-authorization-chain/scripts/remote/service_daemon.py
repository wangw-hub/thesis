#!/usr/bin/env python3
"""Minimal fail-closed process wrapper for formal authorization service instances."""

from __future__ import annotations

import argparse
import json
import signal
import ssl
import time
import urllib.request
from pathlib import Path

import psycopg

running = True


def stop(_signum: int, _frame: object) -> None:
    global running
    running = False


def rpc(url: str, method: str) -> object:
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": []}).encode()
    request = urllib.request.Request(url, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=5) as response:
        result = json.loads(response.read())
    if "error" in result:
        raise RuntimeError("RPC returned an error")
    return result["result"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=("issuer", "verifier"), required=True)
    parser.add_argument("--instance", required=True)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    while running:
        healthy = False
        try:
            chain_id = int(rpc(config["rpc_url"], "eth_chainId"), 16)
            rpc(config["rpc_url"], "eth_blockNumber")
            if chain_id != config["chain_id"]:
                raise RuntimeError("chain mismatch")
            if args.kind == "issuer":
                if Path(config["issuer_private_key_file"]).stat().st_size != 32:
                    raise RuntimeError("invalid issuer key file")
            else:
                password = Path(config["postgres_password_file"]).read_text().strip()
                with psycopg.connect(
                    host="127.0.0.1",
                    dbname="epoch_auth",
                    user="epoch_auth",
                    password=password,
                    connect_timeout=5,
                ) as connection:
                    connection.execute("SELECT 1")
            healthy = True
        except Exception:
            healthy = False
        print(
            json.dumps(
                {
                    "instance_id": args.instance,
                    "kind": args.kind,
                    "healthy": healthy,
                    "fail_closed": not healthy,
                    "checked_at_unix": int(time.time()),
                }
            ),
            flush=True,
        )
        time.sleep(5)


if __name__ == "__main__":
    main()
