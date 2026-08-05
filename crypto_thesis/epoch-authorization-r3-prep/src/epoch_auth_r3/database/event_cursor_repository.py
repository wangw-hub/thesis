from .exceptions import CursorConflict, StaleWriteRejected


class EventCursorRepository:
    def __init__(self, conn):
        self.conn = conn

    def create(self, source_id, chain_id, contract, next_block=0, next_log=0):
        with self.conn.transaction():
            self.conn.execute(
                """INSERT INTO r3_control.revocation_event_cursor
                   (source_id,chain_id,authorization_contract,next_block_number,next_log_index)
                   VALUES (%s,%s,%s,%s,%s) ON CONFLICT (source_id) DO NOTHING""",
                (source_id,chain_id,contract,next_block,next_log),
            )

    def advance(self, source_id, version, expected_block, expected_log,
                next_block, next_log, processed_block, block_hash):
        if (next_block,next_log) < (expected_block,expected_log):
            raise CursorConflict("cursor rollback")
        contiguous = (
            (next_block == expected_block and next_log == expected_log + 1)
            or (next_block == expected_block + 1 and next_log == 0)
        )
        if not contiguous:
            raise CursorConflict("cursor gap")
        with self.conn.transaction():
            existing = self.conn.execute(
                """SELECT next_block_number,next_log_index,last_processed_block_number,
                          last_processed_block_hash,version
                   FROM r3_control.revocation_event_cursor WHERE source_id=%s FOR UPDATE""",
                (source_id,),
            ).fetchone()
            if existing[4] != version:
                raise StaleWriteRejected("cursor CAS rejected")
            if existing[0:2] != (expected_block,expected_log):
                raise CursorConflict("unexpected cursor position")
            if existing[2] == processed_block and existing[3] not in (None,block_hash):
                raise CursorConflict("block hash conflict")
            row = self.conn.execute(
                """UPDATE r3_control.revocation_event_cursor
                   SET next_block_number=%s,next_log_index=%s,
                       last_processed_block_number=%s,last_processed_block_hash=%s,
                       version=version+1,updated_at=clock_timestamp()
                   WHERE source_id=%s AND version=%s
                   RETURNING version""",
                (next_block,next_log,processed_block,block_hash,source_id,version),
            ).fetchone()
            if not row:
                raise StaleWriteRejected("cursor CAS rejected")
            return row[0]
