from epoch_auth_r3.database.event_cursor_repository import EventCursorRepository


def test_cursor_advances_contiguously(db):
    repo=EventCursorRepository(db); repo.create("s",1,b"a"*20)
    assert repo.advance("s",0,0,0,0,1,0,b"h"*32) == 1
