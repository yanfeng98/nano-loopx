# LoopX Desktop

此目录包含 LoopX 个人 Agent 工作区的实验性 Tauri shell。它复用现有的 React dashboard 与 LoopX HTTP 服务;它不引入另一个 Goal、Todo、Gate 或 Chat 状态所有者。

这目前是一个预览版桌面 shell。它不由 LoopX Python 包安装;受支持的浏览器/PWA 启动路径请使用 `loopx dashboard`。当桌面发布工作流成功时,已发布的 LoopX 版本会附带桌面预览产物:

- macOS:`.dmg` 加一个压缩的 `.app` bundle;
- Windows:`.msi` 加一个 NSIS `.exe` 安装器。

桌面 shell 在运行时仍然依赖本地的 `loopx` 命令。先安装或更新 LoopX CLI,再打开桌面应用。

已发布的 macOS 预览产物使用 ad-hoc 代码签名来验证 bundle 完整性,无需 Apple Developer 账户。它们不使用 Developer ID 签名,也未经过公证,因此 macOS 可能需要运营方在"系统设置 > 隐私与安全性"中批准首次启动。

## 运行时模型

该 shell:

1. 立即渲染一个内嵌的启动界面,而不是空白 WebView;
2. 验证或启动 `127.0.0.1:8766` 上的 `loopx serve-status`;
3. 验证或启动 `127.0.0.1:8767` 上的 `loopx chat`;
4. 只有在其轻量 capabilities 端点可读后,才加载带版本号的 LoopX Chat 工作区,并在瞬时服务替换时重试;
5. 在一个原生窗口中打开现有个人工作区;
6. 窗口退出时只终止它自己启动的服务进程组。

两个 LoopX 端口上的任何未知进程都是硬启动错误。现有服务只有在成功响应既暴露出确切的顶层 JSON 指纹、又暴露出与所选 `loopx` 命令相同的已安装发布身份时才会被复用。header 或嵌套值中的类似标记文本不被接受。由旧安装留在运行的服务会被报告为过期,并且只有在 shell 解析出监听器 PID 并确认其命令是匹配端口上预期的 `loopx serve-status` 或 `loopx chat` 调用之后,才会自动替换。如果无法确认进程归属,启动失败关闭,不发送终止信号。未知服务仍然是硬错误。Windows 目前保留这条面向所有者的错误路径,而不是自动终止已有进程。

发布版 launcher 公布一个与其内部 Python 入口模块无关的稳定进程指纹。shell 也识别历史的手动 CLI 与轻量入口 launcher 形态,因此升级 LoopX 可以替换一个已经在运行的旧服务,而不必让运营方手工查找并停止它。

在 macOS 上,当标准的 `com.loopx.status` 或 `com.loopx.chat` LaunchAgent 已加载时,Desktop 保持 launchd 为唯一服务所有者。替换过期监听器后,它请求一次 launchd 唤醒,并等待节流间隔,而不是让第二个 Desktop 自有进程争抢同一个端口。

WebView 固定到已安装 LoopX 版本服务的回环 Chat origin。对 status 与 Chat 服务的 dashboard 请求仍限制在回环 CORS 与既有的 preview/apply 权威边界内。

## 与 `loopx dashboard` 共存

桌面 shell 与 `loopx dashboard` 共享 `8766` 与 `8767` 上的同一组回环服务,两个入口都复用已运行的匹配 LoopX 服务:

- 先启动 `loopx dashboard`,再打开桌面 shell:shell 继续使用正在运行的 status 与 Chat 服务,只打开原生窗口。
- 先启动桌面 shell,再运行 `loopx dashboard`:该命令检测到匹配的 LoopX Chat 服务,打印其 URL,并打开浏览器/PWA 路径,而不启动第二个服务器。

两种顺序都可以。关闭桌面窗口只停止它自己启动的服务进程组;由 `loopx dashboard` 启动的 Chat 服务会持续运行,直到该命令被停止。

## 前置条件

- 已安装 LoopX 且 `loopx` 可用;设置 `LOOPX_BIN` 可覆盖它。
- dashboard 构建需要 Node.js 20.19+ 或 22.12+。
- Rust stable 以及平台特定的 Tauri 构建依赖。

Linux 需要 WebKitGTK 4.1 与 GTK 3 开发包。参见 [Tauri 前置条件](https://v2.tauri.app/start/prerequisites/)。

## 开发

```bash
cd apps/desktop/loopx-control-plane
npm install
npm run dev
```

## 验证

```bash
cd apps/desktop/loopx-control-plane/src-tauri
cargo fmt --check
cargo test
cargo clippy --all-targets -- -D warnings

cd ..
./scripts/dashboard.sh build
npm run build
```

`npm run build` 在 `src-tauri/target/release/bundle/` 下生成配置的平台包。发布工作流在 macOS 上构建 macOS `.dmg` 与 `.app.zip` 产物,在 Windows 上构建 `.msi` 与 `.exe` 产物,并上传到触发该工作流的 GitHub Release。上传前它验证 ad-hoc macOS 应用签名与磁盘镜像完整性。单独的 `DESKTOP-SHA256SUMS` manifest 覆盖工作流附带的全部桌面产物,发布构建使用 Git tag 作为桌面 bundle 版本。对已有 tag 的手动重跑是一次显式的完整桌面重发布:它重建 macOS 与 Windows 两套资产,把上一套桌面产物保留为短期工作流产物,验证完整的新四文件集,替换全部桌面二进制,并最后上传新的校验和 manifest。因此手动重跑后二进制哈希可能变化。

## 禁用或移除

关闭桌面窗口以停止由 shell 拥有的服务进程。shell 打开之前已经在运行的服务保持原样。移除桌面包不会改动 LoopX 项目或运行时状态。
