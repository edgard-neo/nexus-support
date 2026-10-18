"""
Indexa os arquivos de FAQ no ChromaDB.
Uso: uv run python -m app.rag.ingest
"""

from pathlib import Path

import chromadb
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.core.logging import get_logger, setup_logging

# Raiz do projeto para resolver os caminhos relativos da aplicação.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
logger = get_logger(__name__)


def run_ingest(faq_dir: str | None = None) -> None:
    # Resolve o path relativo a raiz do projeto, nao ao diretorio atual
    raw_dir = faq_dir or settings.faq_data_dir
    faq_path = (PROJECT_ROOT / raw_dir).resolve()

    if not faq_path.exists():
        raise FileNotFoundError(f"Diretorio de FAQ nao encontrado: {faq_path}")

    logger.info("Indexando FAQ", extra={"path": str(faq_path)})

    # Carrega documentos
    loader = DirectoryLoader(
        path=str(faq_path),
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    docs = loader.load()

    if not docs:
        raise ValueError(f"Nenhum arquivo .md encontrado em: {faq_path}")

    logger.info("Documentos carregados", extra={"total": len(docs)})

    # Divide em chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=60,
        separators=["\n\n", "\n", ".", " "],
    )
    chunks = splitter.split_documents(docs)
    logger.info("Chunks gerados", extra={"total": len(chunks)})

    # Gera embeddings
    embed_model = SentenceTransformer(settings.embedding_model)
    texts = [c.page_content for c in chunks]
    embeddings = embed_model.encode(texts, show_progress_bar=True).tolist()

    # Persiste no ChromaDB
    persist_dir = (PROJECT_ROOT / settings.chroma_persist_dir).resolve()
    persist_dir.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(persist_dir))

    try:
        client.delete_collection(settings.chroma_collection_faq)
    except Exception:
        pass

    collection = client.create_collection(
        name=settings.chroma_collection_faq,
        metadata={"hnsw:space": "cosine"},
    )
    collection.add(
        ids=[f"chunk_{i}" for i in range(len(chunks))],
        documents=texts,
        embeddings=embeddings,
        metadatas=[
            {"chunk_index": i, **{k: str(v) for k, v in chunks[i].metadata.items()}}
            for i in range(len(chunks))
        ],
    )

    logger.info("Indexacao concluida", extra={"total_chunks": len(chunks)})


if __name__ == "__main__":
    setup_logging()
    run_ingest()
