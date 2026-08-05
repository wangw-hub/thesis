from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from epoch_auth.nonce_store import InMemoryNonceStore


def test_nonce_scope_and_serial_replay():
    store = InMemoryNonceStore()
    nonce = b"n" * 16
    assert store.consume_once("r", 1, nonce)
    assert not store.consume_once("r", 1, nonce)
    assert store.consume_once("r", 2, nonce)
    assert store.consume_once("r2", 1, nonce)


def test_nonce_consumption_is_atomic():
    store = InMemoryNonceStore()
    with ThreadPoolExecutor(max_workers=16) as pool:
        results = list(
            pool.map(lambda _: store.consume_once("r", 1, b"n" * 16), range(100))
        )
    assert sum(results) == 1
