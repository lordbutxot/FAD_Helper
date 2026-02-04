"""
Migration script to add playstyle_tags column to faction table
"""
import sqlite3
import os

db_path = 'instance/fad_lists.db'

if not os.path.exists(db_path):
    print(f"Error: Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Adding playstyle_tags column to faction table...")

try:
    # Check if column already exists
    cursor.execute('PRAGMA table_info(faction)')
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'playstyle_tags' in columns:
        print("✓ Column already exists")
    else:
        # Add the column
        cursor.execute('ALTER TABLE faction ADD COLUMN playstyle_tags TEXT')
        conn.commit()
        print("✓ Added playstyle_tags column")
    
    print("\nMigration completed successfully!")
    
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    conn.close()
