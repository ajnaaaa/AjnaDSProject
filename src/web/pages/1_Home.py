import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Live Music: Digital Popularity vs Reality",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────
st.markdown("""
<style>
    /* Hauptfarben */
    :root {
        --primary: #1DB954;
        --dark: #191414;
        --card-bg: #1e1e1e;
        --text: #FFFFFF;
        --subtext: #b3b3b3;
    }

    .main { background-color: #0e0e0e; }

    /* Hero Section */
    .hero {
        background: linear-gradient(135deg, #191414 0%, #1a3a2a 100%);
        border-radius: 16px;
        padding: 60px 40px;
        text-align: center;
        margin-bottom: 40px;
        border: 1px solid #1DB954;
    }
    .hero h1 {
        font-size: 2.8rem;
        font-weight: 800;
        color: #1DB954;
        margin-bottom: 10px;
    }
    .hero p {
        font-size: 1.2rem;
        color: #b3b3b3;
        max-width: 700px;
        margin: 0 auto;
    }

    /* Research Question Cards */
    .rq-card {
        background: #1e1e1e;
        border-radius: 12px;
        padding: 24px;
        border-left: 4px solid #1DB954;
        margin-bottom: 16px;
        height: 100%;
    }
    .rq-card h4 {
        color: #1DB954;
        margin-bottom: 8px;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .rq-card p {
        color: #ffffff;
        font-size: 0.95rem;
        margin: 0;
        line-height: 1.5;
    }

    /* Stats Cards */
    .stat-card {
        background: #1e1e1e;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #333;
    }
    .stat-number {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1DB954;
    }
    .stat-label {
        font-size: 0.85rem;
        color: #b3b3b3;
        margin-top: 4px;
    }

    /* Section Header */
    .section-header {
        color: #ffffff;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 2px solid #1DB954;
    }

    /* Data Source Badge */
    .badge {
        display: inline-block;
        background: #1DB954;
        color: #000;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 4px;
    }

    /* Sidebar */
    .css-1d391kg { background-color: #191414; }

    /* Methodology Box */
    .methodology-box {
        background: #1a2a1a;
        border: 1px solid #1DB954;
        border-radius: 12px;
        padding: 20px 24px;
        margin-top: 10px;
    }
    .methodology-box p {
        color: #b3b3b3;
        font-size: 0.9rem;
        line-height: 1.7;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)

# ── Hero Section ───────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🎵 Live Music: Digital Popularity vs Reality</h1>
    <p>From Streams to Stages — To what extent do digital streaming metrics 
    predict the physical reality of global concert tours?</p>
    <br>
    <span class="badge">Last.fm API</span>
    <span class="badge">Ticketmaster API</span>
    <span class="badge">OpenRouteService API</span>
    <span class="badge">RestCountries API</span>
</div>
""", unsafe_allow_html=True)

# ── Dataset Stats ──────────────────────────────────────
st.markdown('<div class="section-header">📊 Dataset Overview</div>', unsafe_allow_html=True)

# Daten laden falls vorhanden
data_path = "data/processed/final_dataset.csv"
events_path = "data/raw/ticketmaster_events.csv"
lastfm_path = "data/raw/artists_lastfm.csv"

col1, col2, col3, col4 = st.columns(4)

if os.path.exists(data_path):
    df = pd.read_csv(data_path)
    n_artists = len(df)
    n_events = int(df["total_events"].sum()) if "total_events" in df.columns else "—"
    n_countries = df["countries"].sum() if "countries" in df.columns else "—"
    avg_listeners = f"{int(df['listeners'].mean()):,}" if "listeners" in df.columns else "—"
else:
    n_artists = "—"
    n_events = "—"
    n_countries = "—"
    avg_listeners = "—"

with col1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{n_artists}</div>
        <div class="stat-label">Artists analysiert</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{n_events}</div>
        <div class="stat-label">Konzert Events</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{n_countries}</div>
        <div class="stat-label">Länder abgedeckt</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{avg_listeners}</div>
        <div class="stat-label">Ø Last.fm Listeners</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Research Questions ─────────────────────────────────
st.markdown('<div class="section-header">🔬 Research Questions</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🎟️ Streaming & Ticket Power", "🗺️ Geographic Analysis", "📅 Market Time & Scheduling"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="rq-card">
            <h4>F1 — Correlation</h4>
            <p>How does the number of Last.fm listeners correlate with the scale 
            of an artist's tour, measured by the number of events scheduled?</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="rq-card">
            <h4>F2 — Ticket Status</h4>
            <p>How does Last.fm playcount differ between artists whose events 
            are still onsale and those whose events are already offsale?</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="rq-card">
            <h4>F3 — Viral Charts</h4>
            <p>How do current Last.fm listener counts differ between artists 
            who appeared in Last.fm Weekly Charts (Feb 2023–Feb 2026) 
            and those who did not?</p>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="rq-card">
            <h4>F4 — Revisit Cities</h4>
            <p>What is the ratio of revisit cities to new cities on an 
            artist's current tour?</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="rq-card">
            <h4>F5 — Genre Density</h4>
            <p>How does ticket availability change depending on the density 
            of similar artists (same genre) performing within a 300km radius 
            in the same time window?</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="rq-card">
            <h4>F6 — Capital Cities</h4>
            <p>What proportion of an artist's performances take place in 
            capital cities compared to non-capital cities?</p>
        </div>
        """, unsafe_allow_html=True)

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="rq-card">
            <h4>F7 — Days Between Shows</h4>
            <p>How does the average number of days between concert dates 
            differ between high and low popularity artists?</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="rq-card">
            <h4>F8 — Weekend Shows</h4>
            <p>To what extent does an artist's Last.fm playcount influence 
            the percentage of concerts scheduled on weekends?</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="rq-card">
            <h4>F9 — Lead Time</h4>
            <p>How does the lead time (days between sale start and event date) 
            correlate with an artist's Last.fm listener count?</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Methodology ────────────────────────────────────────
st.markdown('<div class="section-header">📋 Methodology</div>', unsafe_allow_html=True)

st.markdown("""
<div class="methodology-box">
    <p>
    This study originally intended to use Spotify Web API metrics (followers, popularity score). 
    Due to Spotify's <strong style="color:#1DB954">February 2026 API restrictions</strong> which removed these fields 
    from Development Mode access, we substituted <strong style="color:#1DB954">Last.fm listener count and playcount</strong> 
    as equivalent popularity proxies.
    <br><br>
    Last.fm metrics are widely used in academic music research and correlate strongly with 
    cross-platform popularity indicators. Tour scale was measured as the total number of events 
    on Ticketmaster within <strong style="color:#1DB954">January 2022 – December 2026</strong>, capturing the 
    post-COVID concert recovery period and ensuring temporal consistency with the Last.fm listener 
    snapshot collected in March 2026.
    <br><br>
    Analysis was restricted to artists for whom both Last.fm listener data and at least one 
    Ticketmaster event were available.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Navigation ─────────────────────────────────────────
st.markdown('<div class="section-header">🚀 Navigate to Analysis</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.page_link("pages/2_Streaming_Ticket.py", label="🎟️ Streaming & Ticket Power", use_container_width=True)

with col2:
    st.page_link("pages/3_Geographic.py", label="🗺️ Geographic Analysis", use_container_width=True)

with col3:
    st.page_link("pages/4_Scheduling.py", label="📅 Market Time & Scheduling", use_container_width=True)

# ── Sidebar ────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎵 Live Music Project")
    st.markdown("**Christian-Albrechts-Universität zu Kiel**")
    st.markdown("Data Science Projekt – 2026")
    st.divider()
    st.markdown("### Data Sources")
    st.markdown("- 🎧 Last.fm API")
    st.markdown("- 🎟️ Ticketmaster API")
    st.markdown("- 🌍 RestCountries API")
    st.markdown("- 🗺️ OpenRouteService API")
    st.divider()

    if os.path.exists(data_path):
        st.success(f"✅ Dataset loaded: {n_artists} artists")
    else:
        st.warning("⚠️ No data found. Run data collection scripts first.")
        st.code("python scripts/collect_artists_lastfm.py\npython scripts/collect_ticketmaster_ORIG.py\npython scripts/join_data.py")
