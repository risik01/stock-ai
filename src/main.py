import argparse
import sys
import os
import json
import logging
from datetime import datetime
from pathlib import Path

# Create necessary directories first
for dir_name in ['logs', 'data', 'config', 'src']:
    os.makedirs(dir_name, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StockAI:
    def __init__(self):
        self.config = self.create_default_config()
        logger.info("StockAI initialized successfully")
        
    def create_default_config(self):
        """Create and return default configuration"""
        default_config = {
            "trading": {
                "initial_capital": 10000,
                "max_position_size": 0.2,
                "stop_loss": 0.05,
                "take_profit": 0.1
            },
            "rl_agent": {
                "learning_rate": 0.1,
                "discount_factor": 0.95,
                "epsilon": 0.1,
                "batch_size": 32
            },
            "data": {
                "update_interval": 3600,
                "lookback_days": 365,
                "symbols": ["AAPL", "GOOGL", "MSFT", "TSLA"]
            }
        }
        
        # Save config file
        config_path = Path("config/settings.json")
        try:
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created config file: {config_path}")
        except Exception as e:
            logger.warning(f"Could not save config: {e}")
            
        return default_config
    
    def show_portfolio_status(self):
        """Show basic portfolio status"""
        print("\n=== PORTFOLIO STATUS ===")
        print(f"Cash: ${self.config['trading']['initial_capital']:.2f}")
        print(f"Symbols: {', '.join(self.config['data']['symbols'])}")
        print("Status: Initialized")
        
    def update_data(self):
        """Simulate data update"""
        logger.info("Data update requested")
        print("✅ Data update simulated successfully")
        
    def test_api(self):
        """Test API connections"""
        try:
            import yfinance as yf
            ticker = yf.Ticker("AAPL")
            info = ticker.info
            logger.info("✅ API connection test successful")
            return True
        except Exception as e:
            logger.error(f"❌ API connection test failed: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Stock AI Trading System')
    
    parser.add_argument('--version', action='store_true', help='Show version')
    parser.add_argument('--portfolio', choices=['status', 'reset'], help='Portfolio operations')
    parser.add_argument('--update-data', action='store_true', help='Update market data')
    parser.add_argument('--test-api', action='store_true', help='Test API connections')
    parser.add_argument('--show-config', action='store_true', help='Show configuration')
    parser.add_argument('--mode', choices=['live', 'backtest', 'train'], help='Trading mode')
    parser.add_argument('--episodes', type=int, default=100, help='Training episodes')
    parser.add_argument('--start-date', type=str, help='Start date for backtesting')
    parser.add_argument('--end-date', type=str, help='End date for backtesting')
    
    args = parser.parse_args()
    
    try:
        stock_ai = StockAI()
        
        if args.version:
            print("Stock AI Trading System v1.0.0")
            print("Status: Development")
            return 0
            
        elif args.portfolio == 'status':
            stock_ai.show_portfolio_status()
            
        elif args.update_data:
            stock_ai.update_data()
            
        elif args.test_api:
            success = stock_ai.test_api()
            return 0 if success else 1
            
        elif args.show_config:
            print(json.dumps(stock_ai.config, indent=2))
            
        elif args.mode == 'train':
            logger.info(f"Training mode requested with {args.episodes} episodes")
            print(f"🔄 Training simulation with {args.episodes} episodes")
            print("✅ Training completed (simulated)")
            
        elif args.mode == 'backtest':
            if not args.start_date or not args.end_date:
                print("❌ Error: --start-date and --end-date required for backtesting")
                return 1
            logger.info(f"Backtesting from {args.start_date} to {args.end_date}")
            print(f"📊 Backtesting from {args.start_date} to {args.end_date}")
            print("✅ Backtest completed (simulated)")
            
        else:
            parser.print_help()
            
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())