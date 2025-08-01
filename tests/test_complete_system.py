#!/usr/bin/env python3
"""
Test completo di tutto il sistema
=================================
Test di tutti i file Python e script shell
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def test_python_files():
    """Test di tutti i file Python"""
    print("\n" + "="*60)
    print("🐍 TESTING PYTHON FILES")
    print("="*60)
    
    result = subprocess.run([sys.executable, "test_all_imports.py"], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Tutti i file Python sono operativi!")
        return True
    else:
        print(f"❌ Errori nei file Python: {result.stderr}")
        return False

def test_main_py_options():
    """Test delle opzioni del main.py"""
    print("\n" + "="*60)
    print("🔧 TESTING MAIN.PY OPTIONS")
    print("="*60)
    
    tests = [
        ("python src/main.py --version", "Test version"),
        ("python src/main.py --help", "Test help"),
        ("python src/main.py --show-config", "Test show config"),
        ("python src/main.py --system-status", "Test system status"),
    ]
    
    success_count = 0
    for cmd, desc in tests:
        print(f"\n🔍 {desc}...")
        try:
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"✅ {desc} - OK")
                success_count += 1
            else:
                print(f"❌ {desc} - Error: {result.stderr}")
        except subprocess.TimeoutExpired:
            print(f"⏰ {desc} - Timeout")
        except Exception as e:
            print(f"❌ {desc} - Exception: {e}")
    
    print(f"\n📊 Main.py tests: {success_count}/{len(tests)} passed")
    return success_count == len(tests)

def test_shell_scripts():
    """Test degli script shell"""
    print("\n" + "="*60)
    print("🔧 TESTING SHELL SCRIPTS")
    print("="*60)
    
    shell_scripts = [
        ("bin/dual_ai_control.sh", "Dual AI Control"),
        ("bin/dual_ai_monitor.sh", "Dual AI Monitor"),
        ("bin/trading_control.sh", "Trading Control"),
        ("launch.sh", "Master Launcher"),
    ]
    
    success_count = 0
    total_count = len(shell_scripts)
    
    for script_path, description in shell_scripts:
        print(f"\n🔍 Testing {description}...")
        
        if not Path(script_path).exists():
            print(f"❌ {script_path} - File non trovato")
            continue
            
        # Test sintassi bash
        try:
            result = subprocess.run(["bash", "-n", script_path], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {script_path} - Sintassi OK")
                success_count += 1
            else:
                print(f"❌ {script_path} - Errore sintassi: {result.stderr}")
        except Exception as e:
            print(f"❌ {script_path} - Exception: {e}")
    
    print(f"\n📊 Shell scripts: {success_count}/{total_count} passed")
    return success_count == total_count

def test_dual_ai_system():
    """Test del sistema dual AI"""
    print("\n" + "="*60)
    print("🤖 TESTING DUAL AI SYSTEM")
    print("="*60)
    
    print("🔍 Testing simple_dual_ai.py import...")
    try:
        result = subprocess.run([sys.executable, "-c", "import src.simple_dual_ai; print('✅ Import OK')"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Simple Dual AI - Import OK")
            return True
        else:
            print(f"❌ Simple Dual AI - Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("⏰ Simple Dual AI - Timeout")
        return False
    except Exception as e:
        print(f"❌ Simple Dual AI - Exception: {e}")
        return False

def test_news_system():
    """Test del sistema news"""
    print("\n" + "="*60)
    print("📰 TESTING NEWS SYSTEM")
    print("="*60)
    
    news_modules = [
        "news.news_rss_collector",
        "news.news_sentiment_analyzer",
        "news.news_based_trading_ai",
    ]
    
    success_count = 0
    for module in news_modules:
        print(f"\n🔍 Testing {module}...")
        try:
            result = subprocess.run([sys.executable, "-c", f"import {module}; print('✅ OK')"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ {module} - OK")
                success_count += 1
            else:
                print(f"❌ {module} - Error: {result.stderr}")
        except subprocess.TimeoutExpired:
            print(f"⏰ {module} - Timeout")
        except Exception as e:
            print(f"❌ {module} - Exception: {e}")
    
    print(f"\n📊 News modules: {success_count}/{len(news_modules)} passed")
    return success_count == len(news_modules)

def test_dashboard_system():
    """Test del sistema dashboard"""
    print("\n" + "="*60)
    print("🌐 TESTING DASHBOARD SYSTEM")
    print("="*60)
    
    dashboard_files = [
        "dashboard/web_dashboard.py",
        "dashboard/news_web_dashboard.py",
    ]
    
    success_count = 0
    for file_path in dashboard_files:
        print(f"\n🔍 Testing {file_path}...")
        try:
            # Test compilazione
            with open(file_path, 'r') as f:
                code = f.read()
            compile(code, file_path, 'exec')
            print(f"✅ {file_path} - Syntax OK")
            success_count += 1
        except Exception as e:
            print(f"❌ {file_path} - Error: {e}")
    
    print(f"\n📊 Dashboard files: {success_count}/{len(dashboard_files)} passed")
    return success_count == len(dashboard_files)

def generate_system_report():
    """Genera report finale del sistema"""
    print("\n" + "="*80)
    print("📋 REPORT FINALE SISTEMA")
    print("="*80)
    
    # Test tutti i componenti
    results = {
        "Python Files": test_python_files(),
        "Main.py Options": test_main_py_options(),
        "Shell Scripts": test_shell_scripts(),
        "Dual AI System": test_dual_ai_system(),
        "News System": test_news_system(),
        "Dashboard System": test_dashboard_system(),
    }
    
    print(f"\n📊 RISULTATI FINALI:")
    print("-" * 40)
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
    
    print("-" * 40)
    print(f"TOTALE: {passed_tests}/{total_tests} ({(passed_tests/total_tests)*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("\n🎉 SISTEMA COMPLETAMENTE OPERATIVO!")
        print("🚀 Tutte le funzionalità sono pronte per l'uso")
    else:
        print(f"\n⚠️  Componenti da correggere: {total_tests - passed_tests}")
    
    return passed_tests == total_tests

def main():
    """Main test function"""
    print("🔧 CONTROLLO COMPLETO SISTEMA STOCK AI")
    print("=" * 80)
    print(f"📅 Data: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Directory: {os.getcwd()}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    
    # Esegui tutti i test
    system_ok = generate_system_report()
    
    print(f"\n🏁 Test completato!")
    return system_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
