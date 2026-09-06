# Repository Change Window 能力介绍


`repository-change-window` 是一个内置、默认关闭的 capability，服务两种相关的
调用方结果：

1. 在仓库 commit 和 push 之前，应用一个类型化的本地时间表；以及
2. 当该时间表阻塞交付时，保留一份重启安全的未合并工作清单。

该 capability 拥有策略评估与待变更生命周期。捆绑的 `git-hook` provider
拥有 Git 集成。LoopX Kernel 仍是 Goal、todo、gate 和 quota 的权威；安装此
provider 不会授予仓库写入或 remote-write 权威。

## 安装与检查

每个变更型命令默认先预览。下述内置时间表在 `Asia/Shanghai` 时区下阻挡
周一至周五 10:00（含）至 21:00（不含）：

```bash
loopx change-window install --repo-path . --format json
loopx change-window install --repo-path . --execute --format json

loopx change-window status --repo-path . --format json
loopx change-window verify --repo-path . --format json
```

在仓库 provider 存在之前，`status` 上报两种类型化状态之一：

- 当 `core.hooksPath` 与 `core.sshCommand` 都没有提供生效的已配置守卫时，报
  `provider_not_installed`；或
- 当任一表面已配置时，报 `effective_external_guard_detected`。

外部守卫诊断只包含表面与配置作用域枚举。它绝不返回 hook 路径或命令、不推断
时间表，也不把任意脚本当作可信 provider 状态。一个有界的签名可以识别早期
LoopX 全局 commit 时点 gate，并提供类型化、先预览的 repository-provider 迁移。
该预览叠加仓库 provider、保留生效的全局守卫，且不修改全局 Git 配置。未知的
外部守卫保持仅诊断并 fail closed。

安装默认采用向后兼容的 `hook_only` 强制级别。它管理 `pre-commit` 与
`pre-push`；Git 的 `--no-verify` 选项可以跳过这些客户端 hooks。想要更强本地
守卫的仓库必须显式选择：

```bash
loopx change-window install \
  --repo-path . \
  --enforcement-level reference_guard \
  --execute \
  --format json

loopx change-window verify --repo-path . --format json
```

`reference_guard` 额外管理 Git 的 `reference-transaction` hook 与仓库本地的
`core.sshCommand` 路由。在受阻窗口内，它拒绝引入新 commit 的 `HEAD` 或本地分支
更新，包括 `git commit --no-verify`。`pre-push` hook 覆盖普通 push，而 SSH 路由
还会拒绝使用 `--no-verify` 的 SSH push。Checkout、链接 worktree 创建、分支删除、
SSH fetch，以及在另一本地分支或当前 `HEAD` 已可达的 commit 上创建本地分支，
仍然可用。Tags、notes 和自定义 refs 不会让新 commit 在受阻窗口内具备本地分支
更新的资格。未知的 SSH service 命令 fail closed。`status` 与 `verify` 上报类型化
的强制级别、精确的受管 hook 集合与 SSH 路由健康。

用可重复的星期几与 IANA 时区数据自定义一个类型化 v0 窗口：

```bash
loopx change-window install \
  --repo-path . \
  --timezone Europe/Berlin \
  --blocked-weekday mon \
  --blocked-weekday tue \
  --blocked-start 09:30 \
  --blocked-end 18:00 \
  --execute \
  --format json
```

结束早于开始即为与起始日关联的隔夜窗口。起止相等会被拒绝，而不是被解释为
隐式的全天锁定。

该 provider 只写仓库本地 Git 配置与仓库 Git common 目录下的私有状态。因此链接的
worktrees 共享同一套安装与策略。受管 hooks 先评估策略，再以安装前生效的路由调用
同名 hook（包括 stdin 与 hook 参数）。SSH 守卫委托给此前生效的
`core.sshCommand`，未配置时委托给 `ssh`。受管命令被修改、hook 或 SSH 路由变更、
策略无效、或状态缺失，都会使 verify 校验失败关闭（fail closed）。

在 CLI 组合根处，该 capability 注册一个有界、只读的 `interaction_projection`
hook。Kernel 编排在类型化 TypeScript 边界校验注册与候选、隔离 provider 失败，
并在不导入本 capability 的前提下拒绝写作用域或冲突的投影槽位。当 provider 已安装
且所有 provider 检查通过时，`quota should-run` 会加入
`interaction_contract.repository_delivery`。该投影让 `prepare_dirty_worktree`
与 `validate_dirty_worktree` 继续由本地时间表接纳，同时把 `commit` 与 `push`
与已校验的策略决策分开投影。受阻的决策带有 `next_eligible_at`。未安装、
仅外部或已漂移的 provider 不会产生可信的 repository-delivery 接纳。该投影
无路径、跨链接 worktrees 共享、不扩展到独立 clone，且绝不授予 remote-write
权威或覆盖其他 LoopX gate。

这是一个读取时投影 hook，不是 effect 回调：它只接收无路径的 provider 状态
候选，每次调度最多运行一次，不能写 Git 配置、创建 commit、push 或 merge。
未来的 post-writeback hook 使用独立的 durable-receipt 与幂等契约；本注册不会
隐含获得该生命周期。

执行时钟不是调用方参数。活动 hooks 使用调用时钟；测试通过 Python 契约注入
感知时钟的假时钟，因此工件时间戳无法把 commit 或 push 移进允许窗口。

## 待变更台账

当 hook 阻止 commit 或 push 时，它会自动记录或刷新一条稳定的、按 checkout
作用域的待变更记录。已检出分支保留其原有身份；分离头（detached）的 worktree
获得一条无路径、机器本地的 checkout id，因此变更窗口期间准备的工作无需创建
分支即可恢复。共享的运行时事件包含：

- 稳定的 `change_id` 与免凭据的仓库身份；
- 类型化的 `branch` 或 `detached` checkout 身份与精确的 head OID；
- staged、unstaged 与 untracked 状态的计数和内容摘要；
- 类型化的 gate 决策与下一次可执行时间；以及
- 生命周期来源与更新时间。

它**不**包含代码、patch、diff 正文、凭据材料、文件名或本地绝对路径。一条独立的
mode-`0600` 机器私有定位器（locator）保留产生该工作的 worktree 及其仓库相对的
变更路径清单；list、reconciliation 与 verification 数据包只暴露计数，绝不暴露
那些路径。

在可用时显式附带 Goal、todo、PR、write-scope 与校验世系（lineage）：

```bash
loopx change-window record \
  --repo-path . \
  --goal-id example-goal \
  --todo-id todo_example123 \
  --write-scope 'src/**' \
  --validation-ref 'pytest:tests/unit:passed' \
  --execute \
  --format json

loopx change-window list --state open --format json
loopx change-window verify --change-id change_example123 --format json
```

一个 hook 只能观察到一次被尝试的 Git 操作。因此在受阻窗口内准备的工作可能保持
dirty，而未到达 `pre-commit`、`reference-transaction` 或 `pre-push`。在正常
writeback 期间对当前 checkout 做对账，或是在更广泛的手工交接之前，显式清扫同一
Git common 目录下的每一个链接与分离 worktree：

```bash
loopx change-window reconcile --repo-path . --format json
loopx change-window reconcile --repo-path . --execute --format json
loopx change-window reconcile \
  --repo-path . \
  --all-linked-worktrees \
  --execute \
  --format json
```

当策略允许仓库变更时，对账是 no-op，且要求已安装 provider。有界的默认形式只检查
`--repo-path`；`--all-linked-worktrees` 是显式的仓库级恢复清扫。两者都忽略干净
worktree、幂等地记录 dirty checkout，且只返回无路径的 checkout id 与计数。在准备好
受阻工作后运行有界形式，在交接、关闭或 gate 打开交付通道之前运行更宽的清扫。
宽清扫输出保持聚合计数权威，并对每个 checkout 的详情设上限，避免大型历史
worktree 集合淹没控制数据包。

同一身份与指纹下 `record` 是幂等的。head 变更、路径清单变更或 worktree 指纹
变更会追加一条 `refreshed` 事件，而不是覆盖历史。`verify` 区分缺失
locator/worktree、仓库或 checkout 不匹配、未记录的 head、分支或分离 HEAD 移动、
私有变更路径清单漂移，以及 worktree 指纹漂移。Verification 只上报清单计数，
绝不暴露私有路径值。

仅以类型化结果与紧凑的公开安全证据关闭生命周期：

```bash
loopx change-window resolve \
  --change-id change_example123 \
  --resolution merged \
  --evidence 'github:owner/repo#123' \
  --execute \
  --format json
```

终态结果是 `merged`、`superseded` 与 `abandoned`。`superseded` 还要求
`--superseded-by`。精确重试幂等；冲突的终态证据 fail closed。Resolve 保留
公开安全的事件历史，并移除不再需要的机器私有 worktree locator。

## 卸载与回滚

先预览，再移除受管 provider：

```bash
loopx change-window uninstall --repo-path . --format json
loopx change-window uninstall --repo-path . --execute --format json
```

卸载会恢复安装前存在的精确仓库本地 `core.hooksPath` 与 `core.sshCommand` 值，
或在原本没有时移除这两处本地覆盖。它拒绝覆盖已漂移的 provider 状态。卸载不会
删除待变更历史；请通过台账生命周期将其结算。

## 权威与强制边界

这是本地工作流强制，不是分支保护。`hook_only` 可被 `--no-verify` 绕过；
`reference_guard` 关闭了那条 commit 路径与仓库的 SSH 传输路径。同时跳过
`pre-push` 并避开 SSH、替换 `core.hooksPath` 或 `core.sshCommand`、使用替代的
Git 配置或二进制、直接编辑 ref 文件、从另一台机器写入，或调用托管 API 的 HTTPS
push，仍在其权威之外。安全边界请使用 OS 策略加远程分支保护或服务端控制。
该 capability 不 push、不 merge、不创建 PR、不修改受保护分支，也不把时间表接纳
当作这些效果的许可。
