---
name: loopx-pr-program
description: "Use when LoopX must manage a multi-PR or multi-MR delivery program across one or more repositories: inventory current change requests, reconcile new/merged/closed or retargeted work, preserve requirement and dependency priorities, maintain a roadmap document, or monitor material lifecycle/check/review changes over time. Use provider-neutral snapshots and one grouped continuous monitor; do not use for deep per-PR code review, approval, commenting, or merge actions."
---

# LoopX PR 项目

> [English](SKILL.md)

把交付项目作为持久 LoopX 状态管理，而不是从聊天记忆重建队列。保持源获取为
provider 本地化，把观察规范化到一个公开契约，只写回材料性迁移。

## 路由请求

当用户要求管理、排优先级、协调、记录或监控多个 pull request 或 merge request
时，使用本工作流。把每个所选 PR 的深度评审路由到 `loopx-pr-review`。把批准、
评论、重跑、分支重定向、关闭或合并路由到正常 provider 特定工作流，并要求
相应权限。

把文档维护与 monitor 创建视为写入。更新路线图或持续监控项目的请求授权这些
限定范围写入；普通状态问题保持只读。

## 从 LoopX 状态开始

在材料工作前启动或加入项目 goal。用当前协调的一个 advancement todo 与重复
观察的一个 `continuous_monitor` todo 表示该项目。不要为每个 change request
创建一个 monitor todo。

使用稳定的 monitor 身份：

```text
task_class=continuous_monitor
action_kind=pr_program_reconcile
target_key=pr-program-<stable-program-id>
cadence=<user cadence or 30m>
```

保留 `claimed_by`、`last_checked_at`、`next_due_at`、`result_hash`、
`consecutive_no_change` 与 `material_change`。安静的 monitor 轮询保持活性，
但不计为交付进展、不重写路线图文档、不消耗进展 quota。

## 获取完整快照

使用当前环境中任何经授权的源码控制读接口。优先一批查询做库存，对变化的项
做定向读取。绝不在本技能、仓库示例、已提交 fixture 或公开证据中编码私有
传输命令、可执行名、凭据、内部主机名或文档 token。

用 [`references/snapshot-contract.md`](references/snapshot-contract.md)
规范化观察。仅在证明所请求的仓库、作者、状态与时间窗口库存穷尽后，才标记
`result_completeness.complete=true`。不完整的当前快照不得让缺席的行看起来
已关闭或已移除。持久化结构化范围 fingerprint 与基线绑定。不要从
不完整快照、或先前与当前范围 fingerprint 不同时推进持久基线或分组 monitor
的 `result_hash`；否则部分页或收窄的查询可能在下次轮询制造虚假的移除/重加
迁移。

把原始与规范化快照存放在被忽略的所有者本地目录（如
`.local/loopx/pr-program/<program-id>/`）。写入前用 `git check-ignore` 验证
路径。如果没有可用被忽略路径，使用临时目录并只在 LoopX 状态中保留脱敏证据
摘要。

## 协调材料变化

在手动比较行之前运行捆绑 delta helper：

```bash
python skills/loopx-pr-program/scripts/diff_snapshot.py \
  --previous <previous.json> \
  --current <current.json> \
  --output <delta.json>
```

首次基线省略 `--previous`。helper 把 lifecycle、draft、target branch、
head revision、checks、review、work item、requirement、theme、priority 与
dependency 变化视为材料性。仅时间戳移动是观察噪声。更新项目判断前，为每个
新增或材料性变化的行读取实际描述、最新评审上下文、checks 与变更文件证据。

不要仅凭标题、编号、作者、年龄或绿的 CI 推断动机或优先级。产品需求设定
优先级。正确性依赖与真实合并 gate 决定优先级内的顺序。当没有 change request
实现请求行为的一部分时，显式记录 requirement 缺口；不要因相邻参数或功能落地
就称 requirement 完成。

## 与集成分支组合

当几个所选 change request 属于同一仓库时，把此项目视图与 LoopX 的
`integration-branch-reconcile` capability 组合。保持所有权切分显式：

- 本技能决定哪些变更属于候选及原因；
- integration-branch 计划记录其有序本地源 refs，并证明组合的确切代码。

不要从每个打开或 P0 change request 自动填充计划。从显式项目范围、依赖顺序与
当前评审意图选择源。通过经授权的宿主工作流刷新本地 refs，然后在配置或同步
integration 分支前验证每个所选 ref 解析到观察到的 `head_sha`。不匹配是源证据
漂移，不是合并陈旧本地 ref 的许可。

用同一分组项目 monitor 读取规范化 change-request delta 与
`loopx integration-branch status --format json`。把 base/source 移动、意外
integration head 与合并冲突视为材料性项目证据。Monitor 轮询保持只读：它可以
报告候选需要协调，但不得自行运行 `sync --execute`。该命令是单独的显式本地
写入，绝不授予推送、重定向、批准或合并远端 change request 的权限。

## 投影项目

保持一个带三部分的规范项目投影：

1. 已完成工作，按产品主题分组；
2. 进行中工作，按产品主题分组，被归档或取代的开发栈嵌套在存续的
   change request 下；
3. 合并优先级，先按显式产品优先级，再按依赖、正确性风险与当前合并 gate。

保持链接在每个紧凑行的末尾。保留目标文档现有的标题、颜色、标注与删除线惯例。
只更新受影响的块，写入后重新获取它们，并验证无关内容与资源块保持不变。

对每个优先级行，区分以下事实：

- 已交付行为与 requirement 覆盖；
- 依赖或建议合并顺序；
- 当前 checks、评审与外部 work-item gate；
- 没有现有 change request 覆盖的缺失实现或验证。

## 写回并继续

在验证过的材料变化之后：

1. 更新分组 monitor `result_hash` 并重置 `consecutive_no_change=0`；
2. 更新路线图并重新获取变更的段落；
3. 用紧凑证据完成协调 todo，仅在存在具体跟进时创建继任者；
4. 用实际交付分类与结果刷新 LoopX 状态；
5. 只在状态与文档写回验证后消耗配额。

安静轮询后，更新 monitor 调度元数据并递增 `consecutive_no_change`；不产生
合成进展事件。

## 公共与私有边界

只提交 provider-neutral 契约、算法与脱敏 fixture。把私有 provider 适配器、
源命令、原始评论、内部 URL、文档 id、快照与组织特定优先级排除在公开仓库外。
在暂存本技能或其资源的变更前，扫描精确路径中的私有主机名、可执行名、凭据、
本地绝对路径与原始运营上下文。
