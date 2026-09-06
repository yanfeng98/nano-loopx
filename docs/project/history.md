# LoopX 项目历史


本页记录改变 LoopX 身份、治理或稳定产品方向的公开里程碑。它不是逐提交 changelog。普通发布变更属于 [GitHub Releases](https://github.com/huangruiteng/loopx/releases) 与 [update notes](../update-notes/README.md)。

## 公开时间线

### 2026-05-31：公开仓库开始

[初始公开提交](https://github.com/huangruiteng/loopx/commit/7dcdc9dc79226d157ba57d3e8ff4bae664f020c1)
引入 goal-harness 脚手架。核心想法当时已经存在：把长程 agent 工作锚定在显式 goal 状态中，而不是依赖一次性的瞬态 session。

### 2026-06-17：贡献者工作 Surface 出现

[贡献者任务板](https://github.com/huangruiteng/loopx/commit/7bb315246e3082965e2763530cf0da6d37c4e320)
让公开、可认领的工作成为仓库 surface。这为超越创建者本地开发 loop 的贡献确立了一条路径。

### 2026-06-21：产品变为 LoopX

[LoopX 产品 surface 重命名](https://github.com/huangruiteng/loopx/commit/320fbedaa4d90bd02e5149a8fd9a46c9a498c650)
给了控制面现在的公开名称。视觉身份资产于 [2026-06-22](https://github.com/huangruiteng/loopx/commit/ac13d32ab5668b92ef64ddb00a9a41110ae3da76) 跟进。

### 2026-06-23 至 2026-06-24：外部贡献进入主线

早期公开贡献包括 [#597](https://github.com/huangruiteng/loopx/pull/597) 中的 hardware-agent showcase 文档与 [#604](https://github.com/huangruiteng/loopx/pull/604) 中的 Claude Code CLI LoopX 模式，均由 [`liangsalt`](https://github.com/liangsalt) 贡献。这段时期证明仓库可以通过同一公开评审路径接受产品与文档工作。

### 2026-07-02：公开发布归档开始

[LoopX v0.1.3](https://github.com/huangruiteng/loopx/releases/tag/v0.1.3) 是当前 GitHub 发布归档中第一个保留条目。随后的 v0.1 发布在安装、控制面契约、验证与公开文档上迭代。

### 2026-07-10：Agent 协调转向 Peer Runtime

[#1787](https://github.com/huangruiteng/loopx/pull/1787) 把 agent 层级从 runtime authority 模型中移除。Claims 变成软路由与写回信号；实际执行仍由 quota、gates、capabilities、写范围与显式 handoff 状态治理。

### 2026-07-11：v0.2 控制面发布

[LoopX v0.2.0](https://github.com/huangruiteng/loopx/releases/tag/v0.2.0)
晋升 peer-agent runtime，并扩展长期 issue-fix、PR lifecycle、Explore 与控制面验证 surface。v0.2 系列在公开 [release archive](https://github.com/huangruiteng/loopx/releases) 中继续。

## 本历史如何维护

- 只有当里程碑改变项目身份、治理、发布线或持久产品契约时才添加。
- 每个事实声明都链接到公开 commit、pull request、tag 或 release。
- 贡献者归属使用 Git 历史与 GitHub 的贡献者图；不要从提交计数推断人类身份或 maintainer authority。
- 私有运营上下文、原始轨迹、内部链接与本地路径远离公开时间线。

作者与贡献者归属见 [AUTHORS.md](https://github.com/huangruiteng/loopx/blob/main/docs/project/authors.md)，当前 maintainer 模型见 [Governance](https://github.com/huangruiteng/loopx/blob/main/.github/GOVERNANCE.md)。
