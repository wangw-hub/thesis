# Recipient Index Rebuild

The recipient index is a cache. It is rebuilt only from a verified current
signed Header whose digest matches the HeaderRegistry anchor. The rebuilt
entries are deterministic. Missing or conflicting evidence prevents release.
