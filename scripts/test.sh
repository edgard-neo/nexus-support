#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

"$PROJECT_ROOT/scripts/setup.sh"
uv run ruff check .
uv run pytest -q "$@"
