# 033 · 根 README 按用户旅程重排 + 与代码一致性修正

- **日期**: 2026-09-13
- **分支**: `260906-dev`
- **背景**: 用户指出根 `README.md` 写作顺序有问题——唯一可执行的安装/上手内容
  (`## 试用 LoopX`) 在 L166,前面压着 140 行定位与营销内容。同时要求核查 README
  与代码是否一致,并明确"不要破坏 loopx 的正常功能"。

## 用户确认的决策

1. **重排力度**: 用户旅程重排(安装 → 日常操作 → 定位 → 能力 → 证据 → 进阶 → 索引)。
2. **桌面预览段**: 整段删除;README 不再出现 macOS / Windows / 桌面 App 字样。
3. **范围**: README + 因重排而失效的守卫;不改产品代码、不改其它文档。
4. **交付**: 先只改工作区;复核通过后再提交推送。
5. **operation log**: 本文件(第 32 次之后继续配日志的惯例)。

## 变更清单

### 1. README 重排(新 H2 顺序,14 节)

```text
hero + 开场白(不动)
## 试用 LoopX            ← 原 L166 提到最前
## 日常操作与恢复          ← 原 ### 提升为 ##
## 认识个人 Agent 工作区
## 为什么需要 LoopX
## 能力
## 证据                  ← 含 <a id="看几个例子"></a>,锚点随节移动
## 进阶路径
## 当前技术方向
## 进阶文档
## 合作伙伴项目 / 用户群与反馈 / 贡献 / 当前状态
## Star 趋势              ← 守卫锁死:必须是最后一节
```

### 2. 内容修正(3 处)

1. **删除桌面预览段**(原 L49–54): "也可从 1.0 Release 下载桌面预览版 / Apple Silicon
   macOS 签名 App 更新 / Windows 预览版手动更新 / 桌面安装指南链接"。依据 op 032
   (本 fork 只在 Linux/WSL2 运行,已从 live 文档移除 Windows 指引)。保留
   `` `loopx dashboard` 是受支持的浏览器 / PWA 启动方式。`` 一句。
2. **`### 日常操作与恢复` → `## 日常操作与恢复`** 并上移到安装之后。
3. **`loopx check --scan-path …` 发布边界扫描块**从日常操作节移入 `## 贡献`
   (紧跟"不要提交 `.loopx/`、raw benchmark 证据…"段),它属公开发布前的边界检查,
   不是日常循环操作。

### 3. 守卫同步(1 个文件)

`examples/public_entry/readme-demo-surface-smoke.py:31-33`:

```python
# 改前:auto_research = readme.split("### Auto Research", 1)[1].split("## 试用 LoopX", 1)[0]
auto_research = readme.split("### Auto Research", 1)[1].split("\n## ", 1)[0]
```

旧切片假设 `### Auto Research` 出现在 `## 试用 LoopX` **之前**;重排后该假设失效,
切片会一路吃到文件末尾(实测 256 行)并命中 L584 的"未脱敏",导致
`assert "脱敏" not in auto_research` 误报。新右边界取"下一个 `## ` 标题",
与 `docs-governance-smoke.py:518` 处理 `## 进阶文档` 的写法一致。切片语义等价:
实测新切片 15 行 = Auto Research 小节正文 + 一个前导换行(612 vs 613 字符)。

## 验证

### 双树对照(最强证据)

用 `git archive HEAD`(只读)在 `/tmp/loopx-head-baseline` 建干净 HEAD 快照,把
**14 个读根 README 的 smoke** 在两棵树各跑一遍:

- **0 个状态变化**;
- 5 条失败在快照里**同样失败**,且**报错逐字节一致**:
  - `codex-cli-bootstrap-message-smoke` — 生成文案缺 `heartbeat automation`;
  - `release-readiness-doc-smoke` — 缺 `Status: v0.x maintainer contract.`;
  - `quota-contract-smoke` — 缺 `## Allocation Contract`(中文转换漂移);
  - `heartbeat-prompt-smoke` — 载荷 `char_count: 6334 > 6200`,两树同为 6334
    (若重排有影响该数字必然变化);
  - `codex-cli-packaged-install-smoke` — `FileNotFoundError: <repo>/LICENSE`
    (op 023 已删除 LICENSE)。

### 其余门

- **命令面**: 从新 README 提取 33 条 `loopx` 调用逐条 `--help` → **0 FAIL**。
- **链接面**: 75 个本地链接 **0 断链**(改前 76,少 1 正是删掉的桌面指南链接)。
- **边界扫描**: `loopx check --scan-path README.md --scan-path docs/ --scan-path examples/`
  → `errors=0, warnings=0`,876 文件,4 条 credential reference 降级(与改前一致)。
- **canary**: `loopx canary smoke-suite --from-git-diff --git-diff-base HEAD` →
  `ok=true`,4/4 passed;`loopx canary premerge` 的风险 profile 唯一失败项
  `codex-cli-packaged-install-smoke` 经双树对照确认为既存。
- **纯位移证明**: 相对 HEAD 的非空行多重集 **7 删 2 增**(6 行桌面段 + 截短的
  dashboard 句 + `### → ##` 标题行);13 个共有 H2 节里 11 个**逐字节相同**,
  另 2 个的差异经精确 diff 确认只有锚点行 + 一个空行随 `## 证据` 迁移。
- **markdown 结构**: 34 个标题全部前有空行、无连续空行、围栏 20(偶数)、
  0 行尾空格、0 CRLF。
- **产品功能**: `loopx doctor` → `ok: True`(两处 `repair_recommended` 是
  `~/.codex/skills` 未安装与既有 registry 投影状态,与 README 无关);
  `loopx/**` 产品代码不解析 README 内容(`onboarding.py:12`、`project_map.py:38`
  只判存在性);`tests/**` 零个读根 README。

### 自查中发现并修复的自身缺陷(1 处)

第一版重排时,锚点 `<a id="看几个例子"></a>` 与 `## 证据` 之间的空行被空行归一化
逻辑吃掉(HEAD 为 `</a>\n\n## 证据`,改后成 `</a>\n## 证据`),是全文件唯一一个
前一行非空的标题。已补回;复查确认所有标题前均有空行。

### 对抗性复核的误报澄清

`readme-demo-surface-smoke.py:76-77` 的 `loopx-logo.png` 首屏断言**是空转的**:
该字符串在 HEAD 与改后都是 0 次出现,永远不可能失败——它不构成对首屏的约束。
本条为既有事实,不在本批范围内。

## 已知悬空引用(按用户决策未处理)

1. `docs/index.md:51-59`、`docs/guides/getting-started.md:28,167,291` 仍教
   `pip install --upgrade loopx`(上游 PyPI),与"本 fork 唯一支持的开发方式"冲突,
   而 README 正把 getting-started 作为安装入口推荐。
2. `loopx/claude_goal_mode/README.md` 安装路径 A 用
   `LOOPX_INSTALL_CLAUDE=1 scripts/install-local.sh`——本 fork 明令禁止、会静默
   接管 editable 安装的脚本;README 的 host 表把 Claude Code 适配器指向该文档。
3. `benchmark/swe-marathon/agents/codex_loopx_agent.py:101` 的注释按行号引用
   README host 表(`README.md:289-291`)。**改动前就已过期**(HEAD 为 L216-221),
   本批未动——benchmark adapter 文件受 AGENTS.md 单独评审关卡约束。
4. `docs/product/release-readiness.md:196` 与 `apps/desktop/loopx-control-plane/README.md:3`
   仍在宣传 macOS/Windows 桌面预览产物(op 032 未清的历史残留)。
5. `heartbeat-prompt-smoke.py:1049` 断言英文串
   `LoopX is not an autonomous production controller`,该串在 HEAD 与改后都不存在;
   该 smoke 在更早的载荷预算断言处即失败,故该行不可达。

## 与上游分叉

README 的**章节顺序**现在与上游不同,后续合并上游时 README 会持续冲突。
按 `docs/development/editable-dev-loop.md:124-128` 的 precedence 规则,以本 fork
版本为准(上游会带回 PyPI 安装叙述与按 host 排列的结构)。
`mkdocs.yaml:9` 仍排除 `/README.md`,故本次重排不影响文档站导航。

## 提交/推送

- 提交拆分为:README 重排(公开文档) / 守卫同步(聚焦验证) / 本日志,均带
  `-s` DCO 签署:
  - `71c42b2b6` docs: reorder the root README around the install path(`README.md`);
  - `07e7fe146` test: re-seat the README Auto Research guard after the reorder
    (`examples/public_entry/readme-demo-surface-smoke.py`);
  - 本日志与 `000-INDEX.md` 一个 commit。
- 推送目标: `origin/260906-dev`(本 fork 惯例为在 `260906-dev` 上直接提交并推送;
  AGENTS.md 的 `codex/` worktree + PR 条款继承自上游,与本 fork 实践不符)。

按用户指示推送：`c9af7d433..90e25a21a`（本批 3 个提交，一次 push）。
