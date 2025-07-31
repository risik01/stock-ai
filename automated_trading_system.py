#!/usr/bin/env python3
"""
Automated Trading System - Produzione
Sistema di trading automatico per deployment su server Ubuntu
Con AI per P&L e analisi news in tempo reale
"""

import sys
import os
import time
import signal
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import schedule
from pathlib import Path

# Aggiungi path per importazioni
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))
sys.path.insert(0, os.path.join(current_dir, 'trading-new'))
sys.path.insert(0, current_dir)

# Import moduli del trading system
try:
    from src.portfolio import Portfolio
    from src.rl_agent import RLTradingAgent
    from src.data_collector import DataCollector
    from src.strategy_engine import StrategyEngine
    from trading_new.news_rss_collector import NewsRSSCollector
    from trading_new.news_sentiment_analyzer import NewsSentimentAnalyzer
    from trading_new.news_trading_ai import NewsTradingAI
except ImportError as e:
    print(f"❌ Errore importazione moduli: {e}")
    print("🔧 Tentativo import alternativi...")
    try:
        # Fallback imports
        sys.path.append('.')
        from portfolio import Portfolio
        from data_collector import DataCollector
        from news_rss_collector import NewsRSSCollector
        print("✅ Import alternativi riusciti")
    except ImportError as e2:
        print(f"❌ Anche import alternativi falliti: {e2}")
        print("📁 Struttura directory corrente:")
        for item in os.listdir('.'):
            print(f"  {item}")
        print("\n💡 Assicurati che tutti i moduli siano presenti nella directory corretta")
        sys.exit(1)

class AutomatedTradingSystem:
    """Sistema di trading automatico per produzione"""
    
    def __init__(self, config_path: str = "config/production_settings.json"):
        """Inizializza sistema di trading automatico"""
        self.config_path = config_path
        self.config = self._load_config()
        
        # Setup logging
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Flag di controllo
        self.running = True
        self.last_health_check = datetime.now()
        
        # Inizializza componenti
        self._initialize_components()
        
        # Setup signal handlers per shutdown graceful
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info("🚀 Automated Trading System inizializzato")
        self.logger.info(f"💰 Budget iniziale: €{self.config['trading']['initial_capital']}")
        self.logger.info(f"📊 Simboli monitorati: {self.config['data']['symbols']}")
    
    def _load_config(self) -> Dict:
        """Carica configurazione di produzione"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Errore caricamento config: {e}")
            sys.exit(1)
    
    def _setup_logging(self):
        """Setup logging avanzato per produzione"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Main log file
        main_log = log_dir / f"trading_system_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Setup formatters
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        file_handler = logging.FileHandler(main_log)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        
        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
    
    def _initialize_components(self):
        """Inizializza tutti i componenti del sistema"""
        try:
            # Portfolio Manager
            self.portfolio = Portfolio(
                initial_capital=self.config['trading']['initial_capital']
            )
            
            # Data Collector
            self.data_collector = DataCollector(config_path=self.config_path)
            
            # RL Agent
            self.rl_agent = RLTradingAgent(config_path=self.config_path)
            
            # Strategy Engine
            self.strategy_engine = StrategyEngine(config_path=self.config_path)
            
            # News Components
            self.news_collector = NewsRSSCollector(config_path=self.config_path)
            self.sentiment_analyzer = NewsSentimentAnalyzer()
            self.news_trading_ai = NewsTradingAI(config_path=self.config_path)
            
            # Statistiche
            self.stats = {
                'start_time': datetime.now(),
                'total_trades': 0,
                'successful_trades': 0,
                'news_based_trades': 0,
                'ai_decisions': 0,
                'max_drawdown': 0.0,
                'daily_returns': []
            }
            
            self.logger.info("✅ Tutti i componenti inizializzati")
            
        except Exception as e:
            self.logger.error(f"❌ Errore inizializzazione: {e}")
            raise
    
    def _signal_handler(self, signum, frame):
        """Handler per shutdown graceful"""
        self.logger.info(f"🛑 Ricevuto segnale {signum}, avvio shutdown...")
        self.running = False
    
    def update_market_data(self):
        """Aggiorna dati di mercato"""
        try:
            self.logger.info("📊 Aggiornamento dati mercato...")
            
            # Raccoglie dati per tutti i simboli
            symbols = self.config['data']['symbols']
            market_data = {}
            
            for symbol in symbols:
                try:
                    data = self.data_collector.get_stock_data(symbol)
                    if data is not None and not data.empty:
                        market_data[symbol] = data
                        self.logger.debug(f"✅ Dati aggiornati per {symbol}")
                    else:
                        self.logger.warning(f"⚠️ Nessun dato per {symbol}")
                except Exception as e:
                    self.logger.error(f"❌ Errore dati {symbol}: {e}")
            
            return market_data
            
        except Exception as e:
            self.logger.error(f"❌ Errore aggiornamento mercato: {e}")
            return {}
    
    def collect_and_analyze_news(self):
        """Raccoglie e analizza news finanziarie"""
        try:
            self.logger.info("📰 Raccolta news...")
            
            # Raccoglie news da RSS feeds
            articles = self.news_collector.collect_all_news()
            
            if not articles:
                self.logger.info("📭 Nessuna nuova news trovata")
                return []
            
            # Analizza sentiment
            analyzed_articles = []
            for article in articles:
                try:
                    # Analisi sentiment
                    sentiment = self.sentiment_analyzer.analyze_sentiment(
                        article.title + " " + article.summary
                    )
                    article.sentiment = sentiment
                    
                    # Calcola importanza
                    article.importance = self.sentiment_analyzer.calculate_importance(article)
                    
                    analyzed_articles.append(article)
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ Errore analisi articolo: {e}")
            
            self.logger.info(f"📊 Analizzati {len(analyzed_articles)} articoli")
            return analyzed_articles
            
        except Exception as e:
            self.logger.error(f"❌ Errore raccolta news: {e}")
            return []
    
    def make_trading_decisions(self, market_data: Dict, news_articles: List):
        """Prende decisioni di trading usando AI"""
        try:
            self.logger.info("🤖 Elaborazione decisioni AI...")
            
            decisions = []
            
            for symbol in self.config['data']['symbols']:
                if symbol not in market_data:
                    continue
                
                try:
                    # Dati tecnici
                    price_data = market_data[symbol]
                    
                    # Analisi tecnica
                    technical_signals = self.strategy_engine.analyze_symbol(symbol, price_data)
                    
                    # Analisi RL Agent
                    rl_action = self.rl_agent.predict_action(symbol, price_data)
                    
                    # News sentiment per il simbolo
                    symbol_news = [a for a in news_articles if symbol in a.symbols]
                    news_sentiment = 0.0
                    if symbol_news:
                        sentiments = [a.sentiment for a in symbol_news if a.sentiment is not None]
                        if sentiments:
                            news_sentiment = sum(sentiments) / len(sentiments)
                    
                    # Decisione ensemble
                    decision = self._make_ensemble_decision(
                        symbol, technical_signals, rl_action, news_sentiment, price_data
                    )
                    
                    if decision:
                        decisions.append(decision)
                        self.stats['ai_decisions'] += 1
                        
                        self.logger.info(
                            f"🎯 Decisione {symbol}: {decision['action']} "
                            f"(conf: {decision['confidence']:.2f})"
                        )
                
                except Exception as e:
                    self.logger.error(f"❌ Errore decisione {symbol}: {e}")
            
            return decisions
            
        except Exception as e:
            self.logger.error(f"❌ Errore decisioni trading: {e}")
            return []
    
    def _make_ensemble_decision(self, symbol: str, technical_signals: Dict, 
                              rl_action: int, news_sentiment: float, price_data) -> Optional[Dict]:
        """Combina segnali per decisione finale"""
        try:
            # Pesi dai config
            weights = self.config['ai_trading']['models']
            
            # Score tecnico
            technical_score = 0.0
            if technical_signals.get('recommendation') == 'BUY':
                technical_score = 0.7
            elif technical_signals.get('recommendation') == 'SELL':
                technical_score = -0.7
            
            # Score RL
            rl_score = 0.0
            if rl_action == 1:  # BUY
                rl_score = 0.8
            elif rl_action == 2:  # SELL
                rl_score = -0.8
            
            # Score news (normalizzato)
            news_score = max(-1.0, min(1.0, news_sentiment * 2))
            
            # Calcolo finale pesato
            final_score = (
                technical_score * weights['technical_analyzer']['weight'] +
                rl_score * weights['rl_agent']['weight'] +
                news_score * weights['sentiment_analyzer']['weight']
            )
            
            confidence = abs(final_score)
            
            # Soglia minima di confidenza
            min_confidence = self.config['ai_trading']['model_confidence_threshold']
            if confidence < min_confidence:
                return None
            
            # Determina azione
            action = None
            if final_score > 0.3:
                action = 'BUY'
            elif final_score < -0.3:
                action = 'SELL'
            else:
                return None
            
            # Calcola size posizione
            current_price = float(price_data.iloc[-1]['close'])
            position_size = self._calculate_position_size(symbol, current_price, confidence)
            
            return {
                'symbol': symbol,
                'action': action,
                'confidence': confidence,
                'price': current_price,
                'size': position_size,
                'technical_score': technical_score,
                'rl_score': rl_score,
                'news_score': news_score,
                'final_score': final_score,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Errore ensemble decision: {e}")
            return None
    
    def _calculate_position_size(self, symbol: str, price: float, confidence: float) -> float:
        """Calcola dimensione posizione basata su risk management"""
        try:
            # Budget disponibile
            available_capital = self.portfolio.get_available_cash()
            
            # Max position size da config
            max_position_ratio = self.config['trading']['max_position_size']
            
            # Risk per trade
            risk_per_trade = self.config['trading']['live_trading']['risk_per_trade']
            
            # Calcolo base
            base_position_value = available_capital * max_position_ratio
            
            # Aggiusta per confidence
            confidence_multiplier = min(1.0, confidence * 1.5)
            position_value = base_position_value * confidence_multiplier
            
            # Calcola shares
            shares = int(position_value / price)
            
            # Limite minimo
            if shares < 1:
                return 0
            
            # Verifica risk management
            position_value_final = shares * price
            if position_value_final > available_capital * 0.95:  # Mantieni 5% cash
                shares = int((available_capital * 0.95) / price)
            
            return max(0, shares)
            
        except Exception as e:
            self.logger.error(f"❌ Errore calcolo position size: {e}")
            return 0
    
    def execute_trading_decisions(self, decisions: List[Dict]):
        """Esegue decisioni di trading"""
        for decision in decisions:
            try:
                symbol = decision['symbol']
                action = decision['action']
                shares = decision['size']
                price = decision['price']
                
                if shares == 0:
                    self.logger.info(f"⏭️ Skip {symbol}: position size troppo piccola")
                    continue
                
                # Verifica condizioni di sicurezza
                if not self._verify_trade_safety(decision):
                    self.logger.warning(f"⚠️ Trade {symbol} bloccato per sicurezza")
                    continue
                
                # Esegui trade
                success = False
                if action == 'BUY':
                    success = self.portfolio.buy_stock(symbol, shares, price)
                elif action == 'SELL':
                    success = self.portfolio.sell_stock(symbol, shares, price)
                
                # Log risultato
                if success:
                    self.stats['total_trades'] += 1
                    if decision.get('news_score', 0) != 0:
                        self.stats['news_based_trades'] += 1
                    
                    self.logger.info(
                        f"✅ TRADE ESEGUITO: {action} {shares} {symbol} @ €{price:.2f} "
                        f"(conf: {decision['confidence']:.2f})"
                    )
                else:
                    self.logger.error(f"❌ TRADE FALLITO: {action} {shares} {symbol}")
                
            except Exception as e:
                self.logger.error(f"❌ Errore esecuzione trade: {e}")
    
    def _verify_trade_safety(self, decision: Dict) -> bool:
        """Verifica condizioni di sicurezza per il trade"""
        try:
            # Controlla limite giornaliero trades
            max_daily_trades = self.config['safety']['max_daily_trades']
            if self.stats['total_trades'] >= max_daily_trades:
                return False
            
            # Controlla max loss giornaliero
            current_portfolio_value = self.portfolio.get_total_value()
            initial_capital = self.config['trading']['initial_capital']
            current_return = (current_portfolio_value - initial_capital) / initial_capital
            
            max_daily_loss = self.config['trading']['live_trading']['max_daily_loss']
            if current_return < -max_daily_loss:
                self.logger.warning(f"🛑 Max daily loss raggiunto: {current_return:.2%}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Errore verifica sicurezza: {e}")
            return False
    
    def generate_performance_report(self):
        """Genera report performance"""
        try:
            portfolio_value = self.portfolio.get_total_value()
            initial_capital = self.config['trading']['initial_capital']
            total_return = (portfolio_value - initial_capital) / initial_capital
            
            # Calcola statistiche
            uptime = datetime.now() - self.stats['start_time']
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'uptime_hours': uptime.total_seconds() / 3600,
                'portfolio_value': portfolio_value,
                'total_return': total_return,
                'total_return_pct': total_return * 100,
                'total_trades': self.stats['total_trades'],
                'news_based_trades': self.stats['news_based_trades'],
                'ai_decisions': self.stats['ai_decisions'],
                'positions': self.portfolio.get_positions(),
                'cash': self.portfolio.get_available_cash()
            }
            
            # Salva report
            report_file = f"logs/performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"📊 PERFORMANCE: €{portfolio_value:.2f} ({total_return:+.2%})")
            self.logger.info(f"📈 Trades: {self.stats['total_trades']} | AI: {self.stats['ai_decisions']}")
            
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Errore performance report: {e}")
            return {}
    
    def health_check(self):
        """Controllo salute del sistema"""
        try:
            self.last_health_check = datetime.now()
            
            # Controlla componenti
            checks = {
                'portfolio': self.portfolio is not None,
                'data_collector': self.data_collector is not None,
                'news_collector': self.news_collector is not None,
                'memory_usage': True,  # Placeholder
                'disk_space': True     # Placeholder
            }
            
            all_healthy = all(checks.values())
            
            if all_healthy:
                self.logger.debug("💚 Health check: Sistema OK")
            else:
                failed_checks = [k for k, v in checks.items() if not v]
                self.logger.error(f"❤️‍🩹 Health check FAILED: {failed_checks}")
            
            return all_healthy
            
        except Exception as e:
            self.logger.error(f"❌ Errore health check: {e}")
            return False
    
    def run_trading_cycle(self):
        """Esegue un ciclo completo di trading"""
        try:
            self.logger.info("🔄 === INIZIO CICLO TRADING ===")
            
            # 1. Health check
            if not self.health_check():
                self.logger.error("❌ Health check fallito, skip ciclo")
                return
            
            # 2. Aggiorna dati mercato
            market_data = self.update_market_data()
            if not market_data:
                self.logger.warning("⚠️ Nessun dato mercato, skip ciclo")
                return
            
            # 3. Raccoglie news
            news_articles = self.collect_and_analyze_news()
            
            # 4. Decisioni AI
            decisions = self.make_trading_decisions(market_data, news_articles)
            
            # 5. Esegui trades
            if decisions:
                self.execute_trading_decisions(decisions)
            else:
                self.logger.info("📭 Nessuna decisione di trading")
            
            # 6. Performance report
            self.generate_performance_report()
            
            self.logger.info("✅ === CICLO TRADING COMPLETATO ===")
            
        except Exception as e:
            self.logger.error(f"❌ Errore ciclo trading: {e}")
    
    def start(self):
        """Avvia sistema di trading automatico"""
        self.logger.info("🚀 Avvio Automated Trading System...")
        
        # Setup scheduler
        schedule.every(self.config['trading']['live_trading']['check_interval']).seconds.do(self.run_trading_cycle)
        schedule.every(1).hours.do(self.generate_performance_report)
        schedule.every(30).minutes.do(self.health_check)
        
        # Main loop
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(10)  # Check ogni 10 secondi
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Interruzione da utente")
        except Exception as e:
            self.logger.error(f"❌ Errore sistema: {e}")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Shutdown graceful del sistema"""
        self.logger.info("🛑 Shutdown sistema...")
        
        try:
            # Salva stato finale
            final_report = self.generate_performance_report()
            
            # Chiudi posizioni se necessario (opzionale)
            # self.portfolio.close_all_positions()
            
            self.logger.info("✅ Shutdown completato")
            
        except Exception as e:
            self.logger.error(f"❌ Errore shutdown: {e}")

def main():
    """Funzione principale"""
    print("🚀 Automated Trading System - Produzione")
    print("💰 Budget: €1000 | AI-Powered | News Integration")
    print("=" * 50)
    
    try:
        # Inizializza sistema
        trading_system = AutomatedTradingSystem()
        
        # Avvia
        trading_system.start()
        
    except Exception as e:
        print(f"❌ Errore critico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
