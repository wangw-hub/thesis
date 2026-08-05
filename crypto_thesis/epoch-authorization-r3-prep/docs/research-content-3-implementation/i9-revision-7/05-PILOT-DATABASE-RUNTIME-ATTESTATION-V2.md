# Pilot database runtime attestation V2

Each connection verifies exact equality among the client expectation,
`SHOW application_name`, `current_setting('application_name')`, and the
connection's `pg_stat_activity` row. It also checks character length, UTF-8
octet length, backend PID, database, user, port 55432, and PostgreSQL major
version 16.

Prefix matching, substring matching, 63-byte slicing, fixed common names, and
server truncation tolerance are prohibited. Any mismatch closes the connection
and fails closed.

