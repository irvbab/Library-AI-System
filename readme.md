# Système de Recommandation pour une Librairie 📚

Ce projet a pour but de recommander des livres aux utilisateurs en fonction de leurs goûts en utilisant des techniques d'Intelligence Artificielle (NLP).

## 🚀 Étape 1 : Préparation des données (Bloc 1)
L'objectif était de créer un catalogue de livres structuré à partir de sources externes.

### Architecture du Pipeline :
1. **Collecte** (`collect_data.py`) : Extraction de 145 livres via l'API Google Books.
2. **Nettoyage** (`prepare_data.py`) : Traitement des données avec Pandas (suppression des doublons, nettoyage HTML).
3. **Stockage** (`database_setup.py`) : Insertion des données nettoyées dans une base de données SQLite (`library.db`).

## 🛠️ Installation
```bash
pip install pandas
python collect_data.py
python prepare_data.py
python database_setup.py