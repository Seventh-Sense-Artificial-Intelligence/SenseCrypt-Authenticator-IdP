#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d ".venv" ]; then
  echo "==> Creating virtual environment..."
  python3 -m venv .venv
fi

source .venv/bin/activate

if ! command -v uv &> /dev/null; then
  pip install uv
fi

echo "==> Installing dependencies..."
uv pip install -r requirements.txt

echo "==> Starting OIDC Demo Client on port 9000..."
uvicorn main:app --host 0.0.0.0 --port 9000 --reload
