from datetime import datetime, timezone

from fastiptv.epg import normalize_channel_name, parse_xmltv
from fastiptv.models import Channel


def test_normalization_removes_quality_suffixes() -> None:
    assert normalize_channel_name("TVP 1 HD") == normalize_channel_name("TVP-1")


def test_xmltv_current_and_next_resolution() -> None:
    payload = b'''<?xml version="1.0" encoding="UTF-8"?>
<tv>
  <channel id="tvp1"><display-name>TVP 1 HD</display-name></channel>
  <programme start="20260916200000 +0000" stop="20260916210000 +0000" channel="tvp1"><title>Current show</title></programme>
  <programme start="20260916210000 +0000" stop="20260916220000 +0000" channel="tvp1"><title>Next show</title></programme>
</tv>'''
    guide = parse_xmltv(payload)
    channel = Channel("TVP 1", "https://example.test/stream", tvg_id="tvp1")
    current, upcoming = guide.current_next(channel, datetime(2026, 9, 16, 20, 30, tzinfo=timezone.utc))
    assert current and current.title == "Current show"
    assert upcoming and upcoming.title == "Next show"


def test_fuzzy_name_matching_restores_classic_epg_behavior() -> None:
    payload = b'''<?xml version="1.0" encoding="UTF-8"?>
<tv>
  <channel id="discovery-pl"><display-name>Discovery Channel Polska</display-name></channel>
  <programme start="20260916200000 +0000" stop="20260916210000 +0000" channel="discovery-pl"><title>Documentary</title></programme>
</tv>'''
    guide = parse_xmltv(payload)
    channel = Channel("Discovery Channel PL HD", "https://example.test/stream")
    assert guide.resolve_channel_id(channel) == "discovery-pl"
