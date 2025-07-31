#!/usr/bin/env python3
"""
News Trading Web Dashboard - Dashboard web per il trading basato su notizie
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
import threading
import time

# Aggiungi il path per import
sys.path.append(str(Path(__file__).parent))

from news_based_trading_ai import NewsBasedTradingAI
from news_rss_collector import NewsRSSCollector
from news_sentiment_analyzer import NewsSentimentAnalyzer

app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Istanza globale del trading AI
trading_ai = NewsBasedTradingAI()

@app.route('/')
def dashboard():
    """Dashboard principale"""
    return render_template('news_dashboard.html')

@app.route('/api/news/latest')
def get_latest_news():
    """Ottiene ultime notizie"""
    try:
        collector = NewsRSSCollector()
        articles = collector.collect_all_news()
        
        # Converti a formato JSON serializzabile
        news_data = []
        for article in articles[:20]:  # Ultime 20
            news_data.append({
                'title': article.title,
                'source': article.source,
                'published': article.published.isoformat(),
                'symbols': list(article.symbols),
                'url': article.url,
                'summary': article.summary[:200] + '...' if len(article.summary) > 200 else article.summary
            })
        
        return jsonify({
            'success': True,
            'count': len(news_data),
            'news': news_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/news/breaking')
def get_breaking_news():
    """Ottiene breaking news"""
    try:
        collector = NewsRSSCollector()
        breaking = collector.get_breaking_news(minutes=120)
        
        breaking_data = []
        for news in breaking:
            breaking_data.append({
                'title': news.title,
                'source': news.source,
                'published': news.published.isoformat(),
                'symbols': list(news.symbols),
                'url': news.url,
                'summary': news.summary[:150] + '...' if len(news.summary) > 150 else news.summary,
                'is_breaking': True
            })
        
        return jsonify({
            'success': True,
            'count': len(breaking_data),
            'breaking_news': breaking_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/sentiment/overview')
def get_sentiment_overview():
    """Ottiene overview sentiment del mercato"""
    try:
        collector = NewsRSSCollector()
        analyzer = NewsSentimentAnalyzer()
        
        articles = collector.collect_all_news()
        
        # Simboli da analizzare
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX']
        overview = analyzer.get_market_sentiment_overview(articles, symbols)
        
        # Aggiungi timestamp
        overview['last_updated'] = datetime.now().isoformat()
        overview['total_symbols'] = len(symbols)
        
        return jsonify({
            'success': True,
            'sentiment_overview': overview
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/trading/signals')
def get_trading_signals():
    """Ottiene segnali di trading"""
    try:
        collector = NewsRSSCollector()
        analyzer = NewsSentimentAnalyzer()
        
        articles = collector.collect_all_news()
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX']
        
        signals = analyzer.generate_trading_signals(articles, symbols)
        
        signals_data = []
        for signal in signals:
            signals_data.append({
                'symbol': signal.symbol,
                'action': signal.action,
                'confidence': signal.confidence,
                'sentiment_score': signal.sentiment_score,
                'reason': signal.reason,
                'news_count': signal.news_count,
                'timestamp': signal.timestamp.isoformat()
            })
        
        return jsonify({
            'success': True,
            'count': len(signals_data),
            'signals': signals_data,
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/trading/portfolio')
def get_portfolio_status():
    """Ottiene stato del portfolio"""
    try:
        portfolio = trading_ai.get_portfolio_status()
        
        # Calcola performance
        initial_value = 100000  # Valore iniziale
        current_value = portfolio['total_portfolio_value']
        performance = ((current_value - initial_value) / initial_value) * 100
        
        # Aggiungi metriche aggiuntive
        portfolio['performance_pct'] = performance
        portfolio['last_updated'] = datetime.now().isoformat()
        
        # Calcola distribuzione cash/posizioni
        if portfolio['total_portfolio_value'] > 0:
            portfolio['cash_pct'] = (portfolio['cash'] / portfolio['total_portfolio_value']) * 100
            portfolio['positions_pct'] = (portfolio['total_position_value'] / portfolio['total_portfolio_value']) * 100
        else:
            portfolio['cash_pct'] = 100
            portfolio['positions_pct'] = 0
        
        return jsonify({
            'success': True,
            'portfolio': portfolio
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/trading/cycle', methods=['POST'])
def execute_trading_cycle():
    """Esegue un ciclo di trading"""
    try:
        result = trading_ai.run_trading_cycle()
        
        return jsonify({
            'success': True,
            'cycle_result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/trading/auto/start', methods=['POST'])
def start_auto_trading():
    """Avvia trading automatico"""
    try:
        data = request.get_json() or {}
        interval = data.get('interval', 10)  # Default 10 minuti
        
        # Avvia in background
        def run_auto_trading():
            trading_ai.start_automated_trading(cycle_interval_minutes=interval)
        
        thread = threading.Thread(target=run_auto_trading, daemon=True)
        thread.start()
        
        return jsonify({
            'success': True,
            'message': f'Trading automatico avviato (ciclo ogni {interval} minuti)',
            'interval': interval,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/trading/auto/stop', methods=['POST'])
def stop_auto_trading():
    """Ferma trading automatico"""
    try:
        trading_ai.stop_trading()
        
        return jsonify({
            'success': True,
            'message': 'Trading automatico fermato',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/trading/auto/status')
def get_auto_trading_status():
    """Ottiene stato del trading automatico"""
    try:
        return jsonify({
            'success': True,
            'is_running': trading_ai.is_running,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/alerts/active')
def get_active_alerts():
    """Ottiene alert attivi"""
    try:
        alerts = trading_ai.get_active_alerts()
        
        return jsonify({
            'success': True,
            'count': len(alerts),
            'alerts': alerts,
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stats/dashboard')
def get_dashboard_stats():
    """Ottiene statistiche per dashboard"""
    try:
        # Notizie
        collector = NewsRSSCollector()
        articles = collector.collect_all_news()
        breaking = collector.get_breaking_news(minutes=60)
        
        # Portfolio
        portfolio = trading_ai.get_portfolio_status()
        
        # Sentiment
        analyzer = NewsSentimentAnalyzer()
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
        sentiment_overview = analyzer.get_market_sentiment_overview(articles, symbols)
        
        # Segnali
        signals = analyzer.generate_trading_signals(articles, symbols)
        
        # Alert
        alerts = trading_ai.get_active_alerts()
        
        stats = {
            'news': {
                'total_articles': len(articles),
                'breaking_news': len(breaking),
                'last_updated': datetime.now().isoformat()
            },
            'portfolio': {
                'total_value': portfolio['total_portfolio_value'],
                'cash': portfolio['cash'],
                'positions_count': len(portfolio.get('positions', {})),
                'trades_count': portfolio['trade_count']
            },
            'sentiment': {
                'market_sentiment': sentiment_overview['market_sentiment'],
                'market_mood': sentiment_overview['market_mood'],
                'analyzed_symbols': len(sentiment_overview['symbol_details'])
            },
            'trading': {
                'active_signals': len(signals),
                'auto_trading': trading_ai.is_running,
                'active_alerts': len(alerts)
            }
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/export/report')
def export_trading_report():
    """Esporta report di trading"""
    try:
        report_file = trading_ai.export_trading_report()
        
        return jsonify({
            'success': True,
            'report_file': str(report_file),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint non trovato'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Errore interno del server'}), 500

def create_app(debug=False):
    """Factory function per creare l'app"""
    app.config['DEBUG'] = debug
    return app

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='News Trading Web Dashboard')
    parser.add_argument('--host', default='127.0.0.1', help='Host (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5001, help='Porta (default: 5001)')
    parser.add_argument('--debug', action='store_true', help='Modalità debug')
    
    args = parser.parse_args()
    
    print("🚀 Avvio News Trading Web Dashboard...")
    print(f"📡 Server: http://{args.host}:{args.port}")
    print("⚠️  MODALITÀ SIMULAZIONE - Portfolio Virtuale")
    print("-" * 60)
    
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug,
        threaded=True
    )
