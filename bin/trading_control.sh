#!/bin/bash
# Script di controllo Trading AI System
# Path corretto dalla cartella bin/

cd "$(dirname "$0")/.." || exit 1  # Vai alla root del progetto

case "$1" in
    start)
        echo "🚀 Avvio Trading AI System..."
        source .venv/bin/activate
        nohup python3 src/automated_trading_system.py > logs/system.log 2>&1 &
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
