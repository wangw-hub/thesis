from __future__ import annotations

import json
from typing import Any

import rfc8785

from epoch_auth_r3.crypto.exceptions import CryptoValidationError


def _reject_floats(value: Any) -> None:
    if isinstance(value, float):
        raise CryptoValidationError("floating point values are forbidden")
    if isinstance(value, dict):
        if not all(isinstance(k, str) for k in value):
            raise CryptoValidationError("JSON object keys must be strings")
        for item in value.values():
            _reject_floats(item)
    elif isinstance(value, list):
        for item in value:
            _reject_floats(item)


def canonicalize(value: Any) -> bytes:
    _reject_floats(value)
    try:
        return rfc8785.dumps(value)
    except Exception as exc:
        raise CryptoValidationError("JCS canonicalization failed") from exc


def parse_strict(data: str | bytes) -> Any:
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise CryptoValidationError(f"duplicate JSON field: {key}")
            result[key] = value
        return result

    def reject_constant(value):
        raise CryptoValidationError(f"non-finite JSON number: {value}")

    try:
        parsed = json.loads(
            data, object_pairs_hook=pairs, parse_constant=reject_constant
        )
    except CryptoValidationError:
        raise
    except Exception as exc:
        raise CryptoValidationError("invalid JSON") from exc
    _reject_floats(parsed)
    return parsed


def require_exact_fields(value: dict, expected: set[str]) -> None:
    if not isinstance(value, dict):
        raise CryptoValidationError("object required")
    actual = set(value)
    if actual != expected:
        raise CryptoValidationError(
            f"schema fields mismatch: missing={sorted(expected-actual)}, "
            f"unknown={sorted(actual-expected)}"
        )

