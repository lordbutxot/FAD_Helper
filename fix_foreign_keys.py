"""
Migration script to properly add faction_id foreign keys to unit and army_list tables.
SQLite requires table recreation to add foreign keys to existing tables.
"""
import sqlite3
import os

# Get the database path
db_path = 'instance/fad_lists.db'

if not os.path.exists(db_path):
    print(f"Error: Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Enable foreign keys
cursor.execute('PRAGMA foreign_keys = ON')

print("Starting migration to add foreign key constraints...")

# ===== Migrate army_list table =====
print("\n1. Migrating army_list table...")

# Create new table with proper foreign keys
cursor.execute('''
    CREATE TABLE army_list_new (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        faction_id INTEGER,
        name VARCHAR(200) NOT NULL,
        description TEXT,
        units_json TEXT NOT NULL,
        total_points FLOAT NOT NULL DEFAULT 0,
        total_units INTEGER NOT NULL DEFAULT 0,
        is_public BOOLEAN DEFAULT 0,
        views INTEGER DEFAULT 0,
        created_at DATETIME,
        updated_at DATETIME,
        FOREIGN KEY (user_id) REFERENCES user(id),
        FOREIGN KEY (faction_id) REFERENCES faction(id)
    )
''')

# Copy data from old table (excluding old 'faction' column)
cursor.execute('''
    INSERT INTO army_list_new 
    (id, user_id, faction_id, name, description, units_json, total_points, 
     total_units, is_public, views, created_at, updated_at)
    SELECT id, user_id, faction_id, name, description, units_json, total_points, 
           total_units, is_public, views, created_at, updated_at
    FROM army_list
''')

# Drop old table and rename new one
cursor.execute('DROP TABLE army_list')
cursor.execute('ALTER TABLE army_list_new RENAME TO army_list')

# Create indexes
cursor.execute('CREATE INDEX idx_army_list_user_id ON army_list(user_id)')
cursor.execute('CREATE INDEX idx_army_list_faction_id ON army_list(faction_id)')

print("✓ Migrated army_list table with foreign key constraint")

# ===== Migrate unit table =====
print("\n2. Migrating unit table...")

# Get current unit table schema
cursor.execute('PRAGMA table_info(unit)')
columns = cursor.fetchall()
print(f"   Found {len(columns)} columns in unit table")

# Create new table with proper foreign keys
cursor.execute('''
    CREATE TABLE unit_new (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        faction_id INTEGER,
        name VARCHAR(200) NOT NULL,
        unit_type VARCHAR(50) NOT NULL,
        
        -- Squad fields
        squad_size INTEGER,
        basic_weapon_id INTEGER,
        support_weapon_id INTEGER,
        heavy_weapon_id INTEGER,
        
        -- Character fields
        character_level VARCHAR(50),
        character_weapon_id INTEGER,
        
        -- Heavy Weapon fields
        hw_squad_size INTEGER,
        hw_weapon_id INTEGER,
        
        -- Sniper fields
        sniper_weapon_id INTEGER,
        
        -- Psionic fields
        psionic_level VARCHAR(50),
        psionic_powers TEXT,
        
        -- Vehicle fields
        vehicle_type VARCHAR(50),
        vehicle_weapon_id INTEGER,
        vehicle_armor INTEGER,
        
        -- Common fields
        armour_id INTEGER,
        traits TEXT,
        movement INTEGER,
        description TEXT,
        points FLOAT NOT NULL DEFAULT 0,
        is_public BOOLEAN DEFAULT 0,
        views INTEGER DEFAULT 0,
        created_at DATETIME,
        updated_at DATETIME,
        
        FOREIGN KEY (user_id) REFERENCES user(id),
        FOREIGN KEY (faction_id) REFERENCES faction(id),
        FOREIGN KEY (basic_weapon_id) REFERENCES weapon(id),
        FOREIGN KEY (support_weapon_id) REFERENCES weapon(id),
        FOREIGN KEY (heavy_weapon_id) REFERENCES weapon(id),
        FOREIGN KEY (character_weapon_id) REFERENCES weapon(id),
        FOREIGN KEY (hw_weapon_id) REFERENCES weapon(id),
        FOREIGN KEY (sniper_weapon_id) REFERENCES weapon(id),
        FOREIGN KEY (vehicle_weapon_id) REFERENCES weapon(id),
        FOREIGN KEY (armour_id) REFERENCES armour(id)
    )
''')

# Get all column names from old table
old_columns = [col[1] for col in columns]
# Build column list for INSERT (excluding old 'faction' column if it exists)
insert_columns = [col for col in old_columns if col != 'faction']
columns_str = ', '.join(insert_columns)

# Copy data from old table
cursor.execute(f'''
    INSERT INTO unit_new ({columns_str})
    SELECT {columns_str}
    FROM unit
''')

# Drop old table and rename new one
cursor.execute('DROP TABLE unit')
cursor.execute('ALTER TABLE unit_new RENAME TO unit')

# Create indexes
cursor.execute('CREATE INDEX idx_unit_user_id ON unit(user_id)')
cursor.execute('CREATE INDEX idx_unit_faction_id ON unit(faction_id)')
cursor.execute('CREATE INDEX idx_unit_type ON unit(unit_type)')

print("✓ Migrated unit table with foreign key constraint")

# Commit all changes
conn.commit()

# Verify foreign keys were created
print("\n3. Verifying foreign keys...")
cursor.execute('PRAGMA foreign_key_list(army_list)')
army_list_fks = cursor.fetchall()
print(f"   army_list foreign keys: {len(army_list_fks)}")
for fk in army_list_fks:
    print(f"     - {fk[2]}.{fk[3]} -> {fk[4]}")

cursor.execute('PRAGMA foreign_key_list(unit)')
unit_fks = cursor.fetchall()
print(f"   unit foreign keys: {len(unit_fks)}")

conn.close()

print("\n✓ Migration completed successfully!")
print("\nPlease restart the Flask server for changes to take effect.")
