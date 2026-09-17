<!-- SWIR-README-STANDARD:v2 -->

<div align="center">

<img width="100%" src="assets/readme/hero.svg" alt="FastIPTV Player — M3U playlists, XMLTV guide and VLC playback" />

# FastIPTV Player

**Modern M3U/M3U8 playlist browsing, XMLTV programme guide and VLC playback for authorized streams.**

![Python](https://img.shields.io/badge/Python-3.10--3.14-02050A?style=for-the-badge&logo=python&logoColor=62E5FF)
![GUI](https://img.shields.io/badge/GUI-PySide6%20%2F%20Qt%206-02050A?style=for-the-badge&logo=qt&logoColor=62E5FF)
![Guide](https://img.shields.io/badge/Guide-XMLTV-02050A?style=for-the-badge&logoColor=62E5FF)
![Playback](https://img.shields.io/badge/Playback-VLC-02050A?style=for-the-badge&logo=vlcmediaplayer&logoColor=62E5FF)

[![Author](https://img.shields.io/badge/by-Swir-0088FF?style=flat-square&logo=github)](https://github.com/Swir)
[![Release](https://img.shields.io/badge/Release-v2.2.0-0088FF?style=flat-square)](https://github.com/Swir/FASTIPTVPlayer/releases/tag/v2.2.0)
[![Stars](https://img.shields.io/github/stars/Swir/FASTIPTVPlayer?style=flat-square&color=0088FF)](https://github.com/Swir/FASTIPTVPlayer/stargazers)

[**Highlights**](#-highlights) · [**Quick Start**](#-quick-start) · [**Workflow**](#-workflow) · [**Safety**](#-safety-and-resource-limits) · [**Releases**](#-releases)

</div>

<img width="100%" src="https://raw.githubusercontent.com/Swir/Swir/main/assets/power-divider-v4.svg" alt="SWIR electric divider" />

## 📍 Project Status

| Item | Status |
|---|---|
| Current release | [`v2.2.0`](https://github.com/Swir/FASTIPTVPlayer/releases/tag/v2.2.0) |
| Source runtime | Python 3.10–3.14 with PySide6 |
| Playback engine | VLC installed separately |
| UI languages | Polish with English fallback |
| Product progress | **N/A** — no canonical product roadmap is maintained |

<p align="center">
  <img width="100%" src="assets/readme/progress-card.svg" alt="FastIPTV Player product progress — N/A because no canonical roadmap exists" />
</p>

The progress graphic deliberately reports **N/A** instead of deriving a completion percentage from releases, tests or regression-audit history.

## 🚀 Overview

**FastIPTV Player 2.2** is a modular PySide6 desktop client for opening local or authorized remote M3U/M3U8 playlists, browsing channels, maintaining favorites, loading XMLTV programme data and launching selected streams in VLC.

The modern application replaces the older terminal-oriented implementation while preserving useful workflows such as configurable VLC playback, multiple EPG sources, recent playlists and fuzzy EPG matching. Public proxy harvesting from the classic version remains intentionally removed; v2.2 accepts only a proxy explicitly supplied by the user.

FastIPTV does **not** provide channels, subscriptions, credentials or access rights.

## ✨ Highlights

| Feature | What it does |
|---|---|
| 📺 M3U / M3U8 playlists | Open local playlists or authorized HTTP/HTTPS playlist URLs. |
| 🔎 Search and groups | Filter by channel name, group or `tvg-id`. |
| ⭐ Favorites | Keep a persistent local favorites list. |
| 🕘 Recent playlists | Reopen up to 10 recent local or remote playlist references. |
| 🗓️ XMLTV / XMLTV.GZ | Display **Now** and **Next** programme information. |
| 🧩 EPG matching | Match by `tvg-id`, normalized name and a cached fuzzy-name fallback. |
| 📚 Multiple EPG sources | Maintain up to 25 saved guide-source URLs. |
| ▶️ VLC launch | Auto-discover VLC or use a configured executable path. |
| 🌐 Manual proxy | Optionally pass one explicit authorized HTTP proxy to VLC; no harvesting/scanning. |
| 📋 Clipboard | Copy the selected stream URL. |
| 🇵🇱 / 🇬🇧 UI | Polish system-locale selection with English fallback. |
| 🛡️ Bounded inputs | Apply download, parse and visible-row limits to reduce malformed-input risk. |

## 🧭 Regression Audit / Restored Workflows

The current code was compared with the classic implementation instead of treating a successful new build as proof of feature parity. The v2 series restored or replaced useful behavior while keeping unsafe or unnecessary network-proxy automation removed.

Restored workflows include:

- local playlist loading, search and group browsing;
- configurable VLC playback;
- multiple EPG sources;
- Now/Next programme display;
- fuzzy EPG matching;
- recent playlist reopening;
- an explicitly configured VLC HTTP proxy.

### Proxy safety change

The classic terminal program downloaded and tested third-party public proxy lists. **That behavior remains intentionally removed.** FastIPTV 2.2 only accepts an explicit `host:port` or `http(s)://host:port` value supplied by the user. It does not harvest proxy lists, scan for proxies or test them against public IP-check services.

Use the option only with infrastructure you control or are authorized to use.

## ⚙️ Quick Start

### Windows release

The latest verified public package is [**v2.2.0**](https://github.com/Swir/FASTIPTVPlayer/releases/tag/v2.2.0), with a Windows EXE, portable ZIP and SHA-256 sidecars.

VLC Media Player is installed separately and must be discoverable or configured in the application.

### From source

```bash
git clone https://github.com/Swir/FASTIPTVPlayer.git
cd FASTIPTVPlayer
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .
python main.py
```

The historical `python run.py` command remains available as a compatibility launcher.

For an offline GUI startup check that does not fetch playlists/EPG or launch VLC:

```bash
python main.py --smoke-gui
```

## 📋 Requirements / Compatibility

| Component | Current scope |
|---|---|
| Python | `>=3.10,<3.15`; CI covers 3.10–3.14 |
| GUI | PySide6 / Qt 6 |
| HTTP | Requests |
| Settings | platformdirs-backed per-user configuration |
| Playback | VLC installed separately |
| Published binary | Windows x64 |

Playlist and EPG providers still determine stream availability, URL validity, programme data quality and codec/container compatibility.

## 🎮 Workflow

1. Open a local `.m3u` / `.m3u8` file or an authorized remote playlist URL.
2. Use search, group filters or favorites to narrow the channel list.
3. Add one or more XMLTV/XMLTV.GZ sources when guide data is available.
4. Select a channel and review Now/Next information when matched.
5. Launch playback in VLC or copy the selected stream URL.
6. Optionally configure an authorized manual VLC proxy under the Playback menu.

### Upgrade from the classic version

If modern per-user settings do not yet exist, the application can import selected values from the former repository-local `config.json`:

- `vlc_path`;
- `epg_sources`.

Legacy public-proxy-source configuration is ignored. The old config file is not modified, and malformed legacy JSON does not prevent startup.

## 🛡️ Safety and Resource Limits

FastIPTV applies bounded limits to reduce resource-exhaustion risk:

- local/remote playlist: 20 MB;
- parsed playlist: 20,000 channels;
- downloaded compressed EPG: 60 MB;
- decompressed EPG: 120 MB;
- parsed XMLTV programmes: 250,000;
- visible rows at once: 3,000.

Use search/group filters for larger channel sets.

FastIPTV does **not** provide TV channels, subscription credentials, account bypasses or access rights. Use only playlists, streams, guide sources and proxy infrastructure you are entitled or explicitly authorized to use.

## 🧠 Technology / Project Layout

```text
src/fastiptv/
  app.py          # bootstrap + GUI smoke mode
  ui.py           # main PySide6 interface
  enhanced_ui.py  # manual playback settings
  playlist.py     # M3U/M3U8 parser
  epg.py          # XMLTV parser + exact/fuzzy matching
  network.py      # bounded HTTP/HTTPS downloads
  vlc.py          # VLC discovery, proxy validation and launcher
  settings.py     # per-user settings + legacy migration
  i18n.py         # Polish/English strings
assets/
  fastiptv.svg    # application artwork
  readme/         # SWIR README PRO hero and progress graphics
tests/
tools/build_icon.py
tools/generate_progress_svg.py
.github/workflows/
```

## 🧪 Development and Tests

```bash
python -m pip install -e ".[dev]"
pytest
python -m compileall -q src main.py run.py tools tests
python main.py --smoke-gui
python tools/build_icon.py
python tools/generate_progress_svg.py --check
```

The regression suite covers M3U parsing, XMLTV parsing/fuzzy matching, VLC discovery and safe proxy argument construction, settings round-trips, EPG-source persistence and migration of selected classic preferences.

## 🗺️ Progress

<p align="center">
  <img width="100%" src="assets/readme/progress-mini.svg" alt="FastIPTV Player roadmap progress — N/A" />
</p>

There is no canonical product roadmap in the current repository, so completion remains **N/A**. Release version numbers and regression-restoration work are not treated as a product-completion denominator.

## 📦 Releases

The latest verified public release is [**v2.2.0**](https://github.com/Swir/FASTIPTVPlayer/releases/tag/v2.2.0), published on September 17, 2026. It contains:

- `FastIPTVPlayer.exe`;
- `FastIPTVPlayer-v2.2.0-Windows-x64.zip`;
- SHA-256 checksum files for both downloads.

The release workflow runs tests and GUI checks before publishing its generated artifacts. An older 2024 `FASTIPTV BETA v1.0` entry exists as a **draft**, not a current public release.

[**Browse all GitHub Releases →**](https://github.com/Swir/FASTIPTVPlayer/releases)

## 🔎 Search Keywords

`M3U IPTV player python` • `M3U8 playlist browser` • `PySide6 IPTV player` • `XMLTV programme guide` • `VLC playlist launcher` • `IPTV favorites desktop app` • `XMLTV fuzzy channel matching` • `authorized IPTV playlist player` • `Windows IPTV desktop app` • `Python XMLTV viewer` • `M3U channel search` • `VLC manual proxy playback`

<img width="100%" src="https://raw.githubusercontent.com/Swir/Swir/main/assets/power-divider-v4.svg" alt="SWIR electric divider" />

<div align="center">

<img src="assets/fastiptv.svg" width="64" alt="FastIPTV Player application icon" />

### `OPEN • FILTER • GUIDE • PLAY`

**FastIPTV Player — by Swir**

[**← SWIR profile**](https://github.com/Swir) · [**All projects →**](https://github.com/Swir?tab=repositories) · [**Report an issue**](https://github.com/Swir/FASTIPTVPlayer/issues)

</div>
