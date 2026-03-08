FROM python:3.12-slim

# Usuario obrigatorio para HF Spaces (UID 1000)
RUN useradd -m -u 1000 user

WORKDIR /home/user/app

# Redireciona todos os caches para /tmp — unico diretorio gravavel no HF Spaces
ENV HF_HOME=/tmp/hf_cache \
    HF_HUB_CACHE=/tmp/hf_cache/hub \
    SENTENCE_TRANSFORMERS_HOME=/tmp/hf_cache/sentence_transformers \
    TRANSFORMERS_CACHE=/tmp/hf_cache/transformers \
    HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Instala dependencias antes de copiar o codigo (aproveita cache do Docker)
COPY --chown=user pyproject.toml .
RUN pip install --no-cache-dir uv && \
    uv pip install --system --no-cache-dir -e .

# Copia o projeto
COPY --chown=user . .

# Indexa o FAQ no build — assim nao precisa baixar e indexar em cada startup
RUN mkdir -p /tmp/chroma /tmp/hf_cache && \
    python -m app.rag.ingest

EXPOSE 7860

USER user

# Startup: porta 7860 obrigatoria no HF Spaces
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
