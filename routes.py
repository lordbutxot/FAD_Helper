"""
Application routes for F.A.D. List Builder
"""

from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from extensions import db
from models import User, ArmyList, Unit, Weapon, Armour, Trait, Faction, FactionRating, SquadMember
from datetime import datetime, timedelta
from functools import wraps
import json
import re
import os
import uuid
from sqlalchemy import and_, or_


# File upload configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
UPLOAD_FOLDER = 'static/faction_logos'

# Predefined tactical playstyle tags
PLAYSTYLE_TAGS = {
    # Classic Warfare Tactics
    'combined_arms': {'name': 'Combined Arms', 'icon': 'diagram-3', 'description': 'Integrates infantry, armor, and support units effectively', 'category': 'warfare'},
    'artillery_superiority': {'name': 'Artillery Superiority', 'icon': 'crosshair', 'description': 'Overwhelming firepower and bombardment', 'category': 'warfare'},
    'air_superiority': {'name': 'Air Superiority', 'icon': 'airplane', 'description': 'Dominance through aerial units', 'category': 'warfare'},
    'armor_doctrine': {'name': 'Armor Doctrine', 'icon': 'truck', 'description': 'Heavy reliance on armored vehicles and tanks', 'category': 'warfare'},
    'infantry_swarm': {'name': 'Infantry Swarm', 'icon': 'people-fill', 'description': 'Overwhelming numbers of infantry units', 'category': 'warfare'},
    'elite_forces': {'name': 'Elite Forces', 'icon': 'star-fill', 'description': 'Quality over quantity with specialized troops', 'category': 'warfare'},
    'guerrilla_warfare': {'name': 'Guerrilla Warfare', 'icon': 'mask', 'description': 'Hit-and-run tactics and ambushes', 'category': 'warfare'},
    'defensive_warfare': {'name': 'Defensive Warfare', 'icon': 'shield-check', 'description': 'Fortifications and holding ground', 'category': 'warfare'},
    'rapid_assault': {'name': 'Rapid Assault', 'icon': 'lightning-fill', 'description': 'Speed and aggressive offensive tactics', 'category': 'warfare'},
    'siege_warfare': {'name': 'Siege Warfare', 'icon': 'hourglass-split', 'description': 'Attrition and sustained pressure', 'category': 'warfare'},
    'mechanized_warfare': {'name': 'Mechanized Warfare', 'icon': 'gear-fill', 'description': 'Mobile, vehicle-based forces', 'category': 'warfare'},
    'ranged_combat': {'name': 'Ranged Combat', 'icon': 'bullseye', 'description': 'Long-range engagement superiority', 'category': 'warfare'},
    'close_quarters': {'name': 'Close Quarters', 'icon': 'hand-index-thumb', 'description': 'Melee and short-range dominance', 'category': 'warfare'},
    'psychological_warfare': {'name': 'Psychological Warfare', 'icon': 'emoji-dizzy', 'description': 'Morale effects and fear tactics', 'category': 'warfare'},
    'stealth_operations': {'name': 'Stealth Operations', 'icon': 'eye-slash', 'description': 'Infiltration and covert tactics', 'category': 'warfare'},
    'attrition_warfare': {'name': 'Attrition Warfare', 'icon': 'arrow-repeat', 'description': 'Grinding down the enemy over time', 'category': 'warfare'},
    'blitzkrieg': {'name': 'Blitzkrieg', 'icon': 'arrow-right-circle-fill', 'description': 'Fast, overwhelming concentrated strikes', 'category': 'warfare'},
    'support_logistics': {'name': 'Support & Logistics', 'icon': 'boxes', 'description': 'Buffs, healing, and coordination', 'category': 'warfare'},
    'specialist_forces': {'name': 'Specialist Forces', 'icon': 'award', 'description': 'Unique abilities and specialized roles', 'category': 'warfare'},
    'naval_doctrine': {'name': 'Naval/Amphibious', 'icon': 'water', 'description': 'Water-based or amphibious operations', 'category': 'warfare'},
    
    # Sci-Fi & Advanced Warfare (Aligned with game mechanics)
    'psionic_dominance': {'name': 'Psionic Dominance', 'icon': 'stars', 'description': 'Psychic powers and mental warfare - Psionic units', 'category': 'scifi'},
    'elite_specialists': {'name': 'Elite Specialists', 'icon': 'award-fill', 'description': 'Character heroes and specialized individuals', 'category': 'scifi'},
    'sniper_doctrine': {'name': 'Sniper Doctrine', 'icon': 'crosshair2', 'description': 'Precision long-range eliminations - Sniper units', 'category': 'scifi'},
    'heavy_firepower': {'name': 'Heavy Firepower', 'icon': 'radioactive', 'description': 'Heavy weapons teams and devastating ordinance', 'category': 'scifi'},
    'mechanized_assault': {'name': 'Mechanized Assault', 'icon': 'robot', 'description': 'Walkers, hover vehicles, and advanced armor', 'category': 'scifi'},
    'adaptive_camouflage': {'name': 'Adaptive Camouflage', 'icon': 'eye-slash-fill', 'description': 'Advanced stealth and cloaking technology', 'category': 'scifi'},
    'aerial_superiority': {'name': 'Aerial Superiority', 'icon': 'airplane-engines', 'description': 'Flying and hovering vehicle dominance', 'category': 'scifi'},
    'energy_weapons': {'name': 'Energy Weapons', 'icon': 'lightning-charge-fill', 'description': 'Plasma, laser, and directed energy arms', 'category': 'scifi'},
    'combat_drugs': {'name': 'Combat Drugs', 'icon': 'prescription2', 'description': 'Chemical enhancement and stimulants', 'category': 'scifi'},
    'drone_warfare': {'name': 'Drone Warfare', 'icon': 'android2', 'description': 'Autonomous units and robotic forces', 'category': 'scifi'},
    'bestow_abilities': {'name': 'Bestow Abilities', 'icon': 'magic', 'description': 'Characters granting bonuses to nearby units', 'category': 'scifi'},
    'aggressive_advance': {'name': 'Aggressive Advance', 'icon': 'arrow-up-right-circle-fill', 'description': 'Berserk charges and fearless assaults', 'category': 'scifi'},
    'detection_systems': {'name': 'Detection Systems', 'icon': 'radar', 'description': 'Advanced sensors revealing hidden enemies', 'category': 'scifi'},
    'disruptive_tech': {'name': 'Disruptive Tech', 'icon': 'lightning-fill', 'description': 'EMP, jamming, and electronic warfare', 'category': 'scifi'},
    'quality_over_quantity': {'name': 'Quality over Quantity', 'icon': 'gem', 'description': 'Elite units with superior stats and equipment', 'category': 'scifi'},
}

# Official trait lists (from table files)
OFFICIAL_INFANTRY_TRAITS = [
    'Adaptive Camouflage', 'Aerial', 'Aggressive', 'Agile', 'Assault Troops', 'Berserk', 'Bestow Trait', 'Brave',
    'Bug Hunter', 'Cautious', 'Combat Drugs', 'Dependant', 'Detection', 'Disruptive Charge', 'Droids (self-less)',
    'Droids (self-preserving)', 'Drop Troop', 'Elusive', 'Engineer', 'Fanatic', 'Fast', 'Fearless', 'Fire Team',
    'Flyer', 'Frail', 'Frenzied', 'Goon', 'Grav Mount', 'Grizzled', 'Gung Ho', 'Hardened', 'Hero', 'Hesitant',
    'Hive mind (controller)', 'Hive Mind (unit)', 'HQ', 'Huge', 'Ignore Pain', 'Infect', 'Infilration',
    'Inflexible', 'Jet Packs', 'Legend', 'Limited Teleport', 'Mechanized', 'Night Vision', 'No Grenades',
    'Obvious Target', 'Recon', 'Regenerate', 'Relentless', 'Reserves', 'Resilient (2)', 'Resilient (3)',
    'Resilient (4)', 'Resilient (5)', 'Resilient (6)', 'Save', 'Self Repairing', 'Shaky', 'Shock Troops',
    'Slick', 'Slow', 'Slow Firing', 'Stealth', 'Supreme Armour', 'Supreme Weapon', 'Swift', 'Tank Hunter',
    'Terrifying', 'Timid', 'Tough', 'Unstable Technology', 'Villain', 'Weak', 'Zombie'
]

OFFICIAL_VEHICLE_TRAITS = [
    'Advanced Targeting System', 'AI Controlled', 'Alternate Fire Weapons (2)', 'Alternate Fire Weapons (3)',
    'Amphibious', 'Close - In Defense System', 'Command Vehicle', 'Electronic Countermeasures', 'Energy screen',
    'Fast', 'Fixed Mount (1)', 'Fixed Mount (2)', 'Fixed Mount (3)', 'Forward Observer', 'Improved Weapons Control',
    'Jump Jets', 'Linked Weapons', 'Medevac', 'Reactive Armour', 'Reserves', 'Slow', 'Smoke', 'Stealth',
    'Supercharged', 'Under-Powered', 'Weapon Stabilizer'
]

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_faction_logo(file):
    """Save uploaded faction logo and return filename"""
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename):
        return None
    
    # Generate unique filename
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    
    # Create upload folder if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Save file
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    return filename

def delete_faction_logo(filename):
    """Delete faction logo file"""
    if filename:
        try:
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            print(f"Error deleting logo: {e}")


def validate_password_strength(password):
    """Validate password meets security requirements"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is strong"


def check_account_locked(user):
    """Check if account is locked due to failed login attempts"""
    if user.account_locked_until and user.account_locked_until > datetime.utcnow():
        minutes_left = int((user.account_locked_until - datetime.utcnow()).total_seconds() / 60)
        return True, f"Account locked. Try again in {minutes_left} minutes."
    return False, ""


def admin_required(f):
    """Decorator to require admin access for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def init_routes(app):
    """Initialize all routes"""
    
    @app.route('/')
    def index():
        try:
            recent_lists = ArmyList.query.filter_by(is_public=True).order_by(ArmyList.created_at.desc()).limit(6).all()
        except Exception as e:
            # Database tables may not exist yet - show empty list
            print(f"Warning: Could not fetch recent lists: {e}")
            recent_lists = []
        return render_template('index.html', recent_lists=recent_lists)
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip() or None  # Empty email becomes None
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            # Validate username and password are provided
            if not username or not password:
                flash('Username and password are required', 'danger')
                return render_template('register.html')
            
            # Username validation
            if len(username) < 3 or len(username) > 20:
                flash('Username must be between 3 and 20 characters', 'danger')
                return render_template('register.html')
            
            if not re.match(r'^[a-zA-Z0-9_-]+$', username):
                flash('Username can only contain letters, numbers, underscores and hyphens', 'danger')
                return render_template('register.html')
            
            # Password validation
            if password != confirm_password:
                flash('Passwords do not match', 'danger')
                return render_template('register.html')
            
            is_strong, message = validate_password_strength(password)
            if not is_strong:
                flash(message, 'danger')
                return render_template('register.html')
            
            # Check if username already exists
            if User.query.filter_by(username=username).first():
                flash('Username already exists', 'danger')
                return render_template('register.html')
            
            # Check if email already exists (only if email provided)
            if email and User.query.filter_by(email=email).first():
                flash('Email already registered', 'danger')
                return render_template('register.html')
            
            # Create new user with pbkdf2:sha256 hashing
            # Auto-promote the very first registered user to admin, except test accounts
            test_usernames = {'testuser', 'test', 'admin_test'}
            is_first_user = User.query.count() == 0 and username.lower() not in test_usernames
            user = User(  # type: ignore
                username=username,
                email=email,
                password_hash=generate_password_hash(password, method='pbkdf2:sha256', salt_length=16),
                is_admin=is_first_user
            )
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            remember = bool(request.form.get('remember', False))
            
            print(f"DEBUG LOGIN: username={username}, remember={remember}")
            
            if not username or not password:
                flash('Please enter both username and password', 'danger')
                return render_template('login.html')
            
            user = User.query.filter_by(username=username).first()
            
            if user:
                # Check if account is locked
                is_locked, lock_message = check_account_locked(user)
                if is_locked:
                    flash(lock_message, 'danger')
                    return render_template('login.html')
                
                # Verify password
                if check_password_hash(user.password_hash, password):
                    # Successful login - reset failed attempts
                    user.failed_login_attempts = 0
                    user.account_locked_until = None
                    user.last_login = datetime.utcnow()
                    db.session.commit()
                    
                    # Debug logging
                    print(f"DEBUG: Logging in user {user.username} (ID: {user.id})")
                    print(f"DEBUG: User is_active: {user.is_active}")
                    print(f"DEBUG: User is_authenticated: {user.is_authenticated}")
                    print(f"DEBUG: Remember me: {remember}")
                    
                    # Force remember=True for testing
                    login_result = login_user(user, remember=True)
                    print(f"DEBUG: login_user returned: {login_result}")
                    print(f"DEBUG: current_user.is_authenticated: {current_user.is_authenticated}")
                    print(f"DEBUG: current_user ID: {current_user.get_id()}")
                    
                    from flask import session
                    print(f"DEBUG: Session contents: {dict(session)}")
                    
                    next_page = request.args.get('next')
                    flash(f'Welcome back, {user.username}!', 'success')
                    return redirect(next_page if next_page else url_for('dashboard'))
                else:
                    # Failed login - increment counter
                    user.failed_login_attempts += 1
                    
                    # Lock account after 5 failed attempts for 15 minutes
                    if user.failed_login_attempts >= 5:
                        user.account_locked_until = datetime.utcnow() + timedelta(minutes=15)
                        db.session.commit()
                        flash('Too many failed login attempts. Account locked for 15 minutes. Contact admin if needed.', 'danger')
                    else:
                        db.session.commit()
                        attempts_left = 5 - user.failed_login_attempts
                        flash(f'Invalid password. {attempts_left} attempts remaining.', 'danger')
            else:
                flash('Invalid username or password', 'danger')
        
        return render_template('login.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out', 'info')
        return redirect(url_for('index'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        print(f"DEBUG DASHBOARD: current_user.is_authenticated = {current_user.is_authenticated}")
        print(f"DEBUG DASHBOARD: current_user = {current_user}")
        from flask import session
        print(f"DEBUG DASHBOARD: Session = {dict(session)}")
        
        my_lists = ArmyList.query.filter_by(user_id=current_user.id).order_by(ArmyList.updated_at.desc()).all()
        my_units = Unit.query.filter_by(user_id=current_user.id).order_by(Unit.updated_at.desc()).all()
        my_factions = Faction.query.filter_by(user_id=current_user.id).order_by(Faction.updated_at.desc()).all()
        return render_template('dashboard.html', my_lists=my_lists, my_units=my_units, my_factions=my_factions)
    
    # ==================== FACTION CREATOR ====================
    @app.route('/faction/creator', methods=['GET', 'POST'])
    @login_required
    def faction_creator():
        if request.method == 'POST':
            try:
                name = request.form.get('name', '').strip()
                description = request.form.get('description', '').strip()
                color = request.form.get('color', '#0d6efd')
                icon = request.form.get('icon', 'shield')
                background = request.form.get('background', '').strip()
                special_rules = request.form.get('special_rules', '').strip()
                is_public = request.form.get('is_public') == 'true'
                
                # Handle playstyle tags
                selected_tags = request.form.getlist('playstyle_tags')
                # Validate tags against predefined list
                valid_tags = [tag for tag in selected_tags if tag in PLAYSTYLE_TAGS]
                
                # Enforce 5-tag limit per category
                warfare_tags = [tag for tag in valid_tags if PLAYSTYLE_TAGS[tag]['category'] == 'warfare']
                scifi_tags = [tag for tag in valid_tags if PLAYSTYLE_TAGS[tag]['category'] == 'scifi']
                
                if len(warfare_tags) > 5:
                    flash('Maximum 5 warfare tactics tags allowed. Please reduce your selection.', 'warning')
                    return redirect(url_for('faction_creator'))
                
                if len(scifi_tags) > 5:
                    flash('Maximum 5 sci-fi/fantasy tags allowed. Please reduce your selection.', 'warning')
                    return redirect(url_for('faction_creator'))
                
                playstyle_tags_json = json.dumps(valid_tags) if valid_tags else None
                
                # Handle logo upload
                logo_filename = None
                if 'logo' in request.files:
                    file = request.files['logo']
                    if file and file.filename:
                        # Check file size
                        file.seek(0, os.SEEK_END)
                        size = file.tell()
                        file.seek(0)
                        
                        if size > MAX_FILE_SIZE:
                            flash('Logo file too large. Maximum size is 2MB.', 'warning')
                        elif not allowed_file(file.filename):
                            flash('Invalid file type. Only PNG, JPG, JPEG, and GIF are allowed.', 'warning')
                        else:
                            logo_filename = save_faction_logo(file)
                            if not logo_filename:
                                flash('Error uploading logo. Please try again.', 'warning')
                
                faction = Faction(  # type: ignore
                    user_id=current_user.id,
                    name=name,
                    description=description,
                    color=color,
                    icon=icon,
                    logo_filename=logo_filename,
                    playstyle_tags=playstyle_tags_json,
                    background=background,
                    special_rules=special_rules,
                    is_public=is_public
                )
                
                db.session.add(faction)
                db.session.commit()
                
                flash(f'Faction "{name}" created successfully!', 'success')
                return redirect(url_for('view_faction', faction_id=faction.id))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating faction: {str(e)}', 'danger')
        
        return render_template('faction_creator.html', playstyle_tags=PLAYSTYLE_TAGS)
    
    @app.route('/faction/<int:faction_id>')
    def view_faction(faction_id):
        faction = Faction.query.get_or_404(faction_id)
        
        if not faction.is_public and (not current_user.is_authenticated or faction.user_id != current_user.id):
            flash('This faction is private', 'danger')
            return redirect(url_for('index'))
        
        # Get faction units and lists
        units = Unit.query.filter_by(faction_id=faction_id).all()
        lists = ArmyList.query.filter_by(faction_id=faction_id).all()
        
        # Get user's rating if authenticated
        user_rating = None
        if current_user.is_authenticated:
            user_rating = FactionRating.query.filter_by(faction_id=faction_id, user_id=current_user.id).first()
        
        return render_template('view_faction.html', faction=faction, units=units, lists=lists, playstyle_tags=PLAYSTYLE_TAGS, user_rating=user_rating)
    
    @app.route('/faction/<int:faction_id>/rate', methods=['POST'])
    @login_required
    def rate_faction(faction_id):
        try:
            faction = Faction.query.get_or_404(faction_id)
            
            # Only public factions can be rated
            if not faction.is_public:
                return jsonify({'success': False, 'error': 'Cannot rate private factions'}), 403
            
            # Get the rating score (1-5)
            score = request.json.get('score')
            comment = request.json.get('comment', '').strip()
            
            # Validate score
            if not score or int(score) < 1 or int(score) > 5:
                return jsonify({'success': False, 'error': 'Rating must be between 1 and 5'}), 400
            
            score = int(score)
            
            # Check if user already rated this faction
            existing_rating = FactionRating.query.filter_by(faction_id=faction_id, user_id=current_user.id).first()
            
            if existing_rating:
                # Update existing rating
                existing_rating.score = score
                existing_rating.comment = comment if comment else None
                existing_rating.updated_at = datetime.utcnow()
            else:
                # Create new rating
                new_rating = FactionRating(
                    faction_id=faction_id,
                    user_id=current_user.id,
                    score=score,
                    comment=comment if comment else None
                )
                db.session.add(new_rating)
            
            db.session.commit()
            
            # Return updated faction stats
            return jsonify({
                'success': True,
                'average_rating': faction.get_average_rating(),
                'rating_count': faction.get_rating_count()
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/faction/<int:faction_id>/delete', methods=['POST'])
    @login_required
    def delete_faction(faction_id):
        try:
            faction = Faction.query.get_or_404(faction_id)
            
            # Check ownership
            if faction.user_id != current_user.id:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 403
            
            # Delete logo file if exists
            if faction.logo_filename:
                delete_faction_logo(faction.logo_filename)
            
            # Unassign all units and lists from this faction
            Unit.query.filter_by(faction_id=faction_id).update({'faction_id': None})
            ArmyList.query.filter_by(faction_id=faction_id).update({'faction_id': None})
            
            db.session.delete(faction)
            db.session.commit()
            
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/factions/browse')
    def browse_factions():
        """Public faction browser with search and filter"""
        # Get search and filter parameters
        search_query = request.args.get('search', '').strip()
        playstyle_filter = request.args.get('playstyle', '').strip()
        sort_by = request.args.get('sort', 'newest')  # newest, popular, name
        
        # Base query - only public factions
        query = Faction.query.filter_by(is_public=True)
        
        # Apply search filter
        if search_query:
            query = query.filter(
                db.or_(
                    Faction.name.ilike(f'%{search_query}%'),
                    Faction.description.ilike(f'%{search_query}%')
                )
            )
        
        # Apply playstyle filter
        if playstyle_filter and playstyle_filter in PLAYSTYLE_TAGS:
            query = query.filter(Faction.playstyle_tags.like(f'%"{playstyle_filter}"%'))
        
        # Apply sorting
        if sort_by == 'name':
            query = query.order_by(Faction.name.asc())
        elif sort_by == 'oldest':
            query = query.order_by(Faction.created_at.asc())
        else:  # newest (default)
            query = query.order_by(Faction.created_at.desc())
        
        factions = query.all()
        
        return render_template('browse_factions.html', 
                             factions=factions, 
                             playstyle_tags=PLAYSTYLE_TAGS,
                             search_query=search_query,
                             playstyle_filter=playstyle_filter,
                             sort_by=sort_by)
    
    @app.route('/faction/<int:faction_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_faction(faction_id):
        faction = Faction.query.get_or_404(faction_id)
        
        # Check ownership
        if faction.user_id != current_user.id:
            flash('You do not have permission to edit this faction', 'danger')
            return redirect(url_for('view_faction', faction_id=faction_id))
        
        if request.method == 'POST':
            try:
                faction.name = request.form.get('name', '').strip()
                faction.description = request.form.get('description', '').strip()
                faction.color = request.form.get('color', '#0d6efd')
                faction.icon = request.form.get('icon', 'shield')
                faction.background = request.form.get('background', '').strip()
                faction.special_rules = request.form.get('special_rules', '').strip()
                faction.is_public = request.form.get('is_public') == 'true'
                
                # Handle playstyle tags
                selected_tags = request.form.getlist('playstyle_tags')
                valid_tags = [tag for tag in selected_tags if tag in PLAYSTYLE_TAGS]
                
                # Enforce 5-tag limit per category
                warfare_tags = [tag for tag in valid_tags if PLAYSTYLE_TAGS[tag]['category'] == 'warfare']
                scifi_tags = [tag for tag in valid_tags if PLAYSTYLE_TAGS[tag]['category'] == 'scifi']
                
                if len(warfare_tags) > 5:
                    flash('Maximum 5 warfare tactics tags allowed. Please reduce your selection.', 'warning')
                    return redirect(url_for('edit_faction', faction_id=faction_id))
                
                if len(scifi_tags) > 5:
                    flash('Maximum 5 sci-fi/fantasy tags allowed. Please reduce your selection.', 'warning')
                    return redirect(url_for('edit_faction', faction_id=faction_id))
                
                faction.playstyle_tags = json.dumps(valid_tags) if valid_tags else None
                
                # Handle logo upload
                if 'logo' in request.files:
                    file = request.files['logo']
                    if file and file.filename:
                        # Check file size
                        file.seek(0, os.SEEK_END)
                        size = file.tell()
                        file.seek(0)
                        
                        if size > MAX_FILE_SIZE:
                            flash('Logo file too large. Maximum size is 2MB.', 'warning')
                        elif not allowed_file(file.filename):
                            flash('Invalid file type. Only PNG, JPG, JPEG, and GIF are allowed.', 'warning')
                        else:
                            # Delete old logo if exists
                            if faction.logo_filename:
                                delete_faction_logo(faction.logo_filename)
                            
                            logo_filename = save_faction_logo(file)
                            if logo_filename:
                                faction.logo_filename = logo_filename
                            else:
                                flash('Error uploading logo. Please try again.', 'warning')
                
                faction.updated_at = datetime.utcnow()
                db.session.commit()
                
                flash(f'Faction "{faction.name}" updated successfully!', 'success')
                return redirect(url_for('view_faction', faction_id=faction.id))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating faction: {str(e)}', 'danger')
        
        return render_template('edit_faction.html', faction=faction, playstyle_tags=PLAYSTYLE_TAGS)
    
    @app.route('/faction/<int:faction_id>/copy', methods=['POST'])
    @login_required
    def copy_faction(faction_id):
        """Copy a public faction to current user's account"""
        try:
            original_faction = Faction.query.get_or_404(faction_id)
            
            # Can only copy public factions or your own
            if not original_faction.is_public and original_faction.user_id != current_user.id:
                return jsonify({'success': False, 'error': 'Cannot copy private faction'}), 403
            
            # Copy logo file if exists
            new_logo_filename = None
            if original_faction.logo_filename:
                try:
                    import shutil
                    old_path = os.path.join(UPLOAD_FOLDER, original_faction.logo_filename)
                    if os.path.exists(old_path):
                        # Generate new filename
                        ext = original_faction.logo_filename.rsplit('.', 1)[1].lower()
                        new_logo_filename = f"{uuid.uuid4()}.{ext}"
                        new_path = os.path.join(UPLOAD_FOLDER, new_logo_filename)
                        shutil.copy2(old_path, new_path)
                except Exception as e:
                    print(f"Error copying logo: {e}")
                    # Continue without logo
            
            # Create new faction
            new_faction = Faction(  # type: ignore
                user_id=current_user.id,
                name=f"{original_faction.name} (Copy)",
                description=original_faction.description,
                color=original_faction.color,
                icon=original_faction.icon,
                logo_filename=new_logo_filename,
                playstyle_tags=original_faction.playstyle_tags,
                background=original_faction.background,
                special_rules=original_faction.special_rules,
                is_public=False  # Copies are private by default
            )
            
            db.session.add(new_faction)
            db.session.commit()
            
            return jsonify({'success': True, 'faction_id': new_faction.id, 'message': f'Faction copied successfully!'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/unit/builder')
    @login_required
    def unit_builder():
        """Legacy generic unit builder - redirect to unit type selection"""
        return redirect(url_for('dashboard'))
    
    # ==================== SQUAD BUILDER ====================
    @app.route('/unit/builder/squad', methods=['GET', 'POST'])
    @login_required
    def squad_builder():
        weapons = Weapon.query.order_by(Weapon.category, Weapon.points).all()
        # Secondary weapons: pistols, SMG, shotgun only
        secondary_weapons = Weapon.query.filter(
            (Weapon.name.ilike('%pistol%')) |
            (Weapon.name == 'SMG') |
            (Weapon.name == 'Shotgun')
        ).order_by(Weapon.points).all()
        armours = Armour.query.order_by(Armour.points).all()
        # All infantry types share the same traits (per .TXT files)
        traits = Trait.query.filter(
            Trait.category == 'Infantry',
            Trait.name.in_(OFFICIAL_INFANTRY_TRAITS)
        ).order_by(Trait.name).all()
        my_factions = Faction.query.filter_by(user_id=current_user.id).order_by(Faction.name).all()
        
        if request.method == 'POST':
            try:
                # Get form data
                name = request.form.get('name', '').strip()
                faction_id = request.form.get('faction_id') or None
                quality = request.form.get('quality')
                resolve = request.form.get('resolve')
                squad_size = int(request.form.get('squad_size', 5))
                armour_id = request.form.get('armour_id') or None
                basic_weapon_id = request.form.get('basic_weapon_id') or None
                secondary_weapon_id = request.form.get('secondary_weapon_id') or None
                trait_ids = request.form.getlist('traits')
                notes = request.form.get('notes', '').strip()
                description = request.form.get('description', '').strip()
                weapon_distribution = request.form.get('weapon_distribution', '').strip()
                
                # Calculate points
                data = {
                    'unit_type': 'Squad',
                    'quality': quality,
                    'resolve': resolve,
                    'squad_size': squad_size,
                    'armour_id': int(armour_id) if armour_id else None,
                    'basic_weapon_id': int(basic_weapon_id) if basic_weapon_id else None,
                    'traits': [int(t) for t in trait_ids],
                    'weapon_distribution': weapon_distribution
                }
                total_points = calculate_points(data)
                
                # Create unit
                unit = Unit(  # type: ignore
                    user_id=current_user.id,
                    name=name,
                    unit_type='Squad',
                    faction_id=int(faction_id) if faction_id else None,
                    quality=quality,
                    resolve=resolve,
                    squad_size=squad_size,
                    armour_id=int(armour_id) if armour_id else None,
                    basic_weapon_id=int(basic_weapon_id) if basic_weapon_id else None,
                    secondary_weapon_id=int(secondary_weapon_id) if secondary_weapon_id else None,
                    traits_json=json.dumps([int(t) for t in trait_ids]),
                    squad_members_json=weapon_distribution if weapon_distribution else None,
                    description=description,
                    notes=notes,
                    base_points=total_points,
                    total_points=total_points
                )
                
                db.session.add(unit)
                db.session.commit()
                
                flash(f'Squad "{name}" created successfully!', 'success')
                return redirect(url_for('dashboard'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating squad: {str(e)}', 'danger')
        
        return render_template('squad_builder.html', weapons=weapons, secondary_weapons=secondary_weapons, armours=armours, traits=traits, my_factions=my_factions)
    
    # ==================== CHARACTER BUILDER ====================
    @app.route('/unit/builder/character', methods=['GET', 'POST'])
    @login_required
    def character_builder():
        weapons = Weapon.query.order_by(Weapon.category, Weapon.points).all()
        armours = Armour.query.order_by(Armour.points).all()
        # All infantry types share the same traits (per .TXT files)
        traits = Trait.query.filter(
            Trait.category == 'Infantry',
            Trait.name.in_(OFFICIAL_INFANTRY_TRAITS)
        ).order_by(Trait.name).all()
        my_factions = Faction.query.filter_by(user_id=current_user.id).order_by(Faction.name).all()
        
        if request.method == 'POST':
            try:
                name = request.form.get('name', '').strip()
                faction_id = request.form.get('faction_id') or None
                quality = request.form.get('quality')
                resolve = request.form.get('resolve')
                has_personality = request.form.get('has_personality') == 'true'
                leadership_rating = request.form.get('leadership_rating')
                specialization = request.form.get('specialization')
                armour_id = request.form.get('armour_id') or None
                basic_weapon_id = request.form.get('basic_weapon_id') or None
                trait_ids = request.form.getlist('traits')
                notes = request.form.get('notes', '').strip()
                description = request.form.get('description', '').strip()
                
                # Calculate points for Character
                data = {
                    'unit_type': 'Character',
                    'quality': quality,
                    'has_personality': has_personality,
                    'leadership_rating': leadership_rating,
                    'armour_id': int(armour_id) if armour_id else None,
                    'basic_weapon_id': int(basic_weapon_id) if basic_weapon_id else None,
                    'traits': [int(t) for t in trait_ids]
                }
                total_points = calculate_points(data)
                
                unit = Unit(  # type: ignore
                    user_id=current_user.id,
                    name=name,
                    unit_type='Character',
                    faction_id=int(faction_id) if faction_id else None,
                    quality=quality,
                    resolve=resolve,
                    has_personality=has_personality,
                    leadership_rating=leadership_rating,
                    specialization=specialization,
                    armour_id=int(armour_id) if armour_id else None,
                    basic_weapon_id=int(basic_weapon_id) if basic_weapon_id else None,
                    traits_json=json.dumps([int(t) for t in trait_ids]),
                    description=description,
                    notes=notes,
                    base_points=total_points,
                    total_points=total_points
                )
                
                db.session.add(unit)
                db.session.commit()
                
                flash(f'Character "{name}" created successfully!', 'success')
                return redirect(url_for('dashboard'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating character: {str(e)}', 'danger')
        
        return render_template('character_builder.html', weapons=weapons, armours=armours, traits=traits, my_factions=my_factions)
    
    # ==================== HEAVY WEAPONS TEAM BUILDER ====================
    @app.route('/unit/builder/heavy-weapon', methods=['GET', 'POST'])
    @login_required
    def heavy_weapon_builder():
        weapons = Weapon.query.order_by(Weapon.category, Weapon.points).all()
        armours = Armour.query.order_by(Armour.points).all()
        # Heavy weapon teams are small infantry units - Infantry traits only
        traits = Trait.query.filter(
            Trait.category == 'Infantry',
            Trait.name.in_(OFFICIAL_INFANTRY_TRAITS)
        ).order_by(Trait.name).all()
        my_factions = Faction.query.filter_by(user_id=current_user.id).order_by(Faction.name).all()
        
        if request.method == 'POST':
            try:
                name = request.form.get('name', '').strip()
                faction_id = request.form.get('faction_id') or None
                quality = request.form.get('quality')
                resolve = request.form.get('resolve')
                heavy_weapon_id = request.form.get('heavy_weapon_id') or None
                armour_id = request.form.get('armour_id') or None
                crew_count = int(request.form.get('crew_count', 2))
                trait_ids = request.form.getlist('traits')
                notes = request.form.get('notes', '').strip()
                description = request.form.get('description', '').strip()
                
                # Calculate points
                data = {
                    'unit_type': 'HeavyWeapon',
                    'quality': quality,
                    'heavy_weapon_id': int(heavy_weapon_id) if heavy_weapon_id else None,
                    'armour_id': int(armour_id) if armour_id else None,
                    'traits': [int(t) for t in trait_ids]
                }
                total_points = calculate_points(data)
                
                unit = Unit(  # type: ignore
                    user_id=current_user.id,
                    name=name,
                    unit_type='HeavyWeapon',
                    faction_id=int(faction_id) if faction_id else None,
                    quality=quality,
                    resolve=resolve,
                    heavy_weapon_id=int(heavy_weapon_id) if heavy_weapon_id else None,
                    armour_id=int(armour_id) if armour_id else None,
                    crew_count=crew_count,
                    traits_json=json.dumps([int(t) for t in trait_ids]),
                    description=description,
                    notes=notes,
                    base_points=total_points,
                    total_points=total_points
                )
                
                db.session.add(unit)
                db.session.commit()
                
                flash(f'Heavy Weapons Team "{name}" created successfully!', 'success')
                return redirect(url_for('dashboard'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating heavy weapons team: {str(e)}', 'danger')
        
        return render_template('heavy_weapon_builder.html', weapons=weapons, armours=armours, traits=traits, my_factions=my_factions)
    
    # ==================== SNIPER BUILDER ====================
    @app.route('/unit/builder/sniper', methods=['GET', 'POST'])
    @login_required
    def sniper_builder():
        weapons = Weapon.query.order_by(Weapon.category, Weapon.points).all()
        armours = Armour.query.order_by(Armour.points).all()
        # Snipers are individual infantry specialists - Infantry traits only
        traits = Trait.query.filter(
            Trait.category == 'Infantry',
            Trait.name.in_(OFFICIAL_INFANTRY_TRAITS)
        ).order_by(Trait.name).all()
        my_factions = Faction.query.filter_by(user_id=current_user.id).order_by(Faction.name).all()
        
        if request.method == 'POST':
            try:
                name = request.form.get('name', '').strip()
                faction_id = request.form.get('faction_id') or None
                quality = request.form.get('quality')
                resolve = request.form.get('resolve')
                has_personality = request.form.get('has_personality') == 'true'
                basic_weapon_id = request.form.get('basic_weapon_id') or None
                armour_id = request.form.get('armour_id') or None
                trait_ids = request.form.getlist('traits')
                notes = request.form.get('notes', '').strip()
                description = request.form.get('description', '').strip()
                
                # Calculate points
                data = {
                    'unit_type': 'Sniper',
                    'quality': quality,
                    'has_personality': has_personality,
                    'basic_weapon_id': int(basic_weapon_id) if basic_weapon_id else None,
                    'armour_id': int(armour_id) if armour_id else None,
                    'traits': [int(t) for t in trait_ids]
                }
                total_points = calculate_points(data)
                
                unit = Unit(  # type: ignore
                    user_id=current_user.id,
                    name=name,
                    unit_type='Sniper',
                    faction_id=int(faction_id) if faction_id else None,
                    quality=quality,
                    resolve=resolve,
                    has_personality=has_personality,
                    basic_weapon_id=int(basic_weapon_id) if basic_weapon_id else None,
                    armour_id=int(armour_id) if armour_id else None,
                    traits_json=json.dumps([int(t) for t in trait_ids]),
                    description=description,
                    notes=notes,
                    base_points=total_points,
                    total_points=total_points
                )
                
                db.session.add(unit)
                db.session.commit()
                
                flash(f'Sniper "{name}" created successfully!', 'success')
                return redirect(url_for('dashboard'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating sniper: {str(e)}', 'danger')
        
        return render_template('sniper_builder.html', weapons=weapons, armours=armours, traits=traits, my_factions=my_factions)
    
    # ==================== PSIONIC BUILDER ====================
    @app.route('/unit/builder/psionic', methods=['GET', 'POST'])
    @login_required
    def psionic_builder():
        weapons = Weapon.query.order_by(Weapon.category, Weapon.points).all()
        armours = Armour.query.order_by(Armour.points).all()
        # Psionics are individual infantry with special powers - Infantry traits only
        traits = Trait.query.filter(
            Trait.category == 'Infantry',
            Trait.name.in_(OFFICIAL_INFANTRY_TRAITS)
        ).order_by(Trait.name).all()
        my_factions = Faction.query.filter_by(user_id=current_user.id).order_by(Faction.name).all()
        
        if request.method == 'POST':
            try:
                name = request.form.get('name', '').strip()
                faction_id = request.form.get('faction_id') or None
                quality = request.form.get('quality')
                resolve = request.form.get('resolve')
                has_personality = request.form.get('has_personality') == 'true'
                psionic_aptitude = request.form.get('psionic_aptitude')
                psionic_strength = int(request.form.get('psionic_strength', 3))
                basic_weapon_id = request.form.get('basic_weapon_id') or None
                armour_id = request.form.get('armour_id') or None
                trait_ids = request.form.getlist('traits')
                notes = request.form.get('notes', '').strip()
                description = request.form.get('description', '').strip()
                
                # Calculate points
                data = {
                    'unit_type': 'Psionic',
                    'quality': quality,
                    'has_personality': has_personality,
                    'psionic_aptitude': psionic_aptitude,
                    'psionic_strength': psionic_strength,
                    'basic_weapon_id': int(basic_weapon_id) if basic_weapon_id else None,
                    'armour_id': int(armour_id) if armour_id else None,
                    'traits': [int(t) for t in trait_ids]
                }
                total_points = calculate_points(data)
                
                unit = Unit(  # type: ignore
                    user_id=current_user.id,
                    name=name,
                    unit_type='Psionic',
                    faction_id=int(faction_id) if faction_id else None,
                    quality=quality,
                    resolve=resolve,
                    has_personality=has_personality,
                    psionic_aptitude=psionic_aptitude,
                    psionic_strength=psionic_strength,
                    basic_weapon_id=int(basic_weapon_id) if basic_weapon_id else None,
                    armour_id=int(armour_id) if armour_id else None,
                    traits_json=json.dumps([int(t) for t in trait_ids]),
                    description=description,
                    notes=notes,
                    base_points=total_points,
                    total_points=total_points
                )
                
                db.session.add(unit)
                db.session.commit()
                
                flash(f'Psionic "{name}" created successfully!', 'success')
                return redirect(url_for('dashboard'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating psionic: {str(e)}', 'danger')
        
        return render_template('psionic_builder.html', weapons=weapons, armours=armours, traits=traits, my_factions=my_factions)
    
    # ==================== VEHICLE BUILDER ====================
    @app.route('/unit/builder/vehicle', methods=['GET', 'POST'])
    @login_required
    def vehicle_builder():
        weapons = Weapon.query.order_by(Weapon.category, Weapon.points).all()
        armours = Armour.query.order_by(Armour.points).all()
        # Vehicles have their own specific properties/traits
        traits = Trait.query.filter(
            Trait.category == 'Vehicle',
            Trait.name.in_(OFFICIAL_VEHICLE_TRAITS)
        ).order_by(Trait.name).all()
        my_factions = Faction.query.filter_by(user_id=current_user.id).order_by(Faction.name).all()
        
        if request.method == 'POST':
            try:
                name = request.form.get('name', '').strip()
                faction_id = request.form.get('faction_id') or None
                vehicle_type = request.form.get('vehicle_type')
                quality = request.form.get('quality')
                resolve = request.form.get('resolve')
                movement_type = request.form.get('movement_type')
                front_armour = int(request.form.get('vehicle_armour_front', 3))
                side_armour = int(request.form.get('vehicle_armour_side', 2))
                rear_armour = int(request.form.get('vehicle_armour_rear', 1))
                crew_size = int(request.form.get('crew_size', 1))
                capacity = int(request.form.get('carrying_capacity', 0))
                basic_weapon_id = request.form.get('basic_weapon_id') or None
                secondary_weapon_id = request.form.get('secondary_weapon_id') or None
                property_ids = request.form.getlist('traits')  # Vehicle properties use the trait checkboxes
                notes = request.form.get('notes', '').strip()
                description = request.form.get('description', '').strip()
                
                # Calculate points
                data = {
                    'unit_type': 'Vehicle',
                    'quality': quality,
                    'movement_type': movement_type,
                    'vehicle_armour_front': front_armour,
                    'vehicle_armour_side': side_armour,
                    'vehicle_armour_rear': rear_armour,
                    'carrying_capacity': capacity,
                    'basic_weapon_id': int(basic_weapon_id) if basic_weapon_id else None,
                    'secondary_weapon_id': int(secondary_weapon_id) if secondary_weapon_id else None,
                    'traits': [int(t) for t in property_ids]
                }
                total_points = calculate_points(data)
                
                unit = Unit(  # type: ignore
                    user_id=current_user.id,
                    name=name,
                    unit_type='Vehicle',
                    faction_id=int(faction_id) if faction_id else None,
                    vehicle_type=vehicle_type,
                    quality=quality,
                    resolve=resolve,
                    movement_type=movement_type,
                    vehicle_armour_front=front_armour,
                    vehicle_armour_side=side_armour,
                    vehicle_armour_rear=rear_armour,
                    crew_size=crew_size,
                    carrying_capacity=capacity,
                    basic_weapon_id=int(basic_weapon_id) if basic_weapon_id else None,
                    secondary_weapon_id=int(secondary_weapon_id) if secondary_weapon_id else None,
                    traits_json=json.dumps([int(t) for t in property_ids]),
                    description=description,
                    notes=notes,
                    base_points=total_points,
                    total_points=total_points
                )
                
                db.session.add(unit)
                db.session.commit()
                
                flash(f'Vehicle "{name}" created successfully!', 'success')
                return redirect(url_for('dashboard'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating vehicle: {str(e)}', 'danger')
        
        return render_template('vehicle_builder.html', weapons=weapons, armours=armours, traits=traits, my_factions=my_factions)
    
    # ==================== UNIT EDIT ====================
    @app.route('/unit/<int:unit_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_unit(unit_id):
        unit = Unit.query.get_or_404(unit_id)
        
        # Check ownership
        if unit.user_id != current_user.id:
            flash('You do not have permission to edit this unit', 'danger')
            return redirect(url_for('dashboard'))
        
        weapons = Weapon.query.order_by(Weapon.category, Weapon.points).all()
        # Secondary weapons: pistols, SMG, shotgun only
        secondary_weapons = Weapon.query.filter(
            (Weapon.name.ilike('%pistol%')) |
            (Weapon.name == 'SMG') |
            (Weapon.name == 'Shotgun')
        ).order_by(Weapon.points).all()
        armours = Armour.query.order_by(Armour.points).all()
        traits = Trait.query.filter(
            or_(
                and_(Trait.category == 'Infantry', Trait.name.in_(OFFICIAL_INFANTRY_TRAITS)),
                and_(Trait.category == 'Vehicle', Trait.name.in_(OFFICIAL_VEHICLE_TRAITS))
            )
        ).order_by(Trait.category, Trait.name).all()
        
        if request.method == 'POST':
            try:
                # Common fields for all unit types
                unit.name = request.form.get('name', '').strip()
                faction_id = request.form.get('faction_id')
                unit.faction_id = int(faction_id) if faction_id else None
                unit.quality = request.form.get('quality')
                unit.resolve = request.form.get('resolve')
                unit.notes = request.form.get('notes', '').strip()
                
                # Type-specific fields
                if unit.unit_type == 'Squad':
                    unit.squad_size = int(request.form.get('squad_size', 5))
                    unit.armour_id = request.form.get('armour_id') or None
                    unit.basic_weapon_id = request.form.get('basic_weapon_id') or None
                    unit.secondary_weapon_id = request.form.get('secondary_weapon_id') or None
                    trait_ids = request.form.getlist('traits')
                    unit.traits_json = json.dumps([int(t) for t in trait_ids])
                    
                    data = {
                        'unit_type': 'Squad',
                        'quality': unit.quality,
                        'squad_size': unit.squad_size,
                        'armour_id': int(unit.armour_id) if unit.armour_id else None,
                        'basic_weapon_id': int(unit.basic_weapon_id) if unit.basic_weapon_id else None,
                        'traits': [int(t) for t in trait_ids]
                    }
                    
                elif unit.unit_type == 'Character':
                    unit.has_personality = request.form.get('has_personality') == 'true'
                    unit.leadership_rating = request.form.get('leadership_rating')
                    unit.specialization = request.form.get('specialization')
                    unit.armour_id = request.form.get('armour_id') or None
                    unit.basic_weapon_id = request.form.get('basic_weapon_id') or None
                    trait_ids = request.form.getlist('traits')
                    unit.traits_json = json.dumps([int(t) for t in trait_ids])
                    
                    data = {
                        'unit_type': 'Character',
                        'quality': unit.quality,
                        'has_personality': unit.has_personality,
                        'leadership_rating': unit.leadership_rating,
                        'specialization': unit.specialization,
                        'armour_id': int(unit.armour_id) if unit.armour_id else None,
                        'basic_weapon_id': int(unit.basic_weapon_id) if unit.basic_weapon_id else None,
                        'traits': [int(t) for t in trait_ids]
                    }
                    
                elif unit.unit_type == 'HeavyWeapon':
                    unit.heavy_weapon_id = request.form.get('heavy_weapon_id') or None
                    unit.armour_id = request.form.get('armour_id') or None
                    unit.crew_count = int(request.form.get('crew_count', 2))
                    trait_ids = request.form.getlist('traits')
                    unit.traits_json = json.dumps([int(t) for t in trait_ids])
                    
                    data = {
                        'unit_type': 'HeavyWeapon',
                        'quality': unit.quality,
                        'heavy_weapon_id': int(unit.heavy_weapon_id) if unit.heavy_weapon_id else None,
                        'armour_id': int(unit.armour_id) if unit.armour_id else None,
                        'traits': [int(t) for t in trait_ids]
                    }
                    
                elif unit.unit_type == 'Sniper':
                    unit.has_personality = request.form.get('has_personality') == 'true'
                    unit.basic_weapon_id = request.form.get('basic_weapon_id') or None
                    unit.armour_id = request.form.get('armour_id') or None
                    trait_ids = request.form.getlist('traits')
                    unit.traits_json = json.dumps([int(t) for t in trait_ids])
                    
                    data = {
                        'unit_type': 'Sniper',
                        'quality': unit.quality,
                        'has_personality': unit.has_personality,
                        'basic_weapon_id': int(unit.basic_weapon_id) if unit.basic_weapon_id else None,
                        'armour_id': int(unit.armour_id) if unit.armour_id else None,
                        'traits': [int(t) for t in trait_ids]
                    }
                    
                elif unit.unit_type == 'Psionic':
                    unit.has_personality = request.form.get('has_personality') == 'true'
                    unit.psionic_level = request.form.get('psionic_level')
                    unit.armour_id = request.form.get('armour_id') or None
                    unit.basic_weapon_id = request.form.get('basic_weapon_id') or None
                    trait_ids = request.form.getlist('traits')
                    unit.traits_json = json.dumps([int(t) for t in trait_ids])
                    
                    data = {
                        'unit_type': 'Psionic',
                        'quality': unit.quality,
                        'has_personality': unit.has_personality,
                        'psionic_level': unit.psionic_level,
                        'armour_id': int(unit.armour_id) if unit.armour_id else None,
                        'basic_weapon_id': int(unit.basic_weapon_id) if unit.basic_weapon_id else None,
                        'traits': [int(t) for t in trait_ids]
                    }
                    
                elif unit.unit_type == 'Vehicle':
                    unit.vehicle_type = request.form.get('vehicle_type')
                    unit.movement_type = request.form.get('movement_type')
                    unit.vehicle_armour_front = int(request.form.get('vehicle_armour_front', 3))
                    unit.vehicle_armour_side = int(request.form.get('vehicle_armour_side', 2))
                    unit.vehicle_armour_rear = int(request.form.get('vehicle_armour_rear', 1))
                    unit.crew_size = int(request.form.get('crew_size', 2))
                    unit.carrying_capacity = int(request.form.get('carrying_capacity', 0))
                    
                    # Weapons
                    basic_weapon_id = request.form.get('basic_weapon_id') or None
                    secondary_weapon_id = request.form.get('secondary_weapon_id') or None
                    unit.basic_weapon_id = int(basic_weapon_id) if basic_weapon_id else None
                    unit.secondary_weapon_id = int(secondary_weapon_id) if secondary_weapon_id else None
                    
                    property_ids = request.form.getlist('traits')  # Vehicle properties use the trait checkboxes
                    unit.traits_json = json.dumps([int(t) for t in property_ids])
                    
                    data = {
                        'unit_type': 'Vehicle',
                        'quality': unit.quality,
                        'movement_type': unit.movement_type,
                        'vehicle_armour_front': unit.vehicle_armour_front,
                        'vehicle_armour_side': unit.vehicle_armour_side,
                        'vehicle_armour_rear': unit.vehicle_armour_rear,
                        'carrying_capacity': unit.carrying_capacity,
                        'basic_weapon_id': unit.basic_weapon_id,
                        'secondary_weapon_id': unit.secondary_weapon_id,
                        'traits': [int(t) for t in property_ids]
                    }
                
                # Recalculate points
                total_points = calculate_points(data)
                unit.base_points = total_points
                unit.total_points = total_points
                unit.updated_at = datetime.utcnow()
                
                db.session.commit()
                
                flash(f'Unit "{unit.name}" updated successfully!', 'success')
                return redirect(url_for('dashboard'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating unit: {str(e)}', 'danger')
        
        # Get user's factions for dropdown
        my_factions = Faction.query.filter_by(user_id=current_user.id).order_by(Faction.name).all()
        
        # Determine which template to use based on unit type
        template_map = {
            'Squad': 'edit_squad.html',
            'Character': 'edit_character.html',
            'HeavyWeapon': 'edit_heavy_weapon.html',
            'Sniper': 'edit_sniper.html',
            'Psionic': 'edit_psionic.html',
            'Vehicle': 'edit_vehicle.html'
        }
        
        template = template_map.get(unit.unit_type, 'edit_squad.html')
        return render_template(template, unit=unit, weapons=weapons, secondary_weapons=secondary_weapons, armours=armours, traits=traits, my_factions=my_factions)
    
    @app.route('/unit/save', methods=['POST'])
    @login_required
    def save_unit():
        data = request.json
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        try:
            total_points = calculate_points(data)
            
            unit = Unit(  # type: ignore
                user_id=current_user.id,
                name=data['name'],
                unit_type=data['unit_type'],
                faction=data.get('faction', ''),
                quality=data['quality'],
                resolve=data['resolve'],
                squad_size=data.get('squad_size', 1),
                armour_id=data.get('armour_id') or None,
                basic_weapon_id=data.get('basic_weapon_id') or None,
                support_weapon_id=data.get('support_weapon_id') or None,
                heavy_weapon_id=data.get('heavy_weapon_id') or None,
                has_personality=data.get('has_personality', False),
                traits_json=json.dumps(data.get('traits', [])),
                base_points=0,
                total_points=total_points,
                is_public=data.get('is_public', False)
            )
            
            db.session.add(unit)
            db.session.commit()
            
            return jsonify({'success': True, 'unit_id': unit.id, 'message': 'Unit saved successfully!'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400
    
    @app.route('/unit/<int:unit_id>')
    def view_unit(unit_id):
        unit = Unit.query.get_or_404(unit_id)
        
        if not unit.is_public and (not current_user.is_authenticated or unit.user_id != current_user.id):
            flash('This unit is private', 'danger')
            return redirect(url_for('index'))
        
        return render_template('view_unit.html', unit=unit)
    
    @app.route('/unit/<int:unit_id>/delete', methods=['POST'])
    @login_required
    def delete_unit(unit_id):
        unit = Unit.query.get_or_404(unit_id)
        
        if unit.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        db.session.delete(unit)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Unit deleted successfully'})
    
    @app.route('/list/builder')
    @login_required
    def list_builder():
        my_units = Unit.query.filter_by(user_id=current_user.id).order_by(Unit.faction_id, Unit.name).all()
        public_units = Unit.query.filter_by(is_public=True).order_by(Unit.faction_id, Unit.name).all()
        my_factions = Faction.query.filter_by(user_id=current_user.id).order_by(Faction.name).all()
        return render_template('list_builder.html', my_units=my_units, public_units=public_units, my_factions=my_factions)
    
    @app.route('/list/save', methods=['POST'])
    @login_required
    def save_list():
        data = request.json
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        try:
            units_data = data['units']
            total_points = 0
            total_units = 0
            
            for item in units_data:
                unit = Unit.query.get(item['unit_id'])
                if unit:
                    total_points += unit.total_points * item['quantity']
                    total_units += item['quantity']
            
            if data.get('list_id'):
                army_list = ArmyList.query.get(data['list_id'])
                if not army_list or army_list.user_id != current_user.id:
                    return jsonify({'success': False, 'error': 'Unauthorized'}), 403
            else:
                army_list = ArmyList(user_id=current_user.id)  # type: ignore
            
            army_list.name = data['name']
            army_list.faction_id = data.get('faction_id') or None
            army_list.description = data.get('description', '')
            army_list.units_json = json.dumps(units_data)
            army_list.total_points = total_points
            army_list.total_units = total_units
            army_list.is_public = data.get('is_public', False)
            
            db.session.add(army_list)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'list_id': army_list.id,
                'message': 'List saved successfully!',
                'total_points': total_points
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400
    
    @app.route('/list/<int:list_id>')
    def view_list(list_id):
        army_list = ArmyList.query.get_or_404(list_id)
        
        if not army_list.is_public and (not current_user.is_authenticated or army_list.user_id != current_user.id):
            flash('This list is private', 'danger')
            return redirect(url_for('index'))
        
        if not current_user.is_authenticated or army_list.user_id != current_user.id:
            army_list.views += 1
            db.session.commit()
        
        return render_template('view_list.html', army_list=army_list)
    
    @app.route('/list/<int:list_id>/edit')
    @login_required
    def edit_list(list_id):
        army_list = ArmyList.query.get_or_404(list_id)
        
        if army_list.user_id != current_user.id:
            flash('You can only edit your own lists', 'danger')
            return redirect(url_for('dashboard'))
        
        my_units = Unit.query.filter_by(user_id=current_user.id).order_by(Unit.faction_id, Unit.name).all()
        public_units = Unit.query.filter_by(is_public=True).order_by(Unit.faction_id, Unit.name).all()
        
        return render_template('edit_list.html', army_list=army_list, my_units=my_units, public_units=public_units)
    
    @app.route('/list/<int:list_id>/delete', methods=['POST'])
    @login_required
    def delete_list(list_id):
        army_list = ArmyList.query.get_or_404(list_id)
        
        if army_list.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        db.session.delete(army_list)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'List deleted successfully'})
    
    @app.route('/list/<int:list_id>/export-pdf')
    def export_list_pdf(list_id):
        """Export army list as PDF with unit stats"""
        army_list = ArmyList.query.get_or_404(list_id)
        
        # Check permissions
        if not army_list.is_public and (not current_user.is_authenticated or army_list.user_id != current_user.id):
            flash('This list is private', 'danger')
            return redirect(url_for('index'))
        
        try:
            from pdf_generator import generate_army_list_pdf
            from flask import send_file
            
            # Get units with quantities
            units_with_quantities = army_list.get_units()
            
            # Generate PDF
            pdf_buffer = generate_army_list_pdf(army_list, units_with_quantities)
            
            # Create safe filename
            safe_name = "".join(c for c in army_list.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"FAD_List_{safe_name}.pdf"
            
            return send_file(
                pdf_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
        except Exception as e:
            flash(f'Error generating PDF: {str(e)}', 'danger')
            return redirect(url_for('view_list', list_id=list_id))
        
        if army_list.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        db.session.delete(army_list)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'List deleted successfully'})
    
    @app.route('/browse')
    def browse_lists():
        faction = request.args.get('faction', '')
        search = request.args.get('search', '')
        
        query = ArmyList.query.filter_by(is_public=True)
        
        if faction:
            # Filter by faction name, not faction field
            query = query.join(Faction).filter(Faction.name == faction)
        
        if search:
            query = query.filter(ArmyList.name.contains(search) | ArmyList.description.contains(search))
        
        lists = query.order_by(ArmyList.created_at.desc()).all()
        
        # Get list of public factions that have public lists
        factions = db.session.query(Faction.name).join(ArmyList).filter(ArmyList.is_public == True).distinct().all()
        factions = [f[0] for f in factions if f[0]]
        
        return render_template('browse.html', lists=lists, factions=factions, selected_faction=faction, search=search)
    
    @app.route('/armoury')
    def armoury():
        weapons = Weapon.query.order_by(Weapon.category, Weapon.points).all()
        armours = Armour.query.order_by(Armour.points).all()
        traits = Trait.query.filter(
            or_(
                and_(Trait.category == 'Infantry', Trait.name.in_(OFFICIAL_INFANTRY_TRAITS)),
                and_(Trait.category == 'Vehicle', Trait.name.in_(OFFICIAL_VEHICLE_TRAITS))
            )
        ).order_by(Trait.category, Trait.name).all()
        return render_template('armoury.html', weapons=weapons, armours=armours, traits=traits)
    
    
    # ==================== ADMIN ROUTES ====================
    
    @app.route('/admin')
    @admin_required
    def admin_panel():
        """Admin dashboard with user management"""
        users = User.query.order_by(User.created_at.desc()).all()
        
        # Statistics
        total_users = User.query.count()
        total_lists = ArmyList.query.count()
        total_units = Unit.query.count()
        locked_users = User.query.filter(User.account_locked_until > datetime.utcnow()).count()
        
        return render_template('admin/panel.html', 
                             users=users,
                             total_users=total_users,
                             total_lists=total_lists,
                             total_units=total_units,
                             locked_users=locked_users)
    
    @app.route('/admin/user/<int:user_id>/unlock', methods=['POST'])
    @admin_required
    def unlock_user(user_id):
        """Unlock a user account"""
        user = User.query.get_or_404(user_id)
        
        user.failed_login_attempts = 0
        user.account_locked_until = None
        db.session.commit()
        
        flash(f'User {user.username} has been unlocked.', 'success')
        return redirect(url_for('admin_panel'))
    
    @app.route('/admin/user/<int:user_id>/toggle-admin', methods=['POST'])
    @admin_required
    def toggle_admin(user_id):
        """Toggle admin status for a user"""
        user = User.query.get_or_404(user_id)
        
        # Prevent removing your own admin status
        if user.id == current_user.id:
            flash('You cannot remove your own admin status.', 'warning')
            return redirect(url_for('admin_panel'))
        
        user.is_admin = not user.is_admin
        db.session.commit()
        
        status = 'granted' if user.is_admin else 'revoked'
        flash(f'Admin privileges {status} for {user.username}.', 'success')
        return redirect(url_for('admin_panel'))
    
    @app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
    @admin_required
    def delete_user(user_id):
        """Delete a user account (admin only)"""
        user = User.query.get_or_404(user_id)
        
        # Prevent deleting your own account
        if user.id == current_user.id:
            flash('You cannot delete your own account.', 'warning')
            return redirect(url_for('admin_panel'))
        
        username = user.username
        
        # Delete user's units and lists
        Unit.query.filter_by(user_id=user.id).delete()
        ArmyList.query.filter_by(user_id=user.id).delete()
        
        db.session.delete(user)
        db.session.commit()
        
        flash(f'User {username} and all their data has been deleted.', 'success')
        return redirect(url_for('admin_panel'))


def calculate_points(data):
    """Calculate unit points based on configuration - Supports all 6 unit types"""
    unit_type = data.get('unit_type', 'Squad')
    
    # Quality and Resolve multipliers (from F.A.D. rules)
    quality_multipliers = {
        'Rabble': 0.7,
        'Conscript': 0.0,
        'Regular': 1.3,
        'Elite': 1.6
    }
    
    resolve_multipliers = {
        'Reluctant': -0.5,
        'Uncertain': -0.3,
        'Steady': 0.0,
        'Determined': 0.3
    }
    
    quality = data.get('quality', 'Regular')
    resolve = data.get('resolve', 'Steady')
    quality_mult = quality_multipliers.get(quality, 1.3)
    resolve_mult = resolve_multipliers.get(resolve, 0.0)
    
    # Initialize total
    total_points = 0
    
    # ==================== SQUAD ====================
    if unit_type == 'Squad':
        squad_size = data.get('squad_size', 5)
        armour_id = data.get('armour_id')
        
        # Check if weapon distribution is specified
        weapon_distribution = data.get('weapon_distribution', '')
        
        if weapon_distribution and weapon_distribution != '{}':
            # Parse weapon distribution JSON
            try:
                distribution = json.loads(weapon_distribution) if isinstance(weapon_distribution, str) else weapon_distribution
                
                # Calculate cost per weapon type
                for weapon_id_str, quantity in distribution.items():
                    weapon_id = int(weapon_id_str)
                    quantity = int(quantity)
                    
                    # Base cost per trooper
                    cost_per_trooper = 3
                    
                    # Add armour
                    if armour_id:
                        armour = Armour.query.get(armour_id)
                        if armour:
                            cost_per_trooper += armour.points
                    
                    # Add weapon
                    weapon = Weapon.query.get(weapon_id)
                    if weapon:
                        cost_per_trooper += weapon.points
                    
                    # Apply Quality and Resolve multipliers
                    cost_per_trooper = cost_per_trooper * (1 + quality_mult + resolve_mult)
                    
                    # Add to total
                    total_points += cost_per_trooper * quantity
                    
            except (json.JSONDecodeError, ValueError, TypeError):
                # Fall back to default weapon
                weapon_distribution = None
        
        # If no distribution, use default weapon for all
        if not weapon_distribution or weapon_distribution == '{}':
            # Step 1: Base cost per trooper = 3 points
            cost_per_trooper = 3
            
            # Step 2: Add armour per trooper
            if armour_id:
                armour = Armour.query.get(armour_id)
                if armour:
                    cost_per_trooper += armour.points
            
            # Step 3: Add weapon per trooper
            if data.get('basic_weapon_id'):
                weapon = Weapon.query.get(data['basic_weapon_id'])
                if weapon:
                    cost_per_trooper += weapon.points
            
            # Step 4: Apply Quality and Resolve multipliers
            cost_per_trooper = cost_per_trooper * (1 + quality_mult + resolve_mult)
            
            # Step 5: Multiply by squad size
            total_points = cost_per_trooper * squad_size
        
        # Step 6: Apply trait multipliers sequentially (per game rules)
        if data.get('traits'):
            for trait_id in data['traits']:
                trait = Trait.query.get(trait_id)
                if trait:
                    total_points *= trait.points_multiplier
    
    # ==================== CHARACTER ====================
    elif unit_type == 'Character':
        # Step 1: Base cost = 3 points
        total_points = 3
        
        # Step 2: Add armour
        if data.get('armour_id'):
            armour = Armour.query.get(data['armour_id'])
            if armour:
                total_points += armour.points
        
        # Step 3: Add weapon
        if data.get('basic_weapon_id'):
            weapon = Weapon.query.get(data['basic_weapon_id'])
            if weapon:
                total_points += weapon.points
        
        # Step 4: Add personality
        if data.get('has_personality'):
            total_points += 1
        
        # Step 5: Add leadership rating
        leadership_points = {
            'Novice': 0,
            'Experienced': 3,
            'Inspiring': 8,
            'Heroic': 15
        }
        leadership = data.get('leadership_rating', 'Novice')
        total_points += leadership_points.get(leadership, 0)
        
        # Step 6: Apply Quality and Resolve multipliers
        total_points = total_points * (1 + quality_mult + resolve_mult)
        
        # Step 7: Apply trait multipliers sequentially (per game rules)
        if data.get('traits'):
            for trait_id in data['traits']:
                trait = Trait.query.get(trait_id)
                if trait:
                    total_points *= trait.points_multiplier
    
    # ==================== HEAVY WEAPON ====================
    elif unit_type == 'HeavyWeapon':
        # Step 1: Base cost = 2 points × crew count
        crew_count = data.get('crew_count', 2)
        total_points = 2 * crew_count
        
        # Step 2: Add armour
        if data.get('armour_id'):
            armour = Armour.query.get(data['armour_id'])
            if armour:
                total_points += armour.points
        
        # Step 3: Add heavy weapon
        if data.get('heavy_weapon_id'):
            weapon = Weapon.query.get(data['heavy_weapon_id'])
            if weapon:
                total_points += weapon.points
        
        # Step 4: Apply Quality and Resolve multipliers
        total_points = total_points * (1 + quality_mult + resolve_mult)
        
        # Step 5: Apply trait multipliers sequentially (per game rules)
        if data.get('traits'):
            for trait_id in data['traits']:
                trait = Trait.query.get(trait_id)
                if trait:
                    total_points *= trait.points_multiplier
    
    # ==================== SNIPER ====================
    elif unit_type == 'Sniper':
        # Step 1: Base cost = 3 points
        total_points = 3
        
        # Step 2: Add armour
        if data.get('armour_id'):
            armour = Armour.query.get(data['armour_id'])
            if armour:
                total_points += armour.points
        
        # Step 3: Add weapon (sniper rifle)
        if data.get('basic_weapon_id'):
            weapon = Weapon.query.get(data['basic_weapon_id'])
            if weapon:
                total_points += weapon.points
        
        # Step 4: Add personality
        if data.get('has_personality'):
            total_points += 1
        
        # Step 5: Apply Quality and Resolve multipliers
        total_points = total_points * (1 + quality_mult + resolve_mult)
        
        # Step 6: Apply trait multipliers sequentially (per game rules)
        if data.get('traits'):
            for trait_id in data['traits']:
                trait = Trait.query.get(trait_id)
                if trait:
                    total_points *= trait.points_multiplier
    
    # ==================== PSIONIC ====================
    elif unit_type == 'Psionic':
        # Psionic aptitude base costs
        aptitude_base_costs = {
            'Marginal': 5,
            'Competent': 10,
            'Expert': 15,
            'Master': 20
        }
        
        # Step 1: Base cost = 3 points
        total_points = 3
        
        # Step 2: Add armour
        if data.get('armour_id'):
            armour = Armour.query.get(data['armour_id'])
            if armour:
                total_points += armour.points
        
        # Step 3: Add weapon (optional backup)
        if data.get('basic_weapon_id'):
            weapon = Weapon.query.get(data['basic_weapon_id'])
            if weapon:
                total_points += weapon.points
        
        # Step 4: Add personality
        if data.get('has_personality'):
            total_points += 1
        
        # Step 5: Apply Quality and Resolve multipliers
        total_points = total_points * (1 + quality_mult + resolve_mult)
        
        # Step 6: Add psionic aptitude (after multipliers)
        aptitude = data.get('psionic_aptitude', 'Marginal')
        total_points += aptitude_base_costs.get(aptitude, 5)
        
        # Step 7: Add psionic strength (2 pts per level)
        strength = data.get('psionic_strength', 0)
        total_points += strength * 2
        
        # Step 8: Apply trait multipliers sequentially (per game rules)
        if data.get('traits'):
            for trait_id in data['traits']:
                trait = Trait.query.get(trait_id)
                if trait:
                    total_points *= trait.points_multiplier
    
    # ==================== VEHICLE ====================
    elif unit_type == 'Vehicle':
        # Step 1: Base cost = 10 points for vehicle
        total_points = 10
        
        # Step 2: Add armour (average × 3)
        front = data.get('vehicle_armour_front', 0)
        side = data.get('vehicle_armour_side', 0)
        rear = data.get('vehicle_armour_rear', 0)
        avg_armour = (front + side + rear) / 3
        total_points += avg_armour * 3
        
        # Step 3: Add movement type
        movement_points = {
            'Fly': 15,
            'Hover': 10,
            'Wheeled': 8,
            'Tracked': 5,
            'Walk': 3
        }
        movement = data.get('movement_type', 'Tracked')
        total_points += movement_points.get(movement, 5)
        
        # Step 4: Add transport capacity (2 pts per slot)
        capacity = data.get('carrying_capacity', 0)
        total_points += capacity * 2
        
        # Step 5: Add weapons
        if data.get('basic_weapon_id'):
            weapon = Weapon.query.get(data['basic_weapon_id'])
            if weapon:
                total_points += weapon.points
        
        if data.get('secondary_weapon_id'):
            weapon = Weapon.query.get(data['secondary_weapon_id'])
            if weapon:
                total_points += weapon.points
        
        # Step 6: Apply Quality and Resolve multipliers
        total_points = total_points * (1 + quality_mult + resolve_mult)
        
        # Step 7: Apply trait/property multipliers sequentially (per game rules)
        if data.get('traits'):
            for trait_id in data['traits']:
                trait = Trait.query.get(trait_id)
                if trait:
                    total_points *= trait.points_multiplier
    
    return round(total_points, 2)


    # ==================== SQUAD MEMBER MANAGEMENT ====================
    @app.route('/unit/<int:unit_id>/squad-members', methods=['GET'])
    @login_required
    def manage_squad_members(unit_id):
        """View and manage individual squad members"""
        unit = Unit.query.get_or_404(unit_id)
        
        if unit.user_id != current_user.id:
            abort(403)
        
        if unit.unit_type != 'Squad':
            flash('This unit is not a squad', 'warning')
            return redirect(url_for('dashboard'))
        
        weapons = Weapon.query.order_by(Weapon.category, Weapon.points).all()
        squad_members = SquadMember.query.filter_by(unit_id=unit_id).order_by(SquadMember.member_number).all()
        
        return render_template('manage_squad_members.html', 
                             unit=unit, 
                             squad_members=squad_members,
                             weapons=weapons)
    
    @app.route('/unit/<int:unit_id>/squad-member/add', methods=['POST'])
    @login_required
    def add_squad_member(unit_id):
        """Add a new squad member"""
        unit = Unit.query.get_or_404(unit_id)
        
        if unit.user_id != current_user.id:
            abort(403)
        
        if unit.unit_type != 'Squad':
            return jsonify({'success': False, 'message': 'Not a squad unit'}), 400
        
        try:
            member_number = request.form.get('member_number', type=int)
            member_type = request.form.get('member_type', 'Regular')
            weapon_id = request.form.get('weapon_id', type=int) or None
            secondary_weapon_id = request.form.get('secondary_weapon_id', type=int) or None
            notes = request.form.get('notes', '').strip()
            
            member = SquadMember(
                unit_id=unit_id,
                member_number=member_number,
                member_type=member_type,
                weapon_id=weapon_id,
                secondary_weapon_id=secondary_weapon_id,
                notes=notes
            )
            
            db.session.add(member)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Squad member added'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/squad-member/<int:member_id>/edit', methods=['POST'])
    @login_required
    def edit_squad_member(member_id):
        """Edit an existing squad member"""
        member = SquadMember.query.get_or_404(member_id)
        unit = Unit.query.get_or_404(member.unit_id)
        
        if unit.user_id != current_user.id:
            abort(403)
        
        try:
            member.member_type = request.form.get('member_type', 'Regular')
            member.weapon_id = request.form.get('weapon_id', type=int) or None
            member.secondary_weapon_id = request.form.get('secondary_weapon_id', type=int) or None
            member.notes = request.form.get('notes', '').strip()
            
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Squad member updated'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/squad-member/<int:member_id>/delete', methods=['POST'])
    @login_required
    def delete_squad_member(member_id):
        """Delete a squad member"""
        member = SquadMember.query.get_or_404(member_id)
        unit = Unit.query.get_or_404(member.unit_id)
        
        if unit.user_id != current_user.id:
            abort(403)
        
        try:
            db.session.delete(member)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Squad member deleted'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500

