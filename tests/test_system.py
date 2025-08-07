#!/usr/bin/env python3
"""
Test Script per Stock AI System
"""

import os
import sys
import json

print("🔍 === DIAGNOSI SISTEMA STOCK AI ===")
print(f"📁 Working Directory: {os.getcwd()}")
print(f"🐍 Python Version: {sys.version}")

# Test 1: Verifica file essenziali
files_to_check = [
    'config/production_settings.json',
    'config/settings.json', 
    'src/simple_dual_ai.py',
    'src/main.py',
    'requirements.txt'
]

print("\n📋 Test esistenza file:")
for file_path in files_to_check:
    exists = "✅" if os.path.exists(file_path) else "❌"
    print(f"  {exists} {file_path}")

# Test 2: Import moduli critici
print("\n🧪 Test import moduli:")
modules_to_test = [
    'pandas',
    'numpy', 
    'yfinance',
    'requests',
    'asyncio'
]

for module in modules_to_test:
    try:
        __import__(module)
        print(f"  ✅ {module}")
    except ImportError as e:
        print(f"  ❌ {module}: {e}")

# Test 3: Configurazione
print("\n⚙️ Test configurazione:")
try:
    with open('config/production_settings.json') as f:
        config = json.load(f)
    print(f"  ✅ Config caricata: {len(config)} sezioni")
    
    if 'data' in config:
        symbols = config['data'].get('symbols', [])
        print(f"  📊 Simboli configurati: {len(symbols)}")
        print(f"  📈 Simboli: {', '.join(symbols[:3])}{'...' if len(symbols) > 3 else ''}")
    
except Exception as e:
    print(f"  ❌ Errore config: {e}")

# Test 4: Ambiente virtuale
print(f"\n🌐 Virtual Environment: {sys.prefix}")
print(f"📦 Packages path: {sys.path[0]}")

print("\n🎯 === DIAGNOSI COMPLETATA ===")
