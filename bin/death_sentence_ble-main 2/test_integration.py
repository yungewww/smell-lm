#!/usr/bin/env python3
"""
Integration Test Script for Death Sentence BLE System

This script verifies that the integration is properly set up.
"""

import json
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} NOT FOUND: {filepath}")
        return False

def check_json_structure(filepath):
    """Validate JSON file structure"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Check for duplicate locations
        locations = []
        for scent_name, scent_data in data.items():
            if 'location' in scent_data:
                loc = str(scent_data['location'])
                if loc in locations:
                    print(f"⚠️  WARNING: Duplicate location '{loc}' found for '{scent_name}'")
                    return False
                locations.append(loc)
        
        print(f"✅ Valid scent_classification.json with {len(data)} scents")
        print(f"   Locations: {sorted(locations, key=int)}")
        return True
    except Exception as e:
        print(f"❌ Error reading JSON: {e}")
        return False

def check_cors_in_backend():
    """Check if CORS is enabled in backend"""
    try:
        with open('backend.py', 'r') as f:
            content = f.read()
        
        if 'flask_cors' in content and 'CORS(app)' in content:
            print("✅ CORS enabled in backend.py")
            return True
        else:
            print("❌ CORS not found in backend.py")
            return False
    except Exception as e:
        print(f"❌ Error checking backend: {e}")
        return False

def check_integration_code():
    """Check if integration code exists in script.js"""
    try:
        with open('death_sentence/script.js', 'r') as f:
            content = f.read()
        
        checks = [
            ('playSequenceOnDevice' in content, "Play sequence function"),
            ('testBLEConnection' in content, "Test BLE connection function"),
            ('localhost:5001' in content, "BLE backend URL"),
            ('currentSequence' in content, "Sequence storage"),
        ]
        
        all_good = True
        for check, description in checks:
            if check:
                print(f"✅ {description} found")
            else:
                print(f"❌ {description} NOT found")
                all_good = False
        
        return all_good
    except Exception as e:
        print(f"❌ Error checking script.js: {e}")
        return False

def main():
    print("=" * 60)
    print("  Death Sentence BLE - Integration Test")
    print("=" * 60)
    print()
    
    all_checks = []
    
    print("📁 Checking file structure...")
    all_checks.append(check_file_exists('backend.py', 'BLE Backend'))
    all_checks.append(check_file_exists('death_sentence/agents/app.py', 'AI Backend'))
    all_checks.append(check_file_exists('death_sentence/index.html', 'Frontend HTML'))
    all_checks.append(check_file_exists('death_sentence/script.js', 'Frontend JS'))
    all_checks.append(check_file_exists('death_sentence/styles.css', 'Frontend CSS'))
    all_checks.append(check_file_exists('death_sentence/scent_classification.json', 'Scent Data'))
    print()
    
    print("🔍 Checking scent data integrity...")
    all_checks.append(check_json_structure('death_sentence/scent_classification.json'))
    print()
    
    print("🔌 Checking backend CORS configuration...")
    all_checks.append(check_cors_in_backend())
    print()
    
    print("🔗 Checking integration code...")
    all_checks.append(check_integration_code())
    print()
    
    print("📦 Checking dependencies...")
    try:
        import flask
        print(f"✅ Flask installed (v{flask.__version__})")
        all_checks.append(True)
    except ImportError:
        print("❌ Flask not installed")
        all_checks.append(False)
    
    try:
        import flask_cors
        print(f"✅ Flask-CORS installed")
        all_checks.append(True)
    except ImportError:
        print("❌ Flask-CORS not installed - run: pip install flask-cors")
        all_checks.append(False)
    
    try:
        import bleak
        print(f"✅ Bleak installed (BLE library)")
        all_checks.append(True)
    except ImportError:
        print("❌ Bleak not installed")
        all_checks.append(False)
    
    print()
    print("=" * 60)
    
    if all(all_checks):
        print("✨ SUCCESS! All integration checks passed!")
        print()
        print("Next steps:")
        print("1. Set OPENAI_API_KEY: export OPENAI_API_KEY='your-key'")
        print("2. Start BLE backend: ./start_ble_backend.sh")
        print("3. Start AI backend: ./start_ai_backend.sh")
        print("4. Start frontend: ./start_frontend.sh")
        print("5. Open http://localhost:8080")
        return 0
    else:
        print("⚠️  Some checks failed. Please review the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())


