# 为 LoopX 做贡献


你想帮助改进 LoopX？很好，感谢你。贡献有很多形式，并非所有都是代码：

- 提交带复现步骤的清晰 bug 报告；
- 分诊并复现 issue；
- 改进文档、示例与冒烟测试；
- 在 issue 或讨论中回答问题；
- 评审 pull request 并帮助贡献者熟悉评审流程；
- 遵循[行为准则](CODE_OF_CONDUCT.md)；
- 实现公开任务或修复 bug。

每一件事都有帮助。本指南其余部分涵盖寻找工作、维护公共/私有边界、验证变更
以及让 pull request 合并。

最好的代码贡献是小而可评审，并与公开任务或明确 bug 相关。

## 行为准则

所有参与 LoopX 社区空间（包括维护者与贡献者）的人都应遵循
[贡献者公约](CODE_OF_CONDUCT.md)。不可接受行为的报告可发送至
huangrt01@163.com；维护者会及时评审每份报告，并在可行范围内为举报者保密。

## 寻找工作

从[当前技术方向](docs/project/technical-directions.md)开始，了解活跃项目及其
成熟度，然后使用
[docs/development/contributor-tasks.md](docs/development/contributor-tasks.md)
寻找有用、可认领且可在仓库中安全讨论的公开工作。

如果没有匹配的任务：

1. 用贡献者任务模板打开 GitHub issue；
2. 说明问题、提议范围、触及的文件与验证命令；
3. 在开始大型或行为变更工作前等待维护者反馈。

小型文档错别字修复与明显安全的清理可以直接进入 pull request。

## 公共与私有边界

LoopX 协调本地 agent 状态，因此某些文件是运行时数据，必须排除在公开贡献之外：

- 不要提交 `.loopx/`、`.codex/goals/` 或活动中的 `ACTIVE_GOAL_STATE.md` 文件；
- 不要发布私有 benchmark 轨迹、verifier 输出、原始 agent 会话、凭据、内部
  文档链接或本地机器路径；
- 除非维护者为该工作拆分出公开 issue，否则不要运行或重复维护者拥有的
  benchmark 用例。

安全的贡献面包括文档、示例、冒烟测试、CLI 诊断、schema 文档、dashboard UI
代码与脱敏 fixture。

发送文档或示例前运行公共/私有扫描：

```bash
loopx check \
  --scan-path README.md \
  --scan-path CONTRIBUTING.md \
  --scan-path docs/development/contributor-tasks.md \
  --scan-path docs/ \
  --scan-path examples/
```

## 本地开发

使用[开发者指南](docs/development/README.md)作为稳定入口。在更改 scheduler、
quota、todo/gate、onboarding、agent 面向输出或发布行为之前，阅读双语
[测试与质量指南](docs/development/testing-and-quality.md)。在新增或整合公开
冒烟之前，使用双语[良好冒烟指南](docs/development/good-smokes.md)定义其持久
不变量、独立 oracle、节奏与公开安全 fixture 边界。

安装并校验检出：

```bash
git clone https://github.com/huangruiteng/loopx ~/loopx
~/loopx/scripts/install-local.sh
export PATH="$HOME/.local/bin:$PATH"
loopx doctor
loopx demo
```

常用聚焦检查：

```bash
python -m pip install -e ".[test]"
python -m ruff check tests loopx/canary loopx/control_plane loopx/domain_packs loopx/presentation
python -m mypy
python examples/control_plane/cli-output-budget-regression-smoke.py
python -m pytest -q
loopx canary premerge --from-git-diff
loopx check --scan-path loopx/ --scan-path tests/ --scan-path examples/ --scan-path docs/
git diff --check
```

按变更风险选择聚焦冒烟与更广的 canary；不要为每个补丁运行所有公开冒烟或
现场模型调用。质量指南解释了 CI、本地/手动与仅发布边界。

## 许可与 DCO 签署

LoopX 的统一开源核心基于
[Apache License 2.0](LICENSE) 许可。除非在提交前明确说明，否则被本仓库
接受的贡献按 Apache-2.0 提交，不附加额外条款或条件。LoopX 不要求版权转让
或贡献者许可协议。

每个 pull request 提交必须通过包含 sign-off 结尾证明
[Developer Certificate of Origin 1.1](DCO)：

```text
Signed-off-by: Your Name <your.email@example.com>
```

使用 Git 的 `-s` 选项生成该结尾：

```bash
git commit -s -m "feat: describe the change"
```

名称与邮箱必须标识做出证明的人，并且必须是你在永久 Git 历史中被允许发布的
信息。如果提交缺少该结尾，用 `git commit --amend -s` 修正，或使用交互式
rebase 签署相关提交，然后更新 pull request 分支。`DCO` pull request 检查
会拒绝未签名的提交。

`v0.4.7` 及之前的发布仍遵循其原始 MIT 条款。历史通知、专利授权边界与
open-core 范围参见[许可与 v0.4.8 迁移政策](docs/project/licensing.md)。

## 实验性功能

使用 `loopx/experiments/<experiment-id>/` 存放尚无稳定调用方契约、不参与
LoopX 默认生命周期的 opt-in 原型。将其测试、示例与脚本放在匹配的
`experiments/` 路径下，使原型可以作为整体被评估或移除。核心模块不得导入
实验包。参见[实验放置与晋升政策](loopx/experiments/README.md)。

## 宿主 Loop 与 LoopX Turn

把 LoopX Turn 与长程宿主 loop 视为不同层级：

- `loopx turn run-once` 是一次原子化的治理事务。它可以做决策、调用一个有界
  宿主片段、独立验证、写回、消耗一次，并投影最新的调度器阶段。
- Turn Loop Controller 是外层运行时所有者。它决定何时唤醒、调用
  `run-once`、消费类型化结果、应用共享的 `scheduler_hint`，然后等待、路由
  用户动作、修复、重规划、继续或停止。
- 宿主适配器翻译一个类型化请求与结果。它拥有不透明的宿主会话与工具，
  但不拥有 LoopX 状态、quota、完成、验证、调度器策略或重规划策略。

不要在 `run-once` 内添加睡眠循环、cron 实现、周期守护进程、操作员通知路径
或多 Turn 重规划循环。不要复制 Codex App 的 heartbeat 提示词规则到第二个
scheduler。复用现有 interaction、scheduler、autonomous-replan、todo 与
TurnEnvelope 契约；只有运行时特有的"应用唤醒"这一动作才属于 scheduler 适配器。

`replan_required` 结果不是再次调用同一 todo 的许可。控制器必须先记录一个有界
todo 或 vision delta、获取新的 TurnEnvelope，并保留因果 `(goal_id, agent_id,
todo_id)` 前沿。不透明的可恢复宿主会话是恢复元数据，不是绕过该决策的权限。

按可评审切片分阶段提交宿主 loop 贡献：

1. 用独立派生的 fixture 表征当前 Codex App 与 Turn 行为；
2. 添加一个无宿主或无状态效应的纯 next-disposition 决策表；
3. 添加一个带假时钟与假宿主的 scheduler-owner 适配器；
4. 只有在共享迁移契约稳定后才添加运行时特定的唤醒、通知或展示。

对每个控制器或宿主 loop 变更，证明：

- scheduler 所有者、宿主界面与执行模式显式且有效；
- `wait`、用户动作、monitor-only 与 cadence-only 路径不做模型调用、不消耗
  quota；
- 在持久写回与消耗之前，实质性进展需要独立的 postcondition 验证；
- 回放与中断阶段恢复是幂等的；
- repair 与 replan 保持不同，replan 在下一个 Turn 前产生全新前沿；以及
- fixture 不含原始提示词、transcript、凭据、私有状态或宿主本地路径。

阶段性控制器计划参见 [LoopX Turn 协议](docs/reference/protocols/loopx-turn-v0.md)
与[贡献者任务板](docs/development/contributor-tasks.md)。

## 治理与归属

仓库角色与决策权限定义在
[治理](.github/GOVERNANCE.md)。创建者与贡献者归属记录在
[docs/project/authors.md](docs/project/authors.md)，而按路径划分的维护与
优先评审指派记录在同一治理文档中。公开 Git 历史记录个人贡献。贡献不会
自动授予合并或发布权限，agent 或自动化身份不是人类维护者。

命名或打包 fork、集成或托管服务时，遵循项目的
[名称与标识指南](docs/project/trademarks.md)。

对于 dashboard 变更：

```bash
cd apps/presentation/dashboard
npm install
npm run build
npm run smoke:demo-readiness
```

## 认领任务

- 在开始非平凡工作前在 issue 下评论。
- 如果维护者将其标记为 `claimed` 或指派给你，把范围贴近 issue。
- 如果卡住了，评论说明阻塞点和你尝试过的方法。
- 如果需要变更范围，先询问。
- 如果 14 天没有更新，维护者可能释放该任务供他人接手。

## Pull Request 清单

在打开 pull request 之前：

- 有 issue 或任务 ID 时链接它；
- 描述行为变更与你运行的验证；
- 把无关格式或重构排除在 PR 之外；
- 变更用户可见行为时包含文档或测试；
- 确认没有提交私有/本地运行时状态。

如果变更混杂了无关关注点，维护者可能要求更小的 PR。
