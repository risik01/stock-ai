def should_buy(df):
    """Compra se il prezzo attuale è maggiore della media mobile a 3 giorni."""
    if len(df) < 3:
        return False
    avg = df['Close'].rolling(window=3).mean()
    return df['Close'].iloc[-1] > avg.iloc[-1]
