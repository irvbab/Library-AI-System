import streamlit as st
import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Mon Libraire IA", page_icon="")

st.title(" Système de Recommandation de Irvine Babeni-Lutumba")
st.write("Projet de Certification - Épreuve E3 (Déploiement)")

# --- FONCTION DE CHARGEMENT ---
@st.cache_data 
def load_data():
    conn = sqlite3.connect('library.db')
    df = pd.read_sql_query("SELECT * FROM books", conn)
    conn.close()
    return df

try:
    df = load_data()

    # --- PRÉPARATION DE L'IA ---
    df['metadata_soup'] = df['categorie'].fillna('') + " " + df['description'].fillna('')
    
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['metadata_soup'])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # --- INTERFACE UTILISATEUR ---
    col1, col2 = st.columns([2, 1]) # On divise l'écran pour le design
    
    with col1:
        livre_choisi = st.selectbox("Choisissez un livre :", df['titre'].values)
    
    with col2:
        # --- LE CURSEUR POUR LE NOMBRE DE RÉSULTATS ---
        nb_res = st.slider("Nombre de résultats", min_value=3, max_value=10, value=5)

    if st.button("Recommander des livres similaires"):
        idx = df[df['titre'] == livre_choisi].index[0]
        
        # Calcul des scores de similarité
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # On prend le nombre choisi par l'utilisateur (on commence à 1 pour ignorer le livre lui-même)
        top_recommandations = sim_scores[1 : nb_res + 1]

        st.divider()
        st.subheader(f" Top {nb_res} des recommandations pour vous :")
        
        for i, score in top_recommandations:
            # Utilisation de expander pour ne pas encombrer la page si on a 10 résultats
            with st.expander(f" {df['titre'].iloc[i]} (Match : {round(score*100, 2)}%)"):
                st.write(f"**Catégorie :** {df['categorie'].iloc[i]}")
                st.write(f"**Auteur(s) :** {df['auteurs'].iloc[i]}")
                st.info(df['description'].iloc[i])
                st.write(f"**ISBN :** {df['isbn'].iloc[i]}")

except Exception as e:
    st.error(f"Erreur lors du chargement : {e}")
    st.write("Assurez-vous d'avoir lancé 'database_setup.py' avant.")