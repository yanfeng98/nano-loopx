# Codex CLI 首次运行彩排


状态：产品路径与发布彩排。

LoopX 应该先让人觉得简单，再让人觉得强大。初次使用 Codex CLI 的用户应当能留在 TUI 里、粘贴一条消息，然后看到当前 goal 状态、gates、todos 与下一个安全动作，而无需先克隆这个仓库或阅读 LoopX 内部。

该路径连接三个已发布的 surface：

1. PyPI 安装/更新，带打包 workflow skills 与归档兜底；
2. 一条消息的 Codex CLI TUI 引导；
3. 供之后可见自动化使用的 proof-capture 夹具。

## 新用户路径

在用户的项目仓库中：

1. 打开 Codex CLI TUI。
2. 粘贴一条开始消息：

   ```text
   Start LoopX for this repo. If `loopx` is missing, install it from PyPI,
   install the packaged workflow skills, then connect this project. Show
   me the current goal, concrete user gate if any, top todos, and next safe
   action before running longer work. Keep me in this Codex CLI TUI unless I
   explicitly accept a headless fallback. After I paste this, begin the Goal
   Harness loop; do not stop after only explaining what LoopX is.
   ```

3. Agent 在需要时安装或修复 LoopX，使用：

   ```bash
   python3 -m pip install --upgrade loopx
   loopx workflow-skills --install
   loopx doctor
   ```

4. Agent 连接仓库、运行 quota/status、呈现任何具体 user gate，然后如果 guard 允许就启动一个有边界的验证片段。

用户的第一个有用响应应当一屏装下：

- 当前 goal id；
- user gate，或没有；
- 首要 user todo，或没有；
- 首要 agent todo；
- 下一个安全动作。

## 安装之后

一旦 `loopx` 在 PATH 上，生成更严格、项目特定的 TUI 消息：

```bash
loopx codex-cli-bootstrap-message --project . --goal-id <goal-id> --message-only
```

用于不运行 Codex、不读 session 资料的发布彩排：

```bash
loopx codex-cli-tui-bootstrap-smoke-bundle \
  --project . \
  --goal-id <goal-id> \
  --agent-id <agent-id>
```

该 bundle 检查安装-修复命令、粘贴块、quota guard、有界写回与 spend 命令形态。它不是首次用户步骤。在晋升前验证打包安装器与新建项目命令 surface 与该路径一致时，使用
[无克隆发布验证](codex-cli-no-clone-release-verification.md)。

## 后续自动化 gate

在证明路径通过之前，Same-TUI 自动化保持可选。调度器只有在以下全部为真时才能回到 Codex CLI：

- visible-session 证据 public-safe 并被接受；
- runtime idle 证据新鲜；
- quota/status guard 仍允许选中工作；
- 命令边界显式；
- 校验在 spend 之前写入紧凑 evidence 或 blocker。

用公开夹具彩排证明路径：

```bash
loopx --format json codex-cli-visible-attach-acceptance \
  --project . \
  --goal-id public-codex-cli-goal \
  --agent-id codex-side-bypass \
  --fixture examples/fixtures/codex-cli-visible-proof/codex-visible-resume-help.public.json \
  --proof-fixture examples/fixtures/codex-cli-visible-proof/visible-resume-proof.public.json \
  --idle-fixture examples/fixtures/codex-cli-visible-proof/runtime-idle-visible-resume.public.json
```

这一当前可能路径可以作为可见的后续-Turn spike 通过，但它仍未证明 same-open-TUI 自动化。在 same-TUI attach 证据被接受之前，产品路径保持为一条消息的 TUI 引导加显式回退。

## 实时 TUI 试点说明

第一个真实的
[实时 TUI 首消息试点](codex-cli-live-tui-first-message-pilot.md)
确认生成的消息可以通过 `codex [PROMPT]` 启动 Codex CLI，但未证明 LoopX loop 成功启动。进程保持活跃，没有有界的首响应标记可用，而且在真实仓库中把消息作为 argv 传递会把项目特定的 prompt 文本泄露到进程命令行。

所以可靠的首次运行路径仍是在可见 Codex CLI TUI 中手动粘贴。自动化实时启动需要先有有界的可见完成证据。

## 边界

该首次运行路径不得：

- 要求克隆 LoopX 仓库；
- 把 Codex 作为彩排 bundle 的一部分启动；
- 读取原始 Codex transcript、session 文件、stdout、stderr、凭据或私有路径；
- 在验证写回之前 spend LoopX quota；
- 把 headless `codex exec` 当作默认用户体验；
- 在没有可见证据与 idle evidence 的情况下晋升 same-TUI 自动化。

参见：

- [Codex CLI 打包安装路径](codex-cli-packaged-install.md)
- [Codex CLI TUI-first loop](codex-cli-tui-loop.md)
- [Codex CLI proof-capture 演示](codex-cli-proof-capture-demo.md)
