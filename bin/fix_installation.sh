#!/bin/bash
# Fix script per installazione Ubuntu

echo "🔧 FIX INSTALLAZIONE UBUNTU"
echo "=========================="

# 1. Pulizia directory duplicate
echo "🧹 Pulizia directory duplicate..."
if [[ -d "stock-ai" ]]; then
    echo "  - Rimuovo directory stock-ai duplicata"
    rm -rf stock-ai
fi

# 2. Verifica struttura corretta
echo "📂 Verifica struttura directory..."
if [[ ! -f "automated_trading_system.py" ]]; then
    echo "❌ File principale non trovato!"
    echo "💡 Assicurati di essere nella directory stock-ai principale"
    exit 1
fi

# 3. Attiva ambiente virtuale
echo "🐍 Attivazione ambiente virtuale..."
if [[ ! -d ".venv" ]]; then
    echo "❌ Ambiente virtuale non trovato, creazione..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# 4. Test imports con fix paths
echo "🧪 Test import con fix paths..."
python -c "
import sys
import os

# Setup paths corretti
current_dir = os.getcwd()
sys.path.insert(0, os.path.join(current_dir, 'src'))
sys.path.insert(0, os.path.join(current_dir, 'trading-new'))
sys.path.insert(0, current_dir)

print('📁 Paths configurati:')
for p in sys.path[:5]:
    if 'stock-ai' in p or p == current_dir:
        print(f'  - {p}')

print()
print('🔍 Test imports...')

try:
    # Test basic imports
    import pandas as pd
    import numpy as np
    print('✅ Pandas/Numpy OK')
    
    # Test trading-new
    from trading_new.news_rss_collector import NewsRSSCollector
    print('✅ NewsRSSCollector OK')
    
    # Test src
    from src.data_collector import DataCollector
    print('✅ DataCollector OK')
    
    from src.portfolio import Portfolio
    print('✅ Portfolio OK')
    
    print()
    print('🎉 TUTTI GLI IMPORT RIUSCITI!')
    
except ImportError as e:
    print(f'❌ Errore import: {e}')
    print()
    print('📋 File Python disponibili:')
    
    # Mostra file src/
    if os.path.exists('src'):
        print('  src/:')
        for f in os.listdir('src'):
            if f.endswith('.py'):
                print(f'    - {f}')
    
    # Mostra file trading-new/
    if os.path.exists('trading-new'):
        print('  trading-new/:')
        for f in os.listdir('trading-new'):
            if f.endswith('.py'):
                print(f'    - {f}')
    
    exit(1)
"

if [ $? -eq 0 ]; then
    echo
    echo "✅ Fix completato con successo!"
    echo
    echo "🚀 Per avviare il sistema:"
    echo "  ./trading_control.sh start"
    echo
    echo "📊 Per monitorare:"
    echo "  ./trading_control.sh logs"
else
    echo
    echo "❌ Fix non riuscito, debug necessario"
fi
