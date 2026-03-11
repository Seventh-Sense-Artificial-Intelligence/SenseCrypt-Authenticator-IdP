#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
BACKEND_DIR="$SCRIPT_DIR/backend"
STATIC_DIR="$BACKEND_DIR/static"

echo "==> Building frontend..."
cd "$FRONTEND_DIR"
npm install
npx ng build --configuration=production

echo "==> Copying build output to backend static directory..."
rm -rf "$STATIC_DIR"
mkdir -p "$STATIC_DIR"

# Angular 21 outputs to dist/<project-name>/browser/
BUILD_OUTPUT="$FRONTEND_DIR/dist/frontend/browser"
if [ ! -d "$BUILD_OUTPUT" ]; then
  # Fallback for older Angular output structure
  BUILD_OUTPUT="$FRONTEND_DIR/dist/frontend"
fi

cp -r "$BUILD_OUTPUT"/* "$STATIC_DIR"/

echo "==> Build complete. Static files placed in backend/static/"
echo ""
echo "To run the backend:"
echo "  cd backend"
echo "  pip install -r requirements.txt"
echo "  uvicorn app.main:app --reload"
