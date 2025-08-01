#!/usr/bin/env python3
"""
Yahoo Finance API v8 - Direct API Access
Accesso diretto alle nuove API v8 di Yahoo Finance
"""

import requests
import pandas as pd
import numpy as np
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import json

logger = logging.getLogger(__name__)

class YahooFinanceV8:
    """Client per le nuove API v8 di Yahoo Finance"""
    
    def __init__(self):
        self.base_url = "https://query2.finance.yahoo.com/v8/finance/chart"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.5  # 500ms tra richieste
        
        logger.info("🔧 Yahoo Finance v8 API client inizializzato")
    
    def _wait_for_rate_limit(self):
        """Gestione rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _period_to_timestamps(self, period: str) -> tuple:
        """Converte periodo in timestamp Unix"""
        end_time = int(time.time())
        
        period_map = {
            '1d': 1,
            '5d': 5, 
            '1mo': 30,
            '3mo': 90,
            '6mo': 180,
            '1y': 365,
            '2y': 730,
            '5y': 1825,
            '10y': 3650,
            'max': 7300  # ~20 anni
        }
        
        days = period_map.get(period, 365)
        start_time = end_time - (days * 24 * 60 * 60)
        
        return start_time, end_time
    
    def _interval_to_str(self, interval: str) -> str:
        """Converte intervallo in formato API"""
        interval_map = {
            '1m': '1m',
            '2m': '2m', 
            '5m': '5m',
            '15m': '15m',
            '30m': '30m',
            '60m': '1h',
            '90m': '90m',
            '1h': '1h',
            '1d': '1d',
            '5d': '5d',
            '1wk': '1wk',
            '1mo': '1mo',
            '3mo': '3mo'
        }
        
        return interval_map.get(interval, '1d')
    
    def get_stock_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> Optional[pd.DataFrame]:
        """
        Ottiene dati storici usando le API v8 di Yahoo Finance
        
        Args:
            symbol (str): Simbolo ticker (es. AAPL)
            period (str): Periodo dati 
            interval (str): Intervallo dati
            
        Returns:
            pd.DataFrame: Dati OHLCV o None se errore
        """
        try:
            self._wait_for_rate_limit()
            
            # Converte parametri
            start_time, end_time = self._period_to_timestamps(period)
            api_interval = self._interval_to_str(interval)
            
            # Costruisce URL
            url = f"{self.base_url}/{symbol}"
            params = {
                'period1': start_time,
                'period2': end_time,
                'interval': api_interval,
                'events': 'history',
                'includeAdjustedClose': 'true'
            }
            
            logger.debug(f"📡 Request: {url} con parametri {params}")
            
            # Effettua richiesta
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            # Parse JSON
            data = response.json()
            
            if 'chart' not in data or not data['chart']['result']:
                logger.warning(f"⚠️ Nessun dato per {symbol}")
                return None
            
            result = data['chart']['result'][0]
            
            # Estrae dati
            timestamps = result['timestamp']
            quotes = result['indicators']['quote'][0]
            # Validazione dati base
            quotes = result['indicators']['quote'][0]
            if not quotes.get('close') or len(quotes['close']) == 0:
                logger.error(f"❌ Dati 'close' mancanti per {symbol}")
                return None
            
            # Crea DataFrame
            df_data = {
                'Open': quotes['open'],
                'High': quotes['high'], 
                'Low': quotes['low'],
                'Close': quotes['close'],
                'Volume': quotes['volume']
            }
            
            # Aggiunge Adj Close se disponibile
            if 'adjclose' in result['indicators']:
                df_data['Adj Close'] = result['indicators']['adjclose'][0]['adjclose']
            else:
                df_data['Adj Close'] = quotes['close']
            
            # Converte timestamp in datetime
            dates = [datetime.fromtimestamp(ts) for ts in timestamps]
            
            # Crea DataFrame
            df = pd.DataFrame(df_data, index=dates)
            
            # Rimuove valori null
            df.dropna(inplace=True)
            
            # Standardizza nomi colonne (maiuscole)
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']
            
            logger.info(f"✅ Dati v8 API per {symbol}: {len(df)} righe")
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Errore richiesta API per {symbol}: {e}")
            return None
        except KeyError as e:
            logger.error(f"❌ Errore parsing dati per {symbol}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Errore generico per {symbol}: {e}")
            return None
    
    def get_multiple_stocks(self, symbols: List[str], period: str = "1y", interval: str = "1d") -> Dict[str, pd.DataFrame]:
        """
        Ottiene dati per multipli simboli
        
        Args:
            symbols: Lista simboli
            period: Periodo dati
            interval: Intervallo dati
            
        Returns:
            Dict con symbol -> DataFrame
        """
        results = {}
        
        for symbol in symbols:
            try:
                data = self.get_stock_data(symbol, period, interval)
                if data is not None and not data.empty:
                    results[symbol] = data
                    logger.info(f"✅ {symbol}: {len(data)} righe")
                else:
                    logger.warning(f"⚠️ {symbol}: nessun dato")
                    
            except Exception as e:
                logger.error(f"❌ Errore {symbol}: {e}")
        
        logger.info(f"📊 Completato: {len(results)}/{len(symbols)} simboli")
        return results
    
    def test_connection(self) -> bool:
        """Testa connessione API"""
        try:
            test_data = self.get_stock_data('AAPL', period='5d')
            if test_data is not None and not test_data.empty:
                logger.info("✅ Test connessione API riuscito")
                return True
            else:
                logger.warning("⚠️ Test connessione: nessun dato")
                return False
        except Exception as e:
            logger.error(f"❌ Test connessione fallito: {e}")
            return False

# Istanza globale
yahoo_v8 = YahooFinanceV8()
