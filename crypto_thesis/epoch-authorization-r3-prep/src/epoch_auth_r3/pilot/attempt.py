from __future__ import annotations

import re
from dataclasses import dataclass, fields
from datetime import UTC, datetime


_ATTEMPT_ID_PATTERN = re.compile(
    r"I9_(?:(?P<stage>P9[ABCD])|REVISION_(?P<revision>[1-9][0-9]*))_"
    r"(?P<timestamp>[0-9]{8}T[0-9]{6}Z)_(?P<git>[0-9a-f]{7})"
)


@dataclass(frozen=True)
class PilotAttemptIdV1:
    family: str
    timestamp: str
    git_short_sha: str
    revision: int | None = None

    MIN_LENGTH = len("I9_P9A_20000101T000000Z_0000000")
    MAX_LENGTH = 64

    @classmethod
    def create(
        cls,
        *,
        family: str,
        created_at: datetime,
        git_sha: str,
        revision: int | None = None,
    ) -> "PilotAttemptIdV1":
        if created_at.tzinfo is None or created_at.utcoffset() != UTC.utcoffset(created_at):
            raise ValueError("INVALID_ATTEMPT_ID")
        if not re.fullmatch(r"[0-9a-f]{40}", git_sha):
            raise ValueError("INVALID_ATTEMPT_ID")
        timestamp = created_at.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")
        if family in {"P9A", "P9B", "P9C", "P9D"} and revision is None:
            value = cls(family, timestamp, git_sha[:7], None)
        elif family == "REVISION" and type(revision) is int and revision > 0:
            value = cls(family, timestamp, git_sha[:7], revision)
        else:
            raise ValueError("INVALID_ATTEMPT_ID")
        return cls.parse(value.serialize())

    @classmethod
    def parse(cls, value: str) -> "PilotAttemptIdV1":
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
        revision = int(match.group("revision")) if match.group("revision") else None
        family = match.group("stage") if match.group("stage") else "REVISION"
        parsed = cls(family, match.group("timestamp"), match.group("git"), revision)
        if parsed.serialize() != value:
            raise ValueError("INVALID_ATTEMPT_ID")
        return parsed

    @classmethod
    def validate(cls, value: str) -> "PilotAttemptIdV1":
        return cls.parse(value)

    def serialize(self) -> str:
        kind = self.family if self.family in {"P9A", "P9B", "P9C", "P9D"} else f"REVISION_{self.revision}"
        return f"I9_{kind}_{self.timestamp}_{self.git_short_sha}"


@dataclass(frozen=True)
class R3PilotAttemptIdentityV1:
    schemaVersion: int
    attemptId: str
    attemptPurpose: str
    parentAttemptId: str
    softwareCommit: str
    environmentManifestDigest: str
    createdAt: str
    status: str

    def __post_init__(self) -> None:
        if self.schemaVersion != 1:
            raise ValueError("UNSUPPORTED_ATTEMPT_SCHEMA")
        PilotAttemptIdV1.validate(self.attemptId)
        if self.parentAttemptId != "INVALIDATED_I9_ATTEMPT_0":
            raise ValueError("INVALID_PARENT_ATTEMPT")
        if len(self.softwareCommit) != 40 or len(self.environmentManifestDigest) != 64:
            raise ValueError("INVALID_ATTEMPT_DIGEST")

    @classmethod
    def from_strict_dict(cls, value: dict) -> "R3PilotAttemptIdentityV1":
        if type(value) is not dict or set(value) != {f.name for f in fields(cls)}:
            raise ValueError("STRICT_ATTEMPT_FIELDS")
        return cls(**value)
