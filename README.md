# Web Scraper Projekt für Kleinanzeigen.de

Dieses Projekt enthält zwei Python-Skripte für das Web Scraping von Kleinanzeigen.de mit Playwright: `multi_scraper.py` und `target_scraper.py`. 

## multi_scraper.py

Dieses Skript ermöglicht das Scrapen mehrerer Seiten von Kleinanzeigen.de basierend auf den vom Benutzer angegebenen URLs für die erste und zweite Seite sowie der Anzahl der zu scrapenden Seiten.

### Funktionen
- Generiert URLs für die angegebene Anzahl von Seiten basierend auf den URLs der ersten beiden Seiten.
- Scrapt Daten wie Titel, Link, Preis, Standort und Erstellungsdatum von den generierten URLs.
- Berechnet Preisstatistiken wie Durchschnittspreis, Höchstpreis, Niedrigstpreis, Anzahl der Artikel mit Preis, Anzahl der Angebote mit verhandelbaren Preisen und Gesamtzahl der Angebote.
- Speichert die gescrapten Daten in einer JSON-Datei und die Statistiken in einer Textdatei.
- Zeigt eine Zusammenfassung der Scraping-Ergebnisse an.

### Verwendung
1. Führen Sie das Skript aus: `python multi_scraper.py`
2. Geben Sie die URL für Seite 1 ein, wenn Sie dazu aufgefordert werden.
3. Geben Sie die URL für Seite 2 ein, wenn Sie dazu aufgefordert werden.
4. Geben Sie die Anzahl der zu scrapenden Seiten ein, wenn Sie dazu aufgefordert werden.
5. Das Skript wird die Daten scrapen und die Ergebnisse in entsprechenden Dateien speichern.

## target_scraper.py

Dieses Skript liest eine JSON-Datei mit Produktlinks ein und scrapt detaillierte Informationen von den jeweiligen Produktseiten auf Kleinanzeigen.de.

### Funktionen
- Liest eine JSON-Datei mit Produktlinks ein.
- Ermöglicht dem Benutzer, die Anzahl der zu scrapenden Links anzugeben.
- Scrapt detaillierte Produktinformationen wie Titel, Preis, Beschreibung, Standort, Erstellungsdatum und Benutzernamen des Verkäufers von den Produktseiten.
- Aktualisiert die ursprüngliche JSON-Datei mit den gescrapten detaillierten Produktinformationen.

### Verwendung
1. Führen Sie das Skript aus: `python target_scraper.py`
2. Geben Sie den Pfad zur JSON-Datei mit den Produktlinks ein, wenn Sie dazu aufgefordert werden.
3. Geben Sie die Anzahl der zu scrapenden Links ein oder geben Sie 'max' ein, um alle Links zu scrapen.
4. Das Skript wird die detaillierten Produktinformationen scrapen und die ursprüngliche JSON-Datei mit den aktualisierten Daten überschreiben.

## Anforderungen
- Python 3.7 oder höher
- Playwright
- tqdm

## Installation
1. Klonen Sie das Repository: `git clone https://github.com/infynnity/kleinanzeigen-scraper-python-playwright-2024.git`
2. Navigieren Sie in das Projektverzeichnis: `cd kleinanzeigen-scraper-python-playwright-2024`
3. Installieren Sie die erforderlichen Pakete: `pip install -r requirements.txt`
4. Installieren Sie Playwright und die zugehörigen Browser: `playwright install`

## Hinweise
- Stellen Sie sicher, dass Sie die Scraping-Aktivitäten auf ein angemessenes Maß beschränken und die Nutzungsbedingungen von Kleinanzeigen.de einhalten.
- Die Skripte enthalten Verzögerungen zwischen den Anfragen, um eine übermäßige Belastung des Servers zu vermeiden. Passen Sie die Verzögerungen nach Bedarf an.
- Die gescrapten Daten werden in JSON- und Textdateien im selben Verzeichnis wie die Skripte gespeichert.

Bei Fragen oder Problemen können Sie gerne ein Issue in diesem Repository eröffnen.
