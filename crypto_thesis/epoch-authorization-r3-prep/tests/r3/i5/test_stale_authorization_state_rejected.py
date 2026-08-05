def test_stale_authorization_state_rejected(chain_result):
    assert chain_result["rejections"]["staleAuthorizationState"]
