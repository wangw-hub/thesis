import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))


@pytest.fixture
def db():
    from epoch_auth_r3.database.connection import connect
    conn = connect()
    try:
        yield conn
        conn.rollback()
    finally:
        conn.close()
