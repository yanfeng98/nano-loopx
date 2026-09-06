# 005 · merge 复查与修复(任务五)

- **日期**: 2026-09-06(任务四之后)
- **分支**: `260906-dev`
- **目标**: 用户要求再次仔细分析 merge 操作是否正确,如有问题请修复。

## 复查范围与结论
1. **merge 完整性**: `upstream/main` 是 HEAD 祖先 ✓;7 个 commit 全部并入。
2. **5 个文档冲突融合完整性**:
   - 标题结构对照: testing/installing/pr_review README/OPERATOR/SKILL 与上游英文版章节一一对应;
   - testing-and-quality: 新段 + `## Smoke 与 Canary` 衔接正确(上游英文段未引入);
   - installing-loopx: 重试 2 段中译并入正确。
3. **前端/工作流残留**: 0(en 分支、.en.html、mkdocs.en 均无)。
4. **中文唯一性**: `.zh-CN.md` 残留 0、横幅 0。
5. **上游代码测试**(此前仅跑 3 组,本次补齐 merge 引入的全部):
   - python 组(12 文件):159 passed,1 skipped + CI workflow 组 20 passed
   - TS(todo_update/authority_store_conformance):5 passed
   - operator_smoke:19 tests OK(需 `PYTHONPATH=packages/loopx-codex-provider-routing/src`,本地未安装子包属环境)
   - update-smoke / pr-review-smoke / governance / showcase-catalog:全部 ok

## 发现并修复的问题
1. **`test_python_ci_workflow.py` 失败** → 本地环境缺 `pytest-split`/`pytest-xdist`/`pytest-cov`(环境依赖,非代码);安装后 **20 passed**。
2. **`test_chat_completed_todos.py` 2 用例失败** → 上游测试未等待 HTTP 服务线程就绪,在 WSL 调度下 connect 过早被拒(基础 ThreadingHTTPServer 复现)。**已加 5 秒就绪探测**(语义不变),连续 3 次 5 passed。提交 `13ff8f7b`。
3. 融合文档中 3 处 merge 遗留多余空行 → 规整(随 `13ff8f7b` 提交)。

## 提交/推送
- 提交 `13ff8f7b`;push `3081a50f..13ff8f7b`。工作树干净。

## 最终状态
- `260906-dev` 与 `upstream/main` 功能同步(位于上游最新版之上),仓库文档保持中文唯一。
