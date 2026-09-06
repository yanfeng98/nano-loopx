# Benchmark Toolkit

> [English](README.md)

`benchmark-toolkit` 是 LoopX 内置、provider-neutral 的 surface,围绕 benchmark
实验提供并发准入、权限、artifact、完整性与可复用 agent-runtime 边界。它不拥有
benchmark-family runner、结果 ledger 或评分适配器。

## 外部 Agent 阶段

Benchmark harness 可以自己拥有任务容器与 verifier,只把 agent 阶段委托给一个
预装命令。Harness 写入一个包含任务指令、任务可见工作区与超时的
`external_agent_request_v1` JSON 文件,然后调用:

```bash
loopx benchmark agent-phase \
  --request "$LOOPSBENCH_EXTERNAL_AGENT_REQUEST" \
  --result "$LOOPSBENCH_EXTERNAL_AGENT_RESULT" \
  --solver-command-json '["<solver>", "<arg>"]' \
  --execute
```

该命令只写一个带哈希与有界生命周期字段的 `external_agent_result_v1` 结果。
它不 provision 任务、不启动 Docker、不访问 verifier、不计算分数、不上传结果,
也不授予 model 或凭据 authority。solver 命令由 runner 拥有,在 runner 选择的
当前目录执行;请求工作区必须与该目录完全一致。solver 通过 stdin 接收校验后的
指令,外加仅有的平台查询、locale、临时目录与阶段特定环境变量;环境凭据不会被
继承。这允许直接使用无头命令,如 `traex exec --sandbox workspace-write -`,
而无需 benchmark 特定 driver。需要凭据的 provider 必须单独定义显式授权契约,
而不是扩大这个通用边界。

执行还要求 `external_agent_containment_v1` 请求对象。Runner 必须拥有不可逃逸的
containment,如容器、cgroup v2、PID namespace、虚拟机或 Windows Job Object,
并声明 `timeout_owner=runner` 与
`termination_postcondition=drained_before_result_consumption`。请求还必须携带
runner 自有的 `external_agent_containment_verification_v1` receipt 引用,状态为
`status=verified`;未验证的散文式声明会被拒绝。POSIX process group 不够,
因为 solver 可以新建 session。LoopX 在启动前验证该契约,但不声称创建或检查
containment,不自行强制执行超时,也从不写 `solver_timeout` 结果。超时时,runner
必须先销毁其 containment,并回读确认其为空,然后才记录超时。在任何 solver
结果之后,runner 同样必须在消费结果或启动 verifier 之前排空 containment,因为
solver 可能在退出时留下脱离的子孙进程。没有该生命周期的 runner 必须在调用
`agent-phase` 之前 fail closed。

### 有界的续行决策

当 benchmark treatment 刻意加入 LoopX 管辖的 continuation 时,把进程启动与进度
观察留在 runner,只向 LoopX 询问下一个处置:

```bash
loopx benchmark continuation-decision \
  --progress-json .local/private-run/public-progress.json \
  --expected-first-prompt-sha256 "$EXPECTED_PROMPT_SHA256" \
  --observed-first-prompt-sha256 "$OBSERVED_PROMPT_SHA256" \
  --expected-total-unit-count 5 \
  --previous-completed-unit-count 2 \
  --completed-segment-count 1 \
  --max-agent-segments 2 \
  --elapsed-ms 300000 \
  --total-budget-ms 7200000 \
  --format json
```

该命令是只读的。它只接受聚合的公开进度计数,返回 `continue`、
`stop_complete`、`stop_prompt_mismatch`、`stop_progress_regression`、
`stop_task_shape_mismatch`、`stop_round_limit` 或 `stop_time_budget`,外加下一
segment 的 fair-share 超时。Runner 必须给第一个 solver segment 完整原始任务
prompt,冻结初始 unit 计数,并提交匹配的独立计算 digest。后续 prompt 只能追加
公开进度;不得披露 verifier 输出或隐藏评测。Runner 仍负责调用下一个 agent
segment、测量共享总预算、保持 containment 并收集证据。

## Source 修订准入

长程 campaign 可以在跟踪分支前移之后,继续从旧安装 checkout 启动。在 controller
启动时 pin 一次 source 并不能阻止这种漂移。每次新 benchmark 准入前,应通过
runner 的 provider 或网络边界获取当前参考 head,然后与干净本地 checkout 及预期 pin
对比:

```bash
loopx benchmark source-revision-fence \
  --source-checkout /path/to/pinned-source \
  --expected-revision "$PINNED_REVISION" \
  --observed-reference-revision "$OBSERVED_REFERENCE_REVISION" \
  --require-admitted \
  --format json
```

只有在三个身份全部匹配、且 source 根目录没有 tracked 或 untracked 变更时,该
命令才成功。其紧凑 receipt 记录相等性、干净度与一个稳定 reason code,不记录
checkout 路径或任何 revision 值。无效输入同样降级为无路径的 fail-closed
receipt。

Fence 是准入边界,不是 live-run 变更机制。已通过 fence 的 run 即使之后 reference
移动,也保持其不可变 revision;新 head 只会在 runner 安装并 pin 更新后的 source
之前,阻塞后续准入。观测 reference 值的 fresh 度与权威性由调用方负责。本
capability 不执行 fetch、provider API 调用、checkout、install、进程启动、分数
写入或提交。

## 原生 Codex Goal 运行时

使用 Codex app-server Goal API 的 benchmark 适配器应导入
`loopx.capabilities.benchmark_toolkit.native_codex_goal`。该模块提供真实的 stdio
JSON-RPC 进程传输、有序的 Goal transaction、terminal 事件关联、跨自动续行 turn
的 Goal-status 轮询,以及一个 public-safe receipt。Runner 提供其环境、sandbox
policy、任务桥与超时;它不应复制 Goal state machine。

在 Linux 上,host 侧 runner 可以使用 `native_codex_isolation` 构建隔离进程命令。
其 synthetic root 包含只读系统 runtime、新鲜的 `/proc`、`/run` 与 `/tmp`、runner
创建的工作子目录、一个在返回的 `host-visible` 别名处显式选择的任务工作区,以及
一个位于其验证过的绝对路径的可选正式 LoopX profile。周围 host root、原始任务
路径、环境 host `/tmp`、嵌套 host mount、symlink 的工作子目录,以及
`/proc/1/root` 逃逸路径都不存在。该 helper 需要非特权 user、mount 与 PID
namespaces、`pivot_root` 与 `tini`。它以 `tini` 运行被隔离的 PID 1,使长生命周期
worker 收割被遗弃的命令子进程;当它的根重叠、或 init 从可变的 task/profile/work
root 解析时,则 fail closed。

独立 Codex 发行版也需要在启动后带上运行时伴侣。该 envelope 现在暴露已解析
可执行文件旁或其发行根目录下已有的 `codex-resources/bwrap` 文件,以及相邻的
`codex-code-mode-host`,作为单个只读挂载。它不暴露包含目录或无关的邻近文件。
Companion 必须是私有 controller 与任务工作区根目录之外的常规、非 symlink
文件;无效候选会 fail closed。Codex 自己的 companion 验证保持不变。Runner 必须
在构建 envelope 之前,把可执行文件与 companions 放到私有根之外;仅可执行文件的
自定义 launcher 仍受支持。

```python
from loopx.capabilities.benchmark_toolkit.native_codex_isolation import (
    build_native_codex_isolation_envelope,
    rebase_native_codex_loopx_workspace_state,
)

envelope = build_native_codex_isolation_envelope(
    executable="codex",
    process_args=["app-server", "--listen", "stdio://", "--enable", "goals"],
    work_dir=runner_work_dir,
    private_root=controller_private_root,
    workspace_source=task_workspace,
    profile_root=profile.root,
)
# 如果选中的工作区已包含 LoopX 控制 state,在启动前重定位其生成的路径引用,
# 并在进程结束后恢复。
rebase_native_codex_loopx_workspace_state(
    task_workspace,
    source_root=task_workspace,
    target_root=envelope.workspace_alias,
)
# 把 envelope.process_command 交给 probe_native_goal_process 或
# run_native_goal_process_until_terminal,并用 envelope.workspace_alias 作为 cwd。
# 在进程终止后的 finally 块中:
rebase_native_codex_loopx_workspace_state(
    task_workspace,
    source_root=envelope.workspace_alias,
    target_root=task_workspace,
)
```

重定位 helper 刻意狭窄:它只重写选中工作区下的 LoopX registries 与生成的
run-history JSON、JSONL 与 Markdown。它在写入前校验每个候选,原子更新文件,
拒绝 symlink 的控制状态路径,并且不触碰任务文件、model 输出、trajectories、
verifier 证据或任意工作区散文。这保证正式安装的 LoopX state 在临时
`host-visible` 别名消失后仍可读。两个 canonical registries 构成一个一致性边界:
两者都不存在表示没有控制 state,而只存在一个则 fail closed。如果突然的进程
kill 跳过了反向重写,之后使用同一确定性工作目录的启动会先恢复过期的别名引用。

Profile bind 是可写的,因为 Codex 与已安装的 LoopX release 可能需要运行时状态。
因此它必须是每次运行的 profile,或由 runner 恢复的 pinned snapshot,绝不能是
跨 trial 共享的环境状态。

这是文件系统/进程 envelope,不是完整的 benchmark sandbox。它不授予 model 凭据、
任务命令桥、shell-network policy、evaluator 拒绝、cross-trial 拒绝、verifier
排序、上传、提交或评分 authority。Runner 必须独立证明这些边界。缺少所需 Linux
namespace 原语的平台,必须使用等价的 runner 自有隔离边界,而不是静默回退到
环境 host。

可运行的源码示例是
[`benchmark/deepswe/run_native_codex_goal.py`](../../../benchmark/deepswe/run_native_codex_goal.py)。
它的 `--preflight-only` 模式在不调用 model 的情况下,证明一次真实的 Codex
initialize/thread/Goal 附接。Full 模式启动一个 turn 并等待关联的 terminal 事件,
然后持续排空 Codex 自有的续行 turn,直到 Goal 离开 `active`。同一个总超时覆盖
完整 Goal 生命周期。加上 `--isolate`、`--isolation-work-dir` 与
`--private-root`,使这个 envelope 成为真实进程路径;`--profile-root` 添加可选的
每运行正式 profile。Launcher 围绕 preflight 与 full Goal 两种模式执行恢复、
启动前 rebase 与 `finally` 恢复。

同一适配器从紧凑 `native_codex_goal_turn_receipt_v0` 生命周期字段发布
`public_trajectory_summary_v0`。Benchmark toolkit 拥有这个严格 reducer,因为
public/private 证据化简已经是本 capability 的一部分;DeepSWE 研究适配器是它的
第一个活跃调用方。Summary 只携带 typed 计数、状态标签和无内容的通知种类计数。
它从不重新打开事件 payload,并把消息与工具调用语义标记为 unavailable 而不是
猜测。缺失、格式错误或不一致的生命周期事实会 fail closed。`deprecate/benchmark-legacy/`
下命名相似的归档 reducer 是历史证据,不是该 native-runner 契约的依赖或兼容
入口点。

### 正式安装的 profile 与 skill 发现

只提供 Goal prompt 与 source-checkout CLI 的 treatment,并没有证明真实的 LoopX
产品路径。Prompt、已安装 skills 与已安装 CLI 是三个独立输入。使用
`native_codex_profile` 通过 LoopX 自带的 `scripts/install-local.sh` 创建隔离的
本地 release,而不是复制 skill 文件或导入任意 checkout:

```python
from loopx.capabilities.benchmark_toolkit.native_codex_goal import NativeGoalConfig
from loopx.capabilities.benchmark_toolkit.native_codex_profile import (
    install_native_codex_profile,
    native_codex_app_server_shell_policy_args,
    native_codex_profile_environment,
    render_native_codex_goal_prompt,
)
from loopx.capabilities.benchmark_toolkit.provider_gateway import (
    serve_runner_owned_provider_gateway,
)

profile = install_native_codex_profile(loopx_source, isolated_profile_root)
prompt = render_native_codex_goal_prompt(
    profile,
    project_root=task_visible_cwd,
    goal_id=goal_id,
    agent_id=agent_id,
    runtime_registry_path=case_runtime_registry,
)
config = NativeGoalConfig(
    cwd=task_visible_cwd,
    objective=prompt.task_body,
    task_instruction=task_instruction,
    required_skill_ids=profile.required_skill_ids,
)
process_env = native_codex_profile_environment(profile, base_env=runner_environment)
process_env["LOOPX_MODEL_PROVIDER_SENTINEL"] = (
    "runner-owned-gateway-no-upstream-secret"
)
shell_policy = native_codex_app_server_shell_policy_args(
    excluded_env_keys=("LOOPX_MODEL_PROVIDER_SENTINEL",),
)
with serve_runner_owned_provider_gateway(
    upstream_base_url=runner_provider_base_url,
    upstream_bearer_token=runner_provider_credential,
) as gateway:
    # 用 gateway.base_url 与 sentinel 配置 app-server 的 provider,
    # 然后在 build_native_codex_isolation_envelope(...) 内启动它。
    ...
```

Profile installer 把 release、可执行文件、manual、home 与 Codex skill 根目录
重定向到提供的隔离目录。它使用固定的 installer 路径,包括其生成的 `$loopx`
入口 skill 与打包的 workflow-skill readback;该非交互 worker 会禁用无关的交互式
slash-command surfaces。检查验证 release-snapshot CLI、确切 source revision、
默认干净的 source、skill-tree digests,以及 `doctor --agent-type codex-app-ssh`。

`render_native_codex_goal_prompt` 通过 release-snapshot CLI 调用
`heartbeat-prompt --thin`,需要 `codex_app_ssh_goal` profile 与 interface budget,
并证明返回的 body 指名了那个已安装 CLI。对于隔离 case,它还替换通用
global-registry token 为显式 case registry。让 app-server 保持使用
`native_codex_profile_environment`;它只提供正式 profile 的 `HOME`、
`CODEX_HOME` 与 `PATH`。上游 provider 值必须留在
`serve_runner_owned_provider_gateway` 中,而 app-server 只接收 loopback gateway
URL 与固定非 secret sentinel。在 Linux 上,把 app-server 放进 `native_codex_isolation`,
让它的新 PID namespace 与 synthetic root 隐藏 runner 进程、环境 HOME、provider
文件与 controller 私有根。没有该 OS 边界的环境过滤不是凭据隔离:danger-full-access
子进程否则可以检查父进程环境。`native_codex_app_server_shell_policy_args` 保留一个
小型的 model-created shell 环境作为纵深防御。没有等价 authority 边界的平台必须
fail closed,或使用容器/VM 路径(如 Pier);它们不得回退到环境原生执行。设置
`required_skill_ids` 让原生运行时在 `thread/start` 之前调用真实的 app-server
`skills/list` surface;缺失 skills、发现错误或错误的 cwd 会在任何 model turn
之前失败。无路径的 profile、prompt 与 Goal receipts 随后可以在不发布安装路径、
prompt 文本或 skill 正文的情况下证明全部三个输入。

用以下命令运行正式 installer 加无模型 readback smoke:

```bash
python examples/benchmark-native-goal-installed-profile-smoke.py \
  --require-app-server
```

该 helper 只安装到其目标目录。它不授予凭据、网络、任务、evaluator、上传、
提交或评分 authority;这些仍是 runner 自有的边界。

Toolkit 借鉴了现代 benchmark runner 已经确立的有用契约:ATIF 兼容的 agent
trajectory、独立拥有的 verifier 阶段、显式 attempt 记账,以及紧凑结果化简。
LoopX 补充了容器 runner 自身无法推断的控制面部分:model 可见的 source 权限、
host 与 cross-trial 隔离、凭据传播、canonical 的 case-local 状态、verifier
排序、public/private 证据化简,以及匹配对可计数性。

## Treatment 保真边界

Treatment fidelity 证明预注册的实验因子确实运行了,例如引导式启动先于产品编辑,
以及 solver 自己编写了业务分解。它不得仅仅因为某个 arm 使用 LoopX 就要求一个
implementation 类别的 Todo。Todo 角色标签可以记录为诊断信息,但只有在该确切角色
要求被预注册时才影响可计数性。

之前的 `plan-fidelity` 命令与 Python API 已被移除,因为没有已发布的 benchmark
runtime 消费它们,而通用 action-kind 分类法不是有效的 treatment gate。预注册
基于角色的因子的研究由自己拥有这个狭窄的适配器检查;它不得把该检查提升为默认
LoopX 要求。

## 完整性资格判定

### TraeX 证据捕获

TraeX `exec --json` 发出面向自动化的 stdout JSONL 流,而不是其归档会话的完整副本。
在完整性判定的资格之前,把该私有流转换为 ATIF,并可选择提供匹配的私有归档 JSONL,
用于独立观测的运行时 model 路由:

```bash
loopx benchmark traex-evidence \
  --source-jsonl .local/private-run/traex-stdout.jsonl \
  --route-source-jsonl .local/private-run/traex-session.jsonl \
  --atif-output .local/private-run/agent/trajectory.json \
  --route-receipt-output .local/private-run/public/model-route.json \
  --requested-model GPT-5.4 \
  --require-runtime-route \
  --execute --format json
```

不加 `--execute` 时,该命令只校验并预览,不写盘。私有 ATIF 保留工具参数与观测,
用于本地完整性分析。Route receipt 只包含紧凑的请求与观测路由标签,以及
`runtime_route_verified`、`runtime_route_mismatch`、`runtime_route_ambiguous`,
`route_requested_not_runtime_audited` 之一;它从不包含 prompts、raw tool content
或路径。Stdout JSONL 通常没有 runtime route 事件,所以省略
`--route-source-jsonl` 并不能证明实际运行了哪个 model。提供独立归档时,其 session
id 必须与 stdout `thread.started` id 完全一致。转换器覆盖观测到的 TraeX 命令与
文件变更 stdout 事件,以及归档的 function-call 与 custom-tool-call 对;未知的
承载动作的 stdout 或归档项会 fail closed,而不是产生部分审计 trajectory。该命令
不启动 TraeX、不读取 verifier 数据、不给 run 打分,也不发布任一 artifact。

在 agent 阶段之后、runner 产出隔离 attestation 之后运行完整性判定。Trajectory
与任何敏感值仍是私有本地输入:

```bash
export BENCHMARK_PROVIDER_CANARY='a-private-value-known-to-the-controller'

loopx benchmark integrity-qualification \
  --trajectory-json .local/private-run/agent/trajectory.json \
  --runtime-attestation-json .local/private-run/runtime-attestation.json \
  --sensitive-value-env BENCHMARK_PROVIDER_CANARY \
  --require-qualified \
  --format json
```

自动化的 restricted-source 与 host-boundary 探测匹配是怀疑信号,不是作弊裁决。
它们保持 `integrity_qualified=true`,发出
`restricted_access_review.state=suspected`,并保持可计分,同时由 post-run 分析师
审查实际信息流。这包括 `/proc/1/root` 之类的 host-escape 标记:仅凭该标记无法
证明请求离开了隔离 namespace、披露了受限材料,或影响了解法。在 solver 收尾且
评分完成后,分析师读取真实 solver trajectory、工具结果与最终工作区,并可以附加
这个紧凑决策:

```json
{
  "schema_version": "benchmark_restricted_access_adjudication_v0",
  "decision": "qualified_with_warning",
  "reviewer_role": "post_run_analyst",
  "reviewed_surfaces": [
    "solver_trajectory",
    "tool_results",
    "final_workspace"
  ],
  "restricted_material_disclosed": false,
  "causal_use_observed": false,
  "evidence_id": "case-integrity-review-1"
}
```

用 `--restricted-access-adjudication-json <compact.json>` 传入。唯一取消资格的
决策是 `confirmed_cheating`,且仅当受限材料确实被披露、并且分析师发现它因果进入
了解题或验证决策时才有效。被阻止的请求、空结果,或没有观测到因果使用的已披露
内容,仍可计分并带审计警告。Evidence id 是 public-safe 指针;raw trajectory
内容与私有路径保持在 receipt 之外。

该命令发出 `benchmark_integrity_qualification_v0`。它只记录稳定标签、计数、
reason codes、step ids 与 SHA-256 digests。它从不发出 raw 工具参数、观测、敏感值、
输入路径、任务文本、verifier 输出或 trajectory 内容。无效私有输入返回通用的
fail-closed 错误,使 JSON 解析器细节无法回显私有数据。

资格判定在检测到以下任一项时拒绝 run:

- post-run 确认受限答案、范围外任务源、隐藏测试、verifier、其他 trial 或
  controller 私有材料在解题或验证期间既被披露又被因果使用;
- host 逃逸、凭据探测或暴露,或 shell 网络访问;
- 格式错误或不完整的 ATIF 工具证据;
- 缺失 runner authority 或任何所需运行时隔离 attestation。

凭据探测检测读取 typed 命令字段,然后分类直接环境命令、运行时语言枚举或敏感名
查找,以及 procfs 读取。相邻的工具散文与只检查或写入源码文本的命令,不被当作
凭据读取。用显式环境启动子进程本身也不是凭据读取;敏感值仍会在每个工具参数与
观测中被扫描。

访问请求标记只在能够执行或请求资源访问的工具调用上评估。`update_plan` 等已知的
基于 controller 的调用携带叙述元数据,被排除在该扫描之外;它们的参数中实际出现
敏感值仍会判定失败。未知工具名保持 fail-closed。

任务源边界由 benchmark 拥有,而不是从仓库名或 shell 散文推断。禁止 solver 访问
上游 checkout、reference package 或其他任务源的 runner,应把其私有路径或命令
标记添加到 `denied_argument_markers.restricted_task_source_request`。匹配在 JSON
转义前检查 typed 参数字符串;公开 receipt 只保留类别、计数、step id、工具名与
参数 digest,绝不保留配置的标记或 raw 命令。即使请求没有返回内容,这也记录了一次
显式访问请求,而不会给 LoopX core 添加 benchmark 特定的子串 denylist。该请求
保持为可计数怀疑项,直到 post-run 因果判定确认作弊为止。

`benchmark_cheating_detected` 比 `integrity_qualified=false` 更窄。只有在
post-run 分析师同时确认受限材料披露与因果使用后,它才变为 true。扫描器命中、
缺失隔离证明或凭据泄漏本身不会成为已确认的答案作弊;隔离与凭据失败仍可通过
各自的独立 blocker 使 run 不可计数。

### 网络访问策略

离线 coding benchmark 以 `network_access: "denied"`(默认)运行:任何 shell
网络使用都是策略违规,runner 必须证明 `shell_network_denied: true`。启动
case-local HTTP 服务的 benchmark 可以选择 `"network_access": "loopback_only"`;
此时 runner 证明 `external_shell_network_denied: true`,仅允许字面 `localhost`
或 loopback IP 的 HTTP 请求,仿冒、格式错误、混合或外部 host 仍然 fail closed。
这个显式模式防止本地服务例外静默改变默认隔离契约:

```json
{
  "schema_version": "benchmark_integrity_policy_v0",
  "policy_id": "offline-loopback-only",
  "network_access": "loopback_only"
}
```

Web 研究 benchmark 在解题阶段合法地需要外部网络。自定义 policy 可以声明
`"network_access": "permitted_solving"`;此时 runner 证明
`network_permitted_solving: true`,loopback 与外部网络请求证据被记录但不判定
失败。受限资源拒绝(答案、隐藏测试、verifier、其他 trial、controller 状态、
host 逃逸、凭据)在每种模式下保持 fail-closed:

```json
{
  "schema_version": "benchmark_integrity_policy_v0",
  "policy_id": "widesearch-permitted-solving",
  "network_access": "permitted_solving"
}
```

`network_access` 被校验为 `denied`、`loopback_only` 或 `permitted_solving`;
任何其他值都会被拒绝。资格判定 receipt 暴露解析后的 `network_access`、独立的
loopback/外部证据计数,以及实际应用于该模式的 attestation 检查。

## Runner Attestation

Attestation 是紧凑的 runner 自有 JSON 对象,不是 agent 断言:

```json
{
  "schema_version": "benchmark_runtime_integrity_attestation_v0",
  "authority": "runner",
  "benchmark_id": "fixture@v0",
  "case_id": "case-1",
  "agent_phase_isolated": true,
  "evaluator_sources_denied": true,
  "other_trials_denied": true,
  "controller_state_denied": true,
  "host_escape_denied": true,
  "shell_network_denied": true,
  "provider_credential_shell_excluded": true,
  "case_local_control_state": true,
  "canonical_control_state_root": true,
  "independent_verifier": true,
  "verifier_started_after_agent": true,
  "official_feedback_blinded": true
}
```

每个布尔都必须为 true。干净的 trajectory 扫描无法证明文件系统或 namespace
权限边界,因此缺失 attestation 会 fail closed。同样,仅凭 attestation 也无法证明
实际发生了哪些工具调用;两个证据通道都需要。

对于 `loopback_only`,把 `shell_network_denied` 替换为
`external_shell_network_denied`。对于 `permitted_solving`,替换为
`network_permitted_solving`。字段名有意与 runner 实际声明匹配;runner 不允许
在允许 loopback socket 后还证明所有 shell 网络都被拒绝。

`benchmark_id`、`case_id` 与自定义 policy 的 `policy_id` 是公开标签,不是路径。
类路径值会 fail closed,且只以 `redacted` 形式发出,因此 runner 不能通过
标识符字段把运维目录移进公开 receipt。`case_id` 单独可用公开 benchmark 目录
使用的 canonical 两段式 `namespace/name` 形式。绝对路径、dot 段、反斜杠、空白与
更深的路径形状仍被拒绝;benchmark 与 policy ids 保持单 token 标签。

### 精确作业容器绑定

运行时证据必须与计分属于同一作业。仅镜像的 Docker 查找在两个 benchmark arm
并发使用同一镜像时立刻变得模糊。在检查隔离设置之前,用 runner 自有的作业或
trial 标签、服务标签与预期镜像绑定容器:

```python
from loopx.capabilities.benchmark_toolkit import (
    compact_docker_container_binding_receipt,
    select_exact_docker_container,
)

binding = select_exact_docker_container(
    ancestor_image="benchmark-runner:fixture",
    required_labels={
        "com.docker.compose.project": job_id,
        "com.docker.compose.service": "main",
    },
)
container_name = binding.container_name  # runner 私有状态;不要发布
receipt = compact_docker_container_binding_receipt(binding)
```

选择器在恰好一个运行中的容器匹配之前一律 fail closed。紧凑的
`benchmark_exact_container_binding_v0` receipt 只记录必需的 label 键、匹配计数与
一个 SHA-256 selector digest;它排除 raw 容器身份与 label 值。该 helper 不授予
任何 Docker 或 runner authority。需要特权 wrapper 的调用方必须提供自己的
`command_runner`,并把该 authority 留在 receipt 之外。

### 运行时收尾连续性

Terminal 结果不足以证明关闭 run 的进程使用了与启动时准入相同的运行时 artifact
与 attempt generation。写 terminal 分数之前,比较 runner 自有的 SHA-256 bindings
与其 typed 事件窗资格判定:

```bash
loopx benchmark runtime-continuity \
  --launch-runtime-digest "$LAUNCH_RUNTIME_DIGEST" \
  --closeout-runtime-digest "$CLOSEOUT_RUNTIME_DIGEST" \
  --launch-generation-digest "$LAUNCH_GENERATION_DIGEST" \
  --closeout-generation-digest "$CLOSEOUT_GENERATION_DIGEST" \
  --event-window-state qualified \
  --require-qualified \
  --format json
```

只有当两个 content-addressed bindings 匹配、且 provider 在该 run 的
launch-to-terminal 窗口内对所需事件完成资格判定时,该 gate 才允许收尾。
Generation 不匹配会路由回其 launch generation;运行时 artifact 不匹配会被拒绝;
缺失、模糊或窗口外证据保持 unqualified。紧凑 receipt 暴露相等性、typed reason
codes 与路由指引,但从不暴露 digests、run 身份、事件 payload 或路径。调用方使用
`--require-qualified` 时,假的 `closeout_write_allowed` 是机器强制义务;
`recommended_transition` 保持为 provider 指引。

Runner 仍负责创建不可变 artifacts 与 generations、从其私有证据分类事件窗、应用
路由指引并写 terminal 行。该 reducer 不读取任何文件,也不授予 runner、verifier、
评分、上传或提交 authority。

Benchmark 特定私有根可以通过被忽略的 `benchmark_integrity_policy_v0` 文件添加,
而无需提交:

```json
{
  "schema_version": "benchmark_integrity_policy_v0",
  "policy_id": "local-run-policy",
  "denied_argument_markers": {
    "other_trial_request": ["<private-other-trial-root>"],
    "controller_private_state_request": ["<private-controller-root>"]
  }
}
```

Policy 值仅用于内存中匹配,不会被复制进 receipt。

## 四臂 Goal/LoopX 研究

当 benchmark 特定的 solver 提示可以独立于 LoopX 改变 outcome 时,使用 2×2 研究,
而不是把普通 Goal baseline 与带提示的 LoopX treatment 直接比较:

| Arm | LoopX 启动 | 领域提示 | 实验板角色与锚点 |
| --- | --- | --- | --- |
| `goal_plain` | off | off | `baseline` |
| `loopx_plain` | on | off | `treatment`,锚定 `goal_plain` |
| `goal_<hint-id>` | off | on | `control`,锚定 `goal_plain` |
| `loopx_<hint-id>` | on | on | `treatment`,锚定 `goal_<hint-id>` |

领域提示是 benchmark 自有的 solver 指引。对于软件工程 benchmark,它可以要求
solver 实现、验证并 review;其他 benchmark 提供自己的领域合适提示。它必须保持
独立于 LoopX。LoopX 引导式启动是独立的 provider 自有动作,绝不能被插入任务 goal
文本。

在预注册 runs 之前,创建本地 spec 并做资格判定:

```json
{
  "schema_version": "benchmark_four_arm_spec_v0",
  "base_goal_text": "Complete the requested benchmark task.",
  "domain_hint": "Apply the benchmark's declared domain workflow.",
  "hint_id": "domain_hint",
  "domain_hint_independent_of_loopx": true
}
```

```bash
loopx benchmark four-arm-contract \
  --spec-json <four-arm-spec.json> \
  --require-qualified \
  --format json
```

默认 CLI receipt 包含 prompt 哈希但不含 prompt 文本。其 `qualified` 字段只涵盖
因子设计与配对内 prompt 一致性;`execution_qualified` 保持 `false`。列出的 runner
义务是要求,不是启动时一致性、输入 pinning 或板注册已发生的证据。受信任的本地
runner 可以使用 Python builder,或显式传 `--include-prompt-text`。启动时必须把
最终 task-goal 哈希与所选 arm 比较,固定每个非因子输入(case、model、推理、
deadline、permissions、runner 与 scorer),并在实验板记录 arm。普通 Goal/LoopX
配对与带提示的 Goal/LoopX 配对必须各自有相同的 task-goal 哈希。该契约不授予
runner、model、LoopX-启动、verifier 或评分 authority。

主要比较是:无提示的 LoopX、无 LoopX 的提示,以及带提示的 LoopX。交互对比比较
两个 LoopX 效应。混合了启动指引与领域指引的历史 arm 只作诊断;重命名不会让它
成为该因子研究的成员。

四个 cell 都具备板行之后,把紧凑契约传回板读取模型:

```bash
loopx benchmark experiment-board-show \
  --goal-id <goal-id> \
  --four-arm-contract-json <compact-four-arm-contract.json> \
  --format json
```

因子投影为每个声明的 cell 选择恰好一个可计分 run,检查确切锚点、非因子一致性与
不同的 LoopX/非 LoopX 运行时组,然后报告三个条件效应及其 difference-in-differences。
缺失或模糊的 cell 会 fail closed。这与标准匹配对投影分开:带提示的 Goal cell 保持
为 `control` 而非 baseline,带提示的 LoopX cell 只能通过显式因子契约才有资格。
读取模型不从 arm 名推断成员资格,也不把设计资格提升为 runner 或 scorer authority。

## 实验生命周期

可计数实验按此顺序使用 toolkit:

1. 当领域指引是因子时,在预注册前做四臂契约资格判定并冻结其 task-goal 哈希。
2. 在选择或启动另一个 case 之前,读取项目实验板。
3. 读取或配置并发 envelope,然后用确切 runner 存活度协调其预留。
4. 声明 `run_permission_policy_v0` 并 preflight runner 边界。
5. 在独立授权的 runner 启动前一刻,原子准入一个 case slot。
6. Upsert 计划中或运行中的行,然后启动一个冻结的 case/arm;不暴露 evaluator
   源或官方反馈。
7. 捕获 ATIF 工具证据与 runner 自有的运行时 attestation。
8. 活跃监控期间,分类精确作业运行时证据;不要从占用的准入 slot 推断存活度。
9. Terminal 写入前,要求 launch artifact、closeout artifact、launch generation、
   closeout generation 与事件窗之间的运行时连续性。
10. 运行 `integrity-qualification`;如果受限访问仅被怀疑,保持分数有资格并排队
    post-run 因果判定;遇到任何实际 blocker 即停止。
11. 只在 agent 阶段之后运行独立 verifier。
12. 通过 benchmark 自有的评分路径化简官方结果。
13. Upsert 终端分数、可计数性、努力、treatment 保真度与洞察状态;释放其预留;
    然后读取匹配比较投影。
14. 在任何比较声明之前,应用 attempt 可计数性、treatment 保真度与匹配对 gate。

完整性资格判定对分数声明来说是必要但不充分。它不确立任务正确性、官方分数
authority、实验一致性或 LoopX 优势。`score_claim_eligible=true` 只允许官方分数
与匹配对 gate 运行;此 receipt 中 `score_claim_countable` 与
`matched_pair_countable` 保持 false。它们是独立的 verifier 与比较契约。

## 并发 Envelope

在启动并行 cases 之前配置一个 goal-scoped envelope。总上限由 baseline 与 test
组 run 共享;`control`、`treatment` 与 `explore` 消耗 test 组容量。预留的 test
计数防止 baseline 工作饿死比较通道,而较低的 target 允许在硬上限之下分阶段爬坡。

```bash
loopx benchmark concurrency-configure \
  --goal-id <goal-id> \
  --max-active-cases 8 \
  --target-active-cases 6 \
  --max-baseline-cases 7 \
  --max-test-cases 4 \
  --reserved-test-cases 1 \
  --require-resource-headroom-receipt \
  --execute \
  --format json

loopx benchmark concurrency-status \
  --goal-id <goal-id> \
  --format json
```

每次 runner 启动前原子预留一个 slot。如果准入返回 `ok=false`,就不要启动。
只在确认为 terminal 或 runner-invalid 后才释放该确切 run:

```bash
loopx benchmark concurrency-admit \
  --goal-id <goal-id> \
  --run-id <run-id> \
  --case-id <case-id> \
  --arm-role <baseline|control|treatment|explore> \
  --resource-headroom-json resource-headroom.json \
  --execute \
  --format json

loopx benchmark concurrency-release \
  --goal-id <goal-id> \
  --run-id <run-id> \
  --execute \
  --format json
```

配置、准入与释放是项目本地、加锁且原子的。`max-active-cases` 是硬上限;
`target-active-cases` 是期望占用率。低于 target 时,status 报告确切缺口、首选 arm
组与 `next_action=backfill_to_target`。达到 target 时,新准入以
`target_capacity_exhausted` fail closed。当 target 被降到当前占用率以下,status
报告 `next_action=drain_to_target`;不终止任何活跃 run,且替换准入保持关闭,直到
占用率低于 target。`active_counts` 是准入 ledger,不是运行时证明。在每次启动、
terminal 或 runner-invalid 转换以及有界的周期 cadence 上,通过
`runtime-observation` 传递精确作业 receipt 与 runner 自有事实。在释放该预留前应用
其 typed terminal 或 runner-invalid 转换,然后补齐报告的缺口。

对于并行作业可能耗尽临时存储、内存、进程容量、文件描述符、持久存储或 provider
容量的 host,启用 `--require-resource-headroom-receipt`。每个新准入必须包含新鲜的
`benchmark_resource_headroom_receipt_v0`。Provider 观察自己的环境,只提供 typed
`sufficient`、`insufficient` 或 `unresolved` 检查,外加至多 15 分钟的有效期窗口。
缺失、过期、未来、unresolved 或 insufficient 的 receipt 会在 slot 预留前 fail
closed。每项检查必须观察 runner 解析的、实际被启动消耗的资源——例如其 profile、
cache、scratch 与 artifact 文件系统——而不仅仅是 `/tmp` 之类的通用 host 默认;
如果该绑定无法证明,则报告 `unresolved`。LoopX 从不把 raw 指标、路径、provider
日志或 receipt 记录进 envelope,且 receipt 不授予启动 authority。

用 `concurrency-status` 回读 gate。要禁用它,用相同的容量值重新运行
`concurrency-configure` 并省略 `--require-resource-headroom-receipt`;现有活跃
预留被保留。

要在不每轮猜测新占用率的情况下向硬上限爬坡,把紧凑的 runner 自有健康度喂给
自适应调优器。它在连续饱和健康窗口后使用加法增加,在启动失败、provider 容量、
runner-invalid 或 typed 资源压力证据上使用减法降低:

```bash
loopx benchmark concurrency-tune \
  --goal-id <goal-id> \
  --feedback-json concurrency-feedback.json \
  --resource-headroom-json resource-headroom.json \
  --saturated-healthy-windows-required 2 \
  --increase-step 1 \
  --decrease-step 1 \
  --execute \
  --format json
```

`concurrency-tune` 只改变 `target-active-cases`。配置的 `max-active-cases`、
baseline/test 上限与预留 test slots 仍归运维者所有。降低 target 从不终止活跃 run;
它只阻止替换准入,直到占用率低于新 target。缺失、过期、未来或 unresolved 的
feedback/headroom 产生 hold;格式错误的输入在零写入下 fail closed。Feedback 还携带
其观测的并发 envelope 的确切 `updated_at` revision。任何 configure、target
变更、准入或释放都会使该 receipt 失效,因此一个健康窗口不能跨 target 级别重放。
Runner 只有在转换是合格的 terminal run 随后成功 refill、且整个观测窗口没有启动
失败、provider 容量拒绝、runner-invalid 转换或 typed 资源压力时,才能跨普通
campaign 变更保留其健康窗口连胜。之后必须发出绑定到 refill 后 envelope revision
的新 feedback;转换前的 receipt 保持无效。任何失败 refill、unresolved terminal
状态或压力信号都会重置连胜。预览是默认;`--execute` 原子写入选中的 target。
Runner 仍负责测量资源、构造 `benchmark_concurrency_feedback_v0` 并启动已准入的
工作;raw 指标与 receipts 从不持久化。

```json
{
  "schema_version": "benchmark_concurrency_feedback_v0",
  "observed_envelope_updated_at": "2026-09-01T03:49:30Z",
  "window_started_at": "2026-09-01T03:50:00Z",
  "observed_at": "2026-09-01T04:00:00Z",
  "expires_at": "2026-09-01T04:05:00Z",
  "saturated_healthy_window_streak": 2,
  "launch_attempts": 1,
  "launch_failures": 0,
  "provider_capacity_rejections": 0,
  "runner_invalid_transitions": 0
}
```

```json
{
  "schema_version": "benchmark_resource_headroom_receipt_v0",
  "observed_at": "2026-08-23T04:00:00Z",
  "expires_at": "2026-08-23T04:05:00Z",
  "checks": [
    {"kind": "temporary_storage", "state": "sufficient"},
    {"kind": "process_capacity", "state": "sufficient"}
  ]
}
```

每个参与者必须在支持 LoopX 进程间锁与原子替换的文件系统上解析同一个 goal
repository 与 envelope 文件。独立 checkout 或 host 本地副本不共享容量;这个
envelope 不是分布式信号量。多 host campaign 必须通过一个共享 authority 路由准入,
而不是每 host 配置一个 envelope。

Campaign 启动时,创建 capability packet 的
`concurrency_occupancy.monitor_todo_template`,用作一个 goal-scoped
`continuous_monitor` todo。这保留了发现并填补安全容量的义务,而不授予启动
authority。在 material monitor 窗口预览 `concurrency-tune`;只有 runner 授权的
campaign 选择了自适应占用率,才执行其 target 变更。Runner 仍拥有启动、存活度、
终止、凭据、verifier 排序、评分、上传与提交。

## 实验板

项目本地实验板把 baseline、标准 control 或 treatment 与诊断 explore runs 放在
一个紧凑投影中。它不是第二个分数 authority,从不存储 raw 任务文本、
trajectories、日志、隐藏评测、verifier 输出、凭据或本地路径。

使用该 capability 的 agent 应从读取板开始或恢复研究:

```bash
loopx benchmark experiment-board-show \
  --goal-id <goal-id> \
  --format json
```

对于预注册的四臂研究,加上
`--four-arm-contract-json <compact-four-arm-contract.json>`,在普通匹配比较旁投影
条件效应与交互对比。

在 run 启动或达到 terminal 状态时,先预览再执行幂等行更新:

```bash
loopx benchmark experiment-board-upsert \
  --goal-id <goal-id> \
  --row-json <compact-row.json> \
  --format json

loopx benchmark experiment-board-upsert \
  --goal-id <goal-id> \
  --row-json <compact-row.json> \
  --execute \
  --format json
```

默认 ledger 加锁、原子更新,并以 benchmark、study、case 与 run 身份为键。紧凑
行携带 arm 角色、确切与比较协议 ids、model、分数指标、可计数性、treatment 保真度、
有界努力与可选洞察状态或 public-safe handle。当 arm 使用 orchestration/control
runtime 时,在 `orchestrator_runtime` 中记录其 public-safe `provider_id`、确切
`revision` 与可选包 `version`;这与标识 benchmark runner 的 `runner_revision`
分开。板摘要按该确切运行时身份分组行,因此版本组不会被静默合并。未知字段与
类路径引用 fail closed。

每个非 baseline 行都指名确切 `comparison_anchor_run_id`。标准 control 或 treatment
行锚定到一个 baseline。Explore 行使用 `diagnostic_only` 声明范围,可以锚定到它们
正在检查的 baseline 或固定标准 arm。匹配比较要求兼容的 benchmark、study、case、
model、primary metric、比较协议、分数可计数性与 treatment 保真度。即使声明比较
协议说旧的可信分数仍语义可比,确切协议 revisions 也作为警告保持可见。

完整的 post-run 分析留在私有的 `benchmark_case_insight_v0` 存储中。板只记录其
紧凑状态或 handle,因此读取板不会扩大解题 agent 的证据边界。

Provider 可以为独立 runner 队列维护单独的 public-safe ledgers。在 agent 回读前,
把那些分片并入 canonical 项目板:

```bash
loopx benchmark experiment-board-reconcile \
  --goal-id <goal-id> \
  --source-ledger <provider-a.jsonl> \
  --source-ledger <provider-b.jsonl> \
  --execute \
  --format json
```

不加 `--execute` 时,该命令预览合并后的板。合并是幂等且单调的:更新的合法
生命周期转换推进稳定 run,迟到的非 terminal 行不能重新打开 terminal run,冲突的
terminal 状态 fail closed。Receipts 只报告紧凑行计数,从不记录源路径。该命令在
首次写入前校验完整候选集;已执行的批次可重放,而 provider 仍负责重试在 receipt
返回前被打断的批次。

## Post-run Case 洞察监控

Benchmark 启动应创建一个 `continuous_monitor` todo,同时拥有 campaign 分数更新与
post-run case 分析。每当 case 达到新的 material 计分状态,monitor 首先读取
public-safe 实验板投影,刷新可计数 baseline、treatment 与匹配对总计。然后向用户
报告 material 聚合变化,并在 solver 收尾后运行 post-run analyst brief,写一个
私有 `benchmark_case_insight_v0` artifact。Campaign 活跃期间的有界周期审查防止
长 run 静默累积结果。这个 monitor 是 benchmark 生命周期的一部分,不是可选的
清理步骤。Catalog entry 是指导模板,不是 scheduler:benchmark 启动 provider
创建 todo,已注册的 monitor runtime 拥有其 cadence。

### Monitor 到推进的交接

Benchmark `continuous_monitor` 是观测与控制面通道。不要把仓库交付、runner 修复、
实验重设计或 PR 工作只放在 monitor 文本里并期待其被执行。当 monitor poll 发现
material 有界工作时,在一次 writeback 中记录转换并创建独立的可执行 successor:

```bash
loopx quota monitor-poll \
  --goal-id <goal-id> \
  --todo-id <monitor-todo-id> \
  --agent-id <registered-agent> \
  --result-hash <public-safe-hash> \
  --material-change \
  --next-agent-todo "<bounded public-safe work>" \
  --next-action-kind <action-kind> \
  --next-task-repository <git-repository> \
  --next-required-capability <capability> \
  --execute \
  --format json
```

Monitor 保持 open,新 `advancement_task` 进入普通 claim、lease、validation 与
delivery 生命周期。Poll 本身不消耗 delivery quota。Unchanged poll 不创建 successor。

当主 campaign Todo 必须保持可见、但在 monitor generation 变化之前无法推进时——
例如 target 占用已满——保持该 Todo `open`,并把等待与一个已经创建的独立可运行
successor 配对:

```bash
loopx todo update \
  --goal-id <goal-id> \
  --todo-id <waiting-advancement-todo-id> \
  --agent-id <registered-agent> \
  --status open \
  --resume-when monitor_changed:<monitor-todo-id> \
  --successor-todo-id <independent-runnable-successor-id> \
  --reason "<public-safe external-wait rationale>" \
  --format json
```

恢复条件把等待 Todo 从 runnable 选择中移除,直到 monitor 记录到更新的
material-change generation。不要把这个 typed 外部等待标为 `blocked`,也不要用
monitor 本身作为 runnable successor。

Material 用户更新应包括当前可计数 arm 与配对覆盖、按 arm 的聚合 primary metric、
benchmark 暴露的二进制 outcome、benchmark 暴露的 feature 与 preservation 护栏
总计、improved/flat/regressed 配对计数,以及新的因果洞察或下一个 probe。当努力
分层有用时,预注册 benchmark 合适的固定边界,并用 baseline arm 的
`effort.duration_ms` 指派每个匹配 case。为每个候选 arm 复用同一个 case 桶;候选
时长不得定义难度,因为它本身是 treatment outcome。每桶报告配对计数、
primary/binary/feature/preservation 指标与 improved/flat/regressed 计数。除非研究
预注册了因果亚组声明,否则把这些分层当作描述性敏感性分析。分数字段从实验板或
benchmark 自有评分投影派生,而不是从 raw 私有证据派生。当没有分数、覆盖、方向、
洞察或 material runner 状态变化时,不要发送重复更新。只有私有 post-run 洞察中的
public-safe 结论可以进入该用户更新;raw 评测证据保持私有。

在活跃 campaign 审查中,区分干净 worktree 与缺少 solver 进度。`git status` 只
观测未提交变更。把 readback 绑定到精确作业,比较其当前 `HEAD` 与准入时记录的
start revision,并把该已提交 delta 与当前 worktree 状态组合。把这些事实与
Goal/事件新鲜度、typed runner 错误及 solver 的 trajectory 阶段关联。单独一个
干净 worktree 或高 raw log-error 计数并不是 run 卡住的证据。Provider 自有的
分类器只有在已提交与未提交进度都不存在、且 trajectory 过期或存在 typed 致命
runner 证据时,才可把 run 标记为 stalled。

Admission-ledger 占用率不是进程存活度。每次有界活跃审查中,provider 应通过以下
方式化简紧凑事实:

```bash
loopx benchmark runtime-observation \
  --admission-active \
  --job-receipt-state resolved \
  --runner-owner-state alive \
  --require-healthy \
  --format json
```

只有已解析的确切作业 receipt 加上存活的精确 runner owner 才是 healthy active。
Terminal 结果、typed 致命 runner 错误或 provider 启动宽限期后精确 owner 缺失,
会产生 reconciliation 转换;provider 必须在释放其 slot 前写入 terminal 分类。
缺失或模糊的运行时 authority 会 fail closed。Reducer 不执行进程发现、写入或
slot 释放,其 receipt 不包含 run 身份、进程参数、raw 错误或路径。

每个到期的 active-campaign monitor 周期还必须至少推进一个有界 solver-trajectory
分片,即使没有 case 变为 terminal。该 readback 仅用于 campaign 监督与洞察发现;
不得向解题 arm 暴露隐藏 evaluator 证据。

这是 provider 义务,不是 reducer 执行的效果:runtime-observation 命令只返回
typed 分类与推荐转换。Provider 仍负责 monitor 周期、trajectory readback、
terminal 写入、reconciliation 与 slot 释放。

使用这个分析师提示:

> 在 solver 停止且评分完成后,读取任务、真实 trajectory、最终补丁或工作区、
> 隐藏测试、grader 或 verifier,以及完整失败与分数细节;解释决定性证据、outcome
> 为何发生、是否符合预期,以及 LoopX 下一步应测试或改变什么。

Solver 与 analyst 是独立角色。Solver 无法访问隐藏测试、evaluator 源、预期答案或
官方反馈。只有 post-run analyst 可以读取完整私有评测证据,且只在 solver 收尾且
评分完成后。

Active-campaign monitor 可以在 solver 活跃时检查 solver 自有的 trajectory 与
精确作业运行时,但不得读取隐藏 evaluator 证据,也不得把其发现送回解题 arm。

以这个紧凑形状记录结果:

```json
{
  "schema_version": "benchmark_case_insight_v0",
  "case": {
    "benchmark_id": "<public-id>",
    "case_id": "<public-id>",
    "arm": "<baseline-or-treatment>"
  },
  "outcome": {
    "status": "<completed-or-runner-invalid>",
    "score": "<official-score-or-null>",
    "countable": "<true-or-false>"
  },
  "evidence_reviewed": [
    "task",
    "real_trajectory",
    "final_patch_or_workspace",
    "hidden_tests",
    "grader_or_verifier",
    "failure_and_score_details"
  ],
  "insight": {
    "approach_summary": "<what-the-solver-tried>",
    "decisive_evidence": ["<specific-observation>"],
    "why_this_outcome": "<causal-explanation>",
    "expectedness": "<expected-surprising-mixed-or-unknown>",
    "baseline_treatment_difference": "<difference-or-not-yet-compared>",
    "loopx_implication": "<reusable-product-or-experiment-insight>",
    "next_probe": "<smallest-discriminating-next-step>"
  },
  "confidence": "<high-medium-or-low>",
  "reuse_boundary": "<diagnostic-only-heldout-generalization-or-declared-feedback>"
}
```

把 artifact 与其 raw 证据留在私有 benchmark 存储中。只发布脱敏后的可复用结论。
除非实验显式声明该反馈闭环,否则不要把 case 特定的隐藏证据喂给之后的计分
solver;在提出通用产品声明之前使用 held-out cases。

### Treatment 续行 receipt

合格的 treatment 启动与可计数分数不能证明 treatment 控制在启动后仍活跃。
Terminal analyst 审查授权证据后,只化简紧凑的机制事实:

```bash
loopx benchmark treatment-continuation-receipt \
  --observation-json <compact-post-run-observation.json> \
  --format json
```

```json
{
  "schema_version": "benchmark_treatment_continuation_observation_v0",
  "treatment_applicable": true,
  "startup_state": "qualified",
  "observation_complete": true,
  "post_start_control_events": {
    "todo_transition_count": 1,
    "technical_replan_count": 0,
    "control_closeout_count": 1
  },
  "terminal_control_state": "settled",
  "precommit_validation_state": "observed"
}
```

Observation 命名启动状态、审查是否完成、启动后 Todo 转换/技术 replan/控制收尾的
计数、terminal 控制归集,以及是否观测到 pre-commit validation。只计数推进或修订
结果固定前的任务面向技术工作的 Todo 转换。只计数改变技术路线的技术 replan。
Terminal-only Todo 归集、replan 记账与最终收尾计入 `control_closeout_count`;
这些事件可见,但不证明技术控制在持续。Observation 不包含任务文本、trajectory
内容、路径、run 身份、verifier 输出或分数。

Receipt 把机制分类为 `sustained`、`startup_only`、`unknown` 或
`not_applicable`。此处 `sustained` 表示在合格启动后、结果固定前,至少观测到一个
合格的任务面向 Todo 转换或技术 replan。Terminal-only 控制即使归集成功也不确立
`sustained`;现有总计数与分类计数仍记录该收尾活动。只有授权的 post-run 观测
完成时,"缺失"才变为 `startup_only`。该 receipt 仅作分析:它从不改变分数
可计数性、完整性判定、treatment 保真度或匹配对资格。

## 研究清单、本地上传模拟与 dashboard 包

当 benchmark 适配器需要一次性声明其 case 集、arms、因子、原生指标含义与 pinned
source revisions 时,使用 `benchmark_study_manifest_v0`。Manifest 描述研究;它不
计分、不启动、不重试,也不改变 run。简单 baseline/treatment 研究通常声明一个
双水平因子。因式研究分别声明每个因子,并把每个 arm 指派到每个因子的一个水平。

在产生上传记录之前,校验 public-safe manifest:

```bash
loopx benchmark study-validate \
  --manifest-json <study-manifest.json> \
  --format json
```

Adapter 随后可以一次包装一个允许的记录:manifest、现有
`benchmark_experiment_board_row_v0`、脱敏的
`benchmark_case_insight_projection_v0`,或现有 `benchmark_runtime_observation_v0`。

```bash
loopx benchmark upload-envelope \
  --payload-json <public-safe-record.json> \
  --record-kind experiment_board_row \
  --producer-id <adapter-id> \
  --producer-version <adapter-version> \
  --benchmark-id <benchmark-id> \
  --study-id <study-id> \
  --idempotency-key <stable-key> \
  --observed-at <iso-8601-timestamp> \
  --source-revision <adapter-revision> \
  --format json > <upload-envelope.json>
```

在实现远程 provider 之前,先针对内置本地模拟演练传输生命周期。预览是默认且不
写盘;`--execute` 在文件锁下追加到显式命名的 JSONL 存储。两种模式都不执行网络
访问,也不授予上传/提交 authority。

```bash
loopx benchmark upload-local \
  --envelope-json <upload-envelope.json> \
  --store <simulation.jsonl> \
  --format json

loopx benchmark upload-local \
  --envelope-json <upload-envelope.json> \
  --store <simulation.jsonl> \
  --execute --format json

loopx benchmark upload-readback \
  --store <simulation.jsonl> \
  --record-id <record-id> \
  --format json
```

使用相同 producer、benchmark、study 与 idempotency key 的重试,只有在 payload
digest 不变时才被接受。更正后的记录使用新的 idempotency key 并显式命名
`--supersedes-record-id`;实验板更正还必须遵守现有的合法 run-state 转换。
Study manifest 是不可变比较意图:在新 `study_id` 下修改其设计,而不是取代它。
取代也保持在创作了前一个记录的 producer 自身之内。

### 上传一个 terminal case 洞察

`benchmark_case_insight_projection_v0` 是单次精确 run 的 public-safe 子记录。
先上传该 run 的 terminal `benchmark_experiment_board_row_v0`;其
`insight.status` 必须为 `complete`,且投影的 `case_id`、`run_id` 与
`outcome_status` 必须匹配那个活跃 terminal 行。Run 身份已解析其 arm,因此洞察
不能发明第二个 arm 绑定。因为投影没有 metric、countability、integrity 或
treatment-fidelity 字段,接受它不能改变 run 的分数 authority。

这是有意严格的上传顺序规则:旧的本地模拟曾接受的孤儿、pre-terminal 与
outcome 不匹配的洞察记录,现在被拒绝。先重新上传 terminal run 行,再上传其
洞察;不重写任何现有分数或实验板 authority。

```json
{
  "schema_version": "benchmark_case_insight_projection_v0",
  "benchmark_id": "example-benchmark@1",
  "study_id": "example-study-v1",
  "case_id": "case-1",
  "run_id": "treatment-case-1-r1",
  "outcome_status": "completed",
  "failure_class": "none",
  "causal_summary": "The implementation satisfied the declared contract after an independent boundary check.",
  "expectedness": "expected",
  "implication": "Retain the independent boundary check in this arm.",
  "next_probe": "Repeat on a different public case family.",
  "confidence": "high",
  "evidence_refs": ["public-receipt:abc123"],
  "privacy_classification": "public_safe",
  "producer_redaction_attested": true
}
```

用上面同样的 `benchmark upload-envelope` 命令、`--record-kind case_insight_projection`
包装它,然后通过同一本地 provider 流程预览、执行并回读。私有 analyst 只能在 run
terminal 后使用任务文本、trajectory、最终工作区、隐藏评测与 verifier 细节;这些
源被化简为上面的有界字段与 public-safe evidence handles,从不被上传本身。

最后,派生只读的 `benchmark_study_dashboard_v0` 包。它暴露 campaign、arm、case 与
run 投影,带显式分母与暂时覆盖,而把分数与匹配比较委托给实验板。对于有资格的
Goal/LoopX 四臂研究,传入紧凑四臂契约以复用现有因子 reducer。

```bash
loopx benchmark study-dashboard \
  --manifest-json <study-manifest.json> \
  --store <simulation.jsonl> \
  [--four-arm-contract-json <compact-four-arm-contract.json>] \
  --format json
```

Adapter 保留其 benchmark 的原生指标名、单位、方向与总计。Core 字段不是软件工程
特定的,所以同一流程适用于双臂、四臂与其他声明的 benchmark 研究。Raw 任务、
trajectories、日志、隐藏 evaluator 材料、verifier 尾部、凭据与本地路径没有上传
schema slot;producer 必须把 post-run 分析化简为脱敏洞察契约。

## 相关命令

```bash
loopx benchmark classify-artifacts <paths...> --format json
loopx benchmark candidate-source-boundary <paths...> --require-clean --format json
```

所有命令默认都是本地的、不上传的。`benchmark-toolkit` 不授予 model、Docker、
runner、上传、提交、发布或生产 authority。

活跃的 benchmark 研究项目与当前 public-safe 实践位于
[`benchmark/`](https://github.com/huangruiteng/loopx/blob/main/benchmark/README.md)。历史 runner
与单日期研究包保留在
[`deprecate/benchmark-legacy/`](https://github.com/huangruiteng/loopx/blob/main/deprecate/benchmark-legacy/README.md),
仅作源码考古。
