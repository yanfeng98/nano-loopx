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

- 全部操作在 `260906-dev` 分支完成。
- 时间轴: 001 → 002(用户澄清"只保留中文") → 003(自查) → 004(用户发现落后 7 commits) → 005(自查) → 006(用户发现落后 3 commits)。
- 仓库约定: 文档只保留中文版;源码/CI 与文档机制适配保持构建与测试全绿。
- 网络注意: upstream 已改用 SSH 地址(`git@github.com:huangruiteng/loopx.git`),HTTPS 直连在该环境不可用。
