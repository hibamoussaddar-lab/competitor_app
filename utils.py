"""
utils.py
--------
Fonctions utilitaires centralisées pour l'application Competitor Analysis.
Ce fichier est importé par toutes les pages. Il contient :
  - La recherche d'apps Google Play
  - La récupération des avis d'une app
  - L'analyse de sentiment via le modèle pré-entraîné VADER (local, sans API)
"""

import pandas as pd
import streamlit as st
from google_play_scraper import search, reviews, Sort


# ─────────────────────────────────────────────
# 1. RECHERCHE D'APPLICATIONS
# ─────────────────────────────────────────────

def search_apps(query: str, n_results: int = 20, lang: str = "en", country: str = "us") -> pd.DataFrame:
    """
    Cherche des applications sur le Google Play Store.

    Paramètres
    ----------
    query      : Terme de recherche saisi par l'utilisateur (ex: "note taking ai")
    n_results  : Nombre maximum de résultats à retourner
    lang       : Langue des résultats ("en", "fr", "ar"…)
    country    : Pays du store ("us", "ma", "fr"…)

    Retourne
    --------
    Un DataFrame pandas avec une ligne par application.
    """
    try:
        results = search(
            query,
            lang=lang,
            country=country,
            n_hits=n_results,
        )

        # On sélectionne les colonnes utiles pour l'analyse
        records = []
        for app in results:
            records.append({
                "appId":         app.get("appId", ""),
                "title":         app.get("title", ""),
                "developer":     app.get("developer", ""),
                "score":         app.get("score", 0.0),          # Note moyenne (sur 5)
                "ratings":       app.get("ratings", 0),           # Nb total d'évaluations
                "installs":      app.get("installs", "0"),         # Fourchette d'installations
                "price":         app.get("price", 0.0),            # 0.0 = gratuit
                "free":          app.get("free", True),
                "genre":         app.get("genre", "Unknown"),
                "description":   app.get("description", ""),
                "icon":          app.get("icon", ""),
                "url":           app.get("url", ""),
                "released":      app.get("released", ""),
                "updated":       app.get("updated", ""),
            })

        df = pd.DataFrame(records)

        # Nettoyage : remplacer les NaN dans les colonnes numériques
        df["score"]   = pd.to_numeric(df["score"],   errors="coerce").fillna(0.0)
        df["ratings"] = pd.to_numeric(df["ratings"], errors="coerce").fillna(0)
        df["price"]   = pd.to_numeric(df["price"],   errors="coerce").fillna(0.0)

        return df

    except Exception as e:
        st.error(f"Erreur lors de la recherche : {e}")
        return pd.DataFrame()


# ─────────────────────────────────────────────
# 2. RÉCUPÉRATION DES AVIS D'UNE APPLICATION
# ─────────────────────────────────────────────

def get_reviews(app_id: str, n: int = 50, lang: str = "en", country: str = "us") -> list[str]:
    """
    Récupère les avis textuels d'une application Google Play.

    Paramètres
    ----------
    app_id  : Identifiant unique de l'app (ex: "com.google.android.keep")
    n       : Nombre d'avis à récupérer (max recommandé : 100)
    lang    : Langue des avis
    country : Pays du store

    Retourne
    --------
    Une liste de chaînes de caractères (textes des avis).
    """
    try:
        result, _ = reviews(
            app_id,
            lang=lang,
            country=country,
            sort=Sort.MOST_RELEVANT,
            count=n,
        )
        # On extrait uniquement le champ "content" (texte de l'avis)
        texts = [r["content"] for r in result if r.get("content")]
        return texts
    except Exception as e:
        st.warning(f"Impossible de récupérer les avis pour {app_id} : {e}")
        return []


# ─────────────────────────────────────────────
# 3. ANALYSE DE SENTIMENT (modèle pré-entraîné VADER, local)
# ─────────────────────────────────────────────

# VADER (Valence Aware Dictionary and sEntiment Reasoner) est un modèle
# pré-entraîné spécialisé pour les textes courts et informels (réseaux sociaux,
# avis utilisateurs...). Il fonctionne 100% en local, sans API ni GPU,
# ce qui le rend idéal pour un déploiement Streamlit Community Cloud.
#
# Il retourne un score "compound" entre -1 (très négatif) et +1 (très positif).
# On le convertit en 3 classes : positive / neutral / negative
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment_batch(texts: list[str]) -> list[dict]:
    """
    Analyse une liste de textes avec le modèle pré-entraîné VADER.

    Paramètres
    ----------
    texts : Liste de chaînes à analyser

    Retourne
    --------
    Liste de dicts : [{"label": "positive"|"neutral"|"negative", "score": float}, ...]
    """
    if not texts:
        return []

    results = []
    for text in texts:
        scores = _analyzer.polarity_scores(text)
        compound = scores["compound"]

        # Seuils standards recommandés par VADER
        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        results.append({"label": label, "score": abs(compound)})

    return results


def compute_sentiment_score(app_id: str, n_reviews: int = 30) -> dict:
    """
    Calcule un score de sentiment agrégé pour une application.

    Paramètres
    ----------
    app_id    : Identifiant de l'application
    n_reviews : Nombre d'avis à analyser

    Retourne
    --------
    Dict avec les clés :
      - "app_id"    : str
      - "positive"  : float (proportion 0–1)
      - "neutral"   : float
      - "negative"  : float
      - "score"     : float (score composite entre -1 et 1)
      - "n_reviews" : int (nombre d'avis réellement analysés)
    """
    texts = get_reviews(app_id, n=n_reviews)

    if not texts:
        return {
            "app_id": app_id, "positive": 0, "neutral": 0,
            "negative": 0, "score": 0.0, "n_reviews": 0,
        }

    sentiments = analyze_sentiment_batch(texts)

    counts = {"positive": 0, "neutral": 0, "negative": 0}
    for s in sentiments:
        label = s.get("label", "neutral").lower()
        # Normalisation des labels du modèle (parfois "LABEL_0" etc.)
        if "pos" in label:
            counts["positive"] += 1
        elif "neg" in label:
            counts["negative"] += 1
        else:
            counts["neutral"] += 1

    total = len(sentiments) or 1
    pos = counts["positive"] / total
    neu = counts["neutral"]  / total
    neg = counts["negative"] / total

    # Score composite : +1 = 100% positif, -1 = 100% négatif
    composite = pos - neg

    return {
        "app_id":    app_id,
        "positive":  round(pos, 3),
        "neutral":   round(neu, 3),
        "negative":  round(neg, 3),
        "score":     round(composite, 3),
        "n_reviews": len(sentiments),
    }