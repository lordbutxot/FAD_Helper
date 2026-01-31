"""
Migration: Add parent_id to Unit for parent/variant system
"""


from extensions import db
from app import app
from sqlalchemy import text
import os
import sys


def upgrade():
    with db.engine.connect() as conn:
        db_url = os.environ.get('DATABASE_URL', 'not set')
        print(f"[migrate_add_unit_parent] DB URL: {db_url}")
        try:
            user_result = conn.execute(text("SELECT current_user"))
            db_user = user_result.fetchone()[0]
            print(f"[migrate_add_unit_parent] DB User: {db_user}")
        except Exception as e:
            print(f"[migrate_add_unit_parent] Could not get DB user: {e}")

        # Check if parent_id column already exists
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name='unit' AND column_name='parent_id'
        """))
        if result.fetchone():
            print("[migrate_add_unit_parent] parent_id column already exists, skipping...")
            return
        try:
            conn.execute(text('ALTER TABLE unit ADD COLUMN parent_id INTEGER REFERENCES unit(id)'))
            print("[migrate_add_unit_parent] parent_id column added successfully.")
        except Exception as e:
            print(f"[migrate_add_unit_parent] Error adding parent_id column: {e}")
            sys.exit(1)

        # Double-check column exists after migration
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name='unit' AND column_name='parent_id'
        """))
        if not result.fetchone():
            print("[migrate_add_unit_parent] ERROR: parent_id column still does not exist after migration! Aborting.")
            sys.exit(2)
        else:
            print("[migrate_add_unit_parent] parent_id column confirmed present after migration.")


def downgrade():
    with db.engine.connect() as conn:
        try:
            conn.execute(text('ALTER TABLE unit DROP COLUMN parent_id'))
            print("[migrate_add_unit_parent] parent_id column dropped.")
        except Exception as e:
            print(f"[migrate_add_unit_parent] Error dropping parent_id column: {e}")

if __name__ == "__main__":
    with app.app_context():
        upgrade()
