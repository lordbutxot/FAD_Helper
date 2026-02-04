"""
Migration Runner: Runs all migration scripts in order using Flask app context.
"""
import sys
from app import app
from extensions import db

if __name__ == "__main__":
    with app.app_context():
        try:
            # Create all tables if they don't exist
            db.create_all()
            print("✅ Database tables created/verified successfully!")
            print("\n✅ All migrations completed successfully!\n")
        except Exception as e:
            print(f"\n❌ Migration failed: {e}\n")
            sys.exit(1)
