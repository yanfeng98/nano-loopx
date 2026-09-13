# 035 · 文档事实性修正（doctor 字段、验证清单、mkdocs slug 规则与既有断锚）

- **日期**: 2026-09-13
- **分支**: `260906-dev`
- **背景**: 用户报告「`command -v loopx` 与 `docs/development/editable-dev-loop.md` 不一致」。逐条实测后，
  `command -v` 本身与文档**一致**，但由此暴露出该文档两处事实性错误、我自己上一处修复的三个问题，
  以及一处**我此前验证方法的错误假设**。

## 用户报告的核对结果

| 文档要求 | 实测 | 判定 |
| --- | --- | --- |
| `command -v loopx` = `<python-env>/bin/loopx` | `/home/luyanfeng/miniconda3/bin/loopx`（`python3` 在 miniconda3） | 一致 ✓ |
| `pip show loopx \| grep -i editable` = `<checkout>` | `/home/luyanfeng/luyanfeng/nano-loopx` | 一致 ✓ |

"看起来不一致"的根源是文档只说 console script 在解释器 bin 下，**没说明它只是 shim、代码在 checkout 里**。

## 修正 1（事实错误）：`install_kind` 与 `status` 被混为一谈

- 文档称 editable 安装「`install_kind` 恒为 `live_checkout`」。实测 `loopx doctor` 的
  `## Install Freshness`：`status: live_checkout` / `install_kind: release_or_checkout`。
- 代码：`loopx/doctor.py:614` 的 `install_kind` 只有 `python_distribution` / `release_or_checkout`；
  `:479` 的 `status` 才是 `live_checkout`（判据「当前命令不是带时间戳的发布快照」）。
- 机制复核（`loopx/doctor.py:172-190`）：`python_distribution_install()` 查 RECORD 中是否存在
  `loopx/doctor.py` 且其路径等于被导入模块——PEP 660 的 RECORD 没有，故 editable **恒为**
  `release_or_checkout`。文档原有的机制解释正确，**字段名写错**。

## 修正 2（格式）：`loopx version` 实际输出 `loopx 1.0.0`（带前缀），文档写「期望 1.0.0」。

## 修正 3（补全）：验证清单补第 4 条

```bash
python3 -c "import loopx; print(loopx.__file__)"  # 应指向 <checkout>/loopx/__init__.py
```

并写明两条检查的**抗遮蔽能力不同**：console script 的 `sys.path[0]` 是其 bin 目录、cwd 无关；
`python3 -c` 的 `sys.path[0]` 是 cwd，在含 `loopx/` 的目录里会 import 到那一份。

## 修正 4（我上一处修复引入的三个问题）

1. 加了第 4 条命令却没把「验证三件事」改成「四件事」；
2. 第 4 条与本页 cwd 遮蔽章节冲突——在 clone 里实测：`import loopx` 命中
   `/tmp/loopx-now-clone/loopx/__init__.py`；已注明必须在 checkout 根目录运行；
3. 我加的页内链接 `#陷阱cwd-遮蔽` 在**渲染站点上是死的**。

## 修正 5（方法错误 + 由此暴露的既有断锚）

- 根因：**本仓库的 mkdocs 构建使用 ASCII slug**——`## 陷阱：cwd 遮蔽` 渲染为 `id="cwd"`，
  `## skills：什么时候必须重跑` 渲染为 `id="skills"`，纯中文标题退化为 `id="_1"`/`"_2"`。
  仓库惯例「中文标题显式 `{#...}`」正是为此。
- **因此 op 034 第三轮报告的「锚点级全库校验 28 条 / 0 不可达」是用错误的 unicode slug 假设算出的**，
  因多数跨页锚点本身是显式锚点而侥幸通过——该结论作废，已在此更正。
- 用修正后的规则重跑：**29 条锚点 / 1 条不可达**，即既存的
  `topic-long-horizon-convergence.md → 04-state-substrate.md#core-statedomain-state-与-runtime-artifact`
  （真实渲染 id 为 `core-statedomain-state-runtime-artifact`，"与"被 ASCII slug 剥掉）。
  已给该标题加显式锚点 `{#core-state-domain-state-runtime-artifact}` 并改指链接，
  **mkdocs 不再打印该锚点告警**。

## 验证

- 修正规则后的锚点校验：**29 条 / 0 不可达**（规则与 mkdocs 实际行为一致，可复现）。
- `mkdocs build --strict`：exit 0，课程那条锚点 INFO 告警消失。
- `docs-governance-smoke`、`dev-book-publication-smoke` 通过；`release-readiness-doc-smoke`
  维持既存失败（`Status: v0.x maintainer contract.`）。
- **产品代码零改动**：本批只动 3 个 docs 文件。

## 环境备注（非本批引入）

观察到 `~/.codex/skills/.loopx-skill-install.json` 写于 2026-09-13 21:25:17、解释器 bin 下的
console script 重写于 21:13:45。核查：本会话跑过的 smoke 均设隔离 `HOME`/`CODEX_HOME`，且本会话
从未执行 `pip install -e .` 或 `workflow-skills --install`——这两次写入来自会话之外（用户按文档
操作或宿主 agent）。副作用：`doctor` 的 `skill_delivery_status` 由 `repair_recommended` 变为 `ready`。

## 提交/推送

- `5a7395135` docs: correct the install-kind and version claims in the editable dev loop
- `a9e168c69` docs: fix what the review of the previous commit turned up

按用户指示推送：`45d30e987..a9e168c69`（2 个提交，一次 push；本行记录的日志提交为后续补记）。
