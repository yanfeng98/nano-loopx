# LoopX 展示层


本目录拥有把 LoopX 状态变成面向人类展示表面的代码。它绝不能成为控制面真相源。

## 布局

| 目录 | 拥有 | 不拥有 |
| --- | --- | --- |
| `renderers/` | 在已构建的 LoopX 载荷之上的传输中立文本或 Markdown 渲染。 | 调度、quota、todo 或证据决策。 |
| `sinks/` | 外部展示 sink，例如 Lark/飞书表格与卡片。 | Connector 登录权威、私有读取或生产动作。 |
| `projections/` | 未来面向展示的中间读模型，为表面联结或重塑公开安全 LoopX 证据。 | 持久控制状态或基准评分。 |

共享 Markdown 原语（如标量转义与载荷形态守卫）位于 `loopx.presentation.markdown`。
Renderers 应复用这些辅助函数，而不是定义本地表格单元格或标量转义规则。

以用户可见 capability 起步的 Python 代码可以在 `loopx.capabilities.*` 下保留薄
门面，但可复用的展示实现应位于此处。

## 探索结果层

软件探索拓扑的展示侧才属于这里：

- 只重塑公开安全 explore 状态给人类看的 graph/table/card 投影可以位于
  `loopx/presentation/projections/explore/`；
- Lark/飞书表格同步与卡片输出位于 Lark extension 之后，
  `loopx/extensions/lark/presentation/`；
- 核心 explore 日志、发现与 replan 简报输入仍留在 explore capability 或未来的
  控制面 explore/read-model 边界。

这使拓扑卡片、表格与图视图贴近 dashboard，同时不把展示代码变成视觉与 replan
的证据源。

## 静态站点交付契约

`loopx presentation package` 把已构建的公开安全站点目录变成 provider-neutral
发布工件。该工件始终保持本地可用，并同时携带稳定的 latest 布局与不可变的
`revisions/<revision>/` 快照。该命令把确定性 manifest 与部署回执写入工件；相同
内容与发布参数是语义 no-op。

打包要求调用方提供桌面视觉、移动视觉与链接检查的 `passed` 回执。LoopX 校验
文件 manifest 与常见公开边界泄漏，但不假装运行过调用方的浏览器套件。

```bash
loopx --format json presentation package \
  --site-dir output/site \
  --output-dir output/publish \
  --site-id public-frontstage \
  --revision <public-revision> \
  --publisher github-pages \
  --base-url https://example.github.io/project/ \
  --desktop-visual-check passed \
  --mobile-visual-check passed \
  --link-check passed \
  --execute
```

`--publisher local` 是默认值，不需要网络配置。`github-pages` 是第一个可选 URL
适配器；它只把已准备的工件映射到稳定 latest 与 revision URLs，因此仓库凭据与
Pages 启用在宿主工作流中。宿主部署工件后，`presentation verify-readback` 比较
serve 出的部署回执与本地回执，并持久化一条紧凑校验事件。宿主重新发布工件之前，
用 `presentation rollback` 从保留的 revision 重建 latest。
