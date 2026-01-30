#!/usr/bin/env python
"""
Delete test users from database
"""
from app import app, db
from models import User

app.app_context().push()

users_to_delete = ['testuser', 'newuser']

for username in users_to_delete:
    user = User.query.filter_by(username=username).first()
    if user:
        db.session.delete(user)
        print(f"✅ Deleted {username}")
    else:
        print(f"❌ {username} not found")

db.session.commit()
print("\nDone!")
