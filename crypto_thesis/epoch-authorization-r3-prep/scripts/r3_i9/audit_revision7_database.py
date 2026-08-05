from __future__ import annotations

import argparse
import json
from pathlib import Path

from epoch_auth_r3.pilot.database import (
    PilotApplicationNameV1, PilotDatabaseConnectionFactoryV1,
    PilotDatabaseConnectionRoleV1, frozen_pilot_database_config,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--password-file", required=True, type=Path)
    args = parser.parse_args()
    name = PilotApplicationNameV1.generate(
        attempt_id=args.attempt_id, run_identity=args.run_id,
        role=PilotDatabaseConnectionRoleV1.SNAPSHOT,
        software_commit=args.commit,
    )
    factory = PilotDatabaseConnectionFactoryV1(
        frozen_pilot_database_config(name.value), args.password_file,
    )
    with factory.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT job_id, status, operation_id, header_digest,
                body_digest FROM r3_pilot.pilot_canary_job WHERE run_id=%s""",
                        (args.run_id,))
            rows = cur.fetchall()
            cur.execute("""SELECT count(*) FROM pg_stat_activity
                WHERE datname=current_database()
                  AND application_name LIKE 'r3i9-%'
                  AND state='idle in transaction'""")
            idle_transactions = int(cur.fetchone()[0])
            cur.execute("""SELECT table_schema, table_name
                FROM information_schema.tables
                WHERE table_schema IN ('r3_pilot','r3_control')
                ORDER BY table_schema, table_name""")
            tables = [f"{row[0]}.{row[1]}" for row in cur.fetchall()]
    print(json.dumps({
        "schemaVersion": 1,
        "classification": "AUDIT_ONLY",
        "attemptId": args.attempt_id,
        "runId": args.run_id,
        "applicationName": name.value,
        "pilotJobCount": len(rows),
        "pilotJobs": [
            {
                "jobId": row[0], "status": row[1], "operationId": row[2],
                "headerDigest": row[3], "bodyDigest": row[4],
            } for row in rows
        ],
        "idlePilotTransactions": idle_transactions,
        "tablesInspected": tables,
        "identityAttestation": factory.attest(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
