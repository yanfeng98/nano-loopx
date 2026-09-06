# NoKV 规范协调 provider 参考实现

此目录包含 [RFC: LoopX 共享控制面权威与可插拔状态 provider v0](../../docs/architecture/rfcs/shared-goal-authority-state-provider-v0.md) 的小型、可评审的 NoKV 参考。它是一个契约示例,不是已交付的 LoopX 运行时集成,也不是生产部署声明。

## 范围

该参考存储单个 per-goal **规范协调聚合**,并演练 Stage 3 生命周期:`claim_work`、`renew_work`、`release_work`、过期 lease 的 `reclaim_work`、陈旧围栏拒绝,以及带续接/后继的原子完成。该聚合携带当前权威 revision、claim/lease/fence 状态、存储血统绑定与可重放 receipt 索引。它仍然只是覆盖性参考,不迁移当前 LoopX 运行时,也不把该 provider 晋升为产品真相来源。

以下内容仍在这条分支之外:

- 运行产物与运行历史 ledger;
- 状态与关注投影或缓存;
- quota 策略、记账与强制 ledger;
- 宿主本地路由、调度器状态、锁与运行时绑定;
- 原始证据、transcript、凭据与本地绝对路径;
- Agent IM 投递、唤醒、在场与离线队列。

这些组件面在 RFC 持久化矩阵中有各自的所有权与同步策略。一个 provider 不会仅仅因为它们可能从共享 goal 可见,就取得对这些内容的权威。

## 原子聚合与 receipt 重放

当前协调状态与新接受操作的 receipt 映射发布在**同一个 head CAS** 中。参考不使用 last-envelope 捷径,也不使用单独的 `pending -> head -> finalize` receipt 协议。

单 head CAS 是物理序列化点,不是 goal 范围的领域冲突边界。命令点名它们实际观察到的目标 todo revision 与紧凑的授权、依赖与关卡前置条件。CAS 未命中后,权威重载并再次检查那些事实。如果独立 todo 推进了 head,它内部 rebase 并重试;如果目标 todo 或某个点名前置条件变了,它返回领域冲突。`authority_revision` 保持为 goal 范围的提交与审计序列,而不是必需客户端前置条件。在本参考中,独立 claim 使用 `write_scopes=[]`;非空的跨 todo 范围重叠不在本参考资格的考虑内。内部 rebase 还假定发布者绝不把目标范围的令牌复用于不同授权、依赖或关卡快照。确定性探针使用静态引导输入,不资格化那个动态发布者。

这对历史重试很重要:

1. 操作 A 提交并返回 receipt A;
2. 操作 B 推进 goal head;
3. 调用方丢失第一个响应后重试 A;
4. provider 逐字段返回原始 receipt A,而不再次应用 A,也不移动当前 head。

每个 receipt 索引条目把稳定操作身份绑定到不可变请求的摘要。不同不可变输入复用同一操作身份会失败关闭;它绝不会被分类为幂等重放。

provider 契约保持为仅存储:

```text
load() -> (aggregate | none, provider_generation)
compare_and_put(expected_provider_generation, aggregate)
    -> applied(provider_generation)
     | conflict(current_provider_generation)
     | ambiguous
     | failed
```

`provider_generation` 是不透明存储 CAS 令牌。它不同于聚合的 `authority_revision`,也不同于每个 todo 的 lease epoch;这三个版本域互不推导。

存储 provider 确定性地序列化并存储不透明聚合,并返回 CAS 结果。生产
`loopx.control_plane.coordination` 模块(`head` codec 加 `CoordinationAuthorityExecutor`)负责请求验证、权威 revision、claim/lease 转换、请求摘要绑定与原始领域 receipt;此目录不再承载第二个参考权威。provider 不得检查操作 receipt,也不得发明 lease、gate、quota 或调度决策。

## 文件

- `provider.py`:`NoKVCoordinationProvider`,把不透明的 per-goal 聚合映射到 NoKV 路径 generation CAS。它通过生产的规范 head codec 序列化,因此 adapter 不能分叉摘要/对等基础。
- `probes.py`:由生产 executor 与 head codec 驱动的确定性契约回归;每个 claim/CAS 探针都通过生产的 `validated_head` 往返其持久化 head。只有[证据笔记](../../docs/architecture/rfcs/shared-goal-authority-state-provider-v0-evidence.zh-CN.md)中的检查才是修订后 receipt 契约的合并证据。

## 验证边界

provider 映射固定到 NoKV
[`3d75d96965`](https://github.com/NoKV-Lab/NoKV/commit/3d75d96965)(0.11.0 线)。在该基线上,Python `publish_bytes` 组件面接受 create-only 或替换 CAS 的 `expected_generation`,并暴露可选发布 `operation_id` 与 `artifact_revision_id` 输入;`read` 与 `stat` 返回该 adapter 视为 `provider_generation` 的路径 `generation`。从 NoKV 0.11.0 起,SDK 对缺失路径抛出 `FileNotFoundError`,对 create-only 冲突抛出 `FileExistsError`;其他所有客户端失败都是 `RuntimeError`。adapter 只按异常类分类:`FileNotFoundError` 是唯一缺失信号,读路径上的其他任何客户端失败都会抛出类型化 `ProviderUnavailableError`,而不是伪装成未初始化 goal 或逃逸成裸 `RuntimeError`。错误散文永远不是通道——真实的非缺失失败携带如 `invalid root route: root placement does not exist` 之类的消息——而用这种散文报告缺失的 pre-0.11 SDK 无法路由 post-#465 控制面,因此落在固定基线之外。`contract.nokv_adapter_exception_mapping` 用引发 0.11.0 异常类与真实故障消息形态的 fake clients 离线固定该分类。

新的协调 provider 句柄必须通过 `open_nokv_coordination_provider(...)` 接纳。NoKV 在构造 `Client` 时执行路由接纳,在普通 provider 构造函数分类失败之前。adapter 自有的 helper 把那个急切失败映射为同一个 `ProviderUnavailableError`,不执行协调写,也绝不回退到文件 provider。实时矩阵对每个新 provider 句柄都使用该路径。仅用于配置测试工作区与快照的独立客户端不在该 provider 契约内,不能执行权威命令。
`contract.nokv_fresh_client_failure_is_typed` 同时守卫构造期与构造后的故障。

该映射曾在该 pin 上对一个真实 NoKV 栈(etcd、S3 兼容对象存储、`nokv serve` 与从同一 commit 构建的 `nokv-python`)手工演练一次:adapter 动词与第 10 节检查 1 到 9 都带着两个独立客户端句柄通过了。那次运行在这里记录为仅针对映射的证据;它不是合并关卡的一部分,也不资格化重启、恢复、HA 或性能。在 NoKV 0.11.0 之前构建的 SDK 无法解码 0.11.0 控制面路由记录,因此更早的 `90883d13539e31185f0d78131989fb51f2dbd7e` 审计基线不再是可用 pin。

实时资格判定是脚本化且可重复的:`live_e2e.py` 通过生产 `CoordinationAuthorityExecutor` 针对文件支撑的控制 provider 运行十二个共享生命周期场景(包括 renew、宽限期后 reclaim、陈旧围栏拒绝、原子完成/后继、竞争、重放、丢失响应、保留与 revision 推进),并在 `NOKV_COORDINATION_LIVE=1` 且栈变量已设置时针对本 NoKV provider 运行。仅 NoKV 的一行执行一次真实的 commit/snapshot/restore,并证明恢复的血统以 `store_lineage_mismatch` 失败关闭。没有可达栈时 NoKV 行报告未验证,脚本保持绿色,因此它是证据工具,不是合并关卡。

```bash
python3 examples/nokv-shadow-provider/live_e2e.py
```

从仓库根运行合并相关的确定性回归:

```bash
python3 examples/nokv-shadow-provider/probes.py contract
```

它必须证明以下全部:

- 只有显式引导的、可运行的 todo 才能被认领;
- A 应用,B 推进 head,重建的权威重放 A;
- 重放逐字段返回 A 的原始权威 receipt;
- 重放让当前 revision 与聚合保持不变;
- 同一操作身份配不同语义请求被拒绝;
- 仅传输层的重试元数据不改变操作身份;
- 对同一 todo 的竞争 claim 只有一个赢家;
- 独立 todos 上的并发 claim 在内部 CAS 重新验证与 rebase 后都成功,限定在参考的空写范围边界内;
- 过期目标或点名前置条件返回领域冲突;
- 有界的无关争用失败时不创建 receipt,也不假装目标 todo 冲突;
- pre/post-CAS 故障与歧义结果只能在存储 receipt 或目标重新验证后的后续成功 CAS 中恢复成功;同 generation 无 receipt 时判定为未证明;
- NoKV adapter 把可观察到的每个 SDK 结果(缺失 head、create-only 冲突、陈旧 generation、预发布失败)映射到类型化 provider 动词,绝不把 SDK 异常类泄漏进权威;
- 通过 provider 字节 CAS 回读的、手工演进出的完成 head,投影到与 LoopX 持久完成 seam 相同的类型化续接结果(`successor | no_followup | active_goal`),并对矛盾记录(既有 `no_followup` 又有 successors)、悬空声明的后继、与记录字段矛盾的显式 `completion_continuation`,以及省略显式续接的 done 记录失败关闭,且投影重放稳定。

持久完成探针仍是离线读侧比较。Stage 3 聚焦测试与实时矩阵在参考边界资格化匹配的原子完成写侧。

目前九个结果标签是
`contract.bootstrap_and_preconditions`、
`contract.a_success_b_advance_replay_a`、`contract.operation_identity`、
`contract.competing_claims`、`contract.crash_windows_and_ambiguity`、
`contract.version_domains_and_retain_all`、
`contract.nokv_adapter_exception_mapping`、
`contract.durable_completion_projection` 与
`contract.durable_completion_fail_closed`。

`probes.py` 刻意保持离线;真实栈请使用 `live_e2e.py`。该参考仍不确立多宿主唤醒投递、自动 provider 晋升、HA/failover、receipt 压缩或 GC、生产性能、动态资格投影发布者、非空写范围重叠执行,或完整的 LoopX 状态迁移。RFC 链接的 NoKV 存储面问题仍是生产 canary 保留项;一次绿色的有序单节点演练不会抹除它们。
