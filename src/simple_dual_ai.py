#!/usr/bin/env python3
"""
Sistema di Trading AI Semplificato
==================================
Due AI cooperanti:
- Price AI: analisi ogni 10 secondi
- News AI: analisi ogni 10 minuti
"""

import os
import sys
import json
import time
import asyncio
import threading
import logging
from datetime import datetime
from pathlib import Path

# Configurazione logging
log_dir = Path("../data")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'dual_ai_simple.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleMemory:
    """Memoria condivisa semplificata"""
    def __init__(self):
        self.prices = {}
        self.news_sentiment = 0.0
        self.last_news_update = None
        self.trades = []
        self.lock = threading.Lock()
    
    def update_prices(self, prices):
        with self.lock:
            self.prices = prices
            logger.debug(f"📊 {len(prices)} prezzi aggiornati")
    
    def update_news(self, sentiment, articles_count):
        with self.lock:
            self.news_sentiment = sentiment
            self.last_news_update = datetime.now()
            logger.info(f"📰 Sentiment: {sentiment:.3f} ({articles_count} articoli)")
    
    def add_trade(self, trade):
        with self.lock:
            self.trades.append(trade)
            # Mantieni solo gli ultimi 50 trade
            if len(self.trades) > 50:
                self.trades = self.trades[-50:]

class FastPriceCollector:
    """Raccoglie prezzi velocemente"""
    
    def __init__(self):
        self.symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META', 'NVDA']
        # Usa il sistema esistente
        sys.path.append('.')
        try:
            import data_collector
            import json
            with open('../config/production_settings.json') as f:
                config = json.load(f)
            # Disabilita cache per dati freschi
            config['data']['cache_enabled'] = False
            self.collector = data_collector.DataCollector(config)
            logger.info("✅ Data Collector caricato")
        except Exception as e:
            logger.error(f"❌ Errore caricamento data collector: {e}")
            self.collector = None
    
    def get_current_prices(self):
        """Ottiene prezzi correnti"""
        prices = {}
        
        if not self.collector:
            # Prezzi simulati per testing
            import random
            base_prices = {'AAPL': 150, 'GOOGL': 2800, 'MSFT': 330, 'TSLA': 240, 'AMZN': 3300, 'META': 520, 'NVDA': 800}
            for symbol in self.symbols:
                # Simula variazione ±2%
                variation = random.uniform(-0.02, 0.02)
                prices[symbol] = base_prices[symbol] * (1 + variation)
            return prices
        
        for symbol in self.symbols:
            try:
                data = self.collector.get_stock_data(symbol)
                if data is not None and not data.empty:
                    current_price = float(data.iloc[-1]['Close'])
                    prices[symbol] = current_price
                    logger.debug(f"✅ {symbol}: €{current_price:.2f}")
            except Exception as e:
                logger.debug(f"⚠️ Errore {symbol}: {e}")
        
        return prices

class SimpleNewsCollector:
    """Raccoglie e analizza news"""
    
    def __init__(self):
        self.rss_feeds = [
            "https://feeds.finance.yahoo.com/rss/2.0/headline",
            "https://feeds.reuters.com/reuters/businessNews",
            "https://www.investing.com/rss/news.rss"
        ]
    
    def collect_news(self):
        """Raccoglie news da RSS feeds"""
        articles = []
        
        try:
            import feedparser
            
            for feed_url in self.rss_feeds:
                try:
                    feed = feedparser.parse(feed_url)
                    for entry in feed.entries[:5]:  # Prime 5 per feed
                        articles.append({
                            'title': entry.get('title', ''),
                            'description': entry.get('description', ''),
                            'published': entry.get('published', ''),
                            'source': feed_url
                        })
                except Exception as e:
                    logger.debug(f"Errore feed {feed_url}: {e}")
                    
        except ImportError:
            logger.warning("⚠️ feedparser non disponibile, notizie simulate")
            # News simulate con sentiment variabile
            import random
            sentiments = [
                ("mercati in crescita forte", 0.8), 
                ("outlook molto positivo", 0.6), 
                ("vendite record dell'azienda", 0.5),
                ("leggero rialzo previsto", 0.2),
                ("situazione stabile", 0.0),
                ("piccolo calo tecnico", -0.2),
                ("risultati deludenti", -0.5),
                ("calo dei mercati globali", -0.6), 
                ("incertezza economica crescente", -0.8)
            ]
            
            for i in range(10):
                sentiment_text, sentiment_value = random.choice(sentiments)
                articles.append({
                    'title': f"Notizia {i+1}: {sentiment_text}",
                    'description': f'Descrizione con sentiment {sentiment_value}',
                    'published': datetime.now().isoformat(),
                    'source': 'simulated',
                    'sentiment_score': sentiment_value  # Per debug
                })
        
        return articles
    
    def analyze_sentiment(self, articles):
        """Analisi sentiment semplificata"""
        if not articles:
            return 0.0
        
        positive_words = ['crescita', 'record', 'positivo', 'rialzo', 'guadagni', 'profitti', 'rally']
        negative_words = ['calo', 'perdite', 'ribasso', 'crisi', 'crollo', 'deludenti', 'incertezza']
        
        total_sentiment = 0.0
        
        for article in articles:
            text = (article.get('title', '') + ' ' + article.get('description', '')).lower()
            
            positive_count = sum(1 for word in positive_words if word in text)
            negative_count = sum(1 for word in negative_words if word in text)
            
            if positive_count > negative_count:
                total_sentiment += 0.1
            elif negative_count > positive_count:
                total_sentiment -= 0.1
        
        # Normalizza tra -1 e 1
        return max(-1.0, min(1.0, total_sentiment / len(articles)))

class SimpleTradingLogic:
    """Logica di trading semplificata"""
    
    def __init__(self):
        self.portfolio_value = 1000.0  # €1000 iniziali
        self.positions = {}  # {symbol: quantity}
        self.trade_count = 0
    
    def make_decision(self, symbol, current_price, previous_price, news_sentiment):
        """Prende decisione di trading semplificata"""
        
        # Calcola variazione prezzo
        if previous_price and previous_price > 0:
            price_change = (current_price - previous_price) / previous_price
        else:
            price_change = 0.0
        
        # Score combinato
        score = 0.0
        
        # Tecnico (70%): momentum (soglie più basse per più trading)
        if price_change > 0.002:  # +0.2% (era 1%)
            score += 0.7 * (price_change / 0.01)  # Scala con la variazione
        elif price_change < -0.002:  # -0.2% (era -1%)
            score -= 0.7 * abs(price_change / 0.01)
        
        # News sentiment (30%)
        score += 0.3 * news_sentiment
        
        # Decisione (soglie più basse)
        action = 'HOLD'
        if score > 0.3:  # Era 0.5
            action = 'BUY'
        elif score < -0.3:  # Era -0.5
            action = 'SELL'
        
        return {
            'symbol': symbol,
            'action': action,
            'score': score,
            'price_change': price_change,
            'news_sentiment': news_sentiment,
            'current_price': current_price
        }
    
    def execute_trade(self, decision):
        """Esegue un trade simulato"""
        symbol = decision['symbol']
        action = decision['action']
        price = decision['current_price']
        
        # Calcola quante azioni possiamo permetterci (max 10% del portfolio per trade)
        max_investment = self.portfolio_value * 0.1
        max_shares = max(1, int(max_investment / price))
        
        if action == 'BUY' and self.portfolio_value >= price * max_shares:
            # Acquista azioni
            self.positions[symbol] = self.positions.get(symbol, 0) + max_shares
            cost = price * max_shares
            self.portfolio_value -= cost
            self.trade_count += 1
            
            logger.info(f"💰 ACQUISTO: {max_shares} {symbol} a €{price:.2f} (Costo: €{cost:.2f}, Tot: {self.positions[symbol]})")
            return True
            
        elif action == 'SELL' and self.positions.get(symbol, 0) > 0:
            # Vende tutte le azioni disponibili del simbolo
            shares_to_sell = self.positions[symbol]
            revenue = price * shares_to_sell
            self.positions[symbol] = 0
            self.portfolio_value += revenue
            self.trade_count += 1
            
            logger.info(f"💰 VENDITA: {shares_to_sell} {symbol} a €{price:.2f} (Ricavo: €{revenue:.2f})")
            return True
        
        return False
    
    def get_portfolio_value(self, current_prices):
        """Calcola valore attuale portfolio"""
        total_value = self.portfolio_value  # Cash
        
        for symbol, quantity in self.positions.items():
            if symbol in current_prices and quantity > 0:
                total_value += quantity * current_prices[symbol]
        
        return total_value

async def price_ai_loop(memory, price_collector, trading_logic):
    """Loop Price AI (ogni 10 secondi)"""
    logger.info("🚀 Price AI avviata (10s cicli)")
    previous_prices = {}
    
    while True:
        try:
            start_time = time.time()
            
            # Ottieni prezzi
            current_prices = price_collector.get_current_prices()
            
            if current_prices:
                memory.update_prices(current_prices)
                
                # Prendi decisioni per ogni simbolo
                decisions = []
                news_sentiment = memory.news_sentiment
                
                logger.info(f"🤖 === ANALISI AI PER {len(current_prices)} SIMBOLI ===")
                
                for symbol, price in current_prices.items():
                    prev_price = previous_prices.get(symbol, price)
                    
                    decision = trading_logic.make_decision(
                        symbol, price, prev_price, news_sentiment
                    )
                    
                    # LOG DETTAGLIATO DELLE DECISIONI AI
                    price_change_pct = decision['price_change'] * 100
                    logger.info(f"🧠 {symbol}: €{price:.2f} | Δ{price_change_pct:+.2f}% | News:{news_sentiment:+.3f} | Score:{decision['score']:+.3f} → {decision['action']}")
                    
                    if decision['action'] != 'HOLD':
                        decisions.append(decision)
                        logger.info(f"🎯 SEGNALE TRADING: {symbol} → {decision['action']} (score: {decision['score']:.3f})")
                
                if not decisions:
                    logger.info("📋 Nessun segnale di trading generato (tutti HOLD)")
                else:
                    logger.info(f"🚨 {len(decisions)} SEGNALI ATTIVI per esecuzione")
                
                # Esegui trades
                for decision in decisions:
                    if trading_logic.execute_trade(decision):
                        memory.add_trade(decision)
                
                # Portfolio update
                portfolio_value = trading_logic.get_portfolio_value(current_prices)
                profit_pct = ((portfolio_value - 1000) / 1000) * 100
                
                # Mostra posizioni se ci sono trade
                if trading_logic.trade_count > 0:
                    positions_str = ", ".join([f"{sym}:{qty}" for sym, qty in trading_logic.positions.items() if qty > 0])
                    if positions_str:
                        logger.info(f"📊 Portfolio: €{portfolio_value:.2f} ({profit_pct:+.2f}%) | Trades: {trading_logic.trade_count} | Posizioni: {positions_str}")
                    else:
                        logger.info(f"📊 Portfolio: €{portfolio_value:.2f} ({profit_pct:+.2f}%) | Trades: {trading_logic.trade_count} | Cash: €{trading_logic.portfolio_value:.2f}")
                else:
                    logger.info(f"📊 Portfolio: €{portfolio_value:.2f} ({profit_pct:+.2f}%) | Trades: {trading_logic.trade_count}")
                
                previous_prices = current_prices.copy()
            
            elapsed = time.time() - start_time
            logger.debug(f"⏱️ Price AI ciclo: {elapsed:.2f}s")
            
            await asyncio.sleep(10)
            
        except Exception as e:
            logger.error(f"❌ Errore Price AI: {e}")
            await asyncio.sleep(10)

async def news_ai_loop(memory, news_collector):
    """Loop News AI (ogni 10 minuti)"""
    logger.info("📰 News AI avviata (10min cicli)")
    
    while True:
        try:
            start_time = time.time()
            
            # Raccoglie news
            articles = news_collector.collect_news()
            logger.info(f"📡 Raccolti {len(articles)} articoli")
            
            # Analizza sentiment
            if articles:
                sentiment = news_collector.analyze_sentiment(articles)
                memory.update_news(sentiment, len(articles))
            
            elapsed = time.time() - start_time
            logger.info(f"⏱️ News AI ciclo: {elapsed:.2f}s")
            
            # Attende 10 minuti
            await asyncio.sleep(600)
            
        except Exception as e:
            logger.error(f"❌ Errore News AI: {e}")
            await asyncio.sleep(600)

async def main():
    """Funzione principale"""
    logger.info("🚀 === AVVIO SISTEMA DUAL AI SEMPLIFICATO ===")
    
    # Inizializza componenti
    memory = SimpleMemory()
    price_collector = FastPriceCollector()
    news_collector = SimpleNewsCollector()
    trading_logic = SimpleTradingLogic()
    
    # Avvia i due loop in parallelo
    try:
        await asyncio.gather(
            price_ai_loop(memory, price_collector, trading_logic),
            news_ai_loop(memory, news_collector)
        )
    except KeyboardInterrupt:
        logger.info("🛑 Sistema fermato dall'utente")
    except Exception as e:
        logger.error(f"❌ Errore sistema: {e}")

if __name__ == "__main__":
    asyncio.run(main())
