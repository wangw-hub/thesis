from dataclasses import dataclass
import os
import psycopg


@dataclass(frozen=True)
class DatabaseConfig:
    host: str = "127.0.0.1"
    port: int = 65432
    dbname: str = "epoch_auth_r3_i4_test"
    user: str = "epoch_auth_r3_i4_test"
    passfile: str | None = None

    @classmethod
    def from_environment(cls) -> "DatabaseConfig":
        host = os.environ.get("R3_I4_DB_HOST", "127.0.0.1")
        if host not in {"127.0.0.1", "localhost"}:
            raise ValueError("I4 database must use loopback")
        return cls(
            host=host,
            port=int(os.environ.get("R3_I4_DB_PORT", "65432")),
            dbname=os.environ.get("R3_I4_DB_NAME", "epoch_auth_r3_i4_test"),
            user=os.environ.get("R3_I4_DB_USER", "epoch_auth_r3_i4_test"),
            passfile=os.environ.get("R3_I4_PGPASSFILE"),
        )


def connect(config: DatabaseConfig | None = None, *, autocommit: bool = False):
    cfg = config or DatabaseConfig.from_environment()
    if not cfg.passfile:
        raise ValueError("external passfile required")
    return psycopg.connect(
        host=cfg.host, port=cfg.port, dbname=cfg.dbname, user=cfg.user,
        passfile=cfg.passfile, connect_timeout=5, autocommit=autocommit,
        application_name="epoch_auth_r3_i4_test",
    )
