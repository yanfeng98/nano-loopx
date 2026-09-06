# 每两周更新说明自动化


LoopX 更新说明应由一个独立的发布工作流生成，而不是给活跃的 heartbeat 自动化添加自定义行为。

## 为什么不是 Heartbeat

LoopX heartbeat 推动活跃 goals 前进。它读取 quota、gates、todos、scheduler hints 与近期状态，
然后决定当前 agent turn 能否产生有用的转换。两周一次的发布说明不同：它是日历驱动的发布
沟通，而不是推进任务。

把两者混在一起会产生可避免的摩擦：

- heartbeat 可能在一个发布任务上花费或唤醒，而它本应推进项目工作；
- 发布节奏可能被无关的活跃 goal gate 阻塞；
- 更新说明生成可能把项目特定的 watch 逻辑加进一个通用 scheduler prompt；
- 用户必须调试一次漏掉的说明是 scheduler 问题还是 release-note job 问题。

## 推荐的形态

使用一个专用的 release-note job 上传可审查的草稿 artifact。仓库随附第一版
`.github/workflows/update-notes.yml`，由 `scripts/update_notes_release_job.py` 支撑。未来生成器
稳定后，`loopx update-notes` CLI 子命令可以包装同一个契约。

GitHub Action 中没有 LLM。因此它应当从公开 git 历史生成事实性的源稿，而不是假装撰写最终
叙述。维护者或 LoopX agent 应在标记就绪前完善草稿 PR。

该 job 应当：

1. 从 `docs/update-notes/` 中现有说明文件名确定下一个时间段。
2. 为该确切 UTC 时间段收集 first-parent 已合并 PR 证据。
3. 去除直接提交与分支合并噪声，然后把其余 PR 排序进紧凑的产品主题。
4. 在 `docs/update-notes/` 下写入新说明。
5. 更新归档表与最新说明指针。
6. 把根 README 保持为紧凑指针，而不是长 changelog。
7. 对触及的公开文档运行 update-note smoke 与 `loopx check`。
8. 把说明、更新的归档与 patch 作为可审查 artifact 上传。创建 PR 仍然是显式的人为动作。

## 触发策略

节奏以 2026-05-31 的初始公开 scaffold 为锚点。GitHub Actions cron 无法干净地表达
“在该锚定时间段关闭后每两周一次”的可审查规则，因此工作流每周运行，让生成器充当双周边界
gate。如果下一个时间段未到期，脚本无变更退出，不打开任何 PR。

手动 `workflow_dispatch` 通过可选的 `since`、`until` 与 `force` 输入支持修复与补写。

此归档后推荐首次计划发布的时间段是 2026-06-28 至 2026-07-11，在 2026-07-12 或之后开放评审。

## 护栏

- 以公开仓库历史、已交付文档、公开示例与公开 PR 元数据为来源。
- 不摄取原始聊天历史、私有文档、原始 benchmark traces、原始 verifier 输出、本地路径、凭证
  或仅 operator 可见的状态。
- 保持生成的说明足够短，以便人工审查。
- 生成器无法确定前一时间段时 fail closed。
- 保持 GitHub Actions 权限只读；分类置信度低时上传草稿 artifact。
- 默认 job 不要求 LLM secret。
- 把更新说明当作摘要表面。它们不替代 git 历史、review packets 或 LoopX 状态。

## 未来 CLI 契约

当前项目级命令是：

```bash
python3 scripts/update_notes_release_job.py --dry-run
python3 scripts/update_notes_release_job.py --since 2026-06-28 --until 2026-07-11 --force
```

未来的 CLI 表面可以包装同一个生成器：

```bash
loopx update-notes plan --since 2026-06-28 --until 2026-07-11
loopx update-notes write --since 2026-06-28 --until 2026-07-11 --dry-run
loopx update-notes write --since 2026-06-28 --until 2026-07-11 --open-pr
```

在公开/私有边界与分组质量被证明稳定之前，发布始终是经过评审的人为动作。如果项目以后希望
CI 直接产出完整散文，就添加一个显式的可选 LLM 步骤并配合仓库 secret，在缺少该 secret 时
fail closed；把确定性源稿模式保持为默认。
