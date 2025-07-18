FROM python:3.11-slim

WORKDIR /app

COPY ./app /app

RUN pip install --no-cache-dir fastapi uvicorn spacy psycopg[binary] weaviate-client httpx
RUN python -m spacy download fr_core_news_md

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
