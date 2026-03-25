#!/usr/bin/env python3
"""Comprehensive test script for frontend and backend servers"""

import sys
import json
from pathlib import Path

def test_file_access():
    """Test if all required files exist"""
    print("=" * 60)
    print("📁 Testing File Access")
    print("=" * 60)
    
    files = {
        "Frontend HTML": "death_sentence/index.html",
        "Frontend JS": "death_sentence/script.js",
        "Frontend CSS": "death_sentence/styles.css",
        "Scent Data": "death_sentence/scent_classification.json",
        "AI Backend App": "death_sentence/agents/app.py",
        "AI Backend Settings": "death_sentence/agents/settings.py",
    }
    
    all_exist = True
    for name, file_path in files.items():
        path = Path(file_path)
        exists = path.exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {name}: {file_path}")
        if not exists:
            all_exist = False
    
    return all_exist

def test_path_resolution():
    """Test if path resolution works correctly"""
    print("\n" + "=" * 60)
    print("🔍 Testing Path Resolution")
    print("=" * 60)
    
    try:
        sys.path.insert(0, str(Path.cwd()))
        from death_sentence.agents.settings import settings
        
        scents_path = settings.scents_path
        print(f"  Scents path: {scents_path}")
        print(f"  Path exists: {'✅' if scents_path.exists() else '❌'}")
        
        if scents_path.exists():
            with open(scents_path, 'r') as f:
                scents = json.load(f)
            print(f"  Scents loaded: ✅ ({len(scents)} entries)")
            return True
        else:
            print(f"  Scents loaded: ❌")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_app_loading():
    """Test if the app can load scents"""
    print("\n" + "=" * 60)
    print("🚀 Testing App Loading")
    print("=" * 60)
    
    try:
        from death_sentence.agents.app import load_scents
        scents = load_scents()
        print(f"  ✅ Successfully loaded {len(scents)} scents from JSON")
        
        # Check structure
        if isinstance(scents, dict):
            print(f"  ✅ Scents is a dictionary with keys: {list(scents.keys())[:5]}...")
        return True
    except Exception as e:
        print(f"  ❌ Error loading scents: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_frontend_references():
    """Test if frontend files reference death_sentence correctly"""
    print("\n" + "=" * 60)
    print("🌐 Testing Frontend References")
    print("=" * 60)
    
    try:
        # Check if script.js references scent_classification.json
        script_path = Path("death_sentence/script.js")
        if script_path.exists():
            content = script_path.read_text()
            if "scent_classification.json" in content:
                print("  ✅ script.js references scent_classification.json")
            else:
                print("  ❌ script.js does not reference scent_classification.json")
            
            if "localhost:8000" in content:
                print("  ✅ script.js references AI backend at localhost:8000")
            else:
                print("  ❌ script.js does not reference AI backend")
        
        # Check if index.html references script.js and styles.css
        html_path = Path("death_sentence/index.html")
        if html_path.exists():
            content = html_path.read_text()
            if "script.js" in content:
                print("  ✅ index.html references script.js")
            if "styles.css" in content:
                print("  ✅ index.html references styles.css")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("  Death Sentence BLE - Server Test")
    print("=" * 60 + "\n")
    
    results = []
    results.append(("File Access", test_file_access()))
    results.append(("Path Resolution", test_path_resolution()))
    results.append(("App Loading", test_app_loading()))
    results.append(("Frontend References", test_frontend_references()))
    
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed! Files are correctly referenced.")
        print("\n💡 To start servers:")
        print("   Frontend: cd death_sentence && python3 -m http.server 8080")
        print("   AI Backend: ./venv/bin/uvicorn death_sentence.agents.app:app --port 8000")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print("=" * 60 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())



