from types import SimpleNamespace

from epoch_auth_r3.blockchain import (
    CompositeConsistencyClass,
    CompositeStateGateway,
    MaterialReleaseEligibility,
)
from epoch_auth_r3.revocation.guard import AccessMaterialReleaseGuard, ReleaseDecision


def _auth(*, epoch=2, state_version=2, policy=b"p" * 32, present=True):
    owner = "0x" + ("1" * 40) if present else "0x" + ("0" * 40)
    return (owner, policy, epoch, 1, 1, state_version, 12)


def _header(*, epoch=1, state_version=1, policy=b"p" * 32, present=True):
    return (
        b"o" * 32, b"r" * 32, policy, epoch, state_version, 1, 1, 1, 0,
        b"0" * 32, b"h" * 32, b"h" * 32, b"b" * 32,
        "0x" + "2" * 40, 11, present,
    )


class _Call:
    def __init__(self, value): self.value = value
    def call(self, *, block_identifier): return self.value


class _Functions:
    def __init__(self, value, name): self.value, self.name = value, name
    def getResource(self, _): return _Call(self.value)
    def getCurrentAnchor(self, _): return _Call(self.value)


class _Contract:
    def __init__(self, value, name, address):
        self.functions = _Functions(value, name)
        self.address = address


class _Eth:
    chain_id = 2026073005
    def get_block(self, _): return {"number": 12, "hash": bytes.fromhex("ab" * 32)}


def _read(auth, header):
    w3 = SimpleNamespace(eth=_Eth())
    return CompositeStateGateway(
        w3,
        _Contract(auth, "auth", "0x" + "3" * 40),
        _Contract(header, "header", "0x" + "4" * 40),
    ).read_v2(b"r" * 32, block_identifier=12)


def test_composite_state_both_present_but_mismatched():
    result = _read(_auth(), _header())
    assert result.authorization_present and result.header_present
    assert result.authorization_state.epoch == 2
    assert result.header_state.epoch == 1


def test_authorization_ahead_not_missing():
    result = _read(_auth(), _header())
    assert result.consistency_class is CompositeConsistencyClass.AUTHORIZATION_AHEAD_OF_HEADER


def test_authorization_ahead_header_pending():
    result = _read(_auth(), _header())
    assert result.reason_code == "HEADER_UPDATE_PENDING"


def test_header_update_pending_denies_release():
    result = _read(_auth(), _header())
    assert result.material_release_eligibility is MaterialReleaseEligibility.DENIED
    assert AccessMaterialReleaseGuard().evaluate(result, header_object_valid=True) is ReleaseDecision.HEADER_UPDATE_PENDING


def test_old_header_not_usable_during_pending():
    result = _read(_auth(), _header())
    assert AccessMaterialReleaseGuard().evaluate(result, header_object_valid=True) is not ReleaseDecision.ALLOW


def test_composite_state_fixed_block():
    result = _read(_auth(), _header())
    assert result.block_number == 12
    assert result.block_hash == "ab" * 32


def test_missing_authorization_distinct():
    result = _read(_auth(present=False), _header())
    assert result.consistency_class is CompositeConsistencyClass.HEADER_ONLY


def test_missing_header_distinct():
    result = _read(_auth(), _header(present=False))
    assert result.consistency_class is CompositeConsistencyClass.AUTHORIZATION_ONLY


def test_digest_conflict_distinct():
    result = _read(_auth(policy=b"a" * 32), _header(policy=b"b" * 32, epoch=2, state_version=2))
    assert result.consistency_class is CompositeConsistencyClass.DIGEST_CONFLICT
