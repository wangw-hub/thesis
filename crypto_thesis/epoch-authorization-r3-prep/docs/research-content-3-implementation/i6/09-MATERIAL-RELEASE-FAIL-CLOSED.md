# Material Release Fail-Closed

`AccessMaterialReleaseGuard` requires same-context equality of policy digest, epoch, and state version plus a valid Header object. A mismatch returns `HEADER_UPDATE_PENDING`; unavailable or invalid evidence returns `UNKNOWN`. Neither path releases access material.
