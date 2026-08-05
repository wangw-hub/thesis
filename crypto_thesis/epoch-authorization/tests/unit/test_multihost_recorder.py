from __future__ import annotations

import pytest

from experiments.multihost.recorder import AppendOnlyRecorder, REQUIRED_FIELDS


def complete_record():
    record = {field: 0 for field in REQUIRED_FIELDS}
    record.update(
        {
            "experiment_id": "E4",
            "run_id": "run-1",
            "sample_id": "sample-1",
            "method": "B0",
            "label": "PILOT_ONLY",
        }
    )
    return record


def test_recorder_is_append_only_and_resumable(tmp_path):
    path = tmp_path / "raw.jsonl"
    recorder = AppendOnlyRecorder(path)
    assert recorder.append(complete_record())
    assert not recorder.append(complete_record())
    assert not AppendOnlyRecorder(path).append(complete_record())
    assert len(path.read_text("utf-8").splitlines()) == 1


def test_recorder_rejects_incomplete_or_formal_rows(tmp_path):
    recorder = AppendOnlyRecorder(tmp_path / "raw.jsonl")
    with pytest.raises(ValueError, match="missing"):
        recorder.append({"run_id": "x"})
    record = complete_record()
    record["label"] = "FORMAL"
    with pytest.raises(ValueError, match="PILOT_ONLY"):
        recorder.append(record)
