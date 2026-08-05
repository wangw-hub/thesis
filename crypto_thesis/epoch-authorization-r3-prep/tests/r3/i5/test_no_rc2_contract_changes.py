from pathlib import Path


def test_no_rc2_contract_changes():
    source = Path("contracts/r3/HeaderRegistryV1.sol").read_text()
    assert "IAuthorizationStateFrozen" in source
    assert "AuthorizationState.sol" not in source
    assert "keyVersion" not in Path(
        r"D:\Research\crypto_thesis\epoch-authorization\contracts\AuthorizationState.sol"
    ).read_text()
