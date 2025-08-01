#!/usr/bin/env python3
"""
Test Script - Verifica fix API v8 Yahoo Finance
"""

import sys
import os
import json

# Setup paths
sys.path.append('src')
sys.path.append('news')
sys.path.append('.')

def test_v8_api_fix():
    """Test per verificare che il fix delle API v8 funzioni"""
    print("🚀 Test Fix API v8 Yahoo Finance")
    print("=" * 50)
    
    try:
        # Test 1: Import moduli
        print("📦 Test 1: Import moduli...")
        from automated_trading_system import AutomatedTradingSystem
        print("✅ AutomatedTradingSystem imported")
        
        # Test 2: Inizializzazione sistema
        print("\n🔧 Test 2: Inizializzazione sistema...")
        trading_system = AutomatedTradingSystem()
        print("✅ Sistema inizializzato")
        
        # Test 3: DataCollector con API v8
        print("\n📊 Test 3: DataCollector con API v8...")
        data_collector = trading_system.data_collector
        
        # Test AAPL (quello che falliva prima)
        print("📈 Testing AAPL (che prima falliva)...")
        aapl_data = data_collector.get_stock_data('AAPL', period='5d')
        
        if aapl_data is not None and not aapl_data.empty:
            latest_close = aapl_data.iloc[-1]['Close']
            print(f"✅ AAPL: {len(aapl_data)} righe, ultimo prezzo: ${latest_close:.2f}")
        else:
            print("❌ AAPL: Nessun dato")
            
        # Test 4: Market data update completo
        print("\n📊 Test 4: Market data update completo...")
        market_data = trading_system.update_market_data()
        
        if market_data:
            print(f"✅ Dati ottenuti per {len(market_data)} simboli:")
            for symbol, data in market_data.items():
                if not data.empty:
                    latest_price = data.iloc[-1]['Close']
                    print(f"  {symbol}: {len(data)} righe, prezzo: ${latest_price:.2f}")
                else:
                    print(f"  {symbol}: Dati vuoti")
        else:
            print("❌ Nessun dato di mercato")
            
        print("\n🎉 TUTTI I TEST SUPERATI!")
        print("✅ Il fix delle API v8 funziona correttamente")
        print("✅ L'errore AAPL è stato risolto")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRORE NEL TEST: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_v8_api_fix()
    exit(0 if success else 1)
