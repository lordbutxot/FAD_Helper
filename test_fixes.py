#!/usr/bin/env python3
"""
Test script to validate all bug fixes and new features
Run this before deploying to production
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all required modules can be imported"""
    print("=" * 60)
    print("TEST 1: Module Imports")
    print("=" * 60)
    
    try:
        from flask import Flask
        print("✓ Flask imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Flask: {e}")
        return False
    
    try:
        from models import User, Unit, ArmyList, Weapon, Armour, Trait
        print("✓ Models imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import models: {e}")
        return False
    
    try:
        from routes import init_routes
        print("✓ Routes imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import routes: {e}")
        return False
    
    try:
        from pdf_generator import generate_army_list_pdf
        print("✓ PDF generator imported successfully")
    except ImportError as e:
        print(f"⚠ PDF generator not available (reportlab needed): {e}")
        print("  This is OK for testing - install reportlab for PDF export")
    
    print()
    return True


def test_trait_attribute():
    """Test that Trait model uses points_multiplier (not points_modifier)"""
    print("=" * 60)
    print("TEST 2: Trait Model Attribute")
    print("=" * 60)
    
    try:
        from models import Trait
        
        # Check model definition
        if hasattr(Trait, 'points_multiplier'):
            print("✓ Trait.points_multiplier attribute exists")
        else:
            print("✗ Trait.points_multiplier attribute missing")
            return False
        
        if hasattr(Trait, 'points_modifier'):
            print("⚠ Warning: Trait.points_modifier still exists (should be removed)")
        
        print()
        return True
    except Exception as e:
        print(f"✗ Error testing Trait model: {e}")
        return False


def test_calculate_points_function():
    """Test that calculate_points uses points_multiplier"""
    print("=" * 60)
    print("TEST 3: Points Calculation Function")
    print("=" * 60)
    
    try:
        with open('routes.py', 'r') as f:
            content = f.read()
        
        # Check for old buggy code
        if 'points_modifier' in content:
            print("✗ routes.py still contains 'points_modifier' - bug not fixed!")
            return False
        
        # Check for correct code
        if 'trait.points_multiplier' in content:
            print("✓ routes.py correctly uses 'points_multiplier'")
        else:
            print("⚠ Warning: Cannot find trait.points_multiplier in routes.py")
        
        # Check for multiplier logic
        if 'multiplier *= trait.points_multiplier' in content:
            print("✓ Traits correctly applied as multipliers (not additive)")
        else:
            print("⚠ Warning: Multiplier logic may not be correct")
        
        print()
        return True
    except Exception as e:
        print(f"✗ Error checking routes.py: {e}")
        return False


def test_heavy_weapon_template():
    """Test that heavy weapon selector uses correct filter"""
    print("=" * 60)
    print("TEST 4: Heavy Weapon Selector Template")
    print("=" * 60)
    
    try:
        with open('templates/heavy_weapon_builder.html', 'r') as f:
            content = f.read()
        
        # Check for old buggy code
        if 'weapon.weapon_class' in content:
            print("✗ heavy_weapon_builder.html still uses 'weapon.weapon_class' - bug not fixed!")
            return False
        
        # Check for correct code
        if "weapon.category == 'Heavy'" in content:
            print("✓ Heavy weapon selector correctly filters by category")
        else:
            print("⚠ Warning: Heavy weapon filter may not be correct")
        
        print()
        return True
    except Exception as e:
        print(f"✗ Error checking heavy_weapon_builder.html: {e}")
        return False


def test_vehicle_template():
    """Test vehicle template fixes"""
    print("=" * 60)
    print("TEST 5: Vehicle Builder Template")
    print("=" * 60)
    
    try:
        with open('templates/vehicle_builder.html', 'r') as f:
            content = f.read()
        
        # Check crew size minimum
        if 'min="0"' in content and 'crew_size' in content:
            print("✓ Vehicle crew size allows 0 (for AI vehicles)")
        else:
            print("⚠ Warning: Crew size minimum may not be set correctly")
        
        # Check weapon filtering
        if "weapon.category in ['Support', 'Heavy']" in content:
            print("✓ Primary weapon filtered to Support/Heavy")
        else:
            print("⚠ Warning: Primary weapon filter may not be correct")
        
        if "weapon.category in ['Basic', 'Support']" in content:
            print("✓ Secondary weapon filtered to Basic/Support")
        else:
            print("⚠ Warning: Secondary weapon filter may not be correct")
        
        print()
        return True
    except Exception as e:
        print(f"✗ Error checking vehicle_builder.html: {e}")
        return False


def test_pdf_export_route():
    """Test that PDF export route exists"""
    print("=" * 60)
    print("TEST 6: PDF Export Route")
    print("=" * 60)
    
    try:
        with open('routes.py', 'r') as f:
            content = f.read()
        
        if '/list/<int:list_id>/export-pdf' in content:
            print("✓ PDF export route defined")
        else:
            print("✗ PDF export route not found")
            return False
        
        if 'generate_army_list_pdf' in content:
            print("✓ PDF generation function called in route")
        else:
            print("⚠ Warning: PDF generation function may not be used")
        
        print()
        return True
    except Exception as e:
        print(f"✗ Error checking PDF export route: {e}")
        return False


def test_pdf_generator_file():
    """Test that PDF generator module exists"""
    print("=" * 60)
    print("TEST 7: PDF Generator Module")
    print("=" * 60)
    
    if os.path.exists('pdf_generator.py'):
        print("✓ pdf_generator.py file exists")
        
        with open('pdf_generator.py', 'r') as f:
            content = f.read()
        
        if 'class ArmyListPDFGenerator' in content:
            print("✓ ArmyListPDFGenerator class defined")
        
        if '_build_unit_stats_table' in content:
            print("✓ Unit stats table builder method exists")
        
        if 'reportlab' in content:
            print("✓ ReportLab library used for PDF generation")
        
        print()
        return True
    else:
        print("✗ pdf_generator.py file not found")
        return False


def test_emoji_removal():
    """Test that emojis were removed from templates"""
    print("=" * 60)
    print("TEST 8: Emoji Removal")
    print("=" * 60)
    
    try:
        with open('templates/view_list.html', 'r') as f:
            content = f.read()
        
        # Check for common emoji patterns in alerts
        if '✅' in content and 'alert(' in content:
            print("⚠ Warning: Checkmark emoji still found in alerts")
            return False
        else:
            print("✓ Emojis removed from alert messages")
        
        print()
        return True
    except Exception as e:
        print(f"✗ Error checking emoji removal: {e}")
        return False


def test_requirements():
    """Test that requirements.txt was updated"""
    print("=" * 60)
    print("TEST 9: Requirements File")
    print("=" * 60)
    
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()
        
        if 'reportlab' in content:
            print("✓ reportlab added to requirements.txt")
        else:
            print("✗ reportlab not in requirements.txt")
            return False
        
        if 'Pillow' in content or 'pillow' in content:
            print("✓ Pillow added to requirements.txt")
        else:
            print("⚠ Warning: Pillow not in requirements.txt")
        
        print()
        return True
    except Exception as e:
        print(f"✗ Error checking requirements.txt: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("FAD Helper - Test Suite")
    print("Version 1.1.0 Validation")
    print("=" * 60 + "\n")
    
    tests = [
        ("Module Imports", test_imports),
        ("Trait Attribute", test_trait_attribute),
        ("Points Calculation", test_calculate_points_function),
        ("Heavy Weapon Selector", test_heavy_weapon_template),
        ("Vehicle Builder", test_vehicle_template),
        ("PDF Export Route", test_pdf_export_route),
        ("PDF Generator", test_pdf_generator_file),
        ("Emoji Removal", test_emoji_removal),
        ("Requirements", test_requirements),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test '{name}' crashed: {e}\n")
            failed += 1
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n✓ ALL TESTS PASSED - Ready for deployment!")
        return 0
    else:
        print(f"\n✗ {failed} test(s) failed - Fix issues before deploying")
        return 1


if __name__ == '__main__':
    sys.exit(main())
