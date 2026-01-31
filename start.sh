#!/bin/sh
set -e

echo "Initializing database with game data..."
python init_production_db.py

echo "Running database migration..."
python migrate_squad_members.py

echo "Starting gunicorn..."
exec gunicorn app:app
