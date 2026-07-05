import streamlit as st
import sqlite3
import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="Mon Libraire IA", page_icon="")

API_USERNAME = os.getenv("LIBRARY_API_USER", "admin")
API_PASSWORD = os.getenv("LIBRARY_API_PASSWORD", "admin123")

if "authentifie" not in st.session_state:
    st.session_state.authentifie = False

# --- FORMULAIRE DE CONNEXION ---
if not st.session_state.authentifie:
    st.title(" Connexion — Système de Recommandation")
    st.write("Merci de vous identifier pour accéder au moteur de recommandation.")
    nom_utilisateur = st.text_input("Nom d'utilisateur")
    mot_de_passe = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if nom_utilisateur == API_USERNAME and mot_de_passe == API_PASSWORD:
            st.session_state.authentifie = True
            st.rerun()
        else:
            st.error("Identifiants incorrects. Veuillez réessayer.")
    st.stop()  # bloque tout le reste de la page tant qu'on n'est pas connecté

# --- À PARTIR D'ICI : UNIQUEMENT SI CONNECTÉ ---
st.sidebar.button("Se déconnecter", on_click=lambda: st.session_state.update(authentifie=False))

st.title(" Système de Recommandation de Irvine Babeni-Lutumba")
st.write("Projet de Certification - Épreuve E3 (Déploiement)")

@st.cache_data 
def load_data():
    conn = sqlite3.connect('library.db')
    df = pd.read_sql_query("SELECT * FROM books", conn)
    conn.close()
    return df

try:
    df = load_data()
    df['metadata_soup'] = df['categorie'].fillna('') + " " + df['description'].fillna('')
    
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['metadata_soup'])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    col1, col2 = st.columns([2, 1])
    with col1:
        livre_choisi = st.selectbox("Choisissez un livre :", df['titre'].values)
    with col2:
        nb_res = st.slider("Nombre de résultats", min_value=3, max_value=10, value=5)

    if st.button("Recommander des livres similaires"):
        idx = df[df['titre'] == livre_choisi].index[0]
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        top_recommandations = sim_scores[1 : nb_res + 1]

        st.divider()
        st.subheader(f" Top {nb_res} des recommandations pour vous :")
        
        for i, score in top_recommandations:
            with st.expander(f" {df['titre'].iloc[i]} (Match : {round(score*100, 2)}%)"):
                st.write(f"**Catégorie :** {df['categorie'].iloc[i]}")
                st.write(f"**Auteur(s) :** {df['auteurs'].iloc[i]}")
                st.info(df['description'].iloc[i])
                st.write(f"**ISBN :** {df['isbn'].iloc[i]}")

except Exception as e:
    st.error(f"Erreur lors du chargement : {e}")
    st.write("Assurez-vous d'avoir lancé 'database_setup.py' avant.")