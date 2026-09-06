# Integration Branch 对账


长程仓库工作常常同时存在两个事实:

- 每个 feature 或 fix 留在自己的可审阅分支上;
- 一个本地 integration branch 必须包含每个源分支最新的已审阅形式。

`integration-branch-reconcile` 让第二个事实机器可读。它把有序计划存入被忽略的
`.loopx/` 状态,把当前 refs 与最后一次成功同步 receipt 比较,并通过临时 detached
worktree 对账 integration branch。

## 配置

```bash
loopx integration-branch configure \
  --repo-path . \
  --base-ref origin/main \
  --integration-branch codex/local-integration \
  --source-branch codex/feature-a \
  --source-branch codex/fix-b \
  --execute \
  --format json
```

源顺序是重要的。`configure` 校验所有 refs,但只写 `.loopx/integration-branch.json`。
已存在的不同计划需要显式 `--replace`,它同时清除旧的同步 receipt。

备选的 `--plan-file` 仍必须解析到仓库 `.loopx/` 状态根之下。该根之外的路径、
traversal 与 symlink 逃逸会 fail closed。选中的路径还必须是 untracked 且被仓库
ignore 规则覆盖,以保证报告的本地 ignored-state 边界成立。

## 检测 review 漂移

```bash
loopx integration-branch status --repo-path . --format json
```

首次 status 是带 `never_synced` 的 `drifted`。成功后,LoopX 记录确切的 base、
source 与 integration SHAs。之后的 rebase、review 修复或额外 source commit 会成为
`base_ref_moved`、`source_ref_moved` 或 `integration_head_changed`。

Remote-tracking refs 直到 Git 观测到发布者的更新才会移动。要让该观测成为同一
typed 操作的一部分,选择一次 remote 只读刷新:

```bash
loopx integration-branch status \
  --repo-path . \
  --refresh-remotes \
  --format json
```

LoopX 只 fetch 配置的 base 或 source refs 点名的 remote-tracking refs,加上
integration branch 配置的 upstream(当存在时),然后解析精确 SHAs。它不清理无关
refs,也不替代现有 `FETCH_HEAD` 证据。这观测另一个 worker 的已发布分支意图;
它不猜测未推送工作、不读取私有 review 文本,也不推断 draft 已被批准集成。

## 预览与同步

```bash
loopx integration-branch sync --repo-path . --format json
loopx integration-branch sync \
  --repo-path . \
  --refresh-remotes \
  --execute \
  --format json
```

首次同步后,只推进到后代分支的源分支,会被合并到上次验证的 integration head。
这保留早期 merge 与冲突解决决策,同时并入已审阅的更新。如果 base、源集合、
integration head 或源血缘不再匹配 receipt,LoopX 从已解析 base 与所有源 SHAs 按
顺序重建。Preview 移除其临时 worktree,不改变 refs。Execute 只在每个 merge 都
成功后更新本地 integration branch,然后写入并重读 receipt。

重建 merge commits 会在 preview 与 execute 之间改变 `candidate_sha` 时间戳。
比较 `candidate_tree_sha` 获得稳定的内容身份;execute 也会把它记入 receipt。

即使 integration branch worktree 是脏的,Preview 也保持只读。Execute 需要干净的
已检出 integration worktree。脏 worktree、merge 冲突、缺失 ref 或并发
plan/input/integration 移动,会在候选发布前 fail closed。

当有序源 heads 需要有意的手工冲突解决时,在 LoopX 之外构建并验证该 commit,然后
让 LoopX 通过同一 receipt 边界验证并采纳它:

```bash
loopx integration-branch sync \
  --repo-path . \
  --candidate-ref <resolved-commit> \
  --format json
loopx integration-branch sync \
  --repo-path . \
  --candidate-ref <resolved-commit> \
  --execute \
  --format json
```

提供的 commit 必须把配置的 base、每个精确源 SHA 与任何观测到的 integration
upstream head 作为祖先包含。LoopX 不选择或生成解法;它只在正常本地发布与回读流程
之前验证不可变结果。

当提供的 commit 已经是 integration branch head 时,execute 只记录已验证 receipt。
它不 reset 或以其他方式触碰已检出的 worktree。

## 周期性或有事件驱动的对账

对 timer 驱动与 provider-event 驱动检查使用同一命令:

```bash
loopx integration-branch sync \
  --repo-path . \
  --refresh-remotes \
  --execute \
  --format json
```

对于 LoopX 管理的工作,把该操作注册为带项目选择 cadence 与 `next_due_at` 的
`continuous_monitor` Todo。Host 可以按 deadline 唤醒、运行命令并写回返回的精确
SHA 证据。Git provider webhook 可以在 ref 事件后调用同一命令以获得更低延迟。
Webhook 认证与事件投递属于 provider extension,不属于这个 repository-neutral
capability。

## 边界

Capability 保持刻意狭窄的写边界:

- 默认不联系 remotes;`--refresh-remotes` 对远程仓库只读,只更新配置的 base、
  source 与 integration-upstream remote-tracking refs;
- 从不 push;
- 从不更改源分支;
- 从不创建、改目标、批准或合并 PR;
- 从不更新受保护的 base branch;
- v0 使用有序 merge commits,不 squash 也不重写源 history。

没有 `--refresh-remotes` 时,在运行 `status` 或 `sync` 之前,通过仓库的正常工作流
fetch 或更新源 refs。人类审查与聚合 merge authority 保持在本 capability 之外。

## 验证

```bash
python3 examples/integration-branch-cli-smoke.py
python3 -m pytest -q tests/capabilities/test_integration_branch.py
```

公开 CLI smoke 与 focused pytest 覆盖被忽略的 plan 状态、只读预览、有序源更新、
已审阅候选采纳,以及本地-only 的 fail-closed 脏/冲突 case。它们不 fetch、push、
重写源分支,也不改变受保护 base。
