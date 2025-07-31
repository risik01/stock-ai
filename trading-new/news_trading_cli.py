#!/usr/bin/env python3
"""
News Trading CLI - Interfaccia a riga di comando per il trading basato su notizie
"""

import argparse
import sys
import time
import json
from datetime import datetime
from pathlib import Path

# Aggiungi il path per import
sys.path.append(str(Path(__file__).parent))

from news_based_trading_ai import NewsBasedTradingAI
from news_rss_collector import NewsRSSCollector
from news_sentiment_analyzer import NewsSentimentAnalyzer

def show_news_analysis(args):
    """Mostra analisi delle notizie correnti"""
    print("📰 Analisi Notizie Finanziarie...")
    
    collector = NewsRSSCollector()
    analyzer = NewsSentimentAnalyzer()
    
    # Raccoglie notizie
    articles = collector.collect_all_news()
    
    if not articles:
        print("❌ Nessuna notizia trovata")
        return
    
    print(f"✅ Raccolti {len(articles)} articoli")
    
    # Mostra breaking news
    breaking = collector.get_breaking_news(minutes=60)
    if breaking:
        print(f"\n🚨 BREAKING NEWS (ultima ora):")
        for news in breaking[:5]:
            symbols_str = ', '.join(news.symbols) if news.symbols else 'General'
            print(f"   📰 {news.title}")
            print(f"      🏷️  {symbols_str} | 🕒 {news.published.strftime('%H:%M')} | 📡 {news.source}")
    
    # Analisi sentiment per simbolo
    symbols = args.symbols if args.symbols else ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
    market_overview = analyzer.get_market_sentiment_overview(articles, symbols)
    
    print(f"\n📊 SENTIMENT MERCATO:")
    print(f"   🎯 Sentiment Generale: {market_overview['market_sentiment']:.3f}")
    print(f"   😊 Mood: {market_overview['market_mood']}")
    print(f"   📰 Articoli Totali: {market_overview['total_articles']}")
    
    print(f"\n📈 SENTIMENT PER SIMBOLO:")
    for symbol, data in market_overview['symbol_details'].items():
        if data['article_count'] > 0:
            sentiment = data['sentiment_score']
            emoji = "📈" if sentiment > 0.1 else "📉" if sentiment < -0.1 else "➡️"
            print(f"   {emoji} {symbol}: {sentiment:.3f} "
                  f"({data['positive_articles']}+ {data['negative_articles']}- "
                  f"{data['neutral_articles']}=)")

def show_trading_signals(args):
    """Mostra segnali di trading basati su notizie"""
    print("🎯 Segnali di Trading basati su Notizie...")
    
    collector = NewsRSSCollector()
    analyzer = NewsSentimentAnalyzer()
    
    # Raccoglie notizie recenti
    articles = collector.collect_all_news()
    
    if not articles:
        print("❌ Nessuna notizia trovata")
        return
    
    # Genera segnali
    symbols = args.symbols if args.symbols else ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
    signals = analyzer.generate_trading_signals(articles, symbols)
    
    print(f"\n🤖 SEGNALI DI TRADING:")
    
    if not signals:
        print("   ❌ Nessun segnale generato")
        return
    
    for signal in signals:
        action_emoji = "🟢" if signal.action == 'BUY' else "🔴" if signal.action == 'SELL' else "🟡"
        print(f"   {action_emoji} {signal.symbol}: {signal.action} "
              f"(conf: {signal.confidence:.2f}, sentiment: {signal.sentiment_score:.2f})")
        print(f"      📝 {signal.reason}")
        print(f"      📰 Basato su {signal.news_count} notizie")

def run_trading_cycle(args):
    """Esegue un singolo ciclo di trading"""
    print("🔄 Esecuzione Ciclo di Trading...")
    
    trading_ai = NewsBasedTradingAI()
    
    # Esegui ciclo
    result = trading_ai.run_trading_cycle()
    
    print(f"\n📊 RISULTATI CICLO:")
    print(f"   📰 Notizie fresche: {result.get('fresh_news_count', 0)}")
    print(f"   🎯 Segnali generati: {result.get('signals_generated', 0)}")
    print(f"   💼 Trades eseguiti: {result.get('trades_executed', 0)}")
    print(f"   🚨 Alert generati: {result.get('alerts_generated', 0)}")
    
    # Portfolio status
    portfolio = result['portfolio_status']
    print(f"\n💰 PORTFOLIO STATUS:")
    print(f"   💵 Cash: ${portfolio['cash']:,.2f}")
    print(f"   📈 Valore Totale: ${portfolio['total_portfolio_value']:,.2f}")
    print(f"   🔄 Trades Totali: {portfolio['trade_count']}")
    
    # Trades eseguiti
    if result.get('executed_trades'):
        print(f"\n📋 TRADES ESEGUITI:")
        for trade in result['executed_trades']:
            action_emoji = "🟢" if trade['action'] == 'BUY' else "🔴"
            print(f"   {action_emoji} {trade['action']} {trade['quantity']} {trade['symbol']} "
                  f"@ ${trade['price']:.2f}")
            print(f"      📝 {trade['reason']}")
            print(f"      📊 Sentiment: {trade['news_sentiment']:.2f}, Conf: {trade['confidence']:.2f}")
    
    # Alert critici
    if result.get('active_alerts'):
        print(f"\n🚨 ALERT ATTIVI:")
        for alert in result['active_alerts']:
            severity_emoji = "🔴" if alert['severity'] == 'critical' else "🟡"
            print(f"   {severity_emoji} {alert['symbol']}: {alert['message']}")

def start_automated_trading(args):
    """Avvia trading automatico"""
    print("🚀 Avvio Trading Automatico basato su Notizie...")
    print("⚠️  MODALITÀ SIMULAZIONE - Portfolio Virtuale")
    print("⚠️  Premi Ctrl+C per fermare")
    print("-" * 60)
    
    trading_ai = NewsBasedTradingAI()
    
    # Configurazione
    interval = args.interval if args.interval else 10
    
    print(f"⚙️  Configurazione:")
    print(f"   🔄 Ciclo ogni: {interval} minuti")
    print(f"   📊 Simboli monitorati: {', '.join(trading_ai.monitored_symbols)}")
    print(f"   💰 Capitale iniziale: ${trading_ai.virtual_portfolio['cash']:,.2f}")
    
    try:
        # Avvia trading automatico
        trading_ai.start_automated_trading(cycle_interval_minutes=interval)
        
        print("\n✅ Trading automatico avviato!")
        print("📊 Status in tempo reale:")
        
        # Loop di monitoraggio
        while trading_ai.is_running:
            portfolio = trading_ai.get_portfolio_status()
            
            # Calcola performance
            initial_value = 100000  # Valore iniziale di default
            current_value = portfolio['total_portfolio_value']
            performance = ((current_value - initial_value) / initial_value) * 100
            
            performance_emoji = "📈" if performance > 0 else "📉" if performance < 0 else "➡️"
            
            print(f"\r💰 Portfolio: ${current_value:,.2f} "
                  f"({performance_emoji} {performance:+.2f}%) | "
                  f"Trades: {portfolio['trade_count']} | "
                  f"Posizioni: {len(portfolio.get('positions', {}))}", 
                  end='', flush=True)
            
            time.sleep(30)  # Aggiorna ogni 30 secondi
            
    except KeyboardInterrupt:
        print(f"\n🛑 Fermando trading automatico...")
        trading_ai.stop_trading()
        
        # Mostra summary finale
        final_portfolio = trading_ai.get_portfolio_status()
        print(f"\n📊 SUMMARY FINALE:")
        print(f"   💵 Cash: ${final_portfolio['cash']:,.2f}")
        print(f"   📈 Valore Totale: ${final_portfolio['total_portfolio_value']:,.2f}")
        print(f"   🔄 Trades Eseguiti: {final_portfolio['trade_count']}")
        
        if final_portfolio.get('positions'):
            print(f"   📊 Posizioni Aperte:")
            for symbol, pos in final_portfolio['positions'].items():
                pnl = pos['unrealized_pnl']
                pnl_emoji = "📈" if pnl > 0 else "📉"
                print(f"      {pnl_emoji} {symbol}: {pos['shares']} azioni @ ${pos['current_price']:.2f} "
                      f"(P&L: ${pnl:+.2f})")
        
        # Esporta report finale
        report_file = trading_ai.export_trading_report()
        print(f"   💾 Report salvato: {report_file}")
        
        print("✅ Trading fermato correttamente")

def show_portfolio_status(args):
    """Mostra stato del portfolio"""
    print("💰 Portfolio Status...")
    
    trading_ai = NewsBasedTradingAI()
    portfolio = trading_ai.get_portfolio_status()
    
    print(f"\n💼 PORTFOLIO VIRTUALE:")
    print(f"   💵 Cash: ${portfolio['cash']:,.2f}")
    print(f"   📈 Valore Posizioni: ${portfolio['total_position_value']:,.2f}")
    print(f"   🎯 Valore Totale: ${portfolio['total_portfolio_value']:,.2f}")
    print(f"   🔄 Trades Totali: {portfolio['trade_count']}")
    
    if portfolio.get('positions'):
        print(f"\n📊 POSIZIONI APERTE:")
        for symbol, pos in portfolio['positions'].items():
            pnl = pos['unrealized_pnl']
            pnl_emoji = "📈" if pnl > 0 else "📉"
            print(f"   {pnl_emoji} {symbol}: {pos['shares']} azioni")
            print(f"      💰 Prezzo Medio: ${pos['avg_price']:.2f}")
            print(f"      📊 Prezzo Corrente: ${pos['current_price']:.2f}")
            print(f"      🎯 Valore: ${pos['position_value']:,.2f}")
            print(f"      📈 P&L: ${pnl:+.2f}")

def export_report(args):
    """Esporta report completo"""
    print("📄 Esportazione Report...")
    
    trading_ai = NewsBasedTradingAI()
    report_file = trading_ai.export_trading_report()
    
    print(f"✅ Report esportato: {report_file}")

def main():
    """Funzione principale CLI"""
    parser = argparse.ArgumentParser(
        description='🤖 News-Based Trading AI - Sistema di Trading basato su Notizie',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi di utilizzo:
  %(prog)s news                        # Analisi notizie correnti
  %(prog)s signals                     # Segnali di trading
  %(prog)s cycle                       # Esegue un ciclo di trading
  %(prog)s auto --interval 15          # Trading automatico ogni 15 min
  %(prog)s portfolio                   # Stato portfolio
  %(prog)s export                      # Esporta report
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandi disponibili')
    
    # Comando news
    news_parser = subparsers.add_parser('news', help='Analisi notizie correnti')
    news_parser.add_argument('--symbols', type=str, nargs='+',
                           help='Simboli da analizzare')
    
    # Comando signals
    signals_parser = subparsers.add_parser('signals', help='Segnali di trading')
    signals_parser.add_argument('--symbols', type=str, nargs='+',
                               help='Simboli da analizzare')
    
    # Comando cycle
    cycle_parser = subparsers.add_parser('cycle', help='Esegue un ciclo di trading')
    
    # Comando auto
    auto_parser = subparsers.add_parser('auto', help='Trading automatico')
    auto_parser.add_argument('--interval', type=int, default=10,
                           help='Intervallo in minuti tra cicli (default: 10)')
    
    # Comando portfolio
    portfolio_parser = subparsers.add_parser('portfolio', help='Stato portfolio')
    
    # Comando export
    export_parser = subparsers.add_parser('export', help='Esporta report')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'news':
            show_news_analysis(args)
        elif args.command == 'signals':
            show_trading_signals(args)
        elif args.command == 'cycle':
            run_trading_cycle(args)
        elif args.command == 'auto':
            start_automated_trading(args)
        elif args.command == 'portfolio':
            show_portfolio_status(args)
        elif args.command == 'export':
            export_report(args)
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n🛑 Operazione interrotta dall'utente")
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
