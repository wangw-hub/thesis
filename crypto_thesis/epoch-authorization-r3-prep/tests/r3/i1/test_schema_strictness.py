import pytest
from epoch_auth_r3.crypto.hpke_provider import build_hpke_info_v1

BASE = {"schemaVersion":1, "chainId":1, "authorizationContract":"0x"+"11"*20,
        "headerRegistry":"0x"+"22"*20, "resourceId":"33"*32, "bodyVersion":1,
        "policyDigest":"44"*32, "epoch":1, "stateVersion":1, "headerVersion":1,
        "keyVersion":1, "recipientKeyId":"55"*32, "userVersion":1}


@pytest.mark.parametrize("change", [
    lambda x: x.update(extra=1),
    lambda x: x.pop("epoch"),
    lambda x: x.update(chainId=1.5),
    lambda x: x.update(authorizationContract="bad"),
])
def test_hpke_info_schema_rejects_unknown_missing_float_and_bad_address(change):
    value = dict(BASE)
    change(value)
    with pytest.raises((ValueError, TypeError)):
        build_hpke_info_v1(value)
