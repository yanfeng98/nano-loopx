# 004 · 上游 merge(huangruiteng/loopx 7 commits)(任务四)

- **日期**: 2026-09-06
- **分支**: `260906-dev`(merge `upstream/main`)
- **目标**: 用户发现分支相对 `huangruiteng/loopx` 落后 7 个 commit,要求分析是否有必要 merge,且文档仍保持之前的"只保留中文版"要求。

## 上游 7 个 commit 分析
| Commit | 类型 | 内容 | merge 价值 |
|---|---|---|---|
| a07f2178 | CI 改进 | Python 测试分片 + Sonar 覆盖复用(#3989) | ✅ |
| 8fe34c56 | Bug 修复 | update 下载重试 + 安全诊断(#3991) | ✅ |
| 8c08efd3 | Bug 修复 | periodic-report 谓词对齐(#3871) | ✅ |
| 36b27aaa | 新功能 | provider-routing 双 selectors + quota 恢复(#3984) | ✅ |
| 2515fc12 | 新功能 | todo provider-first native update(#3974) | ✅ |
| 52c34cda | 安全增强 | pr-review 要求仓库复用证据(#3988) | ✅ |
| bb71b386 | Bug 修复 | dashboard 完成态回读(#3961) | ✅ |

**建议 merge(全部为上游正式演进),已执行。**

## 冲突解决(6 个双方都改的文件)
- **5 个文档冲突——按"中文唯一"融合**(上游英文新增内容手译入中文主文件,英文源不引入):
  - `docs/development/testing-and-quality.md`: CI 分片说明(作者原文含中文段)→ 中文段并入
  - `docs/guides/installing-loopx.md`: 下载重试/诊断 2 段 → 手译并入
  - `loopx/capabilities/pr_review_queue/README.md`: repository_reuse 条目 + 段落 → 手译并入
  - `packages/loopx-codex-provider-routing/OPERATOR.md`: 新选择器表格 + 4 段重构(18 隐藏行、配额恢复等)→ 全块手译重组
  - `skills/loopx-pr-review/SKILL.md`: packet 证据段落(上游重写 7 步 checklist)→ 中文并入(frontmatter 不变)
- `pyproject.toml`: 自动合并(保留 zh-CN 去除 + 上游 CI 改动)
- `docs/guides/personal-workspace-user-guide.md`: 上游新增内容本身是中文 → 自动合入

## merge 后验证与修复
- mkdocs ×2 exit=0;pytest 3 组 14 passed;上游新代码编译通过。
- **pr-review-command-smoke 失败 → 修复**(2 组残留英文断言→SKILL 中文实际文案,含 frontmatter description 等)。提交 `3081a50f`。
- 结构对照: OPERATOR 7 章、pr_review README 6 章、SKILL 159 行(≤180)与上游一一对应。

## 提交/推送
- merge 提交 `bd9c14f0`、smoke 修复 `3081a50f`;push `8dca866e..3081a50f`。
