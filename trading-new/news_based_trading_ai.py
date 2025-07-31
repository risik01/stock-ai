#!/usr/bin/env python3
"""
News-Based Trading AI - Sistema di trading basato su analisi notizie
Modulo principale che combina raccolta notizie, sentiment analysis e decisioni di trading
"""

import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import pandas as pd
import yfinance as yf
from dataclasses import dataclass, asdict
import numpy as np

from news_rss_collector import NewsRSSCollector, NewsArticle
from news_sentiment_analyzer import NewsSentimentAnalyzer, TradingSignal

@dataclass
class NewsTradeExecution:
    """Esecuzione di un trade basato su notizie"""
    symbol: str
    action: str
    quantity: int
    price: float
    timestamp: datetime
    news_sentiment: float
    confidence: float
    trigger_news: List[str]  # Titoli delle notizie che hanno triggerato il trade
    reason: str

@dataclass
class MarketAlert:
    """Alert di mercato basato su notizie"""
    type: str  # 'breaking_news', 'sentiment_change', 'volume_spike'
    symbol: str
    message: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    timestamp: datetime
    related_news: List[NewsArticle]

class NewsBasedTradingAI:
    """
    Sistema di Trading AI basato su analisi notizie in tempo reale
    """
    
    def __init__(self, config_path: str = "../config/settings.json"):
        """Inizializza il sistema di trading basato su notizie"""
        self.config = self._load_config(config_path)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('../data/news_trading_ai.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Inizializza componenti
        self.news_collector = NewsRSSCollector(config_path)
        self.sentiment_analyzer = NewsSentimentAnalyzer()
        
        # Portfolio virtuale per simulazione
        self.virtual_portfolio = {
            'cash': self.config.get('trading', {}).get('initial_capital', 100000),
            'positions': {},
            'trades': [],
            'performance': []
        }
        
        # Stato del sistema
        self.is_running = False
        self.last_news_check = datetime.now() - timedelta(hours=1)
        self.sentiment_history = {}  # Storico sentiment per simbolo
        self.alert_history = []
        
        # Configurazione trading
        self.trading_config = {
            'min_confidence': 0.6,  # Confidenza minima per trade
            'max_position_size': 0.1,  # Massimo 10% del portfolio per posizione
            'stop_loss_pct': 0.05,  # Stop loss 5%
            'take_profit_pct': 0.15,  # Take profit 15%
            'max_trades_per_hour': 5,  # Massimo 5 trades per ora
            'sentiment_threshold': 0.2,  # Soglia sentiment per azione
            'news_freshness_minutes': 30,  # Considera solo notizie degli ultimi 30 min
            'min_news_count': 2  # Minimo 2 notizie per decisione
        }
        
        # Aggiorna config con parametri custom se presenti
        if 'news_trading' in self.config:
            self.trading_config.update(self.config['news_trading'])
        
        # Simboli da monitorare
        self.monitored_symbols = self.config.get('data', {}).get('symbols', 
            ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META', 'NVDA'])
        
        self.logger.info("NewsBasedTradingAI inizializzato con successo")
    
    def _load_config(self, config_path: str) -> Dict:
        """Carica configurazione"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Config file non trovato: {config_path}")
            return {}
        except Exception as e:
            self.logger.error(f"Errore caricamento config: {e}")
            return {}
    
    def get_current_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Ottiene prezzi correnti per i simboli"""
        prices = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                if not hist.empty:
                    prices[symbol] = float(hist['Close'].iloc[-1])
                else:
                    self.logger.warning(f"Nessun dato prezzo per {symbol}")
            except Exception as e:
                self.logger.error(f"Errore ottenimento prezzo {symbol}: {e}")
        
        return prices
    
    def analyze_breaking_news(self, minutes: int = 30) -> List[MarketAlert]:
        """Analizza breaking news e genera alert"""
        alerts = []
        
        # Ottieni breaking news
        breaking_news = self.news_collector.get_breaking_news(minutes=minutes)
        
        if not breaking_news:
            return alerts
        
        # Analizza ogni breaking news
        for article in breaking_news:
            if not article.symbols:
                continue
            
            # Analizza sentiment
            sentiment = self.sentiment_analyzer.analyze_article_sentiment(article)
            
            for symbol in article.symbols:
                alert_type = "breaking_news"
                severity = "medium"
                
                # Determina severità basata su sentiment e keywords
                if abs(sentiment.polarity) > 0.7:
                    severity = "high"
                    if abs(sentiment.polarity) > 0.9:
                        severity = "critical"
                
                # Keywords critiche
                critical_keywords = ['bankruptcy', 'fraud', 'investigation', 'lawsuit', 
                                   'acquisition', 'merger', 'breakthrough', 'earnings']
                
                if any(keyword in article.title.lower() for keyword in critical_keywords):
                    severity = "critical"
                
                message = f"Breaking: {article.title[:100]}..."
                if sentiment.polarity != 0:
                    sentiment_desc = "positivo" if sentiment.polarity > 0 else "negativo"
                    message += f" (Sentiment {sentiment_desc}: {sentiment.polarity:.2f})"
                
                alert = MarketAlert(
                    type=alert_type,
                    symbol=symbol,
                    message=message,
                    severity=severity,
                    timestamp=article.published,
                    related_news=[article]
                )
                
                alerts.append(alert)
        
        return alerts
    
    def detect_sentiment_changes(self) -> List[MarketAlert]:
        """Rileva cambiamenti significativi nel sentiment"""
        alerts = []
        
        # Ottieni notizie recenti
        recent_news = self.news_collector.get_breaking_news(minutes=60)
        
        for symbol in self.monitored_symbols:
            # Analizza sentiment corrente
            current_analysis = self.sentiment_analyzer.analyze_symbol_sentiment(recent_news, symbol)
            
            if current_analysis['article_count'] == 0:
                continue
            
            current_sentiment = current_analysis['sentiment_score']
            
            # Confronta con sentiment storico
            if symbol in self.sentiment_history:
                previous_sentiment = self.sentiment_history[symbol]['sentiment']
                sentiment_change = current_sentiment - previous_sentiment
                
                # Soglia per cambiamento significativo
                if abs(sentiment_change) > 0.3:
                    severity = "high" if abs(sentiment_change) > 0.5 else "medium"
                    
                    change_direction = "migliorato" if sentiment_change > 0 else "peggiorato"
                    message = (f"Sentiment {symbol} {change_direction} significativamente: "
                             f"{previous_sentiment:.2f} → {current_sentiment:.2f}")
                    
                    alert = MarketAlert(
                        type="sentiment_change",
                        symbol=symbol,
                        message=message,
                        severity=severity,
                        timestamp=datetime.now(),
                        related_news=current_analysis['articles']
                    )
                    
                    alerts.append(alert)
            
            # Aggiorna storico sentiment
            self.sentiment_history[symbol] = {
                'sentiment': current_sentiment,
                'timestamp': datetime.now(),
                'article_count': current_analysis['article_count']
            }
        
        return alerts
    
    def calculate_position_size(self, symbol: str, price: float, 
                              confidence: float) -> int:
        """Calcola dimensione ottimale della posizione"""
        portfolio_value = self.virtual_portfolio['cash']
        
        # Position size basato su confidenza e configurazione
        base_position_pct = self.trading_config['max_position_size']
        confidence_adjusted_pct = base_position_pct * confidence
        
        position_value = portfolio_value * confidence_adjusted_pct
        shares = int(position_value / price)
        
        return max(1, shares) if shares > 0 else 0
    
    def execute_virtual_trade(self, signal: TradingSignal) -> Optional[NewsTradeExecution]:
        """Esegue un trade virtuale basato su segnale"""
        
        # Ottieni prezzo corrente
        current_prices = self.get_current_prices([signal.symbol])
        if signal.symbol not in current_prices:
            self.logger.error(f"Prezzo non disponibile per {signal.symbol}")
            return None
        
        current_price = current_prices[signal.symbol]
        
        # Controlli pre-trade
        if not self._can_execute_trade(signal):
            return None
        
        # Calcola quantità
        quantity = self.calculate_position_size(signal.symbol, current_price, signal.confidence)
        
        if quantity == 0:
            self.logger.warning(f"Quantità 0 calcolata per {signal.symbol}")
            return None
        
        # Esegui trade virtuale
        try:
            if signal.action == 'BUY':
                cost = quantity * current_price
                if self.virtual_portfolio['cash'] >= cost:
                    self.virtual_portfolio['cash'] -= cost
                    
                    if signal.symbol in self.virtual_portfolio['positions']:
                        # Aggiungi alla posizione esistente
                        existing = self.virtual_portfolio['positions'][signal.symbol]
                        total_shares = existing['shares'] + quantity
                        avg_price = ((existing['shares'] * existing['avg_price']) + 
                                   (quantity * current_price)) / total_shares
                        
                        self.virtual_portfolio['positions'][signal.symbol] = {
                            'shares': total_shares,
                            'avg_price': avg_price,
                            'last_update': datetime.now()
                        }
                    else:
                        # Nuova posizione
                        self.virtual_portfolio['positions'][signal.symbol] = {
                            'shares': quantity,
                            'avg_price': current_price,
                            'last_update': datetime.now()
                        }
                else:
                    self.logger.warning(f"Fondi insufficienti per comprare {signal.symbol}")
                    return None
            
            elif signal.action == 'SELL':
                if (signal.symbol in self.virtual_portfolio['positions'] and 
                    self.virtual_portfolio['positions'][signal.symbol]['shares'] >= quantity):
                    
                    proceeds = quantity * current_price
                    self.virtual_portfolio['cash'] += proceeds
                    
                    # Riduci posizione
                    current_shares = self.virtual_portfolio['positions'][signal.symbol]['shares']
                    remaining_shares = current_shares - quantity
                    
                    if remaining_shares > 0:
                        self.virtual_portfolio['positions'][signal.symbol]['shares'] = remaining_shares
                        self.virtual_portfolio['positions'][signal.symbol]['last_update'] = datetime.now()
                    else:
                        # Chiudi posizione completamente
                        del self.virtual_portfolio['positions'][signal.symbol]
                else:
                    self.logger.warning(f"Posizione insufficiente per vendere {signal.symbol}")
                    return None
            
            # Crea record del trade
            trigger_news_titles = [article.title for article in signal.news_articles[:3]]
            
            trade_execution = NewsTradeExecution(
                symbol=signal.symbol,
                action=signal.action,
                quantity=quantity,
                price=current_price,
                timestamp=datetime.now(),
                news_sentiment=signal.sentiment_score,
                confidence=signal.confidence,
                trigger_news=trigger_news_titles,
                reason=signal.reason
            )
            
            # Aggiungi al portfolio
            self.virtual_portfolio['trades'].append(asdict(trade_execution))
            
            self.logger.info(
                f"TRADE ESEGUITO: {signal.action} {quantity} {signal.symbol} "
                f"@ ${current_price:.2f} - Sentiment: {signal.sentiment_score:.2f} "
                f"- {signal.reason}"
            )
            
            return trade_execution
            
        except Exception as e:
            self.logger.error(f"Errore esecuzione trade: {e}")
            return None
    
    def _can_execute_trade(self, signal: TradingSignal) -> bool:
        """Verifica se il trade può essere eseguito"""
        
        # Verifica confidenza minima
        if signal.confidence < self.trading_config['min_confidence']:
            return False
        
        # Verifica limiti orari
        recent_trades = [
            t for t in self.virtual_portfolio['trades']
            if datetime.fromisoformat(t['timestamp']) > datetime.now() - timedelta(hours=1)
        ]
        
        if len(recent_trades) >= self.trading_config['max_trades_per_hour']:
            return False
        
        # Verifica freshness delle notizie
        news_cutoff = datetime.now() - timedelta(minutes=self.trading_config['news_freshness_minutes'])
        fresh_news = [
            article for article in signal.news_articles 
            if article.published > news_cutoff
        ]
        
        if len(fresh_news) < self.trading_config['min_news_count']:
            return False
        
        return True
    
    def analyze_market_impact(self) -> Dict:
        """Analizza l'impatto delle notizie sul mercato"""
        
        # Ottieni notizie recenti
        recent_news = self.news_collector.get_breaking_news(minutes=120)
        
        # Ottieni panoramica sentiment
        market_overview = self.sentiment_analyzer.get_market_sentiment_overview(
            recent_news, self.monitored_symbols
        )
        
        # Genera segnali di trading
        trading_signals = self.sentiment_analyzer.generate_trading_signals(
            recent_news, self.monitored_symbols
        )
        
        # Analizza alert
        breaking_alerts = self.analyze_breaking_news(minutes=30)
        sentiment_alerts = self.detect_sentiment_changes()
        
        all_alerts = breaking_alerts + sentiment_alerts
        
        return {
            'timestamp': datetime.now(),
            'market_overview': market_overview,
            'trading_signals': trading_signals,
            'alerts': all_alerts,
            'recent_news_count': len(recent_news),
            'portfolio_status': self.get_portfolio_status()
        }
    
    def get_portfolio_status(self) -> Dict:
        """Ottiene stato del portfolio virtuale"""
        
        # Calcola valore posizioni correnti
        position_values = {}
        total_position_value = 0
        
        if self.virtual_portfolio['positions']:
            current_prices = self.get_current_prices(list(self.virtual_portfolio['positions'].keys()))
            
            for symbol, position in self.virtual_portfolio['positions'].items():
                if symbol in current_prices:
                    current_price = current_prices[symbol]
                    position_value = position['shares'] * current_price
                    position_values[symbol] = {
                        'shares': position['shares'],
                        'avg_price': position['avg_price'],
                        'current_price': current_price,
                        'position_value': position_value,
                        'unrealized_pnl': position_value - (position['shares'] * position['avg_price'])
                    }
                    total_position_value += position_value
        
        total_portfolio_value = self.virtual_portfolio['cash'] + total_position_value
        
        return {
            'cash': self.virtual_portfolio['cash'],
            'total_position_value': total_position_value,
            'total_portfolio_value': total_portfolio_value,
            'positions': position_values,
            'trade_count': len(self.virtual_portfolio['trades']),
            'last_update': datetime.now().isoformat()
        }
    
    def run_trading_cycle(self) -> Dict:
        """Esegue un ciclo completo di trading basato su notizie"""
        
        self.logger.info("Avvio ciclo trading basato su notizie...")
        
        # Raccoglie notizie fresche
        fresh_news = self.news_collector.collect_all_news()
        
        # Filtra solo notizie molto recenti
        cutoff_time = datetime.now() - timedelta(minutes=self.trading_config['news_freshness_minutes'])
        very_recent_news = [n for n in fresh_news if n.published > cutoff_time]
        
        if not very_recent_news:
            self.logger.info("Nessuna notizia fresca trovata")
            return {'status': 'no_fresh_news', 'news_count': len(fresh_news)}
        
        self.logger.info(f"Trovate {len(very_recent_news)} notizie fresche")
        
        # Genera segnali di trading
        trading_signals = self.sentiment_analyzer.generate_trading_signals(
            very_recent_news, self.monitored_symbols
        )
        
        executed_trades = []
        
        # Esegui trades per segnali qualificati
        for signal in trading_signals:
            if signal.action != 'HOLD':
                trade_execution = self.execute_virtual_trade(signal)
                if trade_execution:
                    executed_trades.append(trade_execution)
        
        # Analizza alert
        alerts = self.analyze_breaking_news(minutes=30) + self.detect_sentiment_changes()
        
        # Aggiorna storico alert
        self.alert_history.extend(alerts)
        
        # Mantieni solo alert degli ultimi 7 giorni
        week_ago = datetime.now() - timedelta(days=7)
        self.alert_history = [a for a in self.alert_history if a.timestamp > week_ago]
        
        cycle_summary = {
            'timestamp': datetime.now(),
            'status': 'completed',
            'fresh_news_count': len(very_recent_news),
            'signals_generated': len(trading_signals),
            'trades_executed': len(executed_trades),
            'alerts_generated': len(alerts),
            'portfolio_status': self.get_portfolio_status(),
            'executed_trades': [asdict(t) for t in executed_trades],
            'active_alerts': [asdict(a) for a in alerts if a.severity in ['high', 'critical']]
        }
        
        self.logger.info(
            f"Ciclo completato: {len(very_recent_news)} notizie, "
            f"{len(trading_signals)} segnali, {len(executed_trades)} trades"
        )
        
        return cycle_summary
    
    def start_automated_trading(self, cycle_interval_minutes: int = 10):
        """Avvia trading automatizzato basato su notizie"""
        
        self.is_running = True
        self.logger.info(f"Avvio trading automatizzato (ciclo ogni {cycle_interval_minutes} minuti)")
        
        def trading_loop():
            while self.is_running:
                try:
                    # Esegui ciclo di trading
                    cycle_result = self.run_trading_cycle()
                    
                    # Log risultati importanti
                    if cycle_result.get('trades_executed', 0) > 0:
                        self.logger.info(f"🔄 Eseguiti {cycle_result['trades_executed']} trades!")
                    
                    if cycle_result.get('active_alerts'):
                        self.logger.warning(f"🚨 {len(cycle_result['active_alerts'])} alert attivi!")
                    
                    # Attendi prossimo ciclo
                    time.sleep(cycle_interval_minutes * 60)
                    
                except KeyboardInterrupt:
                    self.logger.info("Trading fermato dall'utente")
                    break
                except Exception as e:
                    self.logger.error(f"Errore nel ciclo trading: {e}")
                    time.sleep(60)  # Attendi 1 minuto prima di riprovare
        
        # Avvia in thread separato
        trading_thread = threading.Thread(target=trading_loop)
        trading_thread.daemon = True
        trading_thread.start()
        
        return trading_thread
    
    def stop_trading(self):
        """Ferma il trading automatizzato"""
        self.is_running = False
        self.logger.info("Trading automatizzato fermato")
    
    def export_trading_report(self, filename: str = None) -> str:
        """Esporta report completo del trading"""
        
        if filename is None:
            filename = f"../data/news_trading_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'portfolio_status': self.get_portfolio_status(),
            'trading_config': self.trading_config,
            'monitored_symbols': self.monitored_symbols,
            'sentiment_history': {
                symbol: {
                    'sentiment': data['sentiment'],
                    'timestamp': data['timestamp'].isoformat(),
                    'article_count': data['article_count']
                } for symbol, data in self.sentiment_history.items()
            },
            'recent_alerts': [asdict(alert) for alert in self.alert_history[-20:]],
            'all_trades': self.virtual_portfolio['trades']
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"Report trading esportato: {filename}")
        return filename

def main():
    """Funzione principale per testing"""
    print("🚀 Test News-Based Trading AI...")
    
    # Inizializza sistema
    trading_ai = NewsBasedTradingAI()
    
    print("🔄 Esecuzione ciclo di trading...")
    
    # Esegui un ciclo di trading
    result = trading_ai.run_trading_cycle()
    
    print(f"\n📊 RISULTATI CICLO:")
    print(f"   📰 Notizie fresche: {result.get('fresh_news_count', 0)}")
    print(f"   🎯 Segnali generati: {result.get('signals_generated', 0)}")
    print(f"   💼 Trades eseguiti: {result.get('trades_executed', 0)}")
    print(f"   🚨 Alert generati: {result.get('alerts_generated', 0)}")
    
    # Mostra portfolio status
    portfolio = result['portfolio_status']
    print(f"\n💰 PORTFOLIO STATUS:")
    print(f"   💵 Cash: ${portfolio['cash']:,.2f}")
    print(f"   📈 Valore Posizioni: ${portfolio['total_position_value']:,.2f}")
    print(f"   🎯 Valore Totale: ${portfolio['total_portfolio_value']:,.2f}")
    print(f"   🔄 Trades Totali: {portfolio['trade_count']}")
    
    # Mostra trades eseguiti
    if result.get('executed_trades'):
        print(f"\n📋 TRADES ESEGUITI:")
        for trade in result['executed_trades']:
            action_emoji = "🟢" if trade['action'] == 'BUY' else "🔴"
            print(f"   {action_emoji} {trade['action']} {trade['quantity']} {trade['symbol']} "
                  f"@ ${trade['price']:.2f} - {trade['reason']}")
    
    # Mostra alert attivi
    if result.get('active_alerts'):
        print(f"\n🚨 ALERT ATTIVI:")
        for alert in result['active_alerts']:
            severity_emoji = "🔴" if alert['severity'] == 'critical' else "🟡"
            print(f"   {severity_emoji} {alert['symbol']}: {alert['message']}")
    
    # Esporta report
    report_file = trading_ai.export_trading_report()
    print(f"\n💾 Report esportato: {report_file}")
    
    # Opzione per avviare trading automatico
    print("\n❓ Vuoi avviare il trading automatico? (ctrl+c per fermare)")
    print("   Avviando in modalità demo...")
    
    try:
        trading_ai.start_automated_trading(cycle_interval_minutes=5)  # Ciclo ogni 5 minuti
        
        while trading_ai.is_running:
            portfolio = trading_ai.get_portfolio_status()
            print(f"\r💰 Portfolio: ${portfolio['total_portfolio_value']:,.2f} | "
                  f"Trades: {portfolio['trade_count']}", end='', flush=True)
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n🛑 Fermando trading automatico...")
        trading_ai.stop_trading()
        print("✅ Trading fermato correttamente")

if __name__ == "__main__":
    main()
