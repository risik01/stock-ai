#!/usr/bin/env python3
"""
CLI Monitor per il Trading Bot
Uso: python cli_monitor.py [comando]

Comandi:
  status    - Mostra stato generale
  positions - Mostra posizioni aperte
  trades    - Mostra ultime transazioni
  logs      - Mostra log recenti
  rl        - Mostra statistiche RL
  watch     - Modalità watch (aggiornamento continuo)
"""

import sys
import os
import json
import time
import pickle
from datetime import datetime
import argparse

# Aggiungi il path src
sys.path.append(os.path.dirname(__file__))

from portfolio import Portfolio
from data_collector import get_stock_data

class CLIMonitor:
    """Monitor CLI per il trading bot"""
    
    def __init__(self):
        self.data_dir = "/workspaces/stock-ai/data"
        self.portfolio_file = os.path.join(self.data_dir, "current_portfolio.pkl")
        self.log_file = os.path.join(self.data_dir, "aggressive_trader.log")
        self.model_file = os.path.join(self.data_dir, "rl_model.pkl")
        self.control_file = os.path.join(self.data_dir, "trader_control.txt")
    
    def load_portfolio(self):
        """Carica il portfolio corrente"""
        try:
            if os.path.exists(self.portfolio_file):
                with open(self.portfolio_file, "rb") as f:
                    return pickle.load(f)
        except Exception as e:
            print(f"⚠️  Errore nel caricamento portfolio: {e}")
        return Portfolio()
    
    def get_current_prices(self, tickers):
        """Ottiene prezzi attuali"""
        prices = {}
        for ticker in tickers:
            try:
                df = get_stock_data(ticker, period="1d")
                if len(df) > 0:
                    prices[ticker] = float(df["Close"].iloc[-1])
            except Exception:
                prices[ticker] = 0
        return prices
    
    def is_trader_active(self):
        """Controlla se il trader è attivo"""
        return not os.path.exists(self.control_file)
    
    def print_header(self, title):
        """Stampa header colorato"""
        print(f"\n🤖 {title}")
        print("=" * (len(title) + 3))
    
    def print_colored(self, text, value, is_profit=None):
        """Stampa testo colorato"""
        if is_profit is not None:
            if is_profit:
                print(f"{text}: \033[92m{value}\033[0m")  # Verde
            else:
                print(f"{text}: \033[91m{value}\033[0m")  # Rosso
        else:
            print(f"{text}: {value}")
    
    def show_status(self):
        """Mostra stato generale"""
        self.print_header("STATO GENERALE")
        
        # Stato trader
        trader_status = "🟢 ATTIVO" if self.is_trader_active() else "🔴 FERMO"
        print(f"Trader Status: {trader_status}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Portfolio
        portfolio = self.load_portfolio()
        metrics = portfolio.get_performance_metrics()
        
        print(f"\n💰 PORTAFOGLIO:")
        print(f"Liquidità: ${portfolio.cash:.2f}")
        
        # Calcola valore attuale CON prezzi aggiornati
        current_prices = {}
        total_unrealized_pnl = 0
        
        if portfolio.positions:
            current_prices = self.get_current_prices(list(portfolio.positions.keys()))
            
            # Calcola P&L non realizzato correttamente
            for ticker, position in portfolio.positions.items():
                current_price = current_prices.get(ticker, position["avg_price"])
                entry_price = position["avg_price"]
                shares = position["shares"]
                
                position_pnl = (current_price - entry_price) * shares
                total_unrealized_pnl += position_pnl
        
        total_value = portfolio.get_portfolio_value(current_prices)
        print(f"Valore Totale: ${total_value:.2f}")
        
        # Rendimento corretto
        initial_investment = 10000  # Valore iniziale
        total_return = ((total_value - initial_investment) / initial_investment) * 100
        self.print_colored("Rendimento Totale", f"{total_return:.2f}%", total_return >= 0)
        
        # P&L non realizzato CORRETTO
        self.print_colored("P&L Non Realizzato", f"${total_unrealized_pnl:.2f}", total_unrealized_pnl >= 0)
        
        print(f"\n📊 STATISTICHE:")
        print(f"Trades Totali: {metrics['total_trades']}")
        print(f"Win Rate: {metrics['win_rate']:.1f}%")
        print(f"Posizioni Aperte: {len(portfolio.positions)}")
    
    def show_positions(self):
        """Mostra posizioni aperte"""
        self.print_header("POSIZIONI APERTE")
        
        portfolio = self.load_portfolio()
        
        if not portfolio.positions:
            print("Nessuna posizione aperta")
            return
        
        # Ottieni prezzi attuali
        current_prices = self.get_current_prices(list(portfolio.positions.keys()))
        
        print(f"{'Ticker':<8} {'Azioni':<8} {'Prezzo Avg':<12} {'Prezzo Att':<12} {'P&L':<12} {'P&L %':<8}")
        print("-" * 70)
        
        for ticker, position in portfolio.positions.items():
            shares = position["shares"]
            avg_price = position["avg_price"]
            current_price = current_prices.get(ticker, avg_price)
            
            pnl = (current_price - avg_price) * shares
            pnl_pct = ((current_price - avg_price) / avg_price) * 100
            
            # Colore basato su profitto/perdita
            if pnl > 0:
                pnl_str = f"\033[92m${pnl:.2f}\033[0m"
                pnl_pct_str = f"\033[92m{pnl_pct:.1f}%\033[0m"
            elif pnl < 0:
                pnl_str = f"\033[91m${pnl:.2f}\033[0m"
                pnl_pct_str = f"\033[91m{pnl_pct:.1f}%\033[0m"
            else:
                pnl_str = f"${pnl:.2f}"
                pnl_pct_str = f"{pnl_pct:.1f}%"
            
            print(f"{ticker:<8} {shares:<8} ${avg_price:<11.2f} ${current_price:<11.2f} {pnl_str:<20} {pnl_pct_str}")
    
    def show_trades(self, limit=10):
        """Mostra ultime transazioni"""
        self.print_header(f"ULTIME {limit} TRANSAZIONI")
        
        portfolio = self.load_portfolio()
        
        if not portfolio.transactions:
            print("Nessuna transazione")
            return
        
        recent = portfolio.transactions[-limit:] if len(portfolio.transactions) > limit else portfolio.transactions
        
        for tx in reversed(recent):
            type_color = "\033[92m" if tx["type"] == "BUY" else "\033[91m"
            print(f"{type_color}{tx['type']}\033[0m {tx['shares']} azioni di {tx['ticker']} @ ${tx['price']:.2f} = ${tx['total']:.2f}")
    
    def show_logs(self, lines=20):
        """Mostra log recenti"""
        self.print_header(f"ULTIMI {lines} LOG")
        
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, "r") as f:
                    all_lines = f.readlines()
                    recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                    
                    for line in recent_lines:
                        print(line.strip())
            else:
                print("File di log non trovato")
        except Exception as e:
            print(f"Errore nella lettura log: {e}")
    
    def show_rl_stats(self):
        """Mostra statistiche RL"""
        self.print_header("STATISTICHE REINFORCEMENT LEARNING")
        
        try:
            if os.path.exists(self.model_file):
                with open(self.model_file, "rb") as f:
                    model_data = pickle.load(f)
                
                q_table = model_data.get("q_table", {})
                experiences = model_data.get("experiences", [])
                
                print(f"Stati Appresi: {len(q_table)}")
                print(f"Esperienze Totali: {len(experiences)}")
                print(f"Learning Rate: {model_data.get('learning_rate', 0.1)}")
                print(f"Discount Factor: {model_data.get('discount_factor', 0.95)}")
                print(f"Epsilon (Exploration): {model_data.get('epsilon', 0.1):.3f}")
                
                if experiences:
                    last_exp = experiences[-1]
                    print(f"\nUltima Esperienza:")
                    print(f"  Stato: {last_exp.get('state', 'N/A')}")
                    print(f"  Azione: {last_exp.get('action', 'N/A')}")
                    print(f"  Ricompensa: {last_exp.get('reward', 'N/A')}")
                    print(f"  Timestamp: {last_exp.get('timestamp', 'N/A')}")
            else:
                print("Modello RL non trovato")
        except Exception as e:
            print(f"Errore nella lettura modello RL: {e}")
    
    def watch_mode(self, interval=10):
        """Modalità watch con aggiornamento continuo"""
        print("🔄 MODALITÀ WATCH ATTIVA (Ctrl+C per uscire)")
        print(f"Aggiornamento ogni {interval} secondi\n")
        
        try:
            while True:
                # Pulisci schermo
                os.system('clear' if os.name == 'posix' else 'cls')
                
                self.show_status()
                print(f"\n⏰ Prossimo aggiornamento in {interval} secondi...")
                
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n👋 Watch mode terminato")

def main():
    parser = argparse.ArgumentParser(description="CLI Monitor per Stock AI Trading Bot")
    parser.add_argument('command', nargs='?', default='status',
                        choices=['status', 'positions', 'trades', 'logs', 'rl', 'watch'],
                        help='Comando da eseguire')
    parser.add_argument('--lines', type=int, default=20, help='Numero di righe per logs/trades')
    parser.add_argument('--interval', type=int, default=10, help='Intervallo per watch mode (secondi)')
    
    args = parser.parse_args()
    monitor = CLIMonitor()
    
    if args.command == 'status':
        monitor.show_status()
    elif args.command == 'positions':
        monitor.show_positions()
    elif args.command == 'trades':
        monitor.show_trades(args.lines)
    elif args.command == 'logs':
        monitor.show_logs(args.lines)
    elif args.command == 'rl':
        monitor.show_rl_stats()
    elif args.command == 'watch':
        monitor.watch_mode(args.interval)

if __name__ == "__main__":
    main()
