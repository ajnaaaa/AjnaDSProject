import streamlit as st
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.styles import apply_styles
from components.nav import render_nav
from components.glossary import TERMS, glossar_seite

st.set_page_config(
    page_title="Glossar",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_styles()
render_nav()

st.markdown("""
<div class="page-header">
    <h1>📖 Glossar</h1>
    <p>Alle Fachbegriffe einfach erklärt — kein Data-Science-Studium erforderlich</p>
</div>
""", unsafe_allow_html=True)

suche = st.text_input("🔍 Begriff suchen...", placeholder="z.B. p-Wert, Pearson, Median...")

if suche.strip():
    treffer = {t: v for t, v in TERMS.items()
               if suche.lower() in t.lower() or suche.lower() in v["kurz"].lower()}
    if treffer:
        st.markdown("**" + str(len(treffer)) + " Treffer fuer: " + suche + "**")
        for term, t in treffer.items():
            with st.expander(t["emoji"] + " **" + term + "** — *" + t["kurz"] + "*", expanded=True):
                st.markdown(t["lang"])
    else:
        st.warning("Kein Treffer fuer: " + suche)
    st.divider()

glossar_seite()
