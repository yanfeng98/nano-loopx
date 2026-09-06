# 默认工作流规划器缺口事件

> [English](default-workflow-planner-gap-incident-20260625.md)

日期:2026-06-25

读者对象:LoopX workflow 所有者、heartbeat 提示词生成器所有者、status/quota
所有者、connector 维护者,以及 onboarding 作者。

## 摘要

项目所有者希望在可见本地 UI 不再存在后,LoopX 仍能在开发主机上继续运行。
最终方案是成功的,但这是在 operator 和 agent 手动组装了若干组件之后:作用域
quota 防护、agent 身份、IM 或 gateway 入口、无头执行、monitor no-spend 行为、
就绪检查,以及主机级 keepalive。

坏例不在于用户回避了 TUI。TUI、无头 runtime、IM/gateway 入口和混合交接都是
合法的 LoopX 模式。坏例在于:LoopX 没有提供一个默认工作流规划器,能够根据
用户意图和主机能力选择并验证正确的模式组合。

## Public-Safe 形态

本事件在记录时不包含原始聊天消息、私有项目名、内部文档链接、主机名、本地
路径、凭据、服务单元或消息内容。可复用的形态是:

```text
user intent = keep LoopX working when the visible UI may be closed
available modes = visible TUI, headless runtime, IM/gateway intake, hybrid handoff
required invariants = scoped --agent-id, quota guard, no-spend quiet skip,
  durable intake, keepalive, readiness verification
bad interaction = user/agent must manually infer which mode owns each step
expected interaction = LoopX proposes a mode plan and validates it end-to-end
```

## 问题出在哪里

1. **运行时模式是隐式的。** 方案混用了可见 UI、无头执行、IM/gateway 入口
   和主机 keepalive,但 LoopX 没有把它们当作具有清晰转换规则的一等选择来命名。

2. **TUI 与无头被当作二元对立。** 真正的产品需求是一个模式矩阵:当用户想要
   时,TUI 可以保持持久的操作 surface;当主机需要在没有可见 UI 的情况下继续
   工作时,TUI 也可以交接给无头 runtime。系统不应硬编码任一种假设。

3. **身份与 quota 不变量很容易被遗漏。** 已注册 agent 的目标要求在防护、
   monitor 轮询、交付和 spend 记账中使用同样的作用域身份。没有工作流规划器,
   这只能靠 operator 记住的清单。

4. **主机存活状态发现得太晚。** Keepalive 细节(定时器、服务、cron 风格回退、
   锁、就绪探针)本身不是核心产品目标,但当用户要求开发主机连续性时,它们是
   运行时契约的一部分。

5. **No-spend monitor 语义不够可见。** 只有当用户能分辨"runtime 存活、没有
   打开的用户 todo、没有实质转换就不会烧配额"时,静默 monitor 等待才是健康的。

## 期望语义

LoopX 应暴露一个默认工作流规划器,把用户意图和主机能力检查转化为紧凑的模式
计划:

| 模式 | 适用场景 | 需要的证明 |
| --- | --- | --- |
| 可见 TUI | 用户想交互式观看或引导每个回合 | 活动 session、作用域提示词、quota 防护、清晰的 gate 处理 |
| 无头 runtime | 工作应在没有可见 UI 的情况下继续 | 作用域 agent 身份、运行前防护、no-spend monitor 行为、就绪探针 |
| IM/gateway 入口 | 用户想从聊天或其他外部 surface 创建工作 | 持久 todo 创建、文本/卡片回退、来源边界、用户 gate 投影 |
| 混合交接 | 一个模式应升级为另一个,或在另一个模式中继续 | 显式转换事件、目标模式就绪、共享 `--agent-id` 与状态写回 |

规划器绝不应从模式中推断生产权限、凭据访问或破坏性权威。它只选择运行时形态,
以及该形态可信之前所需的检查。

## 后续工作

### GH-C56:默认工作流规划器

为开发主机上的 LoopX 使用设计第一个默认工作流规划器。它应把可见 TUI、无头
runtime、IM/gateway 入口和混合交接建模为一等模式,然后从用户意图与主机能力
生成正确的作用域工作流。

### P1:模式计划 Fixture

添加一个 public-safe fixture,证明生成的计划携带 `--agent-id`,保留 no-spend
monitor 行为,并区分 TUI、无头、IM/gateway 与混合运行时选择。

### P1:就绪文案

Status 与 review packet 应以用户语言总结所选模式:正在运行什么、正在等待
什么、什么会唤醒它,以及什么需要可见的用户决策。

## 相关模式

- `IP-008 Monitor Quiet Skip`:静默 monitor 工作是关注通道,不是交付通道。
- `IP-022 Claimed Todo Visibility And Agent-Lane Next Action`:已认领工作
  与 monitor 通道应保持可见,但不应成为被选中的交付通道。
- `IP-028 Connector Runtime Boundary`:connector 或 gateway 运行时选择需要
  在读取外部材料之前有显式的允许/拒绝策略。
- `scheduler_liveness_backoff_gap`:主机调度器应遵循机器可读的 scheduler
  hints,而不是硬编码轮询循环。
