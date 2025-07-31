#!/usr/bin/env python3
"""
Test completo del sistema di trading basato su notizie
"""

import asyncio
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

# Aggiungi il path per import
sys.path.append(str(Path(__file__).parent))

from news_rss_collector import NewsRSSCollector
from news_sentiment_analyzer import NewsSentimentAnalyzer
from news_based_trading_ai import NewsBasedTradingAI

def test_news_collection():
    """Test raccolta notizie RSS"""
    print("🧪 TEST 1: Raccolta Notizie RSS")
    print("-" * 50)
    
    collector = NewsRSSCollector()
    
    # Test raccolta base
    print("📡 Test raccolta base...")
    articles = collector.collect_all_news()
    print(f"✅ Raccolti {len(articles)} articoli")
    
    if articles:
        # Mostra esempio di articolo
        sample = articles[0]
        print(f"\n📰 Esempio articolo:")
        print(f"   Titolo: {sample.title}")
        print(f"   Fonte: {sample.source}")
        print(f"   Simboli: {', '.join(sample.symbols) if sample.symbols else 'Nessuno'}")
        print(f"   Pubblicato: {sample.published}")
        print(f"   URL: {sample.url}")
    
    # Test breaking news
    print(f"\n🚨 Test breaking news...")
    breaking = collector.get_breaking_news(minutes=60)
    print(f"✅ Trovate {len(breaking)} breaking news nell'ultima ora")
    
    # Test filtro per simbolo
    print(f"\n🎯 Test filtro simboli...")
    aapl_news = [article for article in articles if 'AAPL' in article.symbols]
    print(f"✅ Trovate {len(aapl_news)} notizie per AAPL")
    
    # Test performance
    print(f"\n⚡ Test performance...")
    start_time = time.time()
    collector.collect_all_news()
    elapsed = time.time() - start_time
    print(f"✅ Raccolta completata in {elapsed:.2f} secondi")
    
    print("✅ Test raccolta notizie COMPLETATO\n")
    return True

def test_sentiment_analysis():
    """Test analisi sentiment"""
    print("🧪 TEST 2: Analisi Sentiment")
    print("-" * 50)
    
    collector = NewsRSSCollector()
    analyzer = NewsSentimentAnalyzer()
    
    # Raccoglie notizie per test
    print("📡 Raccolta notizie per analisi...")
    articles = collector.collect_all_news()
    
    if not articles:
        print("❌ Nessuna notizia disponibile per test sentiment")
        return False
    
    print(f"✅ Analizzando {len(articles)} articoli")
    
    # Test analisi singolo articolo
    print(f"\n🔍 Test analisi articolo singolo...")
    sample_article = articles[0]
    sentiment = analyzer.analyze_article_sentiment(sample_article)
    
    print(f"   Articolo: {sample_article.title[:50]}...")
    print(f"   Sentiment Score: {sentiment.sentiment_score:.3f}")
    print(f"   Confidence: {sentiment.confidence:.3f}")
    print(f"   Mood: {sentiment.sentiment_label}")
    print(f"   Metodi: TextBlob={sentiment.textblob_score:.3f}, "
          f"VADER={sentiment.vader_score:.3f}, Finance={sentiment.finance_score:.3f}")
    
    # Test overview mercato
    print(f"\n📊 Test overview sentiment mercato...")
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
    overview = analyzer.get_market_sentiment_overview(articles, symbols)
    
    print(f"   Sentiment Generale: {overview['market_sentiment']:.3f}")
    print(f"   Mood Mercato: {overview['market_mood']}")
    print(f"   Articoli Totali: {overview['total_articles']}")
    
    print(f"\n   Dettagli per simbolo:")
    for symbol, data in overview['symbol_details'].items():
        if data['article_count'] > 0:
            print(f"   📈 {symbol}: {data['sentiment_score']:.3f} "
                  f"({data['positive_articles']}+ {data['negative_articles']}- "
                  f"{data['neutral_articles']}=)")
    
    # Test generazione segnali
    print(f"\n🎯 Test generazione segnali trading...")
    signals = analyzer.generate_trading_signals(articles, symbols)
    
    print(f"✅ Generati {len(signals)} segnali")
    for signal in signals[:5]:  # Mostra primi 5
        print(f"   🤖 {signal.symbol}: {signal.action} "
              f"(conf: {signal.confidence:.2f}, sentiment: {signal.sentiment_score:.2f})")
        print(f"      📝 {signal.reason}")
    
    # Test performance
    print(f"\n⚡ Test performance analisi...")
    start_time = time.time()
    analyzer.get_market_sentiment_overview(articles[:10], symbols)
    elapsed = time.time() - start_time
    print(f"✅ Analisi completata in {elapsed:.2f} secondi")
    
    print("✅ Test analisi sentiment COMPLETATO\n")
    return True

def test_trading_ai():
    """Test sistema trading AI completo"""
    print("🧪 TEST 3: Sistema Trading AI")
    print("-" * 50)
    
    trading_ai = NewsBasedTradingAI()
    
    # Test stato iniziale
    print("💰 Test stato iniziale portfolio...")
    initial_portfolio = trading_ai.get_portfolio_status()
    print(f"✅ Cash iniziale: ${initial_portfolio['cash']:,.2f}")
    print(f"✅ Valore totale: ${initial_portfolio['total_portfolio_value']:,.2f}")
    print(f"✅ Trades iniziali: {initial_portfolio['trade_count']}")
    
    # Test ciclo trading singolo
    print(f"\n🔄 Test ciclo trading singolo...")
    result = trading_ai.run_trading_cycle()
    
    print(f"✅ Risultati ciclo:")
    print(f"   📰 Notizie fresche: {result.get('fresh_news_count', 0)}")
    print(f"   🎯 Segnali generati: {result.get('signals_generated', 0)}")
    print(f"   💼 Trades eseguiti: {result.get('trades_executed', 0)}")
    print(f"   🚨 Alert generati: {result.get('alerts_generated', 0)}")
    
    # Mostra trades eseguiti
    if result.get('executed_trades'):
        print(f"\n   📋 Trades eseguiti:")
        for trade in result['executed_trades']:
            print(f"      🔄 {trade['action']} {trade['quantity']} {trade['symbol']} "
                  f"@ ${trade['price']:.2f}")
            print(f"         📝 {trade['reason']}")
    
    # Test stato portfolio dopo trading
    print(f"\n💰 Test portfolio dopo trading...")
    post_portfolio = trading_ai.get_portfolio_status()
    print(f"✅ Cash finale: ${post_portfolio['cash']:,.2f}")
    print(f"✅ Valore totale: ${post_portfolio['total_portfolio_value']:,.2f}")
    print(f"✅ Trades totali: {post_portfolio['trade_count']}")
    
    # Test posizioni aperte
    if post_portfolio.get('positions'):
        print(f"\n📊 Posizioni aperte:")
        for symbol, pos in post_portfolio['positions'].items():
            pnl = pos['unrealized_pnl']
            print(f"   📈 {symbol}: {pos['shares']} azioni @ ${pos['current_price']:.2f} "
                  f"(P&L: ${pnl:+.2f})")
    
    # Test alert attivi
    print(f"\n🚨 Test alert attivi...")
    alerts = trading_ai.get_active_alerts()
    print(f"✅ Alert attivi: {len(alerts)}")
    
    for alert in alerts[:3]:  # Mostra primi 3
        print(f"   🚨 {alert['symbol']}: {alert['message']} ({alert['severity']})")
    
    # Test export report
    print(f"\n📄 Test export report...")
    report_file = trading_ai.export_trading_report()
    print(f"✅ Report esportato: {report_file}")
    
    print("✅ Test trading AI COMPLETATO\n")
    return True

def test_integration():
    """Test integrazione completa"""
    print("🧪 TEST 4: Integrazione Completa")
    print("-" * 50)
    
    trading_ai = NewsBasedTradingAI()
    
    print("🚀 Simulazione giornata di trading...")
    
    # Simula 3 cicli di trading
    for cycle in range(1, 4):
        print(f"\n🔄 Ciclo {cycle}/3...")
        
        result = trading_ai.run_trading_cycle()
        
        portfolio = result['portfolio_status']
        print(f"   💰 Portfolio: ${portfolio['total_portfolio_value']:,.2f}")
        print(f"   📊 Trades: {result.get('trades_executed', 0)}")
        print(f"   🎯 Segnali: {result.get('signals_generated', 0)}")
        
        # Piccola pausa per simulare tempo reale
        time.sleep(2)
    
    # Statistiche finali
    print(f"\n📊 STATISTICHE FINALI:")
    final_portfolio = trading_ai.get_portfolio_status()
    
    # Ottieni valore iniziale dal trading_ai o usa default
    initial_value = trading_ai.virtual_portfolio.get('initial_cash', 10000)
    final_value = final_portfolio['total_portfolio_value']
    performance = ((final_value - initial_value) / initial_value) * 100
    
    print(f"   💵 Valore Iniziale: ${initial_value:,.2f}")
    print(f"   💰 Valore Finale: ${final_value:,.2f}")
    print(f"   📈 Performance: {performance:+.2f}%")
    print(f"   🔄 Trades Totali: {final_portfolio['trade_count']}")
    print(f"   📊 Posizioni Aperte: {len(final_portfolio.get('positions', {}))}")
    
    # Analisi performance
    if performance > 0:
        print(f"   ✅ Performance POSITIVA!")
    elif performance < -5:  # Solo se performance molto negativa
        print(f"   ⚠️  Performance negativa significativa")
    else:
        print(f"   ➡️  Performance stabile")
    
    print("✅ Test integrazione COMPLETATO\n")
    return True

def run_comprehensive_test():
    """Esegue tutti i test"""
    print("🧪 SISTEMA DI TEST COMPLETO - NEWS TRADING AI")
    print("=" * 60)
    print("⚠️  MODALITÀ SIMULAZIONE - Portfolio Virtuale")
    print("📅 Data:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    
    tests = [
        ("Raccolta Notizie RSS", test_news_collection),
        ("Analisi Sentiment", test_sentiment_analysis),
        ("Trading AI", test_trading_ai),
        ("Integrazione", test_integration)
    ]
    
    results = {}
    start_time = time.time()
    
    for test_name, test_func in tests:
        try:
            print(f"\n🎯 Avvio test: {test_name}")
            result = test_func()
            results[test_name] = "✅ SUCCESSO" if result else "❌ FALLITO"
        except Exception as e:
            print(f"❌ ERRORE in {test_name}: {e}")
            results[test_name] = f"❌ ERRORE: {str(e)}"
            import traceback
            traceback.print_exc()
    
    total_time = time.time() - start_time
    
    # Report finale
    print("\n" + "=" * 60)
    print("📋 REPORT FINALE DEI TEST")
    print("=" * 60)
    
    success_count = 0
    for test_name, result in results.items():
        print(f"{result} {test_name}")
        if "✅" in result:
            success_count += 1
    
    print(f"\n📊 Statistiche:")
    print(f"   ✅ Test superati: {success_count}/{len(tests)}")
    print(f"   ⏱️  Tempo totale: {total_time:.2f} secondi")
    print(f"   📈 Percentuale successo: {(success_count/len(tests)*100):.1f}%")
    
    if success_count == len(tests):
        print(f"\n🎉 TUTTI I TEST SUPERATI! Sistema pronto per l'uso.")
    else:
        print(f"\n⚠️  Alcuni test falliti. Verifica i log sopra.")
    
    print("=" * 60)

if __name__ == "__main__":
    run_comprehensive_test()
