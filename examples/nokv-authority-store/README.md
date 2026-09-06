# Stage 2A NoKV AuthorityStore 候选资格判定(仅测试)

此目录包含针对 Stage 2A `NoKVAuthorityStore` 候选的一个显式的、会产生写入的单节点一致性探针。它是**仅测试**。LoopX 不会因为导入这份代码就选择 NoKV,一次成功运行也不会连接运行时 shadow、运行多 Agent canary 或切换权威来源。

集成优先级仍为:

1. 原生、完整的 NoKV CLI 作为主要运营与生产组件面;
2. NoKV Python SDK 作为次要可编程组件面;
3. 可选 sidecar 仅作为这些组件面之外的 adapter,绝不作主要权威 API。

该探针刻意使用当前 Python SDK 桥,因为它是可用的原始字节 CAS seam。它总是启动本检出中经评审的 `NoKVJsonLinesTransport` 与 `nokv_jsonl_helper.py`;它没有 fake、跳过或"未验证但成功"的 CLI 路径。该 helper 只接纳 NoKV SDK `0.11.0` / Python API `1`,成功报告会重复这两个值。

## 它证明了什么

针对一个**已存在**的 NoKV workbench,该探针启动三个独立的 helper 进程并验证:

- 选中的 tenant/goal 路径最初不存在且可以被创建;
- 存储路径的 generation 在精确 generation CAS 下从 1 推进到 2;
- generation-2 CAS 落地后,一次注入的响应丢失从持久的权威信封与操作 receipt 协调,而不是从下层响应协调;
- 每个成功 CAS 响应只有在一次新鲜读取证明当前 workbench 化身中的确切事务后才被接受;
- 针对 generation 2 同时释放的两次写产生恰好一个 generation-3 赢家与一个类型化冲突;
- 失败的操作不会获得持久 receipt;
- 第三个新打开的 transport 读取获胜信封、其完整三条目历史、响应丢失操作的 receipt 与保留的赢家 receipt。

如果 SDK、helper、workbench、后端、CAS 或独立回读无法证明,进程以非零退出。正常测试套件只使用确定性 fakes 测试该序列,**不**算作实时证据。

该探针不证明原子预期化身发布围栏、运行时 shadow 对等、多 Agent canary、权威晋升、HA、failover、重启恢复、容量或性能。NoKV generation 可以在 workbench 重建后重启,因此当前 adapter 通过权威的写后回读失败关闭;阻止过期化身写入本身需要未来的 provider 原语。该探针也不创建 workbench。绿色运行只是 Stage 2A 单节点存储一致性证据。

## 输入

使用当前的 NoKV Python 环境。把客户端配置保留在被忽略的本地文件中;不要提交凭据。静态路由对单节点 NoKV 部署有效——此探针不要求 etcd。以下形态仅供说明:

```json
{
  "root_id": "00000000000000000000000000000000",
  "routing": {
    "kind": "static",
    "endpoint": "127.0.0.1:7412",
    "logical_shard_id": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    "object_namespace_id": "cccccccccccccccccccccccccccccccc",
    "placement_generation": 1,
    "owner_epoch": 1
  },
  "object_store": {
    "kind": "s3",
    "bucket": "qualification-bucket",
    "region": "us-east-1",
    "root": "/loopx-qualification",
    "endpoint": "http://127.0.0.1:9000",
    "access_key_id": "set-in-your-ignored-local-file",
    "secret_access_key": "set-in-your-ignored-local-file",
    "virtual_host_style": false,
    "skip_signature": false
  }
}
```

配置对象是精确键契约。未知的顶层、routing 或 object-store 键会在 SDK 路由配置、object-store 配置或客户端被构造之前失败。特别是,拼写错误的显式凭据不能静默落入 NoKV 的 ambient provider 链。有意省略的可选 S3 凭据字段保留 NoKV SDK 的正常行为。

只传决议出合格 NoKV SDK 的 Python 可执行文件的绝对路径。探针本身把剩余 argv 固定为解释器隔离标志 `-I` 加本检出中经评审的 helper;调用方不能提供包装参数或替代 helper 路径,`PYTHONPATH`、`PYTHONHOME` 或用户 site-packages 也不能把 `nokv` 导入重定向到那个可执行文件自身环境之外:

```text
/path/to/nokv-python-environment/bin/python
```

每次运行选择一个新鲜的 tenant/goal 对。探针拒绝覆盖已有权威信封,并刻意留下它的三代测试信封供检查。使用一次性资格命名空间,或之后按该环境的保留策略用原生 NoKV CLI 移除。

## 运行

从 LoopX 仓库根:

```bash
node --no-warnings --experimental-strip-types \
  examples/nokv-authority-store/live-qualification.ts \
  --execute-live \
  --config-json /path/to/ignored/nokv-client.json \
  --python-executable /path/to/nokv-python-environment/bin/python \
  --tenant-id qualification-tenant-20260902 \
  --goal-id qualification-goal-20260902-01 \
  --workbench existing-qualification-workbench
```

`--execute-live` 是强制性的,并且在任何 helper 启动前检查。退出 0 意味着所有列出的实时检查都通过。任何不可用、失败、歧义、未围栏、已存在或不可读的状态都以非零退出,并带紧凑 JSON 原因;provider stderr、端点、凭据与原始 SDK 错误不会复制进该结果。成功的 JSON 报告包含 `"qualification_scope":"stage_2a_single_node_store_conformance"`、`"nokv_sdk_version":"0.11.0"` 与 `"nokv_api_version":1`。这两个版本字段是 helper 的接纳常量:helper 拒绝对任何其他 SDK 版本或 API 版本打开客户端,因此成功报告蕴含它们,但它们不是从 NoKV 服务器回读的值。该报告只是 Stage 2A/helper 接纳证据,不是 runtime-shadow、canary、HA 或生产就绪证据。
