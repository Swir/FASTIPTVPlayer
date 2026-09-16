from __future__ import annotations

import locale

_STRINGS = {
    "en": {
        "open_file": "Open playlist",
        "open_url": "Open URL",
        "load_epg": "Load EPG",
        "vlc_path": "VLC path",
        "play": "Play in VLC",
        "favorite": "Favorite",
        "copy_url": "Copy URL",
        "search": "Search channels…",
        "all_groups": "All groups",
        "favorites_only": "Favorites only",
        "channel": "Channel",
        "group": "Group",
        "now": "Now",
        "next": "Next",
        "status": "Status",
        "ready": "Ready — open an authorized M3U/M3U8 playlist.",
        "loaded": "Loaded {count:,} channels from {source}",
        "display_limit": "Showing first {shown:,} of {total:,} matching channels — narrow the search for more.",
        "playlist_error": "Playlist error: {error}",
        "epg_error": "EPG error: {error}",
        "epg_loaded": "EPG loaded: {count:,} channel IDs",
        "url_prompt": "Playlist URL (http/https):",
        "epg_prompt": "XMLTV / XMLTV.GZ URL (http/https):",
        "no_selection": "Select a channel first.",
        "vlc_missing": "VLC was not found. Use ‘VLC path’ to select vlc.exe.",
        "vlc_started": "Opened {name} in VLC.",
        "vlc_error": "VLC error: {error}",
        "copied": "Stream URL copied to clipboard.",
        "favorite_added": "Added to favorites: {name}",
        "favorite_removed": "Removed from favorites: {name}",
        "working": "Working…",
    },
    "pl": {
        "open_file": "Otwórz playlistę",
        "open_url": "Otwórz URL",
        "load_epg": "Wczytaj EPG",
        "vlc_path": "Ścieżka VLC",
        "play": "Odtwórz w VLC",
        "favorite": "Ulubione",
        "copy_url": "Kopiuj URL",
        "search": "Szukaj kanałów…",
        "all_groups": "Wszystkie grupy",
        "favorites_only": "Tylko ulubione",
        "channel": "Kanał",
        "group": "Grupa",
        "now": "Teraz",
        "next": "Następnie",
        "status": "Status",
        "ready": "Gotowe — otwórz legalnie używaną playlistę M3U/M3U8.",
        "loaded": "Wczytano {count:,} kanałów z {source}",
        "display_limit": "Pokazano pierwsze {shown:,} z {total:,} pasujących kanałów — zawęź wyszukiwanie.",
        "playlist_error": "Błąd playlisty: {error}",
        "epg_error": "Błąd EPG: {error}",
        "epg_loaded": "Wczytano EPG: {count:,} identyfikatorów kanałów",
        "url_prompt": "URL playlisty (http/https):",
        "epg_prompt": "URL XMLTV / XMLTV.GZ (http/https):",
        "no_selection": "Najpierw wybierz kanał.",
        "vlc_missing": "Nie znaleziono VLC. Użyj ‘Ścieżka VLC’, aby wskazać vlc.exe.",
        "vlc_started": "Otwarto {name} w VLC.",
        "vlc_error": "Błąd VLC: {error}",
        "copied": "Skopiowano URL strumienia do schowka.",
        "favorite_added": "Dodano do ulubionych: {name}",
        "favorite_removed": "Usunięto z ulubionych: {name}",
        "working": "Pracuję…",
    },
}


def system_language() -> str:
    code = (locale.getlocale()[0] or "").lower()
    return "pl" if code.startswith("pl") else "en"


def translator(language: str | None = None):
    selected = language if language in _STRINGS else system_language()
    strings = _STRINGS[selected]

    def tr(key: str, **values) -> str:
        template = strings.get(key, _STRINGS["en"].get(key, key))
        return template.format(**values)

    return tr
