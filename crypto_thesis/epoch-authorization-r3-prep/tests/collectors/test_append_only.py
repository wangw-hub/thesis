import json

import pytest

from experiments.formal_authorization.rerun_protocol import append_jsonl


def test_append_only_rejects_duplicate_primary_key(tmp_path):
    target = tmp_path / "raw.jsonl"
    row = {"run": "R", "request": "Q", "value": 1}
    append_jsonl(target, row, ("run", "request"))
    before = target.read_bytes()
    with pytest.raises(ValueError):
        append_jsonl(target, {**row, "value": 2}, ("run", "request"))
    assert target.read_bytes() == before
    assert json.loads(target.read_text()) == row
