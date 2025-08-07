#!/usr/bin/env python3
"""
Launcher Script - Script unificato per tutti i componenti
Posizionato nella root per facilità d'uso
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Aggiungi src al path
project_root = Path(__file__).parent
sys.path.append(str(project_root / "src"))

def main():
    """Script launcher principale"""
    parser = argparse.ArgumentParser(description='🚀 Stock AI Trading System Launcher')
    
    subparsers = parser.add_subparsers(dest='command', help='Comandi disponibili')
    
    # === TRADING COMMANDS ===
    trading_group = subparsers.add_parser('trade', help='💰 Comandi di trading')
    trading_subparsers = trading_group.add_subparsers(dest='trade_mode')
    
    normal_parser = trading_subparsers.add_parser('normal', help='Trading normale')
    aggressive_parser = trading_subparsers.add_parser('aggressive', help='Trading aggressivo')
    aggressive_parser.add_argument('--aggressiveness', type=int, default=7, choices=range(1,11))
    
    # === AI TRAINING COMMANDS ===
    train_parser = subparsers.add_parser('train', help='🧠 Addestra AI in background')
    train_parser.add_argument('--days', type=float, default=1, help='Giorni di training')
    train_parser.add_argument('--symbols', nargs='+', help='Simboli da monitorare')
    
    # === DASHBOARD COMMANDS ===
    dash_parser = subparsers.add_parser('dashboard', help='📊 Dashboard live')
    
    # === TEST COMMANDS ===
    test_parser = subparsers.add_parser('test', help='🧪 Test del sistema')
    test_subparsers = test_parser.add_subparsers(dest='test_type')
    
    test_subparsers.add_parser('realtime', help='Test dati real-time')
    test_subparsers.add_parser('api', help='Test API')
    test_subparsers.add_parser('dual-ai', help='Test dual AI minimale')
    test_subparsers.add_parser('training', help='Test AI training')
    
    # === STATUS COMMANDS ===
    status_parser = subparsers.add_parser('status', help='📋 Verifica stato sistema')
    
    # === SMART SYSTEM COMMANDS ===
    smart_parser = subparsers.add_parser('smart', help='🤖 Smart Trading System')
    smart_subparsers = smart_parser.add_subparsers(dest='smart_mode')
    
    smart_subparsers.add_parser('check', help='Verifica AI readiness')
    
    auto_parser = smart_subparsers.add_parser('auto', help='Auto: training + trading')
    auto_parser.add_argument('--train-days', type=float, default=0.1)
    auto_parser.add_argument('--mode', choices=['normal', 'aggressive'], default='normal')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'trade':
            if args.trade_mode == 'normal':
                print("🚀 Avvio Trading Normale...")
                subprocess.run([sys.executable, 'src/simple_dual_ai.py'], cwd=project_root)
            
            elif args.trade_mode == 'aggressive':
                print(f"🔥 Avvio Trading Aggressivo (livello {args.aggressiveness})...")
                subprocess.run([
                    sys.executable, 'src/aggressive_trader.py', 
                    '--aggressiveness', str(args.aggressiveness)
                ], cwd=project_root)
        
        elif args.command == 'train':
            print(f"🧠 Avvio AI Training per {args.days} giorni...")
            cmd = [sys.executable, 'src/ai_background_trainer.py', '--days', str(args.days)]
            if args.symbols:
                cmd.extend(['--symbols'] + args.symbols)
            subprocess.run(cmd, cwd=project_root)
        
        elif args.command == 'dashboard':
            print("📊 Avvio Dashboard Live...")
            # Usa il virtual environment corretto
            venv_python = project_root / ".venv" / "bin" / "python"
            if venv_python.exists():
                python_exec = str(venv_python)
            else:
                python_exec = sys.executable
            
            os.chdir(project_root / "dashboard")
            subprocess.run([python_exec, '-m', 'streamlit', 'run', 'live_dashboard.py', '--server.port', '8501'])
        
        elif args.command == 'test':
            if args.test_type == 'realtime':
                print("🧪 Test Real-Time Data...")
                subprocess.run([sys.executable, 'tests/test_realtime.py'], cwd=project_root)
            
            elif args.test_type == 'api':
                print("🧪 Test API...")
                subprocess.run([sys.executable, 'tests/test_dual_ai_minimal.py'], cwd=project_root)
            
            elif args.test_type == 'dual-ai':
                print("🧪 Test Dual AI...")
                subprocess.run([sys.executable, 'tests/test_dual_ai_minimal.py'], cwd=project_root)
            
            elif args.test_type == 'training':
                print("🧪 Test AI Training...")
                subprocess.run([sys.executable, 'tests/test_ai_training.py'], cwd=project_root)
        
        elif args.command == 'status':
            print("📋 Verifica Stato Sistema...")
            subprocess.run([sys.executable, 'tests/test_system.py'], cwd=project_root)
        
        elif args.command == 'smart':
            if args.smart_mode == 'check':
                print("🔍 Verifica AI Readiness...")
                subprocess.run([sys.executable, 'src/smart_trading_system.py', 'check'], cwd=project_root)
            
            elif args.smart_mode == 'auto':
                print(f"🤖 Auto System: {args.train_days} giorni training + {args.mode} trading...")
                subprocess.run([
                    sys.executable, 'src/smart_trading_system.py', 'auto',
                    '--train-days', str(args.train_days),
                    '--mode', args.mode
                ], cwd=project_root)
        
        else:
            parser.print_help()
            print("\n" + "="*60)
            print("🚀 STOCK AI TRADING SYSTEM")
            print("="*60)
            print("📊 Esempi d'uso:")
            print("  python launcher.py trade normal              # Trading normale")
            print("  python launcher.py trade aggressive --aggressiveness 8  # Trading aggressivo")
            print("  python launcher.py train --days 1           # Training 1 giorno") 
            print("  python launcher.py dashboard                # Dashboard live")
            print("  python launcher.py test realtime            # Test dati real-time")
            print("  python launcher.py smart auto --train-days 0.1  # Auto training+trading")
            print("  python launcher.py status                   # Stato sistema")
    
    except KeyboardInterrupt:
        print("\n🛑 Operazione interrotta dall'utente")
    except Exception as e:
        print(f"❌ Errore: {e}")

if __name__ == "__main__":
    main()
