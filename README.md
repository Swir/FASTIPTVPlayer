# FastIPTV by Swir

## Spis Treści / Table of Contents
- [Opis Projektu / Project Description](#opis-projektu-project-description)
- [Funkcje / Features](#funkcje-features)
- [Wymagania / Requirements](#wymagania-requirements)
- [Instalacja / Installation](#instalacja-installation)
- [Użytkowanie / Usage](#użytkowanie-usage)
- [Konfiguracja / Configuration](#konfiguracja-configuration)
  - [Konfiguracja Proxy / Proxy Configuration](#konfiguracja-proxy-proxy-configuration)
  - [Konfiguracja EPG / EPG Configuration](#konfiguracja-epg-epg-configuration)
- [Dodawanie Playlist / Adding Playlists](#dodawanie-playlist-adding-playlists)
- [Rozwiązywanie Problemów / Troubleshooting](#rozwiązywanie-problemów-troubleshooting)
- [Wkład / Contribution](#wkład-contribution)
- [Licencja / License](#licencja-license)

## Opis Projektu / Project Description

FastIPTV to prosty i intuicyjny odtwarzacz IPTV, który umożliwia użytkownikom łatwe zarządzanie i oglądanie kanałów telewizyjnych za pomocą VLC Media Player. Program obsługuje pliki playlist M3U, konfigurację proxy oraz dane EPG (Elektroniczny Przewodnik Programów).

FastIPTV is a simple and intuitive IPTV player that allows users to easily manage and watch TV channels using VLC Media Player. The program supports M3U playlist files, proxy configuration, and EPG (Electronic Program Guide) data.

## Funkcje / Features

- Ładowanie playlist z folderu `playlists`
- Wyszukiwanie kanałów
- Przeglądanie kanałów według grup
- Integracja z VLC Media Player
- Konfiguracja proxy z wieloma źródłami
- Pobieranie i przetwarzanie danych EPG
- Przyjazny interfejs użytkownika z Rich
- Logowanie błędów do pliku `error.log`

- Load playlists from the `playlists` folder
- Search channels
- Browse channels by groups
- Integration with VLC Media Player
- Proxy configuration with multiple sources
- Downloading and processing EPG data
- User-friendly interface with Rich
- Error logging to `error.log`

## Wymagania / Requirements

- Python 3.7+
- VLC Media Player zainstalowany na systemie
- Biblioteki Python:
  - `rich`
  - `requests`
  - `concurrent.futures`

- Python 3.7+
- VLC Media Player installed on the system
- Python libraries:
  - `rich`
  - `requests`
  - `concurrent.futures`

## Instalacja / Installation

1. **Sklonuj repozytorium:**

    ```bash
    git clone  https://github.com/swir/FastIPTVplayer.git
    cd FastIPTV
    ```

    **Clone the repository:**

    ```bash
    git clone https://github.com/swir/FastIPTVplayer.git
    cd FastIPTV
    ```

2. **Utwórz i aktywuj wirtualne środowisko (opcjonalnie):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # na Linux/Mac
    venv\Scripts\activate     # na Windows
    ```

    **Create and activate a virtual environment (optional):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # on Linux/Mac
    venv\Scripts\activate     # on Windows
    ```

3. **Zainstaluj wymagane biblioteki:**

    ```bash
    pip install -r requirements.txt
    ```

    **Install the required libraries:**

    ```bash
    pip install -r requirements.txt
    ```

Konfiguracja / Configuration
Konfiguracja Proxy / Proxy Configuration

    W menu głównym wybierz opcję "Skonfiguruj proxy".

    Możesz wybrać jedno z dostępnych źródeł proxy lub wprowadzić własne ręcznie.

    Po wybraniu działającego proxy, program automatycznie skonfiguruje VLC do korzystania z niego.

    From the main menu, select "Configure Proxy".

    Choose from the available proxy sources or enter your own manually.

    After selecting a working proxy, the program will automatically configure VLC to use it.

Konfiguracja EPG / EPG Configuration

    W menu głównym wybierz opcję "Skonfiguruj EPG".

    Dodaj lub usuń źródła EPG.

    Aby załadować EPG, wybierz opcję "Załaduj EPG" i wybierz źródło z listy.

    From the main menu, select "Configure EPG".

    Add or remove EPG sources.

    To load EPG, select "Load EPG" and choose a source from the list.

Dodawanie Playlist / Adding Playlists

    Umieść pliki .m3u w folderze playlists.

    Uruchom program i wybierz opcję "Załaduj playlistę z pliku".

    Wybierz playlistę z listy dostępnych.

    Place .m3u files in the playlists folder.

    Run the program and select "Load playlist from file".

    Choose the playlist from the list of available playlists.

Rozwiązywanie Problemów / Troubleshooting

    Brak VLC: Upewnij się, że VLC Media Player jest zainstalowany i skonfiguruj jego ścieżkę w opcjach programu.

    Błędy w error.log: Sprawdź plik error.log w katalogu programu, aby znaleźć szczegóły błędów.

    VLC not found: Ensure that VLC Media Player is installed and configure its path in the program options.

    Errors in error.log: Check the error.log file in the program directory for error details.

Wkład / Contribution

Jeśli chcesz pomóc w rozwoju projektu, otwórz issue lub stwórz pull request.

If you want to help develop the project, open an issue or create a pull request.
