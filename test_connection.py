"""Test Supabase database connection"""
import os
from app import app, db
from models import User

def test_connection():
    """Test if we can connect to Supabase"""
    with app.app_context():
        try:
            # Test connection
            db.engine.connect()
            print("✅ Connected to database successfully!")
            print(f"   Database URI: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
            
            # Check if tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"\n✅ Found {len(tables)} tables: {tables}")
            
            # Count users
            user_count = User.query.count()
            print(f"\n✅ Total users in database: {user_count}")
            
            if user_count > 0:
                print("\nUsers:")
                for user in User.query.all():
                    print(f"  - {user.username} (ID: {user.id}, Admin: {user.is_admin})")
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_connection()
