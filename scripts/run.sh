#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

"$PROJECT_ROOT/scripts/setup.sh"
exec uv run uvicorn app.main:app --reload "$@"
