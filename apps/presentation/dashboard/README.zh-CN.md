# LoopX Dashboard

这是 LoopX 的第一个产品 dashboard shell。它用 React/Vite 控制面 UI 渲染状态数据契约。

## 当前状态

dashboard 是实验性的运营预览,不是 LoopX 的主要工作流。CLI、状态 JSON、运行历史与活动 goal 文件仍然是日常工作的真相来源。在它获得专门的产品迭代之前,请把 dashboard 用于 public-safe 演示、本地检查与聚焦的 UI 实验。

## 全新 Clone 的公开预览

首次 dashboard 预览不需要任何私有 LoopX 状态。应用把 `examples/status.example.json` 打包为 public-safe 示例来源,因此一个全新检出可以在启动任何本地状态服务器之前验证并打开 UI:

```bash
cd apps/presentation/dashboard
npm ci
npm run smoke:demo-readiness -- --skip-browser
npm run dev:web
```

然后打开 `http://127.0.0.1:5173/`。公开演示使用打包的示例来源,或者只在本地启动 `loopx serve-status` 后切换到回环状态 URL。不要提交 `status.local.json` 或实时状态导出;它们可能包含本地 registry/运行时路径与私有项目摘要。

`npm run dev:web` 只启动带打包示例的 Vite UI。`npm run dev` 还会启动回环状态与 Chat 服务,因此需要 Python 3.11+ 解释器;见下方开发一节。

公开 Frontstage 位于 `/frontstage`。它只渲染 public-safe 展示目录与打包的展示 fixtures。旧的密集式 `goal_channel_projection_v0` 面板已隔离为弃用的诊断组件面;Personal Workspace 才是实时运营工作流的产品路径。产品交互基线见
`docs/product/surfaces/frontstage-dashboard-interaction-baseline.md`:showcase 模式是公开的案例驱动首页组件面,而 `mode=ops` 是密集、只读的遗留诊断工作区。其规范路由现在是
`/deprecated/frontstage/ops`;旧的 `mode=ops` URL 会重定向到那里。Personal Workspace(`/`)拥有 Goal 工作流、输出与里程碑报告。

公开首屏在不读取状态 JSON 的情况下讲解控制面模型:其信号条带概括了人工判断、异步 agent 团队、公开案例与实时数据边界。弃用诊断路由保留旧 `Role Map`、投影 todo 通道、搜索与通道过滤器,只是为了开发者在迁移期间能复现一个既有状态切片。
`Efficiency Evidence` 面板从展示目录抽取 public-safe 的自我迭代案例,使托管的 frontstage 可以展示 commit 支撑的基线、实际窗口、压缩与证据边界信号,而不暴露原始会话。`Async Work Loop` 与 `Showcase Cases` 面板把同一目录渲染为动画叙事通道与紧凑案例卡,并链接回公开 GitHub 案例页面以便深入阅读。遗留诊断通道来自只读投影;Showcase 面板只来自 public-safe 展示元数据。两个组件面都没有浏览器写入权威。

默认的 frontstage 路由是公开 showcase 模式。它忽略 `statusUrl`,只渲染打包的 showcase/演示素材,因此被复制或托管的 URL 不会意外投影本地 registry 状态。
`examples/fixtures/frontstage-private-status-trap.public.json` 是该边界的合成负面 fixture:浏览器 smoke 证明它的 `GH_FAKE_*` 实时状态标记不会出现在 showcase URL 中,只会在显式加载弃用诊断界面时出现。

贡献者上手请使用 `/frontstage?mode=developer`。这仍然是一个 public-safe 的只读视图:它展示 agent 优先的起始路径、quota/状态健康检查、同行工作区防护、todo 认领、本地服务器检查与写回边界,而不加载实时 registry 数据。它旨在帮助新开发者在打开更密集的 ops 面板之前,理解如何从 Codex CLI 或其他 agent TUI 进入 LoopX。

开发者扩展驾驶舱位于 `/frontstage/developer`。它是一个只读贡献者工作台,用于状态契约探索、投影对比、fixture 生成规则、smoke 运行清单与组件示例,使新的投影工作不必逆向工程大型 dashboard 页面。它只使用静态公开契约与 fixtures;实时状态 feed、registry 文件与浏览器写入 API 都留在这个路由之外。

要保持对遗留本地控制面的实时检查,请显式进入弃用路由:`/deprecated/frontstage/ops?statusUrl=http://127.0.0.1:8766/status.json`。该路由随后读取 `attention_queue.items[].goal_channel_projection` 并保持只读;如果 feed 缺失或没有投影,打包的演示 fixture 仍然可见。Ops 模式的状态源限于相对或回环 URL,因此公开 frontstage 链接不会静默拉取外部/私有 feed。ops feed 通过 TanStack Query 支撑的本地数据层加载,带 schema 版本新鲜度检查、过期 daemon 修复副本与 `local_dashboard_api` capability 投影。它默认为只读:reward 或控制面写入功能需要显式回环选择加入、公布的 capability URL 与 preview 锁定的本地 API。不要把 ops 模式 URL 当作公开链接。其实现隔离在
`src/views/deprecated/` 下;`src/views/frontstage-page.tsx` 仍然是 Showcase-only。

要为演示、Lark 分享或未来的 GitHub Pages 托管创建 public-safe 静态 bundle,用净化后的 fixture 导出 frontstage:

```bash
cd apps/presentation/dashboard
npm run export:frontstage-share
```

默认输出为 `/tmp/loopx-frontstage-share-bundle`。它包含编译后的 dashboard、`status.frontstage-share.json`、一个直接的 `/frontstage/` 静态路由、一个 manifest,以及一个带本地 serve URL 的 README。导出器在报告成功之前会拒绝本地路径、私有 registry 状态、内部文档主机、原始密钥泄漏、令牌赋值与私钥材料。share-bundle smoke 还会扫描生成的文件中合成的 `GH_FAKE_*` 陷阱标记,以确保公开导出不会意外携带实时状态载荷。之后若要托管到仓库 Pages,用 `-- --base /loopx/ --out-dir <artifact-dir>` 重新运行同一个导出器,并且只发布那个生成的站点产物。

## 运行

在安装 LoopX 后,从任意目录:

```bash
loopx dashboard
```

这一条命令从同一个进程提供打包的 Personal Workspace、状态投影与 Agent Chat。默认会打开浏览器。无头启动请运行 `loopx dashboard --no-open` 并打开命令打印的 URL;默认是 `http://127.0.0.1:8767/chat/`。安装使用不需要单独的 `loopx serve-status` 进程,也不需要在后端安装 npm 依赖。

可以从同一个进程回读打包的 UI 与状态投影:

```bash
curl -fsS http://127.0.0.1:8767/chat/ >/dev/null
curl -fsS http://127.0.0.1:8767/status.json
```

如果默认端口上已有一个 LoopX Chat 服务在运行(例如由 Tauri 桌面 shell 启动),`loopx dashboard` 通过其确切 capability 指纹检测到并复用,而不是失败:它打印正在运行的 URL 并打开浏览器/PWA 路径,然后退出,不启动第二个服务器。桌面 shell 以相反顺序复用同一组服务,因此浏览器/PWA 与原生入口可以按任意顺序启动。

源码检出的开发是另一种模式:

```bash
npm ci
npm run build
npm run dev
```

`npm run dev` 与回环状态及 Chat 服务一起启动 Vite UI,端口为 `5173`、`8766` 与 `8767`。当那些 LoopX 服务已经单独运行时,请使用 `npm run dev:web`。Vite 把默认的 `/status.json` 请求代理到端口 `8766`,因此 SSH 用户只需转发端口 `5173` 即可访问常规开发页面。

全栈启动器需要 Python 3.11+ 解释器来运行状态与 Chat 服务。它优先采用 `LOOPX_PYTHON`,然后是 LoopX 安装在 `.loopx-python` 中记录的 Python,再依次是仓库 `.venv`、`PATH` 上的 `python3.13`/`python3.12`/`python3.11` 以及常见 Homebrew 位置。如果你的默认 `python3` 太旧,把它指向一个现有解释器:

```bash
LOOPX_PYTHON=/path/to/python3.12 npm run dev
```

根 dashboard 与打包的 `/chat/` 路由都暴露同样的可安装 PWA manifest 与图标。默认 `loopx dashboard` 命令打开 `/chat/`;因此其 manifest 把已安装应用限定在 `/chat/`。这是一个可安装的独立组件面,不是离线缓存 service worker。

实时 `/status.json` 路由把仓库范围的公开边界扫描移出首屏请求。其契约投影把该扫描报告为已推迟;在发布或推送公开组件面之前运行 `loopx check` 以执行完整的边界审计。

默认屏幕是 Personal Workspace——LoopX 面向运营方的唯一前端。它为管理长程 agent Goals 提供统一、连贯的体验:

- **LoopX Manager 概览(`/`)**:
  在原始下钻之前回答运营方优先级的跨 Goal 分诊:
  - 4 通道概览流(`需要你` / `执行中` / `观察中` / `已安排`);
  - 突出控制面与 registry 状态的 System Health 诊断;
  - 支持全局问题、Goal 创建草稿与进度摘要的统一会话托盘。

- **Goal 工作区(`/?goalId=<id>`)**:
  单个 Goal 的专用工作区:
  - **Chat**:Goal 范围的 Agent 通信、流式 Turn 与动作预览;
  - **任务**:4 列 kanban 看板(`待确认`, `待执行 / 进行中`, `定时与持续`, `已完成`),支持快速状态更新与把 Agent 回复一键转换为任务草稿;
  - **文件**:仓库产物浏览器与文件检查;
  - **Context 抽屉**:Goal 诊断、仓库绑定、Lark Topic 连接与会话健康。

- **动作安全与控制面**:
  对 Goals、Todos、Heartbeats、监视器或设置的持久修改遵循类型化 preview → 受治理 apply → 已验证 receipt 协议。展现方式随风险与可逆性而变化:受保护或不可逆动作保持 review 优先,而下方可逆的 Goal pause 直接应用就绪的 preview,并把过期或新被关卡约束的结果升级回 review。浏览器从不执行对控制面真相的未调解直接写入。
  Goal 目录的主列表只保留活动 Goals。使用 Goal 旁边的暂停动作一键应用可逆停止;持久反馈报告结果,停止的 Goal 在折叠的 **Stopped Goals** 区域保留其 Todos、历史与证据,并且可以从同一区域恢复。停止 Goal 会暂停自动 Agent Turn;它不把 Goal 标记为完成,也不删除状态。停止的 Goal 离开活动attention 范畴,投影零有效 quota,从而让调度器停止宿主自动化(如 Codex App heartbeat),同时保留配置的 quota。
  Goal stop 与 `quota.compute=0` 共享这条关闭路径,但保留不同的恢复权威:只有 Goal 生命周期恢复可以重新激活一个停止的 Goal,而显式的正向 quota 更新会恢复一个 quota 暂停。Stop 不强制杀死进行中的工具调用;下一个 `quota should-run` 包会告诉宿主在另一个自动 Turn 之前暂停或删除周期性的 heartbeat。等价的 CLI 流程是:

  ```bash
  loopx goal-lifecycle --goal-id <goal-id> --operation stop
  loopx goal-lifecycle --goal-id <goal-id> --operation stop --execute
  loopx goal-lifecycle --goal-id <goal-id> --operation resume --execute
  loopx quota status --goal-id <goal-id>
  ```

  第一条命令是零写入的 preview。执行过的命令会写入权威来源 registry、刷新共享 registry 投影并验证两个回读。Resume 恢复调度资格;quota、Gates 与 Todos 仍然决定工作是否可以运行。

- **公开 Frontstage(`/frontstage`)**:
  公开 `/frontstage` 继续作为无需认证、只读的 showcase 与 public-safe 展示组件面。真实的本地运营工作流专属 Personal Workspace。

## 加载实时状态

作为规范的多项目首页,启动一个全局状态服务器。这是所有接入共享 registry 的项目的正常运营视图:

```bash
loopx serve-status --global-registry --port 8766 --limit 80
```

在 macOS 上,用用户级 LaunchAgent 辅助脚本让状态 feed 与 Chat 服务在登录后保持运行:

```bash
../../scripts/macos-dashboard-launchagent.sh install
```

该辅助脚本启动:

```text
http://127.0.0.1:8766/status.json
http://127.0.0.1:8767/chat/
```

本地服务操作使用 `../../scripts/macos-dashboard-launchagent.sh restart|stop|uninstall|status`。`status` 还会探测
`http://127.0.0.1:8766/status.json` 并打印
`status_contract.schema_version`;如果缺失或低于预期 dashboard 版本,请在演示前运行 `restart`,以免实时 feed 由较旧的 daemon 服务。日志位于 `~/Library/Logs/loopx/`。
状态输出路径由 `python3 examples/macos-dashboard-launchagent-status-smoke.py` 覆盖,无需触碰真实 macOS 服务。

然后打开打包的个人工作区:

```text
http://127.0.0.1:8767/chat/
```

### 命名本地与 SSH 隧道来源

Personal Workspace 的来源切换器维护一个浏览器本地目录,包含一个内置 **Local** 来源与任意数量的命名 SSH 隧道来源。在每个远程主机上启动状态服务器,然后把每个主机转发到不同的本地端口:

```bash
# 在远程主机上
loopx serve-status --global-registry --host 127.0.0.1 --port 8766

# 在运营方机器上;为每个来源选择不同的本地端口
ssh -N -L 8876:127.0.0.1:8766 <remote-host>
```

添加来源面板通过当前回环 Dashboard origin,只从运营方机器的 OpenSSH 配置读取显式、shell 安全的 `Host` 别名。打包的 `loopx dashboard` 从其 Chat 运行时提供该端点,因此自定义 Dashboard 端口无需固定发现端口;开发模式把同一路径代理到本地 Chat 服务。选择别名、选一个本地端口、复制并运行生成的隧道命令,然后添加来源。通配符主机、否定模式、`IdentityFile`、`ProxyCommand`、主机名、凭据与配置路径绝不会投影到浏览器。手动回环 URL 路径对自定义转发设置仍然可用。

浏览器目录只存储所选别名标签与回环 URL;LoopX 不存储 SSH 凭据,也不打开隧道。活动来源报告其连接健康。Local 保持可交互,而每个自定义 SSH 隧道来源即使其转发 URL 是回环,也显式只读。

切换器有意没有合成的 **All** 来源。独立状态 feed 尚未共享权威、身份与去重语义,因此合并它们会暗示控制面尚未建立的主机间协调。

对于项目本地调试或一次性 `loopx demo`,从你想检查的项目启动本地状态服务器:

```bash
loopx serve-status --port 8765
```

`--global-registry` 是有意的显式行为:即使你在项目检出内部启动它,它也把多项目首页保持在共享 registry 上,而普通 `serve-status` 仍适用于项目本地调试。

保持 dashboard 应用运行,使用 `?view=ops`、`Live` 来源按钮,或从来源控件加载这个项目本地 URL:

```text
http://127.0.0.1:8765/status.json
```

状态服务器默认绑定到 `127.0.0.1`,并为 Vite dashboard 发送带本地 CORS 头的 no-store JSON。

它还提供 `POST /reward/dry-run`,用于验证选中的 goal/run 与 public-safe 奖励文本。要允许直接本地 dashboard 提交,用显式写标志启动服务器:

```bash
loopx serve-status --port 8765 --enable-reward-write-api
```

该写标志仅限回环。没有它,dashboard 可以验证奖励草稿,但不能追加反馈。

## 加载静态状态

使用本地静态导出:

```bash
python3 -m loopx.cli --format json status > apps/presentation/dashboard/public/status.local.json
cd apps/presentation/dashboard
npm run dev
```

然后从 dashboard 来源控件加载 `/status.local.json`。

`status.local.json` 有意被 git-ignore,因为实时状态导出可能包含本地 registry/运行时路径与私有项目摘要。只把它作为本地检查文件。公开演示请使用净化的 `examples/status.example.json` fixture,而不是提交实时导出。

你也可以直接在浏览器导入 JSON 文件,或加载一个返回相同 `loopx --format json status` 形态的本地 API URL。

## 实时单页会话面板

观察会话任务进度的主要方式是一个回环单页面板:

```bash
loopx dash                 # 在 http://127.0.0.1:8767/ 服务(每 10 秒自动刷新)
loopx dash --goal-id <goal-id>   # 把面板收窄到单个 goal
```

在任意浏览器打开打印出的 URL,并在 agents 工作时保持打开。该页面是一个面向人类的机群视图:会话、goals、active / needs-you / blocked / done 桶、开放 todos 与运行统计的概览条带,后面是每个会话一张卡,包含其拥有的 goals 以及每个 goal 的状态徽章、todo 进度条、等待原因与最近一次运行。它每 10 秒通过重新拉取 `/panel` 片段在原地刷新。内部控制机制(decision frames、work-lane 契约、quota slot 计算、来源警告)有意不渲染。面板只读:没有写控件,没有浏览器写入权威。服务器只绑定回环,不暴露任何写路由。

一次性静态快照也可用于演示或分享:

```bash
loopx dash generate [--goal-id <goal-id>] --out dash.html
```

在任意浏览器打开 `dash.html`。该命令在报告成功之前运行 public/private 边界扫描,失败时不输出。

```bash
# 改为以 JSON 打印投影 + html
loopx --format json dash generate --goal-id <goal-id>
```

布局、数据边界与验证契约见 [session dash panel 设计](../../../docs/product/surfaces/session-dash-panel-design.md)。

## 浏览器 Smokes

Dashboard 浏览器 smoke 是显式的,因为它们会启动临时 Vite 服务器。演示就绪请运行分组的 public-safe smoke:

```bash
npm run smoke:demo-readiness
```

该命令运行 LaunchAgent 状态输出 smoke、结构化的 `promotion-gate` 新鲜/警告契约 smoke、来源契约 smokes,以及当前 Home 与 Personal Workspace 浏览器 smokes。决策新鲜度与晋升就绪读模型仍由聚焦的控制面 smokes 覆盖,而不是用浏览器测试替代已退役的旧版 Ops 视图。在没有 Playwright/Chrome 的 CI 环境中,使用:

```bash
python3 ../../../examples/dashboard-demo-readiness-smoke.py --skip-browser
```

当你想调试单个组件面时,各个浏览器 smoke 仍然可用:

```bash
npm run smoke:home-browser
npm run smoke:personal-workspace
npm run smoke:frontstage-share-bundle
node examples/dashboard-throttled-browser-smoke.mjs
node examples/dashboard-operator-gate-browser-smoke.mjs
```

home 浏览器 smoke 保护规范控制面首页。它使用一个 public-safe 的四项目 fixture,不带 `view=share` 打开根路由,检查中文运营文案中的用户 todos、agent 优先级、showcase 活动、quota 守卫状态、每项目 top-4 todo 状态与状态写回,并在首屏拒绝原始机器令牌如 `single_surface`、`focus_wait` 或原始内部 slot 约束。它还在
`output/playwright/dashboard-home-visual-acceptance/` 下捕获桌面与移动首屏/decision-frame 截图,并在水平溢出时失败,以便在广泛宣称前端可用之前让密度回退可见。它使用已安装的 Playwright 包,或在可用时使用 Codex 捆绑的运行时,并通过本地 `vite` 包启动 Vite,而不依赖 `PATH` 上的 `npm` / `npx`。

ops 决策新鲜度 smoke 用两个公开 fixtures 保护详细的 `?view=ops` 面板:一个类实时的零条目摘要与一个过期/需要 rebase 的 decision 示例。它验证渲染的中英文运营文案、计数、受影响最大的 goal 与精确重放措辞,而不是只依赖源码字符串检查。

晋升就绪 smoke 用新鲜、过期与缺失的 readiness fixtures 保护详细的 `?view=ops` 面板。它验证 canary 晋升就绪的状态徽章、readiness/rerun 决策、产物窗口、时长、原因与真相来源文案。规范 fixture/浏览器脚本是
`examples/dashboard-promotion-readiness-browser-smoke.mjs`;请使用上面的 npm 脚本,而不是调用临时的重复文件名。
分组 demo-readiness 路径还会在浏览器检查之前运行 `examples/promotion-gate-smoke.py`,因此即使跳过浏览器 smokes,结构化的 `gate_state`、`can_promote` 与 `should_warn` 契约也被覆盖。

节流 smoke 保护"安静调度状态"首屏。运营关卡 smoke 保护计划的高复杂度 goals:它们应显示为控制器/用户动作,而不是 Codex 可处理的工作。那些较旧的浏览器 smokes 仍使用本地 Playwright CLI 包装器。
