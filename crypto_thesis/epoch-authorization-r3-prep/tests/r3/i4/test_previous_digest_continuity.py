import pytest
from psycopg.errors import CheckViolation
from artifact_helpers import make_artifact


def test_previous_digest_must_equal_prior_header(db):
    _,_,_,_,d1,_=make_artifact(db,1)
    make_artifact(db,2,header_version=2,previous=d1)
    with pytest.raises(CheckViolation):
        make_artifact(db,3,header_version=3,previous=b"x"*32)
