def test_header_registry_zero_digest(chain_result):
    assert chain_result["rejections"]["zeroDigest"]
