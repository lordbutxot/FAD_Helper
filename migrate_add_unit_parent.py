"""
Migration: Add parent_id to Unit for parent/variant system
"""
from extensions import db

def upgrade():
    with db.engine.connect() as conn:
        conn.execute('ALTER TABLE unit ADD COLUMN parent_id INTEGER REFERENCES unit(id)')

def downgrade():
    with db.engine.connect() as conn:
        conn.execute('ALTER TABLE unit DROP COLUMN parent_id')
