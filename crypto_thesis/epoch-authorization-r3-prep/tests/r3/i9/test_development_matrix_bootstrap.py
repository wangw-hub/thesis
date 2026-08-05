import socket

import pytest

from scripts.r3_i9.bootstrap_development_matrix import bootstrap


def test_development_bootstrap_is_atomic_and_classified(monkeypatch, tmp_path):
    monkeypatch.setattr(socket, "gethostname", lambda: "experiment-client")
    pilot = tmp_path / "i9-pilot"
    (pilot / "attempts/old/raw/run-old").mkdir(parents=True)
    (tmp_path / "i9-development/autonomous/DEV_OLD/raw/run-dev-old").mkdir(parents=True)
    root = tmp_path / "i9-development/DEV_P9A_TEST"
    result = bootstrap(root, "DEV_P9A_TEST", "a" * 40, pilot)
    assert result["oldRunIdCount"] == 2
    assert (root / "raw").is_dir()
    assert "DEVELOPMENT_ONLY" in (root / "manifests/environment.json").read_text()
    with pytest.raises(RuntimeError, match="DEVELOPMENT_ROOT_OR_ID_INVALID"):
        bootstrap(root, "DEV_P9A_TEST", "a" * 40, pilot)
