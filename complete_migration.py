"""
Complete the migration by finishing army_list and properly migrating unit table
"""
import sqlite3

conn = sqlite3.connect('instance/fad_lists.db')
cursor = conn.cursor()

# Enable foreign keys
cursor.execute('PRAGMA foreign_keys = ON')

print("Completing migration...")

# ===== Complete army_list migration =====
print("\n1. Completing army_list migration...")

# Check if army_list_new exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='army_list_new'")
if cursor.fetchone():
    print("   Found incomplete migration, finishing it...")
    
    # Drop old table and rename new one
    cursor.execute('DROP TABLE army_list')
    cursor.execute('ALTER TABLE army_list_new RENAME TO army_list')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_army_list_user_id ON army_list(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_army_list_faction_id ON army_list(faction_id)')
    
    print("✓ Completed army_list migration")
else:
    print("   army_list already migrated")

# ===== Migrate unit table =====
print("\n2. Migrating unit table...")

# Get actual unit table schema
cursor.execute('PRAGMA table_info(unit)')
columns = cursor.fetchall()
column_definitions = []
column_names = []

for col in columns:
    col_name = col[1]
    col_type = col[2]
    col_notnull = col[3]
    col_default = col[4]
    col_pk = col[5]
    
    # Skip old faction column
    if col_name == 'faction':
        continue
    
    column_names.append(col_name)
    
    # Build column definition
    definition = f"{col_name} {col_type}"
    if col_pk:
        definition += " PRIMARY KEY"
    if col_notnull and not col_pk:
        definition += " NOT NULL"
    if col_default is not None:
        definition += f" DEFAULT {col_default}"
    
    column_definitions.append(definition)

# Add foreign key constraints
foreign_keys = [
    "FOREIGN KEY (user_id) REFERENCES user(id)",
    "FOREIGN KEY (faction_id) REFERENCES faction(id)",
    "FOREIGN KEY (armour_id) REFERENCES armour(id)",
    "FOREIGN KEY (basic_weapon_id) REFERENCES weapon(id)",
    "FOREIGN KEY (support_weapon_id) REFERENCES weapon(id)",
    "FOREIGN KEY (heavy_weapon_id) REFERENCES weapon(id)"
]

# Create new table
create_statement = "CREATE TABLE unit_new (\n    "
create_statement += ",\n    ".join(column_definitions + foreign_keys)
create_statement += "\n)"

print(f"   Creating new unit table with {len(column_names)} columns...")
cursor.execute(create_statement)

# Copy data
columns_str = ", ".join(column_names)
print(f"   Copying data...")
cursor.execute(f"INSERT INTO unit_new ({columns_str}) SELECT {columns_str} FROM unit")

# Drop old and rename
print(f"   Replacing old table...")
cursor.execute('DROP TABLE unit')
cursor.execute('ALTER TABLE unit_new RENAME TO unit')

# Create indexes
cursor.execute('CREATE INDEX IF NOT EXISTS idx_unit_user_id ON unit(user_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_unit_faction_id ON unit(faction_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_unit_type ON unit(unit_type)')

print("✓ Migrated unit table with foreign key constraints")

# Commit
conn.commit()

# Verify
print("\n3. Verifying foreign keys...")
cursor.execute('PRAGMA foreign_key_list(army_list)')
army_list_fks = cursor.fetchall()
print(f"   army_list has {len(army_list_fks)} foreign keys:")
for fk in army_list_fks:
    print(f"     - {fk[3]} -> {fk[2]}.{fk[4]}")

cursor.execute('PRAGMA foreign_key_list(unit)')
unit_fks = cursor.fetchall()
print(f"   unit has {len(unit_fks)} foreign keys:")
for fk in unit_fks:
    print(f"     - {fk[3]} -> {fk[2]}.{fk[4]}")

conn.close()

print("\n✓ Migration completed successfully!")
print("\nPlease restart the Flask server.")
