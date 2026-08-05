# 合约 Artifact 可复现性

- solc：`0.8.30+commit.73712a01.Emscripten.clang`
- EVM：London
- optimizer：enabled，runs=200
- HeaderRegistry Artifact SHA：`6a340049850453a41a02c571ce6c180ace336213da4ff13f25f44df441fc28d2`
- ABI SHA：`3816c251b5648368de4be28543b034af4b9b27092416f59c91ec263ca7f07148`
- bytecode SHA：`9019f8a236139a3742493585bc8994bf850ff0314acdd26e1b17d44eb00aef3e`
- deployedBytecode SHA：`e397b9040f68fe31c01b96d8be655e34bab0d38350c8da518977a04d7f662323`

两次默认 EVM 目标部署耗尽 gas 的失败回执被保留；明确 London 后成功，不以提高 gas 掩盖兼容性问题。
