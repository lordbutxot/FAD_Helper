"""
Remove non-official traits from the database, keeping only traits listed in the official table files.
Safe: Only deletes traits outside the approved lists.
"""

from app import app, db
from models import Trait

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


def clean_non_official_traits():
    allowed = set(OFFICIAL_INFANTRY_TRAITS + OFFICIAL_VEHICLE_TRAITS)

    with app.app_context():
        all_traits = Trait.query.all()
        to_delete = [t for t in all_traits if t.name not in allowed]

        if not to_delete:
            print("✅ No non-official traits found. Nothing to delete.")
            return

        print(f"⚠️  Removing {len(to_delete)} non-official traits...")
        for trait in to_delete:
            print(f"   - Deleting: {trait.name} ({trait.category or 'Uncategorized'})")
            db.session.delete(trait)

        db.session.commit()
        print("✅ Cleanup complete.")


if __name__ == "__main__":
    clean_non_official_traits()
