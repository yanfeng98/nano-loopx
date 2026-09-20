# 040 · 退役贡献者看板

- **日期**: 2026-09-20
- **分支**: `260906-dev`
- **背景**: 工作区里已有一批未提交的删除：`docs/development/contributor-tasks.md`（143 行整页）与
  `README.md` 的一行链接。用户决定**整页退役**该看板。按本仓库先例（op 037/038/039），这类删除
  必须产品侧、路由侧、守卫侧同时收口；分析结论是这批删除**只动了产品侧的一处**，且另有一条
  **已推送的 commit 自身就是守卫回归**。

## 起点状态（两处独立的红）

**① 工作区的删除是半成品。** `README.md` 全文有 3 处看板引用，本批只改了 1 处（`## 贡献` 段），
`:488` 与 `:539` 仍是死链；另有 16 个文件仍指向已删页面。干净 HEAD worktree 对照：
`peer-agent-hard-cut-boundary-smoke`、`session-runtime-control-plane-adapter-doc-smoke` 在 HEAD 为绿、
在工作区为红（都是 `FileNotFoundError` 读该页），`docs-governance-smoke` 在工作区于 `:296` 报
`broken local docs link: docs/README.md -> development/contributor-tasks.md`。

**② 已推送的 `caa3be369` 是守卫回归。** 该 commit 删掉了看板的「当前技术方向」「优先级队列」两节与
「产品管理切口」的两行，而 `docs-governance-smoke` 正钉着这些内容。干净 HEAD worktree 实测：
**`HEAD~1` 绿、`HEAD` 红**，`:354` 报 `四个 canonical 全局 manager CLI 命令已交付`；修掉后 `:418`
还会再红一次（四个方向名也已被删）。这条 commit 只检查了「它看起来改了哪块」，没有跑钉住该块的守卫。

## 归属决策

op 039 把看板定为技术方向的 canonical 投影；本批把看板整页退役，于是方向叙事回到它本来就该在的位置：
`docs/architecture/rfcs/README.md`（职责区的 owner）声明方向，每份 RFC 自标状态与当前边界，可认领工作
回到 GitHub issue。看板的代价是它必须在每次刷新时与 RFC、issue、owner 边界逐条对齐，而它已经漂移
（`caa3be369` 删掉的两节里就有已完成与已改向的条目）。

## 路由侧（16 文件）

| 表面 | 处理 |
| --- | --- |
| `README.md` | `### 项目与社区` 去掉看板链接；`## 贡献` 去掉旧句；`## 当前状态` 末句改指 RFC 索引 + Contributing |
| `CONTRIBUTING.md` | 「寻找工作」改指 RFC 索引与 issue，并去掉指向已不存在 issue 模板的「贡献者任务模板」措辞；公共/私有扫描去掉看板 `--scan-path`；控制器计划改指 `turn-loop-controller-v0.md` |
| `docs/README.md` | 表格行第二列改为[架构 RFC]；项目与社区列表去掉该项 |
| `docs/development/README.md` | 「从这里开始」步骤 2 与核心参考表改指 RFC 索引 |
| `docs/architecture/rfcs/README.md` | 「当前技术方向」句改为自述，不再指向看板 |
| `docs/community/open-strategy-reviews.md` | portfolio 事实源与会前准备改指 RFC |
| `docs/book/`（4 文件 5 处） | `source-protocol-map.md`（2 处入口 + 1 处标签）、`appendix-reference.md`、`source-validation-to-pr.md`、`welcome-wagon.md` 改指 Contributing / RFC 索引 / public issue |
| `docs/operations/pr-issue-labels.md` | `workflow-audit` 的应用方由「贡献者任务板」改为「维护者分类」 |
| `docs/superpowers/plans/2026-08-14-interpret-turn-journal.md` | 示例命令去掉已删路径的 `--scan-path` |
| `docs/product/core-control-plane/smoke-failure-classification-ledger.md` | session-runtime 行的打包缺口按事实改写为「已收口」，行本身保留 |
| `loopx/control_plane/turn_driver/loop_controller.py` | docstring 改指 `docs/reference/protocols/turn-loop-controller-v0.md` |
| `loopx/canary/premerge.py` | `DOC_CONTENT_TOKENS` 去掉该路径 |

## 守卫侧（4 守卫）

- `examples/docs-governance-smoke.py`：删 `CONTRIBUTOR_TASKS.md` 的 `MOVED_PATHS` 项、目录 allowlist 项、
  `STABLE_README_DOCS_ENTRY_LINKS` 项、「项目与社区」契约项与 `combined_public_indexes` 里的 `read()`；
  把 `assert_contributor_task_board_is_current` 与 `assert_contributor_task_links_are_current` 整体换成
  **退役守卫** `assert_contributor_board_is_retired`：页面必须不存在 + `docs/**/*.md`、`README.md`、
  `CONTRIBUTING.md`、`mkdocs.yaml` 不得再出现该 slug + 两个 loopx 文件不得再出现 + 四个活入口文档与
  整个 `docs/book/` 不得再出现 `Contributor Task` 标签；
  `assert_technical_direction_governance_is_current` 去掉读取该页与四个方向名断言。
- `examples/control_plane/peer-agent-hard-cut-boundary-smoke.py`：`SCAN_FILES` 去掉该页。
- `examples/session_runtime/session-runtime-control-plane-adapter-doc-smoke.py`：去掉常量、读取与 require 块
  （顺带结清台账里那条 P2 打包缺口）。
- `examples/dev-book-publication-smoke.py`：`signal-to-bounded-work` 的必需引用由看板 URL 改为
  `CONTRIBUTING.md` blob URL。
- 新增 `architecture/rfcs/README.md` 的目录 allowlist 项：它不在 mkdocs 顶层 nav（由
  `architecture/README.md` 链接），属既有的「非 nav 主入口」类别。

## 验证

**双树对照（干净 HEAD worktree vs 工作区）。**

| 守卫 | HEAD | 工作区 |
| --- | --- | --- |
| `docs-governance-smoke` | 红（`:354`，`caa3be369` 引入） | 绿 |
| `peer-agent-hard-cut-boundary-smoke` | 绿 | 绿 |
| `session-runtime-control-plane-adapter-doc-smoke` | 绿 | 绿 |
| `dev-book-publication-smoke` | 绿 | 绿 |
| `dev-book-welcome-wagon-smoke` | 绿 | 绿 |
| `readme-demo-surface-smoke` | 绿 | 绿 |
| `showcase-catalog-smoke` | 绿 | 绿 |
| `docs-asset-integrity-smoke` | 绿 | 绿 |

**全套 canary `full-public`（480 checks，`--jobs 8`）。** 基线 30 失败 / 工作区 29 失败，
**按命令名做集合差：worktree-only 集合为空**，唯一差异是 `docs-governance-smoke` 由红转绿。
29 条共有失败逐一静态核对：**无一条读取本批改动的文档**，与本批无关。

**新守卫的阴性对照**（只验证「会通过」不算验证）：① 从 HEAD 复活该页且**零引用** → 命中存在性断言；
② 页面不在、但 `docs/README.md` 以**纯文本**提及该 slug → 命中 stale 扫描并点名 `docs/README.md`。
两种都被抓住，随后还原。

**其它。** `mkdocs build --strict` 基线 0 / 工作区 0（本机原本缺 `mkdocs-gen-files`，按
`docs/requirements-docs.txt` 装上后才可跑）；`loopx check` 公共边界扫描 errors=0（862 文件）；
`ruff check` 6 个改动脚本 `All checks passed!`；`python3 -m py_compile` 通过。

**全套 pytest（双树各跑一次）。** 两棵树都是 `4 failed, 5616 passed, 19 skipped, 3 errors`（约 610s），
按**失败身份**逐条比对：7 条 node id 集合完全相同（2 条 scheduler ack 状态机、1 条 change-window
worktree 私有路径、1 条 pr-program skill 文本、3 条收集期 `from tests.capabilities import ...` 导入失败），
无新增、无消失。3 条收集期错误在干净 HEAD 上逐字复现，属本机 pytest 导入环境漂移（op 039 记录的是
`0 errors`），与本批无关。

## 自查中发现并修掉的问题

1. **只修第一个断言不够。** `caa3be369` 触发的是 `docs-governance-smoke` 的两处独立断言
   （`:354` 与 `:418`），这正是 op 038 记过的教训：冒烟首个断言即中止，失败集合一致查不出全部回归。
2. **守卫复查了我的路由清单。** 我第一版把 `docs/README.md` 的表格行改指 `architecture/rfcs/README.md`，
   立刻触发 nav parity 断言（该页不在 mkdocs 顶层 nav 且无 allowlist 原因）——需要显式 allowlist 条目，
   而不是把断言放宽。
3. **编辑器 autofix 会咬人。** markdownlint 自动修正在 `CONTRIBUTING.md`、`docs/README.md`、
   `docs/operations/pr-issue-labels.md`、`rfcs/README.md`、`open-strategy-reviews.md`、`welcome-wagon.md`
   与 superpowers plan 里引入了与本批无关的纯格式改动（H1 后空行、列表前空行、裸邮箱改 autolink、
   grid card 缩进），已逐处还原。其中 `source-protocol-map.md` 的 autofix 把 `#3157` 改成 `# 3157`，
   会**直接打断 `dev-book-publication-smoke` 的 `#3157` 断言**——如果没复查 diff，这就是本批自己造的回归。
4. **退役守卫的范围比想的大。** 按 op 039 的写法把 `docs/**/*.md` 全域纳入扫描后，才发现
   `docs/superpowers/plans/2026-08-14-interpret-turn-journal.md` 的示例命令里也有该路径（守卫必红）。
5. **`CONTRIBUTING.md` 的「贡献者任务模板」是上游遗留。** 该 fork 已无 `.github/`（op 028/029），
   issue 模板并不存在，同段改写时一并去掉。

## 已知遗留（未处理）

1. **DCO**：`HEAD~1..origin/main` 区间 **183/285 条 commit 缺 `Signed-off-by`**，含已推送的 `caa3be369`。
   本批未改写历史（单条 amend 不能使分支合规，且需要 force-push），但本批新提交全部带 `-s`。
   若将来要以 PR 形式合入 `main`，需整段 rebase 签署或改用 squash 合并。
2. 基线即有的 29 条 canary 失败（环境/既存）未在本批处理。
3. `docs/operations/pr-issue-labels.md` 整页仍假设存在 issue/PR 模板（`.github/` 已删），只修了本批
   触碰的 `workflow-audit` 行；整页口径留待单独一批。
5. 本机 pytest 存在 3 条收集期导入错误（干净 HEAD 同样复现），是环境漂移而非仓库缺陷。
4. `docs/showcases/cases/`、`docs/update-notes/2026-*.md`、`skills/loopx-self-repair/SKILL.md` 里的
   「贡献者任务」字样保留：它们是带日期的历史记录或泛指概念，不是指向该页的路由。
5. `operation-logs/000-INDEX.md` 缺 039 行（上一批漏记），本批补上。

## 提交/推送
- `7b111029b` docs: retire the contributor board and its live entry points
- `30ef616f0` test(smoke): pin the retired contributor board instead of reading it

推送至 `origin/260906-dev`。已推送的 `caa3be369` 未改写：它删掉的两节正是本批退役的内容，
其守卫回归由本批的守卫改写结清（`HEAD~1` 未动）。
