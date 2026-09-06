# LoopX 实验（Experiments）

> [English](README.md)

本包是 LoopX 的原型实验室。它容纳那些值得评估、但尚未纳入稳定产品契约的可执行
feature。

## 放置规则

当以下条件全部成立时，把 feature 放入 `loopx/experiments/<experiment-id>/`：

- 它显式 opt-in，且没有默认 LoopX 路径依赖它；
- 其调用方契约或生命周期预期仍会变化；
- 它没有注册的 provider-neutral capability 所有者；且
- 删除该实验不应需要兼容性迁移。

一个实验在一个包里拥有自己的契约、运行时与实验特定 provider 适配器。把它的
测试、可运行示例与手工脚本放到 `tests/experiments/`、`examples/experiments/`
与 `scripts/experiments/` 的对应路径下。

不要仅仅因为某个 capability 标记为 experimental 就把本包用作内置 capability。
具有真实调用方结果、配置与生命周期的 capability 应位于
`loopx/capabilities/<capability-id>/`。通用 extension 注册与兼容机制属于
`loopx/extensions/`；可选 provider 只有在独立于某个原型实现了刻意的产品或
capability 契约之后，才应放在那里。

## 依赖与生命周期边界

- 实验可以导入稳定 LoopX 代码。稳定 LoopX 代码不得导入 `loopx.experiments`。
- 放置于此不注册 CLI 命令、capability、extension、调度器路由、安装器条目或
  发布默认项。
- 实验必须有聚焦的测试和至少一个受限、非实时的示例。实况探测保持为显式手工
  命令。
- 实验版本之间不承诺兼容。优先删除过时的入口点，也不要保留没有已验证调用方的
  包装器。

## 提升或移除

只有当一个实验具备稳定的调用方结果、明确的能力或运行时所有者、显式的启停与
失败语义，以及其目标生命周期的持久校验时，才把它提升。提升会把代码及其测试
移出 `experiments/`；除非真实迁移窗口要求保留第二条实现路径，否则不会让实验包
继续充当第二路线。

当证据不再支撑维护成本时，移除该实验。其共置的包、测试、示例与脚本应能作为
一次可评审变更整体移除。
