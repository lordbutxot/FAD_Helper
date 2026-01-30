"""
F.A.D. (Fast and Dirty) List Builder Web Application
A web-based army list builder for the F.A.D. wargame
"""

from flask import Flask
from extensions import db, login_manager

# Initialize Flask app
app = Flask(__name__)

# Security Configuration
import secrets
import os

# Generate secure secret key if not set in environment
# IMPORTANT: In production, set SECRET_KEY environment variable
# For development, we'll use a consistent key stored in a file
secret_key_file = 'instance/secret_key.txt'
if os.path.exists(secret_key_file):
    with open(secret_key_file, 'r') as f:
        app.config['SECRET_KEY'] = f.read().strip()
else:
    # Create instance directory if it doesn't exist
    os.makedirs('instance', exist_ok=True)
    # Generate and save a new secret key
    new_key = secrets.token_hex(32)
    with open(secret_key_file, 'w') as f:
        f.write(new_key)
    app.config['SECRET_KEY'] = new_key

# Session security
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True when using HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = None  # Changed from 'Lax' to None for VS Code compatibility
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fad_lists.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# WTF CSRF Protection
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = None  # No time limit for CSRF tokens

# Initialize extensions with app
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'  # type: ignore

# Now import models and routes (after db is initialized)
from models import User, ArmyList, Unit, Weapon, Armour, Trait
from routes import init_routes

# Register all routes
init_routes(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
