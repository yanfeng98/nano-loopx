# 013 · 上游七次 merge(14 commits,1.0.0 release)(任务十三)

- **日期**: 2026-09-06(任务十二之后)
- **分支**: `260906-dev`
- **背景**: 分支落后 `huangruiteng/loopx` 14 个 commit(主干 1.0.0 release 系列)。

## 上游 14 个 commit(多为 release 合并提交)
1.0.0 Workspace 里程碑、desktop 维护 IPC/更新失败区分、release 校验解耦、
Doubao 行为限定、书与手册版本对齐(0.5.4→1.0.0)、历史迁移里程碑保留等。

## 冲突与解决(4 处)
1. **docs/book/en/** ×2(modify/delete)— 维持"书只保留中文版"的删除。
2. **docs/book/index.md** — 上游中文更新自动合入,无 en 残留。
3. **man/loopx.1** — 上游仅改版本号 .TH(0.5.4→1.0.0);同步至我们的
   中文 .TH,清理重复行,groff 渲染 exit=0。
4. **pyproject.toml / tests/test_license_metadata.py** — 自动合并
   (保留我们的删 zh-CN data-files 与中文断言 + 上游 decouple license checks)。

## 验证
- pytest(license + chat CORS)12 passed;mkdocs 主站与书-zh 构建 exit=0;
  zh-CN 残留 0;冲突标记 0;工作树干净。

## 提交
- Merge upstream/main(14 commits)。

## 复查确认(无问题)

1. upstream/main 已是 HEAD 祖先;14 commit 全覆盖。
2. 书 en/** 在 HEAD 完全不存在(维持"只保留中文版"删除,未随上游恢复)。
3. 书 zh 与上游结构 1:1:index(4/4 标题)、00-reading-guide(9/9 标题、
   46/46 表格),无 en 残留;01/12 章节与上游 diff=0(上游未改)。
4. man 宏结构 97/97、转义 184/184 与上游逐字节一致,仅 .TH 语义更新为
   LoopX 1.0.0。
5. book 双 smoke(publication/welcome-wagon)exit=0;pytest 12 passed。
6. 全树英文文档残留:仅排除区测试 fixtures(预期)。
