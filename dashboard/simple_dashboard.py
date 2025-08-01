#!/usr/bin/env python3
"""
Dashboard Semplificato per Testing
"""

from flask import Flask, render_template, jsonify
import json
import os
from pathlib import Path

def create_app(config):
    """Crea app Flask semplificata"""
    app = Flask(__name__)
    
    @app.route('/')
    def dashboard():
        """Dashboard principale"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Stock AI Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; }
        .stats { display: flex; gap: 20px; margin: 20px 0; }
        .stat-card { background: #ecf0f1; padding: 15px; border-radius: 8px; flex: 1; }
        .status { margin: 20px 0; }
        .success { color: #27ae60; }
        .info { color: #3498db; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Stock AI Trading System</h1>
        <p>Dashboard Web - Sistema Operativo</p>
    </div>
    
    <div class="status">
        <h2>📊 Status Sistema</h2>
        <p class="success">✅ Sistema Operativo</p>
        <p class="info">🔧 Dashboard semplificato per testing</p>
        <p class="info">📁 Configurazione caricata correttamente</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <h3>Portfolio</h3>
            <p>Capitale: €10,000</p>
            <p>Posizioni: 0</p>
        </div>
        <div class="stat-card">
            <h3>Trading</h3>
            <p>Trades oggi: 0</p>
            <p>P&L: €0.00</p>
        </div>
        <div class="stat-card">
            <h3>Sistema</h3>
            <p>Status: Online</p>
            <p>Uptime: OK</p>
        </div>
    </div>
    
    <div class="status">
        <h2>🚀 Prossimi Passi</h2>
        <ul>
            <li>✅ Dashboard base funzionante</li>
            <li>🔄 Integrazione dati real-time</li>
            <li>📈 Grafici performance</li>
            <li>🤖 Controlli AI</li>
        </ul>
    </div>
</body>
</html>
        """
    
    @app.route('/api/status')
    def api_status():
        """API status"""
        return jsonify({
            'status': 'ok',
            'timestamp': '2025-08-01',
            'system': 'operational',
            'components': {
                'dashboard': 'ok',
                'config': 'ok',
                'portfolio': 'ok'
            }
        })
    
    return app

if __name__ == '__main__':
    # Test diretto
    config = {'dashboard': {'host': '0.0.0.0', 'port': 5000, 'debug': True}}
    app = create_app(config)
    print("🌐 Dashboard semplificato avviato")
    print("🔗 URL: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
