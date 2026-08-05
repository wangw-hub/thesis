from __future__ import annotations

import json
from pathlib import Path

import pytest

from experiments.multihost.generate import generate
from experiments.multihost.run import assert_environment_admitted


def test_multihost_guard_rejects_incomplete_environment():
    with pytest.raises(RuntimeError, match="four independent"):
        assert_environment_admitted(
            {
                "label": "PILOT_ONLY",
                "independent_os_instances": 1,
            }
        )


def test_multihost_guard_accepts_only_complete_attestation():
    assert_environment_admitted(
        {
            "label": "PILOT_ONLY",
            "independent_os_instances": 5,
            "role_separation_verified": True,
            "shared_nonce_verified": True,
            "transaction_nonce_verified": True,
        }
    )


def test_workloads_are_reproducible_and_never_formal(tmp_path):
    root = Path(__file__).resolve().parents[2]
    config = root / "experiments" / "multihost" / "configs" / "pilot.yml"
    first = tmp_path / "first.jsonl"
    second = tmp_path / "second.jsonl"
    assert generate(config, first) == 81
    assert generate(config, second) == 81
    assert first.read_bytes() == second.read_bytes()
    records = [json.loads(line) for line in first.read_text("utf-8").splitlines()]
    assert all(item["label"] == "PILOT_ONLY" for item in records)
    assert not any(item["formal_result"] for item in records)
