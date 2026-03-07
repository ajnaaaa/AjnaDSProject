#!/bin/bash
set -e  # Abbruch bei erstem Fehler

echo "🚀 Starte Datensammlung..."

python src/scripts/get_capitals.py           # einmalig — capitals.json erzeugen
python src/scripts/get_artists_list.py       # artists.py + artists_list.csv
python src/scripts/collect_artists_lastfm.py # Last.fm Metriken
python src/scripts/collect_ticketmaster.py   # Ticketmaster Events
python src/scripts/collect_toptracks.py      # Last.fm Top-Tracks (für F2)
python src/scripts/process_spotify_charts.py # Spotify Charts → chart_artists.csv (für F3)
python src/scripts/join_data.py              # alles zusammenführen → final_dataset.csv

python src/research_question_analyses/analyse_f1_correlation.py
python src/research_question_analyses/analyse_f2_concentration_events.py
python src/research_question_analyses/analyse_f3.py
python src/research_question_analyses/analyse_f4_revisit_cities.py
python src/research_question_analyses/analyse_f5_geo_align.py
python src/research_question_analyses/analyse_f6_capital_ratio.py

echo "✅ Fertig!"
