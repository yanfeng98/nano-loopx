# 同仓库包

此目录包含与 LoopX 共同开发、可独立安装的发行包。每个子包拥有自己的打包元数据、依赖与发布生命周期;它不会仅仅因为被收录在本仓库中就进入 LoopX wheel。

LoopX 自有的源码位于 `loopx/` 下:

- `loopx/capabilities/` 拥有面向调用方的 capability 契约与内置实现;
- `loopx/extensions/` 拥有扩展机制与随 LoopX wheel 一起发布的 provider。

用以下命令创建一个独立的扩展包:

```bash
loopx extension init <extension-id> --execute
```

当前同仓库扩展包括:

- [`loopx-codex-provider-routing`](loopx-codex-provider-routing/README.md):
  public-safe 的 Codex App + CPA 目录编译、资格判定与升级规划;
- [`loopx-repo-health`](loopx-repo-health/README.md):public-safe 的 GitHub
  仓库健康快照。

默认目标位置是 `packages/<extension-id>/`。
