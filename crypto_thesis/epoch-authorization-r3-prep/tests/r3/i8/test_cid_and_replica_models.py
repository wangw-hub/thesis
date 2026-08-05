from dataclasses import replace

import pytest

from epoch_auth_r3.storage.ipfs import ReplicationStatus, VerificationStatus, parse_cid_v1
from epoch_auth_r3.storage.ipfs.exceptions import InvalidCidError, ReplicaVerificationError


@pytest.mark.parametrize("value", ["", "Qm" + "a" * 44, "../cid", "bafy", "B" + "a" * 58])
def test_invalid_cid_rejected(value):
    with pytest.raises(InvalidCidError):
        parse_cid_v1(value)


def test_real_cid_profile(i8_fixture):
    record = i8_fixture["gateway"].replicate(i8_fixture["header_ref"])
    parsed = parse_cid_v1(record.cid)
    assert (parsed.version, parsed.codec, parsed.multihash_code) == (1, 0x55, 0x12)


def test_pinned_requires_object_verification(i8_fixture):
    record = i8_fixture["gateway"].replicate(i8_fixture["body_ref"])
    with pytest.raises(ReplicaVerificationError):
        replace(record, verification_status=VerificationStatus.UNVERIFIED)


def test_pin_status_cannot_lie(i8_fixture):
    record = i8_fixture["gateway"].replicate(i8_fixture["body_ref"])
    with pytest.raises(ReplicaVerificationError):
        replace(record, pin_status=False, replication_status=ReplicationStatus.PINNED)


def test_cid_is_not_file_sha256(i8_fixture):
    record = i8_fixture["gateway"].replicate(i8_fixture["body_ref"])
    assert record.cid != i8_fixture["body_ref"].digest_hex
