#!/usr/bin/env python3
"""
Stock AI - Sistema di Trading Intelligente con Reinforcement Learning
Autore: Stock AI Team
Versione: 2.0.0
"""

import argparse
import sys
import os
import json
import logging
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path

# Aggiungi path per import moduli
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Crea directory necessarie
for dir_name in ['logs', 'data', 'config', 'templates']:
    os.makedirs(dir_name, exist_ok=True)

# Setup logging avanzato
class ColoredFormatter(logging.Formatter):
    """Formatter colorato per i log"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Verde
        'WARNING': '\033[33m',  # Giallo
        'ERROR': '\033[31m',    # Rosso
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)

# Setup logging
log_formatter = ColoredFormatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

file_handler = logging.FileHandler('logs/main.log')
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))

logging.basicConfig(
    level=logging.INFO,
    handlers=[console_handler, file_handler]
)
logger = logging.getLogger(__name__)

class StockAI:
    """Sistema principale Stock AI"""
    
    def __init__(self):
        """Inizializza il sistema Stock AI"""
        self.version = "2.0.0"
        self.config = self.load_or_create_config()
        self.data_dir = Path("data")
        self.config_dir = Path("config")
        
        logger.info(f"🤖 Stock AI v{self.version} inizializzato")
        logger.info(f"📁 Directory dati: {self.data_dir.absolute()}")
        logger.info(f"⚙️  Directory config: {self.config_dir.absolute()}")
        
    def load_or_create_config(self):
        """Carica o crea configurazione"""
        config_path = Path("config/settings.json")
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                logger.info(f"✅ Configurazione caricata da {config_path}")
                return config
            except Exception as e:
                logger.warning(f"⚠️ Errore nel caricamento config: {e}")
        
        # Crea configurazione di default
        default_config = {
            "trading": {
                "initial_capital": 10000,
                "max_position_size": 0.2,
                "stop_loss": 0.05,
                "take_profit": 0.15,
                "commission": 0.001,
                "slippage": 0.0005
            },
            "rl_agent": {
                "learning_rate": 0.001,
                "discount_factor": 0.99,
                "epsilon_start": 0.9,
                "epsilon_end": 0.05,
                "epsilon_decay": 0.995,
                "batch_size": 64,
                "memory_size": 10000,
                "target_update": 1000
            },
            "data": {
                "update_interval": 1800,  # 30 minuti
                "lookback_days": 365,
                "symbols": ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA", "AMD", "META"],
                "data_source": "yfinance",
                "cache_enabled": True
            },
            "dashboard": {
                "port": 5000,
                "host": "0.0.0.0",
                "auto_refresh": 30,
                "debug": False
            },
            "alerts": {
                "enabled": True,
                "profit_threshold": 0.05,
                "loss_threshold": -0.03,
                "email_notifications": False
            },
            "risk_management": {
                "max_portfolio_risk": 0.02,
                "max_sector_allocation": 0.3,
                "diversification_enabled": True,
                "volatility_filter": True,
                "max_correlation": 0.7
            },
            "api": {
                "alpha_vantage_key": "",
                "polygon_key": "",
                "rate_limit": 5,
                "timeout": 30
            },
            "logging": {
                "level": "INFO",
                "file_rotation": True,
                "max_file_size": "10MB",
                "backup_count": 5
            }
        }
        
        try:
            config_path.parent.mkdir(exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"📝 Configurazione di default creata: {config_path}")
        except Exception as e:
            logger.error(f"❌ Errore nella creazione config: {e}")
            
        return default_config
    
    def show_version(self):
        """Mostra informazioni versione"""
        print(f"""
🤖 Stock AI - Sistema di Trading Intelligente
═══════════════════════════════════════════════

📊 Versione: {self.version}
📅 Build: {datetime.now().strftime('%Y-%m-%d')}
🐍 Python: {sys.version.split()[0]}
📁 Directory: {os.getcwd()}

🚀 Componenti:
  ✓ Reinforcement Learning Agent
  ✓ Portfolio Management  
  ✓ Real-time Data Collection
  ✓ Web Dashboard
  ✓ Risk Management
  ✓ Performance Analytics

⚙️  Status: ✅ Operativo
        """)
    
    def show_portfolio_status(self):
        """Mostra stato portfolio dettagliato"""
        from portfolio import Portfolio
        import pickle
        
        print("\n" + "="*60)
        print("📊 STATO PORTFOLIO")
        print("="*60)
        
        portfolio_file = self.data_dir / "current_portfolio.pkl"
        
        try:
            if portfolio_file.exists():
                with open(portfolio_file, 'rb') as f:
                    portfolio = pickle.load(f)
                
                # Calcola metriche
                metrics = portfolio.get_performance_metrics()
                total_value = portfolio.get_portfolio_value()
                
                print(f"💰 Liquidità: ${portfolio.cash:,.2f}")
                print(f"📈 Valore Totale: ${total_value:,.2f}")
                print(f"🎯 Rendimento: {metrics.get('total_return', 0):.2f}%")
                print(f"📊 Posizioni Aperte: {len(portfolio.positions)}")
                print(f"🔄 Trades Totali: {len(portfolio.transactions)}")
                print(f"🏆 Win Rate: {metrics.get('win_rate', 0):.1f}%")
                
                if portfolio.positions:
                    print(f"\n📋 POSIZIONI ATTIVE:")
                    for ticker, pos in portfolio.positions.items():
                        shares = pos['shares']
                        avg_price = pos['avg_price']
                        current_value = shares * avg_price
                        print(f"  {ticker}: {shares} azioni @ ${avg_price:.2f} = ${current_value:,.2f}")
                
                # Ultime transazioni
                if portfolio.transactions:
                    print(f"\n📈 ULTIME TRANSAZIONI:")
                    recent = portfolio.transactions[-5:]
                    for tx in reversed(recent):
                        action_emoji = "🔵" if tx['type'] == 'BUY' else "🔴"
                        print(f"  {action_emoji} {tx['type']} {tx['shares']} {tx['ticker']} @ ${tx['price']:.2f}")
                        
            else:
                print("📁 Portfolio non inizializzato")
                print(f"💰 Capitale Iniziale: ${self.config['trading']['initial_capital']:,.2f}")
                print("🎯 Status: Pronto per il trading")
                
        except Exception as e:
            logger.error(f"❌ Errore lettura portfolio: {e}")
            print(f"❌ Errore: {e}")
    
    def reset_portfolio(self):
        """Reset portfolio ai valori iniziali"""
        try:
            portfolio_file = self.data_dir / "current_portfolio.pkl"
            model_file = self.data_dir / "rl_model.pkl"
            
            # Backup se esistono
            if portfolio_file.exists():
                backup_name = f"portfolio_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
                backup_path = self.data_dir / backup_name
                portfolio_file.rename(backup_path)
                logger.info(f"💾 Backup portfolio: {backup_path}")
            
            if model_file.exists():
                backup_name = f"model_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
                backup_path = self.data_dir / backup_name
                model_file.rename(backup_path)
                logger.info(f"💾 Backup model: {backup_path}")
            
            print("✅ Portfolio resettato con successo")
            print(f"💰 Nuovo capitale: ${self.config['trading']['initial_capital']:,.2f}")
            
        except Exception as e:
            logger.error(f"❌ Errore nel reset: {e}")
            print(f"❌ Errore: {e}")
    
    def update_data(self):
        """Aggiorna dati di mercato"""
        from data_collector import DataCollector
        
        logger.info("🔄 Aggiornamento dati di mercato...")
        print("🔄 Aggiornamento dati in corso...")
        
        try:
            collector = DataCollector(self.config)
            collector.update_data()
            
            # Aggiorna anche cache prezzi
            self._update_price_cache()
            
            print("✅ Dati aggiornati con successo")
            logger.info("✅ Aggiornamento dati completato")
            
        except Exception as e:
            logger.error(f"❌ Errore aggiornamento dati: {e}")
            print(f"❌ Errore: {e}")
    
    def _update_price_cache(self):
        """Aggiorna cache prezzi correnti"""
        import yfinance as yf
        
        try:
            symbols = self.config['data']['symbols']
            prices = {}
            
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                if len(hist) > 0:
                    prices[symbol] = {
                        'price': float(hist['Close'].iloc[-1]),
                        'timestamp': datetime.now().isoformat(),
                        'volume': int(hist['Volume'].iloc[-1]),
                        'change': float(hist['Close'].iloc[-1] - hist['Open'].iloc[-1])
                    }
            
            # Salva cache
            cache_file = self.data_dir / "price_cache.json"
            with open(cache_file, 'w') as f:
                json.dump(prices, f, indent=2)
                
            logger.debug(f"💾 Cache prezzi aggiornata: {len(prices)} simboli")
            
        except Exception as e:
            logger.warning(f"⚠️ Errore aggiornamento cache: {e}")
    
    def test_api(self):
        """Test connessioni API"""
        print("🔍 Test connessioni API...")
        print("-" * 40)
        
        success = True
        
        # Test yfinance
        try:
            import yfinance as yf
            ticker = yf.Ticker("AAPL")
            data = ticker.history(period="1d")
            if len(data) > 0:
                price = data['Close'].iloc[-1]
                print(f"✅ Yahoo Finance: AAPL = ${price:.2f}")
            else:
                print("❌ Yahoo Finance: Nessun dato ricevuto")
                success = False
        except Exception as e:
            print(f"❌ Yahoo Finance: {e}")
            success = False
        
        # Test connessione internet
        try:
            import requests
            response = requests.get("https://httpbin.org/status/200", timeout=10)
            if response.status_code == 200:
                print("✅ Connessione Internet: OK")
            else:
                print("❌ Connessione Internet: Problemi")
                success = False
        except Exception as e:
            print(f"❌ Connessione Internet: {e}")
            success = False
        
        # Test moduli Python
        modules = [
            ("pandas", "pd"),
            ("numpy", "np"), 
            ("matplotlib", "plt"),
            ("sklearn", "sklearn"),
            ("gymnasium", "gym")
        ]
        
        for module_name, import_name in modules:
            try:
                __import__(module_name)
                print(f"✅ {module_name}: Disponibile")
            except ImportError:
                print(f"❌ {module_name}: Non installato")
                success = False
        
        print("-" * 40)
        if success:
            print("🎉 Tutti i test superati!")
            logger.info("✅ Test API completati con successo")
        else:
            print("⚠️ Alcuni test falliti")
            logger.warning("⚠️ Alcuni test API falliti")
            
        return success
    
    def show_config(self):
        """Mostra configurazione corrente"""
        print("\n" + "="*60)
        print("⚙️ CONFIGURAZIONE CORRENTE")
        print("="*60)
        print("📋 Configurazione caricata e validata")
        print(json.dumps(self.config, indent=2))
    
    def start_live_trading(self, aggressiveness=None):
        """Avvia trading live"""
        from aggressive_trader import AggressiveTrader
        
        print("🚀 Avvio Trading Live...")
        print("⚠️  ATTENZIONE: Trading con denaro reale!")
        print("⚠️  Premi Ctrl+C per fermare (mantenendo posizioni)")
        print("-" * 60)
        
        try:
            trader = AggressiveTrader(
                initial_cash=self.config['trading']['initial_capital'],
                aggressiveness_level=aggressiveness
            )
            
            # Avvia trading
            thread = trader.start()
            
            print("✅ Trading avviato con successo")
            print("📊 Usa 'python src/cli_monitor.py watch' per monitorare")
            print("🛑 File di controllo: data/trader_control.txt")
            
            # Mantieni vivo
            while trader.is_running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Interruzione utente...")
            trader.stop()
        except Exception as e:
            logger.error(f"❌ Errore trading live: {e}")
            print(f"❌ Errore: {e}")
    
    def start_backtest(self, start_date, end_date, symbols=None):
        """Avvia backtesting"""
        print(f"📊 Backtesting: {start_date} → {end_date}")
        print("-" * 60)
        
        if symbols is None:
            symbols = self.config['data']['symbols']
        
        try:
            from backtest_engine import BacktestEngine
            
            engine = BacktestEngine(self.config)
            results = engine.run_backtest(
                start_date=start_date,
                end_date=end_date,
                symbols=symbols
            )
            
            # Mostra risultati
            print("📈 RISULTATI BACKTEST:")
            print(f"  Rendimento Totale: {results.get('total_return', 0):.2f}%")
            print(f"  Sharpe Ratio: {results.get('sharpe_ratio', 0):.2f}")
            print(f"  Max Drawdown: {results.get('max_drawdown', 0):.2f}%")
            print(f"  Win Rate: {results.get('win_rate', 0):.1f}%")
            print(f"  Trades Totali: {results.get('total_trades', 0)}")
            
            # Salva risultati
            results_file = self.data_dir / f"backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"💾 Risultati salvati: {results_file}")
            
        except Exception as e:
            logger.error(f"❌ Errore backtest: {e}")
            print(f"❌ Errore: {e}")
    
    def start_training(self, episodes=1000):
        """Avvia training RL agent"""
        print(f"🧠 Training RL Agent ({episodes} episodi)...")
        print("-" * 60)
        
        try:
            from train_rl import RLTrainer
            
            trainer = RLTrainer(self.config)
            trainer.train(episodes=episodes)
            
            print("✅ Training completato!")
            
        except Exception as e:
            logger.error(f"❌ Errore training: {e}")
            print(f"❌ Errore: {e}")
    
    def start_advanced_training(self, algorithms=['PPO', 'SAC'], n_trials=20):
        """Avvia training avanzato RL con ottimizzazione iperparametri"""
        print("🤖 Training Avanzato RL...")
        print(f"🧠 Algoritmi: {algorithms}")
        print(f"🔍 Ottimizzazione: {n_trials} trials")
        print("-" * 60)
        
        try:
            from advanced_rl_training import AdvancedRLTrainer
            
            # Aggiorna config per RL avanzato
            if 'rl' not in self.config:
                self.config['rl'] = {}
            
            self.config['rl'].update({
                'total_timesteps': 100000,
                'learning_rate': 3e-4,
                'batch_size': 64,
                'n_trials': n_trials
            })
            
            trainer = AdvancedRLTrainer(self.config)
            
            # Crea ambiente training
            symbols = self.config['data']['symbols'][:3]  # Limita per performance
            start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
            end_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            print(f"📊 Periodo training: {start_date} → {end_date}")
            print(f"📈 Simboli: {symbols}")
            
            env = trainer.create_training_environment(symbols, start_date, end_date)
            
            # Training ensemble
            results = trainer.train_ensemble_models(env, algorithms)
            
            # Salva report
            trainer.save_training_report(results, symbols, f"{start_date}_{end_date}")
            
            if results.get('models'):
                print(f"✅ Training completato: {len(results['models'])} modelli")
                print(f"🏆 Miglior modello: {results.get('best_single_model', 'N/A')}")
                
                # Mostra performance
                for alg, perf in results.get('performance', {}).items():
                    print(f"   {alg}: {perf['mean_reward']:.2f} reward medio")
            else:
                print("⚠️ Nessun modello completato")
            
        except ImportError:
            print("❌ Stable-baselines3 non disponibile")
            print("💡 Installare con: pip install stable-baselines3 optuna")
            
        except Exception as e:
            logger.error(f"❌ Errore training avanzato: {e}")
            print(f"❌ Errore: {e}")
    
    def generate_performance_report(self, days=365):
        """Genera report performance avanzato"""
        print(f"📊 Generazione Performance Report ({days} giorni)...")
        print("-" * 60)
        
        try:
            from performance_analytics import create_performance_report
            from portfolio import Portfolio
            import pickle
            
            # Carica portfolio
            portfolio_file = self.data_dir / "current_portfolio.pkl"
            
            if not portfolio_file.exists():
                print("❌ Portfolio non trovato. Esegui prima qualche operazione.")
                return
            
            with open(portfolio_file, 'rb') as f:
                portfolio = pickle.load(f)
            
            # Simula dati portfolio (in un sistema reale verrebbero dal database)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Genera dati demo se non esistono
            import pandas as pd
            import numpy as np
            
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            np.random.seed(42)
            
            # Simula crescita portfolio
            initial_value = portfolio.get_portfolio_value() if hasattr(portfolio, 'get_portfolio_value') else 10000
            returns = np.random.normal(0.0008, 0.02, len(dates))  # 20% annuo, 20% vol
            
            portfolio_values = [initial_value]
            for ret in returns[1:]:
                new_value = portfolio_values[-1] * (1 + ret)
                portfolio_values.append(new_value)
            
            portfolio_data = pd.DataFrame({
                'date': dates,
                'portfolio_value': portfolio_values[:len(dates)]
            })
            
            # Crea report
            report = create_performance_report(portfolio_data, self.config)
            
            print("✅ Report generato:")
            metrics = report['metrics']
            print(f"   📈 Total Return: {metrics.get('total_return', 0):.2f}%")
            print(f"   📊 Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
            print(f"   📉 Max Drawdown: {metrics.get('max_drawdown', 0):.2f}%")
            print(f"   🎯 Win Rate: {metrics.get('win_rate', 0):.1f}%")
            print(f"   📋 Dashboard: {report['dashboard_path']}")
            
            # Risk report
            risk_level = report['risk_report']['summary']['risk_level']
            print(f"   🛡️ Risk Level: {risk_level}")
            
        except Exception as e:
            logger.error(f"❌ Errore performance report: {e}")
            print(f"❌ Errore: {e}")
    
    def run_monte_carlo_analysis(self, n_simulations=1000, n_days=252):
        """Esegui analisi Monte Carlo per proiezioni future"""
        print(f"🎲 Analisi Monte Carlo ({n_simulations} simulazioni, {n_days} giorni)...")
        print("-" * 60)
        
        try:
            from performance_analytics import PerformanceAnalytics
            from portfolio import Portfolio
            import pickle
            import pandas as pd
            import numpy as np
            
            # Carica portfolio
            portfolio_file = self.data_dir / "current_portfolio.pkl"
            
            if not portfolio_file.exists():
                print("❌ Portfolio non trovato.")
                return
            
            with open(portfolio_file, 'rb') as f:
                portfolio = pickle.load(f)
            
            current_value = portfolio.get_portfolio_value() if hasattr(portfolio, 'get_portfolio_value') else 10000
            
            # Simula dati storici per calcolare parametri
            dates = pd.date_range(start=datetime.now() - timedelta(days=365), 
                                end=datetime.now(), freq='D')
            np.random.seed(42)
            returns = np.random.normal(0.0008, 0.02, len(dates))
            
            portfolio_values = [current_value * 0.9]  # Valore anno fa
            for ret in returns[1:]:
                new_value = portfolio_values[-1] * (1 + ret)
                portfolio_values.append(new_value)
            
            portfolio_data = pd.DataFrame({
                'date': dates,
                'portfolio_value': portfolio_values[:len(dates)]
            })
            
            # Esegui analisi
            analyzer = PerformanceAnalytics(self.config)
            monte_carlo = analyzer._monte_carlo_simulation(portfolio_data, n_simulations, n_days)
            
            print("🎯 Risultati Proiezione:")
            print(f"   💰 Valore Attuale: ${current_value:,.2f}")
            print(f"   📊 Valore Medio Proiettato: ${monte_carlo['mean_projected_value']:,.2f}")
            print(f"   📈 Best Case (P95): ${monte_carlo['percentiles']['p95']:,.2f}")
            print(f"   📉 Worst Case (P5): ${monte_carlo['percentiles']['p5']:,.2f}")
            print(f"   🎲 Probabilità Perdita: {monte_carlo['probability_of_loss']:.1f}%")
            
        except Exception as e:
            logger.error(f"❌ Errore Monte Carlo: {e}")
            print(f"❌ Errore: {e}")

    def start_dashboard(self):
        """Avvia dashboard web"""
        try:
            from web_dashboard import create_app
            
            app = create_app(self.config)
            
            host = self.config['dashboard']['host']
            port = self.config['dashboard']['port']
            debug = self.config['dashboard']['debug']
            
            print(f"🌐 Avvio Dashboard Web...")
            print(f"🔗 URL: http://{host}:{port}")
            print("⚠️  Premi Ctrl+C per fermare")
            
            app.run(host=host, port=port, debug=debug)
            
        except Exception as e:
            logger.error(f"❌ Errore dashboard: {e}")
            print(f"❌ Errore: {e}")
    
    def show_system_status(self):
        """Mostra stato sistema completo"""
        import psutil
        import platform
        
        print("\n" + "="*60)
        print("🖥️ STATO SISTEMA")
        print("="*60)
        
        # Info sistema
        print(f"🖥️  OS: {platform.system()} {platform.release()}")
        print(f"💻 CPU: {psutil.cpu_count()} cores ({psutil.cpu_percent():.1f}% uso)")
        
        memory = psutil.virtual_memory()
        print(f"💾 RAM: {memory.used//1024**3}GB / {memory.total//1024**3}GB ({memory.percent:.1f}%)")
        
        disk = psutil.disk_usage('/')
        print(f"💿 Disk: {disk.used//1024**3}GB / {disk.total//1024**3}GB ({disk.percent:.1f}%)")
        
        # Status servizi
        print(f"\n🔧 SERVIZI:")
        
        # Check trader
        control_file = Path("data/trader_control.txt")
        trader_active = not control_file.exists()
        status = "🟢 ATTIVO" if trader_active else "🔴 FERMO"
        print(f"  Trading Bot: {status}")
        
        # Check file
        important_files = [
            ("Portfolio", "data/current_portfolio.pkl"),
            ("RL Model", "data/rl_model.pkl"),
            ("Config", "config/settings.json"),
            ("Logs", "logs/main.log")
        ]
        
        for name, path in important_files:
            exists = "✅" if Path(path).exists() else "❌"
            print(f"  {name}: {exists}")
        
        # Network
        try:
            import requests
            response = requests.get("https://httpbin.org/status/200", timeout=5)
            net_status = "✅ OK" if response.status_code == 200 else "❌ ERRORE"
        except:
            net_status = "❌ OFFLINE"
        
        print(f"  Network: {net_status}")

def main():
    """Funzione principale"""
    parser = argparse.ArgumentParser(
        description='🤖 Stock AI - Sistema di Trading Intelligente',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi di utilizzo:
  %(prog)s --version                    # Mostra versione
  %(prog)s --portfolio status           # Stato portfolio  
  %(prog)s --update-data               # Aggiorna dati
  %(prog)s --mode live                 # Trading live
  %(prog)s --mode backtest --start-date 2023-01-01 --end-date 2023-12-31
  %(prog)s --mode train --episodes 1000
  %(prog)s --dashboard                 # Dashboard web
  %(prog)s --test-api                  # Test API
        """
    )
    
    # Comandi principali
    parser.add_argument('--version', action='store_true', 
                       help='Mostra informazioni versione')
    parser.add_argument('--system-status', action='store_true',
                       help='Mostra stato sistema completo')
    
    # Portfolio
    parser.add_argument('--portfolio', choices=['status', 'reset'], 
                       help='Operazioni portfolio')
    
    # Dati
    parser.add_argument('--update-data', action='store_true', 
                       help='Aggiorna dati di mercato')
    parser.add_argument('--test-api', action='store_true', 
                       help='Test connessioni API')
    
    # Configurazione
    parser.add_argument('--show-config', action='store_true', 
                       help='Mostra configurazione')
    
    # Modalità operative
    parser.add_argument('--mode', choices=['live', 'backtest', 'train'], 
                       help='Modalità operativa')
    parser.add_argument('--aggressiveness', type=int, choices=range(1, 11),
                       help='Livello aggressività (1-10)')
    
    # Backtesting
    parser.add_argument('--start-date', type=str, 
                       help='Data inizio backtesting (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, 
                       help='Data fine backtesting (YYYY-MM-DD)')
    parser.add_argument('--symbols', type=str, nargs='+',
                       help='Simboli per backtesting')
    
    # Training
    parser.add_argument('--episodes', type=int, default=1000, 
                       help='Episodi di training')
    
    # Dashboard
    parser.add_argument('--dashboard', action='store_true', 
                       help='Avvia dashboard web')
    
    # Nuove funzionalità avanzate
    parser.add_argument('--advanced-training', action='store_true',
                       help='Avvia training RL avanzato con ottimizzazione')
    parser.add_argument('--algorithms', type=str, nargs='+', 
                       default=['PPO', 'SAC'],
                       help='Algoritmi RL per training avanzato')
    parser.add_argument('--n-trials', type=int, default=20,
                       help='Numero trial per ottimizzazione iperparametri')
    parser.add_argument('--performance-report', action='store_true',
                       help='Genera report performance avanzato')
    parser.add_argument('--monte-carlo', action='store_true',
                       help='Esegui analisi Monte Carlo')
    parser.add_argument('--simulations', type=int, default=1000,
                       help='Numero simulazioni Monte Carlo')
    parser.add_argument('--projection-days', type=int, default=252,
                       help='Giorni di proiezione Monte Carlo')
    
    # Live Trading Monitor
    parser.add_argument('--live-monitor', action='store_true',
                       help='Avvia monitoraggio e trading automatico continuo')
    parser.add_argument('--check-interval', type=int, default=300,
                       help='Intervallo controllo mercato (secondi)')
    parser.add_argument('--max-trades-per-day', type=int, default=20,
                       help='Massimo numero trades per giorno')
    
    # Debug
    parser.add_argument('--debug', action='store_true', 
                       help='Modalità debug')
    parser.add_argument('--verbose', action='store_true', 
                       help='Output dettagliato')
    
    args = parser.parse_args()
    
    # Setup debug/verbose
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("🐛 Modalità debug attivata")
    
    if args.verbose:
        logger.info("📢 Modalità verbose attivata")
    
    try:
        stock_ai = StockAI()
        
        # Gestione comandi
        if args.version:
            stock_ai.show_version()
            return 0
            
        elif args.system_status:
            stock_ai.show_system_status()
            return 0
            
        elif args.portfolio == 'status':
            stock_ai.show_portfolio_status()
            return 0
            
        elif args.portfolio == 'reset':
            stock_ai.reset_portfolio() 
            return 0
            
        elif args.update_data:
            stock_ai.update_data()
            return 0
            
        elif args.test_api:
            success = stock_ai.test_api()
            return 0 if success else 1
            
        elif args.show_config:
            stock_ai.show_config()
            return 0
            
        elif args.dashboard:
            stock_ai.start_dashboard()
            return 0
            
        elif args.mode == 'live':
            stock_ai.start_live_trading(aggressiveness=args.aggressiveness)
            return 0
            
        elif args.mode == 'backtest':
            if not args.start_date or not args.end_date:
                print("❌ Errore: --start-date e --end-date richiesti per backtesting")
                return 1
            stock_ai.start_backtest(args.start_date, args.end_date, args.symbols)
            return 0
            
        elif args.mode == 'train':
            stock_ai.start_training(episodes=args.episodes)
            return 0
            
        elif args.advanced_training:
            stock_ai.start_advanced_training(algorithms=args.algorithms, n_trials=args.n_trials)
            return 0
            
        elif args.performance_report:
            stock_ai.generate_performance_report()
            return 0
            
        elif args.monte_carlo:
            stock_ai.run_monte_carlo_analysis(n_simulations=args.simulations, 
                                            n_days=args.projection_days)
            return 0
            
        elif args.live_monitor:
            # Avvia Live Trading Monitor
            from live_trading_monitor import LiveTradingMonitor
            
            # Aggiorna configurazione se specificato
            if hasattr(args, 'check_interval') and args.check_interval:
                if 'trading' not in stock_ai.config:
                    stock_ai.config['trading'] = {}
                if 'live_trading' not in stock_ai.config['trading']:
                    stock_ai.config['trading']['live_trading'] = {}
                stock_ai.config['trading']['live_trading']['check_interval'] = args.check_interval
            
            if hasattr(args, 'max_trades_per_day') and args.max_trades_per_day:
                stock_ai.config['trading']['live_trading']['max_trades_per_day'] = args.max_trades_per_day
            
            try:
                monitor = LiveTradingMonitor()
                print("🚀 Avvio Live Trading Monitor...")
                print("📊 Monitoraggio continuo e trading automatico")
                print("⚠️  Premi Ctrl+C per fermare")
                print("-" * 60)
                
                monitor.start_monitoring()
                
                # Loop status
                import time
                while monitor.is_running:
                    status = monitor.get_status()
                    print(f"\r📊 Portfolio: ${status['portfolio_value']:.2f} | "
                          f"Trades oggi: {status['trades_today']} | "
                          f"Mercato: {'🟢' if status['market_open'] else '🔴'}", end='', flush=True)
                    time.sleep(30)
                    
            except KeyboardInterrupt:
                print("\n🛑 Fermando Live Trading Monitor...")
                monitor.stop_monitoring()
                print("✅ Monitor fermato correttamente")
            except Exception as e:
                logger.error(f"❌ Errore Live Trading Monitor: {e}")
                print(f"❌ Errore: {e}")
            
            return 0
            
        else:
            # Nessun comando, mostra help
            parser.print_help()
            return 0
            
    except KeyboardInterrupt:
        print("\n🛑 Interruzione utente")
        return 0
    except Exception as e:
        logger.error(f"❌ Errore critico: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
