# 协议契约
> [English](README.md)

这些版本化契约定义面向实现的 LoopX 行为。本迁移期间文件保持扁平，以保留既有链接；本索引按职责分组，使调用方无需扫描时间顺序列表即可找到正确的契约。

## 控制面与状态

- [`active_state_structured_projection_v0`](active-state-structured-projection-v0.md)：活动状态结构化投影 v0
- [`decision_scope_v0`](decision-scope-v0.md)：决策作用域 v0
- [`event_sourced_state_contract_v0`](event-sourced-state-contract-v0.md)：事件溯源状态契约 v0
- [`event_store_migration_bridge_v0`](event-store-migration-bridge-v0.md)：事件存储迁移桥 v0
- [`file_lock_acquisition_v0`](file-lock-acquisition-v0.md)：有界文件锁获取与操作员恢复 v0
- [`global_manager_command_v0`](global-manager-command-v0.md)：全局管理命令 v0
- [`goal_vision_replan_contract_v0`](goal-vision-replan-contract-v0.md)：Goal vision 重规划契约 v0
- [`local_state_write_correctness_v0`](local-state-write-correctness-v0.md)：本地状态写入正确性 v0
- [`loopx_goal_command_v0`](loopx-goal-command-v0.md)：LoopX goal 命令 v0
- [`loopx_turn_v0`](loopx-turn-v0.md)：LoopX Turn v0
- [`quota_cli_hot_path_compaction_v0`](quota-cli-hot-path-compaction-v0.md)：配额 CLI 热路径压缩 v0
- [`quota_planning_horizon_v0`](quota-planning-horizon-v0.md)：有界 agent 规划 horizon v0
- [`rollback_packet_v0`](rollback-packet-v0.md)：回滚包 v0
- [`task_graph_projection_v0`](task-graph-projection-v0.md)：任务图投影 v0
- [`todo_detail_cold_path_v0`](todo-detail-cold-path-v0.md)：Todo 详情冷路径 v0
- [`todo_suggestion_prompt_v0`](todo-suggestion-prompt-v0.md)：Todo 建议 prompt v0
- [`turn_envelope_v0`](turn-envelope-v0.md)：Turn 信封 v0
- [`loop_turn_loop_disposition_v0`](turn-loop-controller-v0.md)：Loop Turn 循环处置 v0

## Agent 与多 Agent 协调

- [`agent_management_projection_v0`](agent-management-projection-v0.md)：Agent 管理投影 v0
- [`agent_material_frontier_v0`](agent-material-frontier-v0.md)：Agent 物料前沿 v0
- [`agent_scoped_evidence_ledger_v0`](agent-scoped-evidence-ledger-v0.md)：Agent 作用域证据 ledger v0
- [`decision_context_architecture_v0`](decision-context-architecture-v0.md)：Decision Context 架构 v0
- [`decision_context_architecture_v0`](decision-context-architecture-v0.zh-CN.md)：Decision Context 架构 v0（中文）
- [`long_horizon_agent_state_protocol_v0`](long-horizon-agent-state-protocol-v0.md)：长程 agent 状态协议 v0
- [`material_lifecycle_architecture_v0`](material-lifecycle-architecture-v0.md)：Material Lifecycle 架构 v0
- [`material_lifecycle_architecture_v0`](material-lifecycle-architecture-v0.zh-CN.md)：Material Lifecycle 架构 v0（中文）
- [`multi_agent_three_layer_minimality_contract_v0`](multi-agent-three-layer-minimality-v0.md)：多 agent 三层最小化契约 v0
- [`multi_agent_visible_launcher_v0`](multi-agent-visible-launcher-v0.md)：多 agent 可见启动器 v0
- [`peer_agent_runtime_v1`](peer-agent-runtime-v1.md)：对等 agent 运行时 v1
- [`peer_supervisor_v0`](peer-supervisor-v0.md)：对等 Supervisor v0
- [`periodic_report_v0`](periodic-report-v0.md)：周期报告 v0
- [`review_batch_v0`](review-batch-v0.md)：评审批次 v0
- [`reward_memory_architecture_v0`](../../../loopx/capabilities/reward_memory/README.md)：Reward Memory 架构 v0
- [`reward_memory_architecture_v0`](../../../loopx/capabilities/reward_memory/README.zh-CN.md)：Reward Memory 架构 v0（中文）
- [`reward_memory_corpus_registry_v0`](reward-memory-corpus-registry-v0.md)：Reward Memory 语料注册表 v0
- [`trajectory_hygiene_v0`](trajectory-hygiene-v0.md)：轨迹卫生 v0

## 运行时与 Host 集成

- [`ark_managed_agent_goal_continuity_qualification_v0`](ark-managed-agent-goal-continuity-qualification-v0.md)：Ark 托管 Agent goal 连续性资格 v0
- [`ark_managed_agent_issue_fix_qualification_v0`](ark-managed-agent-issue-fix-qualification-v0.md)：Ark 托管 Agent issue-fix 资格 v0
- [`codex_app_host_command_registry_v0`](codex-app-host-command-registry-v0.md)：Codex App host 命令注册表 v0
- [`decision_context_advisory_provider_v0`](decision-context-advisory-provider-v0.md)：扩展支撑的、只读的 Decision Context 咨询召回
- [`computer_use_runtime_v0`](computer-use-runtime-v0.md)：Computer-use 运行时 v0
- [`host_integration_plugin_plan_v0`](host-integration-plugin-plan-v0.md)：Host 集成插件计划 v0
- [`host_integration_surface_v0`](host-integration-surface-v0.md)：Host 集成界面 v0
- [`host_mode_plan_v0`](host-mode-plan-v0.md)：Host 模式计划 v0
- [`local_agent_launch_plan_v1`](local-agent-launch-plan-v1.md)：本地 agent 启动计划 v1
- [`openviking_session_memory_adapter_v0`](openviking-session-memory-adapter-v0.md)：OpenViking 会话记忆适配器 v0
- [`protocol_action_packet_codex_cli_wrapper_v0`](protocol-action-packet-codex-cli-wrapper-v0.md)：协议动作包 Codex CLI 包装器 v0
- [`protocol_action_packet_decision_v0`](protocol-action-packet-decision-v0.md)：协议动作包决策 v0
- [`protocol_action_packet_router_comparison_v0`](protocol-action-packet-router-comparison-v0.md)：协议动作包路由器对比 v0
- [`session_runtime_controlled_writeback_v0`](session-runtime-controlled-writeback-v0.md)：会话运行时受控 writeback v0
- [`session_runtime_loopx_projection_v0`](session-runtime-loopx-projection-v0.md)：会话运行时到 LoopX 投影 v0

## 领域能力

- [`auto_research_lane_contract_v1`](auto-research-lane-contract-v1.md)：Auto-research lane 契约 v1
- [`auto_research_role_profile_v0`](auto-research-role-profile-v0.md)：Auto-research 角色 profile v0
- [`auto_research_role_state_machine_v0`](auto-research-role-state-machine-v0.md)：Auto-research 角色状态机 v0
- [`decentralized_auto_research_state_v0`](decentralized-auto-research-state-v0.md)：去中心化 auto-research 状态 v0
- [`content_ops_surface_v0`](content-ops-surface-v0.md)：Content 运维界面 v0
- [`cs_notes_explore_capability_map_v0`](cs-notes-explore-capability-map-v0.md)：CS Notes Explore 能力图 v0
- [`issue_fix_acceptance_loop_v0`](issue-fix-acceptance-loop-v0.md)：Issue-fix 验收循环 v0
- [`value_connector_plan_v0`](value-connector-plan-v0.md)：价值 connector 计划 v0
- [`x_public_channel_ops_v0`](x-public-channel-ops-v0.md)：X 公开 channel 运维 v0
- [`content_ops_item_v0`](content-ops-item-lifecycle-v0.md)：provider-neutral 内容项生命周期 v0
- [`content_ops_queue_projection_v0`](content-ops-queue-v0.md)：只读托管内容队列投影 v0
- [`content_ops_layout_plan_v0`](content-ops-layout-v0.md)：类型化内容布局计划、模板库与验收检查 v0

## 质量、评审与发布

- [`model_behavior_qualification_v0`](model-behavior-qualification-v0.md)：模型行为资格界定 v0
- [`pr_review_command_v0`](../../../loopx/capabilities/pr_review_queue/README.md)：PR 评审命令 v0
