"""
Migration: Add role column to Unit table for battlefield role tags
"""
from app import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        print("🔄 Adding role column to Unit table...")
        print("=" * 60)
        
        try:
            with db.engine.connect() as conn:
                # Check if column exists (PostgreSQL)
                check_column = text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = 'unit' 
                        AND column_name = 'role'
                    )
                """)
                result = conn.execute(check_column).scalar()
                
                if not result:
                    # Column doesn't exist, add it
                    add_column = text("""
                        ALTER TABLE unit 
                        ADD COLUMN role VARCHAR(50)
                    """)
                    conn.execute(add_column)
                    conn.commit()
                    print("   ✅ Added role column to unit table")
                else:
                    print("   ℹ️  role column already exists")
                    
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
            print("   Attempting SQLite fallback...")
            try:
                # Try SQLite syntax
                with db.engine.connect() as conn:
                    check_sqlite = text("""
                        SELECT COUNT(*) 
                        FROM pragma_table_info('unit') 
                        WHERE name='role'
                    """)
                    result = conn.execute(check_sqlite).scalar()
                    
                    if result == 0:
                        add_sqlite = text("""
                            ALTER TABLE unit 
                            ADD COLUMN role VARCHAR(50)
                        """)
                        conn.execute(add_sqlite)
                        conn.commit()
                        print("   ✅ Added role column (SQLite)")
                    else:
                        print("   ℹ️  role column already exists (SQLite)")
            except Exception as e2:
                print(f"   ❌ Error: {e2}")
        
        print("=" * 60)
        print("✅ Migration complete!")
        print("=" * 60)

if __name__ == '__main__':
    migrate()
