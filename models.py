"""
Database models for F.A.D. List Builder
"""

from extensions import db
from flask_login import UserMixin
from datetime import datetime
import json

class User(UserMixin, db.Model):
    """User accounts for the application"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)  # Email is now optional
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    failed_login_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime)
    
    # Relationships
    factions = db.relationship('Faction', backref='user', lazy=True, cascade='all, delete-orphan')
    army_lists = db.relationship('ArmyList', backref='owner', lazy=True, cascade='all, delete-orphan')
    custom_units = db.relationship('Unit', backref='creator', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'


class Faction(db.Model):
    """Factions that contain units and army lists"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#0d6efd')  # Hex color for UI display
    icon = db.Column(db.String(50), default='shield')  # Bootstrap icon name
    logo_filename = db.Column(db.String(255))  # Uploaded logo image filename
    playstyle_tags = db.Column(db.Text)  # JSON list of tactical playstyle tags
    background = db.Column(db.Text)  # Lore/background information
    special_rules = db.Column(db.Text)  # Faction-wide special rules
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    units = db.relationship('Unit', backref='faction_obj', lazy=True, foreign_keys='Unit.faction_id')
    army_lists = db.relationship('ArmyList', backref='faction_obj', lazy=True, foreign_keys='ArmyList.faction_id')
    
    def get_playstyle_tags(self):
        """Get list of playstyle tags for this faction"""
        if not self.playstyle_tags:
            return []
        return json.loads(self.playstyle_tags)
    
    def __repr__(self):
        return f'<Faction {self.name}>'
    
    def get_total_units(self):
        """Get total number of units in this faction"""
        return len(self.units)
    
    def get_total_lists(self):
        """Get total number of army lists in this faction"""
        return len(self.army_lists)


class Weapon(db.Model):
    """Weapons available in the game"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Basic, Support, Heavy
    range_multiplier = db.Column(db.Integer, nullable=False)
    damage = db.Column(db.Integer, nullable=False)
    fire_effect = db.Column(db.Integer, default=0)
    armor_piercing = db.Column(db.Integer, default=0)
    special_rules = db.Column(db.Text)  # JSON string for special abilities
    points = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<Weapon {self.name}>'


class Armour(db.Model):
    """Armour types available in the game"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    special_rules = db.Column(db.Text)
    points = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<Armour {self.name}>'


class Trait(db.Model):
    """Special traits/abilities for units"""
    __table_args__ = (
        db.UniqueConstraint('name', 'category', name='uq_trait_name_category'),
    )
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    points_multiplier = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))  # Infantry, Vehicle, Character, etc.
    is_repeatable = db.Column(db.Boolean, default=False)  # Can this trait be taken multiple times?
    
    def __repr__(self):
        return f'<Trait {self.name}>'


class Unit(db.Model):
    """Custom units created by users - Supports 6 unit types: Squad, Character, Sniper, Heavy Weapons, Psionic, Vehicle"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    faction_id = db.Column(db.Integer, db.ForeignKey('faction.id'), nullable=True)  # Optional: can be unassigned
    name = db.Column(db.String(100), nullable=False)
    unit_type = db.Column(db.String(50), nullable=False)  # Squad, Character, Sniper, HeavyWeapon, Psionic, Vehicle
    
    # Base stats (all units)
    quality = db.Column(db.String(20), nullable=False)  # Rabble, Conscript, Regular, Elite
    resolve = db.Column(db.String(20), nullable=False)  # Reluctant, Uncertain, Steady, Determined
    
    # Squad-specific (Infantry squads only)
    squad_size = db.Column(db.Integer, default=1)
    squad_members_json = db.Column(db.Text)  # JSON list of squad members with individual equipment
    
    # Character-specific
    has_personality = db.Column(db.Boolean, default=False)
    leadership_rating = db.Column(db.String(20))  # Novice, Experienced, Inspiring, Heroic
    specialization = db.Column(db.String(20))  # Infantry, Gunnery, Cavalry
    
    # Equipment (shared)
    armour_id = db.Column(db.Integer, db.ForeignKey('armour.id'))
    basic_weapon_id = db.Column(db.Integer, db.ForeignKey('weapon.id'))
    
    # Heavy Weapons Team specific
    heavy_weapon_id = db.Column(db.Integer, db.ForeignKey('weapon.id'), nullable=True)
    weapon_options_json = db.Column(db.Text)  # JSON list of additional weapon options
    
    # Psionic specific
    psionic_aptitude = db.Column(db.String(20))  # Marginal, Competent, Expert, Master
    psionic_strength = db.Column(db.Integer, default=0)  # 1-6
    
    # Vehicle specific
    vehicle_type = db.Column(db.String(50))  # Light Transport, Medium Tank, Heavy Tank, Walker, etc.
    movement_type = db.Column(db.String(20))  # Fly, Hover, Tracked, Walk, Wheeled
    vehicle_armour_front = db.Column(db.Integer)
    vehicle_armour_side = db.Column(db.Integer)
    vehicle_armour_rear = db.Column(db.Integer)
    crew_size = db.Column(db.Integer)
    carrying_capacity = db.Column(db.Integer)
    vehicle_weapons_json = db.Column(db.Text)  # JSON list of vehicle weapons
    vehicle_properties_json = db.Column(db.Text)  # JSON list of vehicle properties/traits
    
    # Traits (stored as JSON list of trait IDs) - used by Squad, Character, Sniper, Heavy Weapons, Psionic
    traits_json = db.Column(db.Text)  # JSON list: [1, 5, 12]
    
    # Calculated values
    base_points = db.Column(db.Float, nullable=False)
    total_points = db.Column(db.Float, nullable=False)
    
    # Metadata
    is_public = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)  # User notes about the unit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    armour = db.relationship('Armour', foreign_keys=[armour_id])
    basic_weapon = db.relationship('Weapon', foreign_keys=[basic_weapon_id])
    heavy_weapon = db.relationship('Weapon', foreign_keys=[heavy_weapon_id])
    
    def get_traits(self):
        """Get list of trait objects for this unit"""
        if not self.traits_json:
            return []
        trait_ids = json.loads(self.traits_json)
        return Trait.query.filter(Trait.id.in_(trait_ids)).all()
    
    def get_squad_members(self):
        """Get list of squad members (for Squad type only)"""
        if not self.squad_members_json or self.unit_type != 'Squad':
            return []
        return json.loads(self.squad_members_json)
    
    def get_vehicle_weapons(self):
        """Get list of vehicle weapons (for Vehicle type only)"""
        if not self.vehicle_weapons_json or self.unit_type != 'Vehicle':
            return []
        weapon_ids = json.loads(self.vehicle_weapons_json)
        return Weapon.query.filter(Weapon.id.in_(weapon_ids)).all()
    
    def get_vehicle_properties(self):
        """Get list of vehicle properties/traits (for Vehicle type only)"""
        if not self.vehicle_properties_json or self.unit_type != 'Vehicle':
            return []
        return json.loads(self.vehicle_properties_json)
    
    def __repr__(self):
        return f'<Unit {self.name} ({self.unit_type})>'


class ArmyList(db.Model):
    """Army lists created by users"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    faction_id = db.Column(db.Integer, db.ForeignKey('faction.id'), nullable=True)  # Optional: can be unassigned
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Units in the list (stored as JSON)
    units_json = db.Column(db.Text, nullable=False)  # JSON: [{"unit_id": 5, "quantity": 2}, ...]
    
    # Calculated totals
    total_points = db.Column(db.Float, nullable=False, default=0)
    total_units = db.Column(db.Integer, nullable=False, default=0)
    
    # Sharing settings
    is_public = db.Column(db.Boolean, default=False)
    views = db.Column(db.Integer, default=0)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_units(self):
        """Get list of units with their quantities"""
        if not self.units_json:
            return []
        units_data = json.loads(self.units_json)
        result = []
        for item in units_data:
            unit = Unit.query.get(item['unit_id'])
            if unit:
                result.append({
                    'unit': unit,
                    'quantity': item['quantity']
                })
        return result
    
    def __repr__(self):
        return f'<ArmyList {self.name}>'
