"""Migration script to add new unit type fields to database"""
import sqlite3
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'fad_lists.db')

def migrate_database():
    """Add new columns for 6 unit types support"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Starting migration to add unit type fields...")
    
    # List of new columns to add
    new_columns = [
        # Squad specific
        ("squad_members_json", "TEXT"),
        
        # Character specific
        ("specialization", "VARCHAR(20)"),
        
        # Heavy Weapons specific
        ("weapon_options_json", "TEXT"),
        
        # Vehicle specific
        ("vehicle_type", "VARCHAR(50)"),
        ("crew_size", "INTEGER"),
        ("carrying_capacity", "INTEGER"),
        ("vehicle_weapons_json", "TEXT"),
        ("vehicle_properties_json", "TEXT"),
        
        # Shared field - notes
        ("notes", "TEXT"),
    ]
    
    for column_name, column_type in new_columns:
        try:
            cursor.execute(f"ALTER TABLE unit ADD COLUMN {column_name} {column_type}")
            print(f"✓ Added column: {column_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"⊘ Column {column_name} already exists, skipping")
            else:
                print(f"✗ Error adding {column_name}: {e}")
    
    conn.commit()
    conn.close()
    
    print("\nMigration completed successfully!")
    print("\nNew unit types supported:")
    print("  - Squad (with squad_members_json)")
    print("  - Character (with specialization)")
    print("  - Heavy Weapons (with weapon_options_json)")
    print("  - Sniper (uses existing fields)")
    print("  - Psionic (already had psionic fields)")
    print("  - Vehicle (with vehicle_type, crew, capacity, weapons, properties)")

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        exit(1)
    
    migrate_database()
