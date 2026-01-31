"""
Migration Runner: Runs all migration scripts in order using Flask app context.
"""
import sys
from app import app

# Import migration functions from each script
from migrate_trait_constraint import migrate_trait_constraint
from migrate_add_unit_parent import upgrade as migrate_add_unit_parent
from migrate_squad_members import migrate_database
from migrate_add_description import migrate_add_description

if __name__ == "__main__":
    with app.app_context():
        try:
            migrate_trait_constraint()
            migrate_add_unit_parent()
            migrate_database()
            migrate_add_description()
            print("\n✅ All migrations completed successfully!\n")
        except Exception as e:
            print(f"\n❌ Migration failed: {e}\n")
            sys.exit(1)
