"""Derive only public identity from the legacy tracked Besu key."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from eth_keys import keys


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    source = root / "blockchain" / "besu" / "scripts" / "prepare.ps1"
    text = source.read_text("utf-8")
    match = re.search(r'Join-Path \$rpcData "key"\).*?"(0x[0-9a-fA-F]{64})"', text)
    if match is None:
        raise RuntimeError("legacy RPC key assignment not found")
    private_bytes = bytes.fromhex(match.group(1)[2:])
    private = keys.PrivateKey(private_bytes)
    output = {
        "source_path": str(source.relative_to(root)).replace("\\", "/"),
        "source_role": "legacy controlled-development RPC node identity",
        "private_file_fingerprint_sha256": hashlib.sha256(private_bytes).hexdigest(),
        "ethereum_address": private.public_key.to_checksum_address(),
        "node_id": private.public_key.to_bytes().hex(),
    }
    print(json.dumps(output, separators=(",", ":")))


if __name__ == "__main__":
    main()
