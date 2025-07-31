#!/usr/bin/env python3
"""
Live Trading Monitor - Sistema di trading automatico continuo
Monitora costantemente i mercati ed esegue operazioni automatiche
"""

import time
import logging
import threading
from datetime import datetime, time as dt_time
import pandas as pd
import yfinance as yf
from typing import Dict, List, Optional, Tuple
import json
import os
from dataclasses import dataclass

from config_manager import ConfigManager
from rl_agent import RLAgent
from portfolio import Portfolio
from strategy_engine import StrategyEngine

@dataclass
class TradeSignal:
    """Segnale di trading"""
    symbol: str
    action: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float
    price: float
    quantity: int
    timestamp: datetime
    reason: str

class LiveTradingMonitor:
    """
    Sistema di monitoraggio e trading automatico continuo
    """
    
    def __init__(self, config_path: str = "config/settings.json"):
        """Inizializza il monitor di trading live"""
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('data/live_trading.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.portfolio = Portfolio(self.config['trading']['initial_capital'])
        self.rl_agent = RLAgent(self.config['rl_agent'])
        self.strategy_engine = StrategyEngine(self.config)
        
        # Trading state
        self.is_running = False
        self.trading_thread = None
        self.last_prices = {}
        self.trade_history = []
        
        # Configuration
        self.live_config = self.config['trading']['live_trading']
        self.monitoring_config = self.config['monitoring']
        self.symbols = self.config['data']['symbols']
        
        self.logger.info("LiveTradingMonitor inizializzato con successo")
    
    def is_market_open(self) -> bool:
        """Verifica se il mercato è aperto"""
        if not self.live_config.get('market_hours_only', True):
            return True
            
        now = datetime.now().time()
        market_open = dt_time(9, 30)  # 9:30 AM
        market_close = dt_time(16, 0)  # 4:00 PM
        
        # Verifica se è un giorno feriale
        weekday = datetime.now().weekday()
        is_weekday = weekday < 5  # Lunedì=0, Venerdì=4
        
        return is_weekday and market_open <= now <= market_close
    
    def get_real_time_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """Ottiene dati in tempo reale per i simboli specificati"""
        try:
            data = {}
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                
                # Dati intraday
                hist = ticker.history(period="1d", interval="1m")
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    volume = hist['Volume'].iloc[-1]
                    
                    # Calcola indicatori tecnici
                    rsi = self.calculate_rsi(hist['Close'])
                    macd = self.calculate_macd(hist['Close'])
                    
                    data[symbol] = {
                        'price': current_price,
                        'volume': volume,
                        'change': ((current_price - hist['Open'].iloc[0]) / hist['Open'].iloc[0]) * 100,
                        'rsi': rsi,
                        'macd': macd,
                        'timestamp': datetime.now()
                    }
                    
            return data
            
        except Exception as e:
            self.logger.error(f"Errore nel recupero dati real-time: {e}")
            return {}
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calcola RSI (Relative Strength Index)"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1] if not rsi.empty else 50.0
        except:
            return 50.0
    
    def calculate_macd(self, prices: pd.Series) -> Dict[str, float]:
        """Calcola MACD (Moving Average Convergence Divergence)"""
        try:
            exp1 = prices.ewm(span=12).mean()
            exp2 = prices.ewm(span=26).mean()
            macd_line = exp1 - exp2
            signal_line = macd_line.ewm(span=9).mean()
            histogram = macd_line - signal_line
            
            return {
                'macd': macd_line.iloc[-1],
                'signal': signal_line.iloc[-1],
                'histogram': histogram.iloc[-1]
            }
        except:
            return {'macd': 0.0, 'signal': 0.0, 'histogram': 0.0}
    
    def analyze_trading_signals(self, market_data: Dict[str, Dict]) -> List[TradeSignal]:
        """Analizza i dati di mercato e genera segnali di trading"""
        signals = []
        
        for symbol, data in market_data.items():
            try:
                # Analisi tecnica
                rsi = data['rsi']
                macd = data['macd']
                price = data['price']
                volume = data['volume']
                
                # Logica di trading basata su indicatori
                action = 'HOLD'
                confidence = 0.5
                reason = "Nessun segnale chiaro"
                
                # Segnali RSI
                if rsi < self.monitoring_config['alert_thresholds']['rsi_oversold']:
                    action = 'BUY'
                    confidence = 0.7
                    reason = f"RSI oversold ({rsi:.1f})"
                elif rsi > self.monitoring_config['alert_thresholds']['rsi_overbought']:
                    action = 'SELL'
                    confidence = 0.7
                    reason = f"RSI overbought ({rsi:.1f})"
                
                # Segnali MACD
                if macd['histogram'] > 0 and action == 'HOLD':
                    action = 'BUY'
                    confidence = 0.6
                    reason = "MACD bullish"
                elif macd['histogram'] < 0 and action == 'HOLD':
                    action = 'SELL'
                    confidence = 0.6
                    reason = "MACD bearish"
                
                # Usa RL Agent per conferma
                if hasattr(self.rl_agent, 'predict'):
                    rl_signal = self.rl_agent.predict_action(data)
                    if rl_signal and rl_signal != action:
                        confidence *= 0.8  # Riduce confidenza se RL disagree
                
                # Calcola quantity basata su risk management
                quantity = self.calculate_position_size(symbol, price, confidence)
                
                if action != 'HOLD' and confidence > 0.6:
                    signal = TradeSignal(
                        symbol=symbol,
                        action=action,
                        confidence=confidence,
                        price=price,
                        quantity=quantity,
                        timestamp=datetime.now(),
                        reason=reason
                    )
                    signals.append(signal)
                    
            except Exception as e:
                self.logger.error(f"Errore analisi segnali per {symbol}: {e}")
        
        return signals
    
    def calculate_position_size(self, symbol: str, price: float, confidence: float) -> int:
        """Calcola la dimensione ottimale della posizione"""
        try:
            # Risk per trade
            risk_per_trade = self.live_config['risk_per_trade']
            portfolio_value = self.portfolio.get_total_value()
            max_risk_amount = portfolio_value * risk_per_trade
            
            # Posizione massima
            max_position_value = portfolio_value * self.config['trading']['max_position_size']
            
            # Calcola quantity basata su confidence e risk
            risk_adjusted_amount = max_risk_amount * confidence
            position_value = min(risk_adjusted_amount, max_position_value)
            
            quantity = int(position_value / price)
            return max(1, quantity) if quantity > 0 else 0
            
        except Exception as e:
            self.logger.error(f"Errore calcolo position size: {e}")
            return 1
    
    def execute_trade(self, signal: TradeSignal) -> bool:
        """Esegue un trade basato sul segnale"""
        try:
            # Verifica limiti di trading
            if not self.can_execute_trade(signal):
                return False
            
            success = False
            if signal.action == 'BUY':
                success = self.portfolio.buy_stock(
                    signal.symbol, 
                    signal.quantity, 
                    signal.price
                )
            elif signal.action == 'SELL':
                success = self.portfolio.sell_stock(
                    signal.symbol, 
                    signal.quantity, 
                    signal.price
                )
            
            if success:
                self.trade_history.append({
                    'timestamp': signal.timestamp,
                    'symbol': signal.symbol,
                    'action': signal.action,
                    'quantity': signal.quantity,
                    'price': signal.price,
                    'confidence': signal.confidence,
                    'reason': signal.reason
                })
                
                self.logger.info(
                    f"TRADE ESEGUITO: {signal.action} {signal.quantity} {signal.symbol} "
                    f"@ ${signal.price:.2f} - {signal.reason}"
                )
                
                # Salva stato portfolio
                self.save_portfolio_state()
                
            return success
            
        except Exception as e:
            self.logger.error(f"Errore esecuzione trade: {e}")
            return False
    
    def can_execute_trade(self, signal: TradeSignal) -> bool:
        """Verifica se il trade può essere eseguito"""
        try:
            # Verifica limiti giornalieri
            today_trades = len([t for t in self.trade_history 
                              if t['timestamp'].date() == datetime.now().date()])
            
            if today_trades >= self.live_config['max_trades_per_day']:
                self.logger.warning("Limite trades giornalieri raggiunto")
                return False
            
            # Verifica intervallo minimo tra trades
            if self.trade_history:
                last_trade_time = self.trade_history[-1]['timestamp']
                time_diff = (datetime.now() - last_trade_time).total_seconds()
                
                if time_diff < self.live_config['min_trade_interval']:
                    return False
            
            # Verifica fondi disponibili per BUY
            if signal.action == 'BUY':
                required_amount = signal.quantity * signal.price
                if self.portfolio.cash < required_amount:
                    self.logger.warning(f"Fondi insufficienti per {signal.symbol}")
                    return False
            
            # Verifica posizione disponibile per SELL
            elif signal.action == 'SELL':
                current_position = self.portfolio.positions.get(signal.symbol, 0)
                if current_position < signal.quantity:
                    self.logger.warning(f"Posizione insufficiente per vendere {signal.symbol}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Errore verifica trade: {e}")
            return False
    
    def save_portfolio_state(self):
        """Salva lo stato del portfolio"""
        try:
            state = {
                'timestamp': datetime.now().isoformat(),
                'cash': self.portfolio.cash,
                'positions': dict(self.portfolio.positions),
                'total_value': self.portfolio.get_total_value(),
                'trade_count': len(self.trade_history)
            }
            
            with open('data/portfolio_state.json', 'w') as f:
                json.dump(state, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Errore salvataggio stato: {e}")
    
    def monitoring_loop(self):
        """Loop principale di monitoraggio"""
        self.logger.info("Avvio loop di monitoraggio...")
        
        while self.is_running:
            try:
                # Verifica se il mercato è aperto
                if not self.is_market_open():
                    self.logger.info("Mercato chiuso - in attesa...")
                    time.sleep(300)  # Attendi 5 minuti
                    continue
                
                # Ottieni dati real-time
                market_data = self.get_real_time_data(self.symbols)
                
                if market_data:
                    # Analizza segnali di trading
                    signals = self.analyze_trading_signals(market_data)
                    
                    # Esegui trades
                    for signal in signals:
                        if self.execute_trade(signal):
                            # Piccola pausa tra trades
                            time.sleep(5)
                    
                    # Aggiorna prezzi
                    self.last_prices.update({
                        symbol: data['price'] 
                        for symbol, data in market_data.items()
                    })
                
                # Attendi prima del prossimo check
                time.sleep(self.live_config['check_interval'])
                
            except KeyboardInterrupt:
                self.logger.info("Interruzione da utente")
                break
            except Exception as e:
                self.logger.error(f"Errore nel loop di monitoraggio: {e}")
                time.sleep(60)  # Attendi 1 minuto prima di riprovare
    
    def start_monitoring(self):
        """Avvia il monitoraggio in background"""
        if self.is_running:
            self.logger.warning("Monitoraggio già attivo")
            return
        
        self.is_running = True
        self.trading_thread = threading.Thread(target=self.monitoring_loop)
        self.trading_thread.daemon = True
        self.trading_thread.start()
        
        self.logger.info("Monitoraggio automatico avviato!")
    
    def stop_monitoring(self):
        """Ferma il monitoraggio"""
        self.is_running = False
        if self.trading_thread:
            self.trading_thread.join(timeout=10)
        
        self.logger.info("Monitoraggio fermato")
    
    def get_status(self) -> Dict:
        """Ottiene lo status del sistema"""
        return {
            'is_running': self.is_running,
            'market_open': self.is_market_open(),
            'portfolio_value': self.portfolio.get_total_value(),
            'cash': self.portfolio.cash,
            'positions': dict(self.portfolio.positions),
            'trades_today': len([t for t in self.trade_history 
                               if t['timestamp'].date() == datetime.now().date()]),
            'last_update': datetime.now().isoformat()
        }

def main():
    """Funzione principale per testing"""
    monitor = LiveTradingMonitor()
    
    try:
        print("🚀 Avvio Live Trading Monitor...")
        print("Premi Ctrl+C per fermare")
        
        monitor.start_monitoring()
        
        # Loop per mostrare status
        while monitor.is_running:
            status = monitor.get_status()
            print(f"\n📊 Status: Portfolio ${status['portfolio_value']:.2f} | "
                  f"Trades oggi: {status['trades_today']} | "
                  f"Mercato: {'🟢 Aperto' if status['market_open'] else '🔴 Chiuso'}")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n🛑 Fermando il sistema...")
        monitor.stop_monitoring()
        print("✅ Sistema fermato correttamente")

if __name__ == "__main__":
    main()
