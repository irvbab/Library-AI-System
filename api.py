from fastapi import FastAPI
import sqlite3

app = FastAPI(title="Library API for E1 Certification")

@app.get("/books")
def get_books():
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        # On utilise les noms de colonnes en français tels qu'identifiés
        cursor.execute("SELECT titre, auteurs, categorie FROM books LIMIT 10")
        books = cursor.fetchall()
        conn.close()
        
        # On transforme le résultat en liste de dictionnaires pour que ce soit plus joli
        result = []
        for book in books:
            result.append({
                "titre": book[0],
                "auteurs": book[1],
                "categorie": book[2]
            })
            
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API de la Librairie (Bloc E1)"}