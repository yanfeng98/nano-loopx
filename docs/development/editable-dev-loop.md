# 就地开发闭环（Editable Dev Loop）

本页描述**本 fork 唯一支持的开发方式**：把这个 checkout 装成 editable 安装，改完就地验证。
对外分发走另一条路——本地构建的 wheel，见[离线 wheel 安装](../guides/offline-wheel-install.md)。

## 一次性准备

```bash
cd <checkout>
python3 -m pip install -e . --no-deps --no-build-isolation
```

- `-e` 让 `loopx`（console script，位于 `<python-env>/bin/loopx`）永远执行**工作区里的代码**：
  改完 `.py` 直接重跑命令就是验证，没有构建、没有拷贝、没有第二份安装。
- `--no-deps --no-build-isolation` 让这条命令完全离线：`pyproject.toml` 的 `dependencies`
  为空，构建后端 `setuptools` 已随环境提供。换到没有 setuptools 的环境时去掉
  `--no-build-isolation`（代价是联网取构建依赖）。
- 验证四件事：

```bash
loopx version                                     # 期望输出 `loopx 1.1.0`
python3 -m pip show loopx | grep -i editable      # 应指向 <checkout>
command -v loopx                                  # 应是 <python-env>/bin/loopx——它只是 shim
python3 -c "import loopx; print(loopx.__file__)"  # 应指向 <checkout>/loopx/__init__.py（在 <checkout> 根目录运行）
```

后两条要一起看：console script 永远在**解释器的 bin** 下（`<python-env>/bin/loopx`），它本身不含代码，
真正被 import 的是 checkout 里的 `loopx/`。只有 `command -v` 为 `<python-env>/bin/loopx` **且**
`import loopx` 落在 `<checkout>` 下，才是健康的 editable 安装。

两条的抗遮蔽能力不同，所以都要跑：console script 的 `sys.path[0]` 是它的 bin 目录，**不受 cwd 影响**；
而 `python3 -c` 的 `sys.path[0]` 是 cwd，在含 `loopx/` 子目录的目录里会 import 到那一份（见下面的
[cwd 遮蔽](#cwd-shadowing)），所以最后一条要在 `<checkout>` 根目录跑。

**反直觉点**：`pip show loopx` 的 `Version` 可能落后于 `loopx version`。运行时版本是
`loopx/__init__.py` 里的字面量，包元数据只在你跑过安装命令时才刷新——两者不一致不代表装坏了。
刷新元数据（同时重建 console script）：

```bash
python3 -m pip install -e . --no-deps --no-build-isolation
ls <python-env>/bin | grep '^loopx'   # 核对是否有早已废弃的入口残留
```

## 最短闭环：改 → 验证

```bash
# 1. 直接改 checkout 里的代码
# 2. 直接跑——不需要重装、不需要重启（每次执行都是新进程）
loopx <命令>
# 3. 需要更硬的证据时，跑聚焦测试或聚焦 smoke
python3 -m pytest -q tests/test_<area>.py
python3 examples/<focused>-smoke.py
```

正在长驻的进程（例如 `loopx dashboard`）读的是启动时的代码，需要你重启它。
全量测试的口径（含本机 `--continue-on-collection-errors`）见[测试与质量体系](testing-and-quality.md)。

## 什么会立即生效、什么需要重装或重建

| 你改了什么 | 需要做什么 | 为什么 |
| --- | --- | --- |
| `loopx/**/*.py`（CLI、内核、doctor…） | **无**，直接重跑 | editable 安装把 `loopx` 映射到 checkout |
| `loopx/control_plane/**/*.ts`、`*.json` | **无** | Node ≥ 22.6 用 `--experimental-strip-types` 直接执行：无构建步骤、无 npm 依赖 |
| `loopx/web/chat/**`（已提交的构建产物） | **无** | 产物随代码一起在 checkout 里 |
| 新增 `loopx/` 下的子目录（带或不带 `__init__.py`） | **无** | 实测可导入：editable 把 `loopx` 映射到 checkout，子模块走常规 import |
| 新增 `loopx` 之外的**顶层包** | 重装 editable | finder 的包映射表（`MAPPING`）在安装时静态生成，只含 `loopx`；实测新建顶层包在重装前 `ModuleNotFoundError` |
| `pyproject.toml`（`version`、`[project.scripts]`、package-data） | 重装 editable | console script 与元数据由安装器生成 |
| `skills/**` | 重跑 skills 安装（见下节） | skills 是复制，不是链接 |
| `apps/presentation/dashboard/src/**`（前端源码） | `cd apps/presentation/dashboard && npm run build:chat` | `loopx dashboard` 读的是 `loopx/web/chat/`；产物被 git 跟踪，重建会产生 git diff（只重建 chat 即可，完整 `npm run build` 是 dashboard + chat） |
| `docs/**`、`examples/**`、`tests/**` | **无**（除非被某个 smoke 断言） | 内容即产物 |

## skills：什么时候必须重跑

`loopx workflow-skills --install` 把 `skills/` 下的 workflow skill **复制**到宿主 skill 根目录
（不是软链接；内容一致时重复执行是 no-op），并写一份 readback，其中记录安装时的
`git rev-parse HEAD`。因此：

- 改了 `skills/**` → 内容摘要不匹配，必须重跑；
- **产生了新的 commit → 即使 skills 一字未改也必须重跑**（readback 报 `source_revision_mismatch`）；
- 只改工作区、不 commit，不会触发 revision 不匹配。

两个宿主根（Codex CLI 与 Claude Code 都用，所以两条都跑）：

```bash
loopx workflow-skills --install                                  # Codex CLI，默认根 ~/.codex/skills
loopx workflow-skills --install --skills-dir ~/.claude/skills    # Claude Code 必须显式指定
```

- `CODEX_HOME` 覆盖 Codex 默认根；`workflow-skills` **没有** `--surface` / `--link` / `--force`，
  只有 `--install` / `--uninstall` / `--skills-dir` / `--cli-bin` / `--dry-run`。
- 只读自查：直接跑 `loopx workflow-skills`（不带 `--install`），读 `install_required` 与 `before.ready`。
- `loopx slash-commands --install` 是**另一个**安装器（命令 skill，不是 workflow skill），默认同时写
  Codex 与 `~/.claude/skills`。
- skills 在 host 启动时加载：装完要重启 Agent host。

## `loopx doctor` 与本 checkout 的已知边界

- **它不是只读的**：会对全局注册表做一次写探针——在 `~/.codex/loopx/registry.global.json` 旁边
  写一个临时文件再删掉；若 `~/.codex/loopx` 不存在会先创建该目录（目录会留下，探针文件不会）。
- 它**只扫 `~/.codex/skills` 与 `~/.agents/skills`，不扫 `~/.claude/skills`**；只给 Claude 装 skill，
  doctor 仍会报 skills 缺失。
- editable 安装永远不会被识别为 `python_distribution`（PEP 660 的 RECORD 里没有 `loopx/doctor.py`），
  所以 `## Install Freshness` 段的 `install_kind` 恒为 `release_or_checkout`。**容易混淆的是同一段的
  `status`——本 checkout 上它是 `live_checkout`**（判据是"当前命令不是带时间戳的发布快照"；该字段
  另有 `missing` / `stale` / `fresh` / `unknown` 等取值）。两者是两个字段，别把 `live_checkout`
  当成 `install_kind` 的取值。
- 本 fork 已把 checkout 场景的升级建议改成**就地刷新命令**：`pip install -e . --no-deps
  --no-build-isolation` + skills 交付 + `loopx doctor`（其中 `--no-build-isolation` 按运行环境
  自适应：解释器里没有 setuptools 时自动去掉，否则那条命令会以 `ModuleNotFoundError` 失败）。
  `loopx update plan` 对 checkout 报同样的命令，且继续 fail-closed：`apply` 为空，绝不 `git pull`、
  绝不安装发布快照。

## 验证各激活层 {#verify-the-active-layers}

一轮升级不会因为某一层退出码为 0 就算完成——包、宿主材料、受管 runtime 与扩展各自可能独立过期。
逐层读回，并且只把读回成功当作那一层的证据：

| 层 | Readback | 成功证明什么 | 未就绪时的恢复 |
| --- | --- | --- | --- |
| 安装 owner 与包 | `loopx update check` | 无变更地识别活动可执行文件、包 owner、新鲜度与下一步动作。 | 遵循报告给出的 owner 命令；不要在同一个环境里混用 editable、pip、pipx 与归档路径。对本 checkout，owner 命令就是上面的就地刷新三连。 |
| 宿主材料 | `loopx --format json doctor` | `skill_delivery.status` 描述活动宿主使用的 workflow-skill 投递。 | 重跑 `loopx workflow-skills --install`（Claude Code 需显式 `--skills-dir ~/.claude/skills`），按需再刷新 `loopx slash-commands --install`，然后重启宿主。 |
| 受管 Effect runtime | `loopx doctor --deep` | 打包的 TypeScript Effect runtime 能启动并应答深度探测；空闲退出的 `stopped` 生命周期仍是健康的。 | 按 doctor 建议处理；不要用第二条 Python 规则路径替代。 |
| 已启用扩展 | `loopx extension doctor --all-enabled --execute --format json` | 每个启用扩展都有当前 runtime 身份并通过就绪检查。 | 修复点名的 provider 或扩展并重跑其 doctor；失败的 provider 保持闭合。 |

`loopx update plan` 对活动源码 checkout 报的就是上面的就地刷新命令，且继续 fail-closed：
`apply` 为空，绝不 `git pull`、绝不安装发布快照。

表中的独立读回随时可以重跑（它们是恢复入口，不是变更动作）：重跑不会改变安装 owner，
对 checkout 而言 owner 恒为源码所有权（Git）。

**发布提醒**：合入 `main` 的代码不等于处于激活状态——对 checkout 而言，
"激活"只由重跑就地安装与 skills 交付保证，见上面的"什么会立即生效、什么需要重装或重建"表。

## 陷阱：cwd 遮蔽 {#cwd-shadowing}

editable finder 被追加到 `sys.meta_path` **末尾**，所以在**包含 `loopx/` 子目录**的目录里运行
`python3 -m loopx.…` 或 `python3 -c "import loopx"` 时，`PathFinder` 会先命中当前目录，import 到的
不是你的安装。验证请统一用 console script `loopx`（它的 `sys.path[0]` 是 bin 目录，不受影响）；
必须用 `python3 -m` 时，在 checkout 根目录运行。
