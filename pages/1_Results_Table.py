"""
pages/1_Results_Table.py
------------------------
Page 1 de l'application : Recherche et affichage des résultats.

Rôle :
  - Fournir un champ de saisie pour le terme de recherche
  - Appeler utils.search_apps() pour récupérer les données
  - Afficher un DataFrame interactif avec filtres et options de tri
  - Stocker les données dans st.session_state pour les partager avec les autres pages

Concept clé — Session State :
  Streamlit reexécute tout le script à chaque interaction.
  st.session_state est un dictionnaire persistant entre ces réexécutions ET entre les pages.
  On y stocke le DataFrame de résultats sous la clé "df_results".
"""

import streamlit as st
import pandas as pd
import sys
import os

# Ajouter le dossier parent au path Python pour pouvoir importer utils.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import search_apps

# ── Configuration de la page ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Résultats — Competitor Analysis",
    page_icon="🔍",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    [data-testid="stSidebar"] { background-color: #151722; }
    .metric-card {
        background: #1e2130;
        border: 1px solid #2a2f45;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .metric-value { font-size: 1.8rem; font-weight: 700; color: #6c8dff; }
    .metric-label { font-size: 0.8rem; color: #7080a0; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# ── En-tête ───────────────────────────────────────────────────────────────────
st.markdown("## 🔍 Recherche d'applications")
st.markdown("Entrez un terme de recherche pour explorer le marché des applications mobiles.")
st.markdown("---")

# ── Sidebar : paramètres de recherche ─────────────────────────────────────────
# La sidebar permet de configurer la recherche sans encombrer la page principale
with st.sidebar:
    st.markdown("### ⚙️ Paramètres de recherche")

    n_results = st.slider(
        "Nombre de résultats",
        min_value=5,
        max_value=50,
        value=20,
        step=5,
        help="Plus il y a de résultats, plus la requête est longue (~2–5 sec)",
    )

    lang = st.selectbox(
        "Langue des résultats",
        options=["en", "fr", "ar", "es", "de"],
        index=0,
        help="Langue dans laquelle les descriptions sont retournées",
    )

    country = st.selectbox(
        "Pays du store",
        options=["us", "ma", "fr", "gb", "de"],
        index=0,
        help="Pays du Google Play Store à interroger",
    )

    st.markdown("---")
    st.caption("💡 Les données sont mises en cache dans la session. "
               "Naviguez vers Visualisations ou Sentiment sans relancer la recherche.")

# ── Zone de recherche principale ──────────────────────────────────────────────
col_input, col_btn = st.columns([4, 1])

with col_input:
    # text_input retourne la valeur saisie en temps réel
    query = st.text_input(
        "Terme de recherche",
        value=st.session_state.get("last_query", "note taking ai"),
        placeholder="Ex: fitness tracker, language learning, photo editor…",
        label_visibility="collapsed",
    )

with col_btn:
    search_clicked = st.button("🔍 Rechercher", use_container_width=True, type="primary")

# ── Lancement de la recherche ─────────────────────────────────────────────────
# On lance la recherche si :
#   (a) l'utilisateur clique sur le bouton, OU
#   (b) les données n'existent pas encore en session (premier chargement)
should_search = search_clicked or "df_results" not in st.session_state

if should_search and query.strip():
    with st.spinner(f"Recherche de « {query} » en cours…"):
        df = search_apps(query.strip(), n_results=n_results, lang=lang, country=country)

    if df.empty:
        st.error("Aucun résultat trouvé. Essayez un autre terme de recherche.")
    else:
        # ── Stocker dans session_state pour les autres pages ──────────────────
        st.session_state["df_results"] = df
        st.session_state["last_query"] = query.strip()
        st.success(f"✅ {len(df)} applications trouvées pour « {query} »")

# ── Affichage des résultats ───────────────────────────────────────────────────
if "df_results" in st.session_state:
    df: pd.DataFrame = st.session_state["df_results"]

    # ── Métriques résumées ────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(df)}</div>
            <div class="metric-label">Applications trouvées</div>
        </div>""", unsafe_allow_html=True)

    with m2:
        avg_score = df[df["score"] > 0]["score"].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{'N/A' if pd.isna(avg_score) else f'{avg_score:.2f} ⭐'}</div>
            <div class="metric-label">Note moyenne</div>
        </div>""", unsafe_allow_html=True)

    with m3:
        n_free = (df["free"] == True).sum()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{n_free} / {len(df)}</div>
            <div class="metric-label">Applications gratuites</div>
        </div>""", unsafe_allow_html=True)

    with m4:
        n_genres = df["genre"].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{n_genres}</div>
            <div class="metric-label">Genres différents</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Filtres inline ────────────────────────────────────────────────────────
    st.markdown("#### 🎛️ Filtres")

    fc1, fc2, fc3 = st.columns(3)

    with fc1:
        min_score = st.slider("Note minimale", 0.0, 5.0, 0.0, 0.5)

    with fc2:
        genres_available = ["Tous"] + sorted(df["genre"].dropna().unique().tolist())
        genre_filter = st.selectbox("Genre", genres_available)

    with fc3:
        paid_filter = st.radio("Type", ["Tous", "Gratuit", "Payant"], horizontal=True)

    # Application des filtres
    df_filtered = df.copy()

    if min_score > 0:
        df_filtered = df_filtered[df_filtered["score"] >= min_score]

    if genre_filter != "Tous":
        df_filtered = df_filtered[df_filtered["genre"] == genre_filter]

    if paid_filter == "Gratuit":
        df_filtered = df_filtered[df_filtered["free"] == True]
    elif paid_filter == "Payant":
        df_filtered = df_filtered[df_filtered["free"] == False]

    st.caption(f"{len(df_filtered)} résultats après filtrage")

    st.markdown("---")

    # ── Tableau interactif ────────────────────────────────────────────────────
    # st.dataframe avec column_config permet de personnaliser l'affichage de chaque colonne.
    # On utilise column_config.LinkColumn pour rendre les URLs cliquables,
    # ImageColumn pour les icônes, ProgressColumn pour les notes visuelles.

    display_cols = ["icon", "title", "developer", "score", "ratings", "installs",
                    "price", "genre", "url"]
    df_display = df_filtered[display_cols].copy()
    df_display["ratings"] = df_display["ratings"].apply(
        lambda x: f"{int(x):,}" if pd.notna(x) else "0"
    )

    st.dataframe(
        df_display,
        use_container_width=True,
        height=500,
        column_config={
            "icon": st.column_config.ImageColumn(
                "Icône",
                help="Logo de l'application",
                width="small",
            ),
            "title": st.column_config.TextColumn(
                "Application",
                width="medium",
            ),
            "developer": st.column_config.TextColumn(
                "Développeur",
                width="medium",
            ),
            "score": st.column_config.ProgressColumn(
                "Note ⭐",
                help="Note moyenne sur 5",
                format="%.1f",
                min_value=0,
                max_value=5,
            ),
            "ratings": st.column_config.TextColumn(
                "Nb avis",
                width="small",
            ),
            "installs": st.column_config.TextColumn(
                "Installations",
                width="small",
            ),
            "price": st.column_config.NumberColumn(
                "Prix ($)",
                format="$%.2f",
                width="small",
            ),
            "genre": st.column_config.TextColumn(
                "Genre",
                width="small",
            ),
            "url": st.column_config.LinkColumn(
                "Lien Play Store",
                display_text="Voir →",
                width="small",
            ),
        },
        hide_index=True,
    )

    # ── Export CSV ────────────────────────────────────────────────────────────
    # download_button génère un bouton qui télécharge le fichier côté client
    csv_data = df_filtered.drop(columns=["icon", "description", "url"], errors="ignore").to_csv(index=False)
    st.download_button(
        label="⬇️ Télécharger les résultats (CSV)",
        data=csv_data,
        file_name=f"competitor_analysis_{st.session_state.get('last_query', 'results')}.csv",
        mime="text/csv",
    )

else:
    # Écran vide : inviter l'utilisateur à lancer une recherche
    st.info("👆 Entrez un terme de recherche et cliquez sur **Rechercher** pour commencer.")
    st.markdown("""
    **Exemples de recherches :**
    - `note taking ai` — Applications de prise de notes avec IA
    - `fitness tracker` — Suivi d'activité physique
    - `language learning` — Apprentissage des langues
    - `photo editor` — Éditeurs de photos
    """)