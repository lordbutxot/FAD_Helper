#!/usr/bin/env python3
"""
Simple database initialization script for Render
Creates all SQLAlchemy tables in the database
"""
import sys
import os

# Add the project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db
    
    print("=" * 60)
    print("Initializing Supabase Database Tables...")
    print("=" * 60)
    
    with app.app_context():
        print("\n📦 Creating all database tables...")
        db.create_all()
        print("✅ Database tables created successfully!")
        
    print("\n" + "=" * 60)
    print("✨ Database initialization complete!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
