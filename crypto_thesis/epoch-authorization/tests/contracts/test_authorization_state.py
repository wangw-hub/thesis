from __future__ import annotations

import pytest
from eth_tester.exceptions import TransactionFailed
from web3 import Web3


def transact(env, fn, sender):
    tx = fn.transact({"from": sender})
    return env["w3"].eth.wait_for_transaction_receipt(tx)


def register_resource(env):
    return transact(
        env,
        env["contract"].functions.registerResource(
            env["resource_id"], env["owner"], env["digest"]
        ),
        env["owner"],
    )


def register_user(env):
    return transact(
        env,
        env["contract"].functions.registerUser(
            env["user_id"], env["user"], env["key_id"]
        ),
        env["admin"],
    )


def test_resource_lifecycle_epoch_and_events(contract_env):
    env = contract_env
    receipt = register_resource(env)
    assert len(env["contract"].events.ResourceRegistered().process_receipt(receipt)) == 1
    state = env["contract"].functions.getResource(env["resource_id"]).call()
    assert (state[2], state[3], state[4], state[5]) == (1, 1, 1, 1)

    new_digest = Web3.keccak(text="policy-2")
    receipt = transact(
        env,
        env["contract"].functions.updatePolicy(env["resource_id"], new_digest),
        env["owner"],
    )
    assert len(env["contract"].events.PolicyUpdated().process_receipt(receipt)) == 1
    state = env["contract"].functions.getResource(env["resource_id"]).call()
    assert (state[1], state[2], state[4], state[5]) == (new_digest, 2, 2, 2)

    transact(
        env,
        env["contract"].functions.suspendResource(env["resource_id"]),
        env["revoker"],
    )
    transact(
        env,
        env["contract"].functions.activateResource(env["resource_id"]),
        env["revoker"],
    )
    transact(
        env,
        env["contract"].functions.revokeResource(env["resource_id"]),
        env["revoker"],
    )
    state = env["contract"].functions.getResource(env["resource_id"]).call()
    assert (state[2], state[3], state[5]) == (5, 3, 5)
    with pytest.raises(TransactionFailed):
        transact(
            env,
            env["contract"].functions.activateResource(env["resource_id"]),
            env["revoker"],
        )


def test_resource_permissions_and_boundaries(contract_env):
    env = contract_env
    with pytest.raises(TransactionFailed):
        transact(
            env,
            env["contract"].functions.registerResource(
                env["resource_id"], env["owner"], env["digest"]
            ),
            env["outsider"],
        )
    register_resource(env)
    with pytest.raises(TransactionFailed):
        transact(
            env,
            env["contract"].functions.updatePolicy(
                env["resource_id"], Web3.keccak(text="x")
            ),
            env["outsider"],
        )
    with pytest.raises(TransactionFailed):
        transact(
            env,
            env["contract"].functions.advanceEpoch(env["resource_id"], b"\x00" * 32),
            env["outsider"],
        )
    with pytest.raises(TransactionFailed):
        transact(
            env,
            env["contract"].functions.registerResource(
                env["resource_id"], env["owner"], env["digest"]
            ),
            env["owner"],
        )


def test_user_rotation_version_and_reactivation(contract_env):
    env = contract_env
    register_user(env)
    new_key = Web3.keccak(text="user-key-2")
    receipt = transact(
        env,
        env["contract"].functions.rotateUserKey(env["user_id"], new_key),
        env["user"],
    )
    assert len(env["contract"].events.UserKeyRotated().process_receipt(receipt)) == 1
    state = env["contract"].functions.getUser(env["user_id"]).call()
    assert (state[1], state[3]) == (new_key, 2)
    transact(
        env,
        env["contract"].functions.suspendUser(env["user_id"]),
        env["revoker"],
    )
    transact(
        env,
        env["contract"].functions.activateUser(env["user_id"]),
        env["revoker"],
    )
    state = env["contract"].functions.getUser(env["user_id"]).call()
    assert (state[2], state[3]) == (1, 4)


def test_duplicate_key_and_unauthorized_role_change(contract_env):
    env = contract_env
    register_user(env)
    with pytest.raises(TransactionFailed):
        transact(
            env,
            env["contract"].functions.registerUser(
                Web3.keccak(text="user-2"), env["outsider"], env["key_id"]
            ),
            env["admin"],
        )
    role = env["contract"].functions.OWNER_ROLE().call()
    with pytest.raises(TransactionFailed):
        transact(
            env,
            env["contract"].functions.grantRole(role, env["outsider"]),
            env["outsider"],
        )
