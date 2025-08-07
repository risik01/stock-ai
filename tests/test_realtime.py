#!/usr/bin/env python3
"""
Test Real-Time Data Collector
"""

import sys
import time
import os

# Aggiungi il path corretto
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

print("🔴 === TEST REAL-TIME DATA ===")

try:
    from realtime_data import RealTimeDataCollector
    
    collector = RealTimeDataCollector()
    print("✅ RealTimeDataCollector creato")
    
    # Test singolo simbolo
    print("\n📊 Test singolo simbolo (AAPL)...")
    for i in range(5):
        price = collector.get_current_price('AAPL')
        change = collector.get_price_change('AAPL')
        print(f"  Ciclo {i+1}: AAPL = ${price:.2f} (Δ{change*100:+.3f}%)")
        time.sleep(2)
    
    print("\n📈 Test tutti i simboli...")
    summary = collector.get_market_summary()
    
    print("🔴 === PREZZI REAL-TIME ===")
    for symbol, price in summary['prices'].items():
        change = summary['changes'][symbol]
        print(f"  {symbol}: ${price:.2f} (Δ{change*100:+.3f}%)")
    
    print(f"\n📊 Media variazione mercato: {summary['avg_change']*100:+.3f}%")
    print(f"⏰ Timestamp: {summary['timestamp']}")
    
    print("\n✅ Real-Time Data funzionante!")
    
except Exception as e:
    print(f"❌ Errore: {e}")
    import traceback
    traceback.print_exc()
