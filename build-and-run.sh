#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
BACKEND_DIR="$SCRIPT_DIR/backend"
STATIC_DIR="$BACKEND_DIR/static"
VENV_DIR="$BACKEND_DIR/.venv"

# --- Frontend build ---
echo "==> Building frontend..."
cd "$FRONTEND_DIR"
npm install
npx ng build --configuration=production

echo "==> Copying build output to backend static directory..."
rm -rf "$STATIC_DIR"
mkdir -p "$STATIC_DIR"

BUILD_OUTPUT="$FRONTEND_DIR/dist/frontend/browser"
if [ ! -d "$BUILD_OUTPUT" ]; then
  BUILD_OUTPUT="$FRONTEND_DIR/dist/frontend"
fi
cp -r "$BUILD_OUTPUT"/* "$STATIC_DIR"/

# --- Python venv + dependencies ---
cd "$BACKEND_DIR"

if [ ! -d "$VENV_DIR" ]; then
  echo "==> Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

if ! command -v uv &> /dev/null; then
  echo "==> Installing uv..."
  pip install uv
fi

echo "==> Installing Python dependencies..."
uv pip install -r requirements.txt

export PYTHONPATH="$BACKEND_DIR"

# --- Run migrations ---
echo "==> Running database migrations..."
alembic upgrade head

# --- Run server ---
echo "==> Starting server..."
uvicorn app.main:app --reload
