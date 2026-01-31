"""
Migration Script: Add description column to Unit table
"""
from app import app, db
from sqlalchemy import text
import sys

def migrate_add_description():
    """Add description column to unit table if it doesn't exist"""
    with app.app_context():
        try:
            print("\n🔄 Migrating Unit table - Adding description column...")
            
            # Check if description column already exists
            print("   Checking if description column exists...")
            result = db.session.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name='unit' AND column_name='description'
            """))
            column_exists = result.fetchone() is not None
            
            if not column_exists:
                # Add description column
                print("   Adding description column to unit table...")
                db.session.execute(text(
                    "ALTER TABLE unit ADD COLUMN description TEXT;"
                ))
                db.session.commit()
                print("   ✅ Description column added successfully!")
            else:
                print("   ℹ️  Description column already exists, skipping...")
            
        except Exception as e:
            db.session.rollback()
            print(f"   ❌ Error during migration: {e}")
            sys.exit(1)

if __name__ == '__main__':
    migrate_add_description()
