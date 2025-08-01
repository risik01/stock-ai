#!/usr/bin/env python3
"""
Dual AI Trading System
======================
Sistema di trading con due AI che cooperano:
1. Price AI: Analisi tecnica veloce (ogni 10 secondi)
2. News AI: Analisi RSS lenta (ogni 10 minuti)
"""

import os
import sys
import json
import time
import asyncio
import threading
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import queue

# Aggiungi src al path
sys.path.append(str(Path(__file__).parent / "src"))

import config_manager
import data_collector
import strategy_engine
import rl_agent
import portfolio

# Classi importate
ConfigManager = config_manager.ConfigManager
DataCollector = data_collector.DataCollector
StrategyEngine = strategy_engine.StrategyEngine
RLAgent = rl_agent.RLAgent
Portfolio = portfolio.Portfolio

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/dual_ai_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SharedMemory:
    """Memoria condivisa tra le due AI"""
    def __init__(self):
        self.latest_prices = {}
        self.latest_technical = {}
        self.latest_news_sentiment = {}
        self.latest_decisions = {}
        self.last_news_update = None
        self.lock = threading.Lock()
    
    def update_prices(self, prices: Dict):
        with self.lock:
            self.latest_prices = prices
            logger.debug(f"📊 Prezzi aggiornati: {len(prices)} simboli")
    
    def update_technical(self, technical: Dict):
        with self.lock:
            self.latest_technical = technical
            logger.debug(f"📈 Analisi tecnica aggiornata: {len(technical)} simboli")
    
    def update_news_sentiment(self, sentiment: Dict):
        with self.lock:
            self.latest_news_sentiment = sentiment
            self.last_news_update = datetime.now()
            logger.info(f"📰 Sentiment news aggiornato: {sentiment}")
    
    def get_combined_data(self) -> Dict:
        with self.lock:
            return {
                'prices': self.latest_prices.copy(),
                'technical': self.latest_technical.copy(),
                'news_sentiment': self.latest_news_sentiment.copy(),
                'last_news_update': self.last_news_update
            }

class PriceAI:
    """AI veloce per analisi tecnica dei prezzi (ogni 10 secondi)"""
    
    def __init__(self, config: Dict, shared_memory: SharedMemory):
        self.config = config
        self.shared_memory = shared_memory
        self.data_collector = DataCollector(config)
        self.strategy_engine = StrategyEngine('config/production_settings.json')
        self.rl_agent = RLAgent(config)
        self.symbols = config['data']['symbols']
        self.running = False
        
        logger.info(f"🚀 Price AI inizializzata per {len(self.symbols)} simboli")
    
    def get_current_prices(self) -> Dict:
        """Ottiene prezzi correnti usando API veloci"""
        prices = {}
        
        for symbol in self.symbols:
            try:
                # Usa il data_collector per dati veloci
                data = self.data_collector.get_stock_data(symbol, period="1d")
                if data is not None and not data.empty:
                    current_price = float(data.iloc[-1]['Close'])
                    prices[symbol] = {
                        'price': current_price,
                        'data': data.tail(50)  # Ultimi 50 punti per analisi tecnica
                    }
                    logger.debug(f"✅ {symbol}: €{current_price:.2f}")
                else:
                    logger.warning(f"⚠️ Nessun dato per {symbol}")
            except Exception as e:
                logger.error(f"❌ Errore prezzo {symbol}: {e}")
        
        return prices
    
    def analyze_technical(self, prices: Dict) -> Dict:
        """Analizza indicatori tecnici"""
        technical_analysis = {}
        
        for symbol, price_data in prices.items():
            try:
                if 'data' in price_data and price_data['data'] is not None:
                    # Analisi tecnica
                    analysis = self.strategy_engine.analyze_symbol(symbol, price_data['data'])
                    
                    # RL Agent
                    rl_result = self.rl_agent.get_action({symbol: {'close': price_data['price']}})
                    
                    technical_analysis[symbol] = {
                        'recommendation': analysis.get('recommendation', 'HOLD'),
                        'confidence': analysis.get('confidence', 0.0),
                        'signals': analysis.get('signals', []),
                        'rl_action': rl_result.get('type', 'hold'),
                        'current_price': price_data['price']
                    }
                    
                    logger.debug(f"📈 {symbol}: {analysis.get('recommendation')} ({analysis.get('confidence', 0):.2f})")
                    
            except Exception as e:
                logger.error(f"❌ Errore analisi tecnica {symbol}: {e}")
        
        return technical_analysis
    
    async def run(self):
        """Loop principale Price AI (ogni 10 secondi)"""
        self.running = True
        logger.info("🚀 Price AI avviata - ciclo ogni 10 secondi")
        
        while self.running:
            try:
                start_time = time.time()
                
                # 1. Ottieni prezzi correnti
                logger.info("📊 Price AI: Aggiornamento prezzi...")
                prices = self.get_current_prices()
                self.shared_memory.update_prices(prices)
                
                # 2. Analisi tecnica
                if prices:
                    logger.info("📈 Price AI: Analisi tecnica...")
                    technical = self.analyze_technical(prices)
                    self.shared_memory.update_technical(technical)
                
                # 3. Timing
                elapsed = time.time() - start_time
                logger.info(f"⏱️ Price AI ciclo completato in {elapsed:.2f}s")
                
                # 4. Attende 10 secondi
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"❌ Errore Price AI: {e}")
                await asyncio.sleep(10)
    
    def stop(self):
        self.running = False
        logger.info("🛑 Price AI fermata")

class NewsAI:
    """AI lenta per analisi RSS e sentiment news (ogni 10 minuti)"""
    
    def __init__(self, config: Dict, shared_memory: SharedMemory):
        self.config = config
        self.shared_memory = shared_memory
        self.symbols = config['data']['symbols']
        self.running = False
        
        # Importa collector RSS
        try:
            from news_rss_collector import RSSNewsCollector
            self.news_collector = RSSNewsCollector()
            logger.info("📰 News AI inizializzata con RSS collector")
        except ImportError:
            logger.warning("⚠️ RSS collector non disponibile")
            self.news_collector = None
    
    def collect_news(self) -> List[Dict]:
        """Raccoglie news da RSS feeds"""
        if not self.news_collector:
            return []
        
        try:
            logger.info("📡 Raccolta news RSS...")
            articles = self.news_collector.collect_all_news()
            logger.info(f"📰 Raccolti {len(articles)} articoli")
            return articles
        except Exception as e:
            logger.error(f"❌ Errore raccolta news: {e}")
            return []
    
    def analyze_sentiment(self, articles: List[Dict]) -> Dict:
        """Analizza sentiment generale e per simbolo"""
        if not articles:
            return {'general': 0.0, 'symbols': {}}
        
        try:
            # Importa analyzer
            from src.news_sentiment import NewsSentimentAnalyzer
            analyzer = NewsSentimentAnalyzer()
            
            # Sentiment generale
            general_sentiment = 0.0
            symbol_sentiment = {symbol: 0.0 for symbol in self.symbols}
            
            for article in articles:
                # Analisi articolo
                try:
                    sentiment = analyzer.analyze_article_sentiment(article)
                    general_sentiment += sentiment.get('compound', 0.0)
                    
                    # Associa a simboli se menzionati
                    title_lower = article.get('title', '').lower()
                    for symbol in self.symbols:
                        if symbol.lower() in title_lower:
                            symbol_sentiment[symbol] += sentiment.get('compound', 0.0)
                            
                except Exception as e:
                    logger.debug(f"Errore analisi sentiment articolo: {e}")
            
            # Normalizza
            if articles:
                general_sentiment = general_sentiment / len(articles)
                symbol_sentiment = {k: v / max(1, len(articles)) for k, v in symbol_sentiment.items()}
            
            return {
                'general': general_sentiment,
                'symbols': symbol_sentiment,
                'articles_count': len(articles)
            }
            
        except Exception as e:
            logger.error(f"❌ Errore analisi sentiment: {e}")
            return {'general': 0.0, 'symbols': {}}
    
    async def run(self):
        """Loop principale News AI (ogni 10 minuti)"""
        self.running = True
        logger.info("📰 News AI avviata - ciclo ogni 10 minuti")
        
        while self.running:
            try:
                start_time = time.time()
                
                # 1. Raccoglie news
                logger.info("📡 News AI: Raccolta articoli RSS...")
                articles = self.collect_news()
                
                # 2. Analizza sentiment
                if articles:
                    logger.info("🎭 News AI: Analisi sentiment...")
                    sentiment = self.analyze_sentiment(articles)
                    self.shared_memory.update_news_sentiment(sentiment)
                
                # 3. Timing
                elapsed = time.time() - start_time
                logger.info(f"⏱️ News AI ciclo completato in {elapsed:.2f}s")
                
                # 4. Attende 10 minuti
                await asyncio.sleep(600)  # 10 minuti
                
            except Exception as e:
                logger.error(f"❌ Errore News AI: {e}")
                await asyncio.sleep(600)
    
    def stop(self):
        self.running = False
        logger.info("🛑 News AI fermata")

class DecisionMaker:
    """Combina i risultati delle due AI e prende decisioni di trading"""
    
    def __init__(self, config: Dict, shared_memory: SharedMemory):
        self.config = config
        self.shared_memory = shared_memory
        self.portfolio = Portfolio(config)
        self.running = False
    
    def make_trading_decision(self, symbol: str, combined_data: Dict) -> Optional[Dict]:
        """Prende decisione di trading combinando le due AI"""
        try:
            # Dati tecnici
            technical = combined_data['technical'].get(symbol, {})
            if not technical:
                return None
            
            # Sentiment news
            news_sentiment = combined_data['news_sentiment']
            symbol_sentiment = news_sentiment.get('symbols', {}).get(symbol, 0.0)
            general_sentiment = news_sentiment.get('general', 0.0)
            
            # Combina i segnali
            tech_rec = technical.get('recommendation', 'HOLD')
            tech_conf = technical.get('confidence', 0.0)
            rl_action = technical.get('rl_action', 'hold')
            current_price = technical.get('current_price', 0.0)
            
            # Calcola score finale
            score = 0.0
            
            # Peso tecnico (60%)
            if tech_rec == 'BUY':
                score += 0.6 * tech_conf
            elif tech_rec == 'SELL':
                score -= 0.6 * tech_conf
            
            # Peso RL Agent (20%)
            if rl_action == 'buy':
                score += 0.2
            elif rl_action == 'sell':
                score -= 0.2
            
            # Peso sentiment (20%)
            combined_sentiment = (symbol_sentiment + general_sentiment) / 2
            score += 0.2 * combined_sentiment
            
            # Decisione finale
            if score > 0.3:
                action = 'BUY'
            elif score < -0.3:
                action = 'SELL'
            else:
                action = 'HOLD'
            
            decision = {
                'symbol': symbol,
                'action': action,
                'score': score,
                'price': current_price,
                'reasoning': {
                    'technical': f"{tech_rec} ({tech_conf:.2f})",
                    'rl_agent': rl_action,
                    'sentiment': f"Symbol: {symbol_sentiment:.2f}, General: {general_sentiment:.2f}",
                    'final_score': score
                }
            }
            
            logger.info(f"🤖 {symbol}: {action} (score: {score:.3f}) - Tech: {tech_rec}, RL: {rl_action}, Sentiment: {combined_sentiment:.2f}")
            
            return decision
            
        except Exception as e:
            logger.error(f"❌ Errore decisione {symbol}: {e}")
            return None
    
    async def run(self):
        """Loop principale Decision Maker (ogni 30 secondi)"""
        self.running = True
        logger.info("🧠 Decision Maker avviato - ciclo ogni 30 secondi")
        
        while self.running:
            try:
                # Ottiene dati combinati
                combined_data = self.shared_memory.get_combined_data()
                
                if not combined_data['prices']:
                    logger.debug("⏳ Attendo dati Price AI...")
                    await asyncio.sleep(30)
                    continue
                
                # Prende decisioni per ogni simbolo
                decisions = []
                for symbol in self.config['data']['symbols']:
                    decision = self.make_trading_decision(symbol, combined_data)
                    if decision and decision['action'] != 'HOLD':
                        decisions.append(decision)
                
                # Esegue trades se necessario
                if decisions:
                    logger.info(f"💰 Esecuzione {len(decisions)} decisioni di trading")
                    for decision in decisions:
                        await self.execute_trade(decision)
                else:
                    logger.debug("📊 Nessuna decisione di trading")
                
                # Report performance
                await self.report_performance()
                
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ Errore Decision Maker: {e}")
                await asyncio.sleep(30)
    
    async def execute_trade(self, decision: Dict):
        """Esegue un trade"""
        try:
            symbol = decision['symbol']
            action = decision['action']
            price = decision['price']
            
            # Quantità base
            quantity = 10
            
            if action == 'BUY':
                success = self.portfolio.buy_stock(symbol, quantity, price)
                if success:
                    logger.info(f"✅ ACQUISTO: {quantity} {symbol} a €{price:.2f}")
                else:
                    logger.warning(f"⚠️ Acquisto {symbol} fallito")
            elif action == 'SELL':
                success = self.portfolio.sell_stock(symbol, quantity, price)
                if success:
                    logger.info(f"✅ VENDITA: {quantity} {symbol} a €{price:.2f}")
                else:
                    logger.warning(f"⚠️ Vendita {symbol} fallita")
                    
        except Exception as e:
            logger.error(f"❌ Errore esecuzione trade: {e}")
    
    async def report_performance(self):
        """Report performance"""
        try:
            performance = self.portfolio.get_performance_summary()
            total_value = performance.get('total_value', 0)
            pnl_percent = performance.get('total_pnl_percent', 0)
            
            logger.info(f"📊 PORTFOLIO: €{total_value:.2f} ({pnl_percent:+.2f}%)")
            
        except Exception as e:
            logger.error(f"❌ Errore report performance: {e}")
    
    def stop(self):
        self.running = False
        logger.info("🛑 Decision Maker fermato")

class DualAITradingSystem:
    """Sistema principale con due AI cooperanti"""
    
    def __init__(self, config_path: str = "config/production_settings.json"):
        # Carica configurazione
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        
        # Memoria condivisa
        self.shared_memory = SharedMemory()
        
        # Componenti AI
        self.price_ai = PriceAI(self.config, self.shared_memory)
        self.news_ai = NewsAI(self.config, self.shared_memory)
        self.decision_maker = DecisionMaker(self.config, self.shared_memory)
        
        self.running = False
        
        logger.info("🚀 Dual AI Trading System inizializzato")
    
    async def start(self):
        """Avvia il sistema"""
        self.running = True
        logger.info("🚀 === AVVIO DUAL AI TRADING SYSTEM ===")
        
        # Avvia tutte le componenti in parallelo
        tasks = [
            asyncio.create_task(self.price_ai.run()),
            asyncio.create_task(self.news_ai.run()),
            asyncio.create_task(self.decision_maker.run())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("🛑 Ricevuto segnale di stop")
        finally:
            await self.stop()
    
    async def stop(self):
        """Ferma il sistema"""
        logger.info("🛑 Fermando Dual AI Trading System...")
        
        self.price_ai.stop()
        self.news_ai.stop()
        self.decision_maker.stop()
        self.running = False
        
        logger.info("✅ Sistema fermato")

async def main():
    """Funzione principale"""
    system = DualAITradingSystem()
    
    try:
        await system.start()
    except KeyboardInterrupt:
        logger.info("👋 Arrivederci!")

if __name__ == "__main__":
    asyncio.run(main())
