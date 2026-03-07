"""
components/nav.py  —  Custom Box Navigation
Import in jede Page:
    from components.nav import render_nav
    render_nav()
"""
import streamlit as st


# Seitenstruktur
PAGES = [
    {
        "label": "Analyse",    # Section-Label
        "items": [
            {"icon": "🏠",  "title": "Home",              "page": "pages/1_Home.py"},
            {"icon": "🎟️",  "title": "Streaming & Ticket","page": "pages/2_Streaming_Ticket.py"},
            {"icon": "🗺️",  "title": "Geographic",        "page": "pages/3_Geographic.py"},
            {"icon": "📅",  "title": "Scheduling",        "page": "pages/4_Scheduling.py"},
            {"icon": "📖",  "title": "Glossar",            "page": "pages/5_Glossar.py"},
        ]
    },
]

NAV_CSS = """
<style>
.nav-logo {
    padding: 22px 18px 14px;
    border-bottom: 1px solid #232840;
    margin-bottom: 10px;
}
.nav-app-label {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: #475569 !important;
    margin-bottom: 4px;
}
.nav-app-title {
    font-size: 0.95rem;
    font-weight: 800;
    line-height: 1.25;
    background: linear-gradient(90deg, #818cf8, #fbbf24);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.nav-section {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #475569 !important;
    padding: 10px 18px 6px;
    margin-top: 4px;
}
.nav-footer {
    padding: 16px 18px;
    border-top: 1px solid #232840;
    margin-top: 16px;
    font-size: 0.72rem;
    color: #475569 !important;
    line-height: 1.6;
}
</style>
"""


def render_nav():
    """Rendert die komplette Sidebar-Navigation."""
    with st.sidebar:
        # CSS
        st.markdown(NAV_CSS, unsafe_allow_html=True)

        # Logo / App-Titel
        st.markdown("""
        <div class="nav-logo">
            <div class="nav-app-label">🎵 Data Science Project</div>
            <div class="nav-app-title">From Streams<br>to Stages</div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation-Boxen
        for section in PAGES:
            st.markdown(
                f'<div class="nav-section">{section["label"]}</div>',
                unsafe_allow_html=True
            )
            for item in section["items"]:
                st.page_link(
                    item["page"],
                    label=f'{item["icon"]}  {item["title"]}',
                )

        # Trennlinie + Footer
        st.markdown("""
        <div class="nav-footer">
            <strong style="color:#94a3b8 !important">Last.fm</strong> × <strong style="color:#94a3b8 !important">Ticketmaster</strong><br>
            Daten: 2022–2026 · 499 Artists
        </div>
        """, unsafe_allow_html=True)
