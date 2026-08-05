"""Deploy and validate only against the isolated R3 I5 chain.

Private keys are loaded from an external test-only manifest and are never
printed or persisted by this program.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

from web3 import Web3


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from epoch_auth_r3.database.models import SyntheticRevocationEventV1
from epoch_auth_r3.database.operation_id import operation_id_v1

MAIN = Path(r"D:\Research\crypto_thesis\epoch-authorization")
CHAIN_ID = 2026073005


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _signed_tx(w3: Web3, fn: Any, account: dict[str, str], *, value: int = 0) -> dict[str, Any]:
    address = Web3.to_checksum_address(account["address"])
    tx = fn.build_transaction({
        "from": address,
        "nonce": w3.eth.get_transaction_count(address, "pending"),
        "chainId": CHAIN_ID,
        "gas": 15_000_000,
        "gasPrice": w3.eth.gas_price,
        "value": value,
    })
    signed = w3.eth.account.sign_transaction(tx, account["private_key"])
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
    if receipt.status != 1:
        raise RuntimeError(
            f"isolated transaction failed: {tx_hash.hex()} gasUsed={receipt.gasUsed}"
        )
    return dict(receipt)


def _expect_revert(fn: Any, sender: str) -> bool:
    try:
        fn.call({"from": Web3.to_checksum_address(sender)})
    except Exception:
        return True
    return False


def _anchor(resource: bytes, policy: bytes, operation: bytes, header_version: int,
            body_version: int, key_version: int, update_kind: int,
            previous: bytes, header_digest: bytes, header_object: bytes,
            body_object: bytes, *, epoch: int = 1, state_version: int = 1) -> tuple[Any, ...]:
    return (
        operation, resource, policy, epoch, state_version, header_version,
        body_version, key_version, update_kind, previous, header_digest,
        header_object, body_object, "0x0000000000000000000000000000000000000000",
        0, False,
    )


def main() -> None:
    rpc = os.environ.get("R3_I5_RPC_URL", "http://127.0.0.1:16545")
    secret_path = Path(os.environ["R3_I5_ACCOUNTS_FILE"])
    output_path = Path(os.environ["R3_I5_OUTPUT"])
    accounts = _load_json(secret_path)["roles"]
    w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 10}))
    if not w3.is_connected() or w3.eth.chain_id != CHAIN_ID:
        raise RuntimeError("not connected to the frozen isolated I5 chain")

    auth_artifact_path = MAIN / "contracts" / "build" / "AuthorizationState.json"
    auth_artifact = _load_json(auth_artifact_path)
    auth_factory = w3.eth.contract(abi=auth_artifact["abi"], bytecode=auth_artifact["bytecode"])
    auth_receipt = _signed_tx(w3, auth_factory.constructor(), accounts["deployer_admin"])
    auth = w3.eth.contract(address=auth_receipt["contractAddress"], abi=auth_artifact["abi"])

    owner_role = auth.functions.OWNER_ROLE().call()
    authorizer_role = auth.functions.AUTHORIZER_ROLE().call()
    revocation_role = auth.functions.REVOCATION_ROLE().call()
    for role, account_name in (
        (owner_role, "owner"), (authorizer_role, "authorizer"), (revocation_role, "revocation")
    ):
        _signed_tx(w3, auth.functions.grantRole(role, accounts[account_name]["address"]),
                   accounts["deployer_admin"])

    resource = hashlib.sha256(
        b"R3-I5-RESOURCE-V1" + bytes.fromhex(auth.address[2:])
    ).digest()
    def digest(label: bytes) -> bytes:
        return hashlib.sha256(label + resource).digest()
    policy = hashlib.sha256(b"R3-I5-POLICY-V1").digest()
    register_receipt = _signed_tx(
        w3,
        auth.functions.registerResource(resource, accounts["owner"]["address"], policy),
        accounts["owner"],
    )

    build = ROOT / "contracts" / "r3" / "build"
    registry_artifact = _load_json(build / "HeaderRegistryV1.json")
    registry_abi = registry_artifact["abi"]
    registry_bin = registry_artifact["bytecode"]
    registry_factory = w3.eth.contract(abi=registry_abi, bytecode=registry_bin)
    registry_receipt = _signed_tx(
        w3, registry_factory.constructor(auth.address), accounts["deployer_admin"]
    )
    registry = w3.eth.contract(address=registry_receipt["contractAddress"], abi=registry_abi)
    committer_role = registry.functions.HEADER_COMMITTER_ROLE().call()
    _signed_tx(
        w3,
        registry.functions.grantRole(committer_role, accounts["header_committer"]["address"]),
        accounts["deployer_admin"],
    )

    register_log = register_receipt["logs"][0]
    trigger = SyntheticRevocationEventV1(
        chain_id=CHAIN_ID,
        authorization_contract=bytes.fromhex(auth.address[2:]),
        header_registry=bytes.fromhex(registry.address[2:]),
        event_signature=Web3.keccak(
            text="ResourceRegistered(bytes32,address,bytes32,uint64,uint64)"
        ),
        tx_hash=bytes(register_receipt["transactionHash"]),
        log_index=int(register_log["logIndex"]),
        block_number=int(register_receipt["blockNumber"]),
        block_hash=bytes(register_receipt["blockHash"]),
        resource_id=resource,
        new_epoch=1,
        new_state_version=1,
        new_header_version=1,
        new_key_version=1,
    )
    initial_operation_id = operation_id_v1(trigger)
    h1 = digest(b"HEADER-1")
    b1 = digest(b"BODY-1")
    initial = _anchor(
        resource, policy, initial_operation_id, 1, 1, 1, 0,
        bytes(32), h1, digest(b"HEADER-OBJECT-1"), b1,
    )
    initial_receipt = _signed_tx(
        w3, registry.functions.commitHeaderV1(initial), accounts["header_committer"]
    )

    h2 = digest(b"HEADER-2")
    header_only = _anchor(
        resource, policy, hashlib.sha256(b"OP-HEADER-ONLY").digest(), 2, 1, 1, 1,
        h1, h2, digest(b"HEADER-OBJECT-2"), b1,
    )
    header_only_receipt = _signed_tx(
        w3, registry.functions.commitHeaderV1(header_only), accounts["header_committer"]
    )

    h3 = digest(b"HEADER-3")
    b2 = digest(b"BODY-2")
    rotation = _anchor(
        resource, policy, hashlib.sha256(b"OP-BODY-ROTATION").digest(), 3, 2, 2, 2,
        h2, h3, digest(b"HEADER-OBJECT-3"), b2,
    )
    rotation_receipt = _signed_tx(
        w3, registry.functions.commitHeaderV1(rotation), accounts["header_committer"]
    )

    invalid_key = _anchor(
        resource, policy, hashlib.sha256(b"OP-BAD-KEY").digest(), 4, 3, 2, 2,
        h3, digest(b"HEADER-4"),
        digest(b"HEADER-OBJECT-4"), digest(b"BODY-3"),
    )
    invalid_header_body = _anchor(
        resource, policy, hashlib.sha256(b"OP-BAD-HEADER-ONLY").digest(), 4, 2, 2, 1,
        h3, digest(b"HEADER-4B"),
        digest(b"HEADER-OBJECT-4B"), digest(b"BODY-CHANGED"),
    )
    valid_next = _anchor(
        resource, policy, hashlib.sha256(b"OP-NEXT").digest(), 4, 2, 2, 1,
        h3, digest(b"HEADER-4C"),
        digest(b"HEADER-OBJECT-4C"), b2,
    )
    version_jump = list(valid_next); version_jump[5] = 5
    wrong_previous = list(valid_next); wrong_previous[9] = bytes(32)
    wrong_policy = list(valid_next); wrong_policy[2] = digest(b"WRONG-POLICY")
    wrong_epoch = list(valid_next); wrong_epoch[3] = 0
    wrong_state = list(valid_next); wrong_state[4] = 0
    zero_digest = list(valid_next); zero_digest[10] = bytes(32)
    unknown_resource = list(valid_next)
    unknown_resource[1] = digest(b"UNKNOWN-RESOURCE")
    unauthorized_rejected = _expect_revert(
        registry.functions.commitHeaderV1(rotation), accounts["unauthorized"]["address"]
    )
    key_mismatch_rejected = _expect_revert(
        registry.functions.commitHeaderV1(invalid_key), accounts["header_committer"]["address"]
    )
    header_body_change_rejected = _expect_revert(
        registry.functions.commitHeaderV1(invalid_header_body),
        accounts["header_committer"]["address"],
    )
    replay_rejected = _expect_revert(
        registry.functions.commitHeaderV1(initial), accounts["header_committer"]["address"]
    )
    version_jump_rejected = _expect_revert(
        registry.functions.commitHeaderV1(tuple(version_jump)),
        accounts["header_committer"]["address"],
    )
    wrong_previous_rejected = _expect_revert(
        registry.functions.commitHeaderV1(tuple(wrong_previous)),
        accounts["header_committer"]["address"],
    )
    wrong_policy_rejected = _expect_revert(
        registry.functions.commitHeaderV1(tuple(wrong_policy)),
        accounts["header_committer"]["address"],
    )
    wrong_epoch_rejected = _expect_revert(
        registry.functions.commitHeaderV1(tuple(wrong_epoch)),
        accounts["header_committer"]["address"],
    )
    wrong_state_rejected = _expect_revert(
        registry.functions.commitHeaderV1(tuple(wrong_state)),
        accounts["header_committer"]["address"],
    )
    zero_digest_rejected = _expect_revert(
        registry.functions.commitHeaderV1(tuple(zero_digest)),
        accounts["header_committer"]["address"],
    )
    unknown_resource_rejected = _expect_revert(
        registry.functions.commitHeaderV1(tuple(unknown_resource)),
        accounts["header_committer"]["address"],
    )
    admin_bypass_rejected = _expect_revert(
        registry.functions.commitHeaderV1(valid_next), accounts["deployer_admin"]["address"]
    )
    invalid_authorization_contract_rejected = _expect_revert(
        registry_factory.constructor(accounts["unauthorized"]["address"]),
        accounts["deployer_admin"]["address"],
    )
    _signed_tx(
        w3,
        registry.functions.revokeRole(
            committer_role, accounts["header_committer"]["address"]
        ),
        accounts["deployer_admin"],
    )
    revoked_committer_rejected = _expect_revert(
        registry.functions.commitHeaderV1(valid_next),
        accounts["header_committer"]["address"],
    )
    _signed_tx(
        w3,
        registry.functions.grantRole(
            committer_role, accounts["header_committer"]["address"]
        ),
        accounts["deployer_admin"],
    )

    current = registry.functions.getCurrentAnchor(resource).call()
    same_block = rotation_receipt["blockNumber"]
    authorization_at_block = auth.functions.getResource(resource).call(block_identifier=same_block)
    anchor_at_block = registry.functions.getCurrentAnchor(resource).call(block_identifier=same_block)

    _signed_tx(
        w3, auth.functions.advanceEpoch(resource, hashlib.sha256(b"REVOCATION").digest()),
        accounts["authorizer"],
    )
    stale = _anchor(
        resource, policy, hashlib.sha256(b"OP-STALE").digest(), 4, 2, 2, 1,
        h3, digest(b"HEADER-STALE"),
        digest(b"HEADER-OBJECT-STALE"), b2,
    )
    stale_rejected = _expect_revert(
        registry.functions.commitHeaderV1(stale), accounts["header_committer"]["address"]
    )

    result = {
        "schemaVersion": 1,
        "chainId": CHAIN_ID,
        "authorizationState": auth.address,
        "headerRegistry": registry.address,
        "resourceId": resource.hex(),
        "authorizationArtifactSha256": hashlib.sha256(auth_artifact_path.read_bytes()).hexdigest(),
        "blocks": {
            "authorizationDeployment": auth_receipt["blockNumber"],
            "registryDeployment": registry_receipt["blockNumber"],
            "initial": initial_receipt["blockNumber"],
            "headerOnly": header_only_receipt["blockNumber"],
            "bodyRotation": rotation_receipt["blockNumber"],
        },
        "transactions": {
            "trigger": register_receipt["transactionHash"].hex(),
            "initial": initial_receipt["transactionHash"].hex(),
            "headerOnly": header_only_receipt["transactionHash"].hex(),
            "bodyRotation": rotation_receipt["transactionHash"].hex(),
        },
        "trigger": {
            "eventSignature": trigger.event_signature.hex(),
            "transactionHash": trigger.tx_hash.hex(),
            "logIndex": trigger.log_index,
            "blockNumber": trigger.block_number,
            "blockHash": trigger.block_hash.hex(),
            "newEpoch": trigger.new_epoch,
            "newStateVersion": trigger.new_state_version,
            "newHeaderVersion": trigger.new_header_version,
            "newKeyVersion": trigger.new_key_version,
            "operationId": initial_operation_id.hex(),
        },
        "current": {
            "headerVersion": int(current[5]),
            "bodyVersion": int(current[6]),
            "keyVersion": int(current[7]),
            "updateKind": int(current[8]),
        },
        "sameBlockRead": {
            "blockNumber": same_block,
            "authorizationEpoch": int(authorization_at_block[2]),
            "authorizationStateVersion": int(authorization_at_block[5]),
            "headerVersion": int(anchor_at_block[5]),
            "bodyVersion": int(anchor_at_block[6]),
            "keyVersion": int(anchor_at_block[7]),
        },
        "rejections": {
            "unauthorized": unauthorized_rejected,
            "keyBodyMismatch": key_mismatch_rejected,
            "headerOnlyBodyDigestChange": header_body_change_rejected,
            "operationReplay": replay_rejected,
            "versionJump": version_jump_rejected,
            "wrongPreviousHeaderDigest": wrong_previous_rejected,
            "wrongPolicyDigest": wrong_policy_rejected,
            "wrongEpoch": wrong_epoch_rejected,
            "wrongStateVersion": wrong_state_rejected,
            "zeroDigest": zero_digest_rejected,
            "unknownResource": unknown_resource_rejected,
            "adminBypass": admin_bypass_rejected,
            "invalidAuthorizationContract": invalid_authorization_contract_rejected,
            "revokedCommitter": revoked_committer_rejected,
            "staleAuthorizationState": stale_rejected,
        },
        "privateKeysPersisted": False,
        "formalChainAccessed": False,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "chainId": CHAIN_ID,
        "authorizationState": auth.address,
        "headerRegistry": registry.address,
        "current": result["current"],
        "rejections": result["rejections"],
    }))


if __name__ == "__main__":
    main()
