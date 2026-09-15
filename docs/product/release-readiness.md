# 发布就绪度

状态:v0.x 维护者契约。

LoopX 可以快速前进,而不必让每个合并的 PR 都感觉像一次产品发布。本笔记定义维护者在提升发布快照、推荐安装路径或告知用户哪些控制面界面可以安全构建之前应使用的小型思维模型。

## 受支持的安装与更新路径

本 fork 不发布 PyPI 包，也没有发布快照 / canary 通道（`scripts/install-local.sh` 与
`scripts/install-from-github.sh` 已在 op 036 中移除）。**两条受支持的安装路径**是就地 editable
安装（开发用）与本地构建的 wheel（发给别人用，见[离线 wheel 安装](../guides/offline-wheel-install.md)）：

```bash
cd <loopx-checkout> && python3 -m pip install -e . --no-deps --no-build-isolation
loopx workflow-skills --install
loopx doctor
```

首次安装后重启 agent host,使新交付的 workflow skills 生效。

对活动源码 checkout，`loopx update plan` 报的就是这条就地刷新命令，且 fail-closed：`apply` 为空，
绝不 `git pull`、绝不安装发布快照。各激活层的逐层读回与恢复见
[验证各激活层](../development/editable-dev-loop.md#verify-the-active-layers)。

升级使用相同的显式意图流程（对 checkout，第 3 条是 fail-closed 的空操作）：

```bash
loopx update check
loopx update plan
loopx update apply
loopx doctor
loopx extension doctor --all-enabled --execute
```

`loopx update apply` 之后,用
`loopx extension doctor --all-enabled --execute` 重新验证已启用扩展。过时的扩展就绪度
已在成功的 apply 中重新验证;上面的显式命令是独立的读回与恢复入口。仍然失败的
provider 保持关闭,直到其逐扩展 doctor 结果被修复且命令通过。参见
[扩展生命周期](../reference/extensions.md#runtime-lifecycle)。

不要把包获取、host 材料交付、核心运行时激活与已启用扩展就绪度合并为一个"已安装"
声明。
[就地开发闭环的活动层检查清单](../development/editable-dev-loop.md#verify-the-active-layers)
为每层命名了读回与恢复命令。

`loopx update` 只有两种形态（对应上面的两条安装路径）：本地 wheel 安装会重装它**记录的那个 wheel
文件**，checkout 则由 operator 就地刷新（`apply` 为空，fail-closed）。本 fork 没有归档快照、没有
`stable` 引用、也没有 canary wrapper 通道——`--ref` / `--archive-url` / `--rollback` 这些旗标随发布
快照通道在 op 036 中一起移除了。

**回滚 = 放回上一个安装**：保留上一个 wheel 文件，或把 checkout 切回上一个已知可用的提交，然后重跑
该路径的安装命令并跑 `loopx doctor`。本 fork 不做在线版本钉选，也没有"上一条发布快照"可退。

## 已合并不等于运行时活动

合并后检查证明所测源提交上的行为；它不证明已安装的 LoopX 运行时包含该提交。当修复在版本之后到达
`main` 时这一区别很重要：包版本可能仍匹配，而已安装的源提交落后。

本 fork 用两条本地证据回答"我现在跑的是哪一份"：

- `loopx doctor` 的 `install_path`（`editable_checkout` 或 `local_wheel`）与 `wheel_path`；
- checkout 场景下的 `manifest_source_*` 血缘：release manifest 记录的源提交对比 `loopx doctor`
  报告的可信来源。

在最新 `main` 校验后关闭 PR monitor 是有效的，但除非证据表明**已安装的运行时就是修复后的源码**
（editable checkout 且工作区与该提交一致，或该 wheel 由该提交构建），否则收尾不得声称修复在已安装
运行时中活动。

## 命名版本契约

版本来源是 `loopx.__version__`，由 `pyproject.toml` 镜像；期望的 tag 形如 `vX.Y.Z`（当前 `v1.1.0`）。
本 fork 不发布到 PyPI、不构建签名归档，也不提供在线升级通道，所以"命名版本"只在本仓库内生效：

- 当用户可见行为变化时，同时提升 `loopx.__version__` 与 `pyproject.toml`；
- 用 `python3 scripts/release_artifacts.py expected-tag` 核验两者一致（不一致会直接报错）；
- 需要对外分发时，用 `bash scripts/build-wheel.sh` 构建 wheel 并**自行保管**该文件——它就是回滚与
  再分发的依据（见[离线 wheel 安装](../guides/offline-wheel-install.md)）；
- `loopx doctor` 与 `loopx update check` 只报告本地安装的版本与形态；需要确认某个提交的内容时，
  看当前 checkout 的 git 历史，而不是找外部发布源比对。

## 兼容 gate

在对外分发或公开指南告诉用户依赖新界面之前,运行覆盖所触界面的最小 gate:

```bash
python3 -m py_compile loopx/*.py
python3 examples/fresh-clone-quickstart-smoke.py
python3 examples/loopx-update-smoke.py
python3 examples/release/release-version-contract-smoke.py
python3 examples/release/release-readiness-doc-smoke.py
python3 examples/repository-hygiene-smoke.py
git diff --check
loopx check --scan-path README.md --scan-path docs/ --scan-path examples/
```

这不是通用完整套件。为变更的命令、投影或工作流添加聚焦 smoke。不要把基准原始
日志、原始任务文本、轨迹、验证器输出、凭据或本地私有产物路径作为发布 evidence
要求。

在单独车道通过后,把它们的紧凑凭据绑定到精确干净的发布 checkout,再打 tag 或
移动 `stable`:

```bash
loopx canary release-qualification \
  --manifest-json release-qualification.json \
  --repo-root .
```

`exact_release_commit_qualification_manifest_v0` 契约要求在 pytest、Ruff、mypy、
基于风险的 canary、full-public、install/upgrade/host、公开边界与实际默认单臂 Doubao
凭据之间具有相同 Git 提交、Git tree id、包版本与版本 tag。该命令还检查当前 checkout
并拒绝脏源或 rebase 源。它只归约现有有界凭据:不执行测试、不调用 provider、
不移动引用、不创建 tag、不发布发布。

## Canary 模型

发布 canary 是目录知情的就绪度切片。它近 E2E 的意义在于跨多个缝合线跟随真实
提升或运维者路径,但它刻意小于完整端到端测试套件。它的职责是回答"所触公开界面
能否在此声明边界下提升",而不是"每条 LoopX 路径都正确吗"。

从现有交互模式族选择 canary 分组;不要仅为描述校验 bundle 而添加新 IP:

- status/quota/scheduler 变更应包含工作路由检查,如 `quota should-run`、scheduler hints 与热路径接口预算;
- state 投影或公开/私有变更应包含 State And Boundary 检查,如 `loopx check`、任务图或 todo 详情冷路径契约;
- dashboard/frontstage 变更应包含目录或 fixture 路由检查,仅当视觉界面本身被提升时才使用浏览器 smoke;
- release/install 变更应包含安装器、更新、包装器、doctor 与公开边界检查;
- benchmark 或外部 evidence 变更应只用紧凑生命周期 evidence,绝不用原始任务文本、原始日志、轨迹或验证器尾部。

默认提升 canary 是:

```bash
```

默认 dashboard 策略是 `--dashboard-mode=auto`:源 checkout 在
`apps/presentation/dashboard` 存在时运行 dashboard 演示就绪度,而省略该 dashboard
已安装的运行时跳过该可选界面时,在 canary 输出中保持该省略可见。当
dashboard/frontstage 本身被提升时使用 `--dashboard-mode=require`;仅当发布边界刻意
排除 dashboard 应用时使用 `--dashboard-mode=skip`。

仅当你刻意想追加新鲜提升就绪度 evidence 时使用写回形式:

```bash
```

对于更广泛的源 checkout 回归,保持 `loopx canary smoke-suite` 为真相源。本地与
LoopX 自动化应继续直接使用 runner payload:

```bash
python3 examples/run-smokes.py --suite default-public --module canary
loopx canary smoke-suite --suite default-public --module canary
```

对于更大的源 checkout 清扫,使用 runner 的有界并行,而不是把 smoke 语义移入第二个
测试框架。`--jobs` 保持 LoopX runner payload 为真相源,同时为声明调度敏感界面的
smoke 保留串行执行:

```bash
python3 -m loopx.cli canary smoke-suite --profile public-smoke-watch --jobs 4 --timeout-seconds 60
python3 examples/run-smokes.py --suite full-public --jobs 4 --timeout-seconds 60
```

对于可重复的 canary/重构批次,优选命名 smoke-suite profile 而非手工整理的脚本列表。
Profile 展开为与 `--module`、`--script`、目录选择器与 pytest 门面相同的 runner payload:

```bash
loopx canary smoke-profiles
loopx canary smoke-suite --profile core-control-plane --no-execute
loopx canary smoke-suite --profile core-control-plane --offset 20 --limit 20 --timeout-seconds 60
loopx canary smoke-suite --profile canary-runner --timeout-seconds 60
python3 examples/run-smokes.py --profile public-entry-install-release --no-execute
```

使用 `--offset` 加 `--limit` 在稳定窗口内扫描大 profile,而不必在每个心跳重跑同一
前缀批次。

默认 `pytest` 是快速单元与契约车道。Smoke-suite 门面是显式选择加入,因此常规
PR 测试运行不会悄然扩展成 canary 矩阵。CI 在需要 JUnit 报告时可以把显式 runner
选择包装进 pytest。门面仍通过子进程执行每个所选 `examples/**/*-smoke.py`;它不
是把遗留 smoke 迁移为 pytest 单元测试:

```bash
python3 -m pytest tests/test_smoke_suite.py \
  --loopx-smoke-suite default-public \
  --loopx-smoke-profile canary-runner \
  --loopx-smoke-offset 0 \
  --junitxml smoke-suite.xml
```

Ruff 命名空间选择与包覆盖下限属于发布检查的一部分。下限是回归护栏,不是充分覆盖的声明;当持久
行为从子进程 smoke 移入聚焦测试时提高它。

[架构测试](../../tests/architecture/test_control_plane_import_boundaries.py)
无迁移异常地拒绝外向控制面依赖与禁止的状态依赖,并保护配额 Markdown 的呈现归属。
边界理由参见
[依赖策略](../architecture.md#current-dependency-budget)。现有的全源码 lint 债务
单独表征。严格 mypy 范围是 [`pyproject.toml`](../../pyproject.toml) 中的
`[tool.mypy].files` 列表;用 `python -m mypy` 检查该精确范围。只有在有界清理
后扩大每个受保护命名空间,而不是复制变化的文件计数或大规模修复无关代码来让宽泛
gate 变绿。

如果源 checkout 安装了可选前端依赖,dashboard 就绪度可以包含在同一 canary 中。
如果当前安装省略 dashboard 应用,canary 应优雅降级并记录该边界,而不是让无关的
CLI/install 提升失败,或悄然把 dashboard 路径当作已覆盖。

## 可安全依赖的内容

当聚焦 smoke 通过时,把这些 v0.x 界面视为足够稳定,可放入用户指南、示例与 host
集成:

- `loopx doctor`、`loopx update`、`loopx check` 与无 clone 安装器;
- 安装或 update apply 后用于已启用扩展就绪度的 `loopx extension doctor`;
- 项目生命周期命令:`bootstrap`、`connect`、`status`、`refresh-state`、`registry` 与 `sync-global`;
- todo 生命周期命令:`todo add`、`todo claim`、`todo update`、`todo complete`、`todo list`、`todo supersede` 与 `todo archive`;
- 控制面读取路径:`quota should-run`、`quota spend-slot`、`review-packet`、`heartbeat-prompt --thin`、任务图投影与冷 todo 详情引用;
- 公开斜杠命令名:`/loopx`、`/loopx <goal>`、`/loopx-global-summary`、`/loopx-global-gates`、`/loopx-global-todos` 与 `/loopx-global-risks`;
- `~/.codex/loopx` 下被忽略的本地 state 边界、项目本地注册表文件,以及被 `loopx doctor`、`loopx status` 与 `loopx check` 识别的项目本地 active-state 工作台文件。

在契约文档另有说明前,把这些视为实验性:

- benchmark runner 行为、评分、上传与原始任务执行路由;
- 发布协议契约之外的 host-plugin 命令注册实现;
- 不属于公开状态数据契约的 frontstage/dashboard 呈现细节;
- 仍在 todo 创建、配额投影、写回与迁移中推广的 monitor 调度节奏字段。

## 发布说明清单

从规范[发布说明模板](release-note-template.md)开始生成最终 GitHub 发布正文。
它的第一个实质性部分是紧凑的 `## 发布决策` 块,回答读者在查看详细变更日志
前需要的五个问题:

| 字段 | 必需决策 |
| --- | --- |
| `**谁需要升级:**` | 命名受影响的用户或操作者、现在升级的理由,以及谁可以留在当前版本。 |
| `**本版本解决了什么:**` | 用用户结果语言说明具体故障、缺失工作流或可靠性缺口。 |
| `**破坏性变更:**` | 以 `无。` 或 `有。` 开头;为是时给出迁移路径,为否时仍披露变更的默认值、废弃或实验边界。 |
| `**如何验证:**` | 说明升级后期望结果,并包含一个证明包身份与受影响行为的最小可运行 `bash` 块。 |
| `**贡献者:**` | 命名发布维护者与 tag 范围的社区贡献者,或明确说明本发布无社区贡献。 |

发布说明是**单语中文**。不再维护英文版本或与中文镜像并排的双语分节；模板与生成正文
只保留一套分组。决策摘要是决策辅助,不是对下方详细产品分组、逐声明 PR evidence、
可选能力生命周期或精确提交校验 evidence 的替代。

优先保留用户可见的产品变更。当上一与当前范围之间有外部社区贡献时，在产品分组之后、
兼容性、校验或更新材料之前添加显眼的 `## 社区贡献者` 部分，链接每个符合条件的
handle 与相关 pull requests，并总结具体贡献；没有符合条件的贡献时省略本节。

从 tag 到 tag 的 Git 范围与合并 PR 元数据构建列表,而不是提交显示名或未经评审的
生成变更日志。即使同一 pull request 在产品分组下再次链接,归因也是发布契约的一部分。

把其余发布说明组织为下列稳定分组。省略空产品分组,而不是发明填充:

1. **状态内核与控制面**:state、todo、配额、调度器、gate、对等方路由与运行时权威变更。
2. **能力与工作流**:已交付的用户工作流,如 Issue-Fix、Explore、Reward Memory、接入与 LoopX Turn。
3. **质量与测试**:确定性测试、canary、输出预算、模型行为资格确认与发布 gate。
4. **基准与集成**:基准适配器、Lark、host 运行时与其他外部边界。
5. **文档与兼容性**:公开契约、安装/更新指引、迁移、默认值与刻意排除。

有合格社区贡献的发布必须在产品分组之后、兼容性或校验材料之前添加
`## 社区贡献者`,链接每位符合条件的贡献者与其具体贡献范围。
没有合格贡献者时省略本节。发布必须保留这些分组边界,并使用匹配的标题
**状态内核与控制面**、**能力与工作流**、**质量与测试**、
**基准与集成**与**文档与兼容性**；不得把几个分组塌缩成一个泛化亮点列表、
省略非空分组或弱化贡献者归因。

在每个非空分组内,每条实质性声明必须带一个或多个直接 pull request 链接（本仓库的 PR）。
末尾的 compare 链接
仍有用,但它不替代逐声明 PR 归因。避免仅以裸 PR 范围作为 evidence,因为范围可能
隐藏被省略或无关的变更。

在决策摘要与产品分组之后,每条公开发布说明还应记录:

- 此稳定发布使用什么包版本与公开 tag 名称?
- 新用户应跟随哪条安装/更新路径?
- 哪些界面仍是实验性或刻意排除?
- 对于每个新增或实质性变更的实验性、默认关闭或选择加入能力,包含一条**可选能力激活**条目:命名其范围、只读预览、确切的启用与停用命令、前置条件或安全 gate,与规范文档。若不存在持久开关,说明选择加入是按命令或 preset。
- 公开/私有扫描是否在变更的文档、示例与工作流文件上运行?
- 完整 `pytest`、聚焦发布/安装契约、基于风险的 canary 与提升就绪度/公开边界检查是否在精确发布提交上通过?
- `loopx canary release-qualification` 是否确认每个必需的紧凑凭据匹配同一干净提交、Git tree、包版本与 tag?
- 低频实时模型 gate 是否对实际默认面向 agent 包运行并至少重复两次?记录模型 id、检查的行为决策、调用次数、失败与跳过,但绝不保留原始提示、包、响应、凭据或本地路径。这仍是本地/手动发布 gate,而非常规 CI。
- 若发布声称基准或长程结果改进,匹配的稳定版对候选版结果基线是否通过?若没有结果声明,说明这一昂贵 gate 并不需要,而不是暗示它运行过。

### 最终发布正文使用 gate

发布说明 PR 不是充分 evidence。发布前,把完整最终 GitHub 发布正文保存为被忽略
或临时的 Markdown 文件,并校验该精确文件:

```bash
python3 examples/release/release-readiness-doc-smoke.py \
  --release-notes <final-release-body.md> \
  --surface "<new-or-materially-changed-surface>" \
  --surface "<another-surface>"
```

从 tag diff、合并 PR 清单与发布声明派生重复的 `--surface` 值。每个命名界面必须有
`## 可选能力启用与使用` 下的 `### <surface>` 条目,包含这些显式字段:

| 字段 | 必需内容 |
| --- | --- |
| `**启用:**` | 确切安装/启用命令,或无持久开关时确切的按命令/配置选择加入。 |
| `**验证:**` | 最小可运行状态、读回或验证命令。 |
| `**停用 / 回退:**` | 确切停用、卸载、envelope 移除或回退路径。 |
| `**权限边界:**` | 激活不授予的写入、合并、provider、隐私与 host 限制。 |
| `**文档:**` | 规范的带版本文档链接。 |

每个条目需要至少一个可运行 `bash` 块。没有新增或实质性变更可选能力、工作流或 host
界面的发布,必须改用 `--expect-no-optional-capability-changes` 运行 gate,并包含
验证器要求的精确无变更声明。同时省略界面列表与显式无变更决策会失败关闭。

发布后,用 `jq -rj` 读回完整远程正文,将其 hash 与评审的本地文件比较,并对读回应用
同一验证器。不要验证一个草稿然后发布不同的正文。

### 能力叙述 gate

对于每个新增或实质性变更的能力,在三层显式结构上写发布声明:

1. **用户结果**:在命名协议、provider、渲染器或其他实现机制之前,用产品语言说明用户现在可以完成什么。
2. **交付的层**:确定发布提供的是控制面或协议内核、内置适配器或呈现层,还是完整端到端工作流。命名证明该层的命令、文档或 smoke。
3. **最后一英里边界**:命名任何仍然缺失或显式选择加入的默认 profile、收集器、调度器、目的地、凭据设置或发布步骤。不要过度声称完整工作流,但也不要仅用机制措辞隐藏已交付核心。

内置能力不因其部分收集器、渲染器、sink 或 provider 可选,就成为可选扩展。把内置
结果与其生命周期与 provider 激活分开描述。当发布交付一个结果的连续层级时,例如
报告内核之后接 HTML 呈现层,逐一归因并解释每层,而不是把两者折叠进一个通用集成
要点。

发布 PR 与最终 GitHub 发布正文必须使用相同分组与贡献者归因,加上相同校验凭据。
在 rebase 或合并任何额外运行时变更后重跑 gate;更早提交的结果不能认定后一 tag。
公开 git 历史、合并 PR 元数据与交付的 CLI 行为仍是真相源。

## 相关文档

- [Codex CLI 打包安装路径](runtimes/codex-cli/codex-cli-packaged-install.md)
- [快速开始](../guides/getting-started.md)
- [更新说明](../update-notes/README.md)
- [公开/私有边界](../public-private-boundary.md)
- [交互模式目录](../concepts/interaction-pattern-catalog.md)
