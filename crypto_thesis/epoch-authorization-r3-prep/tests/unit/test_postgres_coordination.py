from __future__ import annotations

from deployment.transaction_nonce import PostgresTransactionNonceManager
from services.shared_nonce.postgres import PostgresNonceStore


class FakeCursor:
    def __init__(self, fetches):
        self.fetches = list(fetches)
        self.executions = []
        self.rowcount = 3

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, sql, params):
        self.executions.append((" ".join(sql.split()), params))

    def fetchone(self):
        return self.fetches.pop(0)


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def cursor(self):
        return self._cursor

    def close(self):
        self.closed = True


def test_postgres_nonce_store_uses_complete_unique_context():
    cursor = FakeCursor([(1,)])
    store = PostgresNonceStore(
        lambda: FakeConnection(cursor),
        chain_id=7,
        contract_address=b"\x11" * 20,
        verifier_id="v1",
    )
    assert store.consume_once("r1", 2, b"\x22" * 16)
    params = cursor.executions[0][1]
    assert params == (7, b"\x11" * 20, "r1", 2, b"\x22" * 16, "v1")


def test_postgres_nonce_cleanup_is_explicit():
    cursor = FakeCursor([])
    store = PostgresNonceStore(
        lambda: FakeConnection(cursor),
        chain_id=7,
        contract_address=b"\x11" * 20,
        verifier_id="v1",
    )
    assert store.cleanup_before_epoch("r1", 5) == 3


def test_transaction_nonce_reservation_uses_max_pending_under_lock():
    cursor = FakeCursor([(9,)])
    manager = PostgresTransactionNonceManager(lambda: FakeConnection(cursor))
    reservation = manager.reserve(
        chain_id=7,
        sender="0xABC",
        reservation_id="req-1",
        pending_nonce=12,
    )
    assert reservation.nonce == 12
    assert reservation.sender == "0xabc"
    assert any("FOR UPDATE" in sql for sql, _ in cursor.executions)


def test_transaction_nonce_lifecycle_requires_hash():
    cursor = FakeCursor([])
    cursor.rowcount = 1
    manager = PostgresTransactionNonceManager(lambda: FakeConnection(cursor))
    manager.mark("req-1", "BROADCAST", transaction_hash="0x01")
    assert "UPDATE ethereum_nonce_reservations" in cursor.executions[0][0]


def test_transaction_nonce_reconcile_never_moves_backwards():
    cursor = FakeCursor([(9,)])
    manager = PostgresTransactionNonceManager(lambda: FakeConnection(cursor))
    assert manager.reconcile(chain_id=7, sender="0xABC", pending_nonce=5) == 9
    assert any("FOR UPDATE" in sql for sql, _ in cursor.executions)
