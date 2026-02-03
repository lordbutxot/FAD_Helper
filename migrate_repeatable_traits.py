"""
Migration: Add repeatable traits support
- Adds is_repeatable field to Trait model
- Converts traits_json from array format [1,5,12] to object format {"1":1,"5":1,"12":1}
- Marks "Weapon Stabilizer" and "Linked Weapons" as repeatable
"""

from app import app, db
from models import Trait, Unit
import json

def migrate():
    with app.app_context():
        print("🔄 Starting Repeatable Traits Migration...")
        print("=" * 60)
        
        # Step 1: Add is_repeatable column to Trait table
        print("\n1. Adding is_repeatable column to Trait table...")
        try:
            with db.engine.connect() as conn:
                # Check if column exists
                result = conn.execute(db.text("""
                    SELECT COUNT(*) 
                    FROM pragma_table_info('trait') 
                    WHERE name='is_repeatable'
                """))
                exists = result.scalar() > 0
                
                if not exists:
                    conn.execute(db.text("""
                        ALTER TABLE trait 
                        ADD COLUMN is_repeatable BOOLEAN DEFAULT 0
                    """))
                    conn.commit()
                    print("   ✅ Added is_repeatable column")
                else:
                    print("   ℹ️  Column already exists")
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
            print("   Continuing with migration...")
        
        # Step 2: Mark repeatable traits
        print("\n2. Marking repeatable traits...")
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
                print(f"   ⚠️  Trait '{trait_name}' not found")
        
        db.session.commit()
        
        # Step 3: Convert traits_json format for all units
        print("\n3. Converting traits_json format...")
        units = Unit.query.all()
        converted_count = 0
        
        for unit in units:
            if unit.traits_json:
                try:
                    data = json.loads(unit.traits_json)
                    
                    # Check if already in new format (dict)
                    if isinstance(data, dict):
                        continue
                    
                    # Convert from array [1,5,12] to dict {"1":1,"5":1,"12":1}
                    if isinstance(data, list):
                        new_format = {str(trait_id): 1 for trait_id in data}
                        unit.traits_json = json.dumps(new_format)
                        converted_count += 1
                except json.JSONDecodeError:
                    print(f"   ⚠️  Invalid JSON for unit {unit.id}")
                except Exception as e:
                    print(f"   ⚠️  Error converting unit {unit.id}: {e}")
        
        # Step 4: Convert vehicle_properties_json format
        print("\n4. Converting vehicle_properties_json format...")
        vehicles = Unit.query.filter_by(unit_type='Vehicle').all()
        vehicle_converted = 0
        
        for vehicle in vehicles:
            if vehicle.vehicle_properties_json:
                try:
                    data = json.loads(vehicle.vehicle_properties_json)
                    
                    # Check if already in new format
                    if isinstance(data, dict):
                        continue
                    
                    # Convert from array to dict
                    if isinstance(data, list):
                        new_format = {str(prop_id): 1 for prop_id in data}
                        vehicle.vehicle_properties_json = json.dumps(new_format)
                        vehicle_converted += 1
                except json.JSONDecodeError:
                    print(f"   ⚠️  Invalid JSON for vehicle {vehicle.id}")
                except Exception as e:
                    print(f"   ⚠️  Error converting vehicle {vehicle.id}: {e}")
        
        db.session.commit()
        
        print(f"\n   ✅ Converted {converted_count} units")
        print(f"   ✅ Converted {vehicle_converted} vehicles")
        
        # Step 5: Summary
        print("\n" + "=" * 60)
        print("✅ Migration Complete!")
        print(f"   - Repeatable traits marked: {len(repeatable_traits)}")
        print(f"   - Units converted: {converted_count}")
        print(f"   - Vehicles converted: {vehicle_converted}")
        print("=" * 60)

if __name__ == '__main__':
    migrate()
