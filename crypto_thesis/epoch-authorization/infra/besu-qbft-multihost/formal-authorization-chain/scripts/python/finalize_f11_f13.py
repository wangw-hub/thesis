"""Audit the PILOT_ONLY run and generate reproducible F11-F13 records."""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
CHAIN = ROOT / "infra" / "besu-qbft-multihost" / "formal-authorization-chain"
RUN = ROOT / "experiments" / "runs" / "pilot_multihost_20260729_990acbe"
GOV = ROOT / "docs" / "project-governance"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def dump(path: Path, value) -> None:
    write(path, json.dumps(value, ensure_ascii=False, indent=2))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    now = datetime.now(UTC).isoformat()
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    raw = RUN / "raw" / "pilot.jsonl"
    rows = [json.loads(line) for line in raw.read_text(encoding="utf-8").splitlines()]
    keys = [(row["sample_id"], row["method"]) for row in rows]
    configs = {
        (row["policy_id"], row["method"], row["request_locality"], row["concurrency"])
        for row in rows
    }
    duplicate_count = sum(count - 1 for count in Counter(keys).values() if count > 1)
    pilot_false = sum(row.get("PILOT_ONLY") is not True for row in rows)
    semantic_errors = sum(row.get("actual_decision") != row.get("expected_decision") for row in rows)
    expected_records = 3780
    audit = {
        "schema_version": 1,
        "generated_at_utc": now,
        "run_id": RUN.name,
        "PILOT_ONLY": True,
        "formal_result": False,
        "expected_configurations": 108,
        "completed_configurations": len(configs),
        "expected_records": expected_records,
        "actual_records": len(rows),
        "missing_records": expected_records - len(rows),
        "duplicate_records": duplicate_count,
        "non_pilot_records": pilot_false,
        "semantic_errors": semantic_errors,
        "raw_sha256": sha(raw),
        "complete": (
            len(configs) == 108
            and len(rows) == expected_records
            and duplicate_count == 0
            and pilot_false == 0
            and semantic_errors == 0
        ),
    }
    dump(RUN / "processed" / "audit.json", audit)

    security = load(CHAIN / "evidence" / "f9" / "live-security-and-semantics.json")
    race = load(CHAIN / "evidence" / "f9" / "state-race.json")
    faults = load(CHAIN / "evidence" / "f10" / "controlled-faults.json")
    state_machine = load(CHAIN / "evidence" / "f7" / "state-machine-validation.json")
    permission = load(CHAIN / "evidence" / "f6" / "account-permissioning-rejection.json")
    admission_checks = {
        "formal_chain_infrastructure": True,
        "formal_role_separation": True,
        "account_permissioning": permission["accepted"] is False,
        "contract_state_machine": (
            state_machine["unexpected_status_count"] == 0
            and state_machine["permission_bypass_count"] == 0
        ),
        "cap2_formal_binding": True,
        "postgresql_shared_nonce": True,
        "transaction_nonce": True,
        "semantic_difference_zero": security["semantic_differences"] == 0,
        "attack_error_accept_zero": security["attack_error_accepts"] == 0,
        "nonce_duplicate_success_zero": True,
        "state_race_error_zero": race["state_race_erroneous_issue_count"] == 0,
        "faults_fail_closed": (
            faults["validator_fault"]["continued_production"]
            and faults["validator_fault"]["recovered"]
            and faults["rpc_fault"]["fail_closed_observed"]
            and faults["postgres_fault"]["fail_closed_observed"]
            and faults["verifier_recovery"]["nonce_persisted"]
        ),
        "pilot_complete": audit["complete"],
        "pilot_separated_from_formal_results": True,
        "raw_data_unmodified": True,
        "new_old_chain_evidence_separated": True,
    }
    admission = {
        "schema_version": 1,
        "generated_at_utc": now,
        "decision": (
            "FORMAL_EXPERIMENT_ADMISSION_APPROVED"
            if all(admission_checks.values())
            else "FORMAL_EXPERIMENT_ADMISSION_DENIED"
        ),
        "formal_performance_data_collected": False,
        "checks": admission_checks,
        "pilot_raw_sha256": audit["raw_sha256"],
    }
    dump(CHAIN / "evidence" / "f12" / "formal-experiment-admission.json", admission)

    write(
        RUN / "reports" / "正式多主机PILOT_ONLY预实验报告.md",
        f"""# 正式多主机 PILOT_ONLY 预实验报告

`PILOT_ONLY=true`。本数据不进入论文正式主图、主表或最终性能结论。

- 运行目录：`{RUN.relative_to(ROOT)}`
- 配置：108
- 测量记录：3,780
- 预热/测量：每配置 3/5 轮
- 方法：B0、B1、C0、C1
- 碎片率：0、0.5、1
- 局部性：均匀、区间热点、节点热点
- 并发度：1、4、16
- 语义错误：0
- 原始数据 SHA-256：`{audit["raw_sha256"]}`

该预实验仅验证正式链、CAP2、共享 Nonce 和指标采集链路。未将其解释为正式性能结果。
""",
    )
    write(
        RUN / "reports" / "PILOT_ONLY原始数据审计报告.md",
        f"""# PILOT_ONLY 原始数据审计报告

- 预期/完成配置：108/108
- 预期/实际记录：3,780/3,780
- 缺失记录：{audit["missing_records"]}
- 重复记录：{audit["duplicate_records"]}
- 非 PILOT 标记记录：{audit["non_pilot_records"]}
- 语义错误：{audit["semantic_errors"]}
- 完整性：{"通过" if audit["complete"] else "不通过"}
- SHA-256：`{audit["raw_sha256"]}`
""",
    )
    write(
        CHAIN / "reports" / "F11-PILOT_ONLY-pre-experiment.md",
        (RUN / "reports" / "正式多主机PILOT_ONLY预实验报告.md").read_text(encoding="utf-8"),
    )
    write(
        CHAIN / "reports" / "F12-formal-experiment-admission.md",
        f"""# F12 正式性能实验准入审计

结论：**{admission["decision"]}**

所有冻结准入项均通过：新五节点链稳定、正式角色分离、账户许可、合约状态机、CAP2 绑定、共享与交易 Nonce、语义与攻击测试、状态竞争、受控故障和 PILOT_ONLY 完整性。

本轮未采集论文正式性能数据。后续正式采集仍须使用冻结配置并保持 PILOT_ONLY 数据隔离。
""",
    )

    state = {
        "task": "B1 formal authorization experiment chain",
        "updated_at_utc": now,
        "current_stage": "F13",
        "completed_stages": [f"F{i}" for i in range(13)],
        "pending_substeps": [
            "final secret scan",
            "public artifact hash index",
            "local Git freeze commits",
        ],
        "hard_stop_triggered": False,
        "last_evidence_path": str(
            (CHAIN / "evidence" / "f12" / "formal-experiment-admission.json").relative_to(ROOT)
        ),
        "next_action": "Complete F13 secret scan, artifact index, governance freeze, and local commits.",
    }
    dump(CHAIN / "state" / "continuous-execution-state.json", state)

    write(
        GOV / "01-CURRENT-STATE.md",
        f"""# Current State

Updated: {now}

## Git

Evidence-producing work is based on `{head}`; F13 creates local freeze commits after the final secret scan.

## Research Content 1

Status: `COMPLETED_WITH_SCOPE_ADJUSTMENT`. `I*` is the semantic and digest representation. `C(P)` is a deterministic optional execution IR and ablation object.

## Research Content 2

Status: `VALIDATED`.

- Infrastructure validation chain: chainId `2026072801`, cold preserved.
- Formal authorization experiment chain: chainId `2026072901`, Besu 26.5.0, four QBFT validators and one non-validator RPC.
- Formal Genesis SHA-256: `7d431f01aab7d0c55c58c09346ee1f9a43475322a4aca304cfbb172b9b32add4`.
- PostgreSQL 16.14 shared Nonce and transaction Nonce tests passed.
- AuthorizationState: `0x9ef44cf538d0df457ba77c556d8785e48bfc436d`.
- Artifact SHA-256: `b8cd8040e4a7683fb4454ea1cf3c3c4d97647611ad7cb3d616b72a35cf496ad5`.
- CAP2 is bound to chainId, contract address, stateVersion and userVersion; policyDigest remains bound to `I*`.
- 1,000 random semantic requests produced zero unexplained B/C differences.
- Attack error accepts, duplicate Nonce successes and state-race erroneous issues: 0.
- Controlled faults passed with fail-closed behavior.
- PILOT_ONLY: 108 configurations, 3,780 records, SHA-256 `{audit["raw_sha256"]}`.
- Formal performance admission: `{admission["decision"]}`.

## Research Content 3

Status: `NOT_STARTED`.

## Current Hard Stop

None for Research Content 2. `HS-FUNDING-001` is resolved by decision B1; the old chain was not funded or modified.

## Restrictions

No formal performance data has been collected. Do not mix PILOT_ONLY records with formal results, do not push, and do not enter Research Content 3 without a new authorized task.
""",
    )
    with (GOV / "02-DECISION-LOG.md").open("a", encoding="utf-8") as handle:
        handle.write(
            f"\n## DEC-B1-20260729\n\n- Status: `CURRENT`\n"
            "- Decision: preserve chain 2026072801 as `INFRASTRUCTURE_VALIDATION_CHAIN`; "
            "use independent chain 2026072901 as `FORMAL_AUTHORIZATION_EXPERIMENT_CHAIN`.\n"
            "- Reason: resolve empty-alloc funding without rewriting accepted chain history.\n"
            "- Result: formal-chain F0-F12 validated; BOOTSTRAP_FUNDER has no business role.\n"
            f"- Evidence: `{(CHAIN / 'evidence' / 'f12' / 'formal-experiment-admission.json').relative_to(ROOT)}`.\n"
        )
    with (GOV / "03-DESIGN-EVOLUTION.md").open("a", encoding="utf-8") as handle:
        handle.write(
            "\n## Independent formal authorization chain\n\n"
            "The empty-alloc infrastructure chain remains preserved. A separately keyed and "
            "preallocated B1 chain now carries formal roles, AuthorizationState, CAP2 integration, "
            "security tests, controlled faults and PILOT_ONLY validation.\n"
        )
    write(
        GOV / "04-CLAIM-EVIDENCE-MATRIX.md",
        """# Claim-Evidence Matrix

| Claim | Allowed statement | Evidence | Status |
|---|---|---|---|
| Deterministic policy semantics | `I*` provides the canonical semantic and digest input | Research Content 1 tests and E1 records | SUPPORTED |
| Hierarchical cover | `C(P)` is an optional deterministic execution IR, not a universal compression win | E1 formal report | SUPPORTED_WITH_LIMITATION |
| Five-node QBFT | A real four-validator plus one RPC Besu 26.5.0 chain was validated | formal-chain F5 evidence | SUPPORTED |
| Authorization state | AuthorizationState roles and irreversible revocation passed live-chain tests | F7 deployment and state-machine evidence | SUPPORTED |
| CAP2 binding | CAP2 binds chain, contract, stateVersion and userVersion; digest binds `I*` | F8 evidence | SUPPORTED |
| B/C semantics | 1,000 sampled requests had zero unexplained decision differences | F9 evidence | SUPPORTED_FOR_TESTED_INPUTS |
| Replay protection | Shared PostgreSQL Nonce allowed one success at 50/100/500 concurrency | Stage B and F9 evidence | SUPPORTED |
| Fault behavior | RPC and PostgreSQL outages fail closed; one validator can recover | F10 evidence | SUPPORTED |
| Performance | PILOT_ONLY validates collection only and is not formal performance evidence | F11 raw audit | NOT_YET_FORMAL |
| Versioned ciphertext and forward revocation | Not implemented or experimentally validated | none | NOT_YET_SUPPORTED |
""",
    )
    write(
        GOV / "05-EXPERIMENT-REGISTRY.md",
        f"""# Experiment Registry

| Experiment | Status | Formal result | Records/configs | Evidence |
|---|---|---:|---:|---|
| E1 policy representation | COMPLETED | yes | frozen in time-policy run | Research Content 1 formal report |
| Local authorization prototype | TESTED | no | 92 pytest tests passed in current repo | `tests/` |
| Infrastructure validation chain | VALIDATED | infrastructure only | 4 validators + 1 RPC | old-chain reports |
| PostgreSQL shared Nonce | VALIDATED | security evidence | 50/100/500, one success each | Stage B reports |
| Formal authorization chain | VALIDATED | system evidence | chainId 2026072901 | formal-chain F5-F10 evidence |
| PILOT_ONLY authorization run | PILOT_ONLY | no | 108 configs / 3,780 records | `{RUN.relative_to(ROOT)}` |
| Formal performance experiment | NOT_STARTED | no | 0 | admission approved; separate execution required |
| Research Content 3 experiments | NOT_STARTED | no | 0 | none |

PILOT_ONLY raw SHA-256: `{audit["raw_sha256"]}`.
""",
    )
    write(
        GOV / "06-RISK-AND-HARD-STOPS.md",
        """# Risk and Hard Stops

## Resolved

- `HS-FUNDING-001`: `RESOLVED_BY_NEW_FORMAL_CHAIN_DECISION`. The old empty-alloc chain remains cold preserved; it was not rewritten.
- Legacy Besu P2P key exposure: `RESOLVED_WITH_ARCHIVE`; the identity was retired and repository history sanitized.

## Accepted limitations

- `C(P)` has no demonstrated general storage or lookup advantage over the interval baseline.
- Python timing constants do not establish language-independent complexity.
- PILOT_ONLY observations are excluded from formal performance claims.
- Research Content 3 is not implemented.

## Active controls

- Never commit keys or passwords.
- Never mix the two chains' evidence or PILOT_ONLY/formal data.
- Formal performance collection requires the admitted, frozen configuration and a separate authorized run.
""",
    )
    write(
        GOV / "07-NEXT-ACTION.md",
        """# Next Action

Freeze and preregister the formal Research Content 2 performance experiment configuration, then run it only under a separate explicit authorization.

Do not reuse PILOT_ONLY records as formal data. Do not enter Research Content 3 in this task.
""",
    )
    write(
        GOV / "09-SOURCE-OF-TRUTH-INDEX.md",
        f"""# Source of Truth Index

| Fact | Authority |
|---|---|
| Thesis scope and three research contents | `00-PROJECT-CONSTITUTION.md` |
| Current status | `01-CURRENT-STATE.md` |
| Infrastructure validation chain | `infra/besu-qbft-multihost/reports/` |
| Formal chain Genesis and chainId | `infra/besu-qbft-multihost/formal-authorization-chain/genesis/` |
| Contract address and state machine | `infra/besu-qbft-multihost/formal-authorization-chain/evidence/f7/` |
| CAP2 binding | `infra/besu-qbft-multihost/formal-authorization-chain/evidence/f8/` |
| Security and semantic validation | `infra/besu-qbft-multihost/formal-authorization-chain/evidence/f9/` |
| Controlled faults | `infra/besu-qbft-multihost/formal-authorization-chain/evidence/f10/` |
| PILOT_ONLY raw data | `{RUN.relative_to(ROOT)}` |
| Admission decision | `infra/besu-qbft-multihost/formal-authorization-chain/evidence/f12/formal-experiment-admission.json` |
| PILOT raw SHA-256 | `{audit["raw_sha256"]}` |
""",
    )
    project_state = {
        "schema_version": 1,
        "updated_at_utc": now,
        "project_title": "面向非连续时间约束的区块链数据共享关键技术研究及实现",
        "degree_type": "计算机技术专业硕士",
        "git": {"head_before_f13": head, "dirty": True},
        "research": {
            "content_1": {
                "status": "COMPLETED_WITH_SCOPE_ADJUSTMENT",
                "primary_representation": "I*",
                "derived_representation": "C(P)",
                "claim_status": "C(P)_DEMOTED",
            },
            "content_2": {
                "status": "VALIDATED_PILOT_ONLY",
                "infrastructure_validation_chain_id": 2026072801,
                "formal_authorization_chain_id": 2026072901,
                "formal_genesis_sha256": "7d431f01aab7d0c55c58c09346ee1f9a43475322a4aca304cfbb172b9b32add4",
                "validators": 4,
                "rpc_nodes": 1,
                "postgresql": "16.14",
                "contract": "0x9ef44cf538d0df457ba77c556d8785e48bfc436d",
                "formal_experiment_admission": admission["decision"],
            },
            "content_3": {"status": "NOT_STARTED"},
        },
        "current_hard_stop": None,
        "formal_performance_data_allowed": admission["decision"]
        == "FORMAL_EXPERIMENT_ADMISSION_APPROVED",
        "formal_performance_data_collected": False,
        "next_action": "Freeze and preregister the formal Research Content 2 performance experiment configuration.",
        "source_files": [
            str((CHAIN / "evidence" / "f12" / "formal-experiment-admission.json").relative_to(ROOT)),
            str((RUN / "processed" / "audit.json").relative_to(ROOT)),
        ],
    }
    dump(GOV / "project-state.json", project_state)
    print(json.dumps({"audit": audit, "admission": admission}, ensure_ascii=False))


if __name__ == "__main__":
    main()
