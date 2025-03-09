# Willys Erbjudanden Scraper

Detta script scrapar erbjudanden från Willys e-handel och sparar dem i en markdown-fil.

## Förutsättningar

- Python 3.7 eller senare
- Google Chrome webbläsare installerad
- pip (Python pakethanterare)

## Installation

1. Klona eller ladda ner detta repository
2. Installera de nödvändiga paketen genom att köra:
```bash
pip install -r requirements.txt
```

## Användning

Kör scriptet genom att använda följande kommando:
```bash
python scrape_willys.py
```

Scriptet kommer att:
1. Öppna Willys erbjudandesida i en headless Chrome-webbläsare
2. Scrolla automatiskt genom sidan och klicka på "Visa mer" för att ladda alla erbjudanden
3. Extrahera information om alla produkter med erbjudanden
4. Spara resultaten i en markdown-fil med dagens datum (format: willys_erbjudanden_ÅÅÅÅ-MM-DD.md)

## Output

Scriptet genererar en markdown-fil som innehåller:
- Produktnamn
- Aktuellt pris
- Jämförpris (om tillgängligt)

## Felsökning

Om du stöter på problem:
1. Kontrollera att du har den senaste versionen av Chrome installerad
2. Kontrollera att alla paket är korrekt installerade
3. Om scriptet fastnar, kan du behöva justera värdena för `time.sleep()` i koden 