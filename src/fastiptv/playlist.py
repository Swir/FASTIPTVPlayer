from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

from .models import Channel

ATTR_RE = re.compile(r'([\w-]+)="([^"]*)"')
ALLOWED_STREAM_SCHEMES = {"http", "https", "rtsp", "rtmp", "udp"}
MAX_PLAYLIST_BYTES = 20 * 1024 * 1024
MAX_CHANNELS = 20_000


class PlaylistError(ValueError):
    """Raised when a playlist is invalid or exceeds safety limits."""


def _valid_stream_url(value: str) -> bool:
    try:
        return urlparse(value.strip()).scheme.lower() in ALLOWED_STREAM_SCHEMES
    except ValueError:
        return False


def parse_m3u(text: str, max_channels: int = MAX_CHANNELS) -> list[Channel]:
    if not isinstance(text, str):
        raise PlaylistError("Playlist content must be text.")
    channels: list[Channel] = []
    seen: set[tuple[str, str]] = set()
    pending: tuple[str, dict[str, str]] | None = None

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#EXTINF:"):
            attrs = {key.lower(): value.strip() for key, value in ATTR_RE.findall(line)}
            name = line.split(",", 1)[1].strip() if "," in line else attrs.get("tvg-name", "Unnamed channel")
            pending = (name or "Unnamed channel", attrs)
            continue
        if line.startswith("#"):
            continue
        if pending is None:
            continue

        name, attrs = pending
        pending = None
        if not _valid_stream_url(line):
            continue
        identity = (name.casefold(), line)
        if identity in seen:
            continue
        seen.add(identity)
        channels.append(
            Channel(
                name=name,
                url=line,
                group=attrs.get("group-title") or "Other",
                tvg_id=attrs.get("tvg-id", ""),
                logo=attrs.get("tvg-logo", ""),
            )
        )
        if len(channels) > max_channels:
            raise PlaylistError(f"Playlist contains more than the supported {max_channels:,} channels.")

    if not channels:
        raise PlaylistError("No supported stream entries were found in the playlist.")
    return channels


def load_playlist_file(path: Path) -> list[Channel]:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise PlaylistError(f"Cannot access playlist: {exc}") from exc
    if size > MAX_PLAYLIST_BYTES:
        raise PlaylistError("Playlist file exceeds the 20 MB safety limit.")
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise PlaylistError(f"Cannot read playlist: {exc}") from exc
    text = payload.decode("utf-8-sig", errors="replace")
    return parse_m3u(text)
