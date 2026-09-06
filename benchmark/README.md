# Benchmark 研究工作区

这是 LoopX 用于 benchmark 实践与窄 runner 示例的活动工作区。其权威依据是 [Long-Horizon Harness Benchmark and Research Program v0](../docs/architecture/rfcs/long-horizon-harness-benchmark-research-program-v0.md)。

该工作区遵循三条规则:

1. benchmark 原生的 task、runner、verifier 与 score 语义保持权威;
2. 当前真实运行实践优先于遗留 LoopX benchmark 抽象;
3. 只有通用代码与 public-safe 结论进入此目录。

可复用的产品策略留在 [`benchmark-toolkit`](../docs/capabilities/benchmark-toolkit/README.md)。该 toolkit 拥有 provider-neutral 的权限、artifact 与完整性边界。本目录可以包含精简示例与实践笔记,但它不会作为第二个 LoopX Python 包安装,也不授予执行或发布权威。

## 工程构建图

规范工程计划是[英文研究 RFC 第 11 节](../docs/architecture/rfcs/long-horizon-harness-benchmark-research-program-v0.md#11-engineering-construction-plan)与[中文第 11 节](../docs/architecture/rfcs/long-horizon-harness-benchmark-research-program-v0.md#11-engineering-construction-plan)。它把仓库就绪与 benchmark 结论分开:

- **E0--E1:**类型化契约、public/private 边界、原生 runner 预检与一个一致性切片;
- **E2:**experiment-board 生命周期、并发接纳、精确运行时观察、连续性、协调与安全关闭;
- **E3:**预注册的匹配臂、处理保真、完整性、可计数性与不确定性;
- **E4:**跨 benchmark 复现与非 benchmark 产品资格判定。

活动工作区应把 benchmark 家族的 launch、verifier、scoring 与失败语义保留在 adapter 中,而可复用的权限、完整性、生命周期与 public-safe 投影规则留在 [`benchmark-toolkit`](../loopx/capabilities/benchmark_toolkit/README.md)。贡献者应从有界的合成 fixture 或一致性 seam 开始;实时任务、隐藏评估、凭据、原始轨迹、提交物与未公开对比仍归维护者。工程就绪本身不确立 C2 uplift 结论。

## 当前工作

- [`deepswe/README.md`](deepswe/README.md) 记录当前 public-safe 的 DeepSWE 方法:冻结选择、匹配臂权威、原生 Goal 证明、独立验证、无效运行替换与紧凑证据。
- [`native_codex_goal.py`](native_codex_goal.py) 是 benchmark toolkit 已安装原生 Goal 运行时的兼容导入。可运行的 [`deepswe/run_native_codex_goal.py`](deepswe/run_native_codex_goal.py) 示例把该运行时连接到一个真实 `codex app-server`。Benchmark 家族的 adapter 应导入已安装的运行时及其正式隔离 profile 辅助函数,然后只保留它们自己的隔离、环境桥接、verifier 与 scoring 关注点。该 profile 辅助函数用其已安装 CLI 渲染真实 Goal prompt,并证明 prompt、发现的 skills 与发布快照 CLI 属于同一条固定产品路径。

遗留 runners 与过时包归档在 [`deprecate/benchmark-legacy/`](../deprecate/benchmark-legacy/README.md)。它们只是候选证据,不是新工作的架构。
