# 009 · 上游四次 merge(22 commits)(任务九)

- **日期**: 2026-09-06(任务八之后)
- **分支**: `260906-dev`
- **背景**: 用户提示分支落后 `huangruiteng/loopx` 22 个 commit;沿用 merge 约定(文档中文唯一)。

## 上游 22 个 commit(含中继)
实质提交:桌面签名更新与恢复(#3994/#3985)、scheduler smoke 时钟注入(#4002)、
cli 维护(#4003)、todo claim retry 身份(#3987)、lark 多处修复(#3996-3999)、
模型行为限定强化(#3997)、release 时间线同步(#3982)、todo 硬租约竞态(#3986)等。

## 冲突解决(10 个,全部采用"上游英文为源 + 中文唯一")
| 文件 | 处理 |
|---|---|
| typescript-control-plane-migration-v0.md | **采用上游官方中文版**(617 行)升为主文件,删 zh-CN,交叉链接修复 |
| release-readiness.md | 旧中文为底+上游增量(6 处日期校准、PyPI 激活说明、升级决策引用恢复),1:1 校验 |
| contributor-tasks.md / model-behavior-qualification-v0.md | 以上游英文为源,冲突区补译(模型语义字段/对抗诊断场景等) |
| desktop README / man/loopx.1 | 以上游为源重译(roff 宏 281 token 逐字节一致) |
| dev-book-publication-smoke.py | 保留 zh-only 适配 + 上游 migration_baseline_tag 语义 |
| external-scheduler-worker / outcome-followthrough smoke | 采纳上游(上游已含我们 007 语义) |

## 发现并修复的问题
1. **pytest 导入模式破坏**:008 为规避本机遮蔽加的 `tests/docs/__init__.py` 改变了
   pytest 收集模式,使上游顶层 import 风格的 3 个 host-surface 测试
   (`from host_surface_cli_probes import`)收集失败 → **撤销**(与上游一致,
   host-surface 26 passed 恢复)。本机 site-packages 残留包仍遮蔽 `tests.xxx`
   前缀的 3 个测试文件(仅本机环境,CI 正常);examples/scripts 的 __init__.py
   保留(本地 smoke 顶层导入需要)。

## 验证矩阵(全绿)
- pytest: host-surface 26、上游测试组 97、capability-docs 6 passed
- smoke(冲突相关+关键 5 项): dev-book-publication / external-scheduler-worker /
  outcome-followthrough / docs-governance / capability-extension-registry 全部 exit=0
- mkdocs 主站 exit=0;中文唯一性残留 0;工作树干净
- 已知本机环境限制:3 个 `tests.*` import 测试文件因 site-packages 同名遮蔽无法收集
  (CI 干净环境正常)

## 提交
- `7d028802` Merge upstream/main(22 commits)
- `e34fd6b1` fix(tests): 撤销 tests/docs __init__.py(匹配上游 pytest 导入模式)
