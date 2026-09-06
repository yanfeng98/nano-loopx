# DSH × LoopX:Replan 而不丢失决策链

> [English](dsh-loopx-replan-demo.md)

**可复现 demo · 真实 DSH 录屏 · 合成公开安全工作量**

[![DSH × LoopX 录屏封面](../../assets/showcases/dsh-loopx/dsh-loopx-cover.png)](../../assets/showcases/dsh-loopx/dsh-loopx-quickstart-replan.mp4)

**[观看 60 秒录屏](../../assets/showcases/dsh-loopx/dsh-loopx-quickstart-replan.mp4)** 或
[打开可运行 fixture](../../../examples/dsh-loopx-demo/README.md)。

## 有用的 Loop

一个小型 Node.js CLI 需要结构化日志。DSH agent 比较 Pino、Consola 和 Roarr,记录自己的证据,最初选择 Pino。然后用户加了一个素材约束:该 CLI 将在 serverless 环境中运行,因此冷启动时间和依赖体积现在更重要。

LoopX 没有覆盖第一个答案,而是把它保留为被取代的决定,记录一次 Replan,创建继任工作,并在实现与测试落定之前让同一个 Goal 在 DSH 中保持可见。

| 证据 | 新约束之前 | Replan 之后 |
| --- | --- | --- |
| 决定 | Pino | Roarr |
| 依赖树 | 12 个包 | 4 个包 |
| 记录环境中的已安装体积 | 约 2.2 MB | 548 KB |
| CLI 行为 | 需要 JSON 输出 | 保留 JSON stdout/status 与 JSON stderr/fail |
| 验证 | 决定与初始实现 | 3/3 行为测试,GoalBar 2/2 |

体积数值是本次记录比较中的机器本地测量值。包数与最终行为可以从公开 lockfile 与测试中复现;本案例不声称 Roarr 总是优于 Pino。

## 为什么 LoopX 在这里重要

价值不是日志库推荐本身。价值在于一个约束变更仍然与以下内容保持连接:

- 更早的决定及其证据;
- 那个决定为何变得不足;
- 实现修订计划的继任 Todo;
- 证明修订工作已落定的测试与 GoalBar 状态。

DSH 仍然是执行宿主。LoopX 在该宿主之上提供持久的 Goal、Todo、Replan、证据、quota 与延续控制面。

## 复现

安装已发布的插件:

    dsh plugin --profile web add \
      "https://github.com/huangruiteng/loopx/releases/download/dsh-loopx-plugin-v0.1.1-beta.4/dsh-loopx-plugin-0.1.1-beta.4.tgz"

运行确定性的已完成 fixture:

    cd examples/dsh-loopx-demo
    npm ci --ignore-scripts
    npm test

或者创建基线并运行完整 agent 路径:

    examples/dsh-loopx-demo/reproduce-demo.sh /tmp/dsh-loopx-replan-demo
    cd /tmp/dsh-loopx-replan-demo
    dsh --profile web --port 0

确切的提示词与验收边界在
[demo README](../../../examples/dsh-loopx-demo/README.md) 中。

## 证据边界

视频是使用已发布 LoopX 插件的真实 DSH 会话的剪辑录屏。仓库只包含简短的产品证明片段、合成 CLI、公开包元数据和确定性行为测试。它排除凭据、模型提供方配置、原始推理、设置重试、私有 URL、本地 LoopX 状态和未剪辑录屏。

## 分享文案

发布仍然是所有者的决定;这些是可直接使用的草稿,不是自动发布的请求。

### 中文

把 LoopX 接进 DeepSeek Harness,现在只需要一条很短的路径:

安装 Plugin → 在技能选择器里点 loopx → 直接说任务。

这段 60 秒真实录屏里,Agent 先选择 Pino;收到「serverless 冷启动和体积优先」
的新约束后,LoopX 显式 Replan 到 Roarr:12 个包降到 4 个,行为测试 3/3
通过,GoalBar 最终 2/2。

约束变化,不应该抹掉长程任务的决策与证据链。

https://github.com/huangruiteng/loopx

### English

LoopX now plugs into DeepSeek Harness through a very short path:

install the plugin → pick the loopx skill → describe the task.

In this real 60-second run, the agent first chose Pino. A new serverless
cold-start constraint triggered an explicit Replan to Roarr: 12 packages
became 4, all 3 behavior tests passed, and the GoalBar closed at 2/2.

Changing constraints should not erase the decision and evidence trail of a
long-running task.

https://github.com/huangruiteng/loopx
