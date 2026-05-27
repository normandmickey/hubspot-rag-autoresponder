from pathlib import Path
import json
import psycopg
from .models import KnowledgeHit
from . import config
from openai import OpenAI
import httpx


def load_kb_documents(kb_path: Path):
    docs = []
    for path in sorted(kb_path.rglob('*')):
        if path.is_file() and path.suffix.lower() in {'.md', '.txt'}:
            docs.append({'path': str(path), 'text': path.read_text(errors='ignore')})
    return docs


def simple_search(query: str, docs, limit: int = 5):
    query_terms = [term.lower() for term in query.split() if term.strip()]
    scored = []
    for doc in docs:
        text = doc['text'].lower()
        score = sum(text.count(term) for term in query_terms)
        if score > 0:
            scored.append(KnowledgeHit(path=doc['path'], text=doc['text'], score=score))
    scored.sort(key=lambda item: item.score, reverse=True)
    return scored[:limit]


def embed_query(query: str):
    if not config.KB_QUERY_EMBED_MODEL:
        raise RuntimeError('KB_QUERY_EMBED_MODEL must be set for pgvector retrieval')
    verify = config.LLM_CA_BUNDLE or config.LLM_VERIFY_SSL
    http_client = httpx.Client(verify=verify, timeout=120.0)
    client_kwargs = {
        'api_key': config.EMBED_API_KEY or config.OPENAI_API_KEY,
        'http_client': http_client,
    }
    if config.EMBED_BASE_URL:
        client_kwargs['base_url'] = config.EMBED_BASE_URL
    client = OpenAI(**client_kwargs)
    resp = client.embeddings.create(model=config.KB_QUERY_EMBED_MODEL, input=query)
    return resp.data[0].embedding


def pgvector_search(query: str, limit: int | None = None):
    if not config.KB_DATABASE_URL:
        raise RuntimeError('KB_DATABASE_URL must be set for pgvector retrieval')
    vector = embed_query(query)
    top_k = limit or config.KB_TOP_K
    vector_sql = '[' + ','.join(str(x) for x in vector) + ']'
    collection_join = ''
    collection_where = ''
    params = [vector_sql, vector_sql]
    if config.KB_COLLECTION_NAME:
        collection_join = (
            f" JOIN {config.KB_COLLECTION_TABLE} c"
            f" ON e.{config.KB_EMBEDDING_COLLECTION_ID_COLUMN} = c.{config.KB_COLLECTION_ID_COLUMN}"
        )
        collection_where = f" WHERE c.{config.KB_COLLECTION_NAME_COLUMN} = %s"
        params.append(config.KB_COLLECTION_NAME)
    sql = f"""
        SELECT
            e.{config.KB_DOCUMENT_ID_COLUMN}::text AS document_id,
            COALESCE(e.{config.KB_SOURCE_COLUMN}::text, '') AS source,
            e.{config.KB_TEXT_COLUMN}::text AS chunk_text,
            1 - (e.{config.KB_EMBEDDING_COLUMN} <=> %s::vector) AS score,
            COALESCE(e.{config.KB_METADATA_COLUMN}::text, '{{}}') AS metadata_text
        FROM {config.KB_TABLE} e
        {collection_join}
        {collection_where}
        ORDER BY e.{config.KB_EMBEDDING_COLUMN} <=> %s::vector
        LIMIT %s
    """
    params.append(top_k)
    hits = []
    with psycopg.connect(config.KB_DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            for document_id, source, chunk_text, score, metadata_text in cur.fetchall():
                path = source or document_id or 'pgvector'
                try:
                    metadata = json.loads(metadata_text) if metadata_text else {}
                except Exception:
                    metadata = {}
                if metadata:
                    path = metadata.get('path') or metadata.get('title') or path
                hits.append(KnowledgeHit(path=path, text=chunk_text, score=int(score * 1000)))
    return hits


def search_kb(query: str, kb_path: Path, limit: int | None = None):
    if config.KB_BACKEND == 'pgvector':
        return pgvector_search(query, limit=limit)
    docs = load_kb_documents(kb_path)
    return simple_search(query, docs, limit=limit or config.KB_TOP_K)
