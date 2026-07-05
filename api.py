import logging
import os
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
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

# 2. AUTHENTIFICATION PAR FORMULAIRE + SESSION (C5 / C9)
# Les identifiants sont lus depuis des variables d'environnement pour ne jamais être exposés dans le code
API_USERNAME = os.getenv("LIBRARY_API_USER", "admin")
API_PASSWORD = os.getenv("LIBRARY_API_PASSWORD", "admin123")
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "cle-secrete-a-changer-en-production")

app = FastAPI(
    title="Library AI API",
    description="API REST sécurisée exposant le moteur de recommandation TF-IDF.",
    version="1.0.0"
)
# Middleware de session : permet de garder l'utilisateur connecté via un cookie signé
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)


def is_authenticated(request: Request) -> bool:
    """Vérifie si la session en cours a été validée par un login réussi."""
    return request.session.get("authentifie", False)


LOGIN_FORM_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head><meta charset="utf-8"><title>Connexion — Library AI API</title></head>
<body style="font-family: Arial, sans-serif; max-width: 360px; margin: 80px auto;">
    <h2>Connexion</h2>
    {error_message}
    <form method="post" action="/login">
        <label>Nom d'utilisateur</label><br>
        <input type="text" name="username" style="width: 100%; padding: 8px; margin: 6px 0;"><br>
        <label>Mot de passe</label><br>
        <input type="password" name="password" style="width: 100%; padding: 8px; margin: 6px 0;"><br><br>
        <button type="submit" style="padding: 8px 16px;">Se connecter</button>
    </form>
</body>
</html>
"""


def get_db_connection():
    """Ouvre une connexion à library.db avec accès aux colonnes par nom."""
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    return conn


# Route d'accueil : affiche le formulaire, ou les endpoints si déjà connecté
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    if is_authenticated(request):
        logging.info("Accès à la page d'accueil (authentifié)")
        return ENDPOINTS_HTML
    return LOGIN_FORM_HTML.format(error_message="")


# Traitement du formulaire de connexion
@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == API_USERNAME and password == API_PASSWORD:
        request.session["authentifie"] = True
        logging.info(f"Connexion réussie pour l'utilisateur '{username}'")
        return RedirectResponse(url="/", status_code=303)
    logging.warning(f"Tentative de connexion échouée pour l'utilisateur '{username}'")
    error_html = "<p style='color: red;'>Nom d'utilisateur ou mot de passe incorrect.</p>"
    return LOGIN_FORM_HTML.format(error_message=error_html)


# Déconnexion : ferme la session, revient au formulaire
@app.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


# Route de recommandation : protégée par la session (pas par un en-tête)
@app.get("/recommend/{book_id}")
async def recommend(book_id: int, request: Request):
    if not is_authenticated(request):
        logging.warning("Tentative d'accès à /recommend sans authentification")
        raise HTTPException(status_code=401, detail="Veuillez vous connecter via le formulaire sur la page d'accueil.")
    try:
        conn = get_db_connection()
        df = pd.read_sql_query("SELECT * FROM books", conn)
        conn.close()

        if book_id < 0 or book_id >= len(df):
            logging.warning(f"Tentative de recommandation pour un ID inexistant : {book_id}")
            raise HTTPException(status_code=404, detail="Livre non trouvé")

        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(df['description'].fillna(''))
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

        sim_scores = sorted(enumerate(cosine_sim[book_id]), key=lambda x: x[1], reverse=True)[1:4]
        book_indices = [i for i, _ in sim_scores]
        result = df.iloc[book_indices][['titre', 'auteurs']].reset_index().rename(columns={'index': 'id'}).to_dict(orient='records')

        logging.info(f"Recommandations générées avec succès pour le livre {book_id}")
        return {"book_id": book_id, "recommendations": result}

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Erreur serveur : {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")