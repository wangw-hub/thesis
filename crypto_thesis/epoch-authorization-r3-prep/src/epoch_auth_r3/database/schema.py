from hashlib import sha256
from pathlib import Path
from .connection import connect


def migration_root() -> Path:
    return Path(__file__).resolve().parents[3] / "migrations" / "r3_control"


def apply_migrations(connection=None) -> list[str]:
    own = connection is None
    conn = connection or connect()
    applied: list[str] = []
    try:
        for index, path in enumerate(sorted(migration_root().glob("*.sql")), start=1):
            data = path.read_bytes()
            with conn.transaction():
                metadata_exists = conn.execute(
                    "SELECT to_regclass('r3_control.schema_metadata')"
                ).fetchone()[0] is not None
                if metadata_exists:
                    exists = conn.execute(
                        """SELECT migration_name,migration_sha256
                           FROM r3_control.schema_metadata WHERE version=%s""",
                        (index,),
                    ).fetchone()
                    if exists:
                        if exists[0] != path.name or bytes(exists[1]) != sha256(data).digest():
                            raise RuntimeError(f"migration drift detected: {path.name}")
                        continue
                conn.execute(data.decode("utf-8"))
                conn.execute(
                    """INSERT INTO r3_control.schema_metadata
                       (version,migration_name,migration_sha256)
                       VALUES (%s,%s,%s) ON CONFLICT (version) DO NOTHING""",
                    (index, path.name, sha256(data).digest()),
                )
                applied.append(path.name)
        return applied
    finally:
        if own:
            conn.close()
