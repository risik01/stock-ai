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
    screen \
    build-essential \
    python3-dev \
    pkg-config \
    libfreetype6-dev \
    libpng-dev \
    libjpeg-dev \
    liblapack-dev \
    libblas-dev \
    gfortran

# 3. CLONA REPOSITORY
echo "📥 Clonazione repository..."
if [[ ! -d "stock-ai" ]]; then
    git clone https://github.com/risik01/stock-ai.git
else
    echo "⚠️ Directory stock-ai già esistente, aggiornamento..."
    cd stock-ai
    git pull origin main
    cd ..
fi

cd stock-ai

# 4. SETUP AMBIENTE PYTHON
echo "🐍 Setup ambiente Python virtuale..."
python3 -m venv .venv
source .venv/bin/activate

# Aggiorna pip
pip install --upgrade pip wheel setuptools

# 5. INSTALLAZIONE DIPENDENZE PYTHON
echo "📦 Installazione dipendenze Python..."
pip install -r requirements.txt

# Dipendenze aggiuntive per produzione
pip install schedule psutil

# 6. CREAZIONE DIRECTORY
echo "📁 Creazione directory necessarie..."
mkdir -p logs
mkdir -p data
mkdir -p config
mkdir -p backups

# 7. CONFIGURAZIONE
echo "⚙️ Setup configurazione..."

# Copia configurazione di produzione
cp config/production_settings.json config/settings.json

# 8. PERMESSI
echo "🔐 Impostazione permessi..."
chmod +x automated_trading_system.py
chmod +x setup_ubuntu.sh

# 9. SERVIZIO SYSTEMD (opzionale)
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
Environment=PATH=$CURRENT_DIR/.venv/bin
ExecStart=$CURRENT_DIR/.venv/bin/python $CURRENT_DIR/automated_trading_system.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable trading-ai
    
    echo "✅ Servizio trading-ai installato"
    echo "   Usa: sudo systemctl start trading-ai"
    echo "   Logs: sudo journalctl -u trading-ai -f"
fi

# 10. SCRIPT DI CONTROLLO
echo "📜 Creazione script di controllo..."

cat > trading_control.sh << 'EOF'
#!/bin/bash
# Script di controllo Trading AI System

case "$1" in
    start)
        echo "🚀 Avvio Trading AI System..."
        source .venv/bin/activate
        nohup python automated_trading_system.py > logs/system.log 2>&1 &
        echo $! > trading_ai.pid
        echo "✅ Sistema avviato (PID: $(cat trading_ai.pid))"
        ;;
    stop)
        if [[ -f trading_ai.pid ]]; then
            PID=$(cat trading_ai.pid)
            echo "🛑 Stopping Trading AI System (PID: $PID)..."
            kill $PID
            rm trading_ai.pid
            echo "✅ Sistema fermato"
        else
            echo "❌ Sistema non in esecuzione"
        fi
        ;;
    status)
        if [[ -f trading_ai.pid ]] && kill -0 $(cat trading_ai.pid) 2>/dev/null; then
            echo "✅ Sistema in esecuzione (PID: $(cat trading_ai.pid))"
        else
            echo "❌ Sistema non in esecuzione"
        fi
        ;;
    logs)
        echo "📊 Ultimi log:"
        tail -f logs/system.log
        ;;
    performance)
        echo "📈 Performance report:"
        find logs -name "performance_report_*.json" -exec ls -la {} \; | tail -5
        ;;
    *)
        echo "Uso: $0 {start|stop|status|logs|performance}"
        exit 1
        ;;
esac
EOF

chmod +x trading_control.sh

# 11. TEST SISTEMA
echo "🧪 Test componenti sistema..."
source .venv/bin/activate

echo "  - Test import moduli..."
python -c "
import sys
sys.path.append('src')
sys.path.append('trading-new')
try:
    from src.portfolio import Portfolio
    from src.data_collector import DataCollector
    from trading_new.news_rss_collector import NewsRSSCollector
    print('✅ Import moduli OK')
except Exception as e:
    print(f'❌ Errore import: {e}')
    exit(1)
"

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
    python -c "
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

echo
echo "🎉 SETUP COMPLETATO!"
echo "==================="
echo
echo "📋 COMANDI DISPONIBILI:"
echo "  ./trading_control.sh start    - Avvia sistema"
echo "  ./trading_control.sh stop     - Ferma sistema"
echo "  ./trading_control.sh status   - Stato sistema"
echo "  ./trading_control.sh logs     - Visualizza log"
echo "  ./monitor_system.sh          - Monitor completo"
echo "  ./backup_data.sh             - Backup dati"
echo
echo "🚀 AVVIO RAPIDO:"
echo "  1. ./trading_control.sh start"
echo "  2. ./trading_control.sh logs  (in altro terminale)"
echo
echo "⚙️ CONFIGURAZIONE:"
echo "  - Budget: €1000 (config/settings.json)"
echo "  - Simboli: AAPL, GOOGL, MSFT, TSLA, AMZN, META, NVDA"
echo "  - News AI: Abilitato con 10 RSS feeds"
echo "  - RL Agent: Abilitato per decisioni automatiche"
echo
echo "📊 MONITORING:"
echo "  - Logs: logs/"
echo "  - Performance: logs/performance_report_*.json"
echo "  - Health checks ogni 30 minuti"
echo
echo "🔒 SICUREZZA:"
echo "  - Max loss giornaliero: 5%"
echo "  - Max trades/giorno: 10"
echo "  - Emergency stop attivato"
echo
echo "✨ Sistema pronto per trading multi-giorno!"

# Attiva ambiente per utente
echo
echo "🔧 Per attivare l'ambiente:"
echo "  source .venv/bin/activate"
