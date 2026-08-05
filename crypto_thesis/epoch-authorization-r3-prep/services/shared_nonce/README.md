# Shared nonce service

The formal design uses PostgreSQL because the unique primary key gives durable,
auditable, cross-process `consume_once` semantics. Apply `schema.sql`, then
construct `PostgresNonceStore` with a fresh database connection factory.

This directory is implementation-ready but not accepted until a real
PostgreSQL instance passes 50/100/500-way concurrent consumption, restart,
network-failure, cleanup, and cross-chain/resource isolation tests.
