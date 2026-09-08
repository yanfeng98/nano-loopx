"""安装一份隔离的 LoopX profile，供运行模式共用。

benchmark/deepswe/README.md 的 treatment 要求三项独立的产品路径证据：

  1. 该 profile 渲染出的 Goal body；
  2. LoopX 技能装进 app-server 实际使用的那个 CODEX_HOME；
  3. body 里点名的那个 release-snapshot CLI 确实存在。

只做第 1 项是不够的——实测过：body 里写着让模型用 `loopx-project` /
`loopx-self-repair` 技能、跑 `loopx ...` 命令，但技能没装、PATH 上的 `loopx` 还是
另一个安装，于是模型拿到一份自己无法执行的指令，跑满预算、工作区零改动、
且不报错。三项必须一起给。

这里直接调用 LoopX 自带的 `scripts/install-local.sh` 一次办齐后两项（body 由
session.py 用参数化 profile 渲染），并对技能安装回读与 release-snapshot CLI 做
校验。宿主专用 profile 校验（doctor 的 agent-type 匹配、host_surface 收据）已随
其宿主一起退役，不再属于安装契约。
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from loopx.skill_install_readback import (
    PACKAGED_HOST_SKILL_IDS,
    SKILL_INSTALL_READBACK_FILENAME,
    inspect_skill_install_readback,
)

REQUIRED_SKILL_IDS = ("loopx", *PACKAGED_HOST_SKILL_IDS)
_DEFAULT_RELEASE_ID = "native-goal-profile"
_SAFE_RELEASE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
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
    release_root: Path
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


def _profile_paths(profile_root: Path, release_id: str) -> dict[str, Path]:
    root = profile_root.expanduser().resolve()
    return {
        "root": root,
        "home": root / "home",
        "codex_home": root / "codex-home",
        "skills_dir": root / "codex-home" / "skills",
        "bin_dir": root / "bin",
        "cli_bin": root / "bin" / "loopx",
        "release_root": root / "releases" / release_id,
        "man_root": root / "man",
        "shell_profile": root / "home" / ".profile",
    }


def _install_environment(
    *, paths: dict[str, Path], python_executable: str, release_id: str,
    base_env: dict[str, str] | None,
) -> dict[str, str]:
    """照抄 install-local.sh 的环境契约，少一项可能装成 canary。"""

    source = os.environ if base_env is None else base_env
    env = {key: str(source[key]) for key in _INSTALL_ENV_PASSTHROUGH
           if source.get(key)}
    env.setdefault("PATH", os.defpath)
    env.update(
        {
            "HOME": str(paths["home"]),
            "SHELL": "/bin/sh",
            "CODEX_HOME": str(paths["codex_home"]),
            "LOOPX_PYTHON": python_executable,
            "LOOPX_PROMOTE_DEFAULT": "1",
            "LOOPX_INSTALL_CANARY": "0",
            "LOOPX_BIN_DIR": str(paths["bin_dir"]),
            "LOOPX_RELEASES_DIR": str(paths["release_root"].parent),
            "LOOPX_RELEASE_ID": release_id,
            "LOOPX_MAN_ROOT": str(paths["man_root"]),
            "LOOPX_MAN_DIR": str(paths["man_root"] / "man1"),
            "LOOPX_SHELL_PROFILE": str(paths["shell_profile"]),
            "LOOPX_SKILLS_DIR": str(paths["skills_dir"]),
            # 固定安装器已物化生成的 `$loopx` 入口 skill。额外的 slash-command
            # surface 对非交互 Goal worker 无关，还会在 readback 写完之后改动
            # 那棵树。
            "LOOPX_INSTALL_SLASH_COMMANDS": "0",
            "LOOPX_INSTALL_OPENCODE": "0",
            "LOOPX_INSTALL_CLAUDE": "0",
            "LOOPX_SKILL_DEDUPE_OTHER_ROOT": "0",
        }
    )
    return env


def _resolved_python(value: str | None) -> str:
    requested = value or sys.executable
    resolved = (Path(requested).resolve(strict=True) if os.path.isabs(requested)
                else Path(requested))
    return str(resolved)


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
        top_level = subprocess.run(
            ["git", "-C", str(source_root), "rev-parse", "--show-toplevel"],
            check=False, capture_output=True, text=True,
        )
    except OSError:
        top_level = None
    if top_level is not None and top_level.returncode == 0:
        try:
            repository_root = Path(top_level.stdout.strip()).resolve(strict=True)
        except OSError:
            return None
        if repository_root != source_root:
            return None
        status = subprocess.run(
            ["git", "-C", str(source_root), "status", "--porcelain"],
            check=False, capture_output=True, text=True,
        )
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
    installer = source / "scripts" / "install-local.sh"
    if not installer.is_file():
        raise ProfileError("formal_installer_missing")
    release_id = _DEFAULT_RELEASE_ID
    if not _SAFE_RELEASE_ID.fullmatch(release_id):
        raise ValueError("release_id must be a safe directory name")
    target = Path(profile_root).expanduser()
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        raise ProfileError("profile_root_not_empty")
    if require_clean_source:
        clean = _source_is_clean(source)
        if clean is False:
            raise ProfileError("profile_source_not_clean")
        if clean is None:
            raise ProfileError("profile_source_cleanliness_unproven")
    target.mkdir(parents=True, exist_ok=True)
    paths = _profile_paths(target, release_id)
    paths["home"].mkdir(parents=True, exist_ok=True)
    env = _install_environment(
        paths=paths,
        python_executable=_resolved_python(python_executable),
        release_id=release_id,
        base_env=None,
    )
    completed = subprocess.run(
        [str(installer)],
        cwd=source,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode:
        raise ProfileError(
            "formal_installer_failed:"
            f"returncode={completed.returncode}:stderr_sha256="
            f"{hashlib.sha256(completed.stderr.encode('utf-8')).hexdigest()[:16]}"
        )
    return inspect(target, source_root=source,
                   require_clean_source=require_clean_source)


def inspect(target: str | Path, *, source_root: str | Path | None = None,
            require_clean_source: bool = False) -> InstalledProfile:
    """校验一份已装的 profile（存在时复用，不重复安装）。"""

    paths = _profile_paths(Path(target), _DEFAULT_RELEASE_ID)
    release_root = paths["release_root"]
    cli_bin = paths["cli_bin"]
    if not release_root.is_dir() or not cli_bin.exists():
        raise ProfileError("formal_install_outputs_missing")
    try:
        resolved_cli = cli_bin.resolve(strict=True)
        resolved_release = release_root.resolve(strict=True)
    except OSError as exc:
        raise ProfileError("formal_install_outputs_unreadable") from exc
    if resolved_release not in resolved_cli.parents:
        raise ProfileError("profile_cli_not_release_snapshot")

    expected_source = Path(source_root).expanduser().resolve() if source_root else None
    readback = inspect_skill_install_readback(
        skills_dir=paths["skills_dir"],
        required_skill_ids=REQUIRED_SKILL_IDS,
        source_root=expected_source,
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
    source_revision = readback.get("source_revision")
    if not isinstance(skills_digest, str) or not isinstance(source_revision, str):
        raise ProfileError("profile_identity_missing")
    skill_source = manifest.get("source") if isinstance(manifest, dict) else {}
    if not isinstance(skill_source, dict):
        skill_source = {}
    source_clean = _manifest_source_is_clean(skill_source)
    if require_clean_source and not source_clean:
        raise ProfileError("profile_source_not_clean")

    return InstalledProfile(
        root=paths["root"],
        home=paths["home"],
        codex_home=paths["codex_home"],
        bin_dir=paths["bin_dir"],
        cli_bin=cli_bin,
        release_root=release_root,
        source_revision=source_revision,
        source_clean=source_clean,
        skills_digest=skills_digest,
        required_skill_ids=REQUIRED_SKILL_IDS,
        materialized_skill_ids=tuple(readback.get("materialized_skill_ids") or ()),
    )
