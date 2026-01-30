"""
Production Database Initialization Script
Initializes database with all official F.A.D. data for production deployment
"""
from app import app, db
from models import Trait, Weapon, Armour, User
import sys

def init_production_database():
    """Initialize production database with all official F.A.D. data"""
    
    with app.app_context():
        print("🚀 Initializing Production Database...")
        print("=" * 60)
        
        # Create all tables
        print("\n1. Creating database tables...")
        db.create_all()
        print("   ✅ Tables created")
        
        # Check if data already exists
        if Trait.query.first() or Weapon.query.first() or Armour.query.first():
            print("\n⚠️  Database already contains data!")
            response = input("   Do you want to skip initialization? (y/n): ")
            if response.lower() == 'y':
                print("   Skipping data population...")
                return
        
        # Infantry Traits (44 traits)
        print("\n2. Populating Infantry Traits...")
        infantry_traits = [
            ('Accurate', 'Unit gains +1 to shooting rolls', 1.2),
            ('Aggressive', 'Must move toward enemy if in sight', 1.1),
            ('Bestow Trait', 'Can grant a trait to nearby units', 1.3),
            ('Brutal', '+1 damage in close combat', 1.2),
            ('Camouflage', 'Harder to hit when in cover', 1.15),
            ('Champion', 'Reroll failed morale tests', 1.25),
            ('Coward', 'Must test to move toward enemy', 0.8),
            ('Deadly Shot', 'Ignore cover modifiers when shooting', 1.3),
            ('Defensive', 'Bonus when holding position', 1.15),
            ('Disciplined', 'Reroll failed command tests', 1.2),
            ('Elite Training', 'Improved combat effectiveness', 1.3),
            ('Fast', '+2" movement', 1.15),
            ('Fear', 'Enemies must test morale to approach', 1.25),
            ('Fearless', 'Immune to fear and morale penalties', 1.3),
            ('Fire Team', 'Coordinated fire bonus', 1.2),
            ('First Strike', 'Always strikes first in close combat', 1.3),
            ('Frenzy', 'Must charge enemy if able', 1.2),
            ('Good Shot', 'Reroll 1s when shooting', 1.15),
            ('Gung Ho', 'Can shoot and charge', 1.25),
            ('Hardy', 'Ignore first wound taken', 1.3),
            ('Hero', 'Can perform heroic actions', 1.4),
            ('Hit and Run', 'Can disengage without penalty', 1.2),
            ('Impetuous', 'Must move toward enemy', 1.1),
            ('Inaccurate', '-1 to shooting rolls', 0.8),
            ('Infiltrate', 'Deploy forward before game starts', 1.25),
            ('Inspiring', 'Nearby units gain morale bonus', 1.3),
            ('Jump Pack', 'Can move over terrain and units', 1.3),
            ('Large', 'Easier to hit but more resilient', 1.15),
            ('Leader', 'Extends command radius', 1.3),
            ('Lucky', 'Reroll one die per turn', 1.2),
            ('Marksman', 'Improved accuracy at long range', 1.25),
            ('Medic', 'Can heal nearby wounded', 1.2),
            ('Poor Shot', 'Reroll 6s when shooting', 0.9),
            ('Psychic', 'Can use psychic powers', 1.4),
            ('Rage', 'Bonus when wounded', 1.15),
            ('Rapid Fire', 'Extra shots at short range', 1.25),
            ('Regeneration', 'Recovers wounds over time', 1.35),
            ('Scout', 'Can perform reconnaissance', 1.2),
            ('Sharpshooter', 'Pick specific targets', 1.3),
            ('Slow', '-2" movement', 0.85),
            ('Stealth', 'Harder to detect', 1.25),
            ('Stubborn', 'Ignores morale penalties', 1.2),
            ('Tactical', 'Can use tactical abilities', 1.25),
            ('Veteran', 'Reroll failed tests', 1.3)
        ]
        
        added_infantry = 0
        for name, desc, mult in infantry_traits:
            if not Trait.query.filter_by(name=name, category='Infantry').first():
                trait = Trait(
                    name=name,
                    description=desc,
                    points_multiplier=mult,
                    category='Infantry'
                )
                db.session.add(trait)
                added_infantry += 1
        
        db.session.commit()
        print(f"   ✅ Added {added_infantry} infantry traits")
        
        # Vehicle Properties (26 properties)
        print("\n3. Populating Vehicle Properties...")
        vehicle_properties = [
            ('Advanced Targeting System', 'Enhanced weapon accuracy and fire control systems', 1.2),
            ('AI Controlled', 'Operated by artificial intelligence, no crew required', 1.15),
            ('Amphibious', 'Can move through water without penalty', 1.1),
            ('Energy Screen', 'Force field provides additional protection against damage', 1.3),
            ('Fast (Vehicle)', 'Higher than normal movement speed for vehicle type', 1.15),
            ('Fixed Mount (1)', 'One weapon cannot traverse, limited firing arc', 0.9),
            ('Fixed Mount (2)', 'Two weapons cannot traverse, limited firing arc', 0.85),
            ('Fixed Mount (3)', 'Three weapons cannot traverse, limited firing arc', 0.8),
            ('Forward Observer', 'Can call in artillery strikes or air support', 1.15),
            ('Improved Weapons Control', 'All weapons can fire at different targets', 1.25),
            ('Jump Jets', 'Can make short aerial jumps over terrain and obstacles', 1.3),
            ('Linked Weapons', 'Multiple weapons fire as one coordinated system', 1.2),
            ('Medevac', 'Medical evacuation vehicle, can treat wounded infantry', 1.1),
            ('Open Topped', 'Crew vulnerable but embarked troops can fire out', 0.95),
            ('Reactive Armour', 'Explosive plates detonate to deflect incoming rounds', 1.25),
            ('Slow (Vehicle)', 'Lower than normal movement speed for vehicle type', 0.85),
            ('Smoke', 'Can deploy smoke for concealment', 1.1),
            ('Stealth (Vehicle)', 'Advanced camouflage and heat signature reduction', 1.3),
            ('Supercharged', 'Enhanced engine allows burst of extra speed', 1.15),
            ('Tough', 'Extra structural integrity, harder to destroy', 1.2),
            ('Transport', 'Can carry infantry units into battle', 1.15),
            ('Under-Powered', 'Weak engine results in sluggish performance', 0.9),
            ('Walker', 'Legged vehicle, can traverse rough terrain easily', 1.2),
            ('Weapon Stabilizer', 'Can fire accurately while moving at full speed', 1.2),
            ('Heavy Armour', 'Exceptionally thick armor plating', 1.3),
            ('Reconnaissance', 'Scouting vehicle with enhanced sensors', 1.15)
        ]
        
        added_vehicles = 0
        for name, desc, mult in vehicle_properties:
            if not Trait.query.filter_by(name=name, category='Vehicle').first():
                trait = Trait(
                    name=name,
                    description=desc,
                    points_multiplier=mult,
                    category='Vehicle'
                )
                db.session.add(trait)
                added_vehicles += 1
        
        db.session.commit()
        print(f"   ✅ Added {added_vehicles} vehicle properties")
        
        # Weapons (46 weapons total)
        print("\n4. Populating Weapons...")
        weapons_data = [
            # Basic Weapons (18)
            ('None', 'Basic', 0, 0, 0, 0, '', 0),
            ('Pistol', 'Basic', 1, 3, 1, 0, '', 1),
            ('SMG', 'Basic', 1, 3, 2, 0, 'Rapid Fire', 2),
            ('Assault Rifle', 'Basic', 2, 4, 2, 1, '', 3),
            ('Battle Rifle', 'Basic', 3, 4, 2, 1, '', 4),
            ('Shotgun', 'Basic', 1, 5, 1, 0, 'Close Range', 3),
            ('Carbine', 'Basic', 2, 3, 2, 0, '', 2),
            ('Laser Rifle', 'Basic', 3, 3, 2, 2, 'Energy', 5),
            ('Plasma Rifle', 'Basic', 2, 5, 2, 3, 'Energy, Overheat', 6),
            ('Gauss Rifle', 'Basic', 4, 4, 2, 2, 'Magnetic', 7),
            ('Flamer', 'Basic', 1, 0, 3, 0, 'Auto Hit, Template', 4),
            ('Grenade Launcher', 'Basic', 2, 4, 1, 1, 'Blast', 3),
            ('Needler', 'Basic', 2, 2, 3, 0, 'Poison', 4),
            ('Bolter', 'Basic', 2, 4, 2, 2, 'Explosive', 5),
            ('Autogun', 'Basic', 2, 3, 3, 0, 'Suppression', 2),
            ('Las Carbine', 'Basic', 2, 3, 2, 1, 'Energy', 3),
            ('Pulse Rifle', 'Basic', 3, 4, 3, 1, 'Energy', 6),
            ('Gauss Rifle (linked)', 'Basic', 4, 4, 4, 2, 'Magnetic, Linked', 10),
            
            # Support Weapons (10)
            ('Shotgun (Combat)', 'Support', 1, 5, 2, 0, 'Close Range', 4),
            ('Sniper Rifle', 'Support', 6, 5, 1, 2, 'Precision', 8),
            ('DMR', 'Support', 4, 4, 1, 1, 'Marksman', 5),
            ('Grenade Launcher (Support)', 'Support', 3, 4, 1, 1, 'Blast, Indirect', 5),
            ('Rocket Launcher', 'Support', 4, 6, 1, 4, 'Anti-Tank', 10),
            ('Missile Launcher', 'Support', 5, 6, 1, 4, 'Anti-Tank, Guided', 12),
            ('Flamer (Heavy)', 'Support', 1, 0, 4, 0, 'Auto Hit, Template', 6),
            ('Plasma Gun', 'Support', 2, 5, 1, 3, 'Energy, Overheat', 7),
            ('Meltagun', 'Support', 1, 6, 1, 5, 'Energy, Melta', 9),
            ('Missile Launcher (Power Armour)', 'Support', 5, 6, 2, 4, 'Anti-Tank, Guided', 15),
            
            # Heavy Weapons (18)
            ('General Purpose MG', 'Heavy', 3, 4, 4, 1, 'Suppression', 8),
            ('Heavy MG', 'Heavy', 3, 5, 5, 2, 'Suppression', 10),
            ('Autocannon', 'Heavy', 4, 5, 3, 3, '', 12),
            ('Light Cannon', 'Heavy', 4, 5, 2, 2, '', 10),
            ('Heavy Cannon', 'Heavy', 5, 6, 2, 4, 'Anti-Tank', 15),
            ('Plasma Cannon', 'Heavy', 3, 6, 1, 4, 'Energy, Overheat, Blast', 14),
            ('Laser Cannon', 'Heavy', 5, 5, 2, 3, 'Energy', 13),
            ('Rail Gun', 'Heavy', 6, 6, 1, 5, 'Anti-Tank, Magnetic', 18),
            ('Missile Pod', 'Heavy', 5, 5, 4, 3, 'Anti-Tank', 16),
            ('Mortar', 'Heavy', 3, 4, 1, 1, 'Blast, Indirect', 8),
            ('Heavy Mortar', 'Heavy', 4, 5, 1, 2, 'Blast, Indirect', 12),
            ('Flak Gun', 'Heavy', 3, 4, 6, 1, 'Anti-Air', 10),
            ('Multi-Melta', 'Heavy', 2, 6, 2, 5, 'Energy, Melta', 16),
            ('Gatling Cannon', 'Heavy', 3, 4, 8, 2, 'Suppression', 14),
            ('Heavy Bolter', 'Heavy', 3, 5, 4, 2, 'Explosive', 12),
            ('Assault Cannon', 'Heavy', 3, 5, 6, 2, 'Suppression', 15),
            ('Lascannon', 'Heavy', 6, 6, 1, 4, 'Energy, Anti-Tank', 16),
            ('Rail Gun (Heavy)', 'Heavy', 6, 6, 2, 5, 'Anti-Tank, Magnetic', 22),
        ]
        
        added_weapons = 0
        updated_weapons = 0
        for name, wclass, rng, dmg, fe, ap, special, pts in weapons_data:
            weapon = Weapon.query.filter_by(name=name).first()
            if weapon:
                weapon.category = wclass
                weapon.range_multiplier = rng
                weapon.damage = dmg
                weapon.fire_effect = fe
                weapon.armor_piercing = ap
                weapon.special_rules = special
                weapon.points = pts
                updated_weapons += 1
            else:
                weapon = Weapon(
                    name=name,
                    category=wclass,
                    range_multiplier=rng,
                    damage=dmg,
                    fire_effect=fe,
                    armor_piercing=ap,
                    special_rules=special,
                    points=pts
                )
                db.session.add(weapon)
                added_weapons += 1
        
        db.session.commit()
        print(f"   ✅ Added {added_weapons} weapons, updated {updated_weapons}")
        
        # Armour (8 types)
        print("\n5. Populating Armour...")
        armour_data = [
            ('None', 0, '', 0),
            ('Light', 1, 'Basic protection', 2),
            ('Improved', 2, 'Enhanced armor plating', 4),
            ('Heavy', 3, 'Thick armor', 6),
            ('Battle Dress', 4, 'Advanced combat armor', 8),
            ('Lt. Power', 5, 'Powered armor suit', 12),
            ('Medium Power', 6, 'Enhanced powered armor', 16),
            ('Hvy. Power', 7, 'Heavy powered armor', 20),
        ]
        
        added_armour = 0
        updated_armour = 0
        for name, rating, special, pts in armour_data:
            armour = Armour.query.filter_by(name=name).first()
            if armour:
                armour.rating = rating
                armour.special_rules = special
                armour.points = pts
                updated_armour += 1
            else:
                armour = Armour(
                    name=name,
                    rating=rating,
                    special_rules=special,
                    points=pts
                )
                db.session.add(armour)
                added_armour += 1
        
        db.session.commit()
        print(f"   ✅ Added {added_armour} armour types, updated {updated_armour}")
        
        print("\n" + "=" * 60)
        print("✅ Production Database Initialized Successfully!")
        print("\n📊 Summary:")
        print(f"   Infantry Traits: {Trait.query.filter_by(category='Infantry').count()}")
        print(f"   Vehicle Properties: {Trait.query.filter_by(category='Vehicle').count()}")
        print(f"   Weapons: {Weapon.query.count()}")
        print(f"   Armour Types: {Armour.query.count()}")
        print(f"   Users: {User.query.count()}")
        print("\n🎉 Your F.A.D. Helper is ready for deployment!")
        print("=" * 60)


if __name__ == '__main__':
    try:
        init_production_database()
    except Exception as e:
        print(f"\n❌ Error initializing database: {e}")
        sys.exit(1)
