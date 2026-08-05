# Revocation Job Generation

An event/resource pair maps to one operation and one job. Database uniqueness covers event identity, operation ID, resource/version targets, and event-resource linkage. Conflicting duplicates fail closed; newer state supersedes stale work instead of writing an old Header.
