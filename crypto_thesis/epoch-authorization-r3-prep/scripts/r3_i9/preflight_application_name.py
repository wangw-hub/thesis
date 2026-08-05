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
    parser.add_argument("--run-identity", required=True)
    parser.add_argument("--role", choices=[item.value for item in PilotDatabaseConnectionRoleV1], required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--password-file", type=Path, required=True)
    args = parser.parse_args()
    name = PilotApplicationNameV1.generate(
        attempt_id=args.attempt_id, run_identity=args.run_identity,
        role=PilotDatabaseConnectionRoleV1(args.role), software_commit=args.commit,
    )
    attestation = PilotDatabaseConnectionFactoryV1(
        frozen_pilot_database_config(name.value), args.password_file,
    ).attest()
    print(json.dumps({
        "applicationName": name.value,
        "applicationNameByteLength": attestation["applicationNameByteLength"],
        "showExact": attestation["showApplicationName"] == name.value,
        "currentSettingExact": attestation["currentSettingApplicationName"] == name.value,
        "pgStatActivityExact": attestation["pgStatActivityApplicationName"] == name.value,
        "databaseHost": attestation["databaseHost"],
        "databasePort": attestation["databasePort"],
        "databaseName": attestation["databaseName"],
        "databaseUser": attestation["databaseUser"],
        "serverVersion": attestation["serverVersion"],
        "fallbackAttempts": attestation["fallbackAttempts"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
