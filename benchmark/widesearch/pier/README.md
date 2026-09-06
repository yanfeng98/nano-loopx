# WideSearch 真沙盒模板(pier)

WideSearch 真沙盒路径的可复用、provider-neutral pier 接线。把这些模板复制到本地 pier 数据集根目录,并填入 `<PLACEHOLDER>` 值。不要提交凭据、本地绝对路径、原始运行或 verifier 输出。judge 密钥只注入独立的 verifier;模型 provider 密钥留在 runner-owned gateway 中,位于 agent 容器之外。

pier 期望的布局(任务根目录):

```text
<task-root>/
  task.toml            <- task.toml.template
  environment/
    Dockerfile         <- environment/Dockerfile.template
  tests/
    Dockerfile         <- tests/Dockerfile.template
    test.sh            <- tests/test.sh.template
    widesearch_evaluator.py
    <gold.csv>
  instruction.md
```

关键接线事实:

- 工作区与 `jobs_dir` 必须位于 `$HOME` 下:colima 不 bind-mount macOS 的
  `/tmp`,因此 verifier 的 `/logs/verifier` 绑定挂载在那里会静默失败,reward 永远回不到宿主。
- verifier 镜像必须创建 `/app`(`WORKDIR /app`),因为 pier 用 `docker compose cp` 把答案产物复制进 verifier 容器。
- `test.sh` 写入纯数值的 `reward.json`。pier 的
  `VerifierResult` 是 `dict[str, float | int]`;字符串 detail 字段会使 trial 失败。写入前用
  `loopx benchmark verify-verifier-reward <reward.json> --require-valid` 验证。
- agent 镜像必须把 `/bin/sh` 符号链接到 bash(pier 的 agent setup 使用 `set -o pipefail`;Debian 的 dash 不支持)。
- gold 只存在于 verifier 镜像中;agent 镜像绝不包含它。

模型凭据:可计数的运行必须通过 runner-owned 本地 gateway 路由 agent 镜像。真实 provider 凭据留在 gateway 进程中,位于 agent 容器之外;Codex provider 配置只接收一个固定的非密钥 sentinel。这是完整性证明中 `provider_credential_shell_excluded` 所需的具体边界。web 研究 benchmark 请在完整性策略中使用 `network_access: "permitted_solving"`(见 `loopx.capabilities.benchmark_toolkit.integrity`)。
