"""
Simple SQL migration to add is_admin column to existing database
"""
import sqlite3
import os

db_path = 'instance/fad_lists.db'

if not os.path.exists(db_path):
    print("Error: instance/fad_lists.db not found!")
    print("Please run: python init_db.py first")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check existing columns
    cursor.execute('PRAGMA table_info(user)')
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    # Add missing columns one by one
    new_columns = {
        'is_admin': 'BOOLEAN DEFAULT 0',
        'last_login': 'DATETIME',
        'failed_login_attempts': 'INTEGER DEFAULT 0',
        'account_locked_until': 'DATETIME'
    }
    
    for column_name, column_type in new_columns.items():
        if column_name not in existing_columns:
            print(f"Adding {column_name} column...")
            cursor.execute(f'ALTER TABLE user ADD COLUMN {column_name} {column_type}')
            conn.commit()
            print(f"✓ Added {column_name}")
        else:
            print(f"✓ {column_name} already exists")
    
    # Create admin user if none exists
    cursor.execute('SELECT COUNT(*) FROM user WHERE is_admin = 1')
    admin_count = cursor.fetchone()[0]
    
    if admin_count == 0:
        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash('Admin123', method='pbkdf2:sha256', salt_length=16)
        
        cursor.execute('''
            INSERT INTO user (username, email, password_hash, is_admin, created_at, failed_login_attempts)
            VALUES (?, ?, ?, ?, datetime('now'), ?)
        ''', ('admin', None, password_hash, 1, 0))
        conn.commit()
        
        print("\n" + "=" * 60)
        print("✓ Admin user created!")
        print("=" * 60)
        print("Username: admin")
        print("Password: Admin123")
        print("\nLogin at: http://127.0.0.1:5000/login")
        print("Admin panel: http://127.0.0.1:5000/admin")
        print("=" * 60)
    else:
        print(f"\n✓ {admin_count} admin user(s) already exist")

except sqlite3.OperationalError as e:
    print(f"Error: {e}")
finally:
    conn.close()
