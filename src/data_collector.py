import yfinance as yf
import pandas as pd
import numpy as np
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self, config):
        self.config = config
        self.symbols = config['data']['symbols']
        self.lookback_days = config['data']['lookback_days']
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
    def get_historical_data(self, start_date, end_date):
        """Fetch historical data for given date range"""
        logger.info(f"Fetching historical data from {start_date} to {end_date}")
        
        data = {}
        for symbol in self.symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(start=start_date, end=end_date)
                data[symbol] = hist
                logger.debug(f"Fetched {len(hist)} records for {symbol}")
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {e}")
                
        return data
    
    def update_data(self):
        """Update market data"""
        logger.info("Updating market data...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.lookback_days)
        
        data = self.get_historical_data(start_date, end_date)
        
        # Save to CSV
        for symbol, df in data.items():
            file_path = self.data_dir / f"{symbol}_data.csv"
            df.to_csv(file_path)
            logger.debug(f"Saved {symbol} data to {file_path}")
            
        # Save combined data
        combined_file = self.data_dir / "stock_data.csv"
        if data:
            combined_df = pd.concat([df.assign(Symbol=symbol) for symbol, df in data.items()])
            combined_df.to_csv(combined_file)
            logger.info(f"Saved combined data to {combined_file}")
            
        return data
    
    def get_current_state(self):
        """Get current market state for RL agent"""
        current_data = {}
        
        for symbol in self.symbols:
            try:
                ticker = yf.Ticker(symbol)
                # Get recent data for technical indicators
                hist = ticker.history(period="1mo")
                
                if not hist.empty:
                    # Calculate technical indicators
                    indicators = self.calculate_technical_indicators(hist)
                    current_data[symbol] = indicators
                    
            except Exception as e:
                logger.error(f"Error getting current state for {symbol}: {e}")
                
        return current_data
    
    def calculate_technical_indicators(self, data):
        """Calculate technical indicators"""
        indicators = {}
        
        # Price data
        indicators['close'] = data['Close'].iloc[-1]
        indicators['open'] = data['Open'].iloc[-1]
        indicators['high'] = data['High'].iloc[-1]
        indicators['low'] = data['Low'].iloc[-1]
        indicators['volume'] = data['Volume'].iloc[-1]
        
        # Moving averages
        indicators['sma_5'] = data['Close'].rolling(5).mean().iloc[-1]
        indicators['sma_10'] = data['Close'].rolling(10).mean().iloc[-1]
        indicators['sma_20'] = data['Close'].rolling(20).mean().iloc[-1]
        
        # RSI
        indicators['rsi'] = self.calculate_rsi(data['Close']).iloc[-1]
        
        # MACD
        macd_line, signal_line = self.calculate_macd(data['Close'])
        indicators['macd'] = macd_line.iloc[-1]
        indicators['macd_signal'] = signal_line.iloc[-1]
        
        # Bollinger Bands
        bb_upper, bb_lower = self.calculate_bollinger_bands(data['Close'])
        indicators['bb_upper'] = bb_upper.iloc[-1]
        indicators['bb_lower'] = bb_lower.iloc[-1]
        
        # Price changes
        indicators['price_change_1d'] = (data['Close'].iloc[-1] / data['Close'].iloc[-2] - 1) if len(data) > 1 else 0
        indicators['price_change_5d'] = (data['Close'].iloc[-1] / data['Close'].iloc[-6] - 1) if len(data) > 5 else 0
        
        return indicators
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices):
        """Calculate MACD"""
        exp1 = prices.ewm(span=12).mean()
        exp2 = prices.ewm(span=26).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=9).mean()
        return macd_line, signal_line
    
    def calculate_bollinger_bands(self, prices, period=20):
        """Calculate Bollinger Bands"""
        sma = prices.rolling(period).mean()
        std = prices.rolling(period).std()
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)
        return upper_band, lower_band
    
    def get_training_data(self):
        """Get data for training RL agent"""
        logger.info("Preparing training data...")
        
        try:
            # Load existing data or fetch new
            combined_file = self.data_dir / "stock_data.csv"
            if combined_file.exists() and combined_file.stat().st_size > 0:
                data = pd.read_csv(combined_file, index_col=0, parse_dates=True)
                if not data.empty:
                    return data
                    
            # If no existing data, update first
            logger.info("No existing data found, fetching new data...")
            self.update_data()
            
            if combined_file.exists() and combined_file.stat().st_size > 0:
                data = pd.read_csv(combined_file, index_col=0, parse_dates=True)
                return data
            else:
                logger.error("Failed to fetch training data")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            return pd.DataFrame()
    
    def test_connection(self):
        """Test API connection"""
        try:
            ticker = yf.Ticker("AAPL")
            info = ticker.info
            return True
        except:
            return False
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        temp_files = list(self.data_dir.glob("*.tmp"))
        for file in temp_files:
            file.unlink()
        logger.info(f"Cleaned up {len(temp_files)} temporary files")
