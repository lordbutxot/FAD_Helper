#!/bin/sh
set -e

echo "Running all migrations..."
python migrate_all.py

echo "Ensuring parent_id column exists in unit table..."
if [ -n "$DATABASE_URL" ]; then
	# Convert postgres:// to postgresql:// for psql compatibility
	DB_URL="$DATABASE_URL"
	if echo "$DB_URL" | grep -q '^postgres://'; then
		DB_URL="postgresql://${DB_URL#postgres://}"
	fi
	# Remove query params for psql connection string
	DB_URL_NO_PARAMS="${DB_URL%%\?*}"
	# Use a simple conditional check and ALTER TABLE with correct quoting
	psql "$DB_URL_NO_PARAMS" -tAc "SELECT 1 FROM information_schema.columns WHERE table_name='unit' AND column_name='parent_id'" | grep -q 1 || \
		psql "$DB_URL_NO_PARAMS" -c "ALTER TABLE unit ADD COLUMN parent_id INTEGER REFERENCES unit(id);" || echo "psql fallback for parent_id failed, continuing..."
else
	echo "DATABASE_URL not set, skipping direct SQL migration."
fi

echo "Initializing database with game data..."
python init_production_db.py

echo "Starting gunicorn..."
exec gunicorn app:app
