from dataclasses import dataclass

from epoch_auth_r3.revocation.guard import AccessMaterialReleaseGuard, ReleaseDecision


@dataclass
class S:
    policy_digest: bytes
    epoch: int
    state_version: int


@dataclass
class C:
    authorization: S
    header: S


def test_matching_context_allows():
    state = S(b"a", 2, 3)
    assert AccessMaterialReleaseGuard().evaluate(C(state, state), header_object_valid=True) == ReleaseDecision.ALLOW


def test_stale_header_is_pending():
    assert AccessMaterialReleaseGuard().evaluate(
        C(S(b"a", 2, 3), S(b"a", 1, 2)), header_object_valid=True
    ) == ReleaseDecision.HEADER_UPDATE_PENDING


def test_invalid_object_fails_closed():
    state = S(b"a", 2, 3)
    assert AccessMaterialReleaseGuard().evaluate(C(state, state), header_object_valid=False) == ReleaseDecision.UNKNOWN
