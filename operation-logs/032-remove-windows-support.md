# 032 · 移除 Windows 支持（本 fork 只在 Linux 与 WSL2 运行）

- **日期**: 2026-09-13
- **分支**: `260906-dev`
- **背景**: 用户明确本 fork 只在 **Linux 与 WSL2** 运行。WSL2 的 `os.name` 是 `posix`，
  因此所有 Windows 分支在本机都是死代码。按用户决策**全面清除 CLI 与运行时**的 Windows 面。
- **用户决策（1 项）**: 范围为「CLI 与运行时全面清除」——含安装/升级路径（A 类）与运行时
  移植分支（B 类）；**不动**桌面壳 `apps/desktop`（本机无 Windows 也无 cargo 链，Rust 改动
  无法编译验证，且它是 macOS 产品面）。

## 有意保留（不是"移植代码"，删了会削弱功能）

| 保留项 | 理由 |
| --- | --- |
| `memory_utility.py` / `coordination/head.py` 的 `PureWindowsPath(...).is_absolute()` | **public-safe / 协调域的输入校验**：拒绝把 `C:\…` 当成合法的本地/仓库路径。删掉会削弱校验，与"移除移植分支"无关 |
| `examples/visible-governance-slice-smoke.py:49` 的 `assert "C:\\" not in text` | 同上，是"Windows 风格路径泄漏"的公开边界断言 |
| `package-lock.json` / `Cargo.lock` 里的 win32 依赖条目 | 生成物；手删条目会弄坏锁文件 |
| `docs/archive/**`、`docs/plans/**`、`docs/superpowers/plans/**`、`docs/product/release-readiness.md` 的历史版本条目、`docs/architecture/rfcs/**`、`docs/community/ecosystem-adoption.md`、`docs/book/chapters/source-validation-to-pr.md` 的复盘叙述 | **历史记录**，不是当前行为描述；按 020/027/028/029/030 的既有口径保留 |
| `file_lock.py` 的 stat-identity 降级路径（st_dev/st_ino 全零时退回 birthtime/ctime） | 不是 Windows 专有分支，是"stat 字段缺失"的**通用 fail-closed 降级**（也覆盖部分网络文件系统）；仅把注释里的 Windows 归因改为平台中立 |
| `control_plane/testing/authority_e2e_ladder.py` 的 `posix_only` 字段 | 该字段是**行元数据**且出现在序列化 payload 里；本轮只删掉"在 Windows 上判 unverified"的判断，字段保留（它仍然准确描述这些行的验证范围） |
| `apps/desktop/loopx-control-plane/src-tauri/src/bundled_runtime.rs` 对 `scripts/install-windows.ps1` 的引用 | 桌面壳按用户决策不动 → 该引用现在**悬空**，见「已知悬空引用」 |

## 变更清单

### 删除（4 个 Windows 专有文件 + 1 个目录条目）

`loopx/windows_install.py`（13.8 KB）、`scripts/install-windows.ps1`、`scripts/loopx.ps1`、
`tests/test_windows_install.py`（11.7 KB，17 处断言）；`loopx/canary/quality_surface_catalog.py`
的 `host_upgrade` 条目由 `tests/test_windows_install.py` 改为 `_not_applicable`
（"本 fork 只在 Linux 与 WSL2 运行；Windows 安装面已移除"）。

**依赖核实**：`windows_install.py` 的产品侧消费者为 0（只有自身的 `.ps1`、该测试与 catalog
引用），因此不存在 026 那种"必须先断 import 再删包"的耦合。`scripts/loopx`（POSIX wrapper）
**未受影响**——被删的只有 `.ps1`，核实 `install-local.sh:456/566-567`、`release_candidate.py`、
`premerge.py` 引用的都是 `scripts/loopx`。

### 产品代码（13 个文件）

- `loopx/doctor.py`：删 `_powershell_literal`、`local_install_command` 与
  `no_clone_upgrade_command` 的 nt 分支、`install-windows.ps1`/`loopx.ps1` 的选择、
  fix 文本里的 Windows PATH 分支。
- `loopx/self_update.py`：删 4 处（`_command_for_source` 的 nt 早退、release snapshot 的
  `apply_supported = os.name != "nt"`、`execute_update_plan` 与 `execute_rollback_plan` 的
  `unsupported_platform` 早退）。
- `loopx/command_invocation.py`：**重写**为纯 PATH 解析；删 PowerShell 脚本发现、
  `pwsh` argv 构造、`LOOPX_COMMAND_PATH`（nt 专用逃生口，全库无其他引用）、`home` 与
  `pwsh` 参数。
- `loopx/file_lock.py`：删 `msvcrt` 导入与字节区间锁分支、`_prepare_windows_lock`、
  `*.lock.holder.json` sidecar 命名、`_windows_process_is_alive`（ctypes/WinDLL）与
  `process_is_alive` 的 nt 分支；保留 `flock` 路径与通用降级。
- `loopx/extensions/process_runtime.py`：删 `taskkill` 进程树终止与 `CREATE_NEW_PROCESS_GROUP`；
  `start_new_session=True` 固定为唯一路径。
- `loopx/control_plane/coordination/local_authority_shadow_outbox.py`：删目录 fsync 的 nt 早退。
- `loopx/cli_commands/todo.py`：同上（`os.name != "posix"` 早退）。
- `loopx/control_plane/coordination/file_provider.py`：更新两处把降级路径归因于 Windows 的注释。
- `loopx/control_plane/testing/authority_e2e_fixtures.py`：删 `USERPROFILE` 注入。
- `loopx/control_plane/testing/authority_e2e_ladder.py`：删"posix_only 行在 nt 上判 unverified"。
- `loopx/claude_goal_mode/scripts/install.py`：`venv` 的 `bin/python` 固定（删 `Scripts`/`python.exe`）。
- `loopx/slash_command_install.py`：删 codex-skills 指令里的"原生 Windows 用 PowerShell 7"提示。
- `loopx/python_install_owner.py`：删本轮 031 新增的 nt 引号分支（`_quote_local_path` →
  直接 `shlex.quote`），并随之移除 `os` 导入。
- `scripts/external_scheduler_worker.py`：删 `COMSPEC`/`cmd.exe /d /s /c` 分支。

### 测试与示例（9 个文件）

- 删：`tests/test_windows_install.py` 整文件；`tests/test_workflow_skill_install.py` 的
  `_ByteRangeLockBackend` + `test_install_takes_the_windows_lock_branch_without_fcntl`；
  `tests/test_file_lock.py` 的 `test_cross_runtime_windows_pid_probe_is_non_signaling` 与
  `msvcrt` 导入/skipif 条件；
  `tests/test_self_update_runtime_activation.py` 的 `test_windows_execute_update_fails_closed_without_launching_bash`。
- 改：`tests/test_command_invocation.py` **重写**为 POSIX 版（发现 + argv 两条断言，保住模块覆盖）；
  `tests/test_doctor_install_freshness.py` 的 5 处 nt 断言改为固定 POSIX 期望；
  3 个 control_plane 测试的 `skipif(os.name == "nt")` 去掉；
  `tests/extensions/test_extension_scaffold.py` 的 `symlinks`/`Scripts`/`python.exe` 固定为 POSIX；
  `examples/project/global-registry-writability-smoke.py` 删 nt 早退；
  `examples/dashboard-demo-readiness-smoke.py` 的 `tsc.cmd` 固定为 `tsc`；
  `examples/dev-book-publication-smoke.py` 的断言由 `Windows PowerShell 7` 改为 `POSIX shell`。

### 文档（活文档 6 处；历史记录保留）

- `README.md`：要求行改为「本 fork 只在 Linux 与 WSL2 上运行，使用 POSIX shell」。
- `docs/guides/installing-loopx.md`：**整段删除**「原生 Windows PowerShell 7」（50 行，含其
  升级/回滚/卸载小节）。
- `docs/reference/protocols/file-lock-acquisition-v0.md`：协议描述改为纯 `flock` + `*.lock`
  单文件契约（删 `msvcrt` 与 `*.lock.holder.json` sidecar 两段）。
- `docs/book/chapters/05-connect-existing-project.md`：要求行改 `POSIX shell（macOS、Linux 或 WSL2）`；
  结尾的"原生 Windows 安装"指引改为通用表述 + 本 fork 平台声明。
- `docs/development/control-plane-course/07-host-scheduler-and-heartbeat.md`：删设计叙述里的 "Windows"。
- `examples/shared-goal-authority-e2e/README.md`、`loopx/capabilities/benchmark_toolkit/README.md`：
  删"POSIX 专用行在 Windows 上跳过"与"Windows Job Object"两处过时/无关表述。

## 验证

- **静态**：`ruff check tests loopx/canary loopx/control_plane loopx/domain_packs loopx/presentation`
  → 仅剩 **2 个既存 F401**（`tests/control_plane/test_goal_activation.py`，本 op 未触碰该文件）；
  本 op 触碰的全部文件单独跑 ruff → All checks passed。
- **受影响的聚焦测试**：file_lock、command_invocation、doctor freshness、self_update、
  workflow_skill_install、extension_scaffold、shared_goal_authority_e2e、
  local_authority_shadow_cli_e2e → 全绿。
- **文档与示例守卫**：`docs-governance-smoke`、`dev-book-publication-smoke`、
  `repository-hygiene-smoke`、`cli-help-manpage-smoke`、`global-registry-writability-smoke`、
  `visible-governance-slice-smoke`、`loopx-update-smoke` → 全绿。
- **残留扫描**：`os.name == "nt"` / `sys.platform == "win32"` / `install-windows` / `SkipSkills` /
  `taskkill` / `msvcrt` / `PowerShell` / `pwsh` 在 `loopx`+`tests`+`examples`+`scripts` 内
  **除"有意保留"表列出的项外 0 命中**；`pyproject.toml` / `package.json` 无 Windows 引用；
  被删的 4 个文件在 examples/tests 内 0 引用。
- **全量 pytest**（口径同 015–031：`tests/` + `--continue-on-collection-errors`）：
  `5 failed / 5567 passed / **19** skipped / 3 errors`；与 031 后对照
  `5 / 5567 / 25 / 3` → **失败集合 `diff` 为空**、`passed` **相同**、`skipped −6`。
  **−6 可逐项归因**：被删的 Windows 专有测试在本机（Linux）本来就处于 skipped 状态——
  `tests/test_windows_install.py` 4 个 + `test_self_update_runtime_activation.py` 的
  Windows 边界测试 1 个 + `test_command_invocation.py` 的 PowerShell 测试 1 个 = 恰好 6。
- **`mkdocs build --strict`**：exit 0（构建产物 `output/` 已清理）。
- **premerge 门**：catalog canaries **5 过 3 失败**、risk profile 7 过 1 失败、direct checks 与
  public boundary 通过。4 条失败**全部经三 ref 对照证明为既存**（详见下节）。
- **产品行为未变**（本机实测）：`loopx doctor` → `ok: true`、`install_kind: live_checkout`、
  `upgrade_command` 仍是就地 editable 刷新、`fix` 首行仍是 "Refresh this editable checkout in
  place:"；`loopx update plan` → `owner: source_checkout`、`apply_supported: False`、
  `owner_upgrade_command` 同前。

### 门里 4 条失败的定性（全部既存，逐条有机制解释）

| smoke | 机制 | 对照 |
| --- | --- | --- |
| `codex-cli-packaged-install-smoke` | 打 tar 时读已删除的 `LICENSE`（031 已记录） | 三 ref 一致 |
| `canary/catalog-planner-smoke` | 030/031 已记录的既存失败（catalog profile 数为 0） | 三 ref 一致 |
| `cli-output-budget-regression-smoke` | **基线选取问题**：该 smoke 默认 `--base-ref=origin/main`，而本分支领先 `origin/main` **216 个提交**，于是它把"整条分支的差异"当成输出增长。以 `LOOPX_CLI_OUTPUT_BASE_REF=HEAD` 重跑 → **`ok`、exit 0**（证明本 op 的改动在允许额度内） | 三 ref 一致红；改 base 后绿 |
| `hot-path-interface-budget-smoke` | **绝对预算超限**：`heartbeat_prompt_json` 实测 **3587** > `max_json_chars` **3500**（与本 op 无关的既有溢出） | 三 ref 一致（含以 HEAD 为 base 时） |

> 注：这两条 budget smoke 此前从未被 015–031 的门选中（它们只在 diff 触及 CLI 输出面时才入选），
> 因此本 op 是**首次**把它们暴露出来——属"发现"而非"引入"。

## 已知悬空引用（按用户决策未处理）

`apps/desktop/loopx-control-plane/src-tauri/src/bundled_runtime.rs:108` 仍调用
`scripts/install-windows.ps1`，而该脚本已删除。桌面壳本轮明确不动（本机无 Windows、无 cargo
构建链，Rust 改动无法验证）。影响面仅限"在 Windows 上构建桌面壳"，本 fork 不存在该场景；
若将来要清，属独立一轮。

## 与上游分叉

新增/改写为 fork 版本：上述 13 个产品代码文件、9 个测试/示例文件、6 处文档；4 个 Windows 专有
文件为整删。合并上游时**保留 fork 版本**（上游会带回 Windows 支持），按本日志「有意保留」表
区分"该删的移植分支"与"该留的校验代码"。

## 环境备注

无新增环境性失败。本机 `os.name == "posix"`，所有被删分支此前均未执行；WSL2 同样是 `posix`，
故本次移除不改变本机任何运行路径。
