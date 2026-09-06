# 贡献者任务看板


这个看板是 LoopX 工作面向贡献者的公开投影。它刻意区别于 `.local` active goal
state：

- 本文件列出可以在仓库中讨论、认领、审阅和验证的公开工作；
- `.local`、`.loopx` 和 live `ACTIVE_GOAL_STATE.md` 文件仍是对 maintainer 与自动化
  而言的本地 runtime 数据；
- 私有 benchmark trace、verifier 输出、原始 agent session、凭据、内部文档链接和
  本地机器路径不得复制到这里。

目标是让重要工作可被发现，同时不把仓库变成 maintainer 草稿状态的镜像。

## 状态图例

| Status | 含义 |
| --- | --- |
| Available | 已就绪：任何人均可在关联 issue 上评论或开一个小的 PR。 |
| Claimed | 已有人表示在做，或 maintainer 已指派。 |
| Maintainer-owned | 活跃工作正发生在 maintainer/本地自动化中；触碰前先询问。 |
| Needs design | 欢迎讨论，但实现需要先达成一致。 |
| Blocked | 正在等待决策、依赖或 maintainer writeback。 |
| Done | 已完成，准备从本看板归档。 |

## 如何认领工作

1. 优先使用关联的 GitHub issue。如果还没有 issue，用贡献者任务模板开一个。
2. 评论表示你想做这个任务。Maintainer 会把它标记为 `claimed`，或建议更小的切块。
3. 纯文档 typo 修复或显然很小的清理，直接开 PR 即可。
4. 已认领任务 14 天没有更新，maintainer 发出一次 ping 后可以把它释放回 `Available`。
5. 如果任务是 `Maintainer-owned`，不要重复劳动。询问是否存在公开 helper 切块。

## 当前技术方向

canonical 的[技术方向地图](../project/technical-directions.md)说明结果、成熟度、
属主边界与晋级门禁。本看板列出了有界工作，不重新定义那些方向。

| 方向 | 当前阶段 | 贡献者入口 | 边界 |
| --- | --- | --- | --- |
| 长程 Benchmark 与证据 | Active research | [#3243](https://github.com/huangruiteng/loopx/issues/3243) | 工作在公开安全 fixture、treatment integrity、reducer 与文档上；live case 与评分保持 maintainer 专属。 |
| Operator Surface 与 IM 集成 | 在 `frontend-control-plane-im-prototype-rfc` 上孵化 | [#3244](https://github.com/huangruiteng/loopx/issues/3244) | 说明目标基础分支；UI 仍是投影，晋级 `main` 是分批进行的。 |
| 共享 Goal 权威与跨 Host 协调 | Stage 2 切块已交付（aggregate head、file provider、`claim_work` executor）；NoKV 仍是未晋级候选 | [#3245](https://github.com/huangruiteng/loopx/issues/3245) | 切块保持 provider-neutral 与 file-backed；不产生第二个 scheduler 或写权威。 |
| 架构与研究孵化器 | 按 RFC 混合推进 | [#3246](https://github.com/huangruiteng/loopx/issues/3246) | 阅读每个探索方向的阶段；仅一份 RFC 不代表实现可认领。 |

核心控制面可靠性仍是共享的已交付底座。Effect Program hardening、已验证 transition、
恢复、可观测性、可维护性与贡献者体验，通过下方聚焦行与现有 `control-plane` 标签持续
推进。

## 优先级队列

| 优先级 | 方向 | 切块 | Issue / PR | 状态 |
| --- | --- | --- | --- | --- |
| P0 | Core hardening | remote execution 的 exact-head 审阅与 terminal writeback fencing：fenced journal recovery 吸收进 TypeScript | #3074 | Done |
| P0 | Core hardening | 把调用方批准的 `validation_command` 接入其余 self-report 入口 | #3082 / #3142 #3291 #3343 | Done |
| P1 | Benchmark evidence | 拆出一个确定性的 adapter-fidelity 或 treatment-integrity fixture | #3243 | Needs design |
| P1 | Operator surface / IM | 从孵化分支拆出一个投影或 session-contract 表征单元 | #3244 | Needs design |
| P1 | Shared coordination | 用 provider-neutral parity fixture 表征已交付的 file-backed `claim_work` executor | #3700 / #3245 | Needs design |
| P1 | Core hardening | 一个 budget-aware 的 CLI 输出人性化切块 | #2881 | Needs design |
| P2 | Project docs | 覆盖到 v0.5.4 的 release 文档安装、激活与恢复指引 | GH-C04 | Available |
| P2 | Maintainability | CLI 属主与 hot-module 抽取 | GH-C06 | Available |

## 产品管理切口

LoopX 正在从控制面库收敛为长程 agent 工作的管理层表面。产品能力贡献应优先选择那些
让既有 kernel 对象对用户可理解的切块，而不是再增加一个真相源。

| 产品切片 | 当前底座 | 贡献者规模的下一个切口 |
| --- | --- | --- |
| 管理前厅 | Goals、todos、gates、claims、evidence、quota、run history、`goal_channel_projection_v0`、`task_graph_projection_v0`、`issue_fix_outcome_projection_v0`、`agent_management_projection_v0` 以及同源 Explore 视图都已经是紧凑读模型。公开首页、托管文档与本地化 dashboard 现在暴露这些表面。 | 把读模型翻译成稳定的操作者概念，如 work item、owner、decision、evidence、budget、risk 与 next action；保留 lineage，在 drill-down 中保留原始机器字段，不要创建第二套 task 或 case 存储。公开首视口的变更仍属 maintainer preview 工作。 |
| 对话命令 | 四个 canonical 全局 manager CLI 命令已交付：`/loopx-global-summary`、`/loopx-global-gates`、`/loopx-global-todos` 与 `/loopx-global-risks`；旧的 `/loop-global-*` 形式只是迁移别名。 | 保持它们专注的只读合同与公开安全 smoke 对齐。`/loop-goal-summary` 仍是 host-only，不属于这个贡献者切片；不要发明另一个 manager 命令或别名体系。 |
| Runtime 连接器模式 | `host_mode_plan_v0` 在连接器目录上选择 visible、isolated-headless、gateway、service 与 hybrid 模式。Host-loop 激活现在覆盖 Codex surfaces、Claude Code、OpenCode 1/2 goal loop、TraeX、Pi、Gemini、Cursor、DeepSeek Harness 与 custom agent；一个 scheduler-hint-aware 的外部 worker 演示了一条带签名的 headless 路由。LoopX Turn 仍是单次 request/effect/receipt 事务，而不是循环。 | 为路由保持、skill 交付/readback、continuation 截止、带签名主操作或阶段/receipt 可见性增加一个 provider-neutral parity 切块。把 host wake/进程属主留在 LoopX 核心之外，不要创建第二个 scheduler 或重复控制器。 |
| Planner-worker 模式 | 实验性 planner-worker 合同现在支持一个有界计划、一个选中的 worker 步骤、一个 allowlist 校验集、clean-worktree 边界与 typed receipt；TraeX probe 只是一个扩展 provider。 | 围绕已交付的 fake runtime 增加 provider-neutral 的使用与失败指引。保持模型路由显式、验证由调用方批准，循环调度与广泛的多 agent 编排留在该模式之外。 |
| 可见治理 | Quota、scheduler hint、权威交互合同、decision scope、user gate、peer claim、可选 task lease、带 pending ledger 的仓库 change-window gate (#3319)、interface budget 与 provider-neutral PR program snapshot 都已存在于机器合同中。共享 goal 权威/state-provider RFC 现在定义下一个协调边界，而不让提案成为 runtime 权威。 | 展示谁可行动、谁必须批准、适用哪种 decision scope、花了多少 budget，以及 pause/override/terminate 决策如何映射回 LoopX state；增加一个 provider-neutral 反例，证明锁定的仓库窗口拒绝写入，且在 merge 或 close 后 pending ledger 行以 typed lifecycle 结清。保持提案状态、claim、lease 与 PR program 观察不成为新的 runtime 层级或写权威。 |
| 决策与素材质量 | Decision Context 与 Material Lifecycle 是实验性、内置、默认关闭的能力。它们分离 revision-bound 证据、advisory 提案、素材计划、owner 批准的 apply 与私有 cursor/source 状态。 | 构建无 provider 的合成 walkthrough，让这些边界可见。不要添加私有 adapter、素材正文、provider payload 或第二套 lifecycle 存储。 |
| 记忆与内容工作流 | Agent Turn Recall 把 quota 选中的工作与 scoped Reward Memory 组合，其 post-outcome utility 归因是 advisory 且只读 (#3280)；`content_ops_item_v0` 保留稳定 item 身份、revision-bound 批准、交付/readback receipt 与 supersession。两者都保持 advisory 或 preview 级别，不增加 provider 权威。 | 增加合成 walkthrough 与反例，证明身份、revision 与失败边界。把 provider payload、草稿正文、凭据、原始 session 与外部写入留在 LoopX state 之外。 |
| 扩展与变更验证 | 独立 `extension init` 脚手架与受管理的零权限执行演示可选 provider 交付；`loopx-repo-health` provider 发布公开仓库健康快照 (#3272)。Exact-diff Change Quality 是独立的 goal-scoped、simplify-first，启用时通过新 receipt 强制执行。 | 一次只改进一个已有 provider 或验证缝。不要发明“可安装性”、自动运行已发现仓库任务的能力，或削弱 exact-scope receipt 检查。 |

## 最近的 Maintainer 进展

这些公开里程碑改变了哪些任务仍然是有用的贡献者入口：

| 领域 | 已落地 | 对贡献者的含义 |
| --- | --- | --- |
| Turn 与 settlement | Typed settlement 现在覆盖 CLI、Codex App、task lease 与 todo completion：调用方批准的 `validation_command` 提交已验证 completion receipt (#3142)，user-role done 更新运行同一声明 gate (#3291, #3293)，MCP `complete_task` 继承该 gate 并带固定反例 (#3343)，关闭 GH-C85 / #3082。共用的 typed settlement receipt-chain driver 统一 replay (#3199)，M7 parity fixture 外加只读 journal 检查/`interpret_turn_journal` lens 已交付 (#3189, #3193, #3205)，per-todo validation timeout 覆盖 20s 默认值 (#3210)，replan typed semantic exit 结清 exhausted-goal 与 future-monitor 重入 (#3213)。Failed-session 恢复现在恢复保留 session 而不削弱 drift 检查 (#3262, #3266)，同 turn 的 terminal closeout 也可恢复 (#3261)，关闭 #3228；模糊 quota-spend 重试与 terminal no-followup 顺序也已结清 (#3258, #3250)。Receipt-bound monitor settlement 现在确定性关闭，受治理的 continuous-monitor 提案在 Kernel 中结清 (#3513, #3511)；重放一个已完成 heartbeat turn，在其 completion、writeback 与 spend receipt 存在时返回 `heartbeat_settled_skip`，不重复 spend 也无 successor 冲突 (#3578，关闭 #3567)。v0.5.3 之后，settlement readback 合并进 typed TypeScript 边界，逐 effect reduction case 固定，successor Turn 结果会验证，非完成 terminal closeout 被拒绝，turn 可在 capability 重入后存活，fenced journal recovery 与 terminal-writeback fencing 吸收进 TypeScript (#3074)，Turn 恢复决策统一到 Journal 检查 (#3719)，host Todo settlement 切换到 TypeScript (#3724)，settlement readback facade 退役 (#3714, #3723)，Vision refresh 权威移交 TypeScript (#3720)，只读 autonomous replan settlement 落地 (#3746)，延迟 scheduler ACK 在 autonomous replan 后结清 (#3742)。 | 在共用 driver 上增加 receipt-chain drift 或 replay-identity 反例。不要第二套 settlement ledger、模型调用或双重 quota spend。 |
| Effect program runtime | 共用的 typed Effect Program 驱动 quota、Turn、task-lease 与 todo-completion settlement。Dev Book 课程讲授当前 runtime (#3097)，M7.1 parity fixture 与只读 replay lens 已交付 (#3189, #3193)，turn driver 是 settlement 代数的第二个消费者。TypeScript 控制面迁移进入事务回报阶段 (#3447)：settlement (#3464)、delivery routing (#3481)、scheduler 转换内核 (#3434) 与 todo completion (#3530) 现在切换到 typed TypeScript 事务，receipt-bound 阶段分类移入 typed quota 边界 (#3578)。v0.5.3 之后，host Todo settlement (#3724)、native task-lease acquire (#3702)、Vision refresh 权威 (#3720) 与 settlement readback facade 清理 (#3714, #3723) 也移入 typed 边界，governed-capability-lifecycle 校验 (#3706) 与 scheduler host follow-up (#3704) 处于审阅中。Scheduler 仍在 settlement 之外。 | 在共用 driver 上增加 receipt-chain drift 或 replay-identity 反例；在两个 adapter 共享执行属主之前不要抽取共用 executor，也不要先于两者消费同一 plan/receipt 代数建立 interpreter 协议。 |
| 审阅质量 | PR 审阅现在要求生产表面变更提供 scope-fit 证据 (#3090)，执行合同携带四门 self-dev review lens (#3123)，纯示例 PR 需要 durable smoke-value 证据 (#3134)，age-fair exact-head 调度跨重启保持 (#3317)，要求 durable projection ACK (#3744)，不成比例的变更会被 gate (#3731)。 | 围绕 scope-fit 证据、因果链、exact-head review packet、durable projection ACK 与 durable-smoke-value 声明增加合成一致性与反例。 |
| Task lease | Typed task-lease CLI 带保留 legacy 错误码落地 (#3095)；磁盘上的硬 lease 在 goal-channel projection 中浮现 (#3039)；Turn fencing 使用 lease fence 加 append-only journal，OpenCode 2 goal worker 对自己的 live worker lease 加 fence。Task-lease generation ABA 修复已交付 (#3393)，覆盖已交付 `task_lease_v0` CLI 的 Pi `loopx_task_lease` facade 已合并 (#3559，关闭 #3549)，task-lease settlement 切换到 TypeScript (#3674)，native task-lease acquire 也已切换 (#3702)。 | 在再一个真实 host 集成中采用同一 facade（例如 TraeX），或增加 transfer/重叠写范围 fixture。保持 soft-claim 路由与未声明 lease 权威不变。 |
| 状态、配额、monitor | Replan context 由 evidence ledger 做 host 投影；两个等价的 typed progress 观察构成 obligation，maintenance 写入在 quota 使用的同一全 goal-frontier reducer 上 fail closed，精确 runnable-successor Todo 携带 obligation-bound 语义 receipt 与 turn 边界。Heartbeat todo 在 capability 重入后存活 (#3321)，Todo 身份过滤与 UTC 排序修正 (#3311)，未绑定 `/loopx` session 继承既有 agent 身份 (#3315)，声明的 validation gate 在 user-role done 更新上运行 (#3291, #3293)，quota guard 跟随选中的 Todo (#3506)，有界 fallback action portfolio 让 quota 决策可行动 (#3514)。Guided start 绑定单次 turn (#3572)，过期生成的 Next Actions 重绑当前 todo (#3524)，未知 workspace 因果可修复 (#3519)，畸形 runtime recovery 与 settlement payload fail closed (#3525)，managed 与 queued turn 创建序列化 (#3542, #3562)，guided selection packet 消费显式化 (#3707)。v0.5.3 之后，`todo list` 获得带输出预算上限的有界稀疏投影 (#3679)，dashboard 投影 completed Todo 的 done-count run 进度 (#3689)，guided-todo onboarding delta 覆盖交付 (#3716)，agent-lane Next Action 选择优先于选中 Todo 而非共享散文 (#3693)，typed blocker 结果结清 (#3734)，Turn receipt 优先级在紧凑输出中获胜 (#3726)，CLI 通用命令属主懒加载 (#3717)。手动证据读取、散文 ACK 与历史 repair-delta 声明仅供诊断。紧凑 scheduler-hint 与 heartbeat-prompt 预算以及 todo-detail 冷路径仍是参考。 | 扩展一个测量的性能、detail-readback、锁超时、畸形状态、typed progress 或 obligation-bound 语义转换案例。保持默认输出有界、冷路径详情可用。 |
| 治理与产品化 | 合成 visible-governance 切片落地 (#3086)，其 Stage-2 proposal-vs-shipped 刷新显式包含相加式 `claim_work` / coordination-head 真相与 lease-as-fence 反例；decision-context 证据 cursor 结清 (#3079)；React 首页重建 (#3098) 落地；确定性项目 registry (#3170) 序列化全局同步；per-goal handoff 模式 gate claim/lease 权威 (#3164)，硬 lease gate 自动获取 completion key (#3198)；仓库 change-window gate 与 pending ledger 交付 (#3319)；goal channel 默认新 channel 上 human-gate auto-notify (#3523)；协调状态规则集中化 (#3410)，Stage 2 切片交付 aggregate head、file provider 与 `claim_work` executor (#3529)；项目仓库交付经 capability hook 落地 (#3570)，gitless 交付工作区结清 (#3574)，CPA/provider-routing 验证记录 (#3576, #3573, #3563)；只读 stride shadow observation M1 (#3207)、合成 stride-boundary shadow fixture (#3290) 与 hierarchical stride RFC (#3204) 打开下一个边界；goal-artifact lifecycle projection (#3136) 提出读模型边界，RFC #3215 的 post-outcome memory utility 归因已实现 (#3280)。v0.5.3 之后，periodic-report post-writeback hook 交付 (#3691)，含 terminal Todo closeout 分发 (#3748)、pending-intent 消费 (#3749)、中文分析编辑要求 (#3750)、被拒草稿 reopen (#3751)、实际工作区间 (#3754)、经批准交付绑定 Goal Channel Bot (#3755) 与规范化卡片 readback (#3757)；dashboard 保留启动错误上下文 (#3745)、保持默认状态源同源 (#3732)、避免未绑定 lark-cli 变量 (#3738)；doctor 按安装类型校验 deep check (#3736)；Frontstage Pages PR 校验隔离 (#3728)；Luna 作为有界 account-ring 扩展交付 (#3737)；结构化出站提及已验证 (#3741)。 | 增加一个合成 lifecycle 或 stride-boundary fixture，用缺失反例扩展 visible-governance walkthrough，或用 file-backed parity fixture 表征已交付的 `claim_work` executor。保持激活显式，把源码正文、草稿正文、审阅文本、provider payload、私有 locator、cursor state 与 apply/publish 权威留在公开 fixture 之外。 |
| 安全边界 | 四项合入加固修复包含 state-file 覆盖写入 (#3140)、拒绝 launcher worker 命令中的 shell 元字符 (#3139)、校验 reward 路由中的 `goal_id` (#3138)、停止未认证 status 读取上的 ACAO:* (#3137)。Loopback CORS、worker-command charset 与 state-file symlink 包含被固定为回归测试 (#3340)。GH-C90 审计了四个已交付反例，并各加了一个持久 mutation：path-prefix sibling 包含、worker-command 输入重定向、绝对 `goal_id` 路径段与 `file://localhost` ACAO 拒绝（`tests/test_state_file_containment.py`、`tests/test_worker_command_validation.py`、`tests/test_feedback_goal_id_validation.py`、`tests/test_status_server_cors.py`），完成 GH-C90 切片 (#3655，关闭 #3636)。 | 把凭据、私有复现细节与 advisory 协调留在公开 fixture 之外；仅当新的已交付边界缺少独立的 fail-closed mutation 时才扩展。 |
| Runtime 连接器与内容工作流 | 带真实 e2e smoke 的 DeepSeek Harness Turn adapter 落地 (#3188)；OpenCode 1 与 OpenCode 2 连续 goal loop 交付 (#3151)；content-ops 获得 layout 模板库与 dense-cover 默认 (#3222, #3223)；provider-neutral PR program snapshot 交付 (#2814)；`computer_use_runtime_v0` 现在是可机器检查的协议合同 (#3279)；`loopx-community-discussion` 公开源 provider (#3299) 与 `loopx-repo-health` provider (#3272) 扩展公开源覆盖；goal-channel botmux runtime 集成落地，terminal 分发保留、不确定分发持久化，桌面聊天经 loopback 服务路由，聊天全路由与上下文收件箱回复落地 (#3555)，managed 与 queued turn 创建序列化 (#3542, #3562)；桌面增加工作区语言设置、本地化写入预览，并保留 heartbeat schedule 与 off-hours 语义 (#3594)；host parity、skill-delivery 与 observable-handle 稀疏 pytest 现在覆盖扩展 host 列表。v0.5.3 之后，bot 文档评论 scope 从已发布 app 读取 (#3722)，turn-start reaction replay 有界化 (#3733)，DSH plugin 一步就绪 (#3725)。 | 为 DeepSeek Harness、OpenCode 1/2、goal-channel botmux、content-ops 交付/readback 或桌面 locale parity 增加一个 provider-neutral parity 切片；把原始转写、provider payload、凭据与 host 本地路径留在 fixture 之外。 |
| Benchmark 边界 | Benchmark 研究围绕 native runner 重置 (#3267)：native Codex Goal 连接真实 runtime (#3271)，worker 与 host 隔离 (#3277)，provider env 绑定已安装 Goal profile (#3276)，treatment 形式化验证 (#3275) 与 live continuation (#3273)，runtime 证据绑定精确容器 (#3303)，post-run case analyst brief 交付 (#3289)，integrity qualification toolkit 落地 (#3241)，source-env 使用与凭据探测区分 (#3298, #3278)，可问责 closeout 要求 Todo validation (#3229)。Provider-neutral 四臂研究合同交付 (#3516)，连同受限 task-source 访问 (#3504)、非 http git clone 归类为网络并允许 loopback integrity probe (#3510)、带命名空间的公开 case id (#3532)、锁定 git-clone integrity 边界 (#3515)、orchestrator runtime provenance，以及 fail-closed runtime closeout drift (#3503)。确定性 fixture 已覆盖 GH-C99，无需 live scoring 或上传：`tests/capabilities/test_benchmark_four_arm_contract.py`、`tests/capabilities/test_benchmark_experiment_board.py`（orchestrator runtime provenance 反例）、`tests/capabilities/test_benchmark_runtime_continuity.py`（fail-closed closeout drift），以及 `tests/capabilities/test_benchmark_toolkit.py` 中的 integrity/network/task-source 案例；被覆盖的 GH-C99 fixture 任务已退役 (#3653)。公开 native Goal 轨迹摘要现在从紧凑 lifecycle 事实导出，不保留原始 artifact (#3327)，完成 GH-C16 切片。v0.5.3 之后，外部 agent 阶段交付 (#3565)，受限访问嫌疑按因果使用裁定 (#3747)，plan-role fidelity gate 移除 (#3753)，退役 fidelity 引用清理 (#3756)。共享 lifecycle、readiness、ledger 与 reducer 合同保持公开缝；通用 Effect Program conformance 与 replay 测试加固 settlement 基础设施，但不改变 benchmark 评分，也不授权 live 运行。Live 评分对比保持按住，直到新的无任务 runner lifecycle receipt 证明就绪。 | 扩展合成 setup/termination 归因，为第二个非 SkillsBench adapter 导出公开轨迹摘要，或仅在第二个 SWE 路由需要共享 launch/observe/ingest 行为时增加 SWE adapter。不要启动评分、重复控制器，也不要暴露原始任务文本、日志、轨迹、verifier tail、凭据、上传或本地路径。 |
| 验证与变更质量 | Python 测试在最新带 runtime 的 `main` 变更上全绿；public smoke parity 与 frontstage Pages 构建已恢复，Codex App fallback receipt 身份隔离 (#3233)；public smoke 可靠性再次恢复 (#3302)，stargazer 历史现在经 REST 获取 (#3320)，repository-hygiene smoke 与 release-timeline ratchet 落地 (#3249)。Auto Research KNN evidence-normalization smoke 现在以语义推导的公开 eval fixture（而非墙钟加速）gate improved/contradicted 状态与 protected-scope 检查，完成 GH-C77。v0.5.3 之后，剩余 public smoke 边界修复 (#3740)，public smoke fixture 修复 (#3739)。 | 在确定性 fixture 上保留反例/mutation 覆盖，区分基础设施中断与产品回归。保持 live model/provider 检查显式且低频。 |
| 发布与安装 | v0.5.4 是最新公开 tag 与包版本（v0.5.0-v0.5.4 在上次看板刷新后落地）。PyPI 保持默认完整安装路径 (#3301) 且安装属主显式 (#3566)；canonical 项目链接发布 (#3253)，派生 capability/manpage 表面同步 (#3254)，exact Miaoda 发布在 periodic-report receipt 中验证 (#3508) 并受治理交付 (#3401)，extension doctor readiness 跨发布恢复 (#3556)，doctor deep check 按安装类型校验 (#3736)，公开 release 时间线覆盖 v0.1.3 到 v0.5.4。 | 保持安装、激活与恢复指引与 PyPI 默认路径以及 tagged stable 与 post-tag `main` 的区分一致，继续贡献者安全的更新恢复而不添加并行 release 检查清单。 |
| 公开文档与接入 | 托管文档、公开首页、Dev Book、本地化 dashboard 文案、公开/私有边界示例、GitHub issue 模板与 PR/issue 标签分类已落地。Slash-command 安装现在通过其已交付 CLI wrapper 暴露全部四个 canonical 全局 manager 命令；全新项目接入及其回归 fixture 落地 (#3093, #3103)，harness-above 定位 (#3202)、生态采用与衍生品清单 (#3224)、GitHub 维护与运维自动化最佳实践 (#3227)、长程/商业化策略文档 (#3217-#3220)、TypeScript 控制面迁移 RFC (#3226)、开放策略审阅流程 (#3295)、不自动关闭的 stale-issue 提醒 (#3297)、欢迎所有贡献形态的指引 (#3294)、合并社区政策 (#3238)、Apache-2.0 open-core 采用 (#3235)、能力实现代码地图 (#3252) 连带共置文档 (#3265)、结果/扩展路径澄清 (#3242)、NoKV 语义权威 RFC (#3263)、长程 benchmark 研究计划 RFC (#3240)、已发布技术方向 (#3248) 与 DCO 签名提醒 (#3316) 均已公开。Auto Research stop/takeover/state-aware-wake walkthrough (GH-C43) 记录已交付控制周期，不引入第二启动器或 README 首屏变更。v0.5.3 之后，planner-worker 操作者指南 (#3630)、托管文档导航与 locale-parity 检查 (#3632) 与 atomic-promotion 失败矩阵 (#3633) 落地；GH-C49 frontstage 易读性打磨 (#3663)、host no-spend parity (#3661)、reward-memory walkthrough (#3659)、治理 Stage-2 刷新 (#3657) 与 KNN closeout (#3654) 已合并。 | 保持贡献者、发布、协议、课程、showcase 与 RFC 表面简洁并链接公开证据；增加导航、locale 与 RFC 兼容检查而不追加状态叙事或别名。 |

## Turn Loop 控制器计划

`loopx turn run-once` 仍然是有原子性的受治理执行器：决定、执行一个有界 host 段、
独立验证、写回、单次 spend，并投影最新 scheduler 合同。Host-loop 激活、外部
scheduler worker 与可见 Pi/TraeX 集成提供具体外环，但它们不把 LoopX 变成常驻
scheduler。Maintainer 专属的纯控制器与 replan 转换仍在加固中，因此贡献者应专注于
独立推导的决策表、跨 host parity、fail-closed fixture，或澄清下方边界的文档。

| 优先级 | 计划切片 | 所需边界与证明 |
| --- | --- | --- |
| P0 | 加固 maintainer 专属的纯 Turn Loop 控制器转换合同：一个 typed settlement receipt 加一次新 quota/scheduler 决策。 | 恰好返回一个 typed disposition，如 `run_now`、`wait`、`user_action_required`、`repair`、`replan` 或 `terminal`；拒绝畸形 receipt、无 typed settlement 的 legacy plan、过期 continuation 与无效 budget，且不调用模型、不 sleep、不改 host scheduler、不写状态、不花 quota。 |
| P0 | 让 `replan_required` 成为真正的 continuation 边界。 | 在另一个 Turn 之前，写入有界 todo 或 vision delta，取得新 TurnEnvelope，并保留因果 agent/todo frontier。绝不因为 host session 可恢复就重跑同一个过期 todo。复用既有 autonomous-replan 与 two-stall 合同。 |
| P1 | 鉴定 host-loop 激活与 skill-delivery parity。 | 把 Codex、Claude Code、OpenCode 1/2、TraeX、Pi、Gemini、Cursor、DeepSeek Harness 与 custom-agent packet 对照一个 provider-neutral fixture。必需 skill 与 readback 必须来自 canonical release/goal 合同，而不是环境 host 状态；install dedupe 与 cwd 隔离保持 canonical manifest 为真相源。 |
| P1 | 从已交付外部 worker 扩展 scheduler-owner 与 monitor parity。 | 通过声明的 runtime owner 应用带签名的 `primary_action`、`scheduler_hint` wake/backoff/terminal-stop、具体用户路由与静默不 spend 的 monitor 决策。`run-once` 仍是唯一交付事务。 |
| P2 | 鉴定 Codex App heartbeat 与自适应子代准入的 parity。 | 在 active work、wait、user gate、repair、replan、子代准入/冲突、monitor 与 terminal 状态上使用确定性 fixture，随后做一次显式 opt-in 的真实 host 鉴定。保留独立验证，排除原始 prompt、转写、凭据与 host 本地路径。 |

当 maintainer 专属切片处于活跃时，不要为纯转换合同开第二个实现 PR。Scheduler 进程管理、
host 专属 wake API 与操作者呈现仍是后续 adapter，让每个切片保持可审阅、可回退。

### 入门 / Good First

低配置、文档优先或窄 fixture 工作。这些应适合仍在学习仓库的贡献者作为入口。

| ID | 领域 | 任务 | 验证 |
| --- | --- | --- | --- |
| GH-C02 | tests | 已认领：一个 PR 已经打开 (#3623)，用 archive-completed 覆盖扩展 todo-lifecycle smoke。在 exact head 审阅，或补上审阅发现缺失的 omit/archive 反例。 | `python3 examples/control_plane/todo-lifecycle-cli-smoke.py` 与 `python3 -m py_compile loopx/*.py` |
| GH-C04 | docs | 保持 release 文档更新到 v0.5.4：将安装、激活与恢复指引与 PyPI 默认完整安装路径 (#3301) 和显式安装属主 (#3566) 对齐，保留 tagged stable 与 post-tag `main` 及 release-snapshot 与 canary 的区分，覆盖已安装 runtime 的激活恢复与 extension-doctor readiness (#3556)，并保持公开 release 时间线（v0.1.3-v0.5.4）与 tagged 证据同步，而不是重复 release body 的双语可选能力使用指引。 | `python3 examples/fresh-clone-quickstart-smoke.py`、`python3 examples/loopx-update-smoke.py`、`python3 examples/release/release-readiness-doc-smoke.py`、`python3 examples/release/release-version-contract-smoke.py`，以及 `loopx check --scan-path docs/product/release-readiness.md --scan-path CONTRIBUTING.md` |

### 聚焦实现

小到中等规模、验证面清晰的代码变更。适合能运行本地 CLI smoke 并保持变更范围的
贡献者。

| ID | 领域 | 任务 | 验证 |
| --- | --- | --- | --- |
| GH-C06 | cli | 在近期 quota、status、todo、history 与 scheduler 命令管道抽取之后，表征剩余一个过大的 CLI 属主缝，然后把一个内聚的命令或规则组移入其有界模块。保留公开调用，避免没有真实调用方的兼容 wrapper，保持模块大小/import 预算诚实。一个聚焦 issue 追踪 Goal Channel runtime 切片 (#3710)。 | 命令专属 smoke、`python3 examples/cli-command-module-size-ownership-command-modularization-smoke.py`、`python3 regression/cli-command-module-contract.py`，规则移动时的 focused pytest |
| GH-C88 | cli | 为 #2881 实现一个 budget-aware 的 CLI 输出人性化切片：在其中一个命令族上提供更短的默认摘要与 typed `--json` 逃生舱，保持热路径 payload 预算与差分容限不变。 | `python3 examples/control_plane/cli-output-budget-regression-smoke.py`、聚焦命令 smoke，以及 `loopx check --scan-path docs/status-data-contract.md --scan-path docs/development/contributor-tasks.md` |
| GH-C70 | runtime | 已认领：PR #3664 把 host-loop parity 收窄为外部 scheduler worker 与 Pi 之间一个由生产者生成的有界等待 scheduler-hint 合同：两个真实消费者必须产生同一 provider-neutral stop/wait 计划，包括第三个未变化 poll 触发的最终 quota/replan 复查。 | `python3 -m pytest -q tests/test_host_loop_runtime_parity.py tests/test_external_scheduler_worker.py tests/test_pi_goal_mode.py`、`node --test tests/pi_goal_loop_runtime.test.mjs`、`python3 examples/external-scheduler-worker-smoke.py`，以及 `loopx check --scan-path docs/integrations/runtime-connector-catalog.md --scan-path docs/development/contributor-tasks.md` |
| GH-C100 | state | 用 provider-neutral parity fixture 表征已交付的 file-backed `claim_work` executor (#3700)：同目标竞争恰好一个获胜者，独立目标 rebase，replay 返回原始 receipt，同 operation-id 但命令语义不同则拒绝且无 mutation，过期 provider generation 不重复 transition。Fixture 保持合成与公开安全。 | `python3 -m pytest -q tests/control_plane/test_coordination_executor.py tests/control_plane/test_coordination_file_provider.py`、新 parity fixture，以及 `loopx check --scan-path loopx/control_plane/coordination --scan-path docs/architecture/rfcs/shared-goal-authority-state-provider-v0.md --scan-path docs/development/contributor-tasks.md` |

### 进阶实现

共享状态、adapter 或 benchmark 控制类变更。请先开 issue，并让第一个 PR 保持为窄切片。

| ID | 领域 | 任务 | 验证 |
| --- | --- | --- | --- |
| GH-C07 | state | 全局 registry 同步现在在锁内写入（`tests/test_global_registry_write_serialization.py`）；把同一把锁或乐观修订保护扩展到 per-goal todo/refresh/history 写入方，并加入并发 todo add/update 回归。 | 新并发回归加 `python3 -m py_compile loopx/*.py` |
| GH-C47 | state | Task lease 现在支撑 Turn fencing 与 typed CLI acquire/release，OpenCode 2 goal worker 对自己的 live worker lease 加 fence，lease generation ABA 修复已交付 (#3393)，覆盖已交付 `task_lease_v0` CLI 的 Pi `loopx_task_lease` facade 已合并 (#3559，关闭 #3549)；claim 协调在这里。在再一个真实 host 集成中采用同一 facade（例如 TraeX）：显式宣告 capability，保留 soft-claim 路由，暴露 acquire/renew/transfer/release 结果，证明重叠写范围会失败，而不让 `quota should-run` 强制执行未声明 lease 权威。 | `python3 examples/control_plane/task-lease-runtime-smoke.py`、`python3 -m pytest -q tests/control_plane/test_task_lease.py tests/test_loopx_turn_driver.py`，以及一个 host 聚焦的 fake fixture |

### 设计 / RFC

方向设定类工作。这些任务通常应先产出文档或 issue，再实现。

| ID | 领域 | 任务 | 验证 |
| --- | --- | --- | --- |
| GH-C89 | governance | 回应 AGE 式 attractor 提案 (#2831)：把 goal 方向锚定到仓库属主文档上，使控制面能校验语义漂移而不只是执行状态。定义读边界、漂移信号，以及必须保持 advisory 的内容；不要让仓库文档成为写权威。 | 公开设计说明加合成漂移 fixture 计划，加 `loopx check --scan-path docs/architecture/rfcs --scan-path docs/development/contributor-tasks.md` |
| GH-C96 | design / migration | 审阅 TypeScript 控制面迁移 RFC (#3225, #3226) 的兼容性完整性：验证 typed state rules、领域中立性、行为变更披露与公开/私有边界，然后发布简洁的迁移兼容性说明，不启动迁移。 | `python3 examples/docs-governance-smoke.py` 与 `loopx check --scan-path docs/architecture/rfcs/typescript-control-plane-migration-v0.md --scan-path docs/development/contributor-tasks.md` |
| GH-C35 | integration | 在 LoopX Turn 与 TurnEnvelope 之上设计下一个 provider-neutral 外部 host adapter，以已交付 external worker、Pi 与 TraeX 路由作为一致性示例而非特例。把紧凑 session 事件映射为请求、计划效果、已提交 receipt、独立验证、恢复与 attention item，同时把原始转写、凭据、计费、权限与产品前厅留在 LoopX 之外。 | 公开设计说明加 adapter 中立 fake-host smoke 计划，加 `loopx check --scan-path docs/integrations/runtime-connector-catalog.md --scan-path docs/development/contributor-tasks.md` |
| GH-C37 | interaction model | 用一个新的公开安全 good/bad case 精简 interaction pattern catalog，包含 trigger signal、user channel、agent channel、state contract、bad smell 与 validation reference。不要复制原始聊天、私有 benchmark artifact 或内部链接。 | `loopx check --scan-path docs/concepts/interaction-pattern-catalog.md` |

### Maintainer 专属 / 需要协调

不应重复的可见工作。请索要公开 helper 切片，而不是启动私有运行或广泛产品变更。

| ID | 领域 | 任务 | 验证 |
| --- | --- | --- | --- |
| GH-C72 | workflow runtime | 纯 Turn Loop 控制器及其 fail-closed repair 仍是 maintainer 专属，即使 host-loop 激活、外部 worker、Pi、TraeX 与 typed settlement 已交付。不要重复控制器。公开 helper 可以独立审阅决策表语义，或提出合成畸形 receipt/跨 host fixture；不要启动 host、改变 scheduler 属主，或为让候选通过而削弱验证。 | Maintainer 运行的聚焦控制器 pytest、LoopX Turn 事务测试、autonomous-replan 与有界 monitor no-change smoke，以及基于风险的 premerge canary |
| GH-C67 | issue-fix | `issue_fix_outcome_projection_v0` 的首次操作者渲染是活跃协调泳道。不要构建竞争 case ledger 或操作者表面。请索要一个把 provider、sink 与私有通知状态排除在外的合成 fixture、可访问性或投影 parity helper 切片。 | `python3 examples/issue-fix-outcome-projection-smoke.py`、选定的公开表面 smoke，以及 `loopx check --scan-path loopx/capabilities/issue_fix --scan-path docs/development/contributor-tasks.md` |
| GH-C101 | dashboard | Dashboard Chat turn 完成与单命令启动仍是 maintainer 专属 live 修复 (#3758)：可重试的 Codex app-server Turn 必须渲染回复，一个受支持命令必须同时拉起 status 后端与 UI。不要构建竞争 dashboard 或 chat 路由；请索要合成 app-server 协议 fixture 或回归 smoke。 | Maintainer 运行的打包 dashboard smoke、真实 app-server protocol v2 流程，以及 `loopx check --scan-path apps/presentation/dashboard --scan-path docs/development/contributor-tasks.md` |
| GH-C18 | benchmark | 长程 benchmark 证据计划，包括 live 本地不上传 case、runner 合同、trace 保留、score 记账与 good/bad case 归因。不要重复 live 运行或检查私有 artifact，除非 maintainer 拆出公开 helper issue。 | Maintainer 运行的 benchmark ledger 与公开/私有扫描 |
| GH-C19 | benchmark | Main-table SkillsBench 产品模式对比：原始 Codex autonomous max5 对比合格 LoopX Turn 路由，两臂都不给 verifier 反馈，reward 1 或声明 done 时停止。评分保持按住，直到新的无任务 runner lifecycle receipt 证明就绪；native-runner 研究重置 (#3267) 与已交付公开轨迹摘要缝 (#3327) 定义当前公开 helper 边界。Live 匹配对与官方/可计数 receipt 审阅保持 maintainer 专属；外部贡献者只帮助合成 schema、文档、reducer 与 smoke。 | Maintainer 运行的 readiness receipt、紧凑 ledger、case 分析更新与公开 receipt/边界扫描 |

## 投影来源

本看板由以下公开安全投影维护：

- 本地 `loopx-meta` Agent Todo 列表；
- `docs/` 下的公开文档，尤其是 state interaction model、status data contract、
  quota allocation、integration guide、product vision、仓库 change-window gate 合同
  (#3319)、TypeScript 事务回报阶段 (#3447)、benchmark 研究文档（含四臂研究合同 #3516
  与公开轨迹摘要 #3327）、goal artifact lifecycle projection RFC (#3136)、hierarchical
  stride、post-outcome memory utility、human-attention 与 TypeScript 迁移 RFC、Dev Book
  与控制面课程，以及 PR/issue 标签分类；
- maintainer 对“哪些工作可外部认领、哪些是 maintainer 专属 live 自动化”的近期审阅。

投影规则：

- 复制任务意图，而不是私有证据细节；
- 除非 maintainer 显式发布可运行 issue，否则把私有 benchmark 运行转换为公开 helper
  切片；
- 当重复工作会浪费算力或削弱证据时，把 live benchmark、release 与自动化泳道标记为
  `Maintainer-owned`；
- 优先选择指明可能文件与验证的任务，让贡献者无需阅读本地 active state 即可开始。

## 建议标签

开 issue 或分诊时，使用 `docs/operations/pr-issue-labels.md` 中的公开标签分类：

- Lifecycle 标签：`good first issue`、`help wanted`、`triage`、`workflow-audit`、
  `bug`、`enhancement`、`duplicate`、`question`、`invalid` 与 `wontfix`。
- Area 标签：`control-plane`、`benchmark-boundary`、`capability-extension`、
  `public-docs` 与 `build-or-ci`。

`claimed`、`maintainer-owned`、`needs design` 与 `blocked` 这类看板状态是看板状态，
不是 GitHub 标签。在 issue 评论中并通过 `triage` 或 `workflow-audit` lifecycle 标签跟踪。

## Maintainer 更新规则

- 保持本看板精选。若超过约 35 行开放行，把更旧或更低优先级的工作移到 GitHub issue，
  此处只保留最佳入口。
- 每个公开任务都应包含范围、预期验证与 owner 状态。
- 不要发布私有/本地状态。仅当工作对仓库安全时才把它概括为公开任务。
- 在一个有意义的内部里程碑之后，如果出现新的贡献者规模切片，手动更新本看板。
- 移除或刷新过期任务，而不是把过时的 “good first issue” 条目留在原处。
