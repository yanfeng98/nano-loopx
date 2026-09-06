# DeepSeek Harness 原生控制面集成

> [English](deepseek-harness-control-plane-adapter.md)

状态:已在本仓库中以可选
[`dsh-loopx-plugin`](../../packages/dsh-loopx-plugin/README.md) 包实现。

该包把 LoopX 嵌入一个可见的 DeepSeek Harness(DSH)会话,既不把执行权威移出
DSH,也不把持久控制面权威移出 LoopX。它附带三个协作界面:

- `/loopx-init`:安装或修复 LoopX CLI 与 DSH 工作流 skill;
- 一个被动的同会话 Driver:只有在确切会话调用了已安装的 `loopx` skill 之后,
  它才可以排队一个 LoopX 续接;
- 一个仅限 loopback 的 GoalBar Host 与 Web Client:显示一个确切绑定的
  Goal/Agent lane,并暴露受保护的 Start 与 Pause 动作。

旧的 [`deepseek-harness` 连接器](deepseek-harness-connector.md) 仍是独立的
headless Turn 适配器。原生插件使用 `deepseek-harness-native` 宿主界面,且不
替代该连接器。

## 权威边界

| 责任方 | 职责 |
| --- | --- |
| DSH | Agent 与会话生命周期、模型与工具执行、收件箱排序、会话事件、UI 传输、沙箱、provider 凭证、计费与 trace |
| LoopX | Goal、Agent、Todo、绑定、配额、生命周期、进度、scheduler、证据与结算权威 |
| `dsh-loopx-plugin` | 固定 argv 的 CLI 适配、确切会话激活状态、一个待定续接保留、loopback GoalBar 传输与紧凑 UI 状态 |

该插件没有面向模型的 LoopX 工具、没有绑定 sidecar,也没有持久的 Goal 或 Todo
存储。安装它不会创建 Goal、绑定会话、消耗配额、激活 Driver,也不会授予模型/
工具权威。

## 安装与激活

安装同地点(co-located)包并运行其无参数初始化命令:

```bash
cd packages/dsh-loopx-plugin
./install.sh
```

```text
/loopx-init
```

`/loopx-init` 探测现有 CLI,在 CLI 缺失或不兼容时最多执行一次
`python3 -m pip install --upgrade loopx`,安装打包的工作流 skill 并验证读回。它
不安装定义该命令的插件。只有当返回结果说明已安装的 skill 发生变化时,才重启
DSH。

然后,在应该自动续接的 DSH 会话中,用任务调用已安装的 `loopx` skill。该 skill
使用 DSH 的确切会话 id 与 `deepseek-harness-native` 宿主界面。从该会话的项目
验证得到的绑定:

```bash
loopx --registry .loopx/registry.json --format json \
  resolve-agent-thread \
  --host-surface deepseek-harness-native \
  --thread-id "$DSH_SESSION_ID"
```

只有 `status=bound` 且携带一个确切 Goal/Agent 配对,才允许 GoalBar 与 Driver。
缺失或有歧义的绑定按失败即关闭(fail-closed)处理。

## 同会话 Driver

加载插件是被动的。只有当确切当前会话包含以下类型化激活事实之一时,Driver 才
具备资格:

- 来自 `loopx` skill 调用的 `user/message`;或
- 针对该 skill 的 `tool/call`,且按 call id 与成功的 `tool/result` 配对。

普通散文、shell 文本、`/loopx-init`、skill 目录、失败或未匹配的工具调用、现有
注册表或绑定都不会激活 Driver。激活只存在于内存且限于会话范围;替换或清空会话
后,会从该会话的类型化事件历史重新计算。

在合格的空闲边界,Driver:

1. 让位于现有的人类或插件输入;
2. 用 `resolve-agent-thread` 解析确切会话绑定;
3. 用稳定的 `turn_instance_id` 为绑定的 Goal 与 Agent 调用 `quota should-run`;
4. 仅当配额允许工作时才读取规范的瘦 `heartbeat-prompt`;
5. 最多向同一 Agent 排队一条类型化 `loopx-continuation` 消息;
6. 在消息进入模型步骤之前重新验证 Agent、会话、保留、绑定与配额。

DSH 拥有 provider 重试。Driver 只重试安全的固定 argv LoopX 读取与一次幂等配额
回执,且带有限重试预算。人类输入优先于无人 claim 的自动保留;取消或会话失效会使
待处理工作退役。

## GoalBar

包根 Host 注册一个具有 `loopback` 权威的 `/loopx` Connection 通道。其 Client
只对确切活跃会话绑定渲染一个紧凑 GoalBar。线缆协议是
`loopx_goalbar_request_v2` / `loopx_goalbar_response_v2`,支持:

- `goalbar/read`;
- `goalbar/watch`;
- `goalbar/start`;
- `goalbar/pause`。

Host 从活跃 DSH Agent 派生 cwd 与会话身份。它通过固定 LoopX CLI argv 读取绑定、
生命周期与 agent lane Todo 进度,然后根据项目注册表与活动 Goal 状态计算不透明的
来源修订。浏览器只收到 id、激活状态、Agent 状态、计数、光标、来源修订与固定
错误码——不接收 todo 文本、Goal 目标、证据、CLI 输出、异常详情、注册表路径或
凭证。

`Start` 只对停止的 Goal 与空闲的确切会话允许。`Pause` 停止 Goal 并让未来排队的
续接退役;它不会中止一个已 claim 或运行中的 Turn。每个动作都会重新验证绑定,
并返回类型化的成功、拒绝、结果未知或带警告应用状态。

## 失败与隐私边界

- LoopX CLI 输出按精确 schema 解码;格式错误或不匹配的输出按失败即关闭处理。
- loopback 传输是网络可达性围栏,不是用户认证。当前包不支持远程或局域网
  GoalBar 访问。
- 来源修订是变更令牌,不是授权或 compare-and-swap 授权。
- 原始转录、原始工具输出、私有 trace、凭证、本地路径与完整 Goal/Todo 文本
  不会跨越 GoalBar 线缆边界。
- 原生插件从不接管 DSH 的模型、工具、沙箱、provider 或重试所有权。

## 验证与移除

从包目录中,维护者可以验证实际交付的界面:

```bash
pnpm build
pnpm smoke:artifact
pnpm smoke:profile
pnpm smoke:runtime
```

要禁用全部原生插件界面,请从 web profile 移除该包并重启 DSH:

```bash
dsh plugin --profile web remove dsh-loopx-plugin
```

这会移除 `/loopx-init`、Driver 与 GoalBar。它不会移除 LoopX CLI、项目状态、
绑定或已安装的 skill。关于仅卸载 skill 与包回滚流程,请参阅
[包 README](../../packages/dsh-loopx-plugin/README.md)。

## 相关文档

- [DeepSeek Harness 连接器](deepseek-harness-connector.md)
- [DSH 原生 LoopX 设计](../plans/2026-08-20-dsh-native-skill-driver.md)
- [Runtime 连接器目录](runtime-connector-catalog.md)
- [宿主集成面 v0](../reference/protocols/host-integration-surface-v0.md)
