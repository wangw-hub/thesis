from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from web3 import Web3

from .events import normalize_event


@dataclass(frozen=True)
class ScanResult:
    start_block: int
    end_block: int
    observed: int
    inserted: int
    duplicates: int


class AuthorizationEventScanner:
    """Finite block-range scanner. It never runs an unbounded service loop."""

    def __init__(self, w3: Web3, contract, repository, *, state_observer=None):
        self.w3, self.contract, self.repository = w3, contract, repository
        self.state_observer = state_observer

    def backfill_once(self, start_block: int, end_block: int) -> ScanResult:
        if start_block < 0 or end_block < start_block:
            raise ValueError("invalid bounded scan range")
        observed = inserted = duplicates = 0
        manifest = {item["name"]: item for item in self.contract.abi if item.get("type") == "event"}
        topic_to_name = {
            Web3.keccak(text=f"{name}({','.join(i['type'] for i in abi['inputs'])})").hex(): name
            for name, abi in manifest.items()
        }
        logs = self.w3.eth.get_logs({
            "address": self.contract.address,
            "fromBlock": start_block,
            "toBlock": end_block,
        })
        for raw in logs:
            name = topic_to_name.get(raw["topics"][0].hex())
            if name is None:
                raise RuntimeError("UNKNOWN_AUTHORIZATION_EVENT")
            decoded = getattr(self.contract.events, name)().process_log(raw)
            args = dict(decoded["args"])
            if self.state_observer is not None:
                self.state_observer(name, args, int(raw["blockNumber"]))
            event = normalize_event(
                chain_id=self.w3.eth.chain_id,
                contract_address=self.contract.address,
                event_name=name,
                event_signature=bytes(raw["topics"][0]),
                transaction_hash=bytes(raw["transactionHash"]),
                log_index=raw["logIndex"],
                block_number=raw["blockNumber"],
                block_hash=bytes(raw["blockHash"]),
                args=args,
            )
            observed += 1
            _, created = self.repository.insert(event)
            inserted += int(created)
            duplicates += int(not created)
        return ScanResult(start_block, end_block, observed, inserted, duplicates)
