from __future__ import annotations

import time
from datetime import UTC, datetime, timedelta

from time_policy.compiler import compile_policy
from time_policy.models import Interval

from experiments.formal_authorization.rerun_protocol import (
    aggregate_run,
    generate_slots,
    measure_batch,
    paired_bootstrap,
    sequence_sha256,
)


def policy():
    return compile_policy(
        [Interval(0, 64), Interval(128, 160), Interval(224, 256)],
        time_origin=datetime(2026, 7, 29, tzinfo=UTC),
        delta=timedelta(minutes=1),
        domain_size=256,
    )


def test_localities_are_reproducible_and_distinct():
    sequences = {
        name: generate_slots(policy(), name, 2000, 17)
        for name in ("UNIFORM", "INTERVAL_HOTSPOT", "NODE_HOTSPOT")
    }
    assert sequences["UNIFORM"] == generate_slots(policy(), "UNIFORM", 2000, 17)
    assert generate_slots(policy(), "UNIFORM", 2000, 18) != sequences["UNIFORM"]
    assert len({sequence_sha256(value) for value in sequences.values()}) == 3
    assert all(slot in set(range(0, 64)) | set(range(128, 160)) | set(range(224, 256))
               for sequence in sequences.values() for slot in sequence)


def test_batch_throughput_uses_real_window_and_classifies_failures():
    def task(ok):
        time.sleep(0.01)
        return ok
    batch, results = measure_batch("B", [lambda: task(True), lambda: task(False)], 2)
    assert results == [True, False]
    assert batch.completed_count == 2
    assert batch.successful_count == 1
    assert batch.failed_count == 1
    assert batch.duration_ns > 0
    assert batch.throughput_completed_rps > batch.throughput_success_rps > 0


def test_run_aggregation_and_paired_bootstrap():
    rows = [
        {"method": "B0", "workload_id": "W1", "seed": 1, "repetition": 0,
         "end_to_end_ns": value, "match_ns": 10, "chain_read_ns": 20,
         "cache_hit": False, "success": True}
        for value in (100, 200, 300)
    ]
    batch, _ = measure_batch("B", [lambda: True], 1)
    result = aggregate_run(rows, batch)
    assert result["run_median_end_to_end_ns"] == 200
    bootstrap = paired_bootstrap([1, 2, 3], [2, 3, 4], resamples=100, seed=1)
    assert bootstrap["mean_difference"] == -1
    assert bootstrap["n_runs"] == 3

