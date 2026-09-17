# Changelog

## 2.1.0 - 2026-09-17

### Restored
- Visible recent-playlist reopening for local M3U/M3U8 files and authorized HTTP/HTTPS playlist URLs.
- Multiple saved XMLTV/XMLTV.GZ EPG sources with add/select/remove controls.
- One-time migration of classic `config.json` VLC path and EPG source preferences.

### Improved
- The README now displays the custom FastIPTV application icon and documents the real regression-recovery scope.
- Recent entries are deduplicated and capped to 10.
- Saved EPG sources are deduplicated and capped to 25.
- Legacy proxy-source settings are deliberately excluded from migration.
- Malformed legacy configuration no longer affects application startup.

### Tested
- Settings round-trip with multiple EPG sources.
- Legacy config migration and explicit proxy-setting exclusion.
- Invalid legacy configuration fallback.

## 2.0.0 - 2026-09-16

### Added
- Modern PySide6 / Qt 6 desktop interface with automatic Polish/English startup language.
- Local and remote M3U/M3U8 playlist loading with explicit size and channel-count limits.
- Search, group filtering, favorites, stream URL copy and VLC playback.
- XMLTV/XMLTV.GZ EPG parsing with bounded decompression and current/next programme display.
- Per-user settings stored outside the repository and application directory.
- Automatic VLC discovery plus user-selectable VLC executable.
- Custom FastIPTV application artwork and automated Windows ICO generation.
- Python 3.10-3.14 CI, unit tests and Windows release automation.
- Standalone Windows EXE, portable ZIP and SHA256 checksums.

### Changed
- Replaced the ~44 KB single-file terminal application with a modular `src/fastiptv` package.
- Replaced the terminal-only Rich interface with a desktop UI while retaining `python run.py` as a compatibility launcher.
- Network operations now use bounded timeouts, retries and download-size limits.
- XMLTV matching prefers `tvg-id`, then normalized exact channel names, reducing accidental guide mismatches.

### Removed
- Public proxy-list aggregation and automatic third-party proxy harvesting.
- Repository-local configuration and error-log state.

FastIPTV Player remains a playlist-management and playback utility. It does not provide channels, credentials, subscriptions or access rights.
