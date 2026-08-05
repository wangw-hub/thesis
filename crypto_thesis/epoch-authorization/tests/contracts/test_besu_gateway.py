from __future__ import annotations

import pytest

from epoch_auth.blockchain.besu_gateway import BesuStateGateway
from epoch_auth.blockchain.errors import GatewayUnavailable
from epoch_auth.models import ResourceStatus, UserStatus


def test_gateway_reads_one_block_and_tracks_resource_state_version(contract_env):
    env = contract_env
    contract = env["contract"]
    w3 = env["w3"]
    contract.functions.registerUser(
        env["user_id"], env["user"], env["key_id"]
    ).transact({"from": env["admin"]})
    gateway = BesuStateGateway(
        w3, contract, sender=env["owner"], confirmations=0, retries=0
    )
    gateway.register_resource("resource-1", env["owner"], bytes(env["digest"]))

    snapshot = gateway.get_confirmed_state("resource-1", "user-1")
    assert snapshot.resource_state.status is ResourceStatus.ACTIVE
    assert snapshot.resource_state.updated_version == 1
    assert snapshot.user_state.status is UserStatus.ACTIVE
    assert snapshot.user_state.user_version == 1

    gateway.update_policy("resource-1", b"\x44" * 32)
    updated = gateway.get_resource("resource-1")
    assert updated.epoch == 2
    assert updated.updated_version == 2


def test_gateway_rejects_private_key_sender_mismatch(contract_env):
    env = contract_env
    try:
        BesuStateGateway(
            env["w3"],
            env["contract"],
            sender=env["owner"],
            private_key=b"\x01" * 32,
        )
    except ValueError as exc:
        assert "does not match sender" in str(exc)
    else:
        raise AssertionError("sender mismatch was accepted")


def test_gateway_exercises_role_separated_state_transitions(contract_env):
    env = contract_env
    contract = env["contract"]
    w3 = env["w3"]
    owner = BesuStateGateway(w3, contract, sender=env["owner"], retries=0)
    authorizer = BesuStateGateway(w3, contract, sender=env["authorizer"], retries=0)
    revoker = BesuStateGateway(w3, contract, sender=env["revoker"], retries=0)
    admin = BesuStateGateway(w3, contract, sender=env["admin"], retries=0)
    user = BesuStateGateway(w3, contract, sender=env["user"], retries=0)

    owner.register_resource("resource-2", env["owner"], b"\x21" * 32)
    authorizer.advance_epoch("resource-2", b"\x22" * 32)
    revoker.set_resource_status("resource-2", ResourceStatus.SUSPENDED)
    revoker.set_resource_status("resource-2", ResourceStatus.ACTIVE)
    assert owner.get_resource("resource-2").epoch == 4

    admin.register_user("user-2", env["user"], b"\x31" * 32)
    user.rotate_user_key("user-2", b"\x32" * 32)
    revoker.set_user_status("user-2", UserStatus.SUSPENDED)
    revoker.set_user_status("user-2", UserStatus.ACTIVE)
    assert admin.get_user("user-2").user_version == 4


def test_gateway_submits_locally_signed_raw_transaction(contract_env):
    env = contract_env
    backend = env["w3"].provider.ethereum_tester.backend
    private_key = backend.account_keys[0].to_bytes()
    gateway = BesuStateGateway(
        env["w3"],
        env["contract"],
        sender=env["admin"],
        private_key=private_key,
        retries=0,
    )
    receipt = gateway.register_user(
        "signed-user", env["user"], b"\x51" * 32
    )
    assert receipt["status"] == 1
    assert gateway.get_user("signed-user").user_version == 1


def test_gateway_fails_closed_for_unavailable_confirmed_or_missing_state(contract_env):
    env = contract_env
    too_deep = BesuStateGateway(
        env["w3"],
        env["contract"],
        sender=env["admin"],
        confirmations=env["w3"].eth.block_number + 1,
        retries=0,
    )
    with pytest.raises(GatewayUnavailable, match="insufficient confirmed"):
        too_deep.get_resource("missing")

    gateway = BesuStateGateway(
        env["w3"], env["contract"], sender=env["admin"], retries=0
    )
    with pytest.raises(GatewayUnavailable, match="confirmed state read failed"):
        gateway.get_confirmed_state("missing-resource", "missing-user")
    with pytest.raises(GatewayUnavailable, match="resource read failed"):
        gateway.get_resource("missing-resource")
    with pytest.raises(GatewayUnavailable, match="user read failed"):
        gateway.get_user("missing-user")
