import pytest
from psycopg.errors import CheckViolation

from artifact_helpers import make_artifact


def test_key_and_body_version_constraint(db):
    with pytest.raises(CheckViolation):
        make_artifact(db, 1, body_version=1, key_version=2)
