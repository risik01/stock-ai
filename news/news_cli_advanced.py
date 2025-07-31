#!/usr/bin/env python3
"""
CLI News Trading con controllo feed RSS e AI
"""

import argparse
import time
import json
from datetime import datetime
from news_rss_collector import NewsRSSCollector
from news_sentiment_analyzer import NewsSentimentAnalyzer
from news_based_trading_ai import NewsBasedTradingAI

def cmd_feeds_status(args):
    """Mostra stato dei feed RSS"""
    print("📡 STATO FEED RSS")
    print("="*60)
    
    collector = NewsRSSCollector()
    
    print(f"🔧 Configurazione:")
    print(f"   Update interval: {collector.update_interval}s ({collector.update_interval//60} min)")
    print(f"   User-Agent: {collector.user_agent}")
    print(f"   Feed configurati: {len(collector.rss_feeds)}")
    print(f"   ETag cache: {'✅ Attivo' if collector.etag_cache_enabled else '❌ Disattivo'}")
    print()
    
    print(f"📊 Feed RSS:")
    for name, url in collector.rss_feeds.items():
        last_fetch = collector.last_fetch_time.get(name, 0)
        if last_fetch > 0:
            time_since = time.time() - last_fetch
            next_fetch = max(0, collector.update_interval - time_since)
            status = f"🕒 Prossimo in {next_fetch:.0f}s" if next_fetch > 0 else "✅ Pronto"
        else:
            status = "🆕 Mai utilizzato"
        
        print(f"   {name:20} | {status:15} | {url[:50]}...")

def cmd_feeds_test(args):
    """Testa tutti i feed RSS forzando l'aggiornamento"""
    print("🧪 TEST COMPLETO FEED RSS")
    print("="*60)
    
    collector = NewsRSSCollector()
    
    # Forza reset rate limiting per test
    if args.force:
        print("⚡ Forzando aggiornamento (ignorando rate limit)...")
        collector.last_fetch_time = {}
    
    print(f"🔍 Testing {len(collector.rss_feeds)} feed RSS...")
    print()
    
    start_time = time.time()
    total_articles = 0
    
    for i, (name, url) in enumerate(collector.rss_feeds.items(), 1):
        print(f"{i:2d}. {name:20} ", end="", flush=True)
        
        feed_start = time.time()
        articles = collector.fetch_rss_feed(name, url)
        feed_time = time.time() - feed_start
        
        if articles:
            print(f"✅ {len(articles):2d} articoli ({feed_time:.2f}s)")
            total_articles += len(articles)
            
            # Mostra esempio se richiesto
            if args.verbose and articles:
                print(f"     └─ Esempio: {articles[0].title[:50]}...")
        else:
            print(f"❌ 0 articoli  ({feed_time:.2f}s)")
    
    total_time = time.time() - start_time
    print()
    print(f"📊 RISULTATO: {total_articles} articoli totali in {total_time:.1f}s")
    print(f"⚡ Media: {total_time/len(collector.rss_feeds):.2f}s per feed")

def cmd_ai_analysis(args):
    """Mostra analisi AI delle notizie"""
    print("🤖 ANALISI AI NOTIZIE")
    print("="*60)
    
    # Raccogli notizie
    collector = NewsRSSCollector()
    if args.force:
        collector.last_fetch_time = {}
    
    print("📡 Raccogliendo notizie...")
    articles = collector.collect_all_news()
    
    if not articles:
        print("❌ Nessuna notizia disponibile")
        return
    
    print(f"✅ {len(articles)} articoli raccolti")
    print()
    
    # Analisi sentiment
    analyzer = NewsSentimentAnalyzer()
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META', 'NVDA']
    
    print("🧠 Analizzando sentiment...")
    overview = analyzer.get_market_sentiment_overview(articles, symbols)
    
    print(f"📊 SENTIMENT GENERALE: {overview['market_sentiment']:.3f}")
    print(f"😊 MOOD MERCATO: {overview['market_mood']}")
    print(f"📰 Articoli analizzati: {overview['total_articles']}")
    print()
    
    if overview['symbol_details']:
        print("📈 DETTAGLI PER SIMBOLO:")
        for symbol, details in overview['symbol_details'].items():
            sentiment = details['sentiment_score']
            positive = details['positive_articles']  # Corretto!
            negative = details['negative_articles']  # Corretto!
            neutral = details['neutral_articles']    # Corretto!
            
            print(f"   {symbol}: {sentiment:+.3f} ({positive}+ {negative}- {neutral}=)")
        print()
    
    # Segnali trading
    print("🎯 Generando segnali trading...")
    signals = analyzer.generate_trading_signals(articles, symbols)
    
    if signals:
        print(f"⚡ {len(signals)} segnali generati:")
        for signal in signals:
            print(f"   {signal.symbol}: {signal.action} (conf: {signal.confidence:.2f})")
            print(f"      └─ {signal.reason}")
    else:
        print("❌ Nessun segnale generato")

def cmd_trading_ai(args):
    """Mostra stato Trading AI"""
    print("💼 TRADING AI STATUS")
    print("="*60)
    
    ai = NewsBasedTradingAI()
    
    # Portfolio status
    portfolio = ai.virtual_portfolio  # Corretto!
    print(f"💰 PORTFOLIO:")
    print(f"   Cash: ${portfolio['cash']:,.2f}")
    total_value = portfolio['cash'] + sum(
        pos.get('quantity', 0) * pos.get('last_price', 0) 
        for pos in portfolio['positions'].values()
    )
    print(f"   Valore totale: ${total_value:,.2f}")
    print(f"   Posizioni aperte: {len(portfolio['positions'])}")
    print(f"   Trades totali: {len(portfolio['trades'])}")
    print()
    
    if portfolio['positions']:
        print(f"📊 POSIZIONI ATTIVE:")
        for symbol, pos in portfolio['positions'].items():
            print(f"   {symbol}: {pos.get('quantity', 0)} shares @ ${pos.get('last_price', 0):.2f}")
        print()
    
    # Ciclo trading se richiesto
    if hasattr(args, 'run_cycle') and args.run_cycle:
        print("🔄 ESEGUENDO CICLO TRADING...")
        result = ai.run_trading_cycle()
        print(f"   Notizie processate: {result.get('news_processed', 0)}")
        print(f"   Segnali generati: {result.get('signals_generated', 0)}")
        print(f"   Trades eseguiti: {result.get('trades_executed', 0)}")

def main():
    parser = argparse.ArgumentParser(description="CLI News Trading avanzata")
    subparsers = parser.add_subparsers(dest='command', help='Comandi disponibili')
    
    # Comando feeds
    feeds_parser = subparsers.add_parser('feeds', help='Gestione feed RSS')
    feeds_subparsers = feeds_parser.add_subparsers(dest='feeds_action')
    
    # feeds status
    status_parser = feeds_subparsers.add_parser('status', help='Mostra stato feed')
    status_parser.set_defaults(func=cmd_feeds_status)
    
    # feeds test
    test_parser = feeds_subparsers.add_parser('test', help='Testa tutti i feed')
    test_parser.add_argument('--force', action='store_true', help='Forza aggiornamento ignorando rate limit')
    test_parser.add_argument('--verbose', '-v', action='store_true', help='Output verbose')
    test_parser.set_defaults(func=cmd_feeds_test)
    
    # Comando ai
    ai_parser = subparsers.add_parser('ai', help='Analisi AI notizie')
    ai_parser.add_argument('--force', action='store_true', help='Forza raccolta notizie')
    ai_parser.set_defaults(func=cmd_ai_analysis)
    
    # Comando trading
    trading_parser = subparsers.add_parser('trading', help='Trading AI status')
    trading_parser.add_argument('--run-cycle', action='store_true', help='Esegui ciclo trading')
    trading_parser.set_defaults(func=cmd_trading_ai)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Esegui comando
    try:
        args.func(args)
    except AttributeError:
        if args.command == 'feeds':
            feeds_parser.print_help()
        else:
            parser.print_help()
    except KeyboardInterrupt:
        print("\n⏹️  Operazione interrotta dall'utente")
    except Exception as e:
        print(f"\n❌ Errore: {e}")

if __name__ == "__main__":
    main()
