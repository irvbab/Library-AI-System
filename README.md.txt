# 📚 Système de Recommandation Intelligente - Librairie

## 📖 Présentation du Projet
Ce projet consiste en une solution logicielle complète pour une librairie, intégrant un moteur de recommandation basé sur le Traitement du Langage Naturel (NLP). Il permet d'automatiser la suggestion d'ouvrages en fonction de la similarité sémantique des descriptions.

---

## 🏗️ Architecture du Système
Le projet est structuré selon une approche modulaire pour séparer les responsabilités (Socle de la compétence **C5**) :

* **`app.py`** : Interface utilisateur (Frontend) développée avec Streamlit.
* **`api.py`** : Serveur d'exposition des données (Backend) via FastAPI.
* **`library.db`** : Base de données relationnelle SQLite3.
* **`test_api.py`** : Suite de tests automatisés (Qualité logicielle).
* **`requirements.txt`** : Gestionnaire des dépendances.

---

## 🧪 Détails des Compétences Validées

### 1. Analyse et Traitement de Données (Bloc E3)
* **Vectorisation TF-IDF :** Transformation du texte en vecteurs numériques pour capturer l'importance des mots-clés.
* **Similarité Cosinus :** Algorithme de calcul de distance entre vecteurs pour identifier les livres les plus proches.

### 2. Développement Backend & API (Bloc E3/E4)
* Exposition de points de terminaison (endpoints) RESTful.
* Documentation automatique via **Swagger UI** (disponible sur `/docs`).

### 3. Qualité et Maintenance (Bloc E4)
* **Tests Unitaires :** Validation des endpoints et de la connectivité DB avec Pytest.
* **Versionnage :** Utilisation rigoureuse de Git avec un fichier `.gitignore` optimisé.

---

## ⚙️ Installation et Déploiement

### Prérequis
* Python 3.10+
* Pip (gestionnaire de paquets)

### Installation
1. `git clone https://github.com/irvbab/Library-AI-System.git`
2. `pip install -r requirements.txt`

### Exécution
* **Lancer l'API :** `uvicorn api:app --reload`
* **Lancer l'IHM :** `streamlit run app.py`

---

## 📊 Schéma de Fonctionnement


1. L'utilisateur saisit un livre dans **Streamlit**.
2. Streamlit interroge l'**API FastAPI**.
3. L'API exécute le script de **recommandation (TF-IDF)** sur la base **SQLite**.
4. Les résultats sont renvoyés et affichés en temps réel.