<div align="center">

<img src="assets/fastiptv.svg" width="160" alt="FastIPTV Player application icon">

# FastIPTV Player 2.2

### Modern M3U/M3U8 playlist browser, XMLTV guide and VLC launcher

**Python 3.10-3.14 • PySide6 / Qt 6 • M3U/M3U8 • XMLTV • VLC • PL/EN • Windows EXE**

</div>

## Regression-audit status

FastIPTV Player 2 replaced the old ~44 KB single-file terminal program with a modular desktop application. The follow-up regression audit compares the current code with the classic implementation instead of checking only whether a new build starts.

v2.1 restored recent playlist reopening, multi-source EPG management and safe migration of the old VLC/EPG preferences. v2.2 restores two more useful classic behaviors that were lost in the rewrite: **fuzzy EPG channel matching** and **manual VLC proxy playback**, while keeping automatic public proxy harvesting removed.

## Features

- open local `.m3u` and `.m3u8` playlists
- open authorized remote playlists over HTTP/HTTPS
- reopen up to 10 recent local/remote playlists from the GUI
- search by channel name, group or `tvg-id`
- filter by playlist group and favorites
- persistent favorites and recent playlist references
- XMLTV / XMLTV.GZ guide with **Now** and **Next** programmes
- exact EPG matching by `tvg-id`, normalized name, then a cached fuzzy-name fallback inspired by the classic application
- maintain up to 25 saved EPG source URLs
- safe bounded playlist/EPG downloads with retries and explicit timeouts
- VLC auto-discovery and configurable VLC executable
- **optional manual VLC HTTP proxy** for a proxy you already control or are authorized to use
- copy selected stream URL to the clipboard
- automatic Polish system-locale UI with English fallback
- dark-blue Windows-friendly interface with `by Swir` footer
- custom application icon displayed above, used by the GUI and embedded in the Windows EXE
- CI across Python 3.10, 3.11, 3.12, 3.13 and 3.14
- Windows source-GUI smoke test
- packaged-EXE GUI smoke test before publication
- automated Windows EXE + portable ZIP + SHA256 releases

## Restored classic workflows

The audit checked the old `run.py` and its README. The modern app now preserves the useful parts of those workflows without returning to the old monolith:

- local playlist loading and group browsing
- channel search
- VLC playback with configurable executable
- multiple EPG sources
- Now/Next guide display
- fuzzy EPG matching when providers use slightly different channel names
- recent playlist reopening
- a manually supplied VLC HTTP proxy

### Proxy safety change

The classic terminal version also downloaded, aggregated and tested third-party public proxy lists. **That behavior remains intentionally removed.** FastIPTV 2.2 provides only a manual proxy field under the **Playback** menu. It accepts an explicit `host:port` or `http(s)://host:port`, does not harvest proxy lists, does not scan for proxies and does not test the proxy against public IP-check services.

Use the proxy option only with infrastructure you control or are authorized to use.

## Upgrade from the classic version

The former application stored settings in a repository/application-local `config.json`. When FastIPTV starts and its modern per-user settings file does not exist, it can import:

- `vlc_path`
- `epg_sources`

Legacy public proxy-source configuration is deliberately ignored. The old application did not persist its currently selected manual proxy, so there is no safe manual proxy value to migrate automatically. A proxy entered in v2.2 is stored in the modern per-user settings file.

The old config file is never modified, and malformed legacy JSON does not prevent startup.

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

For an offline startup check that creates the real Qt window but does not download a playlist/EPG or launch VLC:

```bash
python main.py --smoke-gui
```

## Manual VLC proxy

Open **Playback → Manual VLC proxy…** and enter for example:

```text
127.0.0.1:8080
```

or:

```text
http://proxy.internal:3128
```

Leave the field blank to disable it. Credentials, URL paths and unsupported schemes are rejected. The value is passed to VLC using an argument list (`--http-proxy`) without shell execution.

## Safety and resource limits

FastIPTV Player deliberately applies bounded resource limits:

- local/remote playlist: 20 MB
- parsed playlist: 20,000 channels
- downloaded compressed EPG: 60 MB
- decompressed EPG: 120 MB
- parsed XMLTV programmes: 250,000
- visible table rows at once: 3,000; use search/group filters for larger lists

These limits protect the desktop application from malformed or unexpectedly large inputs.

FastIPTV does **not** provide TV channels, subscription credentials, account bypasses or access rights. Use only playlists and streams you are entitled or authorized to access.

## Project layout

```text
src/fastiptv/
  app.py                   application bootstrap + GUI smoke mode
  ui.py                    main PySide6 desktop interface
  enhanced_ui.py           v2.2 restored manual playback settings
  playlist.py              M3U/M3U8 parser
  epg.py                   XMLTV parser + exact/fuzzy guide matching
  network.py               bounded HTTP/HTTPS downloads
  vlc.py                   VLC discovery, proxy validation and safe launcher
  settings.py              per-user settings + safe legacy migration
  i18n.py                  Polish/English UI strings
assets/fastiptv.svg        application artwork shown in this README
tests/                      unit and regression tests
tools/build_icon.py         Windows icon generator
.github/workflows/          CI and release automation
```

## Development and regression tests

```bash
python -m pip install -e ".[dev]"
pytest
python -m compileall -q src main.py run.py tools tests
python main.py --smoke-gui
python tools/build_icon.py
```

The regression suite covers M3U parsing, XMLTV parsing and fuzzy matching, VLC discovery and safe proxy argument construction, settings round-trips, EPG-source persistence, and classic VLC/EPG preference migration.

## Releases

Numbered releases contain:

- `FastIPTVPlayer.exe`
- `FastIPTVPlayer-vX.Y.Z-Windows-x64.zip`
- SHA256 checksum files for both downloads

Before a Release can be published, the workflow runs tests, starts the real source GUI offscreen, builds the application icon and EXE, verifies executable metadata, then starts the **packaged EXE GUI itself** offscreen. Publication happens only after all of those steps succeed.

## Author

Developed by **Swir** — https://github.com/Swir
