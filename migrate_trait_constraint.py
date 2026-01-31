"""
Migration Script: Update Trait table constraint from unique(name) to unique(name, category)
This allows traits with the same name in different categories (e.g., Fast for Infantry and Fast for Vehicles)
"""
from app import app, db
from sqlalchemy import text
import sys

def migrate_trait_constraint():
    """Drop old unique constraint and add composite constraint"""
    with app.app_context():
        try:
            print("\n🔄 Migrating Trait table constraint...")
            
            # Drop the old unique constraint on name
            print("   Dropping old unique constraint on 'name'...")
            db.session.execute(text("ALTER TABLE trait DROP CONSTRAINT IF EXISTS trait_name_key;"))
            
            # Check if the composite constraint already exists
            print("   Checking for existing composite unique constraint...")
            result = db.session.execute(text("""
                SELECT constraint_name FROM information_schema.table_constraints
                WHERE table_name='trait' AND constraint_name='uix_trait_name_category'
            """))
            constraint_exists = result.fetchone() is not None
            
            if not constraint_exists:
                # Add new composite unique constraint on (name, category)
                print("   Adding new composite unique constraint on (name, category)...")
                db.session.execute(text(
                    "ALTER TABLE trait ADD CONSTRAINT uix_trait_name_category UNIQUE (name, category);"
                ))
            else:
                print("   ℹ️  Composite unique constraint already exists, skipping...")
            
            db.session.commit()
            print("   ✅ Constraint migration successful!")
            
        except Exception as e:
            db.session.rollback()
            print(f"   ❌ Error during migration: {e}")
            sys.exit(1)

if __name__ == '__main__':
    migrate_trait_constraint()
