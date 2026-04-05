import requests
import json
import time
import os

def fetch_massive_books(themes_list):
    base_url = "https://www.googleapis.com/books/v1/volumes"
    all_books = []
    
    # On va chercher 100 livres par thème pour être sûr d'avoir du stock
    for theme in themes_list:
        print(f"\n--- 📚 Collecte du thème : {theme} ---")
        
        for start_index in range(0, 100, 40): # 3 appels de 40 par thème = 120 max
            params = {
                'q': theme,
                'startIndex': start_index,
                'maxResults': 40,
                'langRestrict': 'fr',
                'printType': 'books'
            }
            
            try:
                response = requests.get(base_url, params=params)
                if response.status_code == 429:
                    print("⚠️ Trop de requêtes. Pause de 30s...")
                    time.sleep(30)
                    continue
                
                response.raise_for_status()
                data = response.json()
                items = data.get("items", [])
                
                for item in items:
                    v = item.get("volumeInfo", {})
                    desc = v.get("description")
                    # CRITÈRE QUALITÉ : On ne garde que si la description est longue (> 100 car.)
                    if desc and len(desc) > 100:
                        all_books.append({
                            "titre": v.get("title"),
                            "auteurs": ", ".join(v.get("authors", ["Inconnu"])),
                            "description": desc,
                            "isbn": next((i['identifier'] for i in v.get("industryIdentifiers", []) if i['type'] == 'ISBN_13'), "N/A")
                        })
                
                print(f"Sous-total pour {theme}: {len(all_books)} livres valides.")
                time.sleep(1.5) # Sécurité pour l'API

            except Exception as e:
                print(f"Erreur sur {theme}: {e}")
                break
                
    return all_books

if __name__ == "__main__":
    # Liste de thèmes variés pour un catalogue riche
    categories = [
        "roman", "science-fiction", "philosophie", "histoire", 
        "psychologie", "informatique", "cuisine", "biographie",
        "thriller", "économie", "aventure", "poésie"
    ]
    
    data = fetch_massive_books(categories)
    
    # Suppression des doublons bruts (même titre) avant sauvegarde