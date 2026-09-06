# 008 · 上游三次 merge(11 commits)与双语回退处理(任务八)

- **日期**: 2026-09-06(任务七之后)
- **分支**: `260906-dev`
- **背景**: 用户提示分支落后 `huangruiteng/loopx` 11 个 commit;沿用 merge 约定(文档中文唯一)。

## 上游 11 个 commit(含 5 个中继 merge 提交)
| 实质提交 | 内容 | 类型 |
|---|---|---|
| 6fc47230 | lark goal topic root reconnect(#3983) | Bug 修复 |
| 9d70e1e3 | reward-memory 外发消息前召回指引(#3968) | 新功能 |
| 8ed49d7b | chat 幂等键绑定请求(#3981) | Bug 修复 |
| 62a799c5 | chat attached completion closeout | Bug 修复 |
| 92b03ac2 | 打包状态契约刷新 | 构建 |
| 7bb1eb14 | periodic-report 工作区索引有界读取 | 性能 |

## 冲突解决(6 个,全部按中文唯一融合)
1. **periodic-report-v0.md** — 上游英文化并新增 `limit`/`offset` 有界窗口段 → 中文并入(新增段手译)。
2. **agent_turn_recall/README.md** — 上游整篇英文化(含 Turn 契约/使用/Freshness 章节) → 以上游英文为源重译(88 行)。
3. **reward_memory README + 双语回退** — 上游**维护自己的双语对**(README.md 英文 + README.zh-CN.md 中文 530 行,及新 OUTBOUND.md/OUTBOUND.zh-CN.md):
   - 采用上游**官方全中文版**升为主文件(README.md:=zh-CN 全文、OUTBOUND.md:=zh-CN 全文),
   - 删除英文原版与 `.zh-CN.md`;清理横幅与链接目标。
4. **repair-patterns.md** — 上游再次整文件英化,但**内容逐行对应、无新增行**(校验 185/185)→ 保留中文版。
5. **lark-goal-topic-connection-smoke.py** — 双方修改,采用上游最终实现(连接嵌套读取、`connection_id`、reconnect 断言)。
6. **progress: modify/delete**(reward_memory/README.zh-CN.md):维持我们的删除(中文已在 README.md)。

## 环境修复(本地 site-packages 遮蔽,上游干净环境无此问题)
`tests/` 与 `docs/`(与前两轮的 examples/、scripts/)被 site-packages 同名常规包遮蔽 → 补 `__init__.py`(4 个目录全部补齐);此前 `tests.capabilities` 导入失败导致 97 个测试收集报错,修复后 **97 passed**。

## 验证矩阵(全绿)
- pytest(上游测试组 + capability/lark/periodic/chat + 文档): 97 + 22 passed
- smoke: capability-extension-registry / lark-goal-topic / docs-governance / issue-fix-workflow-contract exit=0
- mkdocs 主站 exit=0;中文唯一性残留 0;工作树干净

## 提交
- `742a753b` Merge upstream/main(11 commits)
- `0dcd8b3f` fix(imports): tests/docs __init__.py

## 复查确认(后续追加,无问题)

复查范围与结论(全部通过):
1. upstream/main 已是 HEAD 祖先;11 commit 全覆盖。
2. 上游 zh-CN 文件清单核对:均为旧双语批次(002 已删)+ reward_memory
   双语对(本批处理);merge 后工作树 zh-CN 残留 0。
3. periodic-report-v0:标题 9/9 与上游英文一一对应(产品激活/受众策略/
   拆分相位/发布投影/触发决策/后写 hook/请求与身份/状态与重试/所有权);
   limit/offset 有界窗口段已并入中文。
4. agent_turn_recall README:标题 3/3(Turn Contract/Usage/Freshness And
   Failure),结尾与上游 88 行全文一致(中文密度下 80 行,无缺块)。
5. reward_memory README/OUTBOUND:官方中文全文采用,残留引用
   (【English】横幅/README.zh-CN/OUTBOUND.zh-CN)全部清零;
   catalog_entry aliases 仅保留 README.md 一条(无 zh-CN)。
6. 回归验证:agent_turn_recall/outbound/capability-docs 27 passed;
   007 修复的 9 个代表性 smoke 重跑全部 exit=0(无 merge 回归)。
