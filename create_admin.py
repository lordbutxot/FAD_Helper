"""
Script to create an admin user or grant admin privileges to existing user
"""
from app import app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash

def create_admin():
    with app.app_context():
        print("=" * 50)
        print("F.A.D. List Builder - Admin Creation Tool")
        print("=" * 50)
        
        # Check if any admin exists
        existing_admin = User.query.filter_by(is_admin=True).first()
        if existing_admin:
            print(f"\n✓ Admin user already exists: {existing_admin.username}")
            choice = input("\nDo you want to:\n1. Create another admin\n2. Grant admin to existing user\n3. Exit\nChoice (1-3): ")
        else:
            print("\n⚠ No admin users found in database")
            choice = input("\nDo you want to:\n1. Create new admin user\n2. Grant admin to existing user\n3. Exit\nChoice (1-3): ")
        
        if choice == '1':
            # Create new admin
            print("\n--- Create New Admin User ---")
            username = input("Username: ").strip()
            
            if User.query.filter_by(username=username).first():
                print(f"✗ User '{username}' already exists!")
                return
            
            email = input("Email (optional, press Enter to skip): ").strip() or None
            password = input("Password: ")
            
            if len(password) < 8:
                print("✗ Password must be at least 8 characters!")
                return
            
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password, method='pbkdf2:sha256', salt_length=16),
                is_admin=True
            )
            
            db.session.add(user)
            db.session.commit()
            
            print(f"\n✓ Admin user '{username}' created successfully!")
            
        elif choice == '2':
            # Grant admin to existing user
            print("\n--- Grant Admin Privileges ---")
            
            # Show all users
            users = User.query.all()
            if not users:
                print("✗ No users found in database!")
                return
            
            print("\nExisting users:")
            for user in users:
                admin_badge = " [ADMIN]" if user.is_admin else ""
                print(f"  {user.id}. {user.username}{admin_badge}")
            
            user_id = input("\nEnter user ID to grant admin privileges: ").strip()
            
            try:
                user = User.query.get(int(user_id))
                if not user:
                    print(f"✗ User with ID {user_id} not found!")
                    return
                
                if user.is_admin:
                    print(f"⚠ User '{user.username}' is already an admin!")
                    return
                
                user.is_admin = True
                db.session.commit()
                
                print(f"\n✓ Admin privileges granted to '{user.username}'!")
                
            except ValueError:
                print("✗ Invalid user ID!")
                return
        else:
            print("\nExiting...")
            return
        
        print("\n" + "=" * 50)
        print("You can now log in with admin privileges at:")
        print("http://127.0.0.1:5000/admin")
        print("=" * 50)

if __name__ == '__main__':
    create_admin()
