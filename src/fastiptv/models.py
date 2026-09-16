from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256


@dataclass(frozen=True, slots=True)
class Channel:
    name: str
    url: str
    group: str = "Other"
    tvg_id: str = ""
    logo: str = ""

    @property
    def favorite_key(self) -> str:
        payload = f"{self.name}\n{self.url}".encode("utf-8", errors="replace")
        return sha256(payload).hexdigest()


@dataclass(frozen=True, slots=True)
class Programme:
    channel_id: str
    start: datetime
    stop: datetime
    title: str
    description: str = ""
