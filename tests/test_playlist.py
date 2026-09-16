from fastiptv.playlist import PlaylistError, parse_m3u


def test_parse_playlist_groups_metadata_and_deduplication() -> None:
    text = '''#EXTM3U
#EXTINF:-1 tvg-id="news.pl" tvg-logo="https://example.test/logo.png" group-title="News",News HD
https://example.test/live/news.m3u8
#EXTINF:-1 group-title="Music",Radio One
http://example.test/radio
#EXTINF:-1 group-title="News",News HD
https://example.test/live/news.m3u8
'''
    channels = parse_m3u(text)
    assert len(channels) == 2
    assert channels[0].name == "News HD"
    assert channels[0].group == "News"
    assert channels[0].tvg_id == "news.pl"


def test_reject_playlist_without_supported_streams() -> None:
    try:
        parse_m3u("#EXTM3U\n#EXTINF:-1,Local\nfile:///tmp/video.ts")
    except PlaylistError as exc:
        assert "No supported" in str(exc)
    else:
        raise AssertionError("Expected PlaylistError")
