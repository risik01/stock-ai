#!/usr/bin/env python3
"""
Smart Trading System con AI Training integrato
Sistema completo che può training e trading
"""

import os
import sys
import json
import argparse
import asyncio
import logging
from pathlib import Path
from datetime import datetime

sys.path.append('src')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SmartTradingSystem:
    """Sistema di trading intelligente con AI training"""
    
    def __init__(self):
        self.knowledge_base_path = "../logs/training/ai_knowledge_latest.pkl"  # Corretto path
        self.is_trained = False
        
    def check_ai_readiness(self):
        """Controlla se l'AI è stata addestrata"""
        kb_path = Path(self.knowledge_base_path)
        
        if kb_path.exists():
            # Controlla età e qualità della knowledge base
            from ai_background_trainer import AIKnowledgeBase
            kb = AIKnowledgeBase()
            if kb.load_knowledge_base(kb_path):
                # Verifica requisiti minimi
                min_observations = 1000
                min_accuracy = 0.4  # 40% minimo
                
                if (kb.total_observations >= min_observations and 
                    kb.accuracy_metrics['prediction_accuracy'] >= min_accuracy):
                    
                    logger.info(f"✅ AI pronta per trading!")
                    logger.info(f"📊 Osservazioni: {kb.total_observations}")
                    logger.info(f"🎯 Accuratezza: {kb.accuracy_metrics['prediction_accuracy']:.2%}")
                    self.is_trained = True
                    return True
                else:
                    logger.warning(f"⚠️ AI non sufficientemente addestrata")
                    logger.warning(f"📊 Osservazioni: {kb.total_observations}/{min_observations}")
                    logger.warning(f"🎯 Accuratezza: {kb.accuracy_metrics['prediction_accuracy']:.2%}/{min_accuracy:.0%}")
                    return False
        
        logger.warning(f"❌ Nessuna knowledge base trovata: {kb_path}")
        return False
    
    async def train_ai(self, days=1):
        """Addestra l'AI in background"""
        logger.info(f"🧠 Avvio training AI per {days} giorni...")
        
        from ai_background_trainer import AIBackgroundTrainer
        trainer = AIBackgroundTrainer()
        
        # Carica knowledge base esistente se presente
        if Path(self.knowledge_base_path).exists():
            trainer.knowledge_base.load_knowledge_base(self.knowledge_base_path)
            logger.info("📖 Knowledge base esistente caricata")
        
        # Avvia training
        await trainer.start_training(duration_days=days)
        
        # Salva knowledge base
        trainer.knowledge_base.save_knowledge_base(self.knowledge_base_path)
        logger.info(f"💾 Knowledge base salvata: {self.knowledge_base_path}")
    
    async def start_trading(self, mode='normal'):
        """Avvia trading con AI addestrata"""
        if not self.check_ai_readiness():
            logger.error("❌ AI non pronta per trading! Eseguire prima il training.")
            return False
        
        logger.info(f"🚀 Avvio trading in modalità {mode}")
        
        if mode == 'aggressive':
            from aggressive_trader import main as aggressive_main
            # Nota: aggressive_main() è sincrono, quindi lo wrapppiamo
            await asyncio.get_event_loop().run_in_executor(None, aggressive_main)
        else:
            # Avvia dual AI normale
            from simple_dual_ai import main as dual_ai_main
            await dual_ai_main()
    
    def start_dashboard(self):
        """Avvia dashboard live"""
        logger.info("📊 Avvio dashboard live...")
        dashboard_path = Path(__file__).parent.parent / "dashboard" / "live_dashboard.py"
        os.system(f"cd {dashboard_path.parent} && python -m streamlit run live_dashboard.py --server.port 8501")

def main():
    """Funzione principale"""
    parser = argparse.ArgumentParser(description='Smart Trading System con AI Training')
    
    subparsers = parser.add_subparsers(dest='command', help='Comandi disponibili')
    
    # Comando training
    train_parser = subparsers.add_parser('train', help='Addestra AI in background')
    train_parser.add_argument('--days', type=float, default=1, help='Giorni di training')
    
    # Comando trading
    trade_parser = subparsers.add_parser('trade', help='Avvia trading con AI addestrata')
    trade_parser.add_argument('--mode', choices=['normal', 'aggressive'], default='normal', help='Modalità trading')
    
    # Comando check
    check_parser = subparsers.add_parser('check', help='Verifica stato AI')
    
    # Comando dashboard
    dash_parser = subparsers.add_parser('dashboard', help='Avvia dashboard live')
    
    # Comando completo
    auto_parser = subparsers.add_parser('auto', help='Auto: training poi trading')
    auto_parser.add_argument('--train-days', type=float, default=0.1, help='Giorni di training iniziale')
    auto_parser.add_argument('--mode', choices=['normal', 'aggressive'], default='normal', help='Modalità trading')
    
    args = parser.parse_args()
    
    # Crea sistema
    system = SmartTradingSystem()
    
    try:
        if args.command == 'train':
            asyncio.run(system.train_ai(days=args.days))
        
        elif args.command == 'trade':
            asyncio.run(system.start_trading(mode=args.mode))
        
        elif args.command == 'check':
            system.check_ai_readiness()
        
        elif args.command == 'dashboard':
            system.start_dashboard()
        
        elif args.command == 'auto':
            async def auto_sequence():
                # Prima addestra
                logger.info(f"🎓 Fase 1: Training AI per {args.train_days} giorni")
                await system.train_ai(days=args.train_days)
                
                # Poi avvia trading
                logger.info(f"🚀 Fase 2: Avvio trading modalità {args.mode}")
                await system.start_trading(mode=args.mode)
            
            asyncio.run(auto_sequence())
        
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        logger.info("🛑 Sistema fermato dall'utente")
    except Exception as e:
        logger.error(f"❌ Errore: {e}")

if __name__ == "__main__":
    main()
