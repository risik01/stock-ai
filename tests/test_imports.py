#!/usr/bin/env python3
"""
Test Import Sistema Trading AI
Verifica che tutti i moduli si importino correttamente
"""

import sys
import os
from pathlib import Path

print("🧪 TEST IMPORT SISTEMA TRADING AI")
print("=" * 50)

# Aggiungi path
sys.path.insert(0, 'src')
sys.path.insert(0, 'news')
sys.path.insert(0, '.')

print("📁 Path configurati:")
for p in sys.path[:5]:
    print(f"  {p}")

print("\n🔍 VERIFICA IMPORT STEP BY STEP:")

# Test 1: Import base
try:
    import json
    import pandas as pd
    import numpy as np
    print("✅ Librerie base (json, pandas, numpy)")
except ImportError as e:
    print(f"❌ Librerie base: {e}")
    exit(1)

# Test 2: Import src modules
try:
    from src.portfolio import Portfolio
    print("✅ src.portfolio.Portfolio")
except ImportError as e:
    print(f"❌ Portfolio: {e}")

try:
    from src.data_collector import DataCollector
    print("✅ src.data_collector.DataCollector")
except ImportError as e:
    print(f"❌ DataCollector: {e}")

try:
    from src.rl_agent import RLAgent
    print("✅ src.rl_agent.RLAgent")
except ImportError as e:
    print(f"❌ RLAgent: {e}")

try:
    from src.strategy_engine import StrategyEngine
    print("✅ src.strategy_engine.StrategyEngine")
except ImportError as e:
    print(f"❌ StrategyEngine: {e}")

# Test 3: Import news modules
try:
    from news_rss_collector import NewsRSSCollector
    print("✅ news_rss_collector.NewsRSSCollector")
except ImportError as e:
    print(f"❌ NewsRSSCollector: {e}")

try:
    from news_sentiment_analyzer import NewsSentimentAnalyzer
    print("✅ news_sentiment_analyzer.NewsSentimentAnalyzer")
except ImportError as e:
    print(f"❌ NewsSentimentAnalyzer: {e}")

try:
    from news_based_trading_ai import NewsBasedTradingAI
    print("✅ news_based_trading_ai.NewsBasedTradingAI")
except ImportError as e:
    print(f"❌ NewsBasedTradingAI: {e}")

# Test 4: Configurazione
print("\n📊 VERIFICA CONFIGURAZIONE:")
try:
    with open('config/production_settings.json', 'r') as f:
        config = json.load(f)
    
    print(f"💰 Budget: €{config['trading']['initial_capital']}")
    print(f"📈 Simboli: {config['data']['symbols']}")
    print(f"🤖 AI Models: {list(config['ai_trading']['models'].keys())}")
    print(f"⚠️ Max Daily Loss: {config['trading']['live_trading']['max_daily_loss']*100}%")
    print("✅ Configurazione valida")
    
except Exception as e:
    print(f"❌ Errore configurazione: {e}")

# Test 5: File essenziali
print("\n📁 VERIFICA FILE ESSENZIALI:")
essential_files = [
    'automated_trading_system.py',
    'setup_ubuntu.sh',
    'trading_control.sh',
    'requirements.txt',
    '.env.example'
]

for file in essential_files:
    if Path(file).exists():
        print(f"✅ {file}")
    else:
        print(f"❌ {file} MANCANTE")

print("\n🎯 TEST IMPORT COMPLETATO!")
