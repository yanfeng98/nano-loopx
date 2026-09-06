# Auto-Research 命令路径

本指南是从干净工作区运行 LoopX auto-research demo 的最短运营路径。它说明要运行什么、会出现哪些可见的数字员工、该检查哪些产物,以及如何停止或接管。

只有在这条路径清楚之后,才使用更深入的展示与协议文档:

- [Multi-agent 产品配方](../../../docs/guides/multi-agent-product-recipe.md)
- [停止、接管与状态感知唤醒漫游](../../../docs/guides/auto-research-stop-takeover-wake-walkthrough.md)
- [分布式 auto-research 展示](../../../docs/product/use-cases/auto-research/decentralized-auto-research-showcase.md)
- [auto_research_role_state_machine_v0](../../../docs/reference/protocols/auto-research-role-state-machine-v0.md)
- [auto_research_role_profile_v0](../../../docs/reference/protocols/auto-research-role-profile-v0.md)

实现边界:auto-research 是通用多 agent 内核之上的一个薄预设。`demo/auto_research/preset.py` 只拥有研究角色、交接提示、指标/证据循环默认值与 seed todo 措辞。通用内核拥有真实的 Codex TUI 面板、面板本地 A2A tick、工作区/信任安全启动、todo/evidence/status 协议与紧凑人工状态。面向开发者的配方证明也遵循该边界:`preset.py` 调用通用的 `multi_agent.recipe` 辅助函数,而不是自己定义分布式 A2A 证明机制。
新产品想复制该模式而不复制 auto-research 代码时,请使用[multi-agent 产品配方](../../../docs/guides/multi-agent-product-recipe.md)。

## 晋升决策

经过验证的可见证明晋升到这条现有命令路径,而不是第二个 auto-research runner。公开配方仍是:

- 运营方运行一条命令;
- 用户层只提供 topic、objective、轮数、推理 effort 与可选的角色覆盖;
- auto-research 预设提供研究角色、交接提示、seed todos 与证据默认值;
- 通用多 agent 内核提供 runner、唤醒、面板本地 tick、状态、附加、重试与停止机制。

只有当配置的角色以真实交互式 Codex CLI 面板打开、固定 prompt 唤醒让每个面板运行其本地 A2A tick、角色输出通过 LoopX todo/evidence/status 产物汇总,并且任何实时证据包都紧凑且 public-safe 时,可见证明才准备好进入这条路径。该证明不得依赖原始日志、私有产物、凭据、本地绝对路径,或藏在 auto-research 预设里的产品特定启动器。

## 用户契约入口

最小的用户可见 auto-research 契约是一个开放问题:

```bash
loopx auto-research "<open question>"
```

该命令不启动面板,也不声称研究已完成。它渲染可见多 agent 运行必须满足的固定契约:

- `research_brief`:已读什么、未读什么,以及结论边界;
- `action_plan`:P0/P1/P2 工作,最多五个 todos;
- `evidence_refs`:代码、文档、benchmarks、issues 与 pull requests;
- `next_executable_step`:下一步是否可以自动运行;
- `gate`:跨越边界前所需的确切用户判断。

这保持用户层与 auto-research 预设都很薄。用户提供一个开放问题;auto-research 提供固定输出契约;通用内核拥有 runner、真实 Codex TUI 面板、面板本地 A2A tick 与 todo/evidence/status 协议。

当运行必须以可验证交付物而非仅研究结论结束时,curator 写入 `auto_research_delivery_contract_v0`。该信封把原始愿望、假设、必需产物、验收标准、失败兜底与再入条件连同现有 `research_contract_v0` 一起保存。从该文件创建的证据绑定到其原子 `wish_id`、`contract_ref` 与 `contract_revision` 谱系;部分或不匹配的谱系不具验证资格。

在终态决策与任何必需的独立评审存在之后,构建只读交付 receipt:

```bash
loopx auto-research artifact-receipt \
  --contract delivery-contract.public.json
```

该 receipt 区分 `verified`、`partial`、`inconclusive`、`not_fulfilled` 与 `stale`。单次失败尝试永远不足以判定 `not_fulfilled`;该状态需要一个终态退役决策以及交付契约要求的任何独立评审。非验证 receipt 返回未满足的标准、验证边界、可用兜底产物与再入条件。

该契约还包含下一个一键启动组件面:

```bash
loopx auto-research start "<open question>" --execute
```

不带 `--execute` 时,`start` 返回与 dry-run preview 相同的契约锚定 runner 包。带 `--execute` 时,它创建一个隔离的研究边界,并通过通用多 agent 内核启动可见 Codex TUI 通道。启动器随后广播固定的面板本地 A2A 唤醒 prompt,让每个面板针对 LoopX quota/frontier 状态运行自己的 `$LOOPX_PANE_A2A_TICK`。研究证据必须由可见角色在做完真实工作后撰写。这仍然是分布式 A2A,不是工作流驱动:广播器不选择 todos、不运行 worker turns,也不写 LoopX 状态。
唤醒摘要是供面板读取的状态上下文,不是研究结果或跳过关卡。后续唤醒轮次仍要求每个角色检查自己的 LoopX 状态,并在有可运行工作时执行 tick。
固定唤醒是会话范围的:它指向所请求 tmux session 内稳定的面板通道元数据,并且不得从可变的 Codex 面板标题、过期面板或宿主上其他 session 推断工作。

对于首次可见 demo,优先采用 Codex CLI goal/面板驱动组件面加 LoopX 状态驱动边界。不要把它替换成隐藏的动态工作流驱动。启动器可以打开面板并广播固定唤醒 prompt,但依赖排序必须存在于正常的 LoopX todos、恢复关卡、quota 与 frontier 投影中。例如,evaluator 面板应通过一个可恢复 todo 等待 executor 证据,而不是在证据尚未落地时关闭自己的评审 todo。

用户仍然只提供一个开放问题;agent id、面板本地 tick 命令、证据 schema 与 runner 接线保持在内核内。想跳过默认可见角色唤醒、立即进入 tmux session 时,传入 `--attach`。
默认情况下,可见面板在 `~/loopx-auto-research/<run>/visible-workspace` 下的稳定用户自有工作区中打开,因此首屏不会落到生成的临时目录。用 `--workspace` 选择不同的临时目录。

## 从干净工作区开始

为可见 demo 使用用户自有目录,同时把 LoopX 状态保持在正常共享控制面中。这让研究临时文件与 LoopX 仓库分离,却让每条通道读取同一 registry、quota、todo、frontier 与 rollout-event 状态。为了最顺畅的首次运行,从 Codex CLI 已信任的目录开始,或从你拥有的一个普通非 git demo 目录开始。

```bash
mkdir -p loopx-auto-research-demo
cd loopx-auto-research-demo
export LOOPX_REGISTRY="$HOME/.codex/loopx/registry.global.json"
export LOOPX_RUNTIME_ROOT="$HOME/.codex/loopx"
```

必要时安装或修复 CLI:

```bash
curl -fsSL https://huangruiteng.github.io/loopx/install.sh | bash
export PATH="$HOME/.local/bin:$PATH"
loopx doctor
```

## 0. 证明 Worker-Loop 正向路径

最快诚实的正向检查是一问题启动路径。它播种一个全新 demo 本地 LoopX goal,让角色兼容的 workers 读取 quota/frontier 状态,默认打开可见 Codex TUI 面板,并让首个输出绑定到固定用户契约。它刻意很小,并且在提供紧凑实时证据包之前,不声称可见 Codex 通道撰写了研究结果。

运行正常人行路径并打开可见面板:

```bash
loopx --registry "$LOOPX_REGISTRY" \
  --runtime-root "$LOOPX_RUNTIME_ROOT" \
  auto-research start "How should we evaluate autonomous research agents?" \
  --execute \
  --replace-existing
```

该命令是 auto-research 的用户可见 UX。它默认创建一个全新的隔离 demo goal,启动可见 tmux 通道,广播固定的分布式 A2A 唤醒 prompt,并在用户接管前记录紧凑唤醒/tick 证据。每个 tmux 窗口应打开为真实交互 Codex CLI TUI 角色,而不是 JSON/状态流。通用启动器内部保持在 LoopX 内;运营方不需要知道 `demo-e2e`、agent id、唤醒标志或实现路径。

可见 Codex TUI 面板默认进入稳定的 `~/loopx-auto-research/<run>/visible-workspace`,而不是 demo 本地 git worktree 或生成的临时目录。demo registry、runtime root、队列与证据状态保持隔离,但首屏不应是生成 worktree 的信任提示。如果想要显式临时位置,传入 `--workspace "$HOME/loopx-auto-research-demo" --create-workspace`;避免把 `--workspace` 指向 demo 本地控制面目录。

当本 demo 是从更广泛的产品化 goal(如 `loopx-meta`)推进时,不要把 `--goal-id` 改成那个 meta goal。省略 `--goal-id` 得到隔离 demo goal;当你想让可见通道读取现有目标时,传入一个专门构建的研究边界 goal。只有当调用方需要元数据说明哪个父 goal 在跟踪产品工作时,才添加 `--tracking-goal-id loopx-meta`;跟踪元数据从不驱动可见通道边界。

如果想在打开可见 Codex 通道之前检查,先从只读 dry-run 开始。它告诉运营方哪条命令将运行多轮正向路径:

```bash
loopx --registry "$LOOPX_REGISTRY" \
  --runtime-root "$LOOPX_RUNTIME_ROOT" \
  auto-research start "How should we evaluate autonomous research agents?"
```

dry-run 看起来正确时,运行多轮正向路径:

```bash
loopx --registry "$LOOPX_REGISTRY" \
  --runtime-root "$LOOPX_RUNTIME_ROOT" \
  auto-research start "How should we evaluate autonomous research agents?" \
  --execute
```

该命令启动可见面板,用固定分布式 A2A prompt 唤醒每个面板,并让当前 shell 保持可取用紧凑 JSON 结果。要立即附加,改为传入 `--attach`;那意味着运营方先接管,并跳过默认可见角色唤醒:

```bash
loopx --registry "$LOOPX_REGISTRY" \
  --runtime-root "$LOOPX_RUNTIME_ROOT" \
  auto-research start "How should we evaluate autonomous research agents?" \
  --execute \
  --attach
```

对于仅 JSON 的自动化,把无头路径显式写出:

```bash
loopx --registry "$LOOPX_REGISTRY" \
  --runtime-root "$LOOPX_RUNTIME_ROOT" \
  --format json auto-research start "How should we evaluate autonomous research agents?" \
  --execute \
  --headless
```

可见面板默认为 Codex CLI TUI,并且在记录唤醒证据后,产品启动路径保持在当前 shell。面板本地的 `$LOOPX_PANE_LOOPX` 包装器用于该 TUI 内的人类可读 LoopX 命令,而 `$LOOPX_PANE_LOOPX_JSON` 保留给重定向的机器产物。原始 JSON 不应倾倒到首个可见屏幕;未来控制面可以单独渲染这些产物。

预期的极简 E2E 结果:

- 可见启动控件创建带角色本地引导 prompt 的真实 Codex TUI 面板;
- 每个面板可以运行 `$LOOPX_PANE_A2A_TICK` 读取自己的 quota/frontier;
- 默认 auto-research 预设下 `pane_local_a2a.worker_turn_configured` 为 `false`;
- 除非显式提供通道撰写的 public-safe 证据包,否则不声称任何 dev 或 holdout 指标;
- 可见启动控件与研究结果保持分离,只证明面板可被检查、停止或重试。

维护者对该路径的验收是:

```bash
python3 examples/auto-research-layered-e2e-acceptance-smoke.py
```

该 smoke 检查最短分层契约、可见 Codex TUI runner 契约、todo/frontier 路由与无伪造指标边界,而不让 auto-research 预设拥有通用 runner 机制。

具体的 KNN 可见命令:

```bash
loopx --format json auto-research start \
  "How can the KNN solver improve exact-neighbor speedup?" \
  --preset knn-demo \
  --language zh \
  --execute
```

`--preset knn-demo` 是公开信号,表示 LoopX 应物化一个小型生成的 KNN benchmark 工作区。可见面板获得仅一个可编辑文件 `solution.py`、受保护文件 `task.py`/`eval.py`/`eval.sh`,以及 `bash eval.sh dev` 与 `bash eval.sh test` 的真实命令。开放问题点名研究主题;它不通过自然语言推理把 benchmark 基线偷偷带入系统。

不带预设的通用路径同样可用:

```bash
loopx auto-research start \
  "How should we evaluate whether multi-agent auto research creates value?" \
  --execute
```

KNN 验收:

- 预设物化生成的 benchmark 工作区,而不是推断的自然语言基线;
- 面板按研究角色命名,而不是按后端 agent 实现名;
- 第一次 tick 是 quota/frontier/status,不是研究完成;
- 在可见角色撰写真实 public-safe 证据之前,不存在 dev/holdout uplift;
- 公开边界不记录原始日志、私有产物、凭据或本地绝对路径。

剩余边界:视频/展示证据应来自可见 Codex 面板执行研究工作。无头 smoke 能验证状态管道,但它不是"可见 Codex 面板撰写了研究结果"的声明。

对于维护者级演练,`demo-e2e --launch-visible --attach` 仍被接受为较低层命令。它不是用户可见产品路径;短的 `auto-research start "<open question>" --execute` 命令拥有默认可见角色唤醒行为。

```bash
loopx --registry "$LOOPX_REGISTRY" \
  --runtime-root "$LOOPX_RUNTIME_ROOT" \
  --format json auto-research demo-e2e \
  --agent-id auto-research-operator \
  --reasoning-effort high \
  --execute \
  --launch-visible \
  --launcher tmux \
  --attach
```

如果上一次可见演练仍存活,用 `--replace-existing` 重试,或先停止它:

```bash
tmux kill-session -t loopx-auto-research
```

一键路径不得记录原始日志、私有产物、凭据或本地绝对工作区路径。它只能写入可见角色撰写的 public-safe LoopX 状态。

## 1. 预览一键启动

默认用户路径从一个开放问题开始,在不启动进程的情况下预览可见 Codex TUI 通道包。

```bash
loopx --format json auto-research start \
  "How should we evaluate autonomous research agents?"
```

预览可接受时,启动可见通道:

```bash
loopx --format json auto-research start \
  "How should we evaluate autonomous research agents?" \
  --execute
```

可见通道使用 LoopX 状态作为 quota、frontier、todo 投影与 public-safe 证据。第一个面板 tick 只是守卫/frontier 读取;研究结果必须由可见角色撰写,而不是由隐藏 demo 指标循环。原始 JSON 只写入本地产物。较低层的 `demo-e2e` 命令对维护者仍可用,但它们不是用户可见入口。

## 2. 检查可见员工计划

supervisor 是宿主启动器,不是 leader agent。从 dry-run 包开始,在启动 Codex 前检查它。

```bash
loopx --registry "$LOOPX_REGISTRY" \
  --runtime-root "$LOOPX_RUNTIME_ROOT" \
  --format json auto-research demo-supervisor \
  --goal-id loopx-auto-research-demo \
  --workspace "$PWD"
```

默认的可见数字员工是:

| 面板 | 角色 | 它拥有什么 |
| --- | --- | --- |
| `research-curator:research-curator` | Research curator | 保持研究契约、受保护边界、指标、停止策略、证据评审与运营方关卡显式。 |
| `hypothesis-proposer:hypothesis-proposer` | Hypothesis proposer | 把想法转化为 todo 支撑的假设、后继链接与退役理由。 |
| `research-executor:research-executor` | Research executor | 在需要变更时,于隔离尝试边界内执行选定假设,并保留已评分或未评分证据。 |
| `evaluator-promoter:evaluator-promoter` | Evaluator/promoter | 检查 holdout/验证证据、分类结论,并保持晋升边界显式。 |

每个 Codex TUI 角色必须通过面板内自己的 quota/frontier/worker-turn 路径路由。supervisor 只让这些角色可见、可交互。面板共享同一 LoopX goal 组件面:registry、runtime root、frontier、todo 投影与证据图。不要把每个面板移入无关的空工作区;只用已认领的 git worktree 或等价执行边界隔离变更性的 research-executor 尝试。
可见 Codex TUI 面板应默认进入调用方工作区或显式的用户自有临时工作区。它们不应默认进入 demo 本地控制面仓库或生成的通道 worktree,因为那会在用户看到实际研究角色之前暴露工作区信任提示。

为兼容性或产品实验,`--agent` 仍可命名显式通道,包括单独的 evaluator-promoter 通道。

## 3. 运行 Worker Loop

可见面板应通过 heartbeat worker 使用的同一 CLI 路径做工作:每个 Turn 在写任何东西之前重新读取 quota、frontier、todo 投影与 rollout 证据。
用户终端应首先显示 Codex CLI TUI。当角色运行 LoopX 命令时,角色进度、选定 todo、动作与阻塞摘要应以正常 Codex 交互出现;原始 JSON 属于 `.public.json` 产物,不在首个可见屏幕上。

```bash
loopx --registry "$LOOPX_REGISTRY" \
  --runtime-root "$LOOPX_RUNTIME_ROOT" \
  --format json auto-research worker-loop \
  --goal-id loopx-auto-research-demo \
  --agent-id research-curator \
  --agent-id hypothesis-proposer \
  --agent-id research-executor \
  --agent-id evaluator-promoter \
  --max-rounds 4
```

dry-run 显示选定通道工作安全时,添加 `--execute` 与 `--complete-selected-todo`。这是最小的真实多 agent loop:它是状态中介的,不是隐藏 leader 工作流。

## 3b. 停止、接管与状态感知唤醒

运营方控制保持在这条命令路径上:

- 放置 `workspace/.loopx-auto-research-stop` 让下一个 worker-loop 轮次以 `stop_reason = operator_stop_requested` 退出(单个 `worker-turn` 调用对接管仍可用);
- 在 `auto-research start` 上传入 `--execute --attach`,可在无后台唤醒的情况下立即 tmux 接管;
- 想要跳过 quiet-completion、empty-frontier 或 quota-blocked 通道的状态感知唤醒时,传入 `--no-attach --wake-visible-after-launch`。

`--attach` 与 `--wake-visible-after-launch` 不能组合。完整的停止 → 接管 → 恢复循环及固定它的合成 smokes,见[停止/接管/唤醒漫游](../../../docs/guides/auto-research-stop-takeover-wake-walkthrough.md)。

## 4. 启动可见演练

tmux 可用时使用它,这样用户可以在一个地方观看多个 Codex CLI TUI:

```bash
loopx --registry "$LOOPX_REGISTRY" \
  --runtime-root "$LOOPX_RUNTIME_ROOT" \
  auto-research demo-supervisor \
  --goal-id loopx-auto-research-demo \
  --workspace "$PWD" \
  --execute \
  --launcher tmux \
  --attach
```

用户可以用以下命令停止 tmux 演练:

```bash
tmux kill-session -t loopx-auto-research
```

或者通过附加、中断面板并从可见 prompt 继续来接管一条通道:

```bash
tmux attach -t loopx-auto-research
```

## 5. 检查进度

有用的只读检查:

```bash
loopx --registry "$LOOPX_REGISTRY" --runtime-root "$LOOPX_RUNTIME_ROOT" status
loopx --registry "$LOOPX_REGISTRY" --runtime-root "$LOOPX_RUNTIME_ROOT" \
  --format json auto-research frontier --goal-id loopx-auto-research-demo \
  --agent-id auto-research-operator
```

当用户能识别活动假设、看到哪条通道拥有下一次转换、检查证据或重试理由,并在任何私有材料、凭据、受保护文件或生产动作发生之前停止或接管时,demo 是健康的。

## 边界

这条命令路径用于本地的、可见的、用户可接管的演练。它不是"研究结果已生产就绪"的声明,不是公开首屏审批,也不是发布私有证据的许可。晋升仍然需要 rollout 支撑的证据、相关时的 held-out 检查,以及正常的 LoopX gate/writeback 规则。
