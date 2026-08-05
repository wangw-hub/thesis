import copy
import pytest
from epoch_auth_r3.crypto.hpke_provider import PyHPKEProvider, build_hpke_info_v1
from epoch_auth_r3.crypto.exceptions import IntegrityError

CTX = {
    "schemaVersion": 1, "chainId": 1337,
    "authorizationContract": "0x" + "11" * 20, "headerRegistry": "0x" + "22" * 20,
    "resourceId": "aa" * 32, "bodyVersion": 2, "policyDigest": "bb" * 32,
    "epoch": 3, "stateVersion": 4, "headerVersion": 5, "keyVersion": 6,
    "recipientKeyId": "cc" * 32, "userVersion": 7,
}


def test_info_is_deterministic_and_every_field_is_bound():
    baseline = build_hpke_info_v1(CTX)
    assert baseline == build_hpke_info_v1(dict(reversed(list(CTX.items()))))
    for field in CTX:
        changed = copy.deepcopy(CTX)
        value = changed[field]
        if field == "schemaVersion":
            changed[field] = 2
            with pytest.raises(ValueError):
                build_hpke_info_v1(changed)
        else:
            changed[field] = (value + 1) if isinstance(value, int) else (
                "0x" + "33" * 20 if value.startswith("0x") else "dd" * 32
            )
            assert build_hpke_info_v1(changed) != baseline


def test_wrong_info_fails_closed():
    p = PyHPKEProvider()
    skr = bytes.fromhex("4612c550263fc8ad58375df3f557aac531d26850903e55a9f23f21d8534e8ac8")
    pkr = bytes.fromhex("3948cfe0ad1ddb695d780e59077195da6c56506b027329794ab02bca80815c4d")
    result = p.seal_base(pkr, b"x", build_hpke_info_v1(CTX), b"aad")
    with pytest.raises(IntegrityError):
        p.open_base(skr, result.enc, result.ciphertext, b"wrong", b"aad")
