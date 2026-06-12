"""
Home.py
-------
Page d'accueil de l'application Competitor Analysis.
Ce fichier est le point d'entrée : streamlit run Home.py

Rôle : présenter l'application, ses fonctionnalités, et guider l'utilisateur.
"""

import streamlit as st

# ── Configuration de la page (doit être le 1er appel Streamlit) ──────────────
st.set_page_config(
    page_title="Competitor Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS personnalisé : thème sombre élégant ──────────────────────────────────
st.markdown("""
<style>
    /* Fond général */
    .stApp { background-color: #0f1117; }

    /* Cartes de fonctionnalités */
    .feature-card {
        background: linear-gradient(135deg, #1e2130, #252840);
        border: 1px solid #3a3f5c;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 16px;
        transition: border-color 0.2s;
    }
    .feature-card:hover { border-color: #6c8dff; }
    .feature-card h3 { color: #6c8dff; margin: 0 0 8px 0; font-size: 1.05rem; }
    .feature-card p  { color: #a0a8c0; margin: 0; font-size: 0.9rem; line-height: 1.5; }

    /* Badge de statut */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .badge-done  { background: #1a3a2a; color: #4ade80; border: 1px solid #4ade80; }
    .badge-todo  { background: #3a2a1a; color: #fb923c; border: 1px solid #fb923c; }

    /* Titre hero */
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #6c8dff, #a78bfa, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .hero-sub {
        color: #7080a0;
        font-size: 1.1rem;
        margin-top: 8px;
    }

    /* Séparateur */
    hr { border-color: #2a2f45 !important; margin: 28px 0; }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #151722; }
</style>
""", unsafe_allow_html=True)


# ── Hero Section ─────────────────────────────────────────────────────────────
col_logo, col_text = st.columns([1, 5])
with col_logo:
    st.markdown("<div style='font-size:4rem; text-align:center; padding-top:10px'>📊</div>",
                unsafe_allow_html=True)
with col_text:
    st.markdown('<p class="hero-title">Competitor Analysis</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-sub">Analyse compétitive des applications mobiles via Google Play Store</p>',
                unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)


# ── Description ──────────────────────────────────────────────────────────────
st.markdown("### 📌 À propos")
st.markdown("""
Cette application est un **prototype d'analyse compétitive** d'applications mobiles.
Elle exploite les données du **Google Play Store** en temps réel pour vous aider à :

- Comprendre le paysage concurrentiel d'un marché applicatif
- Identifier les leaders selon les notes, avis et installations
- Analyser la tonalité des avis utilisateurs grâce au **NLP** (sentiment analysis)

> **Source des données :** Google Play Store via `google-play-scraper`  
> **Modèle NLP :** `VADER` (Valence Aware Dictionary and sEntiment Reasoner)
""")

st.markdown("<hr>", unsafe_allow_html=True)


# ── Fonctionnalités ───────────────────────────────────────────────────────────
st.markdown("### 🚀 Fonctionnalités")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="feature-card">
        <h3>🔍 Page 1 — Résultats</h3>
        <p>Saisissez un terme de recherche et obtenez un tableau interactif des applications
        correspondantes avec filtres, tri, et export.</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="feature-card">
        <h3>📈 Page 2 — Visualisations</h3>
        <p>Graphiques interactifs : distribution des notes, top apps, répartition Gratuit/Payant,
        genres, Word Cloud des descriptions.</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="feature-card">
        <h3>🤖 Page 3 — Sentiment</h3>
        <p>Analyse automatique du sentiment des avis utilisateurs grâce à un modèle
        pré-entraîné VADER. Score positif/neutre/négatif par application.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)


# ── Comment utiliser ─────────────────────────────────────────────────────────
st.markdown("### 📖 Comment utiliser l'application")

steps = [
    ("1️⃣", "Aller sur **Résultats** (menu gauche)", "Saisissez votre terme de recherche, ex : *note taking ai*, *fitness tracker*, *language learning*"),
    ("2️⃣", "Explorer les **Visualisations**",       "Les graphiques se génèrent automatiquement à partir des résultats de votre recherche"),
    ("3️⃣", "Analyser les **Sentiments**",            "Sélectionnez une ou plusieurs apps pour lancer l'analyse NLP de leurs avis"),
]

for icon, title, desc in steps:
    st.markdown(f"**{icon} {title}**")
    st.caption(desc)
    st.markdown("")

st.markdown("<hr>", unsafe_allow_html=True)


# ── Roadmap ───────────────────────────────────────────────────────────────────
st.markdown("### 🗺️ Statut & Améliorations futures")

col_done, col_todo = st.columns(2)

with col_done:
    st.markdown("**✅ Implémenté**")
    done_items = [
        "Recherche en temps réel Google Play",
        "Tableau interactif avec filtres",
        "Visualisations (bar, pie, wordcloud, scatter)",
        "Analyse de sentiment VADER (NLP pré-entraîné)",
        "Persistance des données entre pages (session state)",
        "Sidebar de filtrage par app",
    ]
    for item in done_items:
        st.markdown(f'<span class="badge badge-done">✓</span> {item}', unsafe_allow_html=True)

with col_todo:
    st.markdown("**🔜 À améliorer**")
    todo_items = [
        "Ajouter source ProductHunt / GitHub",
        "Comparaison temporelle (évolution des notes)",
        "Export PDF du rapport d'analyse",
        "Authentification utilisateur",
        "Cache persistant pour limiter les appels API",
    ]
    for item in todo_items:
        st.markdown(f'<span class="badge badge-todo">→</span> {item}', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; color:#3a4060; font-size:0.8rem; padding: 10px 0'>
    Competitor Analysis App · ENSIAS BI&A · Lab 2 — Data Applications with Streamlit
</div>
""", unsafe_allow_html=True)