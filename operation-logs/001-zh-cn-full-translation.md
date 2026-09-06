# 001 · 全量文档中文化翻译(任务一)

- **日期**: 2026-09-06
- **分支**: `260906-dev`
- **目标**: 将 loopx 项目全部文档翻译为简体中文;已有中文版的中英对别,中文独有内容合并进英文版,再据合并版重译中文;不破坏功能。
- **最终结果**: 113 个提交,372 文件变更(+65,237/−62),全部为文档。

## 用户拍板事项
1. 功能性文档(AGENTS.md、skills/*/SKILL.md):创建 `.zh-CN.md` 副本,英文原版保持权威。
2. `deprecate/benchmark-legacy/**`(134 个废弃档案):跳过。
3. 5 个只有中文的文档:保持中文-only。
4. 法律文件(LICENSE/LICENSE-MIT/NOTICE/DCO)与 man/loopx.1:全部翻译(创建带后缀中文版)。

## 执行过程
1. **B0 预检**: 盘点 567 英文 md + 39 已有 zh 文件;mkdocs 基线构建 exit=0(4 条既有锚点 INFO)。
2. **B1 合并+重译 54/56 对**(并行 5 代理):
   - README 对(15 节逐节 diff,回填 3 处中文独有内容进英文,重译中文补齐英文独有内容)
   - RFC 16 对 / misc 10 对(decision-context、material-lifecycle 等英文回填)/ capability 6 对(issue_fix 四层架构等回填)
   - docs/book 22 对:轻量结构 diff 确认已完全同步,无需改动
3. **B2–B8 新翻译**(216+369 文件,15 并行代理):主站 reference/product/development/guides/integrations/showcases/archive/concepts/operations/plans/research/superpowers/update-notes/community + loopx/packages/apps/benchmark/demo/examples + skills/根/.github/功能文件副本;man 页与法律文件中文对照版(roff 宏 100% 对齐)。
4. **B9 验证**: 范围守卫(0 源码改动);覆盖率 0 真实缺失;1,856 链接 0 翻译引入坏链;mkdocs 主站/书-zh/书-en 三构建 exit=0;frontmatter 未漂移。
5. **额外修复**: 7 个中文标题补 `{#slug}`(CJK 标题在 python-markdown 下生成 `_N` 数字锚点)。

## 关键发现
- `docs/development/control-plane-course/**`、`personal-workspace-*-guide.md` 等源文件本身即中文/双语混排。
- `demo/auto_research/README.md` 的 5 个 `../../../docs/...` 链接为英文原版固有坏路径(忠实镜像,报告未改)。

## 提交/推送
- 提交后按用户指示 `commit and push`:`bf217e1e..6770b7c9`。
- 提交数:113。工作树干净。
