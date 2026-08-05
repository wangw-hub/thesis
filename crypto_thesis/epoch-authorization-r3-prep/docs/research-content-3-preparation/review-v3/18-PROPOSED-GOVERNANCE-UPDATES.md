# 治理更新提案

本轮不直接修改主仓库治理文件。未来合并后建议：

- `01-CURRENT-STATE`：R3仍为 `PREPARATION_COMPLETE_AWAITING_ENTRY_DECISION`；I0/I1未执行；
- `02-DECISION-LOG`：登记 KeyStore A/B/C、推荐A、独立Header signer、CK记录和ROOT_KEK边界；
- `04-CLAIM-EVIDENCE-MATRIX`：软件托管仅为设计主张，待I1/I4/I7证据；不写HSM级能力；
- `05-EXPERIMENT-REGISTRY`：I1仍NOT_STARTED，不填性能结果；
- `06-RISK-AND-HARD-STOPS`：加入用户私钥进入服务端、CK明文入库、ROOT_KEK与DB同域、秘密经env/CLI、KeyStore夸大等停止项；
- `07-NEXT-ACTION`：用户先选择A/B/C；随后等待V13对账，再单独审批I0；
- `09-SOURCE-OF-TRUTH-INDEX`：登记review-v3决策、state与SHA清单；
- `project-state.json`：只在正式治理合并时更新，不由本分支假装批准。
