#!/usr/bin/env bash
set -euo pipefail

DB_NAME="portaluserdb"
DB_USER="portaluser"

echo "==> Dropping database $DB_NAME..."
dropdb --if-exists "$DB_NAME"

echo "==> Creating database $DB_NAME..."
createdb -O "$DB_USER" "$DB_NAME"

echo "==> Running migrations..."
cd "$(dirname "${BASH_SOURCE[0]}")/backend"
source .venv/bin/activate
PYTHONPATH=. alembic upgrade head

echo "==> Done. Database reset."
