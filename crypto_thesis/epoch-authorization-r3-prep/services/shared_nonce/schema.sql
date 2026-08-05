CREATE TABLE IF NOT EXISTS consumed_nonces (
    chain_id BIGINT NOT NULL,
    contract_address BYTEA NOT NULL CHECK (octet_length(contract_address) = 20),
    resource_id TEXT NOT NULL,
    epoch BIGINT NOT NULL CHECK (epoch >= 0),
    nonce BYTEA NOT NULL CHECK (octet_length(nonce) = 16),
    consumed_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    verifier_id TEXT NOT NULL,
    PRIMARY KEY (chain_id, contract_address, resource_id, epoch, nonce)
);

CREATE INDEX IF NOT EXISTS consumed_nonces_cleanup_idx
    ON consumed_nonces (chain_id, contract_address, resource_id, epoch);
