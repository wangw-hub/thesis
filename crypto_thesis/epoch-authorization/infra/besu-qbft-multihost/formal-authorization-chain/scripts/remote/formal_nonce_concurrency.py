#!/usr/bin/env python3
"""Revalidate shared nonce consumption for the formal chain and contract."""

from __future__ import annotations

import concurrent.futures
import json
from pathlib import Path

import psycopg

CHAIN_ID = 2026072901
CONTRACT = bytes.fromhex("9ef44cf538d0df457ba77c556d8785e48bfc436d")
RESOURCE = "authorization-resource-001"
PASSWORD_FILE = Path("/etc/epoch-auth-formal/private/postgres-password")


def connect() -> psycopg.Connection:
    return psycopg.connect(
        host="127.0.0.1",
        dbname="epoch_auth",
        user="epoch_auth",
        password=PASSWORD_FILE.read_text().strip(),
        connect_timeout=5,
    )


def consume(epoch: int, nonce: bytes, verifier_id: str) -> bool:
    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO consumed_nonces
                    (chain_id, contract_address, resource_id, epoch, nonce, verifier_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                RETURNING 1
                """,
                (CHAIN_ID, CONTRACT, RESOURCE, epoch, nonce, verifier_id),
            )
            return cursor.fetchone() is not None


def main() -> None:
    results = []
    for size in (50, 100, 500):
        epoch = 1000 + size
        nonce = size.to_bytes(16, "big")
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(size, 64)) as pool:
            accepted = list(
                pool.map(
                    lambda index: consume(
                        epoch, nonce, "Verifier-1" if index % 2 == 0 else "Verifier-2"
                    ),
                    range(size),
                )
            )
        with connect() as connection:
            row_count = connection.execute(
                """
                SELECT count(*) FROM consumed_nonces
                WHERE chain_id=%s AND contract_address=%s AND resource_id=%s
                  AND epoch=%s AND nonce=%s
                """,
                (CHAIN_ID, CONTRACT, RESOURCE, epoch, nonce),
            ).fetchone()[0]
        item = {
            "concurrency": size,
            "successful_consumptions": sum(accepted),
            "replay_rejections": size - sum(accepted),
            "database_rows": row_count,
        }
        if item["successful_consumptions"] != 1 or row_count != 1:
            raise RuntimeError(f"nonce uniqueness failed: {item}")
        results.append(item)
    print(json.dumps({"chain_id": CHAIN_ID, "contract_address": CONTRACT.hex(), "results": results}))


if __name__ == "__main__":
    main()
