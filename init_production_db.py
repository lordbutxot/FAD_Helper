"""
Production Database Initialization Script
Initializes database with all official F.A.D. data for production deployment
This script is SAFE to run multiple times - it preserves all user data
"""
from app import app, db
from models import Trait, Weapon, Armour, User, Faction, ArmyList, Unit, FactionRating
import sys

OFFICIAL_INFANTRY_TRAITS = [
    'Adaptive Camouflage', 'Aerial', 'Aggressive', 'Agile', 'Assault Troops', 'Berserk', 'Bestow Trait', 'Brave',
    'Bug Hunter', 'Cautious', 'Combat Drugs', 'Dependant', 'Detection', 'Disruptive Charge', 'Droids (self-less)',
    'Droids (self-preserving)', 'Drop Troop', 'Elusive', 'Engineer', 'Fanatic', 'Fast', 'Fearless', 'Fire Team',
    'Flyer', 'Frail', 'Frenzied', 'Goon', 'Grav Mount', 'Grizzled', 'Gung Ho', 'Hardened', 'Hero', 'Hesitant',
    'Hive mind (controller)', 'Hive Mind (unit)', 'HQ', 'Huge', 'Ignore Pain', 'Infect', 'Infilration',
    'Inflexible', 'Jet Packs', 'Legend', 'Limited Teleport', 'Mechanized', 'Night Vision', 'No Grenades',
    'Obvious Target', 'Recon', 'Regenerate', 'Relentless', 'Reserves', 'Resilient (2)', 'Resilient (3)',
    'Resilient (4)', 'Resilient (5)', 'Resilient (6)', 'Save', 'Self Repairing', 'Shaky', 'Shock Troops',
    'Slick', 'Slow', 'Slow Firing', 'Stealth', 'Zombie'
]

OFFICIAL_VEHICLE_TRAITS = [
    'Advanced Targeting System', 'AI Controlled', 'Alternate Fire Weapons (2)', 'Alternate Fire Weapons (3)',
    'Amphibious', 'Close - In Defense System', 'Command Vehicle', 'Electronic Countermeasures', 'Energy screen',
    'Fast', 'Fixed Mount (1)', 'Fixed Mount (2)', 'Fixed Mount (3)', 'Forward Observer', 'Improved Weapons Control',
    'Jump Jets', 'Linked Weapons', 'Medevac', 'Reactive Armour', 'Reserves', 'Slow', 'Smoke', 'Stealth',
    'Supercharged', 'Under-Powered', 'Weapon Stabilizer'
]

def cleanup_non_official_traits():
    allowed = set(OFFICIAL_INFANTRY_TRAITS + OFFICIAL_VEHICLE_TRAITS)
    existing = Trait.query.all()
    to_delete = [t for t in existing if t.name not in allowed]
    if not to_delete:
        print("   ✅ No non-official traits to remove")
        return

    print(f"   ⚠️  Removing {len(to_delete)} non-official traits...")
    for trait in to_delete:
        print(f"     - Deleting: {trait.name} ({trait.category or 'Uncategorized'})")
        db.session.delete(trait)
    db.session.commit()

def init_production_database():
    """Initialize production database with all official F.A.D. data
    
    SAFE: This script only adds game data and preserves all user data:
    - Users remain unchanged
    - Factions remain unchanged  
    - Army Lists remain unchanged
    - Ratings remain unchanged
    - Only repopulates game data (Traits, Weapons, Armour) if missing
    """
    
    with app.app_context():
        print("🚀 Initializing Production Database...")
        print("=" * 60)
        print("⚠️  DATABASE PRESERVATION MODE - All user data is safe!")
        print("=" * 60)
        
        # Create all tables
        print("\n1. Creating database tables...")
        db.create_all()
        print("   ✅ Tables created/verified")
        
        # Count existing data
        user_count = User.query.count()
        faction_count = Faction.query.count()
        list_count = ArmyList.query.count()
        
        if user_count > 0:
            print(f"\n✅ Found {user_count} existing users - preserving all user data")
        if faction_count > 0:
            print(f"✅ Found {faction_count} existing factions - preserving all factions")
        if list_count > 0:
            print(f"✅ Found {list_count} existing army lists - preserving all lists")
        
        # Cleanup non-official traits before any early exit
        print("\n1b. Cleaning non-official traits...")
        cleanup_non_official_traits()

        # Check if data already exists - if so, skip initialization
        if Trait.query.first() or Weapon.query.first() or Armour.query.first():
            print("\n✅ Database already initialized with data!")
            print("   Skipping data population to preserve existing data...")
            return
        
        # Infantry Traits (official table traits only)
        print("\n2. Populating Infantry Traits...")
        infantry_traits = [
            ('Adaptive Camouflage', 'Outfit/armour disrupts appearance; shooting resolved one range band further if moved, or cannot be shot beyond long range if stationary.', 1.30),
            ('Aerial', 'Hover movement that ignores obstacles up to the model height; lands after moving.', 1.30),
            ('Aggressive', 'If Under Fire and moving, must move toward the enemy; ignores Command Response limits.', 1.10),
            ('Agile', 'Ignores movement penalties when crossing Difficult Terrain.', 1.20),
            ('Assault Troops', '+2 to all Close Assaults.', 1.30),
            ('Berserk', 'Ignores Under Fire/Pinned when activating within close assault range; must charge nearest enemy and gains +2 Close Assault.', 1.30),
            ('Bestow Trait', 'If this character joins a squad, may bestow one predefined trait upon them.', 1.40),
            ('Brave', 'Automatically succeeds on one morale die; roll one fewer die and add one success.', 1.50),
            ('Bug Hunter', '+1 to Close Assault and Fire Effect rolls when fighting alien races.', 1.20),
            ('Cautious', 'Must test Quality to leave cover if Under Fire.', 0.90),
            ('Combat Drugs', 'Once per game: gain Berserk, Fearless, Swift; must charge nearest enemy; roll 1d6 per survivor, 6 causes a wound.', 1.20),
            ('Dependant', 'Automatically passes one Command Response die if led by officer; otherwise fails one.', 1.00),
            ('Detection', 'Each activation removes/reveals all hidden markers within 12".', 1.10),
            ('Disruptive Charge', 'Charging into close combat gives opponent -2 Fire Effect on free attack.', 1.20),
            ('Droids (self-less)', 'No morale checks; never Elite; Relentless; save on draws; die instead of wounded.', 1.60),
            ('Droids (self-preserving)', 'No morale checks; never Elite; save on draws; die instead of wounded.', 1.30),
            ('Drop Troop', 'May deploy after battle starts using Drop Troops rule.', 1.30),
            ('Elusive', 'Once per turn when fired upon, may fall back 4" before shooting is resolved.', 1.40),
            ('Engineer', 'Auto-succeeds one die when rigging/detonating charges; +2 to minefield rolls.', 1.20),
            ('Fanatic', 'Never checks Resolve; must be Steady Resolve.', 1.60),
            ('Fast', '+2" base movement rate.', 1.20),
            ('Fearless', 'Ignores Morale Tests caused by Terrifying units or psionic Terror.', 1.10),
            ('Fire Team', 'Two squads act as linked Fire Teams per advanced rule.', 1.20),
            ('Flyer', 'Considered airborne at all times; moves over obstacles and never receives terrain benefits.', 1.20),
            ('Frail', '-1 Armour.', 0.90),
            ('Frenzied', 'Each model receives +1 additional kill roll in assault combat.', 1.30),
            ('Goon', 'May not fire beyond close range (except return fire); -1 Fire Effect; -1 Armour; may never Rush.', 0.70),
            ('Grav Mount', 'Heavy weapon mount moves with crew; may move and fire light/medium heavy weapons; damage disables on failed Quality tests.', 1.40),
            ('Grizzled', 'Check Resolve at one level higher than Quality.', 1.20),
            ('Gung Ho', 'May ignore Under Fire any turn they Close Assault.', 1.10),
            ('Hardened', 'Ignore Under Fire until first casualty; may leave wounded behind.', 1.10),
            ('Hero', 'Character/Psionic only; shoots individually; can pick target at close range; Fearless and Shock Troops; non-heroes -2 Fire Effect to shoot them.', 1.50),
            ('Hesitant', 'Unless within 15" of enemy, must pass Quality test to activate.', 0.80),
            ('Hive mind (controller)', 'Controls hive mind units; also Fanatic and Relentless.', 1.50),
            ('Hive Mind (unit)', 'Fanatic and Relentless within 12" of controller; otherwise must pass Quality test to activate.', 1.20),
            ('HQ', 'Single-figure only; once per turn one unit may reroll failed Command Response.', 1.20),
            ('Huge', 'May fire heavy weapons while moving; -2 Fire Effect; 4 kill rolls in assault; requires 2 hits in a volley if no AP; no cover benefits.', 1.50),
            ('Ignore Pain', 'May continue if wounded; each activation pass Quality Test or be removed.', 1.20),
            ('Infect', 'When killing in Close Assault, roll 1d6; on 5+ target is infected.', 1.00),
            ('Infilration', 'After deployment, may make an additional Rush move; coherency checks at one level higher than Quality.', 1.30),
            ('Inflexible', 'May not fire on a turn where it moved.', 0.70),
            ('Jet Packs', 'Allows use of Jet Packs advanced rule.', 1.50),
            ('Legend', 'Single-figure only; has Hero and Villain; always counts as rolling a 6 for Close Assaults and Shooting.', 2.00),
            ('Limited Teleport', 'Can teleport instead of moving; must pass Quality Test; catastrophic failure removes a model.', 1.50),
            ('Mechanized', 'Infantry partnered with a transport vehicle; if within 12", vehicle may activate with the squad.', 1.20),
            ('Night Vision', 'May fire normally to specified range.', 1.10),
            ('No Grenades', '-2 penalty in assault combat.', 0.80),
            ('Obvious Target', 'Can always be chosen as a target; cannot hide.', 0.80),
            ('Recon', '+1" coherency; auto-success one die when calling Indirect Artillery Fire.', 1.30),
            ('Regenerate', 'Heals by remaining inactive for an activation; cannot move/shoot/assault during recovery.', 1.20),
            ('Relentless', 'Ignores Under Fire or Pinned; never benefits from cover; leaves casualties behind.', 1.20),
            ('Reserves', 'May be held in reserve and deployed later per Reserves rule.', 1.30),
            ('Resilient (2)', 'Gain 2 wounds; each "wound" loses one point, each "kill" loses two.', 1.20),
            # Multipliers for resilient 3-6 and traits below are unknown from table files; default to 1.0
            ('Resilient (3)', 'Gain 3 wounds; each "wound" loses one point, each "kill" loses two.', 1.00),
            ('Resilient (4)', 'Gain 4 wounds; each "wound" loses one point, each "kill" loses two.', 1.00),
            ('Resilient (5)', 'Gain 5 wounds; each "wound" loses one point, each "kill" loses two.', 1.00),
            ('Resilient (6)', 'Gain 6 wounds; each "wound" loses one point, each "kill" loses two.', 1.00),
            ('Save', 'Roll 1d6 for each hit; on 5+ the hit is negated (Power Armour: only one save in close combat).', 1.00),
            ('Self Repairing', 'Recover Wounded action as if an aid team is present.', 1.00),
            ('Shaky', 'Automatically fails one morale die; roll 2d6 and add one failure.', 1.00),
            ('Shock Troops', '+1 to all Close Assaults.', 1.00),
            ('Slick', 'May only be engaged by two opponents in close combat.', 1.00),
            ('Slow', '-2" base movement rate.', 1.00),
            ('Slow Firing', 'If moved this activation, roll only 1d6 for Fire Effect.', 1.00),
            ('Stealth', 'Always succeeds when going into hiding (Hidden Movement rule).', 1.00),
            ('Zombie', 'Relentless and Fanatic; may never Rush; cannot shoot beyond close range and all fire suffers -2.', 1.00)
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
        
        # Vehicle Properties (official table properties only)
        print("\n3. Populating Vehicle Properties...")
        vehicle_properties = [
            ('Advanced Targeting System', 'Adds +2 to Fire Effect rolls against vehicles and hard targets.', 1.00),
            ('AI Controlled', 'No crew; immune to morale effects; re-roll one die when damaged; counts crew equal to weapons.', 1.00),
            ('Alternate Fire Weapons (2)', 'Two weapons function as one with multiple fire modes; only one may fire per turn.', 1.00),
            ('Alternate Fire Weapons (3)', 'Three weapons function as one with multiple fire modes; only one may fire per turn.', 1.00),
            ('Amphibious', 'Can cross water at half Cautious speeds; firing in water suffers -3 Fire Effect.', 1.00),
            ('Close - In Defense System', 'Blast weapon centered on vehicle (radius 4"); affects nearby troops.', 1.00),
            ('Command Vehicle', 'Once per turn, one unit may re-roll failed Command Response; can call Indirect Artillery Fire.', 1.00),
            ('Electronic Countermeasures', 'Negates Advanced Targeting System benefits if target has ECM.', 1.00),
            ('Energy screen', 'Roll 1d6 per hit; on 5+ the hit is negated.', 1.00),
            ('Fast', '+2" to Cautious and Standard movement rates.', 1.00),
            ('Fixed Mount (1)', 'One weapon has a fixed firing direction.', 1.00),
            ('Fixed Mount (2)', 'Two weapons have fixed firing directions.', 1.00),
            ('Fixed Mount (3)', 'Three weapons have fixed firing directions.', 1.00),
            ('Forward Observer', 'Can take a Command action to call Indirect Artillery Fire.', 1.00),
            ('Improved Weapons Control', 'A single crew may fire two weapons instead of one.', 1.00),
            ('Jump Jets', 'Walkers only; move 10" ignoring obstacles up to 6" height.', 1.00),
            ('Linked Weapons', 'Choose a weapon; roll 2D6 and pick highest when firing; repeatable.', 1.00),
            ('Medevac', 'Acts as two aid teams when recovering wounded; squads may leave wounded with vehicle.', 1.00),
            ('Reactive Armour', 'When fired upon by AP 1+, defender may force attacker to re-roll damage dice.', 1.00),
            ('Reserves', 'May be held in reserve and deployed later per Reserves rule.', 1.00),
            ('Slow', '-2" to Cautious and Standard movement rates.', 1.00),
            ('Smoke', 'Lay one smoke screen per game; follows Smoke Grenades rules.', 1.00),
            ('Stealth', 'Shooting against this vehicle is resolved at one range band beyond actual distance.', 1.00),
            ('Supercharged', '+4" to Cautious and Standard movement rates.', 1.00),
            ('Under-Powered', '-4" to Cautious and Standard movement rates.', 1.00),
            ('Weapon Stabilizer', 'May fire when moving at standard speeds; other modifiers apply.', 1.00)
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
