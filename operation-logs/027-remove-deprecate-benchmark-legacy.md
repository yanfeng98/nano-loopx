# 027 · 移除 `deprecate/`（上游 benchmark 重置遗留归档）

- **日期**: 2026-09-12
- **分支**: `260906-dev`
- **背景**: `deprecate/benchmark-legacy/` 是上游 2026-08-17 提交 `76fe5bfeb`（"refactor: reset benchmark research around native runners", PR #3267）把重置前的整套 benchmark 运行栈搬出活跃树形成的归档区（该提交 575 文件变更中 477 个是 `R100` 纯搬移）。其中 **139 个文件写的是绝对导入 `from loopx.benchmark…`**，而这些模块在同一次重置中已从活跃树删除（`loopx/benchmark`、`loopx/benchmark_adapters`、`loopx/benchmark_case_state`、`loopx/benchmark_ledger`、`loopx/benchmarks` 均不存在）—— 这些代码今天 import 即 `ImportError`，是彻底死代码。用户要求完整移除，且不影响 LoopX 功能。
- **用户决策（3 项）**: ① **一并删除**：连同 2.4 MB 研究档案与 5 个运行账本一起删，不留 stub；② **彻底静默**：文档/代码里的引用句直接删除，不改写为上游 URL；③ **改守卫**：接受与上游 `examples/docs-governance-smoke.py` 分叉，未来 merge 该文件可能冲突。
- **规模**: **481 文件删除（整目录） + 10 文件修改**。

## 扫描结论：为什么可以安全删除

| 面 | 结论 | 证据 |
| --- | --- | --- |
| 交付包 `loopx/**` | **零 import、零文件读取** | 全库仅 3 处命中，均非代码依赖：`canary/premerge.py:71`（字符串 token）、`canary/maintainability_ratchet.py:509`（**调用点只遍历 `loopx/**`，该分支本就不可达**）、`claude_goal_mode/__init__.py:21`（docstring） |
| `tests/**` | **零依赖** | 无任何测试模块读取或断言该路径 |
| 打包面 | 无条目 | `[tool.setuptools.packages.find] include = ["loopx*"]`，且该目录无顶层 `__init__.py` |
| 文档构建 | 无条目 | `mkdocs.yaml` 的 nav / `exclude_docs` 均无；`docs_dir: docs` 不含它 |
| 其他 | 无条目 | `package.json`、`tsconfig.control-plane.json`、`.gitignore`、`.gitattributes`、`loopx.egg-info/SOURCES.txt`、`loopx/canary/module_metric_baseline.json` 全部干净 |
| 全仓遍历器 | 只会变干净 | `loopx/contract.py` 的 `DEFAULT_SKIP_DIRS` 不含 `deprecate`，故以仓库根为 root 的扫描今天会走这 481 个文件；删除后仅 `scanned_files` 减少，**实测 3048 → 2567（差额恰好 481）**，两侧 `ok=True` / `hits=0` |

## 必须避免的破坏点（本次最高风险）

1. **`examples/docs-governance-smoke.py` 是唯一硬破坏面**，且它有 **3 处独立 fail 路径**：
   - `MOVED_PATHS` 两条（`docs/codex-cli-long-run-benchmark-design.md`、`docs/codex-cli-long-run-regression.md`）映射到归档内文件，被 `:630` 的 `assert (REPO_ROOT / new_path).is_file()` 断言 —— 目录一删即 fail；
   - `:644` 的 `read("deprecate/benchmark-legacy/README.md")` —— `read()`（`:128`）**无存在性守卫**，直接 `FileNotFoundError`；它把该 README 拼进 `combined_public_indexes`；
   - `:656` 的 `or new_path.startswith("deprecate/benchmark-legacy/")` 逃生舱 —— 删掉两条 `MOVED_PATHS` 后它失去主体，保留会让断言静默失去覆盖。
   **已实测预演**：脚本复刻该 smoke 断言逻辑，对 13 条 `MOVED_PATHS` 逐条判定 —— 11 条经 `combined_public_indexes` 满足，**仅**这 2 条依赖逃生舱。故「删 2 条 + 删逃生舱」自洽，波及其余条目为零。该 smoke 被 `loopx/canary/runner.py:392` 自动发现，failure 会传播到 canary `full-public` 套件与 profile `docs-project-content-ops`。
2. **`benchmark/README.md` 末尾那条相对链接是本轮唯一静默断链**，且**无任何检查器覆盖它**：`docs-governance-smoke.py` 的 `assert_local_doc_links_resolve` 只遍历 `DOCS.rglob("*")`，而 `benchmark/` 在 `docs_dir` 之外。结论：必须手工删除，不能指望守卫报错。
3. **`pyproject.toml` 的 `norecursedirs` 存在方向性陷阱**：现值为 `["deprecate"]`，它**覆盖**（而非追加）pytest 默认 ignore 集（实测 `getini('norecursedirs')` 只返回 `['deprecate']`）。正确处置是**整表删除**（回落默认集 `*.egg .* _darcs build CVS dist node_modules venv {arch}`，是 `["deprecate"]` 的**超集**，只可能排除更多、不可能多收集）；若改成空列表 `[]`，pytest 将不再排除任何目录 —— 危险方向（仓库内确有 `apps/presentation/dashboard/node_modules`，217 MB）。收集中性已实测：`tests/` 内唯一命中默认模式的是 `tests/fixtures/change_quality/oracles/rust/.cargo`（含 1 个 `config.toml`，无 `.py`、无 `conftest.py`），删除前后 `--collect-only` 均为 **5597 collected / 4 errors**。
4. **canary `BENCHMARK_SENSITIVE_TOKENS` 是死 token，但删它并不能免除本次提交的人工复核**：`premerge.py` 的 `_path_matches`（`:243-252`）是子串匹配且作用于变更文件列表。实测 `build_premerge_validation_gate(changed_files=<本次 494 路径>, execute=False)` → `surfaces` 含 `benchmark_sensitive`、`manual_holds` 1 条、`gate: manual_review_required` —— **本次提交编辑了 `benchmark/README.md`，仅凭 `"benchmark/"` token 就会触发该 surface**，与 deprecate token 无关。因此：删除 token 的理由是**它指向的路径已不存在、会变成永久死配置**（而非免除 hold）；保留它反而会对未来任何 `deprecate/` 命名路径产生幻影 hold。hold 本身是软性的 `manual_review_required`，非失败。
5. **假阳性，绝不可误删**：全库 `deprecate` 宽松命中大多是无关词 —— `authority_registry_deprecated_count`（authority 注册表字段）、`/deprecated/frontstage/ops` 与 `views/deprecated/`（dashboard 弃用路由与目录）、`field-derived-patterns.md` 的 `deprecated`（文档状态词表）、前端 bundle 里的 `deprecated-frontstage-ops-status` CSS 类。精确词必须用 `deprecate/benchmark-legacy`。

## 变更清单

### 整目录删除（481 个 tracked 文件）

`git rm -r deprecate` —— `deprecate/benchmark-legacy/` 全量：341 个 `.py`（30 个 benchmark adapter + skillsbench/terminal-bench 远端容器与隧道基建脚本）、134 个 `.md`（含 `docs/research/long-horizon-agent-benchmarks/` 研究档案）、5 个 `.json`（`benchmark-run-ledger.json` 859 KB 覆盖 skillsbench@1.1 45 case / terminal-bench@2.0 19 case / swe-marathon 3 case 等）、1 个 `.sh`，外加其 `tests/`、`examples/`、`regression/` 子树。

### 守卫手术 `examples/docs-governance-smoke.py`（4 处）

删 `MOVED_PATHS` 两条 + 删 `read("deprecate/benchmark-legacy/README.md")` + 删 `startswith("deprecate/benchmark-legacy/")` 逃生舱 + 删负断言列表里的死条目。

### 文档与 docstring 净删（彻底静默）

`benchmark/README.md`（末段整段）、`docs/research/README.md`（2 行 bullet）、`docs/integrations/worker-bridge-install-contract.md`（归档句，保留其后 `benchmark/` 那句）、`docs/architecture/rfcs/long-horizon-harness-benchmark-research-program-v0.md`（1 行 bullet）、`loopx/capabilities/benchmark_toolkit/README.md`（2 处：归档 reducer 句 + 历史包句）、`docs/development/documentation-layout.md`（表格末格改为「过时 runner 移出活跃交付面」）、`AGENTS.md`（政策句改写为「不进入活跃 CI」，保持语义）、`loopx/claude_goal_mode/__init__.py`（docstring 末句）。

### 配置与 canary 死条目（4 处）

`pyproject.toml`（整删 `[tool.pytest.ini_options]` 表）、`sonar-project.properties`（注释 + exclusion 列表去 `deprecate/**`）、`loopx/canary/premerge.py`（删 token）、`loopx/canary/maintainability_ratchet.py`（`_is_benchmark_module_path` 去不可达分支，函数保留以服务 `benchmark/` 与 `benchmark_toolkit`）。

## 逐字保留（历史记录，不改写）

- 全部 `operation-logs/**`（015–026 中 `deprecate/**` 出现在「逐字保留」清单里 —— 那是对**宿主移除**而言，本次移除对象不同，不冲突）。
- **`deprecate/` 的存证**：上游 commit `76fe5bfeb` + 上游路径 `huangruiteng/loopx:deprecate/benchmark-legacy/`。本 fork 不再保留副本，历史可经本仓库 git 历史与其上游追溯。

## 验证

- **零残留（精确词 `deprecate/benchmark-legacy`）**：全库扫描（排除 `.git/`、`node_modules/`、`__pycache__/`、`operation-logs/`、`loopx.egg-info/`、`.code-review-graph/`）→ **0 命中**。
- **守卫**：`examples/docs-governance-smoke.py` → **通过**（`docs-governance-smoke ok`），文件内 `deprecate` 残留 0。
- **保全面扫描**：`scan_public_boundary([REPO_ROOT])` 两侧对照 → HEAD `scanned_files=3048` / 本树 `2567`（**差额 481，与删除数逐一对应**），两侧均 `ok=True`、`hits=0`。
- **ruff**：改动的 4 个 `.py` `ruff check` **All checks passed**；`git diff --check` 干净。
- **全量 pytest 基线对照**：见下表（口径同 015–026：跑 `tests/`，`--continue-on-collection-errors`，干净 HEAD worktree `e2fbeb689` 对照）。

<!-- PYTEST_TABLE -->
| | collected | passed | failed | skipped | errors |
|---|---|---|---|---|
| 干净 HEAD worktree（`e2fbeb689`） | 5597 | 5561 | 11 | 25 | 4 |
| 本树 | 5597 | 5561 | 11 | 25 | 4 |
| 差额 | **0** | **0** | **0** | 0 | 0 |

**本次与 026 不同：预期差额就是 0** —— 被删归档虽有自带的 `tests/**`（341 个 `.py` 中含测试文件），但 pytest 的收集根是仓库 `tests/`，且归档内**没有** `conftest.py`/`pytest.ini`/`pyproject.toml`，故它从未被收集。

- **收集集合**：两侧 `--collect-only -q` 各 **5597** 条，`comm -3` 双向 **0 差异**；4 个 collection error 归一化路径后**逐字一致**。
- **失败集合逐条比对**：15 条（11 failed + 4 errors）`diff` 为空 → **0 新增失败**。既存失败为 `.github/` 缺失族（`test_python_ci_workflow`、`test_sonarcloud_workflow` ×3）、`test_repository_change_window`（本机 git 不支持 `worktree list --porcelain -z`）、canary fleet health ×3、scheduler ack ×2、dashboard launcher、pr-program snapshot、outbound guidance/refresh checkpoint/shared goal alignment（collection error）。
- **`norecursedirs` 表删除的收集中性已单独实测**（见「必须避免的破坏点」§3），且上表的 0 差额同时覆盖了它。

## 过程记录（自查发现并修正的问题）

- **切勿把已删文件喂给 lint**：首轮 `ruff check` 用了 `git diff --cached --name-only`，把 481 个已 staged 删除的路径一起传进去 → 481 条 `E902 No such file or directory`。改用 `--diff-filter=ACMR` 过滤后正常。
- **`ruff format --check` 的既有不合规不是本次引入**：3 个改动文件在 HEAD 上就已被判定需重排（`docs-governance-smoke.py`、`canary/premerge.py`、`canary/maintainability_ratchet.py`）。本仓库质量门是 `ruff check`（015–026 口径），故**不执行** `ruff format` 以免引入无关 churn；仅手工把 `_is_benchmark_module_path` 缩短后的返回式收敛为单行。
- **`examples/repository-hygiene-smoke.py` 是既存失败**，与本次无关：它在 `validate_required_tracked_files` 处断言缺失 `LICENSE`（本 fork 在 `6ebad6b09` 已移除许可证）。**该失败在干净 HEAD worktree 上逐字复现**。因其在 boundary 断言之前就退出，本轮改为直调 `scan_public_boundary` 取得对照证据（见上）。
- **独立复核纠正了两处初稿错误**（对抗式复查的价值）：
  - 初稿称「同提交删除 canary token 可避免本次提交被判 `benchmark_sensitive`」—— **错误**。实测 `build_premerge_validation_gate(changed_files=<本次 494 路径>, execute=False)`：本次编辑了 `benchmark/README.md`，仅凭 `"benchmark/"` 子串 token 就已触发该 surface 与 `manual_holds`，与 deprecate token 无关。删 token 的正确理由是它已成永久死配置（见「必须避免的破坏点」§4，已订正）。
  - 初稿称「仓库根无 `node_modules`」—— 表述失准。仓库内确有 `apps/presentation/dashboard/node_modules`（217 MB，**含 0 个 `.py`**）。norecursedirs 的结论不变（默认集是超集，只可能排除更多），但论证依据改为「收集中性已实测：两侧 `--collect-only` 均为 5597 / 4 errors」（已订正）。
- **`_is_benchmark_module_path` 的收敛程度经复核后收敛**：两条 `startswith` 分支在唯一调用点（`:585` 只遍历 `loopx/**`）下**均不可达**，唯一活谓词是 `"benchmark_toolkit" in parts`；但该函数是「路径是否归属 benchmark 树」的 policy 谓词，未来若有调用方传仓库相对 `benchmark/...` 路径仍需该子句，故**只去 `deprecate` 分支、保留函数**。

## 第二轮复查（对抗式：换新角度、取新证据）

目标是**找「我的改动是否破坏了什么」**，只采信与首轮不同的角度与证据（首轮已做的不复述）。

| 新角度（首轮未覆盖） | 证据 | 结论 |
| --- | --- | --- |
| **全部 6 个 canary profile**（首轮只单独跑了 8 个守卫，未跑套件本身） | 两侧逐 profile 运行 + `FAILED` 集合逐字 `diff` | **6/6 集合一致，0 新增失败**：docs-project-content-ops 8F/65P、canary-runner 2F/9P、core-control-plane 30F/194P、extension-runtime 12P、public-entry-install-release 8F/12P、public-smoke-watch 32F/194P |
| **`catalog-planner-smoke` 真伪鉴定** | 该 smoke **不在 `tests/` 内**（首轮全量套件覆盖不到它）；在本树与未改动的 `HEAD~1` 两侧各跑一次，归一化路径后 **整体 diff = 0 行** | 既存失败（与 026 记录的 canary 既存失败清单中的 `catalog-planner` 对应），**非本次引入** |
| **裸 `pytest`（无路径参数）行为** —— `norecursedirs` 表删除唯一未被首轮覆盖的面 | 两侧 `pytest --collect-only -q`：收集数 **5649 = 5649**、ID 集合 `comm` **0 差异**；耗时 **8.21s → 2.02s** | 收集集合不变，且默认 ignore 集恢复后遍历更快（首轮只证明了 `pytest tests/` 这一路径参数下的中性） |
| **归档的其它标识符**（首轮只扫了 `deprecate/benchmark-legacy` 这一路径前缀，会漏掉不带前缀的引用） | `benchmark-legacy`｜`benchmark_legacy`｜`long-horizon-agent-benchmarks`｜两条被移走 doc 的文件名，逐词全库扫描 | 仅 `mkdocs.yaml` 命中一条既存悬空条（已按用户决定删除，见下方「第二轮补充处置」）；**其余全部 0 命中** |
| **是否有人 import 我改动的两个符号** | `_is_benchmark_module_path`、`BENCHMARK_SENSITIVE_TOKENS`、`classify_premerge_surfaces` 全仓引用扫描 | 仅同文件内部使用 + `tests/test_public_package_lock_boundary.py`（全量套件已覆盖，两侧一致） |
| **manpage / 构建产物面** | `render-manpage.py --check man/loopx.1` 两侧一致；`cli-help-manpage-smoke` 通过；`loopx.egg-info/SOURCES.txt` 0 命中 | 无影响 |
| **产品自检命令** | `loopx doctor`（TS 控制面 `ready`）、`loopx status` 两侧输出**逐字一致** | 运行时无变化；`status` 里的 `runtime_projection_routes: healthy=False` 两侧同值，属环境性既存状态 |
| **change_quality fixture 是否耦合** | `tests/fixtures/change_quality/{five_pr_calibration,model_shadow_matrix}.json` 里的 `maintainability_ratchet` 命中，均为 `changed_files` 数组中的**文件名**，非 oracle/token 快照 | 与本次改动无耦合 |
| **文档构建** | `dev-book-publication-smoke`（含 `mkdocs build --strict` 路径）、`docs-asset-integrity-smoke`、`showcase-catalog-smoke` 均绿 | 文档面完整 |

**第二轮结论：未发现任何由本次改动引起的问题。** 上面每一格的两侧比对都是「逐字一致」而非「看起来差不多」。

### 第二轮补充处置：`mkdocs.yaml` 的悬空 exclude（用户拍板删除）

`mkdocs.yaml` 的 `exclude_docs` 中有一条 `research/long-horizon-agent-benchmarks/*.json`，是**既存悬空条目**（该目录在本 fork 的 `docs/` 下从未存在，同族文件只在被删归档里）。第二轮把它报给用户后，用户决定**删除**（延续「彻底静默」）。删除前完成的验证：

- 该模式的目标面已证明为空：`docs/research/` 只有 `README.md` 与 `agent-workflow-audits/…v0.md`，**JSON 文件 0 个**、无 `long-horizon-agent-benchmarks` 目录 → 模式零匹配，删除是**可证的 no-op**；
- 两侧 `mkdocs build --strict` 均 **exit 0**；站点产物中带 `long-horizon` 字样的 3 个页面（`reference/protocols/long-horizon-agent-state-protocol-v0`、`architecture/rfcs/long-horizon-harness-benchmark-research-program-v0`、`development/control-plane-course/topic-long-horizon-convergence`）**两侧完全相同**，与归档无关；
- 站点文件清单两侧的唯一差异是 `./__pycache__/__init__.cpython-312.pyc`：来自本机 `docs/__pycache__/`（**未跟踪、被 gitignore、日期 2026-09-06，早于本次工作**），HEAD worktree 因未跟踪文件不进 worktree 而不含它 —— 与本改动无关，非仓库内容。

## 已知遗留（不在本次范围）

- `examples/repository-hygiene-smoke.py` 的 `LICENSE` 断言失败（HEAD 已存在，需另立条目决定是恢复 LICENSE 还是改断言）。**注意**：该 smoke 的 `scan_public_boundary` 断言在 `LICENSE` 检查之后，因此**在本 fork 从未真正执行过** —— 不要把它当作 boundary 证据，boundary 结论以直调扫描为准。
- `loopx/web/chat/assets/*.js` 前端构建产物中的 `deprecated-frontstage-ops-status` 等字符串与本主题无关（dashboard 弃用路由的 CSS 类名），非残留。
- 上游 `deprecate/` 仍存在于 `upstream/main`：未来 merge 上游若该目录有更新，会出现「本 fork 已删除 vs 上游已修改」冲突，**处置约定：一律保留删除**。
- **守卫分叉是永久的**：未来 merge 上游可能把两条 `MOVED_PATHS` 重新引入 `examples/docs-governance-smoke.py`；冲突处置必须「保留删除 + 保留裁剪后的 `MOVED_PATHS`」，否则 `assert (REPO_ROOT / new_path).is_file()` 会再次变红。

## 环境备注

基线对照口径同 015–026。本环境既有 collection error（`.github/` 缺失致 `test_python_ci_workflow.py` 等）与 `test_repository_change_window.py` 的本机 git `worktree list --porcelain -z` 失败原样保留，两侧一致。
