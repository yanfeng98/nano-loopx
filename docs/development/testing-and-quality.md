# 测试与质量体系


LoopX 协调长程 agent。一个局部正确的改动，仍可能改变 agent 选择哪项工作、是否
向用户提问，或 host 是否继续运行。因此质量体系从不同距离验证同一套已交付行为：
快速、确定性的检查保护每个 PR；更广、更昂贵的检查只在信号值得成本时运行。

## 质量分层

| 层 | 证明什么 | 常规频率 |
| --- | --- | --- |
| 单元与合同测试 | 纯规则、schema、状态转换和非法状态拒绝 | 相关 PR 必跑 |
| 稳定公开 smoke | CLI 与跨模块交付行为 | 本地聚焦；主干、每日或手动全量 |
| Catalog 驱动 canary | 覆盖所有变更面的最小风险切片 | 敏感合并与发布前 |
| CLI 输出预算 | 输出有界且能发现相对增长 | 相关 PR CI 与 premerge |
| 公开安全决策回放 | 经审阅的源状态不变量重放真实 quota-to-scheduler 链路 | 回归与控制面变更 |
| 模型行为验证 | 真实模型能正确理解当前默认载荷与安全合同 | 低频本地或手动影子门 |
| 发布结果基线 | 稳定版与候选版在匹配语义下可比较 | 发布验证或周期观察 |

这些层次互补：模型通过不能覆盖确定性合同失败；大规模 smoke 也不能代替明确指出
错误规则的聚焦回归测试。

高风险交付面需要进入可机器审计的质量 surface catalog。每一行都要指明独立语义
oracle，并把每一层明确分类为 `covered`、有理由的 `not_applicable`，或有 owner 的
`deferred`。这样既不会静默漏测，也不会强迫模型去判断确定性的 scheduler 优先级。

```bash
loopx canary quality-audit
```

在源码 checkout 中运行时，命令还会验证引用的产品、测试和文档路径仍然存在；打包
安装仍可审计分类，但会明确报告仓库引用校验不可用。

如果新增高风险 canary profile 却未分类、oracle 直接复用产品实现作为期望值、缺少
确定性最小门禁，或例外没有理由，审计会失败。合法的 deferred 行仍作为 backlog
缺口显式展示，不会伪装成仓库已经完全就绪。

测试先判断状态和规则是否正确，再验证实现是否符合。预期结果必须来自独立审阅的
不变量，不能由被测实现或当前输出生成。Characterization fixture 只记录历史
行为，不授予其正确性；发现矛盾时应修复规则并增加反例或 mutation 覆盖，不得刷新
golden 来让测试通过。

## PR 基线

### 重构真实路径门

重构交付前必须验证受影响的真实生产入口和真实后端。单测、mock 与内存 conformance
不能替代这项证据。影响 PostgreSQL authority 时，配置指向隔离临时实例的
`LOOPX_TEST_POSTGRES_URL`，运行 `npm run test:postgresql-authority-store`；跳过不算
通过。记录精确 commit、后端版本、验证行为与失败或局限；没有安全的真实环境则暂停交付。

测试使用独立临时数据库／tenant 和 runtime 目录，输入为合成 fixture 或经 owner 授权
的只读快照。集成测试会创建角色并注入 schema 级失败 trigger，禁止连接共享或生产库。
不为测试晋升正在运行的 goal、切换 provider，或修改其 registry、writer fence、Todo、
lease。私有快照和原始输出不得进入 Git 或公开 review；快照演练前后比较源指纹。
发现并发源变更只报告，不擅自覆盖或恢复。测试后停止临时数据库。

安装测试依赖一次：

```bash
python -m pip install -e ".[test]"
```

运行快速仓库门：

```bash
python -m ruff check tests loopx/canary loopx/control_plane loopx/domain_packs loopx/presentation
python -m mypy
python examples/control_plane/cli-output-budget-regression-smoke.py
python -m pytest -q
git diff --check
```

`.github/workflows/python-tests.yml` 会在相关 Python PR 上运行这条快速通道。
它刻意不包含真实模型调用和 full smoke catalog，因此普通迭代不依赖凭证、网络
时延、模型服务可用性或两小时级测试矩阵。

## Smoke 与 Canary

Durable smoke 应保护已交付行为、可复用合同、公开/私有边界，或曾让自动化卡死的
回归；不应固化某次研究文案或原始执行证据。

贡献者检查项、语义 oracle 示例、公开安全 fixture 规则和合并流程见
[什么是好的 Smoke](good-smokes.md)。

仓库卫生 smoke 是 LoopX 自身公共 checkout 的薄基线：断言必需跟踪文件存在，
执行规范的公开/私有边界扫描，并把 release 时间线收紧到每个已发布版本 tag。

```bash
python3 examples/repository-hygiene-smoke.py
```

开发时先运行一个聚焦 smoke，然后让 canary 规划器从 Git diff 中选出最小的跨表面
集合：

```bash
python examples/control_plane/interaction-scheduler-authority-smoke.py
loopx canary premerge --from-git-diff
```

`premerge` 会把调用方 Git 根目录用于 diff 卫生检查、变更 Python 编译和公开边界扫描；
LoopX 已安装的 canary catalog 仍从自身可信 release root 运行。因此该命令也可从其他
仓库或其子目录执行。

完整公开扫描保持显式且有界：

```bash
loopx canary smoke-suite --suite full-public --jobs 4 --timeout-seconds 120
```

`full-public-smokes.yml` 在主干、每日定时和手动触发时运行，不是 PR 必须门禁。
这种分层既保护质量，也避免每个小 patch 都等待最宽测试集。

### Smoke 集群健康

full-public workflow 还会把各 shard 回执聚合成一个紧凑健康产物。报告区分四种频率，
而不是把每个 smoke 都变成 PR 必跑项：显式 PR 快速 smoke、catalog 选择的 canary、
每日 full-public 全量，以及高风险 release profile。它会统计耗时、失败、超时、当前
清单覆盖率和定向 profile owner，同时不会复制 stdout/stderr tail 或仓库本地路径。

```bash
loopx canary smoke-health --receipt smoke-results
```

默认输出是有界的审阅摘要；只有显式诊断冷路径才使用 `--include-inventory`。内容完全
相同或直接嵌套执行只会成为审阅候选；名称相似、共同属于某个 profile，不足以证明两个
语义合同等价。健康审计不会自动删除或迁移 smoke。只有 daily 全量覆盖、没有定向
profile 的条目表示 owner 待澄清，并不等于该测试没有价值。

## Agent 输出预算

接口预算门会测量稳定命令场景，并比较 candidate 与 base，捕获意外膨胀、重复诊断
以及重构后悄悄回到热路径的字段。预算变化就是合同变化：实现与期望必须一起修改，
逐项解释新增或删除的语义字段；默认 agent-facing 投影变化时需要 owner review。

完整诊断包保留为显式 drill-down。只有默认路径仍能告诉 agent 下一步做什么、以及
如何请求被省略细节时，字段才能移出默认热路径。

## 决策回放与 #2191

Issue #2191 是跨层控制面回归的参考模式：最终 `interaction_contract` 是调度权威，
原始 `should_run` 和底层兼容字段不能越权；非阻塞 `user_action` 也不能满足 agent
todo 的阻塞 `required_decision_scopes`。

该回归由四层确定性测试保护：

1. 数据驱动调度决策表检查 human gate、active work、repair、mapped no-op 与
   successor-replan 场景；
2. todo-scope 测试区分兼容的阻塞 gate、通知、无关 agent gate 与悬空 scope；
3. 真实 quota builder 必须把 scope 冲突转换为有界控制面自修复，同时禁用正常交付；
4. 公开安全 fixture 存储源 todo 事实、独立审阅的不变量与期望结果；replay smoke 与
   catalog canary 在不包含原始状态、日志、prompt、轨迹或本地路径的情况下重跑真实
   quota-to-scheduler 链路。

回放期望值绝不能由被测实现生成。Reducer shape 测试仍可验证脱敏和兼容性，但必须
与语义 oracle 分开；变形测试还会验证，新增其他 agent 的无关 gate 或修改底层兼容
字段，都不能改变当前 agent 的最终决策。

窄 mutation 检查会主动翻转底层信号，证明它们不能抢占最终 human gate。这比只比对
一份 JSON snapshot 更强，因为它直接验证优先级规则。

## Doubao 模型行为门

provider-neutral 行为合同和可选 Doubao 2.1 actor 位于
`loopx.control_plane.testing`。常规 onboarding profile 是 one-arm：直接测试
candidate checkout 的当前默认载荷。产品默认行为变化时，实现与验证输入一起切换，
不会长期保留一条退休产品路径作为第二臂。

它适合验证模型是否识别 selected todo、尊重人类门禁、在健康 onboarding transition
后继续、或识别已知 projection gap。组合场景还会验证多个单独看来都合理、合在一起
却存在优先级冲突的信号：monitor lane 要求等待但 vision 合同要求 replan；user notice
仍打开但独立 successor 必须运行；advancement 被 capability 阻塞时，agent 必须先
执行 capability-bridge repair，不能退回 monitor wait。schema、冷路径恢复、精确字段
存在性和底层状态转移表仍由确定性测试负责。

Live Doubao 调用是低频本地/手动门，不进入普通 CI。`ARK_API_KEY` 只通过进程环境
注入；packet、prompt、原始响应、凭证和对话都不能成为仓库证据，只保留有界 receipt
与 mismatch code。fake transport 只能验证 adapter 的序列化、脱敏与 fail-closed，不能
作为 Doubao 行为通过证据。运行真实门禁：

```bash
python3 scripts/qualify-doubao-model-behavior-live.py \
  --qualification-id <public-safe-run-id>
```

该命令要求干净的 candidate checkout，缺少 `ARK_API_KEY` 时直接失败，receipt 绑定
该 checkout 的 Git source identity，且任一真实 provider 调用不通过都会以非零状态
退出。Actor 与晋级合同见
[Model behavior qualification v0](../reference/protocols/model-behavior-qualification-v0.md)。

replan semantic action 另有一条 function-tool 行为资格门，因为 no-tool JSON 决策不能
证明模型会使用投影覆盖来选择并持久化不同方向。它创建一个 hermetic、public-safe 的
Goal，包含两个等价的 typed progress observation，把正式 thin Codex App heartbeat
task body 与一个普通 `exec_command` function tool 交给真实模型，并用真实 LoopX CLI
运行被接受的 quota 与 refresh 命令。整个有界 host loop 只有满足以下条件才通过：
真实 quota 输出 host 投影的 coverage context 与最小 action packet，且模型随后提交的
typed semantic delta 通过写时 gate：

```bash
python3 scripts/qualify-doubao-replan-semantic-action-live.py \
  --qualification-id <public-safe-run-id>
```

模型不会收到仅用于测试的决策 schema、期望命令或预构建 quota packet。常规 heartbeat
preflight 支持 clock 与少量 workspace 读取。命令被解析为严格 allowlist，不调用
shell；quota 与 refresh 只能写入临时 fixture 内部，任何外部或仓库写入都不允许。
Actor 在执行前独立鉴定所选的 typed observation。仅读 evidence-log、纯散文、quota 前
动作、等价指纹与未落地的 action 都会失败。Receipt 只保留 action kind、命令 digest
与 typed semantic outcome。

selected-Todo 场景有自己的聚焦真实动作入口，用于 quota 选择、heartbeat 指令或共享
tool 缝的变更：

```bash
python3 scripts/qualify-doubao-selected-todo-tool-live.py \
  --qualification-id <public-safe-run-id>
```

它从同一生产 heartbeat 合同开始，执行真实 quota，并且只有当模型读取了 selected Todo
所命中的目标时才通过。在 quota 之前读取目标、选择延迟 decoy、只描述动作而不调用
tool，或发出不在 allowlist 内的命令，都会失败。

scoped-gate successor 组合场景同样是一个真实 tool loop。它的 hermetic Goal 包含一个
无关的开放 user gate，以及一个前置条件已经完成的 deferred successor。真实 quota 选出
successor 后，模型必须把 user action 呈现为非阻塞 assistant 通知，并读取精确的
successor 目标。通知后等待、省略通知，或读取被 gate 的 decoy，都会失败。

```bash
python3 scripts/qualify-doubao-scoped-gate-successor-tool-live.py \
  --qualification-id <public-safe-run-id>
```

Capability-bridge 重入是第四个真实 tool loop。它的 hermetic Goal 有一个被 capability
阻塞的 advancement Todo 与一个未完成的 monitor fallback。真实 quota 必须投影
`capability_bridge_repair`。Actor 在同一 heartbeat trigger envelope 中发送正式 task
body（含 trigger time），与 Codex App 模型通常收到的一致。默认 CLI projection 把
`interaction_contract` 放在 action-first 前缀里，而不是诊断泳道之后。模型必须先对
阻塞 Todo 的真实任务侧读取验证该 capability，再在同一 heartbeat 执行投影的 quota
重入命令；quota 必须重新选中原 Todo，全程不创建 repair Todo、不结算 turn、也不写
durable capability grant。等待或更新 monitor、在 quota 前读 callsite、在成功验证前
重入，或读取其他目标，都会失败。Quota 前允许有界 workspace 检查；quota 后无关
workspace 读取会被判定为回溯并立即失败。

```bash
python3 scripts/qualify-doubao-capability-monitor-repair-tool-live.py \
  --qualification-id <public-safe-run-id>
```

常规 live suite 是 `actual_default_model_behavior_portfolio_v0`：19 个 one-arm 场景，
每个重复 2 次。9 个 core-contract 场景覆盖正常接入、agent 身份与 goal 选择、selected
todo、peer 身份路由、same-agent 续接、最终 human gate、健康继续和 projection repair；
1 个 effect-settlement 场景覆盖 terminal closeout；2 个 action-portfolio 场景分别要求
一个可运行 fallback 顶替未来的 monitor 或 typed external wait，同时仍保留不可运行的
P0 上下文；1 个 planning-horizon 场景要求模型先检查有界的 typed strategic chain，
再运行被选中的 regression gate；该场景的 action oracle 验证有序语义阶段而不是背诵
唯一轨迹：中间允许有界只读动作，但测试必须先于最终 writeback/spend，不能在拿到测试
证据前预设 edit；writeback 与 spend 是 settlement effect，因此都不能出现在最终
settlement 后缀之前；该场景的场景内语义合同只包含 `planning_horizon`，无关的
peer/scheduler 字段仍由确定性合同覆盖。3 个组合场景覆盖 vision/monitor/peer replan
优先级、非阻塞 user notice 与 ready successor 并存，以及 capability-bridge repair
必须先于 monitor fallback；3 个 compaction 场景覆盖 JSON 预算与 source-derived 语义
一致，并分别让正常 selected work 和阻塞 gate 在超预算省略诊断下重复运行。4 个
contrast group 要求 clean/noisy 场景保持不变，同时要求 blocking gate 与 non-blocking
notice、selected work 与 required vision replan 仍然可区分。每个场景都有在 CLI
projection 前推导的独立确定性 source oracle，所有重复都必须通过；actor 硬错误不自动
重试。selected-Todo 场景从正式 thin heartbeat 开始，执行真实 quota，并要求模型实际
执行 selected Todo 指向的只读目标动作；required-vision replan 场景独立构造缺失
vision 的 hermetic 状态，执行真实 quota，并要求模型使用 host 投影的 frontier/工作源
上下文，再通过真实写路径提交 typed semantic action；其余 turn 场景仍是
packet interpretation 检查，消费 Codex App automation 使用的默认 CLI hot-path
`quota should-run` projection 并返回运行时决策，而不是复读某个全局的仅测试语义合同。
全套是 38 个有界 scenario attempt；其中 5 个真实工具场景的 provider 调用上限由各自
typed behavior harness 持有，本文不再复制易漂移的总数。scheduler、vision、writeback
与 warning 的精确字段继续由 action-signature 确定性覆盖；pair 中的 TurnEnvelope 只用
于明确的 packet 差分或结果提升声明。

Onboarding 输入来自正式 guided packet builder；provider 调用前只替换本地绝对路径。
确定性 oracle 会先检查实际 packet，因此脱敏不能掩盖命令缺失、host activation 丢失、
门禁错误、写入或 quota 消耗。Human gate 的优先级是显式规则：等待用户时没有
executable work 属于预期状态，不能误判为 projection gap。

## 精确发布 Commit 门

最终发布门不会通过第二套编排框架重新运行测试。它聚合现有测试通道的紧凑回执，并
证明它们都对应同一个干净源码身份：

```bash
loopx canary release-qualification \
  --manifest-json release-qualification.json \
  --repo-root .
```

`exact_release_commit_qualification_manifest_v0` 会在每个检查回执中重复
`git_commit`、Git tree id、干净工作树状态、包版本与版本 tag；CLI 还会从
`--repo-root` 独立读取这些字段。缺失、失败、跳过、脏工作树、rebase 漂移或版本不一致
都会 fail closed；旧 commit 的结果不能给新 tag 背书。

| 回执 | 语义下限 |
| --- | --- |
| `pytest` | 至少一项通过且零失败 |
| `ruff`, `mypy` | 零 lint 或类型错误 |
| `risk_canary` | 已选检查通过且没有未解决人工 hold |
| `full_public` | 全量集群 ready 且无失败或超时 |
| `install_upgrade_host` | 安装、升级与 host 路径均通过 |
| `public_boundary` | 零公开私有边界违规 |
| `doubao_actual_default` | 从固定 catalog 推导的实际默认 portfolio，其全部场景重复与对照均通过，且零失败、零跳过 |

每份回执只保留结果 schema、结果 digest、完成时间和有界计数。命令、stdout/stderr、
prompt、packet、模型响应、凭证与本地路径都不得进入 manifest。该命令只是只读资格
reducer：不运行测试、不调用模型、不移动 ref、不创建 tag、也不发布。即使回执 ready，
仍需 owner 作出发布决定。

## Benchmark 研究证据

确定性测试和模型行为测试验证控制面合同，但不能证明发布提升了长程结果。结果声明
必须使用小规模 stable-release-vs-candidate manifest，并匹配任务语义、runner、模型、
reasoning、timeout 与重复次数。任一不匹配或不完整都 fail closed，且不能自动发布。

当前 benchmark 研究遵循
[研究 RFC](../architecture/rfcs/long-horizon-harness-benchmark-research-program-v0.md)，
并在仓库级 [benchmark workspace](https://github.com/huangruiteng/loopx/blob/main/benchmark/README.md)
中沉淀。旧 release reducer 已归档，不再属于 active CLI 或 release qualification surface。

## 按风险审阅

| 变更 | 最小门禁 |
| --- | --- |
| 仅文档 | 链接和边界检查、聚焦文档 smoke、`git diff --check` |
| 纯规则或 schema | 单元表加聚焦 smoke |
| 调度与接入 | 单元表、真实集成、回放、catalog canary、owner review |
| 默认 agent 输出 | 以上加 CLI base/head 预算和语义字段账本 |
| 真实模型行为 | 先确定性门禁，再重复 one-arm 本地影子回执 |
| 发布晋级 | 相关 canary、发布检查、匹配结果基线、显式 owner 决策 |

敏感行为变更应便于审阅：说明权威规则，逐项列出字段变化，写清验证过的确定性与模型
行为，报告跳过项；除非发布合同明确允许，否则保持自动晋级关闭。

## 证据边界

打开 pull request 前，只扫描候选公开路径：

```bash
loopx check \
  --scan-path CONTRIBUTING.md \
  --scan-path docs/development/ \
  --scan-path loopx/control_plane/ \
  --scan-path tests/ \
  --scan-path examples/
```

禁止提交凭证、私有状态、原始 benchmark 材料、模型响应、本地绝对路径或生成日志。
优先保留紧凑 fixture id、reason code、digest 和公开安全语义投影。
