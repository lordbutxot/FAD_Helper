"""
Database Migration: Add Squad Members, Secondary Weapons, and Crew Count
Adds:
- SquadMember table for individual squad member tracking
- secondary_weapon_id column to Unit table
- crew_count column to Unit table for heavy weapons
- crew_size default value for vehicles
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Unit, SquadMember
from sqlalchemy import text

def migrate_database():
    """Apply migration to add new features"""
    with app.app_context():
        print("=" * 60)
        print("Database Migration: Squad Members & Equipment")
        print("=" * 60)
        
        try:
            # Create squad_member table
            print("\n1. Creating squad_member table...")
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS squad_member (
                    id SERIAL PRIMARY KEY,
                    unit_id INTEGER NOT NULL,
                    member_number INTEGER NOT NULL,
                    member_type VARCHAR(20) NOT NULL DEFAULT 'Regular',
                    weapon_id INTEGER,
                    secondary_weapon_id INTEGER,
                    notes VARCHAR(200),
                    FOREIGN KEY (unit_id) REFERENCES unit(id) ON DELETE CASCADE,
                    FOREIGN KEY (weapon_id) REFERENCES weapon(id),
                    FOREIGN KEY (secondary_weapon_id) REFERENCES weapon(id)
                )
            """))
            print("   ✅ squad_member table created")
            
            # Add secondary_weapon_id to unit table
            print("\n2. Adding secondary_weapon_id column to unit table...")
            try:
                db.session.execute(text("""
                    ALTER TABLE unit ADD COLUMN secondary_weapon_id INTEGER REFERENCES weapon(id)
                """))
                print("   ✅ secondary_weapon_id column added")
            except Exception as e:
                if "duplicate column" in str(e).lower():
                    print("   ℹ️  secondary_weapon_id column already exists")
                else:
                    raise
            
            # Add crew_count to unit table  
            print("\n3. Adding crew_count column to unit table...")
            try:
                db.session.execute(text("""
                    ALTER TABLE unit ADD COLUMN crew_count INTEGER DEFAULT 2
                """))
                print("   ✅ crew_count column added")
            except Exception as e:
                if "duplicate column" in str(e).lower():
                    print("   ℹ️  crew_count column already exists")
                else:
                    raise
            
            # Update existing heavy weapon units to have crew_count = 2
            print("\n4. Setting default crew_count for heavy weapons...")
            db.session.execute(text("""
                UPDATE unit 
                SET crew_count = 2 
                WHERE unit_type = 'HeavyWeapon' AND crew_count IS NULL
            """))
            
            # Update existing vehicles to have crew_size = 1 if not set
            print("\n5. Setting default crew_size for vehicles...")
            db.session.execute(text("""
                UPDATE unit 
                SET crew_size = 1 
                WHERE unit_type = 'Vehicle' AND crew_size IS NULL
            """))
            
            db.session.commit()
            
            print("\n" + "=" * 60)
            print("✨ Migration completed successfully!")
            print("=" * 60)
            print("\nNew features added:")
            print("  • Squad member roster system")
            print("  • Secondary weapon support")
            print("  • Crew count tracking")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    migrate_database()
