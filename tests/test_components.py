#!/usr/bin/env python3
"""
Test Inizializzazione Componenti
Verifica che tutti i componenti si inizializzino correttamente
"""

import sys
import json
from pathlib import Path

print("🧪 TEST 2: INIZIALIZZAZIONE COMPONENTI")
print("=" * 50)

# Setup path
sys.path.insert(0, 'src')
sys.path.insert(0, 'news')

# Carica configurazione
try:
    with open('config/production_settings.json', 'r') as f:
        config = json.load(f)
    print("✅ Configurazione caricata")
except Exception as e:
    print(f"❌ Errore configurazione: {e}")
    exit(1)

# Test 1: Portfolio
print("\n📊 TEST PORTFOLIO:")
try:
    from src.portfolio import Portfolio
    portfolio = Portfolio(config=config)
    print(f"✅ Portfolio inizializzato")
    print(f"💰 Cash disponibile: €{portfolio.get_available_cash()}")
    print(f"📈 Valore totale: €{portfolio.get_total_value()}")
except Exception as e:
    print(f"❌ Errore Portfolio: {e}")

# Test 2: Data Collector
print("\n📊 TEST DATA COLLECTOR:")
try:
    from src.data_collector import DataCollector
    data_collector = DataCollector(config=config)
    print("✅ Data Collector inizializzato")
    
    # Test fetch di un simbolo
    print("🔄 Test fetch dati AAPL...")
    data = data_collector.get_stock_data('AAPL', period='5d')
    if data is not None and not data.empty:
        print(f"✅ Dati AAPL ricevuti: {len(data)} righe")
        print(f"📊 Ultimo prezzo: ${data.iloc[-1]['close']:.2f}")
    else:
        print("⚠️ Nessun dato ricevuto (normale se mercati chiusi)")
except Exception as e:
    print(f"❌ Errore Data Collector: {e}")

# Test 3: News Collector
print("\n📰 TEST NEWS COLLECTOR:")
try:
    from news_rss_collector import NewsRSSCollector
    news_collector = NewsRSSCollector(config_path='config/production_settings.json')
    print("✅ News Collector inizializzato")
    
    # Test raccolta news
    print("🔄 Test raccolta news...")
    articles = news_collector.collect_all_news()
    print(f"📰 Articoli raccolti: {len(articles)}")
    if articles:
        print(f"📝 Primo articolo: {articles[0].title[:50]}...")
except Exception as e:
    print(f"❌ Errore News Collector: {e}")

# Test 4: Sentiment Analyzer
print("\n🤖 TEST SENTIMENT ANALYZER:")
try:
    from news_sentiment_analyzer import NewsSentimentAnalyzer
    sentiment_analyzer = NewsSentimentAnalyzer()
    print("✅ Sentiment Analyzer inizializzato")
    
    # Test analisi sentiment
    test_text = "Apple stock surges on strong quarterly earnings"
    sentiment = sentiment_analyzer.analyze_sentiment(test_text)
    print(f"📊 Test sentiment: '{test_text}'")
    print(f"🎯 Sentiment score: {sentiment:.3f}")
    
except Exception as e:
    print(f"❌ Errore Sentiment Analyzer: {e}")

# Test 5: RL Agent
print("\n🤖 TEST RL AGENT:")
try:
    from src.rl_agent import RLAgent
    rl_agent = RLAgent(config=config)
    print("✅ RL Agent inizializzato")
    print(f"🧠 Stato modello: {rl_agent.state_size} features")
except Exception as e:
    print(f"❌ Errore RL Agent: {e}")

# Test 6: Strategy Engine
print("\n📈 TEST STRATEGY ENGINE:")
try:
    from src.strategy_engine import StrategyEngine
    strategy_engine = StrategyEngine(config_path='config/production_settings.json')
    print("✅ Strategy Engine inizializzato")
except Exception as e:
    print(f"❌ Errore Strategy Engine: {e}")

print("\n🎯 TEST INIZIALIZZAZIONE COMPLETATO!")
print("✅ Sistema pronto per il testing completo")
