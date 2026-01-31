"""
Migration: Add parent_id to Unit for parent/variant system
"""

from extensions import db
from app import app


def upgrade():
    with db.engine.connect() as conn:
        # Check if parent_id column already exists
        result = conn.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name='unit' AND column_name='parent_id'
        """)
        if result.fetchone():
            print("[migrate_add_unit_parent] parent_id column already exists, skipping...")
            return
        try:
            conn.execute('ALTER TABLE unit ADD COLUMN parent_id INTEGER REFERENCES unit(id)')
            print("[migrate_add_unit_parent] parent_id column added successfully.")
        except Exception as e:
            print(f"[migrate_add_unit_parent] Error adding parent_id column: {e}")


def downgrade():
    with db.engine.connect() as conn:
        try:
            conn.execute('ALTER TABLE unit DROP COLUMN parent_id')
            print("[migrate_add_unit_parent] parent_id column dropped.")
        except Exception as e:
            print(f"[migrate_add_unit_parent] Error dropping parent_id column: {e}")

if __name__ == "__main__":
    with app.app_context():
        upgrade()
