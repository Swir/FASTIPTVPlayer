from __future__ import annotations

import gzip
from io import BytesIO
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from . import __version__

MAX_PLAYLIST_BYTES = 20 * 1024 * 1024
MAX_EPG_BYTES = 60 * 1024 * 1024
MAX_EPG_DECOMPRESSED_BYTES = 120 * 1024 * 1024


class DownloadError(RuntimeError):
    """Raised when a remote playlist or EPG source cannot be downloaded safely."""


def _validate_http_url(url: str) -> str:
    value = url.strip()
    try:
        parsed = urlparse(value)
    except ValueError as exc:
        raise DownloadError(f"Invalid URL: {url}") from exc
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        raise DownloadError("Only http:// and https:// URLs are supported for remote sources.")
    return value


def _session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        status=3,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        respect_retry_after_header=True,
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.mount("http://", HTTPAdapter(max_retries=retry))
    session.headers.update({"User-Agent": f"FastIPTV/{__version__} (+https://github.com/Swir/FASTIPTVPlayer)"})
    return session


def download_bytes(url: str, max_bytes: int) -> bytes:
    target = _validate_http_url(url)
    try:
        with _session() as session:
            with session.get(target, timeout=(5.0, 20.0), stream=True, allow_redirects=True) as response:
                response.raise_for_status()
                length = response.headers.get("content-length")
                if length and int(length) > max_bytes:
                    raise DownloadError(f"Remote source exceeds the {max_bytes // (1024 * 1024)} MB limit.")
                chunks: list[bytes] = []
                total = 0
                for chunk in response.iter_content(chunk_size=128 * 1024):
                    if not chunk:
                        continue
                    total += len(chunk)
                    if total > max_bytes:
                        raise DownloadError(f"Remote source exceeds the {max_bytes // (1024 * 1024)} MB limit.")
                    chunks.append(chunk)
                return b"".join(chunks)
    except DownloadError:
        raise
    except (requests.RequestException, ValueError) as exc:
        raise DownloadError(f"Download failed: {exc}") from exc


def download_playlist_text(url: str) -> str:
    return download_bytes(url, MAX_PLAYLIST_BYTES).decode("utf-8-sig", errors="replace")


def download_epg(url: str) -> bytes:
    payload = download_bytes(url, MAX_EPG_BYTES)
    if not payload.startswith(b"\x1f\x8b"):
        return payload
    try:
        with gzip.GzipFile(fileobj=BytesIO(payload)) as archive:
            decoded = archive.read(MAX_EPG_DECOMPRESSED_BYTES + 1)
    except OSError as exc:
        raise DownloadError(f"Invalid gzip EPG source: {exc}") from exc
    if len(decoded) > MAX_EPG_DECOMPRESSED_BYTES:
        raise DownloadError("Decompressed EPG exceeds the 120 MB safety limit.")
    return decoded
