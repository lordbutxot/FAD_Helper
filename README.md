# F.A.D. (Fast and Dirty) List Builder

A web-based army list builder for the F.A.D. wargame. Create custom units, build army lists, and share them with the community!

## Features

- **Custom Unit Builder** - Create units following F.A.D. rules with automatic point calculation
- **Army List Manager** - Build complete army lists with point totals
- **User Authentication** - Register and login to save your creations
- **List Sharing** - Share your lists publicly or keep them private
- **Browse Community Lists** - Explore lists created by other players
- **Complete Armoury** - View all weapons, armour, and traits from the game
- **Point Calculator** - Real-time calculation following official F.A.D. formulas

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. **Install Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Initialize the Database**
   ```powershell
   python init_db.py
   ```
   This will create the database and populate it with all weapons, armour, and traits from F.A.D.

3. **Run the Application**
   ```powershell
   python app.py
   ```

4. **Access the Application**
   Open your browser and go to: `http://localhost:5000`

## Usage

### First Time Setup

1. **Register** for an account
2. Browse the **Armoury** to familiarize yourself with available equipment
3. Go to the **Unit Builder** to create your first custom unit
4. Use the **List Builder** to assemble your army

### Creating Units

The unit builder supports all F.A.D. unit types:
- Infantry squads
- Heavy Weapons Teams
- Characters (Officers)
- Psionics
- Snipers
- Vehicles

Points are calculated automatically based on:
- Base unit type
- Quality and Resolve
- Armour and weapons
- Special traits
- Squad size (for infantry)

### Building Army Lists

1. Create units first (or use public units from other players)
2. Go to List Builder
3. Add units and set quantities
4. Save your list (public or private)
5. Export for printing or share with friends

### Sharing Lists

- **Private Lists**: Only you can see them
- **Public Lists**: Visible in the community browse page
- Share URLs directly with friends
- View counts track popularity

## Project Structure

```
FAD Script/
├── app.py              # Main Flask application
├── models.py           # Database models
├── routes.py           # Application routes/views
├── init_db.py          # Database initialization script
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── browse.html
│   ├── armoury.html
│   ├── unit_builder.html
│   └── list_builder.html
└── fad_lists.db       # SQLite database (created after init)
```

## Game Data

The app includes complete data from F.A.D.:
- 18 Basic Weapons
- 10 Support Weapons
- 18 Heavy Weapons
- 8 Armour Types
- 40+ Special Traits

All point calculations follow official F.A.D. rules from the faction creator.

## Technical Details

- **Backend**: Flask (Python web framework)
- **Database**: SQLite (simple, file-based)
- **Frontend**: Bootstrap 5, vanilla JavaScript
- **Authentication**: Flask-Login with password hashing

## Future Enhancements

Possible additions:
- Unit/List comments and ratings
- Advanced search and filters
- Export to PDF
- Mobile app version
- Pre-built faction lists
- Battle reports integration

## Credits

- F.A.D. (Fast and Dirty) wargame rules
- Community contributions welcome!

## License

This is a community tool for the F.A.D. wargame. Please respect the original game's intellectual property.

## Support

For issues or questions:
1. Check the Armoury for reference data
2. Review the F.A.D. rulebooks
3. Ask the community on the browse page

Enjoy building your armies! ⚔️
