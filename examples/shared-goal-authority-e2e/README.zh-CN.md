# Shared-goal-authority E2E 阶段阶梯

这是 [RFC: LoopX 共享控制面权威与可插拔状态 provider v0](../../docs/architecture/rfcs/shared-goal-authority-state-provider-v0.md) 的增量端到端阶梯。每个已完成的 RFC 阶段结论是一行;每行要么通过真实 `python -m loopx.cli`(`real_cli`)驱动产品,要么运行保留的存储级探针(`store_direct`)。该阶梯不添加任何产品路径,只通过生产 TypeScript `FileAuthorityStore` 读取候选,并且只要某选中行未验证就绝不报告绿色。

```bash
python examples/shared-goal-authority-e2e/ladder.py            # 这里退出 1:实时行未验证,对等行待定
python examples/shared-goal-authority-e2e/ladder.py --allow-unverified --allow-pending
python examples/shared-goal-authority-e2e/ladder.py --stage 2c1 --report-json ladder-report.json
python examples/shared-goal-authority-e2e/ladder.py --list
```

pytest 投影是 `tests/control_plane/test_shared_goal_authority_e2e.py`;在那里,未验证行以 `unverified: <reason>` 跳过,POSIX 专用行在 Windows 上跳过。五条断言已由 `tests/control_plane/test_local_authority_shadow_cli_e2e.py` 通过同一产品路径固定的 `s2c1.*` 行(配置往返、默认关闭隔离、候选失败、崩溃间隙、双运行时根)在默认 CI 投影中跳过,以保持在 pytest job 预算内;`LOOPX_LADDER_FULL=1` 让它们在 pytest 中运行,而示例 runner 总是运行每一行。

## 行

| 行 | 阶段 | 路径 | 关卡 | 断言 |
| --- | --- | --- | --- | --- |
| `s0.file_matrix_twelve_rows` | 0 | store_direct | deterministic | `examples/nokv-shadow-provider/live_e2e.py` 恰好报告十二个已知文件 provider 场景行,全部为真 |
| `s0.nokv_live_matrix` | 0 | store_direct | env:nokv_legacy | 同样的十二行加 `restored_lineage_fails_closed` 在实时 NoKV 栈上为真,且文件/NoKV 结果一致 |
| `s1.cli_document_decodes_through_ts_store` | 1 | real_cli | deterministic | 三次 CLI 写(`todo add`、`task-lease acquire`、`todo update`)通过 `FileAuthorityStore` 回读:`loadAuthority` 在游标 `3` 处加载,分页 `scanCommitted` 依次产出三个 `observation_id`,`readReceipt` 找到第一个 |
| `s2a.nokv_live_qualification` | 2a | store_direct | env:nokv_authority | 针对带新鲜 tenant/goal 对的既有 workbench 运行已合并的 `examples/nokv-authority-store/live-qualification.ts --execute-live`;要求 `ok=true`、单节点存储一致性范围、每个检查 `passed`、NoKV SDK `0.11.0` / API `1`,且无晋升或可用性声明;证据携带检查 id、计数与配置及 workbench 摘要前缀,绝不携带配置值或 workbench 名称 |
| `s2b.postgresql_conformance_live` | 2b | store_direct | env:postgresql | node TAP 报告器下的 `postgresql_authority_store.integration.test.ts`:`# pass >= 9`、`# fail 0`、`# skipped 0` |
| `s2c1.configure_enable_disable_roundtrip` | 2c1 | real_cli | deterministic | `configure-goal` preview 不写,enable 写,捕获一个 todo 与一个 lease 的观察,回读摘要 `enabled/file_one_way`,disable 写,之后的写既不能观察也不触碰候选字节 |
| `s2c1.every_writer_family_captures` | 2c1 | real_cli | deterministic | handoff 模式设置,todo add/update/complete/supersede/capture-followups/archive-completed 与 task-lease acquire/renew/transfer 各自携带 `outcome in {captured, replayed, ambiguous_reconciled}`、`primary_writeback_preserved=true`、`provider_to_local_writes=false`、`candidate_read_for_decision=false`;幂等重新获取不携带 `authority_shadow`;候选 `cursor == 捕获数`,操作 id 等于观察 id,head 中无时间活跃 lease,head todos 等于 `todo list` |
| `s2c1.default_off_isolation` | 2c1 | real_cli | deterministic | 默认关闭的 goal 返回与已观察 goal 相同的响应字段,不携带 `authority_shadow`,也不创建 `authority-shadow/` 目录 |
| `s2c1.candidate_failure_preserves_primary` | 2c1 | real_cli | deterministic | 被阻塞的候选目录产生 `outcome=failed`、`reason_code=shadow_observation_failed`,且已提交的 todo 在主状态中 |
| `s2c1.crash_gap_loses_observation` | 2c1 | real_cli | deterministic (POSIX) | 一个 writer 在观察锁持有时被 SIGKILL,提交了它的 todo 但未留下候选文档;下一次写捕获完整两 todo 快照,而不声称 outbox 或关联 |
| `s2c1.dual_runtime_root_consistency` | 2c1 | real_cli | deterministic | 当 `common_runtime_root` 不同于 `--runtime-root` 时,todo add、task-lease acquire、todo update、capture-followups 与一次 lease 完成都观察进同一个存储身份;head 持有两个 todo 与已释放 lease;registry 根既不增加候选血缘也不增加 lease 状态 |
| `s2c1.migration_seeds_new_lineage` | 2c1 | real_cli | deterministic | `migrate-state` dry-run 规划播种而不写;execute 在游标 `1` 处播种一条新鲜 `file:` 血缘,不携带遗留身份、revision、来源路径或私有字节 |

待定行在报告中声明为 `pending`,绝不计为通过,并且除非传入 `--allow-pending`,否则它们阻塞绿色退出。Stage 2C 对等行是待定的:`s2c2.outbox_prepared_then_committed_entries`、`s2c2.drain_idempotent`、`s2c2.sigkill_between_primary_write_and_drain`、`s2c2.sigkill_mid_drain`、`s2c2.rollback_with_pending_entries`、`s2c2.parity_equal`、`s2c2.parity_divergent_detects_foreign_edit`、`s2c2.migration_seeds_and_drains`、`s2c2.growth_measurement_gate`(直到 Stage 2C 对等 PR 落地)。

## 关卡与环境变量

| 关卡 | 要求 | 缺失时的未验证原因 |
| --- | --- | --- |
| `deterministic` | 无(CLI 的 TypeScript 运行时与回读探针需要 `PATH` 上的 `node`) | 探针无法运行时为 `node_missing` |
| `env:postgresql` | `LOOPX_TEST_POSTGRES_URL` 加 `node_modules/pg`(`npm ci`) | `postgres_url_missing`、`pg_dependency_missing`、`node_missing` |
| `env:nokv_legacy` | `NOKV_COORDINATION_LIVE=1` 以及 `NOKV_ETCD`、`NOKV_ETCD_PREFIX`、`NOKV_ROOT_ID`、`NOKV_BUCKET`、`NOKV_OBJECT_ENDPOINT`、`NOKV_OBJECT_ROOT`、`NOKV_OBJECT_KEY`、`NOKV_OBJECT_SECRET`;`nokv` SDK 可导入 | `nokv_live_env_missing`、`nokv_coordination_live_not_enabled`、`nokv_sdk_missing` |
| `env:nokv_authority` | `LOOPX_NOKV_AUTHORITY_LIVE=1`(该探针写入持久测试数据)、`LOOPX_NOKV_AUTHORITY_CONFIG_JSON`(被忽略的 NoKV 客户端配置的绝对路径)、`LOOPX_NOKV_AUTHORITY_PYTHON`(解析出 NoKV SDK 0.11.0 的 Python 可执行文件的绝对路径)、`LOOPX_NOKV_AUTHORITY_WORKBENCH`(一个既有 workbench);`PATH` 上的 `node` | `nokv_authority_env_missing`、`loopx_nokv_authority_live_not_enabled`、`nokv_authority_config_missing`、`nokv_authority_python_missing`、`node_missing` |

POSIX 专用行在 Windows 上报告 `unverified/posix_only`。

## 报告与退出策略

报告 schema 是 `loopx_shared_goal_authority_e2e_report_v0`:
`rows[]`(`status in {pass, fail, unverified}`、`reason_code`、public-safe 的 `evidence`、`duration_ms`)、`pending[]`、`summary{pass, fail, unverified, pending, executed, privacy_violations}`、`bindings{loopx_commit, loopx_tree_dirty, probe_sha256[], nokv_client_config_sha256, nokv_sdk_version, postgres_url_sha256_prefix, pg_package_version}`(未知时为 `null`)以及 `exit_policy`。

退出码为 `0` 当且仅当 `fail == 0` 且 `privacy_violations == 0` 且(`unverified == 0` 或 `--allow-unverified`)且(`pending == 0` 或 `--allow-pending`):一个永远未执行的选中行,无论被关卡限制还是声明为待定,都是未履行的义务,因此 `--row s2c2.parity_equal` 以零执行退出 1,而混合选择即使其可执行行通过也退出 1。`--list` 只打印注册表,从不断言验证。隐私扫描在完成后的报告上运行:任何出现的临时根、主目录、仓库路径、PostgreSQL URL、NoKV 配置值或 NoKV 权威输入路径都会把该行改写为 `fail/privacy_violation`;限于 `bindings` 块内的泄漏会把每个绑定置空,标记 `bindings.privacy_violation`,并仍然通过 `summary.privacy_violations` 退出 `1`,这是任何标志都不能放松的。因此证据只携带计数器、游标、结局令牌与 sha256 前缀。

## 后续 PR 必须提供的测试 seam

待定的 `s2c2.*` 行将针对这些 seam 实现;不暴露它们的 Stage 2C 对等 PR 无法通过阶梯验证:

- `<runtime>/authority-shadow/outbox/<goal>/drain` 处的一个 drain 锁文件,使阶梯能像今天持有 `<runtime>/authority-shadow/file/<goal>/observation` 一样,用 `loopx.file_lock.exclusive_file_lock` 持有 drain 窗口,然后在 drain 之前或期间 SIGKILL 一个 writer;
- `<runtime>/authority-shadow/outbox/<goal>/` 下每个 outbox 条目一个文件,带 prepared-then-committed 标记,使待定条目可计数,且带待定条目的回滚可从磁盘观察;
- 发出 JSON(含 `drained_count`、`cursor_before`、`cursor_after`、`parity_verdict` 以及来源与候选摘要)的 `drain` 与 `verify` 产品命令,使 parity-equal 与 foreign-edit 行能断言类型化字段而不是散文;
- 这些相同命令必须像 `todo` 与 `task-lease` 那样解析运行时根(`effective_runtime_root`),使 `s2c1.dual_runtime_root_consistency` 为观察钩子证明的单血缘保证对 drain 与 verify 同样成立。
