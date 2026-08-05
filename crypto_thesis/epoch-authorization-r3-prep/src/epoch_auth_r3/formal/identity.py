from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, fields
from datetime import UTC, datetime


_ATTEMPT_ID_PATTERN = re.compile(
    r"FORMAL_(?P<timestamp>[0-9]{8}T[0-9]{6}Z)_(?P<git>[0-9a-f]{7})"
)

RUN_ID_DOMAIN = b"EPOCH_AUTH_R3_FORMAL_RUN_V1\x00"
ATTEMPT_RUN_DOMAIN = b"EPOCH_AUTH_R3_FORMAL_RUN_ATTEMPT_V1\x00"


@dataclass(frozen=True)
class FormalAttemptIdV1:
    family: str
    timestamp: str
    git_short_sha: str

    MIN_LENGTH = len("FORMAL_20000101T000000Z_0000000")
    MAX_LENGTH = 64

    @classmethod
    def create(cls, *, created_at: datetime, git_sha: str) -> "FormalAttemptIdV1":
        if created_at.tzinfo is None or created_at.utcoffset() != UTC.utcoffset(created_at):
            raise ValueError("INVALID_ATTEMPT_ID")
        if not re.fullmatch(r"[0-9a-f]{40}", git_sha):
            raise ValueError("INVALID_ATTEMPT_ID")
        timestamp = created_at.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")
        return cls("FORMAL", timestamp, git_sha[:7])

    @classmethod
    def parse(cls, value: str) -> "FormalAttemptIdV1":
        if type(value) is not str or not value.isascii():
            raise ValueError("INVALID_ATTEMPT_ID")
        if not cls.MIN_LENGTH <= len(value) <= cls.MAX_LENGTH:
            raise ValueError("INVALID_ATTEMPT_ID")
        match = _ATTEMPT_ID_PATTERN.fullmatch(value)
        if match is None:
            raise ValueError("INVALID_ATTEMPT_ID")
        try:
            datetime.strptime(match.group("timestamp"), "%Y%m%dT%H%M%SZ")
        except ValueError as exc:
            raise ValueError("INVALID_ATTEMPT_ID") from exc
        parsed = cls("FORMAL", match.group("timestamp"), match.group("git"))
        if parsed.serialize() != value:
            raise ValueError("INVALID_ATTEMPT_ID")
        return parsed

    @classmethod
    def validate(cls, value: str) -> "FormalAttemptIdV1":
        return cls.parse(value)

    def serialize(self) -> str:
        return f"FORMAL_{self.timestamp}_{self.git_short_sha}"


def formal_run_id(attempt_id: str, config_digest: str) -> str:
    """Attempt-scoped formal RUN identity (new domain, disjoint from Pilot)."""
    FormalAttemptIdV1.validate(attempt_id)
    if not re.fullmatch(r"[0-9a-f]{64}", config_digest):
        raise ValueError("INVALID_CONFIG_DIGEST")
    material = RUN_ID_DOMAIN + attempt_id.encode("ascii") + bytes.fromhex(config_digest)
    return hashlib.sha256(material).hexdigest()


def formal_resource_id(attempt_id: str, run_id: str) -> bytes:
    material = (
        b"EPOCH_AUTH_R3_FORMAL_RESOURCE_V1\x00"
        + attempt_id.encode("ascii")
        + run_id.encode("ascii")
    )
    return hashlib.sha256(material).digest()


def strict_formal_identity_dict() -> dict:
    return {
        "schemaVersion": 1,
        "identityDomain": "EPOCH_AUTH_R3_FORMAL_RUN_V1",
        "disjointFrom": ["PILOT", "I9", "RC2", "REVISION_7", "REVISION_8"],
    }
