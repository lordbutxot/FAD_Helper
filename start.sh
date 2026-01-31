#!/bin/sh
set -e

echo "Initializing database with game data..."
python init_production_db.py

echo "Starting gunicorn..."
exec gunicorn app:app
