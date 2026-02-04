import sqlite3

conn = sqlite3.connect('instance/fad_lists.db')
cursor = conn.cursor()

print("All tables:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
for row in cursor.fetchall():
    print(f"  {row[0]}")

print("\narmy_list_new foreign keys:")
cursor.execute('PRAGMA foreign_key_list(army_list_new)')
for row in cursor.fetchall():
    print(f"  {row}")

print("\narmy_list foreign keys:")
cursor.execute('PRAGMA foreign_key_list(army_list)')
for row in cursor.fetchall():
    print(f"  {row}")

conn.close()
