<div align="center">

# FastIPTV Player 2

### Modern M3U/M3U8 playlist browser, XMLTV guide and VLC launcher

**Python 3.10-3.14 • PySide6 / Qt 6 • M3U/M3U8 • XMLTV • VLC • Windows EXE**

</div>

## What changed in v2

FastIPTV Player 2 replaces the old ~44 KB single-file terminal program with a maintainable desktop application. Playlist parsing, downloads, XMLTV processing, settings and VLC launching now live in separate tested modules. The interface starts in Polish when the system locale is Polish and falls back to English for other locales.

The old public proxy-list aggregation was intentionally removed. FastIPTV is focused on playlists and streams that the user is authorized to access; it does not discover access credentials or supply TV services.

## Features

- open local `.m3u` and `.m3u8` playlists
- open authorized remote playlists over HTTP/HTTPS
- search by channel name, group or `tvg-id`
- filter by playlist group and favorites
- persistent favorites and recent playlist references
- optional XMLTV / XMLTV.GZ guide with **Now** and **Next** programmes
- safe bounded playlist/EPG downloads with retries and explicit timeouts
- VLC auto-discovery and configurable VLC executable
- copy selected stream URL to the clipboard
- dark-blue Windows-friendly interface with `by Swir` footer
- custom application icon
- CI across Python 3.10, 3.11, 3.12, 3.13 and 3.14
- automated tested Windows EXE + portable ZIP + SHA256 releases

## Run from source

```bash
git clone https://github.com/Swir/FASTIPTVPlayer.git
cd FASTIPTVPlayer
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .
python main.py
```

The historical command `python run.py` remains available as a compatibility launcher. VLC Media Player is installed separately.

## Safety limits

FastIPTV Player deliberately applies bounded resource limits:

- local/remote playlist: 20 MB
- parsed playlist: 20,000 channels
- downloaded compressed EPG: 60 MB
- decompressed EPG: 120 MB
- parsed XMLTV programmes: 250,000
- visible table rows at once: 3,000; use search/group filters for larger lists

These limits protect the desktop application from malformed or unexpectedly large inputs.

## Project layout

```text
src/fastiptv/              application package
  playlist.py              M3U/M3U8 parser
  epg.py                   XMLTV guide parser/matcher
  network.py               bounded HTTP/HTTPS downloads
  vlc.py                   VLC discovery and launcher
  settings.py              per-user settings
  i18n.py                  Polish/English UI strings
  ui.py                    PySide6 desktop interface
assets/                     project artwork
tests/                      unit tests
tools/build_icon.py         Windows icon generator
.github/workflows/          CI and release automation
```

## Releases

Numbered releases contain `FastIPTVPlayer.exe`, a portable Windows ZIP and SHA256 checksum files. The executable is smoke-tested before publication.

## Responsible use

FastIPTV Player is a playlist-management and playback utility. It does **not** provide TV channels, subscription credentials, account bypasses or access rights. Use only playlists and streams you are entitled or authorized to use, and respect provider terms and applicable law.

## Author

Developed by **Swir** — https://github.com/Swir
