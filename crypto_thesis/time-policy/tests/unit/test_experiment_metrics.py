"""Tests for fair and reproducible E1 query construction."""

from experiments.metrics import build_queries
from time_policy.models import Interval


def test_queries_are_balanced_when_both_classes_exist() -> None:
    queries, hit_rate = build_queries(
        (Interval(10, 20),), domain_size=1000, seed=20260727
    )
    assert len(queries) == 4096
    assert hit_rate == 0.5
    assert {10, 19, 9, 20, 0, 999}.issubset(set(queries))


def test_full_domain_records_unavoidable_all_hit_workload() -> None:
    queries, hit_rate = build_queries(
        (Interval(0, 16),), domain_size=16, seed=20260727
    )
    assert queries
    assert hit_rate == 1.0
