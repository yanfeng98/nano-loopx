# 036 · 切断上游牵连 + 两条安装路径（editable / 本地 wheel）

- **日期**: 2026-09-13 → 2026-09-14
- **分支**: `260906-dev`
- **背景**: 用户决定**不再与 huangruiteng/loopx 源头发生关系**，安装方式收敛为两条：① checkout 就地
  editable 安装；② **本地构建的 `*.whl` 离线安装**（不走 PyPI、不联网、不用上游发布版）。
  这推翻了此前"保留上游发布/canary 通道"的立场（op 031/034）。
- **状态**: **P1–P4 已完成并推送**；**P5–P7 未开始**（见文末）。

## 用户确认的决策（8 条）

1. **范围**：只清**活面**；历史（`operation-logs/`、`docs/archive/`、`docs/update-notes/`）原样保留；
   **保留** `upstream` git remote。
2. **渠道脚本**：`scripts/install-from-github.sh` 与 `scripts/install-local.sh` **都删**，周边机制与守卫
   **一并退役**（这是 P5）。
3. **产品文案**：doctor / bootstrap / `loopx update` 一律指向**本地 wheel 重装**，PyPI / install.sh /
   codeload 字符串归零（P5 收尾）。
4. **包身份**：分发名与 import 包名保持 `loopx`；**版本 → 1.1.0**。
5. **身份 URL**：一律指向 fork 仓库 `https://github.com/yanfeng98/nano-loopx`。
6. **README**：删除 `## Star 趋势` 整节 + 退役其守卫；`loopx first-run-report` 改为**不带外链**的本地提示。
7. **wheel 交付物**：构建脚本 + 文档 + wheel smoke 三件。
8. **明确不做**：fixtures 里的 `huangruiteng/loopx`、frontstage 的 PR 链接与 fixtures、
   `loopx/web/chat/assets/*.js`（52 个产物）、`packages/loopx-repo-health` 与
   `packages/loopx-community-discussion`。

## 已完成的四个阶段（6 个提交，41 文件，+1288/−2619）

### P1 `48a7f2cc6` · 身份与版本

- 版本 1.0.0 → **1.1.0**（`pyproject.toml` + `loopx/__init__.py` + `man/loopx.1` 由
  `scripts/render-manpage.py` 重生）；`[project.urls]` → fork（删 Documentation/Changelog）；
  `mkdocs.yaml` 的 `repo_url`/`edit_uri` → fork、`site_url` 删除；`docs/book/mkdocs.zh.yaml` 同；
  `docs/capability_docs.py` blob 根、`loopx/configuration_catalog.py`（9 处）、
  `loopx/agent_onboarding.py`、`docs/index.md` → fork。
- README：顶部三链接改为**仓库内相对链接**；**删除 Star 趋势整节**并退役 4 个工具文件
  （`examples/readme-star-history-smoke.py`、`examples/frontstage-stargazer-fetch-smoke.py`、
  `scripts/render-star-history.py`、`scripts/fetch-github-stargazers.sh`）；首次运行反馈改为**无外链**。
- `loopx first-run-report`：去掉上游 issue 模板链接，改为本地提示（payload 的 `issue_url` →
  `feedback_hint`）。
- 同提交更新守卫：readme-demo-surface（1.0.x→1.1.x）、showcase-catalog（README 首页串）、
  dev-book-publication（版本派生 marker ×2）、release-artifacts（urls 精确字典）。

### P2 `89c75c587` · wheel 成为完整、离线的安装路径

- **打包缺口全补**（实测 `build/lib` 差集）：`loopx.canary = ["*.json"]`（缺
  `module_metric_baseline.json` 会让 `loopx canary` 的可维护性棘轮挂）、
  `loopx.claude_goal_mode` 的 plugin/commands/hooks/settings 资产、`loopx-material` 与
  `loopx-change-quality` 两个**项目级技能**（含 `.loopx-skill-scope` 标记）、
  `loopx.control_plane` 的 `.ts`/`.json` 改为**递归** glob。
- `loopx/capabilities/project_skill_delivery/core.py`：`canonical_project_skill_source` 先查
  checkout、再查打包的 `share/loopx/skills`（wheel 下原先解析到 `site-packages/skills/<id>` 必失败）。
- 新增 `scripts/build-wheel.sh`（**先 `rm -rf build/`**——setuptools 会复用陈旧 `build/lib`，这正是
  打包缺口长期被掩盖的原因；`pip wheel . --no-deps --no-build-isolation` 全程离线；`--out-dir`
  使测试可复用）、`docs/guides/offline-wheel-install.md`（含 **Node ≥ 22.6** 先决条件与"不要做"清单）、
  以及 **`examples/wheel-install-smoke.py`**（构 wheel → 临时 venv → 装 → 断言载荷/direct_url →
  doctor → skills → canary baseline → 发行版深度检查）。
- 新冒烟注册进质量目录与 `install-update` canary profile。

### P3 `18f66cd1a` · 两路口径（纯增字段）

- 新字段 `install_path ∈ {editable_checkout, local_wheel, index_install, unknown}`；
  `install_kind` 取值不变（兼容既有消费方）。
- `loopx/python_install_owner.py`：`read_direct_url`(PEP 610)、`classify_install_path`、
  `local_wheel_path`、`wheel_reinstall_command`。**pipx 作为同一 wheel 的安装工具**，不是第三条通道。
- 无 wheel 路径 / owner 未知 → **fail-closed**（返回 None，不猜命令）。
- 新增 `tests/test_install_paths.py`（三态判定 + 两种命令 + 负断言"绝不出现上游串"）。

### P4 `903ab12f4` · 退役归档与快照通道（最大一块）

- `loopx/self_update.py` **1432 → ~870 行**：删 source 配置（repo/ref/codeload/`LOOPX_ARCHIVE_URL`）、
  网络版本探测、runtime-activation qualification、快照回滚计划与命令、`build/execute_rollback_plan`、
  以及 `execute_update_plan` 的整个 archive 分支；`_install_lifecycle` 改为 local_wheel / index /
  editable / unknown 四态；载荷删除 `source`/`source_version_check`/
  `runtime_activation_qualification`；apply 改为重装录制的 wheel，无 wheel 时
  `missing_wheel_source` fail-closed。
- 删 `loopx/self_update_download.py` 及其测试；CLI 删 `--rollback/--repo/--ref/--archive-url/
  --installed-doctor-json` 与回滚分支。
- 重写 `tests/test_self_update_runtime_activation.py`（14 → 10 个用例，全部围绕两路）与
  `examples/loopx-update-smoke.py`（断言四个退役旗标不在 `--help` 里且调用被拒）。

### 两处修复

- `87a987490` **既有 bug**：在仓库根跑 `python3 -m loopx.cli` 时，cwd 在 `sys.path` 里让
  `importlib.metadata` 命中**陈旧的 `loopx.egg-info`** → doctor 把 editable checkout 误报成
  "pip 管理的发行版"（控制台脚本则报对，两种调用方式结论不一致）。已修（拒绝含
  `pyproject.toml`/`.git` 的"发行版根"）并补单测。
- `55617e7fa` **复核修正**：① doctor.py 撞破 1500 行棘轮（1508）→ 把两块逻辑下沉到
  `python_install_owner.py`（`distribution_upgrade_command` / `install_identity_fields`），
  doctor 回到 **1481 行**，不加豁免；② 我把 wheel 冒烟插在 canary profile 列表**最前**，挤掉了
  `loopx-update-smoke`（3 项预览上限）→ 破坏 `catalog-run-e2e-smoke`（基线通过），改为**追加到末尾**；
  ③ `docs/book/chapters/appendix-reference.md` 仍在教已删除的 `loopx update --rollback` → 重写为
  两路口径回滚；④ doctor 的人类可读输出补 `install_path`/`wheel_path`；⑤ wheel 冒烟补
  `loopx update plan` 断言（wheel 环境报 `local_wheel_install`）。

## 复核方法与结论

- **实施顺序复核**（Plan agent）给出 5 条设计冻结并被我采纳：新增 `install_path` 而非改
  `install_kind`；wheel 命令走**约定路径**而非 glob；pipx 归入 wheel 工具；`loopx update` 只做离线；
  `release_manifest` 只做最小切除。并纠正顺序：**wheel 路径必须先于删除任何通道**（已按此执行）。
- **全套 pytest**：当前树与基线（推送点 `45d30e987`、真实 clone）**失败集合逐条一致**
  （5 failed / 3 collection errors）。
- **premerge**：本批 diff 只剩 3 项**既存**失败（`codex-cli-packaged-install`、
  `catalog-planner`、`pytest-smoke-suite-facade`），每项都在基线验证"同点失败"。
- **wheel 端到端**：1129 条目 / 71 个 `.ts`（与仓库一致）；`direct_url.json` 记录 `file://…whl`；
  doctor 报 `install_kind: python_distribution` + `install_path: local_wheel`；`loopx update plan`
  在该环境报 `local_wheel_install` 且可 apply；skills 可交付；canary baseline 在包内。

## 未完成（P5–P7，尚未开始）

- **P5（最大、最具破坏性）**：删两个渠道脚本；把 `install_contract.py`/`bootstrap.py`/
  `project_prompt.py` 与 doctor 的 `fix` 树改写为两路口径（PyPI/install.sh/codeload 归零）；
  连带**退役约 30 个守卫与约 20 处文档**（`install-local-smoke`、`install-local-overwrite-smoke`、
  `fresh-clone-quickstart-smoke`、no-clone 验证文档+smoke、`claude-install-optin-smoke`、
  canary promotion 系列、`codex-cli-*-bootstrap-*` 的 install 串断言、`status-data-contract` 等）；
  canary 目录/planner 的脚本引用必须**同提交**更新（`quality_surface_catalog.py:523-538` 会对外不
  存在引用报 `missing_repository_reference`）。
- **P6**：`release-readiness.md` 的 PyPI/Trusted Publisher 段与发布清单；`release-artifacts-smoke`
  的 `.github` 死代码（**基线即红**）。
- **P7**：残余身份——桌面端 `LOOPX_REPO=huangruiteng/loopx` 与上游更新源、
  `apps/presentation/site` 的安装文案、`demo/auto_research` 与 `benchmark/swe-marathon` 的上游 URL。

## 已知残余（用户declined，不在本批处理）

- 打包进 wheel 的 dashboard 产物（`loopx/web/chat/assets/*.js`，52 个文件）**仍含上游 URL**——
  即"受支持的 wheel 安装"里仍能看到上游链接；
- frontstage 展示与 fixtures、`packages/loopx-repo-health` 与 `packages/loopx-community-discussion`
  仍以监控/引用上游为功能；
- `examples/frontstage-share-bundle-smoke.mjs` 要求发布件 `install.sh` 与
  `scripts/install-from-github.sh` **字节一致**——P5 删脚本会**阻断**它（需最小改法或显式排除）。

## 提交/推送

- `48a7f2cc6` docs: cut upstream identity and move to version 1.1.0
- `89c75c587` build: make the wheel a complete, offline install path
- `18f66cd1a` feat(install): tell the two install paths apart
- `903ab12f4` refactor(update): retire the archive and release-snapshot channels
- `87a987490` fix(doctor): stop treating a stale egg-info as an installed distribution
- `55617e7fa` fix(doctor): surface the install path and keep doctor within its line budget

按用户指示推送：`c3e11ee1d..55617e7fa`（6 个提交，一次 push；本日志为随后补记）。
