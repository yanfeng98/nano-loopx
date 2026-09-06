# DSH × LoopX Replan Demo

这个 public-safe demo 展示 LoopX 在一个真实 DeepSeek Harness(DSH)session 内运行。agent 从一个普通库选型决策开始,收到一个新的 serverless 约束,并记录一次显式 Replan,而不是静默改写早先的决策。

[![DSH × LoopX:一个 skill、持久工作、真实 Replan](../../docs/assets/showcases/dsh-loopx/dsh-loopx-cover.png)](../../docs/assets/showcases/dsh-loopx/dsh-loopx-quickstart-replan.mp4)

**[观看 60 秒录屏](../../docs/assets/showcases/dsh-loopx/dsh-loopx-quickstart-replan.mp4)。**

## 录屏证明了什么

1. /loopx 从 DSH 的 skill 选择器中显式选中。
2. 一个普通的研究加实现请求创建了持久的 Goal/Todo 状态。
3. 一个新的 serverless 约束通过一次记录的 Replan 把决策从 Pino 改为 Roarr。
4. 最终实现保留了 CLI 行为,通过 3/3 测试,并把 GoalBar 收尾在 2/2。

运行中显示的依赖树从 12 个包变为 4 个;机器本地安装体积从约 2.2 MB 变为 548 KB。这些测量说明的是本示例的决策,而不是通用的 logger 排名。

## 安装 DSH 插件

要求:Node.js 22.19+、npm、Python 3.11+、pip、pnpm、DSH,以及已在 DSH 中配置的模型 provider。

    dsh plugin --profile web add \
      "https://github.com/huangruiteng/loopx/releases/download/dsh-loopx-plugin-v0.1.1-beta.4/dsh-loopx-plugin-0.1.1-beta.4.tgz"
    dsh --profile web --port 0

在 DSH 编辑器里调用 loopx skill。/loopx-init 是显式修复命令;正常安装不需要它。

## 验证完成的 fixture

    cd examples/dsh-loopx-demo
    npm ci --ignore-scripts
    npm test

这个确定性检查验证 JSON stdout 的成功、JSON stderr 的失败以及它们的退出码。它不声称重放模型的确切措辞。

## 复现 agent loop

    examples/dsh-loopx-demo/reproduce-demo.sh /tmp/dsh-loopx-replan-demo
    cd /tmp/dsh-loopx-replan-demo
    dsh --profile web --port 0

在 DSH 中,选择 loopx 并提交:

> Research Pino, Consola, and Roarr for this CLI. Record the evidence and
> decision, then complete a minimal integration and tests.

在第一次决策后,再次选择 loopx 并提交:

> New constraint: this CLI will run in serverless, so cold start and dependency
> footprint are now high priority. Re-evaluate the decision; if the plan
> changes, record a LoopX Replan and update implementation, docs, and tests.

模型措辞与时机可能有差异。验收边界是持久的决策变更、保留的 CLI 行为、通过的测试与关闭的 Todo 状态。

## 中文说明

这段真实录屏展示了最短接入路径:安装 Plugin,在 DSH 技能选择器中显式选择
loopx,然后直接描述任务。Agent 最初选择 Pino;收到 serverless 冷启动和
依赖体积优先的新约束后,LoopX 保留原决策并记录 Replan,最终切换到 Roarr。

完整案例、证据边界和中英文分享文案见
[DSH × LoopX showcase](../../docs/showcases/cases/dsh-loopx-replan-demo.md)。
