# Attempt atomic publish

All authority files are atomically written, parsed, hashed, and fsynced under `.staging-<attemptId>`. Only after database/Web3 attestation and preflight is the directory atomically renamed and marked `PUBLISHED`.
