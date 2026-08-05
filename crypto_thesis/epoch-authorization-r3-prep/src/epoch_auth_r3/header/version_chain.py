from enum import IntEnum

from .digest import header_core_digest
from .exceptions import HeaderErrorCode, HeaderValidationError
from .models import SignedVersionedHeaderV1



class HeaderUpdateKind(IntEnum):
    INITIAL = 0
    HEADER_ONLY = 1
    BODY_ROTATION = 2


def classify_update(previous: SignedVersionedHeaderV1 | None,
                    current: SignedVersionedHeaderV1) -> HeaderUpdateKind:
    core = current.core
    if previous is None:
        if (core.header_version, core.body_version, core.key_version) != (1, 1, 1):
            raise HeaderValidationError(HeaderErrorCode.KEY_BODY_VERSION_MISMATCH)
        if core.previous_header_digest is not None:
            raise HeaderValidationError(HeaderErrorCode.PREVIOUS_HEADER_DIGEST_MISMATCH)
        return HeaderUpdateKind.INITIAL

    prior = previous.core
    if core.header_version != prior.header_version + 1:
        raise HeaderValidationError(HeaderErrorCode.HEADER_VERSION_MISMATCH)
    if core.previous_header_digest != header_core_digest(prior).hex():
        raise HeaderValidationError(HeaderErrorCode.PREVIOUS_HEADER_DIGEST_MISMATCH)
    if core.key_version != core.body_version:
        raise HeaderValidationError(HeaderErrorCode.KEY_BODY_VERSION_MISMATCH)

    if core.body_version == prior.body_version and core.key_version == prior.key_version:
        if core.body_digest != prior.body_digest or core.body_reference != prior.body_reference:
            raise HeaderValidationError(HeaderErrorCode.BODY_DIGEST_TRANSITION_INVALID)
        return HeaderUpdateKind.HEADER_ONLY

    if (core.body_version == prior.body_version + 1
            and core.key_version == prior.key_version + 1):
        if core.body_digest == prior.body_digest:
            raise HeaderValidationError(HeaderErrorCode.BODY_DIGEST_TRANSITION_INVALID)
        return HeaderUpdateKind.BODY_ROTATION
    raise HeaderValidationError(HeaderErrorCode.KEY_BODY_VERSION_MISMATCH)


def validate_version_chain(headers: list[SignedVersionedHeaderV1]) -> None:
    if not headers:
        raise HeaderValidationError(HeaderErrorCode.PREVIOUS_HEADER_DIGEST_MISMATCH)
    classify_update(None, headers[0])
    for previous, current in zip(headers, headers[1:]):
        classify_update(previous, current)
