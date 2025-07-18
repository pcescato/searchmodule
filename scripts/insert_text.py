import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Text, ForeignKey, insert
from dotenv import load_dotenv

load_dotenv()

PG_USER = os.getenv("POSTGRES_USER", "raguser")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "ragpass")
PG_DB = os.getenv("POSTGRES_DB", "ragdb")
PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"

engine = create_engine(DATABASE_URL)
metadata = MetaData()

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
)

def parse_filename(filename):
    base = os.path.basename(filename)
    name, _ = os.path.splitext(base)
    parts = name.split("_", 1)
    if len(parts) == 2:
        auteur = parts[0].replace("-", " ").title()
        titre = parts[1].replace("-", " ").title()
    else:
        auteur = "Inconnu"
        titre = name.replace("-", " ").title()
    return auteur, titre

def split_into_chunks(text):
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return paragraphs

def insert_document_and_chunks(filepath):
    auteur, titre = parse_filename(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        texte = f.read()

    with engine.connect() as conn:
        stmt_doc = insert(documents).values(titre=titre, auteur=auteur, texte=texte)
        result = conn.execute(stmt_doc)
        doc_id = result.inserted_primary_key[0]

        chunks_list = split_into_chunks(texte)

        for idx, chunk_text in enumerate(chunks_list, start=1):
            stmt_chunk = insert(chunks).values(document_id=doc_id, numero=idx, texte=chunk_text)
            conn.execute(stmt_chunk)

        conn.commit()
        print(f"Document {doc_id} ('{titre}') inséré avec {len(chunks_list)} chunks.")

def insert_all_from_dir(directory):
    files = [f for f in os.listdir(directory) if f.endswith(".txt")]
    if not files:
        print(f"Aucun fichier .txt trouvé dans {directory}")
        return
    for filename in files:
        filepath = os.path.join(directory, filename)
        insert_document_and_chunks(filepath)

if __name__ == "__main__":
    data_dir = "datas"
    if not os.path.exists(data_dir):
        print(f"Le dossier {data_dir} n'existe pas.")
    else:
        insert_all_from_dir(data_dir)
