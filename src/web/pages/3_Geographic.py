import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import os

import sys as _sys, os as _os

from components.util import hex_rgba

_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from components.styles import apply_styles
from components.navbar import render_navbar
from components.glossary import apply_glossary_styles, tt

st.set_page_config(
    page_title="Geographic Analysis",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed"
)
apply_styles()
render_navbar()
apply_glossary_styles()

# ── CSS ───────────────────────────────────────────────────────────────────


# ── Header ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#7C89A3;margin-bottom:10px;">📋 Graph Explanation</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">This scatterplot visualises the touring geography of each artist by comparing the number of<br>new cities (x-axis) against the number of revisit cities (y-axis) on their tour.<br>Each dot represents one artist. The dashed diagonal line marks a ratio of 1:1 — meaning<br>an artist revisits exactly as many cities as they visit for the first time.<br>Artists plotted <strong>above</strong> the diagonal line revisit more cities than they explore new ones,<br>suggesting a strategy focused on proven, established markets.<br>Artists plotted <strong>below</strong> the line visit more new cities than they return to,<br>indicating a broader geographical expansion approach.<br>The colour of each dot can be adjusted to encode a third variable — total number of events,<br>percentage of revisit cities, or total Last.fm listeners — allowing additional patterns<br>to be explored visually.<br>This graph directly contributes to answering Research Question 1 by showing at a glance<br>whether artists tend to favour familiar markets or actively explore new territory.</p></div>
</div>
""", unsafe_allow_html=True)

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

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #6366f1;border-radius:10px;padding:18px 22px;margin-bottom:12px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#818cf8;margin-bottom:10px;">📊 Statistical Analysis</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">The dashed diagonal reference line (ratio = 1) serves as the key benchmark: any artist above<br>it has more revisit cities than new cities, and vice versa. The distribution card below the<br>chart shows the exact percentage split, giving a simple but powerful statistical summary of<br>touring behaviour across the full dataset. When colour-encoded by total events, clustering of<br>brighter dots (larger tours) on one side of the diagonal would indicate a systematic<br>relationship between tour scale and revisit behaviour — a hypothesis tested more rigorously<br>in Graph 2.</p></div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #10b981;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#10b981;margin-bottom:10px;">🔍 Interpretation</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">This graph gives an immediate visual overview of how artists balance exploration and<br>consolidation in their touring strategies. A concentration of artists above the diagonal<br>suggests that revisiting established markets is the dominant strategy — artists prefer the<br>safety of cities where they have already proven audience demand. A spread of artists below<br>the diagonal would indicate the opposite: a preference for geographic expansion. The<br>interactive filters allow the reader to isolate specific subsets (e.g. only large-scale tours)<br>to examine whether touring scale influences this balance, directly informing the answer to<br>Research Question 1.</p></div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# GRAPH 2 — Box Plot Revisit-Rate nach Tour-Größe
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📦 Graph 2 — Revisit Rate by Tour Size: Does Scale Drive Consolidation?</div>',
            unsafe_allow_html=True)

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#7C89A3;margin-bottom:10px;">📋 Graph Explanation</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">This box plot examines whether an artist's tour size influences their tendency to revisit<br>cities. Artists are divided into groups based on the total number of events on their tour<br>(small, medium, large, very large — adjustable via the slider), and for each group the<br>distribution of the revisit metric is shown as a box plot.</p>
<p style="margin:0 0 10px 0;">Each box shows the interquartile range (middle 50% of artists), the horizontal line inside<br>the box is the median, the whiskers extend to the furthest non-outlier values, and individual<br>dots beyond the whiskers are statistical outliers. The y-axis can be switched between three<br>metrics: percentage of revisit cities, the raw revisit ratio, or the percentage of all events<br>taking place in revisit cities.</p>
<p style="margin:0 0 10px 0;">This graph is designed to test the hypothesis stated under Research Question 1: that larger<br>tours tend to favour established markets (higher revisit rates), while smaller tours spread<br>more broadly into new territory.</p></div>
</div>
""", unsafe_allow_html=True)

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
            marker_color=G_COLORS[i],  # type: ignore
            line_color=G_COLORS[i],  # type: ignore
            fillcolor=hex_rgba(G_COLORS[i]),
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

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #6366f1;border-radius:10px;padding:18px 22px;margin-bottom:12px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#818cf8;margin-bottom:10px;">📊 Statistical Analysis</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">The Kruskal-Wallis test is a non-parametric statistical test that checks whether the<br>distributions of a variable differ significantly across multiple independent groups. It is<br>used here instead of a standard ANOVA because revisit rate data may not follow a normal<br>distribution.</p>
<p style="margin:0 0 10px 0;">• <strong>H statistic</strong>: A larger H value indicates greater differences between the group<br>  distributions. It is calculated from the ranked values across all groups.<br>• <strong>p-value</strong>: The probability of observing these group differences by chance alone, assuming<br>  no real effect exists. A p-value below 0.05 is conventionally considered statistically<br>  significant, meaning the observed differences are unlikely to be random.<br>• <strong>Median difference (Δ)</strong>: The raw difference between the median revisit rate of the<br>  smallest and largest tour-size group. A positive Δ means larger tours have higher revisit<br>  rates; a negative Δ means the opposite.</p>
<p style="margin:0 0 10px 0;">If the p-value is significant and Δ is notably positive, this supports the hypothesis that<br>larger-scale artists adopt a consolidation strategy. If the p-value is not significant, tour<br>size does not reliably predict revisit behaviour.</p></div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #10b981;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#10b981;margin-bottom:10px;">🔍 Interpretation</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">This graph directly tests the central hypothesis of Research Question 1. If the box plots<br>show a clear upward trend across tour-size groups — with larger tours having higher median<br>revisit rates and a statistically significant Kruskal-Wallis result — it would confirm that<br>scale drives consolidation: bigger artists return to cities they know rather than expanding<br>into uncharted territory. Conversely, if medians are similar across groups or the test is<br>not significant, revisit behaviour appears to be an individual artistic choice independent of<br>how large the tour is.</p></div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# GRAPH 3 — Meistbesuchte Städte (Balkendiagramm)
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📊 Graph 3 — Most Visited Cities Across All Artists</div>',
            unsafe_allow_html=True)

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#7C89A3;margin-bottom:10px;">📋 Graph Explanation</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">This horizontal bar chart shows which cities are visited most frequently when aggregating<br>all artists in the dataset together. Each bar represents one city, and its length corresponds<br>to the total number of artist visits recorded for that city across the entire observation<br>period. The chart can be coloured by total visits, by the number of distinct artists who<br>performed there, or by whether the city is a capital city.</p>
<p style="margin:0 0 10px 0;">A minimum artist threshold (adjustable slider) filters out cities that only appear in a<br>single artist's dataset, ensuring the results reflect cities with genuine cross-artist<br>relevance rather than individual outliers.</p>
<p style="margin:0 0 10px 0;">This chart provides the geographic "big picture" of touring: which cities function as<br>central hubs of live music activity, and whether the most visited cities are primarily<br>national capitals or economic/cultural centres.</p></div>
</div>
""", unsafe_allow_html=True)

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

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #6366f1;border-radius:10px;padding:18px 22px;margin-bottom:12px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#818cf8;margin-bottom:10px;">📊 Statistical Analysis</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">The insight card below the chart reports the proportion of capital cities within the top 20<br>most-visited cities. This simple count-based statistic (number of capitals out of 20) serves<br>as an early indicator for Research Question 2 on capital city preferences. A proportion<br>above 60% (12 out of 20) suggests capital cities are systematically over-represented in<br>touring routes relative to their share of all cities worldwide, pointing to a structural<br>bias in how tours are planned.</p></div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #10b981;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#10b981;margin-bottom:10px;">🔍 Interpretation</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">This chart reveals the geographic concentration of live music activity. A highly unequal<br>distribution — where a small number of cities account for a disproportionately large share<br>of all visits — indicates that touring is not geographically uniform. If a handful of major<br>cities (London, Paris, Berlin, etc.) dominate the rankings, it suggests that artists<br>converge on the same established markets rather than distributing evenly. This has direct<br>implications for Research Question 1: cities that appear frequently across many artists are<br>the very definition of "proven markets" — the cities most likely to be revisited. Switching<br>the colour encoding to "Number of Artists" further reveals whether high-visit cities owe<br>their ranking to one or two very active artists, or whether they attract broad cross-artist<br>interest.</p></div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# GRAPH 4 — Heatmap Tour-Größe × Revisit-Anteil
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🌡️ Graph 4 — Heatmap: Concentration of Artists by Tour Size and Revisit Rate</div>',
            unsafe_allow_html=True)

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#7C89A3;margin-bottom:10px;">📋 Graph Explanation</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">This heatmap provides a two-dimensional frequency view of the relationship between tour size<br>(x-axis, number of events) and revisit rate (y-axis, percentage of cities that are revisit<br>cities). Each cell in the grid represents a combination of tour-size bracket and revisit-rate<br>bracket, and the number displayed inside the cell — as well as the colour intensity — shows<br>how many artists fall into that particular combination.</p>
<p style="margin:0 0 10px 0;">Darker (more intense) cells indicate that many artists share a particular combination of<br>tour size and revisit rate. A diagonal pattern running from the bottom-left to the top-right<br>would suggest a positive relationship (larger tours → higher revisit rates), while a flat or<br>random distribution would indicate that tour size and revisit behaviour are independent.</p>
<p style="margin:0 0 10px 0;">This heatmap complements Graph 2 by offering a count-based population view rather than a<br>distributional one, making it easy to identify where the majority of artists are clustered.</p></div>
</div>
""", unsafe_allow_html=True)

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

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #6366f1;border-radius:10px;padding:18px 22px;margin-bottom:12px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#818cf8;margin-bottom:10px;">📊 Statistical Analysis</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">The heatmap uses raw counts (number of artists) rather than statistical test results. Its<br>analytical value lies in the spatial distribution of these counts across the grid. Key<br>patterns to look for:</p>
<p style="margin:0 0 10px 0;">• <strong>Row concentration</strong>: If most artists are concentrated in the middle revisit-rate rows<br>  (21–60%), it suggests that extreme revisit behaviour (either very high or very low) is<br>  rare, and most artists adopt a mixed strategy.<br>• <strong>Column concentration</strong>: If smaller tour-size columns (1–5, 6–15 events) contain the<br>  most artists, this reflects the natural distribution of the dataset — most artists are<br>  smaller-scale.<br>• <strong>Diagonal shift</strong>: Comparing where the densest cells sit across columns reveals whether<br>  larger tours systematically occupy higher revisit-rate rows, supporting the hypothesis<br>  tested in Graph 2.</p></div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #10b981;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#10b981;margin-bottom:10px;">🔍 Interpretation</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">The heatmap is particularly useful for identifying structural patterns that averages or<br>medians can obscure. For example, even if the median revisit rate does not differ much<br>across tour-size groups (as tested in Graph 2), the heatmap might reveal that a large tour<br>group contains two distinct subgroups — one with very high and one with very low revisit<br>rates — which would average out to a misleading middle value. This makes the heatmap an<br>important complementary view for Research Question 1, as it shows not just central<br>tendencies but the full shape of the joint distribution between tour size and revisiting<br>behaviour.</p></div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# ARTIST DETAIL VIEW
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🔍 Artist Detail — City Visit Profile</div>',
            unsafe_allow_html=True)

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#7C89A3;margin-bottom:10px;">📋 Graph Explanation</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">This interactive bar chart provides a city-level breakdown for a single selected artist.<br>Each bar represents one city (up to the top 30 most visited), and its height shows the<br>number of times that artist performed there. Bars are colour-coded to distinguish revisit<br>cities (visited 2 or more times, shown in green) from new cities (visited only once, shown<br>in blue).</p>
<p style="margin:0 0 10px 0;">The KPI metrics above the chart provide a summary of the selected artist's overall revisit<br>profile: total events, number of revisit and new cities, revisit rate, and the single<br>most-visited city. The expandable table below the chart shows the complete city list<br>including first and last visit dates, country, and capital status.</p>
<p style="margin:0 0 10px 0;">This detail view allows the reader to move from the aggregated patterns seen in Graphs 1–4<br>down to the individual artist level, making abstract statistics tangible and verifiable.</p></div>
</div>
""", unsafe_allow_html=True)

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

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #6366f1;border-radius:10px;padding:18px 22px;margin-bottom:12px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#818cf8;margin-bottom:10px;">📊 Statistical Analysis</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">The key metric shown in the KPI row is the revisit rate (pct_revisit_cities), which expresses<br>the share of an artist's toured cities that were visited more than once. The colour split<br>in the bar chart gives a visual decomposition of this rate: the proportion of green bars to<br>blue bars directly reflects the revisit rate percentage. Artists with very high revisit rates<br>will show predominantly green bars concentrated on a small number of heavily visited cities,<br>whereas artists with low revisit rates will show a wide spread of single-visit blue bars.</p></div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #10b981;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#10b981;margin-bottom:10px;">🔍 Interpretation</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">By examining individual artists through this detail view, the reader can assess whether the<br>aggregate patterns found in Graphs 1–4 hold at the individual level. For instance, an artist<br>with an unusually high revisit rate might be concentrated in a single country or region,<br>returning repeatedly to the same major cities on separate tour legs. Conversely, an artist<br>with a low revisit rate may be on a first-time world tour, systematically visiting new<br>markets. These individual profiles add qualitative depth to the quantitative findings of<br>Research Question 1 and help contextualise statistical outliers identified in the scatterplot.</p></div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# ZUSAMMENFASSUNG Q1
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">Zusammenfassung — Question 1: Revisit Cities</div>',
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
    <h4>🎯 Antwort auf Question 1</h4>
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
<div style="background:#0f1829;border:1px solid #1e2d45;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#7C89A3;margin-bottom:10px;">📋 Graph Explanation</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">This bar chart examines whether more popular artists (as measured by Last.fm listener counts)<br>tend to perform a higher proportion of their shows in capital cities. Artists are divided into<br>equal-sized popularity tiers (quartiles) based on their listener count or tour size (selectable<br>via the radio button), and the average value of the selected capital-city metric is shown for<br>each tier as a bar.</p>
<p style="margin:0 0 10px 0;">Three metrics can be displayed on the y-axis:<br>• <strong>% Capital Events</strong>: the share of all concerts taking place in capital cities (volume-based)<br>• <strong>% Capital Cities</strong>: the share of uniquely visited cities that are capitals (geographic breadth)<br>• <strong>Average Capitals Visited</strong>: the raw count of distinct capital cities toured per artist</p>
<p style="margin:0 0 10px 0;">This directly tests the hypothesis of Research Question 2 — that higher popularity correlates<br>with a greater concentration of performances in capital cities.</p></div>
</div>
""", unsafe_allow_html=True)

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

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #6366f1;border-radius:10px;padding:18px 22px;margin-bottom:12px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#818cf8;margin-bottom:10px;">📊 Statistical Analysis</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">The Kruskal-Wallis test assesses whether the capital-city metric differs significantly<br>across the popularity tiers. Because artist data is unlikely to be normally distributed<br>(a small number of very popular artists tend to skew the distribution), this<br>non-parametric test is appropriate.</p>
<p style="margin:0 0 10px 0;">• <strong>H statistic</strong>: Reflects how much the rank-based distributions differ between groups.<br>  A higher H means the groups are more different from one another.<br>• <strong>p-value</strong>: If below 0.05, the differences between tiers are statistically significant —<br>  i.e., unlikely to be due to chance.<br>• <strong>Δ (difference between lowest and highest tier mean)</strong>: Indicates the practical magnitude<br>  of the effect. A Δ of 3 percentage points or more is treated here as a meaningful<br>  difference in capital-city concentration.</p>
<p style="margin:0 0 10px 0;">The bar labels show the mean value per tier directly, making it easy to assess trends<br>even without formal testing. Hovering reveals the median per tier as well, which is more<br>robust to outliers than the mean.</p></div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #10b981;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#10b981;margin-bottom:10px;">🔍 Interpretation</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">A clear upward trend in bar heights from left (low popularity) to right (high popularity)<br>would confirm the hypothesis: more-listened-to artists concentrate their touring in capital<br>cities. This could reflect rational booking decisions — capital cities offer larger venues,<br>higher media exposure, and denser fanbase concentrations, making them attractive targets<br>for artists who can fill them. A flat or downward trend would suggest the opposite: highly<br>popular artists can afford to tour broadly, while niche or emerging artists may focus on<br>the one or two capitals they can reliably fill, resulting in a paradoxically higher<br>capital-city share for smaller artists.</p></div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# Q2 — GRAPH 2: Scatterplot pct_capital vs Listeners
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📈 Graph 2 — Scatterplot: Capital City Share vs. Last.fm Listener Popularity</div>',
            unsafe_allow_html=True)

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#7C89A3;margin-bottom:10px;">📋 Graph Explanation</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">This scatterplot examines the continuous relationship between an artist's streaming<br>popularity (Last.fm listener count, log-transformed on the x-axis) and the proportion of<br>their concerts held in capital cities (y-axis). Each dot represents one artist. A linear<br>OLS (Ordinary Least Squares) regression line is overlaid to indicate the overall direction<br>and strength of the relationship.</p>
<p style="margin:0 0 10px 0;">The y-axis can be switched between two capital-city metrics: the percentage of all events<br>in capitals (volume-based) or the percentage of uniquely visited cities that are capitals<br>(geographic breadth). The x-axis always uses a log₁₀ transformation of listener counts to<br>compress the wide range of popularity values and make the relationship easier to visualise.</p>
<p style="margin:0 0 10px 0;">This graph provides a continuous, artist-level test of the hypothesis from Research<br>Question 2, complementing the group-level view in Graph 1.</p></div>
</div>
""", unsafe_allow_html=True)

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

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #6366f1;border-radius:10px;padding:18px 22px;margin-bottom:12px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#818cf8;margin-bottom:10px;">📊 Statistical Analysis</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">Three key statistics are reported for this regression:</p>
<p style="margin:0 0 10px 0;">• <strong>Pearson r</strong>: Measures the linear correlation between log₁₀(listeners) and the capital<br>  share metric, ranging from −1 (perfect negative correlation) to +1 (perfect positive<br>  correlation). Values around 0 indicate no linear relationship.<br>• <strong>R²</strong> (coefficient of determination): Expresses what proportion of the variance in the<br>  capital-city share can be explained by listener popularity alone. For example, R² = 15%<br>  means that 15% of the variation in how often artists play in capitals is statistically<br>  associated with their streaming popularity; the remaining 85% is driven by other factors<br>  (genre, touring region, booking strategy, etc.).<br>• <strong>p-value</strong>: Tests whether the observed correlation could have arisen by chance in a sample<br>  of this size. A value below 0.05 indicates that the correlation is statistically<br>  significant, meaning it is unlikely to be a random artefact.</p>
<p style="margin:0 0 10px 0;">The OLS regression line (green) fits a straight line through the cloud of points, making the<br>overall trend visible regardless of scatter. A steep upward slope with low scatter confirms a<br>strong positive relationship.</p></div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #10b981;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#10b981;margin-bottom:10px;">🔍 Interpretation</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">This graph provides the most direct statistical test of Research Question 2's central<br>hypothesis. If the regression line slopes upward and r is significantly positive, it confirms<br>that listener popularity is a meaningful predictor of capital-city focus in touring. However,<br>even a significant correlation with a low R² suggests that while the relationship exists, it<br>is weak and many other factors drive capital-city share. A non-significant or negative result<br>challenges the hypothesis and prompts alternative explanations — for example, that very<br>popular artists tour so extensively that they must include many non-capital cities simply to<br>fill tour dates, diluting their capital share.</p></div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# Q2 — GRAPH 3: Meistbesuchte Hauptstädte (global)
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📊 Graph 3 — Most Visited Capital Cities Across All Artists</div>',
            unsafe_allow_html=True)

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#7C89A3;margin-bottom:10px;">📋 Graph Explanation</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">This horizontal bar chart ranks capital cities by the total number of concert visits across<br>all artists in the dataset. Unlike Graph 3 in Research Question 1 (which covered all cities),<br>this chart is restricted exclusively to capital cities, providing a focused view of which<br>capitals function as dominant live-music hubs.</p>
<p style="margin:0 0 10px 0;">Each bar represents one capital city. The bar length shows total visits; the colour can be<br>switched between total visits (intensity of use) and number of distinct artists who performed<br>there (breadth of use). The minimum artist threshold filters out capitals visited by only one<br>or a handful of artists.</p>
<p style="margin:0 0 10px 0;">This chart answers the practical question: which specific capitals drive the high capital-city<br>share found in the KPI metrics, and is that share distributed evenly or dominated by a small<br>number of mega-hubs?</p></div>
</div>
""", unsafe_allow_html=True)

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

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #6366f1;border-radius:10px;padding:18px 22px;margin-bottom:12px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#818cf8;margin-bottom:10px;">📊 Statistical Analysis</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">The insight card highlights two summary statistics: the three most-visited capitals (by<br>total visit count) and the capital with the highest number of distinct visiting artists<br>(a measure of cross-artist appeal). These two metrics can diverge: a city with very high<br>total visits but low artist diversity is dominated by a few prolific tourers; a city with<br>high artist diversity but moderate total visits attracts a broad range of artists who each<br>visit relatively rarely. Comparing these two statistics gives a richer picture of capital<br>hub dynamics than visit counts alone.</p>
<p style="margin:0 0 10px 0;">Switching the colour encoding to "Number of Artists" transforms the chart from a volume<br>view (how much touring happens here?) into a breadth view (how universally relevant is this<br>capital to the touring industry?).</p></div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #10b981;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#10b981;margin-bottom:10px;">🔍 Interpretation</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">This chart contextualises the global capital-city share statistic from the KPI row. A steep<br>drop-off in bar length after the top 3–5 cities would indicate that the high overall capital<br>share is driven by just a handful of mega-hub capitals (London, Paris, Berlin), not a<br>broad preference for capitals in general. This would nuance the answer to Research Question<br>2: artists are not drawn to capitals per se, but to the world's most commercially important<br>capitals. Conversely, a more gradual decline would suggest a genuine and broad preference<br>for capital cities across many countries.</p></div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# Q2 — GRAPH 4: Heatmap pct_capital × Listeners-Tier
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🌡️ Graph 4 — Heatmap: Capital City Share vs. Popularity Tier Distribution</div>',
            unsafe_allow_html=True)

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#7C89A3;margin-bottom:10px;">📋 Graph Explanation</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">This heatmap shows how artists are distributed across combinations of popularity tier<br>(x-axis, based on Last.fm listeners divided into four quartiles from low to high) and<br>capital-city event share (y-axis, in 20-percentage-point bands from 0–20% up to 81–100%).<br>Each cell displays the number of artists who fall into that specific combination of<br>popularity and capital-city focus.</p>
<p style="margin:0 0 10px 0;">Brighter, darker cells indicate higher artist counts. If popularity drives capital-city<br>concentration, the densest cells should shift toward higher y-values (higher capital share)<br>as we move from left (low popularity) to right (high popularity) — producing a pattern where<br>the distribution moves upward across columns. A uniform or random distribution would indicate<br>that capital-city share is independent of popularity.</p>
<p style="margin:0 0 10px 0;">This heatmap complements Graphs 1 and 2 of Research Question 2 by providing a full<br>distributional view rather than just comparing averages or correlation coefficients.</p></div>
</div>
""", unsafe_allow_html=True)

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

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #6366f1;border-radius:10px;padding:18px 22px;margin-bottom:12px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#818cf8;margin-bottom:10px;">📊 Statistical Analysis</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">Like the heatmap in Research Question 1, this chart uses artist counts as its core statistic.<br>The key analytical question is whether the modal row (the row with the highest count) shifts<br>upward as we move across popularity columns. If the row with the highest count is "0–20%"<br>for low-popularity artists but "41–60%" for high-popularity artists, this would visually<br>confirm the positive relationship detected in the correlation analysis of Graph 2. The<br>heatmap also reveals the shape of within-tier distributions: a wide spread of counts across<br>multiple rows within a single popularity column indicates high variability in capital<br>preferences even among similarly popular artists.</p></div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #10b981;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#10b981;margin-bottom:10px;">🔍 Interpretation</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">The heatmap is particularly valuable for identifying heterogeneity within popularity tiers —<br>something averages and regression lines cannot show. For instance, even if Graph 1 shows that<br>the average capital share is slightly higher for top-quartile artists, the heatmap might<br>reveal that the Q4 column has counts spread across all capital-share bands, meaning there is<br>no single dominant pattern: some very popular artists play almost exclusively in capitals,<br>while others tour broadly. This would lead to a more nuanced answer to Research Question 2:<br>popularity is associated with capital-city focus on average, but the relationship is not<br>deterministic — individual artist strategy varies widely regardless of popularity level.</p></div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# Q2 — ARTIST DETAIL
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🔍 Artist Detail — Capital City Profile</div>',
            unsafe_allow_html=True)

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#7C89A3;margin-bottom:10px;">📋 Graph Explanation</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">This interactive bar chart provides a capital-city breakdown for a single selected artist,<br>showing which specific capital cities they performed in and how many times. The chart is<br>sorted by visit frequency in descending order, so the artist's most-frequented capitals<br>appear first.</p>
<p style="margin:0 0 10px 0;">The KPI metrics above the chart summarise the artist's overall relationship with capital<br>cities: total events, capital events, non-capital events, percentage of shows in capitals,<br>and the number of distinct capitals visited. This allows the reader to compare an individual<br>artist's profile against the dataset-wide averages reported in the KPI row at the top of<br>Research Question 2.</p>
<p style="margin:0 0 10px 0;">This detail view is designed for qualitative exploration: after identifying patterns at the<br>aggregate level, the reader can investigate which specific artists drive those patterns and<br>which capitals account for their capital-city concentration.</p></div>
</div>
""", unsafe_allow_html=True)

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

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #6366f1;border-radius:10px;padding:18px 22px;margin-bottom:12px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#818cf8;margin-bottom:10px;">📊 Statistical Analysis</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">The key metric here is pct_capital — the share of all this artist's events that took place<br>in capital cities. A value well above the dataset average (shown in the KPI row at the top<br>of this section) marks the artist as a capital-focused outlier; a value well below average<br>indicates an artist who tours primarily in non-capital cities. The bar chart adds geographic<br>specificity: a high pct_capital concentrated in just one or two bars (e.g. only London and<br>Paris) represents a different strategy than the same pct_capital spread across ten different<br>capitals.</p></div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #10b981;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#10b981;margin-bottom:10px;">🔍 Interpretation</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">This detail view adds individual-level granularity to the aggregate findings of Research<br>Question 2. By selecting the artist with the highest pct_capital (the default selection),<br>the reader can immediately inspect the most extreme case — the artist most concentrated in<br>capitals — and assess whether this reflects a deliberate regional focus (e.g. touring<br>primarily in Europe) or a genuinely global capital preference. Comparing artists across the<br>spectrum from lowest to highest capital share helps contextualise the average and distribution<br>statistics found in Graphs 1–4 and makes the answer to Research Question 2 concrete and<br>illustrated.</p></div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# ZUSAMMENFASSUNG Q2
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">Zusammenfassung — Question 2: Capital Cities</div>',
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
        <h4>🎯 Antwort auf Question 2</h4>
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
<div style="background:#0f1829;border:1px solid #1e2d45;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#7C89A3;margin-bottom:10px;">📋 Graph Explanation</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">This scatterplot investigates whether more popular artists (as measured by Last.fm listener<br>counts) tour more closely in line with where their digital fanbase is located. Each dot<br>represents one artist. The x-axis shows the artist's total Last.fm listener count on a<br>log₁₀ scale (to handle the large range of popularity values), and the y-axis shows their<br>geo-alignment score — by default the listener-weighted coverage, or Jaccard similarity if<br>weighted coverage is unavailable.</p>
<p style="margin:0 0 10px 0;">The <strong>Weighted Coverage</strong> metric answers: "Of all the listeners this artist has worldwide,<br>what proportion live in countries the artist actually toured?" A value of 1.0 means the<br>artist toured every country where they have significant listener presence; a value near 0<br>means almost none of their listeners live in countries they toured.</p>
<p style="margin:0 0 10px 0;">A green OLS regression line shows the overall trend. The colour of each dot encodes a third<br>variable (adjustable: number of tour countries, tour coverage, or streaming reach), adding<br>an additional dimension to the analysis.</p>
<p style="margin:0 0 10px 0;">This graph directly addresses the central question of Research Question 3: is there a<br>systematic relationship between how popular an artist is and how well their tour geography<br>matches their streaming geography?</p></div>
</div>
""", unsafe_allow_html=True)

g1a, g1b = st.columns([1, 3])
with g1a:
    color_by = st.selectbox("Farbe nach",
                            ["n_tour_countries", "tour_coverage", "streaming_reach"],
                            format_func=lambda x: {
                                "n_tour_countries": "Tour-Länder",
                                "tour_coverage": "Tour Coverage",
                                "streaming_reach": "Streaming Reach",
                            }[x], key="ga2_color")
    show_labels_g1 = st.checkbox("Namen", value=False, key="ga2_lbl")

GA2_Y = "weighted_coverage" if "weighted_coverage" in ga.columns else "jaccard"
GA2_Y_LABEL = "Weighted Coverage (listener-gewichtet)" if GA2_Y == "weighted_coverage" else "Jaccard-Similarity"
df_g1 = ga.dropna(subset=["listeners", GA2_Y]).copy()
df_g1["log_listeners"] = np.log10(df_g1["listeners"] + 1)

r_g1, p_g1 = stats.pearsonr(df_g1["log_listeners"], df_g1[GA2_Y])
coef_g1 = np.polyfit(df_g1["log_listeners"], df_g1[GA2_Y], 1)
x_line_g1 = np.linspace(df_g1["log_listeners"].min(), df_g1["log_listeners"].max(), 200)
y_line_g1 = np.polyval(coef_g1, x_line_g1)

m1g1, m2g1, m3g1 = st.columns(3)
m1g1.metric("n Artists", len(df_g1))
m2g1.metric("Pearson r", f"{r_g1:.3f}")
m3g1.metric("p-Wert", f"{p_g1:.4f}",
            delta="signifikant ✅" if p_g1 < 0.05 else "nicht signifikant ⚠️",
            delta_color="normal" if p_g1 < 0.05 else "inverse")

fig_g1 = px.scatter(
    df_g1, x="log_listeners", y=GA2_Y,
    color=color_by,
    color_continuous_scale="Viridis",
    hover_name="artist_name",
    hover_data={
        "log_listeners": False,
        "jaccard": ":.3f",
        "tour_coverage": ":.1%",
        "streaming_reach": ":.1%",
        "n_aligned": True,
        "n_tour_countries": True,
        "n_streaming": True,
    },
    text="artist_name" if show_labels_g1 else None,
    labels={
        "log_listeners": "log10(Last.fm Listeners)",
        GA2_Y: GA2_Y_LABEL,
        "n_tour_countries": "Tour-Länder",
    },
    title=f"Listeners vs. {GA2_Y_LABEL}  |  r = {r_g1:.3f}  |  n = {len(df_g1)}",
    template="plotly_dark",
)
fig_g1.add_trace(go.Scatter(
    x=x_line_g1, y=y_line_g1, mode="lines", name="OLS",
    line=dict(color="#f59e0b", width=2.5), hoverinfo="skip",
))
if show_labels_g1:
    fig_g1.update_traces(
        textposition="top center",
        textfont=dict(size=7, color="white"),
        selector=dict(mode="markers+text")
    )
fig_g1.update_layout(
    height=480, paper_bgcolor="#080b14", plot_bgcolor="#161c2d",
    font=dict(color="white"),
    xaxis=dict(gridcolor="#232840"),
    yaxis=dict(gridcolor="#232840", range=[-0.05, 1.05], title=GA2_Y_LABEL),
    coloraxis_colorbar=dict(title=color_by.replace("_", " ").title()),
)
with g1b:
    st.plotly_chart(fig_g1, use_container_width=True)

interpretation_g1 = (
    "Positivkorrelation: Populärere Artists sind besser geo-aligned — sie touren gezielter dorthin wo sie Fans haben."
    if r_g1 > 0.1 and p_g1 < 0.05 else
    "Negativkorrelation: Populärere Artists touren in mehr Länder als ihr Streaming-Footprint — sie erschliessen aktiv neue Märkte."
    if r_g1 < -0.1 and p_g1 < 0.05 else
    "Kein signifikanter Zusammenhang — Geo-Alignment ist unabhängig von der Popularität."
)
st.markdown(f"""
<div class="insight-card">
    <h4>💡 Interpretation</h4>
    <p>{interpretation_g1}</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #6366f1;border-radius:10px;padding:18px 22px;margin-bottom:12px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#818cf8;margin-bottom:10px;">📊 Statistical Analysis</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">• <strong>Pearson r</strong>: Measures the linear correlation between log₁₀(listeners) and the alignment<br>  score. A positive r means more popular artists are better geo-aligned (they tour where<br>  their fans are); a negative r means more popular artists tour more broadly, potentially<br>  beyond their established streaming markets.<br>• <strong>p-value</strong>: Tests statistical significance. Below 0.05, the correlation is unlikely to<br>  be a random artefact of the sample size.<br>• <strong>OLS slope</strong>: The steepness of the regression line indicates the practical magnitude of<br>  the relationship. A shallow slope means that even large differences in popularity<br>  translate to only small differences in geo-alignment.</p>
<p style="margin:0 0 10px 0;">Note that the y-axis is bounded between 0 and 1 (alignment scores are always proportions),<br>while the x-axis is unbounded on the log scale. Artists clustered at the top of the y-axis<br>(alignment ≈ 1.0) are those who tour almost exclusively in countries where they already have<br>a strong streaming presence. Those at the bottom (alignment ≈ 0) tour in countries largely<br>disconnected from their streaming fanbase — for example, artists who stream primarily in<br>Asia but tour only in Europe.</p></div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #10b981;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#10b981;margin-bottom:10px;">🔍 Interpretation</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">This graph is the analytical core of Research Question 3. A significant positive correlation<br>would suggest that the music industry operates efficiently: artists tour where demand (as<br>measured by streaming) is highest. This would be consistent with rational, data-driven<br>booking decisions. A non-significant or negative correlation would be more surprising and<br>potentially more interesting: it would suggest that touring geography is driven by factors<br>other than streaming popularity — historical touring routes, booking agency relationships,<br>visa accessibility, or a deliberate strategy of touring new markets to build streaming<br>audiences rather than serving existing ones.</p></div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# GA2 — GRAPH 2: Balkendiagramm — alle 3 Metriken nach Popularity-Tier
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📊 Graph 2 — All Three Alignment Metrics by Popularity Tier</div>',
            unsafe_allow_html=True)

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#7C89A3;margin-bottom:10px;">📋 Graph Explanation</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">This grouped bar chart presents all three geo-alignment metrics side by side for each<br>popularity tier, allowing a direct comparison of how each metric behaves across the<br>popularity spectrum. Artists are split into four equal-sized quartiles by Last.fm listener<br>count (Q1 = lowest, Q4 = highest), and the average value of each metric is shown as a<br>separate coloured bar within each quartile.</p>
<p style="margin:0 0 10px 0;">The three metrics capture different dimensions of alignment:<br>• <strong>Weighted Coverage</strong> (purple): What proportion of an artist's total listener-weighted<br>  global reach is covered by their tour countries?<br>• <strong>Jaccard Similarity</strong> (dark blue): How much do the sets of streaming countries and tour<br>  countries overlap, treating all countries equally?<br>• <strong>Tour Coverage</strong> (amber): What proportion of the artist's tour countries are also among<br>  their top streaming countries?<br>• <strong>Streaming Reach</strong> (green): What proportion of the artist's streaming countries are also<br>  toured?</p>
<p style="margin:0 0 10px 0;">By showing all four metrics together, the chart reveals whether different dimensions of<br>alignment behave consistently across popularity tiers or diverge in informative ways.</p></div>
</div>
""", unsafe_allow_html=True)

df_g2 = ga.dropna(subset=["listeners", "jaccard"]).copy()
df_g2["tier"] = pd.qcut(df_g2["listeners"], q=4,
                        labels=["Q1\n(niedrig)", "Q2", "Q3", "Q4\n(hoch)"])

tier_cols = [c for c in ["weighted_coverage", "jaccard", "tour_coverage", "streaming_reach"] if c in df_g2.columns]
tier_stats = df_g2.groupby("tier", observed=True)[tier_cols].mean().reset_index()

fig_g2 = go.Figure()
metric_colors = {
    "weighted_coverage": "#818cf8",
    "jaccard": "#6366f1",
    "tour_coverage": "#f59e0b",
    "streaming_reach": "#10b981",
}
metric_labels = {
    "weighted_coverage": "Weighted Coverage (Listener-gew.)",
    "jaccard": "Jaccard-Similarity",
    "tour_coverage": "Tour Coverage",
    "streaming_reach": "Streaming Reach",
}
for metric, col in metric_colors.items():
    if metric not in tier_cols: continue
    fig_g2.add_trace(go.Bar(
        x=tier_stats["tier"],
        y=tier_stats[metric],
        name=metric_labels[metric],
        marker_color=col,
        hovertemplate=f"{metric_labels[metric]}<br>%{{y:.3f}}<extra></extra>",
    ))

# Kruskal-Wallis
kw_groups = [df_g2[df_g2["tier"] == t]["weighted_coverage" if "weighted_coverage" in df_g2.columns else "jaccard"].dropna().values
             for t in df_g2["tier"].unique() if len(df_g2[df_g2["tier"] == t]) > 1]
kw_h = kw_p = None
if len(kw_groups) >= 2:
    kw_h, kw_p = stats.kruskal(*kw_groups)

title_g2 = "Geo-Alignment nach Popularity-Tier"
if kw_p is not None:
    title_g2 += f"  |  Kruskal-Wallis H={kw_h:.1f}  p={kw_p:.3f}  {'✅' if kw_p < 0.05 else '⚠️'}"

fig_g2.update_layout(
    title=title_g2,
    barmode="group",
    xaxis_title="Popularity-Tier (nach Last.fm Listeners)",
    yaxis_title="Durchschnittlicher Wert",
    template="plotly_dark",
    paper_bgcolor="#080b14", plot_bgcolor="#161c2d",
    font=dict(color="white"), height=400,
    xaxis=dict(gridcolor="#232840"),
    yaxis=dict(gridcolor="#232840", range=[0, 1]),
    legend=dict(orientation="h", y=-0.2),
)
st.plotly_chart(fig_g2, use_container_width=True)

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #6366f1;border-radius:10px;padding:18px 22px;margin-bottom:12px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#818cf8;margin-bottom:10px;">📊 Statistical Analysis</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">The Kruskal-Wallis test result embedded in the chart title tests whether the weighted<br>coverage metric (the primary alignment measure) differs significantly across the four<br>popularity tiers. Key values to interpret:</p>
<p style="margin:0 0 10px 0;">• <strong>H statistic</strong>: A high H relative to the number of groups indicates that at least one<br>  tier has a substantially different distribution from the others.<br>• <strong>p-value</strong>: Below 0.05 means the tier differences are statistically significant and<br>  unlikely due to chance.</p>
<p style="margin:0 0 10px 0;">Beyond the test, the visual pattern of bar heights across metrics is analytically rich.<br>If Tour Coverage (amber) is consistently high across all tiers but Streaming Reach (green)<br>is low for lower-tier artists, this would suggest that smaller artists tour almost entirely<br>within their streaming footprint (a small, focused tour) but reach only a small fraction of<br>their total streaming countries — implying many untapped markets. Conversely, high streaming<br>reach with lower weighted coverage would indicate that an artist tours in many of their<br>streaming countries, but those countries have only small listener bases — so the percentage<br>of total listeners "covered" remains low.</p></div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #10b981;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#10b981;margin-bottom:10px;">🔍 Interpretation</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">This multi-metric bar chart allows the reader to assess Research Question 3 from several<br>angles simultaneously. A consistent upward trend across all four metrics from Q1 to Q4<br>would provide robust evidence that more popular artists align their tours more closely with<br>their streaming footprint. If metrics diverge — for example, Jaccard increases with<br>popularity but weighted coverage does not — this would suggest that popular artists tour<br>in more of their streaming countries by count, but the countries they skip are precisely<br>the ones with the largest listener bases (perhaps because those markets are difficult to<br>tour in despite having large streaming audiences, e.g. due to logistical constraints).</p></div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# GA2 — GRAPH 3: Top & Bottom Artists — Heatmap Streaming vs. Tour Countries
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🔥 Graph 3 — Best and Worst Aligned Artists: Streaming Countries vs. Tour Countries</div>',
            unsafe_allow_html=True)

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#7C89A3;margin-bottom:10px;">📋 Graph Explanation</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">This grouped bar chart displays the top or bottom N artists by geo-alignment score, showing<br>for each artist three quantities side by side: the number of countries in which they have<br>a significant streaming presence on Last.fm (purple bars), the number of countries in which<br>they performed on tour (amber bars), and the number of countries that appear in both —<br>the aligned overlap (green bars).</p>
<p style="margin:0 0 10px 0;">The chart can be toggled between showing the best-aligned artists (those whose streaming<br>footprint and tour geography overlap most closely) and the worst-aligned artists (those<br>with the largest gap between their digital audience reach and their physical touring<br>presence). The sorting metric can be changed between weighted coverage, Jaccard similarity,<br>tour coverage, and streaming reach.</p>
<p style="margin:0 0 10px 0;">This chart makes the concept of geo-alignment tangible by attaching it to real artist names<br>and concrete country counts, moving beyond abstract scores to specific cases.</p></div>
</div>
""", unsafe_allow_html=True)

g3a, g3b = st.columns([1, 3])
with g3a:
    n_show = st.slider("Anzahl Artists", 5, 20, 10, key="ga2_n")
    show_type = st.radio("Zeigen", ["Beste Ausrichtung", "Schlechteste Ausrichtung"], key="ga2_type")
    sort_col = st.selectbox("Sortieren nach",
                            [c for c in ["weighted_coverage", "jaccard", "tour_coverage", "streaming_reach"] if c in ga.columns],
                            format_func=lambda x: metric_labels.get(x, x), key="ga2_sort")

top_df = (ga.dropna(subset=["jaccard", "n_tour_countries", "n_streaming"])
          .nlargest(n_show, sort_col) if show_type == "Beste Ausrichtung"
          else ga.dropna(subset=["jaccard", "n_tour_countries", "n_streaming"])
          .nsmallest(n_show, sort_col))

fig_g3 = go.Figure()
fig_g3.add_trace(go.Bar(
    y=top_df["artist_name"],
    x=top_df["n_streaming"],
    name="Streaming-Länder (Last.fm)",
    orientation="h",
    marker_color="#6366f1",
    hovertemplate="%{y}<br>Streaming: %{x} Länder<extra></extra>",
))
fig_g3.add_trace(go.Bar(
    y=top_df["artist_name"],
    x=top_df["n_tour_countries"],
    name="Tour-Länder (Ticketmaster)",
    orientation="h",
    marker_color="#f59e0b",
    hovertemplate="%{y}<br>Tour: %{x} Länder<extra></extra>",
))
fig_g3.add_trace(go.Bar(
    y=top_df["artist_name"],
    x=top_df["n_aligned"],
    name="Ueberlappung",
    orientation="h",
    marker_color="#10b981",  # type: ignore
    hovertemplate="%{y}<br>Aligned: %{x} Länder  Jaccard=%{customdata:.3f}<extra></extra>",
    customdata=top_df["jaccard"],
))
fig_g3.update_layout(
    title=show_type + " — Streaming vs. Tour Länder",
    barmode="group",
    xaxis_title="Anzahl Länder",
    template="plotly_dark",
    paper_bgcolor="#080b14", plot_bgcolor="#161c2d",
    font=dict(color="white"), height=max(300, n_show * 35),
    xaxis=dict(gridcolor="#232840"),
    yaxis=dict(gridcolor="#232840"),
    legend=dict(orientation="h", y=-0.15),
)
with g3b:
    st.plotly_chart(fig_g3, use_container_width=True)

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #6366f1;border-radius:10px;padding:18px 22px;margin-bottom:12px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#818cf8;margin-bottom:10px;">📊 Statistical Analysis</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">The Jaccard similarity for each artist can be derived visually from the chart: it equals the<br>green bar length (aligned countries) divided by the sum of the purple and amber bars minus<br>the green bar (i.e., the union of streaming and tour countries). Artists with a large green<br>bar relative to the other two bars have high Jaccard similarity; artists where the green bar<br>is small compared to large purple and amber bars have low similarity.</p>
<p style="margin:0 0 10px 0;">The "worst aligned" artists are particularly informative. Two patterns can produce low<br>alignment:<br>• <strong>Large streaming footprint, small tour</strong> — the artist is globally streamed but tours<br>   only regionally (e.g. a Latin American artist with global streaming but only South<br>   American tour dates).<br>• <strong>Large tour footprint, small streaming</strong> — the artist tours extensively into markets<br>   where they have little streaming presence, possibly to build new audiences.</p>
<p style="margin:0 0 10px 0;">These two patterns have opposite strategic implications and can be distinguished by comparing<br>the relative lengths of the purple (streaming) and amber (tour) bars.</p></div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #10b981;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#10b981;margin-bottom:10px;">🔍 Interpretation</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;"><p style="margin:0 0 10px 0;">This chart answers Research Question 3 at the individual artist level, making abstract<br>alignment scores concrete. The best-aligned artists demonstrate that it is possible to tour<br>closely in line with one's streaming geography, showing that the gap between digital reach<br>and physical presence is not inevitable. The worst-aligned artists reveal the types of<br>mismatches that exist in practice and raise questions about why they occur — whether by<br>choice (market development strategy), constraint (touring infrastructure, visa access), or<br>simply because streaming audiences in some regions cannot yet be monetised through live<br>events at scale.</p></div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Zusammenfassung ────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Zusammenfassung — Question 3: Geo-Alignment</div>',
            unsafe_allow_html=True)

st.markdown(f"""
| Metrik | Durchschnitt | Interpretation |
|--------|-------------|----------------|
| **Weighted Coverage** | {mean_wc:.1%} | Listener-Reichweite durch Tour abgedeckt |
| **Jaccard-Similarity** | {mean_jac:.3f} | {"Starke" if mean_jac > 0.4 else "Moderate" if mean_jac > 0.2 else "Schwache"} Uebereinstimmung |
| **Tour Coverage** | {mean_tc:.1%} | der Tour-Länder sind auch Streaming-Länder |
| **Streaming Reach** | {mean_sr:.1%} | der Streaming-Länder werden betourt |
| **Pearson r (Listeners vs Jaccard)** | {r_g1:.3f} | {"pos. Zusammenhang" if r_g1 > 0 else "neg. Zusammenhang"}  {"✅" if p_g1 < 0.05 else "⚠️ nicht signifikant"} |
""")

st.markdown(f"""
<div class="insight-card">
    <h4>🎯 Antwort auf Question 3</h4>
    <p>
    Ø Jaccard = <strong style="color:#818cf8">{mean_jac:.3f}</strong> —
    {"Artists touren stark zielgruppenorientiert: wo sie auf Last.fm beliebt sind, spielen sie auch." if mean_jac > 0.4
else "Eine moderate Ausrichtung: Tour und Streaming-Footprint überlappen sich teilweise, aber nicht vollständig."
if mean_jac > 0.2
else "Streaming-Popularität und Tour-Geografie sind weitgehend entkoppelt — viele ungenutzte Märkte."}
    <br><br>
    Ø Tour Coverage = <strong style="color:#f59e0b">{mean_tc:.1%}</strong>:
    Dieser Anteil der Tour-Länder ist durch Last.fm-Streaming-Popularität abgedeckt.
    <br>
    Ø Streaming Reach = <strong style="color:#10b981">{mean_sr:.1%}</strong>:
    Dieser Anteil der Streaming-Länder wird auch tatsächlich betourt.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="methodology-note">
    <p>
    <strong>Methodische Anmerkung:</strong>
    Streaming-Länder = Länder wo der Artist in Last.fm geo.getTopArtists (Top-50) erscheint.
    Tour-Länder = Länder mit mindestens einem Ticketmaster-Event.
    Jaccard-Similarity = |Streaming ∩ Tour| / |Streaming ∪ Tour|.
    Methode robust gegen unterschiedliche Datensatzgrößen.
    Nur Artists mit Daten in beiden Quellen eingeschlossen (n={n_artists}).
    </p>
</div>
""".replace("{n_artists}", str(n_artists)), unsafe_allow_html=True)
