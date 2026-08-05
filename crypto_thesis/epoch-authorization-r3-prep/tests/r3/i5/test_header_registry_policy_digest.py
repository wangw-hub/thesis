def test_header_registry_policy_digest(chain_result):
    assert chain_result["rejections"]["wrongPolicyDigest"]
