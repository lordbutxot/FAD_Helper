#!/bin/sh
set -e

echo "Migrating trait table constraint..."
python migrate_trait_constraint.py
        
	echo "Running parent/variant migration..."
	python migrate_add_unit_parent.py

echo "Initializing database with game data..."
python init_production_db.py

echo "Running database migration..."
python migrate_squad_members.py

echo "Adding description column to units..."
python migrate_add_description.py

echo "Starting gunicorn..."
exec gunicorn app:app
