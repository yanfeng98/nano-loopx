# Codex CLI


Codex CLI 是头等 LoopX host。首选产品路径以一条可见 TUI 消息开始;headless 执行保持为显式回退或有界合作伙伴路径,而非默认用户体验。

## 开始与安装

- [TUI 优先的 LoopX Loop](codex-cli-tui-loop.md):一条可见 TUI 消息启动 LoopX,以会话附加自动化作为首选后续。
- [打包安装](codex-cli-packaged-install.md):PyPI 安装、更新与开始路径;clone-plus-canary 仍是贡献者路由。
- [首次运行演练](codex-cli-first-run-rehearsal.md):连接 PyPI 安装、单消息 TUI 引导与证明捕获 fixture。
- [无 clone 发布验证](codex-cli-no-clone-release-verification.md):证明安装器、引导消息、bundle 与证明 fixture 保持一致。
- [LoopX Turn 快速开始](loopx-turn-codex-cli-quickstart.md):带一个适配器、一个验证器、一条命令与类型化结果的有界隔离 headless 路径。

## 可见会话 evidence

- [Codex CLI 实时 TUI 首条消息试点](codex-cli-live-tui-first-message-pilot.md):记录在可见完成被证明之前,为何手工粘贴仍是主要方式。
- [可见证明捕获协议](codex-cli-visible-proof-capture-protocol.md):把 `resume` 或 `remote-control` 信号转化为公开安全 evidence 的选择加入流程。
- [可见附加证明试点](codex-cli-visible-attach-proof-pilot.md):证明已恢复会话正是预期会话的有界验收路径。
- [证明捕获演示](codex-cli-proof-capture-demo.md):不运行 Codex 或读取会话材料的示例 fixture 与验收决策。
- [同开 TUI 延续观察](codex-cli-same-open-tui-continuation-observation.md):可见首个 Turn 延续的当前 evidence 与剩余的调度附加边界。

Codex CLI 有界可见试点适配器是由 `examples/codex-cli-bounded-visible-pilot-adapter-smoke.py` 覆盖的公开安全包命令。它先校验首响应与运行时空闲 fixture,然后实时 TUI 引导才能算成功。

Codex CLI 可见首响应捕获计划是由 `examples/codex-cli-visible-first-response-capture-plan-smoke.py` 覆盖的复制优先包命令。它在无 argv 提示泄漏或原始转录读取的情况下产生 `public-first-response.json` 与 `public-runtime-idle.json`。

## 调度与自动化

- [自动化驱动审计](codex-cli-automation-driver.md):保持 TUI 引导为主,组合配额/空闲/回退检查,并把 `codex exec` 视为显式回退。
- [TUI 延续优先级](codex-cli-tui-continuation-priority.md):当两者都可运行时,保持同一开 TUI 延续领先于 frontstage 或 showcase 支持工作。

稳定的 host 与 turn schema 位于
[`docs/reference/protocols/`](../../../reference/protocols/README.md)。
