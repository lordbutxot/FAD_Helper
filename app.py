"""
F.A.D. (Fast and Dirty) List Builder Web Application
A web-based army list builder for the F.A.D. wargame
"""

from flask import Flask
from extensions import db, login_manager
import os
import secrets

# Initialize Flask app
app = Flask(__name__)

# Load configuration
from config import config
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Fallback for development: use secret key file if no environment variable
if config_name == 'development' and not os.environ.get('SECRET_KEY'):
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

# Initialize extensions with app
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'  # type: ignore

# Register markdown filter for templates
from extensions import markdown_to_html
app.jinja_env.filters['markdown'] = markdown_to_html

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
