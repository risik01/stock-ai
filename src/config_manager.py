import json
import os
from datetime import datetime

class TradingConfig:
    """Gestisce la configurazione del trading bot"""
    
    def __init__(self, config_file="/workspaces/stock-ai/config/trading_config.json", aggressiveness=None):
        self.config_file = config_file
        self.config = self.load_config()
        
        # Se specificato un livello di aggressività, applica il preset
        if aggressiveness is not None:
            self.apply_aggressiveness_preset(aggressiveness)
    
    def load_config(self):
        """Carica la configurazione dal file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"❌ Errore nel caricamento config: {e}")
        
        # Configurazione di default se il file non esiste
        return self.get_default_config()
    
    def get_default_config(self):
        """Restituisce la configurazione di default"""
        return {
            "trading_settings": {
                "aggressiveness_level": 7,
                "check_interval_seconds": 30,
                "max_positions": 5,
                "risk_per_trade": 0.15,
                "stop_loss_percentage": -0.05,
                "take_profit_percentage": 0.08
            },
            "data_settings": {
                "analysis_period": "5d",
                "price_update_period": "2d",
                "min_data_points": 2,
                "max_retries": 3,
                "retry_delay_seconds": 2
            }
        }
    
    def apply_aggressiveness_preset(self, level):
        """Applica un preset di aggressività (1-10)"""
        level = max(1, min(10, int(level)))  # Clamp tra 1 e 10
        level_str = str(level)
        
        if "aggressiveness_presets" in self.config and level_str in self.config["aggressiveness_presets"]:
            preset = self.config["aggressiveness_presets"][level_str]
            print(f"🎯 Applicando preset: Livello {level} - {preset['name']}")
            
            # Aggiorna le impostazioni di trading
            for key, value in preset.items():
                if key != "name":
                    if key in self.config["trading_settings"]:
                        self.config["trading_settings"][key] = value
                    elif key in self.config.get("market_filters", {}):
                        self.config["market_filters"][key] = value
            
            self.config["trading_settings"]["aggressiveness_level"] = level
            print(f"   ⚡ Aggressività: {level}/10")
            print(f"   ⏱️  Controlli ogni: {self.get('check_interval_seconds')}s")
            print(f"   📊 Max posizioni: {self.get('max_positions')}")
            print(f"   💰 Risk per trade: {self.get('risk_per_trade')*100:.1f}%")
        else:
            print(f"⚠️  Preset {level} non trovato, usando configurazione corrente")
    
    def get(self, key, section=None):
        """Ottiene un valore di configurazione"""
        if section:
            return self.config.get(section, {}).get(key)
        
        # Cerca in tutte le sezioni
        for section_data in self.config.values():
            if isinstance(section_data, dict) and key in section_data:
                return section_data[key]
        return None
    
    def save_config(self):
        """Salva la configurazione corrente"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"✅ Configurazione salvata in {self.config_file}")
        except Exception as e:
            print(f"❌ Errore nel salvare config: {e}")
    
    def print_current_config(self):
        """Stampa la configurazione attuale"""
        print("\n📊 CONFIGURAZIONE ATTUALE:")
        print("=" * 40)
        
        aggressiveness = self.get('aggressiveness_level')
        print(f"🎯 Livello Aggressività: {aggressiveness}/10")
        print(f"⏱️  Intervallo controlli: {self.get('check_interval_seconds')}s")
        print(f"📈 Max posizioni: {self.get('max_positions')}")
        print(f"💰 Risk per trade: {self.get('risk_per_trade')*100:.1f}%")
        print(f"📉 Stop loss: {self.get('stop_loss_percentage')*100:.1f}%")
        print(f"📈 Take profit: {self.get('take_profit_percentage')*100:.1f}%")
        print(f"📊 Periodo analisi: {self.get('analysis_period')}")
        print(f"🔄 Aggiornamento prezzi: {self.get('price_update_period')}")
        print(f"⚡ Soglia aggressività: {self.get('aggressiveness_threshold')}")
        print(f"📈 Max volatilità: {self.get('max_volatility')*100:.1f}%")
