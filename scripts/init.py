import os
from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, Text, ForeignKey
)
from sqlalchemy.dialects.postgresql import VECTOR
from sqlalchemy.exc import ProgrammingError
import weaviate
from dotenv import load_dotenv

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

# Tables PostgreSQL
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
    Column("numero", Integer),  # ordre dans le document
    Column("texte", Text),
    Column("traite", Boolean, default=False, nullable=False),
    Column("traite_ner", Boolean, default=False, nullable=False),
)

embeddings = Table(
    "embeddings", metadata,
    Column("id", Integer, primary_key=True),
    Column("chunk_id", Integer, ForeignKey("chunks.id", ondelete="CASCADE")),
    Column("embedding", VECTOR(384))
)

# Connexion Weaviate
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
client = weaviate.Client(url=WEAVIATE_URL)

def create_pgvector_extension():
    with engine.connect() as conn:
        try:
            conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            print("Extension pgvector activée ou déjà présente.")
        except ProgrammingError as e:
            print("Erreur lors de l'activation de pgvector:", e)

def create_tables():
    create_pgvector_extension()
    metadata.create_all(engine)
    print("Tables PostgreSQL créées ou existantes.")

def init_weaviate_schema(client):
    schema = client.schema

    # 1. Document
    schema.create_class({
        "class": "Document",
        "description": "Texte brut complet",
        "properties": [
            {"name": "title", "dataType": ["text"]},
            {"name": "author", "dataType": ["text"]},
            {"name": "path", "dataType": ["text"]},
        ]
    })

    # 2. Chunk
    schema.create_class({
        "class": "Chunk",
        "description": "Extrait vectorisé d’un document",
        "vectorIndexConfig": {"distance": "cosine"},
        "properties": [
            {"name": "text", "dataType": ["text"]},
            {"name": "processed", "dataType": ["boolean"]},
            {"name": "document", "dataType": ["Document"]}  # FK vers Document
        ]
    })

    # 3. Entity
    schema.create_class({
        "class": "vEntity",
        "description": "Entité nommée extraite du texte",
        "vectorIndexConfig": {"distance": "cosine"},
        "properties": [
            {"name": "text", "dataType": ["text"]},
            {"name": "label", "dataType": ["text"]},  # PER, LOC, ORG, etc.
            {"name": "chunk", "dataType": ["Chunk"]}
        ]
    })

    schema.create_class({
        "class": "Entity",
        "description": "Entité nommée extraite du texte",
        "properties": [
            {"name": "text", "dataType": ["text"]},
            {"name": "label", "dataType": ["text"]},  # PER, LOC, ORG, etc.
            {"name": "chunk", "dataType": ["Chunk"]}
        ]
    })

    # 4. Relation
    schema.create_class({
        "class": "Relation",
        "description": "Relation extraite d’un chunk (SVO ou autre)",
        "properties": [
            {"name": "subject", "dataType": ["text"]},
            {"name": "verb", "dataType": ["text"]},
            {"name": "object", "dataType": ["text"]},
            {"name": "chunk", "dataType": ["Chunk"]}
        ]
    })

    print("✅ Schéma Weaviate mis à jour.")

if __name__ == "__main__":
    create_tables()
    create_weaviate_class()
