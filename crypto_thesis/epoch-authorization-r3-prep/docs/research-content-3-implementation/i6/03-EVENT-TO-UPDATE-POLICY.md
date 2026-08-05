# Event-to-update Policy

Policy/epoch/status and recipient changes select `HEADER_ONLY` when Body and CK are unchanged. Body change or CK compromise selects `BODY_ROTATION`. A permanently revoked resource selects `NO_NEW_HEADER`. Unclassified causes select `POLICY_DECISION_REQUIRED` and fail closed.
