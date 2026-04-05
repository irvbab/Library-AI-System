import sqlite3
import pandas as pd
import os

def setup_database():
    # Définition des chemins
    dossier = os.path.dirname(os.path.abspath(__file__))
    chemin_csv = os.path.join(dossier, "clean_books_data.csv")
    chemin_db = os.path.join(dossier, "library.db")

    # 1. Connexion à SQLite
    conn = sqlite3.connect(chemin_db)
    cursor = conn.cursor()

    # 2. Création de la table avec la colonne CATEGORIE (Bloc 1 - C2)
    # On supprime l'ancienne table si elle existe pour la mettre à jour
    cursor.execute('DROP TABLE IF EXISTS books')
    
    cursor.execute('''
        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            auteurs TEXT,
            description TEXT,
            categorie TEXT,
            isbn TEXT
        )
    ''')

    # 3. Chargement des données du CSV
    if not os.path.exists(chemin_csv):
        print(f"❌ Erreur : Le fichier {chemin_csv} est introuvable !")
        return

    df = pd.read_csv(chemin_csv)
    
    # 4. Insertion des données (Transfert du CSV vers SQL)
    # On s'assure que le DataFrame contient bien les mêmes colonnes que la table
    df.to_sql('books', conn, if_exists='replace', index=False)

    print(f" Base de données mise à jour avec succès : {chemin_db}")
    
    # 5. Vérification
    cursor.execute("SELECT COUNT(*) FROM books")
    count = cursor.fetchone()[0]
    print(f" Nombre de livres insérés dans la table SQL : {count}")

    conn.close()

if __name__ == "__main__":
    setup_database()