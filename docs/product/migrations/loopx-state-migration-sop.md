# LoopX State 迁移 SOP

> [English](loopx-state-migration-sop.md)

状态:LoopX 重命名 PR 的草稿。

本 SOP 面向已有 Goal Harness state 在遗留运行时下、希望在不保留遗留 CLI 兼容别名的情况下把该 state 移入 LoopX 的现有本地用户。

## 迁移什么

`loopx migrate-state` 是一次性迁移工具。它不把 `goal-harness` 变成受支持命令。它只读取显式遗留注册表,重写所选 goal id 与本地路径前缀,然后写入 LoopX state。

它可以迁移:

- 一个所选 goal 条目到 `.loopx/registry.json`;
- 所选 active-state 文件到重写的项目路径;
- `~/.codex/loopx/goals/<new-goal-id>/` 下所选的运行时历史;
- 迁移的项目注册表到 `~/.codex/loopx/registry.global.json`。

它刻意要求显式 goal 选择:要么为已知 goal 重复 `--goal-id`,要么在预览遗留注册表后传 `--all-goals`。没有默认的"迁移全部"行为。

## 推荐顺序

1. 从重命名分支或发布的包安装 LoopX。

```bash
loopx doctor
```

安装器不创建 `goal-harness` 兼容别名。对于现有本地安装,它只在旧本地发布目录被指向时禁用遗留 `goal-harness` 与 `goal-harness-canary` 符号链接。不相关用户命令保持不动。

信任迁移前确认旧命令已消失:

```bash
command -v loopx
! command -v goal-harness
```

2. 首次执行前创建本地备份。

迁移是复制优先的,但现有用户仍应保留遗留注册表、遗留运行时根与任何可能已存在的目标 LoopX state 的时间戳备份。

```bash
backup_dir="$HOME/.codex/loopx-migration-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$backup_dir"

cp -a "$HOME/.codex/goal-harness" "$backup_dir/goal-harness-runtime"
if [ -d "$HOME/.codex/loopx" ]; then
  cp -a "$HOME/.codex/loopx" "$backup_dir/loopx-runtime-before-migration"
fi
```

对于项目本地迁移,在写入 `.loopx/registry.json` 或复制的 active-state 文件前,也备份当前项目 state:

```bash
mkdir -p "$backup_dir/project-state"
if [ -d .loopx ]; then cp -a .loopx "$backup_dir/project-state/.loopx"; fi
if [ -d .codex ]; then cp -a .codex "$backup_dir/project-state/.codex"; fi
if [ -d .local ]; then cp -a .local "$backup_dir/project-state/.local"; fi
```

3. 预览一个 goal 迁移。

```bash
loopx --registry .loopx/registry.json migrate-state \
  --legacy-registry ~/.codex/goal-harness/registry.global.json \
  --legacy-runtime-root ~/.codex/goal-harness \
  --goal-id goal-harness-meta \
  --goal-id-map goal-harness-meta=loopx-meta \
  --path-map /path/to/old/repo=/path/to/new/repo \
  --copy-active-state
```

预览应显示 `dry_run=true`、所选旧 goal id 与迁移后的新 goal id。它不应创建 `.loopx/registry.json`。

4. 预览看起来正确后执行。

```bash
loopx --registry .loopx/registry.json migrate-state \
  --legacy-registry ~/.codex/goal-harness/registry.global.json \
  --legacy-runtime-root ~/.codex/goal-harness \
  --goal-id goal-harness-meta \
  --goal-id-map goal-harness-meta=loopx-meta \
  --path-map /path/to/old/repo=/path/to/new/repo \
  --copy-active-state \
  --copy-runtime \
  --execute
```

只有当旧运行历史应保持对 LoopX 可见时才使用 `--copy-runtime`。对于干净的重命名校验车道,单独复制 active state 通常足够。

5. 对于有几个现有项目的机器,批量迁移前先预览完整遗留注册表。

```bash
loopx --registry ~/.codex/loopx/registry.global.json migrate-state \
  --legacy-registry ~/.codex/goal-harness/registry.global.json \
  --legacy-runtime-root ~/.codex/goal-harness \
  --target-runtime-root ~/.codex/loopx \
  --all-goals \
  --copy-active-state \
  --copy-runtime \
  --no-global-sync
```

只在预览列出精确预期 goal 后执行:

```bash
loopx --registry ~/.codex/loopx/registry.global.json migrate-state \
  --legacy-registry ~/.codex/goal-harness/registry.global.json \
  --legacy-runtime-root ~/.codex/goal-harness \
  --target-runtime-root ~/.codex/loopx \
  --all-goals \
  --copy-active-state \
  --copy-runtime \
  --no-global-sync \
  --execute
```

该批量路径用于共享本地控制面。当仓库再次成为活跃工作 checkout 时,从该仓库运行单 goal 项目本地迁移,使其也拥有自己的 `.loopx/registry.json`。

6. 验证迁移后的 state。

```bash
loopx --registry .loopx/registry.json registry
loopx --registry .loopx/registry.json status --agent-id codex-side-bypass
loopx --registry .loopx/registry.json quota should-run \
  --goal-id loopx-meta \
  --agent-id codex-side-bypass
loopx --registry .loopx/registry.json check --scan-root .
```

7. 只在迁移后的 goal 可见后更新自动化。

心跳提示应使用新 goal id 与 LoopX 命令:

```text
Advance `loopx-meta` from the registry-declared active state.
Use skills: `loopx-project`; if surprising/tiny/contradictory, `loopx-self-repair`.
LoopX CLI is source of truth.
```

不要保留旧自动化 id 或提示正文作为隐藏兼容路径。如果 Codex App 心跳无法就地重命名,删除旧心跳并创建新的 `loopx` 心跳。

8. 只通过恢复备份回滚。

如果验证失败,不要就地手工编辑迁移后的 JSON。恢复备份,用更窄的 `--goal-id` / `--goal-id-map` / `--path-map` 选择重跑 dry-run,在预览干净后再执行。

```bash
# Global rollback.
rm -rf "$HOME/.codex/loopx"
if [ -d "$backup_dir/loopx-runtime-before-migration" ]; then
  cp -a "$backup_dir/loopx-runtime-before-migration" "$HOME/.codex/loopx"
fi

# Project-local rollback from the project root.
rm -rf .loopx .codex .local
if [ -d "$backup_dir/project-state/.loopx" ]; then
  cp -a "$backup_dir/project-state/.loopx" .loopx
fi
if [ -d "$backup_dir/project-state/.codex" ]; then
  cp -a "$backup_dir/project-state/.codex" .codex
fi
if [ -d "$backup_dir/project-state/.local" ]; then
  cp -a "$backup_dir/project-state/.local" .local
fi
```

如果机器没有之前的 `~/.codex/loopx`,全局回滚会留下该目标运行时缺失。下一次迁移尝试将重建它。

## 安全规则

- 从一个 goal 开始,而不是整个注册表。
- 只有在 dry-run 显示预期 goal 列表后才使用 `--all-goals`。
- 保持迁移 state 本地私有;不要提交 `.loopx/`、`.local/` 或运行时历史。
- 只在迁移 SOP、迁移代码与无兼容否定断言中保留旧命令名。
- 在维护者明确批准该 gate 前,停止于 GitHub 仓库重命名、Pages 切换、包发布或破坏性清理。
