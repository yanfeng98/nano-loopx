---
name: loopx-self-repair
description: Diagnose and repair LoopX control-plane drift or agent behavior drift. Use when a LoopX task makes unexpectedly small progress, follows a stale or contradictory recommended_action, ignores a higher-priority blocked item while doing fallback work, reports vague owner/user gates, loses todo projection, misaligns benchmark treatment with the real product path, mixes temporary artifacts into commits, or when the user asks for root-cause analysis, self-repair, or why the harness/agent behaved unexpectedly.
---

# LoopX Self Repair


使用本技能把意外的 LoopX 行为变成持久修复，而不只是道歉或一次性解释。

## 修复循环

1. **暂停交付选择。** 在控制面事实解释为何该工作有效之前，不消耗 quota，
   也不继续适配器工作。
2. **构建紧凑证据包。** 优先结构化界面：

   ```bash
   git status --short --branch
   loopx --format json diagnose --goal-id <goal-id>
   loopx --format json status --goal-id <goal-id> --limit 20
   loopx --format json quota should-run --goal-id <goal-id> [--agent-id <agent-id>]
   loopx --format json history --goal-id <goal-id> --limit 5
   ```

   `status` 默认为 registry/dashboard 视图，但接受 `--goal-id`，
   当修复需要单 goal 投影时使用。用 `diagnose --goal-id` 获取更丰富的
   goal 特定 agent 推理包。相关时也检查项目本地 registry 与 registry 声明的
   活动状态文件。heartbeat/quota 真相使用共享全局 registry。
3. **分类失败。** 阅读 `references/repair-patterns.md` 并把症状匹配到已知
   模式。如果没有匹配模式，修复后添加一个。
4. **指派负责层。** 区分：
   - agent 行为错误；
   - state 投影或 quota 负载 bug；
   - active-state 编写缺口；
   - benchmark harness 不匹配；
   - docs/process 卫生缺口。
5. **在最底层持久层修复。**
   - 如果是一次性 agent 错误，写回正确的状态/todo，并用更大的有界批次继续。
   - 如果机器投影误导了 agent，修复 CLI/status/quota 投影并添加聚焦冒烟。
   - 如果用户修正改变了 goal 验收、说 agent 错过了预期 loop，或暴露了
     quota/status 中不可见的产品瓶颈，在恢复交付前，通过正常
     `loopx refresh-state --vision-*` 字段写入一个有界
     `goal_vision_replan_contract_v0` 包并带 `replan_trigger_summary`，
     使用与当前通道相同的 `--agent-id`；生成多字段补丁时用
     `--agent-vision-json`。如果下一个可执行步骤已知，同时添加或链接具体
     继任 todo；不要把修正只留在聊天或事件记录中。
   - 如果设计规则缺失，在实现宽泛行为前更新交互模型或 todo 列表。
   - 如果 benchmark 证据不可归因，在声称提升或回退前添加事后 trace/parity
     检查。
6. **恢复前验证。** 运行会捕获该问题的最小冒烟或 CLI 检查；docs/契约变化时
   对变更的公开界面加 `loopx check`。
7. **写回教训。** 更新活动 goal 状态、docs、贡献者任务或本技能，使下次
   相同的失败模式可见。

## 上游 Issue 升级

公开 GitHub issue 是可选的最终升级，不是 self-repair 的默认副产品。仅当负责层
是可复用的 LoopX 产品、CLI、skill、安装器或控制面缺口，且持久的上级跟踪在本地
修复或 PR 之外提供价值时才考虑。

发布任何内容前阅读 `references/upstream-issue-escalation.md`。调用本技能
绝不授予发布许可。守卫路径必须：

1. 拒绝私有、项目特定、仅支持与安全敏感的报告；
2. 把证据压缩到最小的公开安全复现，并用 `loopx check` 扫描草稿；
3. 在创建前按稳定 fingerprint 搜索已打开与已关闭的 issue；
4. 仅在显式当前轮次批准或持久所有者 opt-in 下自动提交；否则显示精确草稿并
   一次性请求确认；
5. 每个修复轮次最多创建一个 issue，然后把既有或新的 issue URL 记录到相关
   LoopX todo/证据写回中。

如果认定、权限、认证、边界扫描或重复搜索不确定，保留草稿并在发布前停止。
当不需要单独 issue 来协调时，优先直接修复或 PR。

## Vision / Replan 写回

当 self-repair 发现 LoopX 没有自行注意到缺失结果、路由或验收条件时，使用有界
vision 契约。该包是从人类或 agent 洞察通往 quota 可见 replan 状态的桥梁：

```json
{
  "schema_version": "goal_vision_replan_contract_v0",
  "state": "vision_drift_detected",
  "vision_patch": {
    "vision_summary": "Name the corrected route or acceptance target.",
    "acceptance_summary": "Name the machine-visible condition that must hold.",
    "replan_trigger_summary": "Name why the current frontier is insufficient."
  },
  "todo_delta": ["create_successor"]
}
```

用正常内联 `refresh-state --vision-summary
--vision-acceptance --vision-replan-trigger` 字段记录，使用执行修复的同一
`--agent-id`。当生成补丁比命令行更清晰时用 `--agent-vision-json`。Replan 只能
通过 typed 语义观察或绑定 `--replan-obligation-id`、typed `--action-kind` 与
稳定 `--target-key` 或 Explore 节点 ref 的原子 Todo 迁移关闭；不要追加第二个
`--autonomous-replan-recorded` 修复 ACK。没有可运行 Todo 的 vision 补丁仍有
价值：当 advancement 前沿为空时，`quota should-run` 可以把其
`replan_trigger_summary` 提升到 `goal_frontier_projection.acceptance_gaps[]`。

如果修复得出结论：现有每 agent vision 仍然正确，用 `--vision-unchanged-reason`
关闭必需 checkpoint，而不是写假补丁。如果材料性 `refresh-state` 既无补丁也无
不变/无需跟进决策，LoopX 应保留带 `decision=missing_required` 的每 agent
`vision_checkpoint_v0`，使同一 agent 的下一个 quota 检查可以进入 replan。
单独的 scheduler 唤醒不是材料性 vision 边界：当 quota 显式把正常接纳的开放
advancement Todo 投影为 `delivery_boundary=in_flight_continuation` 时，使用
投影的结算命令，不要虚构 vision 补丁。下一个 heartbeat 只在有账目的
`outcome_progress` 后保持选择该同一 Todo；Todo 完成、blocker/gap、持久 Next
Action 变更、replan 或终态关闭必须回到严格语义 checkpoint。

## 证据纪律

- 不读取或提交原始私有日志、轨迹、verifier 输出、凭据、内部链接或生产材料。
- 不通过猜测解决矛盾负载。如果 `recommended_action`、
  `goal_boundary.write_scope`、todos 与交互契约不一致，先把它视为投影 bug 或
  状态编写 bug。
- 不让回退工作掩盖主 blocker。当高优先级路径被 gate 但安全回退有效时，
  同时报告具体 gate 与回退进展。
- 不让微小安全步骤成为默认。如果最近几轮都很短或仅表面工作，运行 steering
  审计并增大下一有界批次大小，除非真实 gate 阻止。

## 参考路由

- 已知症状到修复映射，阅读 `references/repair-patterns.md`。
- 受守卫的公开 GitHub issue 升级，阅读
  `references/upstream-issue-escalation.md`。
- 用户/agent/状态通道语义，阅读
  `../../docs/state-interaction-model.md` 与
  `../../docs/concepts/interaction-pattern-catalog.md`。
- quota 与 heartbeat 决策，阅读 `../../docs/quota-allocation.md` 与
  `../../docs/heartbeat-automation-prompt.md`。
- 提交/PR 卫生失败，阅读 `../../AGENTS.md`。
