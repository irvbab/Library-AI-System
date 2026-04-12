import os
import sqlite3
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_api_status():
    """Vérifie que l'accueil de l'API fonctionne"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Bienvenue" in response.json()["message"]

def test_database_connection():
    """Vérifie que la base de données est accessible"""
    assert os.path.exists("library.db") == True
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='books'")
    assert cursor.fetchone() is not None
    conn.close()