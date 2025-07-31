#!/usr/bin/env python3
"""
Web Dashboard - Dashboard web per il sistema di trading
Interfaccia web real-time per monitorare portfolio, trades e performance
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import json
import pickle
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
import threading
import time
import pandas as pd
import plotly.graph_objs as go
import plotly.utils
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class TradingDashboard:
    """Dashboard per il sistema di trading"""
    
    def __init__(self, config):
        self.config = config
        self.data_dir = Path("data")
        self.portfolio_file = self.data_dir / "current_portfolio.pkl"
        self.log_file = self.data_dir / "aggressive_trader.log"
        
        # Cache per dati dashboard
        self.cache = {
            'portfolio': None,
            'prices': None,
            'performance': None,
            'last_update': None
        }
        
        # Auto-refresh thread
        self.refresh_thread = None
        self.running = False
        
    def load_portfolio(self):
        """Carica portfolio corrente"""
        try:
            if self.portfolio_file.exists():
                with open(self.portfolio_file, 'rb') as f:
                    portfolio = pickle.load(f)
                return portfolio
        except Exception as e:
            logger.warning(f"⚠️ Errore caricamento portfolio: {e}")
        
        # Portfolio di default
        from portfolio import Portfolio
        return Portfolio()
    
    def load_price_cache(self):
        """Carica cache prezzi"""
        try:
            price_file = self.data_dir / "price_cache.json"
            if price_file.exists():
                with open(price_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"⚠️ Errore caricamento prezzi: {e}")
        return {}
    
    def get_portfolio_summary(self):
        """Ottiene summary del portfolio"""
        portfolio = self.load_portfolio()
        prices = self.load_price_cache()
        
        # Calcola valore totale con prezzi attuali
        current_prices = {}
        for ticker in portfolio.positions.keys():
            if ticker in prices:
                current_prices[ticker] = prices[ticker]['price']
        
        total_value = portfolio.get_portfolio_value(current_prices)
        metrics = portfolio.get_performance_metrics()
        
        # Calcola P&L non realizzato
        unrealized_pnl = 0
        for ticker, position in portfolio.positions.items():
            if ticker in current_prices:
                current_price = current_prices[ticker]
                entry_price = position['avg_price']
                shares = position['shares']
                unrealized_pnl += (current_price - entry_price) * shares
        
        return {
            'cash': portfolio.cash,
            'total_value': total_value,
            'positions_count': len(portfolio.positions),
            'total_trades': len(portfolio.transactions),
            'unrealized_pnl': unrealized_pnl,
            'total_return': metrics.get('total_return', 0),
            'win_rate': metrics.get('win_rate', 0),
            'last_update': datetime.now().isoformat()
        }
    
    def get_positions_data(self):
        """Ottiene dati posizioni"""
        portfolio = self.load_portfolio()
        prices = self.load_price_cache()
        
        positions = []
        for ticker, position in portfolio.positions.items():
            current_price = prices.get(ticker, {}).get('price', position['avg_price'])
            shares = position['shares']
            avg_price = position['avg_price']
            
            current_value = shares * current_price
            cost_basis = shares * avg_price
            pnl = current_value - cost_basis
            pnl_pct = (pnl / cost_basis) * 100 if cost_basis > 0 else 0
            
            positions.append({
                'ticker': ticker,
                'shares': shares,
                'avg_price': avg_price,
                'current_price': current_price,
                'current_value': current_value,
                'cost_basis': cost_basis,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'daily_change': prices.get(ticker, {}).get('daily_change_pct', 0)
            })
        
        return sorted(positions, key=lambda x: abs(x['pnl']), reverse=True)
    
    def get_transactions_data(self, limit: int = 50):
        """Ottiene dati transazioni"""
        portfolio = self.load_portfolio()
        
        transactions = []
        for tx in portfolio.transactions[-limit:]:
            transactions.append({
                'timestamp': tx.get('timestamp', datetime.now().isoformat()),
                'type': tx['type'],
                'ticker': tx['ticker'],
                'shares': tx['shares'],
                'price': tx['price'],
                'total': tx['total'],
                'commission': tx.get('commission', 0)
            })
        
        return list(reversed(transactions))
    
    def get_performance_chart_data(self):
        """Genera dati per grafico performance"""
        portfolio = self.load_portfolio()
        
        # Calcola valore portfolio nel tempo
        dates = []
        values = []
        
        # Se abbiamo transazioni, calcola performance storica
        if portfolio.transactions:
            # Raggruppa per giorno
            daily_values = {}
            running_cash = 10000  # Capitale iniziale
            positions = {}
            
            for tx in portfolio.transactions:
                date = tx.get('timestamp', datetime.now().isoformat())[:10]
                
                if tx['type'] == 'BUY':
                    running_cash -= tx['total']
                    if tx['ticker'] not in positions:
                        positions[tx['ticker']] = {'shares': 0, 'avg_price': 0}
                    
                    old_shares = positions[tx['ticker']]['shares']
                    old_value = old_shares * positions[tx['ticker']]['avg_price']
                    new_value = tx['shares'] * tx['price']
                    total_shares = old_shares + tx['shares']
                    
                    if total_shares > 0:
                        positions[tx['ticker']]['avg_price'] = (old_value + new_value) / total_shares
                    positions[tx['ticker']]['shares'] = total_shares
                
                elif tx['type'] == 'SELL':
                    running_cash += tx['total']
                    if tx['ticker'] in positions:
                        positions[tx['ticker']]['shares'] -= tx['shares']
                        if positions[tx['ticker']]['shares'] <= 0:
                            del positions[tx['ticker']]
                
                # Calcola valore totale (semplificato)
                portfolio_value = running_cash
                for ticker, pos in positions.items():
                    portfolio_value += pos['shares'] * pos['avg_price']
                
                daily_values[date] = portfolio_value
            
            # Converti in liste per grafico
            dates = sorted(daily_values.keys())
            values = [daily_values[date] for date in dates]
        
        # Se non abbiamo abbastanza dati, genera dati di esempio
        if len(dates) < 2:
            start_date = datetime.now() - timedelta(days=30)
            for i in range(30):
                date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
                value = 10000 + (i * 50) + (i % 7 * 25)  # Trend crescente con oscillazioni
                dates.append(date)
                values.append(value)
        
        return {
            'dates': dates,
            'values': values,
            'initial_value': values[0] if values else 10000,
            'current_value': values[-1] if values else 10000
        }
    
    def get_sector_allocation(self):
        """Calcola allocazione per settore"""
        portfolio = self.load_portfolio()
        prices = self.load_price_cache()
        
        # Mapping settori semplificato (in un sistema reale verrebbe da database)
        sector_mapping = {
            'AAPL': 'Technology',
            'GOOGL': 'Technology', 
            'MSFT': 'Technology',
            'TSLA': 'Automotive',
            'NVDA': 'Technology',
            'AMD': 'Technology',
            'META': 'Technology',
            'NFLX': 'Entertainment',
            'AMZN': 'E-commerce',
            'JPM': 'Finance',
            'BAC': 'Finance',
            'GS': 'Finance'
        }
        
        sectors = {}
        total_value = 0
        
        for ticker, position in portfolio.positions.items():
            current_price = prices.get(ticker, {}).get('price', position['avg_price'])
            value = position['shares'] * current_price
            sector = sector_mapping.get(ticker, 'Other')
            
            if sector not in sectors:
                sectors[sector] = 0
            sectors[sector] += value
            total_value += value
        
        # Converti in percentuali
        sector_data = []
        for sector, value in sectors.items():
            percentage = (value / total_value * 100) if total_value > 0 else 0
            sector_data.append({
                'sector': sector,
                'value': value,
                'percentage': percentage
            })
        
        return sorted(sector_data, key=lambda x: x['value'], reverse=True)
    
    def get_recent_logs(self, lines: int = 100):
        """Ottiene log recenti"""
        try:
            if self.log_file.exists():
                with open(self.log_file, 'r') as f:
                    all_lines = f.readlines()
                    recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                    return [line.strip() for line in recent_lines]
        except Exception as e:
            logger.warning(f"⚠️ Errore lettura log: {e}")
        
        return ["Log non disponibili"]
    
    def get_system_status(self):
        """Ottiene stato sistema"""
        try:
            import psutil
            
            # Check trader status
            control_file = Path("data/trader_control.txt")
            trader_active = not control_file.exists()
            
            # System metrics
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'trader_active': trader_active,
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'disk_usage': disk.percent,
                'timestamp': datetime.now().isoformat()
            }
        except ImportError:
            # Fallback se psutil non disponibile
            control_file = Path("data/trader_control.txt")
            trader_active = not control_file.exists()
            
            return {
                'trader_active': trader_active,
                'cpu_usage': 0,
                'memory_usage': 0,
                'disk_usage': 0,
                'timestamp': datetime.now().isoformat()
            }
    
    def start_auto_refresh(self, interval: int = 30):
        """Avvia refresh automatico dati"""
        if self.refresh_thread and self.refresh_thread.is_alive():
            return
        
        self.running = True
        self.refresh_thread = threading.Thread(target=self._refresh_loop, args=(interval,))
        self.refresh_thread.daemon = True
        self.refresh_thread.start()
        
        logger.info(f"🔄 Auto-refresh avviato ({interval}s)")
    
    def stop_auto_refresh(self):
        """Ferma refresh automatico"""
        self.running = False
        if self.refresh_thread:
            self.refresh_thread.join(timeout=5)
        logger.info("🛑 Auto-refresh fermato")
    
    def _refresh_loop(self, interval: int):
        """Loop di refresh dati"""
        while self.running:
            try:
                # Aggiorna cache
                self.cache['portfolio'] = self.get_portfolio_summary()
                self.cache['prices'] = self.load_price_cache()
                self.cache['performance'] = self.get_performance_chart_data()
                self.cache['last_update'] = datetime.now().isoformat()
                
            except Exception as e:
                logger.error(f"❌ Errore refresh: {e}")
            
            time.sleep(interval)

def create_app(config):
    """Crea app Flask con configurazione"""
    app = Flask(__name__, template_folder='../templates')
    app.config['SECRET_KEY'] = 'stock-ai-dashboard-secret-key'
    
    # CORS per API
    CORS(app)
    
    # SocketIO per real-time
    try:
        socketio = SocketIO(app, cors_allowed_origins="*")
    except ImportError:
        logger.warning("⚠️ SocketIO non disponibile, modalità basic")
        socketio = None
    
    # Dashboard instance
    dashboard = TradingDashboard(config)
    
    @app.route('/')
    def index():
        """Homepage dashboard"""
        return render_template('dashboard.html')
    
    @app.route('/api/portfolio/summary')
    def api_portfolio_summary():
        """API: Summary portfolio"""
        try:
            return jsonify(dashboard.get_portfolio_summary())
        except Exception as e:
            logger.error(f"❌ Errore API portfolio summary: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/portfolio/positions')
    def api_positions():
        """API: Posizioni portfolio"""
        try:
            return jsonify(dashboard.get_positions_data())
        except Exception as e:
            logger.error(f"❌ Errore API positions: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/portfolio/transactions')
    def api_transactions():
        """API: Transazioni"""
        try:
            limit = request.args.get('limit', 50, type=int)
            return jsonify(dashboard.get_transactions_data(limit))
        except Exception as e:
            logger.error(f"❌ Errore API transactions: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/charts/performance')
    def api_performance_chart():
        """API: Dati grafico performance"""
        try:
            return jsonify(dashboard.get_performance_chart_data())
        except Exception as e:
            logger.error(f"❌ Errore API performance chart: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/charts/sectors')
    def api_sectors_chart():
        """API: Allocazione settori"""
        try:
            return jsonify(dashboard.get_sector_allocation())
        except Exception as e:
            logger.error(f"❌ Errore API sectors chart: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/system/status')
    def api_system_status():
        """API: Stato sistema"""
        try:
            return jsonify(dashboard.get_system_status())
        except Exception as e:
            logger.error(f"❌ Errore API system status: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/system/logs')
    def api_logs():
        """API: Log sistema"""
        try:
            lines = request.args.get('lines', 100, type=int)
            return jsonify({'logs': dashboard.get_recent_logs(lines)})
        except Exception as e:
            logger.error(f"❌ Errore API logs: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/trader/control', methods=['POST'])
    def api_trader_control():
        """API: Controllo trader"""
        try:
            action = request.json.get('action')
            control_file = Path("data/trader_control.txt")
            
            if action == 'stop':
                with open(control_file, 'w') as f:
                    f.write("CLOSEALLBOT")
                return jsonify({'success': True, 'message': 'Trader fermato'})
            
            elif action == 'start':
                if control_file.exists():
                    control_file.unlink()
                return jsonify({'success': True, 'message': 'Trader avviato'})
            
            else:
                return jsonify({'error': 'Azione non valida'}), 400
                
        except Exception as e:
            logger.error(f"❌ Errore API trader control: {e}")
            return jsonify({'error': str(e)}), 500
    
    if socketio:
        @socketio.on('connect')
        def handle_connect():
            """WebSocket: Connessione"""
            logger.info("🔌 Client connesso")
            emit('status', {'message': 'Connesso alla dashboard'})
        
        @socketio.on('disconnect')
        def handle_disconnect():
            """WebSocket: Disconnessione"""
            logger.info("🔌 Client disconnesso")
        
        @socketio.on('request_update')
        def handle_update_request():
            """WebSocket: Richiesta aggiornamento"""
            try:
                # Invia dati aggiornati
                emit('portfolio_update', dashboard.get_portfolio_summary())
                emit('positions_update', dashboard.get_positions_data())
                emit('system_update', dashboard.get_system_status())
            except Exception as e:
                logger.error(f"❌ Errore WebSocket update: {e}")
                emit('error', {'message': str(e)})
    
    # Avvia auto-refresh
    auto_refresh_interval = config.get('dashboard', {}).get('auto_refresh', 30)
    dashboard.start_auto_refresh(auto_refresh_interval)
    
    # Cleanup on shutdown
    @app.teardown_appcontext
    def cleanup(error):
        dashboard.stop_auto_refresh()
    
    app.dashboard = dashboard  # Per accesso esterno
    if socketio:
        app.socketio = socketio
    
    return app

if __name__ == "__main__":
    # Test della dashboard
    logging.basicConfig(level=logging.INFO)
    
    # Configurazione di test
    test_config = {
        'dashboard': {
            'port': 5000,
            'host': '0.0.0.0',
            'auto_refresh': 30,
            'debug': True
        }
    }
    
    app = create_app(test_config)
    
    print("🌐 Avvio Dashboard Test...")
    print("🔗 URL: http://localhost:5000")
    
    app.run(
        host=test_config['dashboard']['host'],
        port=test_config['dashboard']['port'],
        debug=test_config['dashboard']['debug']
    )
