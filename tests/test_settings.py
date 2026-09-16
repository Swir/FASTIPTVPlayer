from fastiptv.settings import AppSettings, load_settings, save_settings


def test_settings_round_trip(tmp_path) -> None:
    path = tmp_path / "settings.json"
    original = AppSettings(vlc_path="C:/VLC/vlc.exe", favorites=["abc"], recent_playlists=["list.m3u"], epg_url="https://example.test/epg.xml")
    save_settings(original, path)
    loaded = load_settings(path)
    assert loaded == original


def test_settings_deduplicate_lists() -> None:
    settings = AppSettings.from_dict({"favorites": ["a", "a", "b"], "recent_playlists": ["x", "x"]})
    assert settings.favorites == ["a", "b"]
    assert settings.recent_playlists == ["x"]
