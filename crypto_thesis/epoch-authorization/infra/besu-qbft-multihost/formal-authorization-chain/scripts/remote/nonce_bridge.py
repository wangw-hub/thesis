#!/usr/bin/env python3
"""JSON-lines bridge to the local PostgreSQL nonce store for PILOT_ONLY."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import psycopg

PASSWORD = Path("/etc/epoch-auth-formal/private/postgres-password")
CHAIN_ID = 2026072901
CONTRACT = bytes.fromhex("9ef44cf538d0df457ba77c556d8785e48bfc436d")


def main() -> None:
    connection = None
    for line in sys.stdin:
        try:
            request = json.loads(line)
            if connection is None or connection.closed:
                connection = psycopg.connect(
                    host="127.0.0.1",
                    dbname="epoch_auth",
                    user="epoch_auth",
                    password=PASSWORD.read_text().strip(),
                    connect_timeout=5,
                    autocommit=True,
                )
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO consumed_nonces
                        (chain_id, contract_address, resource_id, epoch, nonce, verifier_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING RETURNING 1
                    """,
                    (
                        CHAIN_ID,
                        CONTRACT,
                        request["resource_id"],
                        request["epoch"],
                        bytes.fromhex(request["nonce"]),
                        request["verifier_id"],
                    ),
                )
                accepted = cursor.fetchone() is not None
            response = {"id": request["id"], "accepted": accepted}
        except Exception:
            if connection is not None:
                connection.close()
                connection = None
            response = {"id": request.get("id") if "request" in locals() else None, "error": "database_unavailable"}
        print(json.dumps(response), flush=True)


if __name__ == "__main__":
    main()
