from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from epoch_auth_r3.pilot.chain_write import (
    PilotChainWriteAdmissionGuardV1,
    PilotChainWritePlanV1,
    PilotChainWriteStepV1,
)
from epoch_auth_r3.pilot.database import (
    PilotApplicationNameV1,
    PilotDatabaseConnectionFactoryV1,
    PilotDatabaseConnectionRoleV1,
    frozen_pilot_database_config,
)
from epoch_auth_r3.pilot.job_transaction import (
    PilotJobCandidateV1,
    PilotJobCreateTransactionV1,
    PilotJobVisibilityGateV1,
)


def token(label: str, seed: str) -> str:
    return hashlib.sha256(f"R3_I9_REV8_PREFLIGHT:{label}:{seed}".encode()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", required=True)
    parser.add_argument("--password-file", required=True, type=Path)
    parser.add_argument("--seed", required=True)
    args = parser.parse_args()

    attempt_id = f"REV8_PREFLIGHT_{args.seed}"
    run_id = token("run", args.seed)
    job_id = token("job", args.seed)
    rollback_job_id = token("rollback-job", args.seed)
    rollback_run_id = token("rollback-run", args.seed)
    resource_id = token("resource", args.seed)
    operation_id = token("operation", args.seed)
    body_digest = token("body", args.seed)
    body_object_digest = token("body-object", args.seed)
    header_digest = token("header", args.seed)
    header_object_digest = token("header-object", args.seed)
    plan = PilotChainWritePlanV1(
        attempt_id, run_id, job_id, resource_id, operation_id, 2,
        (
            PilotChainWriteStepV1(
                1, "AuthorizationState", "registerResource",
                "PREFLIGHT_OWNER", "ACCOUNT_PENDING_NONCE",
            ),
            PilotChainWriteStepV1(
                2, "HeaderRegistry", "commitHeaderV1",
                "PREFLIGHT_COMMITTER", "ACCOUNT_PENDING_NONCE",
            ),
        ),
    )
    candidate = PilotJobCandidateV1(
        attempt_id, run_id, job_id, resource_id, operation_id, "INITIAL",
        header_digest, header_object_digest, body_digest, body_object_digest,
        plan.to_dict(),
    )
    app_name = PilotApplicationNameV1.generate(
        attempt_id=attempt_id,
        run_identity=run_id,
        role=PilotDatabaseConnectionRoleV1.WORKER,
        software_commit=args.commit,
    )
    factory = PilotDatabaseConnectionFactoryV1(
        frozen_pilot_database_config(app_name.value), args.password_file,
    )
    attestation = factory.attest()
    created = PilotJobCreateTransactionV1.create(factory, candidate)
    visible = PilotJobVisibilityGateV1.verify(factory, candidate)
    admission = PilotChainWriteAdmissionGuardV1.admit(
        plan=plan,
        visibility=visible,
        object_verification={"headerVerified": True, "bodyVerified": True},
        chain_writes_before_admission=0,
    )

    # The rollback probe uses the same real table but never becomes visible.
    with factory.connect() as conn:
        conn.execute("BEGIN")
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO r3_pilot.pilot_canary_job
                (job_id, run_id, attempt_id, status, operation_id, resource_id,
                 update_kind, header_digest, header_object_digest, body_digest,
                 body_object_digest, chain_write_plan)
                VALUES (%s,%s,%s,'READY_FOR_CHAIN_SUBMISSION',%s,%s,'INITIAL',
                        %s,%s,%s,%s,%s::jsonb)""",
                (
                    rollback_job_id, rollback_run_id, attempt_id,
                    token("rollback-op", args.seed),
                    token("rollback-resource", args.seed), header_digest,
                    header_object_digest, body_digest, body_object_digest,
                    json.dumps(plan.to_dict(), sort_keys=True),
                ),
            )
        conn.rollback()
    with factory.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT count(*) FROM r3_pilot.pilot_canary_job WHERE job_id=%s",
                (rollback_job_id,),
            )
            rollback_visible = int(cur.fetchone()[0])

    with factory.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT count(*) FROM r3_pilot.pilot_canary_job WHERE job_id IN (%s,%s)",
                (job_id, rollback_job_id),
            )
            residual_rows = int(cur.fetchone()[0])

    result = {
        "schemaVersion": 1,
        "databaseIdentityAttested": bool(attestation["connectionAttested"]),
        "jobCreateExplicitCommit": created["transactionState"] == "COMMITTED",
        "independentConnectionVisible": visible["visibleFromIndependentConnection"],
        "rollbackRowVisible": rollback_visible,
        "chainWriteAdmission": admission["decision"],
        "plannedTransactionCount": len(plan.transactionSequence),
        "chainTransactionsExecuted": 0,
        "committedPreflightRowsBeforeAdminCleanup": residual_rows,
    }
    if result != {
        "schemaVersion": 1,
        "databaseIdentityAttested": True,
        "jobCreateExplicitCommit": True,
        "independentConnectionVisible": True,
        "rollbackRowVisible": 0,
        "chainWriteAdmission": "ADMITTED",
        "plannedTransactionCount": 2,
        "chainTransactionsExecuted": 0,
        "committedPreflightRowsBeforeAdminCleanup": 1,
    }:
        raise SystemExit("REVISION8_TRANSACTION_PREFLIGHT_FAILED")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
