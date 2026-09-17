from pathlib import Path

import pytest

from fastiptv.vlc import VLCError, discover_vlc, launch_vlc, normalize_http_proxy


def test_discover_vlc_prefers_configured_existing_file(tmp_path) -> None:
    fake = tmp_path / "vlc.exe"
    fake.write_text("fake", encoding="utf-8")
    assert discover_vlc(str(fake)) == Path(fake).resolve()


def test_normalize_manual_proxy() -> None:
    assert normalize_http_proxy("127.0.0.1:8080") == "127.0.0.1:8080"
    assert normalize_http_proxy("http://proxy.internal:3128") == "proxy.internal:3128"
    assert normalize_http_proxy("") == ""


def test_proxy_rejects_credentials_and_missing_port() -> None:
    with pytest.raises(VLCError):
        normalize_http_proxy("http://user:pass@proxy.test:8080")
    with pytest.raises(VLCError):
        normalize_http_proxy("proxy.test")


def test_launch_vlc_passes_manual_proxy_without_shell(tmp_path, monkeypatch) -> None:
    fake = tmp_path / "vlc.exe"
    fake.write_text("fake", encoding="utf-8")
    captured = {}

    class DummyProcess:
        pass

    def fake_popen(command, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        return DummyProcess()

    monkeypatch.setattr("fastiptv.vlc.subprocess.Popen", fake_popen)
    launch_vlc("https://example.test/live.m3u8", fake, "proxy.internal:3128")

    assert captured["command"] == [
        str(fake),
        "--http-proxy",
        "proxy.internal:3128",
        "https://example.test/live.m3u8",
    ]
    assert captured["kwargs"]["shell"] is False
