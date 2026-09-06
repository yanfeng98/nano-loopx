# LoopX 重命名迁移

> [English](loopx-rename-migration.md)

状态:进行中的迁移计划。

LoopX 是规范产品名,`loopx` 是规范 CLI 命令。重命名在产品界面刻意快速失败:新安装与生成的提示只暴露 `loopx`,因此旧命令名无法悄然隐藏遗漏的迁移工作。

## 规范契约

- 产品名:`LoopX`。
- CLI 命令:`loopx`。
- 遗留 CLI 命令:无。`goal-harness` 不作为别名安装。
- Python 包/导入:`loopx`。
- 本地项目 state:`.loopx/registry.json`。
- 全局运行时 state:`~/.codex/loopx`。
- Skill 名称:`loopx-project`、`loopx-pr-review`、`loopx-doc-registry` 与
  `loopx-self-repair`。

## 迁移 Todo 批次

1. P0 规范契约:文档化无遗留别名的界面,并重命名包/导入/state/skill 命名空间。
2. P0 CLI/安装迁移:只安装 `loopx`,更新包元数据、安装器与安装 smoke。
3. P0 公开文档迁移:把根 README、getting-started 路径与打包安装文档迁移为 LoopX 语言。
4. P0 state 迁移 SOP:为现有本地用户交付显式一次性
   [`migrate-state`](loopx-state-migration-sop.md) 路径。这不是遗留 CLI 兼容别名;它是可审计的 dry-run 优先导入到 `.loopx` 与 `~/.codex/loopx`。
5. P1 外部界面发布 gate:在规范代码重命名落地前无法校验的包发布元数据、托管 Pages URL、外部文档与任何发布说明。
6. P1 GitHub 重命名 gate:在规范重命名 PR 落地、维护者接受公开 URL 迁移计划且 Pages/issue-template 切换 PR 合并后,把 `huangruiteng/goal-harness` 重命名为 `huangruiteng/loopx`。无 clone 安装器已指向新仓库 URL,因此 GitHub 重命名是受控发布切换,而非兼容别名。

## GitHub 重命名 Gate

当前已验证的 GitHub 用户对现有 `huangruiteng/goal-harness` 仓库拥有 admin 权限。在维护者明确批准仓库重命名 gate 且下方切换清单完整后,Codex 可以执行最终重命名为 `huangruiteng/loopx`。

不要把它作为普通代码 PR 的一部分重命名仓库。重命名前:

- 合并 LoopX 规范重命名 PR;
- 确认无 clone 安装器从新 URL 工作;
- 决定托管 Pages URL 策略;
- 把 Pages 基路径与公开 GitHub 链接更新为 `/loopx/`;
- 更新仓库描述/topics;
- 重命名后通过 `git remote set-url origin` 更新本地 remote;
- 让旧仓库名保持未使用,以免 GitHub 重定向失效。

GitHub 重定向重命名仓库的 web 与 git 流量,包括 clone、fetch 与 push 操作,但仓库 Pages URL 是例外,且从重命名仓库使用 action 的 GitHub Actions 不跟随重命名。这使 Pages 与 action 消费者引用成为显式清单项。

## 校验矩阵

重命名 PR 被认为就绪前所需:

- `python3 -m py_compile $(find loopx examples -name '*.py' -print)`
- `python3 examples/install-local-smoke.py`
- `python3 examples/codex-cli-packaged-install-smoke.py`
- `python3 examples/fresh-clone-quickstart-smoke.py`
- `python3 examples/state-migration-smoke.py`
- `python3 examples/docs-governance-smoke.py`
- `loopx check --scan-root .`
- `git diff --check`

自我使用校验应从工作树安装到隔离 home,运行 `loopx doctor`,bootstrap 一个临时项目,并确认通过 `.loopx` 与 `~/.codex/loopx` 的配额/状态工作。
