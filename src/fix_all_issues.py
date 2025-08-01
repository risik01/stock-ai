#!/usr/bin/env python3
"""
SCRIPT DI RIPARAZIONE COMPLETA - Trading AI System
Analizza e corregge tutti i problemi del progetto
"""

import os
import sys
import json
import shutil
from pathlib import Path

class TradingSystemFixer:
    """Riparatore completo del sistema trading"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.errors = []
        self.fixes = []
        
    def log_error(self, error):
        self.errors.append(error)
        print(f"❌ ERRORE: {error}")
    
    def log_fix(self, fix):
        self.fixes.append(fix)
        print(f"✅ FIX: {fix}")
    
    def check_directory_structure(self):
        """Verifica e crea struttura directory"""
        print("\n📁 CONTROLLO STRUTTURA DIRECTORY")
        print("=" * 50)
        
        required_dirs = {
            'src': 'Directory moduli core',
            'news': 'Directory moduli news',
            'config': 'File configurazione',
            'data': 'Directory dati e cache',
            'logs': 'Directory log',
            'templates': 'Template web'
        }
        
        for dir_name, description in required_dirs.items():
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                self.log_error(f"Directory mancante: {dir_name} ({description})")
                dir_path.mkdir(exist_ok=True)
                self.log_fix(f"Creata directory: {dir_name}")
            else:
                print(f"✅ {dir_name}/ - {description}")
    
    def fix_config_files(self):
        """Corregge file di configurazione"""
        print("\n⚙️ CONTROLLO CONFIGURAZIONI")
        print("=" * 50)
        
        # Fix production_settings.json -> settings.json
        production_config = self.project_root / 'config' / 'production_settings.json'
        settings_config = self.project_root / 'config' / 'settings.json'
        
        if production_config.exists() and not settings_config.exists():
            shutil.copy(production_config, settings_config)
            self.log_fix("Copiato production_settings.json → settings.json")
        
        # Verifica file configurazione esistono
        config_files = {
            'config/settings.json': 'Configurazione principale',
            'config/production_settings.json': 'Configurazione produzione'
        }
        
        for config_file, description in config_files.items():
            config_path = self.project_root / config_file
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        json.load(f)
                    print(f"✅ {config_file} - {description}")
                except json.JSONDecodeError as e:
                    self.log_error(f"JSON malformato in {config_file}: {e}")
            else:
                self.log_error(f"File mancante: {config_file}")
    
    def fix_import_paths(self):
        """Corregge tutti i percorsi di import"""
        print("\n🔧 CORREZIONE PERCORSI IMPORT")
        print("=" * 50)
        
        # Fix data collector import
        data_collector_path = self.project_root / 'src' / 'data_collector.py'
        if data_collector_path.exists():
            self._fix_data_collector_imports(data_collector_path)
        
        # Fix automated trading system
        main_system_path = self.project_root / 'automated_trading_system.py'
        if main_system_path.exists():
            self._fix_main_system_imports(main_system_path)
        
        # Fix news modules
        self._fix_news_modules()
    
    def _fix_data_collector_imports(self, file_path):
        """Fix specifico per data_collector.py"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Assicurati che yahoo_api_v8 sia importato correttamente
            if 'from yahoo_api_v8 import yahoo_v8' not in content:
                # Aggiungi import dopo gli altri import
                import_lines = []
                other_lines = []
                in_imports = True
                
                for line in content.split('\n'):
                    if line.startswith('import ') or line.startswith('from '):
                        import_lines.append(line)
                    elif line.strip() == '' and in_imports:
                        import_lines.append(line)
                    else:
                        if in_imports:
                            import_lines.append('# Import nuovo client API v8')
                            import_lines.append('try:')
                            import_lines.append('    from yahoo_api_v8 import yahoo_v8')
                            import_lines.append('except ImportError:')
                            import_lines.append('    yahoo_v8 = None')
                            import_lines.append('')
                            in_imports = False
                        other_lines.append(line)
                
                new_content = '\n'.join(import_lines + other_lines)
                
                with open(file_path, 'w') as f:
                    f.write(new_content)
                
                self.log_fix("Aggiunto import yahoo_api_v8 in data_collector.py")
            else:
                print("✅ data_collector.py - Import yahoo_api_v8 già presente")
                
        except Exception as e:
            self.log_error(f"Errore fix data_collector.py: {e}")
    
    def _fix_main_system_imports(self, file_path):
        """Fix specifico per automated_trading_system.py"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Verifica che tutti i path siano configurati correttamente
            path_setup = '''# Aggiungi path per importazioni
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))
sys.path.insert(0, os.path.join(current_dir, 'news'))
sys.path.insert(0, current_dir)'''
            
            if path_setup not in content:
                self.log_error("Path setup non corretto in automated_trading_system.py")
            else:
                print("✅ automated_trading_system.py - Path setup corretto")
                
        except Exception as e:
            self.log_error(f"Errore verifica main system: {e}")
    
    def _fix_news_modules(self):
        """Fix moduli news"""
        news_dir = self.project_root / 'news'
        if not news_dir.exists():
            self.log_error("Directory news/ non esiste")
            return
        
        # Lista file news da controllare
        news_files = [
            'news_rss_collector.py',
            'news_sentiment_analyzer.py', 
            'news_based_trading_ai.py'
        ]
        
        for news_file in news_files:
            file_path = news_dir / news_file
            if file_path.exists():
                self._fix_news_file_paths(file_path)
            else:
                self.log_error(f"File mancante: news/{news_file}")
    
    def _fix_news_file_paths(self, file_path):
        """Fix percorsi nei file news"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Fix path per log e data
            fixes_made = False
            
            # Fix log paths
            old_patterns = [
                "'../data/news_collector.log'",
                "'../data/news_trading_ai.log'",
                "'../data/sentiment_analyzer.log'"
            ]
            
            new_patterns = [
                "'data/news_collector.log'",
                "'data/news_trading_ai.log'", 
                "'data/sentiment_analyzer.log'"
            ]
            
            for old, new in zip(old_patterns, new_patterns):
                if old in content:
                    content = content.replace(old, new)
                    fixes_made = True
            
            # Fix data paths
            old_data_patterns = [
                "'../data/",
                '"../data/'
            ]
            
            for pattern in old_data_patterns:
                if pattern in content:
                    content = content.replace(pattern, pattern.replace('../data/', 'data/'))
                    fixes_made = True
            
            # Assicurati che ci sia os.makedirs per data directory
            if 'data/' in content and 'os.makedirs' not in content:
                # Aggiungi makedirs dopo imports
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'logging.basicConfig' in line:
                        lines.insert(i, '        os.makedirs("data", exist_ok=True)')
                        fixes_made = True
                        break
                content = '\n'.join(lines)
            
            if fixes_made:
                with open(file_path, 'w') as f:
                    f.write(content)
                self.log_fix(f"Corretti percorsi in {file_path.name}")
            else:
                print(f"✅ {file_path.name} - Percorsi già corretti")
                
        except Exception as e:
            self.log_error(f"Errore fix {file_path.name}: {e}")
    
    def create_missing_files(self):
        """Crea file mancanti essenziali"""
        print("\n📄 CREAZIONE FILE MANCANTI")
        print("=" * 50)
        
        # Crea __init__.py nelle directory Python
        python_dirs = ['src', 'news']
        for dir_name in python_dirs:
            init_file = self.project_root / dir_name / '__init__.py'
            if not init_file.exists():
                init_file.touch()
                self.log_fix(f"Creato {dir_name}/__init__.py")
            else:
                print(f"✅ {dir_name}/__init__.py")
        
        # Crea file .env se non esiste
        env_file = self.project_root / '.env'
        env_example = self.project_root / '.env.example'
        
        if not env_file.exists() and env_example.exists():
            shutil.copy(env_example, env_file)
            self.log_fix("Creato .env da .env.example")
        elif not env_file.exists():
            with open(env_file, 'w') as f:
                f.write("# Trading AI System Environment Variables\n")
                f.write("DEBUG_MODE=false\n")
                f.write("LOG_LEVEL=INFO\n")
            self.log_fix("Creato .env base")
        else:
            print("✅ .env")
    
    def test_imports(self):
        """Test tutti gli import"""
        print("\n🧪 TEST IMPORT MODULI")
        print("=" * 50)
        
        # Setup path per test
        sys.path.insert(0, str(self.project_root / 'src'))
        sys.path.insert(0, str(self.project_root / 'news'))
        sys.path.insert(0, str(self.project_root))
        
        # Test import base
        try:
            import pandas as pd
            import numpy as np
            import yfinance as yf
            print("✅ Librerie base (pandas, numpy, yfinance)")
        except ImportError as e:
            self.log_error(f"Import librerie base: {e}")
        
        # Test import moduli src
        src_modules = [
            ('portfolio', 'Portfolio'),
            ('data_collector', 'DataCollector'),
            ('rl_agent', 'RLAgent'),
            ('strategy_engine', 'StrategyEngine')
        ]
        
        for module_name, class_name in src_modules:
            try:
                module = __import__(f'src.{module_name}', fromlist=[class_name])
                getattr(module, class_name)
                print(f"✅ src.{module_name}.{class_name}")
            except ImportError as e:
                self.log_error(f"Import src.{module_name}: {e}")
            except AttributeError as e:
                self.log_error(f"Classe {class_name} non trovata in {module_name}: {e}")
        
        # Test import moduli news
        news_modules = [
            ('news_rss_collector', 'NewsRSSCollector'),
            ('news_sentiment_analyzer', 'NewsSentimentAnalyzer'),
            ('news_based_trading_ai', 'NewsBasedTradingAI')
        ]
        
        for module_name, class_name in news_modules:
            try:
                module = __import__(module_name, fromlist=[class_name])
                getattr(module, class_name)
                print(f"✅ {module_name}.{class_name}")
            except ImportError as e:
                self.log_error(f"Import {module_name}: {e}")
            except AttributeError as e:
                self.log_error(f"Classe {class_name} non trovata in {module_name}: {e}")
    
    def generate_summary_report(self):
        """Genera report riassuntivo"""
        print("\n📊 REPORT RIPARAZIONE COMPLETATA")
        print("=" * 50)
        
        print(f"🔧 Correzioni applicate: {len(self.fixes)}")
        for fix in self.fixes:
            print(f"  ✅ {fix}")
        
        print(f"\n⚠️ Errori rimanenti: {len(self.errors)}")
        for error in self.errors:
            print(f"  ❌ {error}")
        
        if len(self.errors) == 0:
            print("\n🎉 SISTEMA COMPLETAMENTE RIPARATO!")
            print("✅ Tutti i componenti dovrebbero funzionare correttamente")
        else:
            print(f"\n⚠️ ATTENZIONE: {len(self.errors)} errori da risolvere manualmente")
    
    def run_full_repair(self):
        """Esegue riparazione completa"""
        print("🔧 AVVIO RIPARAZIONE COMPLETA TRADING AI SYSTEM")
        print("=" * 60)
        
        self.check_directory_structure()
        self.fix_config_files()
        self.create_missing_files()
        self.fix_import_paths()
        self.test_imports()
        self.generate_summary_report()

def main():
    """Funzione principale"""
    print("🚨 TRADING AI SYSTEM - RIPARAZIONE COMPLETA")
    print("=" * 60)
    
    fixer = TradingSystemFixer()
    fixer.run_full_repair()
    
    print("\n🔄 Per testare il sistema riparato:")
    print("   python3 test_v8_fix.py")
    print("\n🚀 Per avviare il sistema:")
    print("   python3 automated_trading_system.py")

if __name__ == "__main__":
    main()
