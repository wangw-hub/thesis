def test_header_registry_version_conflict(chain_result):
    assert chain_result["rejections"]["versionJump"]
