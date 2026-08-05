"""Compile Solidity contracts and freeze ABI/bytecode artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import solcx

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "contracts" / "build"


def main() -> None:
    """Compile the fixed Solidity 0.8.30 sources."""

    sources = {
        str(path.relative_to(ROOT)).replace("\\", "/"): {"content": path.read_text("utf-8")}
        for path in (ROOT / "contracts").rglob("*.sol")
        if "build" not in path.parts
    }
    result = solcx.compile_standard(
        {
            "language": "Solidity",
            "sources": sources,
            "settings": {
                "evmVersion": "paris",
                "optimizer": {"enabled": True, "runs": 200},
                "outputSelection": {"*": {"*": ["abi", "evm.bytecode.object"]}},
            },
        },
        solc_version="0.8.30",
    )
    artifact = result["contracts"]["contracts/AuthorizationState.sol"]["AuthorizationState"]
    BUILD.mkdir(parents=True, exist_ok=True)
    (BUILD / "AuthorizationState.json").write_text(
        json.dumps(
            {
                "compiler": "0.8.30",
                "evm_version": "paris",
                "abi": artifact["abi"],
                "bytecode": artifact["evm"]["bytecode"]["object"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
