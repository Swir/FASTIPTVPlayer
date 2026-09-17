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


def normalize_http_proxy(value: str) -> str:
    """Validate and normalize a user-supplied HTTP proxy for VLC.

    This deliberately supports only a manually entered host:port. FastIPTV does
    not discover, harvest, scan or test public proxy lists.
    """
    raw = str(value or "").strip()
    if not raw:
        return ""
    candidate = raw if "://" in raw else f"http://{raw}"
    try:
        parsed = urlparse(candidate)
        port = parsed.port
    except ValueError as exc:
        raise VLCError("Invalid proxy address.") from exc
    if parsed.scheme.lower() not in {"http", "https"}:
        raise VLCError("Proxy must use http:// or https://.")
    if not parsed.hostname or port is None or not 1 <= port <= 65535:
        raise VLCError("Proxy must contain a host and port, for example 127.0.0.1:8080.")
    if parsed.username or parsed.password or parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise VLCError("Use a plain host:port proxy without credentials or URL paths.")
    host = parsed.hostname
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    return f"{host}:{port}"


def launch_vlc(stream_url: str, executable: Path, proxy_url: str = "") -> None:
    try:
        scheme = urlparse(stream_url.strip()).scheme.lower()
    except ValueError as exc:
        raise VLCError("Invalid stream URL.") from exc
    if scheme not in ALLOWED_STREAM_SCHEMES:
        raise VLCError(f"Unsupported stream scheme: {scheme or 'none'}")
    if not executable.is_file():
        raise VLCError("Configured VLC executable does not exist.")

    command = [str(executable)]
    proxy = normalize_http_proxy(proxy_url)
    if proxy:
        command.extend(["--http-proxy", proxy])
    command.append(stream_url)
    try:
        subprocess.Popen(
            command,
            shell=False,
            close_fds=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
    except OSError as exc:
        raise VLCError(f"Could not start VLC: {exc}") from exc
