# 006 · 上游二次 merge(3 commits)与遗留 smoke 适配(任务六)

- **日期**: 2026-09-06(任务五之后)
- **分支**: `260906-dev`
- **背景**: 用户提示分支再次落后 `huangruiteng/loopx` 3 个 commit;沿用之前的 merge 约定(文档保持中文唯一)。
- **网络备注**: 本次 fetch 首两次 HTTPS 拉取失败(GnuTLS recv error / curl 直连超时);origin 的 SSH 通道可用,故将 `upstream` remote 切为 SSH 地址(`git@github.com:huangruiteng/loopx.git`)后 fetch 成功(以后 fetch 走 SSH,不再依赖 HTTPS 直连)。

## 上游 3 个 commit 分析
| Commit | 类型 | 内容 | merge 价值 |
|---|---|---|---|
| 3f605c3f | 新功能 | Workspace stories + owner 任务可见性(#3990) | ✅ |
| df5c557a | Bug 修复 | codex-app automation TOML 往返安全(#3913) | ✅ |
| 2f4c8f33 | 新功能 | todo 延迟原生创建(#3980) | ✅ |

**建议 merge(全部为上游正式演进),已执行。**

## 冲突解决(1 个文档)
- `skills/loopx-self-repair/references/repair-patterns.md`(上游将整表由中文改为英文并新增 `codex_app_automation_toml_contract_gap` pattern):
  - 以上游英文表为**单一事实源**重建中文版:184 行旧中文行按 pattern 名复用 + 新增行手译;
  - 最终 185 行全中文、0 英文行、5 列结构完整,与上游行序一一对应。
  - **教训**: 初版脚本从"带冲突标记的文件"提取中文行,混入 upstream 英文段导致重建出 179 行英文;改为从 `git show HEAD:`(中文侧)提取后验证通过。事后必须用"非中文行=0"校验语言纯度。

## 发现并修复的问题(3 个,均为适配/环境遗留)
1. **`scripts/__init__.py` 新增**: 本地 site-packages 存在无关 `scripts` 常规包(llama.cpp gguf 工具),遮蔽仓库 `scripts/` namespace 目录(regular 包优先于 namespace);加 `__init__.py` 使仓库 scripts 成为常规包、在 sys.path[0] 优先 → `from scripts.codex_app_apply_rrule import` 恢复。上游干净环境无此问题。
2. **`tests/test_codex_app_apply_rrule.py`**: 新增断言 `"reuses the provided parent Turn"` 等指向英文文档 → 改为 `docs/heartbeat-automation-prompt.md` 中文实际文案("复用提供的父 Turn"/"同一 Turn 重放"等),负断言保留。
3. **`examples/interaction-pattern-catalog-smoke.py`**: **前几轮转换遗漏的 smoke**(从未运行过):85/4/21 条断言仍为英文标题/句子 → 子代理全部 1:1 改写为中文文档实际文本(标题 `## 模式族`、`## 可选 OM/HITL Overlay Schema`、`## 目录维护与验证设计` 等;表格行/IP 标识符/代码块等逐字保留英文),**零删除断言**。

## 验证矩阵(全绿)
- upstream 涉及测试: `test_codex_app_apply_rrule` / `test_scheduler_fallback_hint` / `test_workspace_story_demo` + chat_completed_todos: 24 passed(单用例断言修复后 20 passed)
- TS(todo_create / authority_store_conformance): 1 passed
- `upgrade-plan-smoke` / `interaction-pattern-catalog-smoke` / `docs-governance-smoke`: exit=0
- mkdocs 主站构建: exit=0;中文唯一性残留: 0;`upstream/main` 已是 HEAD 祖先

## 提交(本地,待推送)
- `5bcc8a04` Merge upstream/main(3 commits)into 260906-dev
- `44697a67` test(codex-app): heartbeat 断言适配 + scripts/__init__.py
- `cf958663` test(interaction-pattern-catalog-smoke): 断言适配中文文档
