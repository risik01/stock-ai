#!/bin/bash

# 🚀 Stock AI Trading System - Master Launcher
# ============================================
# Organizzazione professionale del progetto

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_header() {
    echo -e "${CYAN}"
    echo "🤖 STOCK AI TRADING SYSTEM"
    echo "=========================="
    echo -e "${NC}"
    echo -e "${GREEN}📁 Struttura Professionale:${NC}"
    echo -e "   📂 ${YELLOW}bin/${NC}      - Scripts di controllo"
    echo -e "   📂 ${YELLOW}src/${NC}      - Core trading system"
    echo -e "   📂 ${YELLOW}news/${NC}     - News & sentiment analysis"
    echo -e "   📂 ${YELLOW}dashboard/${NC} - Web interfaces"
    echo -e "   📂 ${YELLOW}config/${NC}   - Configuration files"
    echo -e "   📂 ${YELLOW}data/${NC}     - Logs & data storage"
    echo ""
}

show_systems() {
    echo -e "${CYAN}🎮 SISTEMI DISPONIBILI:${NC}"
    echo ""
    echo -e "${GREEN}1. 🚀 Dual AI System (RACCOMANDATO)${NC}"
    echo -e "   Avvio:  ${YELLOW}./launch.sh dual${NC}"
    echo -e "   Monitor: ${YELLOW}./launch.sh monitor${NC}"
    echo -e "   Status:  ${YELLOW}./launch.sh status${NC}"
    echo ""
    echo -e "${GREEN}2. 📊 Traditional Trading System${NC}"
    echo -e "   Avvio:  ${YELLOW}./launch.sh classic${NC}"
    echo -e "   Control: ${YELLOW}./launch.sh trading${NC}"
    echo ""
    echo -e "${GREEN}3. 📰 News Trading System${NC}"
    echo -e "   Avvio:  ${YELLOW}./launch.sh news${NC}"
    echo ""
    echo -e "${GREEN}4. 🖥️  Web Dashboard${NC}"
    echo -e "   Avvio:  ${YELLOW}./launch.sh web${NC}"
    echo ""
    echo -e "${GREEN}5. 🔧 Sistema Tools${NC}"
    echo -e "   Setup:  ${YELLOW}./launch.sh setup${NC}"
    echo -e "   Test:   ${YELLOW}./launch.sh test${NC}"
    echo -e "   Backup: ${YELLOW}./launch.sh backup${NC}"
}

launch_dual_ai() {
    echo -e "${GREEN}🚀 Avvio Dual AI System...${NC}"
    cd src && python3 simple_dual_ai.py
}

monitor_dual_ai() {
    echo -e "${CYAN}📊 Monitor Dual AI System...${NC}"
    exec bin/dual_ai_monitor.sh live
}

status_dual_ai() {
    echo -e "${CYAN}📋 Status Dual AI System...${NC}"
    exec bin/dual_ai_monitor.sh status
}

launch_classic() {
    echo -e "${GREEN}📊 Avvio Traditional Trading System...${NC}"
    exec bin/trading_control.sh start
}

trading_control() {
    echo -e "${CYAN}🎮 Trading Control Panel...${NC}"
    echo "Comandi: start|stop|status|logs|performance"
    read -p "Comando: " cmd
    exec bin/trading_control.sh "$cmd"
}

launch_news() {
    echo -e "${GREEN}📰 Avvio News Trading System...${NC}"
    cd news && python3 news_based_trading_ai.py
}

launch_web() {
    echo -e "${GREEN}🖥️  Avvio Web Dashboard...${NC}"
    cd dashboard && python3 web_dashboard.py
}

system_setup() {
    echo -e "${YELLOW}🔧 Sistema Setup...${NC}"
    exec bin/initialize_project.sh setup
}

system_test() {
    echo -e "${YELLOW}🧪 Sistema Test...${NC}"
    cd src && python3 test_system.py
}

system_backup() {
    echo -e "${YELLOW}💾 Sistema Backup...${NC}"
    exec bin/backup_data.sh
}

# Menu principale
case "$1" in
    "dual")
        print_header
        launch_dual_ai
        ;;
    "monitor")
        print_header
        monitor_dual_ai
        ;;
    "status")
        print_header  
        status_dual_ai
        ;;
    "classic")
        print_header
        launch_classic
        ;;
    "trading")
        print_header
        trading_control
        ;;
    "news")
        print_header
        launch_news
        ;;
    "web")
        print_header
        launch_web
        ;;
    "setup")
        print_header
        system_setup
        ;;
    "test")
        print_header
        system_test
        ;;
    "backup")
        print_header
        system_backup
        ;;
    "help"|"")
        print_header
        show_systems
        echo ""
        echo -e "${CYAN}💡 Per iniziare: ${YELLOW}./launch.sh dual${NC}"
        ;;
    *)
        echo -e "${RED}❌ Comando non riconosciuto: $1${NC}"
        echo -e "${YELLOW}💡 Usa: ./launch.sh help${NC}"
        exit 1
        ;;
esac
