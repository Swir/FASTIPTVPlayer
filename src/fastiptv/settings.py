from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from platformdirs import user_config_dir


@dataclass(slots=True)
class AppSettings:
    vlc_path: str = ""
    favorites: list[str] = field(default_factory=list)
    recent_playlists: list[str] = field(default_factory=list)
    epg_url: str = ""
    epg_sources: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Any) -> "AppSettings":
        if not isinstance(data, dict):
            return cls()
        favorites = _clean_strings(data.get("favorites"), limit=5000)
        recent = _clean_strings(data.get("recent_playlists"), limit=10)
        epg_url = str(data.get("epg_url", "")).strip()
        epg_sources = _clean_strings(data.get("epg_sources"), limit=25)
        if epg_url and epg_url not in epg_sources:
            epg_sources.insert(0, epg_url)
        return cls(
            vlc_path=str(data.get("vlc_path", "")).strip(),
            favorites=favorites,
            recent_playlists=recent,
            epg_url=epg_url,
            epg_sources=epg_sources,
        )


def _clean_strings(value: Any, limit: int) -> list[str]:
    result: list[str] = []
    if not isinstance(value, list):
        return result
    for item in value:
        text = str(item).strip()
        if text and text not in result:
            result.append(text)
        if len(result) >= limit:
            break
    return result


def settings_path() -> Path:
    return Path(user_config_dir("FastIPTVPlayer", "Swir")) / "settings.json"


def _load_legacy_config(path: Path) -> AppSettings | None:
    """Import only safe user preferences from the classic terminal config.

    Legacy proxy-source settings are intentionally ignored. We only preserve the VLC
    path and EPG source list, because those are ordinary local playback/guide settings.
    """
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(raw, dict):
        return None
    vlc_path = str(raw.get("vlc_path", "")).strip()
    epg_sources = _clean_strings(raw.get("epg_sources"), limit=25)
    if not vlc_path and not epg_sources:
        return None
    return AppSettings(
        vlc_path=vlc_path,
        epg_url=epg_sources[0] if epg_sources else "",
        epg_sources=epg_sources,
    )


def load_settings(path: Path | None = None, legacy_path: Path | None = None) -> AppSettings:
    target = path or settings_path()
    try:
        return AppSettings.from_dict(json.loads(target.read_text(encoding="utf-8")))
    except json.JSONDecodeError:
        return AppSettings()
    except OSError:
        pass

    legacy = legacy_path or (Path.cwd() / "config.json")
    migrated = _load_legacy_config(legacy)
    if migrated is not None:
        try:
            save_settings(migrated, target)
        except OSError:
            pass
        return migrated
    return AppSettings()


def save_settings(settings: AppSettings, path: Path | None = None) -> Path:
    target = path or settings_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(asdict(settings), indent=2, ensure_ascii=False), encoding="utf-8")
    temporary.replace(target)
    return target
