import logging
import os
from fastapi import FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 1. CONFIGURATION DES LOGS (C21)
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 2. AUTHENTIFICATION PAR CLÉ API (C5 / C9)
# La clé est lue depuis une variable d'environnement pour ne jamais être exposée dans le code
API_KEY = os.getenv("LIBRARY_API_KEY", "dev-key-123")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
    """Vérifie que la clé API fournie dans le header X-API-Key est valide."""
    if api_key != API_KEY:
        logging.warning("Tentative d'accès avec une clé API invalide")
        raise HTTPException(
            status_code=401,
            detail="Clé API invalide ou absente. Fournissez votre clé dans le header X-API-Key."
        )
    return api_key

app = FastAPI(
    title="Library AI API",
    description="API REST sécurisée exposant le moteur de recommandation TF-IDF.",
    version="1.0.0"
)

def get_db_connection():
    """Ouvre une connexion à library.db avec accès aux colonnes par nom."""
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    return conn

# Route d'accueil : health check (non protégée, pour vérifier que l'API est en ligne)
@app.get("/")
async def root():
    logging.info("Accès à la page d'accueil")
    return {"message": "Bienvenue sur l'API de la Librairie IA"}

# Route de recommandation : protégée par clé API
# book_id correspond ici à la position du livre dans la table (0 = premier livre)
@app.get("/recommend/{book_id}")
async def recommend(book_id: int, api_key: str = Security(verify_api_key)):
    try:
        conn = get_db_connection()
        df = pd.read_sql_query("SELECT * FROM books", conn)
        conn.close()

        # Gestion d'erreur : index hors limites → 404
        if book_id < 0 or book_id >= len(df):
            logging.warning(f"Tentative de recommandation pour un ID inexistant : {book_id}")
            raise HTTPException(status_code=404, detail="Livre non trouvé")

        # Algorithme TF-IDF + similarité cosinus
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(df['description'].fillna(''))
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

        sim_scores = sorted(enumerate(cosine_sim[book_id]), key=lambda x: x[1], reverse=True)[1:4]

        book_indices = [i for i, _ in sim_scores]
        # Utilisation des noms de colonnes réels de la base (français), id = index de ligne
        result = df.iloc[book_indices][['titre', 'auteurs']].reset_index().rename(columns={'index': 'id'}).to_dict(orient='records')

        logging.info(f"Recommandations générées avec succès pour le livre {book_id}")
        return {"book_id": book_id, "recommendations": result}

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Erreur serveur : {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")
