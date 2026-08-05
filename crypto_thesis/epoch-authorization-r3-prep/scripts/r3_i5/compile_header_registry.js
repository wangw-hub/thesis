const fs = require("fs");
const path = require("path");
const solc = require(path.resolve(".tools/r3-i5-solc/node_modules/solc"));

const sources = {
  "contracts/r3/HeaderRegistryV1.sol": {
    content: fs.readFileSync("contracts/r3/HeaderRegistryV1.sol", "utf8"),
  },
  "contracts/r3/interfaces/IAuthorizationStateFrozen.sol": {
    content: fs.readFileSync(
      "contracts/r3/interfaces/IAuthorizationStateFrozen.sol",
      "utf8",
    ),
  },
};
const input = {
  language: "Solidity",
  sources,
  settings: {
    optimizer: { enabled: true, runs: 200 },
    evmVersion: "london",
    metadata: { bytecodeHash: "ipfs" },
    outputSelection: {
      "*": { "*": ["abi", "evm.bytecode.object", "evm.deployedBytecode.object"] },
    },
  },
};
const output = JSON.parse(solc.compile(JSON.stringify(input)));
const errors = (output.errors || []).filter((item) => item.severity === "error");
if (errors.length) {
  throw new Error(errors.map((item) => item.formattedMessage).join("\n"));
}
const contract =
  output.contracts["contracts/r3/HeaderRegistryV1.sol"]["HeaderRegistryV1"];
const artifact = {
  compiler: solc.version(),
  evmVersion: "london",
  optimizer: { enabled: true, runs: 200 },
  abi: contract.abi,
  bytecode: contract.evm.bytecode.object,
  deployedBytecode: contract.evm.deployedBytecode.object,
};
fs.mkdirSync("contracts/r3/build", { recursive: true });
fs.writeFileSync(
  "contracts/r3/build/HeaderRegistryV1.json",
  JSON.stringify(artifact, null, 2) + "\n",
);
