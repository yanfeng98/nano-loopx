#!/usr/bin/env python3
"""Smoke-check the decentralized auto-research protocol docs.

This guards the durable product contract: Arbor-inspired auto research must
remain LoopX-native and decentralized, with todo-linked hypotheses,
agent-scoped frontiers, split-aware evidence, and no public/private leakage.
"""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/reference/protocols/decentralized-auto-research-state-v0.md"
LANE_CONTRACT = ROOT / "docs/reference/protocols/auto-research-lane-contract-v1.md"
ROLE_STATE_MACHINE = ROOT / "docs/reference/protocols/auto-research-role-state-machine-v0.md"
ROLE_PROFILE = ROOT / "docs/reference/protocols/auto-research-role-profile-v0.md"
PROTOCOL_README = ROOT / "docs/reference/protocols/README.md"
BLUEPRINT = ROOT / "docs/product/use-cases/auto-research/decentralized-auto-research-showcase.md"


PRIVATE_MARKERS = [
    "byte" + "dance",
    "lark" + "office",
    "fei" + "shu.cn",
    "/" + "Users" + "/",
    "/" + "private" + "/",
    "api" + "_key",
    "pass" + "word",
    "sec" + "ret",
]


def _read(path: Path) -> str:
    assert path.exists(), f"missing {path}"
    return path.read_text(encoding="utf-8")


def _assert_public_safe(text: str, label: str) -> None:
    lower = text.lower()
    for marker in PRIVATE_MARKERS:
        assert marker.lower() not in lower, f"{label} leaks private marker {marker!r}"


def main() -> None:
    protocol = _read(PROTOCOL)
    lane_contract = _read(LANE_CONTRACT)
    role_state_machine = _read(ROLE_STATE_MACHINE)
    role_profile = _read(ROLE_PROFILE)
    protocol_readme = _read(PROTOCOL_README)
    blueprint = _read(BLUEPRINT)
    combined = (
        protocol
        + "\n"
        + lane_contract
        + "\n"
        + role_state_machine
        + "\n"
        + role_profile
        + "\n"
        + protocol_readme
        + "\n"
        + blueprint
    )
    compact_protocol = re.sub(r"\s+", " ", protocol)
    compact_lane_contract = re.sub(r"\s+", " ", lane_contract)
    compact_role_state_machine = re.sub(r"\s+", " ", role_state_machine)
    compact_role_profile = re.sub(r"\s+", " ", role_profile)

    _assert_public_safe(combined, "decentralized auto-research docs")

    required_protocol_terms = [
        "decentralized_auto_research_state_v0",
        "research_contract_v0",
        "research_hypothesis_v0",
        "research_evidence_event_v0",
        "decentralized_research_frontier_v0",
        "research_evidence_graph_v0",
        "agent_lane_next_action_v0",
        "claimed_by",
        "todo_id",
        "agent_id",
        "needs_retry",
        "held-out",
        "grounded_ideation",
        "novelty_audit",
    ]
    for term in required_protocol_terms:
        assert term in protocol, f"protocol missing {term!r}"
    for removed_term in (
        "auto_research_artifact_packet_v0",
        "research_showcase_projection_v0",
        "auto_research_public_claim_boundary_v0",
    ):
        assert removed_term not in protocol, f"protocol kept removed projection {removed_term!r}"
    assert "没有 agent 拥有完整研究树" in compact_protocol
    assert "auto_research_lane_contract_v1" in protocol
    assert "auto_research_role_state_machine_v0" in protocol
    assert "auto_research_lane_contract_v1" in protocol_readme
    assert "auto_research_role_state_machine_v0" in protocol_readme
    assert "auto_research_role_profile_v0" in protocol_readme

    required_lane_terms = [
        "auto_research_lane_contract_v1",
        "research_curator",
        "hypothesis_proposer",
        "research_executor",
        "evaluator_promoter",
        "product_narrator",
        "auto_research_lane_claim_v1",
        "research_contract_v0",
        "research_hypothesis_v0",
        "auto_research_evidence_packet_v0",
        "research_evidence_event_v0",
        "research_evidence_graph_v0",
        "quota should-run --agent-id",
        "首屏评审关卡",
    ]
    for term in required_lane_terms:
        assert term in lane_contract, f"lane contract missing {term!r}"
    assert "没有 lane 有特权" in compact_lane_contract
    assert "不是对完整图的锁" in compact_lane_contract
    assert "任何公开界面都不需要 leader 或协调者 agent" in compact_lane_contract

    required_role_state_machine_terms = [
        "auto_research_role_state_machine_v0",
        "auto_research_state_transition_v0",
        "研究 curator",
        "假设映射器",
        "研究执行者",
        "证据验证器",
        "常开角色集小",
        "转换职责",
        "只读投影构建器",
        "未来角色拆分",
        "Gate 管理人",
        "综合叙述者",
        "前沿保洁员",
        "contract_ready",
        "hypothesis_proposed",
        "frontier_selected",
        "attempt_running",
        "evidence_recorded",
        "evaluated",
        "promotion_gate",
        "quota should-run --agent-id",
        "operator_gate",
        "todo_id",
        "claimed_by",
        "没有一个拥有完整图",
    ]
    for term in required_role_state_machine_terms:
        assert term in role_state_machine, f"role state machine missing {term!r}"
    assert "不是协调者" in compact_role_state_machine
    assert "但不得自行启动 Codex、写入 LoopX 状态或花费配额" in compact_role_state_machine
    assert "未来版本可以" in compact_role_state_machine
    assert "v0 常开角色集之外" in compact_role_state_machine
    assert "提升任何未来角色都需要一次 smoke 更新" in compact_role_state_machine
    assert "Gate 处理是转换职责" in compact_role_state_machine
    for future_role in ("前沿保洁员", "综合叙述者", "Gate 管理人"):
        assert f"| {future_role} |" in role_state_machine, f"future split missing {future_role}"

    required_role_profile_terms = [
        "auto_research_role_profile_v0",
        "LoopX 控制面",
        "worker 局部角色 playbook",
        "AGENTS.md",
        "Host 启动器",
        "agent_id",
        "role_id",
        "phase",
        "capability_token",
        "allowed_actions",
        "write_scope",
        "protected_scope",
        "required_skill",
        "skill_section",
        "stop_conditions",
        "research_curator",
        "hypothesis_proposer",
        "research_executor",
        "evaluator_promoter",
        "loopx-auto-research",
        "quota should-run --goal-id",
        "Pane 标题是装饰性的",
    ]
    for term in required_role_profile_terms:
        assert term in role_profile, f"role profile missing {term!r}"
    assert "保持 playbook 有用，而不让它们成为第二身份来源" in compact_role_profile
    assert "身份来自 profile 与 quota/frontier" in compact_role_profile

    required_blueprint_terms = [
        "去中心化 Auto Research：k-NN 加速",
        "不是 LoopX 已经达成这些数字的声明",
        "Research Contract 卡",
        "去中心化 frontier",
        "Evidence 时间线",
        "晋升决策",
        "没有 leader agent",
        "auto_research_lane_contract_v1",
        "auto_research_role_state_machine_v0",
        "curator",
        "hypothesis proposer",
        "executor",
        "evaluator/promoter",
        "product narrator",
    ]
    for term in required_blueprint_terms:
        assert term in blueprint, f"blueprint missing {term!r}"

    forbidden_patterns = [
        r"single leader agent owns",
        r"leader agent owns the full",
        r"leader agent.*full hypothesis graph",
        r"central Coordinator owns",
        r"Coordinator owns the tree",
        r"Coordinator.*promotion decisions live",
        r"single agent owns the whole research tree",
        r"supervisor owns the full",
    ]
    for pattern in forbidden_patterns:
        assert not re.search(pattern, combined, re.IGNORECASE), (
            f"docs drifted toward centralized wording: {pattern}"
        )

    assert "没有 leader agent" in blueprint or "不是 leader agent" in blueprint
    print("decentralized auto-research protocol smoke passed")


if __name__ == "__main__":
    main()
