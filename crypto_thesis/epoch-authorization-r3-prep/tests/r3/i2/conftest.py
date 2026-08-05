import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))


@pytest.fixture
def store(tmp_path):
    from epoch_auth_r3.storage import LocalObjectStore

    return LocalObjectStore(tmp_path / "store")
