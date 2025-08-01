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
