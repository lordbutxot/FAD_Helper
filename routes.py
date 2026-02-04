"""
Application routes for F.A.D. List Builder
"""

from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from extensions import db
from models import User, ArmyList, Unit, Weapon, Armour, Trait, Faction
from datetime import datetime, timedelta
from functools import wraps
import json
import re
import os
import uuid

VEHICLE_WEAPON_NAMES = None

def load_vehicle_weapon_names():
    """Load vehicle weapon names from Vehicle Table.TXT"""
    global VEHICLE_WEAPON_NAMES
    if VEHICLE_WEAPON_NAMES is not None:
        return VEHICLE_WEAPON_NAMES

    file_path = os.path.join(os.path.dirname(__file__), 'Vehicle Table.TXT')
    names = []

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file.readlines()]

        start_idx = None
        for i, line in enumerate(lines):
            if line.lower() == 'select weapons':
                start_idx = i + 1
                break

        if start_idx is None:
            for i, line in enumerate(lines):
                if line.lower() == 'weapons':
                    start_idx = i + 1
                    break

        if start_idx is not None:
            for line in lines[start_idx:]:
                if not line:
                    continue
                names.append(line.replace('Morter', 'Mortar'))
    except Exception:
        names = []

    VEHICLE_WEAPON_NAMES = names
    return names

def get_vehicle_weapons():
    """Get ordered list of vehicle weapons defined in Vehicle Table.TXT"""
    names = load_vehicle_weapon_names()
    if not names:
        return []

    weapons = Weapon.query.filter(Weapon.name.in_(names)).all()
    weapon_map = {weapon.name: weapon for weapon in weapons}
    return [weapon_map[name] for name in names if name in weapon_map]


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
        recent_lists = ArmyList.query.filter_by(is_public=True).order_by(ArmyList.created_at.desc()).limit(6).all()
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
            user = User(  # type: ignore
                username=username,
                email=email,
                password_hash=generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
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
        
        return render_template('view_faction.html', faction=faction, units=units, lists=lists, playstyle_tags=PLAYSTYLE_TAGS)
    
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
        armours = Armour.query.order_by(Armour.points).all()
        traits = Trait.query.order_by(Trait.category, Trait.name).all()
        vehicle_weapons = get_vehicle_weapons()

        primary_weapon_id = None
        secondary_weapon_id = None
        if unit.unit_type == 'Vehicle' and unit.vehicle_weapons_json:
            try:
                weapon_ids = json.loads(unit.vehicle_weapons_json)
                if len(weapon_ids) > 0:
                    primary_weapon_id = weapon_ids[0]
                if len(weapon_ids) > 1:
                    secondary_weapon_id = weapon_ids[1]
            except Exception:
                primary_weapon_id = None
                secondary_weapon_id = None
        
        if request.method == 'POST':
            try:
                # Get form data
                name = request.form.get('name', '').strip()
                faction = request.form.get('faction', '').strip()
                quality = request.form.get('quality')
                resolve = request.form.get('resolve')
                squad_size = int(request.form.get('squad_size', 5))
                armour_id = request.form.get('armour_id') or None
                basic_weapon_id = request.form.get('basic_weapon_id') or None
                trait_ids = request.form.getlist('traits')
                notes = request.form.get('notes', '').strip()
                
                # Calculate points
                data = {
                    'unit_type': 'Squad',
                    'quality': quality,
                    'squad_size': squad_size,
                    'armour_id': int(armour_id) if armour_id else None,
                    'basic_weapon_id': int(basic_weapon_id) if basic_weapon_id else None,
                    'traits': [int(t) for t in trait_ids]
                }
                total_points = calculate_points(data)
                
                # Create unit
                unit = Unit(  # type: ignore
                    user_id=current_user.id,
                    name=name,
                    unit_type='Squad',
                    faction=faction,
                    quality=quality,
                    resolve=resolve,
                    squad_size=squad_size,
                    armour_id=int(armour_id) if armour_id else None,
                    basic_weapon_id=int(basic_weapon_id) if basic_weapon_id else None,
                    traits_json=json.dumps([int(t) for t in trait_ids]),
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
        
        return render_template('squad_builder.html', weapons=weapons, armours=armours, traits=traits)
    
    # ==================== CHARACTER BUILDER ====================
    @app.route('/unit/builder/character', methods=['GET', 'POST'])
    @login_required
    def character_builder():
        weapons = Weapon.query.order_by(Weapon.category, Weapon.points).all()
        armours = Armour.query.order_by(Armour.points).all()
        traits = Trait.query.order_by(Trait.category, Trait.name).all()
        
        if request.method == 'POST':
            try:
                name = request.form.get('name', '').strip()
                faction = request.form.get('faction', '').strip()
                quality = request.form.get('quality')
                resolve = request.form.get('resolve')
                has_personality = request.form.get('has_personality') == 'true'
                leadership_rating = request.form.get('leadership_rating')
                specialization = request.form.get('specialization')
                armour_id = request.form.get('armour_id') or None
                basic_weapon_id = request.form.get('basic_weapon_id') or None
                trait_ids = request.form.getlist('traits')
                notes = request.form.get('notes', '').strip()
                
                # Calculate points
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
                    faction=faction,
                    quality=quality,
                    resolve=resolve,
                    has_personality=has_personality,
                    leadership_rating=leadership_rating,
                    specialization=specialization,
                    armour_id=int(armour_id) if armour_id else None,
                    basic_weapon_id=int(basic_weapon_id) if basic_weapon_id else None,
                    traits_json=json.dumps([int(t) for t in trait_ids]),
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
        
        return render_template('character_builder.html', weapons=weapons, armours=armours, traits=traits)
    
    # ==================== HEAVY WEAPONS TEAM BUILDER ====================
    @app.route('/unit/builder/heavy-weapon', methods=['GET', 'POST'])
    @login_required
    def heavy_weapon_builder():
        weapons = Weapon.query.order_by(Weapon.category, Weapon.points).all()
        armours = Armour.query.order_by(Armour.points).all()
        traits = Trait.query.order_by(Trait.category, Trait.name).all()
        
        if request.method == 'POST':
            try:
                name = request.form.get('name', '').strip()
                faction = request.form.get('faction', '').strip()
                quality = request.form.get('quality')
                resolve = request.form.get('resolve')
                heavy_weapon_id = request.form.get('heavy_weapon_id') or None
                armour_id = request.form.get('armour_id') or None
                trait_ids = request.form.getlist('traits')
                notes = request.form.get('notes', '').strip()
                
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
                    faction=faction,
                    quality=quality,
                    resolve=resolve,
                    heavy_weapon_id=int(heavy_weapon_id) if heavy_weapon_id else None,
                    armour_id=int(armour_id) if armour_id else None,
                    traits_json=json.dumps([int(t) for t in trait_ids]),
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
        
        return render_template('heavy_weapon_builder.html', weapons=weapons, armours=armours, traits=traits)
    
    # ==================== SNIPER BUILDER ====================
    @app.route('/unit/builder/sniper', methods=['GET', 'POST'])
    @login_required
    def sniper_builder():
        weapons = Weapon.query.order_by(Weapon.category, Weapon.points).all()
        armours = Armour.query.order_by(Armour.points).all()
        traits = Trait.query.order_by(Trait.category, Trait.name).all()
        
        if request.method == 'POST':
            try:
                name = request.form.get('name', '').strip()
                faction = request.form.get('faction', '').strip()
                quality = request.form.get('quality')
                resolve = request.form.get('resolve')
                has_personality = request.form.get('has_personality') == 'true'
                basic_weapon_id = request.form.get('basic_weapon_id') or None
                armour_id = request.form.get('armour_id') or None
                trait_ids = request.form.getlist('traits')
                notes = request.form.get('notes', '').strip()
                
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
                    faction=faction,
                    quality=quality,
                    resolve=resolve,
                    has_personality=has_personality,
                    basic_weapon_id=int(basic_weapon_id) if basic_weapon_id else None,
                    armour_id=int(armour_id) if armour_id else None,
                    traits_json=json.dumps([int(t) for t in trait_ids]),
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
        
        return render_template('sniper_builder.html', weapons=weapons, armours=armours, traits=traits)
    
    # ==================== PSIONIC BUILDER ====================
    @app.route('/unit/builder/psionic', methods=['GET', 'POST'])
    @login_required
    def psionic_builder():
        weapons = Weapon.query.order_by(Weapon.category, Weapon.points).all()
        armours = Armour.query.order_by(Armour.points).all()
        traits = Trait.query.order_by(Trait.category, Trait.name).all()
        
        if request.method == 'POST':
            try:
                name = request.form.get('name', '').strip()
                faction = request.form.get('faction', '').strip()
                quality = request.form.get('quality')
                resolve = request.form.get('resolve')
                has_personality = request.form.get('has_personality') == 'true'
                psionic_aptitude = request.form.get('psionic_aptitude')
                psionic_strength = int(request.form.get('psionic_strength', 3))
                basic_weapon_id = request.form.get('basic_weapon_id') or None
                armour_id = request.form.get('armour_id') or None
                trait_ids = request.form.getlist('traits')
                notes = request.form.get('notes', '').strip()
                
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
                    faction=faction,
                    quality=quality,
                    resolve=resolve,
                    has_personality=has_personality,
                    psionic_aptitude=psionic_aptitude,
                    psionic_strength=psionic_strength,
                    basic_weapon_id=int(basic_weapon_id) if basic_weapon_id else None,
                    armour_id=int(armour_id) if armour_id else None,
                    traits_json=json.dumps([int(t) for t in trait_ids]),
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
        
        return render_template('psionic_builder.html', weapons=weapons, armours=armours, traits=traits)
    
    # ==================== VEHICLE BUILDER ====================
    @app.route('/unit/builder/vehicle', methods=['GET', 'POST'])
    @login_required
    def vehicle_builder():
        weapons = Weapon.query.order_by(Weapon.category, Weapon.points).all()
        armours = Armour.query.order_by(Armour.points).all()
        traits = Trait.query.order_by(Trait.category, Trait.name).all()
        vehicle_weapons = get_vehicle_weapons()
        
        if request.method == 'POST':
            try:
                name = request.form.get('name', '').strip()
                faction = request.form.get('faction', '').strip()
                vehicle_type = request.form.get('vehicle_type')
                quality = request.form.get('quality')
                resolve = request.form.get('resolve')
                movement_type = request.form.get('movement_type')
                front_armour = int(request.form.get('vehicle_armour_front', 3))
                side_armour = int(request.form.get('vehicle_armour_side', 2))
                rear_armour = int(request.form.get('vehicle_armour_rear', 1))
                crew_size = int(request.form.get('crew_size', 2))
                capacity = int(request.form.get('carrying_capacity', 0))
                properties = request.form.get('vehicle_properties', '').strip()
                primary_weapon_id = request.form.get('primary_weapon_id') or None
                secondary_weapon_id = request.form.get('secondary_weapon_id') or None
                notes = request.form.get('notes', '').strip()
                
                # Parse properties (comma-separated)
                props_list = [p.strip() for p in properties.split(',') if p.strip()] if properties else []
                
                # Calculate points
                data = {
                    'unit_type': 'Vehicle',
                    'quality': quality,
                    'movement_type': movement_type,
                    'vehicle_armour_front': front_armour,
                    'vehicle_armour_side': side_armour,
                    'vehicle_armour_rear': rear_armour,
                    'carrying_capacity': capacity,
                    'primary_weapon_id': int(primary_weapon_id) if primary_weapon_id else None,
                    'secondary_weapon_id': int(secondary_weapon_id) if secondary_weapon_id else None
                }
                total_points = calculate_points(data)
                
                unit = Unit(  # type: ignore
                    user_id=current_user.id,
                    name=name,
                    unit_type='Vehicle',
                    faction=faction,
                    vehicle_type=vehicle_type,
                    quality=quality,
                    resolve=resolve,
                    movement_type=movement_type,
                    vehicle_armour_front=front_armour,
                    vehicle_armour_side=side_armour,
                    vehicle_armour_rear=rear_armour,
                    crew_size=crew_size,
                    carrying_capacity=capacity,
                    vehicle_weapons_json=json.dumps([
                        int(w) for w in [primary_weapon_id, secondary_weapon_id] if w
                    ]),
                    vehicle_properties_json=json.dumps(props_list),
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
        
        return render_template(
            'vehicle_builder.html',
            weapons=weapons,
            armours=armours,
            traits=traits,
            vehicle_weapons=vehicle_weapons
        )
    
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
        armours = Armour.query.order_by(Armour.points).all()
        traits = Trait.query.order_by(Trait.category, Trait.name).all()
        
        if request.method == 'POST':
            try:
                # Common fields for all unit types
                unit.name = request.form.get('name', '').strip()
                unit.faction = request.form.get('faction', '').strip()
                unit.quality = request.form.get('quality')
                unit.resolve = request.form.get('resolve')
                unit.notes = request.form.get('notes', '').strip()
                
                # Type-specific fields
                if unit.unit_type == 'Squad':
                    unit.squad_size = int(request.form.get('squad_size', 5))
                    unit.armour_id = request.form.get('armour_id') or None
                    unit.basic_weapon_id = request.form.get('basic_weapon_id') or None
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

                    primary_weapon_id = request.form.get('primary_weapon_id') or None
                    secondary_weapon_id = request.form.get('secondary_weapon_id') or None
                    unit.vehicle_weapons_json = json.dumps([
                        int(w) for w in [primary_weapon_id, secondary_weapon_id] if w
                    ])
                    
                    properties = request.form.get('vehicle_properties', '').strip()
                    props_list = [p.strip() for p in properties.split(',') if p.strip()] if properties else []
                    unit.vehicle_properties_json = json.dumps(props_list)
                    
                    data = {
                        'unit_type': 'Vehicle',
                        'quality': unit.quality,
                        'movement_type': unit.movement_type,
                        'vehicle_armour_front': unit.vehicle_armour_front,
                        'vehicle_armour_side': unit.vehicle_armour_side,
                        'vehicle_armour_rear': unit.vehicle_armour_rear,
                        'carrying_capacity': unit.carrying_capacity,
                        'primary_weapon_id': int(primary_weapon_id) if primary_weapon_id else None,
                        'secondary_weapon_id': int(secondary_weapon_id) if secondary_weapon_id else None
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
        return render_template(
            template,
            unit=unit,
            weapons=weapons,
            armours=armours,
            traits=traits,
            vehicle_weapons=vehicle_weapons,
            primary_weapon_id=primary_weapon_id,
            secondary_weapon_id=secondary_weapon_id
        )
    
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
        my_units = Unit.query.filter_by(user_id=current_user.id).order_by(Unit.faction, Unit.name).all()
        public_units = Unit.query.filter_by(is_public=True).order_by(Unit.faction, Unit.name).all()
        return render_template('list_builder.html', my_units=my_units, public_units=public_units)
    
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
            army_list.faction = data.get('faction', '')
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
        
        my_units = Unit.query.filter_by(user_id=current_user.id).order_by(Unit.faction, Unit.name).all()
        public_units = Unit.query.filter_by(is_public=True).order_by(Unit.faction, Unit.name).all()
        
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
    
    @app.route('/browse')
    def browse_lists():
        faction = request.args.get('faction', '')
        search = request.args.get('search', '')
        
        query = ArmyList.query.filter_by(is_public=True)
        
        if faction:
            query = query.filter(ArmyList.faction == faction)
        
        if search:
            query = query.filter(ArmyList.name.contains(search) | ArmyList.description.contains(search))
        
        lists = query.order_by(ArmyList.created_at.desc()).all()
        
        factions = db.session.query(ArmyList.faction).filter(ArmyList.is_public == True).distinct().all()
        factions = [f[0] for f in factions if f[0]]
        
        return render_template('browse.html', lists=lists, factions=factions, selected_faction=faction, search=search)
    
    @app.route('/armoury')
    def armoury():
        weapons = Weapon.query.order_by(Weapon.category, Weapon.points).all()
        armours = Armour.query.order_by(Armour.points).all()
        traits = Trait.query.order_by(Trait.category, Trait.name).all()
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
    
    # Quality base points (from Rules)
    quality_points = {
        'Rabble': 4,
        'Conscript': 6,
        'Regular': 8,
        'Elite': 10
    }
    
    quality = data.get('quality', 'Regular')
    base_points = quality_points.get(quality, 8)
    
    # Initialize total
    total_points = 0
    
    # ==================== SQUAD ====================
    if unit_type == 'Squad':
        squad_size = data.get('squad_size', 5)
        # Base points × squad size
        total_points = base_points * squad_size
        
        # Equipment per squad member
        if data.get('armour_id'):
            armour = Armour.query.get(data['armour_id'])
            if armour:
                total_points += armour.points * squad_size
        
        if data.get('basic_weapon_id'):
            weapon = Weapon.query.get(data['basic_weapon_id'])
            if weapon:
                total_points += weapon.points * squad_size
        
        # Traits (flat cost, not multiplied)
        if data.get('traits'):
            for trait_id in data['traits']:
                trait = Trait.query.get(trait_id)
                if trait:
                    total_points += trait.points_modifier
    
    # ==================== CHARACTER ====================
    elif unit_type == 'Character':
        total_points = base_points
        
        # Leadership rating
        leadership_points = {
            'Novice': 0,
            'Experienced': 10,
            'Inspiring': 20,
            'Heroic': 30
        }
        leadership = data.get('leadership_rating', 'Novice')
        total_points += leadership_points.get(leadership, 0)
        
        # Personality
        if data.get('has_personality'):
            total_points += 5
        
        # Equipment (single model)
        if data.get('armour_id'):
            armour = Armour.query.get(data['armour_id'])
            if armour:
                total_points += armour.points
        
        if data.get('basic_weapon_id'):
            weapon = Weapon.query.get(data['basic_weapon_id'])
            if weapon:
                total_points += weapon.points
        
        # Traits
        if data.get('traits'):
            for trait_id in data['traits']:
                trait = Trait.query.get(trait_id)
                if trait:
                    total_points += trait.points_modifier
    
    # ==================== HEAVY WEAPON ====================
    elif unit_type == 'HeavyWeapon':
        total_points = base_points
        
        # Heavy weapon
        if data.get('heavy_weapon_id'):
            weapon = Weapon.query.get(data['heavy_weapon_id'])
            if weapon:
                total_points += weapon.points
        
        # Armour
        if data.get('armour_id'):
            armour = Armour.query.get(data['armour_id'])
            if armour:
                total_points += armour.points
        
        # Traits
        if data.get('traits'):
            for trait_id in data['traits']:
                trait = Trait.query.get(trait_id)
                if trait:
                    total_points += trait.points_modifier
    
    # ==================== SNIPER ====================
    elif unit_type == 'Sniper':
        total_points = base_points
        
        # Personality
        if data.get('has_personality'):
            total_points += 5
        
        # Equipment
        if data.get('basic_weapon_id'):
            weapon = Weapon.query.get(data['basic_weapon_id'])
            if weapon:
                total_points += weapon.points
        
        if data.get('armour_id'):
            armour = Armour.query.get(data['armour_id'])
            if armour:
                total_points += armour.points
        
        # Traits
        if data.get('traits'):
            for trait_id in data['traits']:
                trait = Trait.query.get(trait_id)
                if trait:
                    total_points += trait.points_modifier
    
    # ==================== PSIONIC ====================
    elif unit_type == 'Psionic':
        total_points = base_points
        
        # Psionic aptitude
        aptitude_points = {
            'Marginal': 10,
            'Competent': 20,
            'Expert': 30,
            'Master': 40
        }
        aptitude = data.get('psionic_aptitude', 'Marginal')
        total_points += aptitude_points.get(aptitude, 10)
        
        # Psionic strength (5 pts per level)
        strength = data.get('psionic_strength', 0)
        total_points += strength * 5
        
        # Personality
        if data.get('has_personality'):
            total_points += 5
        
        # Equipment (optional backup)
        if data.get('basic_weapon_id'):
            weapon = Weapon.query.get(data['basic_weapon_id'])
            if weapon:
                total_points += weapon.points
        
        if data.get('armour_id'):
            armour = Armour.query.get(data['armour_id'])
            if armour:
                total_points += armour.points
        
        # Traits
        if data.get('traits'):
            for trait_id in data['traits']:
                trait = Trait.query.get(trait_id)
                if trait:
                    total_points += trait.points_modifier
    
    # ==================== VEHICLE ====================
    elif unit_type == 'Vehicle':
        total_points = base_points
        
        # Movement type
        movement_points = {
            'Fly': 15,
            'Hover': 10,
            'Wheeled': 8,
            'Tracked': 5,
            'Walk': 3
        }
        movement = data.get('movement_type', 'Tracked')
        total_points += movement_points.get(movement, 5)
        
        # Armour (5 pts per armour point, directional)
        front = data.get('vehicle_armour_front', 0)
        side = data.get('vehicle_armour_side', 0)
        rear = data.get('vehicle_armour_rear', 0)
        total_points += (front + side + rear) * 5
        
        # Transport capacity (2 pts per slot)
        capacity = data.get('carrying_capacity', 0)
        total_points += capacity * 2
        
        # Vehicle weapons
        primary_weapon_id = data.get('primary_weapon_id')
        secondary_weapon_id = data.get('secondary_weapon_id')
        for weapon_id in [primary_weapon_id, secondary_weapon_id]:
            if weapon_id:
                weapon = Weapon.query.get(weapon_id)
                if weapon:
                    total_points += weapon.points
    
    return round(total_points, 2)
