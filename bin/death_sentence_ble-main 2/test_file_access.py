#!/usr/bin/env python3
"""Test script to verify file access in death_sentence folder"""

import sys
from pathlib import Path

print("=" * 60)
print("Testing File Access in death_sentence folder")
print("=" * 60)
print()

# Test 1: Check if files exist
print("📁 Testing file existence:")
files_to_check = [
    "death_sentence/index.html",
    "death_sentence/script.js",
    "death_sentence/styles.css",
    "death_sentence/scent_classification.json",
    "death_sentence/agents/app.py",
    "death_sentence/agents/settings.py",
]

all_exist = True
for file_path in files_to_check:
    path = Path(file_path)
    exists = path.exists()
    status = "✅" if exists else "❌"
    print(f"  {status} {file_path}")
    if not exists:
        all_exist = False

print()

# Test 2: Check settings path resolution
print("🔍 Testing path resolution:")
try:
    sys.path.insert(0, str(Path.cwd()))
    from death_sentence.agents.settings import settings
    
    scents_path = settings.scents_path
    print(f"  Scents path: {scents_path}")
    print(f"  Path exists: {'✅' if scents_path.exists() else '❌'}")
    
    if scents_path.exists():
        import json
        with open(scents_path, 'r') as f:
            scents = json.load(f)
        print(f"  Scents loaded: ✅ ({len(scents)} entries)")
    else:
        print(f"  Scents loaded: ❌")
        
except Exception as e:
    print(f"  ❌ Error: {e}")
    all_exist = False

print()

# Test 3: Check if we can load the app
print("🚀 Testing app import:")
try:
    from death_sentence.agents.app import load_scents
    scents = load_scents()
    print(f"  ✅ Successfully loaded {len(scents)} scents from JSON")
except Exception as e:
    print(f"  ❌ Error loading scents: {e}")
    all_exist = False

print()
print("=" * 60)
if all_exist:
    print("✅ All file access tests passed!")
else:
    print("❌ Some file access tests failed!")
print("=" * 60)



