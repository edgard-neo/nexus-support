#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

RECREATE_ENV=false

# Evita que um ambiente virtual de outro clone seja reutilizado.
if [[ -n "${VIRTUAL_ENV:-}" && "${VIRTUAL_ENV}" != "$PROJECT_ROOT/.venv" ]]; then
  unset VIRTUAL_ENV
  RECREATE_ENV=true
fi

# Detecta executáveis com shebang apontando para um clone antigo.
for entrypoint in "$PROJECT_ROOT/.venv/bin/python" "$PROJECT_ROOT/.venv/bin/pytest" "$PROJECT_ROOT/.venv/bin/uvicorn"; do
  if [[ -f "$entrypoint" ]] && head -n 1 "$entrypoint" | grep -q "/home/" && ! head -n 1 "$entrypoint" | grep -Fq "$PROJECT_ROOT/.venv/"; then
    RECREATE_ENV=true
  fi
done

if [[ "$RECREATE_ENV" == true ]]; then
  rm -rf "$PROJECT_ROOT/.venv"
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "uv não encontrado. Instale em: https://docs.astral.sh/uv/getting-started/installation/" >&2
  exit 1
fi

uv sync --dev
echo "Ambiente pronto em $PROJECT_ROOT/.venv"
