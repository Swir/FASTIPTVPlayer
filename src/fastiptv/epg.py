from __future__ import annotations

import difflib
import re
from collections import defaultdict
from datetime import datetime, timezone
from io import BytesIO
import xml.etree.ElementTree as ET

from .models import Channel, Programme

MAX_PROGRAMMES = 250_000
FUZZY_MATCH_CUTOFF = 0.72


class EPGError(ValueError):
    """Raised when XMLTV data is invalid or exceeds configured limits."""


def normalize_channel_name(value: str) -> str:
    normalized = value.casefold()
    normalized = re.sub(r"\b(?:uhd|fhd|hd|4k)\b", "", normalized)
    normalized = re.sub(r"[^a-z0-9ąćęłńóśźż]+", " ", normalized)
    return " ".join(normalized.split())


def parse_xmltv_time(value: str | None) -> datetime | None:
    if not value:
        return None
    raw = value.strip()
    try:
        if len(raw) >= 20 and raw[14] == " ":
            parsed = datetime.strptime(raw[:20], "%Y%m%d%H%M%S %z")
        else:
            local_tz = datetime.now().astimezone().tzinfo or timezone.utc
            parsed = datetime.strptime(raw[:14], "%Y%m%d%H%M%S").replace(tzinfo=local_tz)
        return parsed.astimezone(timezone.utc)
    except (ValueError, TypeError):
        return None


class EPGGuide:
    def __init__(self, names: dict[str, tuple[str, ...]], programmes: dict[str, list[Programme]]) -> None:
        self.names = names
        self.programmes = programmes
        self._name_index: dict[str, str] = {}
        self._resolve_cache: dict[tuple[str, str], str | None] = {}
        for channel_id, values in names.items():
            normalized_id = normalize_channel_name(channel_id)
            if normalized_id:
                self._name_index.setdefault(normalized_id, channel_id)
            for name in values:
                normalized = normalize_channel_name(name)
                if normalized:
                    self._name_index.setdefault(normalized, channel_id)
        self._normalized_names = tuple(self._name_index.keys())

    def resolve_channel_id(self, channel: Channel) -> str | None:
        if channel.tvg_id and channel.tvg_id in self.programmes:
            return channel.tvg_id

        normalized = normalize_channel_name(channel.name)
        cache_key = (channel.tvg_id, normalized)
        if cache_key in self._resolve_cache:
            return self._resolve_cache[cache_key]

        exact = self._name_index.get(normalized)
        if exact:
            self._resolve_cache[cache_key] = exact
            return exact

        # The classic FastIPTV app used difflib to recover EPG matches where
        # provider/channel naming differed slightly. Keep that useful fallback,
        # but only after exact tvg-id and normalized-name matching has failed.
        match = difflib.get_close_matches(
            normalized,
            self._normalized_names,
            n=1,
            cutoff=FUZZY_MATCH_CUTOFF,
        )
        resolved = self._name_index.get(match[0]) if match else None
        self._resolve_cache[cache_key] = resolved
        return resolved

    def current_next(self, channel: Channel, now: datetime | None = None) -> tuple[Programme | None, Programme | None]:
        channel_id = self.resolve_channel_id(channel)
        if not channel_id:
            return None, None
        moment = now or datetime.now(timezone.utc)
        if moment.tzinfo is None:
            moment = moment.replace(tzinfo=timezone.utc)
        else:
            moment = moment.astimezone(timezone.utc)
        current: Programme | None = None
        upcoming: Programme | None = None
        for programme in self.programmes.get(channel_id, []):
            if programme.start <= moment < programme.stop:
                current = programme
            elif programme.start > moment:
                upcoming = programme
                break
        return current, upcoming


def parse_xmltv(payload: bytes, max_programmes: int = MAX_PROGRAMMES) -> EPGGuide:
    names: dict[str, tuple[str, ...]] = {}
    programmes: dict[str, list[Programme]] = defaultdict(list)
    count = 0
    try:
        for _event, elem in ET.iterparse(BytesIO(payload), events=("end",)):
            if elem.tag == "channel":
                channel_id = (elem.get("id") or "").strip()
                if channel_id:
                    display_names = tuple(
                        (node.text or "").strip()
                        for node in elem.findall("display-name")
                        if (node.text or "").strip()
                    )
                    names[channel_id] = display_names
                elem.clear()
            elif elem.tag == "programme":
                channel_id = (elem.get("channel") or "").strip()
                start = parse_xmltv_time(elem.get("start"))
                stop = parse_xmltv_time(elem.get("stop"))
                title_node = elem.find("title")
                desc_node = elem.find("desc")
                title = (title_node.text or "Untitled").strip() if title_node is not None else "Untitled"
                description = (desc_node.text or "").strip() if desc_node is not None else ""
                if channel_id and start and stop and stop > start:
                    programmes[channel_id].append(Programme(channel_id, start, stop, title, description))
                    count += 1
                    if count > max_programmes:
                        raise EPGError(f"EPG contains more than the supported {max_programmes:,} programmes.")
                elem.clear()
    except EPGError:
        raise
    except ET.ParseError as exc:
        raise EPGError(f"Invalid XMLTV document: {exc}") from exc

    for entries in programmes.values():
        entries.sort(key=lambda item: item.start)
    if not programmes and not names:
        raise EPGError("No XMLTV channels or programmes were found.")
    return EPGGuide(names, dict(programmes))
