"""PostgreSQL-backed atomic CAP nonce consumption."""

from __future__ import annotations

from contextlib import closing
from typing import Any, Callable


class PostgresNonceStore:
    """Share nonce consumption across verifier processes using one unique key."""

    def __init__(
        self,
        connect: Callable[[], Any],
        *,
        chain_id: int,
        contract_address: bytes,
        verifier_id: str,
    ) -> None:
        if chain_id <= 0:
            raise ValueError("chain_id must be positive")
        if len(contract_address) != 20:
            raise ValueError("contract_address must contain 20 bytes")
        if not verifier_id:
            raise ValueError("verifier_id must be non-empty")
        self._connect = connect
        self.chain_id = chain_id
        self.contract_address = contract_address
        self.verifier_id = verifier_id

    def consume_once(self, resource_id: str, epoch: int, nonce: bytes) -> bool:
        """Atomically insert the complete nonce key; one caller can succeed."""

        if not resource_id or epoch < 0 or len(nonce) != 16:
            raise ValueError("invalid nonce key")
        sql = """
            INSERT INTO consumed_nonces
                (chain_id, contract_address, resource_id, epoch, nonce, verifier_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            RETURNING 1
        """
        with closing(self._connect()) as connection:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        sql,
                        (
                            self.chain_id,
                            self.contract_address,
                            resource_id,
                            epoch,
                            nonce,
                            self.verifier_id,
                        ),
                    )
                    return cursor.fetchone() is not None

    def cleanup_before_epoch(self, resource_id: str, minimum_epoch: int) -> int:
        """Delete obsolete rows only after the caller freezes retention policy."""

        if minimum_epoch < 0:
            raise ValueError("minimum_epoch must be non-negative")
        sql = """
            DELETE FROM consumed_nonces
            WHERE chain_id = %s AND contract_address = %s
              AND resource_id = %s AND epoch < %s
        """
        with closing(self._connect()) as connection:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        sql,
                        (
                            self.chain_id,
                            self.contract_address,
                            resource_id,
                            minimum_epoch,
                        ),
                    )
                    return cursor.rowcount
