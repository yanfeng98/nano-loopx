# 039 · 退役技术方向页与残余社区表面

- **日期**: 2026-09-17
- **分支**: `260906-dev`
- **背景**: 工作区里已有一批未提交的删除。要求分析后收口、提交并推送。分析结论是
  这批删除**只做了产品侧，路由侧与验证侧都没跟上**——按本仓库先例
  （`63192342a` 在同一个提交里同步改守卫），那属于未完成的改动，不是可直接提交的状态。

## 工作区已有的删除

| 文件 | 改动 |
| --- | --- |
| `docs/project/technical-directions.md` | 整页删除（54 行）。`63192342a` 刚把它砍成"live sections"，这是再往前一步 |
| `README.md` | −28 行：「合作伙伴项目」（OpenViking / NoKV）与「用户群与反馈」（Discord、飞书群二维码、微信 `huangrt00`） |
| `docs/assets/loopx-lark-developer-group.png`、`loopx-wechat-contact.png` | 删除（134 KB / 451 KB） |
| `docs/development/contributor-tasks.md` | −33 行：上游看板框架（H1、「公开投影」说明、状态图例、认领步骤） |

三块内容同源：`3ddec0839`（zh-CN 提为主文件）时留下的上游社区身份，与
`fec8a7940`「sever the former upstream identity」、op 037 是同一条线。

## 方向的去向

被删页面里**唯一仍然存活**的内容是「当前技术方向」表——它已经在
`docs/development/contributor-tasks.md` 里存在，列着每个方向的结果、阶段、
贡献者入口与属主边界。所以退役不等于内容消失：**看板承接 canonical 方向投影**，
所有「当前技术方向」引用改指看板。这条判断决定了下面 11 处链接怎么写。

## 路由侧收口（13 文件）

- **11 处失效链接跨 8 个文件**：`README.md`（`:488` 列表项 + `:537` 正文）、
  `CONTRIBUTING.md`、`docs/README.md`（表格行 + 项目与社区列表）、
  `docs/development/README.md`（步骤 2 + 核心参考表）、`docs/architecture/rfcs/README.md`、
  `docs/community/open-strategy-reviews.md`、`docs/book/welcome-wagon.md`、
  `docs/development/contributor-tasks.md` 自身。其中 `63192342a` 的提交信息
  **已显式列出** README 当前投入段、RFC index、CONTRIBUTING 与 Developer Book 四处
  outstanding——本批把它留下的账结清。
- **`mkdocs.yaml:141` nav 条目**：删。实测 `mkdocs build --strict` 因此由 exit 1 转 0
  （非 strict 下是 1 条 nav WARNING + 5 条断链 WARNING）。
- **`ecosystem-adoption.md` 的锚点**：删 README 章节后，该行仍指向
  `../../README.md#合作伙伴项目`。改写为直接陈述合作伙伴边界（NoKV 仍是位于
  LoopX authority 之后、尚未晋级的可选 provider candidate），不再跨树指锚点。
- **Developer Book 保持绝对链接**：`welcome-wagon.md` 原来第 1、2 项分别指向已退役页
  与看板，合并为一项、指向看板，链接仍是 `/loopx/docs/development/contributor-tasks/`。
- **补回 H1**：`contributor-tasks.md` 删掉框架块后从 `## 当前技术方向` 开始、全文 0 个 H1，
  补 `# 贡献者任务`。

## 验证侧收口（3 守卫）

两个守卫在 HEAD 上都是绿的，在工作区都是红的——**是这批退休引入的真回归，不是基线红灯**。
用 `git worktree` 在 HEAD 做对照，排除了"本来就坏"：

| | HEAD 基线 | 工作区 |
| --- | --- | --- |
| `docs-governance-smoke` | exit 0 | exit 1 |
| `readme-demo-surface-smoke` | exit 0 | exit 1 |

**`docs-governance-smoke` 实为 6 处断点，不是 1 处。** 冒烟在首个断言即中止，只暴露
`:558`（文件存在性）。用内存中和探针逐条中和后跑完全程，才枚举出其余五处：
`:297`（本地链接解析）、`:207`/`:230`/`:255`（nav parity、文档目录、稳定 README 入口），
以及 `:399`——它从 `read()` 抛 `FileNotFoundError` 而**不是 AssertionError**，
中和断言的做法对它无效，必须先中和 `:558` 才能撞上。

处置：从五个钉住列表里删掉退役路径，并把原先 `read()` 该页的函数改写成**退役守卫**：
该页必须不存在，且 `docs/**/*.md`、`README.md`、`CONTRIBUTING.md`、`mkdocs.yaml`
里都不得再出现 `technical-directions`。这样这次退役不会被悄悄回滚。

`readme-demo-surface-smoke` 是 1 个断言点、4 个字面量（「用户群与反馈」标题、两张
二维码路径、微信联系行），全在同一个循环里，首断即遮蔽其余三个。

**`showcase-catalog-smoke` 是第三个，也是最隐蔽的一个。** 它钉的是
`https://github.com/yanfeng98/nano-loopx`，而该字符串在 README 里的**唯一出处**正是被删的
「用户群与反馈」块里的 Issue 链接；README 保留下来的 clone 行是 SSH 形式
`git@github.com:...`，不含这个子串。HEAD~2 绿、工作区红，同属本批回归。

修法不是删断言，而是把入口放回去：在**贡献**节恢复 GitHub Issue 链接。社区节退役了，
但"去哪里报问题"属于贡献流程，且公共 fork 的 README 本就该指向自己的仓库。

## 验证

- `docs-governance-smoke`、`readme-demo-surface-smoke`、`showcase-catalog-smoke`、
  `docs-asset-integrity-smoke`、`update-notes-archive-smoke`、`repository-hygiene-smoke`、
  `interaction-pattern-catalog-smoke`、`slash-command-catalog-smoke` 全部 exit 0。
- `mkdocs build --strict` exit 0（收口前 exit 1）。
- `dev-book-publication-smoke`、`dev-book-welcome-wagon-smoke` exit 0。
- `grep -rn technical-directions` 除 `operation-logs/`（历史记录）与守卫自身的退役断言外为空。
- **全套 pytest**：`5 failed, 5637 passed, 19 skipped, 0 errors`（567s）。按**失败身份**
  而非计数与基线逐条比对：集合完全相同，无新增、无消失；5 条原因类别也未变
  （git `worktree list -z` 不支持、scheduler ack 状态机两条、dashboard launcher 的
  Codex bin 发现、pr-program skill 文本），均与本批文档改动无关。
- **新守卫的阴性对照**：本批新增的退役断言只验证"会通过"不算验证，故在 HEAD 的临时
  worktree 里分别制造两种情况——① 页面复活但**零引用** → 命中 `:403` 存在性断言；
  ② 页面不在、但文档以**纯文本**提及该 slug（不构成链接，绕过链接解析）→ 命中 `:410`
  并点名 `docs/README.md`。两种都被抓住。

## 自查中发现并修掉的问题

1. **自查第一轮漏了三处链接，是守卫抓出来的。** 我只改了 `docs/README.md` 的表格行，
   漏了同文件 `:58` 的列表项与 `docs/development/README.md` 的两处步骤/表格引用；
   重跑守卫才在 `:296` 报 `broken local docs link: docs/README.md ->`。这也反过来说明
   文档与守卫**分开提交**是有价值的：守卫不是装饰，它独立复算了一遍我的路由清单。
2. `contributor-tasks.md` 删头部后 0 个 H1（见上）。
3. **只跑"我改过的守卫"会漏掉第三个守卫。** `showcase-catalog-smoke` 与被删内容没有字面
   交集——它钉的是 URL，不是标题或资产路径——所以按被删字符串做的全域 grep 找不到它，
   是**把文档守卫家族整体跑一遍**才暴露的。教训：退役一批内容后，回归检查的广度应由
   "共享主题"（公共入口文档）决定，而不是由"我碰过哪些文件"决定。

## 已知遗留（未处理）

1. `operation-logs/029`、`030` 中对该页的历史提及保留不动——那是当时的记录。
2. Developer Book 里 4 处英文标签仍写 "Contributor Task Board"：标签依然准确（看板还在），
   只是不再有对应的页面标题，未改。
3. 本批未动 `docs/archive/`，也未复核 `docs/book/chapters/` 里对看板的其他引用（均指向文件本身，
   不涉及被退役页）。

## 提交/推送

- `84dcb23dd` docs: retire the technical-directions page and the residual community surfaces
- `e40f95fe3` fix: repair the two guards left stale by the retired surfaces
- `a31b74e54` fix: restore the repository link the community retirement took with it

推送至 `origin/260906-dev`。
