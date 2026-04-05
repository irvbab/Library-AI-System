import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def get_smart_recommendations(book_title):
    # 1. Connexion à la base
    conn = sqlite3.connect('library.db')
    df = pd.read_sql_query("SELECT * FROM books", conn)
    conn.close()

    # On s'assure que les colonnes sont bien remplies
    df['categorie'] = df['categorie'].fillna('')
    df['description'] = df['description'].fillna('')

    # 2. Création de la "Soupe de métadonnées"
    # On donne plus d'importance à la catégorie en la répétant deux fois
    df['metadata_soup'] = df['categorie'] + " " + df['categorie'] + " " + df['description']

    # 3. Vectorisation TF-IDF sur la "soupe"
    tfidf = TfidfVectorizer(stop_words='english') 
    tfidf_matrix = tfidf.fit_transform(df['metadata_soup'])

    # 4. Calcul de la similarité
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    try:
        idx = df[df['titre'] == book_title].index[0]
        
        # 5. Calcul des scores
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # On prend les 5 meilleurs
        sim_scores = sim_scores[1:6]

        print(f"\nRecommandations pour : {book_title}")
        print(f"Genre principal : {df['categorie'].iloc[idx]}")
        print("-" * 30)

        for i, score in sim_scores:
            print(f"- {df['titre'].iloc[i]} | Catégorie : {df['categorie'].iloc[i]} (Match : {round(score*100, 2)}%)")

    except IndexError:
        print("Livre non trouvé.")

if __name__ == "__main__":
    # Teste avec un livre de ta base
    get_smart_recommendations("La philosophie de moïse")