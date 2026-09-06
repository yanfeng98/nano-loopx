# 文件锁获取 v0
> [English](file-lock-acquisition-v0.md)

LoopX 使用同级内核锁文件来串行化本地读-改-写操作：POSIX 使用 `flock`，Windows 使用 `msvcrt` 字节区间锁。决定所有权的是内核锁，而不是文件是否存在。操作员与自动化流程绝不能通过删除锁文件来恢复等待者。

## 获取策略

| 策略 | 截止时间 | 超时行为 |
| --- | ---: | --- |
| `mutation` | 5 秒 | 停止命令，并在手动重试前要求检查持有者。 |
| `monitor` | 1 秒 | 停止轮询；不要紧密循环。仅在后续计划的轮询并进行检查后重试。 |
| `single_flight` | 不等待 | 返回普通重复/空操作结果，不记录 incident。 |

`exclusive_file_lock` 使用 `LOCK_EX | LOCK_NB`、单调截止时间，以及各次尝试之间受限的睡眠。超过截止时间将抛出 `LockAcquireTimeoutError`，且 `error_code=lock_acquire_timeout`。此前无界的 `LOCK_EX` 等待不属于本契约。

## 持有者与 Incident 记录

获取后，持有者将公开安全的 JSON 写入 POSIX 的 `*.lock` 文件，或原子覆盖 Windows 的 `*.lock.holder.json` sidecar：

- 稳定的哈希 `lock_id`（绝不使用目标绝对路径）；
- PID、agent id、操作、策略与获取时间；
- 正常退出后的释放时间。

Windows 元数据单独存放，因为字节区间锁会阻止另一个文件句柄读取被锁字节。POSIX 保留现有单文件契约，其中 advisory 元数据与 `flock` 共享 `*.lock`。两种情况下，内核锁（而非元数据文件是否存在）都是权威。

超时会向同级 `*.lock.incidents.jsonl` 通道追加一行 `file_lock_incident_v0`。该追加直接使用 `O_APPEND`，不获取被阻塞的锁。行内包含持有者与等待者身份、等待时长、策略与 `operator_action`。追加 incident 失败不会隐藏或延迟类型化超时。

## 操作员恢复

1. 检查记录中的持有者 PID、agent、操作与获取时间。
2. 确认进程仍存在且确实停住。
3. 仅在该确认之后，且在操作员现有权限范围内终止进程。
4. 进程退出后按策略重试。不要删除锁文件；后续持有者会覆盖持有者 sidecar。

PID 缺失或元数据过期是待调查的证据，不是删除锁文件的许可。内核会在其进程或文件描述符退出时释放 `flock` 或 `msvcrt` 所有权。
