from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
from urllib.parse import urlparse

from .playlist import ALLOWED_STREAM_SCHEMES


class VLCError(RuntimeError):
    """Raised when VLC cannot be located or launched."""


def discover_vlc(configured: str = "") -> Path | None:
    candidates: list[Path] = []
    if configured:
        candidates.append(Path(configured).expanduser())
    located = shutil.which("vlc")
    if located:
        candidates.append(Path(located))
    if os.name == "nt":
        for variable in ("PROGRAMFILES", "PROGRAMFILES(X86)"):
            root = os.environ.get(variable)
            if root:
                candidates.append(Path(root) / "VideoLAN" / "VLC" / "vlc.exe")
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    return None


def launch_vlc(stream_url: str, executable: Path) -> None:
    try:
        scheme = urlparse(stream_url.strip()).scheme.lower()
    except ValueError as exc:
        raise VLCError("Invalid stream URL.") from exc
    if scheme not in ALLOWED_STREAM_SCHEMES:
        raise VLCError(f"Unsupported stream scheme: {scheme or 'none'}")
    if not executable.is_file():
        raise VLCError("Configured VLC executable does not exist.")
    try:
        subprocess.Popen(
            [str(executable), stream_url],
            shell=False,
            close_fds=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
    except OSError as exc:
        raise VLCError(f"Could not start VLC: {exc}") from exc
