# 034 · 安装口径收口（删除上游安装指南 + 全量清扫 PyPI 文案）

- **日期**: 2026-09-13
- **分支**: `260906-dev`
- **背景**: 用户判定 `docs/guides/installing-loopx.md`「如果没有用，以及删除后不影响 loopx 的
  功能，请你删除」。核查后发现它**不是整页无用**——`### 验证各激活层 {#verify-the-active-layers}`
  是一节活的四层 readback 清单（被 `docs/product/release-readiness.md:40` 引用，且含 fork 自己的
  checkout 修正），其余是上游 PyPI / pipx / 归档通道叙述。据此向用户给出三选一，用户选
  **「删页 + 搬运活内容」**，随后追加 **「全部清扫」**。

## 用户确认的决策

1. **删除 + 搬运**：删页，先把活内容搬进 `docs/development/editable-dev-loop.md`。
2. **收口 getting-started 的 PyPI 段**。
3. **全部清扫**剩余的 PyPI 安装文案（含发布机制类文档）。
4. **交付**：只提交，不推送。

## 变更清单（22 文件，+144/−342，含 1 个整文件删除）

### 1. 删页与搬运

- 删除 `docs/guides/installing-loopx.md`（208 行）。
- 活内容搬进 `docs/development/editable-dev-loop.md` 的新节 `## 验证各激活层 {#verify-the-active-layers}`
  （四层 readback 表 + 恢复列 + checkout 的 fail-closed 更新说明），**锚点 id 原样保留**，
  使 `release-readiness` 只需改路径。
- `editable-dev-loop.md` 两处"上游原文保留在本仓库供对照"的表述改为：原文不再保留，需要时用
  `git show upstream/main:docs/guides/installing-loopx.md`。

### 2. 引用改指（0 处悬空）

`mkdocs.yaml`（移除 Installation 导航项）、`README.md`、`docs/guides/README.md`、
`docs/product/release-readiness.md`、`docs/book/welcome-wagon.md`、
`docs/book/chapters/05-connect-existing-project.md`。

### 3. 守卫同步（3 个）

- `examples/release/release-readiness-doc-smoke.py`：`INSTALL_GUIDE` → `ACTIVE_LAYER_DOC`
  （指向新家），断言换成中文串并**断言锚点自身**，使 release-readiness 的引用被守卫住；
  随上游文本一起退役的英文串（`### Verify The Active Layers`、tagged-package 句、
  `runtime_activation_qualification`）删除。
- `examples/dev-book-welcome-wagon-smoke.py`：`SHARED_COMMANDS` 里的 PyPI 行改为就地安装行。
- `examples/codex-cli-first-run-rehearsal-smoke.py`：文档 `must_have` 的 PyPI 两行改为就地安装行，
  并把 `assert_indexes()` 的 `assert "PyPI" in product` 改为 editable 口径
  （**这条是本批唯一被双树对照抓到的真实回归**，见验证节）。

### 4. 全量清扫：12 处用户安装路径改为就地 editable

`docs/index.md`（文档站首页）、`docs/guides/newcomer-command-path.md`、
`docs/guides/custom-agent-runner-integration.md`、`docs/book/welcome-wagon.md`、
`docs/book/chapters/05-connect-existing-project.md`（含"为什么不先 clone LoopX"的 tip，反转为
本 fork 的口径）、`docs/community/github-maintenance-ops-best-practices.md`（curl 安装器）、
`docs/product/release-readiness.md`、`docs/product/release-note-template.md`、
`docs/product/runtimes/codex-cli/codex-cli-packaged-install.md`（3 处安装块 + 前提）、
`codex-cli-first-run-rehearsal.md`、`codex-cli-tui-loop.md`（3 份相同的"可直接粘贴 setup message"
副本）、`getting-started.md`（安装段 + 两处粘贴消息）。

### 5. 有意保留的发布 / canary 机制（有据，不是遗漏）

`scripts/install-local.sh` 与 `loopx-canary` 通道在本 fork **仍然存在**（README 与
`editable-dev-loop.md` 只禁止在*开发环境*里运行它，因为它会静默接管 editable 安装；
`examples/fresh-clone-quickstart-smoke.py` 仍在隔离 HOME 中测试它）。因此：

- `getting-started.md` 的 `## 全局 Skill 安装、更新、修复与清理`（带 fork 偏差横幅）保留；
- `docs/product/runtimes/codex-cli/codex-cli-no-clone-release-verification.md` 保留，但顶部新增
  **本 fork 偏差段**，并在 `codex-cli/README.md` 的索引行标注它验证的是上游归档通道；
- `docs/status-data-contract.md` 中对 `install-local.sh` 的消费者描述保留。

## 验证

- **双树对照**（真实 git clone 基线，含全部 5 个提交）：**20 个守卫 0 状态变化**；
  8 个既存失败（`release-readiness-doc`、`codex-cli-bootstrap-message`、
  `codex-cli-tui-bootstrap-smoke-bundle`、`codex-cli-no-clone-release-verification`、
  `codex-cli-packaged-install`、`quota-contract`、`heartbeat-prompt`）在两棵树同因失败。
- **回归捕获**：`codex-cli-first-run-rehearsal-smoke` 在改写 `codex-cli/README.md` 后由 OK 转 FAIL
  （其 `assert_indexes()` 逐字要求索引里出现 `PyPI`），双树对照抓到后改为 editable 口径，恢复两树 OK。
  这是本批唯一一次真实回归，也是该方法存在的意义。
- **`mkdocs build --strict`** → exit 0；渲染站点中 `id="verify-the-active-layers"` 存在、
  release-readiness 指向它、被删页面已不在站点。
- **docs 链接** → 818 条 / 0 断链。
- **边界扫描** → `errors=0, warnings=0`，875 文件（876 − 被删文件）。
- **活文档残留**：PyPI / pipx / curl 安装命令只剩三处**故意保留**的"不要运行"警告
  （`README.md`、`editable-dev-loop.md`）。

### 第二轮自查（换角度：文案自身是否自洽、渲染锚点、遗漏站点）

前一轮查的是"守卫是否变红"，第二轮换三个角度，发现并修掉 **2 个我自己引入的缺陷**：

1. **6 处与仓库事实矛盾的过度断言**：改写里写了"本 fork **不提供**归档安装器 / canary wrapper /
   发布快照通道"，但 `scripts/install-local.sh` 与 `scripts/install-from-github.sh` 都在仓库里，
   README 明说 canary 路由保留给发布工作（只禁止在开发环境里运行）。已改为真实口径：
   开发与用户安装 = editable；发布快照/归档 = 发布与 canary 工作、需隔离运行
   （涉及 `codex-cli-packaged-install.md` ×4、`release-readiness.md`、`chapters/05`、
   `github-maintenance-ops`）。
2. **`docs/operations/new-project-codex-prompt.md` 是可粘贴提示，却把 agent 指向
   `$HOME/loopx/scripts/install-local.sh`**（与已修的三份 onboarding 粘贴消息同类，此前漏掉）。
   已改为从 checkout 就地安装；其守卫 `examples/project/project-prompt-smoke.py` 把该命令断言在
   **共享**的 `assert_quota_guard()` 里（CLI 生成的 payload 也走这个函数），故把该断言移出共享函数、
   改为只对文档的 editable 行断言，产品 payload 的期望保持不变。

第三角度的结果（无新动作）：渲染后我新增的跨页链接与锚点全部可达；活文档中仅剩三处**故意保留**的
"不要运行"警告与带偏差横幅的发布/canary 段落。

### 第三轮自查（锚点级校验、提交历史自洽性、premerge）

- **锚点级全库校验**（此前只查文件是否存在）：docs/ 与根 README 的跨文件 `#fragment` 链接
  **28 条，不可达 0 条**。
- **逐提交自洽性**（把 8 个提交各 `git archive` 出来单独检查）：7 个提交 0 断链 / 0 断锚；
  **提交 1（`860f09503`）有 1 处悬空锚点**——它把 getting-started 指向
  `editable-dev-loop.md#verify-the-active-layers`，而该锚点由提交 2（`cb90d02ad`）才引入。
  这是本批唯一的历史中点在缺陷，**判定为不重写历史**：本 fork 的惯例是修复前向的"复查修正"提交，
  且重写会让本日志记录的 8 个 SHA 全部失效；此外两种重排都不更优——把删除提交放前面，getting-started
  反而会留下指向已删文件的**文件级**悬空链接。窗口深度为 1 个提交、仅存在于未推送的本地历史，
  当前树 0 悬空。
- **`loopx canary premerge --from-git-diff --git-diff-base origin/260906-dev`**：本批选中 8 项
  风险检查，7 通过 + 1 失败（`codex-cli-packaged-install-smoke`）。在基线上逐项重跑同一组：
  **结论逐项一致**（该 smoke 在基线亦因 `LICENSE` 已删而失败）→ 无新增失败。
- **产品功能回归**：根 README 提取的 **33 条 `loopx` 调用全部可达（0 FAIL）**；`loopx doctor` → `ok: True`，
  TypeScript Effect runtime `ready`。
- **既存站点问题（在基线 clone 上同样复现）**：① `docs/architecture.md` 与 `docs/architecture/README.md`
  争用同一渲染 URL，导航里的 Architecture 落到后者，`release-readiness.md:323` 的
  `#current-dependency-budget` 锚点在站点上不可达；② `docs/development/control-plane-course/topic-long-horizon-convergence.md`
  的 `04-state-substrate.md#core-statedomain-state-与-runtime-artifact` 锚点告警。两者 mkdocs 都只报 INFO，
  `--strict` 不拦截。

### 第四轮自查（pytest 层 + 修正双树方法自身的盲点）

- **pytest 全套**（`-n 4`，5572 项）：当前树 `5 failed / 5567 passed / 19 skipped / 3 errors`，与基线
  **逐项一致**（同一组 5 个失败 + 同一组 3 个 collection error）→ **测试层零差异**。
- **发现并修正了自己验证方法的盲点**：基线跑在 `/tmp` 的 git clone 里，其 `origin` 是**本地路径**
  而非 SSH URL；`tests/control_plane/test_quota_settlement_cli.py` 会从仓库 remote 推导工作区 git 身份，
  于是本地路径 remote 让其中 2 条测试**确定性失败**。取证：把当前 HEAD 也克隆一份同样失败，而同一份
  内容在真实仓库目录里通过；把 clone 的 remote 改成 `git@github.com:yanfeng98/nano-loopx.git` 后立即
  27/27 通过（机制确认）。修正基线环境后重跑全套：基线 `5 failed / 5567 passed / 3 errors`，与当前树
  完全一致。此前所有"FAIL/FAIL 既存"结论在修正后的基线上逐条复核，**8 项全部同因**。
  → 教训：基线复制必须在**影响被测行为的维度上等价**（remote、路径、git 状态），否则会得到
  方向性偏差的结论。
- 其余新检查：渲染后的四层表格是真表格（4 表头 / 4 数据行 / 恢复列含 fork 口径）；
  `operation-logs/000-INDEX.md` 34 条链接 0 断链；仓库无实验残留（仅既有 ignored 缓存目录）；
  `loopx canary smoke-suite --suite full-public --no-execute` 仍匹配 494 项检查。

**顺带发现的既有问题（非本批引入，未处理）**：

- `docs/product/release-readiness.md:323` 的 `../architecture.md#current-dependency-budget` 锚点在渲染站点
  中不可达（`docs/architecture.md` 与 `docs/architecture/README.md` 争用同一 URL，落点是后者）——
  基线快照中同样存在，`mkdocs --strict` 与 `docs-governance` 的链接检查（会剥离片段）都不覆盖锚点。
- `examples/project/project-prompt-smoke.py` 在基线与当前树上同点失败（CLI 生成 payload 的中文漂移断言，
  在文档断言之前触发），属既存红灯。

## 已知遗留（未处理）

1. **产品代码仍输出上游通道命令**：`loopx codex-cli-bootstrap-message` 的 `install_repair_command`、
   `doctor` 的 `upgrade_command`、`bootstrap` 的 `archive_fallback_install_command` 仍是
   PyPI / `install.sh`。多个既存红灯守卫正是断言这些字符串（`codex-cli-bootstrap-message-smoke:63,225`、
   `fresh-clone-quickstart-smoke:116,148,150`）。改它们属**产品代码变更**，需单独决策。
2. `docs/book/chapters/05-connect-existing-project.md` 的要求行仍写「POSIX shell（macOS、Linux 或
   WSL2）」（op 032 的决定），与本 fork「只在 Linux 与 WSL2 运行」的 README 口径不完全一致。
3. `getting-started.md` 的 canary 段虽按上面的理由保留，但其"以下保留上游原文供对照"的定位与刚被
   删除的 `installing-loopx.md` 同类；是否进一步收敛（把上游原文也移出仓库）留待后续决策。

## 提交/推送

7 个提交，按评审逻辑拆分（日志本提交另计）：

- `860f09503` docs: stop teaching the PyPI install path in onboarding messages
- `cb90d02ad` docs: replace the upstream install guide with a fork-owned checklist
- `a4ee852fe` test: retarget the release-readiness install-guide guard
- `fb7ea43c3` docs: close the PyPI install path in the remaining user-facing docs
- `6206319ee` docs: rewrite the Codex CLI attach docs for the in-place checkout
- `4ba704533` docs: correct the channel claims and the new-project prompt after review
  （第二轮自查的修正）

按用户指示**只提交，不推送**；推送目标为 `origin/260906-dev`。
