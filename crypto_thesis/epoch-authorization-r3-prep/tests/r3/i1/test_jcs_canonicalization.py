import pytest
from epoch_auth_r3.crypto.exceptions import CryptoValidationError
from epoch_auth_r3.serialization.base64url import decode, encode
from epoch_auth_r3.serialization.canonical_types import normalize_address
from epoch_auth_r3.serialization.jcs_adapter import canonicalize, parse_strict


def test_canonical_order_unicode_escape_empty_and_nested():
    a = {"z": [], "é": {"b": 2, "a": "x\n"}, "empty": {}}
    b = {"empty": {}, "é": {"a": "x\n", "b": 2}, "z": []}
    assert canonicalize(a) == canonicalize(b)
    assert parse_strict(canonicalize(a)) == a


def test_address_and_base64url_rules():
    assert normalize_address("0x"+"AB"*20) == "0x"+"ab"*20
    assert encode(b"\xff\xee") == "_-4"
    assert decode("_-4") == b"\xff\xee"
    with pytest.raises(CryptoValidationError): decode("_-4=")


@pytest.mark.parametrize("value", [float("nan"), float("inf"), 1.5])
def test_floats_forbidden(value):
    with pytest.raises(CryptoValidationError): canonicalize({"x": value})


def test_duplicate_json_rejected():
    with pytest.raises(CryptoValidationError): parse_strict('{"x":1,"x":2}')
