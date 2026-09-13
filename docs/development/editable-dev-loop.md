# 就地开发闭环（Editable Dev Loop）

本页描述**本 fork 唯一支持的开发方式**：把这个 checkout 装成 editable 安装，改完就地验证。
它替代了上游的安装叙述——上游的 PyPI / pipx / 归档快照通道在本 fork 不使用，原文保留在
[安装 LoopX](../guides/installing-loopx.md) 仅供合并上游时对照。

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
- 验证三件事：

```bash
loopx version                                   # 期望 1.0.0
python3 -m pip show loopx | grep -i editable    # 应指向 <checkout>
command -v loopx                                # 应是 <python-env>/bin/loopx
```

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
| 新增**带 `__init__.py`** 的子包 | **无** | 子模块走常规 import |
| 新增**不带 `__init__.py`** 的 namespace 目录 | 重装 editable | editable finder 的命名空间表是安装时静态枚举的 |
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
  所以 `install_kind` 恒为 `live_checkout`。
- 本 fork 已把 checkout 场景的升级建议改成**就地刷新命令**：`pip install -e . --no-deps
  --no-build-isolation` + skills 交付 + `loopx doctor`（其中 `--no-build-isolation` 按运行环境
  自适应：解释器里没有 setuptools 时自动去掉，否则那条命令会以 `ModuleNotFoundError` 失败）。
  `loopx update plan` 对 checkout 报同样的命令，且继续 fail-closed：`apply` 为空，绝不 `git pull`、
  绝不安装发布快照。
- 会看到但**应忽略**：`loopx bootstrap` 的 `install_repair_command` 是面向上游包通道的静态字符串。

## 陷阱：cwd 遮蔽

editable finder 被追加到 `sys.meta_path` **末尾**，所以在**包含 `loopx/` 子目录**的目录里运行
`python3 -m loopx.…` 或 `python3 -c "import loopx"` 时，`PathFinder` 会先命中当前目录，import 到的
不是你的安装。验证请统一用 console script `loopx`（它的 `sys.path[0]` 是 bin 目录，不受影响）；
必须用 `python3 -m` 时，在 checkout 根目录运行。

## 不要运行这些（会替换或复制你的开发环境）

| 命令 | 后果 |
| --- | --- |
| `scripts/install-local.sh` | 把 checkout 复制成 `~/.local/share/loopx/releases/<id>` 发布快照，并在 `~/.local/bin` 写 wrapper。**实测本机 `PATH` 里 `~/.local/bin` 排在最前**，于是 `loopx` 被静默接管 |
| `curl -fsSL https://huangruiteng.github.io/loopx/install.sh \| bash` | 同上，且装的是上游发布版 |
| `python3 -m pip install --upgrade loopx`、`pipx install loopx` | 往同一解释器装 PyPI 发布版，覆盖 editable 指向 |
| 把 `LOOPX_RELEASE_ROOT` 指向某个 release 目录 | 让 doctor 误判安装形态 |
| 仓库根的 `npm run test:control-plane`、`typecheck:control-plane` | 需要根 `node_modules`（未安装）。只验单个 TS 测试用 `node --no-warnings --experimental-strip-types --test tests/control_plane_ts/<file>.test.ts`（`postgresql_authority_store.integration.test.ts` 需真实 PostgreSQL） |

若已经误跑：删掉 `~/.local/bin/loopx` 与 `loopx-canary`，检查 shell profile 里的
`export PATH="$HOME/.local/bin:$PATH"`，并用 `loopx workflow-skills --uninstall --skills-dir <root>`
回收 skill 副本。

## 与上游合并

本页、README 的试用段、`CONTRIBUTING.md` 的本地开发段、`docs/guides/getting-started.md` 的贡献者
安装段都是 fork 版本；合并上游时以本 fork 版本为准（上游会带回 PyPI 安装叙述）。
`docs/guides/installing-loopx.md` 保留上游原文并加偏差标注，便于对照。
