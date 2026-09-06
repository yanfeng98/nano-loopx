# Codex CLI 打包安装路径

> [English](codex-cli-packaged-install.md)

状态：已发布 PyPI 路径，带归档回退。

LoopX 应该易于从用户已经打开的工具里接纳。对 Codex CLI 用户而言，第一个成功路径是：

1. 在项目仓库中打开 Codex CLI TUI。
2. 粘贴一条 LoopX 开始消息。
3. 如果 `loopx` 缺失，让 agent 安装 PyPI 发行版及其打包 workflow skills。
4. 回到同一个 TUI，带上当前目标、gate、todo 与下一个安全动作。

用户不该在了解 LoopX 是否帮助其项目之前被迫克隆这个仓库。

## 当前用户路径

对全新机器，无需手动克隆即可安装发布版：

```bash
python3 -m pip install --upgrade loopx
loopx workflow-skills --install
loopx doctor
```

Wheel 安装 `loopx` CLI 并携带可复用 Codex workflows。`workflow-skills --install` 把丰富的 workflow skills 与受管理的 `$loopx` 入口物化到 `~/.codex/skills`，并带版本化回读。额外的 host 命令门面保持显式，通过 `loopx slash-commands --install` 提供：

- `~/.codex/skills/loopx*/SKILL.md`，用于通过 `$loopx` 或 `/skills` 的显式 Codex command-facade 调用；
- `~/.codex/skills/loopx-project/SKILL.md`，用于在 `/skills` 中显示为 `LoopX Project` 的独立项目 workflow skill；
- `~/.claude/skills/loopx*/SKILL.md`，用于 Claude Code slash-command 发现。

当前验证过的 Codex CLI 构建仍拒绝用户安装的 `/loopx` 与 `/prompts:loopx` 命令，所以打包安装把 Codex CLI 报告为不受支持的本地 slash surface。对于显式 Codex skill 调用，使用 `$loopx` 或从 `/skills` 选择 `loopx`。对于可见的长程 TUI loop，使用 `loopx codex-cli-bootstrap-message --project .`，把生成的 setup 粘贴进 TUI，然后设置生成的 `/goal <thin task_body>`。

当可用的 Python 包环境不可用且需要恢复时，GitHub Pages 归档安装器保持为恢复回退。它有意跳过 `loopx-canary`；想要 canary 的贡献者应克隆仓库并运行 `scripts/install-local.sh`。

## Codex CLI TUI 消息

Agent 优先的开始消息现在可以更严格地对待安装修复：

```text
Start LoopX for this repo. If `loopx` is missing, install it with
`python3 -m pip install --upgrade loopx`, run
`loopx workflow-skills --install`, then connect this project. Show me the
current objective, concrete user gate if any, top todos, and next safe action before
running longer work. Keep me in this Codex CLI TUI unless I explicitly accept a
headless fallback.
```

这保持产品层级清晰：

- 首次运行：一条可见 TUI 消息；
- 安装修复：无需手动克隆；
- 生成的 bootstrap packet：精确的 TUI 粘贴块、无克隆修复命令与免 transcript 验证检查清单；
- 纯复制模式：`codex-cli-bootstrap-message --message-only` 只打印可粘贴的 TUI 块，而默认输出仍是评审 packet；
- smoke bundle：`codex-cli-tui-bootstrap-smoke-bundle` 不启动 Codex、不读 transcript 就验证新仓库安装器、粘贴块、quota guard 与有界写回命令；
- 周期性自动化：单独的动力工作；
- 贡献者开发：clone 加 canary 仍可用。

## 更新路径

对 PyPI 用户，一起升级发行版并刷新 host 资料：

```bash
python3 -m pip install --upgrade loopx
loopx workflow-skills --install
loopx slash-commands --install
loopx doctor
```

通道感知的更新流程对 PyPI 与归档安装都使用显式意图：

```bash
loopx update check
loopx update plan
loopx update apply
loopx doctor
```

更新命令在变更前报告安装 owner。对于 pip 或 pipx PyPI 发行版，apply 把包事务委托给同一环境，然后刷新 skills、slash commands、doctor、已启用扩展与受管理服务。对于归档安装，apply 计划源归档，在 `~/.codex/loopx` 下保留 runtime 状态，并原子刷新可执行文件与 host 资料。它从不动写活跃源码 checkout。

对于正常 GitHub repo/ref 归档源，`update check` 用一次短暂的只读网络探测比较已安装包版本与该精确 ref。离线检查仍报告本地安装健康，并把缺失的远程比较显式化。自定义归档 URL 跳过此比较，而不是猜测其中包含的版本。

归档更新默认使用 `stable` ref。只有当你故意想要 dev/head 刷新而不是 stable 通道时，才使用 `loopx update plan --ref main` 与 `loopx update apply --ref main`。

当本地 wrapper 或发布快照损坏到 `loopx update` 无法运行时，重新运行 curl 安装器仍是修复/回退路径。

## 贡献者路径

对于在 LoopX 上工作的贡献者与注册 peers，继续保持真实 checkout：

```bash
git clone https://github.com/huangruiteng/loopx ~/loopx
~/loopx/scripts/install-local.sh
loopx doctor
loopx-canary doctor
```

该路径同时安装稳定发布 wrapper 与实时 canary wrapper，对晋升前验证本地变更有用。

## 未来打包

PyPI 是当前默认。以后通道可能加入：

- 签名或 checksum 固定的发布归档；
- 面向 macOS 用户的 Homebrew formula；
- 签名的发布清单，报告当前 release id、最新可用 release 与已安装 skill 新鲜度。

不要让这些未来通道阻塞当前 Codex CLI TUI 路径。第一个产品胜点是：用户粘贴一条消息就能获得可用的本地控制面，而无需离开仓库。
