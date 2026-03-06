import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import os

st.set_page_config(
    page_title="Geographic Analysis",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.main { background-color: #0e0e0e; }
.page-header {
    background: linear-gradient(135deg, #191414 0%, #1a2a2e 100%);
    border-radius: 16px; padding: 40px; margin-bottom: 32px;
    border-left: 6px solid #1DB954;
}
.page-header h1 { color: #1DB954; font-size: 2rem; margin: 0 0 8px 0; }
.page-header p  { color: #b3b3b3; margin: 0; font-size: 1rem; }
.rq-box {
    background: #1a2a1a; border: 2px solid #1DB954;
    border-radius: 12px; padding: 20px 24px; margin-bottom: 28px;
}
.rq-box h3 { color: #1DB954; margin: 0 0 8px 0; font-size: 0.85rem;
             text-transform: uppercase; letter-spacing: 1px; }
.rq-box p  { color: #ffffff; margin: 0; font-size: 1.1rem; font-weight: 600; }
.section-title {
    font-size: 1.25rem; font-weight: 700; color: #ffffff;
    margin: 32px 0 8px 0; padding-bottom: 8px;
    border-bottom: 2px solid #1DB954;
}
.insight-card {
    background: #1e1e1e; border-radius: 10px;
    padding: 16px 20px; border-left: 4px solid #1DB954; margin-bottom: 12px;
}
.insight-card h4 { color: #1DB954; margin: 0 0 6px 0;
                   font-size: 0.82rem; text-transform: uppercase; letter-spacing: 1px; }
.insight-card p  { color: #e0e0e0; margin: 0; font-size: 0.9rem; line-height: 1.6; }
.methodology-note {
    background: #111; border: 1px solid #333;
    border-radius: 8px; padding: 14px 18px; margin-top: 16px;
}
.methodology-note p { color: #777; font-size: 0.82rem; margin: 0; font-style: italic; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <h1>🗺️ Geographic Analysis</h1>
    <p>Where do artists tour — and do they return to the same cities?</p>
</div>
""", unsafe_allow_html=True)


# ── Daten laden ────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    f1 = "data/processed/final_dataset.csv"
    f2 = "data/processed/f4_city_frequencies.csv"
    if not os.path.exists(f1):
        return None, None
    df = pd.read_csv(f1)
    for col in ["revisit_cities", "new_cities", "pct_revisit_cities",
                "revisit_ratio", "pct_events_revisit", "total_events",
                "listeners", "pct_capital"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    city_df = pd.read_csv(f2) if os.path.exists(f2) else None
    return df, city_df


df, city_df = load_data()

if df is None:
    st.error("⚠️  `data/processed/final_dataset.csv` nicht gefunden.")
    st.code("python scripts/join_data.py")
    st.stop()

F4_COLS = ["revisit_cities", "new_cities", "pct_revisit_cities", "revisit_ratio", "pct_events_revisit"]
if any(c not in df.columns for c in F4_COLS):
    st.error(f"⚠️  F4-Spalten fehlen — `join_data.py` ausführen.")
    st.code("python scripts/join_data.py")
    st.stop()

df_f4 = df.dropna(subset=["revisit_cities", "new_cities"]).copy()

# Globale Kennzahlen
total_rev = df_f4["revisit_cities"].sum()
total_new = df_f4["new_cities"].sum()
total_cities = total_rev + total_new
global_ratio = total_rev / total_new if total_new > 0 else 0
global_pct = total_rev / total_cities * 100 if total_cities > 0 else 0
mean_pct = df_f4["pct_revisit_cities"].mean()
median_pct = df_f4["pct_revisit_cities"].median()

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🗺️ Geographic Analysis")
    st.divider()
    st.markdown("**▶ F4 — Revisit vs New Cities**")
    st.markdown("F5 — Genre Density 300km")
    st.markdown("F6 — Capital vs Non-Capital")
    st.divider()
    st.metric("Künstler gesamt", len(df))
    st.metric("mit F4-Daten", len(df_f4))
    if city_df is not None:
        n_cities = city_df["city"].nunique()
        st.metric("Einzigartige Städte", n_cities)
    st.divider()
    st.markdown("**Graphs auf dieser Seite**")
    st.markdown("📈 Scatterplot · 📊 Balken · 📦 Boxplot · 🌡️ Heatmap · 🔍 Detail")

# ══════════════════════════════════════════════════════════════════════════
# RESEARCH QUESTION 4
# ══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="rq-box">
    <h3>🔬 Research Question 4</h3>
    <p>What is the ratio of revisit cities to new cities on an artist's current tour?</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
**Definitionen**

| Begriff | Bedeutung |
|---------|-----------|
| **New City** | Stadt die der Artist im Beobachtungszeitraum genau **1×** besucht |
| **Revisit City** | Stadt die der Artist **≥ 2×** besucht |
| **pct_revisit_cities** | Anteil Revisit-Städte an allen bereisten Städten (%) |
| **revisit_ratio** | Revisit-Städte / New-Städte (Verhältnis) |
| **pct_events_revisit** | Anteil aller Events die in Revisit-Städten stattfinden (%) — i.d.R. höher als pct_revisit, da diese Städte mehrfach zählen |

**Hypothese:** Künstler mit größeren Touren kehren anteilig öfter in bewährte Städte zurück
— sie optimieren auf sichere Märkte. Kleinere Artists erkunden breitere geografische Gebiete.
""")

# KPIs
st.divider()
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Ø Revisit-Rate", f"{mean_pct:.1f}%", delta=f"Median {median_pct:.1f}%")
k2.metric("Globaler Ratio", f"{global_ratio:.2f}", delta="revisit / new")
k3.metric("Total Revisit Cities", f"{total_rev:.0f}")
k4.metric("Total New Cities", f"{total_new:.0f}")
k5.metric("% des Tourings = Revisit", f"{global_pct:.1f}%")
st.divider()

# ══════════════════════════════════════════════════════════════════════════
# GRAPH 1 — Scatterplot Revisit vs. New Cities
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📈 Graph 1 — Scatterplot: Revisit vs. New Cities pro Artist</div>',
            unsafe_allow_html=True)
st.markdown("""
Jeder Punkt = ein Artist. X = New Cities, Y = Revisit Cities.
Die **gestrichelte Diagonale** markiert ratio = 1 (gleich viele revisit wie neue Städte).
Punkte **oberhalb** der Linie revisiten mehr als sie neue Städte bereisen.
""")

s1, s2 = st.columns([1, 3])
with s1:
    min_ev = st.slider("Mindest-Events", 1, 20, 3, key="f4s_min")
    log_sc = st.checkbox("Log-Skala", value=False, key="f4s_log")
    lbl_sc = st.checkbox("Namen", value=False, key="f4s_lbl")
    col_by = st.radio("Farbe nach",
                      ["total_events", "pct_revisit_cities", "listeners"],
                      index=0, key="f4s_col",
                      format_func=lambda x: {"total_events": "Events",
                                             "pct_revisit_cities": "% Revisit",
                                             "listeners": "Listeners"}[x])

df_s = df_f4[df_f4["total_events"] >= min_ev].dropna(subset=["new_cities", "revisit_cities"]).copy()
if col_by == "listeners" and "listeners" not in df_s.columns:
    col_by = "total_events"
df_s = df_s.dropna(subset=[col_by])

if len(df_s) > 0:
    df_s["x_p"] = (np.log10(df_s["new_cities"] + 1) if log_sc else df_s["new_cities"])
    df_s["y_p"] = (np.log10(df_s["revisit_cities"] + 1) if log_sc else df_s["revisit_cities"])
    max_diag = max(df_s["x_p"].max(), df_s["y_p"].max()) * 1.05

    fig1 = px.scatter(
        df_s, x="x_p", y="y_p",
        color=col_by,
        color_continuous_scale="YlGn",
        hover_name="artist_name",
        hover_data={"x_p": False, "y_p": False,
                    "new_cities": True, "revisit_cities": True,
                    "pct_revisit_cities": ":.1f", "total_events": True},
        text="artist_name" if lbl_sc else None,
        labels={"x_p": ("log₁₀(New Cities)" if log_sc else "New Cities"),
                "y_p": ("log₁₀(Revisit Cities)" if log_sc else "Revisit Cities")},
        title=f"Revisit vs. New Cities  |  n={len(df_s)}  |  min {min_ev} Events",
        template="plotly_dark",
    )
    fig1.add_trace(go.Scatter(
        x=[0, max_diag], y=[0, max_diag],
        mode="lines", name="ratio = 1",
        line=dict(color="white", width=1, dash="dash"),
        hoverinfo="skip",
    ))
    fig1.update_traces(marker=dict(size=9, opacity=0.85,
                                   line=dict(width=0.5, color="white")),
                       selector=dict(mode="markers"))
    if lbl_sc:
        fig1.update_traces(textposition="top center",
                           textfont=dict(size=8, color="white"),
                           selector=dict(mode="markers+text"))
    fig1.update_layout(height=510, paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
                       font=dict(color="white"),
                       xaxis=dict(gridcolor="#333"), yaxis=dict(gridcolor="#333"),
                       coloraxis_colorbar=dict(title=col_by.replace("_", " ")))
    with s2:
        st.plotly_chart(fig1, use_container_width=True)

    above = int((df_s["revisit_cities"] > df_s["new_cities"]).sum())
    below = int((df_s["revisit_cities"] < df_s["new_cities"]).sum())
    equal = int((df_s["revisit_cities"] == df_s["new_cities"]).sum())
    n = len(df_s)
    st.markdown(f"""
    <div class="insight-card">
        <h4>📐 Verteilung um ratio = 1</h4>
        <p>
        <strong style="color:#1DB954">{above} Artists ({above / n * 100:.0f}%)</strong> revisiten mehr als sie neue Städte bereisen (oberhalb der Linie) &nbsp;|&nbsp;
        <strong>{equal} ({equal / n * 100:.0f}%)</strong> gleich viele &nbsp;|&nbsp;
        <strong style="color:#e05050">{below} ({below / n * 100:.0f}%)</strong> bereisen mehr neue Städte
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    with s2:
        st.warning("Keine Daten nach Filter.")

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# GRAPH 2 — Box Plot Revisit-Rate nach Tour-Größe
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📦 Graph 2 — Revisit-Rate nach Tour-Größe</div>',
            unsafe_allow_html=True)
st.markdown("""
Artists werden nach Tour-Größe (Anzahl Events) in Gruppen eingeteilt.
Der **Box Plot** zeigt die Verteilung der Revisit-Rate pro Gruppe —
inklusive Median, Streuung und Ausreißer.
""")

b1, b2 = st.columns([1, 3])
with b1:
    n_grp = st.select_slider("Gruppen", [3, 4, 5], value=4, key="f4b_ng")
    y_met = st.radio("Y-Achse",
                     ["pct_revisit_cities", "revisit_ratio", "pct_events_revisit"],
                     index=0, key="f4b_y",
                     format_func=lambda x: {
                         "pct_revisit_cities": "% Revisit-Städte",
                         "revisit_ratio": "Ratio (R/N)",
                         "pct_events_revisit": "% Events in Revisit-Städten"}[x])

df_bx = df_f4.dropna(subset=[y_met, "total_events"]).copy()
G_LBLS = {3: ["Klein", "Mittel", "Groß"],
          4: ["Klein", "Mittel", "Groß", "Sehr groß"],
          5: ["Mini", "Klein", "Mittel", "Groß", "Sehr groß"]}[n_grp]
G_COLORS = ["#2e86c1", "#1a9850", "#1DB954", "#52BE80", "#A9DFBF"]

try:
    df_bx["grp"] = pd.qcut(df_bx["total_events"], q=n_grp,
                           labels=G_LBLS, duplicates="drop")
    fig2 = go.Figure()
    for i, lbl in enumerate(G_LBLS):
        sub = df_bx[df_bx["grp"] == lbl]
        if len(sub) < 2:
            continue
        emin, emax = int(sub["total_events"].min()), int(sub["total_events"].max())
        fig2.add_trace(go.Box(
            y=sub[y_met],
            name=f"{lbl}<br><sub>{emin}–{emax} Events  n={len(sub)}</sub>",
            marker_color=G_COLORS[i],
            line_color=G_COLORS[i],
            fillcolor=G_COLORS[i] + "33",
            boxpoints="outliers",
            marker=dict(size=5, opacity=0.7),
        ))
    y_labels = {"pct_revisit_cities": "% Revisit-Städte",
                "revisit_ratio": "Ratio (Revisit / New)",
                "pct_events_revisit": "% Events in Revisit-Städten"}
    fig2.update_layout(
        title=f"{y_labels[y_met]} nach Tour-Größe",
        yaxis_title=y_labels[y_met],
        template="plotly_dark",
        paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
        font=dict(color="white"), height=430,
        xaxis=dict(gridcolor="#333"), yaxis=dict(gridcolor="#333"),
        showlegend=False,
    )
    with b2:
        st.plotly_chart(fig2, use_container_width=True)

    # Kruskal-Wallis
    kw_arr = [df_bx[df_bx["grp"] == g][y_met].dropna().values
              for g in G_LBLS if len(df_bx[df_bx["grp"] == g]) > 1]
    if len(kw_arr) >= 2:
        kw_h, kw_p = stats.kruskal(*kw_arr)
        meds = df_bx.groupby("grp", observed=True)[y_met].median()
        m_lo, m_hi = float(meds.iloc[0]), float(meds.iloc[-1])
        st.markdown(f"""
        <div class="insight-card">
            <h4>📊 Kruskal-Wallis Test</h4>
            <p>H = {kw_h:.2f} &nbsp;|&nbsp; p = {kw_p:.4f} &nbsp;→&nbsp;
            <strong>{"Signifikanter Unterschied ✅" if kw_p < 0.05 else "Kein signifikanter Unterschied ⚠️"}</strong>
            <br><br>
            Median {y_labels[y_met]}: Klein = <strong>{m_lo:.1f}</strong>
            → Sehr groß = <strong style="color:#1DB954">{m_hi:.1f}</strong>
            (Δ = {m_hi - m_lo:+.1f}).
            {" Größere Touren revisiten anteilig mehr Städte — Superstar-Strategie: bewährte Märkte bevorzugen." if m_hi > m_lo + 3 and kw_p < 0.05
        else " Kleinere Touren haben einen höheren Revisit-Anteil — möglicherweise regionale Fokus-Strategie." if m_lo > m_hi + 3 and kw_p < 0.05
        else " Tour-Größe hat keinen wesentlichen Einfluss auf den Revisit-Anteil."}
            </p>
        </div>
        """, unsafe_allow_html=True)
except Exception as e:
    with b2:
        st.warning(f"Fehler: {e}")

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# GRAPH 3 — Meistbesuchte Städte (Balkendiagramm)
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📊 Graph 3 — Meistbesuchte Städte (alle Artists)</div>',
            unsafe_allow_html=True)
st.markdown("""
Welche Städte werden über alle Artists hinweg am häufigsten angefahren?
Das **horizontale Balkendiagramm** zeigt geografische Konzentration des gesamten Tourings.
""")

if city_df is not None:
    c1, c2 = st.columns([1, 3])
    with c1:
        top_n = st.slider("Top N Städte", 10, 40, 20, key="f4c_n")
        col_metric = st.radio("Farbe nach",
                              ["Besuche gesamt", "Anzahl Artists", "Hauptstadt?"],
                              index=0, key="f4c_col")
        min_art = st.slider("Mindest-Artists", 1, 10, 2, key="f4c_ma")

    city_agg = (
        city_df.groupby(["city", "country"])
        .agg(total_visits=("visits", "sum"),
             n_artists=("artist_name", "nunique"),
             is_capital=("is_capital", "first"))
        .reset_index()
    )
    city_agg = city_agg[city_agg["n_artists"] >= min_art]
    city_top = city_agg.nlargest(top_n, "total_visits").sort_values("total_visits")

    if col_metric == "Besuche gesamt":
        fig3 = px.bar(city_top, x="total_visits", y="city", orientation="h",
                      color="total_visits", color_continuous_scale="YlGn",
                      hover_data={"city": False, "country": True, "total_visits": True,
                                  "n_artists": True, "is_capital": True},
                      labels={"total_visits": "Besuche", "city": ""},
                      template="plotly_dark")
    elif col_metric == "Anzahl Artists":
        fig3 = px.bar(city_top, x="total_visits", y="city", orientation="h",
                      color="n_artists", color_continuous_scale="Blues",
                      hover_data={"city": False, "country": True, "total_visits": True,
                                  "n_artists": True},
                      labels={"total_visits": "Besuche", "city": "", "n_artists": "Artists"},
                      template="plotly_dark")
    else:
        city_top["cap_label"] = city_top["is_capital"].map({1: "Hauptstadt", 0: "Nicht-Hauptstadt",
                                                            True: "Hauptstadt", False: "Nicht-Hauptstadt"})
        fig3 = px.bar(city_top, x="total_visits", y="city", orientation="h",
                      color="cap_label",
                      color_discrete_map={"Hauptstadt": "#1DB954", "Nicht-Hauptstadt": "#4a4a4a"},
                      hover_data={"city": False, "country": True, "total_visits": True},
                      labels={"total_visits": "Besuche", "city": "", "cap_label": ""},
                      template="plotly_dark")

    fig3.update_layout(
        height=max(360, top_n * 22),
        paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
        font=dict(color="white"),
        xaxis=dict(gridcolor="#333"), yaxis=dict(gridcolor="#333"),
        title=f"Top {top_n} meistbesuchte Städte (mind. {min_art} Artists)",
    )
    with c2:
        st.plotly_chart(fig3, use_container_width=True)

    top20 = city_agg.nlargest(20, "total_visits")
    cap20 = int(top20["is_capital"].sum())
    st.markdown(f"""
    <div class="insight-card">
        <h4>🏛️ Hauptstädte in den Top 20</h4>
        <p>
        {cap20} von 20 meistbesuchten Städten sind Hauptstädte ({cap20 / 20 * 100:.0f}%).
        {"Hauptstädte dominieren deutlich — Touring folgt politischen Zentren." if cap20 >= 12
    else "Hauptstädte sind überrepräsentiert, aber wirtschaftliche Zentren sind ebenso wichtig." if cap20 >= 7
    else "Überraschend: Nicht-Hauptstädte dominieren — Musikmetropolen und Wirtschaftszentren sind relevanter."}
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("⚠️  `f4_city_frequencies.csv` fehlt — `join_data.py` ausführen.")

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# GRAPH 4 — Heatmap Tour-Größe × Revisit-Anteil
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🌡️ Graph 4 — Heatmap: Tour-Größe × Revisit-Anteil</div>',
            unsafe_allow_html=True)
st.markdown("""
Die **Heatmap** zeigt wie viele Artists in jeder Kombination aus Tour-Größe (X) und
Revisit-Anteil (Y) landen. Dunkle Felder = viele Artists. Strukturelle Muster —
z.B. ob große Touren systematisch hohe Revisit-Raten haben — werden sofort sichtbar.
""")

try:
    df_hm = df_f4.dropna(subset=["total_events", "pct_revisit_cities"]).copy()
    max_ev = df_hm["total_events"].max()
    ev_bins = [0, 5, 15, 30, 60, max_ev + 1]
    ev_lbls = ["1–5", "6–15", "16–30", "31–60", "61+"]
    rv_bins = [0, 20, 40, 60, 80, 101]
    rv_lbls = ["0–20 %", "21–40 %", "41–60 %", "61–80 %", "81–100 %"]

    df_hm["ev_bin"] = pd.cut(df_hm["total_events"], bins=ev_bins, labels=ev_lbls, right=False)
    df_hm["rv_bin"] = pd.cut(df_hm["pct_revisit_cities"], bins=rv_bins, labels=rv_lbls, right=False)

    pivot = (df_hm.groupby(["rv_bin", "ev_bin"], observed=True)
             .size().unstack("ev_bin").fillna(0).astype(int))

    fig4 = px.imshow(
        pivot,
        labels=dict(x="Tour-Größe (Events)", y="Revisit-Anteil", color="Anzahl Artists"),
        color_continuous_scale="YlGn",
        aspect="auto",
        text_auto=True,
        title="Anzahl Artists je Tour-Größe × Revisit-Anteil",
        template="plotly_dark",
    )
    fig4.update_traces(textfont=dict(size=14, color="white"))
    fig4.update_layout(
        height=320, paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
        font=dict(color="white"),
        coloraxis_colorbar=dict(title="Artists", tickfont=dict(color="white")),
    )
    st.plotly_chart(fig4, use_container_width=True)
except Exception as e:
    st.warning(f"Heatmap Fehler: {e}")

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# ARTIST DETAIL VIEW
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🔍 Artist Detail — Stadtbesuchs-Profil</div>',
            unsafe_allow_html=True)
st.markdown("Wähle einen Artist und sieh exakt welche Städte er wie oft bereist hat.")

if city_df is not None:
    artists_list = sorted(df_f4["artist_name"].dropna().unique().tolist())
    default_artist = (df_f4.loc[df_f4["pct_revisit_cities"].idxmax(), "artist_name"]
                      if len(df_f4) > 0 else artists_list[0])
    default_idx = artists_list.index(default_artist) if default_artist in artists_list else 0
    sel_art = st.selectbox("Artist", options=artists_list,
                           index=default_idx, key="f4_detail")

    art_cities = city_df[city_df["artist_name"] == sel_art].sort_values("visits", ascending=False).copy()
    art_row = df_f4[df_f4["artist_name"] == sel_art]

    if len(art_row) > 0 and len(art_cities) > 0:
        r = art_row.iloc[0]
        d1, d2, d3, d4, d5 = st.columns(5)
        d1.metric("Total Events", int(r["total_events"]))
        d2.metric("Revisit Cities", int(r["revisit_cities"]))
        d3.metric("New Cities", int(r["new_cities"]))
        d4.metric("Revisit-Rate", f"{r['pct_revisit_cities']:.1f}%")
        if pd.notna(r.get("most_visited_city")):
            d5.metric("Meistbesucht", str(r["most_visited_city"]),
                      delta=f"{int(r['most_visited_n'])}×")

        # Balkendiagramm Städtebesuche
        art_cities["Typ"] = art_cities["visits"].apply(
            lambda v: "🟢 Revisit" if v >= 2 else "🔵 New"
        )
        fig5 = px.bar(
            art_cities.head(30),
            x="city", y="visits",
            color="Typ",
            color_discrete_map={"🟢 Revisit": "#1DB954", "🔵 New": "#7fb3d3"},
            hover_data={"city": True, "country": True,
                        "visits": True, "is_capital": True, "Typ": False},
            labels={"visits": "Besuche", "city": "Stadt"},
            title=f"{sel_art} — Stadtbesuche (Top 30)",
            template="plotly_dark",
        )
        fig5.update_layout(
            height=380, paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
            font=dict(color="white"),
            xaxis=dict(gridcolor="#333", tickangle=-35),
            yaxis=dict(gridcolor="#333"),
            legend=dict(title="", orientation="h", y=1.08),
        )
        st.plotly_chart(fig5, use_container_width=True)

        with st.expander("📋 Vollständige Städteliste"):
            show = ["city", "country", "visits", "first_visit", "last_visit", "is_capital", "is_revisit"]
            show = [c for c in show if c in art_cities.columns]
            st.dataframe(art_cities[show], use_container_width=True)
    else:
        st.info("Keine Stadtdaten für diesen Artist.")
else:
    st.info("⚠️  `f4_city_frequencies.csv` fehlt.")

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# ZUSAMMENFASSUNG F4
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">✅ Zusammenfassung — Research Question 4</div>',
            unsafe_allow_html=True)

corr_tmp = df_f4.dropna(subset=["pct_revisit_cities", "total_events"])
r_s, p_s = stats.pearsonr(corr_tmp["pct_revisit_cities"], corr_tmp["total_events"])
r2_s = r_s ** 2

st.markdown(f"""
| Metrik | Wert |
|--------|------|
| Analysierte Artists | {len(df_f4)} |
| Ø Revisit-Rate (% Städte) | {mean_pct:.1f}% |
| Median Revisit-Rate | {median_pct:.1f}% |
| Globaler Ratio (revisit / new) | {global_ratio:.3f} |
| % aller Tourings = Revisit | {global_pct:.1f}% |
| Pearson r (% Revisit vs. Events) | {r_s:.3f} |
| R² | {r2_s:.1%} |
| p-Wert | {p_s:.4f} |
| Signifikant | {'Ja ✅' if p_s < 0.05 else 'Nein ⚠️'} |
""")

st.markdown(f"""
<div class="insight-card">
    <h4>🎯 Antwort auf Research Question 4</h4>
    <p>
    Im Schnitt sind <strong style="color:#1DB954">{mean_pct:.1f}%</strong> der bereisten
    Städte Revisit-Städte. Der globale Ratio beträgt <strong style="color:#1DB954">{global_ratio:.2f}</strong>
    — auf jede neue Stadt kommen {global_ratio:.2f} Revisit-Städte.
    <br><br>
    {
f"Tour-Größe und Revisit-Rate korrelieren <strong>positiv</strong> (r = {r_s:.3f}) — "
"größere Touren setzen stärker auf bewährte Märkte."
if r_s > 0.15 and p_s < 0.05 else
f"Tour-Größe und Revisit-Rate korrelieren <strong>negativ</strong> (r = {r_s:.3f}) — "
"größere Touren erschließen proportional mehr neue Märkte."
if r_s < -0.15 and p_s < 0.05 else
f"Tour-Größe und Revisit-Rate korrelieren kaum (r = {r_s:.3f}) — "
"die Neigung Städte zu revisiten ist unabhängig von der Tour-Größe."
}
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="methodology-note">
    <p>
    <strong>Methodische Anmerkung:</strong>
    "Revisit City" = Stadt die im Ticketmaster-Datensatz (2022–2026) ≥ 2 Events
    eines Artists enthält. Städte werden über den Städtenamen identifiziert (nicht Venue).
    Mehrere Konzerte am selben Tag in der gleichen Stadt zählen als separate Events.
    Events ohne Städteangabe werden ausgeschlossen.
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()


# ══════════════════════════════════════════════════════════════════════════
# RESEARCH QUESTION 6 — CAPITAL vs. NON-CAPITAL CITIES
# ══════════════════════════════════════════════════════════════════════════

# ── F6 Daten laden ─────────────────────────────────────────────────────────
@st.cache_data
def load_f6_data():
    p1 = "data/processed/f6_capitals_visited.csv"
    p2 = "data/processed/f6_capitals_per_artist.csv"
    cap_gl = pd.read_csv(p1) if os.path.exists(p1) else None
    cap_ar = pd.read_csv(p2) if os.path.exists(p2) else None
    return cap_gl, cap_ar


cap_global, cap_per_artist = load_f6_data()

F6_COLS = ["capital_events", "non_capital_events", "pct_capital",
           "capital_ratio", "unique_capitals", "unique_non_capitals", "pct_capital_cities"]
f6_missing = [c for c in F6_COLS if c not in df.columns]

st.markdown("""
<div class="rq-box">
    <h3>🔬 Research Question 6</h3>
    <p>What proportion of an artist's performances take place in capital cities
    compared to non-capital cities?</p>
</div>
""", unsafe_allow_html=True)

if f6_missing:
    st.error(f"⚠️  F6-Spalten fehlen: {f6_missing} — `join_data.py` erneut ausführen.")
    st.stop()

st.markdown("""
**Definitionen**

| Begriff | Bedeutung |
|---------|-----------|
| **Capital Event** | Konzert in einer Hauptstadt (klassifiziert via RestCountries API) |
| **pct_capital** | Capital Events / Total Events × 100 — misst **Anteil am Konzertvolumen** |
| **pct_capital_cities** | Einzigartige Hauptstädte / Alle einzigartigen Städte × 100 — misst **geografische Breite** |
| **capital_ratio** | Capital Events / Non-Capital Events — wie viele Nicht-Hauptstadtshows pro Hauptstadtshow |
| **unique_capitals** | Anzahl verschiedener Hauptstädte die ein Artist bereist |

**Warum zwei Metriken (pct_capital vs. pct_capital_cities)?**
Ein Artist der dreimal in Berlin und einmal in München spielt hat
`pct_capital = 75%` aber `pct_capital_cities = 50%`.
Beide Perspektiven sind relevant — Volumen vs. geografische Strategie.

**Hypothese:** Populärere Artists (mehr Listeners) spielen anteilig öfter in Hauptstädten —
weil Hauptstädte größere Venues, mehr Presseaufmerksamkeit und dichteren Fanmarkt bieten.
""")

# Daten vorbereiten
for c in F6_COLS:
    df[c] = pd.to_numeric(df[c], errors="coerce")

df_f6 = df.dropna(subset=["capital_events", "non_capital_events"]).copy()

# Globale Kennzahlen
total_cap = df_f6["capital_events"].sum()
total_non = df_f6["non_capital_events"].sum()
total_all = total_cap + total_non
glob_pct = total_cap / total_all * 100 if total_all > 0 else 0
glob_ratio = total_cap / total_non if total_non > 0 else 0
mean_pct = df_f6["pct_capital"].mean()
med_pct = df_f6["pct_capital"].median()

st.divider()
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Ø pct_capital", f"{mean_pct:.1f}%", delta=f"Median {med_pct:.1f}%")
k2.metric("Global Capital-Anteil", f"{glob_pct:.1f}%")
k3.metric("Capital Events gesamt", f"{total_cap:.0f}")
k4.metric("Non-Capital Events", f"{total_non:.0f}")
k5.metric("Ratio (cap/non-cap)", f"{glob_ratio:.3f}")
st.divider()

# ══════════════════════════════════════════════════════════════════════════
# F6 — GRAPH 1: Balkendiagramm pct_capital nach Listeners-Gruppe
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📊 Graph 1 — Ø Capital-Anteil nach Popularitäts-Tier</div>',
            unsafe_allow_html=True)
st.markdown("""
Künstler werden nach Last.fm Listeners in 4 Gruppen eingeteilt.
Das **Balkendiagramm** zeigt den durchschnittlichen Capital-Anteil pro Gruppe —
direkte Antwort auf die Hypothese: spielen populärere Artists öfter in Hauptstädten?
""")

g1, g2 = st.columns([1, 3])
with g1:
    n_tiers_f6 = st.select_slider("Anzahl Gruppen", [3, 4, 5], value=4, key="f6b_nt")
    bar_metric = st.radio("Metrik",
                          ["pct_capital", "pct_capital_cities", "unique_capitals"],
                          index=0, key="f6b_m",
                          format_func=lambda x: {
                              "pct_capital": "% Capital Events",
                              "pct_capital_cities": "% Capital Städte",
                              "unique_capitals": "Ø Hauptstädte besucht"}[x])
    groupby_col = st.radio("Gruppiert nach",
                           ["listeners", "total_events"],
                           index=0, key="f6b_gc",
                           format_func=lambda x: {"listeners": "Listeners", "total_events": "Tour-Größe"}[x])

df_b6 = df_f6.dropna(subset=[bar_metric, groupby_col]).copy()
df_b6[groupby_col] = pd.to_numeric(df_b6[groupby_col], errors="coerce")
df_b6 = df_b6.dropna(subset=[groupby_col])

g_lbls_f6 = {
    3: ["Niedrig", "Mittel", "Hoch"],
    4: ["Q1 Niedrig", "Q2", "Q3", "Q4 Hoch"],
    5: ["Q1", "Q2", "Q3", "Q4", "Q5 Hoch"],
}[n_tiers_f6]
G_COLORS_F6 = ["#4a4a4a", "#7fb3d3", "#1a9850", "#1DB954", "#52BE80"][:n_tiers_f6]

try:
    df_b6["tier"] = pd.qcut(df_b6[groupby_col], q=n_tiers_f6,
                            labels=g_lbls_f6, duplicates="drop")
    grp6 = df_b6.groupby("tier", observed=True)[bar_metric].agg(["mean", "median", "count"]).reset_index()
    grp6.columns = ["tier", "mean", "median", "n"]

    fig_b6 = go.Figure()
    fig_b6.add_trace(go.Bar(
        x=grp6["tier"].astype(str),
        y=grp6["mean"],
        marker=dict(color=G_COLORS_F6),
        text=[f"{v:.1f}" for v in grp6["mean"]],
        textposition="outside",
        textfont=dict(color="white", size=13, family="monospace"),
        customdata=grp6[["median", "n"]].values,
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Mittelwert: %{y:.1f}<br>"
            "Median: %{customdata[0]:.1f}<br>"
            "n Artists: %{customdata[1]}<extra></extra>"
        )
    ))
    y_label_map = {"pct_capital": "Ø % Capital Events",
                   "pct_capital_cities": "Ø % Capital Städte",
                   "unique_capitals": "Ø Hauptstädte besucht"}
    fig_b6.update_layout(
        title=f"{y_label_map[bar_metric]} nach {groupby_col.replace('_', ' ').title()}-Tier",
        yaxis_title=y_label_map[bar_metric],
        xaxis_title=f"{groupby_col.replace('_', ' ').title()}-Gruppe",
        template="plotly_dark",
        paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
        font=dict(color="white"), height=400,
        xaxis=dict(gridcolor="#333"), yaxis=dict(gridcolor="#333"),
        showlegend=False,
    )
    with g2:
        st.plotly_chart(fig_b6, use_container_width=True)

    # Kruskal-Wallis
    kw_arr = [df_b6[df_b6["tier"] == g][bar_metric].dropna().values
              for g in g_lbls_f6 if len(df_b6[df_b6["tier"] == g]) > 1]
    if len(kw_arr) >= 2:
        kw_h, kw_p = stats.kruskal(*kw_arr)
        m_lo = float(grp6["mean"].iloc[0])
        m_hi = float(grp6["mean"].iloc[-1])
        st.markdown(f"""
        <div class="insight-card">
            <h4>📊 Kruskal-Wallis Test</h4>
            <p>H = {kw_h:.2f} &nbsp;|&nbsp; p = {kw_p:.4f} &nbsp;→&nbsp;
            <strong>{"Signifikant ✅" if kw_p < 0.05 else "Nicht signifikant ⚠️"}</strong>
            <br><br>
            {y_label_map[bar_metric]}: Niedrigster Tier = <strong>{m_lo:.1f}</strong>
            → Höchster Tier = <strong style="color:#1DB954">{m_hi:.1f}</strong>
            (Δ = {m_hi - m_lo:+.1f}).&nbsp;
            {"Populärere Artists spielen anteilig mehr in Hauptstädten." if m_hi > m_lo + 3 and kw_p < 0.05
        else "Populärere Artists spielen anteilig weniger in Hauptstädten — breitere Streuung auf nicht-Hauptstädte." if m_lo > m_hi + 3 and kw_p < 0.05
        else "Kein wesentlicher Unterschied zwischen den Popularity-Gruppen."}
            </p>
        </div>
        """, unsafe_allow_html=True)
except Exception as e:
    with g2:
        st.warning(f"Fehler: {e}")

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# F6 — GRAPH 2: Scatterplot pct_capital vs Listeners
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📈 Graph 2 — Scatterplot: pct_capital vs. Last.fm Listeners</div>',
            unsafe_allow_html=True)
st.markdown("""
Jeder Punkt = ein Artist. X = log₁₀(Listeners), Y = % Capital Events.
Die **OLS-Trendlinie** zeigt ob der Zusammenhang linear ist —
positiv = populärere Artists spielen mehr in Hauptstädten.
""")

sc6_1, sc6_2 = st.columns([1, 3])
with sc6_1:
    sc6_y = st.radio("Y-Achse",
                     ["pct_capital", "pct_capital_cities"],
                     index=0, key="f6s_y",
                     format_func=lambda x: {"pct_capital": "% Capital Events",
                                            "pct_capital_cities": "% Capital Städte"}[x])
    sc6_logy = st.checkbox("Log Y-Achse", value=False, key="f6s_logy")
    sc6_lbls = st.checkbox("Namen anzeigen", value=False, key="f6s_lbl")
    sc6_min = st.slider("Mindest-Events", 1, 20, 3, key="f6s_min")

df_sc6 = df_f6[df_f6["total_events"] >= sc6_min].dropna(
    subset=[sc6_y, "listeners"]).copy()
df_sc6["listeners"] = pd.to_numeric(df_sc6["listeners"], errors="coerce")
df_sc6 = df_sc6.dropna(subset=["listeners"])

if len(df_sc6) >= 5:
    x_v = np.log10(df_sc6["listeners"] + 1)
    y_v = np.log10(df_sc6[sc6_y] + 1) if sc6_logy else df_sc6[sc6_y]
    r6, p6 = stats.pearsonr(x_v, y_v)
    r2_6 = r6 ** 2

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("n Artists", len(df_sc6))
    m2.metric("Pearson r", f"{r6:.3f}")
    m3.metric("R²", f"{r2_6:.1%}")
    m4.metric("p-Wert", f"{p6:.4f}",
              delta="signifikant ✅" if p6 < 0.05 else "nicht signifikant ⚠️",
              delta_color="normal" if p6 < 0.05 else "inverse")

    df_sc6["x_plot"] = x_v.values
    df_sc6["y_plot"] = y_v.values

    y_lbl_map = {"pct_capital": "% Capital Events", "pct_capital_cities": "% Capital Städte"}

    # OLS-Trendlinie manuell (kein statsmodels nötig)
    coef = np.polyfit(df_sc6["x_plot"], df_sc6["y_plot"], 1)
    x_line = np.linspace(df_sc6["x_plot"].min(), df_sc6["x_plot"].max(), 200)
    y_line = np.polyval(coef, x_line)

    fig_sc6 = px.scatter(
        df_sc6, x="x_plot", y="y_plot",
        hover_name="artist_name",
        hover_data={"x_plot": False, "y_plot": False,
                    "listeners": ":,", sc6_y: ":.1f", "total_events": True},
        color="pct_capital",
        color_continuous_scale="RdYlGn",
        text="artist_name" if sc6_lbls else None,
        labels={"x_plot": "log₁₀(Last.fm Listeners)",
                "y_plot": ("log₁₀(" if sc6_logy else "") + y_lbl_map[sc6_y] + (")" if sc6_logy else "")},
        title=f"{y_lbl_map[sc6_y]} vs. Last.fm Listeners  |  r = {r6:.3f}  |  n = {len(df_sc6)}",
        template="plotly_dark",
    )
    fig_sc6.add_trace(go.Scatter(
        x=x_line, y=y_line,
        mode="lines", name="OLS",
        line=dict(color="#1DB954", width=2.5),
        hoverinfo="skip",
    ))
    fig_sc6.update_traces(marker=dict(size=9, opacity=0.85,
                                      line=dict(width=0.5, color="white")),
                          selector=dict(mode="markers"))
    if sc6_lbls:
        fig_sc6.update_traces(textposition="top center",
                              textfont=dict(size=8, color="white"),
                              selector=dict(mode="markers+text"))
    fig_sc6.update_layout(
        height=510, paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
        font=dict(color="white"),
        xaxis=dict(gridcolor="#333"), yaxis=dict(gridcolor="#333"),
        coloraxis_showscale=False,
    )
    with sc6_2:
        st.plotly_chart(fig_sc6, use_container_width=True)

    strength = "stark" if abs(r6) >= 0.7 else "moderat" if abs(r6) >= 0.4 else "schwach"
    st.markdown(f"""
    <div class="insight-card">
        <h4>🔍 Interpretation</h4>
        <p>
        r = <strong style="color:#1DB954">{r6:.3f}</strong> →
        <strong>{strength}e {"positive" if r6 > 0 else "negative"} Korrelation</strong>,
        R² = {r2_6:.1%},
        {"statistisch signifikant ✅" if p6 < 0.05 else "nicht signifikant ⚠️"}.
        <br><br>
        {"Populärere Artists spielen anteilig mehr in Hauptstädten — Hauptstädte bieten größere Venues und höhere Presseabdeckung." if r6 > 0.2 and p6 < 0.05
    else "Populärere Artists spielen anteilig weniger in Hauptstädten — größere Touren erschließen mehr nicht-Hauptstadt-Märkte." if r6 < -0.2 and p6 < 0.05
    else "Listeners und Capital-Anteil korrelieren kaum — die Entscheidung für Hauptstädte ist nicht primär von der digitalen Popularität abhängig."}
        </p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# F6 — GRAPH 3: Meistbesuchte Hauptstädte (global)
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📊 Graph 3 — Meistbesuchte Hauptstädte (alle Artists)</div>',
            unsafe_allow_html=True)
st.markdown("""
Welche Hauptstädte werden über alle Artists hinweg am häufigsten angefahren?
Farbe = Anzahl verschiedener Artists — zeigt ob eine Hauptstadt breite
Relevanz hat oder von wenigen Artists dominiert wird.
""")

if cap_global is not None and len(cap_global) > 0:
    h1, h2 = st.columns([1, 3])
    with h1:
        top_n_h = st.slider("Top N Hauptstädte", 10, 30, 20, key="f6h_n")
        h_color = st.radio("Farbe",
                           ["Besuche gesamt", "Anzahl Artists"],
                           index=0, key="f6h_col")

    cap_top = cap_global.nlargest(top_n_h, "total_visits").sort_values("total_visits")

    fig_h = px.bar(
        cap_top,
        x="total_visits", y="city", orientation="h",
        color="total_visits" if h_color == "Besuche gesamt" else "n_artists",
        color_continuous_scale="YlGn",
        hover_data={"city": False, "country": True,
                    "total_visits": True, "n_artists": True},
        labels={"total_visits": "Besuche gesamt", "city": "", "n_artists": "Anzahl Artists"},
        title=f"Top {top_n_h} Hauptstädte nach Konzertbesuchen",
        template="plotly_dark",
    )
    fig_h.update_layout(
        height=max(340, top_n_h * 22),
        paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
        font=dict(color="white"),
        xaxis=dict(gridcolor="#333"), yaxis=dict(gridcolor="#333"),
        coloraxis_colorbar=dict(title="Besuche" if h_color == "Besuche gesamt" else "Artists"),
    )
    with h2:
        st.plotly_chart(fig_h, use_container_width=True)

    top3 = cap_top.nlargest(3, "total_visits")["city"].tolist()
    most_diverse = cap_global.nlargest(1, "n_artists").iloc[0]
    st.markdown(f"""
    <div class="insight-card">
        <h4>🏆 Top Hauptstädte</h4>
        <p>
        Die drei meistbesuchten Hauptstädte sind
        <strong style="color:#1DB954">{", ".join(top3)}</strong>.
        Die Hauptstadt mit den meisten verschiedenen Artists:
        <strong>{most_diverse['city']}</strong>
        ({int(most_diverse['n_artists'])} verschiedene Artists,
        {int(most_diverse['total_visits'])} Besuche insgesamt).
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("⚠️  `f6_capitals_visited.csv` fehlt — `join_data.py` ausführen.")

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# F6 — GRAPH 4: Heatmap pct_capital × Listeners-Tier
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🌡️ Graph 4 — Heatmap: Capital-Anteil × Popularity-Tier</div>',
            unsafe_allow_html=True)
st.markdown("""
Die **Heatmap** zeigt wie viele Artists in jeder Kombination aus
Popularity-Tier (X) und Capital-Anteil (Y) landen.
Konzentriert sich die Diagonale oben-rechts (populär = mehr Capitals) oder ist sie flach?
""")

try:
    df_hm6 = df_f6.dropna(subset=["listeners", "pct_capital"]).copy()
    df_hm6["listeners"] = pd.to_numeric(df_hm6["listeners"], errors="coerce")
    df_hm6 = df_hm6.dropna(subset=["listeners"])

    max_pc = df_hm6["pct_capital"].max()
    pc_bins = [0, 20, 40, 60, 80, max(101, max_pc + 1)]
    pc_lbls = ["0–20 %", "21–40 %", "41–60 %", "61–80 %", "81–100 %"]
    ls_lbls = ["Q1 Niedrig", "Q2", "Q3", "Q4 Hoch"]

    df_hm6["pc_bin"] = pd.cut(df_hm6["pct_capital"], bins=pc_bins,
                              labels=pc_lbls, right=False)
    df_hm6["ls_bin"] = pd.qcut(df_hm6["listeners"], q=4,
                               labels=ls_lbls, duplicates="drop")

    pivot6 = (df_hm6.groupby(["pc_bin", "ls_bin"], observed=True)
              .size().unstack("ls_bin").fillna(0).astype(int))

    fig_hm6 = px.imshow(
        pivot6,
        labels=dict(x="Popularity-Tier (Listeners)", y="Capital-Anteil", color="Anzahl Artists"),
        color_continuous_scale="YlGn",
        aspect="auto", text_auto=True,
        title="Anzahl Artists je Capital-Anteil × Popularity-Tier",
        template="plotly_dark",
    )
    fig_hm6.update_traces(textfont=dict(size=14, color="white"))
    fig_hm6.update_layout(
        height=300, paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
        font=dict(color="white"),
        coloraxis_colorbar=dict(title="Artists"),
    )
    st.plotly_chart(fig_hm6, use_container_width=True)
except Exception as e:
    st.warning(f"Heatmap Fehler: {e}")

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# F6 — ARTIST DETAIL
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🔍 Artist Detail — Hauptstadt-Profil</div>',
            unsafe_allow_html=True)
st.markdown("Welche Hauptstädte bereist ein Artist — und wie oft?")

if cap_per_artist is not None:
    art_list6 = sorted(df_f6["artist_name"].dropna().unique().tolist())
    def_art6 = (df_f6.loc[df_f6["pct_capital"].idxmax(), "artist_name"]
                if len(df_f6) > 0 else art_list6[0])
    def_idx6 = art_list6.index(def_art6) if def_art6 in art_list6 else 0
    sel_art6 = st.selectbox("Artist", options=art_list6,
                            index=def_idx6, key="f6_detail")

    art_row6 = df_f6[df_f6["artist_name"] == sel_art6]
    art_caps = cap_per_artist[cap_per_artist["artist_name"] == sel_art6].sort_values(
        "visits", ascending=False)

    if len(art_row6) > 0:
        r6d = art_row6.iloc[0]
        d1, d2, d3, d4, d5 = st.columns(5)
        d1.metric("Total Events", int(r6d["total_events"]))
        d2.metric("Capital Events", int(r6d["capital_events"]))
        d3.metric("Non-Capital Events", int(r6d["non_capital_events"]))
        d4.metric("% Capital", f"{r6d['pct_capital']:.1f}%")
        d5.metric("Hauptstädte besucht", int(r6d["unique_capitals"]))

    if len(art_caps) > 0:
        fig_det6 = px.bar(
            art_caps, x="city", y="visits",
            hover_data={"city": True, "country": True, "visits": True},
            color="visits", color_continuous_scale="YlGn",
            labels={"visits": "Besuche", "city": "Hauptstadt"},
            title=f"{sel_art6} — Hauptstadtbesuche",
            template="plotly_dark",
        )
        fig_det6.update_layout(
            height=350, paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
            font=dict(color="white"),
            xaxis=dict(gridcolor="#333", tickangle=-30),
            yaxis=dict(gridcolor="#333"),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_det6, use_container_width=True)
    else:
        st.info(f"{sel_art6} hat keine Hauptstadtkonzerte im Dataset.")
else:
    st.info("⚠️  `f6_capitals_per_artist.csv` fehlt.")

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# ZUSAMMENFASSUNG F6
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">✅ Zusammenfassung — Research Question 6</div>',
            unsafe_allow_html=True)

corr6 = df_f6.dropna(subset=["pct_capital", "listeners"]).copy()
corr6["listeners"] = pd.to_numeric(corr6["listeners"], errors="coerce")
corr6 = corr6.dropna(subset=["listeners"])
r6_s = p6_s = None
if len(corr6) >= 5:
    r6_s, p6_s = stats.pearsonr(np.log10(corr6["listeners"] + 1), corr6["pct_capital"])

st.markdown(f"""
| Metrik | Wert |
|--------|------|
| Analysierte Artists | {len(df_f6)} |
| Globaler Capital-Anteil (Events) | {glob_pct:.1f}% |
| Ø pct_capital pro Artist | {mean_pct:.1f}% |
| Median pct_capital | {med_pct:.1f}% |
| Ratio Capital / Non-Capital | {glob_ratio:.3f} |
| Ø Hauptstädte besucht / Artist | {df_f6['unique_capitals'].mean():.1f} |
| Ø pct_capital_cities | {df_f6['pct_capital_cities'].mean():.1f}% |
| Pearson r (log Listeners → pct_capital) | {f'{r6_s:.3f}' if r6_s is not None else 'n/a'} |
| p-Wert | {f'{p6_s:.4f}' if p6_s is not None else 'n/a'} |
""")

if r6_s is not None:
    strength6 = "stark" if abs(r6_s) >= 0.7 else "moderat" if abs(r6_s) >= 0.4 else "schwach"
    st.markdown(f"""
    <div class="insight-card">
        <h4>🎯 Antwort auf Research Question 6</h4>
        <p>
        Im Durchschnitt finden <strong style="color:#1DB954">{mean_pct:.1f}%</strong>
        aller Konzerte in Hauptstädten statt — global über alle Artists.
        Jeder Artist besucht im Schnitt
        <strong style="color:#1DB954">{df_f6['unique_capitals'].mean():.1f}</strong>
        verschiedene Hauptstädte.
        <br><br>
        Der Zusammenhang zwischen Popularität (Last.fm Listeners) und Capital-Anteil
        ist <strong>{strength6}</strong> (r = {r6_s:.3f},
        {"signifikant ✅" if p6_s < 0.05 else "nicht signifikant ⚠️"}).
        {
    " Populärere Artists konzentrieren sich stärker auf Hauptstädte." if r6_s > 0.2 and p6_s < 0.05
    else " Populärere Artists bereisen breitere Märkte — ihr Capital-Anteil ist niedriger." if r6_s < -0.2 and p6_s < 0.05
    else " Popularität ist kein wesentlicher Treiber des Capital-Anteils."
    }
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="methodology-note">
    <p>
    <strong>Methodische Anmerkung:</strong>
    Hauptstädte klassifiziert via RestCountries API (<code>get_capitals.py</code>) —
    245 Hauptstädte weltweit. Matching erfolgt über Städtenamen (case-insensitive).
    Städte die sowohl Haupt- als auch Wirtschaftszentrum sind (z.B. London, Paris)
    können den Capital-Anteil verzerren. Events ohne Städtenamen werden ausgeschlossen.
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()
st.markdown("**Weiter mit:** F5 — Genre Density 300km  *(Reformulierung ausstehend)*")
