# Funding Review Lab

FUNDING_REVIEW_ONLY=true

The lab is isolated from the formal chain: it uses a separate runtime root,
loopback-only ports in the 41000/48000 ranges, generated temporary keys, and a
distinct chain ID. Runtime keys must remain outside the repository.
