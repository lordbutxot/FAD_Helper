#!/bin/sh
set -e

echo "Initializing database..."
python init_db_simple.py

echo "Starting gunicorn..."
exec gunicorn app:app
