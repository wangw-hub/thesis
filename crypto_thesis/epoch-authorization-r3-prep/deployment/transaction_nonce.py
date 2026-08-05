"""Database-coordinated Ethereum transaction nonce reservations."""

from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True, slots=True)
class NonceReservation:
    """Durable reservation identity returned to one transaction producer."""

    chain_id: int
    sender: str
    nonce: int
    reservation_id: str


class PostgresTransactionNonceManager:
    """Serialize nonce allocation per chain and sender with row-level locking."""

    def __init__(self, connect: Callable[[], Any]) -> None:
        self._connect = connect

    def reserve(
        self,
        *,
        chain_id: int,
        sender: str,
        reservation_id: str,
        pending_nonce: int,
    ) -> NonceReservation:
        """Reserve max(database next nonce, RPC pending nonce) atomically."""

        if chain_id <= 0 or not sender or not reservation_id or pending_nonce < 0:
            raise ValueError("invalid transaction nonce reservation")
        with closing(self._connect()) as connection:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO ethereum_nonce_state(chain_id, sender, next_nonce)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (chain_id, sender) DO NOTHING
                        """,
                        (chain_id, sender.lower(), pending_nonce),
                    )
                    cursor.execute(
                        """
                        SELECT next_nonce FROM ethereum_nonce_state
                        WHERE chain_id = %s AND sender = %s
                        FOR UPDATE
                        """,
                        (chain_id, sender.lower()),
                    )
                    current = int(cursor.fetchone()[0])
                    nonce = max(current, pending_nonce)
                    cursor.execute(
                        """
                        UPDATE ethereum_nonce_state SET next_nonce = %s
                        WHERE chain_id = %s AND sender = %s
                        """,
                        (nonce + 1, chain_id, sender.lower()),
                    )
                    cursor.execute(
                        """
                        INSERT INTO ethereum_nonce_reservations
                            (chain_id, sender, nonce, reservation_id, status)
                        VALUES (%s, %s, %s, %s, 'RESERVED')
                        """,
                        (chain_id, sender.lower(), nonce, reservation_id),
                    )
        return NonceReservation(chain_id, sender.lower(), nonce, reservation_id)

    def mark(
        self,
        reservation_id: str,
        status: str,
        *,
        transaction_hash: str | None = None,
    ) -> None:
        """Persist the broadcast lifecycle without allocating another nonce."""

        allowed = {"BROADCAST", "CONFIRMED", "FAILED"}
        if not reservation_id or status not in allowed:
            raise ValueError("invalid reservation transition")
        if status in {"BROADCAST", "CONFIRMED"} and not transaction_hash:
            raise ValueError("broadcast and confirmed states require a transaction hash")
        with closing(self._connect()) as connection:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE ethereum_nonce_reservations
                        SET status = %s, transaction_hash = COALESCE(%s, transaction_hash)
                        WHERE reservation_id = %s
                        """,
                        (status, transaction_hash, reservation_id),
                    )
                    if cursor.rowcount != 1:
                        raise LookupError("transaction nonce reservation not found")

    def reconcile(self, *, chain_id: int, sender: str, pending_nonce: int) -> int:
        """Advance durable allocation state to at least the RPC pending nonce."""

        if chain_id <= 0 or not sender or pending_nonce < 0:
            raise ValueError("invalid transaction nonce reconciliation")
        normalized = sender.lower()
        with closing(self._connect()) as connection:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO ethereum_nonce_state(chain_id, sender, next_nonce)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (chain_id, sender) DO NOTHING
                        """,
                        (chain_id, normalized, pending_nonce),
                    )
                    cursor.execute(
                        """
                        SELECT next_nonce FROM ethereum_nonce_state
                        WHERE chain_id = %s AND sender = %s
                        FOR UPDATE
                        """,
                        (chain_id, normalized),
                    )
                    current = int(cursor.fetchone()[0])
                    reconciled = max(current, pending_nonce)
                    cursor.execute(
                        """
                        UPDATE ethereum_nonce_state SET next_nonce = %s
                        WHERE chain_id = %s AND sender = %s
                        """,
                        (reconciled, chain_id, normalized),
                    )
        return reconciled
