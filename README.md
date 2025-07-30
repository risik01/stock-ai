# Stock-AI 📈🤖

**Stock-AI** è un progetto open source leggero che legge dati azionari da internet, utilizza una semplice intelligenza artificiale (con reinforcement learning) per prendere decisioni automatiche di acquisto e vendita, partendo da un portafoglio virtuale iniziale da **10€** con l'obiettivo di farlo crescere.

---

## 🚀 Funzionalità principali

- 📡 Lettura automatica dei dati azionari da Yahoo Finance
- 🤖 Decisioni di investimento basate su logica semplice o IA
- 🌐 Dashboard Web con Flask
- 🧠 Reinforcement Learning (PPO con Stable Baselines 3)
- 🖥️ Interfaccia CLI semplice per uso locale
- 💼 Simulazione realistica di portafoglio

---

## 📦 Requisiti

- Python 3.8+
- `pip`

### ▶️ Installazione pacchetti:

```bash
pip install -r requirements.txt

## Struttura progetto
stock-ai/
├── src/
│   ├── data_collector.py       # Lettura dati
│   ├── strategy_engine.py      # Strategia base
│   ├── portfolio.py            # Portafoglio simulato
│   ├── dashboard.py            # Web UI (Flask)
│   ├── trading_env.py          # Ambiente RL
│   ├── train_rl.py             # Allenamento IA
│   ├── test_rl.py              # Test IA
│   └── main.py                 # CLI entry point
├── requirements.txt
├── README.md
└── .gitignore

## Esecuzione
python src/main.py

## dashBoard Web
1) python src/dashboard.py
2) Apri il browser su:  http://localhost:5000

## Addestramento IA (Reinforcement Learning)
python src/train_rl.py
Questo addestra un agente IA sul titolo AAPL con dati di 1 mese.

## Testare l’agente addestrato
python src/test_rl.py
Visualizza a video i risultati delle decisioni dell'agente allenato.
