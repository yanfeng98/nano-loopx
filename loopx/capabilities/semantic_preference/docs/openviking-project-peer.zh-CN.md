# OpenViking 项目 Peer Provider

> [English](openviking-project-peer.md)

LoopX 附带一个单薄、opt-in 的 OpenViking provider，用于项目作用域的语义偏好。
一个规范项目映射到一个保留的 OpenViking peer。同一 `origin` 的 Git worktrees
与全新 clone 因此共享一个记忆作用域，而另一个仓库解析到不同的作用域。

该适配器不实现记忆提取、排序、更新或 supersede 语义。OpenViking 拥有这些行为。
LoopX 只推导项目 peer、执行有界的 `find` 调用，并为函数拥有的应用与回执返回
既有语义偏好 provider 协议。

## 作用域契约

- 身份来自规范化的 Git `origin`，绝不来自 checkout 路径。
- 非 Git 项目必须提供稳定的 `--loopx-project-id`。
- Recall 默认针对精确的项目 peer。
- 每次 `find` 都把 OpenViking 请求主体（request actor）绑定到推导出的项目 peer。
- 用户级全局记忆只能通过 `--include-global-fallback` 获得。
- 默认预算是一次 `find`；显式全局回退至少需要两次。
- 只返回所选目标下的具体偏好节点。
- OpenViking 失败仍受外层表面 `fail_open` 或 `fail_closed` 策略约束。

在不联系 OpenViking 的情况下检视本地作用域：

```bash
loopx semantic-preference openviking-provider \
  --project . \
  --user-space default \
  --describe-scope
```

输出包含 peer id 与目标 URIs，但不含仓库 URL 或本地 checkout 路径。它还包含
一个有界的 corpus inventory。项目 peer 偏好语料库是主语料；用户全局偏好只在
调用方显式启用全局回退时出现。

OpenViking agent 集成可以在向会话添加用户消息时使用返回的 `peer_id`。对于隔离的
原生写入，创建该会话时禁用 self memory、启用 peer memory，并允许所需记忆类型。
消息 peer 与请求主体必须是同一个推导出的项目 peer。仅凭消息 `peer_id` 标识
发言者；它并不授权以不同 actor 运行的 extractor 更新该 peer。OpenViking 随后在
所选语料库内部拥有提取、更新与 supersede 语义。

不要把已完成的提取任务当作足够的写入证据。该 provider 的维护关闭需要满足以下
全部条件：

1. 任务报告预期的 add/update 计数与 memory diff。
2. 待处理的 embedding 或索引工作无错误地归零。
3. 直接 L2 读取返回新的语义内容。
4. 通过同一项目 peer provider 的一次作用域 `find` 召回该内容。

如果某个 trigger 不需要语义变更，就发出一条紧凑的 `no_write_rationale`
维护回执。绝不把原始记忆持久化在回执里。

## 仓库模板与语义偏好

对于 PR 描述，仓库当前的 `.github/PULL_REQUEST_TEMPLATE.md` 是权威的硬结构。
构建工件时应从工作 revision 中读取它。OpenViking 只存储如何填充该结构的软性
语义偏好，例如评审者语言、有用细节与基于风险的校验。不要把模板正文复制进
OpenViking：那样会制造一份过时的第二真相源。

当仓库模板变更时，评估项目 peer 偏好语料库，因为其解读可能需要变化。当显式
用户反馈改变了行文偏好时，通过 OpenViking 的原生 extractor 更新该语料库，并完成
上述四步回读。

## 本地私有 hook 配置

首先激活捆绑 provider。该命令只在只读的 `ov status` doctor 成功后注册预安装的
入口点；它不安装也不配置 OpenViking：

```bash
loopx extension install \
  --bundled openviking-semantic-preference \
  --execute \
  --format json
```

保持 hook 配置为忽略且未跟踪。OpenViking 服务配置保持本地化：

```json
{
  "schema_version": "semantic_preference_hook_config_v0",
  "enabled": true,
  "provider": {
    "id": "openviking_semantic_preference",
    "extension_id": "openviking-semantic-preference",
    "args": [
      "--project",
      ".",
      "--user-space",
      "default",
      "--max-find-calls",
      "1"
    ]
  },
  "surfaces": {
    "issue_fix.pr_description": {
      "query": "PR description structure and validation preferences",
      "limit": 3,
      "failure_policy": "fail_open"
    }
  }
}
```

激活前把 `ov` 暴露到 `PATH` 并准备好 OpenViking 的常规本地配置。
`loopx extension doctor openviking-semantic-preference --execute` 重复只读的
`ov status` 探测。Hook `args` 仍可携带项目作用域选项；它们不改变 manifest 拥有的
doctor。

`loopx semantic-preference openviking-provider` 仍是一个惰性委托的兼容别名：
普通 LoopX CLI 启动不导入该 provider，别名只在被调用时加载它。新集成应使用
extension 激活与 `extension_id` 绑定，使 enable、disable、upgrade、rollback、
API 兼容性、权限与 doctor 状态在一个生命周期内可检视。

消费函数仍是最终的应用边界。对于 Issue Fix，
`build_issue_fix_pr_description()` 拥有一次 recall、fail-open 保留、偏好归属、
紧凑应用回执，以及 provider 语料库清单与维护指引的传播。它不执行自动写入，
也不追加第二次 provider 调用。
