import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.styles import apply_styles
from components.navbar import render_navbar
from components.glossary import apply_glossary_styles, tt


def _hex_rgba(hex_color: str, alpha: float = 0.2) -> str:
    """Konvertiert #rrggbb zu rgba(r,g,b,alpha) fuer Plotly fillcolor."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


st.set_page_config(
    page_title="Market Time & Scheduling",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed",
)
apply_styles()
render_navbar()
apply_glossary_styles()


# ── Daten laden ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    p = "data/processed/final_dataset.csv"
    if not os.path.exists(p):
        return None
    df = pd.read_csv(p)
    for c in ["listeners", "playcount", "total_events",
              "avg_days_between_shows", "pct_weekend", "lead_time_days"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


df = load_data()

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <h1>📅 Market Time &amp; Scheduling</h1>
    <p>Wie planen Kuenstler ihre Touren — und haengt die Struktur der Konzertplanung
    mit ihrer digitalen Popularitaet zusammen?</p>
</div>
""", unsafe_allow_html=True)

# ── Fragen-Uebersicht ────────────────────────────────────────────────────────
st.markdown("""
<div style="background:#161c2d;border:1px solid #232840;border-radius:14px;
    padding:24px 28px;margin-bottom:28px;">
    <div style="font-size:.7rem;font-weight:700;text-transform:uppercase;
        letter-spacing:.12em;color:#475569 !important;margin-bottom:14px;">
        Inhaltsübersicht — Forschungsfragen
    </div>
    <div style="display:flex;flex-direction:column;gap:10px;">
        <a href="#sched-1" style="display:flex;align-items:center;gap:12px;
            text-decoration:none;padding:10px 14px;border-radius:8px;
            background:#051a10;border:1px solid #0d3020;">
            <span style="background:#059669;color:white !important;border-radius:50%;
                width:24px;height:24px;display:flex;align-items:center;justify-content:center;
                font-size:.75rem;font-weight:700;flex-shrink:0;">1</span>
            <span style="color:#cbd5e1 !important;font-size:.9rem;">
                Wie unterscheiden sich die durchschnittlichen Tage zwischen Konzerten bei
                Kuenstlern mit hoher vs. niedriger Last.fm Listener-Zahl?
            </span>
        </a>
        <a href="#sched-2" style="display:flex;align-items:center;gap:12px;
            text-decoration:none;padding:10px 14px;border-radius:8px;
            background:#051a10;border:1px solid #0d3020;">
            <span style="background:#059669;color:white !important;border-radius:50%;
                width:24px;height:24px;display:flex;align-items:center;justify-content:center;
                font-size:.75rem;font-weight:700;flex-shrink:0;">2</span>
            <span style="color:#cbd5e1 !important;font-size:.9rem;">
                Wie stark beeinflusst der Last.fm Playcount den Anteil der Konzerte,
                die am Wochenende stattfinden?
            </span>
        </a>
        <a href="#sched-3" style="display:flex;align-items:center;gap:12px;
            text-decoration:none;padding:10px 14px;border-radius:8px;
            background:#051a10;border:1px solid #0d3020;">
            <span style="background:#059669;color:white !important;border-radius:50%;
                width:24px;height:24px;display:flex;align-items:center;justify-content:center;
                font-size:.75rem;font-weight:700;flex-shrink:0;">3</span>
            <span style="color:#cbd5e1 !important;font-size:.9rem;">
                Wie korreliert die Vorlaufzeit (Tage zwischen Ticketstart und erstem Konzert)
                mit der Last.fm Listener-Zahl eines Kuenstlers?
            </span>
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

if df is None:
    st.error("Datei `data/processed/final_dataset.csv` nicht gefunden.")
    st.code("python scripts/join_data.py", language="bash")
    st.stop()

# ── KPIs ────────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Artists", len(df))
if "avg_days_between_shows" in df.columns:
    k2.metric("Ø Tage zwischen Shows",
              f"{df['avg_days_between_shows'].median():.0f} Tage",
              help="Median ueber alle Artists")
if "pct_weekend" in df.columns:
    k3.metric("Ø Weekend-Anteil",
              f"{df['pct_weekend'].mean():.1f}%",
              help="Anteil Konzerte Fr/Sa/So")
if "lead_time_days" in df.columns:
    k4.metric("Ø Vorlaufzeit",
              f"{df['lead_time_days'].mean():.0f} Tage",
              help="Tage zwischen Ticketstart und Konzert")
k5.metric("Ø Last.fm Listeners",
          f"{int(df['listeners'].mean()):,}" if "listeners" in df.columns else "—")
st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# FRAGE 1 — Tage zwischen Shows vs. Popularitaet
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div id="sched-1"></div>', unsafe_allow_html=True)

st.markdown("""
<div class="rq-box">
    <h3>📅 Research Question 1</h3>
    <p>How do average days between concerts differ between high and low
    Last.fm listener count artists?</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
Artists mit grossen Fanbasen koennen haeufiger touren — oder ist es genau umgekehrt,
weil grosse Stars mehr Zeit fuer Produktion, Pause und globale Logistik benoetigen?
Diese Frage untersucht den Zusammenhang zwischen Last.fm Listeners und dem
durchschnittlichen Abstand zwischen zwei Konzerten.

**Hypothese:** Populaere Artists touren dichter getaktet (weniger Tage zwischen Shows),
da groessere Management-Teams effizientere Planung ermoeglichen und die Nachfrage hoeher ist.
""")

col_f1 = "avg_days_between_shows"

if col_f1 not in df.columns or df[col_f1].notna().sum() < 10:
    st.warning("Spalte `avg_days_between_shows` nicht in Dataset — join_data.py neu ausfuehren.")
else:
    df1 = df.dropna(subset=["listeners", col_f1]).copy()
    df1 = df1[df1[col_f1] > 0]
    df1["log_listeners"] = np.log10(df1["listeners"] + 1)
    df1["Popularity-Tier"] = pd.qcut(df1["listeners"], q=4,
                                     labels=["Q1\n(niedrig)", "Q2", "Q3", "Q4\n(hoch)"])

    r1, p1 = stats.pearsonr(df1["log_listeners"], df1[col_f1])
    r1_s, p1_s = stats.spearmanr(df1["listeners"], df1[col_f1])
    coef1 = np.polyfit(df1["log_listeners"], df1[col_f1], 1)
    x_line1 = np.linspace(df1["log_listeners"].min(), df1["log_listeners"].max(), 200)
    y_line1 = np.polyval(coef1, x_line1)

    m1a, m1b, m1c, m1d = st.columns(4)
    m1a.metric("n Artists", len(df1))
    m1b.metric("Pearson r", f"{r1:.3f}")
    m1c.metric("p-Wert", f"{p1:.4f}",
               delta="signifikant ✅" if p1 < 0.05 else "nicht signifikant ⚠️",
               delta_color="normal" if p1 < 0.05 else "inverse")
    m1d.metric("Spearman r", f"{r1_s:.3f}")

    # ── Graph 1a: Scatterplot ────────────────────────────────────────────────
    st.markdown('<div class="section-title">📈 Graph 1 — Listeners vs. Tage zwischen Shows</div>',
                unsafe_allow_html=True)

    g1_ctrl, g1_plot = st.columns([1, 3])
    with g1_ctrl:
        st.markdown("**Filter & Optionen**")
        max_days = st.slider("Max. Tage anzeigen", 30, 365,
                             int(df1[col_f1].quantile(0.95)), key="f7_max")
        show_lbl1 = st.checkbox("Namen anzeigen", False, key="f7_lbl")
        color_by1 = st.selectbox("Farbe nach",
                                 ["total_events", "pct_weekend", "lead_time_days"],
                                 format_func=lambda x: {
                                     "total_events": "Anzahl Events",
                                     "pct_weekend": "Weekend-Anteil",
                                     "lead_time_days": "Vorlaufzeit",
                                 }.get(x, x), key="f7_color")
        color_by1 = color_by1 if color_by1 in df1.columns else None

    df1_plot = df1[df1[col_f1] <= max_days].copy()
    st.markdown(f"""
    <div class="methodology-note">
        <p>Jeder Punkt = ein Artist. X-Achse = log₁₀(Last.fm Listeners), Y-Achse = Ø Tage
        zwischen zwei aufeinanderfolgenden Konzerten. {len(df1) - len(df1_plot)} Artists
        mit &gt;{max_days} Tagen ausgeblendet (Ausreisser-Filter).</p>
    </div>
    """, unsafe_allow_html=True)

    fig1 = px.scatter(
        df1_plot, x="log_listeners", y=col_f1,
        color=color_by1 if color_by1 else "Popularity-Tier",
        color_continuous_scale="Viridis" if color_by1 else None,
        hover_name="artist_name",
        hover_data={"log_listeners": False, col_f1: ":.1f",
                    "listeners": ":,", "total_events": True},
        text="artist_name" if show_lbl1 else None,
        labels={"log_listeners": "log₁₀(Last.fm Listeners)",
                col_f1: "Ø Tage zwischen Shows"},
        title=f"Listeners vs. Ø Tage zwischen Shows  |  r = {r1:.3f}  |  n = {len(df1_plot)}",
        template="plotly_dark",
    )
    fig1.add_trace(go.Scatter(
        x=x_line1[y_line1 <= max_days], y=y_line1[y_line1 <= max_days],
        mode="lines", name="OLS",
        line=dict(color="#10b981", width=2.5), hoverinfo="skip",
    ))
    if show_lbl1:
        fig1.update_traces(textposition="top center",
                           textfont=dict(size=7, color="white"),
                           selector=dict(mode="markers+text"))
    fig1.update_layout(
        height=460, paper_bgcolor="#080b14", plot_bgcolor="#161c2d",
        font=dict(color="white"),
        xaxis=dict(gridcolor="#232840"),
        yaxis=dict(gridcolor="#232840"),
    )
    with g1_plot:
        st.plotly_chart(fig1, use_container_width=True)

    # ── Graph 1b: Box Plot nach Tier ─────────────────────────────────────────
    st.markdown('<div class="section-title">📦 Graph 2 — Tage zwischen Shows nach Popularity-Tier</div>',
                unsafe_allow_html=True)
    st.markdown("""
    Vier gleich grosse Gruppen (Quartile) nach Listener-Zahl aufgeteilt.
    Jede Box zeigt die Verteilung der durchschnittlichen Pausen zwischen Shows.
    Kruskal-Wallis testet ob sich mindestens zwei Gruppen signifikant unterscheiden.
    """)

    df1b = df1[df1[col_f1] <= max_days].copy()
    kw_grps = [df1b[df1b["Popularity-Tier"] == t][col_f1].dropna().values
               for t in df1b["Popularity-Tier"].unique() if len(df1b[df1b["Popularity-Tier"] == t]) > 1]
    kw1_h = kw1_p = None
    if len(kw_grps) >= 2:
        kw1_h, kw1_p = stats.kruskal(*kw_grps)

    TIER_COLORS = {
        "Q1\n(niedrig)": "#475569",
        "Q2": "#6366f1",
        "Q3": "#818cf8",
        "Q4\n(hoch)": "#fbbf24",
    }
    fig1b = go.Figure()
    for tier in ["Q1\n(niedrig)", "Q2", "Q3", "Q4\n(hoch)"]:
        sub = df1b[df1b["Popularity-Tier"] == tier][col_f1].dropna()
        if len(sub) == 0: continue
        fig1b.add_trace(go.Box(
            y=sub, name=tier.replace("\n", " "),
            marker_color=TIER_COLORS.get(tier, "#6366f1"),
            fillcolor=_hex_rgba(TIER_COLORS.get(tier, "#6366f1")),
            line=dict(color=TIER_COLORS.get(tier, "#6366f1"), width=1.5),
            boxpoints="outliers",
            hovertemplate="Median: %{median:.1f} Tage<extra>" + tier.replace('\n', ' ') + "</extra>",
        ))

    title1b = "Tage zwischen Shows nach Popularity-Tier"
    if kw1_p is not None:
        title1b += f"  |  Kruskal-Wallis H={kw1_h:.1f}  p={kw1_p:.4f}  {'✅' if kw1_p < 0.05 else '⚠️'}"

    fig1b.update_layout(
        title=title1b,
        yaxis_title="Ø Tage zwischen Shows",
        xaxis_title="Popularity-Tier (nach Last.fm Listeners)",
        template="plotly_dark",
        paper_bgcolor="#080b14", plot_bgcolor="#161c2d",
        font=dict(color="white"), height=400,
        xaxis=dict(gridcolor="#232840"),
        yaxis=dict(gridcolor="#232840"),
        showlegend=False,
    )
    st.plotly_chart(fig1b, use_container_width=True)

    # Tier-Mittelwerte
    tier_means1 = df1b.groupby("Popularity-Tier", observed=True)[col_f1].agg(
        Median="median", Mittelwert="mean", n="count"
    ).round(1)
    st.markdown("**Kennzahlen pro Tier:**")
    st.dataframe(tier_means1, use_container_width=True)

    st.markdown(f"""
    <div class="insight-card">
        <h4>💡 Erkenntnis Frage 1</h4>
        <p>
        Pearson r = <strong style="color:#10b981">{r1:.3f}</strong>
        (p = {p1:.4f} — {"signifikant ✅" if p1 < 0.05 else "nicht signifikant ⚠️"}).
        {'Ein negativer Zusammenhang bedeutet: Populaerere Artists haben kuerzere Pausen zwischen Shows — sie touren dichter.' if r1 < 0
    else 'Ein positiver Zusammenhang bedeutet: Populaerere Artists haben laengere Pausen — grosse Stars brauchen mehr Zeit zwischen Auftritten.' if r1 > 0
    else 'Kein klarer linearer Zusammenhang.'}
        {f' Kruskal-Wallis bestaetigt signifikante Gruppenunterschiede (p = {kw1_p:.4f}).' if kw1_p is not None and kw1_p < 0.05 else ''}
        </p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# FRAGE 2 — Weekend-Anteil vs. Playcount
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div id="sched-2"></div>', unsafe_allow_html=True)

st.markdown("""
<div class="rq-box">
    <h3>📅 Research Question 2</h3>
    <p>To what extent does an artist's Last.fm playcount influence the percentage
    of concerts scheduled on weekends?</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
Wochenenden (Freitag bis Sonntag) sind fuer Konzertveranstalter attraktiver —
mehr Menschen haben frei, Tickets verkaufen sich besser.
Nutzen populaere Artists diesen Vorteil haeufiger?
Oder spielen weniger bekannte Kuenstler verstaerkt am Wochenende,
weil sie auf Publikum angewiesen sind, das unter der Woche arbeitet?

**Hypothese:** Artists mit hohem Playcount haben einen hoeheren Wochenend-Anteil,
da ihre Konzerte lukrativer sind und Veranstalter Prime-Slots bevorzugen.
""")

col_f2_x = "playcount"
col_f2_y = "pct_weekend"

if col_f2_y not in df.columns or df[col_f2_y].notna().sum() < 10:
    st.warning("Spalte `pct_weekend` nicht verfuegbar.")
else:
    df2 = df.dropna(subset=[col_f2_x, col_f2_y]).copy()
    df2 = df2[df2[col_f2_x] > 0]
    df2["log_playcount"] = np.log10(df2[col_f2_x] + 1)
    df2["Popularity-Tier"] = pd.qcut(df2["listeners"], q=4,
                                     labels=["Q1\n(niedrig)", "Q2", "Q3", "Q4\n(hoch)"])

    r2, p2 = stats.pearsonr(df2["log_playcount"], df2[col_f2_y])
    r2_s, p2_s = stats.spearmanr(df2[col_f2_x], df2[col_f2_y])
    coef2 = np.polyfit(df2["log_playcount"], df2[col_f2_y], 1)
    x_line2 = np.linspace(df2["log_playcount"].min(), df2["log_playcount"].max(), 200)
    y_line2 = np.polyval(coef2, x_line2)

    m2a, m2b, m2c, m2d = st.columns(4)
    m2a.metric("n Artists", len(df2))
    m2b.metric("Pearson r", f"{r2:.3f}")
    m2c.metric("p-Wert", f"{p2:.4f}",
               delta="signifikant ✅" if p2 < 0.05 else "nicht signifikant ⚠️",
               delta_color="normal" if p2 < 0.05 else "inverse")
    m2d.metric("Spearman ρ", f"{r2_s:.3f}")

    # ── Graph 2a: Scatterplot ────────────────────────────────────────────────
    st.markdown('<div class="section-title">📈 Graph 1 — Playcount vs. Wochenend-Anteil</div>',
                unsafe_allow_html=True)

    g2_ctrl, g2_plot = st.columns([1, 3])
    with g2_ctrl:
        show_lbl2 = st.checkbox("Namen anzeigen", False, key="f8_lbl")

    fig2 = px.scatter(
        df2, x="log_playcount", y=col_f2_y,
        color="Popularity-Tier",
        hover_name="artist_name",
        hover_data={"log_playcount": False, col_f2_y: ":.1f%",
                    "playcount": ":,", "listeners": ":,"},
        text="artist_name" if show_lbl2 else None,
        labels={"log_playcount": "log₁₀(Last.fm Playcount)",
                col_f2_y: "Wochenend-Anteil (%)"},
        title=f"Playcount vs. Wochenend-Anteil  |  r = {r2:.3f}  |  n = {len(df2)}",
        template="plotly_dark",
        category_orders={"Popularity-Tier": ["Q1\n(niedrig)", "Q2", "Q3", "Q4\n(hoch)"]},
        color_discrete_sequence=["#475569", "#6366f1", "#818cf8", "#fbbf24"],
    )
    fig2.add_trace(go.Scatter(
        x=x_line2, y=y_line2, mode="lines", name="OLS",
        line=dict(color="#10b981", width=2.5), hoverinfo="skip",
    ))
    if show_lbl2:
        fig2.update_traces(textposition="top center",
                           textfont=dict(size=7, color="white"),
                           selector=dict(mode="markers+text"))
    fig2.update_layout(
        height=460, paper_bgcolor="#080b14", plot_bgcolor="#161c2d",
        font=dict(color="white"),
        xaxis=dict(gridcolor="#232840"),
        yaxis=dict(gridcolor="#232840"),
    )
    with g2_plot:
        st.plotly_chart(fig2, use_container_width=True)

    # ── Graph 2b: Histogramm Weekend-Anteil ──────────────────────────────────
    st.markdown('<div class="section-title">📊 Graph 2 — Verteilung des Wochenend-Anteils</div>',
                unsafe_allow_html=True)
    st.markdown("""
    Wie verteilt sich der Wochenend-Anteil ueber alle Artists?
    Ein Wert von 100% bedeutet: alle Konzerte am Wochenende. 0% = nur Wochentage.
    Die meisten Artists liegen irgendwo dazwischen.
    """)

    fig2b = go.Figure()
    for tier, col in [("Q1\n(niedrig)", "#475569"), ("Q2", "#6366f1"),
                      ("Q3", "#818cf8"), ("Q4\n(hoch)", "#fbbf24")]:
        sub = df2[df2["Popularity-Tier"] == tier][col_f2_y].dropna()
        if len(sub) == 0: continue
        fig2b.add_trace(go.Histogram(
            x=sub, name=tier.replace("\n", " "),
            nbinsx=20, histnorm="probability density",
            marker_color=col, opacity=0.65,
        ))
    fig2b.update_layout(
        barmode="overlay",
        title="Verteilung Wochenend-Anteil nach Popularity-Tier",
        xaxis_title="Wochenend-Anteil (%)",
        yaxis_title="Dichte",
        template="plotly_dark",
        paper_bgcolor="#080b14", plot_bgcolor="#161c2d",
        font=dict(color="white"), height=360,
        xaxis=dict(gridcolor="#232840"),
        yaxis=dict(gridcolor="#232840"),
        legend=dict(orientation="h", y=-0.2),
    )
    st.plotly_chart(fig2b, use_container_width=True)

    # Wochenend-Statistik
    tier_means2 = df2.groupby("Popularity-Tier", observed=True)[col_f2_y].agg(
        Median="median", Mittelwert="mean", n="count"
    ).round(1)
    st.markdown("**Ø Wochenend-Anteil pro Tier:**")
    st.dataframe(tier_means2, use_container_width=True)

    st.markdown(f"""
    <div class="insight-card">
        <h4>💡 Erkenntnis Frage 2</h4>
        <p>
        Pearson r = <strong style="color:#10b981">{r2:.3f}</strong>
        (p = {p2:.4f} — {"signifikant ✅" if p2 < 0.05 else "nicht signifikant ⚠️"}).
        {'Ein positiver Zusammenhang: Artists mit mehr Plays spielen haeufiger am Wochenende.' if r2 > 0.1
    else 'Ein negativer Zusammenhang: Artists mit mehr Plays spielen weniger am Wochenende — sie fuellen auch Wochentage.' if r2 < -0.1
    else 'Kein wesentlicher linearer Zusammenhang — der Wochenend-Anteil ist weitgehend unabhaengig vom Playcount.'}
        </p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# FRAGE 3 — Vorlaufzeit vs. Listeners
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div id="sched-3"></div>', unsafe_allow_html=True)

st.markdown("""
<div class="rq-box">
    <h3>📅 Research Question 3</h3>
    <p>How does lead time (days between sale start and the first concert date)
    correlate with an artist's Last.fm listener count?</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
Grosse Konzerte werden oft Monate im Voraus angekuendigt — um die Nachfrage zu
maximieren und Logistik zu planen. Kleine Kuenstler hingegen koennen kurzfristiger
buchen. Spiegelt sich das in den Daten wider?

**Hypothese:** Artists mit mehr Listeners haben eine laengere Vorlaufzeit,
da grosse Touren mehr Planungsaufwand erfordern und Fans fruehzeitig
Tickets kaufen muessen.
""")

st.info(
    "**Methodik:** Nur Artists mit mindestens einem **zukuenftigen** Konzert "
    "und vorhandenem `onsale_date` fliessen hier ein. "
    "Pro Artist: **1 Wert** = Tage zwischen erstem Ticket-Verkaufsstart "
    "und erstem zukuenftigen Konzertdatum."
)

col_f3 = "lead_time_days"

if col_f3 not in df.columns or df[col_f3].notna().sum() < 10:
    st.warning("Spalte `lead_time_days` nicht verfuegbar.")
else:
    df3 = df.dropna(subset=["listeners", col_f3]).copy()
    df3 = df3[df3[col_f3] >= 0]
    df3["log_listeners"] = np.log10(df3["listeners"] + 1)
    df3["Popularity-Tier"] = pd.qcut(df3["listeners"], q=4,
                                     labels=["Q1\n(niedrig)", "Q2", "Q3", "Q4\n(hoch)"])

    r3, p3 = stats.pearsonr(df3["log_listeners"], df3[col_f3])
    r3_s, p3_s = stats.spearmanr(df3["listeners"], df3[col_f3])
    coef3 = np.polyfit(df3["log_listeners"], df3[col_f3], 1)
    x_line3 = np.linspace(df3["log_listeners"].min(), df3["log_listeners"].max(), 200)
    y_line3 = np.polyval(coef3, x_line3)

    m3a, m3b, m3c, m3d = st.columns(4)
    m3a.metric("n Artists", len(df3))
    m3b.metric("Pearson r", f"{r3:.3f}")
    m3c.metric("p-Wert", f"{p3:.4f}",
               delta="signifikant ✅" if p3 < 0.05 else "nicht signifikant ⚠️",
               delta_color="normal" if p3 < 0.05 else "inverse")
    m3d.metric("Spearman ρ", f"{r3_s:.3f}")

    # ── Graph 3a: Scatterplot ────────────────────────────────────────────────
    st.markdown('<div class="section-title">📈 Graph 1 — Listeners vs. Vorlaufzeit</div>',
                unsafe_allow_html=True)

    g3_ctrl, g3_plot = st.columns([1, 3])
    with g3_ctrl:
        max_lead = st.slider("Max. Vorlaufzeit (Tage)", 30, 730,
                             int(df3[col_f3].quantile(0.95)), key="f9_max")
        show_lbl3 = st.checkbox("Namen anzeigen", False, key="f9_lbl")
        color_by3 = st.selectbox("Farbe nach",
                                 ["total_events", "avg_days_between_shows", "pct_weekend"],
                                 format_func=lambda x: {
                                     "total_events": "Anzahl Events",
                                     "avg_days_between_shows": "Tage zwischen Shows",
                                     "pct_weekend": "Weekend-Anteil",
                                 }.get(x, x), key="f9_color")
        color_by3 = color_by3 if color_by3 in df3.columns else None

    df3_plot = df3[df3[col_f3] <= max_lead].copy()
    st.markdown(f"""
    <div class="methodology-note">
        <p>Vorlaufzeit = Ø Tage zwischen Ticket-Verkaufsstart (onsale_date) und Konzertdatum.
        Gemittelt ueber alle Events des Artists. {len(df3) - len(df3_plot)} Artists
        mit &gt;{max_lead} Tagen ausgeblendet.</p>
    </div>
    """, unsafe_allow_html=True)

    fig3 = px.scatter(
        df3_plot, x="log_listeners", y=col_f3,
        color=color_by3 if color_by3 else "Popularity-Tier",
        color_continuous_scale="Viridis" if color_by3 else None,
        hover_name="artist_name",
        hover_data={"log_listeners": False, col_f3: ":.0f",
                    "listeners": ":,", "total_events": True},
        text="artist_name" if show_lbl3 else None,
        labels={"log_listeners": "log₁₀(Last.fm Listeners)",
                col_f3: "Ø Vorlaufzeit (Tage)"},
        title=f"Listeners vs. Vorlaufzeit  |  r = {r3:.3f}  |  n = {len(df3_plot)}",
        template="plotly_dark",
        category_orders={"Popularity-Tier": ["Q1\n(niedrig)", "Q2", "Q3", "Q4\n(hoch)"]},
        color_discrete_sequence=["#475569", "#6366f1", "#818cf8", "#fbbf24"],
    )
    fig3.add_trace(go.Scatter(
        x=x_line3[y_line3 <= max_lead], y=y_line3[y_line3 <= max_lead],
        mode="lines", name="OLS",
        line=dict(color="#10b981", width=2.5), hoverinfo="skip",
    ))
    if show_lbl3:
        fig3.update_traces(textposition="top center",
                           textfont=dict(size=7, color="white"),
                           selector=dict(mode="markers+text"))
    fig3.update_layout(
        height=460, paper_bgcolor="#080b14", plot_bgcolor="#161c2d",
        font=dict(color="white"),
        xaxis=dict(gridcolor="#232840"),
        yaxis=dict(gridcolor="#232840"),
    )
    with g3_plot:
        st.plotly_chart(fig3, use_container_width=True)

    # ── Graph 3b: Box Plot nach Tier ─────────────────────────────────────────
    st.markdown('<div class="section-title">📦 Graph 2 — Vorlaufzeit nach Popularity-Tier</div>',
                unsafe_allow_html=True)
    st.markdown("""
    Unterscheidet sich die Planungs-Vorlaufzeit systematisch je nach Popularitaet?
    Q4 = bekannteste Artists, Q1 = unbekannteste.
    """)

    df3b = df3[df3[col_f3] <= max_lead].copy()
    kw3_grps = [df3b[df3b["Popularity-Tier"] == t][col_f3].dropna().values
                for t in df3b["Popularity-Tier"].unique()
                if len(df3b[df3b["Popularity-Tier"] == t]) > 1]
    kw3_h = kw3_p = None
    if len(kw3_grps) >= 2:
        kw3_h, kw3_p = stats.kruskal(*kw3_grps)

    fig3b = go.Figure()
    for tier, col in [("Q1\n(niedrig)", "#475569"), ("Q2", "#6366f1"),
                      ("Q3", "#818cf8"), ("Q4\n(hoch)", "#fbbf24")]:
        sub = df3b[df3b["Popularity-Tier"] == tier][col_f3].dropna()
        if len(sub) == 0: continue
        fig3b.add_trace(go.Box(
            y=sub, name=tier.replace("\n", " "),
            marker_color=col, fillcolor=_hex_rgba(col),
            line=dict(color=col, width=1.5),
            boxpoints="outliers",
            hovertemplate="Median: %{median:.0f} Tage<extra>" + tier.replace('\n', ' ') + "</extra>",
        ))

    title3b = "Vorlaufzeit nach Popularity-Tier"
    if kw3_p is not None:
        title3b += f"  |  Kruskal-Wallis H={kw3_h:.1f}  p={kw3_p:.4f}  {'✅' if kw3_p < 0.05 else '⚠️'}"

    fig3b.update_layout(
        title=title3b,
        yaxis_title="Ø Vorlaufzeit (Tage)",
        xaxis_title="Popularity-Tier (nach Last.fm Listeners)",
        template="plotly_dark",
        paper_bgcolor="#080b14", plot_bgcolor="#161c2d",
        font=dict(color="white"), height=400,
        xaxis=dict(gridcolor="#232840"),
        yaxis=dict(gridcolor="#232840"),
        showlegend=False,
    )
    st.plotly_chart(fig3b, use_container_width=True)

    tier_means3 = df3b.groupby("Popularity-Tier", observed=True)[col_f3].agg(
        Median="median", Mittelwert="mean", n="count"
    ).round(1)
    st.markdown("**Ø Vorlaufzeit (Tage) pro Tier:**")
    st.dataframe(tier_means3, use_container_width=True)

    st.markdown(f"""
    <div class="insight-card">
        <h4>💡 Erkenntnis Frage 3</h4>
        <p>
        Pearson r = <strong style="color:#10b981">{r3:.3f}</strong>
        (p = {p3:.4f} — {"signifikant ✅" if p3 < 0.05 else "nicht signifikant ⚠️"}).
        {'Populaerere Artists planen ihre Touren tatsaechlich laenger im Voraus — groessere Produktionen erfordern mehr Vorlauf.' if r3 > 0.1 and p3 < 0.05
    else 'Kein signifikanter Zusammenhang — die Vorlaufzeit haengt nicht systematisch mit der Popularitaet zusammen.' if p3 >= 0.05
    else 'Weniger populaere Artists planen ueberraschenderweise laenger im Voraus — moegliche Erklaerung: sie brauchen mehr Zeit fuer Venue-Buchungen.'}
        {f' Kruskal-Wallis bestaetigt signifikante Tier-Unterschiede (p = {kw3_p:.4f}).' if kw3_p is not None and kw3_p < 0.05 else ''}
        </p>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ZUSAMMENFASSUNG
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
st.markdown('<div class="section-title">✅ Fazit — Market Time &amp; Scheduling</div>',
            unsafe_allow_html=True)

st.markdown("""
<div style="
    background:linear-gradient(135deg,#051a10 0%,#0d3020 100%);
    border:1px solid #059669; border-radius:16px; padding:36px 40px;
">
    <p style="color:#f1f5f9 !important;font-size:1rem;font-weight:500;
        line-height:1.8;margin:0 0 16px 0;">
        <strong style="color:#10b981 !important;">Was haben wir gelernt?</strong>
    </p>
    <p style="color:#cbd5e1 !important;font-size:.95rem;line-height:1.8;margin:0 0 12px 0;">
        Die zeitliche Struktur von Tourneen ist vielschichtiger als erwartet.
        Popularitaet — gemessen an Last.fm Listeners und Playcounts — haengt
        zwar mit Aspekten der Tourplanung zusammen, aber die Zusammenhaenge
        sind oft schwaecher als intuitiv angenommen.
    </p>
    <p style="color:#94a3b8 !important;font-size:.9rem;line-height:1.8;margin:0;">
        Die Vorlaufzeit und der Abstand zwischen Shows deuten auf strategische
        Tourplanung hin, die sich mit zunehmender Popularitaet veraendert.
        Der Wochenend-Anteil hingegen scheint weniger vom Streaming-Erfolg
        abhaengig zu sein — ein Hinweis darauf, dass Venue-Verfuegbarkeit
        und regionale Gewohnheiten eine groessere Rolle spielen.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="methodology-note" style="margin-top:16px;">
    <p>
    avg_days_between_shows: Mittlerer Abstand (in Tagen) zwischen aufeinanderfolgenden
    sortierten Konzertdaten pro Artist. pct_weekend: Anteil der Events mit
    dayofweek >= 4 (Freitag=4, Samstag=5, Sonntag=6). avg_lead_time: Mittlere Differenz
    zwischen onsale_date (Ticketmaster public.startDateTime) und event_date.
    Alle Werte aus data/processed/final_dataset.csv, berechnet in join_data.py.
    </p>
</div>
""", unsafe_allow_html=True)
