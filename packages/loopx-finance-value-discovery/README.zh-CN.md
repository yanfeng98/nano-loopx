# Finance Value Discovery

状态:同仓库可选的 LoopX 扩展示例。

## 定位

- 扩展 id:`loopx-finance-value-discovery`
- capability 注册:无
- 位置:`packages/loopx-finance-value-discovery/`

这个可选工作流拥有自己的命令与包契约。LoopX 不需要 provider-neutral 的财务能力,因此安装该扩展不能把 `finance-value-discovery` 加进 capability 目录。该包拥有自己的依赖、安装、doctor、启用与升级生命周期。

## 契约

reducer 接受一个冻结的 `finance_value_discovery_input_v0` 对象,并发出 `finance_value_discovery_packet_v0`。它不发起任何网络请求。独立的收集器可以准备公开证据卡,但连接器输出是输入证据,不是被接受的事实。

附加的 [`finance_case_contract_v1`](CONTRACT.md) 组件面把一个方法的冻结契约与 provider 观察分开。其确定性关卡引擎在第一个失败、缺失或冲突的关卡处停止。replay harness 用规范 SHA-256 receipt 绑定契约、输入与结果。通过全部关卡只意味着一个案例有资格进入有界的研究后继;它不能晋升一个 revision、给出建议或执行交易。

两个 P1 叠加层在不削弱该契约的前提下复用:

- `finance_beta_attribution_input_v1` 把冻结的总变动分解为市场、利率、行业、窄同业、周期、事件与计算残差各层。如果任何已解释成分缺失或冲突,则不计算残差。
- `finance_metric_pack_input_v1` 选择一个捆绑的行业指标词汇表。pack 定义必需的指标 id、值类型与允许的比较方向。它们不包含阈值,也不评估 provider 声明的通过/失败状态。

该包强制执行:

- 在命名候选被选中之前进行截面筛查;
- 去 beta 路径至少要有三个不相关的筛查组;
- 冻结的控制项以及至少两个同组控制项,之后一个特异性的去 beta 声明才能推进;
- 每张卡都有支撑事实与反证;
- 时点来源截断、终态风险、稀释与完全稀释估值关卡;
- 最多一个后继,无阈值放宽与持续关注。

它拒绝原始 provider 正文、私有路径、凭据、账户或投资组合材料、未来日期证据、不支持的字段与格式错误的公开 URL。它从不发出投资建议、目标价、交易或自动关注。

## Public-Safe 研究组件面

该扩展还声明了一个 public-safe 的 `investment-research` 展示组件面。`finance_research_dashboard_input_v0` 包验证 Finance 语义,并映射到 finance 所有的 `decision_research_dashboard_v0` 视图。契约保持 beta、周期、公司价值与残差 alpha 推理相互独立;要求支撑证据、反证、论点 breakers、情景假设与冻结事件关卡;并可以发布紧凑的研究产物指针,附带用于产出它们的证据引用。产物指针不包含原始内容或本地路径。该视图保留证据不足或被拒绝的结论,同时不允许自由标签或语气覆盖规范裁定、零已验证 alpha 或未变更的活动方法,也不把它们变成投资推荐。

[`examples/research-dashboard.json`](examples/research-dashboard.json) 是一个完全合成的 public-safe 示例。它刻意报告零已验证的公司 alpha 与未变更的活动方法。

在单独安装、启用并通过 doctor 验证该扩展之后,用以下命令发布一个验证过的本地投影:

```bash
loopx extension publish-projection \
  loopx-finance-value-discovery investment-research \
  --input-json owner-research.json \
  --execute \
  --format json
```

发布是显式且本地的。它验证并存储一个绑定到当前活动扩展 revision 的只读投影。被禁用、doctor 过期、缺失或 revision 不匹配的扩展投影会从 status 与 Dashboard 组件面隐藏。发布不会安装或启用扩展、激活或替换 Finance 方法、消耗 LoopX quota、消耗学习队列、创建交易或下单。

## 演练方法:PayPal 如何浮现

历史性的 PayPal 演练从一个全新的去 beta 侦察开始,而不是从 PayPal 论点开始。有界宇宙覆盖五个不相关组:传统支付、包装、农业周期股、人力外包与货运。第一遍比较使用公开申报事实与调整后价格历史,比较增长、利润率、现金转化、资产负债表韧性、回撤与残差表现。

PayPal 之所以浮现,是因为其经营与现金流质量明显优于其价格历史位置所暗示的程度。FIS、GPN 与 WEX 作为控制项留在包中。这一点很关键:控制项把可能的 PayPal 特异性残差从广泛传统支付板块降级中分离出来,并让 GPN 的价值陷阱风险保持可见,而不是把整个组合平均成一个看多故事。

这次筛查没有得出投资结论。它只产生一个有界后继:审查品牌结账与交易利润率的持久性、自由现金流质量、信用敞口、债务与流动性、稀释与回购、集中度、竞争、监管与估值历史。可复用的教训是这个顺序:

```text
broad blind screen
  -> named candidate
  -> frozen peer controls
  -> idiosyncratic-versus-group-wide test
  -> filing falsification
  -> one successor or close
```

[`examples/paypal-debeta-discovery.json`](examples/paypal-debeta-discovery.json) 把该方法编码为说明性历史包。它不是对 PayPal 或任何控制公司的当前观点。

## 安装与运行

安装扩展包,然后向 LoopX 扩展运行时注册其 manifest:

```bash
python3 -m pip install ./packages/loopx-finance-value-discovery
loopx extension install \
  --manifest packages/loopx-finance-value-discovery/extension.toml \
  --execute \
  --format json
```

通过 LoopX 的受管理运行时调用已启用的扩展:

```bash
loopx extension run loopx-finance-value-discovery \
  --input-json packages/loopx-finance-value-discovery/examples/paypal-debeta-discovery.json \
  --execute \
  --format json
```

同一个受管理入口也接受 `finance_case_gate_input_v1` 对象:

```bash
loopx extension run loopx-finance-value-discovery \
  --input-json packages/loopx-finance-value-discovery/examples/finance-case-gates-v1.json \
  --execute \
  --format json
```

分层归因与行业 pack 使用同一个受管理入口:

```bash
loopx extension run loopx-finance-value-discovery \
  --input-json packages/loopx-finance-value-discovery/examples/beta-attribution-v1.json \
  --execute \
  --format json
loopx extension run loopx-finance-value-discovery \
  --input-json packages/loopx-finance-value-discovery/examples/software-metric-pack-v1.json \
  --execute \
  --format json
```

开发者可以直接检查或重放一次冻结评估:

```bash
loopx-finance-value-discovery evaluate \
  --input-json packages/loopx-finance-value-discovery/examples/finance-case-gates-v1.json
loopx-finance-value-discovery replay \
  --input-json packages/loopx-finance-value-discovery/examples/finance-case-gates-v1.json \
  --expected-json evaluation.json
loopx-finance-value-discovery list-packs
loopx-finance-value-discovery attribute-beta \
  --input-json packages/loopx-finance-value-discovery/examples/beta-attribution-v1.json
loopx-finance-value-discovery evaluate-pack \
  --input-json packages/loopx-finance-value-discovery/examples/software-metric-pack-v1.json
```

该 manifest 不声明任何权限:该工作流是对调用方提供的冻结公开证据的确定性 reducer。它不执行任何收集或其他有副作用的操作。有权限的 Finance 工作必须使用带显式类型化权威决策的 capability 或领域命令,而不是独立运行。

没有 `value-connectors` Finance 执行路径。该包二进制是 provider 实现与开发者调试组件面,不是受支持的管理入口。调用方通过 `loopx extension` 安装并调用这个独立版本化的扩展。

已退役的 `finance_market_snapshot` value-connector 选择器只保留为升级用的机器可读迁移墓碑。它们指向本扩展,但不能执行它、注册 capability,或隐式安装不存在的 provider。
