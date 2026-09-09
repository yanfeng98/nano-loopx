"""Codex × LoopX 运行模式的声明式定义。

模式取自 LoopX README 的 Codex host 表。差别不是"接法不同"，而是 LoopX 渲染出
的 body、闸门命令、结算来源不同——这里把差别集中成数据，驱动逻辑（session.py /
codex_host.py）对它们一视同仁。

实测 profile 在同一个 goal 上渲染出的差别（loopx 0.5.3）：

    codex_cli   body 2698 字符  guard 不带 turn 标识    spend --source visible-goal

codex_cli 是 visible-Goal 渲染器（body 开头"in this visible Codex `/goal`"），
Codex 自己拥有续跑。
"""

from __future__ import annotations

from dataclasses import dataclass


class ModeError(RuntimeError):
    """模式定义或使用方式不成立。"""


@dataclass(frozen=True)
class Mode:
    """一种运行模式。"""

    name: str
    """命令行上的短名。"""

    runtime_profile: str
    """传给 loopx 的 --runtime-profile。"""

    host_surface: str
    scheduler_owner: str
    execution_mode: str
    """profile 展开后的三元组，仅用于自检与记录，不重复传给 CLI。"""

    continuation_owner: str
    """'codex' = Codex 自己续跑（visible Goal）；'driver' = 本驱动按节拍再唤醒。"""

    needs_turn_instance: bool = False
    """是否每 tick 需要一个 LOOPX_TURN turn-instance-id。"""

    spend_source: str = "visible-goal"

    notes: str = ""
    """这个模式在无人值守环境下的真实边界，写进产物收据里。"""

    substitution: str = ""
    """若本适配器用了替代传输/替代 host_surface，在这里写清楚。空 = 无替代。"""


#: `Codex CLI` —— 可见 `/goal`。文档（docs/product/runtimes/codex-cli/
#: codex-cli-tui-loop.md 的 "Headless Disabled Boundary"）明确：这条路默认不提供
#: headless 回退，连 opt-in 都没有；`codex-cli-exec-handoff` 已从"输出可运行脚本"
#: 改成"报告禁用边界"。真正的 TUI 注入（Session-Attached Automation）在上游是
#: 一串 dry-run 诊断，没有任何代码真的往活 TUI 里写。
#:
#: 所以本适配器对这个模式做的是**传输替代**：body 仍由 `--runtime-profile codex_cli`
#: 渲染（渲染器、闸门命令、结算来源都是真的），但承载它的是 app-server 的 Goal
#: 事务而不是人值守的 TUI。这样模式语义可测，且不假装有人在场。
CODEX_CLI = Mode(
    name="codex-cli",
    runtime_profile="codex_cli",
    host_surface="codex_cli",
    scheduler_owner="agent_cli_loop",
    execution_mode="interactive",
    continuation_owner="codex",
    spend_source="visible-goal",
    notes=(
        "上游把有人值守的 TUI 当作本模式的定义特征，headless 回退被显式禁用。"
        "无人值守跑分时 body/闸门/结算是真的，承载传输是替代的。"
    ),
    substitution=(
        "transport: 用 codex app-server 的 Goal 事务承载 codex_cli 渲染的 visible "
        "body，替代人值守 TUI 里的 `/goal` 粘贴。渲染 profile 未被替换。"
    ),
)

#: 心跳 —— 自建定时器驱动（generic_cli）。
#:
#: 上游为自建定时器指定的对口是 `--runtime-profile generic_cli`：shell_worker
#: 参考实现 `scripts/external_scheduler_worker.py` 默认就是它，其 help 明写
#: "Quota runtime profile that emits the local_scheduler hint"。
#:
#: 不要直接传 -H local_scheduler：`--turn-instance-id` 只接受 generic_cli
#: （否则报 "requires runtime-profile generic_cli so quota guard creates a
#: heartbeat receipt"），而没有 turn instance 就拿不到心跳收据。
HEARTBEAT = Mode(
    name="heartbeat",
    runtime_profile="generic_cli",
    host_surface="generic_cli",
    scheduler_owner="agent_cli_loop",
    execution_mode="interactive",
    continuation_owner="driver",
    needs_turn_instance=True,
    spend_source="heartbeat",
    notes=(
        "自建定时器拥有唤醒，对应上游 shell_worker 连接器。闸门发 local_scheduler "
        "提示（初始间隔 + 递进阶梯 + 未变轮询上限），驱动照 external_scheduler_"
        "worker.py 的做法推进阶梯。"
    ),
    substitution=(
        "host_surface: generic_cli —— 这是上游为自建定时器指定的对口 profile。"
    ),
)


MODES: dict[str, Mode] = {m.name: m for m in (CODEX_CLI, HEARTBEAT)}


def resolve(name: str) -> Mode:
    """按短名取模式。"""

    try:
        return MODES[name]
    except KeyError:
        raise ModeError(
            f"未知模式 {name!r}；可用：{', '.join(sorted(MODES))}"
        ) from None


def profile_args(mode: Mode) -> list[str]:
    """渲染成 loopx CLI 的 profile 参数。

    有具名 profile 就用 --runtime-profile（上游 round-trip 测试保证它与三元组
    等价）；没有的（local_scheduler）就显式传 -H/-O/-M。
    """

    if mode.runtime_profile:
        return ["--runtime-profile", mode.runtime_profile]
    return [
        "-H", mode.host_surface,
        "-O", mode.scheduler_owner,
        "-M", mode.execution_mode,
    ]
