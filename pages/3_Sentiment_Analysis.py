"""
pages/3_Sentiment_Analysis.py
------------------------------
Page 3 : Analyse de sentiment ML via le modèle pré-entraîné VADER.

Fonctionnement :
  1. L'utilisateur sélectionne les apps à analyser (depuis les résultats de la page 1)
  2. Pour chaque app, on récupère ses avis Google Play via utils.get_reviews()
  3. On analyse chaque avis avec le modèle pré-entraîné VADER (local, sans API)
  4. On calcule les proportions positif/neutre/négatif par application
  5. On affiche : bar chart des scores, détail par app, tableau complet

Concept clé — Modèle pré-entraîné VADER :
  VADER (Valence Aware Dictionary and sEntiment Reasoner) est un modèle de
  sentiment basé sur un lexique, spécialement conçu pour les textes courts et
  informels (réseaux sociaux, avis utilisateurs). Il tourne 100% en local,
  sans GPU et sans appel API, ce qui le rend idéal pour Streamlit Cloud.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import compute_sentiment_score, get_reviews, analyze_sentiment_batch

# ── Configuration ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sentiment Analysis — Competitor Analysis",
    page_icon="🤖",
    layout="wide",
)

st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    [data-testid="stSidebar"] { background-color: #151722; }
    .sentiment-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 2px;
    }
    .pos { background: #1a3a2a; color: #4ade80; border: 1px solid #4ade80; }
    .neu { background: #2a2a1a; color: #facc15; border: 1px solid #facc15; }
    .neg { background: #3a1a1a; color: #f87171; border: 1px solid #f87171; }
    .section-title {
        font-size: 1.1rem; font-weight: 600; color: #a0a8c0;
        border-left: 3px solid #a78bfa;
        padding-left: 10px; margin: 24px 0 12px 0;
    }
    .app-card {
        background: #1e2130; border: 1px solid #2a2f45;
        border-radius: 10px; padding: 16px; margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ── En-tête ────────────────────────────────────────────────────────────────────
st.markdown("## 🤖 Analyse de Sentiment")
st.markdown("""
Analyse automatique du sentiment des avis utilisateurs via le modèle pré-entraîné
**VADER** (Valence Aware Dictionary and sEntiment Reasoner).
""")
st.markdown("---")

# ── Vérification des données en session ───────────────────────────────────────
if "df_results" not in st.session_state or st.session_state["df_results"].empty:
    st.warning("⚠️ Aucune donnée disponible.")
    st.info("Allez d'abord sur la page **Résultats** pour lancer une recherche.")
    st.stop()

df: pd.DataFrame = st.session_state["df_results"]
query = st.session_state.get("last_query", "")

# ── Sidebar : sélection des apps + paramètres ─────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")

    # Sélection des apps à analyser (max 5 recommandé pour éviter trop d'appels API)
    app_options = {
        f"{row['title']} ({row['appId']})": row["appId"]
        for _, row in df.iterrows()
        if row.get("appId")
    }

    selected_labels = st.multiselect(
        "Applications à analyser",
        options=list(app_options.keys()),
        default=list(app_options.keys())[:3],   # Les 3 premières par défaut
        help="Limitez à 3–5 apps pour des résultats rapides",
    )

    n_reviews_per_app = st.slider(
        "Avis par application",
        min_value=10,
        max_value=80,
        value=20,
        step=10,
        help="Plus d'avis = meilleure précision, mais analyse plus longue",
    )

    analyze_btn = st.button("▶️ Lancer l'analyse", type="primary", use_container_width=True)

    st.markdown("---")
    st.markdown("**À propos du modèle**")
    st.caption("""
    **VADER** est un modèle de sentiment basé sur un lexique,
    conçu pour les textes courts et informels (avis, tweets...).
    Il prédit 3 classes : **Positif**, **Neutre**, **Négatif**.
    Fonctionne 100% en local, sans API.
    """)

# ── Affichage explications ────────────────────────────────────────────────────
if not selected_labels:
    st.info("👈 Sélectionnez au moins une application dans la barre latérale.")
    st.stop()

selected_app_ids = [app_options[label] for label in selected_labels]

# Afficher les apps sélectionnées
st.markdown(f"**{len(selected_app_ids)} application(s) sélectionnée(s) :**")
for label in selected_labels:
    st.markdown(f"- {label}")

st.markdown("---")

# ── Lancement de l'analyse ────────────────────────────────────────────────────
# Clé de cache : on recalcule uniquement si les apps ou le nb d'avis changent
cache_key = f"sentiment_{','.join(sorted(selected_app_ids))}_{n_reviews_per_app}"

if analyze_btn or ("sentiment_results" not in st.session_state):
    if analyze_btn:
        # Vider le cache si l'utilisateur relance manuellement
        st.session_state.pop("sentiment_results", None)
        st.session_state.pop("sentiment_cache_key", None)

if "sentiment_results" not in st.session_state or \
   st.session_state.get("sentiment_cache_key") != cache_key:

    if analyze_btn or "sentiment_results" not in st.session_state:

        results_list = []
        progress_bar = st.progress(0, text="Initialisation…")

        for i, app_id in enumerate(selected_app_ids):
            app_title = df[df["appId"] == app_id]["title"].iloc[0] \
                        if not df[df["appId"] == app_id].empty else app_id

            progress_bar.progress(
                (i) / len(selected_app_ids),
                text=f"Analyse de « {app_title} » ({i+1}/{len(selected_app_ids)})…"
            )

            result = compute_sentiment_score(app_id, n_reviews=n_reviews_per_app)
            result["title"] = app_title
            results_list.append(result)

        progress_bar.progress(1.0, text="Analyse terminée ✅")

        df_sentiment = pd.DataFrame(results_list)
        st.session_state["sentiment_results"]  = df_sentiment
        st.session_state["sentiment_cache_key"] = cache_key

# ── Affichage des résultats ───────────────────────────────────────────────────
if "sentiment_results" in st.session_state:
    df_sent: pd.DataFrame = st.session_state["sentiment_results"]

    if df_sent.empty or df_sent["n_reviews"].sum() == 0:
        st.warning("Aucun avis récupéré. Les apps sélectionnées n'ont peut-être pas d'avis disponibles.")
        st.stop()

    # ── KPIs globaux ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📊 Résumé global</div>', unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        best_app = df_sent.loc[df_sent["score"].idxmax(), "title"]
        st.metric("🏆 App la plus positive", best_app[:25] + ("…" if len(best_app) > 25 else ""))

    with k2:
        avg_pos = df_sent["positive"].mean() * 100
        st.metric("😊 % Positif moyen", f"{avg_pos:.1f}%")

    with k3:
        avg_neg = df_sent["negative"].mean() * 100
        st.metric("😞 % Négatif moyen", f"{avg_neg:.1f}%")

    with k4:
        total_reviews = df_sent["n_reviews"].sum()
        st.metric("📝 Avis analysés", f"{total_reviews:,}")

    st.markdown("---")

    # ── Bar chart : Score composite par app ───────────────────────────────────
    st.markdown('<div class="section-title">🎯 Score de sentiment par application</div>',
                unsafe_allow_html=True)
    st.caption("Score composite entre -1 (très négatif) et +1 (très positif)")

    df_sent_sorted = df_sent.sort_values("score", ascending=True)

    colors = ["#f87171" if s < 0 else "#4ade80" for s in df_sent_sorted["score"]]

    fig_score = go.Figure(go.Bar(
        x=df_sent_sorted["score"],
        y=df_sent_sorted["title"],
        orientation="h",
        marker_color=colors,
        text=[f"{s:+.2f}" for s in df_sent_sorted["score"]],
        textposition="outside",
    ))
    fig_score.add_vline(x=0, line_color="#ffffff", line_width=1, opacity=0.3)
    fig_score.update_layout(
        template="plotly_dark",
        plot_bgcolor="#1e2130",
        paper_bgcolor="#1e2130",
        xaxis=dict(range=[-1.2, 1.2], title="Score (-1 = négatif, +1 = positif)"),
        yaxis_title="",
        margin=dict(l=10, r=60, t=10, b=10),
        height=max(200, len(df_sent_sorted) * 55),
    )
    st.plotly_chart(fig_score, use_container_width=True)

    st.markdown("---")

    # ── Bar chart empilé : répartition pos/neu/neg ─────────────────────────────
    st.markdown('<div class="section-title">📊 Répartition des sentiments par application</div>',
                unsafe_allow_html=True)

    # Transformer le DataFrame en format long pour Plotly
    df_stacked = df_sent[["title", "positive", "neutral", "negative"]].copy()
    df_stacked_long = df_stacked.melt(
        id_vars="title",
        value_vars=["positive", "neutral", "negative"],
        var_name="sentiment",
        value_name="proportion",
    )
    df_stacked_long["proportion_pct"] = (df_stacked_long["proportion"] * 100).round(1)
    df_stacked_long["sentiment_label"] = df_stacked_long["sentiment"].map({
        "positive": "😊 Positif",
        "neutral":  "😐 Neutre",
        "negative": "😞 Négatif",
    })

    fig_stacked = px.bar(
        df_stacked_long,
        x="proportion_pct",
        y="title",
        color="sentiment_label",
        orientation="h",
        text="proportion_pct",
        color_discrete_map={
            "😊 Positif": "#4ade80",
            "😐 Neutre":  "#facc15",
            "😞 Négatif": "#f87171",
        },
        template="plotly_dark",
        labels={"proportion_pct": "Proportion (%)", "title": "Application",
                "sentiment_label": "Sentiment"},
    )
    fig_stacked.update_traces(texttemplate="%{text:.0f}%", textposition="inside")
    fig_stacked.update_layout(
        plot_bgcolor="#1e2130",
        paper_bgcolor="#1e2130",
        barmode="stack",
        xaxis=dict(range=[0, 105], title="Proportion (%)"),
        yaxis_title="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=10, r=10, t=40, b=10),
        height=max(200, len(df_sent) * 55),
    )
    st.plotly_chart(fig_stacked, use_container_width=True)

    st.markdown("---")

    # ── Détail par application ─────────────────────────────────────────────────
    st.markdown('<div class="section-title">🔍 Détail par application</div>', unsafe_allow_html=True)

    selected_detail = st.selectbox(
        "Choisir une application pour voir le détail des avis",
        options=df_sent["title"].tolist(),
    )

    row_detail = df_sent[df_sent["title"] == selected_detail].iloc[0]
    app_id_detail = row_detail["app_id"]

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("😊 Positif",  f"{row_detail['positive']*100:.1f}%")
    d2.metric("😐 Neutre",   f"{row_detail['neutral']*100:.1f}%")
    d3.metric("😞 Négatif",  f"{row_detail['negative']*100:.1f}%")
    d4.metric("📝 Avis analysés", int(row_detail["n_reviews"]))

    # Bouton pour voir quelques avis avec leur sentiment
    if st.button(f"🔎 Analyser les avis de « {selected_detail[:30]} »", key="detail_btn"):
        with st.spinner("Récupération et analyse des avis…"):
            sample_texts = get_reviews(app_id_detail, n=15)
            if sample_texts:
                sample_sentiments = analyze_sentiment_batch(sample_texts)
                df_sample = pd.DataFrame({
                    "Avis": sample_texts[:len(sample_sentiments)],
                    "Sentiment": [s.get("label", "neutral").capitalize()
                                  for s in sample_sentiments],
                    "Confiance": [f"{s.get('score', 0)*100:.0f}%"
                                  for s in sample_sentiments],
                })
                # Coloriser selon le sentiment
                def color_sentiment(val):
                    if "pos" in val.lower(): return "background-color: #1a3a2a; color: #4ade80"
                    if "neg" in val.lower(): return "background-color: #3a1a1a; color: #f87171"
                    return "background-color: #2a2a1a; color: #facc15"

                st.dataframe(
                    df_sample.style.applymap(color_sentiment, subset=["Sentiment"]),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("Aucun avis disponible pour cette application.")

    st.markdown("---")

    # ── Tableau récapitulatif complet ─────────────────────────────────────────
    with st.expander("📋 Tableau complet des résultats"):
        df_display = df_sent[["title", "positive", "neutral", "negative", "score", "n_reviews"]].copy()
        df_display.columns = ["Application", "Positif", "Neutre", "Négatif", "Score", "Avis analysés"]
        for col in ["Positif", "Neutre", "Négatif"]:
            df_display[col] = (df_display[col] * 100).round(1).astype(str) + "%"
        df_display["Score"] = df_display["Score"].round(3)

        st.dataframe(df_display, use_container_width=True, hide_index=True)

        csv = df_sent.to_csv(index=False)
        st.download_button(
            "⬇️ Télécharger (CSV)",
            data=csv,
            file_name="sentiment_analysis.csv",
            mime="text/csv",
        )