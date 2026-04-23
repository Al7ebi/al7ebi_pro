import yfinance as yf
import pandas_ta as ta

def get_stock_data(symbol):
    # جلب البيانات من Yahoo Finance
    df = yf.download(symbol, period="1y")
    # حساب مؤشر RSI كمثال
    df['RSI'] = ta.rsi(df['Close'], length=14)
    return df
