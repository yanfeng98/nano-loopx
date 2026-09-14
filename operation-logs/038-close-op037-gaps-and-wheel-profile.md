# 038 · 收口 op 037 的残余缺口 + benchmark 隔离 profile 改走 wheel 路径

- **日期**: 2026-09-14
- **分支**: `260906-dev`
- **背景**: 用户要求"仔细检查修复是否正确，如果存在问题就修复，不要破坏 loopx 的正常功能"。
  检查首先推翻了 op 037 的验证方法本身，再据此修掉它引入的两个**被掩盖**的回归，
  并把 benchmark 的隔离 profile 从已退役的发布快照安装器改写到 wheel 路径。

## 先推翻验证方法（本批最重要的发现）

op 037 记的是「全套 pytest 失败集合与基线逐条一致」。**这个检查无效**：
`heartbeat-prompt-smoke` 是顺序执行的脚本，**第一个断言失败即终止**；它死在
`:279` 的 compact 预算断言（6200 上限，实测 6403），而文档/生成物断言在
`:1001–1100`，**一行都执行不到**。同一测试名在基线与改动后都失败 → 集合当然
"一致"，但里面可能新藏了断点。

自查手法（本批新造，可复用）：

- **内存中和探针**：把失败断言整条改写成 `pass`（多行语句按括号配平），重跑并
  累积，直到跑完；全程不落盘。
- **基线对照**：对推送点 `45d30e98` 开 `git worktree` 跑同一探针，
  **按断言内容（不是行号，行号会漂移）**做集合差。
- **纯文档断言静态求值**：直接提取 `assert "<字面量>" in <变量>` 与真实文件内容
  比对，比重跑快得多。

结果：HEAD 43 条 vs 基线 41 条，集合差**恰好 2 条且都只在 HEAD**——即 op 037
引入的两个真回归；其余 41 条既有失败本批一条也没修好。

## P1 `8a82aa62a` · 收口（5 文件，+23/−147）

### 被掩盖的两个回归

1. **`getting-started` 丢了被断言的 `loopx-canary`**：P5 删掉该文档的 canary 章节
   （日志自称"整个上游 canary 章节删除"），却没同提交更新
   `heartbeat-prompt-smoke:1011`。该断言改为钉住文档**实际写出**的两种安装形态
   `editable_checkout` / `local_wheel`（已核两串确实存在，属非空通过，不是把期望
   改到不存在的东西上）。
2. **`compact_generated` 缺 `in-place editable checkout`**：P5 把守卫期望换成了
   `INSTALL_PATHS_HINT` 的措辞，而 heartbeat 生产者实际发的是
   `use the LoopX checkout (…) or a locally built wheel (…)`。生产者本身是准确的
   两路文案，**是期望抄错了来源**，故改期望而非改产品。

### 产品面（公开首页）

`App.tsx` 四处仍在宣传已退役的安装器：setup prompt 教 "no-clone installer"；
quickstart 正文称"官方安装器会注册轻量命令入口"；安装器链接指向
`docs/guides/offline-wheel-install.sh`——**该路径在本仓库从未存在过**
（真实文件是 `.md`，`git log --all` 为空）；标签仍是 "Inspect installer"。
四处一并改为本 fork 真实的两路口径，同提交更新 `frontstage-share-bundle-smoke.mjs`
的契约列表（该守卫自己第 138 行的注释早已写明安装器已删，契约列表却仍要求
`no-clone installer`——内部自相矛盾）。

### 其它

- `docs/integration.md` 的 canary 块结尾是一条**可复制执行**的
  `~/loopx/scripts/install-local.sh`；删该步，保留守卫钉住的
  `loopx-canary heartbeat-prompt` / `--cli-bin loopx-canary`。
- `cli-help-manpage-smoke` 仍断言已删安装器的 `--help`/`--unknown` 契约，
  `bash -n` 必崩；删该退役块与随之失效的 3 个导入 → **由崩转绿**。
- `--cli-bin loopx-canary` 属另一类：`loopx-canary` 是**被删安装器生成的 wrapper**
  （不在 `[project.scripts]`），与 op 037 遗留 #2 的晋升产品面同源，**未擅自退役**。

## P2 `d00f061f0` · benchmark 隔离 profile 改走 wheel（4 文件，+228/−109）

`profile_install.py` 整个建立在已退役的发布快照安装器上：要求
`scripts/install-local.sh` 存在、按安装器的 `LOOPX_*` 环境契约运行它，并用
`profile_cli_not_release_snapshot` 断言一个只有快照布局才满足的身份。op 037 删脚本
后它只能抛 `formal_installer_missing`，连带 swe-marathon 的 `run_mode` 臂与整个
widesearch case。op 037 把这条记成"行号注释"，**严重低估——它是执行路径**。

改为本 fork 支持的路径：从源树离线构建 wheel → `pip install --target` 铺进 profile
→ 用 profile 自己的 CLI 把技能物化进 profile 的 CODEX_HOME 并校验回读。
签名与消费者用到的字段不变（`release_root` 无外部消费者，已移除）。

三个取舍都由证据决定，不是偏好：

- **不用 venv**：`loopx_native_codex.py` 写明 profile 是**宿主机构建、随 tarball
  投递到任务镜像、两侧同一绝对路径**；venv 带宿主绝对路径与指向宿主解释器的
  `bin/python`。同理不用 pip 生成的 console script（实测 shebang 是
  `#!/home/.../miniconda3/bin/python3`）。落进 profile 的是纯 Python 发行版 +
  仓库自带 `scripts/loopx` 启动器（它已负责过滤 `sys.path` 上的 cwd、校验 3.11+、
  设 `LOOPX_RELEASE_ROOT`）。
- **写 `.loopx-python`**：与已删安装器同一机制（`install-local.sh:613`），也是
  `bundled_runtime.rs` 与容器臂都依赖的契约。实测最小 `PATH` 下启动器会选到
  `/usr/bin/python3`(3.10) 而拒绝运行；容器侧 `export LOOPX_PYTHON` 覆盖它
  （`loopx_native_codex.py:189-195` 的注释正是这段历史）。
- **按源树取键的构建锁**：`build-wheel.sh` 在源树里 `rm -rf build/`，
  **同一源树并发安装必有一个失败**（实测）。锁只覆盖构建，锁文件在临时目录。

`inspect()` 不再拿源树 revision 比对回读——wheel 安装与源树刻意解耦——改为钉住
"技能与 CLI 出自同一个已安装发行版且版本一致"以及"CLI 解析在 profile 之内"。

**查过但有意不改**：profile 不带 `release.json`。`doctor` 对它报
`release_manifest: unavailable`，但本 fork **官方支持的 wheel 安装报的是同一状态**
（`reason: "release root is not available"`）且 `install_freshness.status` 同为
`python_distribution`——补清单等于让它自称一个连官方路径都没有的身份。这次对抗
检查的价值正在于**拦住了一个错误的"修复"**。

## 验证

- **探针集合差**：修复后 41 条 = 基线 41 条，HEAD-only = 0。
- **文档断言静态核对**：17 条既有缺失，新增 0。
- **首页按守卫自身规则**：正则可解析、757/421 字符（预算 300–1000）、契约串齐全、
  禁串全无。
- **profile 端到端**：脏源放宽装成 / 复用 / 脏源严格拒装 / 非空目录拒装 /
  干净源严格装成；除 `.loopx-python` 外零宿主绝对路径；cwd 诱饵包不能遮蔽；
  最小环境可跑；并发加锁后两个都成功（无锁变体必有一个失败）；profile 内
  `loopx bootstrap` 写出 registry 与 active state、`heartbeat-prompt --thin`
  渲染 1273 字符 Goal body、`doctor` ok=true；两次构建的 wheel **内容一致**
  （1129 成员无一不同，仅 zip 元数据有别）。
- **守卫**：docs-governance、readme-demo-surface、dev-book-publication、
  repository-hygiene、wheel-install、release-artifacts、loopx-update、
  update-notes-quality、catalog-run-e2e、codex-cli-first-run-rehearsal、
  public-boundary、cli-help-manpage 全绿；`mkdocs build --strict` exit 0。
- **pytest 子集**：`test_install_paths` / `test_doctor_install_freshness` /
  `test_self_update_runtime_activation` **45 passed**。

## 自查中发现并修掉的问题

1. `_package_version` 曾**继承宿主环境**，而 `_install_skills` 用干净的 profile
   环境——宿主里若有 `LOOPX_PYTHON`（LoopX 自己的 harness 很容易有）就会拿另一个
   解释器做身份判定，留下"技能装好、校验不过"的半状态。实测
   `LOOPX_PYTHON=/usr/bin/python3`(3.10) 会击穿它；改为与装技能同一环境。
2. **我自己引入的并发缺陷**：改用 `build-wheel.sh` 后同一源树并发安装必有一个失败；
   加锁后两者都成功（A/B 对照）。
3. 一度以为该给 profile 补 `release.json`；对照官方 wheel 路径后确认**不该补**。
4. 验证脚本自身两处判据过时（`venv` 布局、"两个 wheel 哈希相同"），已就地纠正为
   按内容比对——**错误的期望，不是代码问题**。

## 已知遗留（未处理，需单独决策）

1. `codex_loopx_agent.py:308` 的**容器内**安装仍跑
   `bash {_SRC}/scripts/install-local.sh`，`swe-marathon-five-arm/SKILL.md` 还有
   2 处描述它。修它要在任务镜像里做等价安装，**本机无法执行或验证容器**，
   故不写未验证的代码。
2. `loopx-canary` 幽灵 wrapper（`integration.md` 与 `heartbeat-prompt-smoke` 仍钉着）
   ——属 op 037 遗留 #2 的待决晋升产品面。
3. `bundled_runtime.rs:101` 的桌面端捆绑运行时：非 Windows 分支跑
   `scripts/install-local.sh`、Windows 分支跑 `scripts/install-windows.ps1`
   （`deaa365d1` 删），**两个分支的脚本都不存在**；该路径是活的
   （`maintenance.rs:205 → resume_pending → install`），但需 Rust 重写，而
   `cargo check --offline` 解析不了 `command-group`，无法编译验证。
4. 17 条"英文断言 vs 中文文档"的既有缺失（多数是语言错配，个别是内容真的没了，
   如 `--cli-bin loopx-canary`）；重写期望列表属改变验证契约。
5. `codex-cli-bootstrap-message-smoke` 既有红灯：断言 `'heartbeat automation'`，
   该短语在 `2f9a91f89`（早于推送点）从 bootstrap 消息移除，但仍活在 manpage 等
   4 处。**op 037 的既存红灯清单漏列了它**。
6. `scripts/build-wheel.sh` 对直接调用者仍非并发安全（本批只在 profile 安装侧加锁）。

## 提交/推送

- `8a82aa62a` fix: close the coverage gaps operation log 037 left behind
- `d00f061f0` refactor(benchmark): install the isolated profile from the wheel path

已推送至 `origin/260906-dev`（`96e0a5b89..d00f061f0`，含 op 036 的 P5–P7 三个提交）。
