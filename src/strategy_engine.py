#!/usr/bin/env python3
"""
Strategy Engine - Motore di strategie di trading
Analisi tecnica e generazione segnali di trading
"""

import pandas as pd
import numpy as np
import json
import logging
from typing import Dict, List, Optional
import ta

logger = logging.getLogger(__name__)

class StrategyEngine:
    """Motore di strategie per analisi tecnica"""
    
    def __init__(self, config_path: str = "config/production_settings.json"):
        """Inizializza il motore di strategie"""
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path: str) -> Dict:
        """Carica configurazione"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Errore caricamento config: {e}")
            return {}
    
    def analyze_symbol(self, symbol: str, data: pd.DataFrame) -> Dict:
        """Analizza un simbolo e genera segnali"""
        try:
            if data is None or data.empty or len(data) < 50:
                return {'recommendation': 'HOLD', 'confidence': 0.0, 'signals': []}
            
            # Calcola indicatori tecnici
            indicators = self._calculate_indicators(data)
            
            # Genera segnali
            signals = self._generate_signals(indicators)
            
            # Combina segnali per raccomandazione finale
            recommendation = self._combine_signals(signals)
            
            return {
                'recommendation': recommendation['action'],
                'confidence': recommendation['confidence'],
                'signals': signals,
                'indicators': indicators
            }
            
        except Exception as e:
            logger.error(f"Errore analisi {symbol}: {e}")
            return {'recommendation': 'HOLD', 'confidence': 0.0, 'signals': []}
    
    def _calculate_indicators(self, data: pd.DataFrame) -> Dict:
        """Calcola indicatori tecnici"""
        indicators = {}
        
        try:
            # RSI
            indicators['rsi'] = ta.momentum.RSIIndicator(data['Close']).rsi().iloc[-1]
            
            # MACD
            macd = ta.trend.MACD(data['Close'])
            indicators['macd'] = macd.macd().iloc[-1]
            indicators['macd_signal'] = macd.macd_signal().iloc[-1]
            indicators['macd_diff'] = macd.macd_diff().iloc[-1]
            
            # Bollinger Bands
            bb = ta.volatility.BollingerBands(data['Close'])
            indicators['bb_upper'] = bb.bollinger_hband().iloc[-1]
            indicators['bb_lower'] = bb.bollinger_lband().iloc[-1]
            indicators['bb_middle'] = bb.bollinger_mavg().iloc[-1]
            indicators['bb_width'] = (indicators['bb_upper'] - indicators['bb_lower']) / indicators['bb_middle']
            
            # Moving Averages
            indicators['sma_20'] = data['Close'].rolling(20).mean().iloc[-1]
            indicators['sma_50'] = data['Close'].rolling(50).mean().iloc[-1]
            indicators['ema_12'] = data['Close'].ewm(span=12).mean().iloc[-1]
            indicators['ema_26'] = data['Close'].ewm(span=26).mean().iloc[-1]
            
            # Prezzo corrente
            indicators['current_price'] = data['Close'].iloc[-1]
            
            # Volume
            indicators['volume'] = data['Volume'].iloc[-1]
            indicators['volume_sma'] = data['Volume'].rolling(20).mean().iloc[-1]
            
        except Exception as e:
            logger.error(f"Errore calcolo indicatori: {e}")
            
        return indicators
    
    def _generate_signals(self, indicators: Dict) -> List[Dict]:
        """Genera segnali basati su indicatori"""
        signals = []
        
        try:
            # RSI Signal
            rsi = indicators.get('rsi', 50)
            if rsi < 30:
                signals.append({'type': 'RSI', 'signal': 'BUY', 'strength': 0.8, 'reason': f'RSI oversold: {rsi:.1f}'})
            elif rsi > 70:
                signals.append({'type': 'RSI', 'signal': 'SELL', 'strength': 0.8, 'reason': f'RSI overbought: {rsi:.1f}'})
            
            # MACD Signal
            macd_diff = indicators.get('macd_diff', 0)
            if macd_diff > 0:
                signals.append({'type': 'MACD', 'signal': 'BUY', 'strength': 0.6, 'reason': 'MACD positive divergence'})
            elif macd_diff < 0:
                signals.append({'type': 'MACD', 'signal': 'SELL', 'strength': 0.6, 'reason': 'MACD negative divergence'})
            
            # Moving Average Signal
            current_price = indicators.get('current_price', 0)
            sma_20 = indicators.get('sma_20', 0)
            sma_50 = indicators.get('sma_50', 0)
            
            if current_price > sma_20 > sma_50:
                signals.append({'type': 'MA', 'signal': 'BUY', 'strength': 0.7, 'reason': 'Price above rising MA'})
            elif current_price < sma_20 < sma_50:
                signals.append({'type': 'MA', 'signal': 'SELL', 'strength': 0.7, 'reason': 'Price below falling MA'})
            
            # Bollinger Bands Signal
            bb_upper = indicators.get('bb_upper', 0)
            bb_lower = indicators.get('bb_lower', 0)
            
            if current_price < bb_lower:
                signals.append({'type': 'BB', 'signal': 'BUY', 'strength': 0.6, 'reason': 'Price below BB lower band'})
            elif current_price > bb_upper:
                signals.append({'type': 'BB', 'signal': 'SELL', 'strength': 0.6, 'reason': 'Price above BB upper band'})
            
            # Volume Signal
            volume = indicators.get('volume', 0)
            volume_sma = indicators.get('volume_sma', 0)
            
            if volume > volume_sma * 1.5:
                signals.append({'type': 'VOLUME', 'signal': 'ATTENTION', 'strength': 0.4, 'reason': 'High volume detected'})
                
        except Exception as e:
            logger.error(f"Errore generazione segnali: {e}")
            
        return signals
    
    def _combine_signals(self, signals: List[Dict]) -> Dict:
        """Combina segnali per raccomandazione finale"""
        if not signals:
            return {'action': 'HOLD', 'confidence': 0.0}
        
        # Conta segnali BUY/SELL pesati per strength
        buy_score = sum([s['strength'] for s in signals if s['signal'] == 'BUY'])
        sell_score = sum([s['strength'] for s in signals if s['signal'] == 'SELL'])
        
        # Determina azione
        if buy_score > sell_score and buy_score > 1.0:
            action = 'BUY'
            confidence = min(0.9, buy_score / (buy_score + sell_score + 0.1))
        elif sell_score > buy_score and sell_score > 1.0:
            action = 'SELL'
            confidence = min(0.9, sell_score / (buy_score + sell_score + 0.1))
        else:
            action = 'HOLD'
            confidence = 0.3
        
        return {'action': action, 'confidence': confidence}

def should_buy(df):
    """
    Determina se comprare un titolo basandosi sui dati storici
    
    Strategia semplice: compra se il prezzo attuale è sopra la media mobile a 3 giorni
    
    Args:
        df (pandas.DataFrame): DataFrame con i dati del titolo
    
    Returns:
        bool: True se dovremmo comprare, False altrimenti
    """
    if len(df) < 3:
        return False
    
    try:
        current_price = df["Close"].iloc[-1]
        avg_3d = df['Close'].rolling(window=3).mean().iloc[-1]
        
        # Strategia: compra se prezzo attuale > media 3 giorni
        return current_price > avg_3d
    except Exception as e:
        print(f"Errore nella strategia: {e}")
        return False

def should_sell(df):
    """
    Determina se vendere un titolo
    
    Args:
        df (pandas.DataFrame): DataFrame con i dati del titolo
    
    Returns:
        bool: True se dovremmo vendere, False altrimenti
    """
    if len(df) < 3:
        return False
    
    try:
        current_price = df["Close"].iloc[-1]
        avg_3d = df['Close'].rolling(window=3).mean().iloc[-1]
        
        # Strategia: vendi se prezzo attuale < media 3 giorni
        return current_price < avg_3d
    except Exception as e:
        print(f"Errore nella strategia di vendita: {e}")
        return False
