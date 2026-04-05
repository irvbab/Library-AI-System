import sqlite3
import pandas as pd
import os

def setup_database():
    dossier = os.path.dirname(os.path.abspath(__file__))
    chemin_csv = os.path.join(dossier, "clean_books_data.csv")
    chemin_db = os.path.join(dossier, "library.db")

    if not os.path.exists(chemin_csv):
        print(" Erreur : Fichier CSV introuvable !")
        return

    # 1. Charger le CSV
    df = pd.read_csv(chemin_csv)

    # 2. AJOUTER LA COLONNE MANQUANTE (La Magie !)
    # Si la colonne n'existe pas, on la crée avec une valeur par défaut
    if 'categorie' not in df.columns:
        print("💡 Ajout automatique de la colonne 'categorie'...")
        df['categorie'] = "Littérature" # Valeur par défaut
        
        # Petit bonus : si le titre contient "philosophie", on change la catégorie
        df.loc[df['titre'].str.contains('philosophie', case=False), 'categorie'] = 'Philosophie'

    # 3. Connexion et Injection dans SQL
    conn = sqlite3.connect(chemin_db)
    df.to_sql('books', conn, if_exists='replace', index=False)
    conn.close()
    
    print(f" Base de données 'library.db' créée avec la colonne 'categorie' !")

if __name__ == "__main__":
    setup_database()