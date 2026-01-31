# F.A.D. Helper

**F.A.D. Helper** is a comprehensive web-based army list builder for the **F.A.D. (Fast and Dirty)** tabletop wargame. Build legal armies faster with official game data, intuitive UI, and real-time points calculation.

🔗 **Live Site:** [https://fad-helper.onrender.com](https://fad-helper.onrender.com)

---

## 🎯 Features

### Unit Builders (6 Types)
- **Infantry Squads** - Standard troops with customizable weapons and equipment
  - Individual squad member roster management
  - Primary + secondary weapon support (pistols, SMG, shotgun)
  - Squad size: 1-20 soldiers
- **Characters** - Heroes and officers with leadership abilities
  - Leadership ratings: Novice, Experienced, Inspiring, Heroic
  - Branch specialization: Infantry, Gunnery, Cavalry
  - Personality traits
- **Heavy Weapon Teams** - Crew-served weapons
  - Customizable crew count (default: 2)
  - Support for heavy MGs, cannons, mortars, rail guns
- **Snipers** - Precision marksmen
  - Long-range engagement specialists
  - Individual personality options
- **Psionics** - Psychic warriors
  - Psionic aptitude levels: Marginal, Minor, Major, Potent
  - Psionic strength ratings (1-5)
- **Vehicles** - Armor, walkers, and transports
  - Directional armor (front/side/rear)
  - Movement types: Fly, Hover, Wheeled, Tracked, Walk
  - Crew size (0-10, supports AI-controlled vehicles)
  - Transport capacity
  - Vehicle-specific properties

### Game Data Library
- **44 Infantry Traits** - Adaptive Camouflage, Berserk, Drop Troop, Engineer, etc.
- **73 Vehicle Properties** - Advanced Targeting, Jump Jets, Stealth, ECM, etc.
- **50+ Weapons** across 3 categories:
  - Basic: Pistols, Rifles, Gauss weapons, Blasters (0.25-2.00 pts)
  - Support: Shotguns, Flamers, SAW, Plasma Rifles (1.00-6.00 pts)
  - Heavy: Machine guns, Cannons, Beam weapons, Rail Guns (5.00-30.00 pts)
- **9 Armour Types** - None through Heavy Power Armour (3-9 rating)

### Faction System
- Create custom factions with names, colors, and icons
- Organize units by faction
- Public faction browsing and rating system
- Tactical playstyle tags (40+ tags):
  - Classic warfare: Combined Arms, Blitzkrieg, Guerrilla, Siege
  - Sci-fi tactics: Psionic Dominance, Energy Weapons, Drone Warfare

### Army List Management
- Save and organize multiple army lists
- Assign units to lists with point tracking
- Public/private list visibility
- Share lists for events and club play
- Browse community lists

### Live Preview & Points Calculator
- Real-time unit preview while building
- Automatic points calculation based on official rules
- Quality/Resolve multipliers
- Trait stacking
- Equipment cost aggregation

### User System
- Secure account registration and login
- Personal dashboard with saved content
- Role-based access control

---

## 🚀 Quick Start

### For Players

1. **Register an Account**
   - Visit [https://fad-helper.onrender.com](https://fad-helper.onrender.com)
   - Create a secure account
   - Start building your armies

2. **Create a Faction** (Optional)
   - Navigate to "Faction Creator"
   - Choose name, color, icon
   - Add playstyle tags to describe your army

3. **Build Units**
   - Select unit type (Squad, Character, Vehicle, etc.)
   - Configure stats: Quality, Resolve, equipment
   - Add traits for special abilities
   - Watch live preview calculate points
   - Save to your collection

4. **Create Army Lists**
   - Go to "List Builder"
   - Name your list and set point limit
   - Add units from your collection
   - Mark as public to share with community

5. **Browse & Share**
   - View public factions and lists
   - Rate other players' creations
   - Export for tournament play

---

## 📋 Workflows

### Building a Squad
```
Squad Builder → Configure Stats → Choose Weapons → Select Traits → Save
                    ↓
            Live Preview Updates
                    ↓
            Points Auto-Calculate
                    ↓
        Secondary Weapon (Optional)
                    ↓
    Squad Member Manager (After Save)
```

### Managing Squad Members
After saving a squad, click **"Manage Squad Members"** to:
- Assign individual weapons per soldier
- Designate member types: Regular, Support, Leader
- Equip secondary weapons (pistols, SMG, shotgun)
- Add notes per member

### Creating a Vehicle
```
Vehicle Builder → Select Type → Set Armor Values → Choose Movement
                    ↓
            Add Properties (Traits)
                    ↓
        Configure Crew Size (0-10)
                    ↓
        Set Transport Capacity
                    ↓
            Save Vehicle
```

### Army List Workflow
```
List Builder → Set Name & Points → Add Units → Review Total
                    ↓
        Units from Your Collection
                    ↓
        Real-time Point Tracking
                    ↓
        Public/Private Toggle
                    ↓
            Save & Share
```

---

## 🛠️ Technical Stack

### Backend
- **Flask 3.0.0** - Python web framework
- **SQLAlchemy** - ORM and database management
- **PostgreSQL** - Production database
- **Flask-Login** - User authentication

### Frontend
- **Jinja2** - Template engine
- **Bootstrap 5** - Responsive UI framework
- **Bootstrap Icons** - Icon library
- **JavaScript** - Interactive features

### Deployment
- **Render.com** - Web hosting
- **Gunicorn** - WSGI HTTP server
- **Python 3.12.8** - Runtime environment

---

## 🎮 Game Rules Integration

F.A.D. Helper implements the official **Fast and Dirty** wargame rules:

### Points System
```python
Base Cost = Quality Points × Squad Size
+ Equipment (Armour + Weapons) × Squad Size
× (Quality Multiplier + Resolve Multiplier)
× Trait Multipliers (applied sequentially)
```

### Quality Levels
| Quality   | Test | Base Cost | Multiplier |
|-----------|------|-----------|------------|
| Rabble    | 5+   | 4 pts     | 0.7        |
| Conscript | 4+   | 6 pts     | 0.0        |
| Regular   | 3+   | 8 pts     | 1.3        |
| Elite     | 2+   | 10 pts    | 1.6        |

### Resolve Levels
| Resolve    | Multiplier |
|------------|------------|
| Reluctant  | -0.5       |
| Uncertain  | -0.3       |
| Steady     | 0.0        |
| Determined | +0.3       |

### Secondary Weapons (Sidearms Only)
- Pistol, Gauss Pistol, Blaster Pistol
- SMG (Submachine Gun)
- Shotgun

*All secondary weapons have "+1 to close assaults" per official rules*

---

## 📦 Installation (Local Development)

### Prerequisites
- Python 3.12.8
- Git
- Virtual environment tool

### Setup Steps

1. **Clone Repository**
   ```bash
   git clone https://github.com/lordbutxot/FAD_Helper.git
   cd FAD_Helper
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Database**
   ```bash
   python init_production_db.py
   ```

5. **Run Development Server**
   ```bash
   flask run
   ```

6. **Access Application**
   - Open browser to `http://localhost:5000`
   - Register an account to get started

### Environment Variables (Optional)
Create `.env` file for PostgreSQL:
```env
DATABASE_URL=postgresql://user:password@host:port/database
```

---

## 🤝 Contributing

Contributions welcome! Areas for enhancement:
- Additional unit types (artillery, fortifications)
- Scenario generator
- Print-friendly list export
- Mobile app version
- Multiplayer army matchmaking

---

## 📜 License

This project is provided as-is for the F.A.D. wargaming community. Game rules and mechanics are property of their respective creators.

---

## 🙏 Credits

- **Fast and Dirty** wargame rules by their original creators
- Built by the F.A.D. community for the F.A.D. community
- Hosted on Render.com
- Database by Supabase

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/lordbutxot/FAD_Helper/issues)
- **Live Site:** [https://fad-helper.onrender.com](https://fad-helper.onrender.com)

---

**Build armies faster. Play more games. Welcome to F.A.D. Helper.**
