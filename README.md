# Benchmark vectoriel : PostgreSQL + pgvector vs Weaviate

📍 Objectif : comparaison vectorielle Weaviate vs pgvector

📌 Pas de front. Pas de LLM génératif. Pas de RAG. Pas de storytelling.
📌 Juste du texte, du vecteur, des requêtes, du benchmark.

---

Ce projet est un Proof of Concept (PoC) destiné à évaluer les performances et les usages comparés de deux systèmes de vectorisation et de recherche sémantique :

- **PostgreSQL + pgvector**
- **Weaviate** (avec ou sans graphe, selon les tests)

Le corpus utilisé est issu de textes littéraires français (Victor Hugo & Honoré de Balzac, via le Projet Gutenberg), ce qui permet une base riche, structurée et textuellement dense.

---

## 🔧 Stack technique

- **PostgreSQL** avec l'extension `pgvector`
- **Weaviate**
- **FastAPI** pour exposer une API minimale
- **spaCy (fr_core_news_lg)** pour l’extraction d’entités nommées (NER)
- **Traefik** pour le reverse proxy + Let's Encrypt
- **Portainer** pour la gestion de containers
- Accès via sous-domaines dédiés : `portainer.docker.tsw.ovh`, `traefik.docker.tsw.ovh`, etc.

---

## 📐 Objectifs

- Évaluer la **vitesse d’indexation** (corpus entier)
- Comparer la **pertinence des résultats** pour une requête donnée
- Analyser les **capacités de structuration** et d’interrogation sémantique (triplets, graphe…)
- Identifier les **limites ou avantages** concrets de chaque solution dans une architecture orientée exploration de texte.

---

## 🗃️ Structure des données

Les textes sont stockés en base et découpés si besoin.  
Les entités suivantes sont extraites via spaCy :
- Personnes (avec genre, âge si détectable)
- Lieux, dates
- Types d’interactions
- Caractères, rôles, ou attributs saillants

Ces données sont :
- indexées dans PostgreSQL + vecteurs via `pgvector`
- ou bien envoyées dans Weaviate pour structuration possible en vecteurs / graphes

---

## 🚀 Lancement

```bash
cp .env.example .env  # personnalise les valeurs
docker-compose up -d  # lance toute la stack
