# Codex CLI 无克隆发布验证


状态：发布验证说明。

只有当已发布的命令 surface 与文档相符时，Codex CLI 首次运行路径才能宣传为偏好的交互路径。用户不必先克隆 LoopX 就能从项目仓库尝试它。

## 验证形态

发布验证器按新用户所见的路径走一遍：

1. 创建临时 HOME 与临时项目仓库；
2. 用与公开无克隆命令相同的归档安装器机制运行 `scripts/install-from-github.sh`；
3. 确认安装的 `loopx` wrapper 可以运行 `doctor`；
4. 确认安装的顶级 help 指向 `loopx commands`，并且安装的命令参考暴露首次运行命令：`codex-cli-bootstrap-message`、`codex-cli-tui-bootstrap-smoke-bundle` 与 `codex-cli-visible-attach-acceptance`；
5. 从新项目生成一条消息的 TUI bootstrap 文本；
6. 从新项目生成免 transcript bootstrap bundle；
7. 从安装的发布快照回放公开 proof-capture 夹具。

验证器不启动 Codex、不读 transcript、不读 session 文件、不读凭据、不改动 Codex session，也不 spend LoopX quota。

运行方式：

```bash
python3 examples/release/codex-cli-no-clone-release-verification-smoke.py
```

## 当前结果

当前归档路由：**合格作为恢复回退，带一个边界**。

就绪：

- 归档安装器在不要求本地 LoopX checkout 的情况下创建稳定发布快照；
- 已安装 wrapper 暴露首次运行 TUI bootstrap、smoke bundle 与 visible-attach acceptance 命令；
- 生成的 bootstrap 文本告诉 agent 安装、连接、运行 quota、保留可见 TUI、写回 evidence，并避免 raw transcripts；
- smoke bundle 确认无 Codex 启动、无 LoopX quota spend；
- proof-capture 夹具被打包进发布快照，并可由已安装 wrapper 回放。

边界：

- 除非调用方用受信任归档覆盖 `LOOPX_ARCHIVE_URL`，公开安装仍依赖对 GitHub 归档端点的网络访问；
- 在可见证据加 runtime idle evidence 通过之前，same-TUI 自动化不是默认路径。

这意味着 PyPI 保持默认、contributor 的 clone-plus-canary 保持开发路径时，归档路由可以继续作为经过测试的恢复选项。

## 发布检查清单

晋升新的发布快照之前，运行：

```bash
python3 examples/release/codex-cli-no-clone-release-verification-smoke.py
python3 examples/codex-cli-first-run-rehearsal-smoke.py
python3 examples/codex-cli-tui-bootstrap-smoke-bundle-smoke.py
python3 examples/codex-cli-proof-capture-demo-fixtures-smoke.py
```

如果第一个命令失败，在失败被归结为紧凑 blocker 之前不要宣传归档回退合格：缺少安装器依赖、归档布局不匹配、缺少已安装命令、bootstrap 生成损坏或缺少公开证明夹具。

## 边界

保持此项验证 public-safe：

- 无原始 Codex transcript 或 session 资料；
- 无凭据、认证资料或私有本地路径；
- 无 benchmark 日志、任务文本、轨迹或生产 evidence；
- 验证器不执行 Codex。

参见：

- [Codex CLI 打包安装路径](codex-cli-packaged-install.md)
- [Codex CLI 首次运行彩排](codex-cli-first-run-rehearsal.md)
- [Codex CLI proof-capture 演示](codex-cli-proof-capture-demo.md)
