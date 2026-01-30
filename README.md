# F.A.D. (Fast and Dirty) List Builder

A web-based army list builder for the F.A.D. wargame. Create custom factions, build units, assemble army lists, and share them with the community!

## ✨ Features

### Core Functionality
- **🎨 Faction Creator** - Design custom factions with logos, colors, and playstyle tags
- **⚔️ Advanced Unit Builder** - Create 6 types of units with automatic point calculation
  - Infantry Squads with individual equipment
  - Characters with leadership and specialization
  - Snipers, Heavy Weapons Teams, Psionics, Vehicles
- **📋 Army List Manager** - Build complete army lists with point totals
- **👥 User System** - Register, login, and manage your creations
- **🌐 Community Sharing** - Share factions/lists publicly or keep them private
- **📚 Complete Armoury** - View all weapons, armour, and traits from the game
- **🧮 Point Calculator** - Real-time calculation following official F.A.D. formulas

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Option 1: Quick Start Script (Windows)
```bash
start.bat
```

### Option 2: Manual Setup
1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize the Database**
   ```bash
   python init_db.py
   ```

3. **Create Admin User (Optional)**
   ```bash
   python create_admin.py
   ```

4. **Run the Application**
   ```bash
   python app.py
   ```

5. **Access the Application**
   Open your browser and go to: `http://localhost:5000`

## 📖 Usage Guide

### First Time Setup
1. **Register** for an account
2. Browse the **Armoury** to see available equipment
3. Create your first **Faction**
4. Build **Units** for your faction
5. Assemble **Army Lists** from your units

### Creating Factions
- Set faction name, description, and lore
- Choose colors and upload custom logos
- Add playstyle tags (artillery, psionic, elite forces, etc.)
- Define faction-wide special rules
- Make public to share with community

### Building Units
Supports all 6 F.A.D. unit types with automatic point calculation:
- **Squads**: Infantry units with individual member equipment
- **Characters**: Heroes with leadership ratings and specializations
- **Snipers**: Long-range precision specialists
- **Heavy Weapons**: Crew-served heavy ordinance teams
- **Psionics**: Psychic units with aptitude and strength ratings
- **Vehicles**: Tanks, walkers, transports with armor facings

Points calculated from:
- Quality (Rabble → Elite) and Resolve (Reluctant → Determined)
- Armour and weapons
- Special traits and abilities
- Squad size and equipment variations

### Managing Army Lists
1. Create units or browse public units
2. Add units to your list with quantities
3. Track total points and unit counts
4. Save as public or private
5. Share URLs with friends

## 🌐 Deployment

Ready for free deployment! See [DEPLOYMENT.md](DEPLOYMENT.md) for complete guides.

**Recommended:** [Render.com](https://render.com) (free PostgreSQL + HTTPS included)

Quick deploy:
```bash
git push origin main  # Push to GitHub
# Then connect repo on Render.com - auto-deploys!
```

## 📁 Project Structure

```
FAD_Helper/
├── app.py                  # Main Flask application
├── config.py              # Production/development configuration
├── models.py              # Database models (User, Faction, Unit, ArmyList)
├── routes.py              # Application routes/views
├── extensions.py          # Flask extensions (SQLAlchemy, Flask-Login)
├── init_db.py            # Database initialization script
├── create_admin.py       # Admin user creation utility
├── requirements.txt      # Python dependencies
├── Procfile             # For Heroku/Render deployment
├── render.yaml          # Render.com auto-deploy config
├── runtime.txt          # Python version specification
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore rules
├── DEPLOYMENT.md       # Complete deployment guide
├── start.bat           # Quick start script (Windows)
├── start.sh            # Quick start script (Unix/Linux/Mac)
├── templates/          # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── faction_creator.html
│   ├── unit_builder.html
│   ├── list_builder.html
│   ├── dashboard.html
│   ├── browse_factions.html
│   └── ... (and more)
└── instance/           # Instance folder (created on first run)
    └── fad_lists.db   # SQLite database
```

## 🎮 Game Data Included

Complete F.A.D. armory:
- **Basic Weapons**: 18 types (Pistol → Gauss Rifle)
- **Support Weapons**: 10 types (Shotgun → Beam Rifle)
- **Heavy Weapons**: 18 types (HMG → Hellfire Cannon)
- **Armour**: 8 types (None → Hardened Power Armour)
- **Traits**: 40+ special abilities
- **Playstyle Tags**: 35+ tactical doctrines

All point calculations follow official F.A.D. rules.

## 🛠️ Technical Stack

- **Backend**: Flask 3.0, SQLAlchemy ORM
- **Database**: SQLite (dev) / PostgreSQL (production)
- **Authentication**: Flask-Login with secure password hashing
- **Security**: CSRF protection, secure sessions, HTTPS-ready
- **Frontend**: Bootstrap 5, vanilla JavaScript
- **Deployment**: Production-ready with gunicorn

## 🔧 Development

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set development mode
$env:FLASK_ENV="development"  # PowerShell
export FLASK_ENV=development  # Bash

# Run with auto-reload
python app.py
```
