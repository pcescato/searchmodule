import os
import requests
from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, Text, ForeignKey,
    insert, select, update, Boolean
)
from sqlalchemy.dialects.postgresql import VECTOR
from dotenv import load_dotenv
import weaviate
import time

load_dotenv()

# Config PostgreSQL
PG_USER = os.getenv("POSTGRES_USER", "raguser")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "ragpass")
PG_DB = os.getenv("POSTGRES_DB", "ragdb")
PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Tables
documents = Table(
    "documents", metadata,
    Column("id", Integer, primary_key=True),
    Column("titre", Text),
    Column("auteur", Text),
    Column("texte", Text),
)

chunks = Table(
    "chunks", metadata,
    Column("id", Integer, primary_key=True),
    Column("document_id", Integer, ForeignKey("documents.id", ondelete="CASCADE")),
    Column("numero", Integer),
    Column("texte", Text),
    Column("traite", Boolean, nullable=False, default=False),
)

embeddings = Table(
    "embeddings", metadata,
    Column("id", Integer, primary_key=True),
    Column("chunk_id", Integer, ForeignKey("chunks.id", ondelete="CASCADE")),
    Column("embedding", VECTOR(384))
)

# Weaviate config
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
client = weaviate.Client(url=WEAVIATE_URL)

# DeepInfra API config
DEEPINFRA_API_KEY = os.getenv("DEEPINFRA_API_KEY")
EMBEDDING_MODEL = "BAAI/bge-m3-multi"
DEEPINFRA_URL = "https://api.deepinfra.com/v1/embedding"

headers = {
    "Authorization": f"Bearer {DEEPINFRA_API_KEY}",
    "Content-Type": "application/json"
}

def get_embedding(text):
    payload = {
        "model": EMBEDDING_MODEL,
        "input": text
    }
    response = requests.post(DEEPINFRA_URL, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data["data"][0]

def process_embeddings():
    with engine.connect() as conn:
        chunks_to_embed = conn.execute(
            select(chunks).where((chunks.c.traite == False) | (chunks.c.traite.is_(None)))
        ).fetchall()

        if not chunks_to_embed:
            print("Aucun chunk non traité à traiter.")
            return

        for chunk in chunks_to_embed:
            chunk_id = chunk.id
            texte = chunk.texte

            print(f"Traitement embedding chunk_id={chunk_id}")

            embedding_vector = get_embedding(texte)

            # Insérer dans PG embeddings
            stmt_insert = insert(embeddings).values(chunk_id=chunk_id, embedding=embedding_vector)
            conn.execute(stmt_insert)

            # Insérer dans Weaviate
            client.data_object.create(
                data_object={
                    "chunkId": chunk_id,
                    "texte": texte,
                },
                vector=embedding_vector,
                class_name="Embedding"
            )

            # Mettre à jour le statut 'traite' à True
            stmt_update = (
                update(chunks)
                .where(chunks.c.id == chunk_id)
                .values(traite=True)
            )
            conn.execute(stmt_update)

            # Petite pause
            time.sleep(0.1)

        conn.commit()
        print(f"Traitement terminé pour {len(chunks_to_embed)} chunks.")

if __name__ == "__main__":
    process_embeddings()
