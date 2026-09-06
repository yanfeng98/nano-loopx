# 002 · 只保留中文版转换(任务二)

- **日期**: 2026-09-06(任务一之后)
- **分支**: `260906-dev`
- **目标**: 用户澄清最终形态——文档只保留中文版本,删除英文版本;`.zh-CN.md` 提升为标准文件名,英文原版删除;文档仍符合"中文唯一"约定。
- **最终结果**: 4 个提交(阶段 A/B/C + demo 链接修复),GitHub 路径一致。

## 用户拍板事项
1. 法律文件与 man 页:英文删除,中文译文改标准名(接受 GitHub license 识别失效)。
2. docs/book:删 `en/**`(22 文件)、`mkdocs.en.yaml`;`mkdocs.zh.yaml` 移除 alternate English。
3. 功能性文件:中文副本升为主名(AGENTS.zh-CN.md→AGENTS.md、SKILL.zh-CN.md→SKILL.md、PULL_REQUEST_TEMPLATE.md.zh-CN.md→PULL_REQUEST_TEMPLATE.md),frontmatter 功能字段保持英文。
4. 英中混排源文件:纯中文版替代。
5. 全适配:源码/CI/测试同步改(仅路径与断言,不改逻辑),保持全绿。
6. 删除 `.en.html` 展示孪生(13 个)并适配 showcase-catalog.json / export-frontstage-share-bundle.mjs。

## 执行过程
1. **阶段 A 置换**(分类脚本 + 复核):REPLACE 360 对、MIRROR 16(删复制镜像)、ZH-ONLY 5 个改名、DELETE(book/en 22、mkdocs.en.yaml、法律/man 5、.en.html 14);提交 `3ddec083`。
   - *事故与恢复*: 分类脚本初版 bug 误对 REPLACE 列表执行 `git rm`(删除 zh 源),发现后 `git reset --hard HEAD` 恢复(381 个 zh 文件完好),修正 base 计算(双重 `.md` bug: `X.md.zh-CN.md`)后重执行,零损失。
2. **阶段 B 内容清理**: 删除 299 个 `[English]` 横幅与 12 处冗余双语双链;全局 `X.zh-CN.md→X.md` 链接改写(38 文件);`/loopx/docs/book/en/` 路径改中文版;10 个中文标题补 `{#slug}`;kunluncode-adapter.zh-CN.html→.html;提交 `48db9aaa`。
3. **阶段 C 机制适配**: 提交 `f314a268`(详见下)。
4. **demo/auto_research 坏路径修复**: `../../../docs/`→`../../docs/`(5 处,提交 `139a7f55`)。

## 阶段 C 适配清单(构建/CI/src 全绿)
- 源码: reward_memory catalog_entry 移除 README.zh-CN.md alias(gen-files ValueError 修复);decision_context/material_lifecycle/reliability_diagnostics catalog docs 路径;windows_install.py;pr_review.py;pyproject.toml data-files。
- 前端: apps/presentation/site/src/App.tsx book 链接去 en/;showcase-html-pages.py 只生成中文;showcase-catalog.json 删 interactive_page_en/localized_pages.en;export-frontstage-share-bundle.mjs 去 index.en.html;frontstage-share-bundle-smoke.mjs、showcase-catalog-smoke.py。
- CI: frontstage-pages.yml 删 mkdocs.en.yaml 构建步与 README.zh-CN.md/mkdocs.en.yaml 触发;full-public-smokes.yml 触发;mkdocs.zh.yaml alternate。
- 测试: docs-governance、dev-book-publication、dev-book-welcome-wagon、issue-fix-capability-guide、readme-star-history、capability-extension-placement、frontstage-pages-workflow、public_entry/readme-demo-surface、control_plane/peer-agent-hard-cut 等 smoke(10 个)+ pytest 3 个(test_license_metadata/DCO、test_local_authority_shadow_config、test_capability_documentation)。

## 验证
- `.zh-CN.md` 残留 0、`.en.html` 残留 0、横幅 0;链接 1,081 → 0 损坏;mkdocs 主站/书 exit=0;pytest 14 passed;工作树干净。
- 提交: `3ddec083`(A)、`48db9aaa`(B)、`f314a268`(C)、`139a7f55`(demo 链接);push `6770b7c9..139a7f55`。

## 备注
- GitHub LICENSE 自动授权识别因中文译文失效(仅徽章,无功能影响)。
- `language: zh-CN`(periodic_report 周报、前端 i18n)为产品功能字段,保留。
