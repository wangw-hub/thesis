import hashlib
from pathlib import Path


def test_authorization_state_artifact_identity(chain_result):
    path = Path(r"D:\Research\crypto_thesis\epoch-authorization\contracts\build\AuthorizationState.json")
    assert hashlib.sha256(path.read_bytes()).hexdigest() == chain_result["authorizationArtifactSha256"]
