# Web Scraper Projekt für Kleinanzeigen.de

Dieses Projekt enthält zwei Python-Skripte für das Web Scraping mit Playwright: `multi_scraper.py` und `target_scraper.py`. Diese Skripte sind speziell dafür entwickelt, um Daten von Kleinanzeigen.de automatisch zu extrahieren.

## Funktionen

- Asynchrones Web Scraping mit Playwright.
- Unterstützung für Logging und Threading.
- URL-Generierung und Extraktionsfunktionen.
- Detailliertes Logging der Scraping-Aktivitäten.

## Anforderungen

- Python 3.7 oder höher
- Playwright
- Tqdm

## Installation

1. Klone das Repository:
    ```sh
    git clone https://github.com/yourusername/web-scraper.git
    cd web-scraper
    ```

2. Installiere die benötigten Pakete:
    ```sh
    pip install -r requirements.txt
    ```

3. Installiere Playwright und dessen Browser-Abhängigkeiten:
    ```sh
    playwright install
    ```

## Verwendung

### multi_scraper.py

Dieses Skript generiert mehrere URLs basierend auf der angegebenen ersten und zweiten URL und scrapt Daten von diesen URLs auf Kleinanzeigen.de.

#### Ausführen des Skripts

```sh
python multi_scraper.py
