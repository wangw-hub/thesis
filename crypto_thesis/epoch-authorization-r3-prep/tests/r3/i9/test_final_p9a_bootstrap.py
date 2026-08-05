import json
import socket

import pytest

from scripts.r3_i9.bootstrap_final_p9a import CLASSIFICATION, bootstrap


def test_final_p9a_bootstrap_freezes_all_old_identity_namespaces(monkeypatch, tmp_path):
    monkeypatch.setattr(socket, "gethostname", lambda: "experiment-client")
    pilot = tmp_path / "i9-pilot"
    (pilot / "attempts/old/raw/pilot-old").mkdir(parents=True)
    (tmp_path / "i9-development/autonomous/dev/raw/dev-old").mkdir(parents=True)
    result = bootstrap(pilot, "a" * 40, "b" * 64)
    assert result["oldRunIdCount"] == 2
    root = pilot / "attempts" / result["attemptId"]
    assert json.loads((root / "manifests/old-run-ids.json").read_text()) == ["dev-old", "pilot-old"]
    manifest = json.loads((root / "manifests/attempt-bootstrap-manifest.json").read_text())
    assert manifest["plannedRuns"] == 8 and manifest["classification"] == CLASSIFICATION


def test_final_p9a_bootstrap_is_remote_only(monkeypatch, tmp_path):
    monkeypatch.setattr(socket, "gethostname", lambda: "wrong-host")
    with pytest.raises(RuntimeError, match="REMOTE_EXECUTION_REQUIRED"):
        bootstrap(tmp_path / "i9-pilot", "a" * 40, "b" * 64)
