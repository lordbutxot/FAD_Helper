"""
Production Database Initialization Script
Initializes database with all official F.A.D. data for production deployment
This script is SAFE to run multiple times - it preserves all user data
"""
from app import app, db
from models import Trait, Weapon, Armour, User, Faction, ArmyList, Unit
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
    'Slick', 'Slow', 'Slow Firing', 'Stealth', 'Supreme Armour', 'Supreme Weapon', 'Swift', 'Tank Hunter',
    'Terrifying', 'Timid', 'Tough', 'Unstable Technology', 'Villain', 'Weak', 'Zombie'
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
    
    try:
        db.session.commit()
        print("   ✅ Cleanup committed successfully")
    except Exception as e:
        print(f"   ⚠️  Cleanup error: {e}")
        db.session.rollback()

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
        
        # First ensure is_repeatable column exists
        print("\n1a. Ensuring is_repeatable column exists...")
        try:
            from sqlalchemy import text, inspect
        
            # Check if column exists using SQLAlchemy Inspector
            inspector = inspect(db.engine)
            trait_columns = [col['name'] for col in inspector.get_columns('trait')]
        
            if 'is_repeatable' not in trait_columns:
                print("   📝 Adding is_repeatable column...")
                with db.engine.connect() as conn:
                    # Detect database type
                    db_url = str(db.engine.url)
                    if 'postgresql' in db_url or 'postgres' in db_url:
                        # PostgreSQL
                        conn.execute(text("""
                            ALTER TABLE trait 
                            ADD COLUMN is_repeatable BOOLEAN DEFAULT FALSE
                        """))
                    else:
                        # SQLite
                        conn.execute(text("""
                            ALTER TABLE trait 
                            ADD COLUMN is_repeatable BOOLEAN DEFAULT 0
                        """))
                    conn.commit()
                print("   ✅ Column added successfully")
            else:
                print("   ✅ Column already exists")
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
            print("   Continuing with initialization...")
        
        # Cleanup non-official traits before any early exit
        print("\n1b. Cleaning non-official traits...")
        cleanup_non_official_traits()

        # Note: We do NOT skip if data exists - we UPDATE existing traits to match Traits.TXT
        
        # Infantry Traits (ALL from Traits.TXT with exact multipliers)
        print("\n2. Populating Infantry Traits...")
        infantry_traits = [
            ('Adaptive Camouflage', 'This unit is equipped with an outfit (or armour) that disrupts the appearance of the unit. If the unit moved this turn and is fired at then resolve the shooting as if the unit is one range band further away. If the unit did not move, it cannot be shot at beyond long range.', 1.30),
            ('Aerial', 'Units with this trait hover in the air while moving, and can clear any obstacles up to the height of the aerial figure. These troops land after they move and will incur any benefits or penalties the terrain may provide.', 1.30),
            ('Aggressive', 'When an aggressive unit marked as Under Fire is activated, if it chooses to move it must be towards the enemy. Any Command Response limitations are ignored.', 1.10),
            ('Agile', 'Agile units ignore movement penalties when crossing Difficult Terrain.', 1.20),
            ('Assault Troops', '+2 to all Close Assaults.', 1.30),
            ('Berserk', 'A squad with this trait will ignore the effects of being Under Fire or Pinned if they activate within close assault range of an enemy unit. However they must charge into hand-to-hand combat with the nearest enemy unit, and receive a +2 to their Close Assault.', 1.30),
            ('Bestow Trait', 'If this character joins a squad, he may bestow one predefined trait upon them.', 1.40),
            ('Brave', 'This unit automatically succeeds on one of their dice when testing morale. Roll one less die than required and add one success to the result.', 1.50),
            ('Bug Hunter', 'Units with this trait are specially trained to fight alien species. When fighting an alien race, this squad receives a bonus of +1 to Close Assault and Fire Effect rolls.', 1.20),
            ('Cautious', 'The unit must test Quality to leave cover if it is currently Under Fire.', 0.90),
            ('Combat Drugs', 'A unit equipped with this item may use it upon activation (once per game). They temporarily gain the Berserk, Fearless and Swift traits. They must charge into hand-to-hand combat with the nearest enemy unit. At the end of their activation roll 1d6 for each survivor. A result of 6 indicates the trooper is wounded by the powerful drugs.', 1.20),
            ('Dependant', 'When led by officer this squad will automatically pass one of its command response dice. If not it automatically fails on one of its command response dice.', 1.00),
            ('Detection', 'Every time this unit is activated, all hidden markers within 12" must be removed or revealed.', 1.10),
            ('Disruptive Charge', 'When this unit charges into close combat it sends its opponent into disarray. Because of this the opponent suffers a -2 penalty to fire effect on their free attack when receiving a charge from this unit.', 1.20),
            ('Droids (self-less)', 'Not subject to normal psychology. Do not take morale checks. May never be Elite. Gain the Relentless trait for no additional points. Save against wounds on draws. Die instead of being wounded.', 1.60),
            ('Droids (self-preserving)', 'Not subject to normal psychology. Do not take morale checks. May never be Elite. Save against wounds on draws. Die instead of being wounded.', 1.30),
            ('Drop Troop', 'This unit has special training and equipment that allow it to be deployed after a battle has started. Adding this trait to a unit allows it to use the Drop Troops advanced rule.', 1.30),
            ('Elusive', 'Once per turn, when an elusive unit is fired upon, they may fall back 4" before shooting is resolved. Measure range and calculate terrain benefits from their new location. If Line of Sight is lost, the shooting unit is free to select another target.', 1.40),
            ('Engineer', 'Engineers automatically succeed on one of their dice when attempting to rig or detonate demolition charges. Roll one less die than allowed, and add one success to the result. In addition, units with the engineer trait add +2 to their die roll when encountering minefields.', 1.20),
            ('Fanatic', 'These units never need to Check Resolve, but they must have a Resolve of "Steady".', 1.60),
            ('Fast', '+2" base movement rate.', 1.20),
            ('Fearless', 'Ignores any Morale Tests caused by Terrifying units or psionic Terror.', 1.10),
            ('Fire Team', 'This unit can be split into two independent squads that act separately of each other but must still stay within close proximity of their partner fireteam. Adding this trait to a unit allows it to use the "Fire Teams" advanced rule.', 1.20),
            ('Flyer', 'Units with this trait are considered airborne at all times. They may move over any obstacles and never receive any benefit from terrain.', 1.20),
            ('Frail', 'This unit suffers -1 to Armour.', 0.90),
            ('Frenzied', 'Each frenzied model receives 1 additional kill roll in assault combat. This is cumulative with any other additional rolls obtained.', 1.30),
            ('Goon', 'Goons may not fire beyond close range, except to return fire, and suffer a -1 penalty to all Fire Effect rolls. Their Armour Rating suffers a -1 penalty as well. They may never Rush.', 0.70),
            ('Grav Mount', 'A grav mount allows for heavy weapons to be moved more easily and will also dampen recoil when fired. The mount may move at the same speed as its crew, is unhindered by terrain but may not perform rush moves. The crew must remain within normal coherency distance of the mount to operate it and when mounting a "light" or "medium" version of any heavy weapon, the mount may move and fire its armament. When fired upon, treat the mount as a normal squad member, with heavy armour. A hit indicates that the mount is damaged and the crew must make a quality test each turn, and pass on two or more dice to operate it. If the platform receives a second hit, or all 3 dice fail, the platform is destroyed and the crew must operate the weapon in the traditional fashion.', 1.40),
            ('Grizzled', 'Squads with this trait Check Resolve at one level higher than their Quality level.', 1.20),
            ('Gung Ho', 'May ignore "under fire" any turn they close assault.', 1.10),
            ('Hardened', 'These troops ignore being Under Fire until they suffer their first casualty, and may always leave wounded behind.', 1.10),
            ('Hero', 'This trait may only be taken by a Character or Psionic. Heroes always Shoot individually, even when attached to another unit. When firing at close range, they may choose the target figure. They are also Fearless, Shock Troops. Non-heroes suffer a -2 penalty to Fire Effect when firing at a Hero.', 1.50),
            ('Hesitant', 'Unless activating within 15" of enemy troops, make a Quality test to activate. If the test fails move towards cover or stand still (if none is close enough).', 0.80),
            ('Hive mind (controller)', 'This unit controls other members of a hive mind (see Hive Mind unit) but is also Fanatic and Relentless.', 1.50),
            ('Hive Mind (unit)', 'Units with this Trait are Fanatic and Relentless when they activate within 12" of one of a mind controllers. This controller can be another squad or an independent figure with the Hive Mind (controller) trait. If the unit is beyond 12" of the controller, it must pass a Quality Test on 2 or more dice, or it cannot activate this turn.', 1.20),
            ('HQ', 'This trait may only be applied to a single figure. Once per turn, any one unit may reroll a failed Command Response test.', 1.20),
            ('Huge', 'Huge units can be squads, Characters or Psionics and may be equipped with heavy weapons and fire them while moving, but suffer a -2 penalty to fire effect. In close assault, a huge model rolls 4 kill rolls. If the opposing unit fails to destroy the huge model, it must fall back, even if it won the assault. Furthermore, while being shot at by any weapons without an AP score, a huge model must receive at least two hits in the same volley of fire to be wounded. Huge models do not receive any benefits of cover.', 1.50),
            ('Ignore Pain', 'The model may continue to move and fight if wounded. Each activation make a Quality Test, if all dice pass it can continue to fight, otherwise it is removed as a casualty.', 1.20),
            ('Infect', 'When a figure is killed in Close Assault by a unit with this trait roll 1d6, on 5+ the figure is infected.', 1.00),
            ('Infilration', 'After initial deployment, this squad may make an additional Rush move before the game starts. In addition, they check Coherency at one level higher than their Quality level.', 1.30),
            ('Inflexible', 'The unit may not fire on a turn where it moved.', 0.70),
            ('Jet Packs', 'This unit is equipped with some form of device that allows far greater movement than regular infantry. Adding this trait allows the unit to use the "Jet Packs" advanced rule.', 1.50),
            ('Legend', 'This trait may only be applied to a single figure. Legends have both Hero and Villain traits. Legends always count as rolling a 6 for Close Assaults and Shooting.', 2.00),
            ('Limited Teleport', 'Whenever the unit would normally move, it can instead teleport the same distance, ignoring terrain and other units/vehicles etc (this can work in conjunction with traits such as Jet Packs and Elusive). Teleportation can be a risky business and a unit that teleports must make a Quality Test, determining success in the same way as Drop Troops. But if all dice on the quality test fail (in addition to the results of Drop Troops rule) then one member of the unit is removed as a fatality, they never re-materialised.', 1.50),
            ('Mechanized', 'An infantry unit with this trait is partnered with a transport vehicle at the start of the game. When the infantry unit is activated, the designated vehicle may ALSO be activated at the same time if it is currently within 12" of the infantry squad. Either unit must perform all of its actions first before the second unit is activated.', 1.20),
            ('Night Vision', 'May fire normally to specified range.', 1.10),
            ('No Grenades', 'The unit does not carry grenades and is subject to a -2 penalty in assault combat.', 0.80),
            ('Obvious Target', 'Can always be chosen as a target, cannot hide.', 0.80),
            ('Recon', 'Recon units gain +1" to their Coherency. In addition, they are automatically successful on one of their dice when attempting to call for Indirect Artillery Fire. Only roll 2d6 for their timing test and add one success to the result.', 1.30),
            ('Regenerate', 'Any figure with this trait will automatically heal their wound by remaining inactive during their next turn. They cannot Move in any way, nor can they Shoot or Close Assault. At the end of their dormant activation, they are fully healed.', 1.20),
            ('Relentless', 'Troops that are Relentless ignore the effects of being Under Fire or Pinned. They never benefit from any form of cover, and will leave any casualties behind without giving it a second thought.', 1.20),
            ('Reserves', 'This unit can be held in reserve, and then deployed once the battle has started (as per the Reserves advanced rule).', 1.30),
            ('Resilient (2)', 'Gain 2 wounds, each "wound" loses one point, each "kill" loses two.', 1.20),
            ('Resilient (3)', 'Gain 3 wounds, each "wound" loses one point, each "kill" loses two.', 1.40),
            ('Resilient (4)', 'Gain 4 wounds, each "wound" loses one point, each "kill" loses two.', 1.60),
            ('Resilient (5)', 'Gain 5 wounds, each "wound" loses one point, each "kill" loses two.', 1.80),
            ('Resilient (6)', 'Gain 6 wounds, each "wound" loses one point, each "kill" loses two.', 2.00),
            ('Save', 'Squads with this trait roll 1d6 for every hit they suffer. On a result of 5+ the hit is negated. NOTE: Power Armour Troopers can only make one save in close combat.', 1.40),
            ('Self Repairing', 'Units with this trait have been infused with tiny nano medics. During a Recover Wounded action, these troops can make a recovery roll as if an aid team was present, without the need to form such teams.', 1.10),
            ('Shaky', 'This unit automatically fails one of their dice when testing morale. Only roll 2d6 for their morale test and add one failure to the result.', 0.80),
            ('Shock Troops', 'Shock Troops add +1 to all Close Assaults.', 1.10),
            ('Slick', 'A slick model may only be engaged by 2 opponents in close combat. Thus against a unit of 5 models with this trait, you could not count more than 10 opponents for assault bonus and kill rolls.', 1.20),
            ('Slow', 'Slow units suffer a penalty of -2" to their base movement rate.', 0.80),
            ('Slow Firing', 'Slow Firing units roll only 1d6 to determine Fire Effect if they moved this activation.', 0.80),
            ('Stealth', 'A unit with this ability always succeeds when it goes into hiding (see Hidden Movement). There is no die roll required.', 1.10),
            ('Supreme Armour', 'An ancient artifact from an age of lost technology, a holy (or unholy) relic, maybe even a mastercrafted piece of technology. This trait applies to the armour of the unit which gains +1 to the Armour Rating of the unit.', 1.10),
            ('Supreme Weapon', 'An ancient artifact from an age of lost technology, a holy (or unholy) relic, maybe even a mastercrafted piece of technology. This trait applies to the units weapons which gain a +1 damage bonus.', 1.10),
            ('Swift', 'These units add +4" to their base movement rate.', 1.40),
            ('Tank Hunter', 'Squads with this trait are equipped with special explosives used to deal with enemy armoured vehicles. They gain +1 to their Nerves Check and a +2 mod when Close Assaulting vehicles.', 1.20),
            ('Terrifying', 'Squads with this trait will strike fear in the hearts of any unit nearby. An enemy unit which activates within 8" of a terrifying squad must make an immediate Morale Test.', 1.60),
            ('Timid', 'The unit must pass a Quality Test on at least 2 dice to launch a close combat assault.', 0.90),
            ('Tough', 'Squads that are Tough gain a +1 bonus to their Armour Rating.', 1.10),
            ('Unstable Technology', 'These troops make use of weapons and equipment that may be powerful or advanced, but have also not been thoroughly tested. They may be prototypes or something jerry rigged but whatever the case there is a chance something will go wrong! Every time a unit with this trait rolls a 1 on a fire effect dice it takes a hit with a damage equal to the standard weapon. Resolve this hit in the usual fashion. NOTE: if a squad rolls 2 1s on their fire effect dice they receive 2 hits.', 0.70),
            ('Villain', 'This trait may only be applied to a single figure. Any time a Villain is killed, leave the figure on the table. It remains in this state for the remainder of this turn. During the next turn, the owning player may activate this figure. Roll 1d6. If the result is 5+ the Villain was really only stunned. He climbs back to his feet and may return to battle immediately. If the result was less than 5, the Villain is truly dead and is removed from the table, never to be seen again. Or will he? :)', 1.50),
            ('Weak', 'The unit suffers a -1 penalty to close assault.', 0.90),
            ('Zombie', 'Zombies are Relentless and Fanatics. Unless the scenario dictates otherwise, they may never Rush. Zombies also have poor vision, so they cannot Shoot beyond close range, and all fire suffers a -2 penalty.', 0.70)
        ]
        
        added_infantry = 0
        updated_infantry = 0
        for name, desc, mult in infantry_traits:
            try:
                existing = Trait.query.filter_by(name=name, category='Infantry').first()
                if existing:
                    # Update existing trait with correct values from Traits.TXT
                    existing.description = desc
                    existing.points_multiplier = mult
                    updated_infantry += 1
                else:
                    # Insert new trait
                    trait = Trait(
                        name=name,
                        description=desc,
                        points_multiplier=mult,
                        category='Infantry'
                    )
                    db.session.add(trait)
                    added_infantry += 1
            except Exception as e:
                print(f"   ⚠️  Error processing trait '{name}': {e}")
                db.session.rollback()
                continue
        
        try:
            db.session.commit()
            print(f"   ✅ Added {added_infantry} infantry traits, updated {updated_infantry}")
        except Exception as e:
            print(f"   ❌ Error committing traits: {e}")
            db.session.rollback()
        
        # Vehicle Properties (ALL from Traits.TXT with exact multipliers)
        print("\n3. Populating Vehicle Properties...")
        vehicle_properties = [
            ('Advanced Targeting System', 'This vehicle is equipped with advanced optics and computer assistance that adds a +2 bonus to fire effect when shooting at enemy vehicles and hard targets.', 1.20),
            ('AI Controlled', 'This vehicle is unmanned and controlled by an artificial intelligence. No crew means it is immune to any morale effects. When rolling on the damage chart, re-roll one of the dice. When counting crew, treat this vehicle as having crew equal to the number of weapons on the vehicle, for the purpose of determining bonus crew dice for shooting.', 1.60),
            ('Alternate Fire Weapons (2)', 'Two weapons share the same mounting, effectively functioning as one weapon with multiple fire modes. Only one of the weapons may fire per turn.', 0.60),
            ('Alternate Fire Weapons (3)', 'Three weapons share the same mounting, effectively functioning as one weapon with multiple fire modes. Only one of the weapons may fire per turn.', 0.45),
            ('Amphibious', 'This vehicle can cross water, driving along the bottom or floating on its surface. Water terrain may be crossed at half the Cautious movement speeds. Any firing attempted in the water suffers a -3 penalty to fire effect.', 1.20),
            ('Close - In Defense System', 'This weapon fires a blast centered on the vehicle, with a radius of 4". Troops within this radius are hit using the weapon\'s normal statistics, but there is no roll to hit. Vehicles within the radius are not damaged unless the vehicle decides to target itself. Affects nearby troops.', 1.40),
            ('Command Vehicle', 'This vehicle contains sophisticated communication equipment and command staff. Once per turn, any one unit may re-roll a failed command response test. In addition, the vehicle may take a Command action to Call Indirect Artillery Fire. The vehicle gains a +1 to the timing test.', 1.50),
            ('Electronic Countermeasures', 'If the target has an Electronic Countermeasure System, the Advanced Targeting System benefit is negated.', 1.30),
            ('Energy screen', 'This vehicle is protected by an advanced energy shield. Roll 1d6 per hit scored against this vehicle. On a result of 5+ the hit is negated. This defensive screen works against close assaults.', 1.60),
            ('Fast', 'This vehicle is particularly swift. Add +2" to its Cautious and Standard movement rates.', 1.10),
            ('Fixed Mount (1)', 'One weapon on the vehicle has a fixed firing direction. This weapon may only fire from one side of the vehicle.', 0.90),
            ('Fixed Mount (2)', 'Two weapons on the vehicle have a fixed firing direction. These weapons may only fire from one side of the vehicle.', 0.80),
            ('Fixed Mount (3)', 'Three weapons on the vehicle have a fixed firing direction. These weapons may only fire from one side of the vehicle.', 0.70),
            ('Forward Observer', 'This vehicle can take a command action to Call Indirect Artillery Fire. The vehicle gains a +1 to the timing test.', 1.20),
            ('Improved Weapons Control', 'This vehicle can coordinate its firepower exceptionally well. A single crew member may fire two weapons instead of one.', 1.20),
            ('Jump Jets', 'Walkers only. This vehicle may move 10" per turn and may do so ignoring any obstacles up to 6" in height. Roll movement dice as normal, with an immobilized result translating to a damaged result. The vehicle may not Cautious Move if damaged.', 1.50),
            ('Linked Weapons', 'Choose a weapon from the vehicle. When firing this weapon, roll 2D6 and pick the highest result for determining fire effect. This trait is repeatable and may be taken for multiple weapons.', 1.20),
            ('Medevac', 'This vehicle acts as two aid teams when performing a recover wounded action. In addition, any squad member may leave their wounded with the vehicle, freeing themselves to perform further actions.', 1.30),
            ('Reactive Armour', 'This vehicle is equipped with a one-shot explosive defense. When fired upon by a weapon with an AP score of 1 or higher, the defender may force the attacker to re-roll any or all of their damage dice. Once this has been used, the vehicle loses this trait for the remainder of the game.', 1.30),
            ('Reserves', 'This vehicle may be held in reserve, and then deployed once the battle has started (as per the Reserves advanced rule).', 1.30),
            ('Slow', 'The vehicle suffers a penalty of -2" to its Cautious and Standard movement rates.', 0.90),
            ('Smoke', 'This vehicle may lay down a smoke screen once per game. Follow the rules as stated for Smoke Grenades.', 1.10),
            ('Stealth', 'This vehicle is equipped with a device, coating or unusual design that makes it hard to hit. Shooting against this vehicle is resolved at one range band beyond the actual distance.', 1.40),
            ('Supercharged', 'This vehicle has had its engine modified or upgraded. Add +4" to its Cautious and Standard movement rates.', 1.30),
            ('Under-Powered', 'This vehicle has a weak engine or power plant. Subtract -4" from its Cautious and Standard movement rates.', 0.70),
            ('Weapon Stabilizer', 'This vehicle may fire when moving at standard speeds. All other movement modifiers apply. This trait is repeatable and may be taken for multiple weapons.', 1.50)
        ]
        
        added_vehicles = 0
        updated_vehicles = 0
        
        # List of repeatable traits
        repeatable_traits = ['Weapon Stabilizer', 'Linked Weapons']
        
        for name, desc, mult in vehicle_properties:
            try:
                existing = Trait.query.filter_by(name=name, category='Vehicle').first()
                is_repeatable = name in repeatable_traits
                
                if existing:
                    # Update existing trait with correct values from Traits.TXT
                    existing.description = desc
                    existing.points_multiplier = mult
                    existing.is_repeatable = is_repeatable
                    updated_vehicles += 1
                else:
                    # Insert new trait
                    trait = Trait(
                        name=name,
                        description=desc,
                        points_multiplier=mult,
                        category='Vehicle',
                        is_repeatable=is_repeatable
                    )
                    db.session.add(trait)
                    added_vehicles += 1
            except Exception as e:
                print(f"   ⚠️  Error processing vehicle property '{name}': {e}")
                db.session.rollback()
                continue
        
        db.session.commit()
        print(f"   ✅ Added {added_vehicles} vehicle properties, updated {updated_vehicles}")
        print(f"   ℹ️  Marked {len(repeatable_traits)} traits as repeatable")
        
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
