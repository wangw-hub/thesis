CREATE TABLE IF NOT EXISTS consumed_nonces (
    chain_id BIGINT NOT NULL,
    contract_address BYTEA NOT NULL CHECK (octet_length(contract_address) = 20),
    resource_id TEXT NOT NULL,
    epoch BIGINT NOT NULL CHECK (epoch >= 0),
    nonce BYTEA NOT NULL CHECK (octet_length(nonce) = 16),
    verifier_id TEXT NOT NULL,
    consumed_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (chain_id, contract_address, resource_id, epoch, nonce)
);

CREATE TABLE IF NOT EXISTS ethereum_nonce_state (
    chain_id BIGINT NOT NULL,
    sender TEXT NOT NULL,
    next_nonce BIGINT NOT NULL CHECK (next_nonce >= 0),
    PRIMARY KEY (chain_id, sender)
);

CREATE TABLE IF NOT EXISTS ethereum_nonce_reservations (
    chain_id BIGINT NOT NULL,
    sender TEXT NOT NULL,
    nonce BIGINT NOT NULL CHECK (nonce >= 0),
    reservation_id TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK (status IN ('RESERVED', 'BROADCAST', 'CONFIRMED', 'FAILED')),
    transaction_hash TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (chain_id, sender, nonce)
);

ALTER TABLE consumed_nonces OWNER TO epoch_auth;
ALTER TABLE ethereum_nonce_state OWNER TO epoch_auth;
ALTER TABLE ethereum_nonce_reservations OWNER TO epoch_auth;
