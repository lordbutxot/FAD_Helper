# FAD Helper - Changelog

## Version 1.1.0 - 2026-01-31

### Critical Bug Fixes
- **Fixed Squad Creation Error**: Changed `trait.points_modifier` to `trait.points_multiplier` across all unit types (Squad, Character, Heavy Weapon, Sniper, Psionic)
- **Fixed Traits Application**: Traits now correctly apply as multipliers sequentially per official game rules, not as additive bonuses
- **Fixed Heavy Weapon Selector**: Corrected weapon filter from `weapon.weapon_class` to `weapon.category == 'Heavy'`
- **Fixed Vehicle Crew Size**: Allows 0 crew for AI-controlled/autonomous vehicles

### New Features
- **PDF Export System**: Professional PDF export for army lists with unit stat tables (similar to OPR Army Forge output)
  - Comprehensive unit statistics tables
  - Equipment and traits display
  - Faction information and metadata
  - Print-ready format with proper headers and footers
  - Accessible via "Export PDF" button on list view page

### Improvements
- **Vehicle Weapon Filtering**: 
  - Primary weapons now filtered to Support/Heavy categories only
  - Secondary weapons filtered to Basic/Support categories
  - Weapons show category badges for clarity
- **Vehicle Builder**: Improved crew size tooltip clarification
- **UI Cleanup**: Removed emojis from alert messages for professional appearance

### Technical Changes
- Added ReportLab 4.0.9 for PDF generation
- Added Pillow 10.2.0 for image support in PDFs
- Created new `pdf_generator.py` module with `ArmyListPDFGenerator` class
- Added `/list/<int:list_id>/export-pdf` route
- Updated `requirements.txt` with new dependencies

### Files Modified
- `routes.py`: Fixed 5 instances of points calculation, added PDF export route
- `templates/heavy_weapon_builder.html`: Fixed weapon category filter
- `templates/vehicle_builder.html`: Fixed weapon filters and crew size
- `templates/view_list.html`: Added PDF export button, removed emojis
- `requirements.txt`: Added PDF generation libraries
- `pdf_generator.py`: New file for PDF export functionality

## Version 1.0.0 - Initial Release

### Core Features
- 6 Unit Builder Types (Squad, Character, Heavy Weapon, Sniper, Psionic, Vehicle)
- Faction System with ratings and playstyle tags
- Army List Builder and Management
- Squad Member Roster System
- Public/Private Sharing
- User Authentication and Admin Panel
- Armoury Reference Database
- Browse and Search Functionality

---

## Upgrade Instructions

### For Deployment
1. Pull latest changes from repository
2. Install new dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Restart the application:
   ```bash
   # For production (Render)
   # Will auto-deploy on git push
   
   # For local development
   python app.py
   ```

### Database Changes
No database migrations required for this release.

---

## Known Issues & Future Enhancements

### Planned Features
- [ ] Unit validation warnings (e.g., Elite + Reluctant combo alerts)
- [ ] Advanced search with points range filters
- [ ] Mobile-responsive improvements for builders
- [ ] Batch unit import/export
- [ ] Army list comparison tool
- [ ] Battle report system

### Minor Issues
- None reported

---

## Credits
- Built with Flask, SQLAlchemy, and ReportLab
- Designed for F.A.D. (Fast and Dirty) wargame
- Community-driven feature requests
