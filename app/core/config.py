import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# No HF Spaces so /tmp e gravavel — detecta pelo env HF_SPACE_ID
_IN_HF_SPACES = bool(os.getenv("HF_SPACE_ID"))
_TMP = "/tmp" if _IN_HF_SPACES else "./data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Groq
    groq_api_key: str  # <- sem default
    groq_model: str = (
        "meta-llama/llama-4-scout-17b-16e-instruct"  # <- modelo atualizado
    )
    groq_temperature: float = 0.1
    groq_max_tokens: int = 1024

    # Embeddings (local)
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

    # ChromaDB
    chroma_persist_dir: str = "./data/chroma"
    chroma_collection_faq: str = "nexus_faq"
    rag_top_k: int = 4
    rag_threshold: float = 0.5

    # Memoria de sessao
    sqlite_db_path: str = "./data/checkpoints.db"

    # LangSmith — LANGCHAIN_API_KEY vazio desativa o tracing
    langchain_tracing_v2: bool = True
    langchain_endpoint: str = "https://api.smith.langchain.com"
    langchain_api_key: str = ""
    langchain_project: str = "nexus-support"

    # FastAPI
    api_title: str = "NexusSupport API"
    api_version: str = "1.0.0"
    api_debug: bool = False

    # Paths
    faq_data_dir: str = "./data/faq"
    prompts_dir: str = "./app/core/prompts"

    @property
    def system_prompt_path(self) -> Path:
        return Path(self.prompts_dir) / "system.md"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore


settings = get_settings()
