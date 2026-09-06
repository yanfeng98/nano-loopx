# issue_fix_acceptance_loop_v0


`issue_fix_acceptance_loop_v0` 是首个可执行的 LoopX 仓库 issue fix 工作协议。
它的目标是验收,而不是展示:给定公开 issue/PR 元数据信号,loop 必须证明 agent
可以从信号推进到已验证的修复 artifact。

初始实现是一个确定性 fixture 命令:

```bash
loopx issue-fix acceptance-fixture --format json
```

该命令创建临时 fixture 工作区,运行一个失败的聚焦复现,应用一个最小代码补丁,
重新运行同一聚焦校验,并返回 `issue_fix_validated_fix_artifact_v0`。只有当复现
在补丁前失败、且校验在补丁后通过时,artifact 才就绪。

下一个 fixture 通过真实临时 git 仓库与 issue branch 演练同一修复路径:

```bash
loopx issue-fix repo-branch-fixture --format json
```

它初始化本地 fixture 仓库,提交失败的 baseline,创建
`codex/issue-123-public-metadata-fixture`,运行复现,给分支打补丁,重新运行校验,
在不暴露 raw git 输出的情况下确认分支本地补丁 diff,并返回同一已验证修复
artifact 形状,外加一个 `issue_fix_repo_branch_artifact_v0` 段。

被提升的 caller 批准分支模式把同一契约移到调用方选择的真实本地仓库:

```bash
loopx issue-fix caller-repo-branch \
  --repo-path /path/to/approved/repo \
  --url https://github.com/owner/repo/issues/123 \
  --base-branch main \
  --validation-command "python test_calculator.py" \
  --validation-label "python test_calculator.py" \
  --execute \
  --format json
```

该模式创建或认领一个 `codex/` issue 分支,只运行调用方声明的校验命令,并返回
`issue_fix_caller_repo_branch_packet_v0`。公开 packet 记录仓库标签、issue 分支、
校验通过/失败、repo-relative 变更文件与 PR review 就绪度。创建新 issue 分支前,
它记录 typed base snapshot,要求已批准的本地 base 分支与其本地 tracking ref
匹配,从该不可变 revision 创建,并对照 snapshot 回读新分支。过期、超前或分歧的
base 会在分支创建前 fail closed。旧 base 分支不再存在时,已创建的 issue 分支仍
可认领。该命令从不隐式刷新远程 refs;需要新远程证据的调用方必须显式 fetch 并
对账。它不暴露本地仓库路径、校验 stdout 或 stderr、raw issue 正文/评论内容、
外部 remotes 或 raw git 输出。不加 `--execute` 时,该命令是 dry-run 计划,不检查
或修改本地仓库。

## 产品契约

用户可见价值是已验证的修复路径:

1. 公开元数据 intake 建立 repo/issue 信号,而不复制 issue 正文或评论正文;
2. 复现命令证明 bug 当前存在;
3. 代码路由为最小补丁指出文件与原因;
4. 补丁在 fixture 工作区中应用;
5. 聚焦校验通过;
6. PR-review packet 就绪,但本 fixture 不执行任何外部评论、PR 创建、merge 或
   publish 动作。

对于 caller 批准的本地仓库,只有 issue 分支已存在或被认领、caller 声明的校验
通过、且存在 repo-relative 变更证据时,PR-review 就绪度才为 true。外部 issue 评论、
PR 创建、merge 与 publish 动作仍分别是显式 caller 决策。

这让协议对自动化有用,同时保留安全默认值。Packet 是已完成修复 loop 的证据,
不是修复 loop 的替代品。

## Public-Safe 字段

Fixture packets 必须报告:

- `external_reads_performed: false`
- `external_writes_performed: false`
- `issue_body_captured: false`
- `comment_bodies_captured: false`
- `local_paths_captured: false`
- `private_repo_state_read: false`
- `destructive_git_used: false`

Caller 批准仓库模式在一处狭窄地不同:使用 `--execute` 时,
`private_repo_state_read` 为 `true`,因为 LoopX 检查 caller 批准的本地 git
仓库。该 packet 仍必须保持 `local_paths_captured: false`,必须摘要校验
stdout/stderr,并且不得执行外部 issue 评论、PR 创建、merge、publish 或破坏性
git。

校验命令输出只以通过/失败与退出码摘要。Fixture 不向 artifact 暴露 stdout、
stderr、本地临时路径或 raw provider payloads。

## 下一步提升

下一个实现步骤是:在 caller 批准的仓库分支模式之上做 agent 应用补丁编排——
分支准备好后,项目 agent 应选择最小代码路由、应用补丁、重新运行声明的校验,
然后把 PR-ready packet 用作 review 证据。外部评论、PR 创建、merge 或 publish
动作仍需要显式 caller 动作。

## Smoke

持久化 smoke 是:

```bash
python3 examples/issue-fix-acceptance-loop-smoke.py
```

它演练 CLI,检查 failure-before/fix-after 校验序列,并拒绝公开 artifact 中的本地
路径暴露。
