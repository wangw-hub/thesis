def test_header_only_body_digest_must_match(contracts, chain_result):
    _, registry = contracts
    resource = bytes.fromhex(chain_result["resourceId"])
    assert registry.functions.getAnchor(resource, 1).call()[12] == registry.functions.getAnchor(resource, 2).call()[12]
    assert chain_result["rejections"]["headerOnlyBodyDigestChange"]
