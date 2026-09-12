# 操作日志索引(2026-09-06,分支 `260906-dev`)

| 序号 | 文件 | 内容 |
|---|---|---|
| 001 | [001-zh-cn-full-translation.md](001-zh-cn-full-translation.md) | 全量文档中文化翻译(113 提交) |
| 002 | [002-zh-only-conversion.md](002-zh-only-conversion.md) | 只保留中文版转换(删除英文,4 提交) |
| 003 | [003-self-review-fix.md](003-self-review-fix.md) | 转换自查与修复(showcase-catalog-smoke) |
| 004 | [004-upstream-merge.md](004-upstream-merge.md) | 上游 7 commits merge(中文融合) |
| 005 | [005-merge-self-review-fix.md](005-merge-self-review-fix.md) | merge 复查与修复(chat server 时序等) |
| 006 | [006-upstream-merge-2.md](006-upstream-merge-2.md) | 上游二次 merge(3 commits,SSH remote)+ 遗留 smoke 适配 |
| 007 | [007-merge2-self-review-fix.md](007-merge2-self-review-fix.md) | 二次 merge 复查与修复(doctor 产品缺陷、42 smoke、demo README) |
| 008 | [008-upstream-merge-3.md](008-upstream-merge-3.md) | 上游三次 merge(11 commits):双语回退、官方中文采用、环境 4 目录初始化 |
| 009 | [009-upstream-merge-4.md](009-upstream-merge-4.md) | 上游四次 merge(22 commits):5 文档重译、pytest 导入模式修复 |
| 010 | [010-upstream-merge-5.md](010-upstream-merge-5.md) | 上游五次 merge(3 commits):官方中文 README 采用、CORS 时序修复 |
| 011 | [011-upstream-merge-6.md](011-upstream-merge-6.md) | 上游六次 merge(1 commit,零冲突) |
| 012 | [012-merge-series-review.md](012-merge-series-review.md) | 连续 merge 系列复查(006–011):发现并修复 2 处信息丢失 |
| 013 | [013-upstream-merge-7.md](013-upstream-merge-7.md) | 上游七次 merge(14 commits,1.0.0 release) |
| 014 | [014-upstream-merge-8.md](014-upstream-merge-8.md) | 上游八次 merge(1 commit,#4005) |
| 015 | [015-remove-kunluncode.md](015-remove-kunluncode.md) | 移除 KunlunCode 宿主适配器(32 文件,+16/−5630;HEAD 基线对照 362 失败同为环境问题) |
| 016 | [016-remove-zcode.md](016-remove-zcode.md) | 移除 ZCode 宿主适配器(14 文件;残留仅历史 changelog,专注测试 + HEAD 基线对照) |
| 017 | [017-remove-codex-ide-plugin.md](017-remove-codex-ide-plugin.md) | 移除 Codex IDE plugin 宿主适配器(22 文件;协议/指南文档静默净删,全量基线对照) |
| 018 | [018-remove-antigravity-cli.md](018-remove-antigravity-cli.md) | 移除 Antigravity CLI 宿主适配器(13 文件;README 行删除,全量基线对照) |
| 019 | [019-remove-codex-app-ssh.md](019-remove-codex-app-ssh.md) | 移除 Codex App over SSH 宿主适配器(~60 文件;枚举手术 + scheduler_hint + benchmark ssh-goal 臂完整退役) |
| 020 | [020-remove-codex-app-desktop-host.md](020-remove-codex-app-desktop-host.md) | 移除 Codex App 桌面宿主接缝(~150 文件;blob 改名 codex_cli + fallback/begin-turn/--codex-app-heartbeat 整套退役,app-server 传输保留) |
| 021 | [021-remove-gemini-cli.md](021-remove-gemini-cli.md) | 移除 Gemini CLI 宿主(skill-facade;~14 文件;catalog/别名/表面映射整套退役,共享 skill-facade 与 cursor-agent 保留) |
| 022 | [022-remove-cursor-agent.md](022-remove-cursor-agent.md) | 移除 Cursor 宿主(skill-facade 终结;27 文件 +39/−935;最后 skill-facade 宿主,`_skill_facade_cli_activation` 与 cursor 测试文件整套退役,附带对齐 README smoke) |
| 023 | [023-readme-code-reconciliation.md](023-readme-code-reconciliation.md) | README 与代码一致性修复(版本号、host 表补齐、7 条命令陷阱、仓库级死链清零、许可证移除;修复崩溃的 docs-governance-smoke 并补齐两个同源守卫;二轮复查扩至全仓库) |
| 024 | [024-remove-ark-managed-agent.md](024-remove-ark-managed-agent.md) | 移除 Ark Managed Agent 宿主(42 文件 +236/−1803;`NATIVE_GOAL_RUNTIME_PROFILES` 收缩保留以免打破 Codex 配额记账、必需技能集常量改名、两个 Ark 测试文件改名保留共享测试、`LOOPX_ENTRY_HOST_SURFACE` 机制整删) |
| 025 | [025-remove-opencode-host.md](025-remove-opencode-host.md) | 移除 OpenCode 宿主(70 文件 +170/−5259;v1 bridge + v2 worker + `.opencode/skills` 投递面;`generic-cli` connector 改名保留以免废掉 Pi、`install_skill_facade` 最后消费者离场、man page 重新生成、先清理本机 22 个托管 facade) |
| 026 | [026-remove-deepseek-harness.md](026-remove-deepseek-harness.md) | 移除 DeepSeek Harness 全部集成(152 文件 +54/−36028,本系列最大;**三处耦合**——两个 host 变体 + `packages/dsh-loopx-plugin` 51 文件整包 + `reliability-diagnostics` 通用能力随之退役;`turn.py`→`dsh_goal_mode` 是无条件深层依赖、`reliability-diagnostics` 是顶级 CLI 命令且在 manpage help-only 表内、showcase 生成产物重生成、`deepseek-v4-flash` 模型名假阳性) |

- 全部操作在 `260906-dev` 分支完成。
- 时间轴: 001 → 002(用户澄清"只保留中文") → 003(自查) → 004(用户发现落后 7 commits) → 005(自查) → 006(用户发现落后 3 commits)。
- 仓库约定: 文档只保留中文版;源码/CI 与文档机制适配保持构建与测试全绿。
- 网络注意: upstream 已改用 SSH 地址(`git@github.com:huangruiteng/loopx.git`),HTTPS 直连在该环境不可用。
