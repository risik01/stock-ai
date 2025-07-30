def should_buy(df):
    """
    Determina se comprare un titolo basandosi sui dati storici
    
    Strategia semplice: compra se il prezzo attuale è sopra la media mobile a 3 giorni
    
    Args:
        df (pandas.DataFrame): DataFrame con i dati del titolo
    
    Returns:
        bool: True se dovremmo comprare, False altrimenti
    """
    if len(df) < 3:
        return False
    
    try:
        current_price = df["Close"].iloc[-1]
        avg_3d = df['Close'].rolling(window=3).mean().iloc[-1]
        
        # Strategia: compra se prezzo attuale > media 3 giorni
        return current_price > avg_3d
    except Exception as e:
        print(f"Errore nella strategia: {e}")
        return False

def should_sell(df):
    """
    Determina se vendere un titolo
    
    Args:
        df (pandas.DataFrame): DataFrame con i dati del titolo
    
    Returns:
        bool: True se dovremmo vendere, False altrimenti
    """
    if len(df) < 3:
        return False
    
    try:
        current_price = df["Close"].iloc[-1]
        avg_3d = df['Close'].rolling(window=3).mean().iloc[-1]
        
        # Strategia: vendi se prezzo attuale < media 3 giorni
        return current_price < avg_3d
    except Exception as e:
        print(f"Errore nella strategia di vendita: {e}")
        return False
