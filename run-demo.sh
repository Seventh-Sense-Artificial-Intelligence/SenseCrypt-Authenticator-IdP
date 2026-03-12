#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
BACKEND_DIR="$SCRIPT_DIR/backend"
DEMO_DIR="$SCRIPT_DIR/demo"
STATIC_DIR="$BACKEND_DIR/static"
VENV_DIR="$BACKEND_DIR/.venv"
DEMO_VENV_DIR="$DEMO_DIR/.venv"

DB_NAME="portaluserdb"
DB_USER="portaluser"

echo "============================================"
echo "  Sensecrypt Authenticator — OIDC Demo"
echo "============================================"
echo ""

# ── 0. Kill any existing servers on ports 8000 and 9000 ──
for port in 8000 9000; do
  pids=$(lsof -ti :"$port" 2>/dev/null || true)
  if [ -n "$pids" ]; then
    echo "==> Killing existing processes on port $port..."
    echo "$pids" | xargs kill 2>/dev/null || true
    sleep 1
  fi
done

# ── 1. Ensure backend .env ──
if [ ! -f "$BACKEND_DIR/.env" ]; then
  echo "==> Creating backend/.env ..."
  cat > "$BACKEND_DIR/.env" <<EOF
DATABASE_URL=postgresql+asyncpg://${DB_USER}@localhost:5432/${DB_NAME}
SECRET_KEY=$(openssl rand -hex 32)
SENDGRID_API_KEY=
SENDGRID_FROM_EMAIL=noreply@sensecrypt.com
ACCESS_TOKEN_EXPIRE_MINUTES=30
BASE_URL=http://localhost:8000
OIDC_ISSUER_URL=http://localhost:8000
EOF
fi

# ── 2. Drop and recreate database ──
echo "==> Resetting database $DB_NAME..."
psql -U "$DB_USER" -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();" &>/dev/null || true
dropdb -U "$DB_USER" --if-exists "$DB_NAME"
createdb -O "$DB_USER" "$DB_NAME"

# ── 3. Frontend build ──
echo "==> Building frontend..."
cd "$FRONTEND_DIR"
npm install --silent
npx ng build --configuration=production 2>&1 | tail -3

echo "==> Copying build to backend/static..."
rm -rf "$STATIC_DIR"
mkdir -p "$STATIC_DIR"
BUILD_OUTPUT="$FRONTEND_DIR/dist/frontend/browser"
[ ! -d "$BUILD_OUTPUT" ] && BUILD_OUTPUT="$FRONTEND_DIR/dist/frontend"
cp -r "$BUILD_OUTPUT"/* "$STATIC_DIR"/

# ── 4. Backend venv + deps ──
cd "$BACKEND_DIR"
if [ ! -d "$VENV_DIR" ]; then
  echo "==> Creating backend venv..."
  python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
command -v uv &>/dev/null || pip install uv -q
echo "==> Installing backend dependencies..."
uv pip install -r requirements.txt -q

export PYTHONPATH="$BACKEND_DIR"

# ── 5. Run migrations ──
echo "==> Running migrations..."
alembic upgrade head

# ── 6. Seed demo data ──
echo "==> Seeding demo user + OAuth application..."
python seed_demo.py

# ── 7. Demo app venv + deps ──
cd "$DEMO_DIR"
if [ ! -d "$DEMO_VENV_DIR" ]; then
  echo "==> Creating demo venv..."
  python3 -m venv "$DEMO_VENV_DIR"
fi
source "$DEMO_VENV_DIR/bin/activate"
command -v uv &>/dev/null || pip install uv -q
echo "==> Installing demo dependencies..."
uv pip install -r requirements.txt -q

# ── 8. Start both servers ──
echo ""
echo "============================================"
echo "  Starting servers..."
echo "  IdP:  http://localhost:8000"
echo "  Demo: http://localhost:9000"
echo "============================================"
echo "  IdP admin:  demo-idp@seventhsense.ai / Demo1234!"
echo "  IdP login:  http://localhost:8000"
echo "============================================"
echo ""

# Start IdP in background
cd "$BACKEND_DIR"
source "$VENV_DIR/bin/activate"
export PYTHONPATH="$BACKEND_DIR"
uvicorn app.main:app --port 8000 &
IDP_PID=$!

# Start demo in foreground
cd "$DEMO_DIR"
source "$DEMO_VENV_DIR/bin/activate"
uvicorn main:app --port 9000 &
DEMO_PID=$!

# Trap to kill both on exit
trap "kill $IDP_PID $DEMO_PID 2>/dev/null; exit" INT TERM EXIT

echo ""
echo "Press Ctrl+C to stop both servers."
echo ""

wait
