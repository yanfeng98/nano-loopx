#!/usr/bin/env python3
"""Smoke-test the public issue-fix capability entry surface."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "loopx/capabilities/issue_fix/README.md"
CAPABILITY_INDEX = ROOT / "loopx/capabilities/README.md"
README = ROOT / "README.md"
REVIEWER_PROTOCOL = (
    ROOT
    / "loopx/capabilities/issue_fix/docs/protocols/issue-fix-reviewer-recommendation-v0.md"
)
REVIEWER_REQUEST_PROTOCOL = (
    ROOT / "loopx/capabilities/issue_fix/docs/protocols/issue-fix-reviewer-request-v0.md"
)
REVIEWER_NOTIFICATION_SINK_PROTOCOL = (
    ROOT
    / "loopx/capabilities/issue_fix/docs/protocols/issue-fix-reviewer-notification-sinks-v0.md"
)

PRIVATE_PATTERNS = (
    re.compile(r"/Users/[A-Za-z0-9._-]+/"),
    re.compile(r"/home/[A-Za-z0-9._-]+/"),
    re.compile(r"/private/"),
    re.compile(r"[A-Za-z]:\\\\Users\\\\"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._-]+"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
)


def assert_public_safe(text: str) -> None:
    for pattern in PRIVATE_PATTERNS:
        assert not pattern.search(text), pattern.pattern


def assert_markers(text: str, markers: tuple[str, ...]) -> None:
    for marker in markers:
        assert marker in text, marker


def main() -> int:
    guide = GUIDE.read_text(encoding="utf-8")
    capability_index = CAPABILITY_INDEX.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    reviewer_protocol = REVIEWER_PROTOCOL.read_text(encoding="utf-8")
    reviewer_request_protocol = REVIEWER_REQUEST_PROTOCOL.read_text(encoding="utf-8")
    reviewer_notification_sink_protocol = REVIEWER_NOTIFICATION_SINK_PROTOCOL.read_text(
        encoding="utf-8"
    )

    assert guide.startswith("# Issue-Fix 能力")
    assert "README.zh-CN.md" not in guide
    assert "[English](README.md)" not in guide
    assert "[issue-fix](issue_fix/README.md)" in capability_index
    assert "issue_fix/README.zh-CN.md" not in capability_index
    assert "loopx/capabilities/issue_fix/README.md" in readme
    assert "loopx/capabilities/issue_fix/README.zh-CN.md" not in readme

    shared_markers = (
        "issue_fix_repository_context_input_v0",
        "fix_pr",
        "comment_only",
        "triage_only",
        "loopx issue-fix reviewer-plan",
        "loopx issue-fix reviewer-request",
        "loopx issue-fix promote-discovered-issue",
        "loopx semantic-preference recall",
        "loopx lark-inbox collector-install",
        "loopx lark-inbox collector-status",
        "CODEOWNERS",
        "continuous_monitor",
        "runnable_successor",
        "https://github.com/volcengine/OpenViking/issues/3102",
        "https://github.com/volcengine/OpenViking/pull/3115",
        "https://github.com/volcengine/OpenViking/pull/3121",
        "https://github.com/volcengine/OpenViking/pull/3148",
        "https://github.com/volcengine/OpenViking/issues/3152",
        "https://github.com/volcengine/OpenViking/pull/3176",
        "https://github.com/huangruiteng/loopx/pull/1784",
        "https://github.com/huangruiteng/loopx/pull/1883",
        "https://github.com/huangruiteng/loopx/pull/1887",
        "resume_when=pr_merged:#123",
        "pr_merge",
        "issue_fix_reusable_knowledge_input_v0",
        "memory_verified_decision_influence",
        "positive-but-mixed",
        "5bfa9b617ecff478f825ca435a35bc4222b30582",
        "python3 examples/issue-fix-reviewer-recommendation-smoke.py",
        "python3 examples/issue-fix-reviewer-request-smoke.py",
        "python3 examples/issue-fix-discovered-issue-promotion-smoke.py",
        "lark-kanban sync-projection --reconcile-source",
        "--notification-sinks-json",
        "python3 examples/issue-fix-reviewer-notification-sink-smoke.py",
        "explore_graph.enabled",
        "explore_harness.enabled",
        "https://github.com/huangruiteng/loopx/pull/1991",
        "https://github.com/huangruiteng/loopx/pull/1995",
        "https://github.com/huangruiteng/loopx/pull/2000",
    )
    assert_markers(guide, shared_markers)
    assert_markers(
        guide,
        (
            "## 产品定位",
            "## LoopX 底座提供什么",
            "持久化 goal state",
            "Kanban/status 投影",
            "Quota 与 scheduler policy",
            "Authority 与 interaction gate",
            "## 端到端设计",
            "## 已实现能力面",
            "## Reviewer 路由 Contract",
            "## 人机交互模型",
            "## Roadmap",
            "## 成功指标",
            "## 对话式 `/loopx` 入口",
            "具体 blocker",
            "结构化 no-follow-up",
            "权限不足 comment fallback",
            "不会重复 comment",
            "项目专属",
            "## OpenViking 的公开用法与 Pilot 证据",
            "事件驱动的 wait/resume",
            "Merge 后自动恢复",
            "三条 OpenViking 知识通道",
            "Workspace-scoped user memory",
            "通用入站反馈",
        ),
    )
    assert reviewer_protocol.startswith("# issue_fix_reviewer_recommendation_v0")
    assert_markers(
        reviewer_protocol,
        (
            "仓库第一个受支持 `CODEOWNERS`",
            "变更路径",
            "最近 module 目录",
            "推荐不是指派",
            "automatic_review_request_allowed: true",
            "request_top_requestable_when_authorized",
            "review_request_performed: false",
            "python3 examples/issue-fix-reviewer-recommendation-smoke.py",
        ),
    )
    assert reviewer_request_protocol.startswith("# issue_fix_reviewer_request_v0")
    assert_markers(
        reviewer_request_protocol,
        (
            "request_top_requestable_when_authorized",
            "排除 PR author",
            "external_review_request",
            "写后验证",
            "仅权限 fallback 评论",
            "issue_fix_reviewer_comment_fallback_verified",
            "python3 examples/issue-fix-reviewer-request-smoke.py",
        ),
    )
    assert reviewer_notification_sink_protocol.startswith(
        "# issue_fix_reviewer_notification_sinks_v0"
    )
    assert_markers(
        reviewer_notification_sink_protocol,
        (
            "reader/user binding",
            "Sender/bot binding",
            "config_pointer_registered",
            "自动物化",
            "刻意是本地 capability",
            "lark_bot_group_access_required",
            "private_destination_captured",
            "python3 examples/issue-fix-reviewer-notification-sink-smoke.py",
        ),
    )

    for text in (
        guide,
        capability_index,
        readme,
        reviewer_protocol,
        reviewer_request_protocol,
        reviewer_notification_sink_protocol,
    ):
        assert_public_safe(text)

    print("issue-fix-capability-guide-smoke: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
