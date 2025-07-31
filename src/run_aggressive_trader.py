#!/usr/bin/env python3
"""
Launcher per il trader aggressivo
Uso: python run_aggressive_trader.py
"""

import sys
import os
import subprocess
import time
from datetime import datetime

# Aggiungi il path src
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def check_dependencies():
    """Controlla che tutte le dipendenze siano installate"""
    try:
        import yfinance
        import pandas
        import numpy
        print("✅ Dipendenze verificate")
        return True
    except ImportError as e:
        print(f"❌ Dipendenza mancante: {e}")
        print("   Esegui: pip install -r requirements.txt")
        return False

def main():
    print("🤖 AGGRESSIVE TRADING BOT LAUNCHER")
    print("=" * 50)
    print(f"Avvio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    if not check_dependencies():
        return 1
    
    print("🚀 Avviando il trader aggressivo...")
    print("   Premi Ctrl+C per fermare")
    print("   Oppure esegui: python src/main.py CLOSEALL")
    print()
    
    try:
        # Avvia il trader aggressivo
        from src.aggressive_trader import main as trader_main
        trader_main()
        
    except KeyboardInterrupt:
        print("\n🛑 Trader fermato dall'utente")
        return 0
    except Exception as e:
        print(f"❌ Errore: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
