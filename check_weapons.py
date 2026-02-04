import sqlite3

conn = sqlite3.connect('instance/fad_database.db')
cursor = conn.cursor()

# Get all weapons
cursor.execute('SELECT id, name, category FROM weapon ORDER BY category, name')
weapons = cursor.fetchall()

print("Weapons in Database:")
print("=" * 70)
for weapon_id, name, category in weapons:
    print(f"{weapon_id:3} | {name:40} | {category}")

conn.close()
