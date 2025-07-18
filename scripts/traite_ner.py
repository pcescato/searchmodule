from sqlalchemy import update
from sqlalchemy.orm import Session
import spacy
import textacy.extract
import weaviate

# Import ORM
from models import ChunkPG, EntityPG, RelationPG

nlp = spacy.load("fr_core_news_md")  # ou autre modèle adapté

def insert_entity_pg(session: Session, text, label, chunk_id):
    ent = EntityPG(text=text, label=label, chunk_id=chunk_id)
    session.add(ent)
    session.flush()  # flush pour récupérer ent.id si besoin
    return ent

def insert_relation_pg(session: Session, subject, verb, obj, chunk_id):
    rel = RelationPG(subject=subject, verb=verb, object=obj, chunk_id=chunk_id)
    session.add(rel)
    session.flush()
    return rel

def insert_entity_wv(client, entity, chunk_id):
    obj = {
        "text": entity.text,
        "label": entity.label,
        "chunk": {
            "beacon": f"weaviate://localhost/Chunk/{chunk_id}"
        }
    }
    client.data_object.create(obj, "Entity", uuid=str(entity.id))

def insert_relation_wv(client, relation, chunk_id):
    obj = {
        "subject": relation.subject,
        "verb": relation.verb,
        "object": relation.object,
        "chunk": {
            "beacon": f"weaviate://localhost/Chunk/{chunk_id}"
        }
    }
    client.data_object.create(obj, "Relation", uuid=str(relation.id))

def extract_entities_relations(session: Session, client_wv):
    chunks = session.query(ChunkPG).filter(ChunkPG.traite_ner == False).all()
    for chunk in chunks:
        doc = nlp(chunk.text)

        # Extraction entités
        entities = [(ent.text, ent.label_) for ent in doc.ents]

        # Extraction triplets SVO
        triplets = list(textacy.extract.subject_verb_object_triples(doc))

        # Insertion en PostgreSQL
        for text, label in entities:
            ent_pg = insert_entity_pg(session, text, label, chunk.id)

        for subj, verb, obj in triplets:
            insert_relation_pg(session, subj.text, verb.lemma_, obj.text, chunk.id)

        session.commit()

        # Insertion Weaviate
        for ent_pg in session.query(EntityPG).filter(EntityPG.chunk_id == chunk.id).all():
            insert_entity_wv(client_wv, ent_pg, chunk.id)

        for rel_pg in session.query(RelationPG).filter(RelationPG.chunk_id == chunk.id).all():
            insert_relation_wv(client_wv, rel_pg, chunk.id)

        # Mise à jour flag traite_ner
        session.execute(update(ChunkPG).where(ChunkPG.id == chunk.id).values(traite_ner=True))
        session.commit()

        print(f"Chunk {chunk.id} traité: {len(entities)} entités, {len(triplets)} relations.")
