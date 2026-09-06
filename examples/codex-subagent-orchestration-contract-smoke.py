#!/usr/bin/env python3
"""Smoke-test the Codex sub-agent shared-control-plane contract."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "integrations" / "codex-subagent-orchestration.md"

REQUIRED_PHRASES = (
    "共享控制面",
    "subagent_control_plane_handoff_v0",
    "`parent_goal_id`",
    "`authority_artifact`",
    "`latest_state_ref`",
    "`quota_gate_snapshot`",
    "`evidence_boundary`",
    "`writeback_spend_contract`",
    "`child_decision`",
    "`continue`、`wait` 或 `reuse_existing_evidence`",
    "临时任务协调者",
    "子 worker 只报告证据;临时任务协调者写入已接受状态并进行消耗",
    "control_plane_handoff_version",
    "它不拥有持久的 goal 权威",
    "只有一个待处理租约",
    "`goal_id` 是共享控制面 lane",
    "`todo_id` 是被 claim 的工作项",
    '"agent_model": "peer_v1"',
    "独立 worktree",
    "`action_kind=review`",
    "休眠的注册 agent 以及已关闭、被阻止或 延期的 todo 都不是协调者候选",
)

FORBIDDEN_PHRASES = (
    "PRIVATE_HOME/",
    "lark" + "office.com",
    "~/.codex/sessions",
    "raw_thread",
    "session_history",
    "coordination.primary_agent",
    "primary-agent review todo",
    "side agents",
    "main controller",
    '"role": "controller"',
    '"role": "subagent"',
    "controller owns",
    "parent writes and spends",
)


def main() -> int:
    text = DOC.read_text(encoding="utf-8")
    compact = " ".join(text.split())
    for phrase in REQUIRED_PHRASES:
        assert phrase in compact, phrase
    for phrase in FORBIDDEN_PHRASES:
        assert phrase not in text, phrase
    assert text.count("subagent_control_plane_handoff_v0") >= 2, text
    assert text.count("## ") >= 7, text
    print("codex-subagent-orchestration-contract-smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
