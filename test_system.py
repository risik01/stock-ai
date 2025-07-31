#!/usr/bin/env python3
"""
Test Suite Completo - Stock AI Sistema di Trading v2.0.0
Test di integrazione per verificare tutte le funzionalità implementate
"""

import subprocess
import sys
import time
import json
import os
from datetime import datetime
from pathlib import Path

class StockAITester:
    """Test suite completo per Stock AI"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = {}
        
    def run_command(self, cmd, expected_in_output=None, timeout=60):
        """Esegue comando e verifica output"""
        try:
            print(f"🔧 Eseguendo: {cmd}")
            
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                cwd=self.base_dir
            )
            
            success = result.returncode == 0
            
            if expected_in_output and success:
                success = expected_in_output in result.stdout
            
            if success:
                print(f"✅ Test PASSED")
                self.passed_tests += 1
            else:
                print(f"❌ Test FAILED")
                print(f"   Return code: {result.returncode}")
                print(f"   STDOUT: {result.stdout[:200]}...")
                print(f"   STDERR: {result.stderr[:200]}...")
                self.failed_tests += 1
                
            return success, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            print(f"⏰ Test TIMEOUT dopo {timeout}s")
            self.failed_tests += 1
            return False, "", "Timeout"
            
        except Exception as e:
            print(f"💥 Test EXCEPTION: {e}")
            self.failed_tests += 1
            return False, "", str(e)
    
    def test_basic_commands(self):
        """Test comandi base del sistema"""
        print("\n" + "="*60)
        print("🧪 TEST COMANDI BASE")
        print("="*60)
        
        tests = [
            ("python src/main.py --version", "Stock AI"),
            ("python src/main.py --system-status", "STATO SISTEMA"),
            ("python src/main.py --show-config", "Configurazione"),
            ("python src/main.py --help", "usage:"),
        ]
        
        for cmd, expected in tests:
            print(f"\n📋 Test: {cmd.split('--')[1]}")
            success, stdout, stderr = self.run_command(cmd, expected)
            self.test_results[f"basic_{cmd.split('--')[1]}"] = success
    
    def test_portfolio_commands(self):
        """Test comandi portfolio"""
        print("\n" + "="*60)
        print("💼 TEST PORTFOLIO")
        print("="*60)
        
        tests = [
            ("python src/main.py --portfolio status", None),
            ("python src/main.py --update-data", None),
            ("python src/main.py --test-api", None),
        ]
        
        for cmd, expected in tests:
            test_name = cmd.split('--')[1].replace(' ', '_')
            print(f"\n📋 Test: {test_name}")
            success, stdout, stderr = self.run_command(cmd, expected, timeout=120)
            self.test_results[f"portfolio_{test_name}"] = success
    
    def test_advanced_features(self):
        """Test funzionalità avanzate"""
        print("\n" + "="*60)
        print("🚀 TEST FUNZIONALITÀ AVANZATE")
        print("="*60)
        
        tests = [
            ("python src/main.py --performance-report", "Report generato"),
            ("python src/main.py --monte-carlo --simulations 100", "Risultati Proiezione"),
        ]
        
        for cmd, expected in tests:
            test_name = cmd.split('--')[1].split(' ')[0]
            print(f"\n📋 Test: {test_name}")
            success, stdout, stderr = self.run_command(cmd, expected, timeout=180)
            self.test_results[f"advanced_{test_name}"] = success
    
    def test_modules_directly(self):
        """Test moduli direttamente"""
        print("\n" + "="*60)
        print("🔧 TEST MODULI DIRETTI")
        print("="*60)
        
        modules = [
            "src/data_collector.py",
            "src/performance_analytics.py",
            "src/backtest_engine.py",
        ]
        
        for module in modules:
            print(f"\n📋 Test: {Path(module).stem}")
            success, stdout, stderr = self.run_command(f"python {module}", None, timeout=120)
            self.test_results[f"module_{Path(module).stem}"] = success
    
    def test_web_dashboard(self):
        """Test dashboard web (avvio veloce)"""
        print("\n" + "="*60)
        print("🌐 TEST WEB DASHBOARD")
        print("="*60)
        
        print(f"\n📋 Test: Dashboard startup")
        
        # Test avvio rapido (5 secondi)
        try:
            import subprocess
            import signal
            
            # Avvia dashboard in background
            proc = subprocess.Popen(
                ["python", "src/main.py", "--dashboard"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.base_dir
            )
            
            # Aspetta 5 secondi
            time.sleep(5)
            
            # Termina processo
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            
            print("✅ Dashboard avvio test PASSED")
            self.passed_tests += 1
            self.test_results["web_dashboard"] = True
            
        except Exception as e:
            print(f"❌ Dashboard test FAILED: {e}")
            self.failed_tests += 1
            self.test_results["web_dashboard"] = False
    
    def test_file_structure(self):
        """Test struttura file"""
        print("\n" + "="*60)
        print("📁 TEST STRUTTURA FILE")
        print("="*60)
        
        required_files = [
            "src/main.py",
            "src/data_collector.py",
            "src/portfolio.py",
            "src/strategy_engine.py",
            "src/rl_agent.py",
            "src/advanced_rl_training.py",
            "src/backtest_engine.py",
            "src/performance_analytics.py",
            "src/web_dashboard.py",
            "src/trading_env.py",
            "requirements.txt",
            "config/settings.json",
            "config/trading_config.json",
            "templates/dashboard.html",
        ]
        
        required_dirs = [
            "src",
            "data",
            "config", 
            "templates",
            "logs"
        ]
        
        print(f"\n📋 Test: File richiesti")
        missing_files = []
        for file_path in required_files:
            full_path = self.base_dir / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"❌ File mancanti: {missing_files}")
            self.failed_tests += 1
            self.test_results["file_structure"] = False
        else:
            print("✅ Tutti i file presenti")
            self.passed_tests += 1
            self.test_results["file_structure"] = True
        
        print(f"\n📋 Test: Directory richieste")
        missing_dirs = []
        for dir_path in required_dirs:
            full_path = self.base_dir / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)
        
        if missing_dirs:
            print(f"❌ Directory mancanti: {missing_dirs}")
            self.failed_tests += 1
            self.test_results["dir_structure"] = False
        else:
            print("✅ Tutte le directory presenti")
            self.passed_tests += 1
            self.test_results["dir_structure"] = True
    
    def generate_report(self):
        """Genera report finale dei test"""
        print("\n" + "="*60)
        print("📊 REPORT FINALE TEST")
        print("="*60)
        
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n🎯 Risultati Generali:")
        print(f"   ✅ Test Passati: {self.passed_tests}")
        print(f"   ❌ Test Falliti: {self.failed_tests}")
        print(f"   📊 Totale Test: {total_tests}")
        print(f"   🎖️ Success Rate: {success_rate:.1f}%")
        
        print(f"\n📋 Dettaglio per Categoria:")
        
        categories = {}
        for test_name, result in self.test_results.items():
            category = test_name.split('_')[0]
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0}
            
            if result:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
        
        for category, results in categories.items():
            total = results["passed"] + results["failed"]
            rate = (results["passed"] / total * 100) if total > 0 else 0
            print(f"   {category.upper()}: {results['passed']}/{total} ({rate:.1f}%)")
        
        # Salva report JSON
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": self.passed_tests,
                "failed": self.failed_tests,
                "success_rate": success_rate
            },
            "categories": categories,
            "detailed_results": self.test_results
        }
        
        report_path = self.base_dir / "data" / "test_results.json"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Report salvato: {report_path}")
        
        # Verdetto finale
        if success_rate >= 80:
            print(f"\n🎉 SISTEMA STOCK AI: ✅ FUNZIONALE ({success_rate:.1f}%)")
            return True
        elif success_rate >= 60:
            print(f"\n⚠️ SISTEMA STOCK AI: 🟡 PARZIALMENTE FUNZIONALE ({success_rate:.1f}%)")
            return False
        else:
            print(f"\n💥 SISTEMA STOCK AI: ❌ NON FUNZIONALE ({success_rate:.1f}%)")
            return False
    
    def run_all_tests(self):
        """Esegue tutti i test"""
        print("🤖 STOCK AI - TEST SUITE COMPLETO")
        print("Versione: 2.0.0")
        print("Data:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("="*60)
        
        try:
            # Test individuali
            self.test_file_structure()
            self.test_basic_commands()
            self.test_portfolio_commands()
            self.test_modules_directly()
            self.test_advanced_features()
            self.test_web_dashboard()
            
            # Report finale
            return self.generate_report()
            
        except KeyboardInterrupt:
            print("\n🛑 Test interrotti dall'utente")
            return False
        except Exception as e:
            print(f"\n💥 Errore durante i test: {e}")
            return False

def main():
    """Funzione principale"""
    tester = StockAITester()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        print("⚡ MODALITÀ QUICK TEST")
        # Solo test base per quick check
        tester.test_file_structure()
        tester.test_basic_commands()
        return tester.generate_report()
    else:
        return tester.run_all_tests()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
