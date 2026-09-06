# 012 · 连续 merge 系列复查(006–011)(任务十二)

- **日期**: 2026-09-06(任务十一之后)
- **目标**: 用户要求仔细分析连续多次 merge huangruiteng/loopx 落后操作(006–011,
  共 56 个上游 commit)的正确性并修复问题。

## 复查方法与覆盖
1. upstream/main 是 HEAD 祖先;全部 56 commit 入历史。
2. **全树英文文档残留扫描**(CJK 比例 <15% 的 .md):仅剩已知排除项
   (示例数据、tests/fixtures、缓存)——文档 100% 中文。
3. **8 个重点重写/融合文档与上游结构 1:1 校验**(标题/表格行/代码块/链接集):
   periodic-report(10/10、6/6)、agent_turn_recall(5/5、4/4)、
   release-readiness(13/13、26/26、38/38)、contributor-tasks(16/16、71/71)、
   model-behavior(11/11、4/4)、desktop README(8/8、4/4)、repair-patterns、
   README(官方中文)。
4. doctor.py 短语仍为中文(上游后续未改)。
5. **全量 299 smoke 扫描**:失败仅剩 2 项,其一(benchmark-native)系复查期间
   工作树修正前暂脏,提交后 exit=0;另一(cli-help-manpage)为已知上游超预算项
   (与中文无关,留档)。

## 发现并修复的问题(2 处,同一模式)
**根因**: 此前融合校验只对比"表格模式行/链接集合",漏掉非表格增量。
1. **repair-patterns.md(008 解决时)**:上游在表格后新增 `## Minimal Evidence
   Packet` 小节(标题 + text 代码块 + 说明),当时仅对比 185 pattern 行(1:1)
   而未发现 → 该小节丢失。**已补译**;标题 1=1、代码块 2=2 恢复。
2. **README.md(010 采用官方中文版)**:官方中文版缺少英文版 "Session dash"
   表格行与 design 链接(官方译文与英文的自身差异)→ **按信息不丢原则补齐**;
   其余链接差异均为预期删除项(英文锚点→中文锚点、README.zh-CN.md、
   book/en 链接)。

## 教训
- "整文件英化 vs 内容变化"的融合校验必须覆盖**全部结构计数器**
  (标题/表格/代码块/链接),不能只看单一维度(如 pattern 行集合)。
- 采用"官方中文版"时,需与官方英文版做结构对账,补齐官方译文自身遗漏。

## 提交
- 修复提交(repair-patterns 证据包 + README Session dash 行)。
