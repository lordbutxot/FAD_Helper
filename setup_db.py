"""
Complete database setup - Run this once to initialize everything
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from models import Weapon, Armour, Trait, User
from werkzeug.security import generate_password_hash

def setup_database():
    with app.app_context():
        print("=" * 60)
        print("F.A.D. List Builder - Complete Database Setup")
        print("=" * 60)
        
        # Delete existing database
        db_path = 'fad_lists.db'
        if os.path.exists(db_path):
            os.remove(db_path)
            print("✓ Removed old database")
        
        # Create all tables
        db.create_all()
        print("✓ Created fresh database schema")
        
        # Initialize weapons
        print("\nAdding game data...")
        from init_db import init_weapons, init_armour, init_traits
        init_weapons()
        init_armour()
        init_traits()
        
        # Create admin user
        print("\nCreating admin user...")
        admin = User(
            username='admin',
            email=None,
            password_hash=generate_password_hash('Admin123', method='pbkdf2:sha256', salt_length=16),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        
        print("\n" + "=" * 60)
        print("✓ Database setup complete!")
        print("=" * 60)
        print("\nAdmin Account Created:")
        print("  Username: admin")
        print("  Password: Admin123")
        print("\nYou can now:")
        print("  1. Start the app: python app.py")
        print("  2. Login at: http://127.0.0.1:5000/login")
        print("  3. Access admin panel at: http://127.0.0.1:5000/admin")
        print("=" * 60)

if __name__ == '__main__':
    setup_database()
