# 多 Agent 产品配方


本指南是产品作者构建 LoopX 多 Agent 组合的路径，无需复制 auto-research 内部。
目标形态是：

1. **用户层：** 少数几个意图字段。
2. **产品预设：** 一个小的领域配方。
3. **多 Agent 内核：** 每个可复用 runner 与状态机制。

"以最少行数启动多 Agent auto-research"的公开承诺，是这个切分的强制函数。如果
auto-research 预设变成第二个 runner，仅把用户命令改短是不够的。用户层与产品预设
都必须保持薄，这样另一个产品可以用不同的角色列表、skill 片段与证据 Loop 复用
同一内核。

配合以下内容使用：

- [多 Agent 可见 launcher v0](../reference/protocols/multi-agent-visible-launcher-v0.md)
- [三层极简契约](../reference/protocols/multi-agent-three-layer-minimality-v0.md)
- [Auto-research 命令路径](../../demo/auto_research/README.md)

## 分层规则

| 层 | 通过"拥有什么"保持小 | 不得拥有 |
| --- | --- | --- |
| 用户 | 主题、目标、轮数、可选角色覆盖，以及可选的数据或 eval 入口。 | Tmux、Codex TUI 启动标志、pane 本地 tick 命令、quota/frontier 管道、机器 JSON 路由或角色 bootstrap 脚本。 |
| 产品预设 | 领域角色列表、agent 范围、交接/todo 提示、worker skill 片段、默认 seed todos，以及领域证据或指标 adapter。 | 通用多 Agent runner、真实 Codex TUI pane、工作区/信任安全启动、pane 本地 A2A tick、todo/evidence/status 协议、附加/停止/重试或 JSON 可见性策略。 |
| 内核 | 多 Agent runner、真实交互式 Codex pane、pane 本地 A2A tick、工作区/信任安全启动、todo/evidence/status 协议、紧凑人工状态、角色 prompt 脚手架与宿主生命周期控制。 | 研究、支持、benchmark、销售或其他产品专属语义。 |

如果第二个产品需要同样的代码，就把那部分代码移进内核。如果逻辑点名了领域结果、
领域角色、指标、artifact 类型或交接含义，就把它留在预设里。

## 产品预设形态

预设应当接近"数据加一两个小 adapter"。它不应构造 tmux 命令、Codex 调用字符串或
pane wrapper 脚本。

最小预设字段：

- `product_id`：稳定产品命名空间，例如 `auto-research`；
- `objective_fields`：产品接受的用户可见意图字段；
- `roles`：带 `agent_id`、`role_id`、`lane_id` 与 agent 范围的角色列表；
- `skill`：每个角色的小型 worker 本地 skill 片段或源码路径；
- `handoff_hints`：一个角色如何为下一角色创建或完成 LoopX todos；
- `seed_todos`：新 run 的首批 todo 标题或动作种类；
- `evidence_adapter`：若产品有带评分的证据，则为小型领域写回或指标 Loop。

产品配方示例：

```json
{
  "schema_version": "generic_multi_agent_launch_spec_v0",
  "goal_id": "loopx-demo-goal",
  "session_name": "loopx-product-team",
  "default_reasoning_effort": "high",
  "roles": [
    {
      "lane_id": "planner",
      "agent_id": "codex-main-control",
      "role_id": "planner",
      "scope": "Turn the objective into one bounded todo and a review handoff.",
      "skill": {
        "name": "product-planner",
        "source": "skills/planner/SKILL.md"
      },
      "handoff_hints": [
        "Create a LoopX todo for builder when the plan is ready."
      ]
    },
    {
      "lane_id": "builder",
      "agent_id": "codex-side-bypass",
      "role_id": "builder",
      "scope": "Claim the selected todo, execute the bounded work, and write evidence.",
      "skill": {
        "name": "product-builder",
        "source": "skills/builder/SKILL.md"
      },
      "handoff_hints": [
        "Complete the todo or create a focused review todo with compact evidence."
      ]
    }
  ]
}
```

内核把该 spec 展开为带角色 profile、受限 LoopX wrapper、`$LOOPX_PANE_A2A_TICK`、
仅 artifact 的机器 JSON 与 tmux 宿主控制的可见 launcher packet。
每个 pane 还从内核角色 prompt 收到通用的 `$loopx-project` 与 `$loopx-doc-registry`
skill 提示。产品 worker skills 不应复制那些通用项目/doc-registry 指令；它们只应
说明该角色如何决策、写证据与交接 todos。

## Worker Skill 片段

每个角色都应收到一个小型 worker 本地 skill。该 skill 解释领域行为，而非 runner
机制。

好的 skill 片段：

```markdown
# product-builder

Use when this pane has a selected builder todo.

1. Read your selected frontier through LoopX state.
2. Work only inside the selected todo and role scope.
3. Write public-safe evidence before completing the todo.
4. If another role should continue, create a focused LoopX todo and name the
   target role in the handoff hint.
```

不要把这些放进产品 skill：

- 如何启动 tmux；
- 如何运行 Codex；
- 如何编写 pane wrapper 脚本；
- 如何隐藏或重定向机器 JSON；
- quota/frontier/status 文件如何被路由；
- attach、stop、retry 或工作区信任如何实现。

这些是内核职责。

## 交接与 Todo 提示

产品预设应该用 LoopX 术语描述交接，而不是把它当作隐藏工作流引擎。角色可以：

- 写入紧凑证据后完成选中的 todo；
- 当下一角色已知时，用 `claimed_by` 或目标角色元数据创建后继 todo；
- 没有安全动作可用时留下阻塞理由；
- 为下一角色写入公开安全的证据指针。

预设不应直接调用另一 Agent、向另一 pane 注入文本或保留私有侧信道状态。Agent
通过读写共享 LoopX 状态界面协同：registry、runtime root、todo 投影、quota/frontier、
run history 与公开安全证据。

## 单命令启动

对于自定义组合，通用路径是：

```bash
loopx multi-agent launch \
  --spec ./multi-agent-spec.public.json \
  --workspace "$PWD" \
  --execute \
  --attach
```

对于 auto-research 预设，产品路径仍是：

```bash
loopx auto-research start "<open question>" --execute
```

两条命令都应打开真实的交互式 Codex CLI TUI pane。首屏应是角色 TUI，而不是原始
JSON、shell 流、隐藏 executor 或生成的工作区信任提示。

对 auto-research，一个已验证的可见证明只在证明保持该层切分不变时，才把现有预设
晋升为参考配方。操作者仍然得到一条命令，但固定 prompt 唤醒、pane 本地 A2A tick、
runner 生命周期、紧凑状态与公开 artifact 路由仍留在通用多 Agent 内核中。
auto-research 预设可以提供角色、交接提示、seed todos 与证据默认值；它绝不能为了
让 demo 看起来更短而长出私有 launcher 或隐藏工作流驱动器。

## 附加、停止、重试

每个可见多 Agent 产品都应暴露同样的宿主控制：

```bash
tmux attach -t <session-name>
tmux kill-session -t <session-name>
```

重试意味着在刷新 quota/frontier/bootstrap 状态后重跑产品命令。它不能重放过期的
隐藏 prompt，也不能假设先前 pane 仍具权威。仅当操作者有意要用同名会话替换时，
才使用 `--replace-existing`。

在任何 pane 内，用户可以中断角色并正常打字。该 pane 是真正的 Codex CLI Agent，
不是被动的日志查看器。

## 验收清单

一个新产品预设健康时满足：

- 用户可见入口是"意图加少量选项"；
- 预设定义角色列表、agent 范围、skill 片段、交接/todo 提示、seed todos 与可选
  evidence adapter；
- 预设导入通用多 Agent 内核，而不是复制 runner、TUI、tick、工作区、状态或 JSON
  策略代码；
- 每个可见 pane 都以交互式 Codex CLI TUI 启动；
- 每个角色的第一个动作是 pane 本地 A2A tick；
- 机器 JSON 写入公开 artifacts 或显式机器通道，而不是倾倒到首屏；
- todos 与证据是唯一交接权威；
- attach、stop 与 retry 无需产品专属宿主逻辑即可用；
- 晋升的 auto-research 证明，在 lane 作者证据被认领时，演示同一单命令可见路径，
  带真实 Codex TUI pane、固定 prompt 唤醒、pane 本地 A2A tick 与紧凑的公开安全
  实时证据；
- 原始日志、凭证、私有材料、绝对本地路径或生成记录不进入已提交的 docs 或夹具。

## Auto-Research 作为参考预设

Auto-research 应保持为参考预设，而不是内核。其预设拥有：

- 研究角色，如 curator、hypothesis mapper、evidence runner 与 verifier；
- 角色专属的允许动作；
- 研究交接提示；
- metric/evidence Loop 默认值；
- demo 的 seed todo 措辞。

它不应拥有：

- 多 Agent runner 生命周期；
- 真实 Codex TUI pane 启动；
- pane 本地 A2A tick 实现；
- 工作区信任处理；
- 通用 todo/evidence/status 协议；
- attach、stop、retry 或机器 JSON 可见性规则。

当 auto-research 需要新的通用能力时，先在多 Agent 内核实现，然后让
auto-research 预设通过小型角色或 evidence adapter 消费它。这是通往可复用、轻量
内核与小型推广示例的路径。
