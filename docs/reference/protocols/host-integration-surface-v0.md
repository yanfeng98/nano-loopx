# Host 集成界面 v0

LoopX host 集成让 agent host 使用 LoopX 控制面，而无需成为第二个 LoopX 运行时。兼容基线仍是 CLI。Hook、MCP 与 server 适配器是同一 registry、active state、run 历史、quota、todo、gate、可选 lease 与公开/私有边界契约之上的薄门面。

v0 协议契约有意保持小：薄 hook 激活、生命周期读取、受控 todo/gate 写入、可选显式 lease 写入、紧凑状态投影、CLI 回退与公开/私有边界恒等式。它不证明任何适配器已安装，也不授予超出既有 CLI 等价 LoopX 生命周期的写权限。

Codex CLI slash 命令解析由 Codex CLI shell/技能覆盖：host 在普通聊天之前识别 `/loopx`、`/loopx <goal text>` 与 `/loopx-global-*`，然后交接给同一 CLI 支撑的生命周期。

## 角色

| 界面 | 工作 | 不得 |
| --- | --- | --- |
| Hook 激活 | 以当前 LoopX 生命周期契约启动 host Turn，并把 agent 路由到 `quota should-run`。 | 内嵌过期项目策略、调度隐藏工作或替换用户可见 TUI/控制界面。 |
| MCP 适配器 | 向已理解工具调用的 host 暴露读取与受控写入工具。 | 存储原始 transcript、绕过 LoopX CLI 语义或发明 host 特定权限规则。 |
| 回环 server 适配器 | 为本地 dashboard 或 host 运行时提供紧凑状态与受控写入端点。 | 默认远程绑定、发布私有状态，或使浏览器/frontstage/server 写入在无 CLI 等价 dry-run 的情况下权威。 |
| CLI 回退 | 在 hook/MCP/server 层缺失或不健康时，为每次读取与写入保留确定性路径。 | 除非用户显式选择，为 TUI 优先引导成为隐藏无头执行路径。 |

## 薄 Hook 激活

一个 host hook 只能激活当前 LoopX 生命周期。它应：

1. 解析 goal id 与已注册 agent id；
2. CLI 缺失时运行或指示 host 运行 `loopx doctor`；
3. 用共享全局 registry 读取 `quota should-run`；
4. 把得到的 `interaction_contract`、`goal_boundary` 与所选 `agent_lane_next_action` 传入 host Turn；
5. 用户 channel 需要具体问题或载荷 todo 时停止；并且
6. 把调度、配额花费与 writeback 留给正常 LoopX 生命周期。

Hook 正文应保持像生成的 heartbeat prompt 一样薄。项目策略属于 registry 元数据、active state、权威源与适配器输出。若 hook 需要项目特定分支，先把该情况当作 LoopX 产品缺口处理，再复制策略进 host 代码。

对于 Codex CLI /goal 可见 TUI 引导，hook 激活必须把可见 TUI 保持为主界面。它可以生成薄 `/goal` 正文或可复制 bootstrap 消息，但不得在没有可见证明与空闲检测契约的情况下静默切换到隐藏 `codex exec`、读取会话 transcript 或声称同 TUI 自动化。

## Ark Managed Agent host

`ark-managed-agent` 是一次性 goal host，不是 LoopX Turn 驱动器。LoopX 生成一个简短、传输中立的 goal prompt；Managed Agent goal 运行时拥有所有内部迭代与继续。

该 prompt 使用与 Codex CLI 可见 goal host 相同的 4,000 字符接口预算与受保护 goal 策略；只有 host 所有权前言不同。

用以下命令生成 prompt：

```bash
loopx heartbeat-prompt --thin --goal-id <GOAL_ID> --agent-id <AGENT_ID> \
  --runtime-profile ark_managed_agent_goal
```

同一契约通过 `--agent-type ark-managed-agent` 的一等 onboarding 可见。Onboarding 是只读验证器，不是安装器或安装前置条件。因为该 host 不使用 Codex 特定 skill 目录，与 Codex 共享的固定安装器把 LoopX workflow skills 写入 host 原生目标根。打包的 no-clone 路径是：

```bash
curl -fsSL \
  https://huangruiteng.github.io/loopx/install.sh \
  | env LOOPX_SKILLS_DIR=<PROJECT_WORKSPACE>/.agents/skills \
      LOOPX_ENTRY_HOST_SURFACE=ark-managed-agent \
      LOOPX_INSTALL_SLASH_COMMANDS=0 bash
```

对于贡献者 checkout，等价命令是：

```bash
LOOPX_SKILLS_DIR=<PROJECT_WORKSPACE>/.agents/skills \
  LOOPX_ENTRY_HOST_SURFACE=ark-managed-agent \
  LOOPX_INSTALL_SLASH_COMMANDS=0 \
  <LOOPX_CHECKOUT>/scripts/install-local.sh
```

这也是不信任或脏 checkout 的受支持 canary 路径。带显式 `LOOPX_SKILLS_DIR` 时，脚本物化发行所有的 workflow skills，包括生成的 `$loopx` 任务入口 skill，并写入 `.loopx-skill-install.json`，而不把 checkout 提升为默认 `loopx` 可执行文件。Managed Agent 的普通任务 Turn 以 `$loopx <task>` 开始；该 skill 在 host 恰好一次提交生成的 Goal 任务正文前写入业务 todo。Controller 不得预置该业务 todo。生成入口 skill 在安装时绑定精确 Managed Agent host，其 start-goal 事务在 bootstrap 检查期间保留该 host、任务文本与声明能力。无显式目标时，仅 canary 安装保持既有默认 skill 根不变。

安装器是 Codex 与 Ark Managed Agent 文件系统变更的唯一 owner。其默认目标是 Codex skill 根；Ark Managed Agent 提供 host 原生 `LOOPX_SKILLS_DIR` 并用 `LOOPX_ENTRY_HOST_SURFACE` 绑定生成入口。Manifest 记录已物化 skill id、来源修订与每 skill 内容摘要，使 `doctor` 与 onboarding 能只读验证投递，而不成为第二安装器。运行任一检查对安装是可选的。用相同 `LOOPX_SKILLS_DIR` 运行检查以报告文件系统回读状态与来源修订。文件系统物化不同于 host 的运行时已加载 skill 回读；在声称技能已注入活动 agent 上下文之前，后者仍然必需。

本地开发与云传输必须发送与 goal prompt 完全相同的 `task_body`。它们可以在端点、认证、会话 id 或线封包上不同，但这些字段不改变 prompt，也不成为 LoopX 策略。Host 没有自动化模式，且不得把每个内层 goal 迭代包装在 `loopx turn run-once` 中。

生成的 `host_contract` 声明激活发生一次、goal 运行时拥有继续、生命周期作用域是注册的 Goal 直到终态、不允许相位交接、host 会话状态非权威、LoopX Turn 驱动器不是必需的。有界投递段落是该 Goal 内的进展，不是在筛选、实现、评审或另一普通相位转换后用 successor host Goal 替换它的许可。持久化策略仍在当前 `quota should-run.interaction_contract`、active state、todos、vision 与 writeback 中。

对于 `--runtime-profile ark_managed_agent_goal`，同一配额读取还发出 schema 为 `goal_runtime_continuation_v0` 的 `scheduler_hint.goal_runtime_continuation`。其处置是 `continue_now`、`defer` 或 `complete`。推迟结果包含有界 `recheck_after_seconds` 与类型化 `wake_policy=state_change_or_deadline`：当持久化前沿写入改变同级 `scheduler_hint.reset_policy` 身份时 host 重跑 quota，或不晚于重新检查截止时间。继续包不重复该身份或 `scheduler_hint.reason_code`；它们的来源引用由 Host 契约声明。截止时间使到期的 monitor 在无推送信号时也可运行；provider 特定的 CI/review 观察仍归其 capability connector 所有。这是机器继续契约。Goal prompt 不被改写来教授等待策略，模型也不被用作机械轮询循环。

状态身份包括所选 Todo id、动作、目标、claim owner 与 capability 绑定引用。因此切换工作或准入权限即使在渲染推荐未变时也会唤醒 Goal；诊断笔记与其他非契约细节不产生唤醒。

当前沿携带显式 `next_due_at` 值时，截止时间是该最早精确到期时间。较粗的 host 节奏仍是自动化关注点，不得把 Goal 运行时唤醒推迟过该边界。

`defer` 是整前沿决策，不是每 PR 等待。安静 CI/review monitor 在任一独立推进 todo 可运行时保持辅助上下文，因此混合前沿投影 `continue_now`。只有无可执行推进、无到期 monitor 的前沿才可进入推迟唤醒策略。

依赖工作步骤只能在物化上游结果越过持久化边界后开始：更新当前 todo 证据与下一个可执行 todo 的任何 scope、验收或非 goal 增量，然后刷新状态并回读 quota。聊天/模型摘要不是持久化状态。

激活后发现运行时能力不会重新生成 Goal prompt。`quota should-run` 在 `interaction_contract.cli_channel.runtime_capability_reentry` 返回既有 `runtime_capability_reentry_v0` 包，并在 JSON 输出开头附近投影同一包为 `runtime_capability_reentry`。提前复制防止有界工具结果捕获把规范包藏在大诊断之后。

每个候选仍需要成功实时调用点观察，生成的重新进入命令才可声明该能力。后续 `next_cli_actions` 继承已验证会话能力；LoopX 不把该观察持久化为常驻权限授予。

该 host 上的 issue-fix 资格使用分阶段证据契约。已验证补丁证明 worker 路径，而 Goal 满意度必须从 host 单独读取。参见 [ark-managed-agent-issue-fix-qualification-v0](ark-managed-agent-issue-fix-qualification-v0.md)。

暂停、会话替换与模糊失败资格在 [ark-managed-agent-goal-continuity-qualification-v0](ark-managed-agent-goal-continuity-qualification-v0.md) 中定义。特别是，存活的 session id 或存在的 Goal journal 不足以声称恢复；替换 host 必须重建 LoopX 前沿，且 Goal 运行时必须证明 journal rehydrate 而无重复效果。

## 生命周期读取

Host 集成应暴露直接映射到 CLI 读取的读取方法：

| 能力 | CLI 基线 | 输出形状 |
| --- | --- | --- |
| 健康与安装 | `loopx doctor` | 紧凑就绪产品加缺失部分 |
| Registry 与 goal 边界 | `loopx registry` 与 `quota should-run` | goal id、适配器状态、写 scope、已注册 agent、停止条件 |
| 状态与关注队列 | `loopx --format json status` | 首屏状态、用户 todos、agent todos、gate 状态、新鲜度警告、可选只读投影如 `task_graph_projection_v0` 与 `local_agent_launch_plan_v1` |
| 配额决策 | `loopx --format json quota should-run --goal-id <goal-id> --agent-id <agent-id>` | `interaction_contract`、执行义务、工作区 guard、花费策略 |
| 评审包 | `loopx --format json review-packet --goal-id <goal-id>` | 人类/controller 决策包与 agent 交接上下文 |
| Run 历史 | `loopx history` 或状态投影 | 紧凑 run id、分类、结局、验证、blocker 指针 |

读取方法返回紧凑控制事实。它们不得返回原始会话日志、原始 benchmark 任务文本、原始轨迹、私有文档正文、凭据、本地绝对路径或 host 认证物料。`task_graph_projection_v0`、`local_agent_launch_plan_v1` 与 `cadence_hint_v0` 等可选投影是 host 集成的只读输入。它们不增加图写权限、不启动 worker、不改变 quota 关卡、不创建新事实来源。

## 受控写入

写入必须 CLI 等价、尽可能幂等，且 host 缺权限时失效关闭。Host 适配器可以暴露这些写入类别：

| 写入类别 | CLI 基线 | 必需 guard |
| --- | --- | --- |
| Todo claim 与生命周期 | `loopx todo claim/update/complete` | 已注册 agent id、active-state 文件锁、任务类别、存在时的活动 task-lease 执行键、可选带 `blocks_agent` / `unblocks_todo_id` 的 successor 交接 |
| 用户/agent todo 创建 | `loopx todo add --role user --task-class user_gate\|user_action` / `--role agent` | 公开安全文本、具体执行者、重复检测 |
| Gate 决策 | `loopx operator-gate --decision approve|reject|defer` | 显式 controller/用户决策、写入前 dry-run 预览 |
| 人类奖励 | `loopx reward ... --dry-run` 然后显式写入 | 绑定 run 的判定、公开安全原因、无分数冒充 |
| 软 claim 或可选硬 lease | 默认 `claimed_by`；host 需要硬写 scope 排斥时显式 `loopx task-lease acquire/renew/transfer/release/inspect` | `(goal_id, todo_id)` 竞争键；`task_lease_v0` 可选且不被 `quota should-run` 强制 |
| 状态刷新与配额花费 | `refresh-state`，然后 `quota spend-slot --todo-id <SELECTED_TODO_ID> --source heartbeat --execute` | 先验证证据、每个完成的自动 Turn 一次花费、绑定到所选 todo |

适配器不得把 host 批准、模型置信度、浏览器点击、frontstage 动作、server 回调或 scheduler 定时器翻译成受保护写入，除非相应 LoopX 契约允许该写入。浏览器/frontstage/server 写入默认保持非权威，除非回环 capability 广告 dry-run/预览端点且同一操作有 CLI 回退。

## 紧凑状态投影

面向 host 的状态投影应足够小，供 dashboard、hook 与 MCP 客户端使用：

```json
{
  "schema_version": "host_integration_surface_v0",
  "goal_id": "loopx-meta",
  "agent_id": "codex-side-bypass",
  "host_kind": "codex_cli_tui",
  "activation": {
    "mode": "thin_hook",
    "visible_surface_required": true
  },
  "lifecycle_reads": ["doctor", "status", "quota_should_run", "review_packet"],
  "projection_inputs": [
    "task_graph_projection_v0",
    "local_agent_launch_plan_v1",
    "cadence_hint_v0"
  ],
  "write_capabilities": ["todo_lifecycle", "gate_decision"],
  "optional_write_capabilities": ["task_lease_v0"],
  "cli_fallback": {
    "available": true,
    "required_for_writes": true
  },
  "boundary": {
    "raw_transcripts_copied": false,
    "credentials_copied": false,
    "private_paths_copied": false,
    "remote_bind_default": false
  }
}
```

该投影不是项目真相。它是 host 能力图加当前 LoopX 生命周期指针。Registry、active state、event ledger、todos、gates、quota 与可选 task leases 保持权威。Host 可以消费任务图或节奏投影，但那些投影保持派生的只读事实，绝不授予写权限。

## CLI 回退

每个 host 集成必须为同一操作文档化 CLI 回退。最小回退集：

```bash
loopx doctor
loopx --format json status --agent-id <agent-id>
loopx --format json --registry "$HOME/.codex/loopx/registry.global.json" quota should-run --goal-id <goal-id> --agent-id <agent-id>
loopx todo claim --goal-id <goal-id> --todo-id <todo_id> --claimed-by <agent-id>
loopx todo complete --goal-id <goal-id> --todo-id <todo_id> --claimed-by <agent-id> --evidence "<public-safe evidence>"
loopx refresh-state --goal-id <goal-id> --agent-id <agent-id>
loopx quota spend-slot --goal-id <goal-id> --todo-id <selected-todo-id> --slots 1 --source heartbeat --execute --agent-id <agent-id>
```

Host 显式广告 `task_lease_v0` 时，它也必须暴露等价 CLI 回退。获取硬 lease 不替换 todo claim、quota、capability、写 scope 或工作区 guard：

```bash
loopx task-lease acquire --goal-id <goal-id> --todo-id <todo_id> --owner <agent-id> --idempotency-key <turn-key> --write-scope <scope>
loopx todo complete --goal-id <goal-id> --todo-id <todo_id> --claimed-by <agent-id> --task-lease-idempotency-key <turn-key> --task-lease-expected-version <lease-version> --evidence "<public-safe evidence>"
```

获取键与返回版本构成执行实例围栏。生命周期写者不能仅依赖 `agent_id`，因为多个 host 进程可能共享一个已注册对等身份。有效 lease 存在时，`todo complete` 与 `todo supersede` 要求两个字段，在规范状态 writeback 期间持有 lease 锁，并在创建 successors 前拒绝缺失、过期或不匹配的围栏。Renew、transfer 与 release 也要求 `--expected-version`。Release 保留不活动终态记录，使后续 acquire 推进每 todo 版本与 `lease_epoch`，而不是重建版本 1。

Host 适配器不可用时，用户或自动化可以运行那些命令并保留相同状态迁移。Host 提供无 CLI 回退的操作时，该操作是实验性的，不得用作默认项目控制路径。

## 公开/私有边界

Host 集成必须保留这些恒等式：

- 原始 host transcript、原始工具输出、原始 benchmark 任务文本、轨迹、verifier 尾部、凭据、生产日志与本地私有路径留在 host 或私有项目存储中。
- LoopX 状态存储紧凑摘要、公开安全证据指针、决策标签、todo id、gate id、lease id 与 run id。
- 回环 server 默认本地绑定，且除非独立部署契约另有说明，拒绝远程写权限。
- MCP/server 工具必须把拒绝或缺失权限报告为结构化 blockers，而非绕过关卡猜测。
- Hook prompt 与适配器代码不得携带长项目特定策略分支；每 Turn 重新生成或读取当前 LoopX 状态。
- Codex CLI TUI 路径保持可见优先。隐藏无头执行只是显式回退，不是默认引导或同会话证明。

## 验收检查

一个 host 适配器在以下条件下可接受：

1. `quota should-run` 保持首个投递关卡；
2. 用户 channel 动作要求呈现具体用户 todos/问题；
3. 每个写入类别都有 CLI 等价命令，且当写入影响 gates、reward、leases 或浏览器触发动作时带 dry-run/预览；
4. 重复 todo claim、过期 lease、过期状态与 daemon 下线情况失效关闭或回退到 CLI；
5. 紧凑状态投影排除原始/私有物料，并把可选投影标记为只读输入而非权限；并且
6. 验证覆盖一个 hook 激活包、一次生命周期读取、一次受控写入预览、一条 CLI 回退路径与一个公开/私有边界陷阱。
