#!/bin/bash

# 🚀 Stock AI - Script Tmux per Monitoring
# Script per creare sessione tmux con monitoring completo

SESSION_NAME="stock-ai-monitor"

# Colori
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Avvio Stock AI Monitoring Session${NC}"

# Termina sessione esistente se c'è
tmux kill-session -t $SESSION_NAME 2>/dev/null

# Crea nuova sessione
echo -e "${YELLOW}📱 Creazione sessione tmux: $SESSION_NAME${NC}"
tmux new-session -d -s $SESSION_NAME

# Setup finestre
# Finestra 0: Sistema principale
tmux rename-window -t $SESSION_NAME:0 'Trading-System'

# Finestra 1: Logs
tmux new-window -t $SESSION_NAME:1 -n 'Logs'

# Finestra 2: Monitoring  
tmux new-window -t $SESSION_NAME:2 -n 'Monitor'

# Finestra 3: Commands
tmux new-window -t $SESSION_NAME:3 -n 'Commands'

# Setup panelli nella finestra principale (0)
tmux select-window -t $SESSION_NAME:0

# Split verticale
tmux split-window -h

# Split orizzontale nel pannello destro
tmux select-pane -t 1
tmux split-window -v

# Setup comandi per ogni pannello
# Pannello 0: Status sistema
tmux send-keys -t $SESSION_NAME:0.0 'watch -n 5 "./trading_control.sh status && echo && ./monitor_system.sh"' Enter

# Pannello 1: Performance
tmux send-keys -t $SESSION_NAME:0.1 'watch -n 10 "./trading_control.sh performance"' Enter

# Pannello 2: Risorse sistema
tmux send-keys -t $SESSION_NAME:0.2 'watch -n 3 "echo \"=== PROCESSI ===\"; ps aux | grep python | head -5; echo; echo \"=== MEMORIA ===\"; free -h; echo; echo \"=== DISK ===\"; df -h /"' Enter

# Setup finestra logs (1)
tmux send-keys -t $SESSION_NAME:1 'echo "📊 Logs Trading System"; echo "Usa Ctrl+C per interrompere"; echo; tail -f logs/trading_system_$(date +%Y%m%d).log 2>/dev/null || echo "Log file non ancora creato"' Enter

# Setup finestra monitor (2)  
tmux send-keys -t $SESSION_NAME:2 'echo "🖥️  System Monitor"; echo; htop 2>/dev/null || top' Enter

# Setup finestra commands (3)
tmux send-keys -t $SESSION_NAME:3 'echo "🎮 Trading Commands"; echo; echo "Comandi disponibili:"; echo "  ./trading_control.sh start|stop|status|logs|performance"; echo "  ./monitor_system.sh"; echo "  ./backup_data.sh"; echo "  ./initialize_project.sh test|reset|clean"; echo; echo "Per avviare il sistema:"; echo "  ./trading_control.sh start"; echo'

# Torna alla finestra principale
tmux select-window -t $SESSION_NAME:0
tmux select-pane -t 0

echo -e "${GREEN}✅ Sessione tmux creata!${NC}"
echo -e "${YELLOW}Per accedere: tmux attach -t $SESSION_NAME${NC}"
echo -e "${YELLOW}Per uscire: Ctrl+B poi D${NC}"
echo -e "${YELLOW}Cambiare finestra: Ctrl+B poi 0,1,2,3${NC}"
echo -e "${YELLOW}Cambiare pannello: Ctrl+B poi frecce${NC}"
echo

# Mostra layout
echo "📱 Layout creato:"
echo "  Finestra 0 (Trading-System): Status | Performance | Risorse"
echo "  Finestra 1 (Logs): Tail logs in tempo reale" 
echo "  Finestra 2 (Monitor): htop/top sistema"
echo "  Finestra 3 (Commands): Comandi disponibili"
echo

# Attacca automaticamente se richiesto
if [[ "$1" == "--attach" ]] || [[ "$1" == "-a" ]]; then
    echo -e "${GREEN}🔗 Collegamento automatico...${NC}"
    tmux attach -t $SESSION_NAME
else
    echo -e "${BLUE}💡 Per collegarti: tmux attach -t $SESSION_NAME${NC}"
fi
