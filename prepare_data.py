import pandas as pd
import json
import os
import re

def clean_html(text):
    """Supprime les résidus de code HTML dans les descriptions."""
    if not text or not isinstance(text, str):
        return "Description non disponible"
    # Supprime les balises type <p>, <br>, <b>...
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip()

def prepare_all_data():
    # 1. Localisation du fichier
    dossier = os.path.dirname(os.path.abspath(__file__))
    chemin_entree = os.path.join(dossier, "raw_books_data.json")
    chemin_sortie = os.path.join(dossier, "clean_books_data.csv")

    if not os.path.exists(chemin_entree):
        print("❌ Erreur : Le fichier 'raw_books_data.json' est introuvable !")
        return

    # 2. Chargement de TOUS les documents
    with open(chemin_entree, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    total_initial = len(df)
    print(f"📂 Lecture de {total_initial} documents...")

    # 3. Nettoyage global (C3)
    # Suppression des doublons (si un livre a été collecté deux fois)
    df = df.drop_duplicates(subset=['titre', 'isbn'], keep='first')
    
    # Nettoyage des textes sur TOUTES les colonnes textuelles
    df['description'] = df['description'].apply(clean_html)
    df['titre'] = df['titre'].apply(lambda x: x.strip().capitalize() if isinstance(x, str) else x)
    
    # Remplacement des valeurs vides pour SQL
    df = df.fillna("Non renseigné")

    # 4. Sauvegarde
    df.to_csv(chemin_sortie, index=False, encoding="utf-8-sig") # utf-8-sig pour que Excel l'ouvre bien
    
    print(f" Nettoyage terminé !")
    print(f" Résultat : {len(df)} livres uniques et propres sur {total_initial} au départ.")
    print(f" Fichier créé : {chemin_sortie}")

if __name__ == "__main__":
    prepare_all_data()