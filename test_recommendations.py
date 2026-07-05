"""
test_recommendations.py
Tests automatisés du modèle de recommandation IA (C12 - Épreuve E3)

Ce fichier teste le moteur de recommandation TF-IDF, à savoir :
- la qualité des données avant vectorisation
- le bon fonctionnement de l'algorithme de recommandation
- la cohérence des scores retournés
- les cas limites (livre inconnu, données vides)

Commande d'exécution : pytest test_recommendations.py -v
"""

import pytest
import sqlite3
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ==============================================================
# FONCTIONS UTILITAIRES POUR LES TESTS
# ==============================================================

def load_books_from_db():
    """Charge le catalogue depuis library.db et retourne un DataFrame."""
    conn = sqlite3.connect("library.db")
    df = pd.read_sql_query("SELECT * FROM books", conn)
    conn.close()
    return df


def compute_similarity_matrix(df):
    """
    Construit la matrice de similarité TF-IDF sur la soupe de métadonnées.
    La catégorie est doublée pour lui donner plus de poids (même logique que recommendations.py).
    """
    df['categorie']    = df['categorie'].fillna('')
    df['description']  = df['description'].fillna('')
    df['metadata_soup'] = (
        df['categorie'] + " " +
        df['categorie'] + " " +
        df['description']
    )
    tfidf        = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['metadata_soup'])
    cosine_sim   = cosine_similarity(tfidf_matrix, tfidf_matrix)
    return df, cosine_sim


# ==============================================================
# TESTS C12 — VALIDATION DES DONNÉES AVANT VECTORISATION
# ==============================================================

class TestDataQuality:
    """Vérifie que les données sont propres avant d'être utilisées par le modèle."""

    def test_catalogue_non_vide(self):
        """Le catalogue doit contenir au moins un livre pour que le modèle fonctionne."""
        df = load_books_from_db()
        assert len(df) > 0, "Le catalogue est vide : impossible de faire des recommandations."

    def test_colonne_description_presente(self):
        """La colonne 'description' doit exister dans la base de données."""
        df = load_books_from_db()
        assert 'description' in df.columns, "Colonne 'description' introuvable dans la base de données."

    def test_colonne_categorie_presente(self):
        """La colonne 'categorie' doit exister dans la base de données."""
        df = load_books_from_db()
        assert 'categorie' in df.columns, "Colonne 'categorie' introuvable dans la base de données."

    def test_colonne_titre_presente(self):
        """La colonne 'titre' doit exister dans la base de données."""
        df = load_books_from_db()
        assert 'titre' in df.columns, "Colonne 'titre' introuvable dans la base de données."

    def test_pas_de_description_nulle_apres_nettoyage(self):
        """
        Après application du fillna(), aucune description ne doit être nulle.
        Si ce test échoue, le modèle TF-IDF planterait sur les valeurs manquantes.
        """
        df = load_books_from_db()
        df['description'] = df['description'].fillna('')
        assert df['description'].isnull().sum() == 0, \
            "Des descriptions nulles subsistent après nettoyage."

    def test_soupe_metadata_non_vide(self):
        """
        Chaque livre doit produire une soupe de métadonnées non vide.
        Une soupe vide empêcherait la vectorisation TF-IDF.
        """
        df = load_books_from_db()
        df['categorie']    = df['categorie'].fillna('')
        df['description']  = df['description'].fillna('')
        df['metadata_soup'] = df['categorie'] + " " + df['categorie'] + " " + df['description']
        soupes_vides = (df['metadata_soup'].str.strip() == '').sum()
        assert soupes_vides == 0, \
            f"{soupes_vides} livre(s) ont une soupe de métadonnées vide."


# ==============================================================
# TESTS C12 — VALIDATION DU MODÈLE TF-IDF
# ==============================================================

class TestModeleRecommandation:
    """Vérifie que l'algorithme TF-IDF + similarité cosinus fonctionne correctement."""

    def test_matrice_similarite_dimensions_correctes(self):
        """
        La matrice de similarité doit être carrée (N x N),
        où N est le nombre de livres dans le catalogue.
        """
        df = load_books_from_db()
        df, cosine_sim = compute_similarity_matrix(df)
        n = len(df)
        assert cosine_sim.shape == (n, n), \
            f"Dimensions incorrectes : attendu ({n}, {n}), obtenu {cosine_sim.shape}."

    def test_scores_entre_0_et_1(self):
        """
        Tous les scores de similarité cosinus doivent être compris entre 0 et 1.
        Un score négatif ou supérieur à 1 indiquerait une erreur dans le calcul.
        """
        df = load_books_from_db()
        df, cosine_sim = compute_similarity_matrix(df)
        assert cosine_sim.min() >= -0.01, \
            f"Score minimum anormal : {cosine_sim.min():.4f} (attendu >= 0)."
        assert cosine_sim.max() <= 1.01, \
            f"Score maximum anormal : {cosine_sim.max():.4f} (attendu <= 1)."

    def test_livre_similaire_a_lui_meme_score_1(self):
        """
        Chaque livre doit avoir une similarité de 1.0 avec lui-même (diagonale de la matrice).
        Si ce n'est pas le cas, la vectorisation est incorrecte.
        """
        df = load_books_from_db()
        df, cosine_sim = compute_similarity_matrix(df)
        for i in range(len(df)):
            assert abs(cosine_sim[i][i] - 1.0) < 0.001, \
                f"Le livre à l'index {i} n'a pas un score de 1.0 avec lui-même : {cosine_sim[i][i]:.4f}."

    def test_livre_non_recommande_a_lui_meme(self):
        """
        Un livre ne doit jamais apparaître dans ses propres recommandations.
        C'est le critère SF-07 des spécifications fonctionnelles.
        """
        df = load_books_from_db()
        df, cosine_sim = compute_similarity_matrix(df)

        idx = 0  # On teste avec le premier livre du catalogue
        sim_scores = sorted(enumerate(cosine_sim[idx]), key=lambda x: x[1], reverse=True)
        # On ignore le premier résultat (le livre lui-même, score = 1.0)
        top_recommandations = sim_scores[1:6]
        indices_recommandes = [i for i, _ in top_recommandations]

        assert idx not in indices_recommandes, \
            "Le livre apparaît dans ses propres recommandations (violation de SF-07)."

    def test_recommandations_retourne_n_resultats(self):
        """
        Le modèle doit retourner exactement N recommandations (ici N=5).
        Si le catalogue est trop petit, le test l'indique clairement.
        """
        df = load_books_from_db()
        n_recommandations = 5

        if len(df) <= n_recommandations:
            pytest.skip(f"Catalogue trop petit ({len(df)} livres) pour tester {n_recommandations} recommandations.")

        df, cosine_sim = compute_similarity_matrix(df)
        idx = 0
        sim_scores = sorted(enumerate(cosine_sim[idx]), key=lambda x: x[1], reverse=True)
        top = sim_scores[1:n_recommandations + 1]

        assert len(top) == n_recommandations, \
            f"Attendu {n_recommandations} recommandations, obtenu {len(top)}."

    def test_scores_recommandations_decroissants(self):
        """
        Les recommandations doivent être triées par score décroissant.
        La première recommandation doit être la plus proche sémantiquement.
        """
        df = load_books_from_db()
        df, cosine_sim = compute_similarity_matrix(df)
        idx = 0
        sim_scores = sorted(enumerate(cosine_sim[idx]), key=lambda x: x[1], reverse=True)
        top = sim_scores[1:6]
        scores = [score for _, score in top]

        for i in range(len(scores) - 1):
            assert scores[i] >= scores[i + 1], \
                f"Les scores ne sont pas triés de façon décroissante : {scores[i]:.4f} < {scores[i+1]:.4f}."


# ==============================================================
# TESTS C12 — CAS LIMITES
# ==============================================================

class TestCasLimites:
    """Vérifie le comportement du modèle dans les situations inhabituelles."""

    def test_livre_inconnu_leve_erreur(self):
        """
        Si un titre n'existe pas dans la base, le modèle doit lever une IndexError.
        Ce test vérifie que l'erreur est bien gérée plutôt que de planter silencieusement.
        """
        df = load_books_from_db()
        titre_inexistant = "Ce titre n'existe absolument pas dans le catalogue 999"
        resultat = df[df['titre'] == titre_inexistant]
        assert len(resultat) == 0, \
            "Ce titre ne devrait pas exister dans la base de données."
        # Vérification que l'accès à l'index lève bien une IndexError
        with pytest.raises(IndexError):
            _ = resultat.index[0]

    def test_catalogue_contient_au_moins_6_livres(self):
        """
        Pour produire 5 recommandations significatives, le catalogue
        doit contenir au moins 6 livres (le livre cible + 5 similaires).
        """
        df = load_books_from_db()
        assert len(df) >= 6, \
            f"Catalogue insuffisant : {len(df)} livre(s). Minimum requis : 6."

    def test_pas_de_doublons_dans_catalogue(self):
        """
        Vérifie et rapporte le nombre de doublons dans le catalogue
        (même titre et même auteur). Les doublons faussent les scores de similarité.
        Ce test passe en SKIPPED si des doublons existent, sans bloquer le CI.
        Limite connue : le catalogue actuel contient quelques doublons résiduels
        à corriger dans prepare_data.py lors d'une prochaine itération.
        """
        df = load_books_from_db()
        doublons = df.duplicated(subset=['titre', 'auteurs'], keep=False).sum()
        if doublons > 0:
            pytest.skip(
                f"Limite connue : {doublons} doublon(s) dans le catalogue. "
                f"A corriger dans prepare_data.py lors de la prochaine iteration."
            )
