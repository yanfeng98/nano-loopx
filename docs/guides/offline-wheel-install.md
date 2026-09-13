# 离线 wheel 安装

本 fork 只有两条受支持的安装路径：**checkout 就地 editable 安装**（开发用，见
[就地开发闭环](../development/editable-dev-loop.md)）与**本地构建的 wheel 文件**（发给其他人用）。
两者都不走 PyPI、不联网、不使用任何上游发布版。

本页讲第二条：在一台机器上构建 wheel，拷到目标机器离线安装。

## 先决条件（目标机器）

| 依赖 | 要求 | 说明 |
| --- | --- | --- |
| Python | 3.11+ | wheel 的 `requires-python` |
| Node.js | **22.6+** | TypeScript 控制面**直接执行** `.ts`（`node --experimental-strip-types`），wheel 带不走 Node，必须目标机自备 |
| 平台 | Linux 或 WSL2，POSIX shell | 本 fork 不提供 Windows 路径 |

不需要网络、不需要 pip 索引、不需要 clone 仓库，也不需要 Node 的 npm 依赖（控制面没有构建步骤）。

## 1. 在构建机生成 wheel

```bash
cd <loopx-checkout>
bash scripts/build-wheel.sh
```

它做三件事：校验 `pyproject.toml` 与 `loopx/__init__.py` 的版本一致、**清掉 `build/`**
（setuptools 会复用陈旧的 `build/lib`，可能把旧文件或缺失文件打进 wheel）、再用
`pip wheel . --no-deps --no-build-isolation` 离线构建。产物：

```
dist/loopx-<version>-py3-none-any.whl        # 例：dist/loopx-1.1.0-py3-none-any.whl
```

可用 `--out-dir <dir>` 改输出目录。构建**不需要**网络：`--no-build-isolation` 让构建使用解释器里
已有的 setuptools，而不是去索引拉 `[build-system].requires` 里钉住的版本。

## 2. 拷到目标机器并安装

```bash
# 可选但推荐：装进独立 venv，避免与系统 Python 互相污染
python3 -m venv ~/.venvs/loopx
~/.venvs/loopx/bin/python -m pip install --no-deps <path-to>/loopx-<version>-py3-none-any.whl

# 交付 workflow skills 并自检
~/.venvs/loopx/bin/loopx workflow-skills --install
~/.venvs/loopx/bin/loopx doctor
```

`--no-deps` 是对的：本包没有运行期依赖（`dependencies = []`）。skills 从 wheel 内的
`share/loopx/skills/` 复制到宿主根（Codex 默认 `~/.codex/skills`；Claude Code 需显式
`--skills-dir ~/.claude/skills`）。

`loopx doctor` 会报告 `install_kind: python_distribution` 与 `status: python_distribution`——
这就是"由 pip 管理的发行版"形态。skills 未交付时它会提示重跑 `workflow-skills --install`。

## 3. 升级与回滚

升级 = 用新 wheel 覆盖安装，然后重新交付宿主材料：

```bash
<venv>/bin/python -m pip install --force-reinstall --no-deps <new-wheel>
<venv>/bin/loopx workflow-skills --install
<venv>/bin/loopx doctor
```

回滚 = 用上一个 wheel 重跑同样三条命令（**保留旧 wheel 文件**就是回滚方案；本 fork 没有索引版本
可钉，也没有发布快照通道）。`loopx update check|plan` 会把这些命令按当前安装形态打印出来，
方便你确认。

## 4. 验证 wheel 是否完整

仓库内有一个端到端冒烟，它构建 wheel、装进临时 venv、在隔离 `HOME`/`CODEX_HOME` 下跑
`doctor`、交付 skills 并跑发行版深度检查：

```bash
python3 examples/wheel-install-smoke.py
```

它同时断言 wheel 里**必须有**：控制面全部 `.ts`（与仓库数量一致）、
`loopx/canary/module_metric_baseline.json`、`loopx/claude_goal_mode` 的 plugin 资产、
6 个宿主 skills 与 2 个项目级 skills（含 `.loopx-skill-scope` 标记）。
少任何一项，`loopx canary` 或 `loopx project-skill` 在 wheel 安装下就会失败。

## 不要做的

- **不要**用 PyPI / pipx / 归档安装器安装本 fork：它不发布这些通道，而且它们会在同一环境里
  生成第二份 `loopx`（`~/.local/bin` 通常排在 `PATH` 最前），静默接管你的安装。
- **不要**手工解压 wheel 或 `pip install --target`：skills 的定位依赖 pip 写下的 RECORD /
  `direct_url.json`，绕过 pip 会让 `workflow-skills --install` 找不到源。
- **不要**把 `dist/*.whl` 当通配路径喂给 `pip`：`dist/` 里若有多个版本，pip 会拒绝；请用精确文件名。
