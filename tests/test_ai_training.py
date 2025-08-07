#!/usr/bin/env python3
"""
Test AI Background Training System
"""

import sys
import time
import asyncio
sys.path.append('../src')  # Torna indietro e vai in src

print("🧠 === TEST AI BACKGROUND TRAINING ===")

async def test_short_training():
    """Test training breve"""
    from ai_background_trainer import AIBackgroundTrainer
    
    # Crea trainer
    trainer = AIBackgroundTrainer()
    
    print("✅ Trainer creato")
    print("🚀 Avvio training di 1 minuto per test...")
    
    # Training di 1 minuto per test
    await trainer.start_training(duration_days=1/1440)  # 1 minuto = 1/1440 giorni
    
    print("🏁 Test completato!")

if __name__ == "__main__":
    try:
        asyncio.run(test_short_training())
    except KeyboardInterrupt:
        print("🛑 Test interrotto")
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()
