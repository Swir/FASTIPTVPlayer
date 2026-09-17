<div align="center">

<img src="assets/fastiptv.svg" width="160" alt="FastIPTV Player application icon">

# FastIPTV Player 2.1

### Modern M3U/M3U8 playlist browser, XMLTV guide and VLC launcher

**Python 3.10-3.14 • PySide6 / Qt 6 • M3U/M3U8 • XMLTV • VLC • Recent Playlists • Windows EXE**

</div>

## Why v2.1 exists

FastIPTV Player 2 replaced the old ~44 KB single-file terminal program with a safer and maintainable desktop application. The regression audit found that several useful, non-proxy workflows from the classic version were no longer directly available after the rewrite. v2.1 restores them without bringing back automatic public proxy harvesting.

## Restored and improved classic workflows

- **Recent playlist reopening** is now visible directly in the GUI. Both local M3U/M3U8 files and authorized HTTP/HTTPS playlist URLs can be reopened from the recent list.
- **Multiple saved EPG sources** are restored. XMLTV/XMLTV.GZ URLs can be added, selected and removed from the GUI instead of keeping only one source.
- **Safe migration from legacy `config.json`** preserves the old VLC path and EPG source list when modern settings do not exist yet.
- Legacy proxy-source settings are deliberately ignored during migration.
- Search, group browsing and current/next EPG information remain available in the modern table interface.

## Features

- open local `.m3u` and `.m3u8` playlists
- open authorized remote playlists over HTTP/HTTPS
- reopen up to 10 recent local/remote playlists from the GUI
- search by channel name, group or `tvg-id`
- filter by playlist group and favorites
- persistent favorites and recent playlist references
- XMLTV / XMLTV.GZ guide with **Now** and **Next** programmes
- maintain up to 25 saved EPG source URLs
- safe bounded playlist/EPG downloads with retries and explicit timeouts
- VLC auto-discovery and configurable VLC executable
- copy selected stream URL to the clipboard
- automatic Polish system-locale UI with English fallback
- dark-blue Windows-friendly interface with `by Swir` footer
- custom application icon displayed here, used by the GUI and embedded in the Windows EXE
- CI across Python 3.10, 3.11, 3.12, 3.13 and 3.14
- automated tested Windows EXE + portable ZIP + SHA256 releases

## Intentionally not restored

The classic terminal application could download, aggregate and test public proxy lists. That feature stays removed. v2.1 is focused on playlist management, guide data and playback for streams that the user is entitled or authorized to access. Legacy proxy-source entries in `config.json` are not imported.

## Upgrade from the classic version

The former application stored settings in a repository/application-local `config.json`. When FastIPTV 2.1 starts and its modern per-user settings file does not exist, it can import:

- `vlc_path`
- `epg_sources`

Proxy configuration is ignored. The old file is not modified, and malformed legacy JSON never prevents the modern application from starting.

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
  settings.py              per-user settings + safe legacy migration
  i18n.py                  Polish/English UI strings
  ui.py                    PySide6 desktop interface
assets/fastiptv.svg        application artwork shown in this README
tests/                      unit and regression tests
tools/build_icon.py         Windows icon generator
.github/workflows/          CI and release automation
```

## Development and regression tests

```bash
python -m pip install -e ".[dev]"
pytest
python -m compileall -q src main.py run.py
python tools/build_icon.py
```

The regression suite covers M3U parsing, XMLTV handling, VLC launch validation, settings round-trips and safe migration of classic VLC/EPG preferences.

## Releases

Numbered releases contain:

- `FastIPTVPlayer.exe`
- `FastIPTVPlayer-vX.Y.Z-Windows-x64.zip`
- SHA256 checksum files for both downloads

The executable is smoke-tested before publication.

## Responsible use

FastIPTV Player is a playlist-management and playback utility. It does **not** provide TV channels, subscription credentials, account bypasses or access rights. Use only playlists and streams you are entitled or authorized to use, and respect provider terms and applicable law.

## Author

Developed by **Swir** — https://github.com/Swir
