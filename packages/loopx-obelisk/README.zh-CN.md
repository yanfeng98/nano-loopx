# loopx-obelisk

`loopx-obelisk` 是 LoopX `decision-context` 的可选咨询上下文 provider。它让一个显式配置的 Decision Context profile 搜索一个由 LoopX 标准化的宿主会话 scope 选出的历史 Codex 任务。

该 provider 不解析 Codex 深链。LoopX Core 解析链接一次,并返回 `context_scope_ref=host-session:codex:<thread-id>`,来源是:

```bash
loopx --format json resolve-agent-thread \
  --thread-link 'codex://threads/<thread-id>'
```

把 provider 选择保留在被忽略的、owner 本地的 Decision Context profile 中,但只把一次性任务链接传给 `recall-context`。一个最小化的仅 provider profile 是:

```json
{
  "schema_version": "decision_context_profile_v0",
  "goal_id": "<goal-id>",
  "enabled": true,
  "enabled_agents": ["<agent-id>"],
  "source_provider_bindings": [],
  "sources": [],
  "context_provider": {
    "provider": "extension",
    "namespace": "peer-session",
    "max_results": 4,
    "timeout_seconds": 10,
    "config": {
      "extension_id": "loopx-obelisk"
    }
  },
  "automation": {
    "automatic_capture": false,
    "fail_open": true
  }
}
```

把该文件存放在被忽略的 owner 本地状态下。完整的 Decision Context 证据工作流可能还会配置权威来源与一个稳定的默认 `scope_ref`;一次性的任务回忆两者都不需要。

## 安装与激活

Obelisk 是一个单独的 AGPL-3.0 应用程序。这个 Apache-2.0 provider 不复制其实现,也不读取其 SQLite schema;它通过 `obelisk --version` 与 `obelisk --query` 边界调用已安装的公开 CLI。先单独安装 Obelisk,然后在与 LoopX 相同的 Python 环境中安装并激活本包:

```bash
npm install --global @obelisk-apps/cli
obelisk --build
python3 -m pip install packages/loopx-obelisk
loopx extension install \
  --manifest packages/loopx-obelisk/extension.toml \
  --execute --format json
loopx extension doctor loopx-obelisk --execute --format json
```

`obelisk --build` 是显式的、由 owner 控制的索引刷新。provider 从不隐式启动它;当新完成的任务历史需要可搜索时,重新运行它。

Decision Context profile 可以在安装这个可选包之前就已启用。provider 缺失、禁用或 doctor 过期的状态不会让 `recall-context` 作为命令失败:它返回 `status=unavailable` 加一个类型化的 `provider_readiness` receipt,不执行任何 provider 扫描或写入,并保持 profile 不变。按 receipt 恢复:

```bash
# provider 发行版或生命周期注册缺失
python3 -m pip install packages/loopx-obelisk
loopx extension install \
  --manifest packages/loopx-obelisk/extension.toml \
  --execute --format json

# 生命周期注册存在但被禁用
loopx extension enable loopx-obelisk --execute --format json

# 启用的注册没有当前 doctor 证明
loopx extension doctor loopx-obelisk --execute --format json
```

如果 doctor 报告 Obelisk CLI 或索引不可用,先安装 CLI 并显式构建 owner 本地索引,再运行 doctor:

```bash
npm install --global @obelisk-apps/cli
obelisk --build
loopx extension doctor loopx-obelisk --execute --format json
```

修复后无需编辑 profile;每次 recall 都会解析当前扩展生命周期状态。LoopX 绝不替 owner 安装 Obelisk 或运行 `obelisk --build`。

如果项目使用非默认的 LoopX runtime root,请把相同的全局 `--runtime-root <path>` 选项传给扩展生命周期命令与 Decision Context 命令。provider 从那个确切的生命周期状态解析;它绝不从不相关的默认运行时发现。

在不改动那类 profile 的情况下运行一次只读任务回忆:

```bash
loopx decision-context recall-context \
  --goal-id <goal-id> \
  --agent-id <agent-id> \
  --profile <ignored-private-profile.json> \
  --context-scope-ref 'host-session:codex:<thread-id>' \
  --query '<specific question for the selected task>' \
  --query-summary '<public-safe intent summary>' \
  --format json
```

提供的 scope 与 query 只用于这一次有界的 provider 调用,不会被 LoopX 持久化。顶层输出是本地私有的、瞬态的,因为它包含为当前 agent 回忆的文本。其嵌套的 public-safe receipt 只保留 `--query-summary`、provider 安全的摘要、分数与哈希引用。该命令不扫描权威来源,不创建 cursor 或 settlement 状态。回忆到的条目是不可信的咨询内容,绝不是指令。

不再需要时,禁用该 provider、移除 owner 本地 profile 绑定,并卸载其 Python 发行版:

```bash
loopx extension disable loopx-obelisk --execute --format json
python3 -m pip uninstall loopx-obelisk
```

LoopX v0 有意没有扩展状态删除命令。被禁用的注册保留为未就绪的生命周期历史;它不可调用。

## 权威与隐私边界

深链是非权威定位符。启用该扩展不授予 Goal、Agent、claim、lease、权限、工作区、生命周期、amendment 或写入权威。检索到的文本保持为本地私有、瞬态的咨询证据,绝不是指令。嵌套的公开 Decision Context receipt 只保留紧凑摘要、分数与哈希后的 provider 引用;它不包含原始 transcript 文本或 Obelisk 资源 id。事实只有通过现有的 LoopX 所有者(如 Todo evidence、Agent 证据日志、注册素材或受治理的 amendment)才变得持久。

该 provider 从不调用 `obelisk --build` 或 `obelisk --attune`。Obelisk 可能在 `--query` 过程中刷新其 provider 自有的本地搜索索引;该查询对来源任务与 LoopX 状态是只读的。失败、禁用、歧义的 provider 选择或过期的 doctor 状态在 Decision Context 内失败开放,不阻塞无关的权威来源。

wire 契约与验证命令见 [CONTRACT.md](CONTRACT.md)。
