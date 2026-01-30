"""
Migration script to add logo_filename column to faction table
"""
import sqlite3
import os

db_path = 'instance/fad_lists.db'

if not os.path.exists(db_path):
    print(f"Error: Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Adding logo_filename column to faction table...")

try:
    # Check if column already exists
    cursor.execute('PRAGMA table_info(faction)')
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'logo_filename' in columns:
        print("✓ Column already exists")
    else:
        # Add the column
        cursor.execute('ALTER TABLE faction ADD COLUMN logo_filename VARCHAR(255)')
        conn.commit()
        print("✓ Added logo_filename column")
    
    # Create the upload directory if it doesn't exist
    upload_dir = 'static/faction_logos'
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        print(f"✓ Created upload directory: {upload_dir}")
    else:
        print(f"✓ Upload directory exists: {upload_dir}")
    
    print("\nMigration completed successfully!")
    
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    conn.close()
