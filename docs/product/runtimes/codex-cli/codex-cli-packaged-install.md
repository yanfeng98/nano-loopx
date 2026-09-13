# Codex CLI 打包安装路径


状态：本 fork 的就地 editable 路径（PyPI 通道不使用；发布快照 / 归档通道保留给发布与 canary 工作）。

LoopX 应该易于从用户已经打开的工具里接纳。对 Codex CLI 用户而言，第一个成功路径是：

1. 在项目仓库中打开 Codex CLI TUI。
2. 粘贴一条 LoopX 开始消息。
3. 如果 `loopx` 缺失，让 agent 从 LoopX checkout 就地装成 editable 安装并交付 workflow skills。
4. 回到同一个 TUI，带上当前目标、gate、todo 与下一个安全动作。

本 fork 的安装就是 clone 这个仓库并就地装成 editable——不存在需要绕开的门槛，也不走 PyPI wheel
与归档快照通道（后者属发布/canary 工作，见"贡献者路径"）。上游这些通道的原文不再保留在仓库内，
需要对照时用 `git show upstream/main:docs/product/runtimes/codex-cli/codex-cli-packaged-install.md`。

## 当前用户路径

把 checkout 装成 editable 安装（唯一支持的安装方式，见
[就地开发闭环](../../../development/editable-dev-loop.md)）：

```bash
cd <loopx-checkout> && python3 -m pip install -e . --no-deps --no-build-isolation
loopx workflow-skills --install
loopx doctor
```

Wheel 安装 `loopx` CLI 并携带可复用 Codex workflows。`workflow-skills --install` 把丰富的 workflow skills 与受管理的 `$loopx` 入口物化到 `~/.codex/skills`，并带版本化回读。额外的 host 命令门面保持显式，通过 `loopx slash-commands --install` 提供：

- `~/.codex/skills/loopx*/SKILL.md`，用于通过 `$loopx` 或 `/skills` 的显式 Codex command-facade 调用；
- `~/.codex/skills/loopx-project/SKILL.md`，用于在 `/skills` 中显示为 `LoopX Project` 的独立项目 workflow skill；
- `~/.claude/skills/loopx*/SKILL.md`，用于 Claude Code slash-command 发现。

当前验证过的 Codex CLI 构建仍拒绝用户安装的 `/loopx` 与 `/prompts:loopx` 命令，所以本安装路径把 Codex CLI 报告为不受支持的本地 slash surface。对于显式 Codex skill 调用，使用 `$loopx` 或从 `/skills` 选择 `loopx`。对于可见的长程 TUI loop，使用 `loopx codex-cli-bootstrap-message --project .`，把生成的 setup 粘贴进 TUI，然后设置生成的 `/goal <thin task_body>`。

安装修复走同一条就地路径：从 checkout 重跑 editable 安装与 `loopx workflow-skills --install`。
**不要**在就地开发环境里用 `scripts/install-local.sh`——它属发布/canary 通道，会把 checkout 复制成
发布快照并在 `~/.local/bin` 写 wrapper，从而静默接管 editable 安装（见
[就地开发闭环](../../../development/editable-dev-loop.md)的"不要运行这些"表）。

## Codex CLI TUI 消息

Agent 优先的开始消息现在可以更严格地对待安装修复：

```text
Start LoopX for this repo. If `loopx` is missing, set it up from the LoopX
checkout with `cd <loopx-checkout> && python3 -m pip install -e . --no-deps
--no-build-isolation`, run `loopx workflow-skills --install`, then connect this
project. Show me the current objective, concrete user gate if any, top todos,
and next safe action before running longer work. Keep me in this Codex CLI TUI
unless I explicitly accept a headless fallback.
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

更新就是重跑同一条就地刷新命令（`git` 拉取新代码后）：

```bash
cd <loopx-checkout> && python3 -m pip install -e . --no-deps --no-build-isolation
loopx workflow-skills --install
loopx slash-commands --install
loopx doctor
```

`loopx update check` 与 `loopx update plan` 对活动源码 checkout 报的正是这条命令，且继续
fail-closed：`apply` 为空，绝不 `git pull`、绝不安装发布快照。各激活层（包 owner、宿主材料、
Effect runtime、已启用扩展）的逐层读回与恢复见
[验证各激活层](../../../development/editable-dev-loop.md#verify-the-active-layers)。

## 贡献者路径

贡献者就用同一份 checkout：见[就地开发闭环](../../../development/editable-dev-loop.md)。
`scripts/install-local.sh`（→ 发布快照 + `~/.local/bin/loopx-canary`）仍然存在，但**属于发布/canary
工作**，只应在明确要验证发布快照时、在与开发环境隔离的机器或 HOME 里运行；就地开发用它会被静默接管。
上游那篇教程（`git clone huangruiteng/loopx && scripts/install-local.sh`）的原文不再保留在仓库内。

## 未来打包

本 fork 不做通道扩展：没有 PyPI、Homebrew、签名归档或 release manifest 计划
（上游的后续通道设想用 `git show upstream/main:docs/product/runtimes/codex-cli/codex-cli-packaged-install.md` 对照）。
第一个产品胜点保持不变：用户粘贴一条消息就能获得可用的本地控制面。
