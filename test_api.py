import os
import sqlite3
import pytest
from fastapi.testclient import TestClient
from api import app, API_USERNAME, API_PASSWORD


@pytest.fixture
def client():
    """Fournit un client de test avec une session neuve pour chaque test."""
    return TestClient(app)


def test_accueil_sans_authentification_affiche_formulaire(client):
    """Sans session, la page d'accueil doit montrer le formulaire de connexion"""
    response = client.get("/")
    assert response.status_code == 200
    assert "se connecter" in response.text.lower()


def test_recommend_refuse_sans_authentification(client):
    """Sans session, /recommend doit être refusé"""
    response = client.get("/recommend/0")
    assert response.status_code == 401


def test_login_reussi_puis_acces_page_accueil(client):
    """Avec les bons identifiants, la page d'accueil doit montrer les endpoints"""
    response = client.post(
        "/login",
        data={"username": API_USERNAME, "password": API_PASSWORD},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "endpoints disponibles" in response.text.lower()


def test_recommend_accessible_apres_login(client):
    """Une fois connecté, /recommend doit répondre normalement"""
    client.post("/login", data={"username": API_USERNAME, "password": API_PASSWORD})
    response = client.get("/recommend/0")
    assert response.status_code == 200


def test_database_connection():
    """Vérifie que la base de données est accessible"""
    assert os.path.exists("library.db") == True
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='books'")
    assert cursor.fetchone() is not None
    conn.close()