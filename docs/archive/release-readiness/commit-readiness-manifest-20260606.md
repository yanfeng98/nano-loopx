# 提交就绪清单 - 2026-06-06

> [English](commit-readiness-manifest-20260606.md)

状态:当前公开脏树就绪地图。在 canary 晋升、提交、推送或 PR 创建之前,使用
本文件审阅并暂存当前的 LoopX checkout。它就当前树而言取代已关闭的 2026-06-03
历史快照。

本清单不是发布私有材料的批准。它是对 `git status --short` 中当前可见的公开
LoopX 变更的分组与验证地图。

## Steering 审计

选定切片:把大型公开脏树整理成发布审阅批次。

考虑过的候选:

- 脏树的 P0/P1 提交就绪清单:选定,因为现在的树横跨晋升 gate、dashboard、
  quota/state、docs 与 smoke surface;不分组的话,以后的提交或 canary 晋升会
  更难审阅。
- P1 再添加一个晋升 gate fixture:推迟,因为结构化 gate 路径现在已有 JSON、
  status、dashboard、installer、分组 demo 就绪与 no-write 契约覆盖。
- P1 dashboard 打磨:推迟,直到当前产品加固批次被暂存或有意保持在一起。

无进展自停检查:未触发。近期合格 turn 产生了验证过的工件、新的分组 smoke
覆盖、状态写回与契约文档,而不是重复的状态检查。

## 暂存决策 - 2026-06-06T05:34:28+08:00

决策:本 heartbeat 中不要把 Batch 1 作为整文件暂存。

原因:第一个审阅批次产品上是连贯的,但若干必需文件没有 hunk 隔离。整文件暂存
会静默混淆发布晋升就绪与当前脏树的其他 surface:

- `loopx/status.py` 包含晋升 gate 投影,但也包含依赖 blocker、自主 backlog
  候选、事件 ledger 摘要、决策新鲜度、quota/handoff 助手与 status 契约变更。
- `README.md`、`docs/status-data-contract.md`、
  `examples/control_plane/status-markdown-smoke.py` 与 `examples/status.example.json`
  在更广的控制面与 status 契约更新之外,还携带晋升 gate 文档或 fixture。
- `apps/dashboard/src/views/dashboard-page.tsx` 不属于 Batch 1,但它消费相关
  status 字段,使得通过整文件暂存验证纯 Batch 1 审阅边界更难。

发布阻塞:当前脏树不应以普通 `git add <file>` 暂存为 Batch 1,因为那会抹掉清单
的审阅边界。安全路径是:

1. 在最低最终验证通过后,暂存一个更大的组合发布就绪产品加固批次,覆盖共享的
   Batch 1、Batch 2 与 Batch 4 status/dashboard surface;或
2. 为上述共享文件添加 hunk 级暂存地图,然后只暂存晋升 gate hunks 及其精确的
   测试/文档。

本决策没有暂存任何文件。Git index 保持可用,便于后续干净的暂存流程。

本决策后的验证:`python3 examples/promotion-gate-smoke.py`、
`python3 examples/control_plane/status-markdown-smoke.py`、`loopx-canary check`
与 `git diff --check` 通过。

## Hunk 级暂存地图 - 2026-06-06T05:38:30+08:00

目标:让下一次暂存流程在不丢失审阅边界的情况下可执行。

首选暂存策略:不要把 Batch 1 作为整文件暂存。要么暂存更大的组合发布就绪批次,
要么应用下方 hunk 地图,然后只暂存精确的发布晋升 hunks。

### 整文件暂存候选

这些文件足够窄,可为发布就绪批次整体暂存:

- `loopx/promotion_gate.py`
- `examples/promotion-gate-smoke.py`
- `examples/canary/canary-promotion-readiness-smoke.py`
- `examples/canary/canary-promotion-readiness-writeback-smoke.py`
- `examples/canary/canary-promotion-no-write-contract-smoke.py`
- `examples/dashboard-promotion-readiness-browser-smoke.mjs`
- `examples/dashboard-promotion-gate-warning-status.json`

这些文件也是发布就绪候选,但暂存前先审阅更大的组合批次是否包含
dashboard/demo 就绪:

- `apps/dashboard/smoke/usage-progress-smoke.ts`
- `examples/dashboard-demo-readiness-smoke.py`
- `examples/install-local-smoke.py`
- `scripts/install-local.sh`

### 共享文件的 Hunk 锚点

使用 `git add -p` 或等价的缓存 patch。除非选择更大的组合发布就绪批次,否则不要
整文件暂存这些文件。

- `loopx/cli.py`
  - 暂存 `.promotion_gate` 导入;
  - 暂存 `promotion-gate` 子解析器定义;
  - 暂存 `if args.command == "promotion-gate"` 处理器;
  - 避免无关的 review-packet、todo、heartbeat 或 global-registry hunks。
- `loopx/doctor.py`
  - 暂存 `PROMOTION_READINESS_CLASSIFICATIONS`、
    `PROMOTION_READINESS_FRESHNESS_HOURS`、
    `add_promotion_readiness_freshness()` 与 `latest_promotion_readiness_event()`;
  - 暂存 `release_provenance.promotion_readiness` 收集/渲染 hunks;
  - 避免无关的 install wrapper 或 PATH 诊断,除非组合发布就绪批次有意包含
    它们。
- `loopx/status.py`
  - 暂存来自 `doctor.py` 的 promotion-readiness 导入与 `build_promotion_gate`
    导入;
  - 暂存 `PROMOTION_READINESS_PROXY_NOTE`;
  - 暂存 `build_promotion_readiness_summary()`;
  - 暂存 `collect_status()` 中添加 `promotion_readiness_summary` 与
    `promotion_gate` 的 hunks;
  - 暂存 `render_status_markdown()` 中渲染 `## Promotion Readiness Summary` 与
    `## Promotion Gate` 的 hunks;
  - 避免依赖 blocker、自主 backlog、事件 ledger、决策新鲜度与 handoff-outcome
    hunks,除非使用更大的组合发布就绪批次。
- `README.md`
  - 暂存 install/canary-promotion 就绪说明;
  - 暂存 `promotion-gate --format json` 操作员指引;
  - 仅当批次也包含 dashboard 就绪文件时,暂存 dashboard demo 就绪引用;
  - 避免广泛的 README 重写 hunks,除非选择组合批次。
- `docs/status-data-contract.md`
  - 暂存 `promotion_readiness_summary` 与 `promotion_gate` 的可选顶层字段;
  - 暂存 `Promotion Gate JSON` 小节;
  - 暂存 `Promotion Readiness Summary` 小节与 quota 防护警告段落;
  - 避免无关的 top-4 todo、依赖 blocker、operator gate 或新鲜度契约 hunks,
    除非选择组合批次。
- `examples/control_plane/status-markdown-smoke.py`
  - 暂存 `build_promotion_readiness_summary` 的导入;
  - 暂存 `assert_promotion_readiness_summary_markdown()`;
  - 暂存 `assert_promotion_gate_summary_markdown()`;
  - 暂存 `assert_promotion_readiness_full_scan_fallback()`;
  - 暂存 `assert_promotion_readiness_warning_in_quota_guard()`;
  - 暂存匹配的 `main()` 调用;
  - 避免 connected-delivery outcome-floor 与其他 queue/handoff 断言,除非选择
    组合批次。
- `examples/status.example.json`
  - 只暂存 `promotion_readiness_summary` 与 `promotion_gate` 顶层 JSON 块以及
    直接需要的可选字段引用。
- `apps/dashboard/src/data/status.ts`
  - 暂存 `promotionReadinessSummarySchema`、`promotionGateSchema`、顶层
    `promotion_readiness_summary` / `promotion_gate` 与其导出类型;
  - 避免事件 ledger、决策新鲜度、依赖 blocker 与 handoff schema hunks,除非
    选择组合批次。
- `apps/dashboard/src/views/dashboard-page.tsx`
  - 暂存 promotion-readiness 与 promotion-gate 导入/类型;
  - 暂存 ops 面板中 `PromotionReadinessSummaryPanel` 与 `PromotionGatePanel`
    的插入;
  - 暂存两个面板组件及其变体助手;
  - 避免无关的 home-control-plane、top-4 todo、依赖 blocker、决策新鲜度与
    handoff UI hunks,除非选择组合批次。

### 推荐的下一暂存流程

冲突较小的路径是一个更大的组合发布就绪批次,覆盖 Batch 1 加上 Batch 2 与
Batch 4 中依赖的 dashboard/status 契约部件。该批次应在最低最终验证通过后才整
文件暂存:

```bash
python3 examples/run-smokes.py
python3 examples/canary/canary-promotion-readiness-smoke.py --no-write-evidence
npm --prefix apps/dashboard run smoke:demo-readiness
npm --prefix apps/dashboard run build
loopx-canary check
git diff --check
```

如果验证通过且没有私有边界问题,就暂存组合发布就绪批次,或写回阻塞暂存的精确
文件/hunk。

添加本地图后的验证:`python3 examples/promotion-gate-smoke.py`、
`python3 examples/control_plane/status-markdown-smoke.py`、`loopx-canary check`
与 `git diff --check` 通过。

## 已应用的暂存 - 2026-06-06T05:43:51+08:00

决策:最低最终验证通过后,以显式文件列表暂存更大的组合发布就绪产品加固批次。

原因:精确的 promotion-gate-only hunk 路径可用,但当前脏树已经是一个连贯的发布
就绪加固集,横跨晋升 gate、dashboard/demo 可用性、status 契约、quota/heartbeat
handoff、决策新鲜度与公开验证 smokes。把这些 hunks 保持拆分会增加审阅开销,而
不降低已验证的产品风险。

暂存前验证:

- `python3 examples/run-smokes.py`:通过,31 个 smoke 脚本。
- `python3 examples/canary/canary-promotion-readiness-smoke.py --no-write-evidence`:
  通过。
- `npm --prefix apps/dashboard run smoke:demo-readiness`:通过,包括 browser
  smokes。
- `npm --prefix apps/dashboard run build`:通过,带现有的 Vite chunk-size 警告。
- `loopx-canary check`:通过;公开边界扫描干净。
- `git diff --check`:通过。

暂存规则:使用该决策点的显式 `git status --short` 文件列表,而不是 `git add .`。

暂存结果:于 2026-06-06T05:44:53+08:00 以显式文件列表应用。Git index 现在为该
组合发布就绪产品加固批次包含 63 个已暂存文件。暂存后 `git diff --cached --check`
与 `git diff --check` 通过;`git status --short` 只显示发布就绪批次的已暂存条目。

## 提交决策 - 2026-06-06T05:47:20+08:00

决策:在分支 `codex/release-readiness-hardening` 上为已暂存的组合发布就绪产品
加固批次创建一个公开提交。

理由:已暂存批次通过了完整最低验证,公开边界扫描干净,且活动目标边界允许验证后
的常规 public-safe 仓库发布。该分支从当前本地 `main` 创建,本地 `main` 已领先
于 `origin/main`;本决策尚未推送或打开 PR。

提交作用域防护:不要添加未暂存的 runtime 输出、`.loopx/`、`.local/`、生成的
dashboard `dist/`、私有项目证据、凭据或生产标识符。

## 发布决策 - 2026-06-06T05:52:18+08:00

决策:推送分支 `codex/release-readiness-hardening` 并打开一个 draft PR。

结果:

- 分支已推送到 `origin/codex/release-readiness-hardening`;
- draft PR:https://github.com/huangruiteng/loopx/pull/1;
- PR 标题:`[codex] Harden release readiness control plane`。

发布备注:draft PR 有意叠在当前本地 `main` 谱系上。相对 `origin/main`,它包含
10 个提交:9 个围绕 handoff/delivery-scale 控制面加固的本地前驱提交,外加
`6fd9270 Harden release readiness control plane`。没有执行 rebase 或历史重写。

## Batch 1 - 晋升 Gate 与发布就绪

目的:把发布晋升就绪做成共享的结构化契约,而不是 installer stderr 散文或聊天
记忆。

候选文件:

- `loopx/promotion_gate.py`
- `loopx/cli.py`(promotion-gate 命令接线)
- `loopx/doctor.py`(release provenance 与 promotion readiness)
- `loopx/status.py`(promotion readiness 与 promotion_gate 投影)
- `scripts/install-local.sh`
- `README.md`(canary-promotion 与 promotion-gate 操作员路径)
- `docs/status-data-contract.md`
- `examples/promotion-gate-smoke.py`
- `examples/canary/canary-promotion-readiness-smoke.py`
- `examples/canary/canary-promotion-readiness-writeback-smoke.py`
- `examples/canary/canary-promotion-no-write-contract-smoke.py`
- `examples/install-local-smoke.py`
- `examples/control_plane/status-markdown-smoke.py`
- `examples/status.example.json`

近期切片已观察到的验证:

- `python3 examples/promotion-gate-smoke.py`
- `python3 examples/canary/canary-promotion-readiness-smoke.py --no-write-evidence`
- `python3 examples/canary/canary-promotion-readiness-writeback-smoke.py`
- `python3 examples/install-local-smoke.py`
- `python3 examples/control_plane/status-markdown-smoke.py`
- live status 读回,显示 `promotion_gate.gate_state=ready`、`can_promote=True`、
  `should_warn=False` 与就绪度 `fresh`。

审阅备注:

- `promotion-gate --format json` 是只读且非阻塞的。自动化应断言 `gate_state`、
  `can_promote`、`should_warn`、`non_blocking` 与 `readiness.freshness_status`,
  而不是解析 `warning_message` 或 installer stderr。
- `scripts/install-local.sh` 可能在就绪缺失/过时时告警,但显式晋升仍由 operator
  控制。
- 证据写回必须通过 refresh-state/run history 保持 append-only。

## Batch 2 - Dashboard、Demo 就绪与 macOS 本地可用性

目的:让 dashboard demo 路径稳健且便于分享时打开,包括稳定的本地服务与
browser/source smokes。

候选文件:

- `.gitignore`
- `apps/dashboard/README.md`
- `apps/dashboard/package.json`
- `apps/dashboard/src/data/status.ts`
- `apps/dashboard/src/router.tsx`
- `apps/dashboard/src/views/dashboard-page.tsx`
- `apps/dashboard/smoke/home-route-smoke.ts`
- `apps/dashboard/smoke/usage-progress-smoke.ts`
- `examples/dashboard-demo-readiness-smoke.py`
- `examples/dashboard-home-browser-smoke.mjs`
- `examples/dashboard-ops-decision-freshness-smoke.mjs`
- `examples/dashboard-promotion-readiness-browser-smoke.mjs`
- `examples/dashboard-promotion-gate-warning-status.json`
- `examples/macos-dashboard-launchagent-status-smoke.py`
- `examples/serve-status-global-registry-smoke.py`
- `scripts/macos-dashboard-launchagent.sh`

近期切片已观察到的验证:

- `npm run smoke:demo-readiness -- --skip-browser`
- `npm run smoke:demo-readiness`
- `npm run smoke:home-route`
- `npm run smoke:usage-progress`
- `npm run smoke:promotion-readiness`
- `node ../../examples/dashboard-home-browser-smoke.mjs`
- `node ../../examples/dashboard-ops-decision-freshness-smoke.mjs`
- `python3 examples/macos-dashboard-launchagent-status-smoke.py`
- `npm run build`

审阅备注:

- 本地 demo 服务目标为 dashboard 的 `127.0.0.1:5174` 与 status JSON 的
  `127.0.0.1:8766`。
- Browser smokes 有意启动临时 Vite server;保持它们显式或分组到 demo-readiness
  下,而不是藏在每次 heartbeat 里。
- 除非发布明确要求构建产物,否则不要暂存生成的 `apps/dashboard/dist/` 工件。

## Batch 3 - 控制面状态、Quota、Handoff 与决策新鲜度

目的:通过 registry 支持的状态、append-only 事件、quota 真相与检查点式决策
新鲜度,保持长时间运行 worker 的协调。

候选文件:

- `docs/heartbeat-automation-prompt.md`
- `docs/integration.md`
- `docs/quota-allocation.md`
- `docs/state-interaction-model.md`
- `skills/loopx-project/SKILL.md`
- `loopx/execution_profile.py`
- `loopx/heartbeat_prompt.py`
- `loopx/operator_gate.py`
- `loopx/quota.py`
- `loopx/review_packet.py`
- `loopx/state_refresh.py`
- `loopx/project_prompt.py`
- `examples/blocker-push-runtime-smoke.py`
- `examples/project/global-registry-sync-smoke.py`
- `examples/control_plane/heartbeat-prompt-smoke.py`
- `examples/project/operator-gate-resume-contract-smoke.py`
- `examples/control_plane/quota-contract-smoke.py`
- `examples/control_plane/quota-plan-smoke.py`
- `examples/control_plane/review-packet-cli-smoke.py`
- `examples/control_plane/review-packet-smoke.py`

近期切片已观察到的验证:

- `python3 examples/control_plane/heartbeat-prompt-smoke.py`
- `python3 examples/project/operator-gate-resume-contract-smoke.py`
- `python3 examples/control_plane/quota-contract-smoke.py`
- `python3 examples/control_plane/quota-plan-smoke.py`
- `python3 examples/control_plane/review-packet-cli-smoke.py`
- `python3 examples/control_plane/review-packet-smoke.py`
- `python3 examples/project/global-registry-sync-smoke.py`

审阅备注:

- 本批次编码的原则是:Codex 线程是 worker;append-only 运行历史与 registry
  支持的活动状态是持久的控制面。
- 决策点 rebase 意味着在复用旧 reward/gate 之前重新读取当前状态。它不会把
  repository 或 worker 上下文回滚。
- 验证通过且边界扫描干净后,常规 public-safe commit/push/PR 仍被允许;破坏性
  git、私有材料、凭据、生产动作或显式仓库审阅 gate 仍会阻止自动化。

## Batch 4 - Status、Demo 示例与公开边界 Fixture

目的:随着控制面契约增长,保持 status/check/demo 示例连贯。

候选文件:

- `loopx/bootstrap.py`
- `loopx/contract.py`
- `loopx/demo.py`
- `loopx/global_registry.py`
- `loopx/status.py`(共享 status/data 投影 hunks)
- `apps/dashboard/src/data/action-packet.ts`
- `examples/contract-reward-overlay-smoke.py`
- `examples/demo-cli-smoke.py`
- `examples/live-project-asset-handoff-readiness.py`
- `examples/registry.example.json`
- `examples/run-smokes.py`
- `examples/usage-summary-smoke.py`

近期切片已观察到的验证:

- `python3 examples/contract-reward-overlay-smoke.py`
- `python3 examples/demo-cli-smoke.py`
- `python3 examples/usage-summary-smoke.py`
- `python3 examples/run-smokes.py`(31 个公开 smoke 脚本)
- `loopx-canary check`

审阅备注:

- 有些文件,尤其是 `loopx/status.py` 与
  `apps/dashboard/src/views/dashboard-page.tsx`,横跨几个批次。如果审阅者想要
  小提交,请使用 hunk staging。否则,把相关 status/dashboard 批次合并为一个
  经审阅的产品加固提交。
- 保持 fixture public-safe 且基于相对路径。

## 跨领域状态与清单文件

候选文件:

- `goals/loopx-meta/ACTIVE_GOAL_STATE.md`
- `docs/commit-readiness-manifest-20260606.md`

指引:

- 只在提交意在随实现工作一起保留公开项目控制历史时,才包含活动状态写回。
- 本清单可作为发布审阅元数据提交,或在暂存中使用、后于最终分支偏好纯功能提交
  时移除。

## 不要提交

让这些远离任何公开提交:

- `.local/**`、`.loopx/**` runtime 输出、共享 `~/.codex/loopx/**` 运行历史、
  quota 事件或实时 reward overlay 数据。
- Codex App 自动化配置、线程元数据、截图、生成的浏览器会话状态与私有本地日志。
- `apps/dashboard/dist/**`,除非发布明确要求构建产物。
- 私有项目 worktree、内部链接、公司专属文档、原始本地用户路径、凭据、token、
  生产运行 id 或私有任务 ledger 数据。

## 提交或 Canary 晋升前的最低最终验证

最终暂存后或 canary 晋升前立即运行此集合:

```bash
python3 examples/run-smokes.py
python3 examples/canary/canary-promotion-readiness-smoke.py --no-write-evidence
npm --prefix apps/dashboard run smoke:demo-readiness
npm --prefix apps/dashboard run build
loopx-canary check
git diff --check
```

对于发布晋升证据写回,运行:

```bash
python3 examples/canary/canary-promotion-readiness-smoke.py
loopx-canary promotion-gate --format json
```

第二条命令应在 `scripts/install-local.sh` 把 live checkout 晋升为默认本地发布
快照前报告 `gate_state=ready`、`can_promote=true` 与 `should_warn=false`。

## 最近观察到的验证

近期 heartbeat 切片在此脏树或其直接子集上观察到:

- `python3 examples/run-smokes.py`:通过,31 个 smoke 脚本。
- `python3 examples/canary/canary-promotion-readiness-smoke.py --no-write-evidence`:
  通过,并在证据写回前显示了 dashboard demo 就绪。
- `npm --prefix apps/dashboard run smoke:demo-readiness`:通过,包括 browser
  smokes。
- `npm --prefix apps/dashboard run build`:通过,带现有的 Vite chunk size 警告。
- `loopx-canary check`:通过;公开边界扫描干净。
- `git diff --check`:通过。

本清单被编辑或任何额外实现文件被触碰后,重新运行最低验证。
