# 提交就绪清单 - 2026-06-03(已关闭的历史快照)

> [English](commit-readiness-manifest-20260603.md)

状态:已关闭的历史快照。下述公开脏树已经过验证,并在后续 LoopX 切片中提交、
推送。不要把这个文件当作当前脏树检查清单。

当前用途:

- 把这个文件当作档案证据:2026-06-03 公开树在发布前如何分组。
- 在任何簇(cluster)行动之前,用 `git status --short`、`git log -1
  --oneline`、`loopx --format json check --scan-root .` 和
  `goals/loopx-meta/ACTIVE_GOAL_STATE.md` 重新检查当前就绪状态。
- 把下述发布策略说明当作历史上下文,而不是当前树已可发布的证明。

对于公开 LoopX 每日迭代,当 public-sensitive 扫描干净、验证通过,且变更不含
公司内部或私有材料时,允许自主提交/推送与 PR 创建。

## Steering 审计

选定切片:为当前公开脏树生成一个四簇提交就绪清单。

考虑过的候选:

- P0 脏树提交就绪清单:选定,因为未分组的公开变更现在造成了协调负担。
- P0 健康/状态复查:有价值,但已经干净,且单靠它不足以让脏树可审阅。
- P1 dashboard/demo 打磨:再次允许,但在现有变更被分组并验证之前价值较低。

无进展自停检查:未触发。近期合格的 heartbeat 产生了真实状态、自动化和公开
提示词生成器变更,所以这不是一个 5-turn 状态循环。

## Cluster 1 - 首次运行与 Heartbeat 生命周期契约

目的:让全新用户路径与循环 heartbeat 提示词更安全地复制,内置无进展自停防护,
使自动运行不会在反复状态检查上无限空转。

候选文件:

- `README.md`
- `docs/heartbeat-automation-prompt.md`
- `loopx/heartbeat_prompt.py`
- `skills/loopx-project/SKILL.md`
- `examples/control_plane/heartbeat-prompt-smoke.py`

本切片已运行的验证:

- `python3 examples/control_plane/heartbeat-prompt-smoke.py`
- `python3 -m py_compile loopx/heartbeat_prompt.py examples/control_plane/heartbeat-prompt-smoke.py`
- `python3 -m compileall -q loopx`

提交前剩余:

- 手动重新生成一个样例 `loopx heartbeat-prompt --goal-id ...` 输出,并浏览
  确认其保持人类可读。
- 检查公开模板没有承诺超出"通过自动化管理删除或暂停"的特定 Codex App API
  surface。

边界风险:

- 该提示词讨论 Codex App 自动化行为。把它保持得足够通用以面向公开用户,不要
  提及本地线程 id、超出示例的本地自动化 id,或私有操作员历史。

## Cluster 2 - Runtime、Status 与契约真相

目的:当存在本地/demo 运行时残留或 run 绑定的人类奖励叠加(human reward
overlay)时,保持 status 与健康可信。

候选文件:

- `loopx/history.py`
- `loopx/status.py`(runtime/status hunks)
- `loopx/contract.py`
- `examples/control_plane/status-markdown-smoke.py`
- `examples/contract-reward-overlay-smoke.py`

先前切片或本切片已运行的验证:

- `python3 examples/control_plane/status-markdown-smoke.py`
- `python3 examples/contract-reward-overlay-smoke.py`
- `loopx --format json check --scan-root .`

提交前剩余:

- 在最终暂存集上运行聚合公开 smoke runner:`python3 examples/run-smokes.py`。
- 确认 reward-overlay 重复处理仍在普通重复索引行上报警,而不只是新 fixture。

边界风险:

- `status.py` 还携带 Cluster 3 的审阅材料变更,所以文件级提交会混入簇,除非
  使用 hunk staging。
- 共享本地 runtime 下的 runtime 或 demo 目录绝不能暂存。

## Cluster 3 - 用户 Todo 审阅材料读取器

目的:让面向用户的 todo 携带安全的 Markdown 审阅材料,使 dashboard 能在不强迫
操作员手动浏览项目文件的情况下展示第一个有用的阅读包。

候选文件:

- `loopx/materials.py`
- `loopx/status.py`(todo 审阅材料 hunks)
- `loopx/status_server.py`(回环 `/review-material` 端点)
- `apps/dashboard/src/data/status.ts`
- `apps/dashboard/src/views/dashboard-page.tsx`(审阅材料 UI hunks)
- `examples/user-todo-review-material-smoke.py`

先前切片已运行的验证:

- `python3 examples/user-todo-review-material-smoke.py`

提交前剩余:

- 最终暂存后重新运行 `python3 examples/user-todo-review-material-smoke.py`,因为
  它覆盖路径包含检查与服务器访问。
- 确认共享 dashboard hunks 后 dashboard 构建仍通过:
  `npm --prefix apps/dashboard run build`。

边界风险:

- 审阅材料读取必须保持仅本地 Markdown,根限制在 goal repo/state/runtime 根目录
  内,并且只通过 status server 回环访问。
- 本簇中不要为支持远程 URL 而削弱 URL/路径检查。

## Cluster 4 - Dashboard 奖励追加流程

目的:让 dashboard 奖励追加路径使用精确的 dry-run 载荷,包括 `recorded_at`,使
追加动作不能偏离操作员接受的预览。

候选文件:

- `apps/dashboard/src/views/dashboard-page.tsx`(奖励 dry-run 载荷锁定 hunks)
- `examples/dashboard-reward-append-browser-smoke.mjs`

先前切片已运行的验证:

- `npm --prefix apps/dashboard run build`
- `node examples/dashboard-reward-append-browser-smoke.mjs`

提交前剩余:

- Cluster 3 与 Cluster 4 hunks 都暂存后,重新运行 dashboard 构建。
- 如果提交奖励追加路径,重新运行 browser smoke。

边界风险:

- `apps/dashboard/src/views/dashboard-page.tsx` 同时含 Cluster 3 与 Cluster 4
  hunks。如果操作员想要独立提交,请使用 hunk staging;如果不想要,就把
  Cluster 3 与 Cluster 4 一起作为"dashboard 操作员动作路径"提交。
- 奖励追加有意由回环 status server 与 `--enable-reward-write-api` 把门;不要
  为远程 status URL 提供它。

## 跨领域状态与清单文件

候选文件:

- `goals/loopx-meta/ACTIVE_GOAL_STATE.md`
- `docs/commit-readiness-manifest-20260603.md`

提交指引:

- 把 `goals/loopx-meta/ACTIVE_GOAL_STATE.md` 当作公开状态写回。若公开边界扫描
  保持干净,可随最终"状态与清单"提交一起包含。
- 本清单可作为审阅元数据提交,或视操作员发布偏好,在最终纯功能提交前删除。

## 不要提交

这些不属于公开脏树,必须排除在任何提交之外:

- 任何 connected 项目的 `.local/**`。
- Codex App 自动化配置与线程元数据。
- 本地 LoopX runtime 目录下的共享 runtime 历史,包括 quota spend、状态刷新、
  归档 demo 与 reward overlay 运行文件。
- 临时 demo 项目目录、dashboard dev-server 工件、生成的截图、浏览器会话状态,
  以及 `apps/dashboard/dist/`(除非发布明确要求构建产物)。
- 私有项目 worktree、内部链接、私有文档、原始本地路径、凭据、token、任务 id,
  或生产运行标识符。

## 最低最终验证

任何提交或 PR 前,运行:

```bash
python3 examples/run-smokes.py
python3 examples/control_plane/heartbeat-prompt-smoke.py
python3 examples/control_plane/status-markdown-smoke.py
python3 examples/user-todo-review-material-smoke.py
python3 examples/contract-reward-overlay-smoke.py
npm --prefix apps/dashboard run build
node examples/dashboard-reward-append-browser-smoke.mjs
loopx --format json check --scan-root .
git diff --check
```

如果任何 dashboard/browser smoke 被跳过,在提交前把跳过原因记录到活动目标状态
中。

## 最终验证运行 - 2026-06-03T10:53:49+08:00

状态:通过。

运行的命令:

- `python3 examples/run-smokes.py`
- `python3 examples/control_plane/heartbeat-prompt-smoke.py`
- `python3 examples/control_plane/status-markdown-smoke.py`
- `python3 examples/user-todo-review-material-smoke.py`
- `python3 examples/contract-reward-overlay-smoke.py`
- `npm --prefix apps/dashboard run build`
- `node examples/dashboard-reward-append-browser-smoke.mjs`
- `loopx --format json check --scan-root .`
- `git diff --check`

备注:

- 聚合 smoke runner 通过了 18 个公开 smoke 脚本。
- Dashboard 构建通过,带现有的 Vite chunk-size 警告。
- Dashboard 奖励追加 browser smoke 通过。
- `loopx check` 通过,errors=0、warnings=0,86 个文件上公开边界扫描干净。

## Public-Sensitive 差异审阅 - 2026-06-03T10:56:57+08:00

状态:通过。该切片中没有提交、推送或暂存。

审阅范围:

- 来自 `git diff --name-status` 的 13 个修改过的已跟踪文件。
- 来自 `git ls-files --others --exclude-standard` 的 5 个未跟踪公开候选文件。
- 当前脏树仍属于上面列出的四个簇加状态/清单写回。

运行的命令:

- `git status --short`
- `git diff --name-status`
- `git ls-files --others --exclude-standard`
- `git diff --stat`
- 对候选文件进行针对性 `rg` 敏感模式扫描。

发现:

- 在审阅的候选文件中未发现私有路径、内部 URL、公司文档标记、敏感指派、认证头
  模式或云密钥模式。
- `apps/dashboard/src/views/dashboard-page.tsx` 同时含审阅材料与奖励追加 hunks;
  若操作员想为 Cluster 3 与 Cluster 4 分开提交,请使用 hunk staging。
- `loopx/status.py` 同时含 runtime/status 与审阅材料 hunks;若 Cluster 2 与
  Cluster 3 要保持分离,请使用 hunk staging。
- `goals/loopx-meta/ACTIVE_GOAL_STATE.md` 是大型状态写回;把它保留为最终
  状态/清单提交,或当操作员想要精简发布分支时从功能提交中省略。

自主或操作员请求提交的建议暂存顺序:

1. Cluster 1:首次运行与 heartbeat 生命周期契约。
2. Cluster 2:runtime、status 与契约真相。
3. Cluster 3:用户 todo 审阅材料读取器。
4. Cluster 4:dashboard 奖励追加流程。
5. 状态与清单写回,若适合作审阅元数据。

任何 hunk staging 后重新运行最低最终验证,因为 hunk 拆分可能把共享的
dashboard/status 假设意外移到不同提交之间。

## 发布策略更新 - 2026-06-03T11:05:02+08:00

操作员澄清:公开每日迭代在提交、推送或 PR 创建前不需要显式请求。

当前策略:

- 公开边界扫描干净且验证通过时,允许公开 LoopX 变更的自主提交/推送。
- 同一边界下允许自主 PR 创建,通常在工作不在意图目标分支上时。
- 如果变更包含私有状态、公司内部材料、凭据、生产标识符或无法解释的生成工件,
  在发布前停止。
- 对这个已验证的脏树,使用上述暂存顺序,并在发布前重新运行最低最终验证。

## 发布验证 - 2026-06-03T11:06:50+08:00

状态:通过;发布当前公开 LoopX 脏树是安全的。

运行的命令:

- `python3 examples/run-smokes.py`
- `python3 examples/control_plane/heartbeat-prompt-smoke.py`
- `python3 examples/control_plane/status-markdown-smoke.py`
- `python3 examples/user-todo-review-material-smoke.py`
- `python3 examples/contract-reward-overlay-smoke.py`
- `npm --prefix apps/dashboard run build`
- `node examples/dashboard-reward-append-browser-smoke.mjs`
- `loopx --format json check --scan-root .`
- `git diff --check`
- 对候选文件进行针对性 `rg` 敏感模式扫描。

备注:

- 聚合 smoke runner 通过了 18 个公开 smoke 脚本。
- Dashboard 构建通过,带现有的 Vite chunk-size 警告。
- Dashboard 奖励追加 browser smoke 通过。
- `loopx check` 通过,errors=0、warnings=0,88 个文件上公开边界扫描干净。
- 针对性敏感模式扫描没有发现任何内容。
