#!/usr/bin/env python3
"""
Test di un singolo feed RSS per verificare funzionamento
"""

import sys
import time
from news_rss_collector import NewsRSSCollector

def test_single_feed():
    print("🧪 TEST SINGOLO FEED RSS")
    print("="*50)
    
    # Inizializza collector
    collector = NewsRSSCollector()
    
    # Forza il reset del rate limiting per test
    collector.last_fetch_time = {}
    
    # Test Investing.com che dovrebbe funzionare
    feed_name = "investing_com"
    feed_url = "https://www.investing.com/rss/news.rss"
    
    print(f"📡 Testando: {feed_name}")
    print(f"🌐 URL: {feed_url}")
    print(f"🤖 User-Agent: {collector.user_agent}")
    print()
    
    start_time = time.time()
    articles = collector.fetch_rss_feed(feed_name, feed_url)
    end_time = time.time()
    
    print(f"⏱️  Tempo: {end_time - start_time:.2f}s")
    print(f"📰 Articoli trovati: {len(articles)}")
    
    if articles:
        print("\n📋 PRIMI 3 ARTICOLI:")
        for i, article in enumerate(articles[:3]):
            print(f"\n{i+1}. {article.title}")
            print(f"   📅 {article.published}")
            print(f"   🏷️  Simboli: {article.symbols}")
            print(f"   🔗 {article.url}")
    else:
        print("❌ Nessun articolo trovato")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    test_single_feed()
