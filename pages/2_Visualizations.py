"""
pages/2_Visualizations.py
--------------------------
Page 2 : Data Visualizations pour l'analyse compétitive.

Visualisations incluses :
  1. Distribution des notes (histogramme)
  2. Top 10 apps par note (bar chart horizontal)
  3. Top 10 apps par nombre d'installations (bar chart)
  4. Répartition Gratuit vs Payant (pie chart)
  5. Distribution par genre (bar chart)
  6. Scatter plot Note vs Popularité
  7. Word Cloud des descriptions

Concept clé — st.session_state :
  On récupère le DataFrame stocké par la page 1.
  Si l'utilisateur arrive directement sur cette page sans avoir cherché,
  on affiche un message d'invitation.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Configuration ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Visualisations — Competitor Analysis",
    page_icon="📈",
    layout="wide",
)

# Thème Plotly personnalisé : fond sombre cohérent avec l'app
PLOTLY_TEMPLATE = "plotly_dark"
PRIMARY_COLOR   = "#6c8dff"
COLORS_PALETTE  = ["#6c8dff", "#a78bfa", "#38bdf8", "#34d399", "#fb923c", "#f472b6",
                   "#facc15", "#60a5fa", "#c084fc", "#4ade80"]

st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    [data-testid="stSidebar"] { background-color: #151722; }
    .section-title {
        font-size: 1.1rem; font-weight: 600; color: #a0a8c0;
        border-left: 3px solid #6c8dff;
        padding-left: 10px; margin: 24px 0 12px 0;
    }
</style>
""", unsafe_allow_html=True)

# ── En-tête ────────────────────────────────────────────────────────────────────
st.markdown("## 📈 Visualisations")
st.markdown("Analyse graphique des applications trouvées.")
st.markdown("---")

# ── Vérification des données en session ───────────────────────────────────────
if "df_results" not in st.session_state or st.session_state["df_results"].empty:
    st.warning("⚠️ Aucune donnée disponible.")
    st.info("Allez d'abord sur la page **Résultats** pour lancer une recherche.")
    st.stop()   # Arrête l'exécution du script ici

df: pd.DataFrame = st.session_state["df_results"]
query = st.session_state.get("last_query", "")

st.caption(f"Données basées sur la recherche : **« {query} »** · {len(df)} applications")
st.markdown("---")

# ── Sidebar : filtres ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎛️ Filtres")

    # Filtre par App ID (pour focaliser sur une ou plusieurs apps)
    all_app_ids = sorted(df["appId"].tolist())
    selected_apps = st.multiselect(
        "Filtrer par App ID",
        options=all_app_ids,
        default=[],
        help="Laissez vide pour afficher toutes les applications",
    )

    min_score_viz = st.slider("Note minimale", 0.0, 5.0, 0.0, 0.5, key="viz_score")

    show_free_only = st.checkbox("Applications gratuites uniquement", value=False)

    st.markdown("---")
    st.caption("Les filtres s'appliquent à tous les graphiques simultanément.")

# Application des filtres sidebar
df_viz = df.copy()
if selected_apps:
    df_viz = df_viz[df_viz["appId"].isin(selected_apps)]
if min_score_viz > 0:
    df_viz = df_viz[df_viz["score"] >= min_score_viz]
if show_free_only:
    df_viz = df_viz[df_viz["free"] == True]

if df_viz.empty:
    st.error("Aucune application ne correspond aux filtres sélectionnés.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# ROW 1 : Distribution des notes + Top 10 par note
# ══════════════════════════════════════════════════════════════════════════════

row1_c1, row1_c2 = st.columns(2)

# ── 1. Histogramme de la distribution des notes ────────────────────────────────
with row1_c1:
    st.markdown('<div class="section-title">📊 Distribution des notes</div>', unsafe_allow_html=True)

    # On ne garde que les apps ayant une note > 0 (certaines n'ont pas encore d'avis)
    df_scored = df_viz[df_viz["score"] > 0]

    fig_hist = px.histogram(
        df_scored,
        x="score",
        nbins=10,
        title="",
        color_discrete_sequence=[PRIMARY_COLOR],
        template=PLOTLY_TEMPLATE,
        labels={"score": "Note (sur 5)", "count": "Nombre d'apps"},
    )
    fig_hist.update_layout(
        plot_bgcolor="#1e2130",
        paper_bgcolor="#1e2130",
        bargap=0.1,
        xaxis=dict(range=[0, 5.5], tickmode="linear", tick0=0, dtick=0.5),
        margin=dict(l=10, r=10, t=10, b=10),
    )
    # Ajouter une ligne médiane
    median_score = df_scored["score"].median()
    fig_hist.add_vline(
        x=median_score,
        line_dash="dash",
        line_color="#fb923c",
        annotation_text=f"Médiane: {median_score:.1f}",
        annotation_position="top right",
    )
    st.plotly_chart(fig_hist, use_container_width=True)
    st.caption(f"Médiane : {median_score:.2f} · Apps avec note : {len(df_scored)}/{len(df_viz)}")

# ── 2. Top 10 apps par note ────────────────────────────────────────────────────
with row1_c2:
    st.markdown('<div class="section-title">🏆 Top 10 par note</div>', unsafe_allow_html=True)

    top_rated = (
        df_viz[df_viz["score"] > 0]
        .nlargest(10, "score")[["title", "score", "ratings"]]
        .sort_values("score")
    )

    fig_top = px.bar(
        top_rated,
        x="score",
        y="title",
        orientation="h",          # Barres horizontales → plus lisible pour les noms longs
        color="score",
        color_continuous_scale=[[0, "#3a3f5c"], [0.5, "#6c8dff"], [1, "#a78bfa"]],
        template=PLOTLY_TEMPLATE,
        text="score",
        labels={"score": "Note", "title": "Application"},
    )
    fig_top.update_traces(texttemplate="%{text:.1f} ⭐", textposition="outside")
    fig_top.update_layout(
        plot_bgcolor="#1e2130",
        paper_bgcolor="#1e2130",
        coloraxis_showscale=False,
        xaxis=dict(range=[0, 5.8]),
        margin=dict(l=10, r=80, t=10, b=10),
        yaxis_title="",
    )
    st.plotly_chart(fig_top, use_container_width=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# ROW 2 : Top 10 installations + Pie Gratuit/Payant
# ══════════════════════════════════════════════════════════════════════════════

row2_c1, row2_c2 = st.columns(2)

# ── 3. Top 10 par installations ────────────────────────────────────────────────
with row2_c1:
    st.markdown('<div class="section-title">📥 Top 10 par popularité (avis)</div>',
                unsafe_allow_html=True)

    top_popular = (
        df_viz.nlargest(10, "ratings")[["title", "ratings", "score"]]
        .sort_values("ratings")
    )

    fig_pop = px.bar(
        top_popular,
        x="ratings",
        y="title",
        orientation="h",
        color="score",
        color_continuous_scale=[[0, "#1a3a2a"], [0.5, "#34d399"], [1, "#6c8dff"]],
        template=PLOTLY_TEMPLATE,
        text="ratings",
        labels={"ratings": "Nombre d'avis", "title": "Application", "score": "Note"},
    )
    fig_pop.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig_pop.update_layout(
        plot_bgcolor="#1e2130",
        paper_bgcolor="#1e2130",
        margin=dict(l=10, r=80, t=10, b=10),
        yaxis_title="",
    )
    st.plotly_chart(fig_pop, use_container_width=True)

# ── 4. Pie chart Gratuit vs Payant ────────────────────────────────────────────
with row2_c2:
    st.markdown('<div class="section-title">💰 Modèle économique</div>', unsafe_allow_html=True)

    free_count = (df_viz["free"] == True).sum()
    paid_count = (df_viz["free"] == False).sum()

    fig_pie = go.Figure(data=[go.Pie(
        labels=["Gratuit", "Payant"],
        values=[free_count, paid_count],
        hole=0.5,                          # Donut chart : plus moderne qu'un pie plein
        marker_colors=["#34d399", "#fb923c"],
        textinfo="label+percent",
        textfont_size=13,
    )])
    fig_pie.update_layout(
        template=PLOTLY_TEMPLATE,
        plot_bgcolor="#1e2130",
        paper_bgcolor="#1e2130",
        showlegend=False,
        annotations=[dict(
            text=f"{free_count + paid_count}<br>apps",
            x=0.5, y=0.5,
            font_size=14,
            font_color="#a0a8c0",
            showarrow=False,
        )],
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    st.caption(f"{free_count} gratuites · {paid_count} payantes")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# ROW 3 : Distribution par genre + Scatter Note vs Popularité
# ══════════════════════════════════════════════════════════════════════════════

row3_c1, row3_c2 = st.columns(2)

# ── 5. Distribution par genre ─────────────────────────────────────────────────
with row3_c1:
    st.markdown('<div class="section-title">🏷️ Distribution par genre</div>', unsafe_allow_html=True)

    genre_counts = (
        df_viz["genre"]
        .value_counts()
        .reset_index()
        .rename(columns={"index": "genre", "count": "nombre"})
    )
    # Compatibilité pandas : les noms de colonnes peuvent varier selon la version
    if genre_counts.columns.tolist() == ["genre", "count"]:
        pass  # pandas >= 2.0
    else:
        genre_counts.columns = ["genre", "nombre"]

    # Renommer pour être sûr
    genre_counts.columns = ["genre", "nombre"]

    fig_genre = px.bar(
        genre_counts,
        x="genre",
        y="nombre",
        color="nombre",
        color_continuous_scale=[[0, "#1e2848"], [1, "#6c8dff"]],
        template=PLOTLY_TEMPLATE,
        labels={"genre": "Genre", "nombre": "Nombre d'apps"},
    )
    fig_genre.update_layout(
        plot_bgcolor="#1e2130",
        paper_bgcolor="#1e2130",
        coloraxis_showscale=False,
        xaxis_tickangle=-30,
        margin=dict(l=10, r=10, t=10, b=60),
        yaxis_title="",
    )
    st.plotly_chart(fig_genre, use_container_width=True)

# ── 6. Scatter Note vs Popularité ────────────────────────────────────────────
with row3_c2:
    st.markdown('<div class="section-title">🔵 Note vs Popularité</div>', unsafe_allow_html=True)

    df_scatter = df_viz[(df_viz["score"] > 0) & (df_viz["ratings"] > 0)].copy()

    fig_scatter = px.scatter(
        df_scatter,
        x="score",
        y="ratings",
        color="genre",
        size="ratings",
        size_max=40,
        hover_name="title",
        hover_data={"score": ":.2f", "ratings": ":,", "developer": True, "genre": False},
        template=PLOTLY_TEMPLATE,
        color_discrete_sequence=COLORS_PALETTE,
        labels={"score": "Note (sur 5)", "ratings": "Nombre d'avis", "genre": "Genre"},
    )
    fig_scatter.update_layout(
        plot_bgcolor="#1e2130",
        paper_bgcolor="#1e2130",
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font_size=10),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.caption("La taille des bulles est proportionnelle au nombre d'avis.")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# ROW 4 : Word Cloud des descriptions
# ══════════════════════════════════════════════════════════════════════════════

st.markdown('<div class="section-title">☁️ Word Cloud des descriptions</div>', unsafe_allow_html=True)

# Concaténer toutes les descriptions disponibles
all_text = " ".join(df_viz["description"].dropna().astype(str).tolist())

if len(all_text.strip()) < 50:
    st.info("Pas assez de texte pour générer un Word Cloud.")
else:
    # Nettoyage basique : supprimer les caractères spéciaux et les mots trop courts
    all_text_clean = re.sub(r"[^a-zA-Z\s]", " ", all_text.lower())

    # Mots vides à exclure (stopwords manuels pour compléter ceux de WordCloud)
    extra_stopwords = {"app", "apps", "application", "use", "using", "get", "make",
                       "one", "also", "will", "can", "new", "free", "best", "your",
                       "the", "and", "for", "you", "this", "with", "that", "are",
                       "from", "have", "more", "all", "our", "their", "they", "its"}

    try:
        wc = WordCloud(
            width=1400,
            height=400,
            background_color="#1e2130",    # Fond sombre
            colormap="cool",               # Palette bleue/violette cohérente avec l'app
            max_words=120,
            stopwords=extra_stopwords,
            collocations=False,            # Éviter les bigrams pour plus de lisibilité
            min_font_size=10,
        ).generate(all_text_clean)

        # Affichage via matplotlib (WordCloud ne supporte pas Plotly nativement)
        fig_wc, ax = plt.subplots(figsize=(14, 4), facecolor="#1e2130")
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        plt.tight_layout(pad=0)
        st.pyplot(fig_wc, use_container_width=True)
        st.caption(f"Basé sur {len(df_viz)} descriptions d'applications.")
    except Exception as e:
        st.error(f"Erreur Word Cloud : {e}")

st.markdown("---")

# ── Résumé statistique ────────────────────────────────────────────────────────
with st.expander("📋 Voir le résumé statistique détaillé"):
    num_cols = ["score", "ratings", "price"]
    st.dataframe(
        df_viz[num_cols].describe().round(2),
        use_container_width=True,
    )