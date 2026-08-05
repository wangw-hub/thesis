"""Smoke tests for deterministic workload generation."""

import json
from pathlib import Path

from experiments.generate import generate_from_config, generate_policy
from time_policy.models import Interval
from time_policy.normalize import normalize


def test_generated_raw_policy_preserves_semantic_policy() -> None:
    case = generate_policy(
        sample_id="test",
        group="TEST",
        seed=20260727,
        domain_size=100,
        coverage=0.2,
        fragmentation=0.5,
        redundancy=4,
        config_hash="abc",
    )
    raw = tuple(Interval(*bounds) for bounds in case["raw_policy"])
    semantic = tuple(
        Interval(*bounds) for bounds in case["normalized_policy"]
    )
    assert normalize(raw, domain_size=100) == semantic


def test_generation_is_reproducible_for_fixed_seed() -> None:
    arguments = {
        "sample_id": "test",
        "group": "TEST",
        "seed": 20260727,
        "domain_size": 100,
        "coverage": 0.2,
        "fragmentation": 0.5,
        "redundancy": 2,
        "config_hash": "abc",
    }
    first = generate_policy(**arguments)
    second = generate_policy(**arguments)
    assert first == second


def test_power_two_supplement_cases_are_full_domain(tmp_path: Path) -> None:
    config = tmp_path / "supplement.yaml"
    config.write_text(
        """
groups:
  - name: E1-C
    seeds: [1]
    domain_sizes: [8]
    cases: [p2_full]
  - name: E1-C
    seeds: [1]
    domain_sizes: [7]
    cases: [np2_full]
""".strip(),
        encoding="utf-8",
    )
    output = tmp_path / "samples.jsonl"
    assert generate_from_config(config, output) == 2
    samples = [
        json.loads(line)
        for line in output.read_text(encoding="utf-8").splitlines()
    ]
    assert [(item["case_type"], item["U"]) for item in samples] == [
        ("p2_full", 8),
        ("np2_full", 7),
    ]
    assert all(
        item["normalized_policy"] == [[0, item["U"]]] for item in samples
    )
