# F.A.D. Helper

**F.A.D. Helper** is a comprehensive web-based army list builder for the **F.A.D. (Fast and Dirty)** tabletop wargame. Build legal armies faster with official game data, intuitive UI, and real-time points calculation.

🔗 **Live Site:** [https://fad-helper.onrender.com](https://fad-helper.onrender.com)  
📦 **Version:** 1.1.0 (2026-01-31)

---

## 📖 About

F.A.D. Helper is a full-featured web application designed to streamline army building for the Fast and Dirty wargame. Whether you're a competitive tournament player or casual hobbyist, this tool helps you create, manage, and share army lists with ease. The application implements all official F.A.D. game rules and provides comprehensive data libraries for weapons, armor, traits, and unit types.

Built with Flask and PostgreSQL, F.A.D. Helper offers both local development support and production deployment on Render.com with Supabase database hosting.

---

## 🎯 Features

### Unit Builders (6 Types)
- **Infantry Squads** - Standard troops with customizable weapons and equipment
  - Individual squad member roster management with per-soldier weapon assignments
  - Primary + secondary weapon support (pistols, SMG, shotgun)
  - Squad size: 1-20 soldiers
  - Member types: Regular, Support, Leader
  - Individual notes per squad member
- **Characters** - Heroes and officers with leadership abilities
  - Leadership ratings: Novice, Experienced, Inspiring, Heroic
  - Branch specialization: Infantry, Gunnery, Cavalry
  - Personality trait system
  - Join squads to provide bonuses
- **Heavy Weapon Teams** - Crew-served weapons
  - Customizable crew count (default: 2)
  - Support for heavy MGs, cannons, mortars, rail guns
  - Weapon options for versatility
- **Snipers** - Precision marksmen
  - Long-range engagement specialists
  - Individual personality options
  - High-quality marksman ratings
- **Psionics** - Psychic warriors
  - Psionic aptitude levels: Marginal, Minor, Major, Potent
  - Psionic strength ratings (1-5)
  - Special mental warfare abilities
- **Vehicles** - Armor, walkers, and transports
  - Directional armor (front/side/rear)
  - Movement types: Fly, Hover, Wheeled, Tracked, Walk
  - Crew size (0-10, supports AI-controlled vehicles)
  - Transport capacity
  - Multiple weapon mounts
  - 25+ vehicle-specific properties/traits

### Game Data Library
- **73+ Infantry Traits** - Adaptive Camouflage, Berserk, Drop Troop, Engineer, Stealth, etc.
- **25+ Vehicle Properties** - Advanced Targeting, Jump Jets, Stealth, ECM, Reactive Armour, etc.
- **50+ Weapons** across 3 categories:
  - Basic: Pistols, Rifles, Gauss weapons, Blasters (0.25-2.00 pts)
  - Support: Shotguns, Flamers, SAW, Plasma Rifles (1.00-6.00 pts)
  - Heavy: Machine guns, Cannons, Beam weapons, Rail Guns (5.00-30.00 pts)
- **9 Armour Types** - None through Heavy Power Armour (3-9 rating)
- All data from official F.A.D. rulebook

### Faction System
- Create custom factions with names, colors, and icons
- Upload custom faction logos (PNG, JPG, GIF - max 2MB)
- Organize units by faction
- Public faction browsing and rating system (5-star ratings)
- 40+ tactical playstyle tags:
  - Classic warfare: Combined Arms, Blitzkrieg, Guerrilla, Siege
  - Sci-fi tactics: Psionic Dominance, Energy Weapons, Drone Warfare, Stealth Operations
- Faction background and lore
- Special faction-wide rules
- Copy factions to create variations

### Army List Management
- Create and organize multiple army lists
- Set point limits for balanced games
- Add units from your collection with quantity tracking
- Public/private list visibility
- Share lists for events and club play
- Browse community lists by faction or playstyle
- **PDF Export** - Professional PDF generation with unit stat tables (OPR Army Forge style)
  - Comprehensive unit statistics
  - Equipment and traits display
  - Faction information and metadata
  - Print-ready format for tournaments

### Live Preview & Points Calculator
- Real-time unit preview while building
- Automatic points calculation based on official F.A.D. rules
- Quality/Resolve multipliers (Rabble 0.7x to Elite 1.6x)
- Sequential trait stacking (official rule implementation)
- Equipment cost aggregation
- Instant feedback on point changes

### User System
- Secure account registration and login (optional email)
- Password strength validation
- Account lockout after failed login attempts (5 attempts)
- Personal dashboard with saved content
- Role-based access control (User/Admin)
- Session management with 12-hour persistence

### Admin Features
- Admin panel for user management
- View all users with statistics
- Unlock locked accounts
- Toggle admin privileges
- Delete user accounts (with cascade deletion of content)
- Monitor platform usage

### Unit Variants
- Create variants of existing units
- Parent-child relationship tracking
- Inherit traits and equipment from parent
- Quick iteration for different loadouts

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
- **Flask 3.0.0** - Modern Python web framework
- **SQLAlchemy 3.1.1** - ORM and database management
- **PostgreSQL** - Production database (Supabase)
- **SQLite** - Local development database
- **Flask-Login 0.6.3** - User authentication and session management
- **Flask-WTF 1.2.1** - Form handling and CSRF protection
- **Werkzeug 3.0.1** - Password hashing and security utilities
- **ReportLab 4.0.9** - PDF generation
- **Pillow 10.2.0** - Image processing for PDFs
- **Markdown 3.5.1** - Rich text formatting
- **Bleach 6.1.0** - HTML sanitization

### Frontend
- **Jinja2** - Server-side template engine
- **Bootstrap 5** - Responsive UI framework
- **Bootstrap Icons** - Comprehensive icon library
- **JavaScript** - Interactive features and AJAX
- **SortableJS** - Drag-and-drop functionality

### Deployment
- **Render.com** - Cloud hosting platform
- **Supabase** - PostgreSQL database hosting
- **Gunicorn 21.2.0** - WSGI HTTP server
- **Python 3.12.8** - Runtime environment

### Security Features
- Password strength validation (8+ chars, uppercase, lowercase, number, special)
- Rate limiting with account lockout (5 failed attempts)
- CSRF protection on all forms
- Session cookie security (HTTPOnly, SameSite)
- SQL injection prevention via SQLAlchemy ORM
- HTML sanitization for user content

### Database Architecture
- **User** - Account management with admin roles
- **Faction** - Faction organization with ratings
- **Unit** - 6 unit types with variant support
- **SquadMember** - Individual soldier tracking
- **ArmyList** - List management with unit associations
- **Weapon/Armour/Trait** - Game data tables
- **FactionRating** - Community rating system

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
- **Python 3.12.8** or higher
- **Git** for version control
- **pip** package manager
- Virtual environment tool (venv)

### Setup Steps

1. **Clone Repository**
   ```bash
   git clone https://github.com/lordbutxot/FAD_Helper.git
   cd FAD_Helper
   ```

2. **Create Virtual Environment**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate
   
   # Linux/Mac
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Database**
   ```bash
   python init_production_db.py
   ```
   This script:
   - Creates all database tables
   - Populates official F.A.D. game data (weapons, armor, traits)
   - Safe to run multiple times (preserves user data)
   - Loads 73+ infantry traits, 25+ vehicle properties, 50+ weapons

5. **Run Development Server**
   ```bash
   # Option 1: Using Flask
   flask run
   
   # Option 2: Using Python
   python app.py
   ```

6. **Access Application**
   - Open browser to `http://localhost:5000`
   - Register an account to get started
   - Default uses SQLite database (fad_lists.db)

### Environment Variables (Optional)

#### PostgreSQL Database
Create `.env` file for production database:
```env
DATABASE_URL=postgresql://user:password@host:port/database
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
```

#### Development Settings
```env
FLASK_ENV=development
FLASK_DEBUG=1
```

### Configuration Options

The application supports multiple configurations in [config.py](config.py):
- **Development**: SQLite database, debug mode enabled
- **Production**: PostgreSQL with SSL, secure cookies
- Automatic detection based on `FLASK_ENV` variable

### Database Migrations

If you need to update the database schema:
```bash
# View available migration scripts
ls migrate_*.py

# Run all migrations
python migrate_all.py

# Run specific migration
python migrate_add_description.py
```

---

## 📁 Project Structure

```
FAD_Helper/
├── app.py                      # Flask application entry point
├── config.py                   # Configuration for dev/production
├── extensions.py               # Flask extensions initialization
├── models.py                   # Database models (User, Faction, Unit, etc.)
├── routes.py                   # All application routes and logic (2100+ lines)
├── pdf_generator.py            # PDF export functionality
├── requirements.txt            # Python dependencies
│
├── init_production_db.py       # Database initialization script
├── migrate_*.py                # Database migration scripts
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html              # Base template with navbar
│   ├── dashboard.html         # User dashboard
│   ├── index.html             # Landing page
│   ├── login.html             # Authentication
│   ├── register.html          # User registration
│   │
│   ├── faction_creator.html   # Faction creation
│   ├── edit_faction.html      # Faction editing
│   ├── view_faction.html      # Faction display
│   ├── browse_factions.html   # Public faction browsing
│   │
│   ├── squad_builder.html     # Squad unit builder
│   ├── character_builder.html # Character builder
│   ├── heavy_weapon_builder.html
│   ├── sniper_builder.html
│   ├── psionic_builder.html
│   ├── vehicle_builder.html
│   ├── edit_unit.html         # Generic unit editor
│   ├── view_unit.html         # Unit display
│   │
│   ├── list_builder.html      # Army list creation
│   ├── edit_list.html         # List editing
│   ├── view_list.html         # List display with PDF export
│   ├── browse.html            # Public list browsing
│   │
│   ├── armoury.html           # Game data reference
│   └── admin/
│       └── panel.html         # Admin dashboard
│
├── static/                    # Static assets
│   ├── sortable.js           # Drag-and-drop library
│   └── faction_logos/        # Uploaded faction images
│
├── instance/                  # Instance-specific files
│   ├── secret_key.txt        # Auto-generated secret key
│   └── fad_lists.db          # SQLite database (dev)
│
├── Procfile                   # Render.com deployment config
├── render.yaml                # Render infrastructure as code
├── build.sh                   # Production build script
├── start.sh                   # Production start script
│
├── README.md                  # This file
└── CHANGELOG.md               # Version history
```

### Key Files

- **[app.py](app.py)** - Initializes Flask app, configures extensions, registers routes
- **[models.py](models.py)** - 8 database models with relationships and helper methods
- **[routes.py](routes.py)** - 50+ routes handling all application logic
- **[config.py](config.py)** - Environment-aware configuration with security settings
- **[pdf_generator.py](pdf_generator.py)** - ReportLab-based PDF generation for army lists
- **[init_production_db.py](init_production_db.py)** - Loads official F.A.D. game data

---

## 🤝 Contributing

Contributions welcome! This project is open for community enhancement.

### Ways to Contribute
- **Bug Reports**: Found an issue? Open a GitHub issue with details
- **Feature Requests**: Have an idea? Suggest it in the issues
- **Code Contributions**: Fork, develop, and submit a pull request
- **Documentation**: Improve README, add code comments, write guides
- **Testing**: Test features and report edge cases

### Development Priorities

#### High Priority
- [ ] Mobile-responsive improvements for unit builders
- [ ] Unit validation warnings (e.g., Elite + Reluctant combinations)
- [ ] Advanced search with points range filters
- [ ] Batch unit import/export (JSON format)
- [ ] Army list comparison tool

#### Medium Priority
- [ ] Additional unit types (artillery, fortifications, drones)
- [ ] Scenario generator with objectives
- [ ] Battle report system with results tracking
- [ ] Tournament bracket manager
- [ ] Unit card printer (physical cards)

#### Nice to Have
- [ ] Mobile app version (React Native/Flutter)
- [ ] Multiplayer army matchmaking
- [ ] 3D model integration
- [ ] Voice-controlled unit builder
- [ ] AI opponent generator

### Contribution Guidelines

1. **Fork the Repository**
2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make Your Changes**
   - Follow existing code style
   - Add comments for complex logic
   - Test thoroughly
4. **Commit with Clear Messages**
   ```bash
   git commit -m "Add: Feature description"
   ```
5. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Code Style
- Python: Follow PEP 8 guidelines
- HTML: Use proper indentation and semantic tags
- JavaScript: Use ES6+ features, clear variable names
- Comments: Explain "why" not "what"

### Testing
- Test all unit types after changes
- Verify points calculation accuracy
- Check responsive design on mobile
- Test with different user roles (regular/admin)

---

## � Deployment

### Production Deployment (Render.com)

The application is configured for automatic deployment on Render.com:

1. **Connect Repository**
   - Link your GitHub repository to Render
   - Render will auto-detect Flask application

2. **Environment Variables**
   Set these in Render dashboard:
   ```
   DATABASE_URL=postgresql://...  (from Supabase)
   SECRET_KEY=<random-secure-key>
   FLASK_ENV=production
   PYTHON_VERSION=3.12.8
   ```

3. **Build Configuration**
   - Build Command: `./build.sh` (installs dependencies, runs migrations)
   - Start Command: `gunicorn app:app` (production WSGI server)
   - Auto-deploy on git push to main branch

4. **Database Setup**
   - Create PostgreSQL database on Supabase
   - Copy connection string to `DATABASE_URL`
   - Application will auto-create tables on first run

### Manual Deployment

For other hosting providers:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://..."
export SECRET_KEY="your-secret-key"
export FLASK_ENV="production"

# Initialize database
python init_production_db.py

# Start with Gunicorn
gunicorn --bind 0.0.0.0:8000 app:app
```

### Health Monitoring
- Application includes automatic connection pooling
- Database connections recycled every 5 minutes
- Pre-ping verification prevents stale connections

---

## 📜 License

This project is provided as-is for the F.A.D. wargaming community. Game rules and mechanics are property of their respective creators.

**Open Source**: Feel free to fork, modify, and use for your own projects.

---

## 🙏 Credits & Acknowledgments

### Game Design
- **Fast and Dirty (F.A.D.)** wargame rules by their original creators
- All unit stats, traits, and weapons from official F.A.D. rulebook

### Technology
- Built with **Flask** (Python web framework)
- **SQLAlchemy** for database ORM
- **ReportLab** for PDF generation
- **Bootstrap 5** for responsive UI
- **SortableJS** for drag-and-drop

### Hosting
- **Render.com** - Web hosting and deployment
- **Supabase** - PostgreSQL database hosting

### Community
- Built by the F.A.D. community for the F.A.D. community
- Feature requests from players and tournament organizers
- Bug reports and testing from community members

### Inspiration
- PDF export inspired by **OPR Army Forge**
- UI design influenced by modern army builders

---

## 📞 Support & Contact

### Get Help
- **GitHub Issues**: [Report bugs or request features](https://github.com/lordbutxot/FAD_Helper/issues)
- **Live Site**: [https://fad-helper.onrender.com](https://fad-helper.onrender.com)
- **Documentation**: This README and [CHANGELOG.md](CHANGELOG.md)

### Frequently Asked Questions

**Q: Is my data safe?**  
A: Yes. All user data is stored securely with password hashing (Werkzeug). Session cookies are HTTPOnly and secure in production.

**Q: Can I export my army lists?**  
A: Yes! Use the "Export PDF" button on any army list to generate a professional print-ready PDF.

**Q: How are points calculated?**  
A: Points follow official F.A.D. rules: Base cost × modifiers × trait multipliers (applied sequentially).

**Q: Can I share my factions with friends?**  
A: Yes! Set factions and lists to "public" to share them. Others can view and rate them.

**Q: What if I find a bug?**  
A: Please open a GitHub issue with details about what happened and how to reproduce it.

**Q: Can I contribute to the project?**  
A: Absolutely! See the Contributing section above for guidelines.

---

## 📊 Project Stats

- **Lines of Code**: 6000+ (Python, HTML, JavaScript)
- **Database Models**: 8 core models with relationships
- **Routes**: 50+ application endpoints
- **Templates**: 30+ HTML templates
- **Game Data**: 150+ weapons, traits, and equipment items
- **Version**: 1.1.0 (actively maintained)
- **License**: Open source, community-driven

---

**⚔️ Build armies faster. Play more games. Welcome to F.A.D. Helper. ⚔️**
