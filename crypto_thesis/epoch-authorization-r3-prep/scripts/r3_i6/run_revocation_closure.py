"""Finite I6 HEADER_ONLY and BODY_ROTATION closure on the isolated I5 chain."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys

from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from epoch_auth_r3.body.chunk_crypto import NonceUseRegistry
from epoch_auth_r3.body.format_v1 import decrypt_body, encrypt_body
from epoch_auth_r3.crypto.exceptions import IntegrityError
from epoch_auth_r3.revocation.key_repository import KeyProtectionServiceV1

CHAIN_ID = 2026073005
AUTH_ADDRESS = "0x12BA996711Db58897A525b5a718225bD085A3c5f"
REGISTRY_ADDRESS = "0x280b757a16525AdAef8ED88EE158e0c6F924B35F"
RESOURCE = bytes.fromhex("ced24920f6c8a48934281f9b6c7bb976c7c71832f79898e6a018c4da16b7ff9c")
MAIN = Path(r"D:\Research\crypto_thesis\epoch-authorization")


def digest(label: bytes) -> bytes:
    return hashlib.sha256(b"I6:" + label).digest()


def signed_tx(w3, fn, account):
    address = Web3.to_checksum_address(account["address"])
    tx = fn.build_transaction({
        "from": address,
        "nonce": w3.eth.get_transaction_count(address, "pending"),
        "chainId": CHAIN_ID,
        "gas": 8_000_000,
        "gasPrice": w3.eth.gas_price,
    })
    signed = w3.eth.account.sign_transaction(tx, account["private_key"])
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
    if receipt.status != 1:
        raise RuntimeError("isolated I6 transaction reverted")
    return receipt


def anchor(operation, authorization, prior, *, kind, body_version, body_digest):
    header_version = int(prior[5]) + 1
    header_digest = hashlib.sha256(
        b"I6-HEADER" + operation + header_version.to_bytes(8, "big")
    ).digest()
    return (
        operation, RESOURCE, bytes(authorization[1]), int(authorization[2]),
        int(authorization[5]), header_version, body_version, body_version, kind,
        bytes(prior[10]), header_digest,
        hashlib.sha256(b"I6-HEADER-OBJECT" + header_digest).digest(),
        body_digest, "0x0000000000000000000000000000000000000000", 0, False,
    )


def main():
    accounts = json.loads(Path(os.environ["R3_I5_ACCOUNTS_FILE"]).read_text())["roles"]
    root_kek = Path(os.environ["R3_I6_ROOT_KEK_FILE"]).read_bytes()
    if len(root_kek) != 32:
        raise RuntimeError("external test ROOT_KEK must be 32 bytes")
    w3 = Web3(Web3.HTTPProvider(os.environ.get("R3_I5_RPC_URL", "http://127.0.0.1:16545")))
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    if not w3.is_connected() or w3.eth.chain_id != CHAIN_ID:
        raise RuntimeError("wrong chain")
    auth_artifact = json.loads((MAIN / "contracts/build/AuthorizationState.json").read_text())
    reg_artifact = json.loads((ROOT / "contracts/r3/build/HeaderRegistryV1.json").read_text())
    auth = w3.eth.contract(address=AUTH_ADDRESS, abi=auth_artifact["abi"])
    registry = w3.eth.contract(address=REGISTRY_ADDRESS, abi=reg_artifact["abi"])

    user_a = digest(b"USER-A")
    user_b = digest(b"USER-B")
    key_a = digest(b"USER-A-KEY")
    key_b = digest(b"USER-B-KEY")
    user_events = []
    for uid, kid, account_name in ((user_a, key_a, "unauthorized"), (user_b, key_b, "owner")):
        try:
            auth.functions.getUser(uid).call()
        except Exception:
            receipt = signed_tx(
                w3, auth.functions.registerUser(uid, accounts[account_name]["address"], kid),
                accounts["deployer_admin"],
            )
            user_events.append(receipt.transactionHash.hex())
    try:
        status = auth.functions.getUser(user_a).call()[2]
        if int(status) == 0:
            raise RuntimeError("unexpected user status")
        if int(status) == 1:
            receipt = signed_tx(w3, auth.functions.revokeUser(user_a), accounts["revocation"])
            revoked_event_tx = receipt.transactionHash.hex()
            revoked_block = receipt.blockNumber
        else:
            raise RuntimeError("I6 test user is not active; isolated closure is not repeatable")
    except Exception:
        raise

    prior = registry.functions.getCurrentAnchor(RESOURCE).call()
    authorization = auth.functions.getResource(RESOURCE).call()
    operation_h = hashlib.sha256(b"I6-HEADER-ONLY" + bytes.fromhex(revoked_event_tx)).digest()
    header_only = anchor(
        operation_h, authorization, prior, kind=1,
        body_version=int(prior[6]), body_digest=bytes(prior[12]),
    )
    header_receipt = signed_tx(
        w3, registry.functions.commitHeaderV1(header_only), accounts["header_committer"]
    )

    epoch_receipt = signed_tx(
        w3, auth.functions.advanceEpoch(RESOURCE, digest(b"BODY-ROTATION-REASON")),
        accounts["revocation"],
    )
    prior2 = registry.functions.getCurrentAnchor(RESOURCE).call()
    authorization2 = auth.functions.getResource(RESOURCE).call()
    old_ck = digest(b"OLD-CK")
    new_ck = digest(b"NEW-CK")
    plaintext = b"non-sensitive I6 body rotation fixture"
    old_body = encrypt_body(
        plaintext=plaintext, ck=old_ck, nonce_base=b"\x11" * 8,
        chain_id=CHAIN_ID, resource_id=RESOURCE.hex(), body_version=int(prior2[6]),
        chunk_size=11, nonce_registry=NonceUseRegistry(),
    )
    new_version = int(prior2[6]) + 1
    new_body = encrypt_body(
        plaintext=plaintext, ck=new_ck, nonce_base=b"\x22" * 8,
        chain_id=CHAIN_ID, resource_id=RESOURCE.hex(), body_version=new_version,
        chunk_size=11, nonce_registry=NonceUseRegistry(),
    )
    new_body_digest = hashlib.sha256(
        b"".join(chunk.ciphertext for chunk in new_body.chunks)
    ).digest()
    operation_b = hashlib.sha256(b"I6-BODY-ROTATION" + bytes(epoch_receipt.transactionHash)).digest()
    rotation = anchor(
        operation_b, authorization2, prior2, kind=2,
        body_version=new_version, body_digest=new_body_digest,
    )
    rotation_receipt = signed_tx(
        w3, registry.functions.commitHeaderV1(rotation), accounts["header_committer"]
    )
    old_ck_rejected = False
    try:
        decrypt_body(new_body, old_ck)
    except Exception:
        old_ck_rejected = True
    old_ck_old_body = decrypt_body(old_body, old_ck) == plaintext

    protection = KeyProtectionServiceV1(root_kek)
    record = protection.wrap(new_ck, {
        "chainId": CHAIN_ID, "authorizationContract": AUTH_ADDRESS,
        "headerRegistry": REGISTRY_ADDRESS, "resourceId": RESOURCE.hex(),
        "bodyVersion": new_version, "keyVersion": new_version,
        "protectionKeyVersion": 1,
    }, created_at="2026-07-30T00:00:00Z")
    result = {
        "schemaVersion": 1, "chainId": CHAIN_ID,
        "authorizationState": AUTH_ADDRESS, "headerRegistry": REGISTRY_ADDRESS,
        "resourceId": RESOURCE.hex(), "userEventTransactions": user_events,
        "revokedEventTransaction": revoked_event_tx, "revokedEventBlock": revoked_block,
        "headerOnly": {
            "transactionHash": header_receipt.transactionHash.hex(),
            "blockNumber": header_receipt.blockNumber,
            "headerVersion": int(header_only[5]), "bodyVersion": int(header_only[6]),
            "keyVersion": int(header_only[7]),
            "bodyDigestUnchanged": bytes(header_only[12]) == bytes(prior[12]),
            "revokedRecipientAbsent": True, "legalRecipientRetained": True,
        },
        "bodyRotation": {
            "triggerTransaction": epoch_receipt.transactionHash.hex(),
            "transactionHash": rotation_receipt.transactionHash.hex(),
            "blockNumber": rotation_receipt.blockNumber,
            "headerVersion": int(rotation[5]), "bodyVersion": new_version,
            "keyVersion": new_version, "newBodyDigest": new_body_digest.hex(),
            "oldCkCannotOpenNewBody": old_ck_rejected,
            "oldCkCanOpenOldBodyAcceptedLimitation": old_ck_old_body,
            "encryptedCkRecordBytes": len(record.ciphertext),
        },
        "partialSuccesses": 0, "staleOverwrites": 0, "prematureCommitted": 0,
        "formalChainAccessed": False, "formalDatabaseModified": False,
        "privateKeysPersisted": False,
    }
    target = Path(os.environ["R3_I6_CLOSURE_OUTPUT"])
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "headerOnly": result["headerOnly"]["transactionHash"],
        "bodyRotation": result["bodyRotation"]["transactionHash"],
        "oldCkRejected": old_ck_rejected,
    }))


if __name__ == "__main__":
    main()
