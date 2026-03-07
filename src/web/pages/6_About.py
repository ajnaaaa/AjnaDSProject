import streamlit as st

from components.styles import apply_styles
from components.navbar import render_navbar
from components.glossary import apply_glossary_styles, tt

st.set_page_config(
    page_title="About Us — From Streams to Stages",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="collapsed",
)
apply_styles()
render_navbar()
apply_glossary_styles()

st.markdown("""
<div class="page-header">
    <h1>👥 About Us</h1>
    <p>Wer steckt hinter diesem Projekt?</p>
</div>
""", unsafe_allow_html=True)

# ── Projekt-Beschreibung ───────────────────────────────────────────────────
st.markdown("""
<div style="
    background: #161c2d;
    border: 1px solid #232840;
    border-radius: 16px;
    padding: 40px 48px;
    margin-bottom: 32px;
    max-width: 860px;
">
    <h2 style="color:#818cf8 !important; font-size:1.4rem; margin:0 0 20px 0;">
        Ein Data-Science-Projekt im 5. Semester
    </h2>
    <p style="color:#cbd5e1 !important; font-size:1.05rem; line-height:1.8; margin:0 0 20px 0;">
        Wir sind vier Studierende der Informatik und Wirtschaftsinformatik an der
        <strong style="color:#f1f5f9 !important;">Christian-Albrechts-Universitaet zu Kiel</strong>
        und haben dieses Projekt im Rahmen des Data-Science-Praktikums im fuenften Semester entwickelt.
    </p>
    <p style="color:#cbd5e1 !important; font-size:1.05rem; line-height:1.8; margin:0 0 20px 0;">
        Die Frage, die uns von Anfang an angetrieben hat, klingt einfach —
        ist es aber nicht: <em style="color:#818cf8 !important;">Laesst sich aus digitalen Streaming-Daten
        voraussagen, wie und wo Kuenstler auf Tour gehen?</em> Mit anderen Worten: Spiegeln
        die Zahlen, die Millionen von Nutzern taglich auf Last.fm und Spotify erzeugen,
        tatsaechlich die physische Realitaet von Konzerttourneen wider?
    </p>
    <p style="color:#cbd5e1 !important; font-size:1.05rem; line-height:1.8; margin:0;">
        Dieses Thema liegt uns persoenlich am Herzen — wir alle hoeren viel Musik,
        besuchen regelmaessig Konzerte und haben uns oft gefragt, warum manche
        Kuenstler bestimmte Staedte bevorzugen, waehrend andere scheinbar an
        ihren groessten Fanmaerkten vorbeizuziehen scheinen. Dieses Projekt ist
        unser Versuch, dieser Frage mit echten Daten auf den Grund zu gehen.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Datenquellen ───────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📡 Verwendete Datenquellen</div>', unsafe_allow_html=True)

sources = [
    {"icon": "🎧", "name": "Last.fm API", "desc": "Listener-Zahlen, Playcounts, Top Tracks, Geo-Popularitaet pro Land"},
    {"icon": "🎟️", "name": "Ticketmaster API", "desc": "Konzertdaten: Staedte, Laender, Datum, Hauptstadt-Status (2022–2026)"},
    {"icon": "🌍", "name": "RestCountries API", "desc": "Hauptstaedte aller Laender fuer die Kapital-Analyse (F6)"},
    {"icon": "🗺️", "name": "Spotify Chart Data",
     "desc": "Wochentliche Chart-Daten Feb 2023–Feb 2026 fuer Chart-Artist-Klassifizierung (F3)"},
]

s_cols = st.columns(2)
for i, src in enumerate(sources):
    with s_cols[i % 2]:
        st.markdown(f"""
        <div class="insight-card" style="margin-bottom:12px;">
            <h4>{src['icon']} {src['name']}</h4>
            <p>{src['desc']}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Hinweis Spotify ────────────────────────────────────────────────────────
st.markdown("""
<div class="methodology-note">
    <p>
    <strong>Hinweis zur Datenerhebung:</strong>
    Urspruenglich war die Nutzung der Spotify Web API geplant (Followers, Popularity Score).
    Aufgrund von API-Einschraenkungen im Februar 2026, die diese Felder im Development Mode entfernten,
    wurden <strong>Last.fm Listener-Zahlen und Playcounts</strong> als gleichwertige
    Popularitaets-Proxies verwendet. Last.fm-Metriken sind in der akademischen
    Musikforschung weit verbreitet und korrelieren stark mit plattformuebergreifenden
    Popularitaetsindikatoren.
    </p>
</div>
""", unsafe_allow_html=True)
