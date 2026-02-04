"""
Initialize F.A.D. game data into the database
Run this script once to populate weapons, armour, and traits
"""

from app import app
from extensions import db
# Import ALL models to ensure tables are created
from models import Weapon, Armour, Trait, User, Unit, ArmyList
import json


def init_weapons():
    """Initialize all weapons from the armoury"""
    
    # Clear existing weapons
    Weapon.query.delete()
    
    # Basic Weapons
    basic_weapons = [
        ("None", "Basic", 0, 0, 0, 0, None, 0.00),
        ("Pistol", "Basic", 1, 1, 0, 0, json.dumps({"close_assault_bonus": 1}), 0.25),
        ("SMG", "Basic", 2, 2, 0, 0, json.dumps({"close_assault_bonus": 1}), 0.50),
        ("Assault Carbine", "Basic", 4, 2, 0, 0, None, 0.75),
        ("Low-Tech Rifle", "Basic", 5, 1, 0, 0, None, 0.75),
        ("Assault Rifle", "Basic", 5, 2, 0, 0, None, 1.00),
        ("High Tech Rifle", "Basic", 6, 2, 0, 0, None, 1.25),
        ("Gauss Pistol", "Basic", 3, 3, 0, 0, json.dumps({"close_assault_bonus": 1}), 1.50),
        ("Laser Rifle", "Basic", 7, 2, 0, 0, None, 1.50),
        ("Gauss Carbine", "Basic", 5, 3, 0, 0, None, 1.75),
        ("Blaster Pistol", "Basic", 1, 4, 0, 0, json.dumps({"close_assault_bonus": 1}), 2.00),
        ("Assault Rifle (linked)", "Basic", 5, 2, 0, 0, json.dumps({"double_troops_fe": True, "vehicle_pa_only": True}), 2.00),
        ("Blaster", "Basic", 3, 4, 0, 0, None, 2.00),
        ("Gauss Rifle", "Basic", 6, 3, 0, 0, None, 2.00),
        ("High Tech Rifle (linked)", "Basic", 6, 2, 0, 0, json.dumps({"double_troops_fe": True, "vehicle_pa_only": True}), 2.25),
        ("Laser Rifle (linked)", "Basic", 7, 2, 0, 0, json.dumps({"double_troops_fe": True, "vehicle_pa_only": True}), 2.50),
        ("Gauss Carbine (linked)", "Basic", 5, 3, 0, 0, json.dumps({"double_troops_fe": True, "vehicle_pa_only": True}), 2.75),
        ("Gauss Rifle (linked)", "Basic", 6, 3, 0, 0, json.dumps({"double_troops_fe": True, "vehicle_pa_only": True}), 3.00),
    ]
    
    # Support Weapons
    support_weapons = [
        ("Shotgun", "Support", 2, 2, 2, 0, json.dumps({"close_assault_bonus": 1}), 1.00),
        ("Flamethrower", "Support", 1, 2, 0, 2, json.dumps({"fe_bonus_dice": 1, "close_assault_bonus": 1}), 3.00),
        ("Grenade Launcher", "Support", 2, 2, 0, 1, json.dumps({"fe_bonus_dice": 1}), 3.00),
        ("SAW", "Support", 6, 2, 2, 0, None, 3.00),
        ("Fusion Gun", "Support", 2, 2, 0, 3, None, 3.00),
        ("Plasma Rifle", "Support", 5, 2, 1, 1, None, 4.00),
        ("SAW (Linked)", "Support", 6, 2, 2, 0, json.dumps({"double_troops_fe": True, "vehicle_pa_only": True}), 4.00),
        ("Beam Rifle", "Support", 7, 2, 0, 1, None, 5.00),
        ("Plasma Rifle (Linked)", "Support", 5, 2, 1, 1, json.dumps({"double_troops_fe": True, "vehicle_pa_only": True}), 5.00),
        ("Missile Launcher (Power Armour)", "Support", 5, 3, 0, 1, json.dumps({"fe_bonus_dice": 1, "power_armour_only": True}), 6.00),
    ]
    
    # Heavy Weapons
    heavy_weapons = [
        ("General Purpose MG", "Heavy", 7, 3, 3, 0, None, 5.00),
        ("Sniper Rifle", "Heavy", 10, 3, 0, 0, None, 5.00),
        ("Heavy MG", "Heavy", 8, 4, 2, 0, None, 6.00),
        ("Mounted Flamethrower", "Heavy", 3, 2, 0, 2, json.dumps({"fe_bonus_dice": 1, "close_assault_bonus": 1}), 6.00),
        ("Chain Gun - Light", "Heavy", 4, 2, 5, 0, None, 8.00),
        ("Beam - Light", "Heavy", 15, 2, 0, 1, None, 10.00),
        ("Cannon - Light", "Heavy", 10, 3, 0, 0, json.dumps({"blast": 3}), 10.00),
        ("Chain Gun - Heavy", "Heavy", 7, 2, 7, 0, None, 10.00),
        ("Missile Launcher", "Heavy", 8, 2, 1, 3, json.dumps({"modes": ["HE: Blast 3, 0 AP", "AP: Blast 0, 3 AP"]}), 10.00),
        ("Mortar - Light", "Heavy", 10, 2, 1, 0, json.dumps({"blast": 3, "no_los": True}), 10.00),
        ("Auto Cannon - Light", "Heavy", 10, 5, 1, 0, None, 10.00),
        ("Beam - Heavy", "Heavy", 20, 2, 0, 3, None, 16.00),
        ("Cannon - Medium", "Heavy", 12, 3, 1, 1, json.dumps({"auto_pin_infantry": True, "blast": 4}), 16.00),
        ("Auto Cannon - Heavy", "Heavy", 13, 6, 1, 0, None, 16.00),
        ("Mortar - Heavy", "Heavy", 12, 2, 1, 0, json.dumps({"auto_pin": True, "blast": 3, "no_los": True}), 16.00),
        ("Rail Gun - Light", "Heavy", 12, 4, 0, 1, None, 20.00),
        ("Cannon - Heavy", "Heavy", 15, 3, 3, 2, json.dumps({"auto_pin_infantry": True, "blast": 5}), 22.00),
        ("Rail Gun - Heavy", "Heavy", 15, 4, 0, 3, None, 30.00),
    ]
    
    # Add all weapons to database
    for weapon_data in basic_weapons + support_weapons + heavy_weapons:
        weapon = Weapon(  # type: ignore
            name=weapon_data[0],
            category=weapon_data[1],
            range_multiplier=weapon_data[2],
            damage=weapon_data[3],
            fire_effect=weapon_data[4],
            armor_piercing=weapon_data[5],
            special_rules=weapon_data[6],
            points=weapon_data[7]
        )
        db.session.add(weapon)
    
    db.session.commit()
    print(f"✓ Added {len(basic_weapons + support_weapons + heavy_weapons)} weapons")


def init_armour():
    """Initialize all armour types"""
    
    # Clear existing armour
    Armour.query.delete()
    
    armour_types = [
        ("None", 3, None, -1.00),
        ("Light", 4, None, 0.00),
        ("Improved", 5, None, 1.00),
        ("Heavy", 6, None, 2.00),
        ("Battle Dress", 7, None, 3.00),
        ("Lt. Power", 7, None, 6.00),
        ("Medium Power", 8, None, 8.00),
        ("Hvy. Power", 9, None, 10.00),
    ]
    
    for armour_data in armour_types:
        armour = Armour(  # type: ignore
            name=armour_data[0],
            rating=armour_data[1],
            special_rules=armour_data[2],
            points=armour_data[3]
        )
        db.session.add(armour)
    
    db.session.commit()
    print(f"✓ Added {len(armour_types)} armour types")


def init_traits():
    """Initialize all traits"""
    
    # Clear existing traits
    Trait.query.delete()
    
    traits_data = [
        ("Adaptive Camouflage", "This unit is equipped with an outfit (or armour) that disrupts the appearance of the unit. If the unit moved this turn and is fired at then resolve the shooting as if the unit is one range band further away. If the unit did not move, it cannot be shot at beyond long range.", 1.30, "Infantry"),
        ("Aerial", "Units with this trait hover in the air while moving, and can clear any obstacles up to the height of the aerial figure. These troops land after they move and will incur any benefits or penalties the terrain may provide.", 1.30, "Infantry"),
        ("Aggressive", "When an aggressive unit marked as Under Fire is activated, if it chooses to move it must be towards the enemy. Any Command Response limitations are ignored.", 1.10, "Infantry"),
        ("Agile", "Agile units ignore movement penalties when crossing Difficult Terrain.", 1.20, "Infantry"),
        ("Assault Troops", "+2 to all Close Assaults.", 1.30, "Infantry"),
        ("Berserk", "A squad with this trait will ignore the effects of being Under Fire or Pinned if they activate within close assault range of an enemy unit. However they must charge into hand-to-hand combat with the nearest enemy unit, and receive a +2 to their Close Assault.", 1.30, "Infantry"),
        ("Bestow Trait", "If this character joins a squad, he may bestow one predefined trait upon them.", 1.40, "Character"),
        ("Brave", "This unit automatically succeeds on one of their dice when testing morale. Roll one less die than required and add one success to the result.", 1.50, "Infantry"),
        ("Bug Hunter", "Units with this trait are specially trained to fight alien species. When fighting an alien race, this squad receives a bonus of +1 to Close Assault and Fire Effect rolls.", 1.20, "Infantry"),
        ("Cautious", "The unit must test Quality to leave cover if it is currently Under Fire", 0.90, "Infantry"),
        ("Combat Drugs", "A unit equipped with this item may use it upon activation (once per game). They temporarily gain the Berserk, Fearless and Swift traits. They must charge into hand-to-hand combat with the nearest enemy unit. At the end of their activation roll 1d6 for each survivor. A result of 6 indicates the trooper is wounded by the powerful drugs.", 1.20, "Infantry"),
        ("Dependant", "When led by officer this squad will automatically pass one of it's command response dice. If not it automatically fails on one of it's command response dice.", 1.00, "Infantry"),
        ("Detection", "Every time this unit is activated, all hidden markers within 12\" must be removed or revealed.", 1.10, "Infantry"),
        ("Disruptive Charge", "When this unit charges into close combat it sends it's opponent into disarray. Because of this the opponent suffers a -2 penalty to fire effect on their free attack when receiving a charge from this unit.", 1.20, "Infantry"),
        ("Droids (self-less)", "Not subject to normal psychology. Do not take morale checks. May never be Elite. Gain the Relentless trait for no additional points. Save against wounds on draws. Die instead of being wounded.", 1.60, "Infantry"),
        ("Droids (self-preserving)", "Not subject to normal psychology. Do not take morale checks. May never be Elite. Save against wounds on draws. Die instead of being wounded.", 1.30, "Infantry"),
        ("Drop Troop", "This unit has special training and equipment that allow it to be deployed after a battle has started. Adding this trait to a unit allows it to use the Drop Troops advanced rule.", 1.30, "Infantry"),
        ("Elusive", "Once per turn, when an elusive unit is fired upon, they may fall back 4\" before shooting is resolved. Measure range and calculate terrain benefits from their new location. If Line of Sight is lost, the shooting unit is free to select another target.", 1.40, "Infantry"),
        ("Engineer", "Engineers automatically succeed on one of their dice when attempting to rig or detonate demolition charges. Roll one less die than allowed, and add one success to the result. In addition, units with the engineer trait add +2 to their die roll when encountering minefields.", 1.20, "Infantry"),
        ("Fanatic", "These units never need to Check Resolve, but they must have a Resolve of 'Steady'", 1.60, "Infantry"),
        ("Fast", "+2\" base movement rate.", 1.20, "Infantry"),
        ("Fearless", "Ignores any Morale Tests caused by Terrifying units or psionic Terror.", 1.10, "Infantry"),
        ("Fire Team", "This unit can be split into two independent squads that act separately of each other but must still stay within close proximity of their partner fireteam. Adding this trait to a unit allows it to use the 'Fire Teams' advanced rule.", 1.20, "Infantry"),
        ("Flyer", "Units with this trait are considered airborne at all times. They may move over any obstacles and never receive any benefit from terrain.", 1.20, "Infantry"),
        ("Frail", "This unit suffers -1 to Armour.", 0.90, "Infantry"),
        ("Frenzied", "Each frenzied model receives 1 additional kill roll in assault combat. This is cumulative with any other additional rolls obtained.", 1.30, "Infantry"),
        ("Goon", "Goons may not fire beyond close range, except to return fire, and suffer a -1 penalty to all Fire Effect rolls. Their Armour Rating suffers a -1 penalty as well. They may never Rush.", 0.70, "Infantry"),
        ("Grav Mount", "A grav mount allows for heavy weapons to be moved more easily and will also dampen recoil when fired. The mount may move at the same speed as it's crew, is unhindered by terrain but may not perform rush moves. The crew must remain within normal coherency distance of the mount to operate it and when mounting a 'light' or 'medium' version of any heavy weapon, the mount may move and fire its armament.", 1.40, "Infantry"),
        ("Grizzled", "Squads with this trait Check Resolve at one level higher than their Quality level.", 1.20, "Infantry"),
        ("Gung Ho", "May ignore 'under fire' any turn they close assault", 1.10, "Infantry"),
        ("Hardened", "These troops ignore being Under Fire until they suffer their first casualty, and may always leave wounded behind.", 1.10, "Infantry"),
        ("Hero", "This trait may only be taken by a Character or Psionic. Heroes always Shoot individually, even when attached to another unit. When firing at close range, they may choose the target figure. They are also Fearless, Shock Troops. Non-heroes suffer a -2 penalty to Fire Effect when firing at a Hero.", 1.50, "Character"),
        ("Hesitant", "Unless activating within 15\" of enemy troops, make a Quality test to activate. If the test fails move towards cover or stand still (if none is close enough).", 0.80, "Infantry"),
        ("Hive mind (controller)", "This unit controls other members of a hive mind but is also Fanatic and Relentless.", 1.50, "Infantry"),
        ("Hive Mind (unit)", "Units with this Trait are Fanatic and Relentless when they activate within 12\" of one of a mind controllers. This controller can be another squad or an independent figure with the Hive Mind (controller) trait. If the unit is beyond 12\" of the controller, it must pass a Quality Test on 2 or more dice, or it cannot activate this turn.", 1.20, "Infantry"),
        ("HQ", "This trait may only be applied to a single figure. Once per turn, any one unit may reroll a failed Command Response test.", 1.20, "Character"),
        ("Huge", "Huge units can be squads, Characters or Psionics and may be equipped with heavy weapons and fire them while moving, but suffer a -2 penalty to fire effect. In close assault, a huge model rolls 4 kill rolls. If the opposing unit fails to destroy the huge model, it must fall back, even if it won the assault. Furthermore, while being shot at by any weapons without an AP score, a huge model must receive at least two hits in the same volley of fire to be wounded. Huge models do not receive any benefits of cover.", 1.50, "Infantry"),
        ("Ignore Pain", "The model may continue to move and fight if wounded. Each activation make a Quality Test, is all dice pass it can continue to fight, otherwise it is removed as a casualty", 1.20, "Infantry"),
        ("Infect", "When a figure is killed in Close Assault by a unit with this trait roll 1d6, on 5+ the figure is infected.", 1.00, "Infantry"),
        ("Infiltration", "After initial deployment, this squad may make an additional Rush move before the game starts. In addition, they check Coherency at one level higher than their Quality level.", 1.30, "Infantry"),
        ("Inflexible", "The unit may not fire on a turn where it moved.", 0.70, "Infantry"),
        ("Jet Packs", "This unit is equipped with some form of device that allows far greater movement than regular infantry. Adding this trait allows the unit to use the 'Jet Packs' advanced rule.", 1.50, "Infantry"),
        ("Legend", "This trait may only be applied to a single figure. Legends have both Hero and Villain traits. Legends always count as rolling a 6 for Close Assaults and Shooting.", 2.00, "Character"),
        ("Limited Teleport", "Whenever the unit would normally move, it can instead teleport the same distance, ignoring terrain and other units/vehicles etc. Teleportation can be a risky business and a unit that teleports must make a Quality Test, determining success in the same way as Drop Troops.", 1.50, "Infantry"),
    ]
    
    for trait_data in traits_data:
        trait = Trait(  # type: ignore
            name=trait_data[0],
            description=trait_data[1],
            points_multiplier=trait_data[2],
            category=trait_data[3]
        )
        db.session.add(trait)
    
    db.session.commit()
    print(f"✓ Added {len(traits_data)} traits")


def initialize_all():
    """Initialize all game data"""
    print("Initializing F.A.D. game data...")
    print("-" * 50)
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Initialize data
        init_weapons()
        init_armour()
        init_traits()
        
        print("-" * 50)
        print("✓ Database initialization complete!")
        print("\nYou can now run the app with: python app.py")


if __name__ == '__main__':
    initialize_all()
