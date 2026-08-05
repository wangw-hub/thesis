import json

import pytest

from epoch_auth_r3.pilot.evidence import PilotEvidenceWriter, REQUIRED, validate_raw_run


def test_raw_evidence_complete_immutable_and_hashed(tmp_path):
    raw = tmp_path / "raw"; raw.mkdir()
    writer = PilotEvidenceWriter(raw, "a"*64)
    for name in REQUIRED:
        writer.write_once(name, "" if name.endswith(".log") or name.endswith(".jsonl") else
                          {"classification": "PILOT_ONLY"})
    assert writer.seal()["errors"] == 0
    assert validate_raw_run(writer.root) == []
    with pytest.raises(ValueError): writer.write_once("stdout.log", "overwrite")


def test_failed_run_is_evidence_not_deleted(tmp_path):
    raw = tmp_path / "raw"; raw.mkdir()
    writer = PilotEvidenceWriter(raw, "b"*64)
    for name in REQUIRED:
        writer.write_once(name, {"status": "FAILED_EXPECTED"} if name.endswith(".json") else "")
    writer.seal()
    assert json.loads((writer.root / "run-state.json").read_text())["status"] == "FAILED_EXPECTED"
