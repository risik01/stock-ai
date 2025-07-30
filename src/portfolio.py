import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)

class Portfolio:
    """Classe per gestire un portafoglio di investimenti"""
    
    def __init__(self, config):
        """
        Inizializza il portafoglio
        
        Args:
            config (dict): Configurazione del portafoglio, include 'trading' e 'data'
        """
        self.config = config
        self.initial_capital = config['trading']['initial_capital']
        self.portfolio_file = Path("data/portfolio.json")
        self.load_portfolio()
        
    def load_portfolio(self):
        """Carica il portafoglio da un file"""
        if self.portfolio_file.exists():
            with open(self.portfolio_file, 'r') as f:
                data = json.load(f)
                self.cash = data.get('cash', self.initial_capital)
                self.positions = data.get('positions', {})
                self.trades = data.get('trades', [])
        else:
            self.cash = self.initial_capital
            self.positions = {}
            self.trades = []
            self.save_portfolio()
    
    def save_portfolio(self):
        """Salva il portafoglio su un file"""
        data = {
            'cash': self.cash,
            'positions': self.positions,
            'trades': self.trades,
            'last_updated': datetime.now().isoformat()
        }
        with open(self.portfolio_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def execute_trade(self, action):
        """Esegue un'operazione di trading reale (non implementata)"""
        # Questo si collegherebbe a un'API di broker reale
        logger.warning("Trading reale non implementato - utilizza il paper trading")
        return self.simulate_trade(action)
    
    def simulate_trade(self, action):
        """Simula un'operazione di trading per il paper trading"""
        symbol = action.get('symbol')
        trade_type = action.get('type')  # 'buy' o 'sell'
        quantity = action.get('quantity', 0)
        price = action.get('price', 0)
        
        if trade_type == 'buy':
            cost = quantity * price
            if cost <= self.cash:
                self.cash -= cost
                self.positions[symbol] = self.positions.get(symbol, 0) + quantity
                
                trade = {
                    'timestamp': datetime.now().isoformat(),
                    'symbol': symbol,
                    'type': 'buy',
                    'quantity': quantity,
                    'price': price,
                    'total': cost
                }
                self.trades.append(trade)
                logger.info(f"Acquistato {quantity} azioni di {symbol} a ${price:.2f}")
                
        elif trade_type == 'sell':
            if symbol in self.positions and self.positions[symbol] >= quantity:
                revenue = quantity * price
                self.cash += revenue
                self.positions[symbol] -= quantity
                
                if self.positions[symbol] == 0:
                    del self.positions[symbol]
                
                trade = {
                    'timestamp': datetime.now().isoformat(),
                    'symbol': symbol,
                    'type': 'sell',
                    'quantity': quantity,
                    'price': price,
                    'total': revenue
                }
                self.trades.append(trade)
                logger.info(f"Venduto {quantity} azioni di {symbol} a ${price:.2f}")
        
        self.save_portfolio()
        return True
    
    def get_total_value(self):
        """Calcola il valore totale del portafoglio"""
        # Questo avrebbe bisogno dei prezzi di mercato attuali
        # Per ora, restituisce liquidità + valore stimato della posizione
        return self.cash + sum(pos * 100 for pos in self.positions.values())  # Segnaposto
    
    def get_positions(self):
        """Ottieni le posizioni correnti"""
        return self.positions.copy()
    
    def show_status(self):
        """Mostra lo stato del portafoglio"""
        print("\n=== STATO PORTAFOGLIO ===")
        print(f"Liquidità: ${self.cash:.2f}")
        print(f"Valore Totale: ${self.get_total_value():.2f}")
        print(f"Operazioni Totali: {len(self.trades)}")
        
        if self.positions:
            print("\nPosizioni:")
            for symbol, quantity in self.positions.items():
                print(f"  {symbol}: {quantity} azioni")
        else:
            print("\nNessuna posizione aperta")
            
        if self.trades:
            print(f"\nOperazioni Recenti:")
            for trade in self.trades[-5:]:
                print(f"  {trade['timestamp'][:19]} - {trade['type'].upper()} {trade['quantity']} {trade['symbol']} @ ${trade['price']:.2f}")
    
    def reset(self):
        """Ripristina il portafoglio allo stato iniziale"""
        self.cash = self.initial_capital
        self.positions = {}
        self.trades = []
        self.save_portfolio()
    
    def add_symbol(self, symbol):
        """Aggiungi un simbolo alla lista di osservazione"""
        if 'symbols' not in self.config['data']:
            self.config['data']['symbols'] = []
        if symbol not in self.config['data']['symbols']:
            self.config['data']['symbols'].append(symbol)
            # Il salvataggio della configurazione dovrebbe essere implementato
    
    def remove_symbol(self, symbol):
        """Rimuovi un simbolo dalla lista di osservazione"""
        if symbol in self.config['data']['symbols']:
            self.config['data']['symbols'].remove(symbol)
    
    def set_config_param(self, param, value):
        """Imposta un parametro di configurazione"""
        # Questo avrebbe bisogno di una gestione adeguata della configurazione
        logger.info(f"Imposterei {param} = {value}")
    
    def get_portfolio_value(self, current_prices=None):
        """
        Calcola il valore totale del portafoglio
        
        Args:
            current_prices (dict): Prezzi attuali {ticker: price}
        
        Returns:
            float: Valore totale del portafoglio
        """
        total_value = self.cash
        
        for ticker, position in self.positions.items():
            if current_prices and ticker in current_prices:
                market_value = position["shares"] * current_prices[ticker]
            else:
                market_value = position["shares"] * position["avg_price"]
            total_value += market_value
        
        return total_value
    
    def get_performance_metrics(self, initial_value=10000):
        """
        Calcola metriche di performance del portafoglio
        
        Args:
            initial_value: Valore iniziale del portafoglio
            
        Returns:
            dict: Metriche di performance
        """
        current_value = self.get_portfolio_value()
        total_return = ((current_value - initial_value) / initial_value) * 100
        
        # Calcola profitti/perdite per transazione
        profits = []
        for i, transaction in enumerate(self.transactions):
            if transaction["type"] == "SELL":
                # Trova la transazione di acquisto corrispondente
                ticker = transaction["ticker"]
                sell_price = transaction["price"]
                
                # Cerca l'ultimo acquisto per questo ticker
                buy_price = None
                for j in range(i-1, -1, -1):
                    if (self.transactions[j]["type"] == "BUY" and 
                        self.transactions[j]["ticker"] == ticker):
                        buy_price = self.transactions[j]["price"]
                        break
                
                if buy_price:
                    profit_pct = ((sell_price - buy_price) / buy_price) * 100
                    profits.append(profit_pct)
        
        win_rate = (sum(1 for p in profits if p > 0) / len(profits) * 100) if profits else 0
        avg_profit = np.mean(profits) if profits else 0
        
        return {
            "total_return": total_return,
            "current_value": current_value,
            "win_rate": win_rate,
            "avg_profit_per_trade": avg_profit,
            "total_trades": len(self.transactions),
            "cash_remaining": self.cash
        }

    def report(self, show_performance=True):
        """Stampa un report del portafoglio con metriche di performance"""
        print("=== REPORT PORTAFOGLIO ===")
        print(f"Liquidità disponibile: ${self.cash:.2f}")
        print()
        
        if self.positions:
            print("Posizioni aperte:")
            for ticker, position in self.positions.items():
                shares = position["shares"]
                avg_price = position["avg_price"]
                market_value = shares * avg_price
                print(f"  {ticker}: {shares} azioni @ ${avg_price:.2f} = ${market_value:.2f}")
        else:
            print("Nessuna posizione aperta")
        
        print()
        total_value = self.get_portfolio_value()
        print(f"Valore totale portafoglio: ${total_value:.2f}")
        
        if self.transactions:
            print(f"Transazioni effettuate: {len(self.transactions)}")
        
        if show_performance:
            metrics = self.get_performance_metrics()
            print(f"\n=== METRICHE PERFORMANCE ===")
            print(f"Rendimento totale: {metrics['total_return']:.2f}%")
            print(f"Win rate: {metrics['win_rate']:.1f}%")
            print(f"Profitto medio per trade: {metrics['avg_profit_per_trade']:.2f}%")
