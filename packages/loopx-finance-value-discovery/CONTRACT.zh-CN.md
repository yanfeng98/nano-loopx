# 统一 Finance Gate 契约

`finance_case_contract_v1` 是本扩展评估的研究案例共用的 provider-neutral 契约。它不收集市场数据,也不计算财务指标。收集器与指标 provider 产生冻结的类型化观察;关卡引擎把这些值与契约拥有的规则和阈值比较。

## 所有权

| 组件面 | 所有者 | 职责 |
| --- | --- | --- |
| 契约 | Finance 扩展 | revision、截断、冻结身份与阈值、关卡顺序、安全边界 |
| 观察 | 收集器或指标 provider | 公开证据引用和一个类型化值、缺失标记或冲突标记 |
| 关卡引擎 | Finance 扩展 | 类型化比较、确定性短路、判定 |
| Replay harness | Finance 扩展 | 规范哈希与逐字节一致的重新评估 |
| Revision 晋升 | 人工所有者 | 历史、walk-forward 与影子评审后批准 |

该契约刻意比任何单个方法更小。去 beta、质量、估值或市场制度方法可以选择不同的关卡 id,但都必须使用相同的类型化比较与转换规则。布尔与字符串关卡支持相等;数值关卡支持相等与有序比较。provider 不能声明自己的通过或失败结果。

## 归因与行业叠加层

分层 beta 归因是对调用方提供的时点观察的确定性算术。已解释顺序冻结为市场、利率、行业、窄同业、周期与事件。只有当每个成分都被观察到时,残差才计算为总变动减去全部六个已解释成分。`de_beta_residual` 关卡必须使用该计算值;独立或矛盾的残差观察会被拒绝。归因不估算因子,也不选择来源。它确实执行绑定的关卡输入,并要求观察窗口满足契约截断,然后才能报告完整结果。顶层 `disposition` 保留关卡判定(包括 `rejected`),而 `completeness` 独立报告关卡证据与全部六个成分是否完整。

一次归因绑定到一个被关卡约束的案例身份。关卡输入携带所评估案例的 `case_id` 与 `subject_ref`,而归因的 `case_reference` 必须与两者都匹配。因此,一个通过的关卡不能复用于把另一个案例或另一只证券的归因呈现为研究完成。`observation_window` 必须是位于契约冻结的 `[point_in_time, evaluation_as_of]` 窗口内的真实 ISO-8601 日期,因此畸形或未来窗口不能被呈现为完成。

行业指标 pack 是同一案例契约上的语义叠加层。pack 可以要求指标 id、值类型与允许的运算符方向。它不能提供阈值、重排公共来源或截断关卡、重新解释缺失或冲突证据,或改变晋升权威。必需的 `source_lineage` 与 `point_in_time` 关卡是 provider-neutral 的 `boolean eq true` 权威关卡;pack 输入不能保留它们的 id 却改变它们的类型、运算符或引用语义。指标阈值仍留在冻结的案例契约内,观察仍经过公共关卡引擎。

## 关卡状态

| 结果状态 | 含义 | 判定 |
| --- | --- | --- |
| `passed` | 证据满足冻结关卡 | 继续 |
| `failed` | 证据证伪冻结关卡 | `rejected` |
| `missing` | 必需证据缺失 | `insufficient_evidence` |
| `conflict` | 有效证据相互矛盾 | `insufficient_evidence` |
| `not_run` | 更早的关卡已阻止评估 | 无新结论 |

观察必须与有序的 `gates` 列表精确匹配。`observed` 值是类型化的,与冻结规则比较产生 `passed` 或 `failed`。provider 也可以报告 `missing` 或 `conflict`。第一个 `failed`、`missing` 或 `conflict` 结果会阻断该案例,后续每个观察都必须为 `not_run`。

证据引用是状态相关的:`observed` 观察至少需要一个引用,`conflict` 观察至少需要两个引用,`not_run` 观察不得包含任何引用。

在阻断之后运行后续关卡会被拒绝为无效输入,而不是被静默接受。

通过全部关卡只意味着 `eligible_for_research_successor`。它绝不意味着方法晋升、投资建议或交易许可。

## Replay

replay receipt 绑定三个 SHA-256 值:

- 规范化契约;
- 完整输入,包括证据引用;
- 在附加 receipt 之前的评估。

规范化使用排序键的紧凑 ASCII JSON。replay 重新计算评估,并要求哈希匹配加上逐字节一致的规范输出。变更阈值、截断、观察、原因或结果都会失败关闭。

## 兼容性

现有的 `finance_value_discovery_input_v0` reducer 与 `finance_value_discovery_extension_v0` provider 协议仍然受支持。`finance_case_gate_input_v1` 现在要求一个命名案例主体的 `subject_ref`,因此关卡输入包必须声明它所评估的主体;这把案例身份端到端绑定起来。`finance_value_discovery_input_v0` 包不会被重新分类,也不会新增字段。
