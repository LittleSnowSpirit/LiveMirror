# Alembic Migrations

## Naming Convention

Migration files use the format: `YYYYMMDDHHMM_description.py`

- Timestamp in UTC
- Description in snake_case, matching the change intent
- Example: `202605070001_add_excellent_examples.py`

## Creating a New Migration

Use the helper script (from `backend/` directory):

```bash
./scripts/new_migration.sh "add column foo to bar"
```

This generates a properly named file with revision chain pre-filled.

## Applying Migrations

```bash
# Apply all pending
alembic upgrade head

# Rollback one step
alembic downgrade -1

# Show current revision
alembic current

# Show history
alembic history
```

## CI

Both `test.yml` and `core.yml` run a migration validation step that applies
`upgrade head` then `downgrade base` on a throwaway SQLite database, ensuring
every migration has a working downgrade path.
