#!/usr/bin/env python3
"""
Data Collector - Sistema di raccolta dati finanziari avanzato
Gestisce la raccolta, pulizia e caching dei dati di mercato
"""

import yfinance as yf
import pandas as pd
import numpy as np
import logging
import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import pickle
import requests
from typing import Dict, List, Optional, Union
import warnings

# Ignora warning di pandas
warnings.filterwarnings('ignore', category=pd.errors.PerformanceWarning)

logger = logging.getLogger(__name__)

class DataCollector:
    """Raccoglitore di dati finanziari con cache e gestione errori avanzata"""
    
    def __init__(self, config):
        self.config = config
        self.symbols = config['data']['symbols']
        self.lookback_days = config['data']['lookback_days']
        self.data_dir = Path("data")
        self.cache_dir = self.data_dir / "cache"
        
        # Crea directory se non esistono
        self.data_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.2  # 200ms tra richieste
        
        # Cache settings
        self.cache_enabled = config['data'].get('cache_enabled', True)
        self.cache_duration = 300  # 5 minuti
        
        logger.info(f"🔧 DataCollector inizializzato per {len(self.symbols)} simboli")
        
    def _wait_for_rate_limit(self):
        """Gestione rate limiting per evitare ban API"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _get_cache_filename(self, symbol: str, period: str, interval: str = "1d") -> Path:
        """Genera nome file cache"""
        return self.cache_dir / f"{symbol}_{period}_{interval}.pkl"
    
    def _is_cache_valid(self, cache_file: Path) -> bool:
        """Controlla se cache è ancora valida"""
        if not cache_file.exists():
            return False
            
        try:
            stat = cache_file.stat()
            age = time.time() - stat.st_mtime
            return age < self.cache_duration
        except:
            return False
    
    def _save_to_cache(self, data: pd.DataFrame, cache_file: Path):
        """Salva dati in cache"""
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump({
                    'data': data,
                    'timestamp': datetime.now(),
                    'version': '1.0'
                }, f)
            logger.debug(f"💾 Cache salvata: {cache_file.name}")
        except Exception as e:
            logger.warning(f"⚠️ Errore salvataggio cache {cache_file}: {e}")
    
    def _load_from_cache(self, cache_file: Path) -> Optional[pd.DataFrame]:
        """Carica dati da cache"""
        try:
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            data = cache_data['data']
            timestamp = cache_data['timestamp']
            
            logger.debug(f"📦 Cache caricata: {cache_file.name} ({timestamp})")
            return data
            
        except Exception as e:
            logger.warning(f"⚠️ Errore caricamento cache {cache_file}: {e}")
            return None
    
    def get_stock_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> Optional[pd.DataFrame]:
        """
        Ottiene dati storici per un singolo titolo con cache
        
        Args:
            symbol (str): Simbolo ticker (es. AAPL)
            period (str): Periodo dati (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval (str): Intervallo dati (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            pd.DataFrame: Dati OHLCV o None se errore
        """
        cache_file = self._get_cache_filename(symbol, period, interval)
        
        # Prova cache se abilitata
        if self.cache_enabled and self._is_cache_valid(cache_file):
            cached_data = self._load_from_cache(cache_file)
            if cached_data is not None:
                return cached_data
        
        # Rate limiting
        self._wait_for_rate_limit()
        
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                logger.warning(f"⚠️ Nessun dato per {symbol}")
                return None
            
            # Pulizia dati
            data = self._clean_data(data, symbol)
            
            # Salva in cache
            if self.cache_enabled:
                self._save_to_cache(data, cache_file)
            
            logger.debug(f"✅ Dati ottenuti per {symbol}: {len(data)} righe")
            return data
            
        except Exception as e:
            logger.error(f"❌ Errore nel recupero dati per {symbol}: {e}")
            return None
    
    def _clean_data(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Pulisce e valida i dati
        
        Args:
            data (pd.DataFrame): Dati grezzi
            symbol (str): Simbolo per logging
            
        Returns:
            pd.DataFrame: Dati puliti
        """
        original_len = len(data)
        
        # Rimuovi righe con valori nulli
        data = data.dropna()
        
        # Rimuovi outlier (prezzi negativi o zero)
        data = data[(data['Close'] > 0) & (data['Volume'] >= 0)]
        
        # Rimuovi spike irragionevoli (cambio > 50% in un giorno)
        if len(data) > 1:
            price_change = data['Close'].pct_change().abs()
            data = data[price_change < 0.5]
        
        cleaned_len = len(data)
        
        if cleaned_len < original_len:
            logger.debug(f"🧹 Pulizia {symbol}: {original_len} → {cleaned_len} righe")
        
        return data
    
    def get_multiple_stocks(self, symbols: List[str], period: str = "1y") -> Dict[str, pd.DataFrame]:
        """
        Ottiene dati per multipli titoli
        
        Args:
            symbols (List[str]): Lista simboli
            period (str): Periodo dati
            
        Returns:
            Dict[str, pd.DataFrame]: Dizionario simbolo -> dati
        """
        data = {}
        total = len(symbols)
        
        logger.info(f"📊 Raccolta dati per {total} simboli...")
        
        for i, symbol in enumerate(symbols, 1):
            try:
                stock_data = self.get_stock_data(symbol, period)
                if stock_data is not None and not stock_data.empty:
                    data[symbol] = stock_data
                    logger.info(f"✅ {i}/{total} - {symbol}: {len(stock_data)} righe")
                else:
                    logger.warning(f"⚠️ {i}/{total} - {symbol}: Nessun dato")
                    
            except Exception as e:
                logger.error(f"❌ {i}/{total} - {symbol}: {e}")
                
            # Piccola pausa tra richieste
            if i < total:
                time.sleep(0.1)
        
        logger.info(f"📈 Raccolti dati per {len(data)}/{total} simboli")
        return data
    
    def get_current_prices(self, symbols: List[str] = None) -> Dict[str, Dict]:
        """
        Ottiene prezzi correnti per i simboli
        
        Args:
            symbols (List[str]): Lista simboli (default: self.symbols)
            
        Returns:
            Dict[str, Dict]: Prezzi correnti con metadati
        """
        if symbols is None:
            symbols = self.symbols
        
        prices = {}
        
        logger.debug(f"💰 Recupero prezzi correnti per {len(symbols)} simboli...")
        
        for symbol in symbols:
            try:
                # Prova prima con dati intraday
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d", interval="1m")
                
                if not hist.empty:
                    current_price = float(hist['Close'].iloc[-1])
                    volume = int(hist['Volume'].iloc[-1])
                    
                    # Calcola variazione giornaliera
                    day_data = ticker.history(period="2d")
                    if len(day_data) >= 2:
                        prev_close = float(day_data['Close'].iloc[-2])
                        daily_change = current_price - prev_close
                        daily_change_pct = (daily_change / prev_close) * 100
                    else:
                        daily_change = 0
                        daily_change_pct = 0
                    
                    prices[symbol] = {
                        'price': current_price,
                        'volume': volume,
                        'daily_change': daily_change,
                        'daily_change_pct': daily_change_pct,
                        'timestamp': datetime.now().isoformat(),
                        'source': 'yfinance'
                    }
                    
                    logger.debug(f"💲 {symbol}: ${current_price:.2f} ({daily_change_pct:+.1f}%)")
                
            except Exception as e:
                logger.warning(f"⚠️ Errore prezzo {symbol}: {e}")
                
            # Rate limiting
            time.sleep(0.1)
        
        logger.info(f"💰 Prezzi ottenuti per {len(prices)}/{len(symbols)} simboli")
        return prices
    
    def get_market_data(self, symbol: str) -> Dict:
        """
        Ottiene dati di mercato completi per un simbolo
        
        Args:
            symbol (str): Simbolo ticker
            
        Returns:
            Dict: Dati completi del titolo
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Info generale
            info = ticker.info
            
            # Dati storici
            hist = ticker.history(period="1mo")
            
            # Calcola metriche
            if not hist.empty:
                current_price = float(hist['Close'].iloc[-1])
                avg_volume = int(hist['Volume'].mean())
                volatility = float(hist['Close'].pct_change().std() * np.sqrt(252))
                
                # Support e resistance (semplificati)
                high_52w = float(hist['High'].max())
                low_52w = float(hist['Low'].min())
                
                # RSI (semplificato)
                delta = hist['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                current_rsi = float(rsi.iloc[-1]) if not rsi.empty else 50
                
                market_data = {
                    'symbol': symbol,
                    'name': info.get('longName', symbol),
                    'sector': info.get('sector', 'Unknown'),
                    'industry': info.get('industry', 'Unknown'),
                    'current_price': current_price,
                    'market_cap': info.get('marketCap', 0),
                    'pe_ratio': info.get('trailingPE', 0),
                    'dividend_yield': info.get('dividendYield', 0),
                    'avg_volume': avg_volume,
                    'volatility': volatility,
                    'high_52w': high_52w,
                    'low_52w': low_52w,
                    'rsi': current_rsi,
                    'timestamp': datetime.now().isoformat()
                }
                
                return market_data
            
        except Exception as e:
            logger.error(f"❌ Errore dati mercato {symbol}: {e}")
        
        return {}
    
    def update_data(self):
        """Aggiorna tutti i dati di mercato"""
        logger.info("🔄 Inizio aggiornamento dati completo...")
        
        try:
            # Aggiorna dati storici
            historical_data = self.get_multiple_stocks(self.symbols, "1y")
            
            # Salva dati storici
            for symbol, data in historical_data.items():
                file_path = self.data_dir / f"{symbol}_historical.csv"
                data.to_csv(file_path)
                logger.debug(f"💾 Salvato {symbol} storico: {file_path}")
            
            # Aggiorna prezzi correnti
            current_prices = self.get_current_prices()
            
            # Salva cache prezzi
            price_cache_file = self.data_dir / "price_cache.json"
            with open(price_cache_file, 'w') as f:
                json.dump(current_prices, f, indent=2)
            
            # Aggiorna dati di mercato completi
            market_data = {}
            for symbol in self.symbols:
                market_data[symbol] = self.get_market_data(symbol)
            
            # Salva dati mercato
            market_file = self.data_dir / "market_data.json"
            with open(market_file, 'w') as f:
                json.dump(market_data, f, indent=2)
            
            # Statistiche aggiornamento
            summary = {
                'timestamp': datetime.now().isoformat(),
                'symbols_updated': len(historical_data),
                'total_symbols': len(self.symbols),
                'prices_updated': len(current_prices),
                'success_rate': len(historical_data) / len(self.symbols) * 100
            }
            
            summary_file = self.data_dir / "update_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"✅ Aggiornamento completato: {summary['success_rate']:.1f}% successo")
            
        except Exception as e:
            logger.error(f"❌ Errore aggiornamento dati: {e}")
            raise
    
    def get_technical_indicators(self, symbol: str, period: str = "3mo") -> Dict:
        """
        Calcola indicatori tecnici per un simbolo
        
        Args:
            symbol (str): Simbolo ticker
            period (str): Periodo dati
            
        Returns:
            Dict: Indicatori tecnici
        """
        try:
            data = self.get_stock_data(symbol, period)
            if data is None or data.empty:
                return {}
            
            # Moving averages
            data['SMA_20'] = data['Close'].rolling(window=20).mean()
            data['SMA_50'] = data['Close'].rolling(window=50).mean()
            data['EMA_12'] = data['Close'].ewm(span=12).mean()
            data['EMA_26'] = data['Close'].ewm(span=26).mean()
            
            # MACD
            data['MACD'] = data['EMA_12'] - data['EMA_26']
            data['MACD_Signal'] = data['MACD'].ewm(span=9).mean()
            
            # Bollinger Bands
            data['BB_Middle'] = data['Close'].rolling(window=20).mean()
            bb_std = data['Close'].rolling(window=20).std()
            data['BB_Upper'] = data['BB_Middle'] + (bb_std * 2)
            data['BB_Lower'] = data['BB_Middle'] - (bb_std * 2)
            
            # RSI
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data['RSI'] = 100 - (100 / (1 + rs))
            
            # Ultimi valori
            latest = data.iloc[-1]
            
            indicators = {
                'sma_20': float(latest['SMA_20']) if pd.notna(latest['SMA_20']) else None,
                'sma_50': float(latest['SMA_50']) if pd.notna(latest['SMA_50']) else None,
                'macd': float(latest['MACD']) if pd.notna(latest['MACD']) else None,
                'macd_signal': float(latest['MACD_Signal']) if pd.notna(latest['MACD_Signal']) else None,
                'rsi': float(latest['RSI']) if pd.notna(latest['RSI']) else None,
                'bb_upper': float(latest['BB_Upper']) if pd.notna(latest['BB_Upper']) else None,
                'bb_middle': float(latest['BB_Middle']) if pd.notna(latest['BB_Middle']) else None,
                'bb_lower': float(latest['BB_Lower']) if pd.notna(latest['BB_Lower']) else None,
                'current_price': float(latest['Close']),
                'volume': int(latest['Volume']),
                'timestamp': datetime.now().isoformat()
            }
            
            return indicators
            
        except Exception as e:
            logger.error(f"❌ Errore calcolo indicatori {symbol}: {e}")
            return {}
    
    def cleanup_old_cache(self, days: int = 7):
        """
        Rimuove file cache vecchi
        
        Args:
            days (int): Giorni dopo cui rimuovere cache
        """
        try:
            cutoff_time = time.time() - (days * 24 * 3600)
            removed = 0
            
            for cache_file in self.cache_dir.glob("*.pkl"):
                if cache_file.stat().st_mtime < cutoff_time:
                    cache_file.unlink()
                    removed += 1
            
            if removed > 0:
                logger.info(f"🧹 Rimossi {removed} file cache vecchi")
                
        except Exception as e:
            logger.warning(f"⚠️ Errore pulizia cache: {e}")

# Funzione di compatibilità per codice esistente
def get_stock_data(symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
    """
    Funzione wrapper per compatibilità con codice esistente
    
    Args:
        symbol (str): Simbolo ticker
        period (str): Periodo dati
        
    Returns:
        pd.DataFrame: Dati storici o None
    """
    # Configurazione di default semplice
    simple_config = {
        'data': {
            'symbols': [symbol],
            'lookback_days': 365,
            'cache_enabled': True
        }
    }
    
    collector = DataCollector(simple_config)
    return collector.get_stock_data(symbol, period)

if __name__ == "__main__":
    # Test del modulo
    logging.basicConfig(level=logging.INFO)
    
    # Configurazione di test
    test_config = {
        'data': {
            'symbols': ['AAPL', 'GOOGL'],
            'lookback_days': 30,
            'cache_enabled': True
        }
    }
    
    collector = DataCollector(test_config)
    
    # Test raccolta dati
    print("🧪 Test DataCollector...")
    
    # Test singolo simbolo
    data = collector.get_stock_data('AAPL', '1mo')
    if data is not None:
        print(f"✅ AAPL: {len(data)} righe")
    
    # Test prezzi correnti
    prices = collector.get_current_prices(['AAPL'])
    if prices:
        print(f"✅ Prezzi: {prices}")
    
    # Test indicatori tecnici
    indicators = collector.get_technical_indicators('AAPL')
    if indicators:
        print(f"✅ Indicatori: RSI={indicators.get('rsi', 'N/A'):.1f}")
    
    print("🎉 Test completato!")
