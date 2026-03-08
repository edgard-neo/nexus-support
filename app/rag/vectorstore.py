from functools import lru_cache
from pathlib import Path
from typing import NamedTuple

import chromadb
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class RetrievedChunk(NamedTuple):
    content: str
    source: str
    distance: float


@lru_cache(maxsize=1)
def get_embed_model() -> SentenceTransformer:
    return SentenceTransformer(settings.embedding_model)


@lru_cache(maxsize=1)
def get_chroma_client():
    persist_dir = (PROJECT_ROOT / settings.chroma_persist_dir).resolve()
    return chromadb.PersistentClient(path=str(persist_dir))


def get_collection() -> chromadb.Collection:
    try:
        return get_chroma_client().get_collection(settings.chroma_collection_faq)
    except Exception as exc:
        raise RuntimeError(
            f"Colecao '{settings.chroma_collection_faq}' nao encontrada. "
            "Execute: uv run python -m app.rag.ingest"
        ) from exc


def retrieve_faq(
    query: str, top_k: int | None = None, threshold: float | None = None
) -> list[RetrievedChunk]:
    top_k = top_k or settings.rag_top_k
    threshold = threshold if threshold is not None else settings.rag_threshold

    query_embedding: list[float] = get_embed_model().encode(query).tolist()

    collection = get_collection()
    n_fetch = min(top_k * 2, collection.count())
    if n_fetch == 0:
        return []

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_fetch,
        include=["documents", "metadatas", "distances"],
    )

    documents: list[str] = results.get("documents", [[]])[0]  # type: ignore
    metadatas: list[dict] = results.get("metadatas", [[]])[0]  # type: ignore
    distances: list[float] = results.get("distances", [[]])[0]  # type: ignore

    chunks: list[RetrievedChunk] = []
    seen_sources: list[str] = []

    for doc, meta, dist in zip(documents, metadatas, distances):
        if dist > threshold:
            continue
        source = meta.get("source", "desconhecido")
        if seen_sources.count(source) >= 2:
            continue
        chunks.append(RetrievedChunk(content=doc, source=source, distance=dist))
        seen_sources.append(source)
        if len(chunks) >= top_k:
            break

    return chunks


def format_context(chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return ""
    parts = []
    for chunk in chunks:
        source_name = chunk.source.split("/")[-1]
        parts.append(f"[Fonte: {source_name}]\n{chunk.content}")
    return "\n\n".join(parts)
