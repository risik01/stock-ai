#!/bin/bash

# 🚀 Stock AI Trading System v4.0 - Setup Ubuntu
# Installazione automatica per produzione

set -e

echo "🚀 STOCK AI TRADING SYSTEM v4.0 - SETUP UBUNTU"
echo "=================================================="
echo "📅 $(date)"
echo ""

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funzioni helper
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verifica OS
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    log_error "Questo script è per Ubuntu/Linux. OS rilevato: $OSTYPE"
    exit 1
fi

log_info "Verifica privilegi sudo..."
if ! sudo -v; then
    log_error "Sono necessari privilegi sudo"
    exit 1
fi

log_success "Sistema Ubuntu rilevato"

# Update sistema
log_info "Aggiornamento pacchetti sistema..."
sudo apt update && sudo apt upgrade -y

# Installazione Python 3.12+
log_info "Verifica Python..."
if ! command -v python3 &> /dev/null; then
    log_info "Installazione Python 3..."
    sudo apt install -y python3 python3-pip python3-venv
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
log_success "Python $PYTHON_VERSION installato"

# Installazione dipendenze sistema
log_info "Installazione dipendenze sistema..."
sudo apt install -y \
    curl \
    wget \
    git \
    htop \
    screen \
    tmux \
    nano \
    tree \
    jq \
    python3-dev \
    build-essential

# Verifica Git
if ! command -v git &> /dev/null; then
    log_error "Git non installato"
    exit 1
fi

# Setup directory
PROJECT_DIR="$(pwd)"
log_info "Directory progetto: $PROJECT_DIR"

# Creazione virtual environment
log_info "Creazione Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    log_success "Virtual environment creato"
else
    log_warning "Virtual environment già esistente"
fi

# Attivazione venv e installazione dipendenze
log_info "Attivazione virtual environment..."
source .venv/bin/activate

log_info "Upgrade pip..."
pip install --upgrade pip

log_info "Installazione dipendenze Python..."
pip install yfinance pandas numpy requests textblob flask python-dotenv

# Download corpora per sentiment analysis
log_info "Download TextBlob corpora..."
python -m textblob.download_corpora

# Creazione directory necessarie
log_info "Creazione directory sistema..."
mkdir -p data logs config templates

# Verifica file .env
if [ ! -f ".env" ]; then
    log_warning "File .env non trovato. Creazione template..."
    cat > .env << EOF
# Trading AI System - API Keys Configuration
# Configura le tue API keys qui

# API Keys per trading (RICHIESTE)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
FINNHUB_API_KEY=your_finnhub_key_here

# API Keys opzionali per news
NEWS_API_KEY=your_news_api_key_here
TWITTER_BEARER_TOKEN=

# Configurazioni opzionali
DEBUG_MODE=false
LOG_LEVEL=INFO
EOF
    log_warning "IMPORTANTE: Configura le API keys in .env"
else
    log_success "File .env già configurato"
fi

# Impostazione permessi
log_info "Impostazione permessi..."
chmod +x bin/*.sh 2>/dev/null || true
chmod +x launch.sh 2>/dev/null || true

# Test installazione
log_info "Test installazione..."
if python -c "import yfinance, pandas, numpy, requests, textblob, flask; print('✅ Tutti i moduli importati correttamente')" 2>/dev/null; then
    log_success "Test dipendenze Python: OK"
else
    log_error "Errore nell'importazione moduli Python"
    exit 1
fi

# Setup servizio systemd (opzionale)
read -p "🤖 Vuoi configurare il servizio systemd per avvio automatico? (y/N): " setup_service
if [[ $setup_service =~ ^[Yy]$ ]]; then
    log_info "Configurazione servizio systemd..."
    
    sudo tee /etc/systemd/system/stock-ai.service > /dev/null << EOF
[Unit]
Description=Stock AI Trading System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/.venv/bin
ExecStart=$PROJECT_DIR/.venv/bin/python $PROJECT_DIR/src/simple_dual_ai.py
Restart=on-failure
RestartSec=5
StandardOutput=append:$PROJECT_DIR/logs/systemd.log
StandardError=append:$PROJECT_DIR/logs/systemd.log

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable stock-ai.service
    log_success "Servizio systemd configurato"
    log_info "Comandi utili:"
    log_info "  sudo systemctl start stock-ai    # Avvia servizio"
    log_info "  sudo systemctl stop stock-ai     # Ferma servizio"
    log_info "  sudo systemctl status stock-ai   # Stato servizio"
fi

# Setup monitoring con crontab (opzionale)
read -p "📊 Vuoi configurare il monitoring automatico? (y/N): " setup_monitoring
if [[ $setup_monitoring =~ ^[Yy]$ ]]; then
    log_info "Configurazione crontab per monitoring..."
    
    # Backup crontab esistente
    crontab -l > /tmp/crontab.backup 2>/dev/null || true
    
    # Aggiungi job di monitoring
    (crontab -l 2>/dev/null; echo "# Stock AI Monitoring") | crontab -
    (crontab -l 2>/dev/null; echo "0 */6 * * * cd $PROJECT_DIR && $PROJECT_DIR/.venv/bin/python src/main.py --system-status >> logs/monitoring.log 2>&1") | crontab -
    (crontab -l 2>/dev/null; echo "0 0 * * * cd $PROJECT_DIR && tar -czf backups/backup_\$(date +\%Y\%m\%d).tar.gz data/ logs/") | crontab -
    
    # Crea directory backup
    mkdir -p backups
    
    log_success "Monitoring automatico configurato"
    log_info "Backup giornaliero: backups/"
    log_info "Log monitoring: logs/monitoring.log"
fi

echo ""
echo "🎉 INSTALLAZIONE COMPLETATA!"
echo "================================"
log_success "Setup Ubuntu completato con successo"
log_info "Directory progetto: $PROJECT_DIR"
log_info "Virtual environment: $PROJECT_DIR/.venv"

echo ""
echo "📋 PROSSIMI PASSI:"
echo "==================="
echo "1. 🔑 Configura API keys:"
echo "   nano .env"
echo ""
echo "2. 🧪 Test sistema (demo sicuro):"
echo "   source .venv/bin/activate"
echo "   python src/simple_dual_ai.py --demo"
echo ""
echo "3. 🌐 Dashboard web:"
echo "   python src/main.py --dashboard"
echo "   # Apri http://localhost:5000"
echo ""
echo "4. 🚀 Trading live (ATTENZIONE!):"
echo "   python src/simple_dual_ai.py --live"
echo ""
echo "5. 📊 Monitoring:"
echo "   python src/main.py --system-status"
echo ""

if [[ $setup_service =~ ^[Yy]$ ]]; then
    echo "6. 🤖 Servizio automatico:"
    echo "   sudo systemctl start stock-ai"
    echo ""
fi

log_warning "IMPORTANTE: Configura sempre le API keys prima dell'uso"
log_warning "Inizia sempre con la modalità demo per test"

echo ""
echo "📖 Documentazione completa:"
echo "https://github.com/risik01/stock-ai/wiki"
echo ""
echo "🚀 Happy Trading! 📈"
