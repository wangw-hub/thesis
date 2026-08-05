from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, fields
from enum import Enum
import hashlib
from pathlib import Path
import re
from typing import Iterator

import psycopg

APPLICATION_NAME_DOMAIN = "EPOCH_AUTH_R3_I9_PG_APPLICATION_NAME_V1"
APPLICATION_NAME_PATTERN = re.compile(r"^[a-z0-9-]+$")
APPLICATION_NAME_MAX_BYTES = 63


class PilotDatabaseConnectionRoleV1(str, Enum):
    BOOTSTRAP = "bootstrap"
    CANARY = "canary"
    MIGRATION = "migration"
    FIXTURE = "fixture"
    JOB = "job"
    WORKER = "worker"
    EVIDENCE = "evidence"
    QUALITY = "quality"
    SNAPSHOT = "snapshot"
    FINALIZE = "finalize"


@dataclass(frozen=True)
class PilotApplicationNameV1:
    value: str
    role: PilotDatabaseConnectionRoleV1
    digestPrefix: str

    @classmethod
    def generate(
        cls, *, attempt_id: str, run_identity: str,
        role: PilotDatabaseConnectionRoleV1, software_commit: str,
    ) -> "PilotApplicationNameV1":
        if not isinstance(role, PilotDatabaseConnectionRoleV1):
            raise ValueError("UNKNOWN_PILOT_DATABASE_CONNECTION_ROLE")
        values = (attempt_id, run_identity, role.value, software_commit)
        if any(type(value) is not str or not value for value in values):
            raise ValueError("INVALID_APPLICATION_NAME_IDENTITY")
        encoded = b"\x00".join(
            value.encode("utf-8") for value in (APPLICATION_NAME_DOMAIN, *values)
        )
        prefix = hashlib.sha256(encoded).hexdigest()[:32]
        value = f"r3i9-{role.value}-{prefix}"
        if (
            not APPLICATION_NAME_PATTERN.fullmatch(value)
            or len(value.encode("utf-8")) > APPLICATION_NAME_MAX_BYTES
            or len(value) != len(value.encode("utf-8"))
        ):
            raise ValueError("INVALID_PILOT_APPLICATION_NAME")
        return cls(value, role, prefix)


@dataclass(frozen=True)
class PilotDatabaseConfigV1:
    schemaVersion: str
    host: str
    port: int
    database: str
    user: str
    connectTimeoutSeconds: int
    applicationName: str
    credentialSource: str
    expectedClusterName: str
    expectedServerVersionMajor: int
    sslMode: str

    def __post_init__(self) -> None:
        if self.schemaVersion != "1" or self.host != "127.0.0.1" or type(self.port) is not int or self.port != 55432:
            raise ValueError("INVALID_PILOT_DATABASE_ENDPOINT")
        if self.database != "epoch_auth_r3_i9_pilot" or self.user != "epoch_auth_r3_i9_pilot":
            raise ValueError("INVALID_PILOT_DATABASE_IDENTITY")
        if (
            not APPLICATION_NAME_PATTERN.fullmatch(self.applicationName)
            or len(self.applicationName.encode("utf-8")) > APPLICATION_NAME_MAX_BYTES
        ):
            raise ValueError("INVALID_PILOT_APPLICATION_NAME")
        if self.credentialSource not in {"external_file", "controlled_environment"}:
            raise ValueError("INVALID_CREDENTIAL_SOURCE")
        if self.expectedClusterName != "16/r3_i4" or self.expectedServerVersionMajor != 16:
            raise ValueError("INVALID_EXPECTED_CLUSTER")
        if self.sslMode != "disable" or self.connectTimeoutSeconds < 1:
            raise ValueError("INVALID_CONNECTION_POLICY")

    @classmethod
    def from_strict_dict(cls, value: dict) -> "PilotDatabaseConfigV1":
        if type(value) is not dict or set(value) != {item.name for item in fields(cls)}:
            raise ValueError("STRICT_PILOT_DATABASE_CONFIG_FIELDS")
        return cls(**value)

    def redacted_dict(self) -> dict:
        return {item.name: getattr(self, item.name) for item in fields(self)}


def frozen_pilot_database_config(application_name: str) -> PilotDatabaseConfigV1:
    return PilotDatabaseConfigV1("1", "127.0.0.1", 55432, "epoch_auth_r3_i9_pilot",
        "epoch_auth_r3_i9_pilot", 5, application_name,
        "external_file", "16/r3_i4", 16, "disable")


class PilotDatabaseConnectionFactoryV1:
    def __init__(self, config: PilotDatabaseConfigV1, password_file: Path):
        self.config = config
        self.password_file = password_file

    @contextmanager
    def connect(self) -> Iterator[psycopg.Connection]:
        password = self.password_file.read_text("utf-8").strip()
        if not password:
            raise RuntimeError("EMPTY_EXTERNAL_DATABASE_CREDENTIAL")
        conn = psycopg.connect(host=self.config.host, port=self.config.port,
            dbname=self.config.database, user=self.config.user, password=password,
            connect_timeout=self.config.connectTimeoutSeconds,
            application_name=self.config.applicationName, sslmode=self.config.sslMode)
        try:
            with conn.cursor() as cur:
                cur.execute("""SELECT current_database(), current_user,
                    inet_server_addr()::text, inet_server_port(),
                    current_setting('server_version'),
                    current_setting('application_name'),
                    char_length(current_setting('application_name')),
                    octet_length(current_setting('application_name')),
                    pg_backend_pid()""")
                database, user, host, port, version, setting, chars, octets, pid = cur.fetchone()
                cur.execute("SHOW application_name")
                shown = cur.fetchone()[0]
                cur.execute("SELECT application_name FROM pg_stat_activity WHERE pid = pg_backend_pid()")
                activity = cur.fetchone()[0]
            if database != self.config.database or user != self.config.user or int(port) != self.config.port:
                raise RuntimeError("PILOT_DATABASE_IDENTITY_MISMATCH")
            expected = self.config.applicationName
            if (
                int(str(version).split(".")[0]) != self.config.expectedServerVersionMajor
                or shown != expected or setting != expected or activity != expected
                or shown != setting or setting != activity
                or chars != len(expected)
                or octets != len(expected.encode("utf-8"))
                or octets > APPLICATION_NAME_MAX_BYTES
            ):
                raise RuntimeError("PILOT_DATABASE_IDENTITY_MISMATCH")
            self._last_attestation = {
                "showApplicationName": shown,
                "currentSettingApplicationName": setting,
                "pgStatActivityApplicationName": activity,
                "applicationNameCharacterLength": chars,
                "applicationNameByteLength": octets,
                "backendPid": pid,
            }
            yield conn
        finally:
            conn.close()

    def attest(self) -> dict:
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT current_database(), current_user,
                    inet_server_addr()::text, inet_server_port(),
                    current_setting('server_version')""")
                database, user, host, port, version = cur.fetchone()
        return {"databaseHost": host or self.config.host, "databasePort": int(port),
                "databaseName": database, "databaseUser": user, "serverVersion": version,
                "applicationName": self.config.applicationName,
                **self._last_attestation,
                "connectionAttested": True, "fallbackAttempts": 0}
