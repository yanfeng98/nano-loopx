# DeepSWE 实践

本笔记归纳当前 DeepSWE 试点,不发布任务文本、案例特定轨迹、verifier 输出、凭据、本地路径、私有 runner 细节或不合格的分数结论。

## 研究问题

在两个 harness 臂下,把同一模型放在同一个固定的 DeepSWE 任务上比较:

- 基线:无 LoopX 状态或续接协议的原生 Codex Goal;
- 处理组:预注册的 LoopX 产品路径。

比较关乎 harness 价值,不是仅模型的排行榜结果。每个结论都限定在固定的任务集、runner、模型、权限、budget 与 verifier 内。

## 冻结选择与替换

在观察新结果之前冻结候选顺序。按该顺序以并发数一与预注册重试策略筛选基线案例。只有当基线尝试可计数、且其官方结局满足预注册选择规则时,候选才进入处理组批次。

基础设施、设置、agent 启动、终态收尾或 verifier 失败都不算评分任务失败。用冻结队列中的下一个案例替换不可计数的尝试。verifier 结果已告知控制器后不要重跑案例,也绝不要通过浏览原始任务或解决方案产物来选择替换项。

## 原生 Goal 证明

基线必须使用 Codex app-server Goal API,而不是 `codex exec`、第一个 token 是 `/goal` 的 prompt,或标成 Goal 模式的外层轮询循环。事务是:

```text
initialize(experimentalApi=true)
  -> initialized
  -> thread/start
  -> thread/goal/set(status=active)
  -> thread/goal/get
  -> turn/start
  -> observe correlated turn terminal event
  -> thread/goal/get
  -> while Goal remains active, observe the next automatic continuation turn
  -> stop only after Goal leaves active or the shared Goal timeout expires
  -> stop worker
  -> independent verifier
```

`turn/start` 接受不是完成。benchmark 宿主在排空 app-server 事件期间必须继续服务任何环境桥。它只启动初始任务 turn;当 Goal 保持活动时,Codex 拥有自动续接 turns。如果响应 turn id 与事件流 turn id 不同,则以事件流 id 为准。已安装的事务、stdio 传输、事件 reducer 与 receipt 位于
[`benchmark_toolkit.native_codex_goal`](../../loopx/capabilities/benchmark_toolkit/native_codex_goal.py) 中。
[`../native_codex_goal.py`](../native_codex_goal.py) 有意只是一个兼容导入,因此 runner 代码与示例不会漂移成第二个实现。

### 真实 Codex 连接

可运行示例调用 `codex app-server --listen stdio:// --enable goals`,执行上面的事务,并只打印一个紧凑 receipt。把 objective 与 task 放在文件中,以免原始文本被复制进命令历史:

```bash
python benchmark/deepswe/run_native_codex_goal.py \
  --cwd <task-worktree> \
  --objective-file <objective.txt> \
  --task-file <task.txt> \
  --model <model-route>
```

用 `--preflight-only` 验证 initialize、thread 创建与 Goal 附加,而不启动模型 turn。在 Linux 上,同一个可运行程序可以选择加入 toolkit 的宿主文件系统边界:

```bash
python benchmark/deepswe/run_native_codex_goal.py \
  --cwd <task-worktree> \
  --objective-file <objective.txt> \
  --task-file <task.txt> \
  --isolate \
  --isolation-work-dir <runner-created-per-run-dir> \
  --private-root <controller-private-root> \
  --profile-root <per-run-installed-profile>
```

隔离是显式的;默认调用保持不变。工作目录必须在私有根与任务工作区之外。可选 profile 是可写进程输入,因此请每次运行创建它或从固定的快照恢复,而不是跨试验共享。使用确定性的每运行工作目录:如果 worker 在正常清理前被杀掉,下一次相同调用会在启动前修复过期的 workspace 别名引用,并在退出时恢复宿主路径。

当任务本地 LoopX 控制状态存在时,`.loopx/registry.json` 与 `.loopx/runtime/registry.global.json` 必须都存在。两个文件都不存在意味着没有需要搬移的控制状态;只有一个文件被视为不完整状态并失败关闭。

benchmark adapter 可以直接复用同一运行时,同时保持其环境桥在另一个任务中活动:

```python
from loopx.capabilities.benchmark_toolkit.native_codex_goal import (
    NativeGoalConfig,
    run_native_goal_process_until_terminal,
)

turn = run_native_goal_process_until_terminal(
    NativeGoalConfig(
        cwd=task_worktree,
        objective=objective,
        task_instruction=instruction,
        model=model,
        sandbox_policy=runner_owned_sandbox_policy,
    ),
    process_command=runner_owned_isolated_app_server_command,
    process_env=runner_owned_environment,
    process_cwd=runner_control_directory,
    goal_timeout_sec=timeout_seconds,
)
```

导入的运行时不拥有评估器访问、任务命令桥、凭据策略或分数权威。这些仍然显式是 runner 的职责。当 Goal 可见的 `cwd` 只存在于 runner 的挂载命名空间内时,单独的 `process_cwd` 很有用。

处理组还需要三个独立的产品路径证明:

1. 为 `codex_app_ssh_goal` profile 生成的 Goal 正文;
2. LoopX skills 安装进 app-server 使用的确切 `CODEX_HOME`;
3. 该 Goal 正文点名的 LoopX 发布快照 CLI。

用 `benchmark_toolkit.native_codex_profile.install_native_codex_profile` 准备后两项。不要把 `SKILL.md` 文件复制进 runner 镜像。用 `render_native_codex_goal_prompt` 生成第一项输入,让 app-server 保持在无凭据的 `native_codex_profile_environment` 上,并通过 `serve_runner_owned_provider_gateway` 路由其 provider。app-server 只接收 gateway URL 与一个固定的非密钥 env sentinel。Linux 宿主侧 worker 也必须运行在 `native_codex_isolation` 内;仅过滤子进程 env 并不能阻止 danger-full-access agent 读取父进程环境或环境中的 HOME 文件。`native_codex_app_server_shell_policy_args` 仍是为模型创建的 shell 提供的纵深防御,而不是凭据边界。设置 `NativeGoalConfig.required_skill_ids=profile.required_skill_ids`。运行时随后在 thread 创建之前使用 `skills/list`,并且除非 Codex 实际发现已安装的 skill 集,否则在模型工作之前失败。仅文件系统检查不是处理保真证据。

## 权威与反作弊

两个臂获得相同的任务可见文件系统、网络、sandbox、批准策略、模型凭据信封与工具 surface。两个臂都不得读取:

- 评估器答案、隐藏引用、verifier 源码或预期补丁;
- 另一次试验的工作区、状态或轨迹;
- 控制器私有 manifest 或证据;
- agent 阶段的官方 reward 或 verifier 反馈。

私有结构化审计把观察到的工具访问对照 runner 自有的隔离证明。公开 receipt 只包含稳定标签、计数、摘要与原因码。完整性资格判定与处理保真是独立的关卡:处理组未执行预注册 LoopX 路径时,一次干净运行仍可能不可计数。

## 预检与生命周期

每次启动前,无 agent 预检必须证明:

- 固定的 runner 与任务集 revision;
- 确切的案例与臂身份;
- 模型、effort、时间、token、并发与重试信封;
- 答案/verifier 拒绝与跨试验隔离;
- 不上传、不提交策略;
- 从固定 revision 读回的正式已安装 LoopX CLI 与 skill;
- 真实 app-server 对必需 LoopX skills 的发现;
- worker 先于 verifier 的顺序;
- 当并发任务可以共享镜像时,在运行时隔离检查之前确定任务与容器的绑定;
- 紧凑结果与终态收尾目的地。

runner 拥有任务执行与 verifier 调用。LoopX settlement 只在控制器验证紧凑终态结果之后发生。成功的状态写入、Todo 转换或 quota 消耗不能把无效的 benchmark 尝试变成证据。

## 公开证据

记录足够紧凑的信息来复现分类,而不暴露受保护材料:

- manifest 与 runner revision 摘要;
- arm、模型、effort、budget、重试与权限标签;
- 生命周期阶段与失败归因;
- 原生 Goal 方法/状态证据;
- 完整性与处理保真判定;
- 只在独立评分与可计数性检查之后的官方分数。

把原始任务、轨迹、工具参数、日志、diff、凭据、verifier 输出、私有审计引用与本地路径留在被忽略的私有存储中。只有在匹配研究足够扎实、能支撑所声明的结论级别后,才提升具体结果表。

### 公开轨迹生命周期摘要

可运行的原生 Goal adapter 现在在其现有紧凑 receipt 旁边发出一个嵌套的 `public_trajectory_summary_v0`。该摘要只从 receipt 的类型化 Goal 生命周期计数器推导:通知类型、条目事件计数、完成的 turns、续接 turns、错误事件与 Goal 状态轮询。`goal_terminal` 意味着 adapter 观察到一个完成的 turn,然后读到一个非活动 Goal 状态;`attached`、`in_progress` 与 `turn_terminal` 仍显式不完整。

该摘要不检查或保留事件载荷、任务或 assistant 文本、工具参数或输出、verifier 输出、凭据或路径。其条目类型计数是事件计数,不是推断的工具调用计数;coverage 块把这限制保持为机器可读。畸形、缺失或内部不一致的生命周期事实失败关闭,而不是产生部分公开产物。这是当前原生产 runner 契约,不恢复也不依赖已归档的遗留 benchmark reducer。
