# 014 · 上游八次 merge(1 commit)(任务十四)

- **日期**: 2026-09-06(任务十三之后)
- **分支**: `260906-dev`
- **背景**: 分支落后 `huangruiteng/loopx` 2 个 commit(1 个实质 + 中继)。

## 上游 commit
`1b7cf11f` fix(todo): preserve claim-neutral correction after promotion (#4005)
- 代码/TS/测试 + typescript RFC(英文+官方中文对)。

## 冲突与解决(2 个,与前两次同法)
1. **typescript-control-plane-migration-v0.md**(内容冲突)— 采用上游官方中文版
   (624 行,CJK 485)升为主文件;
2. **.zh-CN.md**(modify/delete)— 维持删除;交叉链接修复(锚点指向上游
   `<a id>` 的英文 slug)。

## 验证
- pytest 14 passed;mkdocs exit=0;zh-CN 残留 0;工作树干净。
