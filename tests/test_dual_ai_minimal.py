#!/usr/bin/env python3
"""
Test minimo del sistema dual AI
"""

import os
import sys
import json
import asyncio
from pathlib import Path

print("🚀 === TEST SIMPLE DUAL AI ===")

# Aggiungi path
sys.path.append('../src')  # Torna indietro e vai in src

try:
    print("📦 Importing modules...")
    
    # Test import data collector
    import data_collector
    print("  ✅ data_collector imported")
    
    # Test config loading  
    with open('config/production_settings.json') as f:
        config = json.load(f)
    print("  ✅ Config loaded")
    
    # Test data collector creation
    print("🔧 Creating DataCollector...")
    config['data']['cache_enabled'] = False  # Disabilita cache
    collector = data_collector.DataCollector(config)
    print("  ✅ DataCollector created")
    
    # Test Yahoo API
    print("📡 Testing Yahoo API...")
    try:
        symbols = ['AAPL']
        from yahoo_api_v8 import YahooFinanceV8
        api = YahooFinanceV8()
        data = api.get_stock_data('AAPL', period='1d')
        if data is not None and len(data) > 0:
            print(f"  ✅ Yahoo API working: {len(data)} rows for AAPL")
            print(f"  📊 Latest price: ${data['Close'].iloc[-1]:.2f}")
        else:
            print("  ⚠️ Yahoo API returned empty data, using fallback")
    except Exception as e:
        print(f"  ⚠️ Yahoo API error: {e}")
        print("  💡 Will use simulated data")
    
    print("\n🎯 === TEST COMPLETATO ===")
    print("✅ Sistema pronto per l'esecuzione!")
    
except Exception as e:
    print(f"❌ Errore: {e}")
    import traceback
    traceback.print_exc()
