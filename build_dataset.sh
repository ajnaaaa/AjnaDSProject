#!/bin/bash
set -e  # Abbruch bei erstem Fehler

echo "🚀 Starte Datensammlung..."

python src/scripts/get_capitals.py           # einmalig — capitals.json erzeugen
python src/scripts/get_artists_list.py       # artists.py + artists_list.csv
python src/scripts/collect_artists_lastfm.py # Last.fm Metriken
python src/scripts/collect_ticketmaster.py   # Ticketmaster Events
python src/scripts/collect_toptracks.py      # Last.fm Top-Tracks (für F2)
python src/scripts/join_data.py              # alles zusammenführen → final_dataset.csv

echo "✅ Fertig!"
