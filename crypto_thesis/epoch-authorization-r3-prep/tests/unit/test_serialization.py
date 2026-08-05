from __future__ import annotations

import pytest

from epoch_auth.errors import TokenDecodeError
from epoch_auth.models import CapabilityPayload, ChainBinding, MatchedNode, Operation
from epoch_auth.serialization import decode_capability, encode_capability


def payload(node=False):
    return CapabilityPayload(
        1,
        "as-1",
        "resource-1",
        b"a" * 32,
        7,
        b"b" * 32,
        Operation.READ,
        100,
        200,
        b"c" * 16,
        100,
        matched_node=MatchedNode(0, 8) if node else None,
        cover_version=b"d" * 32 if node else None,
    )


@pytest.mark.parametrize("with_node", [False, True])
def test_cap1_round_trip(with_node):
    original = payload(with_node)
    encoded = encode_capability(original)
    assert encoded.startswith(b"CAP1")
    assert decode_capability(encoded) == original


@pytest.mark.parametrize(
    "mutator",
    [
        lambda data: b"BAD!" + data[4:],
        lambda data: data[:-1],
        lambda data: data + b"\x00",
        lambda data: data[:4] + b"\x02" + data[5:],
        lambda data: data[:5] + b"\x02" + data[6:],
    ],
)
def test_rejects_malformed_cap1(mutator):
    with pytest.raises(TokenDecodeError):
        decode_capability(mutator(encode_capability(payload(True))))


def test_cap2_round_trip_and_context_fields():
    original = CapabilityPayload(
        2,
        "as-1",
        "resource-1",
        b"a" * 32,
        7,
        b"b" * 32,
        Operation.READ,
        100,
        200,
        b"c" * 16,
        100,
        chain_binding=ChainBinding(20260728, b"\x12" * 20, 9, 4),
    )
    encoded = encode_capability(original)
    assert encoded.startswith(b"CAP2")
    assert decode_capability(encoded) == original
