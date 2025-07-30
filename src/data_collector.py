import yfinance as yf
import pandas as pd

def get_stock_data(ticker, period="1mo"):
    """
    Scarica i dati storici di un titolo
    
    Args:
        ticker (str): Simbolo del titolo (es. "AAPL")
        period (str): Periodo dei dati ("1d", "5d", "1mo", "3mo", "6mo", "1y", etc.)
    
    Returns:
        pandas.DataFrame: DataFrame con i dati del titolo
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        if df.empty:
            # Non stampare più questo messaggio, sarà gestito dal chiamante
            return pd.DataFrame()
        
        return df
    except Exception as e:
        # Re-raise l'eccezione per permettere al chiamante di gestirla
        raise e
