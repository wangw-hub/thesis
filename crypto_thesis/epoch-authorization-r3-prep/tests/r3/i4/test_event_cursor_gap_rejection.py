import pytest
from epoch_auth_r3.database.event_cursor_repository import EventCursorRepository
from epoch_auth_r3.database.exceptions import CursorConflict


def test_cursor_gap_and_rollback_rejected(db):
    repo=EventCursorRepository(db); repo.create("s",1,b"a"*20)
    with pytest.raises(CursorConflict): repo.advance("s",0,0,0,0,2,0,b"h"*32)
    with pytest.raises(CursorConflict): repo.advance("s",0,0,0,0,-1,0,b"h"*32)
    with pytest.raises(CursorConflict): repo.advance("s",0,0,0,2,0,1,b"h"*32)
