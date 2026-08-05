import pytest
from psycopg.errors import UniqueViolation
from artifact_helpers import make_artifact


def test_header_resource_version_unique(db):
    make_artifact(db,1)
    with pytest.raises(UniqueViolation):
        make_artifact(db,2,header_version=1)
