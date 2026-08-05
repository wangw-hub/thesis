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
