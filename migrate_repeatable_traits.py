"""
Migration: Add repeatable traits support
- Adds is_repeatable field to Trait model
- Marks "Weapon Stabilizer" and "Linked Weapons" as repeatable
"""

from app import app, db
from sqlalchemy import text
import sys

def migrate():
    with app.app_context():
        print("🔄 Starting Repeatable Traits Migration...")
        print("=" * 60)
        
        # Step 1: Add is_repeatable column to Trait table (PostgreSQL)
        print("\n1. Adding is_repeatable column to Trait table...")
        try:
            with db.engine.connect() as conn:
                # For PostgreSQL - check if column exists
                check_column = text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = 'trait' 
                        AND column_name = 'is_repeatable'
                    )
                """)
                result = conn.execute(check_column).scalar()
                
                if not result:
                    # Column doesn't exist, add it
                    add_column = text("""
                        ALTER TABLE trait 
                        ADD COLUMN is_repeatable BOOLEAN DEFAULT FALSE
                    """)
                    conn.execute(add_column)
                    conn.commit()
                    print("   ✅ Added is_repeatable column")
                else:
                    print("   ℹ️  Column already exists")
        except Exception as e:
            print(f"   ⚠️  Error adding column: {e}")
            print("   Continuing with migration...")
        
        # Step 2: Mark repeatable traits
        print("\n2. Marking repeatable traits...")
        try:
            from models import Trait
            
            repeatable_traits = [
                'Weapon Stabilizer',
                'Linked Weapons'
            ]
            
            for trait_name in repeatable_traits:
                trait = Trait.query.filter_by(name=trait_name).first()
                if trait:
                    trait.is_repeatable = True
                    print(f"   ✅ Marked '{trait_name}' as repeatable")
                else:
                    print(f"   ⚠️  Trait '{trait_name}' not found (will be marked during init_production_db)")
            
            db.session.commit()
        except Exception as e:
            print(f"   ⚠️  Error marking traits: {e}")
            db.session.rollback()
        
        # Step 3: Summary
        print("\n" + "=" * 60)
        print("✅ Migration Complete!")
        print("=" * 60)

if __name__ == '__main__':
    migrate()

