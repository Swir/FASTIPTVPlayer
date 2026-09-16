from pathlib import Path

from fastiptv.vlc import discover_vlc


def test_discover_vlc_prefers_configured_existing_file(tmp_path) -> None:
    fake = tmp_path / "vlc.exe"
    fake.write_text("fake", encoding="utf-8")
    assert discover_vlc(str(fake)) == Path(fake).resolve()
