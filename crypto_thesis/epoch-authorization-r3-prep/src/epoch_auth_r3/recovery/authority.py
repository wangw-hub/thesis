from dataclasses import dataclass
from enum import StrEnum


class RecoveryAuthority(StrEnum):
    AUTHORIZATION_STATE = "AUTHORIZATION_STATE"
    HEADER_REGISTRY = "HEADER_REGISTRY"
    LOCAL_OBJECT_STORE = "LOCAL_OBJECT_STORE"
    POSTGRESQL_R3_CONTROL = "POSTGRESQL_R3_CONTROL"
    EXTERNAL_KEYSTORE = "EXTERNAL_KEYSTORE"


@dataclass(frozen=True)
class RecoveryAuthorityMatrixV1:
    authorization_fields: tuple[str, ...] = (
        "resourceStatus", "policyDigest", "epoch", "stateVersion"
    )
    header_fields: tuple[str, ...] = (
        "currentHeaderVersion", "currentBodyVersion", "currentKeyVersion",
        "updateKind", "previousHeaderDigest", "headerDigest",
        "headerObjectDigest", "bodyObjectDigest", "operationIdUsed",
    )
    object_content: tuple[str, ...] = ("signedHeaderBytes", "bodyCiphertextBytes")
    database_state: tuple[str, ...] = (
        "workflow", "events", "jobs", "commitAttempts", "recoveryAudit",
        "encryptedContentKeys", "recipientIndexCache",
    )
    keystore_secrets: tuple[str, ...] = (
        "TEST_ONLY_ROOT_KEK", "testSigningKeys", "testTransactionKeys"
    )

    def authority_for(self, field: str) -> RecoveryAuthority:
        if field in self.authorization_fields:
            return RecoveryAuthority.AUTHORIZATION_STATE
        if field in self.header_fields:
            return RecoveryAuthority.HEADER_REGISTRY
        if field in self.object_content:
            return RecoveryAuthority.LOCAL_OBJECT_STORE
        if field in self.database_state:
            return RecoveryAuthority.POSTGRESQL_R3_CONTROL
        if field in self.keystore_secrets:
            return RecoveryAuthority.EXTERNAL_KEYSTORE
        raise KeyError(f"UNASSIGNED_RECOVERY_AUTHORITY:{field}")
