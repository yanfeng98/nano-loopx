#!/usr/bin/env python3
"""Smoke-test durable interaction-pattern documentation coverage."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOG = REPO_ROOT / "docs" / "concepts" / "interaction-pattern-catalog.md"
STATE_MODEL = REPO_ROOT / "docs" / "state-interaction-model.md"
SELF_REPAIR_PATTERNS = (
    REPO_ROOT
    / "skills"
    / "loopx-self-repair"
    / "references"
    / "repair-patterns.md"
)


def require(text: str, snippets: list[str], *, source: Path) -> None:
    missing = [snippet for snippet in snippets if snippet not in text]
    assert not missing, f"{source}: missing {missing}"


def main() -> int:
    catalog = CATALOG.read_text(encoding="utf-8")
    state_model = STATE_MODEL.read_text(encoding="utf-8")
    repair_patterns = SELF_REPAIR_PATTERNS.read_text(encoding="utf-8")

    require(
        catalog,
        [
            "## 模式族",
            "| Work Routing |",
            "| Human Decision |",
            "| State And Boundary |",
            "| Evidence Lifecycle |",
            "| Planning Governance |",
            "## 可选 OM/HITL Overlay Schema",
            "human_ai_role_contract_v0",
            "ops_metric_overlay_v0",
            "escalation_failure_type_v0",
            "这些 overlay 是描述性和分析性的。",
            "这些 overlay 应保持可选，直到某个 UI 或 controller 路径消费它们。",
            "IP-027 | Deferred Gate Resume",
            "延迟 todos 表示停在恢复 gate 后面的闲置工作。",
            "就绪的延迟工作不是无候选状态。",
            "Human Decision / gate-resume 模式，而不是 no-todo 模式。",
            "IP-029 | Handoff Todo Gate State",
            "`blocks_agent` todos 不只是积压行。",
            "`todo_handoff_gate_v0`",
            "`cleared_without_successor`",
            "当前 Agent 的 `blocking` handoff 胜过过期的 done\nhandoff",
            "都是状态机 bug，不是提示措辞 bug。",
            "examples/control_plane/quota-cleared-blocker-successor-gate-smoke.py",
            "当一个用户 gate 携带 `blocks_agent=<agent-id>` 时",
            "Agent 作用域用户 gate 越界",
            "这不是 IP-026 作用域耗尽；",
            "examples/control_plane/quota-agent-scoped-user-gate-smoke.py",
            "docs/archive/incidents/agent-scoped-user-gate-overreach-incident-20260624.md",
            "IP-017 | User Reward Lesson Promotion",
            "IP-018 | Plan To Todo Writeback",
            "把纠正提升为持久教训",
            "面向用户的计划本身不是持久控制面状态。",
            "写回目标",
            "IP-022 | Claimed Todo Visibility And Agent-Lane Next Action",
            "同一作用域身份必须贯穿整个成功 turn。",
            "用相同 --agent-id refresh/spend",
            "不加 `--agent-id` 就 spend",
            "Todo 投影有两个职责，不应塌缩成一个列表：",
            "`current_agent_claimed_advancement_items`",
            "面向 Agent 的默认 lane 上限应保持克制",
            "IP-026 | Agent-Scoped No-Candidate Gap",
            "Agent 作用域 quota 必须区分\"目标有可运行工作\"与\"该 Agent 有可运行工作\"。",
            "没有当前 Agent 或未声明的就绪延迟恢复候选",
            "并且 IP-029 未找到当前 Agent 的应等待或 replan 的 handoff gate 状态",
            "如果唯一明显的 blocker 是一个 `blocks_agent` 指向不同 Agent 的用户 todo，\nIP-003 在 IP-026 之前拥有该情况",
            "IP-029 handoff gate 状态？",
            "`scope_exhausted`",
            "`agent_scope_wait`",
            "边界不能产生 `delivery_allowed=true`",
            "2026-06-21 的 monitor-only replan 停滞是这个模式的 canonical public-safe 坏用例。",
            "agent todo lane contains only monitor-style work",
            "no runnable todo, blocker, successor, supersede, or watch-lane expiry changed",
            "watch lane 可以保持可见，",
            "不能渲染为立即的 Codex delivery\n或用户/controller 批准 gate",
            "IP-023 | Status Neutral Run Window",
            "IP-025 | Experimental Diagnostic Sidecar Boundary",
            "实验性证明/调试 verdict 先是 sidecar 诊断。",
            "不属于 `protocol_action_packet_v0` 或常规 quota/status packet 形状。",
            "从 sidecar 晋升到稳定 schema 需要显式 schema 决策：",
            "`same_tui_visible_attach_accepted`\n或 `visible_session_proof_required`",
            "IP-028 | Connector Runtime Boundary",
            "Connector packet 必须在首次浏览器/API 运行前携带机器可读运行时策略。",
            "content_ops_connector_runtime_policy_v0",
            "browser_open_allowed_before_gate: false",
            "消息列表或消息详情 API",
            "UI 显示上限不得成为控制面推理窗口。",
            "## 目录维护与验证设计",
            "不要仅仅因为维护者需要\n一种验证技巧、smoke 组、发布清单、dashboard 卡片或上线流程，就添加一个新 IP。",
            "这些都是目录的用途，而不是目录模式本身。",
            "如果行为已被某个 IP 覆盖，就把新的 smoke、fixture、协议文档或视觉说明\n  加到该 IP 的验证或细节里",
            "因此 canary 与就绪组默认应参考目录，而不是扩张目录。",
            "但除非 canary 行为本身是未来 controller 必须路由\n的运行时/状态交互，否则不应成为独立 IP。",
            "fixture 级\n`loopx canary run` 检查当作第一层证据",
            "`loopx canary run` 默认必须无写：",
            "但不应写晋升证据、创建运行时契约、\n轮询外部目标，或运行深度/浏览器检查",
            "Replan 收尾是语义且因果绑定的。",
            "--replan-obligation-id",
            "host_action=end_current_heartbeat",
            "绑定到当前确切义务的语义收据",
            "分类散文、证据读取收据",
            "重算与 quota 相同的完整目标边界上下文。",
            "IP-024 | Repair Delta Contract",
            "成功的修复/replan 必须改变机器可见边界。",
            "应在远程开发机上跑，但 Codex 留在本地",
            "未来的 `user_reward_lesson_projection_gap`",
        ],
        source=CATALOG,
    )
    require(
        state_model,
        [
            "候选运维教训",
            "Codex stays local;\nthe remote host is only the execution substrate",
            "这是 gate-resume 模式，\n  不是 Agent 作用域无候选等待。",
            "仅聊天记忆不是可重放控制面信号。",
        ],
        source=STATE_MODEL,
    )
    require(
        repair_patterns,
        [
            "user_reward_lesson_projection_gap",
            "status_projection_history_neutral_gap",
            "monitor_replan_noop_loop",
            "agent_scoped_user_gate_overreach",
            "agent_scoped_no_candidate_gap",
            "deferred_gate_resume_misclassified",
            "handoff_gate_state_projection_gap",
            "plan_todo_writeback_gap",
            "connector_runtime_boundary_gap",
            "shell_pr_comment_command_substitution",
            "修正留在聊天/模型信念",
            "Agent 范围 quota 不区分\"goal 有可运行工作\"与\"该 peer 有可运行工作\"",
            "推迟工作被建模为 todo 缺失而非 gate-恢复生命周期条件。",
            "交接生命周期从打开 todo 通道推断而非小型状态机",
            "`todo_handoff_gate_v0`",
            "Agent 理解计划后把聊天当记忆；",
            "连接器安全活在散文或事后包字段",
            "Markdown 反引号通过双引号 `gh ... --body \"...\"`",
            "安全时用单引号正文，多行文本用 stdin 或 `--body-file`",
            "User-gate 投影把 agent 限定路由元数据当作诊断文本",
            "刷新状态使 `quota should-run` 选择修正规则",
        ],
        source=SELF_REPAIR_PATTERNS,
    )

    print("interaction-pattern-catalog-smoke: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
