from __future__ import annotations

import hashlib
from collections.abc import Callable

from epoch_auth_r3.storage import LocalObjectStore, ObjectKind, ObjectReferenceV1

from .cid import parse_cid_v1
from .client import KuboRpcClient
from .exceptions import ReplicaVerificationError
from .models import (
    ReplicaVerificationResultV1, ReplicationStatus, StorageReplicaRecordV1,
    VerificationStatus,
)


class IpfsReplicaGatewayV1:
    CHUNKER_PROFILE = "size-262144/raw-leaves=true/cid-v1/sha2-256"

    def __init__(self, store: LocalObjectStore, client: KuboRpcClient,
                 validators: dict[ObjectKind, Callable[[bytes], None]]):
        self.store = store
        self.client = client
        self.validators = validators

    def _validate_object(self, reference: ObjectReferenceV1, data: bytes) -> None:
        validator = self.validators.get(reference.object_kind)
        if validator is None:
            raise ReplicaVerificationError("OBJECT_VALIDATOR_REQUIRED")
        validator(data)

    def replicate(self, reference: ObjectReferenceV1) -> StorageReplicaRecordV1:
        data = self.store.get(reference)
        cid = self.client.add_bytes(data)
        parsed = parse_cid_v1(cid)
        candidate = self.client.cat(cid)
        if candidate != data:
            raise ReplicaVerificationError("READBACK_BYTES_MISMATCH")
        self._validate_object(reference, candidate)
        if not self.client.pin_ls(cid):
            raise ReplicaVerificationError("PIN_NOT_CONFIRMED")
        return StorageReplicaRecordV1(
            1, "sha256", reference.digest_hex, reference.size_bytes,
            reference.object_kind, "IPFS_KUBO", cid, parsed.version,
            parsed.multihash_code, parsed.codec, self.CHUNKER_PROFILE, True,
            ReplicationStatus.PINNED, VerificationStatus.OBJECT_VERIFIED,
            self.client.identity()["ID"],
        )

    def verify_replica(self, reference: ObjectReferenceV1,
                       replica: StorageReplicaRecordV1) -> ReplicaVerificationResultV1:
        try:
            self._fetch_verified_candidate(reference, replica)
            return ReplicaVerificationResultV1(True, True, True, True)
        except ReplicaVerificationError as exc:
            return ReplicaVerificationResultV1(False, False, False, False, str(exc))

    def _fetch_verified_candidate(
        self, reference: ObjectReferenceV1, replica: StorageReplicaRecordV1
    ) -> bytes:
        if replica.object_kind != reference.object_kind:
            raise ReplicaVerificationError("OBJECT_KIND_MISMATCH")
        if replica.object_digest_hex != reference.digest_hex:
            raise ReplicaVerificationError("REPLICA_MAPPING_CONFLICT")
        data = self.client.cat(replica.cid)
        if len(data) != reference.size_bytes:
            raise ReplicaVerificationError("REPLICA_SIZE_MISMATCH")
        if hashlib.sha256(data).hexdigest() != reference.digest_hex:
            raise ReplicaVerificationError("REPLICA_DIGEST_MISMATCH")
        self._validate_object(reference, data)
        return data

    def fetch_verified(self, reference: ObjectReferenceV1,
                       replica: StorageReplicaRecordV1) -> bytes:
        return self._fetch_verified_candidate(reference, replica)

    def restore_local(self, reference: ObjectReferenceV1,
                      replica: StorageReplicaRecordV1) -> ObjectReferenceV1:
        data = self.fetch_verified(reference, replica)
        if self.store.exists(reference):
            verification = self.store.verify(reference)
            if verification.verified:
                return reference
            self.store.quarantine_corrupt(reference)
        restored = self.store.put(
            data, namespace=reference.namespace, object_kind=reference.object_kind,
            expected_digest=reference.digest_hex,
        )
        if restored != reference or not self.store.verify(reference).verified:
            raise ReplicaVerificationError("ATOMIC_RESTORE_FAILED")
        return restored
