# 可靠 SSH 反向出口代理


远程 agent runtime 可能拥有健康的 SSH 控制通道,却缺少通往其模型 API 的可靠
出站路由。这是两条彼此独立的数据路径。通过 SSH 启动远程 runtime 的桌面应用,
并不必然把桌面的 HTTPS 连通性转发给该 runtime。

本指南提供一个公开安全参考:在桌面侧运行仅限 loopback 的 HTTPS CONNECT 代理,
并通过 SSH 反向转发把它暴露给一个远程 runtime。它只转发网络流量,不复制凭证、
会话数据库、发布文件或 runtime 状态。

实现是带参数的
[`examples/ssh_reverse_proxy_supervisor.py`](../../examples/ssh_reverse_proxy_supervisor.py)
脚本。它是可选的集成示例,不是 LoopX 控制面能力,也不是宿主应用原生 SSH 连接
的替代品。

## 数据路径与所有权

```text
remote agent process
  -> remote 127.0.0.1:<remote-port>
  -> managed SSH reverse-forward channel
  -> desktop 127.0.0.1:<local-port>
  -> loopback HTTPS CONNECT proxy
  -> public model endpoint:443
```

桌面拥有本地代理以及创建反向转发的 SSH 客户端。远程侧只接收一个 loopback
监听器。把两个监听器都保持在 `127.0.0.1` 上,可以防止其他机器使用该代理。

为该 bridge 使用专用端口。不要复用原生控制通道端口、项目状态端口或共享代理
端口。

## 值得保留的故障模式

### 过时的远程监听器并不一定是定时器

当路由、VPN 或网络接口突然变化时,桌面 SSH 客户端可能先于远程 `sshd` 子进程
察觉而消失。该子进程可能暂时保留反向转发监听器。带有 `KeepAlive` 或等价重启
策略的进程管理器随后会启动新的 SSH 客户端,由于旧监听器仍占用端口,新客户端会
以 `remote port forwarding failed` 失败。

重启策略造成的是重复尝试,而不是过时监听器。诊断该循环时,把远程 `sshd` 子进程
与本地监督进程视为两个不同的生命周期所有者。

### 带外 SSH 健康探测可能放大故障

周期检查打开第二个 SSH 连接时,可能在慢速握手期间超时,即便受管隧道仍然可用。
如果该检查杀掉隧道,一次瞬时路由变慢就变成了确定的重启循环。

优先使用受管 SSH 进程的 `ServerAliveInterval` 与 `ServerAliveCountMax`。只有在该
进程退出后才运行远程检查。这使故障检测器始终处于它自己管理的那条连接上。

### 全局范围的 IPv6 仍可能不可达

DNS 可能先返回 IPv6 再返回 IPv4,而活动路由没有可用的 IPv6 出站。顺序连接器
可能把调用者的整个超时都浪费在第一个 IPv6 地址上。该示例过滤非公开目标、优先
IPv4,并把 IPv6 保留为兜底。

## 运行监督进程

为远程 runtime 配置一个普通 SSH alias,然后运行:

```bash
python3 examples/ssh_reverse_proxy_supervisor.py \
  --ssh-host example-runtime \
  --local-port 18080 \
  --remote-port 18080
```

本地代理在其受管 SSH 子进程重连期间保持存活。该 SSH 命令使用 batch 模式、禁用
连接共享、启用 server-alive 检查,并要求反向转发成功绑定。

在远程 runtime 上,把 HTTPS 客户端指向远程 loopback 监听器:

```bash
export HTTPS_PROXY=http://127.0.0.1:18080
```

把凭证保留在远程 runtime 现有的凭证源中。代理配置应只包含 loopback URL。

## 可选的过时监听器清理

自动清理刻意采用 opt-in:

```bash
python3 examples/ssh_reverse_proxy_supervisor.py \
  --ssh-host example-runtime \
  --local-port 18080 \
  --remote-port 18080 \
  --cleanup-stale-listener
```

清理只在受管隧道退出后运行。除非以下所有条件成立,否则它拒绝终止进程:

- 该进程监听的正是所配置的远程 loopback 端口;
- 该进程属于当前远程用户;
- 其可执行文件名为 `sshd` 或 `sshd-session`。

远程账户必须能够检查该监听器。如果 `lsof` 需要特权,只允许对该专用 loopback
端口进行非交互式检查。不要授予宽泛的进程管理规则。终止同用户 `sshd` 子进程
不应需要提权。

如果清理被关闭或拒绝,本地代理保持运行,监督进程继续重试。操作员可以先检查
确切监听器,再决定是否移除它。

## 端到端验证

先在不依赖 SSH 的情况下验证本地代理:

```bash
curl --proxy http://127.0.0.1:18080 \
  --noproxy '' \
  --connect-timeout 10 \
  https://example.com/ \
  --output /dev/null \
  --write-out 'status=%{http_code} total=%{time_total}\n'
```

然后在远程 runtime 上验证反向转发路径。合成健康主机由该示例在本地应答,
不使用公开 DNS:

```bash
curl --proxy http://127.0.0.1:18080 \
  --noproxy '' \
  --max-time 15 \
  --output /dev/null \
  --write-out 'status=%{http_code} total=%{time_total}\n' \
  http://reverse-proxy-health.invalid/
```

预期状态是 `204`。最后,请求预期的公开 HTTPS 端点。任何真实 HTTP 响应,包括
认证或方法错误,都证明 DNS 解析、反向转发、CONNECT、TLS 与 HTTP 已经到达服务。
健康端点成功而 HTTPS 请求失败,说明问题被缩小到桌面 DNS 或公开出站,而不是反向
转发。

## 受控恢复测试

在依赖进程管理器之前,只终止监督进程的受管 SSH 子进程。不要终止宿主应用的原生
SSH 控制进程。预期结果是:

1. 监督进程保持存活;
2. 旧 SSH 子进程退出;
3. 仅在启用清理时,确切过时监听器才被清理;
4. 出现新的 SSH 子进程;
5. 远程健康端点再次返回 `204`。

使用 `launchd`、`systemd` 或其他进程管理器时,要验证其重启计数器在该测试期间
不增加。监督进程稳定而子进程被替换,证明重连所有权在监督进程内部,而不是被委托
给崩溃循环。

## 安全边界

该示例刻意采用狭窄政策:

- 本地与远程监听器只绑定 IPv4 loopback;
- 只接受发往端口 `443` 的 HTTPS `CONNECT` 请求;
- 解析出的目标必须是全球可路由地址;
- 代理认证数据既不被接受也不记录;
- SSH 主机、端口、重试政策与清理行为都是显式 CLI 配置;
- 日志包含生命周期事件与错误类别,不包含请求头或响应体。

分享诊断时,不要公开真实 SSH alias、主机名、私有地址、本地绝对路径、进程列表、
路由表、凭证或事件日志。保留生命周期模式与验证方法,而不是原始环境。

## 仓库验证

该 smoke 是离线的:它模拟地址解析,只打开一个临时 loopback 服务器,绝不联系
SSH 主机或公开端点。

```bash
python3 examples/ssh-reverse-proxy-supervisor-smoke.py
python3 -m py_compile examples/ssh_reverse_proxy_supervisor.py
```
