from flask import Flask, render_template_string
from data_collector import get_stock_data
from strategy_engine import should_buy

app = Flask(__name__)

TEMPLATE = """
<!doctype html>
<title>Stock AI Dashboard</title>
<h2>Analisi titolo: {{ ticker }}</h2>
<p>Ultimo prezzo: {{ price }}</p>
<p>Decisione: <b>{{ decision }}</b></p>
"""

@app.route("/")
def index():
    ticker = "AAPL"
    df = get_stock_data(ticker)
    price = df["Close"].iloc[-1]
    decision = "✅ COMPRA" if should_buy(df) else "⏳ ATTENDI"
    return render_template_string(TEMPLATE, ticker=ticker, price=round(price, 2), decision=decision)

if __name__ == "__main__":
    app.run(debug=True)
