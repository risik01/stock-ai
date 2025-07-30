from flask import Flask, render_template, jsonify
import json
import os
from datetime import datetime, timedelta
import threading
import time
from portfolio import Portfolio
from data_collector import get_stock_data
import pickle

app = Flask(__name__, template_folder='../templates', static_folder='../static')

class DashboardData:
    """Classe per gestire i dati del dashboard"""
    
    def __init__(self):
        self.data_file = "/workspaces/stock-ai/data/dashboard_data.json"
        self.portfolio_file = "/workspaces/stock-ai/data/current_portfolio.pkl"
        self.log_file = "/workspaces/stock-ai/data/aggressive_trader.log"
        self.model_file = "/workspaces/stock-ai/data/rl_model.pkl"
        
        # Crea directory se non esiste
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        # Thread per aggiornamento continuo
        self.update_thread = None
        self.is_running = False
    
    def get_portfolio_data(self):
        """Carica i dati del portfolio"""
        try:
            if os.path.exists(self.portfolio_file):
                with open(self.portfolio_file, "rb") as f:
                    portfolio = pickle.load(f)
                return portfolio
        except Exception as e:
            print(f"Errore nel caricare portfolio: {e}")
        
        # Portfolio vuoto se non trovato
        return Portfolio()
    
    def get_current_prices(self, tickers):
        """Ottiene i prezzi attuali per i ticker"""
        prices = {}
        for ticker in tickers:
            try:
                df = get_stock_data(ticker, period="1d")
                if len(df) > 0:
                    prices[ticker] = float(df["Close"].iloc[-1])
                else:
                    prices[ticker] = 0
            except Exception:
                prices[ticker] = 0
        return prices
    
    def get_recent_logs(self, lines=50):
        """Ottiene i log recenti"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, "r") as f:
                    all_lines = f.readlines()
                    return all_lines[-lines:] if len(all_lines) > lines else all_lines
        except Exception:
            pass
        return []
    
    def get_rl_stats(self):
        """Ottiene statistiche del modello RL"""
        try:
            if os.path.exists(self.model_file):
                with open(self.model_file, "rb") as f:
                    model_data = pickle.load(f)
                
                q_table = model_data.get("q_table", {})
                experiences = model_data.get("experiences", [])
                
                return {
                    "states_learned": len(q_table),
                    "total_experiences": len(experiences),
                    "epsilon": model_data.get("epsilon", 0.1),
                    "learning_rate": model_data.get("learning_rate", 0.1)
                }
        except Exception:
            pass
        
        return {
            "states_learned": 0,
            "total_experiences": 0,
            "epsilon": 0.1,
            "learning_rate": 0.1
        }
    
    def update_dashboard_data(self):
        """Aggiorna i dati del dashboard"""
        try:
            portfolio = self.get_portfolio_data()
            
            # Ottieni prezzi attuali per le posizioni
            current_prices = {}
            if portfolio.positions:
                tickers = list(portfolio.positions.keys())
                current_prices = self.get_current_prices(tickers)
            
            # Calcola metriche
            metrics = portfolio.get_performance_metrics()
            
            # Calcola P&L per posizione
            positions_data = []
            total_unrealized_pnl = 0
            
            for ticker, position in portfolio.positions.items():
                shares = position["shares"]
                avg_price = position["avg_price"]
                current_price = current_prices.get(ticker, avg_price)
                
                market_value = shares * current_price
                cost_basis = shares * avg_price
                unrealized_pnl = market_value - cost_basis
                unrealized_pnl_pct = (unrealized_pnl / cost_basis) * 100 if cost_basis > 0 else 0
                
                total_unrealized_pnl += unrealized_pnl
                
                positions_data.append({
                    "ticker": ticker,
                    "shares": shares,
                    "avg_price": avg_price,
                    "current_price": current_price,
                    "market_value": market_value,
                    "cost_basis": cost_basis,
                    "unrealized_pnl": unrealized_pnl,
                    "unrealized_pnl_pct": unrealized_pnl_pct,
                    "status": "profit" if unrealized_pnl > 0 else "loss" if unrealized_pnl < 0 else "neutral"
                })
            
            # Ultime transazioni
            recent_transactions = portfolio.transactions[-10:] if portfolio.transactions else []
            
            # Log recenti
            recent_logs = self.get_recent_logs(20)
            
            # Statistiche RL
            rl_stats = self.get_rl_stats()
            
            # Controlla se il trader è attivo
            trader_active = os.path.exists("/workspaces/stock-ai/data/trader_control.txt") == False
            
            data = {
                "timestamp": datetime.now().isoformat(),
                "trader_status": "ACTIVE" if trader_active else "STOPPED",
                "portfolio": {
                    "cash": portfolio.cash,
                    "total_value": portfolio.get_portfolio_value(current_prices),
                    "total_return": metrics["total_return"],
                    "win_rate": metrics["win_rate"],
                    "total_trades": metrics["total_trades"],
                    "unrealized_pnl": total_unrealized_pnl
                },
                "positions": positions_data,
                "recent_transactions": [
                    {
                        "type": t["type"],
                        "ticker": t["ticker"],
                        "shares": t["shares"],
                        "price": t["price"],
                        "total": t["total"]
                    } for t in recent_transactions
                ],
                "recent_logs": [log.strip() for log in recent_logs],
                "rl_stats": rl_stats
            }
            
            # Salva i dati
            with open(self.data_file, "w") as f:
                json.dump(data, f, indent=2)
            
            return data
            
        except Exception as e:
            print(f"Errore nell'aggiornamento dati dashboard: {e}")
            return None
    
    def start_auto_update(self, interval=10):
        """Avvia l'aggiornamento automatico"""
        def update_loop():
            while self.is_running:
                self.update_dashboard_data()
                time.sleep(interval)
        
        self.is_running = True
        self.update_thread = threading.Thread(target=update_loop, daemon=True)
        self.update_thread.start()
    
    def stop_auto_update(self):
        """Ferma l'aggiornamento automatico"""
        self.is_running = False
        if self.update_thread:
            self.update_thread.join()

dashboard_data = DashboardData()

@app.route('/')
def index():
    """Pagina principale del dashboard"""
    return render_template('dashboard.html')

@app.route('/api/data')
def get_data():
    """API per ottenere i dati del dashboard"""
    data = dashboard_data.update_dashboard_data()
    return jsonify(data)

@app.route('/api/logs')
def get_logs():
    """API per ottenere i log"""
    logs = dashboard_data.get_recent_logs(100)
    return jsonify({"logs": [log.strip() for log in logs]})

def run_dashboard(host='0.0.0.0', port=5000, debug=False):
    """Avvia il server web"""
    print(f"🌐 Dashboard disponibile su: http://localhost:{port}")
    print("   Aggiornamento automatico ogni 10 secondi")
    
    # Avvia aggiornamento automatico
    dashboard_data.start_auto_update()
    
    try:
        app.run(host=host, port=port, debug=debug, threaded=True)
    finally:
        dashboard_data.stop_auto_update()

if __name__ == "__main__":
    run_dashboard()
