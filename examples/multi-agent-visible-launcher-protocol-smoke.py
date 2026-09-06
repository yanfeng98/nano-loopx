#!/usr/bin/env python3
"""Smoke-check the generic multi-agent visible launcher protocol contract."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/reference/protocols/multi-agent-visible-launcher-v0.md"
THREE_LAYER = ROOT / "docs/reference/protocols/multi-agent-three-layer-minimality-v0.md"
LOCAL_PLAN = ROOT / "docs/reference/protocols/local-agent-launch-plan-v1.md"
AUTO_RESEARCH_PROFILE = ROOT / "docs/reference/protocols/auto-research-role-profile-v0.md"
AUTO_RESEARCH_GUIDE = ROOT / "demo/auto_research/README.md"
PROTOCOL_INDEX = ROOT / "docs/reference/protocols/README.md"
DOCS_INDEX = ROOT / "docs/README.md"


PRIVATE_MARKERS = [
    "byte" + "dance",
    "lark" + "office",
    "fei" + "shu.cn",
    "/" + "Users" + "/",
    "/" + "private" + "/",
    "/" + "tmp" + "/",
    "api" + "_key",
    "pass" + "word",
    "sec" + "ret",
]


def read(path: Path) -> str:
    assert path.exists(), f"missing {path}"
    return path.read_text(encoding="utf-8")


def require(text: str, snippets: list[str], *, source: Path) -> None:
    compact = " ".join(text.split())
    missing = [
        snippet for snippet in snippets if snippet not in text and " ".join(snippet.split()) not in compact
    ]
    assert not missing, f"{source}: missing {missing}"


def assert_public_safe(text: str, label: str) -> None:
    lower = text.lower()
    leaked = [marker for marker in PRIVATE_MARKERS if marker.lower() in lower]
    assert not leaked, f"{label} leaks private markers: {leaked}"


def main() -> int:
    protocol = read(PROTOCOL)
    three_layer = read(THREE_LAYER)
    local_plan = read(LOCAL_PLAN)
    auto_research_profile = read(AUTO_RESEARCH_PROFILE)
    auto_research_guide = read(AUTO_RESEARCH_GUIDE)
    protocol_index = read(PROTOCOL_INDEX)
    docs_index = read(DOCS_INDEX)
    changed_public_docs = "\n".join(
        [
            protocol,
            three_layer,
            protocol_index,
        ]
    )

    assert_public_safe(changed_public_docs, "multi-agent visible launcher docs")

    require(
        protocol,
        [
            "multi_agent_visible_launcher_v0",
            "local_agent_launch_plan_v1",
            "领域 capability",
            "不得成为 leader agent",
            "multi_agent_three_layer_minimality_contract_v0",
            "面向用户的 recipe 与领域 preset 都保持薄",
            "内核模块",
            "demo/multi_agent/",
            "generic_multi_agent_role_profile_v0",
            "multi_agent_three_layer_minimality_contract_v0",
            "紧凑人类状态",
            "的运行时脚本",
            "pane 级 A2A tick",
            "机器 JSON 包装器策略",
            "visible_multi_agent_launcher.py",
            "所有权拆分",
            "LoopX 控制面",
            "多 agent 可见启动器",
            "Host shell 或 App",
            "schema_version",
            "reasoning_contract",
            "default_reasoning_effort",
            "model_reasoning_effort",
            "shared_goal_surface",
            "LOOPX_REGISTRY_and_LOOPX_RUNTIME_ROOT",
            "agent 作用域 `quota should-run`",
            "todo 投影、前沿投影与 run 历史",
            "公开安全证据",
            "all_lane_workspace_isolation=false",
            "only mutating attempts require a claimed worktree",
            "role_profile",
            "quota_guard",
            "frontier",
            "bootstrap_message",
            "visible_launch_command",
            "reasoning_effort",
            "lane_timeline",
            "Pane 标题是装饰性的",
            "启动顺序",
            "把角色 profile、作用域 LoopX 包装器与 bootstrap prompt 准备为本地工件",
            "为每个角色窗口启动一个全新交互式 Codex CLI TUI",
            "让 Codex 角色通过 TUI 内的 pane 级 LoopX 包装器读取 quota/frontier/todo 状态",
            "Host 控件",
            "attach",
            "stop",
            "retry",
            "可见验收证明",
            "交互式 TUI 契约",
            "默认无额外 frontier/status JSON 窗口",
            "而非 `codex exec`",
            "不出现预 Codex 字符流",
            "边界",
            "hidden_prompt_injection",
            "public_safe_redaction",
            "领域适配器职责",
            "验收检查",
        ],
        source=PROTOCOL,
    )
    require(
        protocol,
        [
            "进程与写入字段必须保持 false",
            "LoopX 状态写入与配额花费仍在验证 writeback 后通过普通 agent lane 发生",
            "隔离只应用于变更文件的 lane 或尝试",
            "可见 Codex TUI pane 不得默认进入生成的演示局部 git worktree 或控制面仓库",
            "生成的 workspace trust 提示",
        ],
        source=PROTOCOL,
    )
    forbidden = [
        "launcher owns promotion decisions",
        "all lanes must use separate goal state",
        "may hide guard output",
        "is a hidden scheduler",
    ]
    for phrase in forbidden:
        assert phrase not in protocol, f"forbidden phrase present: {phrase}"

    require(
        three_layer,
        [
            "multi_agent_three_layer_minimality_contract_v0",
            "用户层",
            "Preset 层",
            "内核层",
            "user_and_preset_stay_thin_kernel_owns_reusable_mechanics",
            "目标不只是最小化用户的片段",
            "Auto-research 是通用内核之上的一个 preset",
            "复用同一内核",
        ],
        source=THREE_LAYER,
    )
    require(
        local_plan,
        [
            "local_agent_launch_plan_v1",
            "mode=dry_run",
            "它不得启动进程",
        ],
        source=LOCAL_PLAN,
    )
    require(
        auto_research_profile,
        [
            "Host 启动器",
            "可见 pane",
            "attach/stop 控件",
            "Pane 标题是装饰性的",
            "为每个角色启动一个全新交互式 Codex CLI TUI",
        ],
        source=AUTO_RESEARCH_PROFILE,
    )
    require(
        auto_research_guide,
        [
            "面板共享同一 LoopX goal 组件面",
            "隔离变更性的 research-executor 尝试",
            "每个 Codex TUI 角色必须通过面板内自己的 quota/frontier/worker-turn 路径路由",
            "应首先显示 Codex CLI TUI",
            "它们不应默认进入 demo 本地控制面仓库或生成的通道 worktree",
        ],
        source=AUTO_RESEARCH_GUIDE,
    )
    require(
        protocol_index,
        [
            "multi_agent_three_layer_minimality_contract_v0",
            "multi-agent-three-layer-minimality-v0.md",
            "multi_agent_visible_launcher_v0",
            "multi-agent-visible-launcher-v0.md",
        ],
        source=PROTOCOL_INDEX,
    )
    require(
        docs_index,
        ["reference/README.md"],
        source=DOCS_INDEX,
    )

    print("multi-agent-visible-launcher-protocol-smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
