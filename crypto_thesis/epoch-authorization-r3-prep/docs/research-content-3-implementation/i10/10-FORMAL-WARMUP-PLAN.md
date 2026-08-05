# Warmup Plan

Warmups are excluded from all statistics and are marked `WARMUP_ONLY`. Before measured runs, warm the JVM/Besu process, PostgreSQL connection and cache path, filesystem/object-store cache, Python process/import graph, Kubo connection pool, and network connection pool. One configuration warmup plus one environment warmup per service class is required; a warmup failure is handled by the frozen infrastructure policy and never silently counted as a measured RUN.
