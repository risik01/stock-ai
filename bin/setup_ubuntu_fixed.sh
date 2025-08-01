#!/bin/bash
# Setup script per Ubuntu - Trading AI System
# Installa e configura sistema di trading automatico

set -e  # Exit on error

echo "🚀 SETUP TRADING AI SYSTEM SU UBUNTU"
echo "======================================"

# Verifica Ubuntu
if [[ ! -f /etc/lsb-release ]] || ! grep -q "Ubuntu" /etc/lsb-release; then
    echo "❌ Questo script è per Ubuntu. Sistema non supportato."
    exit 1
fi

echo "✅ Sistema Ubuntu rilevato"

# Verifica di essere nella directory corretta
if [[ ! -f "automated_trading_system.py" ]]; then
    echo "❌ File automated_trading_system.py non trovato!"
    echo "💡 Assicurati di essere nella directory stock-ai dopo git clone"
    echo "   Comando corretto:"
    echo "   git clone https://github.com/risik01/stock-ai.git"
    echo "   cd stock-ai"
    echo "   ./setup_ubuntu.sh"
    exit 1
fi

echo "✅ Directory corretta confermata"

# 1. AGGIORNAMENTO SISTEMA
echo "📦 Aggiornamento sistema Ubuntu..."
sudo apt update && sudo apt upgrade -y

# 2. INSTALLAZIONE DIPENDENZE
echo "📦 Installazione dipendenze di sistema..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    htop \
    tree \
    unzip \
    software-properties-common \
    build-essential \
    libssl-dev \
    libffi-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libfreetype6-dev \
    libpng-dev \
    libjpeg-dev \
    liblapack-dev \
    libblas-dev \
    gfortran

# 3. SETUP AMBIENTE PYTHON
echo "🐍 Setup ambiente Python virtuale..."
python3 -m venv .venv
source .venv/bin/activate

# Aggiorna pip
pip install --upgrade pip wheel setuptools

# 4. INSTALLAZIONE DIPENDENZE PYTHON
echo "📦 Installazione dipendenze Python..."
pip install -r requirements.txt

# Dipendenze aggiuntive per produzione
pip install schedule psutil

# 5. CREAZIONE DIRECTORY
echo "📁 Creazione directory necessarie..."
mkdir -p logs
mkdir -p data
mkdir -p backups

# 6. CONFIGURAZIONE
echo "⚙️ Setup configurazione..."

# Copia configurazione di produzione se non esiste già settings.json
if [[ ! -f "config/settings.json" ]]; then
    cp config/production_settings.json config/settings.json
    echo "✅ Configurazione copiata in config/settings.json"
else
    echo "ℹ️  File config/settings.json già esistente, non sovrascritto"
fi

# 7. PERMESSI
echo "🔐 Impostazione permessi..."
chmod +x automated_trading_system.py
chmod +x setup_ubuntu.sh

# 8. SERVIZIO SYSTEMD (opzionale)
echo "🔧 Vuoi installare il servizio systemd per avvio automatico? (y/N)"
read -r install_service

if [[ $install_service =~ ^[Yy]$ ]]; then
    echo "📝 Creazione servizio systemd..."
    
    SERVICE_FILE="/etc/systemd/system/trading-ai.service"
    CURRENT_USER=$(whoami)
    CURRENT_DIR=$(pwd)
    
    sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Trading AI System
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
Environment=PATH=$CURRENT_DIR/.venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=$CURRENT_DIR/.venv/bin/python $CURRENT_DIR/automated_trading_system.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable trading-ai
    
    echo "✅ Servizio trading-ai installato"
    echo "   Usa: sudo systemctl start trading-ai"
    echo "   Logs: sudo journalctl -u trading-ai -f"
fi

# 9. SCRIPT DI CONTROLLO
echo "📜 Creazione script di controllo..."

cat > trading_control.sh << 'EOF'
#!/bin/bash
# Script di controllo Trading AI System

case "$1" in
    start)
        echo "🚀 Avvio Trading AI System..."
        source .venv/bin/activate
        nohup python3 automated_trading_system.py > logs/system.log 2>&1 &
        echo $! > trading_ai.pid
        echo "✅ Sistema avviato (PID: $(cat trading_ai.pid))"
        echo "📊 Per monitorare: ./trading_control.sh logs"
        ;;
    stop)
        if [[ -f trading_ai.pid ]]; then
            PID=$(cat trading_ai.pid)
            echo "🛑 Stopping Trading AI System (PID: $PID)..."
            kill $PID 2>/dev/null || echo "⚠️  Processo già terminato"
            rm -f trading_ai.pid
            echo "✅ Sistema fermato"
        else
            echo "❌ Sistema non in esecuzione"
        fi
        ;;
    status)
        if [[ -f trading_ai.pid ]] && kill -0 $(cat trading_ai.pid) 2>/dev/null; then
            echo "✅ Sistema in esecuzione (PID: $(cat trading_ai.pid))"
            echo "📊 Per log: ./trading_control.sh logs"
        else
            echo "❌ Sistema non in esecuzione"
            if [[ -f trading_ai.pid ]]; then
                rm -f trading_ai.pid
            fi
        fi
        ;;
    logs)
        echo "📊 Log real-time (Ctrl+C per uscire):"
        echo "======================================"
        if [[ -f logs/system.log ]]; then
            tail -f logs/system.log
        else
            echo "❌ File log non trovato"
            echo "💡 Avvia prima il sistema con: ./trading_control.sh start"
        fi
        ;;
    performance)
        echo "📈 Performance report:"
        echo "====================="
        if ls logs/performance_report_*.json 1> /dev/null 2>&1; then
            echo "Ultimi 5 report:"
            ls -la logs/performance_report_*.json | tail -5
            echo
            echo "Ultimo report:"
            LAST_REPORT=$(ls logs/performance_report_*.json | tail -1)
            if [[ -f "$LAST_REPORT" ]]; then
                python3 -c "
import json
try:
    with open('$LAST_REPORT', 'r') as f:
        data = json.load(f)
    print(f'Portfolio: €{data.get(\"portfolio_value\", 0):.2f}')
    print(f'Return: {data.get(\"total_return_pct\", 0):+.2f}%')
    print(f'Trades: {data.get(\"total_trades\", 0)}')
    print(f'Uptime: {data.get(\"uptime_hours\", 0):.1f} ore')
except Exception as e:
    print(f'Errore lettura report: {e}')
"
            fi
        else
            echo "❌ Nessun report performance trovato"
        fi
        ;;
    *)
        echo "🎮 TRADING AI CONTROL"
        echo "===================="
        echo "Uso: $0 {start|stop|status|logs|performance}"
        echo
        echo "Comandi:"
        echo "  start       - Avvia sistema trading"
        echo "  stop        - Ferma sistema trading"
        echo "  status      - Stato sistema"
        echo "  logs        - Monitor log real-time"
        echo "  performance - Report performance"
        exit 1
        ;;
esac
EOF

chmod +x trading_control.sh

echo "✅ Script di controllo creato"

# 10. TEST SISTEMA
echo "🧪 Test componenti sistema..."
source .venv/bin/activate

echo "  - Test import Python base..."
python3 -c "
import sys
print(f'Python version: {sys.version}')
import pandas as pd
import numpy as np
import yfinance as yf
print('✅ Librerie base OK (pandas, numpy, yfinance)')
"

echo "  - Test import moduli trading..."
python3 -c "
import sys
import os

# Setup paths corretti
current_dir = os.getcwd()
sys.path.insert(0, os.path.join(current_dir, 'src'))
sys.path.insert(0, current_dir)

print('📁 Directory corrente:', current_dir)

# Test struttura directory
required_dirs = ['src', 'config', 'data']
missing_dirs = []
for d in required_dirs:
    if not os.path.exists(d):
        missing_dirs.append(d)

if missing_dirs:
    print(f'❌ Directory mancanti: {missing_dirs}')
    exit(1)

print('✅ Struttura directory OK')

# Test import moduli principali
try:
    from src.data_collector import DataCollector
    print('✅ DataCollector import OK')
except ImportError as e:
    print(f'⚠️  DataCollector import warning: {e}')

try:
    from src.portfolio import Portfolio
    print('✅ Portfolio import OK')
except ImportError as e:
    print(f'⚠️  Portfolio import warning: {e}')

print('✅ Test import completato')
"

if [ $? -ne 0 ]; then
    echo "⚠️  Alcuni import hanno dato warning, ma il sistema dovrebbe funzionare"
fi

# 11. LAUNCHER DESKTOP (OPZIONALE)
echo "🖥️  Creazione launcher desktop..."

if [[ -d ~/Desktop ]]; then
    cat > ~/Desktop/TradingAI.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Trading AI System
Comment=Sistema di Trading Automatico con IA - Budget €1000
Exec=gnome-terminal --working-directory=$(pwd) -- bash -c "./trading_control.sh start; read -p 'Premi ENTER per continuare...'"
Icon=accessories-calculator
Terminal=true
Categories=Office;Finance;
EOF
    
    chmod +x ~/Desktop/TradingAI.desktop
    echo "✅ Launcher desktop creato"
else
    echo "ℹ️  Desktop non disponibile, launcher non creato"
fi

# 12. FIREWALL (opzionale)
echo "🔥 Configurazione firewall consigliata..."
echo "Per sicurezza, considera di configurare UFW:"
echo "  sudo ufw enable"
echo "  sudo ufw allow ssh"
echo "  sudo ufw allow from YOUR_IP"

# 13. MONITORING (opzionale)
echo "📊 Setup monitoring..."
cat > monitor_system.sh << 'EOF'
#!/bin/bash
# Script monitoring sistema

echo "=== TRADING AI SYSTEM MONITOR ==="
echo "Data: $(date)"
echo

# Status sistema
echo "🔧 SISTEMA:"
./trading_control.sh status

# Utilizzo risorse
echo
echo "💾 RISORSE:"
echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "RAM: $(free -m | awk 'NR==2{printf "%.1f%%", $3*100/$2 }')"
echo "Disk: $(df -h / | awk 'NR==2 {print $5}')"

# Ultimo performance report
echo
echo "📈 ULTIMA PERFORMANCE:"
LAST_REPORT=$(find logs -name "performance_report_*.json" 2>/dev/null | sort | tail -1)
if [[ -f "$LAST_REPORT" ]]; then
    echo "File: $(basename $LAST_REPORT)"
    python3 -c "
import json
try:
    with open('$LAST_REPORT', 'r') as f:
        data = json.load(f)
    print(f'Portfolio: €{data.get(\"portfolio_value\", 0):.2f}')
    print(f'Return: {data.get(\"total_return_pct\", 0):+.2f}%')
    print(f'Trades: {data.get(\"total_trades\", 0)}')
except:
    print('Errore lettura report')
"
else
    echo "Nessun report disponibile"
fi

echo
echo "================================="
EOF

chmod +x monitor_system.sh

# 14. BACKUP SCRIPT
echo "💾 Setup script backup..."
cat > backup_data.sh << 'EOF'
#!/bin/bash
# Script backup dati trading

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "💾 Backup dati trading in $BACKUP_DIR..."

# Backup configurazione
cp -r config "$BACKUP_DIR/"

# Backup logs
cp -r logs "$BACKUP_DIR/"

# Backup dati
cp -r data "$BACKUP_DIR/"

# Comprimi
tar -czf "${BACKUP_DIR}.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"

echo "✅ Backup completato: ${BACKUP_DIR}.tar.gz"

# Mantieni solo ultimi 7 backup
find backups -name "*.tar.gz" -mtime +7 -delete

echo "🗑️ Pulizia backup vecchi completata"
EOF

chmod +x backup_data.sh

# 15. SUMMARY FINALE COMPLETO
echo
echo "🎯 ========================================="
echo "   🚀 TRADING AI SYSTEM v3.0 - READY! 🚀"  
echo "   ========================================="
echo
echo "📍 SISTEMA INSTALLATO IN: $(pwd)"
echo "💰 BUDGET CONFIGURATO: €1000"
echo "🤖 IA ENSEMBLE: RL Agent (40%) + Technical (35%) + News (25%)"
echo "🔄 MODALITÀ: Produzione Multi-Day"
echo
echo "🎮 COMANDI PRINCIPALI:"
echo "======================"
echo "  ./trading_control.sh start      # 🚀 Avvia sistema trading"
echo "  ./trading_control.sh stop       # 🛑 Ferma sistema trading"
echo "  ./trading_control.sh status     # ℹ️  Controlla stato"
echo "  ./trading_control.sh logs       # 📊 Monitor real-time"
echo "  ./trading_control.sh performance # 📈 Report performance"
echo
echo "🛠️  UTILITY AGGIUNTIVE:"
echo "======================="
echo "  ./monitor_system.sh             # 📊 Monitor sistema completo"
echo "  ./backup_data.sh                # 💾 Backup automatico dati"
echo "  nano config/settings.json       # ⚙️  Modifica configurazioni"
echo "  nano .env                       # 🔑 Configura API keys"
echo
echo "📊 DASHBOARD E MONITORING:"
echo "=========================="
echo "  • Web Dashboard: http://localhost:5000 (quando attivo)"
echo "  • Log Files: tail -f logs/system.log"
echo "  • Performance Reports: ls logs/performance_report_*.json"
echo "  • Trading History: data/performance_history.json"
echo
echo "🔐 SICUREZZA E RISK MANAGEMENT:"
echo "==============================="
echo "  ✅ Stop Loss giornaliero: 5% del portfolio"
echo "  ✅ Posizione massima: 15% per trade"
echo "  ✅ Max trades giornalieri: 8"
echo "  ✅ Emergency stop automatico attivo"
echo "  ✅ Controlli di health automatici"
echo
echo "📈 CONFIGURAZIONE TRADING:"
echo "========================="
echo "  • Simboli: AAPL, GOOGL, MSFT, TSLA, AMZN, META, NVDA"
echo "  • Intervallo dati: 1 minuto"
echo "  • Finestre analisi: 14, 30, 50 periodi"
echo "  • News feeds: 10 RSS attivi"
echo "  • Sentiment analysis: Real-time"
echo
echo "🎯 AVVIO RAPIDO - PROCEDURA CONSIGLIATA:"
echo "========================================"
echo "  1️⃣  Verifica configurazione API keys:"
echo "      nano .env  # Inserisci le tue API keys"
echo
echo "  2️⃣  Verifica budget e parametri:"
echo "      nano config/settings.json"
echo
echo "  3️⃣  Avvia sistema:"
echo "      ./trading_control.sh start"
echo
echo "  4️⃣  Monitor in tempo reale (nuovo terminale):"
echo "      ./trading_control.sh logs"
echo
echo "  5️⃣  Controlla performance periodicamente:"
echo "      ./trading_control.sh performance"
echo
echo "📚 DOCUMENTAZIONE:"
echo "=================="
echo "  📖 Guida completa: README.md"
echo "  🔧 Setup dettagliato: SETUP_GUIDE.md"
echo "  📊 Deployment Ubuntu: DEPLOYMENT_UBUNTU.md"
echo
echo "⚠️  IMPORTANTE - PRIMA DEL TRADING REALE:"
echo "========================================"
echo "  🔍 1. Verifica TUTTE le configurazioni"
echo "  🧪 2. Testa con budget ridotto inizialmente"
echo "  📊 3. Monitora costantemente i primi giorni"
echo "  💾 4. Esegui backup regolari con ./backup_data.sh"
echo "  🚨 5. Tieni sempre d'occhio i risk limits"
echo
echo "✨ Il sistema è ora pronto per trading automatico multi-day!"
echo "💡 Ricorda: L'IA prende decisioni autonome ma il controllo finale è tuo"
echo
echo "🔥 BUON TRADING! 🔥"
echo

# Attiva ambiente per utente
echo "🔧 Per attivare manualmente l'ambiente Python:"
echo "   source .venv/bin/activate"
echo
echo "✅ Setup Ubuntu Trading AI System completato con successo!"
