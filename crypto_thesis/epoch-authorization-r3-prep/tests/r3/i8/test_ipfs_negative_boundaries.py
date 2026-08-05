from dataclasses import replace

import pytest

from epoch_auth_r3.storage import ObjectKind
from epoch_auth_r3.storage.ipfs import KuboRpcClient
from epoch_auth_r3.storage.ipfs.exceptions import KuboUnavailableError, ReplicaVerificationError


def test_cross_object_kind_rejected(i8_fixture):
    record = i8_fixture["gateway"].replicate(i8_fixture["header_ref"])
    bad = replace(record, object_kind=ObjectKind.BODY)
    with pytest.raises(ReplicaVerificationError):
        i8_fixture["gateway"].fetch_verified(i8_fixture["header_ref"], bad)


def test_cross_resource_digest_mapping_rejected(i8_fixture):
    record = i8_fixture["gateway"].replicate(i8_fixture["header_ref"])
    bad = replace(record, object_digest_hex="00" * 32)
    with pytest.raises(ReplicaVerificationError):
        i8_fixture["gateway"].fetch_verified(i8_fixture["header_ref"], bad)


def test_header_cid_cannot_restore_body(i8_fixture):
    record = i8_fixture["gateway"].replicate(i8_fixture["header_ref"])
    bad = replace(record, object_kind=ObjectKind.BODY,
                  object_digest_hex=i8_fixture["body_ref"].digest_hex,
                  object_size_bytes=i8_fixture["body_ref"].size_bytes)
    with pytest.raises(ReplicaVerificationError):
        i8_fixture["gateway"].fetch_verified(i8_fixture["body_ref"], bad)


def test_wrong_valid_cid_digest_rejected(i8_fixture):
    header = i8_fixture["gateway"].replicate(i8_fixture["header_ref"])
    body = i8_fixture["gateway"].replicate(i8_fixture["body_ref"])
    bad = replace(body, cid=header.cid)
    with pytest.raises(ReplicaVerificationError):
        i8_fixture["gateway"].fetch_verified(i8_fixture["body_ref"], bad)


def test_kubo_unavailable_fails_closed():
    client = KuboRpcClient("http://127.0.0.1:1", timeout_seconds=0.1)
    with pytest.raises(KuboUnavailableError):
        client.identity()


@pytest.mark.parametrize("url", ["https://ipfs.io", "http://192.168.6.133:15001", "file:///tmp/x"])
def test_public_or_nonloopback_api_forbidden(url):
    with pytest.raises(ValueError):
        KuboRpcClient(url)
