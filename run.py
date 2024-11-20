import os
import re
import sys
import json
import time
import threading
import requests
import subprocess
import logging
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from rich.traceback import install
from rich.theme import Theme
from rich import box
import xml.etree.ElementTree as ET
import gzip
import io
import difflib  # Do porównywania nazw kanałów

# Funkcja do uzyskiwania ścieżki bazowej
def get_base_path():
    """Zwraca ścieżkę bazową do zasobów."""
    if getattr(sys, 'frozen', False):
        # PyInstaller tworzy atrybut 'frozen'
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def resource_path(relative_path):
    """Zwraca pełną ścieżkę do zasobu."""
    base_path = get_base_path()
    return os.path.join(base_path, relative_path)

# Konfiguracja Rich i logowania
custom_theme = Theme({
    "title": "bold magenta",
    "options": "bold cyan",
    "highlight": "bold yellow",
    "error": "bold red",
    "success": "bold green",
    "info": "bold blue"
})
console = Console(theme=custom_theme)
install()  # Rich będzie formatował tracebacki

# Konfiguracja logowania
LOG_FILE = "error.log"
logging.basicConfig(
    filename=resource_path(LOG_FILE),
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Globalne zmienne
PLAYLIST = {}
CURRENT_GROUP = "Wszystkie"
PROXY_URL = None
VLC_PATH = None
EPG_DATA = {}
EPG_LOADED = False  # Flaga informująca, czy EPG zostało załadowane
EPG_SOURCES = []
DEFAULT_EPG_SOURCES = [
    "http://epg.ovh/pl/plar.xml",
    "http://epg.ovh/pl/pl.xml",
    # Możesz dodać inne polskie źródła EPG
]

# Domyślne źródła proxy
DEFAULT_PROXY_SOURCES = {
    "FreeProxyList": "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "ProxyScrape": "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all",
    "GeoNode": "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=http",
}

# Ścieżka do konfiguracji i playlists
CONFIG_FILE = "config.json"
PLAYLISTS_DIR = "playlists"  # Upewnij się, że nazwa folderu jest zgodna
AVAILABLE_PROXY_SOURCES = {}
ENABLED_PROXY_SOURCES = []

# Funkcja do załadowania konfiguracji
def load_config():
    """Załaduj konfigurację z pliku JSON."""
    global ENABLED_PROXY_SOURCES, AVAILABLE_PROXY_SOURCES, VLC_PATH, EPG_SOURCES
    config_path = resource_path(CONFIG_FILE)
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as file:
                config = json.load(file)
            AVAILABLE_PROXY_SOURCES = config.get("available_proxy_sources", DEFAULT_PROXY_SOURCES)
            ENABLED_PROXY_SOURCES = config.get("enabled_proxy_sources", list(AVAILABLE_PROXY_SOURCES.keys()))
            VLC_PATH = config.get("vlc_path")
            EPG_SOURCES = config.get("epg_sources", DEFAULT_EPG_SOURCES)
        except Exception as e:
            logging.warning(f"Nie udało się załadować konfiguracji: {e}")
            AVAILABLE_PROXY_SOURCES = DEFAULT_PROXY_SOURCES.copy()
            ENABLED_PROXY_SOURCES = list(AVAILABLE_PROXY_SOURCES.keys())
            EPG_SOURCES = DEFAULT_EPG_SOURCES.copy()
    else:
        # Jeśli plik konfiguracyjny nie istnieje, użyj domyślnych wartości
        AVAILABLE_PROXY_SOURCES = DEFAULT_PROXY_SOURCES.copy()
        ENABLED_PROXY_SOURCES = list(AVAILABLE_PROXY_SOURCES.keys())
        EPG_SOURCES = DEFAULT_EPG_SOURCES.copy()

# Funkcja do zapisania konfiguracji
def save_config():
    """Zapisz konfigurację do pliku JSON."""
    config = {
        "available_proxy_sources": AVAILABLE_PROXY_SOURCES,
        "enabled_proxy_sources": ENABLED_PROXY_SOURCES,
        "vlc_path": VLC_PATH,
        "epg_sources": EPG_SOURCES,
    }
    config_path = resource_path(CONFIG_FILE)
    try:
        with open(config_path, "w", encoding="utf-8") as file:
            json.dump(config, file, indent=4)
    except Exception as e:
        logging.error(f"Nie udało się zapisać konfiguracji: {e}")

# Funkcja do zarządzania źródłami EPG
def configure_epg_sources():
    """Zarządzaj źródłami EPG (dodaj/usuń własne)."""
    global EPG_SOURCES
    while True:
        options = EPG_SOURCES + ["Dodaj własne źródło", "Usuń źródło", "Zapisz i powrót"]
        choice = display_menu(options, "Zarządzanie źródłami EPG")
        if choice is None or choice == len(options) - 1:
            save_config()
            console.print("[success]Zapisano zmiany w źródłach EPG.[/success]")
            wait_for_enter("Naciśnij Enter, aby powrócić do menu głównego...")
            break
        elif choice == len(options) - 3:
            add_custom_epg_source()
        elif choice == len(options) - 2:
            remove_epg_source()
        else:
            # Wyświetl podgląd wybranego źródła
            console.print(f"[info]Źródło EPG: {EPG_SOURCES[choice]}[/info]")
            wait_for_enter("Naciśnij Enter, aby kontynuować...")

# Funkcja do dodawania własnego źródła EPG
def add_custom_epg_source():
    """Dodaj własne źródło EPG."""
    global EPG_SOURCES
    url = Prompt.ask("[bold yellow]Podaj URL nowego źródła EPG[/bold yellow]").strip()
    if url:
        if url in EPG_SOURCES:
            console.print("[error]Takie źródło EPG już istnieje.[/error]")
        else:
            EPG_SOURCES.append(url)
            console.print(f"[success]Dodano nowe źródło EPG: {url}[/success]")
    else:
        console.print("[error]URL nie może być pusty.[/error]")

# Funkcja do usuwania źródła EPG
def remove_epg_source():
    """Usuń źródło EPG."""
    global EPG_SOURCES
    if not EPG_SOURCES:
        console.print("[error]Brak źródeł EPG do usunięcia.[/error]")
        wait_for_enter("Naciśnij Enter, aby kontynuować...")
        return
    options = EPG_SOURCES + ["Anuluj"]
    choice = display_menu(options, "Usuń źródło EPG")
    if choice is not None and choice < len(EPG_SOURCES):
        source_to_remove = EPG_SOURCES[choice]
        EPG_SOURCES.remove(source_to_remove)
        console.print(f"[success]Usunięto źródło EPG: {source_to_remove}[/success]")
    else:
        console.print("[info]Anulowano usuwanie źródła.[/info]")

# Funkcja do pobierania i parsowania EPG
def load_epg():
    """Pobierz i przetwórz dane EPG."""
    global EPG_DATA, EPG_LOADED
    EPG_DATA.clear()
    # Pozwól użytkownikowi wybrać źródło EPG
    if not EPG_SOURCES:
        console.print("[error]Brak dostępnych źródeł EPG. Dodaj źródło w konfiguracji EPG.[/error]")
        wait_for_enter("Naciśnij Enter, aby kontynuować...")
        return

    choice = display_menu(EPG_SOURCES, "Wybierz źródło EPG")
    if choice is None:
        console.print("[info]Anulowano ładowanie EPG.[/info]")
        return

    selected_source = EPG_SOURCES[choice]
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Pobieranie danych EPG...", total=None)
        try:
            response = requests.get(selected_source, timeout=60, stream=True)
            if response.status_code == 200:
                progress.update(task, description=f"Przetwarzanie EPG z {selected_source}")
                if selected_source.endswith('.gz'):
                    # Rozpakuj skompresowany plik .gz
                    with gzip.GzipFile(fileobj=response.raw) as f:
                        xml_content = f.read()
                    parse_epg(xml_content)
                else:
                    parse_epg(response.content)
            else:
                console.print(f"[error]Nie udało się pobrać EPG z {selected_source} (Status {response.status_code})[/error]")
        except Exception as e:
            console.print(f"[error]Błąd podczas pobierania EPG z {selected_source}: {e}[/error]")
        progress.update(task, completed=True)
    EPG_LOADED = True
    console.print("[success]Dane EPG zostały załadowane.[/success]")

# Funkcja do parsowania EPG
def parse_epg(xml_data):
    """Przetwórz dane EPG w formacie XMLTV."""
    try:
        tree = ET.ElementTree(ET.fromstring(xml_data))
        root = tree.getroot()
        # Przechowuj informacje o kanałach
        channels_info = {}
        for channel in root.findall('channel'):
            channel_id = channel.get('id')
            display_names = [elem.text for elem in channel.findall('display-name')]
            channels_info[channel_id] = display_names

        for programme in root.findall('programme'):
            channel_id = programme.get('channel')
            start_time = parse_xmltv_time(programme.get('start'))
            stop_time = parse_xmltv_time(programme.get('stop'))
            title_element = programme.find('title')
            if title_element is not None:
                title = title_element.text
            else:
                title = "Brak tytułu"

            if channel_id not in EPG_DATA:
                EPG_DATA[channel_id] = []
            EPG_DATA[channel_id].append({
                'start': start_time,
                'stop': stop_time,
                'title': title
            })
        # Dodaj informacje o nazwach kanałów
        EPG_DATA['channel_names'] = channels_info
    except Exception as e:
        logging.error(f"Błąd podczas parsowania EPG: {e}")

# Funkcja do parsowania czasu XMLTV
def parse_xmltv_time(time_str):
    """Przetwórz czas w formacie XMLTV na obiekt datetime."""
    try:
        return datetime.strptime(time_str[:14], "%Y%m%d%H%M%S")
    except Exception as e:
        logging.error(f"Błąd parsowania czasu XMLTV: {e}")
        return None

# Funkcja do dopasowania kanału z EPG do kanału z playlisty
def match_channel_epg(channel_name):
    """Znajdź najlepsze dopasowanie kanału EPG do podanej nazwy kanału."""
    epg_channel_names = EPG_DATA.get('channel_names', {})
    all_epg_names = []
    channel_id_map = {}
    for channel_id, names in epg_channel_names.items():
        for name in names:
            all_epg_names.append(name)
            channel_id_map[name] = channel_id

    # Użyj funkcji get_close_matches do znalezienia najbliższego dopasowania
    matches = difflib.get_close_matches(channel_name, all_epg_names, n=1, cutoff=0.6)
    if matches:
        best_match = matches[0]
        matched_channel_id = channel_id_map[best_match]
        return matched_channel_id
    else:
        return None

# Funkcja do wyświetlania EPG dla kanału
def get_channel_epg(channel_name):
    """Pobierz aktualne i następne programy dla danego kanału."""
    if not EPG_LOADED:
        return None, None
    now = datetime.now()
    current_program = None
    next_program = None
    matched_channel_id = match_channel_epg(channel_name)
    if matched_channel_id and matched_channel_id in EPG_DATA:
        programs = EPG_DATA[matched_channel_id]
        for program in programs:
            if program['start'] <= now < program['stop']:
                current_program = program
            elif now < program['start'] and (next_program is None or program['start'] < next_program['start']):
                next_program = program
    return current_program, next_program

# Funkcja do przetwarzania playlisty na grupy i kanały
def parse_playlist(data):
    """Przetwarzaj zawartość playlisty na słownik grup i kanałów."""
    groups = {}
    lines = data.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF:"):
            attrs = {}
            channel_name = "Nieznany kanał"
            # Pobierz atrybuty i nazwę kanału
            if ',' in line:
                extinf, name = line.split(',', 1)
                channel_name = name.strip()
            else:
                extinf = line
            # Wyszukaj atrybuty w EXTINF
            matches = re.findall(r'([\w-]+)="([^"]+)"', extinf)
            for key, value in matches:
                attrs[key] = value
            current_group = attrs.get('group-title', 'Inne')
            # Pobierz URL z następnej linii
            i += 1
            if i < len(lines):
                url = lines[i].strip()
                if url.startswith("http"):
                    if current_group not in groups:
                        groups[current_group] = []
                    groups[current_group].append({
                        'name': channel_name,
                        'url': url,
                    })
        i += 1
    return dict(sorted(groups.items()))

# Funkcja do ładowania playlisty z pliku
def load_playlist(file_path):
    """Wczytaj playlistę z określonego pliku."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = file.read()
        return parse_playlist(data)
    except Exception as e:
        raise RuntimeError(f"Błąd ładowania playlisty: {e}")

# Funkcja do ładowania playlisty z pliku
def load_playlist_from_file():
    """Załaduj playlistę z pliku."""
    global PLAYLIST, EPG_LOADED
    playlists = list_playlists()
    if not playlists:
        console.print("[error]Brak dostępnych playlist w folderze 'playlists'.[/error]")
        wait_for_enter("Naciśnij Enter, aby wrócić do menu...")
        return

    choice = display_menu(playlists, "Wybierz Playlistę")
    if choice is not None:
        file_path = os.path.join(resource_path(PLAYLISTS_DIR), playlists[choice])
        try:
            PLAYLIST.clear()
            PLAYLIST.update(load_playlist(file_path))
            console.print(f"[success]Playlista '{playlists[choice]}' załadowana pomyślnie![/success]")
            wait_for_enter("Naciśnij Enter, aby kontynuować...")
        except RuntimeError as e:
            logging.error(str(e))
            console.print(f"[error]{str(e)}[/error]")
            wait_for_enter("Naciśnij Enter, aby kontynuować...")

# Funkcja do wyświetlania kanałów w wybranej grupie
def display_channels():
    """Wyświetl kanały w wybranej grupie."""
    global CURRENT_GROUP
    channels = PLAYLIST.get(CURRENT_GROUP, [])
    if not channels:
        console.print("[error]Brak dostępnych kanałów w tej grupie.[/error]")
        wait_for_enter("Naciśnij Enter, aby wrócić...")
        return

    page_size = 20
    total_pages = (len(channels) + page_size - 1) // page_size
    current_page = 0

    while True:
        console.clear()
        draw_header(f"Kanały: {CURRENT_GROUP} (Strona {current_page + 1}/{total_pages})")
        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        table.add_column("Nr", style="dim", width=6)
        table.add_column("Kanał", style="options")
        table.add_column("Teraz", style="highlight")
        table.add_column("Następnie", style="highlight")

        start_idx = current_page * page_size
        end_idx = start_idx + page_size
        for idx, channel in enumerate(channels[start_idx:end_idx], start=1):
            epg_current, epg_next = get_channel_epg(channel['name'])
            current_title = epg_current['title'] if epg_current else "-"
            next_title = epg_next['title'] if epg_next else "-"
            table.add_row(str(idx), channel['name'], current_title, next_title)

        console.print(table)
        console.print(f"[info]Wybierz kanał (1 - {len(channels[start_idx:end_idx])}), 'n' - następna strona, 'p' - poprzednia strona, 'q' - powrót[/info]")
        choice = Prompt.ask("[bold cyan]Twój wybór[/bold cyan]")
        if choice.lower() == 'q':
            break
        elif choice.lower() == 'n':
            if current_page < total_pages - 1:
                current_page += 1
            else:
                console.print("[error]To jest ostatnia strona.[/error]")
                time.sleep(1)
        elif choice.lower() == 'p':
            if current_page > 0:
                current_page -= 1
            else:
                console.print("[error]To jest pierwsza strona.[/error]")
                time.sleep(1)
        elif choice.isdigit():
            num = int(choice)
            if 1 <= num <= len(channels[start_idx:end_idx]):
                channel = channels[start_idx + num - 1]
                play_stream_vlc(channel['url'], channel['name'])
            else:
                console.print("[error]Nieprawidłowy wybór. Spróbuj ponownie.[/error]")
                time.sleep(1)
        else:
            console.print("[error]Nieprawidłowy wybór. Spróbuj ponownie.[/error]")
            time.sleep(1)

# Funkcja do wyszukiwania kanałów
def search_channels():
    """Wyszukaj kanały po nazwie."""
    if not PLAYLIST:
        console.print("[error]Brak załadowanych playlist.[/error]")
        wait_for_enter("Naciśnij Enter, aby wrócić...")
        return

    search_term = Prompt.ask("[bold yellow]Wprowadź nazwę lub fragment nazwy kanału do wyszukania[/bold yellow]").strip()
    if not search_term:
        console.print("[error]Wyszukiwana fraza nie może być pusta.[/error]")
        wait_for_enter("Naciśnij Enter, aby kontynuować...")
        return

    # Utwórz listę wszystkich kanałów
    all_channels = []
    for group, channels in PLAYLIST.items():
        for channel in channels:
            all_channels.append((channel, group))

    # Wyszukaj kanały pasujące do frazy (niezależnie od wielkości liter)
    matching_channels = [(channel, group) for (channel, group) in all_channels if search_term.lower() in channel['name'].lower()]

    if not matching_channels:
        console.print("[error]Nie znaleziono kanałów pasujących do wyszukiwania.[/error]")
        wait_for_enter("Naciśnij Enter, aby kontynuować...")
        return

    page_size = 20
    total_pages = (len(matching_channels) + page_size - 1) // page_size
    current_page = 0

    while True:
        console.clear()
        draw_header(f"Wyniki wyszukiwania dla '{search_term}' (Strona {current_page + 1}/{total_pages})")
        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        table.add_column("Nr", style="dim", width=6)
        table.add_column("Kanał", style="options")
        table.add_column("Grupa", style="options")
        table.add_column("Teraz", style="highlight")
        table.add_column("Następnie", style="highlight")

        start_idx = current_page * page_size
        end_idx = min(start_idx + page_size, len(matching_channels))
        for idx, (channel, group) in enumerate(matching_channels[start_idx:end_idx], start=1):
            epg_current, epg_next = get_channel_epg(channel['name'])
            current_title = epg_current['title'] if epg_current else "-"
            next_title = epg_next['title'] if epg_next else "-"
            table.add_row(str(idx), channel['name'], group, current_title, next_title)

        console.print(table)
        console.print(f"[info]Wybierz kanał (1 - {end_idx - start_idx}), 'n' - następna strona, 'p' - poprzednia strona, 'q' - powrót[/info]")
        choice = Prompt.ask("[bold cyan]Twój wybór[/bold cyan]")
        if choice.lower() == 'q':
            break
        elif choice.lower() == 'n':
            if current_page < total_pages - 1:
                current_page += 1
            else:
                console.print("[error]To jest ostatnia strona.[/error]")
                time.sleep(1)
        elif choice.lower() == 'p':
            if current_page > 0:
                current_page -= 1
            else:
                console.print("[error]To jest pierwsza strona.[/error]")
                time.sleep(1)
        elif choice.isdigit():
            num = int(choice)
            if 1 <= num <= (end_idx - start_idx):
                channel_idx = start_idx + num - 1
                channel, _ = matching_channels[channel_idx]
                play_stream_vlc(channel['url'], channel['name'])
            else:
                console.print("[error]Nieprawidłowy wybór. Spróbuj ponownie.[/error]")
                time.sleep(1)
        else:
            console.print("[error]Nieprawidłowy wybór. Spróbuj ponownie.[/error]")
            time.sleep(1)

# Funkcja do wyświetlania grup kanałów
def display_groups():
    """Wyświetl dostępne grupy kanałów."""
    global CURRENT_GROUP
    if not PLAYLIST:
        console.print("[error]Brak załadowanych playlist.[/error]")
        wait_for_enter("Naciśnij Enter, aby wrócić...")
        return

    groups = sorted([(group, len(channels)) for group, channels in PLAYLIST.items()])
    if not groups:
        console.print("[error]Brak dostępnych grup w playliście.[/error]")
        wait_for_enter("Naciśnij Enter, aby wrócić...")
        return

    options = [f"{group} ({count} kanałów)" for group, count in groups]
    choice = display_menu(options, "Grupy Kanałów")
    if choice is not None:
        CURRENT_GROUP = groups[choice][0]
        display_channels()

# Funkcja do wyświetlania głównego menu
def main_menu():
    """Wyświetl główne menu."""
    options = [
        "Załaduj playlistę z pliku",
        "Wyświetl grupy kanałów",
        "Wyszukaj kanał",
        "Załaduj EPG",  # Opcja ładowania EPG z możliwością wyboru źródła
        "Skonfiguruj EPG",
        "Skonfiguruj proxy",
        "Zarządzaj źródłami proxy",
        "Skonfiguruj ścieżkę do VLC",
        "Wyjdź",
    ]
    while True:
        choice = display_menu(options, "FastIPTV  by Swir")
        if choice == 0:
            load_playlist_from_file()
        elif choice == 1:
            display_groups()
        elif choice == 2:
            search_channels()
        elif choice == 3:
            load_epg()  # Opcja ładowania EPG
            wait_for_enter("Naciśnij Enter, aby kontynuować...")
        elif choice == 4:
            configure_epg_sources()
        elif choice == 5:
            configure_proxy()
        elif choice == 6:
            configure_proxy_sources()
        elif choice == 7:
            configure_vlc_path()
        elif choice is None or choice == 8:
            console.print("[success]Dziękujemy za korzystanie z programu IPTV Player. Do zobaczenia![/success]")
            break

# Pozostałe funkcje (configure_proxy, configure_proxy_sources, play_stream_vlc, itd.) pozostają bez zmian

# Funkcja do konfiguracji proxy
def configure_proxy():
    """Konfiguracja proxy dla VLC."""
    global PROXY_URL
    while True:
        sources = list(AVAILABLE_PROXY_SOURCES.keys())
        options = sources + ["Wprowadź proxy ręcznie", "Wyłącz proxy", "Sprawdź moje IP", "Powrót"]
        choice = display_menu(options, "Konfiguracja Proxy")
        if choice is None or choice == len(options) - 1:  # Opcja "Powrót"
            console.print("[info]Powrót do menu głównego.[/info]")
            break
        elif choice == len(options) - 4:  # Opcja "Wprowadź proxy ręcznie"
            while True:
                proxy = Prompt.ask("[bold yellow]Podaj adres proxy (IP:PORT) lub 'q' aby wrócić[/bold yellow]")
                if proxy.lower() == 'q':
                    break
                if ":" in proxy:
                    ip_port = proxy.split(":")
                    if len(ip_port) == 2 and test_proxy_quick({"ip": ip_port[0], "port": ip_port[1]}):
                        if test_proxy(proxy):
                            PROXY_URL = proxy
                            console.print(f"[success]Ustawiono proxy: {PROXY_URL}[/success]")
                            wait_for_enter("Naciśnij Enter, aby kontynuować...")
                            return
                        else:
                            console.print("[error]Podane proxy nie działa poprawnie. Spróbuj inne.[/error]")
                    else:
                        console.print("[error]Podane proxy ma nieprawidłowy format lub nie działa. Spróbuj ponownie.[/error]")
                else:
                    console.print("[error]Podane proxy ma nieprawidłowy format. Użyj IP:PORT[/error]")
        elif choice == len(options) - 3:  # Opcja "Wyłącz proxy"
            PROXY_URL = None
            console.print("[success]Proxy zostało wyłączone.[/success]")
            wait_for_enter("Naciśnij Enter, aby kontynuować...")
            break
        elif choice == len(options) - 2:  # Opcja "Sprawdź moje IP"
            check_my_ip()
            wait_for_enter("Naciśnij Enter, aby kontynuować...")
        else:
            selected_source = sources[choice]
            console.print(f"[info]Pobieranie proxy ze źródła: {selected_source}...[/info]")

            proxies = fetch_proxies(selected_source)
            if proxies:
                tested_proxies = test_proxies(proxies)
                if any(is_working for _, is_working, _ in tested_proxies):
                    select_working_proxy(tested_proxies)
                    break
                else:
                    console.print("[error]Nie znaleziono działających proxy. Spróbuj ponownie później.[/error]")
                    wait_for_enter("Naciśnij Enter, aby wrócić...")
            else:
                console.print("[error]Nie udało się pobrać listy proxy.[/error]")
                wait_for_enter("Naciśnij Enter, aby wrócić...")

# Funkcja do zarządzania źródłami proxy
def configure_proxy_sources():
    """Zarządzaj źródłami proxy (włącz/wyłącz/dodaj własne)."""
    global ENABLED_PROXY_SOURCES, AVAILABLE_PROXY_SOURCES
    while True:
        # Usuń nieistniejące źródła z ENABLED_PROXY_SOURCES
        ENABLED_PROXY_SOURCES = [source for source in ENABLED_PROXY_SOURCES if source in AVAILABLE_PROXY_SOURCES]
        options = [f"{'[X]' if source in ENABLED_PROXY_SOURCES else '[ ]'} {source}" for source in AVAILABLE_PROXY_SOURCES.keys()]
        options.extend(["Dodaj własne źródło", "Usuń własne źródło", "Zapisz i powrót"])
        choice = display_menu(options, "Zarządzanie źródłami proxy")
        if choice is None or choice == len(options) - 1:
            save_config()
            console.print("[success]Zapisano zmiany w źródłach proxy.[/success]")
            wait_for_enter("Naciśnij Enter, aby powrócić do menu głównego...")
            break
        elif choice == len(options) - 3:
            add_custom_proxy_source()
        elif choice == len(options) - 2:
            remove_custom_proxy_source()
        else:
            selected_source = list(AVAILABLE_PROXY_SOURCES.keys())[choice]
            if selected_source in ENABLED_PROXY_SOURCES:
                ENABLED_PROXY_SOURCES.remove(selected_source)
            else:
                ENABLED_PROXY_SOURCES.append(selected_source)
            console.print(f"[info]Źródło '{selected_source}' {'włączone' if selected_source in ENABLED_PROXY_SOURCES else 'wyłączone'}.[/info]")
            wait_for_enter("Naciśnij Enter, aby kontynuować...")

# Funkcja do dodawania własnego źródła proxy
def add_custom_proxy_source():
    """Dodaj własne źródło proxy."""
    global AVAILABLE_PROXY_SOURCES, ENABLED_PROXY_SOURCES
    name = Prompt.ask("[bold yellow]Podaj nazwę dla nowego źródła proxy[/bold yellow]").strip()
    url = Prompt.ask("[bold yellow]Podaj URL API nowego źródła proxy[/bold yellow]").strip()
    if name and url:
        if name in AVAILABLE_PROXY_SOURCES:
            console.print("[error]Źródło o tej nazwie już istnieje.[/error]")
        else:
            AVAILABLE_PROXY_SOURCES[name] = url
            ENABLED_PROXY_SOURCES.append(name)
            console.print(f"[success]Dodano nowe źródło proxy: {name}[/success]")
    else:
        console.print("[error]Nazwa i URL nie mogą być puste.[/error]")

# Funkcja do usuwania własnego źródła proxy
def remove_custom_proxy_source():
    """Usuń własne źródło proxy."""
    global AVAILABLE_PROXY_SOURCES, ENABLED_PROXY_SOURCES
    custom_sources = [src for src in AVAILABLE_PROXY_SOURCES.keys() if src not in DEFAULT_PROXY_SOURCES]
    if not custom_sources:
        console.print("[error]Brak własnych źródeł do usunięcia.[/error]")
        wait_for_enter("Naciśnij Enter, aby kontynuować...")
        return
    options = custom_sources + ["Anuluj"]
    choice = display_menu(options, "Usuń własne źródło")
    if choice is not None and choice < len(custom_sources):
        source_to_remove = custom_sources[choice]
        AVAILABLE_PROXY_SOURCES.pop(source_to_remove)
        if source_to_remove in ENABLED_PROXY_SOURCES:
            ENABLED_PROXY_SOURCES.remove(source_to_remove)
        console.print(f"[success]Usunięto źródło proxy: {source_to_remove}[/success]")
    else:
        console.print("[info]Anulowano usuwanie źródła.[/info]")

# Funkcja do pobierania proxy
def fetch_proxies(source_name):
    """Pobierz listę proxy z wybranego źródła."""
    proxies = []
    if source_name not in AVAILABLE_PROXY_SOURCES:
        logging.warning(f"Źródło proxy '{source_name}' nie jest dostępne.")
        return proxies

    api_url = AVAILABLE_PROXY_SOURCES[source_name]
    try:
        response = requests.get(api_url, timeout=10)
        logging.debug(f"URL: {response.url}")
        logging.debug(f"Status code: {response.status_code}")
        logging.debug(f"Response text: {response.text[:200]}")  # Wyświetl pierwsze 200 znaków odpowiedzi

        if response.status_code == 200:
            data = response.text
            proxies.extend(parse_proxy_data(api_url, data, source_name))
        else:
            logging.warning(f"Błąd pobierania proxy z {source_name}: Status {response.status_code}")
    except Exception as e:
        logging.warning(f"Błąd pobierania proxy z {source_name}: {e}")
    return proxies

# Funkcja do przetwarzania danych proxy
def parse_proxy_data(api_url, data, source_name):
    """Przetwórz dane proxy."""
    proxies = []
    try:
        if "geonode" in api_url.lower():
            json_data = json.loads(data)
            for item in json_data.get("data", []):
                proxy = {
                    "ip": item["ip"],
                    "port": item["port"],
                    "country": item.get("country"),
                    "country_code": item.get("country_code")
                }
                proxies.append(proxy)
        else:
            lines = data.strip().splitlines()
            for line in lines:
                if ":" in line:
                    ip, port = line.split(":")
                    proxy = {"ip": ip.strip(), "port": port.strip(), "country": None, "country_code": None}
                    proxies.append(proxy)
    except Exception as e:
        logging.error(f"Błąd przetwarzania danych z {source_name}: {e}")
    return proxies

# Funkcja do testowania listy proxy z użyciem Rich Progress
def test_proxies(proxies):
    """Przetestuj listę proxy, zmierz ich prędkość i zwróć ich status."""
    results = []
    total = len(proxies)

    console.print(f"[info]Testowanie {total} proxy...[/info]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Testowanie proxy", total=total)
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(test_proxy_with_latency, proxy): proxy for proxy in proxies}
            for future in as_completed(futures):
                proxy = futures[future]
                try:
                    is_working, latency, country_code = future.result()
                    proxy['country_code'] = country_code or proxy.get('country_code')
                    results.append((proxy, is_working, latency))
                except Exception as e:
                    logging.warning(f"Błąd testowania proxy {proxy}: {e}")
                    results.append((proxy, False, None))
                progress.update(task, advance=1)
    return results

# Funkcja do testowania proxy z pomiarem latencji
def test_proxy_with_latency(proxy):
    """Sprawdź, czy proxy działa i zmierz jego latencję."""
    proxy_url = f"{proxy['ip']}:{proxy['port']}"
    try:
        proxies = {
            "http": f"http://{proxy_url}",
            "https": f"http://{proxy_url}",
        }
        start_time = time.time()
        response = requests.get("http://ip-api.com/json", proxies=proxies, timeout=5)
        latency = time.time() - start_time
        if response.status_code == 200:
            data = response.json()
            country_code = data.get("countryCode")
            return True, latency, country_code
    except requests.exceptions.RequestException:
        pass
    return False, None, None

# Funkcja do testowania połączenia przez proxy
def test_proxy(proxy_url):
    """Testuj połączenie przez ustawione proxy."""
    try:
        proxies = {
            "http": f"http://{proxy_url}",
            "https": f"http://{proxy_url}",
        }
        response = requests.get("http://ip-api.com/json", proxies=proxies, timeout=10)
        if response.status_code == 200:
            data = response.json()
            country = data.get("country", "Nieznany")
            ip = data.get("query", "Nieznany")
            console.print(f"[success]Proxy działa! Twój adres IP: {ip} (Kraj: {country})[/success]")
            return True
        else:
            console.print("[error]Nie udało się połączyć przez proxy.[/error]")
            return False
    except Exception as e:
        logging.error(f"Błąd podczas testowania proxy: {e}")
        console.print(f"[error]Błąd podczas testowania proxy: {e}[/error]")
        return False

# Funkcja do szybkiego testowania proxy (bez pomiaru latencji)
def test_proxy_quick(proxy):
    """Szybko sprawdź, czy proxy działa."""
    proxy_url = f"{proxy['ip']}:{proxy['port']}"
    try:
        proxies = {
            "http": f"http://{proxy_url}",
            "https": f"http://{proxy_url}",
        }
        response = requests.get("http://www.google.com", proxies=proxies, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# Funkcja do wyboru działającego proxy
def select_working_proxy(tested_proxies):
    """Pozwól użytkownikowi wybrać działające proxy i upewnij się, że działa."""
    global PROXY_URL
    working_proxies = [(proxy, latency) for proxy, is_working, latency in tested_proxies if is_working]
    if not working_proxies:
        console.print("[error]Brak działających proxy do wyświetlenia.[/error]")
        wait_for_enter("Naciśnij Enter, aby kontynuować...")
        return

    while True:
        options = []
        for idx, (proxy, latency) in enumerate(working_proxies):
            country_code = proxy.get("country_code", "??")
            proxy_str = f"{proxy['ip']}:{proxy['port']} ({country_code}) - {latency*1000:.0f} ms"
            options.append(proxy_str)
            if len(options) >= 50:  # Ograniczenie do 50 działających proxy
                break

        if not options:
            console.print("[error]Brak działających proxy do wyświetlenia.[/error]")
            wait_for_enter("Naciśnij Enter, aby kontynuować...")
            return

        choice = display_menu(options, "Wybierz Proxy")
        if choice is not None:
            selected_proxy = working_proxies[choice][0]
            proxy_url = f"{selected_proxy['ip']}:{selected_proxy['port']}"
            console.print(f"[info]Testowanie wybranego proxy: {proxy_url}...[/info]")
            if test_proxy(proxy_url):
                PROXY_URL = proxy_url
                console.print(f"[success]Ustawiono proxy: {PROXY_URL}[/success]")
                wait_for_enter("Naciśnij Enter, aby kontynuować...")
                return
            else:
                console.print("[error]Wybrane proxy nie działa poprawnie. Wybierz inne.[/error]")
                # Usuń niedziałające proxy z listy
                working_proxies.pop(choice)
                if not working_proxies:
                    console.print("[error]Brak pozostałych działających proxy do wybrania.[/error]")
                    wait_for_enter("Naciśnij Enter, aby kontynuować...")
                    return
        else:
            console.print("[info]Nie wybrano proxy.[/info]")
            return

# Funkcja do sprawdzania aktualnego adresu IP
def check_my_ip():
    """Sprawdź aktualny adres IP."""
    try:
        proxies = None
        if PROXY_URL:
            proxies = {
                "http": f"http://{PROXY_URL}",
                "https": f"http://{PROXY_URL}",
            }
        response = requests.get("http://ip-api.com/json", proxies=proxies, timeout=10)
        if response.status_code == 200:
            data = response.json()
            ip = data.get("query", "Nieznany")
            country = data.get("country", "Nieznany")
            console.print(f"[success]Twój aktualny adres IP: {ip} (Kraj: {country})[/success]")
        else:
            console.print("[error]Nie udało się pobrać adresu IP.[/error]")
    except Exception as e:
        logging.error(f"Błąd podczas sprawdzania IP: {e}")
        console.print(f"[error]Błąd podczas sprawdzania IP: {e}[/error]")

# Funkcja do odtwarzania strumienia za pomocą VLC
def play_stream_vlc(url, channel_name):
    """Odtwórz strumień za pomocą zewnętrznej aplikacji VLC."""
    console.print(f"[info]Odtwarzanie kanału: [bold]{channel_name}[/bold][/info]")
    try:
        global VLC_PATH
        if VLC_PATH is None:
            VLC_PATH = get_vlc_path()
            if VLC_PATH is None:
                console.print("[error]Nie znaleziono aplikacji VLC Media Player.[/error]")
                wait_for_enter("Upewnij się, że VLC jest zainstalowany. Naciśnij Enter, aby kontynuować...")
                return
            else:
                save_config()

        if not os.path.exists(VLC_PATH):
            console.print("[error]Ścieżka do VLC jest nieprawidłowa.[/error]")
            configure_vlc_path()
            if VLC_PATH is None:
                return

        vlc_command = [VLC_PATH, url]
        if PROXY_URL:
            vlc_command.extend(["--http-proxy", PROXY_URL])
        # Uruchom VLC jako nowy proces
        subprocess.run(vlc_command)
    except Exception as e:
        logging.error(f"Błąd podczas uruchamiania VLC: {e}")
        console.print(f"[error]Błąd podczas uruchamiania VLC: {e}[/error]")
        wait_for_enter("Naciśnij Enter, aby kontynuować...")

# Funkcja do znajdowania ścieżki do VLC
def get_vlc_path():
    """Próbuj znaleźć plik wykonywalny VLC w standardowych lokalizacjach."""
    possible_paths = [
        r"C:\Program Files\VideoLAN\VLC\vlc.exe",
        r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
        r"/usr/bin/vlc",
        r"/usr/local/bin/vlc",
        r"/Applications/VLC.app/Contents/MacOS/VLC",
        # Dodaj inne potencjalne ścieżki, jeśli to konieczne
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

# Funkcja do konfiguracji ścieżki do VLC
def configure_vlc_path():
    """Pozwól użytkownikowi ustawić ścieżkę do VLC."""
    global VLC_PATH
    while True:
        vlc_path = Prompt.ask("[bold yellow]Podaj pełną ścieżkę do pliku VLC lub 'q' aby anulować[/bold yellow]")
        if vlc_path.lower() == 'q':
            break
        if os.path.exists(vlc_path):
            VLC_PATH = vlc_path
            console.print(f"[success]Ustawiono ścieżkę do VLC: {VLC_PATH}[/success]")
            save_config()
            wait_for_enter("Naciśnij Enter, aby kontynuować...")
            break
        else:
            console.print("[error]Podana ścieżka jest nieprawidłowa. Spróbuj ponownie.[/error]")

# Funkcja do rysowania nagłówka z logo
def draw_header(title):
    """Wyświetl nagłówek z logo za pomocą Rich."""
    logo = r"""
      _____   ___       ___    _____   ______     ________   __    __   ________    _____     ____       __    __    
     / ____\ (  (       )  )  (_   _) (   __ \   (___  ___)  ) )  ( (  (___  ___)  / ___/    (    )      \ \  / /    
    ( (___    \  \  _  /  /     | |    ) (__) )      ) )    ( (    ) )     ) )    ( (__      / /\ \      () \/ ()    
     \___ \    \  \/ \/  /      | |   (    __/      ( (      \ \  / /     ( (      ) __)    ( (__) )     / _  _ \    
         ) )    )   _   (       | |    ) \ \  _      ) )      \ \/ /       ) )    ( (        )    (     / / \/ \ \   
     ___/ /     \  ( )  /      _| |__ ( ( \ \_))    ( (        \  /       ( (      \ \___   /  /\  \   /_/      \_\  
    /____/       \_/ \_/      /_____(  )_) \__/     /__\        \/        /__\      \____\ /__(  )__\ (/          \) 
                                                                                                                     
    
    
    """
    header_text = Text(logo + "\n" + title, justify="center", style="title")
    header = Panel(header_text, style="bold green", expand=True, box=box.DOUBLE)
    console.print(header)

# Funkcja do oczekiwania na wciśnięcie Enter
def wait_for_enter(prompt):
    """Poczekaj na wciśnięcie Enter."""
    console.print(f"[bold white]{prompt}[/bold white]")
    Prompt.ask("", default="", show_default=False)

# Funkcja do wyświetlania menu
def display_menu(options, title="Menu"):
    """Wyświetl menu za pomocą Rich i pobierz wybór użytkownika."""
    while True:
        console.clear()
        draw_header(title)
        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        table.add_column("Nr", style="dim", width=6)
        table.add_column("Opcja", style="options")

        for idx, option in enumerate(options, start=1):
            table.add_row(str(idx), option)

        console.print(table)
        console.print(f"[info]Wybierz opcję (1 - {len(options)}), lub 'q' aby wrócić.[/info]")
        choice = Prompt.ask("[bold cyan]Twój wybór[/bold cyan]")
        if choice.lower() == 'q':
            return None
        elif choice.isdigit():
            num = int(choice)
            if 1 <= num <= len(options):
                return num - 1
            else:
                console.print("[error]Nieprawidłowy wybór. Spróbuj ponownie.[/error]")
                time.sleep(1)
        else:
            console.print("[error]Nieprawidłowy wybór. Spróbuj ponownie.[/error]")
            time.sleep(1)

# Funkcja do wyszukiwania playlist w folderze
def list_playlists(directory=None):
    """Wyszukaj wszystkie playlisty M3U w podanym folderze."""
    if directory is None:
        directory = resource_path(PLAYLISTS_DIR)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return [f for f in os.listdir(directory) if f.endswith(".m3u")]

# Załaduj konfigurację przy starcie (bez ładowania EPG)
load_config()

if __name__ == "__main__":
    try:
        main_menu()
    except Exception as e:
        logging.exception("Wystąpił błąd")
        console.print(f"[error]Wystąpił błąd: {e}. Szczegóły zapisano do pliku 'error.log'.[/error]")
        wait_for_enter("Naciśnij Enter, aby zakończyć...")
