#!/usr/bin/env python3
"""Smoke-check the goal vision/replan contract stays compact and reusable."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = ROOT / "docs" / "reference" / "protocols" / "goal-vision-replan-contract-v0.md"
PROTOCOL_INDEX = ROOT / "docs" / "reference" / "protocols" / "README.md"
DOCS_INDEX = ROOT / "docs" / "README.md"
STATE_MACHINE = ROOT / "docs" / "product" / "core-control-plane" / "state-machine.md"
RULE_SEAM = ROOT / "docs" / "product" / "core-control-plane" / "rule-seam-map.md"
THREE_LAYER = ROOT / "docs" / "reference" / "protocols" / "multi-agent-three-layer-minimality-v0.md"
SELF_REPAIR_SKILL = ROOT / "skills" / "loopx-self-repair" / "SKILL.md"
REPAIR_PATTERNS = ROOT / "skills" / "loopx-self-repair" / "references" / "repair-patterns.md"


PRIVATE_MARKERS = [
    "byte" + "dance",
    "lark" + "office",
    "/" + "Users" + "/",
    "/" + "private" + "/",
    "/" + "tmp" + "/",
    "api" + "_key",
    "pass" + "word",
    "client" + "_secret",
    "app" + "_secret",
    "secret" + "_key",
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
    protocol_index = read(PROTOCOL_INDEX)
    docs_index = read(DOCS_INDEX)
    state_machine = read(STATE_MACHINE)
    rule_seam = read(RULE_SEAM)
    three_layer = read(THREE_LAYER)
    self_repair_skill = read(SELF_REPAIR_SKILL)
    repair_patterns = read(REPAIR_PATTERNS)

    assert_public_safe(
        "\n".join(
            [
                protocol,
                protocol_index,
                docs_index,
                state_machine,
                rule_seam,
                three_layer,
                self_repair_skill,
                repair_patterns,
            ]
        ),
        "goal vision/replan docs",
    )

    require(
        protocol,
        [
            "goal_vision_replan_contract_v0",
            "CLI 预算",
            "`vision_summary` | 420",
            "`advancement_policy` | 32",
            "`total_agent_vision` | 1200",
            "以 `vision_budget_exceeded` 拒绝超预算写入",
            "不静默截断字段",
            "长推理属于证据工件或设计文档",
            "正常轻量 CLI 写边界是带内联 vision 补丁字段的 `loopx refresh-state`",
            "--vision-summary",
            "--vision-replan-trigger",
            "--vision-advancement-policy repeat_until_closed",
            "它默认为 `as_needed`",
            "显式 monitor successors 与 watch ACK",
            "`--agent-vision-json <packet.json>`",
            "两种形式互斥",
            "内联 vision 写入要求 `--agent-id`",
            "`goal_vision_patch` 修复增量",
            "goal_path_delta_v0",
            "而不增加更多内联 CLI 标志或展开 heartbeat prompt",
            "`continue`、`replan`、`wait`、`no_change`、`ask_human` 或",
            "`prior_assumption` 与 `observed_reality` 必需",
            "至少一个 `retained`、`changed` 或 `stopped`",
            "共享既有 1,200 字符 `total_agent_vision` 预算",
            "紧凑审计/读模型，不是第二规划器或新状态机",
            "每个 vision 包与检查点按 `agent_id` 作用域",
            "Vision 检查点",
            "`vision_checkpoint_v0`",
            "`missing_required` 不是聊天提醒",
            "`--vision-unchanged-reason`",
            "状态机",
            "ActiveVision --> VisionDriftDetected",
            "ReplanRequired --> ReplanDrafted",
            "VisionPatchProposed --> ActiveVision",
            "Replan 决策不得被 monitor 静默跳过",
            "坏例：被 Scheduler 记账隐藏的 ACK",
            "status 必须跨中性记账与 monitor 轮询 run 投影最新持久化 replan ACK",
            "无义务接受类型化语义增量的确认是",
            "`replan_noop`",
            "新具体 blocker",
            "覆盖背书的探索耗尽或 no-follow-up",
            "持久化 replan ACK 在物化前沿状态变更前存活中性 scheduler/记账 run",
            "Vision 继续审计",
            "`vision_continuation_audit_v0`",
            "Quota/status 在 CLI 载荷与 `interaction_contract` 中把它暴露为",
            "所选 todo 是活动每 agent vision 的有界步骤",
            "把弱、间接、过期或仅协议证据视为不完整",
            "公开 web 研究发现",
            "registry 声明",
            "`topic_authority` 与 `project_materials`",
            "注册指引发现；它既不授予访问也不证明验收",
            "`vision_gap_judge_v0` 指令包",
            "agent 被告知把活动 vision",
            "投影的必需读取",
            "`loopx evidence-log",
            "有界公开 web 研究",
            "`done=true` 只在响应或状态明确提供以下结局之一时有效",
            "带权威证据的显式完成",
            "完成的 todo 只是证据输入",
            "15 个以上推进 todos",
            "写/修正机制",
            "Vision 修正是正常状态机迁移",
            "物化 `refresh-state` closeout 发出每 agent `vision_checkpoint_v0`",
            "quota/status 与 `interaction_contract` 在 todo closeout",
            "前暴露 `vision_continuation_audit_v0`",
            "普通 `refresh-state` 调用可写有界 vision 修正",
            "缺失每 agent 检查点可以成为 agent 作用域 replan 缺口",
            "`quota.py` 消费所得投影，而非存储 vision 逻辑",
        ],
        source=PROTOCOL,
    )
    require(
        state_machine,
        [
            "Agent 愿景/重规划机器",
            "愿景按 `agent_id` 划分",
            "`vision_checkpoint_v0`",
            "必需的重规划在 monitor 安静跳过、有范围 gate 等待或单个 agent 的无候选状态之前评估",
            "没有愿景、todo、验收或不跟进增量的确认",
            "`vision_checkpoint_missing`",
            "约 15 个推进 todo",
            "在本地 evidence 不足以支撑公开声明时使用有界公开研究",
            "goal-vision-replan-contract-v0.md",
        ],
        source=STATE_MACHINE,
    )
    require(
        rule_seam,
        [
            "Agent 愿景与 goal 路由契约",
            "逐 agent 愿景检查点",
            "超预算愿景在 status/quota 之前失败或压缩",
            "实质性收尾发出 `vision_checkpoint_v0`",
            "配额只消费投影,不拥有逐 agent 愿景存储",
            "逐 agent 愿景是有界的 goal 路由契约",
        ],
        source=RULE_SEAM,
    )
    require(
        three_layer,
        [
            "逐 agent vision/replan 状态",
            "逐 agent vision 预算",
            "vision/replan 状态迁移",
            "preset 没有逐 agent vision/replan 机制的产品特定分叉",
        ],
        source=THREE_LAYER,
    )
    require(
        self_repair_skill,
        [
            "Vision / Replan 写回",
            "goal_vision_replan_contract_v0",
            "replan_trigger_summary",
            "使用与当前通道相同的 `--agent-id`",
            "`--agent-vision-json`",
            "`--vision-unchanged-reason`",
            "`vision_checkpoint_v0`",
            "goal_frontier_projection.acceptance_gaps[]",
            "不要把修正只留在聊天或事件记录中",
        ],
        source=SELF_REPAIR_SKILL,
    )
    require(
        repair_patterns,
        [
            "vision_replan_writeback_gap",
            "无 `goal_frontier_projection.acceptance_gaps[]`",
            "--agent-id <agent-id>",
            "--vision-unchanged-reason",
            "vision_checkpoint_missing",
        ],
        source=REPAIR_PATTERNS,
    )
    require(
        protocol_index,
        ["goal_vision_replan_contract_v0", "goal-vision-replan-contract-v0.md"],
        source=PROTOCOL_INDEX,
    )
    require(
        docs_index,
        ["reference/README.md"],
        source=DOCS_INDEX,
    )

    print("goal-vision-replan-contract-smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
