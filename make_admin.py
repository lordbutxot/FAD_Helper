#!/usr/bin/env python
"""
Make a user admin - run locally or anywhere
Usage: DATABASE_URL="postgresql://..." python make_admin.py
"""
from app import app, db
from models import User

app.app_context().push()

username = 'Lord_Butxot'
user = User.query.filter_by(username=username).first()

if user:
    user.is_admin = True
    db.session.commit()
    print(f"✅ {username} is now admin")
else:
    print(f"❌ User '{username}' not found")
