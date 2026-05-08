#!/usr/bin/env bash
# Create a new Alembic migration with the standard naming convention.
#
# Usage:
#   ./scripts/new_migration.sh "add column foo to bar"
#
# Produces: migrations/versions/YYYYMMDDHHMM_add_column_foo_to_bar.py

set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <description>"
  echo "  description: human-readable migration summary (spaces allowed)"
  exit 1
fi

DESCRIPTION="$1"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
cd "$BACKEND_DIR"

# Generate timestamp and slug
TIMESTAMP="$(date -u +%Y%m%d%H%M)"
SLUG="$(echo "$DESCRIPTION" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/_/g' | sed 's/__*/_/g' | sed 's/^_//;s/_$//')"
REVISION="${TIMESTAMP}"
FILENAME="${TIMESTAMP}_${SLUG}.py"
FILEPATH="migrations/versions/${FILENAME}"

# Find current head
CURRENT_HEAD=$(python3 -c "
from alembic.config import Config
from alembic import command
import re, sys

cfg = Config('alembic.ini')
cfg.set_main_option('script_location', 'migrations')

from alembic.script import ScriptDirectory
script = ScriptDirectory.from_config(cfg)
head = script.get_current_head()
print(head or '')
" 2>/dev/null || echo "")

if [ -z "$CURRENT_HEAD" ]; then
  echo "Error: could not determine current Alembic head."
  exit 1
fi

# Generate next revision number by incrementing the last one
NEXT_REV=$(python3 -c "
head = '${CURRENT_HEAD}'
# Extract numeric part and increment
import re
m = re.match(r'(\d+)', head)
if m:
    num = int(m.group(1)) + 1
    # Pad to same length
    print(str(num).zfill(len(m.group(1))))
else:
    print(head + '_next')
")

cat > "$FILEPATH" <<MIGRATION
"""${DESCRIPTION}

Revision ID: ${NEXT_REV}
Revises: ${CURRENT_HEAD}
Create Date: $(date -u +%Y-%m-%d)
"""

from alembic import op
import sqlalchemy as sa


revision = "${NEXT_REV}"
down_revision = "${CURRENT_HEAD}"
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
MIGRATION

echo "Created migration: ${FILEPATH}"
echo "  Revision: ${NEXT_REV} (parent: ${CURRENT_HEAD})"
echo ""
echo "Edit the upgrade() and downgrade() functions, then run:"
echo "  cd backend && alembic upgrade head"
