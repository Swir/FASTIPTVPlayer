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
    git clone https://github.com/TwojeRepozytorium/FastIPTV.git
    cd FastIPTV
    ```

    **Clone the repository:**

    ```bash
    git clone https://github.com/YourRepository/FastIPTV.git
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

## Użytkowanie / Usage

Uruchom program za pomocą Pythona:

```bash
python main.py
