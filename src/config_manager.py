#!/usr/bin/env python3
"""
Configuration Manager
====================
Gestore delle configurazioni per il sistema di trading
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ConfigManager:
    """Gestore delle configurazioni"""
    
    def __init__(self, config_path: str = "config/settings.json"):
        """
        Inizializza il gestore delle configurazioni
        
        Args:
            config_path: Percorso del file di configurazione
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        logger.info(f"✅ ConfigManager inizializzato: {config_path}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Carica la configurazione dal file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info(f"📁 Configurazione caricata da {self.config_path}")
                return config
            else:
                logger.warning(f"⚠️ File configurazione non trovato: {self.config_path}")
                return self._create_default_config()
        except Exception as e:
            logger.error(f"❌ Errore nel caricamento configurazione: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Crea una configurazione di default"""
        default_config = {
            "trading": {
                "initial_capital": 10000,
                "max_position_size": 0.2,
                "stop_loss": 0.05,
                "take_profit": 0.15,
                "commission": 0.001,
                "slippage": 0.0005,
                "live_trading": {
                    "enabled": True,
                    "check_interval": 300,
                    "market_hours_only": True,
                    "max_trades_per_day": 20,
                    "min_trade_interval": 60,
                    "risk_per_trade": 0.02
                }
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
                "update_interval": 1800,
                "lookback_days": 365,
                "symbols": ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA", "AMD", "META"],
                "data_source": "yfinance",
                "cache_enabled": True,
                "real_time": {
                    "enabled": True,
                    "source": "yfinance",
                    "refresh_rate": 60
                }
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
            },
            "monitoring": {
                "price_alerts": True,
                "volume_alerts": True,
                "technical_indicators": ["RSI", "MACD", "BB"],
                "alert_thresholds": {
                    "rsi_oversold": 30,
                    "rsi_overbought": 70,
                    "volume_spike": 2.0
                }
            }
        }
        
        # Salva la configurazione di default
        try:
            self.config_path.parent.mkdir(exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"📝 Configurazione di default salvata in {self.config_path}")
        except Exception as e:
            logger.error(f"❌ Errore nel salvataggio configurazione: {e}")
        
        return default_config
    
    def get_config(self) -> Dict[str, Any]:
        """Restituisce la configurazione corrente"""
        return self.config
    
    def get_section(self, section: str) -> Optional[Dict[str, Any]]:
        """
        Restituisce una sezione specifica della configurazione
        
        Args:
            section: Nome della sezione (es. 'trading', 'data', etc.)
            
        Returns:
            Dizionario della sezione o None se non trovata
        """
        return self.config.get(section)
    
    def get_value(self, key_path: str, default=None) -> Any:
        """
        Restituisce un valore usando un percorso di chiavi
        
        Args:
            key_path: Percorso delle chiavi separato da punti (es. 'trading.initial_capital')
            default: Valore di default se non trovato
            
        Returns:
            Valore trovato o default
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            logger.warning(f"⚠️ Chiave non trovata: {key_path}, usando default: {default}")
            return default
    
    def set_value(self, key_path: str, value: Any) -> bool:
        """
        Imposta un valore usando un percorso di chiavi
        
        Args:
            key_path: Percorso delle chiavi separato da punti
            value: Valore da impostare
            
        Returns:
            True se successo, False altrimenti
        """
        keys = key_path.split('.')
        config_ref = self.config
        
        try:
            # Naviga fino al penultimo livello
            for key in keys[:-1]:
                if key not in config_ref:
                    config_ref[key] = {}
                config_ref = config_ref[key]
            
            # Imposta il valore
            config_ref[keys[-1]] = value
            logger.info(f"✅ Valore impostato: {key_path} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore nell'impostazione valore {key_path}: {e}")
            return False
    
    def save_config(self) -> bool:
        """
        Salva la configurazione su file
        
        Returns:
            True se successo, False altrimenti
        """
        try:
            self.config_path.parent.mkdir(exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"💾 Configurazione salvata in {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Errore nel salvataggio configurazione: {e}")
            return False
    
    def reload_config(self) -> bool:
        """
        Ricarica la configurazione dal file
        
        Returns:
            True se successo, False altrimenti
        """
        try:
            self.config = self._load_config()
            logger.info("🔄 Configurazione ricaricata")
            return True
        except Exception as e:
            logger.error(f"❌ Errore nel ricaricamento configurazione: {e}")
            return False
    
    def validate_config(self) -> Dict[str, list]:
        """
        Valida la configurazione
        
        Returns:
            Dizionario con errori e avvertimenti
        """
        errors = []
        warnings = []
        
        # Validazione sezioni obbligatorie
        required_sections = ['trading', 'data', 'rl_agent']
        for section in required_sections:
            if section not in self.config:
                errors.append(f"Sezione obbligatoria mancante: {section}")
        
        # Validazione valori trading
        if 'trading' in self.config:
            trading = self.config['trading']
            if trading.get('initial_capital', 0) <= 0:
                errors.append("initial_capital deve essere > 0")
            if not 0 < trading.get('max_position_size', 0) <= 1:
                errors.append("max_position_size deve essere tra 0 e 1")
        
        # Validazione simboli
        if 'data' in self.config:
            symbols = self.config['data'].get('symbols', [])
            if not symbols:
                warnings.append("Nessun simbolo configurato per il trading")
        
        return {
            'errors': errors,
            'warnings': warnings
        }
    
    def __str__(self) -> str:
        """Rappresentazione string del ConfigManager"""
        return f"ConfigManager(config_path={self.config_path}, sections={list(self.config.keys())})"
