#!/usr/bin/env python3
"""
Aggressive Trading System - Wrapper per Simple Dual AI
Sistema di trading più aggressivo con parametri ottimizzati per maggiori trade
"""

import logging
import sys
import os
import argparse
from pathlib import Path

# Aggiungi src al path
sys.path.append(str(Path(__file__).parent))

from simple_dual_ai import SimpleTradingLogic, FastPriceCollector, SimpleNewsCollector, SimpleMemory
import asyncio
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/aggressive_trader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AggressiveTradingLogic(SimpleTradingLogic):
    """Versione più aggressiva del trading logic"""
    
    def __init__(self, aggressiveness_level=5):
        super().__init__()
        self.aggressiveness_level = aggressiveness_level
        logger.info(f"🔥 Aggressive Trading Logic inizializzato - Livello: {aggressiveness_level}/10")
    
    def make_decision(self, symbol, current_price, previous_price, news_sentiment):
        """Decisioni più aggressive con soglie più basse"""
        
        # Calcola variazione prezzo
        if previous_price and previous_price > 0:
            price_change = (current_price - previous_price) / previous_price
        else:
            price_change = 0.0
        
        # Score combinato con aggressività
        score = 0.0
        
        # Fattore aggressività (1-10 -> 0.1-1.0)
        aggression_factor = self.aggressiveness_level / 10.0
        
        # Tecnico (70%): soglie ridotte per più trading
        base_threshold = 0.001 * (1.0 / aggression_factor)  # Più aggressivo = soglia più bassa
        if price_change > base_threshold:
            score += 0.7 * (price_change / (base_threshold * 10)) * aggression_factor
        elif price_change < -base_threshold:
            score -= 0.7 * abs(price_change / (base_threshold * 10)) * aggression_factor
        
        # News sentiment (30%) amplificato
        score += 0.3 * news_sentiment * aggression_factor
        
        # Soglie decision più aggressive
        buy_threshold = 0.2 * (1.0 / aggression_factor)  # Più bassa per più trade
        sell_threshold = -0.2 * (1.0 / aggression_factor)
        
        action = 'HOLD'
        if score > buy_threshold:
            action = 'BUY'
        elif score < sell_threshold:
            action = 'SELL'
        
        return {
            'symbol': symbol,
            'action': action,
            'score': score,
            'price_change': price_change,
            'news_sentiment': news_sentiment,
            'current_price': current_price,
            'aggressiveness': self.aggressiveness_level
        }
    
    def execute_trade(self, decision):
        """Esecuzione trade più aggressiva"""
        symbol = decision['symbol']
        action = decision['action']
        price = decision['current_price']
        
        # Position sizing più aggressivo
        aggression_factor = self.aggressiveness_level / 10.0
        max_investment = self.portfolio_value * (0.05 + 0.10 * aggression_factor)  # 5-15% del portfolio
        max_shares = max(1, int(max_investment / price))
        
        if action == 'BUY' and self.portfolio_value >= price * max_shares:
            # Acquista azioni
            self.positions[symbol] = self.positions.get(symbol, 0) + max_shares
            cost = price * max_shares
            self.portfolio_value -= cost
            self.trade_count += 1
            
            logger.info(f"🔥 AGGRESSIVE BUY: {max_shares} {symbol} a €{price:.2f} (Costo: €{cost:.2f}, Aggressività: {self.aggressiveness_level})")
            return True
            
        elif action == 'SELL' and self.positions.get(symbol, 0) > 0:
            # Vende tutte le azioni disponibili del simbolo
            shares_to_sell = self.positions[symbol]
            revenue = price * shares_to_sell
            self.positions[symbol] = 0
            self.portfolio_value += revenue
            self.trade_count += 1
            
            logger.info(f"🔥 AGGRESSIVE SELL: {shares_to_sell} {symbol} a €{price:.2f} (Ricavo: €{revenue:.2f}, Aggressività: {self.aggressiveness_level})")
            return True
        
        return False

class AggressiveTrader:
    """Wrapper per sistema di trading aggressivo"""
    
    def __init__(self, aggressiveness_level=5):
        self.aggressiveness_level = aggressiveness_level
        self.memory = SimpleMemory()
        self.price_collector = FastPriceCollector()
        self.news_collector = SimpleNewsCollector()
        self.trading_logic = AggressiveTradingLogic(aggressiveness_level)
        
        logger.info(f"🚀 Aggressive Trader inizializzato - Livello {aggressiveness_level}/10")
    
    async def run(self):
        """Avvia il sistema di trading aggressivo"""
        logger.info("🔥 === AVVIO AGGRESSIVE TRADING SYSTEM ===")
        
        # Avvia i loop in parallelo con cicli più veloci
        await asyncio.gather(
            self.price_ai_loop(),
            self.news_ai_loop()
        )
    
    async def price_ai_loop(self):
        """Loop Price AI più aggressivo (ogni 5 secondi)"""
        logger.info("⚡ Price AI aggressiva avviata (5s cicli)")
        previous_prices = {}
        
        while True:
            try:
                start_time = time.time()
                
                # Ottieni prezzi
                current_prices = self.price_collector.get_current_prices()
                
                if current_prices:
                    self.memory.update_prices(current_prices)
                    
                    # Prendi decisioni per ogni simbolo
                    decisions = []
                    news_sentiment = self.memory.news_sentiment
                    
                    logger.info(f"🔥 === ANALISI AGGRESSIVE AI PER {len(current_prices)} SIMBOLI ===")
                    
                    for symbol, price in current_prices.items():
                        previous_price = previous_prices.get(symbol, price)
                        
                        decision = self.trading_logic.make_decision(
                            symbol, price, previous_price, news_sentiment
                        )
                        
                        # Calcola variazione percentuale
                        if previous_price and previous_price > 0:
                            price_change_pct = ((price - previous_price) / previous_price) * 100
                        else:
                            price_change_pct = 0.0
                        
                        logger.info(f"🔥 {symbol}: €{price:.2f} | Δ{price_change_pct:+.2f}% | News:{news_sentiment:+.3f} | Score:{decision['score']:+.3f} | Aggr:{decision['aggressiveness']} → {decision['action']}")
                        
                        if decision['action'] != 'HOLD':
                            decisions.append(decision)
                            logger.info(f"⚡ AGGRESSIVE SIGNAL: {symbol} → {decision['action']} (score: {decision['score']:.3f})")
                    
                    if not decisions:
                        logger.info("📋 Nessun segnale aggressivo generato (tutti HOLD)")
                    else:
                        logger.info(f"🔥 {len(decisions)} SEGNALI AGGRESSIVI per esecuzione")
                    
                    # Esegui trades
                    for decision in decisions:
                        if self.trading_logic.execute_trade(decision):
                            self.memory.add_trade(decision)
                    
                    # Portfolio update
                    portfolio_value = self.trading_logic.get_portfolio_value(current_prices)
                    profit_pct = ((portfolio_value - 1000) / 1000) * 100
                    
                    # Mostra posizioni se ci sono trade
                    if self.trading_logic.trade_count > 0:
                        positions_str = ", ".join([f"{sym}:{qty}" for sym, qty in self.trading_logic.positions.items() if qty > 0])
                        if positions_str:
                            logger.info(f"🔥 Portfolio: €{portfolio_value:.2f} ({profit_pct:+.2f}%) | Trades: {self.trading_logic.trade_count} | Posizioni: {positions_str}")
                        else:
                            logger.info(f"🔥 Portfolio: €{portfolio_value:.2f} ({profit_pct:+.2f}%) | Trades: {self.trading_logic.trade_count} | Cash: €{self.trading_logic.portfolio_value:.2f}")
                    else:
                        logger.info(f"🔥 Portfolio: €{portfolio_value:.2f} ({profit_pct:+.2f}%) | Trades: {self.trading_logic.trade_count}")
                    
                    previous_prices = current_prices.copy()
                
                elapsed = time.time() - start_time
                logger.debug(f"⏱️ Aggressive Price AI ciclo: {elapsed:.2f}s")
                
                # Cicli più veloci per trading aggressivo
                await asyncio.sleep(5)  # 5 secondi invece di 10
                
            except Exception as e:
                logger.error(f"❌ Errore Aggressive Price AI: {e}")
                await asyncio.sleep(5)
    
    async def news_ai_loop(self):
        """Loop News AI (ogni 5 minuti per più reattività)"""
        logger.info("📰 News AI aggressiva avviata (5min cicli)")
        
        while True:
            try:
                start_time = time.time()
                
                # Raccoglie news
                articles = self.news_collector.collect_news()
                logger.info(f"📡 Raccolti {len(articles)} articoli")
                
                # Analizza sentiment
                if articles:
                    sentiment = self.news_collector.analyze_sentiment(articles)
                    self.memory.update_news(sentiment, len(articles))
                
                elapsed = time.time() - start_time
                logger.info(f"⏱️ Aggressive News AI ciclo: {elapsed:.2f}s")
                
                # Attende 5 minuti invece di 10
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"❌ Errore Aggressive News AI: {e}")
                await asyncio.sleep(300)

def main():
    """Funzione principale"""
    parser = argparse.ArgumentParser(description='Aggressive Trading System')
    parser.add_argument('--aggressiveness', type=int, choices=range(1, 11),
                       default=5, help='Livello aggressività (1-10, default: 5)')
    args = parser.parse_args()
    
    # Crea e avvia trader aggressivo
    trader = AggressiveTrader(aggressiveness_level=args.aggressiveness)
    
    try:
        asyncio.run(trader.run())
    except KeyboardInterrupt:
        logger.info("🛑 Aggressive Trading System fermato dall'utente")
    except Exception as e:
        logger.error(f"❌ Errore critico: {e}")

if __name__ == "__main__":
    main()
