# 安装 LoopX

**本 fork 偏差（2026-09-07 起的 fork 决策）：本页余下内容描述上游的 PyPI / pipx / 归档
快照发布通道；本 fork 的日常开发不使用它，而是把 checkout 就地装成 editable 安装。就地
开发闭环见[就地开发闭环](../development/editable-dev-loop.md)。合并上游时保留本段说明。**

本 fork 的就地开发安装：

```bash
cd <checkout>
python3 -m pip install -e . --no-deps --no-build-isolation
loopx workflow-skills --install                                  # Codex CLI，默认根 ~/.codex/skills
loopx workflow-skills --install --skills-dir ~/.claude/skills    # Claude Code 必须显式指定
loopx doctor
```

---

以下为上游原文。

PyPI 是 LoopX 的默认发布通道。在激活的虚拟环境、受管的用户环境或另一个 console
脚本已位于 `PATH` 上且使用 Python 3.11 及更高版本的环境中安装：

```bash
python3 -m pip install --upgrade loopx
loopx workflow-skills --install
loopx doctor
```

选择一个安装 owner 并保持其权威：

| 使用场景 | Owner | 安装或获取 | 升级 |
| --- | --- | --- | --- |
| 常规发布 | Python 包环境 | `python3 -m pip install loopx` | `loopx update apply` 或下面的手动 pip 序列 |
| 在外部管理的机器上的隔离 CLI | `pipx` | `pipx install loopx` | `pipx upgrade loopx`，然后刷新 LoopX 宿主材料 |
| 贡献者或源码资格验证 | Git checkout | clone/fetch 加 `scripts/install-local.sh` | 显式更新 checkout、重跑安装器、在晋升前验证 `loopx-canary` |
| 无需 clone 的恢复回退 | LoopX 归档快照 | 已发布的归档安装器 | `loopx update apply` |

PyPI 是常规发布的规范来源。源码 checkout 是开发与资格验证界面，不是第二个隐式
包通道。归档快照仍是恢复路径，而不是竞争性默认项。

LoopX 的 Effect Program 核心运行在一个受管、空闲即退出的 TypeScript runtime 中，
要求 Node.js 22.6 或更高。LoopX 自动启动并复用该本地 runtime；用户不需要手动运行
daemon。该 runtime 只绑定 loopback，用用户私有 token 认证请求，在打包的 Effect
core 变化时轮换，并在空闲一段时间后退出。`loopx doctor` 将其报告为 `ready`、
`missing`、`unsupported` 或 `probe_failed`；缺失或过期的 runtime 会 fail closed，
而不是回退到第二个 Python 规则引擎。同一 doctor 投影把 `runtime_lifecycle.state`
暴露为 `running`、`stopped` 或 `unavailable`，外加一个公开安全的
`diagnostic_code`；App 可以直接渲染该投影，无需发明第二套健康模型。`stopped` 是
健康状态，表示空闲退出的 runtime 会在下一次控制面请求时重启。安装或升级 LoopX
前验证 Node：

```bash
node --version
# v22.6.0 or newer
```

安装后使用 `loopx doctor --deep` 启动受管 runtime，并演练打包的 Effect 语义与
原生 journal 检查点处理器。`workflow-skills --install` 把打包的 LoopX workflow
skills 复制到用户的 Codex skill 目录并写入 revision readback；它不改变项目状态，
也不授予仓库、网络或 merge 权限。首次安装后重启宿主，让它重新加载新 skills。

如果机器上 Python 包受外部管理，使用专用工具环境，而不是修改系统解释器：

```bash
pipx install loopx
loopx workflow-skills --install
loopx doctor
```

## 宿主命令界面

workflow-skill 命令安装丰富的 Codex workflows 与受管 `$loopx` 入口。只为需要它们的
宿主安装额外的命令 facade：

```bash
loopx slash-commands --install
```

默认命令 facade 集合覆盖 Codex 与 Claude Code。其他界面保持显式；启用前
检查 `loopx slash-commands --help`。宿主集成只改变命令发现方式。它不授予 LoopX
写仓库、联系外部系统或绕过用户 gate 的权限。

## 升级与修复

`loopx update` 是通道感知的升级入口。其动作对人与 agent 具有相同含义：

```bash
loopx update check       # read-only freshness and installation-owner check
loopx update plan        # read-only command, validation, and rollback plan
loopx update apply       # explicit local-environment mutation
```

archive 安装时，`update apply` 会先把 bootstrap 安装器下载到私有临时文件再执行。
下载限制为三次尝试、60 秒总下载预算（或更小的命令超时）与每次传输 20 秒，
重试间隔为 1 秒和 2 秒。瞬态 403/408/429/500/502/503/504 响应与选中的连接／传输
失败会重试；401/404 与证书校验失败会立即停止。安装器执行从不重试，部分下载从不执行。
命令超时同时覆盖下载与安装器执行。

JSON `execution.installer_download` 与文本执行报告显示阶段与每次尝试的 HTTP 状态和
curl 退出码。HTTP `0` 表示未收到可用 HTTP 状态。下载诊断排除 URL、响应体、请求头与
原始 curl 错误，以免代理凭据与签名参数泄漏。这些重试只覆盖 bootstrap 下载，不覆盖
后续 archive 下载或失败安装。Pip/pipx 与只读计划保持原有行为。

裸 `loopx update` 仍是只读计划。较旧的 `--check`、`--dry-run` 与 `--execute`
拼写仍作为兼容别名保留，但新指令应使用命名动作。

人类可读输出以 **No update was applied** 和一个可复制的 **Next Action** 命令开头。
JSON 输出把同一决策暴露为 `requested_action`、`changes_applied` 与一个带 mutation
和 explicit-approval 字段的 typed `next_action` 对象。Agent 应检查这些字段，而不是
从散文推断权威。

对于由 pip 安装的 PyPI 发行版，`update apply` 要求拥有 LoopX 的那个确切 Python
解释器升级其环境，然后启动新进程安装 workflow skills 与 slash commands、运行
doctor、重新验证已启用的扩展，并重启受管的本地 LoopX 服务。它不把安装切换到归档
快照。

等效手动序列：

```bash
python3 -m pip install --upgrade loopx
loopx workflow-skills --install
loopx slash-commands --install
loopx doctor
```

第一条命令是包事务；其余命令是 LoopX 激活与 readback 契约。只运行 `pip install`
可能让上一版本的宿主材料保持激活。反之，`loopx update apply` 不取代 pip 作为
依赖解析、环境策略、包索引或卸载的 owner。

### 验证各激活层 {#verify-the-active-layers}

升级不会因为包管理器步骤成功退出就算完全合格。逐一读取可能独立过期的每一层：

| 层 | Readback | 成功证明什么 | 未就绪时的恢复 |
| --- | --- | --- | --- |
| 安装 owner 与包 | `loopx update check` | 无变更地识别活动可执行文件、包 owner、新鲜度与下一步动作。 | 遵循报告的 owner 命令；不要混用 pip、pipx、归档与源码 checkout 升级路径。 |
| 宿主材料 | `loopx --format json doctor` | `skill_delivery.status` 描述活动宿主使用的 workflow-skill 投递。 | 运行 `loopx workflow-skills --install`；使用这些 facade 时刷新 `loopx slash-commands --install`，然后重启宿主。 |
| 受管 Effect runtime | `loopx doctor --deep` | 打包的 TypeScript Effect runtime 能启动并应答深度探测。空闲退出的 `stopped` 生命周期仍是健康的。 | 应用 doctor 建议或重装所选包版本；不要用第二条 Python 规则路径替代。 |
| 已启用扩展 | `loopx extension doctor --all-enabled --execute --format json` | 每个启用扩展都有当前 runtime 身份并通过就绪检查。 | 修复点名的 provider 或扩展并重跑其 doctor；失败的 provider 保持闭合。 |

在拥有包或归档更新成功后，`loopx update apply` 运行宿主材料刷新、核心 doctor 与
已启用扩展 doctor。上面的独立命令作为独立 readback 与恢复入口仍有用；重跑它们
不会改变安装 owner。

这些检查也防止一个常见的发布错误：合入 `main` 的代码不一定在已安装的发布里处于
激活状态。归档维护者可以用 `loopx update check --ref main` 检查
`runtime_activation_qualification`；普通 pip 与 pipx 用户应留在打标签的包通道上，
等待对应发布，而不是尝试把已安装的发行版切换到 `main`。

对于由其他 Python 包管理器拥有的安装，`update plan` 报告该 owner 及其命令；
LoopX fail closed，而不是猜测 pip 变更。对于活动源码 checkout，它报告**就地 editable
刷新命令**（`pip install -e . --no-deps --no-build-isolation` 加宿主材料刷新），**不**报告
`scripts/install-local.sh` 或归档安装器，也绝不执行 `git pull` 或改写工作区。源码获取与
仓库变更始终是显式的人类或授权 Agent 动作。**（本 fork 偏差，上游为报告贡献者安装器。）**

`loopx doctor` 对这条路径报告 `install_kind: python_distribution`，并在打包
skills 缺失或过期时返回同一 pip 原生修复序列。它还验证控制面升级被视为健康之前
所需的 TypeScript Effect runtime。Runtime 元数据由已安装源码做指纹，因此升级后的
LoopX 启动匹配进程，而旧进程在空闲后退出。当发布需要回滚时，重装先前选择的
版本、刷新打包宿主材料并再次验证：

```bash
python3 -m pip install "loopx==<previous-version>"
loopx workflow-skills --install
loopx slash-commands --install
loopx doctor
```

## 归档回退

GitHub Pages 安装器仍是回退方案，用于没有合适 Python 包环境、或 CLI 损坏到无法
运行自身修复路径的机器：

```bash
curl -fsSL https://huangruiteng.github.io/loopx/install.sh | bash
export PATH="$HOME/.local/bin:$PATH"
loopx doctor
```

该回退把归档快照、wrapper、man page 与宿主材料一起安装。LoopX 拥有该快照的
生命周期，因此其更新路径是：

```bash
loopx update check
loopx update plan
loopx update apply
```

归档 apply 保留原子发布指针、doctor 验证、扩展 readback、受管服务重启与一等
快照回滚。安装 owner 投影防止该路径与活动 PyPI 可执行文件混用。

## 卸载

先移除 LoopX 拥有的宿主材料，再卸载 Python 包：

```bash
loopx slash-commands --uninstall
loopx workflow-skills --uninstall
python3 -m pip uninstall loopx
```

两个宿主卸载器都保留 LoopX 安装后内容被修改过的同名文件。项目本地的 `.loopx/`、
`.codex/goals/`、证据与 runtime 状态不会被包卸载删除。

需要在线 canary 的贡献者应使用真实 checkout 与 `scripts/install-local.sh`（**就地开发不需要
它**，见[就地开发闭环](../development/editable-dev-loop.md)）；见
[开始使用](getting-started.md)。
