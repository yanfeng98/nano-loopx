# Content-Ops 能力


content-ops capability 是创作者/运维者工作流的产品路径:public handles、私有
connector gates、来源项、角度候选、草稿状态、反馈信号与发布 gates。

当前实现仍处于 preview 级别。它的价值在于:在 raw 材料被复制或发布之前,为真实
connector 与审查 surface 提供安全的 packet 格式。

该 capability 还为真实本地运维队列提供 provider-neutral 的项生命周期。它在
LoopX state 之外保留稳定的项身份、修订绑定审批、交付 receipts、精确 readback
与取代关系,而不复制草稿正文或 provider 凭据。见
[`content_ops_item_v0`](../../../docs/reference/protocols/content-ops-item-lifecycle-v0.md)。

`loopx content-ops queue-status` 把调用方自有的项文件投影成带状态计数与下一步
动作的只读托管队列 surface。优先级是 `--item-json` 输入的顺序;窗口存在于项
审批与交付意图记录中。见
[`content_ops_queue_projection_v0`](../../../docs/reference/protocols/content-ops-queue-v0.md)。

内置布局模板库把可复用的展示规则从写作 skills 中移出。`template-list` 与
`template-show` 暴露四种通用视觉系统;`layout-plan` 在渲染前记录 typed 页面
角色;`layout-check` 拒绝稀疏、过度拥挤、溢出、碰撞或角色不完整的页面集。见
[`content_ops_layout_plan_v0`](../../../docs/reference/protocols/content-ops-layout-v0.md)。

## 已实现的 surface

| 层 | 当前路径 |
| --- | --- |
| Capability 模块 | `loopx/capabilities/content_ops/` |
| CLI 入口 | `loopx content-ops ...` |
| 协议文档 | `docs/reference/protocols/content-ops-surface-v0.md` |
| 队列投影 | `docs/reference/protocols/content-ops-queue-v0.md` |
| 布局契约 | `docs/reference/protocols/content-ops-layout-v0.md` |
| Smoke | `examples/content-ops-*-smoke.py` |

## 安全默认值

- 公开源是 metadata-first。
- 私有 connector 通过 owner gates 或紧凑的已批准计数进入。
- Raw chats、transcripts、凭据、日志与本地路径不被复制进公开 packets。
- 发布保持阻塞,直到显式用户决策。
- 修订已批准内容会使审批与任何交付意图失效。
- Provider 交付与 readback receipts 必须匹配已批准修订与 digest;生命周期
  helper 不执行外部写。
- 布局验收绝不意味着内容审批或发布 authority。
- 内置封面页要求 `0.90–0.98` 的有效垂直密度;模板字段是
  `density.role_overrides.cover`。
- 内置 `page_sequence` 默认要求封面在前,使其为密度最大值,并要求内页至少
  `0.80` 的有效密度;最后一页保留其 closing/CTA 角色限值。

## Connector 优先的运维模式

对于社交与创作者运维,从 connector 源映射开始,而不是凭记忆起草:

```bash
loopx value-connectors source-map --format json
```

这个 packet 给新连接的 agent 提供当前 read-first connector 目录,包括公开
GitHub 元数据、content-ops public handles、浏览器支撑的 X 研究、Agent-Reach
源路由与 finance snapshot probes:

```text
doctor -> read-only source map -> maturity score -> ops brief -> draft packet
       -> publish/audit record -> compact monitor
```

该模式让新连接的 LoopX agent 复用外部信号,而不把 LoopX 变成 raw 平台归档或
未跟踪发布者。即使 owner 授予宽泛发帖裁量权,agent 仍应在外部发帖前记录确切
正文、账号/频道、源映射、时机与停止条件。

## 社交浏览器 Provider

`content-ops` 拥有内置 `social_browser_x` provider,因为公开社交观测、源提升、
草稿准备与发布 gates 是内容 outcome。Provider 提供一个共享源 profile、安装检查
与 metadata-only connector trial。`value-connectors` CLI 仍是兼容 facade,委托
那些 packets 而不改变其输出。

Provider 不打开浏览器、不读取 timeline、不发布。真实的浏览器会话保持
owner-controlled,且每次外部写仍需要确切账号、正文、媒体/链接计划、来源引用与
停止条件。
