import streamlit as st
import pandas as pd

# ── PARTIE 1 : Display widgets ──────────────────────────────────────────────
# Ces widgets servent uniquement à afficher du contenu (pas d'interaction)

st.title("🧪 Test App — Découverte de Streamlit")
st.header("1. Display Widgets")
st.subheader("Texte et mise en forme")
st.text("Ceci est du texte brut.")
st.markdown("Ceci est du **markdown** : *italique*, **gras**, `code`")
st.code("print('Hello Streamlit!')", language="python")
st.latex(r"E = mc^2")

# ── PARTIE 2 : Input widgets ────────────────────────────────────────────────
# Ces widgets permettent à l'utilisateur d'entrer des données

st.header("2. Input Widgets")

nom = st.text_input("Ton prénom", placeholder="Ex: Hiba")
age = st.number_input("Ton âge", min_value=0, max_value=120, value=20)
date = st.date_input("Date d'aujourd'hui")

if nom:
    st.success(f"Bonjour {nom}, tu as {age} ans !")

# ── PARTIE 3 : Filter widgets ────────────────────────────────────────────────
# Widgets de sélection : utiles pour filtrer des données

st.header("3. Filter Widgets")

choix = st.radio("Choisis une option", ["Option A", "Option B", "Option C"])
st.write(f"Tu as choisi : {choix}")

slider_val = st.slider("Sélectionne une valeur", 0, 100, 50)
st.write(f"Valeur du slider : {slider_val}")

options = st.multiselect("Choisis plusieurs langues",
                          ["Python", "R", "SQL", "Java", "JavaScript"],
                          default=["Python"])
st.write(f"Langues choisies : {options}")

coché = st.checkbox("J'accepte les conditions")
if coché:
    st.info("Conditions acceptées ✅")

# ── PARTIE 4 : Streamlit Magic ───────────────────────────────────────────────
# La "magie" Streamlit : écrire df suffit pour l'afficher automatiquement
# Sans avoir besoin de st.dataframe(df) !

st.header("4. Streamlit Magic")

df = pd.DataFrame({
    "Nom":   ["Alice", "Bob", "Hiba", "Rime"],
    "Note":  [4.5, 3.2, 4.8, 4.1],
    "Ville": ["Rabat", "Casablanca", "Salé", "Fès"]
})

# MAGIC : juste écrire df sans rien d'autre — Streamlit l'affiche tout seul !
df

# ── PARTIE 5 : Layout et containers ─────────────────────────────────────────
# Organiser les éléments en colonnes et sections

st.header("5. Layout & Containers")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Utilisateurs", "1,234", "+12%")

with col2:
    st.metric("Revenus", "45,678 €", "-3%")

with col3:
    st.metric("Apps analysées", "89", "+5")

with st.expander("Cliquer pour voir plus de détails"):
    st.write("Ce contenu est caché par défaut.")
    st.dataframe(df)

# Sidebar
with st.sidebar:
    st.title("⚙️ Paramètres")
    theme = st.selectbox("Thème", ["Clair", "Sombre"])
    st.write(f"Thème choisi : {theme}")