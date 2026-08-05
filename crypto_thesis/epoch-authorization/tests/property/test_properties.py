from __future__ import annotations

from datetime import UTC, datetime, timedelta

from hypothesis import given, settings, strategies as st
from time_policy.compiler import compile_policy
from time_policy.models import Interval

from epoch_auth.baseline_i import BaselineIExecutor
from epoch_auth.models import CapabilityPayload, Operation
from epoch_auth.proposed_c import ProposedCExecutor
from epoch_auth.serialization import decode_capability, encode_capability


@settings(max_examples=500)
@given(
    epoch=st.integers(min_value=0, max_value=(1 << 64) - 1),
    nonce=st.binary(min_size=16, max_size=16),
)
def test_cap1_round_trip_property(epoch, nonce):
    payload = CapabilityPayload(
        1,
        "issuer",
        "resource",
        b"d" * 32,
        epoch,
        b"k" * 32,
        Operation.READ,
        10,
        20,
        nonce,
        10,
    )
    assert decode_capability(encode_capability(payload)) == payload


@settings(max_examples=1000)
@given(
    intervals=st.lists(
        st.tuples(st.integers(0, 63), st.integers(1, 64)),
        min_size=1,
        max_size=20,
    ),
    slot=st.integers(0, 63),
)
def test_baseline_and_proposed_semantics(intervals, slot):
    valid = [Interval(left, right) for left, right in intervals if left < right]
    if not valid:
        valid = [Interval(0, 1)]
    origin = datetime(2026, 1, 1, tzinfo=UTC)
    policy = compile_policy(
        valid, time_origin=origin, delta=timedelta(seconds=1), domain_size=64
    )
    timestamp = int(origin.timestamp()) + slot
    baseline = BaselineIExecutor().evaluate(policy, timestamp)
    proposed = ProposedCExecutor().evaluate(policy, timestamp)
    assert baseline.allowed == proposed.allowed
    assert baseline.window_end == proposed.window_end
