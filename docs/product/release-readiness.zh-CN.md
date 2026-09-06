# 发布就绪度

> [English](release-readiness.md)

状态:v0.x 维护者契约。

LoopX 可以快速前进,而不必让每个合并的 PR 都感觉像一次产品发布。本笔记定义维护者在提升发布快照、推荐安装路径或告知用户哪些控制面界面可以安全构建之前应使用的小型思维模型。

## 受支持的安装与更新路径

对于首次用户,优选规范 PyPI 发布:

```bash
python3 -m pip install --upgrade loopx
loopx workflow-skills --install
loopx doctor
```

PyPI 负责常规发布获取与依赖解析。`loopx update
apply` 使用同一持有环境,然后刷新 LoopX host 材料与读回;它不切换通道。

PyPI 与归档安装使用相同的显式意图流程:

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
[安装指南的活动层检查清单](../guides/installing-loopx.md#verify-the-active-layers)
为每层命名了读回与恢复命令。

对于 pip 或 pipx 发行,apply 委托给该 owner。对于归档快照,apply 默认使用公开
`stable` 引用并保留原子快照回滚。仅对维护者/开发归档资格确认使用
`loopx update plan --ref main` 与 `loopx update apply
--ref main`。当归档包装器损坏到无法运行自己的更新器时,重新运行 curl 安装器仍是
修复路径。

对于贡献者,保持 clone-plus-canary 路径:

```bash
git clone https://github.com/huangruiteng/loopx ~/loopx
~/loopx/scripts/install-local.sh
loopx doctor
loopx-canary doctor
```

PyPI 路径是用户默认路径。Clone-plus-canary 路径是维护者校验路径,无 clone 归档是
恢复回退。

在提升一个稳定的安装/更新建议之前,维护者必须把公开 `stable` 引用移动到通过本
gate 的发布提交。当 `stable` 缺失或过时时,不要声称稳定通道就绪。

## 原子本地提升失败矩阵

本地 clone 安装通过 `scripts/install-local.sh` 提升。默认可执行文件切换是原子
符号链接替换,仅在候选发布目录通过深度 `loopx doctor` 校验及任何必要的
workflow-skill 预检后运行。贡献者应把下面矩阵视为安全失败契约;不要发明第二条
提升路径,也不要声称失败的候选成为活跃默认。

已交付覆盖位于
`examples/release/release-promotion-concurrency-smoke.py`(锁、等待与预切换拒绝)与
`examples/release/local-install-promotion-boundary-smoke.py`(仅 canary 边界、
显式覆盖与 skill 预检停止)。

| 情形 | 何时发生 | 在默认符号链接切换之前? | 等待方/恢复行为 | 贡献者停止点 |
| --- | --- | --- | --- | --- |
| 提升守卫被持有 | 另一安装持有 `releases/.install-guard` | 是:等待方尚未保留或切换 | 等待方轮询 flock;被阻塞期间不得创建竞争的 `.install-lock`。Owner 解锁后,等待方获取守卫并完成 | 重试是安全的。不要删除活跃守卫或绕过它强制提升 |
| 活跃遗留锁 owner | `releases/.install-lock` 命名一个活跃 PID | 是:超时的等待方永远不进入候选构建或切换 | 等待方以 `timed out waiting for another local install` 超时;活跃 owner 锁与 PID 文件保持不动 | 停止并等待活跃安装器,或请求维护者。不要收割活跃 owner 的锁 |
| 空或死锁遗留锁 | 锁目录没有有效活跃 PID | 是:新 owner 发布其 PID 前被收割 | 等待方收割被中断的锁,然后获取所有权并继续 | 安全的自动恢复。无需维护者动作 |
| 并发同秒安装 | 两个提升安装以共享 release-id 种子竞争 | 部分:每个等待方在自身切换前在守卫/锁下串行化 | 每次运行获得不同的发布目录(`id`、`id-2`、…);两者完成后保留一个经审计的默认符号链接 | 把不同 release id 视为预期。不要中途手工编辑发布目录名 |
| 不完整候选(doctor 失败) | 候选包无法通过深度 doctor 或必需的包根检查 | 是:候选目录被删除;先前默认目标被保留 | 不发生等待方切换。仅在 checkout 完整且 doctor 干净后重跑 | 停止提升。修复 checkout;不要设置 `LOOPX_PROMOTE_DEFAULT=1` 绕过 doctor |
| Skill 预检被阻塞 | 精确 host 入口 skill 无法物化(例如用户拥有的冲突 skill) | 是:发布候选被移除;现有默认二进制保持不变 | 失败局限于安装尝试本身;没有部分默认提升 | 停止。解决 skill 所有权冲突,或先不带该 skill 界面重试 |
| 不受信任的 checkout(自动模式) | Checkout 脏、不在批准的默认引用上,或否则不受信任 | 默认时为是:安装器从不构建提升的发布快照 | 安装器以仅 canary 退出(`promotion mode: canary_only_untrusted_checkout`),保持现有默认可执行文件不动,并可能刷新 `loopx-canary` | 使用 `loopx-canary` 校验。除非你明确批准该 checkout 为维护者拥有的默认,否则不要设置 `LOOPX_PROMOTE_DEFAULT=1` |
| 显式覆盖 | 在否则不受信任的 checkout 上设置 `LOOPX_PROMOTE_DEFAULT=1` | 否:这是候选校验后的刻意识别切换路径 | 提升在 `release.json` 与 doctor 来源中可审计为 `explicit_override` | 贡献者边界到此为止。显式默认提升、移动公开 `stable`、打 tag 与 PyPI 发布仍为维护者专属 |

贡献者安全的默认行为:

- 从普通功能 checkout 优先做仅 canary 安装。
- 把任何列为"在默认符号链接切换之前"的失败视为前一默认仍必须存活的证明。
- 当等待方在活跃 owner 上超时,停止;恢复属于该 owner 完成或维护者回收真正死锁。
- 不要文档化、脚本化或 smoke 化一条在没有 `LOOPX_PROMOTE_DEFAULT=1` 加显式维护者批准的情况下移动 `stable`、发布包或声称默认提升的贡献者路径。

## 已合并不等于运行时活动

合并后检查证明所测源提交上的行为。它不证明已安装的 LoopX 运行时包含该提交。
当修复在最新命名版本之后到达 `main` 时,这一区别很重要:包版本可能仍匹配,而
已安装的源提交落后。

对归档维护者资格确认使用 `loopx update check --ref main`。其
`runtime_activation_qualification` 结果把 release-manifest 源提交与 `loopx doctor`
报告的受信来源血缘比较:

- `runtime_active` 意味着已安装提交就是目标提交或包含它;
- `release_or_install_successor_required` 意味着已安装提交落后或发散,因此必须显式保持发布/安装后继;
- `activation_qualification_required` 意味着提交血缘不可用或属于不同的 `repo/ref`;运行时活动声明必须失败关闭,直到身份被刷新。

在最新 `main` 校验后关闭 PR monitor 是有效的,但除非此凭据为 `runtime_active`,
否则收尾不得声称该修复在已安装运行时中活动。发布仍是单独的维护者动作。当资格
确认命令本身从更新的源代码运行时,请用 `--installed-doctor-json` 传入旧版已安装 CLI
的本地快照;此选项是只读的,仅由 `update check` 接受。

## 命名版本契约

LoopX v0.x 版本从 GitHub 打 tag 并构建。发布工作流把产物发布到 GitHub Releases,
并在其 Trusted Publisher gate 通过时发布到 PyPI;每次稳定提升仍需一个包版本名。
版本来源是 `loopx.__version__`,由 `pyproject.toml` 镜像;该版本期望的公开 tag 是
`vX.Y.Z`。

移动 `stable` 前,维护者应:

- 当用户可见的发布行为变化时,同时提升 `loopx.__version__` 与 `pyproject.toml`;
- 创建或验证匹配的 Git tag,例如 `v0.1.3`;
- 发布 canary 通过后,把 `stable` fast-forward 到该 tagged 提交;
- 确认 `release.json`、`loopx doctor` 与 `loopx update check` 报告相同的包版本与 tag;
- 告诉现有用户先运行 `loopx update check`,当检查推荐或他们想要刷新到命名稳定发布时再运行 `loopx update apply`。

发布工作流从 tagged 提交构建 wheel 与 source distribution。其发布资产包含规范的
`SHA256SUMS` 文件,且 GitHub 为两个包与校验清单记录构建来源证明。安装前验证下载的
bundle:

```bash
sha256sum --check SHA256SUMS
gh attestation verify loopx-X.Y.Z-py3-none-any.whl --repo huangruiteng/loopx
gh attestation verify loopx-X.Y.Z.tar.gz --repo huangruiteng/loopx
```

校验和证明下载字节与发布清单匹配。单独的 attestation 把这些字节绑定到仓库、
工作流、提交与构建事件;两种机制都不声称包无漏洞。

PyPI 发布是同一构建的显式、失败关闭扩展。发布工作流仅在维护者配置了以下全部条件
时才发布:

- 名为 `loopx`、带 `huangruiteng/loopx` 与 `.github/workflows/release-artifacts.yml` 的 Trusted Publisher 的 PyPI 项目;
- 名为 `pypi` 且匹配 Trusted Publisher 配置的受保护 GitHub 环境;
- 仓库变量 `PYPI_PUBLISH_ENABLED=true`。

不要添加长期 PyPI token。缺上述任一条件时,GitHub Release 包及其验证材料仍会生成,
而 PyPI 任务保持跳过。

## 公开发布时间线

公开 GitHub 发布时间线从 `v0.1.3` 开始。更早的工作应视为本地控制面、安装器、
更新路径与 canary 路线的公开前引导,而不是面向用户的发布基线。

- `v0.1.3` 于 2026-07-02 14:45 +08:00:提交 `10509b06` 的初始公开稳定通道发布。此版本让 LoopX 可解释为面向长程 AI agent 的无 clone、local-first 控制面:安装、更新、doctor、命名版本报告,以及首批公开 status/quota/todo/gate 界面可一起推荐。
- `v0.1.4` 于 2026-07-03 00:24 +08:00:提交 `07d0a753` 的快速跟进发布。此版本收紧了产品能力 monitor 投影、发布就绪度检查与 canary evidence,使首批公开基线更容易诊断与刷新。
- `v0.1.5` 于 2026-07-03 13:28 +08:00:提交 `c036d60e` 的长程执行加固发布。此版本改进了 quota/status/runtime 路由、monitor 与调度器投影、发布打包覆盖,以及针对停滞或低进展 Loop 的结果下限恢复。
- `v0.1.6` 于 2026-07-03 17:07 +08:00:提交 `1e3df9df` 的可见多 agent 启动加固版本。此版本让自动研究启动更容易看到与触发,澄清了去中心化 pane 路由,收紧了 monitor 与调度器投影,并扩展了 Codex CLI 首次运行发布检查。
- `v0.1.7` 于 2026-07-04 12:52 +08:00:匹配 `v0.1.7` tag 的命令入口集成发布。此版本让受支持的入口层显式化:Codex 安装 LoopX 命令门面 skill 如 `$loopx`,Claude Code 获得匹配的 skill 入口,遗留 prompt shim 退役,丰富的 workflow skills 仍可用于隐式 LoopX 行为。
- `v0.1.8` 于 2026-07-04 16:53 +08:00:匹配 `v0.1.8` tag 的确定性 host-loop 激活发布。此版本为新的 agent host 提供显式 `agent-onboard` 契约,用于选择 `codex-app`、`codex-cli`、`claude-code`、`opencode`、`manual` 或 `other-agent`,拒绝 `codex` 等含糊输入,并在 todo 写回后让 `/loopx <task>` 激活或 gate 正确的 host loop。
- `v0.1.9` 于 2026-07-05 21:45 +08:00:匹配 `v0.1.9` tag 的真实自动研究与 agent 范围 evidence 发布。此版本移除了虚假的自动研究演示指标,让 KNN preset 使用带公开安全 evidence 写回的真实基准工作区,暴露按角色命名的可见研究 pane,把 agent 范围 evidence 读取提示接入重规划,并在已完成的推进没有下一个可执行 todo 时加固后继/前沿恢复。
- `v0.1.10` 于 2026-07-06 11:50 +08:00:匹配 `v0.1.10` tag 的有范围用户 gate 与 agent 管理发布。此版本让阻碍型 owner todo 显式类型化为 `user_gate` 或非阻碍 `user_action`,用 `blocks_agent` 限定逐 agent gate,添加只读的实时 agent 管理状态投影,并继续把 quota、todo、scheduler、review packet 与 handoff 规则移入有界控制面上下文,附聚焦 canary 覆盖。
- `v0.1.11` 于 2026-07-06 19:38 +08:00:匹配 `v0.1.11` tag 的愿景重规划与恢复路由发布。此版本让 goal 愿景缺口参与配额/重规划决策面,在配额与交互契约中保留延续审计,在新 evidence 关闭时取代陈旧的愿景检查点缺口,并在愿景缺口是真实工作还是陈旧状态时添加 judge 指引。它还提升了最新控制面有界上下文清理、自动研究后继/evidence 修复、connector source-map 包、结构化 run-index 分类与 Codex CLI/TUI 恢复修复。
- `v0.1.12` 于 2026-07-08 02:05 +08:00:匹配 `v0.1.12` tag 的呈现代码与读模型、前沿恢复发布。此版本把大型 status、goal-channel、dashboard 与 Lark 渲染路径移入有界的 presentation/read-model 模块,修复仅 monitor 加开放愿景的前沿重规划缺口,让安装器重跑安全覆盖过时的包装器/文件,更早暴露 premerge canary 进度,并提升自动研究可见 worker/后继路由加上所选的公开基准 route/profile 与 SkillsBench 辅助函数加固。
- `v0.1.13` 于 2026-07-08 18:15 +08:00:匹配 `v0.1.13` tag 的引导式接入与多 agent 控制面发布。此版本让新项目设置更易修复:引导式 start-goal 预览(#1631, #1633)、非破坏性写入范围迁移(#1636)、交付尺度别名与更清晰的 refresh-state 诊断(#1641);把主控制器路由到 subagent 编排(#1622)并在显式默认关闭的功能开关后(#1643);改进调度器 ACK/退避恢复与心跳迁移(#1626, #1639);把 quota/status fixture 热路径、Lark 投影行辅助函数与 content-ops markdown 渲染器拆进更窄的模块(#1640, #1642, #1644, #1646);添加公开安全的外部 ML 任务台账(#1627);加固 SkillsBench 来源/可计数性/启动器 evidence(#1612, #1620, #1621, #1625);并放宽本地 `next_action` / `recommended_action` 文本以允许本地项目路由引用,同时仍拒绝内联凭据(#1645)。
- `v0.1.14` 于 2026-07-09 11:49 +08:00:匹配 `v0.1.14` tag 的开发者贡献探索拓扑与 monitor/quota 恢复发布。此版本提升软件探索结果层(#1546):公开 explore 节点/边/发现记录、Lark 呈现映射、图导出、router/load-profile 规划原语,以及受各 goal 的 `spawn_policy` gate 的默认拒绝 `explore_harness` worker/todo 分支规划器。它还发布了防止安静 monitor 轮询塌缩回短间隔的 monitor 调度节奏修复(#1699 及相关调度器修复),加上针对用户 gate 计数、已完成 todo 后继、evidence 日志计数、交付血缘与紧凑 agent 车道状态摘要的 quota/status/todo 读模型加固(#1707-#1716)。
- `v0.1.15` 于 2026-07-10:匹配 `v0.1.15` tag 的可执行路由与长程可靠性发布。此版本让面向 agent 的当前动作与配额所选 todo 更显式,集中主动作解析,并在有界进展中保留重规划确认、过滤恢复、愿景生命周期状态与 due monitor(#1720, #1731, #1751, #1757, #1764-#1766, #1769-#1770)。它通过静默超时处理、身份/能力 gate、无交接车道保真与类型化延续策略加固外部 monitor 与多 agent 延续(#1722-#1724, #1745, #1747, #1754, #1773)。实验性 issue-fix 与 SkillsBench 路由获得可行性、生命周期、evidence、失败归因、缓存/代理、预热与台账收尾改进(#1726, #1734, #1738-#1744, #1748-#1750, #1753, #1756, #1759-#1763, #1767-#1768, #1771-#1772)。本版本还新增并修复了并行 full-public smoke 清扫,修复了直接安装 doctor 行为,澄清了 Explore 的可测量指标契合度,并关闭了 todo CLI 所有权预算回归(#1721, #1725, #1727-#1730, #1735, #1743, #1752, #1774)。
- `v0.1.16` 于 2026-07-10:匹配 `v0.1.16` tag 的归档安装来源热修复。此版本把 release-manifest 生成与调用方的工作目录及继承的 Python 路径隔离,因此从较旧 LoopX checkout 运行更新不会把该 checkout 的包版本烙印进新的稳定快照。无 clone 发布 gate 现在直接覆盖这种陈旧 checkout 调用(#1776)。此热修复无产品能力或 state 迁移变更。
- `v0.2.0` 于 2026-07-11:匹配 `v0.2.0` tag 的对等 agent 运行时与 issue-fix 控制面发布。此版本完成 v0.2 运行时从层级 agent 所有权向对等 agent 的切换:任务认领是软路由信号,独立交接使用 `continuation_policy=independent_handoff` 加 `excluded_agents`,陈旧遗留评审延续路径被拒绝或迁移。它还把 issue-fix 能力从可行性规划提升为更完整的公开维护者 Loop,含调用方仓库分支准备、验收产物、评审者请求回退、PR 生命周期观察与 domain-state 写回。Explore Harness 与长程基准投影获得更强的公开结果契约,而 install/update、release provenance、quota、todo、scheduler 与 protocol-action smoke 被清扫进 0.2 发布截线下的 full-public 套件。
- `v0.2.1` 于 2026-07-12:匹配 `v0.2.1` tag 的面向 agent 质量与长程可靠性快速跟进。此版本通过 TurnEnvelope 契约让有界 Turn 上下文显式,新增轨迹卫生与包重复测量,并在修剪重复热路径材料的同时保留动作契约。Issue-Fix 获得仓库快照、决策有用记忆、Explore 投影、评审者/CI 凭据、影响指标与新发现公开缺陷的受保护提升。可选 Explore 规划现在保留独立实验车道并支持资源感知的投资组合决策。对等路由在任务租约有效性、建议性 agent 配置、延迟后继排除与非阻碍用户动作上加固。仓库还建立并行 pytest、Ruff、严格类型、导入边界、覆盖下限与发布提升并发检查,使这些更广泛能力保持可维护。
- `v0.2.2` 于 2026-07-12:匹配 `v0.2.2` tag 的可见执行与投影可靠性快速跟进。Explore 获得可恢复执行片段与基于 ReplayPoint 的反事实分支,加上可选的面向 owner 的视觉 sink 与公开入口界面中的真实图示例(#1892, #1962, #1965-#1966, #1971)。可见多 agent 运行现在只唤醒其可运行状态变化的车道,并在启动前冻结最新兼容 host Codex CLI(#1967, #1973)。Diagnose 能力投影、终结 PR gate 调和与 monitor 负载下的愿景重规划得到修复(#1963-#1964, #1969)。基准比较、报告、学习台账与结果读模型移入其控制面运行时 owner,同时保留兼容导入并恢复 full-public smoke 分片(#1961, #1968, #1970, #1972)。无需持久 state 迁移;Explore 执行与视觉 sink 仍是显式选择加入。
- `v0.2.3` 于 2026-07-13:匹配 `v0.2.3` tag 的控制面真实性维护者界面发布。LoopX 添加 provider-neutral 模型行为资格确认契约,含公开安全语料与决策凭据,加上可选直接 provider actor(#1994, #1998-#1999, #2001, #2003)。可选能力发现与 Lark 事件收件箱/收集器成为更清晰的产品界面,而不增加强制性首次运行配置(#1978, #1986, #1997, #2000)。Monitor、todo、quota 与愿景路由现在保留能力与归因,优先推进而非陈旧 monitor 压力,保持未来等待安静,并关联实质转换凭据(#1989-#1993, #2008, #2011, #2013-#2015)。Explore 图激活现在尊重运行范围 sink 权威(#1995, #2016),而确定性更新说明与项目治理让公开仓库更易维护(#1983, #1996, #2012)。无需持久 state 迁移;可选 provider、Lark、语义偏好与 Explore 界面仍是选择加入。
- `v0.2.4` 于 2026-07-14:匹配 `v0.2.4` tag 的 Explore 呈现与交付可靠性发布。Explore 看板布局现在是头等 `board_style` 产品参数,有两个受支持值:`auto_flow` 使用 Mermaid 自动图布局用于拓扑导向视图,而 `semantic_lane_columns` 为具有有意义并行车道的运维者看板输出确定性阶段 SVG(#2062)。Lark 视觉 sink 可以按 evidence 阶段发布一个托管看板,把所选样式投影进每个阶段,保持标签位于车道节点内,重试最终视觉读回,并调和生成的文档分节,使陈旧或重复阶段不累积(#2051, #2063, #2065-#2066, #2068)。同一规范 Explore 结果图对两种样式都是权威,现有仅 Mermaid 的配置继续解析为 `auto_flow`。此版本还包括同源规范/执行视图、显式 issue-fix 语义偏好调用点、provider 诊断,以及进一步 monitor、调度器、安装器、接入与公开 smoke 加固(#2002, #2005-#2006, #2018-#2021, #2027-#2028, #2032, #2036, #2052-#2061)。无需持久 state 迁移;Explore 与其 Lark 视觉 sink 保持选择加入。
- `v0.2.5` 于 2026-07-15:匹配 `v0.2.5` tag 的奖励记忆与跨运行时可靠性发布。LoopX 现在交付 provider-neutral Reward Memory 路径,从已评审语料与健康契约到候选评审、选择加入的召回/应用、评估、dogfood 控制,以及在 Issue-Fix 规划边界的显式 actor 对等路由(#2076-#2085, #2096, #2100, #2103, #2128)。运行时投影路由成为共享运行时上实质事件、刷新与 Explore 命令的头等真相源,并修复源镜像歧义与紧凑诊断(#2091, #2094, #2097, #2099, #2102, #2129)。Issue-Fix 获得更强 commit evidence、evidence 支撑的关闭计数、候选去重、评审者回退与交付窗口排队(#2071, #2087, #2098, #2105, #2107, #2111)。Monitor、调度器、对等重规划、Lark 收件箱、Explore 读回与长程 SkillsBench 路径在重复 host 失败、有范围 gate、传输丢失、设置漂移与计数歧义上加固(#2101, #2104, #2108-#2127, #2130-#2131)。无需持久 state 迁移;Reward Memory 与高级 fixer 执行保持显式激活且有界。
- `v0.2.6` 于 2026-07-16:匹配 `v0.2.6` tag 的类型化交互权威与隔离 Turn 运行时发布。调度器决策现在遵循类型化交互契约,精确的受阻后继可以触发有界自主重规划,用户 gate 不再死锁无关 agent 车道([#2136](https://github.com/huangruiteng/loopx/pull/2136), [#2177](https://github.com/huangruiteng/loopx/pull/2177), [#2187](https://github.com/huangruiteng/loopx/pull/2187), [#2188](https://github.com/huangruiteng/loopx/pull/2188), [#2198](https://github.com/huangruiteng/loopx/pull/2198), [#2203](https://github.com/huangruiteng/loopx/pull/2203), [#2204](https://github.com/huangruiteng/loopx/pull/2204))。LoopX Turn 成为交付的隔离 headless 路由,含可执行 envelopes、会话恢复、独立校验、真实 CLI 资格确认与 SkillsBench 集成([#2158](https://github.com/huangruiteng/loopx/pull/2158), [#2166](https://github.com/huangruiteng/loopx/pull/2166), [#2169](https://github.com/huangruiteng/loopx/pull/2169), [#2171](https://github.com/huangruiteng/loopx/pull/2171), [#2173](https://github.com/huangruiteng/loopx/pull/2173), [#2193](https://github.com/huangruiteng/loopx/pull/2193), [#2199](https://github.com/huangruiteng/loopx/pull/2199), [#2202](https://github.com/huangruiteng/loopx/pull/2202))。新用户接入由确定性生命周期 canary 与对实际默认包的重复单臂 Doubao 资格确认保护,而 CLI 输出预算与发布结果契约在提升前让语义回归可见([#2144](https://github.com/huangruiteng/loopx/pull/2144), [#2148](https://github.com/huangruiteng/loopx/pull/2148), [#2153](https://github.com/huangruiteng/loopx/pull/2153), [#2157](https://github.com/huangruiteng/loopx/pull/2157), [#2159](https://github.com/huangruiteng/loopx/pull/2159), [#2167](https://github.com/huangruiteng/loopx/pull/2167), [#2168](https://github.com/huangruiteng/loopx/pull/2168), [#2201](https://github.com/huangruiteng/loopx/pull/2201))。Explore 源调和、可选 Reward Memory 实验与评审者 gate、Lark 交付也得到加固而不使其成为首次运行要求([#2200](https://github.com/huangruiteng/loopx/pull/2200))。无需持久 state 迁移;高级能力保持显式激活。
- `v0.2.7` 于 2026-07-17:匹配 `v0.2.7` tag 的控制面收敛与精确发布 evidence 发布。调度器、quota 与 todo 决策共享一个 agent/runtime/capability/ACK 范围;monitor 独立收敛而不互相重置;阻碍型用户 gate 使用一个类型化响应计划;Reward Memory v1 交付项目语料配置与有界 Issue-Fix 召回。
- `v0.2.8` 于 2026-07-19:匹配 `v0.2.8` tag 的类型化 Codex App 自动化契约与周期报告控制面发布。Agent 范围调度器、quota、todo、monitor、用户 gate 与前沿决策成为类型化运行时契约,同时交付 provider-neutral 周期报告控制面用于计划或实质性进展报告,而不授予外部写入权威。
- `v0.2.9` 于 2026-07-20:匹配 `v0.2.9` tag 的车道隔离调度与 OpenCode host 支持发布。一个 agent 车道不能再消费或抑制另一车道的前沿,OpenCode 成为头等 Turn 支撑 host,周期报告获得密集的自包含 HTML 呈现。
- `v0.2.10` 于 2026-07-20:匹配 `v0.2.10` tag 的会话内周报快速开始。普通项目会话可以请求本地报告,无需 profile、RRULE、host Automation、provider 或外部 sink;owner 暂停对仅 monitor 的配额工作保持权威。
- `v0.2.11` 于 2026-07-20:匹配 `v0.2.11` tag 的打包周报 preset。`loopx periodic-report inspect-profile --preset weekly` 暴露内置 provider-neutral preset;它不创建调度、不调用外部 sink、不授予外部写入权威。
- `v0.2.12` 于 2026-07-23:匹配 `v0.2.12` tag 的心跳凭据与评审质量发布。每个心跳 Turn 持久一个配额凭据,monitor/重规划路由保持新鲜,`loopx pr-review` 获得代码量与简化透镜,自适应多 Turn 活跃 worker 生命周期阶段通过紧凑 run 与台账视图保持可见。
- `v0.2.13` 于 2026-07-24:匹配 `v0.2.13` tag 的 monitor 跟进发布。实质性 monitor 写回在目标键回退前解析精确 todo,立即暴露新可运行后继,并在仅投影重载失败时返回结构化的陈旧投影警告而非报告写入失败。连续 monitor todo 不再携带 `resume_when`。
- `v0.3.0` 于 2026-07-30:匹配 `v0.3.0` tag 的能力与控制契约发布。LoopX 提升 simplify-first 变更资格确认、provider-neutral 决策上下文、受治理的实质生命周期工作流、受管项目交付与 Ark Managed Agent host 支持,同时对配额规则排序并使可恢复 Turn 阶段显式。
- `v0.4.0` 于 2026-08-01:匹配 `v0.4.0` tag 的接入与 Turn 权威发布。Goal 启动投影能力拥有的准入路由,重规划确认需要规范的 agent 可见 evidence,默认 `quota should-run` JSON 保持在有界面向模型预算内,README 前台展示两个可查证的 200+ 小时 Loop 轨迹。
- `v0.4.1` 于 2026-08-04:匹配 `v0.4.1` tag 的持久工作选择与 Goal-host 延续发布。能力准入的 Todo 路由跨 Turn 持久,Goal host 在最早的实质前沿转换唤醒,分组 Issue Fix PR monitor 显式物化,默认关闭的 Agent Turn Recall 交付 agent/goal/project/Todo/authority 作用域。
- `v0.4.2` 于 2026-08-06:匹配 `v0.4.2` tag 的 host 与工作流界面发布。Pi 与 TraeX 成为头等 host 路径,自适应子准入强制领域/能力/仓库/写入范围就绪,交付 provider-neutral PR 队列观察与 PR program 工作流,Issue Fix 把工作固定到已批准的基快照。
- `v0.4.3` 于 2026-08-08:匹配 `v0.4.3` tag 的效果解释器演进发布。第二个真实 `EffectTurn` 解释器消费 Turn 结果,数据编码执行与有序效果程序形态落地,运行时计划是替换优先,统一双语 Dev Book 添加独立 Control-Plane Course 章节。
- `v0.4.4` 于 2026-08-09:匹配 `v0.4.4` tag 的 M6 效果程序质量 gate 完成。热控制面模块有界,`EffectTurn`/`EffectProgram` 被真实运行时路径消费,M6 RFC 以审计 evidence 标记为 Complete。
- `v0.4.5` 于 2026-08-12:匹配 `v0.4.5` tag 的安全加固与控制面发布。LoopX 修复五个私下报告的安全公告,添加调用方批准的完成校验,交付持久 smoke 评审 gate,并继续以 16 位贡献者的社区贡献推进重规划/evidence/结算加固。
- `v0.4.6` 于 2026-08-13:匹配 `v0.4.6` tag 的重规划与通知加固发布。重规划收尾变为语义化,配额/心跳通知正确性被修复,refresh-state 写回护栏落地,两个架构 RFC 记录效果程序方向。
- `v0.4.7` 于 2026-08-15:匹配 `v0.4.7` tag 的受治理 host 延续发布。OpenCode 1/2 goal Loop 不再因用户消息或任务收尾而中断,DeepSeek Harness 通过受管 Turn connector 连接,逐 goal 交接模式在 state 文件中 gate claim/租约权威,Explore 可以在一个自动化步骤中发布多个 Feishu 视觉看板。
- `v0.4.8` 于 2026-08-16:匹配 `v0.4.8` tag 的开源核心打包与资格确认发布。LoopX 为开源核心采用 Apache-2.0,作为头等 PyPI 发行交付,添加逐 Todo 校验预算,并收紧基准完整性资格确认与 Content Ops 呈现密度。
- `v0.4.9` 于 2026-08-19:匹配 `v0.4.9` tag 的跨平台 host 与长 Loop 可靠性发布。LoopX 让 PyPI 成为默认完整安装路径,添加原生 Windows PowerShell 与 KunlunCode Goal Pro 支持,交付带持久待处理变更台账的选择加入仓库变更窗口 provider,并加固心跳结算、Todo 校验、PR 评审调度、原生 Goal 基准隔离与公开仓库信号 provider。
- `v0.5.0` 于 2026-08-20:匹配 `v0.5.0` tag 的个人控制面工作区发布。LoopX 把 dashboard 提升为受支持的浏览器/PWA 工作区,在同一本地权威之上添加源构建原生桌面外壳,让 Goal 停止/恢复与仓库变更窗口对运维者可见,并准入 goal 边界外部能力 provider。
- `v0.5.1` 于 2026-08-21:匹配 `v0.5.1` tag 的运维者工作流与协作加固。LoopX 添加可下载的 macOS 与 Windows 桌面预览、头等 DeepSeek Harness 打包、botmux Goal Channel Turn、三种 agent 范围 Lark ingress 模式,并修复 Goal 生命周期、Todo 延迟、配额结算、重规划收尾与事件溯源新鲜度路径。
- `v0.5.2` 于 2026-08-23:匹配 `v0.5.2` tag 的事务与多源工作区可靠性发布。LoopX 把核心 Turn 结算路径移到类型化效果事务之后,让本地/SSH 源变更代数栅栏化,添加原生 DeepSeek Harness Goal 工作区与 agent 范围外部 Connector provider,并加固长 Todo 链、预备效果恢复、基准准入与公开 smoke 发布 gate。
- `v0.5.3` 于 2026-08-27:匹配 `v0.5.3` tag 的 host 触达与自主延续可靠性发布。LoopX 添加 ZCode 与 Antigravity CLI Goal 界面、有界引文驱动的深研工作流与显式 Pi 任务租约门面;它还加强 Lark 收件箱路由与追赶、类型化 Todo/quota/scheduler 结算、仓库交付准入与运行时启动恢复。
- `v0.5.4` 于 2026-09-03:匹配 `v0.5.4` tag 的类型化控制面与受治理工作流发布。LoopX 把更多 Todo、task-lease、quota、scheduler、Vision 与重规划事务移到 TypeScript owner 之后;推进分阶段文件、PostgreSQL 与 NoKV 共享权威 provider;完成周期报告生命周期;让 DSH plugin 一步就绪;并添加公开安全基准研究投影而不授予上传权威。

当提升新的公开发布时,仅在匹配的 tag、发布说明、stable 引用、更新路径与聚焦发布
canary 一致后在此添加。

## 兼容 gate

在提升发布快照或公开指南告诉用户依赖新界面之前,运行覆盖所触界面的最小 gate:

```bash
python3 -m py_compile loopx/*.py
python3 examples/release/codex-cli-no-clone-release-verification-smoke.py
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
python3 examples/canary/canary-promotion-readiness-smoke.py --no-write-evidence
```

默认 dashboard 策略是 `--dashboard-mode=auto`:源 checkout 在
`apps/presentation/dashboard` 存在时运行 dashboard 演示就绪度,而省略该 dashboard
应用的已安装发布快照跳过该可选界面,并在 canary 输出中保持该省略可见。当
dashboard/frontstage 本身被提升时使用 `--dashboard-mode=require`;仅当发布边界刻意
排除 dashboard 应用时使用 `--dashboard-mode=skip`。

仅当你刻意想追加新鲜提升就绪度 evidence 时使用写回形式:

```bash
python3 examples/canary/canary-promotion-readiness-smoke.py
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

必需的 [Python 测试工作流](../../.github/workflows/python-tests.yml)
拥有 Ruff 命名空间选择与包覆盖下限。下限是回归护栏,不是充分覆盖的声明;当持久
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
如果发布快照省略 dashboard 应用,canary 应优雅降级并记录该边界,而不是让无关的
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
它的第一个实质性部分是紧凑的 `## Release Decision` 块,回答读者在查看详细变更日志
前需要的五个问题:

| 字段 | 必需决策 |
| --- | --- |
| `**Who should upgrade:**` | 命名受影响的用户或操作者、现在升级的理由,以及谁可以留在当前版本。 |
| `**What this release solves:**` | 用用户结果语言说明具体故障、缺失工作流或可靠性缺口。 |
| `**Breaking changes:**` | 以 `No.` 或 `Yes.` 开头;为是时给出迁移路径,为否时仍披露变更的默认值、废弃或实验边界。 |
| `**How to verify:**` | 说明升级后期望结果,并包含一个证明包身份与受影响行为的最小可运行 `bash` 块。 |
| `**Contributors:**` | 命名发布维护者与 tag 范围的社区贡献者,或明确说明本发布无社区贡献。 |

在中文摘要中以 `**谁需要升级：**`、`**解决了什么：**`、`**是否有破坏性变更：**`、
`**如何验证：**` 与 `**贡献者：**` 镜像同样决策。摘要是决策辅助,不是对下方
详细产品分组、逐声明 PR evidence、可选能力生命周期或精确提交校验 evidence 的替代。

优先保留用户可见的产品变更。当上一与当前 tag 之间的合并 PR 包含项目创始人
`@huangruiteng` 以外的社区贡献者时,在英文产品分组之后、兼容性、校验或更新材料之前
添加显眼的 `## Community Contributors` 部分。链接每个符合条件的 GitHub handle 与
相关 pull requests,总结具体贡献,适用时点名外部或首次贡献者。

不要在本节列出或致谢 `@huangruiteng`;创始人主导权蕴含在每个 LoopX 发布中。
当 tag 范围没有符合条件的社区贡献时省略本节。贡献者认可必须补充发布叙述,而不是
替代或先于其产品亮点。

从 tag 到 tag 的 Git 范围与合并 PR 元数据构建列表,而不是提交显示名或未经评审的
生成变更日志。即使同一 pull request 在产品分组下再次链接,归因也是发布契约的一部分。

把其余发布说明组织为下列稳定分组。省略空产品分组,而不是发明填充:

1. **状态内核与控制面**:state、todo、配额、调度器、gate、对等方路由与运行时权威变更。
2. **能力与工作流**:已交付的用户工作流,如 Issue-Fix、Explore、Reward Memory、接入与 LoopX Turn。
3. **质量与测试**:确定性测试、canary、输出预算、模型行为资格确认与发布 gate。
4. **基准与集成**:基准适配器、Lark、host 运行时与其他外部边界。
5. **文档与兼容性**:公开契约、安装/更新指引、迁移、默认值与刻意排除。

有合格社区贡献的双语发布必须在中文产品分组之后、中文兼容性或校验材料之前添加
`### 社区贡献者`,与英文版本保持相同人员、pull request 链接与具体贡献范围。
没有合格贡献者时,两种语言的分节一并省略。双语发布必须在两种语言中保留这些相同
分组边界。使用匹配的标题**状态内核与控制面**、**能力与工作流**、**质量与测试**、
**基准与集成**与**文档与兼容性**。中文文案可以更短,但不得把几个分组塌缩成一个
泛化亮点列表、省略非空英文分组或弱化贡献者归因。

在每个非空分组内,每条实质性声明必须带一个或多个直接 GitHub pull request 链接,
如 `[#2051](https://github.com/huangruiteng/loopx/pull/2051)`。末尾的 compare 链接
仍有用,但它不替代逐声明 PR 归因。避免仅以裸 PR 范围作为 evidence,因为范围可能
隐藏被省略或无关的变更。

在决策摘要与产品分组之后,每条公开发布说明还应记录:

- 此稳定发布使用什么包版本与公开 tag 名称?
- 新用户应跟随哪条安装/更新路径?
- 哪些界面仍是实验性或刻意排除?
- 对于每个新增或实质性变更的实验性、默认关闭或选择加入能力,包含两种语言的**可选能力激活**条目:命名其范围、只读预览、确切的启用与停用命令、前置条件或安全 gate,与规范文档。若不存在持久开关,说明选择加入是按命令或 preset。
- 公开/私有扫描是否在变更的文档、示例与工作流文件上运行?
- 完整 `pytest`、聚焦发布/安装契约、基于风险的 canary 与提升就绪度/公开边界检查是否在精确发布提交上通过?
- `loopx canary release-qualification` 是否确认每个必需的紧凑凭据匹配同一干净提交、Git tree、包版本与 tag?
- 低频实时模型 gate 是否对实际默认面向 agent 包运行并至少重复两次?记录模型 id、检查的行为决策、调用次数、失败与跳过,但绝不保留原始提示、包、响应、凭据或本地路径。这仍是本地/手动发布 gate,而非常规 CI。
- 若发布声称基准或长程结果改进,匹配的稳定版对候选版结果基线是否通过?若没有结果声明,说明这一昂贵 gate 并不需要,而不是暗示它运行过。
- 对于中文运维者,包含一个紧凑的 `## 中文摘要` 部分,用中性产品语言镜像英文分组结构与实质声明。保持每个分组短于其英文对应物,同时保留直接 PR 归因与兼容边界。

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
`## Optional Capability Activation & Use` 下的专门英文 `### <surface>` 条目,以及
`### 可选能力启用与使用` 下的匹配中文 `#### <surface>` 条目。两个条目都必须包含
这些显式字段:

| 英文 | 中文 | 必需内容 |
| --- | --- | --- |
| `**Activation:**` | `**启用：**` | 确切安装/启用命令,或无持久开关时确切的按命令/配置选择加入。 |
| `**Validation:**` | `**验证：**` | 最小可运行状态、读回或验证命令。 |
| `**Disable / rollback:**` | `**停用 / 回退：**` | 确切停用、卸载、envelope 移除或回退路径。 |
| `**Authority boundary:**` | `**权限边界：**` | 激活不授予的写入、合并、provider、隐私与 host 限制。 |
| `**Docs:**` | `**文档：**` | 规范的带版本文档链接。 |

每个条目需要至少一个可运行 `bash` 块。没有新增或实质性变更可选能力、工作流或 host
界面的发布,必须改用 `--expect-no-optional-capability-changes` 运行 gate,并包含
验证器要求的精确双语声明。同时省略界面列表与显式无变更决策会失败关闭。

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

中文摘要必须保留相同的用户结果、交付的层与最后一英里边界。翻译可以更短,但不得
把面向用户的结果替换为仅架构术语。

发布 PR 与最终 GitHub 发布正文必须使用相同分组与贡献者归因,加上相同校验凭据。
在 rebase 或合并任何额外运行时变更后重跑 gate;更早提交的结果不能认定后一 tag。
公开 git 历史、合并 PR 元数据与交付的 CLI 行为仍是真相源。

## 相关文档

- [Codex CLI 打包安装路径](runtimes/codex-cli/codex-cli-packaged-install.md)
- [Codex CLI 无 clone 发布验证](runtimes/codex-cli/codex-cli-no-clone-release-verification.md)
- [快速开始](../guides/getting-started.md)
- [更新说明](../update-notes/README.md)
- [公开/私有边界](../public-private-boundary.md)
- [交互模式目录](../concepts/interaction-pattern-catalog.md)
