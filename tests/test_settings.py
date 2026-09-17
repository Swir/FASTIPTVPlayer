import json

from fastiptv.settings import AppSettings, load_settings, save_settings


def test_settings_round_trip(tmp_path) -> None:
    path = tmp_path / "settings.json"
    original = AppSettings(
        vlc_path="C:/VLC/vlc.exe",
        favorites=["abc"],
        recent_playlists=["list.m3u"],
        epg_url="https://example.test/epg.xml",
        epg_sources=["https://example.test/epg.xml", "https://example.test/epg2.xml.gz"],
    )
    save_settings(original, path)
    loaded = load_settings(path)
    assert loaded == original


def test_settings_deduplicate_lists() -> None:
    settings = AppSettings.from_dict(
        {
            "favorites": ["a", "a", "b"],
            "recent_playlists": ["x", "x"],
            "epg_url": "https://one.test/epg.xml",
            "epg_sources": ["https://one.test/epg.xml", "https://one.test/epg.xml", "https://two.test/epg.xml"],
        }
    )
    assert settings.favorites == ["a", "b"]
    assert settings.recent_playlists == ["x"]
    assert settings.epg_sources == ["https://one.test/epg.xml", "https://two.test/epg.xml"]


def test_legacy_config_migrates_only_safe_preferences(tmp_path) -> None:
    target = tmp_path / "modern" / "settings.json"
    legacy = tmp_path / "config.json"
    legacy.write_text(
        json.dumps(
            {
                "vlc_path": "C:/Program Files/VideoLAN/VLC/vlc.exe",
                "epg_sources": ["https://one.test/epg.xml", "https://two.test/epg.xml.gz"],
                "enabled_proxy_sources": ["legacy-proxy-source"],
                "available_proxy_sources": {"legacy-proxy-source": "https://proxy.test/list"},
            }
        ),
        encoding="utf-8",
    )

    loaded = load_settings(target, legacy)

    assert loaded.vlc_path.endswith("vlc.exe")
    assert loaded.epg_url == "https://one.test/epg.xml"
    assert loaded.epg_sources == ["https://one.test/epg.xml", "https://two.test/epg.xml.gz"]
    persisted = json.loads(target.read_text(encoding="utf-8"))
    assert "enabled_proxy_sources" not in persisted
    assert "available_proxy_sources" not in persisted


def test_invalid_legacy_config_does_not_break_startup(tmp_path) -> None:
    target = tmp_path / "settings.json"
    legacy = tmp_path / "config.json"
    legacy.write_text("not-json", encoding="utf-8")
    assert load_settings(target, legacy) == AppSettings()
