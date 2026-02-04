"""Migration script to add Faction system to database"""
import sqlite3
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'fad_lists.db')

def migrate_database():
    """Add faction table and update unit/army_list tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Starting faction system migration...")
    
    # Create faction table
    try:
        cursor.execute("""
            CREATE TABLE faction (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                color VARCHAR(7) DEFAULT '#0d6efd',
                icon VARCHAR(50) DEFAULT 'shield',
                background TEXT,
                special_rules TEXT,
                is_public BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user(id)
            )
        """)
        print("✓ Created faction table")
    except sqlite3.OperationalError as e:
        if "already exists" in str(e).lower():
            print("⊘ Faction table already exists, skipping")
        else:
            print(f"✗ Error creating faction table: {e}")
    
    # Add faction_id to unit table
    try:
        cursor.execute("ALTER TABLE unit ADD COLUMN faction_id INTEGER")
        cursor.execute("CREATE INDEX idx_unit_faction ON unit(faction_id)")
        print("✓ Added faction_id to unit table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("⊘ Unit.faction_id already exists, skipping")
        else:
            print(f"✗ Error adding faction_id to unit: {e}")
    
    # Add faction_id to army_list table
    try:
        cursor.execute("ALTER TABLE army_list ADD COLUMN faction_id INTEGER")
        cursor.execute("CREATE INDEX idx_army_list_faction ON army_list(faction_id)")
        print("✓ Added faction_id to army_list table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("⊘ ArmyList.faction_id already exists, skipping")
        else:
            print(f"✗ Error adding faction_id to army_list: {e}")
    
    conn.commit()
    conn.close()
    
    print("\nMigration completed successfully!")
    print("\nNew Faction System Features:")
    print("  - Create custom factions with descriptions and lore")
    print("  - Assign units to factions")
    print("  - Organize army lists by faction")
    print("  - Faction-wide special rules and customization")

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        exit(1)
    
    migrate_database()
