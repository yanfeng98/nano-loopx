# Codex CLI Proof-Capture 演示


该演示 bundle 让用户或贡献者在不运行 Codex、不读 session 资料、不动本地 LoopX 状态的情况下彩排可见证明协议。它刻意 fixture-first：命令校验 public-safe evidence 形态，并展示真实 opt-in 证明需要产生的验收决策。

## 文件

- `examples/fixtures/codex-cli-visible-proof/codex-visible-resume-help.public.json`
  建模一个带 `resume [PROMPT]` / `remote-control` 的 Codex CLI surface。
- `examples/fixtures/codex-cli-visible-proof/visible-resume-proof.public.json`
  记录该 surface 的可见、可中断证明。
- `examples/fixtures/codex-cli-visible-proof/runtime-idle-visible-resume.public.json`
  记录该 surface 的新鲜 idle guard。
- `examples/fixtures/codex-cli-visible-proof/codex-same-tui-help.public.json`
  建模一个未来的显式 same-TUI attach 原语。
- `examples/fixtures/codex-cli-visible-proof/same-tui-proof.public.json`
  记录可以晋升 same-TUI 自动化的证明形态。
- `examples/fixtures/codex-cli-visible-proof/runtime-idle-same-tui.public.json`
  记录匹配的 idle guard。

## 彩排当前可能路径

```bash
loopx --format json codex-cli-visible-attach-acceptance \
  --project . \
  --goal-id public-codex-cli-goal \
  --agent-id codex-side-bypass \
  --fixture examples/fixtures/codex-cli-visible-proof/codex-visible-resume-help.public.json \
  --proof-fixture examples/fixtures/codex-cli-visible-proof/visible-resume-proof.public.json \
  --idle-fixture examples/fixtures/codex-cli-visible-proof/runtime-idle-visible-resume.public.json
```

预期决策：

```text
decision: visible_surface_spike_passed_not_same_tui
accepted_for_visible_later_turn: true
accepted_for_same_tui_automation: false
blocker: same_tui_visible_attach_not_proven
```

这是重要的产品区分。可见的 `resume` 或 `remote-control` 路径可以成为有用的证明 spike，但它仍不证明 LoopX 能安全地往同一个打开的 TUI 里加 Turn。

## 彩排未来晋升路径

```bash
loopx --format json codex-cli-visible-attach-acceptance \
  --project . \
  --goal-id public-codex-cli-goal \
  --agent-id codex-side-bypass \
  --fixture examples/fixtures/codex-cli-visible-proof/codex-same-tui-help.public.json \
  --proof-fixture examples/fixtures/codex-cli-visible-proof/same-tui-proof.public.json \
  --idle-fixture examples/fixtures/codex-cli-visible-proof/runtime-idle-same-tui.public.json
```

预期决策：

```text
decision: same_tui_visible_attach_accepted
accepted_for_visible_later_turn: true
accepted_for_same_tui_automation: true
blockers: []
```

该结果仍是验收 packet，不是执行器。之后的驱动必须重跑 quota、重跑新鲜 idle guard、遵守命令边界、写紧凑 evidence 或 blocker，并且只在验证后 spend quota。
