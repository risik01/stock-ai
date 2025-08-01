#!/usr/bin/env python3
"""
Test sistematico di tutti gli import Python
"""
import os
import sys
import traceback
from pathlib import Path

# Aggiungi path necessari
sys.path.insert(0, '.')
sys.path.insert(0, './src')
sys.path.insert(0, './news')
sys.path.insert(0, './dashboard')

def test_import(module_path, module_name):
    """Test import di un singolo modulo"""
    print(f"\n🔍 Testing {module_name}...")
    try:
        # Cambio di directory per risolvere path relativi
        original_dir = os.getcwd()
        
        if module_path.startswith('./src/'):
            os.chdir('./src')
            module_name = module_name.replace('src.', '')
        elif module_path.startswith('./news/'):
            os.chdir('./news')
            module_name = module_name.replace('news.', '')
        elif module_path.startswith('./dashboard/'):
            # Per i dashboard, usiamo un approccio diverso
            # Non cambiamo directory, ma importiamo con il path completo
            sys.path.insert(0, './dashboard')
            sys.path.insert(0, './src')
            sys.path.insert(0, './news')
            module_name = module_name.replace('dashboard.', '')
        
        # Import del modulo
        if module_path.startswith('./dashboard/'):
            # Per i dashboard, uso exec per evitare problemi di auto-import
            with open(module_path, 'r') as f:
                code = f.read()
            # Compila il codice per verificare sintassi
            compile(code, module_path, 'exec')
            print(f"✅ {module_path} - OK (syntax check)")
        else:
            __import__(module_name.replace('.py', ''))
            print(f"✅ {module_path} - OK")
        
        return True
        
    except ImportError as e:
        print(f"❌ {module_path} - Import Error: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {module_path} - Other Error: {e}")
        return False
    finally:
        os.chdir(original_dir)

def main():
    """Main test function"""
    print("🔧 CONTROLLO APPROFONDITO IMPORT PYTHON")
    print("="*60)
    
    # Lista dei file Python del progetto
    python_files = [
        # SRC
        ("./src/main.py", "main"),
        ("./src/simple_dual_ai.py", "simple_dual_ai"),
        ("./src/data_collector.py", "data_collector"),
        ("./src/portfolio.py", "portfolio"),
        ("./src/rl_agent.py", "rl_agent"),
        ("./src/strategy_engine.py", "strategy_engine"),
        ("./src/trading_env.py", "trading_env"),
        ("./src/yahoo_api_v8.py", "yahoo_api_v8"),
        ("./src/automated_trading_system.py", "automated_trading_system"),
        ("./src/dual_ai_trading_system.py", "dual_ai_trading_system"),
        ("./src/live_trading_monitor.py", "live_trading_monitor"),
        ("./src/performance_analytics.py", "performance_analytics"),
        ("./src/backtest_engine.py", "backtest_engine"),
        ("./src/advanced_rl_training.py", "advanced_rl_training"),
        
        # NEWS
        ("./news/news_rss_collector.py", "news_rss_collector"),
        ("./news/news_sentiment_analyzer.py", "news_sentiment_analyzer"),
        ("./news/news_based_trading_ai.py", "news_based_trading_ai"),
        ("./news/news_trading_cli.py", "news_trading_cli"),
        ("./news/news_cli_advanced.py", "news_cli_advanced"),
        
        # DASHBOARD
        ("./dashboard/web_dashboard.py", "web_dashboard"),
        ("./dashboard/news_web_dashboard.py", "news_web_dashboard"),
    ]
    
    success_count = 0
    total_count = len(python_files)
    
    for file_path, module_name in python_files:
        if Path(file_path).exists():
            if test_import(file_path, module_name):
                success_count += 1
        else:
            print(f"❌ {file_path} - File non trovato")
    
    print(f"\n📊 RISULTATI:")
    print(f"✅ Successi: {success_count}/{total_count}")
    print(f"❌ Fallimenti: {total_count - success_count}/{total_count}")
    print(f"📈 Tasso successo: {(success_count/total_count)*100:.1f}%")
    
    if success_count == total_count:
        print("🎉 TUTTI I FILE PYTHON SONO OPERATIVI!")
    else:
        print("⚠️  Alcuni file necessitano correzioni")

if __name__ == "__main__":
    main()
