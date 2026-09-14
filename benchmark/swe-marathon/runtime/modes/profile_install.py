"""安装一份隔离的 LoopX profile，供运行模式共用。

benchmark/deepswe/README.md 的 treatment 要求三项独立的产品路径证据：

  1. 该 profile 渲染出的 Goal body；
  2. LoopX 技能装进 app-server 实际使用的那个 CODEX_HOME；
  3. body 里点名的那个 `loopx` CLI 确实存在。

只做第 1 项是不够的——实测过：body 里写着让模型用 `loopx-project` /
`loopx-self-repair` 技能、跑 `loopx ...` 命令，但技能没装、PATH 上的 `loopx` 还是
另一个安装，于是模型拿到一份自己无法执行的指令，跑满预算、工作区零改动、
且不报错。三项必须一起给。

本 fork 只有两条安装路径（就地 editable checkout 与本地构建的 wheel，见
docs/product/release-readiness.md）。隔离 profile 要的是一份与源工作树解耦、
可复现的安装，所以这里走 wheel：从 source_root 离线构建 wheel，用
`pip install --target` 把发行版铺进 profile，再由 profile 自己的 CLI 把技能
物化进 profile 的 CODEX_HOME。

刻意不用 venv：profile 是**在宿主机构建、随后被搬进容器**的
（见 runtime/turn/loopx_native_codex.py），而 venv 里带着构建解释器的绝对路径、
且 `bin/python` 是指向宿主解释器的符号链接。这里落进 profile 的是纯 Python
发行版 + 仓库自带的 `scripts/loopx` 启动器；需要一个 3.11+ 的 python3，构建用的
解释器记在 profile 的 `.loopx-python` 里（与已退役安装器同一机制），容器侧在运行
前 export `LOOPX_PYTHON` 覆盖它。发布快照安装器
`scripts/install-local.sh` 与它物化出的 release-snapshot 目录布局已在 op 036
退役，不再是安装契约的一部分。宿主专用 profile 校验（doctor 的 agent-type
匹配、host_surface 收据）已随其宿主一起退役，同样不在安装契约内。
"""

from __future__ import annotations

import contextlib
import fcntl
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from loopx.skill_install_readback import (
    PACKAGED_HOST_SKILL_IDS,
    SKILL_INSTALL_READBACK_FILENAME,
    inspect_skill_install_readback,
)

REQUIRED_SKILL_IDS = ("loopx", *PACKAGED_HOST_SKILL_IDS)
_INSTALL_ENV_PASSTHROUGH = (
    "LANG",
    "LC_ALL",
    "LC_CTYPE",
    "PATH",
    "SSL_CERT_DIR",
    "SSL_CERT_FILE",
    "TERM",
    "TZ",
)


class ProfileError(RuntimeError):
    """隔离 profile 没装成。"""


@dataclass(frozen=True)
class InstalledProfile:
    """装好的 profile + 它的公开身份摘要。"""

    root: Path
    home: Path
    codex_home: Path
    bin_dir: Path
    cli_bin: Path
    launcher: Path
    source_revision: str
    source_clean: bool
    skills_digest: str
    required_skill_ids: tuple[str, ...]
    materialized_skill_ids: tuple[str, ...]

    def env(self, *, base: dict[str, str] | None = None) -> dict[str, str]:
        """app-server 该用的环境。

        把 HOME/CODEX_HOME/PATH 指到 profile 里，并且是 credential-free 的：
        模型凭证只通过 provider 网关的 URL 和一个固定的非密 env 哨兵进去，
        不把宿主机的密钥暴露给 danger-full-access 的 agent。
        """

        source = os.environ if base is None else base
        env = {key: str(source[key]) for key in _INSTALL_ENV_PASSTHROUGH
               if source.get(key)}
        inherited_path = env.get("PATH", os.defpath)
        env.update(
            {
                "HOME": str(self.home),
                "CODEX_HOME": str(self.codex_home),
                "PATH": f"{self.bin_dir}{os.pathsep}{inherited_path}",
            }
        )
        return env

    def receipt(self) -> dict[str, Any]:
        """写进产物的公开身份，只有摘要和 id，不含本地路径。"""

        return {
            "source_revision": self.source_revision,
            "source_clean": self.source_clean,
            "skills_digest": self.skills_digest,
            "required_skill_ids": list(self.required_skill_ids),
            "materialized_skill_ids": list(self.materialized_skill_ids),
        }


def _profile_paths(profile_root: Path) -> dict[str, Path]:
    """profile 布局。

    发行版直接铺在 profile 根上，因为仓库自带的 `scripts/loopx` 启动器按
    `<release_root>/loopx/entrypoint.py` 找入口——这样 profile 根就是它认的
    release root，不需要另写一份启动器。
    """

    root = profile_root.expanduser().resolve()
    return {
        "root": root,
        "home": root / "home",
        "codex_home": root / "codex-home",
        "skills_dir": root / "codex-home" / "skills",
        "bin_dir": root / "bin",
        "cli_bin": root / "bin" / "loopx",
        "launcher": root / "scripts" / "loopx",
        "dist_dir": root / "dist",
    }


def _resolved_python(value: str | None) -> str:
    requested = value or sys.executable
    resolved = (Path(requested).resolve(strict=True) if os.path.isabs(requested)
                else Path(requested))
    return str(resolved)


def _profile_env(paths: dict[str, Path]) -> dict[str, str]:
    """跑 profile 自己的 CLI 时要用的环境：HOME/CODEX_HOME/PATH 都落在 profile 里。"""

    env = {key: str(os.environ[key]) for key in _INSTALL_ENV_PASSTHROUGH
           if os.environ.get(key)}
    inherited_path = env.get("PATH", os.defpath)
    env.update(
        {
            "HOME": str(paths["home"]),
            "CODEX_HOME": str(paths["codex_home"]),
            "PATH": f"{paths['bin_dir']}{os.pathsep}{inherited_path}",
        }
    )
    return env


def _run(command: list[str], *, cwd: Path | None = None,
         env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command, cwd=str(cwd) if cwd else None, env=env,
        check=False, capture_output=True, text=True,
    )


def _failure(prefix: str, completed: subprocess.CompletedProcess[str]) -> ProfileError:
    """失败只留可复现的摘要，不把原始 stderr 泄漏进产物。"""

    return ProfileError(
        f"{prefix}:returncode={completed.returncode}:stderr_sha256="
        f"{hashlib.sha256(completed.stderr.encode('utf-8')).hexdigest()[:16]}"
    )


def _manifest_source_is_clean(source: dict[str, Any]) -> bool:
    if source.get("git_dirty") is False:
        return True
    return bool(
        source.get("git_dirty") is None
        and (
            source.get("revision_kind") == "archive_sha256"
            or (source.get("kind") == "github_archive" and source.get("archive_sha256"))
        )
    )


def _source_is_clean(source_root: Path) -> bool | None:
    """source 是否干净：git 仓库看 porcelain；否则看 release.json 血缘。"""

    try:
        top_level = _run(["git", "-C", str(source_root), "rev-parse", "--show-toplevel"])
    except OSError:
        top_level = None
    if top_level is not None and top_level.returncode == 0:
        try:
            repository_root = Path(top_level.stdout.strip()).resolve(strict=True)
        except OSError:
            return None
        if repository_root != source_root:
            return None
        status = _run(["git", "-C", str(source_root), "status", "--porcelain"])
        if status.returncode != 0:
            return None
        return not bool(status.stdout.strip())
    try:
        manifest = json.loads((source_root / "release.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    release_source = (
        manifest.get("source")
        if isinstance(manifest, dict) and isinstance(manifest.get("source"), dict)
        else {}
    )
    return True if _manifest_source_is_clean(release_source) else None


@contextlib.contextmanager
def _source_build_lock(source: Path):
    """按源树取键的跨进程构建锁。

    `scripts/build-wheel.sh` 会在源树里 `rm -rf build/` 再构建，所以同一源树
    上并发构建会互相踩——实测两个并发里必有一个失败。锁只覆盖构建本身，
    不覆盖整个安装；锁文件放在临时目录，不进源树。
    """

    digest = hashlib.sha256(str(source).encode("utf-8")).hexdigest()[:16]
    lock_path = Path(tempfile.gettempdir()) / f"loopx-wheel-build-{digest}.lock"
    with lock_path.open("w", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _build_wheel(source: Path, *, dist_dir: Path, python_executable: str) -> Path:
    """离线构建 wheel。构建产物只落在 profile 的 dist 目录里。"""

    builder = source / "scripts" / "build-wheel.sh"
    if not builder.is_file():
        raise ProfileError("profile_wheel_builder_missing")
    dist_dir.mkdir(parents=True, exist_ok=True)
    with _source_build_lock(source):
        completed = _run(
            ["bash", str(builder), "--out-dir", str(dist_dir)],
            cwd=source,
            env={**os.environ, "PYTHON": python_executable},
        )
    if completed.returncode:
        raise _failure("profile_wheel_build_failed", completed)
    wheels = sorted(dist_dir.glob("loopx-*.whl"))
    if len(wheels) != 1:
        raise ProfileError(f"profile_wheel_artifact_unexpected:count={len(wheels)}")
    return wheels[0]


def _install_wheel(source: Path, paths: dict[str, Path], wheel: Path, *,
                   python_executable: str) -> None:
    """把 wheel 铺进 profile，并接上仓库自带的启动器。"""

    installed = _run(
        [
            python_executable, "-m", "pip", "install",
            "--no-index", "--no-deps", "--no-warn-script-location",
            "--target", str(paths["root"]), str(wheel),
        ]
    )
    if installed.returncode:
        raise _failure("profile_pip_install_failed", installed)
    if not (paths["root"] / "loopx" / "entrypoint.py").is_file():
        raise ProfileError("profile_package_missing")
    # 记下构建用的解释器：PATH 上的 python3 可能低于 3.11（本机 /usr/bin/python3
    # 就是 3.10），而启动器会先读 LOOPX_PYTHON、再读这个文件、最后才回落 python3。
    # 容器臂在运行前显式 export LOOPX_PYTHON，所以这条记录在那里会被覆盖。
    (paths["root"] / ".loopx-python").write_text(
        f"{python_executable}\n", encoding="utf-8"
    )

    # 仓库自带的启动器负责过滤 sys.path 上的 cwd、校验 Python 版本并设置
    # LOOPX_RELEASE_ROOT；profile 根就是它认的 release root。pip 在 --target
    # 下自己生成的 console script 不能要：它的 shebang 指向构建时的解释器路径。
    source_launcher = source / "scripts" / "loopx"
    if not source_launcher.is_file():
        raise ProfileError("profile_launcher_missing")
    paths["launcher"].parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_launcher, paths["launcher"])
    paths["launcher"].chmod(0o755)

    # pip 在 --target 下把 console script 写进 bin/，每个都带构建解释器的绝对
    # shebang；搬进容器后全会失效，而且 bin/ 还要上 PATH，所以整目录重建。
    shutil.rmtree(paths["bin_dir"], ignore_errors=True)
    paths["bin_dir"].mkdir(parents=True, exist_ok=True)
    paths["cli_bin"].symlink_to(paths["launcher"])


def _package_version(paths: dict[str, Path]) -> str:
    """profile 里那个 CLI 自报的版本。

    走 CLI 本身而不是 `python -c "import loopx"`：从源码 checkout 启动的控制
    进程会把 cwd 放进 sys.path，直接 import 可能命中源工作树而不是 profile，
    身份判定就成了自证。启动器会先把这类路径滤掉。

    用 profile 环境而不是继承宿主环境：宿主里若恰好有 `LOOPX_PYTHON` 或
    `PYTHONPATH`（LoopX 自己的 harness 很容易有），就会拿另一个解释器/另一份
    包去做身份判定，而装技能那步用的是干净的 profile 环境——两边不一致会留下
    "技能装好了、校验却不过"的半状态。
    """

    completed = _run([str(paths["cli_bin"]), "--version"], cwd=paths["root"],
                     env=_profile_env(paths))
    printed = completed.stdout.strip()
    if completed.returncode or not printed:
        raise _failure("profile_cli_version_unreadable", completed)
    return printed.rsplit(" ", 1)[-1]


def _install_skills(paths: dict[str, Path]) -> None:
    """用 profile 自己的 CLI 把 workflow skills 物化进 profile 的 CODEX_HOME。"""

    completed = _run(
        [
            str(paths["cli_bin"]), "workflow-skills", "--install",
            "--skills-dir", str(paths["skills_dir"]),
        ],
        cwd=paths["root"],
        env=_profile_env(paths),
    )
    if completed.returncode:
        raise _failure("profile_skill_install_failed", completed)


def install(source_root: str | Path, profile_root: str | Path, *,
            python_executable: str | None = None,
            require_clean_source: bool = False) -> InstalledProfile:
    """装一份隔离 profile 并校验安装回读。

    profile_root 必须不存在或为空——刻意不修复半装的 profile，因为混着两个
    安装版本会让整个 treatment 失效。所以每次跑用一个新目录。

    require_clean_source 默认放宽：本地 loopx 是带改动的工作副本时，严格模式
    会直接拒装。跑正式对照时应当传 True。
    """

    source = Path(source_root).expanduser().resolve(strict=True)
    target = Path(profile_root).expanduser()
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        raise ProfileError("profile_root_not_empty")
    # 先在源工作树上判干净，再开始构建：构建会在源树里落 build/ 与 egg-info
    # （二者都已 gitignore）。
    if require_clean_source:
        clean = _source_is_clean(source)
        if clean is False:
            raise ProfileError("profile_source_not_clean")
        if clean is None:
            raise ProfileError("profile_source_cleanliness_unproven")
    target.mkdir(parents=True, exist_ok=True)
    paths = _profile_paths(target)
    paths["home"].mkdir(parents=True, exist_ok=True)
    interpreter = _resolved_python(python_executable)
    wheel = _build_wheel(source, dist_dir=paths["dist_dir"],
                         python_executable=interpreter)
    _install_wheel(source, paths, wheel, python_executable=interpreter)
    _install_skills(paths)
    return inspect(target, source_root=source,
                   require_clean_source=require_clean_source)


def inspect(target: str | Path, *, source_root: str | Path | None = None,
            require_clean_source: bool = False) -> InstalledProfile:
    """校验一份已装的 profile（存在时复用，不重复安装）。"""

    paths = _profile_paths(Path(target))
    launcher = paths["launcher"]
    cli_bin = paths["cli_bin"]
    if not launcher.is_file() or not cli_bin.exists():
        raise ProfileError("profile_install_outputs_missing")
    try:
        resolved_cli = cli_bin.resolve(strict=True)
        resolved_root = paths["root"].resolve(strict=True)
    except OSError as exc:
        raise ProfileError("profile_install_outputs_unreadable") from exc
    if resolved_root not in resolved_cli.parents:
        raise ProfileError("profile_cli_outside_profile")

    # wheel 安装与源工作树是刻意解耦的，所以这里不拿源树 revision 去比对；
    # 改为核对技能与 CLI 出自同一个已安装发行版。
    readback = inspect_skill_install_readback(
        skills_dir=paths["skills_dir"],
        required_skill_ids=REQUIRED_SKILL_IDS,
        source_root=None,
    )
    if readback.get("ready") is not True:
        status = re.sub(r"[^A-Za-z0-9_.:-]", "_", str(readback.get("status")))
        raise ProfileError(f"profile_skill_readback_not_ready:{status}")

    manifest_path = paths["skills_dir"] / SKILL_INSTALL_READBACK_FILENAME
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProfileError("profile_skill_manifest_unreadable") from exc
    skills = manifest.get("skills") if isinstance(manifest, dict) else None
    skills_digest = skills.get("digest") if isinstance(skills, dict) else None
    skill_source = manifest.get("source") if isinstance(manifest, dict) else {}
    if not isinstance(skill_source, dict):
        skill_source = {}
    source_revision = skill_source.get("revision")
    if not isinstance(skills_digest, str) or not isinstance(source_revision, str):
        raise ProfileError("profile_identity_missing")
    source_kind = skill_source.get("kind")
    if source_kind != "python_distribution":
        # 就地 editable 装出来的 profile 会绑死源工作树，失去隔离语义。
        raise ProfileError(f"profile_install_not_isolated:{source_kind}")
    if source_revision != _package_version(paths):
        raise ProfileError("profile_skill_readback_not_ready:source_revision_mismatch")
    source_clean = _manifest_source_is_clean(skill_source)
    if require_clean_source:
        if source_root is None:
            raise ProfileError("profile_source_cleanliness_unproven")
        if _source_is_clean(Path(source_root).expanduser().resolve()) is not True:
            raise ProfileError("profile_source_not_clean")

    return InstalledProfile(
        root=paths["root"],
        home=paths["home"],
        codex_home=paths["codex_home"],
        bin_dir=paths["bin_dir"],
        cli_bin=cli_bin,
        launcher=launcher,
        source_revision=source_revision,
        source_clean=source_clean,
        skills_digest=skills_digest,
        required_skill_ids=REQUIRED_SKILL_IDS,
        materialized_skill_ids=tuple(readback.get("materialized_skill_ids") or ()),
    )
