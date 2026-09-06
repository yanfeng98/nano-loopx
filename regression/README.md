# LoopX Regression Suite

此目录用于低频行为回归,检查 worker/executor 组件面如何消费 Goal Harness CLI 契约。

快速确定性示例留在 `examples/` 下。此处的文件在被显式要求时可以运行真实本地工具(如 Codex CLI),因此应在发布或重大控制面变更期间有意识地运行。

## 当前回归项

运行全部默认的仅契约回归:

为 LoopX 选择同一个 Python 3.11+ 运行时:

```bash
"${LOOPX_PYTHON:-python3}" regression/run-regressions.py
```

默认套件必须保持 public-safe 且依赖轻量:无真实 Codex CLI、Docker、私有 prompts、原始轨迹、原始日志、verifier 尾部或本地凭据材料。真实 agent 路径保留为显式的逐文件选择加入。

```bash
python3 regression/cli-command-module-contract.py
```

对第一个模块化 CLI 命令 seam 运行仅契约的兼容性检查。它导入 `loopx.cli_commands`,然后验证旧的公开 `doctor`、`new-project-prompt`、`demo`、`check`、`status` 与 `review-packet` 调用在注册/处理移出顶层 `cli.py` 文件后仍返回成功的 JSON 载荷。

```bash
python3 regression/blocked-priority-fallback-contract.py
```

针对人机协同模式运行仅契约的投影回归:一个更高优先级的 todo 被阻塞,但一个较低优先级的兜底是安全的。它检查 `quota should-run` 在结构性上保持被阻塞条目可见,而不捏造用户动作或通知,并仍在交互契约与协议包中选择安全兜底作为 agent 动作。

```bash
python3 regression/scoped-user-gate-fallback-contract.py
```

针对带范围用户关卡运行仅契约的投影回归:一个用户决策阻塞了匹配的 agent todo,但一个非依赖的可执行兜底仍可用。它检查 `quota should-run` 保持用户关卡的 `NOTIFY` 路径可见,同时仍要求 agent 执行选中的兜底,并且只在校验过的写回后消耗。它还检查纯散文用户关卡不会仅仅因为两个文本共享通用 benchmark 术语,就阻塞一个显式带范围的、无关的 agent 动作。

```bash
python3 regression/no-progress-self-repair-contract.py
```

运行自主的无进展自我修复契约。该包装器刻意复用 `examples/autonomous-replan-obligation-smoke.py` 而不是复制 fixture:重复的无进展信号应在又一次安静等待之前强制产生自主 replan/自我修复义务。

```bash
python3 regression/autonomous-replan-vs-dreaming-contract.py
```

运行自主 replan 与空想(dreaming)之间的仅契约分离检查。它创建紧凑的 `dreaming_exploration_proposal` fixture,并验证 status/quota 把它作为建议性的用户/控制器关卡暴露,不带 `agent_command`、不带自主 replan 义务、不带投递权限、不带 quota 消耗路径。它还验证紧凑的 `server_managed_planning_contract_v0` 投影:planning 可以对候选 todos 排序并建议证据探测,但不得执行受保护动作、读取私有材料、变更活动状态、追加投递历史,或在晋升前消耗投递 quota。

```bash
python3 regression/external-evidence-observation-real-codex.py
```

运行仅契约路径。它创建隔离的 LoopX fixture 并检查两个投影契约:

- 显式 `waiting_on=external_evidence` 的 goals 在观察或紧凑阻塞器写回之前返回投递被禁用的外部证据观察义务;
- 交给 Codex 的紧凑守卫/prompt 足以在不存在可观察 worker/controller 句柄时要求 `compact_blocker_writeback`,同时禁止安静 no-op 与 benchmark 执行;
- 已启动的、带紧凑结果轮询上下文的推进工作仍是一条有界投递通道,外部监视器被视为辅助上下文,而不是安静 no-op 的借口。

```bash
python3 regression/quota-executable-backlog-projection.py
```

在隔离 registry/runtime fixture 上运行 CLI 级 quota 投影回归。它检查:当 P0 外部监视器保持打开但未变化,而 P1 推进 todo 可执行时,`quota should-run` 把 P1 backlog 条目选为 `recommended_action`、交互主动作与协议包动作,同时保持监视器为上下文。它还检查当可见 `Next Action` 仍指向过期监视器动作时,载荷暴露状态动作投影警告。该回归保持 `refresh-state` 所有权分离:在没有显式替换时,它保留撰写的 `Next Action`,而 quota 对当前 Turn 中选择的可执行动作保持权威。

```bash
python3 regression/automation-loop-heartbeat-poll-contract.py
```

通过复用 `examples/control_plane/heartbeat-quota-flow-smoke.py` 运行自动化循环 heartbeat 轮询契约。它检查有界 heartbeat 投递只在校验过的状态写回后消耗,重复监视器轮询保持安静且不消耗,紧凑外部证据观察保持有界,并且投影警告把过期的 `Next Action` 文本路由到选中的可执行 todo 之后。

```bash
python3 regression/interaction-contract-state-machine.py
```

通过默认回归套件运行规范交互契约状态机 smoke。它保持用户通知、agent 投递、安静监视器、自主 replan 与 quota 消耗通道对齐,而不把 fixture 复制成第二个测试。

```bash
python3 regression/external-evidence-observation-real-codex.py --real-codex
```

另外以 `--ephemeral`、只读模式并带输出 schema 调用宿主 `codex exec`。这会消耗一次真实 Codex 运行,并验证 worker 把缺失的外部证据句柄解释为紧凑阻塞器写回,而不是安静 no-op 或 benchmark 执行。

真实路径默认为 `--codex-model gpt-5.4-mini`,因此它不依赖用户的 Codex CLI 默认模型。发布通道需要特定模型组件面时,用 `--codex-model <model>` 覆盖。

```bash
python3 regression/agentissue-lagent239-real-codex-runner.py
```

运行 AgentIssue-Bench `lagent_239` runner 的仅契约路径。它物化私有 runner 包装器,并在不调用 Codex 或 Docker的情况下,检查无生成器执行、选定图像、源码提取、入口 eval、紧凑 reducer 与凭据边界契约。

```bash
python3 regression/codex-app-server-goal-baseline-contract.py
```

运行仅契约的 Codex Goal benchmark 基线 seam。它验证首选自动化组件面是带 `experimentalApi=true` 的 Codex app-server `thread/goal/set` 加 `thread/goal/get`,`codex exec` 仍只是连通性 smoke,并且斜杠前缀 prompts 或 LoopX 状态泄漏不能被提升为成对基线证据。

```bash
python3 regression/codex-app-server-goal-baseline-contract.py --real-codex
```

可选地启动一个带隔离 `HOME` 与 `CODEX_HOME` 的真实本地 `codex app-server`,设置一个暂停的 goal,回读它,并只打印紧凑 public-safe 证据。这是显式的发布/调试探针,不属于默认套件。

```bash
python3 regression/agentissue-lagent239-real-codex-runner.py \
  --real-codex \
  --prompt-path <private-agentissue-prompt.md>
```

另外调用宿主 `codex exec` 与选中的 `alfin06/agentissue-bench:lagent_239` Docker 镜像。它只在临时私有回归根目录下写入原始 prompt、stdout/stderr 与 patch 产物,然后打印紧凑 public-safe 分数与边界摘要。
