# 📚 PoC RAG Littéraire : Victor Hugo & Honoré de Balzac

Ce projet est une démonstration de Recherche Augmentée par Génération (RAG) appliquée à un corpus littéraire, reposant sur les œuvres de Victor Hugo et Honoré de Balzac. Il combine traitement du langage naturel (spaCy), recherche vectorielle (Weaviate et pgvector), et API d’interrogation (FastAPI).

---

## 🎯 Objectifs

- Créer un moteur de recherche intelligent sur un corpus de romans en français.
- Indexer le texte par paragraphes avec embeddings (BAAI/bge-m3-multi et thenlper/gte-large via DeepInfra).
- Extraire les entités nommées (personnages, lieux, dates, etc.) via spaCy.
- Utiliser Weaviate pour la recherche vectorielle et les relations entre entités.
- Utiliser PostgreSQL + pgvector pour le stockage et la recherche manuelle.

---

## 🧱 Stack technique

- **FastAPI** : Backend léger pour les API d’accès au corpus, aux entités et aux résultats de recherche.
- **PostgreSQL + pgvector** : Stockage structuré des textes, entités, embeddings.
- **Weaviate** : Recherche vectorielle avec graphe de relations (triplets).
- **spaCy** : Traitement de texte, NER, enrichissement sémantique (modèle `fr_core_news_lg`).
- **Traefik** : Reverse proxy + HTTPS (Let's Encrypt).
- **Portainer** : Gestion visuelle des containers.
- **Docker** : Conteneurisation de l’ensemble.

---

## 🔍 Recherche & Graphe

- Chaque paragraphe est encodé en vecteurs via BAAI/bge-m3-multi (DeepInfra).
- Weaviate stocke et relie les passages entre eux, et aux entités détectées.
- Le graphe permet de naviguer dans les interactions entre personnages, lieux, événements.

---

## 🔧 Accès via Traefik

Les modules frontend sont accessibles via des sous-domaines :
- `portainer.docker.domain.com`
- `weaviate.docker.domain.com` (console graphique)
- `api.docker.domain.com` (FastAPI)
- etc.

---

## 🚧 TODO

- [ ] Préparer le corpus (téléchargement, nettoyage, segmentation)
- [ ] Générer les embeddings via API DeepInfra
- [ ] Extraire les entités avec spaCy (`fr_core_news_lg`)
- [ ] Indexer dans PostgreSQL et Weaviate
- [ ] Construire l’API de recherche
- [ ] Exposer les services via Traefik + Let's Encrypt

---

## 📘 Sources

- [Projet Gutenberg](https://www.gutenberg.org)
- [DeepInfra](https://deepinfra.com) (hébergement des modèles)
- [pgvector](https://github.com/pgvector/pgvector)
- [Weaviate](https://weaviate.io)
- [spaCy](https://spacy.io)

---

## ⚠️ Remarques

Ce projet est un **PoC non destiné à la production**. Il vise à évaluer la pertinence d’un pipeline IA appliqué à la littérature classique, à des fins exploratoires.

---

## 📄 Licence

Projet sous licence MIT. Corpus utilisé dans le respect des droits d’auteur (œuvres tombées dans le domaine public).

