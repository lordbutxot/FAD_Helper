#!/usr/bin/env python
"""
List all users in database
"""
from app import app, db
from models import User

app.app_context().push()

users = User.query.all()
print(f"Total users: {len(users)}\n")
for u in users:
    print(f"  {u.username} - Admin: {u.is_admin}")
