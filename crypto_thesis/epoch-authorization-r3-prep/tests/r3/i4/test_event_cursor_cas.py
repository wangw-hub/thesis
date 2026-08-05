import pytest
from epoch_auth_r3.database.event_cursor_repository import EventCursorRepository
from epoch_auth_r3.database.exceptions import CursorConflict, StaleWriteRejected


def test_cursor_stale_version_and_hash_conflict_rejected(db):
    repo=EventCursorRepository(db); repo.create("s",1,b"a"*20)
    repo.advance("s",0,0,0,0,1,0,b"a"*32)
    with pytest.raises(StaleWriteRejected): repo.advance("s",0,0,1,0,2,0,b"a"*32)
    with pytest.raises(CursorConflict): repo.advance("s",1,0,1,0,2,0,b"b"*32)
